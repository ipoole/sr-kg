"""Candidate generation and diagnostics for authored concept modules.

This module is an authoring aid.  It proposes and compares partitions but never
changes the knowledge-base module files.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random
from typing import Hashable, Mapping, Sequence

import networkx as nx
import pandas as pd

from srkg.layout import concept_sort_key


DEFAULT_RELATIONS = ("REQUIRES", "DERIVES_FROM", "CONSTRUCTED_FROM")


@dataclass(frozen=True)
class PartitionEdge:
    source: str
    target: str
    relation: str
    weight: float


@dataclass(frozen=True)
class DomainGraph:
    domain: str
    relations: tuple[str, ...]
    concept_ids: tuple[str, ...]
    labels: dict[str, str]
    display_ids: dict[str, str]
    edges: tuple[PartitionEdge, ...]


@dataclass(frozen=True)
class PartitionBoundaryPair:
    source_module: int
    target_module: int
    edges: tuple[PartitionEdge, ...]
    relation_counts: dict[str, int]

    @property
    def edge_count(self) -> int:
        return len(self.edges)


@dataclass(frozen=True)
class PartitionCandidate:
    origin: str
    modules: tuple[tuple[str, ...], ...]
    module_sizes: tuple[int, ...]
    internal_edge_count: int
    boundary_edge_count: int
    boundary_relation_counts: dict[str, int]
    weighted_boundary: float
    modularity: float
    boundary_pairs: tuple[PartitionBoundaryPair, ...]
    is_dag: bool
    quotient_cycles: tuple[tuple[int, ...], ...]
    cycle_boundary_edges: tuple[PartitionEdge, ...]

    @property
    def module_count(self) -> int:
        return len(self.modules)

    @property
    def assignment(self) -> dict[str, int]:
        return {
            concept_id: module_index
            for module_index, members in enumerate(self.modules)
            for concept_id in members
        }


@dataclass(frozen=True)
class PartitionSearchConfig:
    module_counts: tuple[int, ...]
    min_module_size: int = 3
    max_module_size: int = 20
    restarts: int = 8
    random_seed: int = 0
    candidates_per_count: int = 5
    cycle_penalties: tuple[float, ...] = (0.0, 8.0, 1000.0)
    balance_weight: float = 0.05


def build_domain_graph(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    domain: str,
    relations: Sequence[str] = DEFAULT_RELATIONS,
    relation_weights: Mapping[str, float] | None = None,
) -> DomainGraph:
    """Restrict concepts and selected edges to one owning domain."""
    relation_names = tuple(dict.fromkeys(str(value) for value in relations))
    weights = {relation: 1.0 for relation in relation_names}
    if relation_weights:
        weights.update({str(key): float(value) for key, value in relation_weights.items()})

    selected_nodes = nodes_df[nodes_df["domain"].astype(str) == str(domain)].copy()
    if selected_nodes.empty:
        raise ValueError(f"Domain {domain!r} has no concepts")
    selected_nodes["id"] = selected_nodes["id"].astype(str)
    selected_nodes["display_id"] = selected_nodes.get("display_id", "").astype(str)
    selected_nodes["label"] = selected_nodes.get("label", "").astype(str)
    labels = dict(zip(selected_nodes["id"], selected_nodes["label"]))
    display_ids = dict(zip(selected_nodes["id"], selected_nodes["display_id"]))
    concept_ids = tuple(sorted(
        labels,
        key=lambda concept_id: (
            concept_sort_key(display_ids.get(concept_id, concept_id)),
            concept_id,
        ),
    ))
    concept_set = set(concept_ids)

    edges: list[PartitionEdge] = []
    for row in edges_df.itertuples(index=False):
        source = str(row.source)
        target = str(row.target)
        relation = str(row.relation)
        if relation not in weights or source not in concept_set or target not in concept_set:
            continue
        edges.append(PartitionEdge(source, target, relation, weights[relation]))
    edges.sort(key=lambda edge: (edge.source, edge.target, edge.relation))
    return DomainGraph(
        domain=str(domain),
        relations=relation_names,
        concept_ids=concept_ids,
        labels=labels,
        display_ids=display_ids,
        edges=tuple(edges),
    )


def analyse_partition(
    graph: DomainGraph,
    assignment: Mapping[str, Hashable],
    *,
    origin: str,
) -> PartitionCandidate:
    """Measure cohesion and quotient cycles for one complete partition."""
    missing = sorted(set(graph.concept_ids) - set(assignment))
    extra = sorted(set(assignment) - set(graph.concept_ids))
    if missing or extra:
        raise ValueError(f"Partition coverage mismatch: missing={missing}, extra={extra}")

    grouped: dict[Hashable, list[str]] = {}
    for concept_id in graph.concept_ids:
        grouped.setdefault(assignment[concept_id], []).append(concept_id)
    ordered_groups = sorted(
        grouped.values(),
        key=lambda members: min(graph.concept_ids.index(member) for member in members),
    )
    modules = tuple(tuple(members) for members in ordered_groups)
    canonical_assignment = {
        concept_id: module_index
        for module_index, members in enumerate(modules)
        for concept_id in members
    }

    internal_count = 0
    boundary_edges: list[PartitionEdge] = []
    boundary_counts: Counter[str] = Counter()
    weighted_boundary = 0.0
    quotient = nx.DiGraph()
    quotient.add_nodes_from(range(len(modules)))
    for edge in graph.edges:
        source_module = canonical_assignment[edge.source]
        target_module = canonical_assignment[edge.target]
        if source_module == target_module:
            internal_count += 1
            continue
        boundary_edges.append(edge)
        boundary_counts[edge.relation] += 1
        weighted_boundary += edge.weight
        quotient.add_edge(source_module, target_module)

    cycles = _canonical_cycles(quotient)
    cyclic_pairs = _cyclic_module_pairs(quotient)
    cycle_boundary_edges = tuple(
        edge
        for edge in boundary_edges
        if (
            canonical_assignment[edge.source],
            canonical_assignment[edge.target],
        ) in cyclic_pairs
    )
    return PartitionCandidate(
        origin=origin,
        modules=modules,
        module_sizes=tuple(len(members) for members in modules),
        internal_edge_count=internal_count,
        boundary_edge_count=len(boundary_edges),
        boundary_relation_counts=dict(sorted(boundary_counts.items())),
        weighted_boundary=weighted_boundary,
        modularity=_partition_modularity(graph, modules),
        boundary_pairs=_group_boundary_pairs(boundary_edges, canonical_assignment),
        is_dag=nx.is_directed_acyclic_graph(quotient),
        quotient_cycles=cycles,
        cycle_boundary_edges=cycle_boundary_edges,
    )


def search_module_partitions(
    graph: DomainGraph,
    config: PartitionSearchConfig,
    *,
    seed_partitions: Sequence[Mapping[str, Hashable]] = (),
) -> tuple[PartitionCandidate, ...]:
    """Search reproducibly for strong candidates at each requested module count."""
    if config.min_module_size < 1:
        raise ValueError("Minimum module size must be positive")
    if config.max_module_size < config.min_module_size:
        raise ValueError("Maximum module size must not be smaller than minimum size")
    if config.restarts < 0 or config.candidates_per_count < 1:
        raise ValueError("Restarts must be non-negative and candidates per count positive")

    all_candidates: list[PartitionCandidate] = []
    for module_count in config.module_counts:
        _validate_size_feasibility(len(graph.concept_ids), module_count, config)
        initial: list[tuple[str, dict[str, int]]] = []
        greedy = _greedy_modularity_assignment(graph, module_count)
        initial.append(("greedy modularity", greedy))
        initial.append(("topological strata", _topological_assignment(graph, module_count)))
        for index, seed_partition in enumerate(seed_partitions, start=1):
            coarsened = _coarsen_seed_partition(
                graph,
                seed_partition,
                module_count,
                config.max_module_size,
            )
            if coarsened is not None:
                initial.append((f"authored seed {index}", coarsened))

        rng = random.Random(config.random_seed + module_count * 1009)
        for restart in range(config.restarts):
            initial.append((
                f"balanced restart {restart + 1}",
                _random_balanced_assignment(graph, module_count, rng),
            ))

        found: dict[tuple[tuple[str, ...], ...], PartitionCandidate] = {}
        for origin, assignment in initial:
            rebalanced = _rebalance_assignment(graph, assignment, module_count, config)
            if rebalanced is None:
                continue
            for cycle_penalty in config.cycle_penalties:
                improved = _improve_assignment(
                    graph,
                    rebalanced,
                    config,
                    cycle_penalty=cycle_penalty,
                    rng=rng,
                )
                candidate = analyse_partition(
                    graph,
                    improved,
                    origin=f"{origin}; cycle penalty {cycle_penalty:g}",
                )
                if not _sizes_valid(candidate.module_sizes, config):
                    continue
                previous = found.get(candidate.modules)
                if previous is None or _candidate_rank(candidate) < _candidate_rank(previous):
                    found[candidate.modules] = candidate

        ranked = sorted(found.values(), key=_candidate_rank)
        all_candidates.extend(ranked[:config.candidates_per_count])
    return tuple(all_candidates)


def format_partition_report(
    graph: DomainGraph,
    candidates: Sequence[PartitionCandidate],
    *,
    include_boundary_edges: bool = False,
    max_edges_per_pair: int = 20,
) -> str:
    """Render metrics, memberships, and concrete cycle causes as Markdown."""
    title = graph.domain.upper()
    lines = [
        f"# {title} module partition candidates",
        "",
        f"Concepts: {len(graph.concept_ids)}",
        f"Selected edges: {len(graph.edges)}",
        f"Relations: {', '.join(graph.relations)}",
    ]
    if not candidates:
        return "\n".join(lines + ["", "No feasible candidates found."])

    for candidate_number, candidate in enumerate(candidates, start=1):
        lines.extend([
            "",
            f"## Candidate {candidate_number}: {candidate.module_count} modules",
            "",
            f"Origin: {candidate.origin}",
            f"Module sizes: {', '.join(str(size) for size in candidate.module_sizes)}",
            (
                f"Boundary edges: {candidate.boundary_edge_count} of {len(graph.edges)} "
                f"({candidate.boundary_edge_count / max(1, len(graph.edges)):.1%})"
            ),
            f"Boundary relations: {_format_counts(candidate.boundary_relation_counts)}",
            f"Weighted boundary: {candidate.weighted_boundary:.2f}",
            f"Modularity: {candidate.modularity:.3f}",
            f"Quotient DAG: {'yes' if candidate.is_dag else 'no'}",
            "Boundary module pairs:",
        ])
        for pair in candidate.boundary_pairs:
            lines.append(
                f"- M{pair.source_module + 1} -> M{pair.target_module + 1}: "
                f"{pair.edge_count} ({_format_counts(pair.relation_counts)})"
            )
            if include_boundary_edges:
                for edge in pair.edges[:max_edges_per_pair]:
                    lines.append(
                        f"  - {graph.labels[edge.source]} {edge.relation} "
                        f"{graph.labels[edge.target]}"
                    )
                if len(pair.edges) > max_edges_per_pair:
                    lines.append(
                        f"  - … {len(pair.edges) - max_edges_per_pair} more"
                    )
        if candidate.quotient_cycles:
            shown_cycles = candidate.quotient_cycles[:10]
            lines.append("Module cycles: " + "; ".join(
                " -> ".join(f"M{module + 1}" for module in cycle) + f" -> M{cycle[0] + 1}"
                for cycle in shown_cycles
            ))
            if len(candidate.quotient_cycles) > len(shown_cycles):
                lines.append(
                    f"Additional module cycles omitted: {len(candidate.quotient_cycles) - len(shown_cycles)}"
                )
            lines.append("Cycle-causing boundary edges:")
            shown_edges = candidate.cycle_boundary_edges[:20]
            for edge in shown_edges:
                lines.append(
                    f"- {graph.labels[edge.source]} {edge.relation} {graph.labels[edge.target]}"
                )
            if len(candidate.cycle_boundary_edges) > len(shown_edges):
                lines.append(
                    f"- … {len(candidate.cycle_boundary_edges) - len(shown_edges)} more"
                )

        for module_index, members in enumerate(candidate.modules, start=1):
            lines.extend(["", f"### M{module_index} ({len(members)} concepts)", ""])
            for concept_id in members:
                display_id = graph.display_ids.get(concept_id, "").strip()
                prefix = f"{display_id} " if display_id else ""
                lines.append(f"- `{concept_id}` — {prefix}{graph.labels[concept_id]}")

        exposed = _boundary_exposure(graph, candidate.assignment)
        if exposed:
            lines.extend(["", "Most boundary-exposed concepts:"])
            for concept_id, count in exposed[:8]:
                lines.append(f"- {graph.labels[concept_id]}: {count}")
    return "\n".join(lines)


def _weighted_graph(graph: DomainGraph) -> nx.Graph:
    result = nx.Graph()
    result.add_nodes_from(graph.concept_ids)
    for edge in graph.edges:
        current = result.get_edge_data(edge.source, edge.target, {}).get("weight", 0.0)
        result.add_edge(edge.source, edge.target, weight=current + edge.weight)
    return result


def _partition_modularity(graph: DomainGraph, modules: Sequence[Sequence[str]]) -> float:
    undirected = _weighted_graph(graph)
    if not undirected.number_of_edges():
        return 0.0
    return float(nx.community.modularity(
        undirected,
        [set(members) for members in modules],
        weight="weight",
    ))


def _group_boundary_pairs(
    edges: Sequence[PartitionEdge],
    assignment: Mapping[str, int],
) -> tuple[PartitionBoundaryPair, ...]:
    grouped: dict[tuple[int, int], list[PartitionEdge]] = {}
    for edge in edges:
        key = (assignment[edge.source], assignment[edge.target])
        grouped.setdefault(key, []).append(edge)
    pairs = []
    for (source_module, target_module), pair_edges in grouped.items():
        ordered = tuple(sorted(
            pair_edges,
            key=lambda edge: (edge.relation, edge.source, edge.target),
        ))
        pairs.append(PartitionBoundaryPair(
            source_module=source_module,
            target_module=target_module,
            edges=ordered,
            relation_counts=dict(sorted(Counter(edge.relation for edge in ordered).items())),
        ))
    return tuple(sorted(
        pairs,
        key=lambda pair: (-pair.edge_count, pair.source_module, pair.target_module),
    ))


def _canonical_cycles(graph: nx.DiGraph) -> tuple[tuple[int, ...], ...]:
    cycles = set()
    for cycle in nx.simple_cycles(graph):
        rotations = [tuple(cycle[index:] + cycle[:index]) for index in range(len(cycle))]
        cycles.add(min(rotations))
    return tuple(sorted(cycles, key=lambda cycle: (len(cycle), cycle)))


def _cyclic_module_pairs(graph: nx.DiGraph) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for component in nx.strongly_connected_components(graph):
        if len(component) < 2:
            continue
        pairs.update(
            (source, target)
            for source, target in graph.edges
            if source in component and target in component
        )
    return pairs


def _candidate_rank(candidate: PartitionCandidate) -> tuple:
    return (
        not candidate.is_dag,
        candidate.weighted_boundary,
        candidate.boundary_edge_count,
        -candidate.modularity,
        max(candidate.module_sizes) - min(candidate.module_sizes),
        candidate.modules,
    )


def _objective(
    graph: DomainGraph,
    assignment: Mapping[str, int],
    config: PartitionSearchConfig,
    cycle_penalty: float,
) -> tuple[float, float, tuple[int, ...]]:
    module_labels = sorted(set(assignment.values()))
    sizes = Counter(assignment.values())
    weighted_boundary = 0.0
    boundary_pairs = []
    for edge in graph.edges:
        source_module = assignment[edge.source]
        target_module = assignment[edge.target]
        if source_module == target_module:
            continue
        weighted_boundary += edge.weight
        boundary_pairs.append((source_module, target_module))
    cycle_severity = _fast_cycle_severity(module_labels, boundary_pairs) if cycle_penalty else 0
    mean_size = len(graph.concept_ids) / len(module_labels)
    imbalance = sum(abs(sizes[module] - mean_size) for module in module_labels)
    score = (
        weighted_boundary
        + cycle_penalty * cycle_severity
        + config.balance_weight * imbalance
    )
    signature = tuple(assignment[concept_id] for concept_id in graph.concept_ids)
    return score, weighted_boundary, signature


def _greedy_modularity_assignment(graph: DomainGraph, module_count: int) -> dict[str, int]:
    undirected = _weighted_graph(graph)
    if undirected.number_of_edges():
        communities = nx.community.greedy_modularity_communities(
            undirected,
            weight="weight",
            cutoff=module_count,
            best_n=module_count,
        )
        if len(communities) == module_count:
            return {
                concept_id: index
                for index, community in enumerate(communities)
                for concept_id in community
            }
    return _balanced_assignment(graph.concept_ids, module_count)


def _topological_assignment(graph: DomainGraph, module_count: int) -> dict[str, int]:
    directed = nx.DiGraph()
    directed.add_nodes_from(graph.concept_ids)
    directed.add_edges_from((edge.source, edge.target) for edge in graph.edges)
    if nx.is_directed_acyclic_graph(directed):
        ordered = list(nx.lexicographical_topological_sort(
            directed,
            key=lambda node: graph.concept_ids.index(node),
        ))
    else:
        ordered = list(graph.concept_ids)
    return _balanced_assignment(ordered, module_count)


def _balanced_assignment(nodes: Sequence[str], module_count: int) -> dict[str, int]:
    quotient, remainder = divmod(len(nodes), module_count)
    sizes = [quotient + (1 if index < remainder else 0) for index in range(module_count)]
    assignment = {}
    cursor = 0
    for module_index, size in enumerate(sizes):
        for concept_id in nodes[cursor:cursor + size]:
            assignment[concept_id] = module_index
        cursor += size
    return assignment


def _random_balanced_assignment(
    graph: DomainGraph,
    module_count: int,
    rng: random.Random,
) -> dict[str, int]:
    nodes = list(graph.concept_ids)
    rng.shuffle(nodes)
    return _balanced_assignment(nodes, module_count)


def _coarsen_seed_partition(
    graph: DomainGraph,
    seed: Mapping[str, Hashable],
    module_count: int,
    max_size: int,
) -> dict[str, int] | None:
    if set(seed) != set(graph.concept_ids):
        return None
    groups: dict[Hashable, set[str]] = {}
    for concept_id in graph.concept_ids:
        groups.setdefault(seed[concept_id], set()).add(concept_id)
    communities = list(groups.values())
    if len(communities) < module_count:
        return None
    while len(communities) > module_count:
        best = None
        for left in range(len(communities)):
            for right in range(left + 1, len(communities)):
                combined_size = len(communities[left]) + len(communities[right])
                if combined_size > max_size:
                    continue
                affinity = sum(
                    edge.weight
                    for edge in graph.edges
                    if (
                        edge.source in communities[left] and edge.target in communities[right]
                    ) or (
                        edge.source in communities[right] and edge.target in communities[left]
                    )
                )
                key = (-affinity, combined_size, left, right)
                if best is None or key < best[0]:
                    best = (key, left, right)
        if best is None:
            return None
        _, left, right = best
        communities[left] |= communities[right]
        communities.pop(right)
    return {
        concept_id: module_index
        for module_index, community in enumerate(communities)
        for concept_id in community
    }


def _rebalance_assignment(
    graph: DomainGraph,
    assignment: Mapping[str, int],
    module_count: int,
    config: PartitionSearchConfig,
) -> dict[str, int] | None:
    result = dict(assignment)
    if set(result) != set(graph.concept_ids) or len(set(result.values())) != module_count:
        return None
    labels = {old: new for new, old in enumerate(sorted(set(result.values()), key=str))}
    result = {node: labels[module] for node, module in result.items()}
    for _ in range(len(graph.concept_ids) * module_count):
        sizes = Counter(result.values())
        over = [module for module in range(module_count) if sizes[module] > config.max_module_size]
        under = [module for module in range(module_count) if sizes[module] < config.min_module_size]
        if not over and not under:
            return result
        donors = over or [module for module in range(module_count) if sizes[module] > config.min_module_size]
        targets = under or [module for module in range(module_count) if sizes[module] < config.max_module_size]
        moves = []
        for source_module in donors:
            for concept_id in graph.concept_ids:
                if result[concept_id] != source_module:
                    continue
                for target_module in targets:
                    if target_module == source_module or sizes[target_module] >= config.max_module_size:
                        continue
                    trial = dict(result)
                    trial[concept_id] = target_module
                    violation = _size_violation(Counter(trial.values()), module_count, config)
                    boundary = analyse_partition(graph, trial, origin="rebalance").weighted_boundary
                    moves.append((violation, boundary, concept_id, target_module, trial))
        if not moves:
            return None
        moves.sort(key=lambda item: item[:4])
        result = moves[0][4]
    return None


def _improve_assignment(
    graph: DomainGraph,
    assignment: Mapping[str, int],
    config: PartitionSearchConfig,
    *,
    cycle_penalty: float,
    rng: random.Random,
) -> dict[str, int]:
    result = dict(assignment)
    current = _objective(graph, result, config, cycle_penalty)
    module_count = len(set(result.values()))
    for _ in range(40):
        sizes = Counter(result.values())
        moves = []
        nodes = list(graph.concept_ids)
        rng.shuffle(nodes)
        for concept_id in nodes:
            source_module = result[concept_id]
            if sizes[source_module] <= config.min_module_size:
                continue
            targets = list(range(module_count))
            rng.shuffle(targets)
            for target_module in targets:
                if target_module == source_module or sizes[target_module] >= config.max_module_size:
                    continue
                trial = dict(result)
                trial[concept_id] = target_module
                objective = _objective(graph, trial, config, cycle_penalty)
                if objective < current:
                    moves.append((objective, concept_id, target_module, trial))
        if not moves:
            break
        moves.sort(key=lambda item: (item[0], item[1], item[2]))
        current, _, _, result = moves[0]
    return result


def _validate_size_feasibility(
    concept_count: int,
    module_count: int,
    config: PartitionSearchConfig,
) -> None:
    if module_count < 1:
        raise ValueError("Module counts must be positive")
    if concept_count < module_count * config.min_module_size:
        raise ValueError(
            f"{module_count} modules need at least "
            f"{module_count * config.min_module_size} concepts"
        )
    if concept_count > module_count * config.max_module_size:
        raise ValueError(
            f"{module_count} modules can contain at most "
            f"{module_count * config.max_module_size} concepts"
        )


def _sizes_valid(sizes: Sequence[int], config: PartitionSearchConfig) -> bool:
    return bool(sizes) and min(sizes) >= config.min_module_size and max(sizes) <= config.max_module_size


def _size_violation(
    sizes: Mapping[int, int],
    module_count: int,
    config: PartitionSearchConfig,
) -> int:
    return sum(
        max(0, config.min_module_size - sizes.get(module, 0))
        + max(0, sizes.get(module, 0) - config.max_module_size)
        for module in range(module_count)
    )


def _boundary_exposure(
    graph: DomainGraph,
    assignment: Mapping[str, int],
) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    for edge in graph.edges:
        if assignment[edge.source] != assignment[edge.target]:
            counts[edge.source] += 1
            counts[edge.target] += 1
    return sorted(
        counts.items(),
        key=lambda item: (-item[1], graph.concept_ids.index(item[0])),
    )


def _format_counts(counts: Mapping[str, int]) -> str:
    if not counts:
        return "(none)"
    return ", ".join(f"{key}: {value}" for key, value in sorted(counts.items()))


def _fast_cycle_severity(
    module_labels: Sequence[int],
    boundary_pairs: Sequence[tuple[int, int]],
) -> int:
    """Return a cheap gradient for cyclic quotient structure during search."""
    reachable = {module: {module} for module in module_labels}
    for source, target in boundary_pairs:
        reachable[source].add(target)
    for intermediate in module_labels:
        for source in module_labels:
            if intermediate in reachable[source]:
                reachable[source].update(reachable[intermediate])
    cyclic_modules = {
        source
        for source in module_labels
        if any(
            source != target
            and target in reachable[source]
            and source in reachable[target]
            for target in module_labels
        )
    }
    if not cyclic_modules:
        return 0
    cyclic_edges = sum(
        source in cyclic_modules and target in cyclic_modules
        for source, target in boundary_pairs
    )
    return len(cyclic_modules) + cyclic_edges
