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

from srkg.config import EDGE_COLUMNS, EDGE_KEY_COLUMNS
from srkg.dag import build_dag_reports
from srkg.data import find_edge_key_path, load_edge_key, normalise_edges
from srkg.edges import relation_is_directed
from srkg.layout import parse_layer_value


Severity = Literal["error", "warning"]

NODE_REQUIRED_COLUMNS = (
    "id",
    "label",
    "layer",
    "layer_title",
    "definition_new",
    "derivation_new",
    "explanation_new",
)
BASE_TEXT_COLUMNS = ("definition_new", "derivation_new", "explanation_new")
SUPPORTED_CUSTOM_MACROS = {"cref", "optional_details"}
CONTROL_CHARS = tuple(chr(code) for code in range(32) if chr(code) not in ("\r", "\n"))


@dataclass(frozen=True)
class ValidationIssue:
    """One validation diagnostic."""

    severity: Severity
    code: str
    message: str
    location: str = ""


@dataclass(frozen=True)
class MacroCall:
    """A parsed two-argument macro call."""

    name: str
    args: tuple[str, str]
    start: int
    end: int


def load_validation_issues(
    *,
    nodes_path: str | Path,
    edges_path: str | Path,
    edge_key_path: str | Path | None = None,
) -> list[ValidationIssue]:
    """Load graph CSV files and validate them."""
    nodes_file = Path(nodes_path)
    edges_file = Path(edges_path)
    issues: list[ValidationIssue] = []

    try:
        nodes_df = pd.read_csv(nodes_file).fillna("")
    except Exception as exc:
        return [_issue("error", "nodes-read", f"Could not read nodes CSV: {exc}", str(nodes_file))]

    try:
        edges_df = pd.read_csv(edges_file).fillna("")
    except Exception as exc:
        return [_issue("error", "edges-read", f"Could not read edges CSV: {exc}", str(edges_file))]

    resolved_edge_key_path = find_edge_key_path(
        edges_file,
        str(edge_key_path) if edge_key_path else None,
    )
    edge_key: dict[str, dict[str, str | bool]] = {}
    if resolved_edge_key_path is not None:
        try:
            edge_key_df = pd.read_csv(resolved_edge_key_path).fillna("")
        except Exception as exc:
            issues.append(
                _issue(
                    "error",
                    "edge-key-read",
                    f"Could not read edge key CSV: {exc}",
                    str(resolved_edge_key_path),
                )
            )
        else:
            missing = set(EDGE_KEY_COLUMNS) - set(edge_key_df.columns)
            if missing:
                issues.append(
                    _issue(
                        "error",
                        "edge-key-columns",
                        f"edges_key.csv is missing columns: {', '.join(sorted(missing))}",
                        str(resolved_edge_key_path),
                    )
                )
            else:
                edge_key = load_edge_key(resolved_edge_key_path)

    issues.extend(validate_graph_data(nodes_df, edges_df, edge_key))
    return issues


def validate_graph_data(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    edge_key: dict[str, dict[str, str | bool]] | None = None,
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

    text_columns = _text_columns(nodes)
    cref_pairs: set[tuple[str, str]] = set()
    cref_targets_by_node: dict[str, set[str]] = {}
    for row_index, row in nodes.iterrows():
        node_id = str(row["id"]).strip()
        for column in text_columns:
            text = str(row.get(column, ""))
            location = _node_location(row_index, node_id, column)
            issues.extend(_validate_control_characters(text, location))
            issues.extend(_validate_backslash_end(text, location))
            issues.extend(_validate_balanced_braces(text, location))
            issues.extend(_validate_math_delimiters(text, location))
            issues.extend(_validate_custom_macro_typos(text, location))

            cref_calls, cref_errors = _parse_two_arg_macro_calls(text, "cref", location)
            issues.extend(cref_errors)
            for call in cref_calls:
                target = call.args[1].strip()
                cref_pairs.add((node_id, target))
                cref_targets_by_node.setdefault(node_id, set()).add(target)

            _, optional_errors = _parse_two_arg_macro_calls(text, "optional_details", location)
            issues.extend(optional_errors)

    node_ids = set(nodes["id"])
    for source, target in sorted(cref_pairs):
        if target not in node_ids:
            issues.append(
                _issue(
                    "error",
                    "cref-target",
                    f"\\cref target '{target}' is not a known concept id",
                    f"node {source}",
                )
            )

    if any(issue.severity == "error" for issue in issues):
        return issues

    issues.extend(_validate_cref_edge_consistency(nodes, edges, cref_pairs, cref_targets_by_node))
    issues.extend(_validate_study_questions(nodes))
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
        for column in ("id", "label", "layer", "layer_title", "definition_new"):
            if not str(row.get(column, "")).strip():
                issues.append(
                    _issue("error", "node-required-value", f"Concept has empty {column}", location)
                )

        layer = str(row.get("layer", "")).strip()
        if layer and parse_layer_value(node_id, layer) <= 0:
            issues.append(_issue("error", "node-layer", f"Layer is not an integer: {layer}", location))

    duplicate_ids = sorted(id_ for id_ in ids[ids.duplicated()].unique() if id_)
    for node_id in duplicate_ids:
        issues.append(_issue("error", "node-duplicate-id", f"Duplicate concept id '{node_id}'"))

    labels = nodes_df["label"].astype(str).str.strip()
    duplicate_labels = sorted(label for label in labels[labels.duplicated()].unique() if label)
    for label in duplicate_labels:
        issues.append(_issue("warning", "node-duplicate-label", f"Duplicate concept label '{label}'"))

    layer_titles: dict[str, set[str]] = {}
    for _, row in nodes_df.iterrows():
        layer = str(row.get("layer", "")).strip()
        title = str(row.get("layer_title", "")).strip()
        if layer and title:
            layer_titles.setdefault(layer, set()).add(title)
    for layer, titles in sorted(layer_titles.items(), key=lambda item: item[0]):
        if len(titles) > 1:
            issues.append(
                _issue(
                    "warning",
                    "layer-title",
                    f"Layer {layer} has multiple titles: {', '.join(sorted(titles))}",
                )
            )

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
        if name.startswith("optional") or name.startswith("cref"):
            issues.append(
                _issue(
                    "warning",
                    "text-unknown-custom-macro",
                    f"Unknown custom macro \\{name}; expected one of {', '.join(sorted(SUPPORTED_CUSTOM_MACROS))}",
                    location,
                )
            )
    return issues


def _parse_two_arg_macro_calls(
    text: str,
    name: str,
    location: str,
) -> tuple[list[MacroCall], list[ValidationIssue]]:
    calls: list[MacroCall] = []
    issues: list[ValidationIssue] = []
    macro = "\\" + name
    pos = 0
    while True:
        start = text.find(macro, pos)
        if start == -1:
            break
        after = start + len(macro)
        if after < len(text) and (text[after].isalnum() or text[after] == "_"):
            pos = after
            continue
        try:
            first_start = _skip_whitespace(text, after)
            arg1, first_end = _parse_braced_arg(text, first_start)
            second_start = _skip_whitespace(text, first_end)
            arg2, second_end = _parse_braced_arg(text, second_start)
        except ValueError as exc:
            issues.append(_issue("error", f"{name}-syntax", str(exc), location))
            pos = after
            continue
        calls.append(MacroCall(name=name, args=(arg1, arg2), start=start, end=second_end))
        pos = second_end
    return calls, issues


def _parse_braced_arg(text: str, index: int) -> tuple[str, int]:
    if index >= len(text) or text[index] != "{":
        raise ValueError("Expected braced macro argument")
    depth = 0
    arg_start = index + 1
    pos = index
    while pos < len(text):
        char = text[pos]
        if char == "\\" and pos + 1 < len(text) and text[pos + 1] in "{}\\":
            pos += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[arg_start:pos], pos + 1
        pos += 1
    raise ValueError("Unclosed braced macro argument")


def _skip_whitespace(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


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


def _validate_study_questions(nodes_df: pd.DataFrame) -> list[ValidationIssue]:
    issues = []
    question_numbers = sorted(
        {
            int(match.group(1))
            for column in nodes_df.columns
            for match in [re.fullmatch(r"study_question_(\d+)", str(column))]
            if match
        }
    )
    for row_index, row in nodes_df.iterrows():
        node_id = str(row["id"]).strip()
        for number in question_numbers:
            question = str(row.get(f"study_question_{number}", "")).strip()
            answer = str(row.get(f"study_answer_{number}", "")).strip()
            location = _node_location(row_index, node_id, f"study_question_{number}")
            if question and not answer:
                issues.append(_issue("warning", "study-answer-missing", "Study question has no answer", location))
            if answer and not question:
                issues.append(_issue("warning", "study-question-missing", "Study answer has no question", location))
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
        for edge in report.layer_forward_edges:
            issues.append(
                _issue(
                    "warning",
                    "directed-layer-forward",
                    (
                        f"{edge.source} {edge.source_label} [L{edge.source_layer}] "
                        f"{edge.relation} {edge.target} {edge.target_label} [L{edge.target_layer}]"
                    ),
                    report.name,
                )
            )
        for edge in report.same_layer_order_violations:
            issues.append(
                _issue(
                    "warning",
                    "directed-same-layer-order",
                    (
                        f"{edge.source} {edge.source_label} should come after "
                        f"{edge.target} {edge.target_label} for target-first ordering"
                    ),
                    report.name,
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


def _text_columns(nodes_df: pd.DataFrame) -> tuple[str, ...]:
    columns = list(BASE_TEXT_COLUMNS)
    for column in nodes_df.columns:
        if re.fullmatch(r"study_(question|answer)_\d+", str(column)):
            columns.append(str(column))
    return tuple(columns)


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
