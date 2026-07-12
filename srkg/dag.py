"""DAG diagnostics for directed edge relations.

The graph stores directed relation edges as ``source -> target``. This module
checks directed relation subgraphs for cycles and summarizes their layer
structure without depending on rendering code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import networkx as nx
import pandas as pd

from srkg.data import (
    find_edge_key_path,
    load_edge_key,
    normalise_edges,
    validate_edge_endpoints,
)
from srkg.layout import concept_sort_key, parse_layer_value


@dataclass(frozen=True)
class DagEdge:
    """A labelled edge in a directed relation subgraph."""

    source: str
    source_label: str
    source_layer: int
    target: str
    target_label: str
    target_layer: int
    relation: str


@dataclass(frozen=True)
class DagRename:
    """A proposed node ID change inside one pedagogical layer."""

    old_id: str
    new_id: str
    label: str


@dataclass(frozen=True)
class LayerRenumbering:
    """A target-first order and the ID changes it implies for one layer."""

    layer: int
    current_order: tuple[str, ...]
    proposed_order: tuple[str, ...]
    renames: tuple[DagRename, ...]
    resolved_violation_count: int
    remaining_order_violations: tuple[DagEdge, ...]


@dataclass(frozen=True)
class TransitiveRedundancy:
    """A direct edge that is also implied by a longer path."""

    edge: DagEdge
    path: tuple[str, ...]
    path_labels: tuple[str, ...]


@dataclass(frozen=True)
class DagReport:
    """Cycle and layer diagnostics for one relation group."""

    name: str
    relations: tuple[str, ...]
    node_count: int
    edge_count: int
    is_dag: bool
    cycles: tuple[tuple[DagEdge, ...], ...]
    layer_forward_edges: tuple[DagEdge, ...]
    same_layer_edges: tuple[DagEdge, ...]
    same_layer_order_violations: tuple[DagEdge, ...]
    transitive_redundancies: tuple[TransitiveRedundancy, ...]
    layer_renumberings: tuple[LayerRenumbering, ...]
    foundation_nodes: tuple[str, ...]
    capstone_nodes: tuple[str, ...]
    longest_chain: tuple[str, ...]


def load_dag_reports(
    nodes_path: str | Path,
    edges_path: str | Path,
    relations: Sequence[str] | None = None,
    edge_key_path: str | Path | None = None,
) -> list[DagReport]:
    """Load CSV files and build DAG diagnostics for the selected relations."""
    edges_file = Path(edges_path)
    nodes_df = pd.read_csv(nodes_path).fillna("")
    edges_df = pd.read_csv(edges_file).fillna("")

    edges_df = normalise_edges(edges_df)
    nodes_df["id"] = nodes_df["id"].astype(str)
    edges_df["source"] = edges_df["source"].astype(str)
    edges_df["target"] = edges_df["target"].astype(str)
    edges_df["relation"] = edges_df["relation"].astype(str)

    validate_edge_endpoints(nodes_df, edges_df)

    edge_key_file = find_edge_key_path(edges_file, str(edge_key_path) if edge_key_path else None)
    edge_key = load_edge_key(edge_key_file)
    selected_relations = tuple(relations) if relations is not None else _directed_relations(edges_df, edge_key)

    if not selected_relations:
        raise ValueError(
            "No directed relations were found for DAG diagnostics. "
            "Check edges_key.csv or pass --dag-relations explicitly."
        )

    return build_dag_reports(nodes_df, edges_df, selected_relations)


def build_dag_reports(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    relations: Sequence[str],
) -> list[DagReport]:
    """Build per-relation and combined DAG diagnostics."""
    selected_relations = tuple(dict.fromkeys(str(relation) for relation in relations if str(relation)))
    reports = [
        analyse_relation_group(nodes_df, edges_df, (relation,), relation)
        for relation in selected_relations
    ]
    if len(selected_relations) > 1:
        reports.append(
            analyse_relation_group(
                nodes_df,
                edges_df,
                selected_relations,
                "+".join(selected_relations),
            )
        )
    return reports


def _directed_relations(
    edges_df: pd.DataFrame,
    edge_key: dict[str, dict[str, str | bool]],
) -> tuple[str, ...]:
    """Return relation names that should be treated as directed."""
    edge_relations = list(dict.fromkeys(edges_df["relation"].astype(str)))
    relations = []
    for relation, metadata in edge_key.items():
        if relation in edge_relations and bool(metadata.get("directed", True)):
            relations.append(relation)
    for relation in edge_relations:
        if relation in relations:
            continue
        if bool(edge_key.get(relation, {}).get("directed", True)):
            relations.append(relation)
    return tuple(relations)


def analyse_relation_group(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    relations: Sequence[str],
    name: str,
) -> DagReport:
    """Analyze one relation group as a directed graph."""
    node_metadata = _node_metadata(nodes_df)
    relation_set = set(relations)
    selected_edges = edges_df[edges_df["relation"].isin(relation_set)]

    graph = nx.DiGraph()
    edge_lookup: dict[tuple[str, str], DagEdge] = {}
    for row in selected_edges.itertuples(index=False):
        source = str(row.source)
        target = str(row.target)
        relation = str(row.relation)
        graph.add_node(source)
        graph.add_node(target)
        graph.add_edge(source, target, relation=relation)
        edge_lookup[(source, target)] = _make_dag_edge(source, target, relation, node_metadata)

    cycles = tuple(
        _cycle_edges(cycle, edge_lookup)
        for cycle in sorted(nx.simple_cycles(graph), key=lambda item: (len(item), item))
    )
    is_dag = nx.is_directed_acyclic_graph(graph)

    all_edges = tuple(edge_lookup[key] for key in sorted(edge_lookup, key=_edge_sort_key))
    layer_forward_edges = tuple(
        edge for edge in all_edges if edge.source_layer < edge.target_layer
    )
    same_layer_edges = tuple(
        edge for edge in all_edges if edge.source_layer == edge.target_layer
    )
    same_layer_order_violations = tuple(
        edge
        for edge in same_layer_edges
        if concept_sort_key(edge.source) < concept_sort_key(edge.target)
    )
    layer_renumberings = _build_layer_renumberings(
        nodes_df,
        same_layer_edges,
        same_layer_order_violations,
        node_metadata,
    )
    transitive_redundancies = _find_transitive_redundancies(graph, all_edges, node_metadata)

    foundation_nodes = tuple(
        sorted(
            (node for node in graph.nodes if graph.out_degree(node) == 0),
            key=concept_sort_key,
        )
    )
    capstone_nodes = tuple(
        sorted(
            (node for node in graph.nodes if graph.in_degree(node) == 0),
            key=concept_sort_key,
        )
    )

    longest_chain = ()
    if is_dag and graph.number_of_edges() > 0:
        longest_chain = tuple(nx.dag_longest_path(graph, topo_order=list(nx.topological_sort(graph))))

    return DagReport(
        name=name,
        relations=tuple(relations),
        node_count=graph.number_of_nodes(),
        edge_count=graph.number_of_edges(),
        is_dag=is_dag,
        cycles=cycles,
        layer_forward_edges=layer_forward_edges,
        same_layer_edges=same_layer_edges,
        same_layer_order_violations=same_layer_order_violations,
        transitive_redundancies=transitive_redundancies,
        layer_renumberings=layer_renumberings,
        foundation_nodes=foundation_nodes,
        capstone_nodes=capstone_nodes,
        longest_chain=longest_chain,
    )


def format_dag_reports(
    reports: Iterable[DagReport],
    *,
    max_items: int = 12,
) -> str:
    """Format DAG reports for command-line output."""
    lines = [
        "DAG diagnostics",
        "Edge direction is source -> target.",
    ]
    for report in reports:
        lines.append("")
        lines.append(
            f"{report.name}: nodes={report.node_count}, edges={report.edge_count}, "
            f"dag={'yes' if report.is_dag else 'no'}, cycles={len(report.cycles)}"
        )

        if report.cycles:
            lines.append("  Cycles:")
            for cycle in report.cycles[:max_items]:
                lines.append(f"    {_format_edge_chain(cycle)}")
            if len(report.cycles) > max_items:
                lines.append(f"    ... {len(report.cycles) - max_items} more")

        lines.append(
            "  Layer-forward directed edges "
            f"(source layer < target layer): {len(report.layer_forward_edges)}"
        )
        for edge in report.layer_forward_edges[:max_items]:
            lines.append(f"    {_format_edge(edge)}")
        if len(report.layer_forward_edges) > max_items:
            lines.append(f"    ... {len(report.layer_forward_edges) - max_items} more")

        lines.append(f"  Same-layer directed edges: {len(report.same_layer_edges)}")
        for edge in report.same_layer_edges[:max_items]:
            lines.append(f"    {_format_edge(edge)}")
        if len(report.same_layer_edges) > max_items:
            lines.append(f"    ... {len(report.same_layer_edges) - max_items} more")

        lines.append(
            "  Same-layer order violations "
            f"(lower-numbered source points to higher-numbered target): "
            f"{len(report.same_layer_order_violations)}"
        )
        for edge in report.same_layer_order_violations[:max_items]:
            lines.append(f"    {_format_edge(edge)}")
        if len(report.same_layer_order_violations) > max_items:
            lines.append(f"    ... {len(report.same_layer_order_violations) - max_items} more")

        lines.append(
            "  Transitively redundant direct edges "
            f"(A -> C also has A -> ... -> C): {len(report.transitive_redundancies)}"
        )
        for redundancy in report.transitive_redundancies[:max_items]:
            lines.append(f"    {_format_edge(redundancy.edge)}")
            lines.append(f"      via {_format_path(redundancy.path, redundancy.path_labels)}")
        if len(report.transitive_redundancies) > max_items:
            lines.append(f"    ... {len(report.transitive_redundancies) - max_items} more")

        if report.layer_renumberings:
            lines.append("  Suggested target-first renumbering within affected layers:")
            for renumbering in report.layer_renumberings[:max_items]:
                lines.append(
                    f"    Layer {renumbering.layer} "
                    f"(resolves {renumbering.resolved_violation_count} current violations):"
                )
                for rename in renumbering.renames:
                    lines.append(
                        f"      {rename.old_id} {rename.label} -> {rename.new_id}"
                    )
                lines.append(
                    "      Remaining forward references after proposed renumbering: "
                    f"{len(renumbering.remaining_order_violations)}"
                )
                for edge in renumbering.remaining_order_violations[:max_items]:
                    lines.append(f"        {_format_edge(edge)}")
                if len(renumbering.remaining_order_violations) > max_items:
                    lines.append(
                        f"        ... {len(renumbering.remaining_order_violations) - max_items} more"
                    )
            if len(report.layer_renumberings) > max_items:
                lines.append(f"    ... {len(report.layer_renumberings) - max_items} more layers")

        if report.longest_chain:
            lines.append(f"  Longest source -> target chain: {' -> '.join(report.longest_chain)}")
        lines.append(f"  Foundations (out-degree 0): {_format_node_list(report.foundation_nodes, max_items)}")
        lines.append(f"  Capstones (in-degree 0): {_format_node_list(report.capstone_nodes, max_items)}")

    return "\n".join(lines)


def _node_metadata(nodes_df: pd.DataFrame) -> dict[str, tuple[str, int]]:
    metadata = {}
    for row in nodes_df.itertuples(index=False):
        node_id = str(row.id)
        label = str(getattr(row, "label", "")).strip()
        layer = parse_layer_value(node_id, getattr(row, "layer", ""))
        metadata[node_id] = (label, layer)
    return metadata


def _build_layer_renumberings(
    nodes_df: pd.DataFrame,
    same_layer_edges: Sequence[DagEdge],
    same_layer_order_violations: Sequence[DagEdge],
    node_metadata: dict[str, tuple[str, int]],
) -> tuple[LayerRenumbering, ...]:
    """Suggest target-first IDs for layers with same-layer order violations."""
    violation_count_by_layer: dict[int, int] = {}
    for edge in same_layer_order_violations:
        violation_count_by_layer[edge.source_layer] = (
            violation_count_by_layer.get(edge.source_layer, 0) + 1
        )
    if not violation_count_by_layer:
        return ()

    nodes_by_layer: dict[int, list[str]] = {}
    for row in nodes_df.itertuples(index=False):
        node_id = str(row.id)
        _, layer = node_metadata.get(node_id, ("", 0))
        if layer in violation_count_by_layer:
            nodes_by_layer.setdefault(layer, []).append(node_id)

    edges_by_layer: dict[int, list[DagEdge]] = {}
    for edge in same_layer_edges:
        if edge.source_layer in violation_count_by_layer:
            edges_by_layer.setdefault(edge.source_layer, []).append(edge)

    suggestions = []
    for layer in sorted(violation_count_by_layer):
        current_order = tuple(sorted(nodes_by_layer.get(layer, []), key=concept_sort_key))
        dependency_first_graph = nx.DiGraph()
        dependency_first_graph.add_nodes_from(current_order)
        for edge in edges_by_layer.get(layer, []):
            dependency_first_graph.add_edge(edge.target, edge.source)

        if nx.is_directed_acyclic_graph(dependency_first_graph):
            proposed_order = tuple(_best_topological_order(dependency_first_graph, current_order, layer))
        else:
            proposed_order = current_order

        renames = []
        for index, node_id in enumerate(proposed_order, start=1):
            new_id = f"{layer}.{index}"
            if node_id == new_id:
                continue
            label, _ = node_metadata.get(node_id, ("", layer))
            renames.append(DagRename(old_id=node_id, new_id=new_id, label=label))

        proposed_index = {node_id: index for index, node_id in enumerate(proposed_order)}
        remaining_order_violations = tuple(
            edge
            for edge in edges_by_layer.get(layer, [])
            if proposed_index.get(edge.source, 0) < proposed_index.get(edge.target, 0)
        )

        suggestions.append(
            LayerRenumbering(
                layer=layer,
                current_order=current_order,
                proposed_order=proposed_order,
                renames=tuple(renames),
                resolved_violation_count=violation_count_by_layer[layer],
                remaining_order_violations=remaining_order_violations,
            )
        )

    return tuple(suggestions)


def _best_topological_order(graph: nx.DiGraph, current_order: Sequence[str], layer: int) -> list[str]:
    """Find a target-first order that minimizes ID churn for small layers."""
    if len(current_order) <= 8:
        best_order = None
        best_score = None
        for candidate in nx.all_topological_sorts(graph):
            score = _renumbering_score(candidate, current_order, layer)
            if best_score is None or score < best_score:
                best_score = score
                best_order = candidate
        if best_order is not None:
            return list(best_order)

    return _stable_topological_order(graph, current_order)


def _renumbering_score(candidate: Sequence[str], current_order: Sequence[str], layer: int):
    """Score lower for less disruptive proposed IDs."""
    current_index = {node_id: index for index, node_id in enumerate(current_order)}
    fixed_count = 0
    movement = 0
    candidate_indices = []

    for new_index, node_id in enumerate(candidate):
        new_suffix = new_index + 1
        if node_id == f"{layer}.{new_suffix}":
            fixed_count += 1
        old_suffix = _node_suffix(node_id)
        if old_suffix is None:
            old_suffix = current_index.get(node_id, new_index) + 1
        movement += abs(old_suffix - new_suffix)
        candidate_indices.append(current_index.get(node_id, len(current_order)))

    inversions = 0
    for left_index, left_value in enumerate(candidate_indices):
        for right_value in candidate_indices[left_index + 1:]:
            if left_value > right_value:
                inversions += 1

    return (-fixed_count, movement, inversions, tuple(candidate_indices))


def _node_suffix(node_id: str) -> int | None:
    try:
        return int(str(node_id).split(".", 1)[1])
    except Exception:
        return None


def _stable_topological_order(graph: nx.DiGraph, current_order: Sequence[str]) -> list[str]:
    """Topologically sort greedily while preserving current numeric order."""
    order_index = {node_id: index for index, node_id in enumerate(current_order)}
    in_degree = {node_id: graph.in_degree(node_id) for node_id in graph.nodes}
    ready = sorted(
        (node_id for node_id, degree in in_degree.items() if degree == 0),
        key=lambda node_id: order_index.get(node_id, len(order_index)),
    )
    result = []

    while ready:
        node_id = ready.pop(0)
        result.append(node_id)
        for successor in sorted(
            graph.successors(node_id),
            key=lambda item: order_index.get(item, len(order_index)),
        ):
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                ready.append(successor)
        ready.sort(key=lambda item: order_index.get(item, len(order_index)))

    return result


def _make_dag_edge(
    source: str,
    target: str,
    relation: str,
    node_metadata: dict[str, tuple[str, int]],
) -> DagEdge:
    source_label, source_layer = node_metadata.get(source, ("", 0))
    target_label, target_layer = node_metadata.get(target, ("", 0))
    return DagEdge(
        source=source,
        source_label=source_label,
        source_layer=source_layer,
        target=target,
        target_label=target_label,
        target_layer=target_layer,
        relation=relation,
    )


def _find_transitive_redundancies(
    graph: nx.DiGraph,
    all_edges: Sequence[DagEdge],
    node_metadata: dict[str, tuple[str, int]],
) -> tuple[TransitiveRedundancy, ...]:
    """Find direct edges whose reachability is preserved by an alternate path."""
    redundancies = []
    for edge in all_edges:
        edge_data = dict(graph.get_edge_data(edge.source, edge.target) or {})
        graph.remove_edge(edge.source, edge.target)
        if nx.has_path(graph, edge.source, edge.target):
            path = tuple(nx.shortest_path(graph, edge.source, edge.target))
            redundancies.append(
                TransitiveRedundancy(
                    edge=edge,
                    path=path,
                    path_labels=tuple(node_metadata.get(node_id, ("", 0))[0] for node_id in path),
                )
            )
        graph.add_edge(edge.source, edge.target, **edge_data)

    return tuple(
        sorted(
            redundancies,
            key=lambda item: (
                concept_sort_key(item.edge.source),
                concept_sort_key(item.edge.target),
                item.edge.relation,
            ),
        )
    )


def _cycle_edges(
    cycle: list[str],
    edge_lookup: dict[tuple[str, str], DagEdge],
) -> tuple[DagEdge, ...]:
    path = cycle + [cycle[0]]
    return tuple(edge_lookup[(source, target)] for source, target in zip(path, path[1:]))


def _edge_sort_key(edge_key: tuple[str, str]):
    source, target = edge_key
    return (concept_sort_key(source), concept_sort_key(target))


def _format_edge(edge: DagEdge) -> str:
    return (
        f"{edge.source} {edge.source_label} [L{edge.source_layer}] "
        f"{edge.relation} {edge.target} {edge.target_label} [L{edge.target_layer}]"
    )


def _format_edge_chain(edges: Sequence[DagEdge]) -> str:
    if not edges:
        return ""
    parts = [f"{edge.source} {edge.relation} {edge.target}" for edge in edges]
    return " | ".join(parts)


def _format_path(path: Sequence[str], labels: Sequence[str]) -> str:
    return " -> ".join(
        f"{node_id} {label}".rstrip()
        for node_id, label in zip(path, labels)
    )


def _format_node_list(nodes: Sequence[str], max_items: int) -> str:
    if not nodes:
        return "(none)"
    shown = ", ".join(nodes[:max_items])
    if len(nodes) > max_items:
        return f"{shown}, ... {len(nodes) - max_items} more"
    return shown
