"""Validation checks for knowledge-graph CSV content.

This module validates source CSV data before rendering. It reports structured
issues instead of raising for ordinary data problems, so callers can decide
whether warnings should fail a run.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Literal

import pandas as pd

from srkg.text_macros import MacroCall, parse_two_arg_macro_calls
from srkg.config import EDGE_COLUMNS
from srkg.dag import build_dag_reports
from srkg.data import normalise_edges
from srkg.edges import relation_is_directed
from srkg.kb import KnowledgeBase, KnowledgeBaseLoadError, load_knowledge_base
from srkg.module_diagnostics import (
    DEFAULT_MODULE_RELATIONS,
    ModuleBoundaryEdge,
    build_module_diagnostics,
)


Severity = Literal["error", "warning"]

NODE_REQUIRED_COLUMNS = (
    "id",
    "display_id",
    "label",
    "domain",
    "domain_title",
)
SUPPORTED_CUSTOM_MACROS = {"cref", "optional_details", "explanation", "explain"}
CONTROL_CHARS = tuple(chr(code) for code in range(32) if chr(code) not in ("\r", "\n"))


@dataclass(frozen=True)
class ValidationIssue:
    """One validation diagnostic."""

    severity: Severity
    code: str
    message: str
    location: str = ""



def load_validation_issues_from_root(data_root: str | Path) -> list[ValidationIssue]:
    """Load and validate a directory-backed knowledge base."""
    try:
        kb = load_knowledge_base(data_root, include_graphics=False)
    except KnowledgeBaseLoadError as exc:
        return [_issue("error", "kb-load", str(exc), str(data_root))]
    except Exception as exc:
        return [_issue("error", "kb-load", f"Could not load KB data root: {exc}", str(data_root))]

    return validate_knowledge_base(kb)


def validate_knowledge_base(kb: KnowledgeBase) -> list[ValidationIssue]:
    """Editorial diagnostics for an already selected/resolved KB."""
    issues = validate_graph_data(
        kb.nodes_df,
        kb.edges_df,
        kb.edge_key,
        check_cref_edge_consistency=False,
    )
    block_owners = {unit.source_id: unit.owner_id for unit in kb.content_units.values()}
    issues.extend(_validate_content_block_text((*kb.concepts, *kb.modules), kb.nodes_df,
        kb.edges_df, external_domains=kb.missing_domains, block_owners=block_owners))
    issues.extend(_validate_study_question_text(kb.concepts, kb.nodes_df, kb.edges_df,
        external_domains=kb.missing_domains, block_owners=block_owners))
    if kb.modules:
        issues.extend(_validate_module_structure(kb))
    return issues


def validate_graph_data(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    edge_key: dict[str, dict[str, str | bool]] | None = None,
    *,
    check_cref_edge_consistency: bool = True,
) -> list[ValidationIssue]:
    """Validate loaded graph data frames."""
    edge_key = edge_key or {}
    issues: list[ValidationIssue] = []

    issues.extend(_validate_required_columns(nodes_df, "nodes.csv", NODE_REQUIRED_COLUMNS))
    issues.extend(_validate_required_columns(edges_df, "edges.csv", EDGE_COLUMNS))
    if any(issue.severity == "error" for issue in issues):
        return issues

    nodes = nodes_df.copy().fillna("")
    edges = normalise_edges(edges_df.copy().fillna(""))
    nodes["id"] = nodes["id"].astype(str).str.strip()
    edges["source"] = edges["source"].astype(str).str.strip()
    edges["target"] = edges["target"].astype(str).str.strip()
    edges["relation"] = edges["relation"].astype(str).str.strip()

    issues.extend(_validate_nodes(nodes))
    issues.extend(_validate_edges(nodes, edges, edge_key))

    if any(issue.severity == "error" for issue in issues):
        return issues

    issues.extend(_validate_dag(nodes, edges, edge_key))
    return issues


def format_validation_issues(issues: Iterable[ValidationIssue]) -> str:
    """Format validation issues for CLI output."""
    issue_list = list(issues)
    error_count = sum(1 for issue in issue_list if issue.severity == "error")
    warning_count = sum(1 for issue in issue_list if issue.severity == "warning")
    lines = [
        "Validation diagnostics",
        f"Errors: {error_count}; warnings: {warning_count}",
    ]
    if not issue_list:
        lines.append("No validation issues found.")
        return "\n".join(lines)

    severity_order = {"error": 0, "warning": 1}
    for issue in sorted(issue_list, key=lambda item: (severity_order[item.severity], item.code, item.location, item.message)):
        location = f" {issue.location}" if issue.location else ""
        lines.append(f"{issue.severity.upper()} {issue.code}{location}: {issue.message}")
    return "\n".join(lines)


def has_validation_errors(
    issues: Iterable[ValidationIssue],
    *,
    strict: bool = False,
) -> bool:
    """Return whether a set of issues should fail validation."""
    if strict:
        return any(issue.severity in {"error", "warning"} for issue in issues)
    return any(issue.severity == "error" for issue in issues)


def _validate_required_columns(
    df: pd.DataFrame,
    name: str,
    required_columns: Iterable[str],
) -> list[ValidationIssue]:
    missing = set(required_columns) - set(df.columns)
    if not missing:
        return []
    return [
        _issue(
            "error",
            "required-columns",
            f"{name} is missing columns: {', '.join(sorted(missing))}",
            name,
        )
    ]


def _validate_nodes(nodes_df: pd.DataFrame) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    ids = nodes_df["id"].astype(str).str.strip()

    for row_index, row in nodes_df.iterrows():
        node_id = str(row["id"]).strip()
        location = _node_location(row_index, node_id)
        for column in ("id", "display_id", "label", "domain", "domain_title"):
            if not str(row.get(column, "")).strip():
                issues.append(
                    _issue("error", "node-required-value", f"Concept has empty {column}", location)
                )

    duplicate_ids = sorted(id_ for id_ in ids[ids.duplicated()].unique() if id_)
    for node_id in duplicate_ids:
        issues.append(_issue("error", "node-duplicate-id", f"Duplicate concept id '{node_id}'"))

    labels = nodes_df["label"].astype(str).str.strip()
    duplicate_labels = sorted(label for label in labels[labels.duplicated()].unique() if label)
    for label in duplicate_labels:
        issues.append(_issue("warning", "node-duplicate-label", f"Duplicate concept label '{label}'"))

    return issues


def _validate_edges(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    edge_key: dict[str, dict[str, str | bool]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    node_ids = set(nodes_df["id"].astype(str).str.strip())
    known_relations = set(edge_key)

    for row_index, row in edges_df.iterrows():
        source = str(row.get("source", "")).strip()
        target = str(row.get("target", "")).strip()
        relation = str(row.get("relation", "")).strip()
        location = f"edges.csv row {row_index + 2}: {source}->{target}"
        if not source or not target:
            issues.append(_issue("error", "edge-required-value", "Edge has empty source or target", location))
        if source and source not in node_ids:
            issues.append(_issue("error", "edge-endpoint", f"Unknown edge source '{source}'", location))
        if target and target not in node_ids:
            issues.append(_issue("error", "edge-endpoint", f"Unknown edge target '{target}'", location))
        if source and target and source == target:
            issues.append(_issue("warning", "edge-self-loop", "Edge source and target are the same", location))
        if known_relations and relation not in known_relations:
            issues.append(
                _issue(
                    "warning",
                    "edge-relation",
                    f"Relation '{relation}' is not defined in edges_key.csv",
                    location,
                )
            )

    duplicate_edges = (
        edges_df.groupby(["source", "target", "relation"])
        .size()
        .reset_index(name="count")
    )
    for row in duplicate_edges.itertuples(index=False):
        if row.count > 1:
            issues.append(
                _issue(
                    "warning",
                    "edge-duplicate",
                    f"Duplicate edge {row.source}->{row.target} ({row.relation}) appears {row.count} times",
                )
            )
    return issues


def _validate_control_characters(text: str, location: str) -> list[ValidationIssue]:
    for char in CONTROL_CHARS:
        if char in text:
            name = "tab" if char == "\t" else f"U+{ord(char):04X}"
            return [_issue("error", "text-control-character", f"Text contains control character {name}", location)]
    return []


def _validate_backslash_end(text: str, location: str) -> list[ValidationIssue]:
    if text.endswith("\\"):
        return [_issue("error", "text-backslash", "Text ends with a dangling backslash", location)]
    return []


def _validate_balanced_braces(text: str, location: str) -> list[ValidationIssue]:
    depth = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text) and text[index + 1] in "{}\\":
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            if depth == 0:
                return [_issue("error", "text-braces", "Unmatched closing brace", location)]
            depth -= 1
        index += 1
    if depth:
        return [_issue("error", "text-braces", "Unclosed opening brace", location)]
    return []


def _validate_math_delimiters(text: str, location: str) -> list[ValidationIssue]:
    stack: list[str] = []
    index = 0
    while index < len(text) - 1:
        token = text[index:index + 2]
        if token in (r"\(", r"\["):
            stack.append(token)
            index += 2
            continue
        if token in (r"\)", r"\]"):
            expected = r"\(" if token == r"\)" else r"\["
            if not stack or stack[-1] != expected:
                return [_issue("error", "math-delimiter", f"Unmatched math delimiter {token}", location)]
            stack.pop()
            index += 2
            continue
        index += 1
    if stack:
        return [_issue("error", "math-delimiter", f"Unclosed math delimiter {stack[-1]}", location)]
    return []


def _validate_custom_macro_typos(text: str, location: str) -> list[ValidationIssue]:
    issues = []
    for match in re.finditer(r"\\([A-Za-z_]+)", text):
        name = match.group(1)
        if name in SUPPORTED_CUSTOM_MACROS:
            continue
        if name.startswith(("optional", "cref", "explain")):
            issues.append(
                _issue(
                    "warning",
                    "text-unknown-custom-macro",
                    f"Unknown custom macro \\{name}; expected one of {', '.join(sorted(SUPPORTED_CUSTOM_MACROS))}",
                    location,
                )
            )
    return issues


def _parse_two_arg_macro_calls(text, name, location):
    calls, errors = parse_two_arg_macro_calls(text, name)
    return calls, [_issue("error", f"{name}-syntax", message, location) for message in errors]


def _validate_cref_edge_consistency(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    cref_pairs: set[tuple[str, str]],
    cref_targets_by_node: dict[str, set[str]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    edge_pairs = {
        (str(row.source).strip(), str(row.target).strip())
        for row in edges_df.itertuples(index=False)
    }
    undirected_edge_pairs = {frozenset(pair) for pair in edge_pairs}

    for source, target in sorted(cref_pairs):
        if source == target:
            continue
        if frozenset((source, target)) not in undirected_edge_pairs:
            issues.append(
                _issue(
                    "warning",
                    "cref-edge-missing",
                    f"\\cref from {source} to {target} has no corresponding edge in either direction",
                    f"node {source}",
                )
            )

    node_labels = {
        str(row.id).strip(): str(row.label).strip()
        for row in nodes_df.itertuples(index=False)
    }
    for row in edges_df.itertuples(index=False):
        source = str(row.source).strip()
        target = str(row.target).strip()
        if target in cref_targets_by_node.get(source, set()):
            continue
        if source in cref_targets_by_node.get(target, set()):
            continue
        issues.append(
            _issue(
                "warning",
                "edge-cref-missing",
                (
                    f"Edge {source} {node_labels.get(source, '')} -> "
                    f"{target} {node_labels.get(target, '')} has no reciprocal \\cref in either node"
                ),
                f"edge {source}->{target}",
            )
        )
    return issues


def _validate_dag(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    edge_key: dict[str, dict[str, str | bool]],
) -> list[ValidationIssue]:
    directed_relations = tuple(
        relation
        for relation in dict.fromkeys(edges_df["relation"].astype(str).str.strip())
        if relation_is_directed(relation, edge_key)
    )
    if not directed_relations:
        return []

    issues = []
    for report in build_dag_reports(nodes_df, edges_df, directed_relations):
        if not report.is_dag:
            example = ""
            if report.cycles:
                example = " Example cycle: " + " -> ".join(
                    edge.source for edge in report.cycles[0]
                )
            issues.append(
                _issue(
                    "error",
                    "directed-cycle",
                    f"Directed relation group {report.name} is not a DAG.{example}",
                )
            )
        for redundancy in report.transitive_redundancies:
            issues.append(
                _issue(
                    "warning",
                    "directed-transitive-redundancy",
                    (
                        f"{redundancy.edge.source}->{redundancy.edge.target} is also implied by "
                        f"{' -> '.join(redundancy.path)}"
                    ),
                    report.name,
                )
            )
    return issues


def _validate_module_structure(kb: KnowledgeBase) -> list[ValidationIssue]:
    """Validate structural module DAGs and authored prerequisite ordering."""
    diagnostics = build_module_diagnostics(
        kb,
        relations=DEFAULT_MODULE_RELATIONS,
    )
    issues: list[ValidationIssue] = []
    for report in diagnostics.quotient_dag_reports:
        if report.is_dag:
            continue
        example = ""
        if report.cycles:
            example = " Example cycle: " + " -> ".join(
                edge.source for edge in report.cycles[0]
            )
        issues.append(_issue(
            "error",
            "module-directed-cycle",
            f"Module relation group {report.name} is not a DAG.{example}",
        ))
    for edge in diagnostics.module_order_violations:
        issues.append(_module_order_issue(
            "module-order-contradiction",
            "Module sequence places a dependency before its prerequisite",
            edge,
        ))
    for edge in diagnostics.member_order_violations:
        issues.append(_module_order_issue(
            "module-member-order-contradiction",
            "Member sequence places a dependency before its prerequisite",
            edge,
        ))
    return issues


def _module_order_issue(
    code: str,
    message: str,
    edge: ModuleBoundaryEdge,
) -> ValidationIssue:
    return _issue(
        "warning",
        code,
        (
            f"{message}: {edge.source_concept_id} {edge.relation} "
            f"{edge.target_concept_id}"
        ),
        f"{edge.source_module_id}->{edge.target_module_id}",
    )


def _validate_content_block_text(
    concepts,
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    *, external_domains=(), block_owners=None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    block_owners = block_owners or {}
    node_ids = set(nodes_df["id"].astype(str).str.strip())
    cref_pairs: set[tuple[str, str]] = set()

    for concept in concepts:
        owner_id = getattr(concept, "id", None) or concept.module_id
        for block in concept.content_blocks:
            for field_name, text in (("body", block.body), ("statement", block.statement), ("title", block.title)):
                location = f"content block {block.block_id}" + (" statement" if field_name == "statement" else "")
                issues.extend(_validate_control_characters(text, location))
                issues.extend(_validate_backslash_end(text, location))
                issues.extend(_validate_balanced_braces(text, location))
                issues.extend(_validate_math_delimiters(text, location))
                issues.extend(_validate_custom_macro_typos(text, location))

                cref_calls, cref_errors = _parse_two_arg_macro_calls(text, "cref", location)
                issues.extend(cref_errors)
                for call in cref_calls:
                    target = call.args[1].strip()
                    cref_pairs.add((owner_id, target))

                _, optional_errors = _parse_two_arg_macro_calls(text, "optional_details", location)
                issues.extend(optional_errors)

    for source, target in sorted(cref_pairs):
        if target not in node_ids and target not in block_owners and target.partition(".")[0] not in external_domains:
            issues.append(
                _issue(
                    "error",
                    "cref-target",
                    f"\\cref target '{target}' is not a known concept or block id",
                    f"content block source {source}",
                )
            )

    if any(issue.severity == "error" for issue in issues):
        return issues

    # Only owning concepts participate in graph diagnostics, never blocks.
    concept_pairs = {(source, block_owners.get(target, target)) for source, target in cref_pairs
                     if source in node_ids and block_owners.get(target, target) in node_ids}
    targets_by_owner: dict[str, set[str]] = {}
    for source, target in concept_pairs:
        targets_by_owner.setdefault(source, set()).add(target)
    issues.extend(_validate_cref_edge_consistency(nodes_df, edges_df, concept_pairs, targets_by_owner))
    return issues


def _validate_study_question_text(
    concepts,
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    *, external_domains=(), block_owners=None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    block_owners = block_owners or {}
    node_ids = set(nodes_df["id"].astype(str).str.strip())
    cref_pairs: set[tuple[str, str]] = set()
    cref_targets_by_node: dict[str, set[str]] = {}

    for concept in concepts:
        for question in concept.study_questions:
            authored_text = [
                ("prompt", question.prompt),
                ("answer", question.answer),
            ]
            authored_text.extend(
                (f"option {option.option_id}", option.text)
                for option in question.options
            )
            for field_name, text in authored_text:
                location = f"study question {question.question_id} {field_name}"
                issues.extend(_validate_control_characters(text, location))
                issues.extend(_validate_backslash_end(text, location))
                issues.extend(_validate_balanced_braces(text, location))
                issues.extend(_validate_math_delimiters(text, location))
                issues.extend(_validate_custom_macro_typos(text, location))

                cref_calls, cref_errors = _parse_two_arg_macro_calls(text, "cref", location)
                issues.extend(cref_errors)
                for call in cref_calls:
                    target = call.args[1].strip()
                    cref_pairs.add((concept.id, target))
                    cref_targets_by_node.setdefault(concept.id, set()).add(target)

                _, optional_errors = _parse_two_arg_macro_calls(text, "optional_details", location)
                issues.extend(optional_errors)

            if not str(question.answer).strip():
                issues.append(
                    _issue(
                        "warning",
                        "study-answer-missing",
                        "Study question has no answer",
                        f"study question {question.question_id}",
                    )
                )

    for source, target in sorted(cref_pairs):
        if target not in node_ids and target not in block_owners and target.partition(".")[0] not in external_domains:
            issues.append(
                _issue(
                    "error",
                    "cref-target",
                    f"\\cref target '{target}' is not a known concept or block id",
                    f"study question source {source}",
                )
            )

    if any(issue.severity == "error" for issue in issues):
        return issues

    return issues


def _node_location(row_index: int, node_id: str, column: str | None = None) -> str:
    base = f"nodes.csv row {row_index + 2}"
    if node_id:
        base += f" ({node_id})"
    if column:
        base += f" {column}"
    return base


def _issue(
    severity: Severity,
    code: str,
    message: str,
    location: str = "",
) -> ValidationIssue:
    return ValidationIssue(severity=severity, code=code, message=message, location=location)
