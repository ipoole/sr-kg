"""PyVis network rendering for the SR knowledge graph.

This module converts prepared node, edge, relation, and layout data into the
base PyVis HTML file. It owns the PyVis ``Network`` object, native node/edge
attributes, relation colours, initial coordinates, and the temporary native node
representation used before the injected viewer customizes rendering.

It deliberately stops at writing PyVis output. It does not inject controls,
MathJax configuration, HTML labels, or application JavaScript; that belongs in
``srkg.html_injection``. It also assumes data frames have already been
validated and normalized by the pipeline.
"""

from pathlib import Path
import html
import math

import networkx as nx
import pandas as pd
from pyvis.network import Network

from srkg.config import (
    EDGE_ARROW_ENDPOINT_OFFSET,
    EDGE_WIDTH,
    NODE_CIRCLE_BASE_SIZE,
    NODE_CIRCLE_IMPORTANCE_SCALE,
    NODE_COLLISION_HEIGHT,
    NODE_COLLISION_WIDTH,
)
from srkg.edges import make_edge_tooltip, relation_is_directed, stable_edge_colour
from srkg.module_colours import UNKNOWN_MODULE_VISUAL


def write_pyvis_html(
    *,
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    edge_key: dict[str, dict[str, str | bool]],
    edge_colour_map: dict[str, str],
    hierarchy_levels: dict[str, int],
    hierarchy_positions: dict[str, tuple[float, float]],
    module_visuals_by_concept: dict[str, dict[str, str]] | None = None,
    out_path: Path,
    height: str,
    width: str,
) -> None:
    """Write the base PyVis HTML before viewer controls are injected."""
    graph = nx.DiGraph()
    for _, row in nodes_df.iterrows():
        graph.add_node(row["id"])
    for _, row in edges_df.iterrows():
        graph.add_edge(row["source"], row["target"])

    incoming = dict(graph.in_degree())

    net = Network(
        height=height,
        width=width,
        directed=True,
        bgcolor="#ffffff",
        font_color="#222222",
        notebook=False,
    )

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
        "endPointOffset": {
          "to": __EDGE_ARROW_ENDPOINT_OFFSET__
        },
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
        "enabled": false
      },
      "interaction": {
        "hover": true,
        "hoverConnectedEdges": false,
        "selectConnectedEdges": false,
        "navigationButtons": false,
        "keyboard": false,
        "tooltipDelay": 120
      }
    }
    """.replace(
        "__NODE_COLLISION_WIDTH__",
        str(NODE_COLLISION_WIDTH),
    ).replace(
        "__NODE_COLLISION_HEIGHT__",
        str(NODE_COLLISION_HEIGHT),
    ).replace(
        "__EDGE_ARROW_ENDPOINT_OFFSET__",
        str(EDGE_ARROW_ENDPOINT_OFFSET),
    ))

    node_labels = {}

    for _, row in nodes_df.iterrows():
        cid = row["id"]
        display_id = str(row.get("display_id", "")).strip() or str(cid)
        label = str(row.get("label", "")).strip()
        node_labels[str(cid)] = label or str(cid)
        module_visual = dict(
            (module_visuals_by_concept or {}).get(str(cid), UNKNOWN_MODULE_VISUAL)
        )
        module_id = str(module_visual.get("module_id", ""))
        background = str(module_visual.get("background", UNKNOWN_MODULE_VISUAL["background"]))
        border = str(module_visual.get("border", UNKNOWN_MODULE_VISUAL["border"]))

        title = f"{display_id} {html.escape(label)}"

        importance = incoming.get(cid, 0)
        size = NODE_CIRCLE_BASE_SIZE + NODE_CIRCLE_IMPORTANCE_SCALE * math.sqrt(importance + 1)
        x_pos, y_pos = hierarchy_positions.get(cid, (0, 0))

        net.add_node(
            cid,
            label=" ",
            title=title,
            shape="dot",
            moduleGroup=module_id,
            level=hierarchy_levels.get(cid, 0),
            x=x_pos,
            y=y_pos,
            size=size,
            visualSize=size,
            visualColor={
                "background": background,
                "border": border,
            },
            font={
                "size": 1,
                "color": "rgba(0,0,0,0)",
            },
            color={
                "background": background,
                "border": border,
                "highlight": {
                    "background": background,
                    "border": border,
                },
                "hover": {
                    "background": background,
                    "border": border,
                },
            },
        )

    for _, row in edges_df.iterrows():
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
            title=make_edge_tooltip(
                rel,
                note,
                source_label=node_labels.get(str(source), str(source)),
                target_label=node_labels.get(str(target), str(target)),
            ),
            relation=rel,
            note=note,
            arrows="to" if directed else "",
            color={
                "color": edge_colour,
                "highlight": edge_colour,
                "hover": edge_colour,
            },
            width=EDGE_WIDTH,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(str(out_path), notebook=False, open_browser=False)
