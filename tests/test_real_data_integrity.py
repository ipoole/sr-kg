from pathlib import Path
import re

import pandas as pd

from srkg.kb import STUDY_QUESTION_TYPES, load_knowledge_base


DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
SEMANTIC_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
DISPLAY_ID_RE = re.compile(r"^(?:\d+(\.\d+)+|[A-Z]+ \d+(\.\d+)+)$")


def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_ROOT / name, dtype=str).fillna("")


def test_real_data_loads_through_canonical_kb_root():
    kb = load_knowledge_base(DATA_ROOT)

    assert len(kb.concepts) > 0
    assert all("definition_new" not in concept.to_viewer_data() for concept in kb.concepts)


def test_real_data_concepts_use_semantic_ids_and_display_ids():
    nodes = _read_csv("nodes.csv")

    assert nodes["id"].map(lambda value: bool(SEMANTIC_ID_RE.fullmatch(value))).all()
    assert nodes["display_id"].map(lambda value: bool(DISPLAY_ID_RE.fullmatch(value))).all()
    assert not (nodes["id"] == nodes["display_id"]).any()


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


def test_real_module_titles_include_domain_and_layer_number():
    modules = _read_csv("modules.csv")

    expected_prefixes = modules.apply(
        lambda row: f"{'MATHS' if row['domain'] == 'math' else row['domain'].upper()}-"
        f"{int(row['sequence']) // 10} ",
        axis=1,
    )
    assert all(
        title.startswith(prefix)
        for title, prefix in zip(modules["title"], expected_prefixes)
    )


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
