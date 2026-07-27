#!/usr/bin/env python3
"""Analyze experimental fine-grained block graph worksheets.

The worksheets are Markdown discussion documents, not production KB data. This
tool parses their block headings and edge tables, then computes dependency-order
diagnostics so we can test the model before changing the runtime schema.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import networkx as nx


ORDER_RELATION_DIRECTIONS: dict[str, str] = {
    "requires": "target_to_source",
    "derives_from": "target_to_source",
    "special_case_of": "target_to_source",
    "supplies_algebra_for": "source_to_target",
}

OPTIONAL_ROLE_NAMES = {
    "algebra_support",
    "intuition",
    "warning",
    "example",
    "connection",
    "summary",
}

BLOCK_HEADING_RE = re.compile(r"^### `([^`]+)`\s*$")
ROLE_RE = re.compile(r"^Role: `([^`]+)`\s*$")
EDGE_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*$")
DRAFT_ORDER_RE = re.compile(r"^[^.]+\.([0-9]+)\.")


@dataclass(frozen=True)
class Block:
    block_id: str
    role: str
    draft_order: int | None
    line_no: int


@dataclass(frozen=True)
class Edge:
    source: str
    relation: str
    target: str
    note: str
    line_no: int


@dataclass(frozen=True)
class Worksheet:
    title: str
    path: Path
    blocks: dict[str, Block]
    edges: tuple[Edge, ...]


@dataclass(frozen=True)
class OrderConstraint:
    before: str
    after: str
    relation: str
    source: str
    target: str
    line_no: int


@dataclass(frozen=True)
class WorksheetAnalysis:
    worksheet: Worksheet
    constraints: tuple[OrderConstraint, ...]
    ignored_edges: tuple[Edge, ...]
    graph: nx.DiGraph
    cycles: tuple[tuple[str, ...], ...]
    topological_order: tuple[str, ...]
    longest_path: tuple[str, ...]
    draft_order_conflicts: tuple[OrderConstraint, ...]
    isolated_blocks: tuple[str, ...]
    optional_role_blocks: tuple[str, ...]

    @property
    def is_dag(self) -> bool:
        return not self.cycles


def parse_worksheet(path: str | Path) -> Worksheet:
    """Parse block IDs, roles, and edge rows from one Markdown worksheet."""
    worksheet_path = Path(path)
    lines = worksheet_path.read_text(encoding="utf-8").splitlines()
    title = worksheet_path.stem
    blocks: dict[str, Block] = {}
    edges: list[Edge] = []
    current_block_id: str | None = None
    section: str | None = None

    for line_no, line in enumerate(lines, start=1):
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line == "## Fine Blocks":
            section = "blocks"
            current_block_id = None
            continue
        if line == "## Edge List":
            section = "edges"
            current_block_id = None
            continue
        if line.startswith("## "):
            section = None
            current_block_id = None
            continue

        if section == "blocks":
            heading_match = BLOCK_HEADING_RE.match(line)
            if heading_match:
                block_id = heading_match.group(1)
                blocks[block_id] = Block(
                    block_id=block_id,
                    role="",
                    draft_order=parse_draft_order(block_id),
                    line_no=line_no,
                )
                current_block_id = block_id
                continue
            role_match = ROLE_RE.match(line)
            if role_match and current_block_id:
                existing = blocks[current_block_id]
                blocks[current_block_id] = Block(
                    block_id=existing.block_id,
                    role=role_match.group(1),
                    draft_order=existing.draft_order,
                    line_no=existing.line_no,
                )
            continue

        if section == "edges":
            row_match = EDGE_ROW_RE.match(line)
            if not row_match:
                continue
            source, relation, target, note = row_match.groups()
            edges.append(
                Edge(
                    source=source,
                    relation=relation,
                    target=target,
                    note=_clean_note(note),
                    line_no=line_no,
                )
            )

    missing_roles = [block.block_id for block in blocks.values() if not block.role]
    if missing_roles:
        missing = ", ".join(missing_roles)
        raise ValueError(f"{worksheet_path} has block(s) without Role lines: {missing}")
    if not blocks:
        raise ValueError(f"{worksheet_path} has no parseable fine blocks")
    if not edges:
        raise ValueError(f"{worksheet_path} has no parseable edge rows")

    return Worksheet(
        title=title,
        path=worksheet_path,
        blocks=blocks,
        edges=tuple(edges),
    )


def parse_draft_order(block_id: str) -> int | None:
    """Return the numeric discussion handle from IDs such as ``mee.010.foo``."""
    match = DRAFT_ORDER_RE.match(block_id)
    return int(match.group(1)) if match else None


def analyze_worksheet(
    worksheet: Worksheet,
    order_relation_directions: dict[str, str] | None = None,
) -> WorksheetAnalysis:
    """Build dependency-order diagnostics for a parsed worksheet."""
    relation_directions = order_relation_directions or ORDER_RELATION_DIRECTIONS
    graph = nx.DiGraph()
    graph.add_nodes_from(worksheet.blocks)
    constraints: list[OrderConstraint] = []
    ignored_edges: list[Edge] = []

    for edge in worksheet.edges:
        direction = relation_directions.get(edge.relation)
        if direction is None:
            ignored_edges.append(edge)
            continue
        before, after = orient_edge(edge, direction)
        graph.add_node(before)
        graph.add_node(after)
        graph.add_edge(before, after, relation=edge.relation, source=edge.source, target=edge.target)
        constraints.append(
            OrderConstraint(
                before=before,
                after=after,
                relation=edge.relation,
                source=edge.source,
                target=edge.target,
                line_no=edge.line_no,
            )
        )

    cycles = tuple(tuple(cycle) for cycle in sorted(nx.simple_cycles(graph), key=lambda item: (len(item), item)))
    topological_order: tuple[str, ...] = ()
    longest_path: tuple[str, ...] = ()
    if not cycles:
        topological_order = tuple(
            nx.lexicographical_topological_sort(
                graph,
                key=lambda node: node_sort_key(str(node), worksheet),
            )
        )
        if graph.number_of_edges():
            longest_path = tuple(nx.dag_longest_path(graph, topo_order=list(topological_order)))

    draft_order_conflicts = tuple(
        constraint
        for constraint in constraints
        if _has_draft_order_conflict(constraint, worksheet)
    )
    isolated_blocks = tuple(
        sorted(
            (
                block_id
                for block_id in worksheet.blocks
                if graph.degree(block_id) == 0
            ),
            key=lambda block_id: node_sort_key(block_id, worksheet),
        )
    )
    optional_role_blocks = tuple(
        sorted(
            (
                block.block_id
                for block in worksheet.blocks.values()
                if block.role in OPTIONAL_ROLE_NAMES
            ),
            key=lambda block_id: node_sort_key(block_id, worksheet),
        )
    )

    return WorksheetAnalysis(
        worksheet=worksheet,
        constraints=tuple(constraints),
        ignored_edges=tuple(ignored_edges),
        graph=graph,
        cycles=cycles,
        topological_order=topological_order,
        longest_path=longest_path,
        draft_order_conflicts=draft_order_conflicts,
        isolated_blocks=isolated_blocks,
        optional_role_blocks=optional_role_blocks,
    )


def orient_edge(edge: Edge, direction: str) -> tuple[str, str]:
    """Convert a worksheet edge to ``before -> after`` dependency order."""
    if direction == "target_to_source":
        return edge.target, edge.source
    if direction == "source_to_target":
        return edge.source, edge.target
    raise ValueError(f"Unknown relation direction: {direction}")


def format_analysis_report(analyses: Sequence[WorksheetAnalysis]) -> str:
    """Format analyses as a Markdown report."""
    lines = [
        "# Fine-Grained Block Graph Analysis",
        "",
        "Generated from the experimental Markdown worksheets. This report is not",
        "runtime KB data.",
        "",
        "## Dependency Relation Orientation",
        "",
        "| Relation | Dependency-order interpretation |",
        "| --- | --- |",
    ]
    for relation, direction in ORDER_RELATION_DIRECTIONS.items():
        interpretation = (
            "`target` must appear before `source`"
            if direction == "target_to_source"
            else "`source` must appear before `target`"
        )
        lines.append(f"| `{relation}` | {interpretation} |")
    lines.extend([
        "",
        "Other relations are treated as non-ordering side links for this pass.",
        "",
    ])

    for analysis in analyses:
        lines.extend(format_one_analysis(analysis))
        lines.append("")

    lines.extend(format_cross_experiment_summary(analyses))
    return "\n".join(lines).rstrip() + "\n"


def format_one_analysis(analysis: WorksheetAnalysis) -> list[str]:
    worksheet = analysis.worksheet
    relation_counts = Counter(edge.relation for edge in worksheet.edges)
    ignored_counts = Counter(edge.relation for edge in analysis.ignored_edges)
    local_constraint_nodes = sorted(
        (
            node
            for node in analysis.graph.nodes
            if node in worksheet.blocks and analysis.graph.degree(node) > 0
        ),
        key=lambda node: node_sort_key(str(node), worksheet),
    )
    external_nodes = sorted(
        (node for node in analysis.graph.nodes if node not in worksheet.blocks),
        key=lambda node: node_sort_key(str(node), worksheet),
    )

    lines = [
        f"## {worksheet.title}",
        "",
        f"Source: [{worksheet.path.name}]({worksheet.path.name})",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Fine blocks | {len(worksheet.blocks)} |",
        f"| Edge rows | {len(worksheet.edges)} |",
        f"| Ordering constraints | {len(analysis.constraints)} |",
        f"| Non-ordering side links | {len(analysis.ignored_edges)} |",
        f"| External dependency nodes | {len(external_nodes)} |",
        f"| DAG? | {'yes' if analysis.is_dag else 'no'} |",
        f"| Cycles | {len(analysis.cycles)} |",
        f"| Draft-order conflicts | {len(analysis.draft_order_conflicts)} |",
        "",
        "**Relation Counts**",
        "",
        _format_counter(relation_counts),
        "",
        "**Non-Ordering Relations**",
        "",
        _format_counter(ignored_counts) if ignored_counts else "None.",
        "",
        "**External Dependency Nodes**",
        "",
        _format_node_list(external_nodes, worksheet),
        "",
        "**Main Ordered Blocks**",
        "",
        _format_node_list(local_constraint_nodes, worksheet),
        "",
        "**Isolated Blocks Under Ordering Relations**",
        "",
        _format_node_list(analysis.isolated_blocks, worksheet),
        "",
        "**Optional-Role Blocks**",
        "",
        _format_node_list(analysis.optional_role_blocks, worksheet),
        "",
    ]

    if analysis.cycles:
        lines.extend([
            "**Cycles**",
            "",
            *_format_cycles(analysis.cycles, worksheet),
            "",
        ])
    else:
        lines.extend([
            "**Topological Dependency Order**",
            "",
            _format_numbered_nodes(analysis.topological_order, worksheet),
            "",
            "**Longest Dependency Chain**",
            "",
            _format_path(analysis.longest_path, worksheet),
            "",
        ])

    lines.extend([
        "**Ordering Conflicts With Draft Handles**",
        "",
        _format_conflicts(analysis.draft_order_conflicts, worksheet),
    ])
    return lines


def format_cross_experiment_summary(analyses: Sequence[WorksheetAnalysis]) -> list[str]:
    dag_sentence = (
        "All analyzed worksheet graphs are acyclic under the current relation orientation."
        if all(analysis.is_dag for analysis in analyses)
        else "At least one worksheet graph has a cycle under the current relation orientation."
    )
    lines = [
        "## Cross-Experiment Observations",
        "",
        dag_sentence,
        "That makes dependency-order presentation mechanically feasible for the",
        "acyclic examples.",
        "",
        "The ordering conflicts are useful rather than alarming: they identify",
        "places where the original prose introduced a memorable or familiar item",
        "before its graph prerequisites. MEE should be expected to have more of",
        "these than the EM-field worksheet because the famous rest-energy formula",
        "comes late in the derivation graph.",
        "",
        "For this pass, only `requires`, `derives_from`, `special_case_of`, and",
        "`supplies_algebra_for` constrain the main order. Side-link relations such",
        "as `elaborates`, `warns_about`, `gives_example_of`, and `connects_to` are",
        "better treated as optional expansions, annotations, or navigation links.",
        "",
        "The largest unresolved modelling issue is the orientation and purpose of",
        "`supplies_algebra_for`. Some algebra support is genuinely on the main",
        "derivation spine; other algebra support is explanatory detail that should",
        "probably unfold after its target. This relation may need to split into",
        "two relations before becoming production schema.",
    ]
    if analyses:
        lines.extend([
            "",
            "| Worksheet | Blocks | Constraints | Draft Conflicts | Side Links |",
            "| --- | ---: | ---: | ---: | ---: |",
        ])
        for analysis in analyses:
            lines.append(
                "| "
                f"{analysis.worksheet.title} | "
                f"{len(analysis.worksheet.blocks)} | "
                f"{len(analysis.constraints)} | "
                f"{len(analysis.draft_order_conflicts)} | "
                f"{len(analysis.ignored_edges)} |"
            )
    return lines


def node_sort_key(node: str, worksheet: Worksheet) -> tuple[int, int, str]:
    """Sort external nodes first, then local blocks by draft handle."""
    block = worksheet.blocks.get(node)
    if block:
        order = block.draft_order if block.draft_order is not None else 999_999
        return (1, order, node)
    return (0, 999_999, node)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "worksheets",
        nargs="+",
        type=Path,
        help="Markdown worksheet files to analyze.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional Markdown report path. Prints to stdout when omitted.",
    )
    args = parser.parse_args(argv)

    analyses = [analyze_worksheet(parse_worksheet(path)) for path in args.worksheets]
    report = format_analysis_report(analyses)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


def _has_draft_order_conflict(constraint: OrderConstraint, worksheet: Worksheet) -> bool:
    before = worksheet.blocks.get(constraint.before)
    after = worksheet.blocks.get(constraint.after)
    if not before or not after:
        return False
    if before.draft_order is None or after.draft_order is None:
        return False
    return before.draft_order > after.draft_order


def _format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "None."
    return "\n".join(
        f"- `{relation}`: {count}"
        for relation, count in sorted(counter.items())
    )


def _format_node_list(nodes: Iterable[str], worksheet: Worksheet) -> str:
    node_list = list(nodes)
    if not node_list:
        return "None."
    return "\n".join(f"- {_format_node(node, worksheet)}" for node in node_list)


def _format_numbered_nodes(nodes: Iterable[str], worksheet: Worksheet) -> str:
    node_list = list(nodes)
    if not node_list:
        return "None."
    return "\n".join(
        f"{index}. {_format_node(node, worksheet)}"
        for index, node in enumerate(node_list, start=1)
    )


def _format_path(nodes: Iterable[str], worksheet: Worksheet) -> str:
    node_list = list(nodes)
    if not node_list:
        return "None."
    return " -> ".join(_format_node(node, worksheet) for node in node_list)


def _format_cycles(cycles: Iterable[Iterable[str]], worksheet: Worksheet) -> list[str]:
    lines = []
    for cycle in cycles:
        lines.append(f"- {_format_path(cycle, worksheet)}")
    return lines


def _format_conflicts(
    conflicts: Sequence[OrderConstraint],
    worksheet: Worksheet,
) -> str:
    if not conflicts:
        return "None."
    lines = [
        "| Required-before | Required-after | Relation | Worksheet edge |",
        "| --- | --- | --- | --- |",
    ]
    for conflict in sorted(
        conflicts,
        key=lambda item: (
            node_sort_key(item.before, worksheet),
            node_sort_key(item.after, worksheet),
            item.relation,
        ),
    ):
        lines.append(
            "| "
            f"{_format_node(conflict.before, worksheet)} | "
            f"{_format_node(conflict.after, worksheet)} | "
            f"`{conflict.relation}` | "
            f"`{conflict.source}` -> `{conflict.target}` |"
        )
    return "\n".join(lines)


def _format_node(node: str, worksheet: Worksheet) -> str:
    block = worksheet.blocks.get(node)
    if not block:
        return f"`{node}` _(external)_"
    return f"`{node}` _{block.role}_"


def _clean_note(note: str) -> str:
    return note.replace("<br>", " ").strip()


if __name__ == "__main__":
    main(sys.argv[1:])
