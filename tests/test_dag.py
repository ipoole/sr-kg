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
        {"id": "foundation", "display_id": "TEST-1.1", "label": "Foundation"},
        {"id": "middle", "display_id": "TEST-1.2", "label": "Middle"},
        {"id": "capstone", "display_id": "TEST-1.3", "label": "Capstone"},
        {"id": "other", "display_id": "TEST-1.4", "label": "Other"},
    ])


def _edges_df():
    return pd.DataFrame([
        {"source": "capstone", "target": "middle", "relation": "PREREQ", "note": ""},
        {"source": "middle", "target": "foundation", "relation": "PREREQ", "note": ""},
        {"source": "capstone", "target": "foundation", "relation": "PREREQ", "note": ""},
        {"source": "other", "target": "foundation", "relation": "MENTIONS", "note": ""},
    ])


def test_build_dag_reports_deduplicates_relations_and_adds_combined_report():
    reports = build_dag_reports(
        _nodes_df(), _edges_df(), ["PREREQ", "PREREQ", "", "MENTIONS"]
    )

    assert [report.name for report in reports] == [
        "PREREQ", "MENTIONS", "PREREQ+MENTIONS"
    ]


def test_analyse_relation_group_reports_generic_dag_structure_and_redundancy():
    report = analyse_relation_group(_nodes_df(), _edges_df(), ("PREREQ",), "PREREQ")

    assert report.is_dag is True
    assert report.cycles == ()
    assert report.longest_chain == ("capstone", "middle", "foundation")
    assert report.foundation_nodes == ("foundation",)
    assert report.capstone_nodes == ("capstone",)
    assert len(report.transitive_redundancies) == 1
    redundancy = report.transitive_redundancies[0]
    assert (redundancy.edge.source, redundancy.edge.target) == (
        "capstone", "foundation"
    )
    assert redundancy.path == ("capstone", "middle", "foundation")


def test_analyse_relation_group_reports_cycles_without_partition_metadata():
    edges = pd.DataFrame([
        {"source": "middle", "target": "foundation", "relation": "CYCLE", "note": ""},
        {"source": "foundation", "target": "middle", "relation": "CYCLE", "note": ""},
    ])

    report = analyse_relation_group(_nodes_df(), edges, ("CYCLE",), "CYCLE")

    assert report.is_dag is False
    assert report.longest_chain == ()
    assert len(report.cycles) == 1


def test_format_dag_reports_contains_only_partition_independent_diagnostics():
    text = format_dag_reports(
        [analyse_relation_group(_nodes_df(), _edges_df(), ("PREREQ",), "PREREQ")],
        max_items=1,
    )

    assert "DAG diagnostics" in text
    assert "PREREQ: nodes=3, edges=3, dag=yes, cycles=0" in text
    assert "Transitively redundant direct edges" in text
    assert "via capstone Capstone -> middle Middle -> foundation Foundation" in text
    assert "Longest source -> target chain: capstone -> middle -> foundation" in text
    assert "layer" not in text.lower()


def test_load_dag_reports_uses_directed_edge_key_metadata(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    _nodes_df().to_csv(nodes_path, index=False)
    pd.DataFrame([
        {"source": "middle", "target": "foundation", "relation": "DIRECTED", "note": ""},
        {"source": "other", "target": "foundation", "relation": "UNDIRECTED", "note": ""},
        {"source": "capstone", "target": "middle", "relation": "MISSING_KEY", "note": ""},
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {"relation": "DIRECTED", "directed": "true", "category": "", "meaning": "", "example": ""},
        {"relation": "UNDIRECTED", "directed": "false", "category": "", "meaning": "", "example": ""},
    ]).to_csv(edge_key_path, index=False)

    reports = load_dag_reports(nodes_path, edges_path, edge_key_path=edge_key_path)

    assert [report.name for report in reports] == [
        "DIRECTED", "MISSING_KEY", "DIRECTED+MISSING_KEY"
    ]


def test_load_dag_reports_explicit_relations_override_edge_key_direction(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    _nodes_df().to_csv(nodes_path, index=False)
    pd.DataFrame([
        {"source": "middle", "target": "foundation", "relation": "UNDIRECTED", "note": ""},
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {"relation": "UNDIRECTED", "directed": "false", "category": "", "meaning": "", "example": ""},
    ]).to_csv(edge_key_path, index=False)

    reports = load_dag_reports(
        nodes_path, edges_path, relations=["UNDIRECTED"], edge_key_path=edge_key_path
    )

    assert len(reports) == 1
    assert reports[0].edge_count == 1


def test_load_dag_reports_rejects_empty_default_directed_relation_set(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    _nodes_df().to_csv(nodes_path, index=False)
    pd.DataFrame([
        {"source": "middle", "target": "foundation", "relation": "UNDIRECTED", "note": ""},
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {"relation": "UNDIRECTED", "directed": "false", "category": "", "meaning": "", "example": ""},
    ]).to_csv(edge_key_path, index=False)

    with pytest.raises(ValueError, match="No directed relations"):
        load_dag_reports(nodes_path, edges_path, edge_key_path=edge_key_path)
