"""Deterministic concept ordering and local layout within authored modules.

Structural knowledge edges point from a concept to something it depends on.
For teaching order and layout those edges are reversed, giving a graph from
fundamental concepts towards concepts derived from them.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable, Mapping, Sequence

import networkx as nx
import pandas as pd

from srkg.model import Module


STRUCTURAL_RELATIONS = frozenset(
    {"REQUIRES", "DERIVES_FROM", "CONSTRUCTED_FROM"}
)
_MODULE_CODE = re.compile(r"^(SR-\d+|GR-\d+|MATHS-\d+)(?:\s|$)")


@dataclass(frozen=True)
class ModuleLayoutResult:
    """Resolved local concept geometry and its dependency diagnostics."""

    positions: dict[str, tuple[float, float]]
    ranks: dict[str, int]
    ordered_members: dict[str, tuple[str, ...]]
    cycles: dict[str, tuple[tuple[str, ...], ...]]


@dataclass(frozen=True)
class ModuleAnchorLayoutResult:
    """Generated module-anchor geometry and dependency diagnostics."""

    anchors: dict[str, tuple[float, float]]
    ranks: dict[str, int]
    cycles: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class ConceptNumberingProposal:
    """One proposed module-based display identifier."""

    concept_id: str
    old_display_id: str
    new_display_id: str
    module_id: str
    module_title: str
    dependency_rank: int
    member_sequence: int
    rationale: str


@dataclass(frozen=True)
class _ModuleOrder:
    ranks: dict[str, int]
    ordered_members: tuple[str, ...]
    cycles: tuple[tuple[str, ...], ...]


def build_generated_module_anchors(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    modules: Iterable[Module],
    *,
    structural_relations: Sequence[str] = tuple(sorted(STRUCTURAL_RELATIONS)),
    x_spacing: float = 3300.0,
    y_spacing: float = 2700.0,
) -> ModuleAnchorLayoutResult:
    """Generate deterministic module anchors from the structural module DAG."""
    if not math.isfinite(float(x_spacing)) or float(x_spacing) <= 0:
        raise ValueError("x_spacing must be a positive finite number")
    if not math.isfinite(float(y_spacing)) or float(y_spacing) <= 0:
        raise ValueError("y_spacing must be a positive finite number")
    module_list = tuple(modules)
    _validate_members(nodes_df, module_list)
    module_by_concept = {
        concept_id: module.module_id
        for module in module_list
        for concept_id in map(str, module.members)
    }
    module_index = {
        module.module_id: index
        for index, module in enumerate(
            sorted(module_list, key=lambda item: (item.domain, item.sequence, item.module_id))
        )
    }
    dependency_graph = nx.DiGraph()
    dependency_graph.add_nodes_from(module.module_id for module in module_list)
    relations = {str(value) for value in structural_relations}
    for row in edges_df.itertuples(index=False):
        if str(row.relation) not in relations:
            continue
        source_module = module_by_concept.get(str(row.source))
        target_module = module_by_concept.get(str(row.target))
        if source_module and target_module and source_module != target_module:
            dependency_graph.add_edge(target_module, source_module)

    components = sorted(
        (
            tuple(sorted(component, key=lambda value: (module_index[value], value)))
            for component in nx.strongly_connected_components(dependency_graph)
        ),
        key=lambda component: (min(module_index[value] for value in component), component),
    )
    component_by_module = {
        module_id: component_index
        for component_index, component in enumerate(components)
        for module_id in component
    }
    condensed = nx.DiGraph()
    condensed.add_nodes_from(range(len(components)))
    for source, target in dependency_graph.edges:
        source_component = component_by_module[source]
        target_component = component_by_module[target]
        if source_component != target_component:
            condensed.add_edge(source_component, target_component)
    component_key = lambda component_index: (
        min(module_index[value] for value in components[component_index]),
        components[component_index],
    )
    topo_components = tuple(nx.lexicographical_topological_sort(condensed, key=component_key))
    component_rank: dict[int, int] = {}
    for component_index in topo_components:
        component_rank[component_index] = max(
            (component_rank[parent] + 1 for parent in condensed.predecessors(component_index)),
            default=0,
        )
    ranks = {
        module_id: component_rank[component_by_module[module_id]]
        for module_id in dependency_graph.nodes
    }
    modules_by_rank: dict[int, list[str]] = {}
    for module_id, rank in ranks.items():
        modules_by_rank.setdefault(rank, []).append(module_id)
    anchors: dict[str, tuple[float, float]] = {}
    for rank, module_ids in sorted(modules_by_rank.items()):
        module_ids.sort(key=lambda value: (module_index[value], value))
        row_width = (len(module_ids) - 1) * float(x_spacing)
        for column, module_id in enumerate(module_ids):
            anchors[module_id] = (
                (column * float(x_spacing)) - (row_width / 2.0),
                -(rank * float(y_spacing)),
            )
    cycles = tuple(
        component
        for component in components
        if len(component) > 1
        or dependency_graph.has_edge(component[0], component[0])
    )
    return ModuleAnchorLayoutResult(anchors=anchors, ranks=ranks, cycles=cycles)


def build_module_local_layout(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    modules: Iterable[Module],
    *,
    module_anchors: Mapping[str, tuple[float, float]] | None = None,
    structural_relations: Sequence[str] = tuple(sorted(STRUCTURAL_RELATIONS)),
    x_spacing: float = 350.0,
    y_spacing: float = 300.0,
    max_columns: int = 4,
) -> ModuleLayoutResult:
    """Lay out compact concept islands centred on their module anchors.

    Dependency rank determines vertical bands, with fundamental concepts at
    the bottom and progressively derived concepts above. Authored member order
    resolves ties. Wide ranks wrap without exceeding ``max_columns``.
    """
    if max_columns < 1:
        raise ValueError("max_columns must be positive")
    if not math.isfinite(float(x_spacing)) or float(x_spacing) <= 0:
        raise ValueError("x_spacing must be a positive finite number")
    if not math.isfinite(float(y_spacing)) or float(y_spacing) <= 0:
        raise ValueError("y_spacing must be a positive finite number")

    module_list = tuple(modules)
    _validate_members(nodes_df, module_list)
    anchors = dict(module_anchors or {})
    relations = {str(value) for value in structural_relations}
    positions: dict[str, tuple[float, float]] = {}
    ranks: dict[str, int] = {}
    ordered_members: dict[str, tuple[str, ...]] = {}
    cycles: dict[str, tuple[tuple[str, ...], ...]] = {}

    for module in module_list:
        order = _order_module(module, edges_df, relations)
        ranks.update(order.ranks)
        ordered_members[module.module_id] = order.ordered_members
        if order.cycles:
            cycles[module.module_id] = order.cycles

        members_by_rank: dict[int, list[str]] = {}
        member_index = {concept_id: index for index, concept_id in enumerate(module.members)}
        for concept_id in module.members:
            members_by_rank.setdefault(order.ranks[concept_id], []).append(concept_id)
        for members in members_by_rank.values():
            members.sort(key=lambda concept_id: (member_index[concept_id], concept_id))

        max_chunks = max(
            (math.ceil(len(members) / max_columns) for members in members_by_rank.values()),
            default=1,
        )
        rank_band_height = max_chunks * float(y_spacing)
        local_positions: dict[str, tuple[float, float]] = {}
        for rank, members in sorted(members_by_rank.items()):
            for chunk_index, offset in enumerate(range(0, len(members), max_columns)):
                chunk = members[offset : offset + max_columns]
                row_width = (len(chunk) - 1) * float(x_spacing)
                for column, concept_id in enumerate(chunk):
                    local_positions[concept_id] = (
                        (column * float(x_spacing)) - (row_width / 2.0),
                        -(rank * rank_band_height) - (chunk_index * float(y_spacing)),
                    )

        if not local_positions:
            continue
        centre_x = sum(value[0] for value in local_positions.values()) / len(local_positions)
        centre_y = sum(value[1] for value in local_positions.values()) / len(local_positions)
        anchor_x, anchor_y = anchors.get(module.module_id, (0.0, 0.0))
        for concept_id, (local_x, local_y) in local_positions.items():
            positions[concept_id] = (
                float(anchor_x) + local_x - centre_x,
                float(anchor_y) + local_y - centre_y,
            )

    return ModuleLayoutResult(
        positions=positions,
        ranks=ranks,
        ordered_members=ordered_members,
        cycles=cycles,
    )


def propose_module_concept_numbering(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    modules: Iterable[Module],
    *,
    structural_relations: Sequence[str] = tuple(sorted(STRUCTURAL_RELATIONS)),
) -> tuple[ConceptNumberingProposal, ...]:
    """Propose module-prefixed IDs in loose fundamental-to-derived order."""
    module_list = tuple(modules)
    _validate_members(nodes_df, module_list)
    old_display_ids = {
        str(row["id"]): str(row.get("display_id", "")).strip()
        for _, row in nodes_df.iterrows()
    }
    relations = {str(value) for value in structural_relations}
    proposals: list[ConceptNumberingProposal] = []
    for module in sorted(module_list, key=lambda item: (item.domain, item.sequence, item.module_id)):
        code = module_display_code(module)
        order = _order_module(module, edges_df, relations)
        cyclic_members = {
            concept_id for cycle in order.cycles for concept_id in cycle
        }
        for index, concept_id in enumerate(order.ordered_members, start=1):
            rank = order.ranks[concept_id]
            rationale = (
                f"dependency rank {rank}; stable topological order prefers authored member order"
            )
            if concept_id in cyclic_members:
                rationale += "; cycle requires editorial review"
            proposals.append(
                ConceptNumberingProposal(
                    concept_id=concept_id,
                    old_display_id=old_display_ids.get(concept_id, ""),
                    new_display_id=f"{code}.{index}",
                    module_id=module.module_id,
                    module_title=module.title,
                    dependency_rank=rank,
                    member_sequence=index * 10,
                    rationale=rationale,
                )
            )
    return tuple(proposals)


def module_display_code(module: Module) -> str:
    """Read the visible module code from its title."""
    match = _MODULE_CODE.match(module.title.strip())
    if not match:
        raise ValueError(
            f"Module {module.module_id} title does not start with SR-N, GR-N, or MATHS-N"
        )
    return match.group(1)


def _order_module(
    module: Module,
    edges_df: pd.DataFrame,
    structural_relations: set[str],
) -> _ModuleOrder:
    members = tuple(str(value) for value in module.members)
    member_set = set(members)
    member_index = {concept_id: index for index, concept_id in enumerate(members)}
    dependency_graph = nx.DiGraph()
    dependency_graph.add_nodes_from(members)
    for row in edges_df.itertuples(index=False):
        source = str(row.source)
        target = str(row.target)
        relation = str(row.relation)
        if relation in structural_relations and source in member_set and target in member_set:
            dependency_graph.add_edge(target, source)

    components = sorted(
        (tuple(sorted(component, key=lambda value: (member_index[value], value)))
         for component in nx.strongly_connected_components(dependency_graph)),
        key=lambda component: (min(member_index[value] for value in component), component),
    )
    component_by_member = {
        concept_id: component_index
        for component_index, component in enumerate(components)
        for concept_id in component
    }
    condensed = nx.DiGraph()
    condensed.add_nodes_from(range(len(components)))
    for source, target in dependency_graph.edges:
        source_component = component_by_member[source]
        target_component = component_by_member[target]
        if source_component != target_component:
            condensed.add_edge(source_component, target_component)

    component_key = lambda component_index: (
        min(member_index[value] for value in components[component_index]),
        components[component_index],
    )
    topo_components = tuple(nx.lexicographical_topological_sort(condensed, key=component_key))
    component_rank: dict[int, int] = {}
    for component_index in topo_components:
        component_rank[component_index] = max(
            (component_rank[parent] + 1 for parent in condensed.predecessors(component_index)),
            default=0,
        )
    ranks = {
        concept_id: component_rank[component_by_member[concept_id]]
        for concept_id in members
    }
    ordered = tuple(
        concept_id
        for component_index in topo_components
        for concept_id in components[component_index]
    )
    cycles = tuple(
        sorted(
            (
                component
                for component in components
                if len(component) > 1
                or dependency_graph.has_edge(component[0], component[0])
            ),
            key=lambda component: (min(member_index[value] for value in component), component),
        )
    )
    return _ModuleOrder(ranks=ranks, ordered_members=ordered, cycles=cycles)


def _validate_members(nodes_df: pd.DataFrame, modules: Sequence[Module]) -> None:
    known = {str(value) for value in nodes_df["id"]}
    seen: dict[str, str] = {}
    for module in modules:
        for raw_concept_id in module.members:
            concept_id = str(raw_concept_id)
            if concept_id not in known:
                raise ValueError(
                    f"Module {module.module_id} references unknown concept {concept_id}"
                )
            previous = seen.get(concept_id)
            if previous is not None:
                raise ValueError(
                    f"Concept {concept_id} belongs to both {previous} and {module.module_id}"
                )
            seen[concept_id] = module.module_id
