from pathlib import Path
import json
import math
import re

import pandas as pd
from srkg.domain_sources import read_authored_table

from srkg.kb import (
    STUDY_QUESTION_MARKING_MODES,
    STUDY_QUESTION_TYPES,
    load_knowledge_base,
)


DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
SEMANTIC_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
DISPLAY_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*-[1-9]\d*\.[1-9]\d*$")


def _read_csv(name: str) -> pd.DataFrame:
    return read_authored_table(DATA_ROOT, name)


def test_real_data_loads_through_canonical_kb_root():
    kb = load_knowledge_base(DATA_ROOT)

    assert len(kb.concepts) > 0
    assert all("definition_new" not in concept.to_viewer_data() for concept in kb.concepts)


def test_real_data_concepts_use_semantic_ids_and_display_ids():
    nodes = _read_csv("nodes.csv")

    assert "layer" not in nodes.columns
    assert "layer_title" not in nodes.columns
    assert nodes["id"].map(lambda value: bool(SEMANTIC_ID_RE.fullmatch(value))).all()
    assert nodes["display_id"].map(lambda value: bool(DISPLAY_ID_RE.fullmatch(value))).all()
    assert not (nodes["id"] == nodes["display_id"]).any()


def test_module_graphic_designs_are_optional_and_reference_known_modules():
    designs = _read_csv("module_graphic_designs.csv")
    modules = _read_csv("modules.csv")

    assert designs["module_id"].is_unique
    from srkg.graphic_providers import default_graphics
    assert set(designs["module_id"]) == set(default_graphics().modules)


def test_real_data_display_ids_and_sequences_follow_owning_modules():
    nodes = _read_csv("nodes.csv").set_index("id")
    modules = _read_csv("modules.csv").set_index("module_id")
    members = _read_csv("module_members.csv")

    for module_id, rows in members.groupby("module_id", sort=False):
        code = modules.loc[module_id, "title"].split(" ", 1)[0]
        ordered = rows.assign(sequence_number=rows["sequence"].astype(int)).sort_values(
            "sequence_number"
        )
        assert list(ordered["sequence_number"]) == list(
            range(10, (len(ordered) + 1) * 10, 10)
        )
        assert [nodes.loc[concept_id, "display_id"] for concept_id in ordered["concept_id"]] == [
            f"{code}.{index}" for index in range(1, len(ordered) + 1)
        ]

    designs = _read_csv("concept_graphic_designs.csv")
    assert "layer" not in designs.columns


def test_real_data_edges_and_content_reference_known_semantic_concepts():
    nodes = _read_csv("nodes.csv")
    edges = _read_csv("edges.csv")
    content_blocks = _read_csv("content_blocks.csv")
    study_questions = _read_csv("study_questions.csv")
    concept_ids = set(nodes["id"])

    assert set(edges["source"]).issubset(concept_ids)
    assert set(edges["target"]).issubset(concept_ids)
    assert set(content_blocks["concept_id"]).issubset(concept_ids)
    assert set(study_questions["concept_id"]).issubset(concept_ids)
    assert not set(edges["source"]).intersection(set(nodes["display_id"]))
    assert not set(edges["target"]).intersection(set(nodes["display_id"]))


def test_real_data_study_question_types_are_canonical():
    study_questions = _read_csv("study_questions.csv")

    assert set(study_questions["question_type"]).issubset(STUDY_QUESTION_TYPES)
    assert set(study_questions["marking_mode"]).issubset(
        STUDY_QUESTION_MARKING_MODES
    )


def test_existing_authored_multiple_choice_questions_are_structured():
    study_questions = _read_csv("study_questions.csv")
    options = _read_csv("study_question_options.csv")
    multiple_choice = study_questions[
        study_questions["question_type"].eq("multiple_choice")
    ]
    automatic = multiple_choice[multiple_choice["marking_mode"].eq("automatic")]
    assert not multiple_choice.empty
    assert len(automatic) == len(multiple_choice)
    assert set(automatic["question_id"]).issubset(set(options["question_id"]))
    assert options.groupby("question_id").size().eq(4).all()
    assert options[options["is_correct"].eq("true")].groupby("question_id").size().eq(1).all()


def test_editorially_selected_calculations_and_concepts_are_automatically_marked():
    study_questions = _read_csv("study_questions.csv").set_index("question_id")
    options = _read_csv("study_question_options.csv")
    from srkg.domain_sources import discover_domains
    from srkg.kb import resolve_knowledge_base_paths
    automatic_calculations, automatic_concepts = set(), set()
    for package in discover_domains(resolve_knowledge_base_paths(DATA_ROOT)):
        path = package.root / "tests/study_expectations.json"
        if path.exists():
            expectations = json.loads(path.read_text())
            automatic_calculations.update(expectations["automatic_calculations"])
            automatic_concepts.update(expectations["automatic_concepts"])
    selected = automatic_calculations | automatic_concepts

    assert study_questions.loc[list(selected), "marking_mode"].eq("automatic").all()
    selected_options = options[options["question_id"].isin(selected)]
    assert set(selected_options["question_id"]) == selected
    assert selected_options.groupby("question_id").size().eq(4).all()
    assert (
        selected_options[selected_options["is_correct"].eq("true")]
        .groupby("question_id")
        .size()
        .eq(1)
        .all()
    )


def test_filtered_study_questions_do_not_reference_authored_question_numbers():
    study_questions = _read_csv("study_questions.csv")
    reference_pattern = re.compile(
        r"\bq\d+\b|\bquestion\s+\d+\b|\bprevious question\b",
        re.IGNORECASE,
    )

    failures = [row.question_id for row in study_questions.itertuples(index=False)
                if reference_pattern.search(f"{row.prompt} {row.answer}")]
    assert failures == []


def test_authored_layout_covers_all_concepts_and_modules():
    layout = load_knowledge_base(DATA_ROOT, include_graphics=False).published_layout.to_viewer_data()
    nodes = _read_csv("nodes.csv")
    modules = _read_csv("modules.csv")
    assert layout["revision"]
    assert set(layout["concepts"]) == set(nodes["id"])
    assert set(layout["modules"]) == set(modules["module_id"])
    assert modules["default_collapsed"].str.lower().eq("true").all()
    for module in layout["modules"].values():
        assert set(module["anchor"]) == {"x", "y"}
        assert all(isinstance(value, (int, float)) for value in module["anchor"].values())
    # Published positions are editable; validate geometry rather than freezing
    # individual coordinates that an author may legitimately rearrange.
    for position in layout["concepts"].values():
        assert set(position) == {"x", "y"}
        assert all(math.isfinite(value) for value in position.values())


def test_real_data_reference_links_resolve_to_known_rows():
    nodes = _read_csv("nodes.csv")
    content_blocks = _read_csv("content_blocks.csv")
    study_questions = _read_csv("study_questions.csv")
    references = _read_csv("references.csv")
    reference_links = _read_csv("reference_links.csv")

    known_sources = {
        "concept": set(nodes["id"]),
        "content_block": set(content_blocks["block_id"]),
        "study_question": set(study_questions["question_id"]),
    }
    assert set(reference_links["reference_id"]).issubset(set(references["reference_id"]))
    for row in reference_links.itertuples(index=False):
        assert row.source_id in known_sources[row.source_type]
