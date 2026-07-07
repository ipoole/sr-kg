#!/usr/bin/env python3
"""
generate_pyvis.py

Generate a standalone interactive HTML knowledge-graph viewer from nodes.csv and edges.csv.

This script is the command-line entry point only. It parses arguments, delegates
the generation workflow to srkg.pipeline, and prints a short summary.

Expected nodes.csv columns:
    id,label,layer,layer_title,definition_new,derivation_new,explanation_new

Expected edges.csv columns:
    source,target,relation,note

Expected edges_key.csv columns:
    relation,directed,category,meaning,example

Only the documented columns are supported.

Usage:
    python generate_pyvis.py --nodes data/nodes.csv --edges data/edges.csv --out interactive_graph.html

Dependencies:
    pip install pandas networkx pyvis
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srkg.pipeline import generate_viewer
from srkg.dag import format_dag_reports, load_dag_reports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", default="data/nodes.csv", help="Path to nodes.csv")
    parser.add_argument("--edges", default="data/edges.csv", help="Path to edges.csv")
    parser.add_argument(
        "--edge-key",
        default=None,
        help="Path to edges_key.csv. Defaults to edges_key.csv beside the edges file when present.",
    )
    parser.add_argument("--out", default="interactive_graph.html", help="Output HTML file")
    parser.add_argument("--height", default="100vh")
    parser.add_argument("--width", default="100%")
    parser.add_argument(
        "--title",
        nargs="+",
        default=["Knowledge Graph"],
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
    args = parser.parse_args()

    if args.dag_report or args.dag_report_only:
        reports = load_dag_reports(
            nodes_path=args.nodes,
            edges_path=args.edges,
            edge_key_path=args.edge_key,
            relations=args.dag_relations,
        )
        print(format_dag_reports(reports))
        if args.dag_report_only:
            return

    out_path, node_count, edge_count, edge_key_path, edge_key_count = generate_viewer(
        nodes_path=args.nodes,
        edges_path=args.edges,
        edge_key_path=args.edge_key,
        out_path=args.out,
        height=args.height,
        width=args.width,
        title=" ".join(args.title),
    )

    print(f"Wrote {out_path}")
    print(f"Nodes: {node_count}")
    print(f"Edges: {edge_count}")
    if edge_key_path:
        print(f"Edge key: {edge_key_path} ({edge_key_count} relation types)")


if __name__ == "__main__":
    main()
