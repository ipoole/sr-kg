#!/usr/bin/env python3
"""
generate_pyvis.py

Generate a standalone interactive HTML knowledge-graph viewer from nodes.csv and edges.csv.

Expected nodes.csv columns:
    id,label,layer,layer_title,body

Expected edges.csv columns:
    source,target,type

The edge relation column may be named either type or relation. Optional note/notes
columns are shown in edge hover text.

Expected edges_key.csv columns:
    relation,directed,category,meaning,example

Only id/source/target are strictly required. Other columns are used when present.

Usage:
    python generate_pyvis.py --nodes nodes.csv --edges edges.csv --out interactive_graph.html

Dependencies:
    pip install pandas networkx pyvis
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import textwrap
from pathlib import Path

import pandas as pd
import networkx as nx
from pyvis.network import Network


LAYER_COLOURS = [
    "#e6194b", "#f58231", "#ffe119", "#3cb44b", "#46f0f0",
    "#4363d8", "#911eb4", "#f032e6", "#fabed4", "#9a6324",
    "#808080", "#469990", "#dcbeff", "#aaffc3"
]

EDGE_RELATION_COLUMNS = ("type", "relation")
EDGE_NOTE_COLUMNS = ("note", "notes")
EDGE_KEY_COLUMNS = ("relation", "directed", "category", "meaning", "example")
EDGE_TOOLTIP_LINE_WIDTH = 50
EDGE_WIDTH = 5.0
LAYOUT_X_SPACING = 600
LAYOUT_Y_SPACING = 320
LAYOUT_ROW_STAGGER = 70
NODE_COLLISION_WIDTH = 280
NODE_COLLISION_HEIGHT = 170
NODE_LABEL_WIDTH = 180
NODE_LABEL_FONT_SIZE = 28
UNDIRECTED_EDGE_COLOUR = "#c8c8c8"
EDGE_COLOURS = [
    "#1f77b4",
    "#d62728",
    "#2ca02c",
    "#9467bd",
    "#ff7f0e",
    "#17becf",
    "#8c564b",
    "#e377c2",
]


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


def concept_sort_key(cid: str):
    """Sort concept IDs like 3.12 numerically."""
    try:
        return tuple(int(x) for x in str(cid).split("."))
    except Exception:
        return (9999, str(cid))


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


def build_concept_data(nodes_df: pd.DataFrame) -> dict[str, dict[str, str]]:
    """Build panel data directly from nodes.csv, independent of PyVis metadata."""
    concept_data = {}
    for _, row in nodes_df.iterrows():
        cid = str(row.get("id", "")).strip()
        if not cid:
            continue
        concept_data[cid] = {
            "label": str(row.get("label", "")).strip(),
            "layer": str(row.get("layer", "")).strip(),
            "layer_title": str(row.get("layer_title", "")).strip(),
            "body": str(row.get("body", "")),
        }
    return concept_data


def normalise_edges(edges_df: pd.DataFrame) -> pd.DataFrame:
    """Validate and standardise edge data from supported CSV variants."""
    if not {"source", "target"}.issubset(edges_df.columns):
        raise ValueError("edges.csv must contain 'source' and 'target' columns")

    edges_df = edges_df.copy()

    relation_column = next((col for col in EDGE_RELATION_COLUMNS if col in edges_df.columns), None)
    if relation_column is None:
        edges_df["relation"] = "REFERENCE"
    else:
        edges_df["relation"] = edges_df[relation_column].replace("", "REFERENCE")

    note_column = next((col for col in EDGE_NOTE_COLUMNS if col in edges_df.columns), None)
    edges_df["note"] = edges_df[note_column] if note_column else ""

    return edges_df


def parse_bool(value, default: bool = True) -> bool:
    """Parse common CSV boolean spellings."""
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"true", "t", "yes", "y", "1"}:
        return True
    if text in {"false", "f", "no", "n", "0"}:
        return False
    return default


def load_edge_key(path: Path | None) -> dict[str, dict[str, str | bool]]:
    """Load relation metadata that controls edge direction and help text."""
    if path is None or not path.exists():
        return {}

    edge_key_df = pd.read_csv(path).fillna("")
    missing = set(EDGE_KEY_COLUMNS) - set(edge_key_df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"{path} must contain columns: {missing_cols}")

    edge_key = {}
    for _, row in edge_key_df.iterrows():
        relation = str(row.get("relation", "")).strip()
        if not relation:
            continue
        edge_key[relation] = {
            "relation": relation,
            "directed": parse_bool(row.get("directed", ""), default=True),
            "category": str(row.get("category", "")).strip(),
            "meaning": str(row.get("meaning", "")).strip(),
            "example": str(row.get("example", "")).strip(),
        }
    return edge_key


def build_edge_colour_map(edge_key: dict[str, dict[str, str | bool]]) -> dict[str, str]:
    """Assign stable colours to relation types, using grey for undirected edges."""
    colour_map = {}
    directed_relations = sorted(
        relation
        for relation, metadata in edge_key.items()
        if bool(metadata.get("directed", True))
    )

    for index, relation in enumerate(directed_relations):
        colour_map[relation] = EDGE_COLOURS[index % len(EDGE_COLOURS)]

    for relation, metadata in edge_key.items():
        if not bool(metadata.get("directed", True)):
            colour_map[relation] = UNDIRECTED_EDGE_COLOUR

    return colour_map


def stable_edge_colour(relation: str) -> str:
    """Return a repeatable fallback colour for relation names not present in the key."""
    digest = hashlib.sha256(relation.encode("utf-8")).digest()
    return EDGE_COLOURS[digest[0] % len(EDGE_COLOURS)]


def enrich_edge_key_with_colours(
    edge_key: dict[str, dict[str, str | bool]],
    edge_colour_map: dict[str, str],
) -> dict[str, dict[str, str | bool]]:
    """Add generated display colours to edge-key metadata shown in the UI."""
    return {
        relation: {
            **metadata,
            "colour": edge_colour_map.get(relation, EDGE_COLOURS[0]),
        }
        for relation, metadata in edge_key.items()
    }


def relation_is_directed(relation: str, edge_key: dict[str, dict[str, str | bool]]) -> bool:
    """Return whether a relation should be treated as directed."""
    return bool(edge_key.get(relation, {}).get("directed", True))


def build_hierarchy_levels(
    node_ids: list[str],
    edges_df: pd.DataFrame,
    edge_key: dict[str, dict[str, str | bool]],
) -> dict[str, int]:
    """Assign best-effort top-to-bottom levels from directed edges.

    Directed edge orientation is source -> target, so larger levels place edge
    targets lower in a top-down hierarchical layout. Cycles are collapsed into
    strongly connected components before ranking.
    """
    directed_graph = nx.DiGraph()
    directed_graph.add_nodes_from(node_ids)

    for _, row in edges_df.iterrows():
        relation = str(row.get("relation", "REFERENCE") or "REFERENCE")
        if relation_is_directed(relation, edge_key):
            directed_graph.add_edge(row["source"], row["target"])

    components = list(nx.strongly_connected_components(directed_graph))
    node_to_component = {}
    for index, component in enumerate(components):
        for node_id in component:
            node_to_component[node_id] = index

    component_graph = nx.DiGraph()
    component_graph.add_nodes_from(range(len(components)))
    for source, target in directed_graph.edges():
        source_component = node_to_component[source]
        target_component = node_to_component[target]
        if source_component != target_component:
            component_graph.add_edge(source_component, target_component)

    component_levels = {component: 0 for component in component_graph.nodes()}
    for component in nx.topological_sort(component_graph):
        for target in component_graph.successors(component):
            component_levels[target] = max(
                component_levels[target],
                component_levels[component] + 1,
            )

    return {
        node_id: component_levels[node_to_component[node_id]]
        for node_id in node_ids
    }


def build_hierarchy_positions(
    hierarchy_levels: dict[str, int],
    x_spacing: int = LAYOUT_X_SPACING,
    y_spacing: int = LAYOUT_Y_SPACING,
    row_stagger: int = LAYOUT_ROW_STAGGER,
) -> dict[str, tuple[float, float]]:
    """Place nodes in compact staggered rows derived from hierarchy levels."""
    nodes_by_level: dict[int, list[str]] = {}
    for node_id, level in hierarchy_levels.items():
        nodes_by_level.setdefault(level, []).append(node_id)

    positions = {}
    for level, level_nodes in nodes_by_level.items():
        sorted_nodes = sorted(level_nodes, key=concept_sort_key)
        row_width = (len(sorted_nodes) - 1) * x_spacing
        for index, node_id in enumerate(sorted_nodes):
            stagger = 0
            if len(sorted_nodes) > 1:
                stagger = ((index % 3) - 1) * row_stagger
            positions[node_id] = (
                (index * x_spacing) - (row_width / 2),
                (level * y_spacing) + stagger,
            )

    return positions


def make_edge_tooltip(relation: str, note: str, width: int = EDGE_TOOLTIP_LINE_WIDTH) -> str:
    """Build a readable wrapped tooltip for an edge relation and optional note."""
    relation_text = html.escape(relation)
    note = str(note or "").strip()
    if not note:
        return relation_text

    wrapped_note = textwrap.wrap(
        note,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    wrapped_note_text = "\n".join(html.escape(line) for line in wrapped_note)
    return f"{relation_text}:\n{wrapped_note_text}"


def find_edge_key_path(edges_path: Path, configured_path: str | None) -> Path | None:
    """Use an explicit edge key, or edges_key.csv beside the edge file when present."""
    if configured_path:
        return Path(configured_path)

    sibling = edges_path.parent / "edges_key.csv"
    if sibling.exists():
        return sibling

    return None


def inject_controls(
    html_text: str,
    concept_data: dict[str, dict[str, str]],
    edge_key: dict[str, dict[str, str | bool]],
) -> str:
    """Inject a small control panel and useful vis.js event handlers."""
    mathjax = """
    <script>
      window.MathJax = {
        tex: {
          inlineMath: [['\\\\(', '\\\\)']],
          displayMath: [['\\\\[', '\\\\]']],
          processEscapes: true
        },
        svg: {
          fontCache: 'global'
        }
      };
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
    """

    css = """
    <style>
      #kg_controls {
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 10px;
        font-family: Arial, sans-serif;
        font-size: 13px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.18);
        max-width: 320px;
      }
      #kg_controls input {
        width: 210px;
        padding: 4px;
      }
      #kg_controls button {
        margin-top: 6px;
        margin-right: 4px;
        padding: 4px 8px;
      }
      #kg_status {
        margin-top: 6px;
        font-size: 12px;
        color: #333;
      }
      #kg_legend {
        margin-top: 8px;
        max-height: 180px;
        overflow-y: auto;
        font-size: 12px;
      }
      #kg_edge_filters {
        margin-top: 8px;
        border-top: 1px solid #ddd;
        padding-top: 8px;
        font-size: 12px;
      }
      .kg-edge-filter {
        align-items: center;
        display: flex;
        gap: 5px;
        margin: 3px 0;
      }
      .kg-edge-filter input {
        width: auto;
      }
      .kg-edge-filter-swatch {
        border: 1px solid #777;
        display: inline-block;
        height: 9px;
        width: 16px;
      }
      .kg-edge-filter-label {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      #kg_concept_list {
        margin-top: 8px;
        max-height: 260px;
        overflow-y: auto;
        border-top: 1px solid #ddd;
        padding-top: 8px;
        font-size: 12px;
      }
      .kg-concept-item {
        display: block;
        width: 100%;
        border: 0;
        border-radius: 4px;
        background: transparent;
        color: #222;
        cursor: pointer;
        font: inherit;
        margin: 0;
        padding: 4px 5px;
        text-align: left;
      }
      .kg-concept-item:hover,
      .kg-concept-item:focus {
        background: #eef3fd;
        outline: none;
      }
      .kg-concept-item.active {
        background: #dbe8ff;
        font-weight: 700;
      }
      .kg-concept-id {
        color: #555;
        font-variant-numeric: tabular-nums;
      }
      .legend-dot {
        display: inline-block;
        width: 11px;
        height: 11px;
        border-radius: 50%;
        margin-right: 5px;
        vertical-align: middle;
      }

      #mynetwork {
        position: relative;
      }

      #kg_node_labels {
        bottom: 0;
        left: 0;
        overflow: hidden;
        pointer-events: none;
        position: absolute;
        right: 0;
        top: 0;
        z-index: 5;
      }

      .kg-node-label {
        box-sizing: border-box;
        color: #111;
        display: block;
        font-family: Arial, sans-serif;
        font-size: __NODE_LABEL_FONT_SIZE__px;
        line-height: 1.2;
        overflow-wrap: anywhere;
        position: absolute;
        text-align: center;
        text-shadow:
          -1px -1px 0 rgba(255,255,255,0.9),
          1px -1px 0 rgba(255,255,255,0.9),
          -1px 1px 0 rgba(255,255,255,0.9),
          1px 1px 0 rgba(255,255,255,0.9);
        white-space: normal;
        width: __NODE_LABEL_WIDTH__px;
      }

      .kg-node-label mjx-container {
        display: inline-block;
        margin: 0 !important;
        vertical-align: -0.15em;
      }

      .kg-node-label-id {
        color: #333;
        display: block;
        font-variant-numeric: tabular-nums;
        font-weight: 700;
      }
    
    #info_panel {
        position: fixed;
        top: 12px;
        right: 12px;
        width: 420px;
        height: 90vh;
        overflow-y: auto;

        background: rgba(255,255,255,0.97);
        border: 1px solid #ccc;
        border-radius: 8px;

        padding: 12px;

        font-family: Arial, sans-serif;
        font-size: 14px;

        box-shadow: 0 2px 8px rgba(0,0,0,0.18);

        z-index: 9998;
    }

    #info_panel .concept-body {
        white-space: pre-wrap;
        font-family: inherit;
        line-height: 1.45;
    }

    #info_panel mjx-container[display="true"] {
        overflow-x: auto;
        overflow-y: hidden;
        max-width: 100%;
        padding: 4px 0;
    }

    #info_panel strong {
        font-weight: 700;
    }

    #info_panel .concept-link {
        color: #174ea6;
        text-decoration: none;
        cursor: pointer;
    }

    #info_panel .concept-link:hover,
    #info_panel .concept-link:focus {
        text-decoration: underline;
    }

    #info_panel .edge-key-table {
        border-collapse: collapse;
        font-size: 13px;
        width: 100%;
    }

    #info_panel .edge-key-table th,
    #info_panel .edge-key-table td {
        border: 1px solid #ddd;
        padding: 6px;
        text-align: left;
        vertical-align: top;
    }

    #info_panel .edge-key-table th {
        background: #f4f4f4;
    }

    #info_panel .edge-colour-swatch {
        border: 1px solid #777;
        display: inline-block;
        height: 10px;
        margin-right: 6px;
        vertical-align: -1px;
        width: 18px;
    }

    div.vis-tooltip {
        z-index: 10000 !important;
        max-width: 380px;
        padding: 6px 8px;
        background: #ffffff;
        border: 1px solid #b8b8b8;
        color: #222;
        font-family: Arial, sans-serif;
        font-size: 12px;
        white-space: pre-line;
        line-height: 1.35;
        box-shadow: 0 2px 6px rgba(0,0,0,0.18);
    }
    </style>
    """

    controls = """
    <div id="kg_controls">
      <b>Knowledge graph explorer</b><br>
      <input id="kg_search" placeholder="Search ID or title, e.g. 3.1 or Lorentz">
      <button onclick="kgSearch()">Find</button>
      <button onclick="kgReset()">Reset</button>
      <br>
      <button onclick="kgFocusSelected()">Neighbourhood</button>
      <button onclick="kgShowAll()">Show all</button>
      <button onclick="kgShowEdgeKey()">Edge key</button>
      <button onclick="kgFreezeLayout()">Freeze</button>
      <button onclick="kgRestartLayout()">Restart layout</button>
      <div id="kg_status">Click a node to highlight its immediate neighbours.</div>
      <div id="kg_legend"></div>
      <div id="kg_edge_filters"></div>
      <div id="kg_concept_list"></div>
    </div>

    <div id="info_panel">
      <h2>Knowledge Graph</h2>
      <p>Click a concept node to view details.</p>
    </div>
    """

    concept_data_json = json.dumps(concept_data, ensure_ascii=False).replace("</", "<\\/")
    edge_key_json = json.dumps(edge_key, ensure_ascii=False).replace("</", "<\\/")

    js = """
    <script type="text/javascript">
      var conceptData = __CONCEPT_DATA__;
      var edgeKey = __EDGE_KEY__;

      function kgAfterReady() {
        var allNodes = nodes.get();
        var allEdges = edges.get();
        var graphContainer = document.getElementById("mynetwork");
        var nodeLabelLayer = document.createElement("div");
        var nodeLabelEls = {};

        nodeLabelLayer.id = "kg_node_labels";
        graphContainer.appendChild(nodeLabelLayer);

        var originalNodes = {};
        var originalEdges = {};
        var enabledEdgeRelations = {};
        var currentView = {mode: "all", nodeId: null};
        var activeNodeId = null;
        var layoutFinalized = false;

        var transparentNodeColor = {
          background: "rgba(255,255,255,0)",
          border: "rgba(255,255,255,0)",
          highlight: {
            background: "rgba(255,255,255,0)",
            border: "rgba(255,255,255,0)"
          },
          hover: {
            background: "rgba(255,255,255,0)",
            border: "rgba(255,255,255,0)"
          }
        };

        function applyCollisionNodeStyle(node) {
          var o = Object.assign({}, node);
          o.label = " ";
          o.borderWidth = 0;
          o.color = Object.assign({}, transparentNodeColor);
          o.font = Object.assign({}, o.font || {}, {
            size: 1,
            color: "rgba(0,0,0,0)"
          });
          return o;
        }

        nodes.update(allNodes.map(applyCollisionNodeStyle));
        allNodes = nodes.get();
        allNodes.forEach(function(n) { originalNodes[n.id] = Object.assign({}, n); });
        allEdges.forEach(function(e) { originalEdges[e.id] = Object.assign({}, e); });
        Object.keys(edgeKey).forEach(function(relation) {
          enabledEdgeRelations[relation] = true;
        });

        function htmlToText(s) {
          var div = document.createElement("div");
          div.innerHTML = s || "";
          return (div.textContent || div.innerText || "").toLowerCase();
        }

        function escapeHtml(s) {
          return String(s || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
        }

        function renderConceptText(s) {
          return escapeHtml(s).replace(
            /\\\\cref\\{([^{}]*)\\}\\{([^{}]*)\\}/g,
            function(match, label, targetId) {
              if (!getConcept(targetId)) {
                return "<strong>" + label + "</strong>";
              }
              return '<a href="#" class="concept-link" data-concept-id="' +
                escapeHtml(targetId) +
                '"><strong>' + label + "</strong></a>";
            }
          );
        }

        function typesetInfoPanel() {
          var panel = document.getElementById("info_panel");
          if (window.MathJax && MathJax.typesetPromise) {
            if (MathJax.typesetClear) {
              MathJax.typesetClear([panel]);
            }
            MathJax.typesetPromise([panel]).catch(function(err) {
              console.warn("MathJax typesetting failed:", err);
            });
          }
        }

        function getConcept(nodeId) {
          return conceptData[String(nodeId)] || null;
        }

        function conceptIdParts(id) {
          return String(id).split(".").map(function(part) {
            var n = Number(part);
            return Number.isFinite(n) ? n : part;
          });
        }

        function compareConceptIds(a, b) {
          var aa = conceptIdParts(a);
          var bb = conceptIdParts(b);
          var len = Math.max(aa.length, bb.length);
          for (var i = 0; i < len; i++) {
            if (aa[i] === undefined) { return -1; }
            if (bb[i] === undefined) { return 1; }
            if (aa[i] === bb[i]) { continue; }
            if (typeof aa[i] === "number" && typeof bb[i] === "number") {
              return aa[i] - bb[i];
            }
            return String(aa[i]).localeCompare(String(bb[i]));
          }
          return 0;
        }

        function conceptSearchText(nodeId, node) {
          var concept = getConcept(nodeId) || {};
          return [
            String(nodeId),
            node && node.label ? String(node.label) : "",
            concept.label || "",
            concept.layer || "",
            concept.layer_title || "",
            concept.body || ""
          ].join(" ").toLowerCase();
        }

        function edgeRelation(edge) {
          return String(edge.relation || "");
        }

        function edgeRelationEnabled(edge) {
          var relation = edgeRelation(edge);
          return enabledEdgeRelations[relation] !== false;
        }

        function enabledConnectedNodes(nodeId) {
          var connected = {};
          allEdges.forEach(function(edge) {
            if (!edgeRelationEnabled(edge)) { return; }
            if (edge.from == nodeId) { connected[edge.to] = true; }
            if (edge.to == nodeId) { connected[edge.from] = true; }
          });
          return Object.keys(connected);
        }

        function relationColour(relation) {
          var item = edgeKey[relation] || {};
          return item.colour || "#999999";
        }

        function buildEdgeFilters() {
          var relations = Object.keys(edgeKey).sort();
          var html = "<b>Edge types</b>";

          if (relations.length === 0) {
            html += '<div style="color:#555; padding-top:4px;">No edge key loaded.</div>';
            document.getElementById("kg_edge_filters").innerHTML = html;
            return;
          }

          relations.forEach(function(relation) {
            var inputId = "kg_edge_filter_" + relation.replace(/[^a-zA-Z0-9_-]/g, "_");
            html += '<label class="kg-edge-filter" for="' + escapeHtml(inputId) + '">' +
              '<input type="checkbox" id="' + escapeHtml(inputId) +
              '" data-edge-relation="' + escapeHtml(relation) + '" checked>' +
              '<span class="kg-edge-filter-swatch" style="background:' +
              escapeHtml(relationColour(relation)) + '"></span>' +
              '<span class="kg-edge-filter-label">' + escapeHtml(relation) + "</span>" +
              "</label>";
          });

          document.getElementById("kg_edge_filters").innerHTML = html;
        }

        function applyCurrentView() {
          if (currentView.mode === "highlight" && currentView.nodeId !== null) {
            kgHighlight(currentView.nodeId, true);
            return;
          }
          if (currentView.mode === "neighbourhood" && currentView.nodeId !== null) {
            kgApplyNeighbourhood(currentView.nodeId, true);
            return;
          }
          kgReset(true);
        }

        function visibleConceptLabel(nodeId) {
          var concept = getConcept(nodeId) || {};
          return '<span class="kg-node-label-id">' + escapeHtml(nodeId) + '</span>' +
            renderConceptText(concept.label || "");
        }

        function buildNodeLabels() {
          nodeLabelLayer.innerHTML = "";
          Object.keys(conceptData).forEach(function(id) {
            var el = document.createElement("div");
            el.className = "kg-node-label";
            el.setAttribute("data-node-id", id);
            el.innerHTML = visibleConceptLabel(id);
            nodeLabelLayer.appendChild(el);
            nodeLabelEls[id] = el;
          });
          typesetNodeLabels();
          updateNodeLabelPositions();
        }

        function typesetNodeLabels() {
          if (window.MathJax && MathJax.typesetPromise) {
            if (MathJax.typesetClear) {
              MathJax.typesetClear([nodeLabelLayer]);
            }
            MathJax.typesetPromise([nodeLabelLayer]).catch(function(err) {
              console.warn("MathJax label typesetting failed:", err);
            }).then(function() {
              updateNodeLabelPositions();
            });
          } else {
            setTimeout(typesetNodeLabels, 250);
          }
        }

        function updateNodeLabelPositions() {
          if (!network || !nodeLabelLayer) { return; }

          var positions = network.getPositions();
          var labelScale = Math.max(0.35, network.getScale ? network.getScale() : 1);
          Object.keys(nodeLabelEls).forEach(function(id) {
            var el = nodeLabelEls[id];
            var node = nodes.get(id);
            var pos = positions[id];
            if (!node || !pos || node.hidden) {
              el.style.display = "none";
              return;
            }

            var dom = network.canvasToDOM(pos);
            var radius = Number(node.visualSize) || Number(node.size) || 18;
            var radiusEdge = network.canvasToDOM({x: pos.x + radius, y: pos.y});
            var radiusPx = Math.abs(radiusEdge.x - dom.x);
            var canvasEl = network.canvas && network.canvas.frame ? network.canvas.frame.canvas : null;
            var canvasRect = canvasEl ? canvasEl.getBoundingClientRect() : graphContainer.getBoundingClientRect();
            var layerRect = nodeLabelLayer.getBoundingClientRect();
            var labelCenterX = canvasRect.left - layerRect.left + dom.x;
            var labelTopY = canvasRect.top - layerRect.top + dom.y + Math.max(4, radiusPx + 3);
            var labelWidth = __NODE_LABEL_WIDTH__ * labelScale;
            el.style.display = "block";
            el.style.width = labelWidth + "px";
            el.style.fontSize = (__NODE_LABEL_FONT_SIZE__ * labelScale) + "px";
            el.style.left = (labelCenterX - labelWidth / 2) + "px";
            el.style.top = labelTopY + "px";
            el.style.opacity = node.opacity === undefined ? "1" : String(node.opacity);
          });
        }

        function lockLayout() {
          network.stopSimulation();
          network.setOptions({physics: {enabled: false}});
        }

        function captureCurrentNodeLayout() {
          var positions = network.getPositions();
          allNodes = nodes.get();
          originalNodes = {};
          allNodes.forEach(function(n) {
            var o = Object.assign({}, n);
            if (positions[n.id]) {
              o.x = positions[n.id].x;
              o.y = positions[n.id].y;
            }
            originalNodes[n.id] = applyCollisionNodeStyle(o);
          });
          nodes.update(Object.keys(originalNodes).map(function(id) {
            return Object.assign({}, originalNodes[id]);
          }));
          allNodes = nodes.get();
        }

        function finalizeLayoutForInteraction() {
          if (layoutFinalized) { return; }
          lockLayout();
          captureCurrentNodeLayout();
          layoutFinalized = true;
          updateNodeLabelPositions();
        }

        function drawVisibleNodes(ctx) {
          var positions = network.getPositions();
          nodes.get().forEach(function(node) {
            if (node.hidden) { return; }

            var pos = positions[node.id];
            if (!pos) { return; }

            var radius = Number(node.visualSize) || 18;
            var opacity = node.opacity === undefined ? 1 : Number(node.opacity);
            var color = node.visualColor || {};
            var fill = color.background || "#999999";
            var border = color.border || "#333333";

            ctx.save();
            ctx.globalAlpha = Number.isFinite(opacity) ? opacity : 1;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, 2 * Math.PI, false);
            ctx.fillStyle = fill;
            ctx.fill();
            ctx.lineWidth = 1.5;
            ctx.strokeStyle = node.id === activeNodeId ? "#000000" : border;
            ctx.stroke();
            ctx.restore();
          });
        }

        function showConcept(nodeId) {
          var concept = getConcept(nodeId);
          if (!concept) {
            document.getElementById("info_panel").innerHTML =
              "<h2>" + escapeHtml(nodeId) + "</h2>" +
              "<p>No concept data was found for this node.</p>";
            typesetInfoPanel();
            return;
          }

          var layerParts = [];
          if (concept.layer) { layerParts.push("Layer " + escapeHtml(concept.layer)); }
          if (concept.layer_title) { layerParts.push(escapeHtml(concept.layer_title)); }

          var html = "";
          html += "<h2>" + escapeHtml(nodeId) + "<br>" + renderConceptText(concept.label) + "</h2>";
          if (layerParts.length > 0) {
            html += "<p><b>Layer:</b> " + layerParts.join(" - ") + "</p>";
          }
          html += "<hr>";
          html += '<div class="concept-body">' + renderConceptText(concept.body) + "</div>";
          document.getElementById("info_panel").innerHTML = html;
          typesetInfoPanel();
        }

        window.kgShowEdgeKey = function() {
          var relations = Object.keys(edgeKey).sort();
          var html = "<h2>Edge Key</h2>";

          if (relations.length === 0) {
            html += "<p>No edge key data was loaded.</p>";
            document.getElementById("info_panel").innerHTML = html;
            return;
          }

          html += '<table class="edge-key-table">';
          html += "<thead><tr>" +
            "<th>Relation</th>" +
            "<th>Colour</th>" +
            "<th>Direction</th>" +
            "<th>Category</th>" +
            "<th>Meaning</th>" +
            "<th>Example</th>" +
            "</tr></thead><tbody>";

          relations.forEach(function(relation) {
            var item = edgeKey[relation] || {};
            var colour = item.colour || "#999999";
            html += "<tr>" +
              "<td><strong>" + escapeHtml(relation) + "</strong></td>" +
              '<td><span class="edge-colour-swatch" style="background:' + escapeHtml(colour) + '"></span>' +
              escapeHtml(colour) + "</td>" +
              "<td>" + (item.directed ? "directed" : "undirected") + "</td>" +
              "<td>" + escapeHtml(item.category || "") + "</td>" +
              "<td>" + escapeHtml(item.meaning || "") + "</td>" +
              "<td>" + escapeHtml(item.example || "") + "</td>" +
              "</tr>";
          });

          html += "</tbody></table>";
          document.getElementById("info_panel").innerHTML = html;
        };

        function setActiveConceptItem(nodeId) {
          document.querySelectorAll(".kg-concept-item.active").forEach(function(el) {
            el.classList.remove("active");
          });
          var item = Array.prototype.find.call(
            document.querySelectorAll(".kg-concept-item"),
            function(el) { return el.getAttribute("data-concept-id") === String(nodeId); }
          );
          if (item) {
            item.classList.add("active");
            item.scrollIntoView({block: "nearest"});
          }
        }

        function focusConcept(nodeId, statusPrefix) {
          if (!getConcept(nodeId)) { return; }
          finalizeLayoutForInteraction();
          activeNodeId = nodeId;
          network.focus(nodeId, {scale: 0.7, animation: true});
          kgHighlight(nodeId);
          showConcept(nodeId);
          setActiveConceptItem(nodeId);
          if (statusPrefix) {
            document.getElementById("kg_status").innerText = statusPrefix + " " + nodeId + ".";
          }
        }

        function buildConceptList(filterText) {
          var q = String(filterText || "").trim().toLowerCase();
          var ids = Object.keys(conceptData).sort(compareConceptIds);
          var html = "<b>Concepts</b><br>";
          var count = 0;

          ids.forEach(function(id) {
            var concept = getConcept(id);
            var haystack = [
              id,
              concept.label || "",
              concept.layer || "",
              concept.layer_title || "",
              concept.body || ""
            ].join(" ").toLowerCase();
            if (q && !haystack.includes(q)) { return; }

            html += '<button type="button" class="kg-concept-item" data-concept-id="' +
              escapeHtml(id) +
              '"><span class="kg-concept-id">' +
              escapeHtml(id) +
              '</span> ' +
              escapeHtml(concept.label || "") +
              "</button>";
            count += 1;
          });

          if (count === 0) {
            html += '<div style="color:#555; padding:4px 0;">No matching concepts.</div>';
          }
          document.getElementById("kg_concept_list").innerHTML = html;
        }

        window.kgFreezeLayout = function() {
          finalizeLayoutForInteraction();
          document.getElementById("kg_status").innerText = "Layout frozen.";
        };

        window.kgRestartLayout = function() {
          network.setOptions({
            physics: {enabled: false}
          });
          network.fit({animation: true});
          document.getElementById("kg_status").innerText = "Initial compact layout restored.";
        };

        window.kgReset = function(preserveStatus) {
          finalizeLayoutForInteraction();
          network.unselectAll();
          currentView = {mode: "all", nodeId: null};
          activeNodeId = null;
          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = false;
            o.opacity = 1.0;
            return o;
          }));
          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            o.hidden = !edgeRelationEnabled(e);
            return o;
          }));
          updateNodeLabelPositions();
          if (!preserveStatus) {
            document.getElementById("kg_status").innerText = "Click a node to highlight its immediate neighbours.";
          }
          setActiveConceptItem(null);
        };

        window.kgShowAll = window.kgReset;

        window.kgSearch = function() {
          finalizeLayoutForInteraction();
          var q = document.getElementById("kg_search").value.trim().toLowerCase();
          if (!q) { return; }

          var matches = allNodes.filter(function(n) {
            return conceptSearchText(n.id, n).includes(q) || htmlToText(n.title || "").includes(q);
          });

          if (matches.length === 0) {
            document.getElementById("kg_status").innerText = "No matching concept found.";
            return;
          }

          var id = matches[0].id;
          var concept = getConcept(id) || {};
          focusConcept(id, null);
          document.getElementById("kg_status").innerText =
            "Found " + matches.length + " match(es). Showing first: " + (concept.label || id);
        };

        window.kgHighlight = function(nodeId, preserveStatus) {
          finalizeLayoutForInteraction();
          activeNodeId = nodeId;
          currentView = {mode: "highlight", nodeId: nodeId};
          var connected = enabledConnectedNodes(nodeId);
          var keep = {};
          keep[nodeId] = true;
          connected.forEach(function(id) { keep[id] = true; });

          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            if (keep[n.id]) {
              o.opacity = 1.0;
              o.font = Object.assign({}, o.font || {}, {color: "#111111"});
            } else {
              o.opacity = 1.0;
              o.font = Object.assign({}, o.font || {}, {color: "#999999"});
              o.visualColor = {
                background: "#f2f2f2",
                border: "#d0d0d0"
              };
            }
            o = applyCollisionNodeStyle(o);
            o.hidden = false;
            return o;
          }));

          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            if (!edgeRelationEnabled(e)) {
              o.hidden = true;
            } else if (e.from == nodeId || e.to == nodeId) {
              o.hidden = false;
              o.color = Object.assign({}, o.color || {}, {opacity: 0.95});
              o.width = Math.max(Number(o.width) || 0, 3.0);
            } else {
              o.color = {
                color: "#cccccc",
                highlight: "#cccccc",
                hover: "#cccccc",
                opacity: 0.10
              };
              o.width = 0.4;
              o.hidden = false;
            }
            return o;
          }));
          network.unselectAll();
          updateNodeLabelPositions();

          if (!preserveStatus) {
            document.getElementById("kg_status").innerText =
              "Selected " + nodeId + ": showing immediate neighbours.";
          }
        };

        function kgApplyNeighbourhood(nodeId, preserveStatus) {
          finalizeLayoutForInteraction();
          activeNodeId = nodeId;
          currentView = {mode: "neighbourhood", nodeId: nodeId};
          var connected = enabledConnectedNodes(nodeId);
          var keep = {};
          keep[nodeId] = true;
          connected.forEach(function(id) { keep[id] = true; });

          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = !keep[n.id];
            return o;
          }));

          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            o.hidden = !(edgeRelationEnabled(e) && keep[e.from] && keep[e.to]);
            return o;
          }));

          network.fit({animation: true});
          updateNodeLabelPositions();
          if (!preserveStatus) {
            document.getElementById("kg_status").innerText =
              "Neighbourhood mode for " + nodeId + ".";
          }
        }

        window.kgFocusSelected = function() {
          var selected = network.getSelectedNodes();
          var nodeId = activeNodeId || selected[0];
          if (!nodeId) {
            document.getElementById("kg_status").innerText = "Select a node first.";
            return;
          }

          kgApplyNeighbourhood(nodeId, false);
        };

        network.on("click", function(params) {

            if (params.nodes.length === 0)
                return;

            const nodeId = params.nodes[0];

            kgHighlight(nodeId);
            showConcept(nodeId);
            setActiveConceptItem(nodeId);
        });

        network.once("stabilized", function() {
          finalizeLayoutForInteraction();
          updateNodeLabelPositions();
        });

        network.on("afterDrawing", function(ctx) {
          drawVisibleNodes(ctx);
          updateNodeLabelPositions();
        });
        network.on("dragEnd", updateNodeLabelPositions);
        network.on("zoom", updateNodeLabelPositions);
        network.on("animationFinished", updateNodeLabelPositions);

        document.getElementById("kg_search").addEventListener("keydown", function(e) {
          if (e.key === "Enter") { kgSearch(); }
        });

        document.getElementById("kg_search").addEventListener("input", function(e) {
          buildConceptList(e.target.value);
        });

        document.getElementById("kg_edge_filters").addEventListener("change", function(e) {
          var input = e.target.closest("input[data-edge-relation]");
          if (!input) { return; }

          enabledEdgeRelations[input.getAttribute("data-edge-relation")] = input.checked;
          applyCurrentView();
        });

        document.getElementById("kg_concept_list").addEventListener("click", function(e) {
          var item = e.target.closest(".kg-concept-item");
          if (!item) { return; }

          e.preventDefault();
          focusConcept(item.getAttribute("data-concept-id"), "Selected");
        });

        document.getElementById("info_panel").addEventListener("click", function(e) {
          var link = e.target.closest(".concept-link");
          if (!link) { return; }

          e.preventDefault();
          var id = link.getAttribute("data-concept-id");
          if (!getConcept(id)) { return; }

          focusConcept(id, "Selected");
        });

        // Build legend from node groups.
        var groups = {};
        allNodes.forEach(function(n) {
          if (n.group !== undefined) { groups[n.group] = true; }
        });
        var legend = document.getElementById("kg_legend");
        var html = "<b>Layers</b><br>";
        Object.keys(groups).sort(function(a,b){return Number(a)-Number(b);}).forEach(function(g) {
          var sample = allNodes.find(function(n) { return String(n.group) === String(g); });
          var color = sample && sample.visualColor && sample.visualColor.background ? sample.visualColor.background : "#999";
          var sampleConcept = sample ? getConcept(sample.id) : null;
          var layerTitle = sampleConcept && sampleConcept.layer_title ? sampleConcept.layer_title : "";
          html += '<span class="legend-dot" style="background:' + color + '"></span>' +
                  'Layer ' + g + (layerTitle ? ': ' + layerTitle : '') + '<br>';
        });
        legend.innerHTML = html;
        buildNodeLabels();
        buildEdgeFilters();
        buildConceptList("");
      }

      // Wait until pyvis has created network/nodes/edges variables.
      setTimeout(kgAfterReady, 500);
    </script>
    """.replace("__CONCEPT_DATA__", concept_data_json).replace("__EDGE_KEY__", edge_key_json)
    js = js.replace("__NODE_LABEL_WIDTH__", str(NODE_LABEL_WIDTH))
    js = js.replace("__NODE_LABEL_FONT_SIZE__", str(NODE_LABEL_FONT_SIZE))

    css = css.replace("__NODE_LABEL_WIDTH__", str(NODE_LABEL_WIDTH))
    css = css.replace("__NODE_LABEL_FONT_SIZE__", str(NODE_LABEL_FONT_SIZE))

    html_text = html_text.replace("</head>", mathjax + "\n" + css + "\n</head>")
    html_text = html_text.replace("<body>", "<body>\n" + controls)
    html_text = html_text.replace("</body>", js + "\n</body>")
    return html_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", default="nodes.csv", help="Path to nodes.csv")
    parser.add_argument("--edges", default="edges.csv", help="Path to edges.csv")
    parser.add_argument(
        "--edge-key",
        default=None,
        help="Path to edges_key.csv. Defaults to edges_key.csv beside the edges file when present.",
    )
    parser.add_argument("--out", default="interactive_graph.html", help="Output HTML file")
    parser.add_argument("--height", default="900px")
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
    hierarchy_levels = build_hierarchy_levels(list(nodes_df["id"]), edges_df, edge_key)
    hierarchy_positions = build_hierarchy_positions(hierarchy_levels)

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
            "scaleFactor": 0.65
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
          "iterations": 200,
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
            shape="box",
            group=layer_int,
            level=hierarchy_levels.get(cid, 0),
            x=x_pos,
            y=y_pos,
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
                "background": "rgba(255,255,255,0)",
                "border": "rgba(255,255,255,0)",
                "highlight": {
                    "background": "rgba(255,255,255,0)",
                    "border": "rgba(255,255,255,0)",
                },
                "hover": {
                    "background": "rgba(255,255,255,0)",
                    "border": "rgba(255,255,255,0)",
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
            stable_edge_colour(rel) if directed else UNDIRECTED_EDGE_COLOUR,
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
