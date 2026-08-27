"""Diagnostics for authored modules and module-boundary graph structure."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence

import pandas as pd

from srkg.dag import DagReport, build_dag_reports, format_dag_reports
from srkg.kb import KnowledgeBase, load_knowledge_base
from srkg.model import Concept, Module


@dataclass(frozen=True)
class ModuleBoundaryEdge:
    """One concrete concept edge crossing an authored module boundary."""

    source_module_id: str
    source_module_title: str
    target_module_id: str
    target_module_title: str
    source_concept_id: str
    source_concept_label: str
    target_concept_id: str
    target_concept_label: str
    relation: str
    note: str = ""


@dataclass(frozen=True)
class ModuleBoundaryPair:
    """Aggregated concrete edges between two authored modules."""

    source_module_id: str
    source_module_title: str
    target_module_id: str
    target_module_title: str
    edge_count: int
    relation_counts: dict[str, int]
    declared_support: bool
    edges: tuple[ModuleBoundaryEdge, ...]


@dataclass(frozen=True)
class ModuleDiagnostics:
    """Summary of module membership, boundary edges, and quotient DAGs."""

    module_count: int
    concept_count: int
    internal_edge_count: int
    boundary_edge_count: int
    internal_relation_counts: dict[str, int]
    boundary_relation_counts: dict[str, int]
    boundary_pairs: tuple[ModuleBoundaryPair, ...]
    undeclared_boundary_pairs: tuple[ModuleBoundaryPair, ...]
    declared_supports_without_boundary: tuple[tuple[str, str], ...]
    quotient_dag_reports: tuple[DagReport, ...]


def load_module_diagnostics(
    data_root: str,
    *,
    relations: Sequence[str] | None = None,
) -> ModuleDiagnostics:
    """Load a KB data root and build module diagnostics."""
    return build_module_diagnostics(load_knowledge_base(data_root), relations=relations)


def build_module_diagnostics(
    kb: KnowledgeBase,
    *,
    relations: Sequence[str] | None = None,
) -> ModuleDiagnostics:
    """Build diagnostics for authored module boundaries in a loaded KB."""
    membership = _concept_module_index(kb.modules)
    concept_index = kb.concept_index
    module_index = kb.module_index
    relation_filter = _relation_filter(relations)

    internal_relation_counts: Counter[str] = Counter()
    boundary_edges: list[ModuleBoundaryEdge] = []
    quotient_rows = []

    for row in kb.edges_df.itertuples(index=False):
        relation = str(getattr(row, "relation", "")).strip()
        if relation_filter is not None and relation not in relation_filter:
            continue
        source_concept_id = str(getattr(row, "source")).strip()
        target_concept_id = str(getattr(row, "target")).strip()
        source_module_id = membership.get(source_concept_id)
        target_module_id = membership.get(target_concept_id)
        if not source_module_id or not target_module_id:
            continue
        if source_module_id == target_module_id:
            internal_relation_counts[relation] += 1
            continue

        source_module = module_index[source_module_id]
        target_module = module_index[target_module_id]
        source_concept = concept_index.get(source_concept_id)
        target_concept = concept_index.get(target_concept_id)
        boundary_edges.append(ModuleBoundaryEdge(
            source_module_id=source_module_id,
            source_module_title=source_module.title,
            target_module_id=target_module_id,
            target_module_title=target_module.title,
            source_concept_id=source_concept_id,
            source_concept_label=_concept_label(source_concept, source_concept_id),
            target_concept_id=target_concept_id,
            target_concept_label=_concept_label(target_concept, target_concept_id),
            relation=relation,
            note=str(getattr(row, "note", "")).strip(),
        ))
        quotient_rows.append({
            "source": source_module_id,
            "target": target_module_id,
            "relation": relation,
            "note": "",
        })

    support_pairs = _declared_module_support_pairs(kb.modules, membership)
    boundary_pairs = _module_boundary_pairs(boundary_edges, support_pairs)
    boundary_pair_keys = {
        (pair.source_module_id, pair.target_module_id)
        for pair in boundary_pairs
    }
    declared_supports_without_boundary = tuple(
        sorted(pair for pair in support_pairs if pair not in boundary_pair_keys)
    )

    quotient_dag_reports: tuple[DagReport, ...] = ()
    selected_relations = tuple(relations or _directed_relations_from_key(kb))
    if selected_relations and quotient_rows:
        quotient_dag_reports = tuple(build_dag_reports(
            _module_nodes_df(kb.modules),
            pd.DataFrame(quotient_rows),
            selected_relations,
        ))

    return ModuleDiagnostics(
        module_count=len(kb.modules),
        concept_count=len(membership),
        internal_edge_count=sum(internal_relation_counts.values()),
        boundary_edge_count=len(boundary_edges),
        internal_relation_counts=dict(sorted(internal_relation_counts.items())),
        boundary_relation_counts=dict(sorted(Counter(
            edge.relation for edge in boundary_edges
        ).items())),
        boundary_pairs=boundary_pairs,
        undeclared_boundary_pairs=tuple(
            pair for pair in boundary_pairs if not pair.declared_support
        ),
        declared_supports_without_boundary=declared_supports_without_boundary,
        quotient_dag_reports=quotient_dag_reports,
    )


def format_module_diagnostics(
    diagnostics: ModuleDiagnostics,
    *,
    max_items: int = 12,
) -> str:
    """Format module diagnostics for command-line output."""
    lines = [
        "Module diagnostics",
        "Concrete concept edges are contracted through authored module membership.",
        "",
        f"Modules: {diagnostics.module_count}",
        f"Concepts with module membership: {diagnostics.concept_count}",
        f"Internal concept edges: {diagnostics.internal_edge_count}",
        f"Boundary concept edges: {diagnostics.boundary_edge_count}",
        "Internal relation counts: "
        + _format_counts(diagnostics.internal_relation_counts),
        "Boundary relation counts: "
        + _format_counts(diagnostics.boundary_relation_counts),
        "",
        f"Boundary module pairs: {len(diagnostics.boundary_pairs)}",
    ]

    for pair in diagnostics.boundary_pairs[:max_items]:
        lines.append(
            "  "
            + _format_pair_heading(pair)
            + f": {pair.edge_count} edge(s), "
            + f"relations={_format_counts(pair.relation_counts)}, "
            + f"supports={'yes' if pair.declared_support else 'no'}"
        )
        for edge in pair.edges[:max_items]:
            lines.append("    " + _format_boundary_edge(edge))
        if len(pair.edges) > max_items:
            lines.append(f"    ... {len(pair.edges) - max_items} more")
    if len(diagnostics.boundary_pairs) > max_items:
        lines.append(f"  ... {len(diagnostics.boundary_pairs) - max_items} more pairs")

    lines.append("")
    lines.append(
        f"Undeclared module boundary pairs: {len(diagnostics.undeclared_boundary_pairs)}"
    )
    for pair in diagnostics.undeclared_boundary_pairs[:max_items]:
        lines.append(
            "  "
            + _format_pair_heading(pair)
            + f": {pair.edge_count} edge(s), relations={_format_counts(pair.relation_counts)}"
        )
    if len(diagnostics.undeclared_boundary_pairs) > max_items:
        lines.append(
            f"  ... {len(diagnostics.undeclared_boundary_pairs) - max_items} more"
        )

    lines.append("")
    lines.append(
        "Declared module supports without matching boundary edges: "
        f"{len(diagnostics.declared_supports_without_boundary)}"
    )
    for source_module_id, target_module_id in diagnostics.declared_supports_without_boundary[:max_items]:
        lines.append(f"  {source_module_id} -> {target_module_id}")
    if len(diagnostics.declared_supports_without_boundary) > max_items:
        lines.append(
            "  ... "
            + str(len(diagnostics.declared_supports_without_boundary) - max_items)
            + " more"
        )

    if diagnostics.quotient_dag_reports:
        lines.append("")
        lines.append("Module quotient DAGs")
        lines.append(
            format_dag_reports(
                diagnostics.quotient_dag_reports,
                max_items=max_items,
            )
        )

    return "\n".join(lines)


def _concept_module_index(modules: Sequence[Module]) -> dict[str, str]:
    membership = {}
    for module in modules:
        for concept_id in module.members:
            membership[str(concept_id)] = module.module_id
    return membership


def _concept_label(concept: Concept | None, fallback: str) -> str:
    return concept.label if concept and concept.label else fallback


def _relation_filter(relations: Sequence[str] | None) -> set[str] | None:
    if relations is None:
        return None
    return {str(relation) for relation in relations if str(relation)}


def _declared_module_support_pairs(
    modules: Sequence[Module],
    membership: dict[str, str],
) -> set[tuple[str, str]]:
    pairs = set()
    for module in modules:
        for support in module.supports:
            target_type = str(support.target_type)
            target_id = str(support.target_id)
            if target_type == "module":
                pairs.add((module.module_id, target_id))
            elif target_type == "concept" and target_id in membership:
                pairs.add((module.module_id, membership[target_id]))
    return pairs


def _module_boundary_pairs(
    boundary_edges: Sequence[ModuleBoundaryEdge],
    support_pairs: set[tuple[str, str]],
) -> tuple[ModuleBoundaryPair, ...]:
    grouped: dict[tuple[str, str], list[ModuleBoundaryEdge]] = {}
    for edge in boundary_edges:
        grouped.setdefault(
            (edge.source_module_id, edge.target_module_id),
            [],
        ).append(edge)

    pairs = []
    for (source_module_id, target_module_id), edges in grouped.items():
        ordered_edges = tuple(sorted(
            edges,
            key=lambda edge: (
                edge.relation,
                edge.source_concept_id,
                edge.target_concept_id,
            ),
        ))
        first_edge = ordered_edges[0]
        pairs.append(ModuleBoundaryPair(
            source_module_id=source_module_id,
            source_module_title=first_edge.source_module_title,
            target_module_id=target_module_id,
            target_module_title=first_edge.target_module_title,
            edge_count=len(ordered_edges),
            relation_counts=dict(sorted(Counter(
                edge.relation for edge in ordered_edges
            ).items())),
            declared_support=(source_module_id, target_module_id) in support_pairs,
            edges=ordered_edges,
        ))

    return tuple(sorted(
        pairs,
        key=lambda pair: (
            -pair.edge_count,
            pair.source_module_id,
            pair.target_module_id,
        ),
    ))


def _module_nodes_df(modules: Sequence[Module]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "id": module.module_id,
            "display_id": module.module_id,
            "label": module.title,
            "layer": module.sequence,
        }
        for module in modules
    ])


def _directed_relations_from_key(kb: KnowledgeBase) -> tuple[str, ...]:
    edge_relations = list(dict.fromkeys(kb.edges_df["relation"].astype(str)))
    relations = []
    for relation, metadata in kb.edge_key.items():
        if relation in edge_relations and bool(metadata.get("directed", True)):
            relations.append(relation)
    for relation in edge_relations:
        if relation in relations:
            continue
        if bool(kb.edge_key.get(relation, {}).get("directed", True)):
            relations.append(relation)
    return tuple(relations)


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "(none)"
    return ", ".join(
        f"{relation}: {count}"
        for relation, count in sorted(counts.items())
    )


def _format_pair_heading(pair: ModuleBoundaryPair) -> str:
    return (
        f"{pair.source_module_id} {pair.source_module_title} -> "
        f"{pair.target_module_id} {pair.target_module_title}"
    )


def _format_boundary_edge(edge: ModuleBoundaryEdge) -> str:
    return (
        f"{edge.source_concept_id} {edge.source_concept_label} "
        f"{edge.relation} "
        f"{edge.target_concept_id} {edge.target_concept_label}"
    )
