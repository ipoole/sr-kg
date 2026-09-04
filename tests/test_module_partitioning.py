from pathlib import Path

import pandas as pd

from srkg.module_partitioning import (
    PartitionSearchConfig,
    analyse_partition,
    build_domain_graph,
    format_partition_report,
    search_module_partitions,
)


RELATIONS = ("REQUIRES", "DERIVES_FROM", "CONSTRUCTED_FROM")


def _nodes():
    return pd.DataFrame([
        {"id": "sr.a1", "display_id": "1.1", "label": "A one", "domain": "sr"},
        {"id": "sr.a2", "display_id": "1.2", "label": "A two", "domain": "sr"},
        {"id": "sr.b1", "display_id": "2.1", "label": "B one", "domain": "sr"},
        {"id": "sr.b2", "display_id": "2.2", "label": "B two", "domain": "sr"},
        {"id": "math.x", "display_id": "M 1.1", "label": "External", "domain": "math"},
    ])


def _edges():
    return pd.DataFrame([
        {"source": "sr.a2", "target": "sr.a1", "relation": "REQUIRES", "note": ""},
        {"source": "sr.b1", "target": "sr.a2", "relation": "DERIVES_FROM", "note": ""},
        {"source": "sr.b2", "target": "sr.b1", "relation": "CONSTRUCTED_FROM", "note": ""},
        {"source": "sr.a1", "target": "sr.b2", "relation": "REQUIRES", "note": ""},
        {"source": "sr.a1", "target": "math.x", "relation": "REQUIRES", "note": "excluded"},
        {"source": "sr.a1", "target": "sr.b1", "relation": "RELATED", "note": "excluded"},
    ])


def test_build_domain_graph_excludes_other_domains_and_relations():
    graph = build_domain_graph(_nodes(), _edges(), "sr", RELATIONS)

    assert graph.concept_ids == ("sr.a1", "sr.a2", "sr.b1", "sr.b2")
    assert len(graph.edges) == 4
    assert {edge.relation for edge in graph.edges} == set(RELATIONS)
    assert "math.x" not in graph.labels


def test_analyse_partition_counts_boundaries_and_reports_quotient_cycle():
    graph = build_domain_graph(_nodes(), _edges(), "sr", RELATIONS)
    candidate = analyse_partition(
        graph,
        {
            "sr.a1": 0,
            "sr.a2": 0,
            "sr.b1": 1,
            "sr.b2": 1,
        },
        origin="test",
    )

    assert candidate.module_sizes == (2, 2)
    assert candidate.internal_edge_count == 2
    assert candidate.boundary_edge_count == 2
    assert candidate.boundary_relation_counts == {
        "DERIVES_FROM": 1,
        "REQUIRES": 1,
    }
    assert candidate.is_dag is False
    assert candidate.quotient_cycles == ((0, 1),)
    assert [
        (pair.source_module, pair.target_module, pair.edge_count)
        for pair in candidate.boundary_pairs
    ] == [(0, 1, 1), (1, 0, 1)]
    assert {
        (edge.source, edge.target)
        for edge in candidate.cycle_boundary_edges
    } == {
        ("sr.a1", "sr.b2"),
        ("sr.b1", "sr.a2"),
    }


def test_search_is_deterministic_and_respects_requested_size_bounds():
    nodes = pd.DataFrame([
        {
            "id": f"sr.n{index}",
            "display_id": f"1.{index}",
            "label": f"Node {index}",
            "domain": "sr",
        }
        for index in range(1, 9)
    ])
    edges = pd.DataFrame([
        {
            "source": f"sr.n{index + 1}",
            "target": f"sr.n{index}",
            "relation": "REQUIRES",
            "note": "",
        }
        for index in range(1, 8)
    ])
    graph = build_domain_graph(nodes, edges, "sr", RELATIONS)
    config = PartitionSearchConfig(
        module_counts=(2,),
        min_module_size=3,
        max_module_size=5,
        restarts=6,
        random_seed=19,
        candidates_per_count=4,
    )

    first = search_module_partitions(graph, config)
    second = search_module_partitions(graph, config)

    assert first == second
    assert first
    assert all(candidate.module_count == 2 for candidate in first)
    assert all(min(candidate.module_sizes) >= 3 for candidate in first)
    assert all(max(candidate.module_sizes) <= 5 for candidate in first)
    assert any(candidate.is_dag for candidate in first)


def test_report_exposes_metrics_membership_and_cycle_causes():
    graph = build_domain_graph(_nodes(), _edges(), "sr", RELATIONS)
    candidate = analyse_partition(
        graph,
        {"sr.a1": 0, "sr.a2": 0, "sr.b1": 1, "sr.b2": 1},
        origin="test seed",
    )

    report = format_partition_report(graph, [candidate], include_boundary_edges=True)

    assert "SR module partition candidates" in report
    assert "Boundary edges: 2 of 4" in report
    assert "Quotient DAG: no" in report
    assert "M1 -> M2: 1" in report
    assert "A one REQUIRES B two" in report
    assert "A one" in report
    assert "B one DERIVES_FROM A two" in report


def test_proposed_sr_partition_is_complete_cohesive_and_acyclic():
    root = Path(__file__).resolve().parents[1]
    nodes = pd.read_csv(root / "data" / "nodes.csv").fillna("")
    edges = pd.read_csv(root / "data" / "edges.csv").fillna("")
    members = pd.read_csv(
        root / "tests" / "fixtures" / "module_partitions" / "sr.csv"
    ).fillna("")
    graph = build_domain_graph(nodes, edges, "sr", RELATIONS)
    assignment = dict(zip(members["concept_id"], members["module_id"]))

    candidate = analyse_partition(graph, assignment, origin="editorial proposal")

    assert candidate.module_count == 5
    assert candidate.module_sizes == (11, 6, 9, 13, 8)
    assert candidate.internal_edge_count == 60
    assert candidate.boundary_edge_count == 28
    assert candidate.is_dag is True


def test_proposed_gr_partition_is_complete_cohesive_and_acyclic():
    root = Path(__file__).resolve().parents[1]
    nodes = pd.read_csv(root / "data" / "nodes.csv").fillna("")
    edges = pd.read_csv(root / "data" / "edges.csv").fillna("")
    members = pd.read_csv(
        root / "tests" / "fixtures" / "module_partitions" / "gr.csv"
    ).fillna("")
    graph = build_domain_graph(nodes, edges, "gr", RELATIONS)
    assignment = dict(zip(members["concept_id"], members["module_id"]))

    candidate = analyse_partition(graph, assignment, origin="editorial proposal")

    assert candidate.module_count == 6
    assert sorted(candidate.module_sizes) == [6, 6, 7, 10, 12, 14]
    # The Schwarzschild chart is a prerequisite of its coordinate-failure example.
    assert candidate.internal_edge_count == 53
    assert candidate.boundary_edge_count == 28
    assert candidate.boundary_relation_counts == {
        "CONSTRUCTED_FROM": 8,
        "DERIVES_FROM": 10,
        "REQUIRES": 10,
    }
    assert candidate.is_dag is True
