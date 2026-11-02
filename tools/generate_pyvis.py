#!/usr/bin/env python3
"""
generate_pyvis.py

Generate a standalone interactive HTML knowledge-graph viewer from a KB data root.

This script is the command-line entry point only. It parses arguments, delegates
the generation workflow to srkg.pipeline, and prints a short summary.

Expected manifest-backed nodes.csv columns:
    id,display_id,label,domain,domain_title

Expected manifest-backed content_blocks.csv columns:
    block_id,concept_id,sequence,kind,title,body

Expected manifest-backed study_questions.csv columns:
    question_id,concept_id,sequence,question_type,marking_mode,prompt,answer

Expected manifest-backed study_question_options.csv columns:
    question_id,option_id,sequence,text,is_correct

Expected manifest-backed references.csv columns:
    reference_id,reference_type,citation,authors,title,year,url,note

Expected manifest-backed reference_links.csv columns:
    source_type,source_id,reference_id,locator,note

Expected optional manifest-backed modules.csv columns:
    module_id,domain,title,sequence,default_collapsed

Expected optional manifest-backed module_members.csv columns:
    module_id,concept_id,sequence

Expected optional manifest-backed module_supports.csv columns:
    module_id,target_type,target_id,role,note

Expected optional manifest-backed module_content_blocks.csv columns:
    block_id,module_id,sequence,kind,title,body

Expected edges.csv columns:
    source,target,relation,note

Expected edges_key.csv columns:
    relation,directed,category,meaning,example

Only the documented columns are supported.

Usage:
    python generate_pyvis.py --data-root data --out PhysicsKG.html

Dependencies:
    pip install pandas networkx pyvis
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srkg.branding import PRODUCT_TITLE
from srkg.config import DEFAULT_GOOGLE_DRIVE_CLIENT_ID
from srkg.pipeline import generate_viewer_from_root, load_viewer_knowledge_base
from srkg.domain_references import format_build_warnings
from srkg.dag import format_dag_reports, build_dag_reports, directed_relations
from srkg.module_diagnostics import (
    format_module_diagnostics,
    build_module_diagnostics,
)
from srkg.validation import (
    format_validation_issues,
    has_validation_errors,
    validate_knowledge_base,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the graph viewer generator."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-root",
        default="data",
        help="Path to a KB data root containing manifest.yaml.",
    )
    parser.add_argument("--out", default="PhysicsKG.html", help="Output HTML file")
    parser.add_argument("--height", default="100vh")
    parser.add_argument("--width", default="100%")
    parser.add_argument(
        "--google-drive-client-id",
        default=os.environ.get(
            "PHYSICSKG_GOOGLE_DRIVE_CLIENT_ID",
            DEFAULT_GOOGLE_DRIVE_CLIENT_ID,
        ),
        help=(
            "Google OAuth web-client ID for optional personal-data sync. "
            "PHYSICSKG_GOOGLE_DRIVE_CLIENT_ID overrides the project default."
        ),
    )
    parser.add_argument(
        "--title",
        nargs="+",
        default=[PRODUCT_TITLE],
        help="Title shown at the top of the viewer",
    )
    parser.add_argument(
        "--dag-report",
        action="store_true",
        help=(
            "Print DAG diagnostics for directed relations before writing "
            "the viewer."
        ),
    )
    parser.add_argument(
        "--dag-report-only",
        action="store_true",
        help="Print DAG diagnostics and skip HTML generation.",
    )
    parser.add_argument(
        "--dag-relations",
        nargs="+",
        default=None,
        help=(
            "Relations to include in DAG diagnostics. Defaults to all "
            "relations marked directed in edges_key.csv."
        ),
    )
    parser.add_argument(
        "--module-report",
        action="store_true",
        help=(
            "Print module boundary, support, and quotient DAG diagnostics "
            "before writing the viewer."
        ),
    )
    parser.add_argument(
        "--module-report-only",
        action="store_true",
        help="Print module diagnostics and skip HTML generation.",
    )
    parser.add_argument(
        "--module-relations",
        nargs="+",
        default=None,
        help=(
            "Relations to include in module diagnostics. Defaults to "
            "REQUIRES, DERIVES_FROM, and CONSTRUCTED_FROM."
        ),
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate source CSV data before writing the viewer.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate source CSV data and skip HTML generation.",
    )
    parser.add_argument(
        "--validation-strict",
        action="store_true",
        help="Treat validation warnings as failures.",
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        default=None,
        help=(
            "Only render concepts from the listed domain(s). Uses nodes.csv "
            "'domain' when present, otherwise the semantic id prefix before '.'."
        ),
    )
    parser.add_argument(
        "--relations",
        nargs="+",
        default=None,
        help=(
            "Only include the listed edge relations in the generated viewer. "
            "Source CSV data is not changed."
        ),
    )
    parser.add_argument(
        "--also-load-linked-concepts",
        action="store_true",
        help="Legacy single-root option; collection builds retain only the explicitly selected domains.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    reports_seen = set()
    missing_domains = set()
    def report_warnings(warnings):
        missing_domains.update(warning.domain for warning in warnings)
        report = format_build_warnings(warnings)
        if report and report not in reports_seen:
            print(report, file=sys.stderr)
            reports_seen.add(report)

    if any((args.dag_report, args.dag_report_only, args.module_report, args.module_report_only,
            args.validate, args.validate_only)):
        kb = load_viewer_knowledge_base(args.data_root, domains=args.domains,
            also_load_linked_concepts=args.also_load_linked_concepts, include_graphics=False)
        report_warnings(kb.build_warnings)

    if args.dag_report or args.dag_report_only:
        relations = args.dag_relations if args.dag_relations is not None else directed_relations(kb.edges_df, kb.edge_key)
        if not relations:
            raise ValueError("No directed relations found for DAG diagnostics")
        reports = build_dag_reports(kb.nodes_df, kb.edges_df, relations)
        print(format_dag_reports(reports))
        if args.dag_report_only:
            return

    if args.module_report or args.module_report_only:
        diagnostics = build_module_diagnostics(
            kb,
            relations=args.module_relations,
        )
        print(format_module_diagnostics(diagnostics))
        if args.module_report_only:
            return

    if args.validate or args.validate_only:
        issues = validate_knowledge_base(kb)
        print(format_validation_issues(issues))
        if has_validation_errors(issues, strict=args.validation_strict):
            raise SystemExit(1)
        if args.validate_only:
            return

    out_path, node_count, edge_count, edge_key_path, edge_key_count = (
        generate_viewer_from_root(
            data_root=args.data_root,
            out_path=args.out,
            height=args.height,
            width=args.width,
            title=" ".join(args.title),
            domains=args.domains,
            also_load_linked_concepts=args.also_load_linked_concepts,
            relations=args.relations,
            google_drive_client_id=args.google_drive_client_id,
            warning_handler=report_warnings,
        )
    )

    print(f"Wrote {out_path}")
    print(f"Nodes: {node_count}")
    print(f"Edges: {edge_count}")
    if edge_key_path:
        print(f"Edge key: {edge_key_path} ({edge_key_count} relation types)")
    if missing_domains:
        print("Missing domains: " + ", ".join(sorted(missing_domains)))


if __name__ == "__main__":
    main()
