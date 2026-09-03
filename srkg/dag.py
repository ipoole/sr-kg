"""Generic DAG diagnostics for directed concept and module relations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import networkx as nx
import pandas as pd

from srkg.data import load_edge_key, normalise_edges, validate_edge_endpoints
from srkg.layout import concept_sort_key


@dataclass(frozen=True)
class DagNodeMetadata:
    label: str
    display_id: str


@dataclass(frozen=True)
class DagEdge:
    source: str
    source_display_id: str
    source_label: str
    target: str
    target_display_id: str
    target_label: str
    relation: str


@dataclass(frozen=True)
class TransitiveRedundancy:
    edge: DagEdge
    path: tuple[str, ...]
    path_labels: tuple[str, ...]


@dataclass(frozen=True)
class DagReport:
    name: str
    relations: tuple[str, ...]
    node_count: int
    edge_count: int
    is_dag: bool
    cycles: tuple[tuple[DagEdge, ...], ...]
    transitive_redundancies: tuple[TransitiveRedundancy, ...]
    foundation_nodes: tuple[str, ...]
    capstone_nodes: tuple[str, ...]
    longest_chain: tuple[str, ...]


def load_dag_reports(
    nodes_path: str | Path,
    edges_path: str | Path,
    relations: Sequence[str] | None = None,
    edge_key_path: str | Path | None = None,
) -> list[DagReport]:
    """Load CSV files and build DAG diagnostics for selected relations."""
    nodes_df = pd.read_csv(nodes_path).fillna("")
    edges_df = normalise_edges(pd.read_csv(edges_path).fillna(""))
    nodes_df["id"] = nodes_df["id"].astype(str)
    for column in ("source", "target", "relation"):
        edges_df[column] = edges_df[column].astype(str)
    validate_edge_endpoints(nodes_df, edges_df)

    edge_key = load_edge_key(Path(edge_key_path) if edge_key_path else None)
    selected = tuple(relations) if relations is not None else _directed_relations(
        edges_df, edge_key
    )
    if not selected:
        raise ValueError(
            "No directed relations were found for DAG diagnostics. "
            "Check edges_key.csv or pass --dag-relations explicitly."
        )
    return build_dag_reports(nodes_df, edges_df, selected)


def build_dag_reports(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    relations: Sequence[str],
) -> list[DagReport]:
    """Build per-relation and combined DAG diagnostics."""
    selected = tuple(dict.fromkeys(str(value) for value in relations if str(value)))
    reports = [
        analyse_relation_group(nodes_df, edges_df, (relation,), relation)
        for relation in selected
    ]
    if len(selected) > 1:
        reports.append(
            analyse_relation_group(nodes_df, edges_df, selected, "+".join(selected))
        )
    return reports


def analyse_relation_group(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    relations: Sequence[str],
    name: str,
) -> DagReport:
    """Analyse one relation group without assuming a pedagogical partition."""
    metadata = _node_metadata(nodes_df)
    sort_keys = {
        node_id: concept_sort_key(value.display_id)
        for node_id, value in metadata.items()
    }
    selected_edges = edges_df[edges_df["relation"].isin(set(relations))]
    graph = nx.DiGraph()
    edge_lookup: dict[tuple[str, str], DagEdge] = {}
    for row in selected_edges.itertuples(index=False):
        source = str(row.source)
        target = str(row.target)
        relation = str(row.relation)
        graph.add_edge(source, target, relation=relation)
        edge_lookup[(source, target)] = _make_edge(source, target, relation, metadata)

    cycles = tuple(
        _cycle_edges(cycle, edge_lookup)
        for cycle in sorted(nx.simple_cycles(graph), key=lambda item: (len(item), item))
    )
    is_dag = nx.is_directed_acyclic_graph(graph)
    all_edges = tuple(
        edge_lookup[key]
        for key in sorted(
            edge_lookup,
            key=lambda pair: (
                sort_keys.get(pair[0], concept_sort_key(pair[0])),
                sort_keys.get(pair[1], concept_sort_key(pair[1])),
            ),
        )
    )
    redundancies = _find_transitive_redundancies(
        graph, all_edges, metadata, sort_keys
    )
    foundations = tuple(sorted(
        (node for node in graph.nodes if graph.out_degree(node) == 0),
        key=lambda node: sort_keys.get(node, concept_sort_key(node)),
    ))
    capstones = tuple(sorted(
        (node for node in graph.nodes if graph.in_degree(node) == 0),
        key=lambda node: sort_keys.get(node, concept_sort_key(node)),
    ))
    longest_chain: tuple[str, ...] = ()
    if is_dag and graph.number_of_edges() > 0:
        longest_chain = tuple(nx.dag_longest_path(graph))
    return DagReport(
        name=name,
        relations=tuple(relations),
        node_count=graph.number_of_nodes(),
        edge_count=graph.number_of_edges(),
        is_dag=is_dag,
        cycles=cycles,
        transitive_redundancies=redundancies,
        foundation_nodes=foundations,
        capstone_nodes=capstones,
        longest_chain=longest_chain,
    )


def format_dag_reports(
    reports: Iterable[DagReport],
    *,
    max_items: int = 12,
) -> str:
    """Format generic DAG reports for command-line output."""
    lines = ["DAG diagnostics", "Edge direction is source -> target."]
    for report in reports:
        lines.extend([
            "",
            f"{report.name}: nodes={report.node_count}, edges={report.edge_count}, "
            f"dag={'yes' if report.is_dag else 'no'}, cycles={len(report.cycles)}",
        ])
        if report.cycles:
            lines.append("  Cycles:")
            for cycle in report.cycles[:max_items]:
                lines.append("    " + " | ".join(
                    f"{edge.source_display_id} {edge.relation} {edge.target_display_id}"
                    for edge in cycle
                ))
        lines.append(
            "  Transitively redundant direct edges "
            f"(A -> C also has A -> ... -> C): {len(report.transitive_redundancies)}"
        )
        for redundancy in report.transitive_redundancies[:max_items]:
            lines.append(f"    {_format_edge(redundancy.edge)}")
            lines.append("      via " + " -> ".join(
                f"{node_id} {label}".rstrip()
                for node_id, label in zip(redundancy.path, redundancy.path_labels)
            ))
        if len(report.transitive_redundancies) > max_items:
            lines.append(
                f"    ... {len(report.transitive_redundancies) - max_items} more"
            )
        if report.longest_chain:
            lines.append(
                "  Longest source -> target chain: " + " -> ".join(report.longest_chain)
            )
        lines.append(
            "  Foundations (out-degree 0): "
            + _format_node_list(report.foundation_nodes, max_items)
        )
        lines.append(
            "  Capstones (in-degree 0): "
            + _format_node_list(report.capstone_nodes, max_items)
        )
    return "\n".join(lines)


def _directed_relations(edges_df, edge_key) -> tuple[str, ...]:
    edge_relations = list(dict.fromkeys(edges_df["relation"].astype(str)))
    return tuple(
        relation for relation in edge_relations
        if bool(edge_key.get(relation, {}).get("directed", True))
    )


def _node_metadata(nodes_df: pd.DataFrame) -> dict[str, DagNodeMetadata]:
    return {
        str(row.id): DagNodeMetadata(
            label=str(getattr(row, "label", "")).strip(),
            display_id=str(getattr(row, "display_id", "")).strip() or str(row.id),
        )
        for row in nodes_df.itertuples(index=False)
    }


def _make_edge(source, target, relation, metadata) -> DagEdge:
    source_meta = metadata.get(source, DagNodeMetadata("", source))
    target_meta = metadata.get(target, DagNodeMetadata("", target))
    return DagEdge(
        source=source,
        source_display_id=source_meta.display_id,
        source_label=source_meta.label,
        target=target,
        target_display_id=target_meta.display_id,
        target_label=target_meta.label,
        relation=relation,
    )


def _find_transitive_redundancies(graph, edges, metadata, sort_keys):
    redundancies = []
    for edge in edges:
        edge_data = dict(graph.get_edge_data(edge.source, edge.target) or {})
        graph.remove_edge(edge.source, edge.target)
        if nx.has_path(graph, edge.source, edge.target):
            path = tuple(nx.shortest_path(graph, edge.source, edge.target))
            redundancies.append(TransitiveRedundancy(
                edge=edge,
                path=path,
                path_labels=tuple(
                    metadata.get(node_id, DagNodeMetadata("", node_id)).label
                    for node_id in path
                ),
            ))
        graph.add_edge(edge.source, edge.target, **edge_data)
    return tuple(sorted(
        redundancies,
        key=lambda item: (
            sort_keys.get(item.edge.source, concept_sort_key(item.edge.source)),
            sort_keys.get(item.edge.target, concept_sort_key(item.edge.target)),
            item.edge.relation,
        ),
    ))


def _cycle_edges(cycle, edge_lookup):
    path = cycle + [cycle[0]]
    return tuple(edge_lookup[(source, target)] for source, target in zip(path, path[1:]))


def _format_edge(edge: DagEdge) -> str:
    return (
        f"{edge.source_display_id} {edge.source_label} "
        f"{edge.relation} {edge.target_display_id} {edge.target_label}"
    )


def _format_node_list(nodes: Sequence[str], max_items: int) -> str:
    if not nodes:
        return "(none)"
    shown = ", ".join(nodes[:max_items])
    if len(nodes) > max_items:
        shown += f", ... {len(nodes) - max_items} more"
    return shown
