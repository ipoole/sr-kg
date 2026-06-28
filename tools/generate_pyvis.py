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
import html
import math
import re
import sys
from pathlib import Path

import pandas as pd
import networkx as nx
from pyvis.network import Network

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srkg.config import (
    EDGE_WIDTH,
    LAYER_COLOURS,
    NODE_COLLISION_HEIGHT,
    NODE_COLLISION_WIDTH,
)
from srkg.data import (
    build_concept_data,
    find_edge_key_path,
    load_edge_key,
    normalise_edges,
)
from srkg.edges import (
    build_edge_colour_map,
    enrich_edge_key_with_colours,
    make_edge_tooltip,
    relation_is_directed,
    stable_edge_colour,
)
from srkg.html_injection import inject_controls
from srkg.layout import (
    build_hierarchy_levels,
    build_hierarchy_positions,
    concept_sort_key,
)


def strip_latex(text: str, max_chars: int = 700) -> str:
    """Crude but useful LaTeX-to-plain-text cleanup for hover tooltips."""
    if not isinstance(text, str):
        return ""

    s = text

    # Replace concept refs with readable text.
    s = re.sub(r"\\cref\{([^}]*)\}\{([^}]*)\}", r"\1 [\2]", s)

    # Remove common display math wrappers but keep contents.
    s = re.sub(r"\\\[(.*?)\\\]", r"\1", s, flags=re.S)
    s = re.sub(r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}", r"\1", s, flags=re.S)
    s = re.sub(r"\\begin\{align\*?\}(.*?)\\end\{align\*?\}", r"\1", s, flags=re.S)

    # Remove simple LaTeX commands but preserve their braced content.
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textit\{([^}]*)\}", r"\1", s)

    # Drop remaining command names but leave following text.
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)

    # Clean LaTeX punctuation.
    s = s.replace("~", " ")
    s = s.replace("\\,", " ")
    s = s.replace("\\;", " ")
    s = s.replace("\\:", " ")
    s = s.replace("\\!", "")
    s = s.replace("$", "")

    # Whitespace.
    s = re.sub(r"\s+", " ", s).strip()

    if len(s) > max_chars:
        s = s[:max_chars].rstrip() + "..."
    return s


def make_tooltip(node: dict, prerequisites: list[str], dependents: list[str]) -> str:
    cid = html.escape(str(node.get("id", "")))
    label = html.escape(str(node.get("label", "")))
    layer = html.escape(str(node.get("layer", "")))
    layer_title = html.escape(str(node.get("layer_title", "")))
    body = html.escape(strip_latex(str(node.get("body", ""))))

    prereq_html = "<br>".join(html.escape(x) for x in prerequisites[:12])
    dep_html = "<br>".join(html.escape(x) for x in dependents[:12])

    if len(prerequisites) > 12:
        prereq_html += f"<br>... {len(prerequisites) - 12} more"
    if len(dependents) > 12:
        dep_html += f"<br>... {len(dependents) - 12} more"

    return f"""
    <div style="max-width:520px; white-space:normal;">
      <b>{cid} {label}</b><br>
      <i>Layer {layer}: {layer_title}</i>
      <hr>
      <b>Definition / note</b><br>
      {body}
      <hr>
      <b>References / prerequisites</b><br>
      {prereq_html if prereq_html else "<i>none</i>"}
      <br><br>
      <b>Referenced by / dependents</b><br>
      {dep_html if dep_html else "<i>none</i>"}
    </div>
    """


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

    G = nx.DiGraph()
    for _, row in nodes_df.iterrows():
        G.add_node(row["id"])
    for _, row in edges_df.iterrows():
        G.add_edge(row["source"], row["target"])

    incoming = dict(G.in_degree())
    outgoing = dict(G.out_degree())

    # Lookup labels for neighbours.
    label_lookup = {
        row["id"]: f'{row["id"]} {row.get("label", "")}'.strip()
        for _, row in nodes_df.iterrows()
    }

    net = Network(
        height=args.height,
        width=args.width,
        directed=True,
        bgcolor="#ffffff",
        font_color="#222222",
        notebook=False,
    )

    # Physics and interaction options.
    net.set_options("""
    {
      "nodes": {
        "shape": "box",
        "borderWidth": 0,
        "font": {
          "size": 1,
          "face": "arial",
          "multi": true,
          "color": "rgba(0,0,0,0)"
        },
        "margin": {
          "top": 0,
          "right": 0,
          "bottom": 0,
          "left": 0
        },
        "widthConstraint": {
          "minimum": __NODE_COLLISION_WIDTH__,
          "maximum": __NODE_COLLISION_WIDTH__
        },
        "heightConstraint": {
          "minimum": __NODE_COLLISION_HEIGHT__,
          "valign": "middle"
        },
        "color": {
          "background": "rgba(255,255,255,0)",
          "border": "rgba(255,255,255,0)",
          "highlight": {
            "background": "rgba(255,255,255,0)",
            "border": "rgba(255,255,255,0)"
          },
          "hover": {
            "background": "rgba(255,255,255,0)",
            "border": "rgba(255,255,255,0)"
          }
        }
      },
      "layout": {
        "improvedLayout": false
      },
      "edges": {
        "chosen": false,
        "selectionWidth": 0,
        "hoverWidth": 0,
        "arrows": {
          "to": {
            "enabled": false,
            "scaleFactor": 2.0
          }
        },
        "smooth": {
          "enabled": true,
          "type": "cubicBezier",
          "forceDirection": "vertical",
          "roundness": 0.35
        },
        "color": {
          "color": "#999999",
          "opacity": 0.35
        },
        "width": 1
      },
      "physics": {
        "enabled": true,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
            "gravitationalConstant": -100,
            "centralGravity": 0.0,
            "springLength": 100,
            "springConstant": 0.008,
            "damping": 0.85,
            "avoidOverlap": 1.0
        },
        "stabilization": {
          "enabled": true,
          "iterations": 50,
          "fit": true
        },
        "minVelocity": 1.5
      },
      "interaction": {
        "hover": true,
        "hoverConnectedEdges": false,
        "selectConnectedEdges": false,
        "navigationButtons": true,
        "keyboard": true,
        "tooltipDelay": 120
      }
    }
    """.replace("__NODE_COLLISION_WIDTH__", str(NODE_COLLISION_WIDTH)).replace("__NODE_COLLISION_HEIGHT__", str(NODE_COLLISION_HEIGHT)))

    for _, row in nodes_df.iterrows():
        cid = row["id"]
        label = str(row.get("label", "")).strip()
        layer = str(row.get("layer", "")).strip()

        try:
            layer_int = int(float(layer))
        except Exception:
            layer_int = 0

        colour = LAYER_COLOURS[(layer_int - 1) % len(LAYER_COLOURS)] if layer_int > 0 else "#999999"

        prereq_ids = sorted(list(G.successors(cid)), key=concept_sort_key)
        dependent_ids = sorted(list(G.predecessors(cid)), key=concept_sort_key)
        prereqs = [label_lookup.get(x, x) for x in prereq_ids]
        dependents = [label_lookup.get(x, x) for x in dependent_ids]

        title = f"{cid} {html.escape(label)}"

        # Node size mainly reflects how many other concepts point to it.
        importance = incoming.get(cid, 0)
        size = 40 + 4.0 * math.sqrt(importance + 1)
        x_pos, y_pos = hierarchy_positions.get(cid, (0, 0))

        net.add_node(
            cid,
            label=" ",
            title=title,
            shape="dot",
            layerGroup=layer_int,
            level=hierarchy_levels.get(cid, 0),
            x=x_pos,
            y=y_pos,
            fixed={
                "x": False,
                "y": True,
            },
            size=size,
            visualSize=size,
            visualColor={
                "background": colour,
                "border": "#333333",
            },
            font={
                "size": 1,
                "color": "rgba(0,0,0,0)",
            },
            color={
                "background": colour,
                "border": "#333333",
                "highlight": {
                    "background": colour,
                    "border": "#000000",
                },
                "hover": {
                    "background": colour,
                    "border": "#000000",
                },
            },
        )

    for i, row in edges_df.iterrows():
        source = row["source"]
        target = row["target"]
        rel = str(row.get("relation", "REFERENCE") or "REFERENCE")
        directed = relation_is_directed(rel, edge_key)
        edge_colour = edge_colour_map.get(
            rel,
            stable_edge_colour(rel),
        )
        note = str(row.get("note", "")).strip()

        net.add_edge(
            source,
            target,
            title=make_edge_tooltip(rel, note),
            relation=rel,
            arrows="to" if directed else "",
            color={
                "color": edge_colour,
                "highlight": edge_colour,
                "hover": edge_colour,
            },
            width=EDGE_WIDTH,
        )

    concept_data = build_concept_data(nodes_df)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(str(out_path), notebook=False, open_browser=False)

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
