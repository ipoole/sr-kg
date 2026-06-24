#!/usr/bin/env python3
"""
generate_pyvis.py

Generate a standalone interactive HTML knowledge-graph viewer from nodes.csv and edges.csv.

Expected nodes.csv columns:
    id,label,layer,layer_title,body

Expected edges.csv columns:
    source,target,type

Only id/source/target are strictly required. Other columns are used when present.

Usage:
    python generate_pyvis.py --nodes nodes.csv --edges edges.csv --out interactive_graph.html

Dependencies:
    pip install pandas networkx pyvis
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
from pathlib import Path

import pandas as pd
import networkx as nx
from pyvis.network import Network


LAYER_COLOURS = [
    "#e6194b", "#f58231", "#ffe119", "#3cb44b", "#46f0f0",
    "#4363d8", "#911eb4", "#f032e6", "#fabed4", "#9a6324",
    "#808080", "#469990", "#dcbeff", "#aaffc3"
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


def inject_controls(html_text: str, concept_data: dict[str, dict[str, str]]) -> str:
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
      <button onclick="kgFreezeLayout()">Freeze</button>
      <button onclick="kgRestartLayout()">Restart layout</button>
      <div id="kg_status">Click a node to highlight its immediate neighbours.</div>
      <div id="kg_legend"></div>
      <div id="kg_concept_list"></div>
    </div>

    <div id="info_panel">
      <h2>Knowledge Graph</h2>
      <p>Click a concept node to view details.</p>
    </div>
    """

    concept_data_json = json.dumps(concept_data, ensure_ascii=False).replace("</", "<\\/")

    js = """
    <script type="text/javascript">
      var conceptData = __CONCEPT_DATA__;

      function kgAfterReady() {
        var allNodes = nodes.get();
        var allEdges = edges.get();

        var originalNodes = {};
        var originalEdges = {};
        allNodes.forEach(function(n) { originalNodes[n.id] = Object.assign({}, n); });
        allEdges.forEach(function(e) { originalEdges[e.id] = Object.assign({}, e); });

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
          network.selectNodes([nodeId]);
          network.focus(nodeId, {scale: 1.4, animation: true});
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
          network.stopSimulation();
          network.setOptions({physics: {enabled: false}});
          document.getElementById("kg_status").innerText = "Layout frozen.";
        };

        window.kgRestartLayout = function() {
          network.setOptions({physics: {enabled: true}});
          network.startSimulation();
          document.getElementById("kg_status").innerText = "Layout physics restarted.";
        };

        window.kgReset = function() {
          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = false;
            return o;
          }));
          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            o.hidden = false;
            return o;
          }));
          document.getElementById("kg_status").innerText = "Click a node to highlight its immediate neighbours.";
          setActiveConceptItem(null);
        };

        window.kgShowAll = window.kgReset;

        window.kgSearch = function() {
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
          focusConcept(id, null);
          document.getElementById("kg_status").innerText =
            "Found " + matches.length + " match(es). Showing first: " + matches[0].label;
        };

        window.kgHighlight = function(nodeId) {
          var connected = network.getConnectedNodes(nodeId);
          var keep = {};
          keep[nodeId] = true;
          connected.forEach(function(id) { keep[id] = true; });

          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            if (keep[n.id]) {
              o.opacity = 1.0;
              o.font = Object.assign({}, o.font || {}, {color: "#111111"});
            } else {
              o.opacity = 0.18;
              o.font = Object.assign({}, o.font || {}, {color: "#999999"});
            }
            o.hidden = false;
            return o;
          }));

          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            if (e.from == nodeId || e.to == nodeId) {
              o.hidden = false;
              o.color = {color: "#111111", opacity: 0.95};
              o.width = 2.6;
            } else {
              o.color = {color: "#cccccc", opacity: 0.10};
              o.width = 0.4;
              o.hidden = false;
            }
            return o;
          }));

          document.getElementById("kg_status").innerText =
            "Selected " + nodeId + ": showing immediate neighbours.";
        };

        window.kgFocusSelected = function() {
          var selected = network.getSelectedNodes();
          if (selected.length === 0) {
            document.getElementById("kg_status").innerText = "Select a node first.";
            return;
          }

          var nodeId = selected[0];
          var connected = network.getConnectedNodes(nodeId);
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
            o.hidden = !(keep[e.from] && keep[e.to]);
            return o;
          }));

          network.fit({animation: true});
          document.getElementById("kg_status").innerText =
            "Neighbourhood mode for " + nodeId + ".";
        };

        network.on("click", function(params) {

            if (params.nodes.length === 0)
                return;

            const nodeId = params.nodes[0];

            kgHighlight(nodeId);
            showConcept(nodeId);
            setActiveConceptItem(nodeId);
        });

        network.once("stabilizationIterationsDone", function() {
          kgFreezeLayout();
        });

        document.getElementById("kg_search").addEventListener("keydown", function(e) {
          if (e.key === "Enter") { kgSearch(); }
        });

        document.getElementById("kg_search").addEventListener("input", function(e) {
          buildConceptList(e.target.value);
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
          var color = sample && sample.color && sample.color.background ? sample.color.background : "#999";
          var sampleConcept = sample ? getConcept(sample.id) : null;
          var layerTitle = sampleConcept && sampleConcept.layer_title ? sampleConcept.layer_title : "";
          html += '<span class="legend-dot" style="background:' + color + '"></span>' +
                  'Layer ' + g + (layerTitle ? ': ' + layerTitle : '') + '<br>';
        });
        legend.innerHTML = html;
        buildConceptList("");
      }

      // Wait until pyvis has created network/nodes/edges variables.
      setTimeout(kgAfterReady, 500);
    </script>
    """.replace("__CONCEPT_DATA__", concept_data_json)

    html_text = html_text.replace("</head>", mathjax + "\n" + css + "\n</head>")
    html_text = html_text.replace("<body>", "<body>\n" + controls)
    html_text = html_text.replace("</body>", js + "\n</body>")
    return html_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", default="nodes.csv", help="Path to nodes.csv")
    parser.add_argument("--edges", default="edges.csv", help="Path to edges.csv")
    parser.add_argument("--out", default="interactive_graph.html", help="Output HTML file")
    parser.add_argument("--height", default="900px")
    parser.add_argument("--width", default="100%")
    args = parser.parse_args()

    nodes_df = pd.read_csv(args.nodes).fillna("")
    edges_df = pd.read_csv(args.edges).fillna("")

    if "id" not in nodes_df.columns:
        raise ValueError("nodes.csv must contain an 'id' column")
    if not {"source", "target"}.issubset(edges_df.columns):
        raise ValueError("edges.csv must contain 'source' and 'target' columns")

    # Normalise IDs as strings.
    nodes_df["id"] = nodes_df["id"].astype(str)
    edges_df["source"] = edges_df["source"].astype(str)
    edges_df["target"] = edges_df["target"].astype(str)

    node_ids = set(nodes_df["id"])
    edges_df = edges_df[edges_df["source"].isin(node_ids) & edges_df["target"].isin(node_ids)].copy()

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
        "shape": "dot",
        "borderWidth": 1,
        "font": {
          "size": 16,
          "face": "arial",
          "multi": true
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.65
          }
        },
        "smooth": {
          "enabled": true,
          "type": "dynamic"
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
          "gravitationalConstant": -80,
          "centralGravity": 0.012,
          "springLength": 170,
          "springConstant": 0.045,
          "damping": 0.5,
          "avoidOverlap": 0.8
        },
        "stabilization": {
          "enabled": true,
          "iterations": 900
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true,
        "tooltipDelay": 120
      }
    }
    """)

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

        title = f"{cid} {label}"

        # Node size mainly reflects how many other concepts point to it.
        importance = incoming.get(cid, 0)
        size = 18 + 4.0 * math.sqrt(importance + 1)

        visible_label = f"{cid}\n{label}"

        net.add_node(
            cid,
            label=visible_label,
            title=title,
            group=layer_int,
            size=size,
            color={
                "background": colour,
                "border": "#333333",
                "highlight": {
                    "background": colour,
                    "border": "#000000",
                },
            },
        )

    for i, row in edges_df.iterrows():
        source = row["source"]
        target = row["target"]
        rel = str(row.get("type", row.get("relation", "REFERENCE")) or "REFERENCE")
        net.add_edge(
            source,
            target,
            title=html.escape(rel),
        )

    concept_data = build_concept_data(nodes_df)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(str(out_path), notebook=False, open_browser=False)

    html_text = out_path.read_text(encoding="utf-8")
    html_text = inject_controls(html_text, concept_data)
    out_path.write_text(html_text, encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"Nodes: {len(nodes_df)}")
    print(f"Edges: {len(edges_df)}")


if __name__ == "__main__":
    main()
