from pathlib import Path
import pandas as pd
from srkg.module_partitioning import analyse_partition, build_domain_graph, format_partition_report
RELATIONS = ("REQUIRES", "DERIVES_FROM", "CONSTRUCTED_FROM")
DOMAIN_ROOT = Path(__file__).resolve().parents[1]


def test_proposed_sr_partition_is_complete_cohesive_and_acyclic():
    root = DOMAIN_ROOT.parents[1]
    from srkg.kb import load_knowledge_base
    kb = load_knowledge_base(root / "data", include_graphics=False)
    nodes, edges = kb.nodes_df, kb.edges_df
    members = pd.read_csv(
        DOMAIN_ROOT / "tests" / "module_partition.csv"
    ).fillna("")
    graph = build_domain_graph(nodes, edges, "sr", RELATIONS)
    assignment = dict(zip(members["concept_id"], members["module_id"]))

    candidate = analyse_partition(graph, assignment, origin="editorial proposal")

    assert candidate.module_count == 5
    assert candidate.module_sizes == (13, 6, 9, 13, 8)
    assert candidate.internal_edge_count == 70
    assert candidate.boundary_edge_count == 34  # Genuine field-variation and source prerequisites.
    assert candidate.is_dag is True
