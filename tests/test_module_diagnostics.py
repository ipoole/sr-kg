import pandas as pd

from srkg.kb import KnowledgeBase, KnowledgeBasePaths
from srkg.model import Concept, Module, ModuleSupport
from srkg.module_diagnostics import (
    build_module_diagnostics,
    format_module_diagnostics,
)


def _concept(concept_id, label):
    return Concept(id=concept_id, label=label, display_id=concept_id, domain="test")


def _kb_with_modules():
    return KnowledgeBase(
        paths=KnowledgeBasePaths(root=None, nodes="nodes.csv", edges="edges.csv"),
        nodes_df=pd.DataFrame([
            {"id": "a.1", "label": "A one", "display_id": "TEST-1.1"},
            {"id": "a.2", "label": "A two", "display_id": "TEST-1.2"},
            {"id": "b.1", "label": "B one", "display_id": "TEST-2.1"},
            {"id": "c.1", "label": "C one", "display_id": "TEST-3.1"},
        ]),
        edges_df=pd.DataFrame([
            {
                "source": "a.2",
                "target": "a.1",
                "relation": "REQUIRES",
                "note": "Internal A edge.",
            },
            {
                "source": "b.1",
                "target": "a.2",
                "relation": "REQUIRES",
                "note": "B needs A.",
            },
            {
                "source": "c.1",
                "target": "b.1",
                "relation": "REQUIRES",
                "note": "C needs B.",
            },
            {
                "source": "a.1",
                "target": "c.1",
                "relation": "REQUIRES",
                "note": "A loops to C.",
            },
        ]),
        edge_key={"REQUIRES": {"directed": True}},
        concepts=(
            _concept("a.1", "A one"),
            _concept("a.2", "A two"),
            _concept("b.1", "B one"),
            _concept("c.1", "C one"),
        ),
        modules=(
            Module(
                module_id="module.a",
                domain="test",
                title="Module A",
                sequence=10,
                members=["a.1", "a.2"],
            ),
            Module(
                module_id="module.b",
                domain="test",
                title="Module B",
                sequence=20,
                members=["b.1"],
                supports=[
                    ModuleSupport(
                        module_id="module.b",
                        target_type="module",
                        target_id="module.a",
                        role="prerequisite",
                    ),
                ],
            ),
            Module(
                module_id="module.c",
                domain="test",
                title="Module C",
                sequence=30,
                members=["c.1"],
            ),
        ),
    )


def test_build_module_diagnostics_counts_boundary_edges_and_support_coverage():
    diagnostics = build_module_diagnostics(_kb_with_modules(), relations=["REQUIRES"])

    assert diagnostics.module_count == 3
    assert diagnostics.concept_count == 4
    assert diagnostics.internal_edge_count == 1
    assert diagnostics.boundary_edge_count == 3
    assert diagnostics.boundary_relation_counts == {"REQUIRES": 3}
    assert diagnostics.internal_relation_counts == {"REQUIRES": 1}
    assert diagnostics.member_order_violations == ()
    assert [
        (edge.source_concept_id, edge.target_concept_id)
        for edge in diagnostics.module_order_violations
    ] == [("a.1", "c.1")]

    pairs = {
        (pair.source_module_id, pair.target_module_id): pair
        for pair in diagnostics.boundary_pairs
    }
    assert pairs[("module.b", "module.a")].edge_count == 1
    assert pairs[("module.b", "module.a")].declared_support is True
    assert pairs[("module.c", "module.b")].declared_support is False
    assert pairs[("module.a", "module.c")].declared_support is False

    assert [
        (issue.source_module_id, issue.target_module_id, issue.edge_count)
        for issue in diagnostics.undeclared_boundary_pairs
    ] == [
        ("module.a", "module.c", 1),
        ("module.c", "module.b", 1),
    ]


def test_build_module_diagnostics_reports_quotient_dag_cycles():
    diagnostics = build_module_diagnostics(_kb_with_modules(), relations=["REQUIRES"])

    assert len(diagnostics.quotient_dag_reports) == 1
    report = diagnostics.quotient_dag_reports[0]
    assert report.name == "REQUIRES"
    assert report.is_dag is False
    assert len(report.cycles) == 1


def test_build_module_diagnostics_reports_within_module_order_contradictions():
    kb = _kb_with_modules()
    extra = pd.DataFrame([{
        "source": "a.1",
        "target": "a.2",
        "relation": "REQUIRES",
        "note": "Contradicts member order.",
    }])
    kb = KnowledgeBase(
        paths=kb.paths,
        nodes_df=kb.nodes_df,
        edges_df=pd.concat([kb.edges_df, extra], ignore_index=True),
        edge_key=kb.edge_key,
        concepts=kb.concepts,
        modules=kb.modules,
    )

    diagnostics = build_module_diagnostics(kb, relations=["REQUIRES"])

    assert [
        (edge.source_concept_id, edge.target_concept_id)
        for edge in diagnostics.member_order_violations
    ] == [("a.1", "a.2")]


def test_module_sequence_comparisons_do_not_cross_domains():
    kb = _kb_with_modules()
    cross_domain_modules = (
        kb.modules[0],
        Module(
            module_id="other.b",
            domain="other",
            title="Other B",
            sequence=20,
            members=["b.1"],
        ),
        kb.modules[2],
    )
    kb = KnowledgeBase(
        paths=kb.paths,
        nodes_df=kb.nodes_df,
        edges_df=kb.edges_df,
        edge_key=kb.edge_key,
        concepts=kb.concepts,
        modules=cross_domain_modules,
    )

    diagnostics = build_module_diagnostics(kb, relations=["REQUIRES"])

    assert [
        (edge.source_concept_id, edge.target_concept_id)
        for edge in diagnostics.module_order_violations
    ] == [("a.1", "c.1")]


def test_format_module_diagnostics_includes_summary_pairs_and_dag_status():
    text = format_module_diagnostics(
        build_module_diagnostics(_kb_with_modules(), relations=["REQUIRES"]),
        max_items=3,
    )

    assert "Module diagnostics" in text
    assert "Modules: 3" in text
    assert "Concepts with module membership: 4" in text
    assert "Boundary concept edges: 3" in text
    assert "REQUIRES: 3" in text
    assert (
        "module.b Module B -> module.a Module A: 1 edge(s), "
        "relations=REQUIRES: 1, supports=yes"
    ) in text
    assert "Undeclared module boundary pairs: 2" in text
    assert "Module quotient DAGs" in text
    assert "REQUIRES: nodes=3, edges=3, dag=no, cycles=1" in text
    assert "Module-order contradictions: 1" in text
    assert "Within-module member-order contradictions: 0" in text
