from pathlib import Path
import json
import math
import re

import pandas as pd

from srkg.kb import STUDY_QUESTION_TYPES, load_knowledge_base


DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
SEMANTIC_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
DISPLAY_ID_RE = re.compile(r"^(?:SR|GR|MATHS)-[1-9]\d*\.[1-9]\d*$")


def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_ROOT / name, dtype=str).fillna("")


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
    assert set(designs["module_id"]) == {
        "gr.foundations_and_spacetime_geometry",
        "gr.connections_transport_and_motion",
        "gr.curvature_and_gravitational_action",
        "gr.matter_and_einstein_equations",
        "gr.weak_field_and_classical_tests",
        "gr.schwarzschild_geometry_and_black_holes",
        "sr.spacetime_foundations",
        "sr.relativistic_mechanics",
        "sr.variational_and_field_theory",
        "sr.electromagnetic_structure_gauge_and_stress_energy",
        "sr.field_dynamics_conservation_and_radiation",
    }
    assert set(designs["module_id"]).issubset(set(modules["module_id"]))
    assert designs["icon_caption"].str.strip().ne("").all()
    assert designs["detail_caption"].str.strip().ne("").all()


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


def test_four_vector_examples_retain_taxonomy_and_teaching_dependency():
    edges = _read_csv("edges.csv")
    triples = set(zip(edges["source"], edges["target"], edges["relation"]))

    assert ("sr.position_four_vector", "sr.four_vectors", "REQUIRES") in triples
    for concept in ("position", "velocity", "momentum"):
        assert (f"sr.{concept}_four_vector", "sr.four_vectors", "INSTANCE_OF") in triples
    # Later examples inherit the prerequisite through the derivation chain.
    assert ("sr.velocity_four_vector", "sr.position_four_vector", "DERIVES_FROM") in triples
    assert ("sr.momentum_four_vector", "sr.velocity_four_vector", "DERIVES_FROM") in triples


def test_real_data_study_question_types_are_canonical():
    study_questions = _read_csv("study_questions.csv")

    assert set(study_questions["question_type"]).issubset(STUDY_QUESTION_TYPES)


def test_filtered_study_questions_do_not_reference_authored_question_numbers():
    study_questions = _read_csv("study_questions.csv")
    filtered_types_by_mode = {
        "core": {"short_answer"},
        "maths": {"calculation"},
        "context": {"multiple_choice"},
    }
    reference_pattern = re.compile(
        r"\bq\d+\b|\bquestion\s+\d+\b|\bprevious question\b",
        re.IGNORECASE,
    )

    failures = []
    for mode, question_types in filtered_types_by_mode.items():
        filtered = study_questions[study_questions["question_type"].isin(question_types)]
        for row in filtered.itertuples(index=False):
            text = f"{row.prompt} {row.answer}"
            if reference_pattern.search(text):
                failures.append(f"{mode}: {row.question_id}")

    assert failures == []


def test_lorentz_maths_view_has_standard_boost_setup_context():
    content_blocks = _read_csv("content_blocks.csv")
    lorentz_blocks = content_blocks[content_blocks["concept_id"] == "sr.lorentz_transformations"]
    maths_kinds = {
        "construction",
        "derivation",
        "derivation_step",
        "result",
        "decomposition",
        "convention",
        "worked_example",
    }
    visible_blocks = lorentz_blocks[lorentz_blocks["kind"].isin(maths_kinds)]

    assert "sr.lorentz_transformations.setup" in set(visible_blocks["block_id"])
    assert visible_blocks.loc[
        visible_blocks["block_id"] == "sr.lorentz_transformations.setup",
        "body",
    ].str.contains("standard boost", case=False).any()


def test_gr_and_maths_text_does_not_double_escape_latex_backslashes():
    nodes = _read_csv("nodes.csv")
    concept_ids = set(nodes.loc[nodes["domain"].isin({"gr", "math"}), "id"])
    content_blocks = _read_csv("content_blocks.csv")
    study_questions = _read_csv("study_questions.csv")
    modules = _read_csv("modules.csv")
    module_content_blocks = _read_csv("module_content_blocks.csv")

    content_text = content_blocks.loc[
        content_blocks["concept_id"].isin(concept_ids), ["title", "body"]
    ]
    question_text = study_questions.loc[
        study_questions["concept_id"].isin(concept_ids), ["prompt", "answer"]
    ]
    module_ids = set(modules.loc[modules["domain"].isin({"gr", "math"}), "module_id"])
    module_text = module_content_blocks.loc[
        module_content_blocks["module_id"].isin(module_ids), ["title", "body"]
    ]
    assert not content_text.apply(lambda column: column.str.contains(r"\\\\", regex=True)).any().any()
    assert not question_text.apply(lambda column: column.str.contains(r"\\\\", regex=True)).any().any()
    assert not module_text.apply(lambda column: column.str.contains(r"\\\\", regex=True)).any().any()


def test_gr_and_maths_module_titles_include_domain_and_module_number():
    modules = _read_csv("modules.csv")
    modules = modules[modules["domain"].isin({"gr", "math"})]

    expected_prefixes = modules.apply(
        lambda row: f"{'MATHS' if row['domain'] == 'math' else row['domain'].upper()}-"
        f"{int(row['sequence']) // 10} ",
        axis=1,
    )
    assert all(
        title.startswith(prefix)
        for title, prefix in zip(modules["title"], expected_prefixes)
    )


def test_runtime_sr_modules_match_the_reviewed_partition_candidate():
    root = DATA_ROOT.parent
    modules = _read_csv("modules.csv")
    runtime_members = _read_csv("module_members.csv")
    candidate_members = pd.read_csv(
        root / "tests" / "fixtures" / "module_partitions" / "sr.csv",
        dtype=str,
    ).fillna("")

    sr_modules = modules.loc[modules["domain"] == "sr", ["module_id", "title"]]
    assert list(sr_modules.itertuples(index=False, name=None)) == [
        ("sr.spacetime_foundations", "SR-1 Spacetime and Lorentz Symmetry"),
        ("sr.relativistic_mechanics", "SR-2 Relativistic Particle Mechanics"),
        ("sr.variational_and_field_theory", "SR-3 Action and Field Theory"),
        (
            "sr.electromagnetic_structure_gauge_and_stress_energy",
            "SR-4 Covariant Electromagnetism",
        ),
        (
            "sr.field_dynamics_conservation_and_radiation",
            "SR-5 Field Dynamics and Radiation",
        ),
    ]
    sr_concept_ids = set(candidate_members["concept_id"])
    actual = runtime_members.loc[
        runtime_members["concept_id"].isin(sr_concept_ids),
        ["module_id", "concept_id"],
    ].sort_values(["module_id", "concept_id"]).reset_index(drop=True)
    expected = candidate_members[["module_id", "concept_id"]].sort_values(
        ["module_id", "concept_id"]
    ).reset_index(drop=True)
    pd.testing.assert_frame_equal(actual, expected)

    supports = _read_csv("module_supports.csv")
    sr_supports = supports[supports["module_id"].str.startswith("sr.")]
    actual_supports = set(zip(sr_supports["module_id"], sr_supports["target_id"]))
    assert actual_supports == {
        ("sr.relativistic_mechanics", "sr.spacetime_foundations"),
        ("sr.variational_and_field_theory", "sr.spacetime_foundations"),
        ("sr.variational_and_field_theory", "sr.relativistic_mechanics"),
        (
            "sr.electromagnetic_structure_gauge_and_stress_energy",
            "sr.spacetime_foundations",
        ),
        (
            "sr.electromagnetic_structure_gauge_and_stress_energy",
            "sr.relativistic_mechanics",
        ),
        (
            "sr.electromagnetic_structure_gauge_and_stress_energy",
            "sr.variational_and_field_theory",
        ),
        (
            "sr.field_dynamics_conservation_and_radiation",
            "sr.variational_and_field_theory",
        ),
        (
            "sr.field_dynamics_conservation_and_radiation",
            "sr.electromagnetic_structure_gauge_and_stress_energy",
        ),
    }


def test_runtime_gr_modules_match_the_reviewed_partition_candidate():
    root = DATA_ROOT.parent
    modules = _read_csv("modules.csv")
    runtime_members = _read_csv("module_members.csv")
    candidate_members = pd.read_csv(
        root / "tests" / "fixtures" / "module_partitions" / "gr.csv",
        dtype=str,
    ).fillna("")

    gr_modules = modules.loc[modules["domain"] == "gr", ["module_id", "title"]]
    assert list(gr_modules.itertuples(index=False, name=None)) == [
        (
            "gr.foundations_and_spacetime_geometry",
            "GR-1 Foundations of Curved Spacetime",
        ),
        (
            "gr.connections_transport_and_motion",
            "GR-2 Connections and Geodesics",
        ),
        (
            "gr.curvature_and_gravitational_action",
            "GR-3 Curvature and Gravitational Action",
        ),
        (
            "gr.matter_and_einstein_equations",
            "GR-4 Matter and Einstein Equations",
        ),
        (
            "gr.weak_field_and_classical_tests",
            "GR-5 Weak-Field Gravity",
        ),
        (
            "gr.schwarzschild_geometry_and_black_holes",
            "GR-6 Schwarzschild Black Holes",
        ),
    ]
    gr_concept_ids = set(candidate_members["concept_id"])
    actual = runtime_members.loc[
        runtime_members["concept_id"].isin(gr_concept_ids),
        ["module_id", "concept_id"],
    ].sort_values(["module_id", "concept_id"]).reset_index(drop=True)
    expected = candidate_members.sort_values(
        ["module_id", "concept_id"]
    ).reset_index(drop=True)
    pd.testing.assert_frame_equal(actual, expected)

    supports = _read_csv("module_supports.csv")
    gr_supports = supports[supports["module_id"].str.startswith("gr.")]
    actual_supports = set(zip(gr_supports["module_id"], gr_supports["target_id"]))
    assert actual_supports == {
        (
            "gr.connections_transport_and_motion",
            "gr.foundations_and_spacetime_geometry",
        ),
        (
            "gr.curvature_and_gravitational_action",
            "gr.foundations_and_spacetime_geometry",
        ),
        (
            "gr.curvature_and_gravitational_action",
            "gr.connections_transport_and_motion",
        ),
        (
            "gr.matter_and_einstein_equations",
            "gr.foundations_and_spacetime_geometry",
        ),
        (
            "gr.matter_and_einstein_equations",
            "gr.connections_transport_and_motion",
        ),
        (
            "gr.matter_and_einstein_equations",
            "gr.curvature_and_gravitational_action",
        ),
        (
            "gr.weak_field_and_classical_tests",
            "gr.foundations_and_spacetime_geometry",
        ),
        (
            "gr.weak_field_and_classical_tests",
            "gr.connections_transport_and_motion",
        ),
        (
            "gr.weak_field_and_classical_tests",
            "gr.matter_and_einstein_equations",
        ),
        (
            "gr.schwarzschild_geometry_and_black_holes",
            "gr.foundations_and_spacetime_geometry",
        ),
        (
            "gr.schwarzschild_geometry_and_black_holes",
            "gr.connections_transport_and_motion",
        ),
        (
            "gr.schwarzschild_geometry_and_black_holes",
            "gr.curvature_and_gravitational_action",
        ),
    }


def test_authored_layout_covers_all_concepts_and_modules():
    edges = _read_csv("edges.csv")
    assert not (
        (edges["source"] == "sr.wave_equation")
        & (edges["target"] == "sr.metric_tensor")
        & (edges["relation"] == "REQUIRES")
    ).any()

    layout = json.loads((DATA_ROOT / "layout.json").read_text(encoding="utf-8"))
    nodes = _read_csv("nodes.csv")
    modules = _read_csv("modules.csv")
    assert layout["revision"] == "7"
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


def test_sr_transitive_edge_policy_omits_redundant_direct_edges():
    edges = _read_csv("edges.csv")
    actual_edges = set(zip(edges["source"], edges["target"], edges["relation"]))
    redundant_edges = {
        ("sr.vector_field", "sr.lorentz_transformations", "REQUIRES"),
        ("sr.mass_energy_equivalence", "sr.metric_tensor", "DERIVES_FROM"),
        ("sr.electromagnetic_waves", "sr.electric_field", "REQUIRES"),
        ("sr.electromagnetic_waves", "sr.magnetic_field", "REQUIRES"),
        ("sr.maxwells_equations", "sr.field_tensor", "REQUIRES"),
        ("sr.electromagnetic_waves", "sr.maxwells_equations", "DERIVES_FROM"),
        ("sr.hamiltonian_formalism", "sr.lagrangian", "DERIVES_FROM"),
        ("sr.lorentz_invariance", "sr.metric_tensor", "DERIVES_FROM"),
        ("sr.lorentz_transformations", "sr.metric_tensor", "DERIVES_FROM"),
    }

    assert actual_edges.isdisjoint(redundant_edges)


def test_gr_actions_treat_the_general_action_principle_as_related_context():
    edges = _read_csv("edges.csv")
    action_links = edges[
        edges["source"].isin({"gr.geodesic_action", "gr.einstein_hilbert_action"})
        & (edges["target"] == "sr.action_principle")
    ]

    assert set(zip(action_links["source"], action_links["relation"])) == {
        ("gr.geodesic_action", "RELATED"),
        ("gr.einstein_hilbert_action", "RELATED"),
    }


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
