#!/usr/bin/env python3
"""
generate_pyvis.py

Generate a standalone interactive HTML knowledge-graph viewer from nodes.csv and knowledge_edges.csv.

Expected nodes.csv columns:
    id,label,layer,layer_title,body

Expected knowledge_edges.csv columns:
    source,target,relation,note

Expected edges_key.csv columns:
    relation,directed,category,meaning,example

Only the documented columns are supported.

Usage:
    python generate_pyvis.py --nodes nodes.csv --edges knowledge_edges.csv --out interactive_graph.html

Dependencies:
    pip install pandas networkx pyvis
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srkg.data import (
    build_concept_data,
    find_edge_key_path,
    load_edge_key,
    normalise_edges,
)
from srkg.edges import (
    build_edge_colour_map,
    enrich_edge_key_with_colours,
)
from srkg.html_injection import inject_controls
from srkg.layout import (
    build_hierarchy_levels,
    build_hierarchy_positions,
)
from srkg.render_pyvis import write_pyvis_html


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", default="nodes.csv", help="Path to nodes.csv")
    parser.add_argument("--edges", default="data/knowledge_edges.csv", help="Path to knowledge_edges.csv")
    parser.add_argument(
        "--edge-key",
        default=None,
        help="Path to edges_key.csv. Defaults to edges_key.csv beside the edges file when present.",
    )
    parser.add_argument("--out", default="interactive_graph.html", help="Output HTML file")
    parser.add_argument("--height", default="100vh")
    parser.add_argument("--width", default="100%")
    args = parser.parse_args()

    edges_path = Path(args.edges)
    edge_key_path = find_edge_key_path(edges_path, args.edge_key)

    nodes_df = pd.read_csv(args.nodes).fillna("")
    edges_df = pd.read_csv(edges_path).fillna("")
    edge_key = load_edge_key(edge_key_path)
    edge_colour_map = build_edge_colour_map(edge_key)

    if "id" not in nodes_df.columns:
        raise ValueError("nodes.csv must contain an 'id' column")

    edges_df = normalise_edges(edges_df)

    # Normalise IDs as strings.
    nodes_df["id"] = nodes_df["id"].astype(str)
    edges_df["source"] = edges_df["source"].astype(str)
    edges_df["target"] = edges_df["target"].astype(str)

    node_ids = set(nodes_df["id"])
    edges_df = edges_df[edges_df["source"].isin(node_ids) & edges_df["target"].isin(node_ids)].copy()
    hierarchy_levels = build_hierarchy_levels(nodes_df)
    hierarchy_positions = build_hierarchy_positions(hierarchy_levels, edges_df)

    concept_data = build_concept_data(nodes_df)

    out_path = Path(args.out)
    write_pyvis_html(
        nodes_df=nodes_df,
        edges_df=edges_df,
        edge_key=edge_key,
        edge_colour_map=edge_colour_map,
        hierarchy_levels=hierarchy_levels,
        hierarchy_positions=hierarchy_positions,
        out_path=out_path,
        height=args.height,
        width=args.width,
    )

    html_text = out_path.read_text(encoding="utf-8")
    html_text = inject_controls(
        html_text,
        concept_data,
        enrich_edge_key_with_colours(edge_key, edge_colour_map),
    )
    out_path.write_text(html_text, encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"Nodes: {len(nodes_df)}")
    print(f"Edges: {len(edges_df)}")
    if edge_key_path:
        print(f"Edge key: {edge_key_path} ({len(edge_key)} relation types)")


if __name__ == "__main__":
    main()
