from pathlib import Path
import pandas as pd
import re
DOMAIN_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = DOMAIN_ROOT.parents[1] / "data"


def _read_csv(name):
    return pd.read_csv(DOMAIN_ROOT / "data" / name, dtype=str).fillna("")


def test_four_vector_examples_retain_taxonomy_and_teaching_dependency():
    edges = _read_csv("edges.csv")
    triples = set(zip(edges["source"], edges["target"], edges["relation"]))

    assert ("sr.position_four_vector", "sr.four_vectors", "REQUIRES") in triples
    for concept in ("position", "velocity", "momentum"):
        assert (f"sr.{concept}_four_vector", "sr.four_vectors", "INSTANCE_OF") in triples
    # Later examples inherit the prerequisite through the derivation chain.
    assert ("sr.velocity_four_vector", "sr.position_four_vector", "DERIVES_FROM") in triples
    assert ("sr.momentum_four_vector", "sr.velocity_four_vector", "DERIVES_FROM") in triples


def test_em_density_and_flux_are_components_of_the_em_stress_energy_tensor():
    edges = _read_csv("edges.csv")
    blocks = _read_csv("content_blocks.csv").set_index("block_id")
    component_edges = set(
        zip(
            edges.loc[edges["relation"] == "COMPONENT_OF", "source"],
            edges.loc[edges["relation"] == "COMPONENT_OF", "target"],
        )
    )

    assert ("sr.em_energy_density", "sr.em_stress_energy") in component_edges
    assert ("sr.poynting_vector", "sr.em_stress_energy") in component_edges
    assert ("sr.em_energy_density", "sr.energy_momentum_tensor") not in component_edges
    assert ("sr.poynting_vector", "sr.energy_momentum_tensor") not in component_edges
    for block_id in (
        "sr.em_energy_density.tensor_component",
        "sr.poynting_vector.tensor_origin",
    ):
        assert r"\cref{electromagnetic stress--energy tensor}{sr.em_stress_energy}" in blocks.loc[
            block_id, "body"
        ]


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


def test_runtime_sr_modules_match_the_reviewed_partition_candidate():
    root = DATA_ROOT.parent
    modules = _read_csv("modules.csv")
    runtime_members = _read_csv("module_members.csv")
    candidate_members = pd.read_csv(
        DOMAIN_ROOT / "tests" / "module_partition.csv",
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
