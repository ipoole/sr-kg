import pandas as pd
import pytest

from srkg.dag import (
    analyse_relation_group,
    build_dag_reports,
    format_dag_reports,
    load_dag_reports,
)


def _nodes_df():
    return pd.DataFrame([
        {"id": "1.1", "label": "Foundation", "layer": "1"},
        {"id": "1.2", "label": "Early Forward Source", "layer": "1"},
        {"id": "2.1", "label": "Middle", "layer": "2"},
        {"id": "2.2", "label": "Peer Source", "layer": "2"},
        {"id": "2.3", "label": "Peer Target", "layer": "2"},
        {"id": "2.4", "label": "Forward Target", "layer": "2"},
        {"id": "3.1", "label": "Capstone", "layer": "3"},
    ])


def _edges_df():
    return pd.DataFrame([
        {"source": "3.1", "target": "2.1", "relation": "PREREQ", "note": ""},
        {"source": "2.1", "target": "1.1", "relation": "PREREQ", "note": ""},
        {"source": "3.1", "target": "1.1", "relation": "PREREQ", "note": ""},
        {"source": "2.2", "target": "2.3", "relation": "PREREQ", "note": ""},
        {"source": "1.2", "target": "2.4", "relation": "PREREQ", "note": ""},
        {"source": "1.1", "target": "2.2", "relation": "MENTIONS", "note": ""},
    ])


def test_build_dag_reports_deduplicates_relations_and_adds_combined_report():
    reports = build_dag_reports(
        _nodes_df(),
        _edges_df(),
        ["PREREQ", "PREREQ", "", "MENTIONS"],
    )

    assert [report.name for report in reports] == [
        "PREREQ",
        "MENTIONS",
        "PREREQ+MENTIONS",
    ]
    assert [report.relations for report in reports] == [
        ("PREREQ",),
        ("MENTIONS",),
        ("PREREQ", "MENTIONS"),
    ]


def test_analyse_relation_group_filters_edges_and_reports_dag_structure():
    report = analyse_relation_group(
        _nodes_df(),
        _edges_df(),
        ("PREREQ",),
        "PREREQ",
    )

    assert report.node_count == 7
    assert report.edge_count == 5
    assert report.is_dag is True
    assert report.cycles == ()
    assert report.longest_chain == ("3.1", "2.1", "1.1")
    assert report.foundation_nodes == ("1.1", "2.3", "2.4")
    assert report.capstone_nodes == ("1.2", "2.2", "3.1")


def test_analyse_relation_group_reports_layer_and_same_layer_order_issues():
    report = analyse_relation_group(
        _nodes_df(),
        _edges_df(),
        ("PREREQ",),
        "PREREQ",
    )

    assert [(edge.source, edge.target) for edge in report.layer_forward_edges] == [
        ("1.2", "2.4"),
    ]
    assert [(edge.source, edge.target) for edge in report.same_layer_edges] == [
        ("2.2", "2.3"),
    ]
    assert [(edge.source, edge.target) for edge in report.same_layer_order_violations] == [
        ("2.2", "2.3"),
    ]

    violation = report.same_layer_order_violations[0]
    assert violation.source_label == "Peer Source"
    assert violation.source_layer == 2
    assert violation.target_label == "Peer Target"
    assert violation.target_layer == 2
    assert violation.relation == "PREREQ"


def test_analyse_relation_group_reports_transitive_redundant_edges():
    report = analyse_relation_group(
        _nodes_df(),
        _edges_df(),
        ("PREREQ",),
        "PREREQ",
    )

    assert len(report.transitive_redundancies) == 1
    redundancy = report.transitive_redundancies[0]
    assert (redundancy.edge.source, redundancy.edge.target) == ("3.1", "1.1")
    assert redundancy.path == ("3.1", "2.1", "1.1")
    assert redundancy.path_labels == ("Capstone", "Middle", "Foundation")


def test_analyse_relation_group_suggests_target_first_renumbering():
    report = analyse_relation_group(
        _nodes_df(),
        _edges_df(),
        ("PREREQ",),
        "PREREQ",
    )

    assert len(report.layer_renumberings) == 1
    renumbering = report.layer_renumberings[0]
    assert renumbering.layer == 2
    assert renumbering.current_order == ("2.1", "2.2", "2.3", "2.4")
    assert renumbering.proposed_order == ("2.1", "2.3", "2.2", "2.4")
    assert [
        (rename.old_id, rename.new_id, rename.label)
        for rename in renumbering.renames
    ] == [
        ("2.3", "2.2", "Peer Target"),
        ("2.2", "2.3", "Peer Source"),
    ]
    assert renumbering.resolved_violation_count == 1
    assert renumbering.remaining_order_violations == ()


def test_analyse_relation_group_reports_cycles_and_skips_longest_chain_for_cycles():
    nodes_df = pd.DataFrame([
        {"id": "1.1", "label": "A", "layer": "1"},
        {"id": "1.2", "label": "B", "layer": "1"},
    ])
    edges_df = pd.DataFrame([
        {"source": "1.1", "target": "1.2", "relation": "CYCLE", "note": ""},
        {"source": "1.2", "target": "1.1", "relation": "CYCLE", "note": ""},
    ])

    report = analyse_relation_group(nodes_df, edges_df, ("CYCLE",), "CYCLE")

    assert report.is_dag is False
    assert report.longest_chain == ()
    assert len(report.cycles) == 1
    assert {
        (edge.source, edge.target)
        for edge in report.cycles[0]
    } == {
        ("1.1", "1.2"),
        ("1.2", "1.1"),
    }


def test_format_dag_reports_includes_core_diagnostics_and_truncates_lists():
    report = analyse_relation_group(
        _nodes_df(),
        _edges_df(),
        ("PREREQ",),
        "PREREQ",
    )

    text = format_dag_reports([report], max_items=1)

    assert "DAG diagnostics" in text
    assert "Edge direction is source -> target." in text
    assert "PREREQ: nodes=7, edges=5, dag=yes, cycles=0" in text
    assert "Layer-forward directed edges (source layer < target layer): 1" in text
    assert "1.2 Early Forward Source [L1] PREREQ 2.4 Forward Target [L2]" in text
    assert "Same-layer directed edges: 1" in text
    assert "Transitively redundant direct edges (A -> C also has A -> ... -> C): 1" in text
    assert "via 3.1 Capstone -> 2.1 Middle -> 1.1 Foundation" in text
    assert "Suggested target-first renumbering within affected layers:" in text
    assert "Longest source -> target chain: 3.1 -> 2.1 -> 1.1" in text
    assert "Foundations (out-degree 0): 1.1, ... 2 more" in text
    assert "Capstones (in-degree 0): 1.2, ... 2 more" in text


def test_load_dag_reports_uses_directed_edge_key_metadata_and_default_direction(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    pd.DataFrame([
        {"id": "1.1", "label": "A", "layer": "1"},
        {"id": "1.2", "label": "B", "layer": "1"},
        {"id": "1.3", "label": "C", "layer": "1"},
    ]).to_csv(nodes_path, index=False)
    pd.DataFrame([
        {"source": "1.2", "target": "1.1", "relation": "DIRECTED", "note": ""},
        {"source": "1.3", "target": "1.1", "relation": "UNDIRECTED", "note": ""},
        {"source": "1.3", "target": "1.2", "relation": "MISSING_KEY", "note": ""},
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {
            "relation": "DIRECTED",
            "directed": "true",
            "category": "",
            "meaning": "",
            "example": "",
        },
        {
            "relation": "UNDIRECTED",
            "directed": "false",
            "category": "",
            "meaning": "",
            "example": "",
        },
    ]).to_csv(edge_key_path, index=False)

    reports = load_dag_reports(nodes_path, edges_path)

    assert [report.name for report in reports] == [
        "DIRECTED",
        "MISSING_KEY",
        "DIRECTED+MISSING_KEY",
    ]
    assert [report.edge_count for report in reports] == [1, 1, 2]


def test_load_dag_reports_explicit_relations_override_edge_key_direction(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    pd.DataFrame([
        {"id": "1.1", "label": "A", "layer": "1"},
        {"id": "1.2", "label": "B", "layer": "1"},
    ]).to_csv(nodes_path, index=False)
    pd.DataFrame([
        {"source": "1.2", "target": "1.1", "relation": "UNDIRECTED", "note": ""},
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {
            "relation": "UNDIRECTED",
            "directed": "false",
            "category": "",
            "meaning": "",
            "example": "",
        },
    ]).to_csv(edge_key_path, index=False)

    reports = load_dag_reports(
        nodes_path,
        edges_path,
        relations=["UNDIRECTED"],
    )

    assert len(reports) == 1
    assert reports[0].name == "UNDIRECTED"
    assert reports[0].edge_count == 1


def test_load_dag_reports_rejects_empty_default_directed_relation_set(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    pd.DataFrame([
        {"id": "1.1", "label": "A", "layer": "1"},
        {"id": "1.2", "label": "B", "layer": "1"},
    ]).to_csv(nodes_path, index=False)
    pd.DataFrame([
        {"source": "1.2", "target": "1.1", "relation": "UNDIRECTED", "note": ""},
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {
            "relation": "UNDIRECTED",
            "directed": "false",
            "category": "",
            "meaning": "",
            "example": "",
        },
    ]).to_csv(edge_key_path, index=False)

    with pytest.raises(ValueError) as exc:
        load_dag_reports(nodes_path, edges_path)

    assert str(exc.value) == (
        "No directed relations were found for DAG diagnostics. "
        "Check edges_key.csv or pass --dag-relations explicitly."
    )
