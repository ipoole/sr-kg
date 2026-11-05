from pathlib import Path
import pandas as pd
import re
DOMAIN_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = DOMAIN_ROOT.parents[1] / "data"


def _read_csv(name):
    return pd.read_csv(DOMAIN_ROOT / "data" / name, dtype=str).fillna("")


def test_runtime_gr_modules_match_the_reviewed_partition_candidate():
    root = DATA_ROOT.parent
    modules = _read_csv("modules.csv")
    runtime_members = _read_csv("module_members.csv")
    candidate_members = pd.read_csv(
        DOMAIN_ROOT / "tests" / "module_partition.csv",
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
        (
            "gr.schwarzschild_geometry_and_black_holes",
            "gr.matter_and_einstein_equations",
        ),
    }


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


def test_text_does_not_double_escape_latex_backslashes():
    nodes = _read_csv("nodes.csv")
    concept_ids = set(nodes.loc[nodes["domain"].eq("gr"), "id"])
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
    module_ids = set(modules.loc[modules["domain"].eq("gr"), "module_id"])
    module_text = module_content_blocks.loc[
        module_content_blocks["module_id"].isin(module_ids), ["title", "body"]
    ]
    assert not content_text.apply(lambda column: column.str.contains(r"\\\\", regex=True)).any().any()
    assert not question_text.apply(lambda column: column.str.contains(r"\\\\", regex=True)).any().any()
    assert not module_text.apply(lambda column: column.str.contains(r"\\\\", regex=True)).any().any()


def test_module_titles_include_domain_and_module_number():
    modules = _read_csv("modules.csv")
    modules = modules[modules["domain"].eq("gr")]

    expected_prefixes = modules.apply(
        lambda row: f"{'MATHS' if row['domain'] == 'math' else row['domain'].upper()}-"
        f"{int(row['sequence']) // 10} ",
        axis=1,
    )
    assert all(
        title.startswith(prefix)
        for title, prefix in zip(modules["title"], expected_prefixes)
    )


def test_schwarzschild_derivation_reaches_vacuum_equations_and_metric_action():
    edges = _read_csv("edges.csv")
    derivations = set(zip(
        edges.loc[edges["relation"].eq("DERIVES_FROM"), "source"],
        edges.loc[edges["relation"].eq("DERIVES_FROM"), "target"],
    ))
    route = [
        "gr.schwarzschild_metric",
        "gr.vacuum_field_equations",
        "gr.einstein_field_equations",
        "gr.einstein_hilbert_action",
    ]
    assert all(pair in derivations for pair in zip(route, route[1:]))
    # A solution can retain its taxonomy as well as its derivation dependency.
    assert not edges[
        edges["source"].eq(route[0])
        & edges["target"].eq(route[1])
        & edges["relation"].eq("INSTANCE_OF")
    ].empty
