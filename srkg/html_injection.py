"""HTML, CSS, and JavaScript injection for the generated viewer.

This module owns the browser-side application shell layered on top of PyVis:
MathJax setup, control panels, responsive CSS, node-label overlays, custom
canvas node drawing, edge filters, concept search, and interaction handlers.

The function here accepts an already-generated PyVis HTML document and injects
viewer assets by string replacement. It should not load CSV files, compute
layout, or create PyVis networks. Large embedded asset strings live here until
they are split into separate template/static files.
"""

import json
from html import escape as html_escape

from srkg.config import (
    EDGE_HOVER_WIDTH,
    LAYOUT_ROW_STAGGER,
    LAYOUT_X_SPACING,
    LAYOUT_Y_SPACING,
    NODE_LABEL_FONT_SIZE,
    NODE_LABEL_FONT_WEIGHT,
    NODE_LABEL_WIDTH,
)


def require_html_marker(html_text: str, marker: str) -> None:
    """Fail clearly if PyVis output no longer contains an injection marker."""
    if marker not in html_text:
        raise ValueError(f"Generated PyVis HTML is missing expected marker: {marker}")


def inject_controls(
    html_text: str,
    concept_data: dict[str, dict[str, str]],
    edge_key: dict[str, dict[str, str | bool]],
    view_title: str,
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
        top: 48px;
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
      #kg_controls.kg-hidden {
        display: none;
      }
      .kg-canvas-toggle {
        position: fixed;
        top: 12px;
        z-index: 10000;
        padding: 5px 9px;
        border: 1px solid #bbb;
        border-radius: 8px;
        background: rgba(255,255,255,0.96);
        box-shadow: 0 2px 8px rgba(0,0,0,0.14);
        color: #222;
        cursor: pointer;
        font-family: Arial, sans-serif;
        font-size: 13px;
      }
      #kg_controls_toggle {
        left: 12px;
      }
      #kg_info_toggle {
        left: 128px;
      }
      .kg-canvas-toggle:hover,
      .kg-canvas-toggle:focus {
        background: #eef3fd;
        outline: none;
      }
      #kg_view_title {
        position: fixed;
        top: 12px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9997;
        max-width: min(760px, 42vw);
        padding: 7px 12px;
        border: 1px solid rgba(0,0,0,0.12);
        border-radius: 8px;
        background: rgba(255,255,255,0.94);
        box-shadow: 0 2px 8px rgba(0,0,0,0.14);
        color: #222;
        font-family: Arial, sans-serif;
        font-size: 18px;
        font-weight: 700;
        line-height: 1.2;
        overflow: hidden;
        pointer-events: none;
        text-align: center;
        text-overflow: ellipsis;
        white-space: nowrap;
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
      .kg-mode-controls {
        display: flex;
        gap: 4px;
        margin: 6px 0 4px;
      }
      #kg_controls .kg-mode-button {
        border: 1px solid #bbb;
        border-radius: 999px;
        background: #f7f7f7;
        color: #222;
        cursor: pointer;
        flex: 1 1 0;
        font: inherit;
        margin: 0;
        padding: 4px 8px;
      }
      #kg_controls .kg-mode-button.kg-active {
        background: #174ea6;
        border-color: #174ea6;
        color: #fff;
        font-weight: 700;
      }
      #kg_status {
        margin-top: 6px;
        font-size: 12px;
        color: #333;
      }
      #kg_search_block {
        padding-top: 6px;
      }
      .kg-fold {
        margin-top: 8px;
        border-top: 1px solid #ddd;
        padding-top: 8px;
        font-size: 12px;
      }
      .kg-fold summary {
        cursor: pointer;
        font-weight: 700;
        list-style-position: outside;
      }
      .kg-fold summary:hover,
      .kg-fold summary:focus {
        color: #174ea6;
        outline: none;
      }
      #kg_legend {
        max-height: 180px;
        overflow-y: auto;
        padding-top: 4px;
      }
      #kg_edge_filters {
        padding-top: 4px;
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
        max-height: 260px;
        overflow-y: auto;
        padding-top: 6px;
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
        font-weight: __NODE_LABEL_FONT_WEIGHT__;
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

    #info_panel.kg-hidden {
        display: none;
    }

    #info_panel .concept-body {
        white-space: pre-wrap;
        font-family: inherit;
        line-height: 1.45;
    }

    #info_panel .concept-figure {
        margin: 0.1em 0 0.85em;
    }

    #info_panel .concept-graphic {
        display: flex;
        justify-content: center;
        margin: 0;
        overflow: visible;
    }

    #info_panel .concept-graphic svg {
        display: block;
        height: auto;
        margin: -30px 0 -38px;
        max-height: 300px;
        max-width: min(100%, 380px);
        width: 100%;
    }

    #info_panel .concept-graphic-caption {
        color: #555;
        font-size: 0.95em;
        font-style: italic;
        line-height: 1.35;
        margin: 0.15em 0 0;
        text-align: center;
    }

    #info_panel h2 {
        font-size: 1.5em;
        line-height: 1.15;
        margin: 0 0 0.6em;
    }

    #info_panel h3 {
        font-size: 1.05em;
        font-weight: 700;
        line-height: 1.2;
        margin: 1em 0 0.35em;
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

    @media (max-width: 1100px) {
        #kg_controls {
            max-width: 240px;
            font-size: 12px;
        }

        #kg_controls input {
            width: 160px;
        }

        #kg_view_title {
            max-width: min(520px, 36vw);
            font-size: 15px;
        }

        #info_panel {
            width: 300px;
            font-size: 13px;
        }

        #info_panel h2 {
            font-size: 1.3em;
        }
    }

    @media (max-width: 850px) {
        #kg_controls {
            max-width: 150px;
        }

        #kg_view_title {
            display: none;
        }

        #info_panel {
            width: 150px;
            font-size: 12px;
        }

        #info_panel h2 {
            font-size: 1.15em;
        }
    }
    </style>
    """

    title_html = f'<div id="kg_view_title">{html_escape(view_title)}</div>'
    controls = """
    __TITLE_HTML__
    <button id="kg_controls_toggle" class="kg-canvas-toggle" onclick="kgToggleControls()">Hide controls</button>
    <button id="kg_info_toggle" class="kg-canvas-toggle" onclick="kgToggleInfoPanel()">Hide details</button>
    <div id="kg_controls">
      <b>Knowledge graph explorer</b><br>
      <div class="kg-mode-controls" role="group" aria-label="Graph view mode">
        <button id="kg_mode_neighbourhood" class="kg-mode-button" onclick="kgFocusSelected()" aria-pressed="false">Neighbourhood</button>
        <button id="kg_mode_descendants" class="kg-mode-button" onclick="kgFocusDescendantsSelected()" aria-pressed="false">Descendants</button>
        <button id="kg_mode_all" class="kg-mode-button kg-active" onclick="kgShowAll()" aria-pressed="true">All</button>
      </div>
      <button onclick="kgShowEdgeKey()">Edge key</button>
      <div id="kg_status">Click a node to highlight its immediate neighbours.</div>
      <details id="kg_edge_filters_section" class="kg-fold" open>
        <summary>Edge types</summary>
        <div id="kg_edge_filters"></div>
      </details>
      <details id="kg_legend_section" class="kg-fold" open>
        <summary>Layers</summary>
        <div id="kg_legend"></div>
      </details>
      <details id="kg_search_section" class="kg-fold" open>
        <summary>Search</summary>
        <div id="kg_search_block">
          <input id="kg_search" placeholder="Search ID or title, e.g. 3.1 or Lorentz">
          <button onclick="kgSearch()">Find</button>
        </div>
        <div id="kg_concept_list"></div>
      </details>
    </div>

    <div id="info_panel">
      <h2>__VIEW_TITLE__</h2>
      <p>Click a concept node to view details.</p>
    </div>
    """.replace("__TITLE_HTML__", title_html).replace("__VIEW_TITLE__", html_escape(view_title))

    concept_data_json = json.dumps(concept_data, ensure_ascii=False).replace("</", "<\\/")
    edge_key_json = json.dumps(edge_key, ensure_ascii=False).replace("</", "<\\/")

    js = """
    <script type="text/javascript">
      var conceptData = __CONCEPT_DATA__;
      var edgeKey = __EDGE_KEY__;
      var layoutXSpacing = __LAYOUT_X_SPACING__;
      var layoutYSpacing = __LAYOUT_Y_SPACING__;
      var layoutRowStagger = __LAYOUT_ROW_STAGGER__;
      var edgeHoverWidth = __EDGE_HOVER_WIDTH__;

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
        var hoveredEdgeId = null;
        var hoveredEdgeBeforeHover = null;
        var svgImageCache = {};
        var activeNodeRadiusScale = 1.4;
        var activeNodeBorderWidth = 6;

        /*
         * Custom node rendering
         *
         * PyVis/vis-network is still responsible for edge routing, hit testing,
         * and node selection. The visible nodes are deliberately split into
         * three pieces:
         *
         * 1. native vis-network dot nodes for the first frame, avoiding a blank
         *    graph while this injected script waits for network/nodes/edges;
         * 2. invisible fixed-size box nodes after startup, giving interaction a
         *    larger hit area that includes the external label footprint;
         * 3. canvas-drawn circles plus HTML labels, so node labels can contain
         *    MathJax and still track pan/zoom.
         */
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
          o.shape = "box";
          o.label = " ";
          o.borderWidth = 0;
          o.color = Object.assign({}, transparentNodeColor);
          o.font = Object.assign({}, o.font || {}, {
            size: 1,
            color: "rgba(0,0,0,0)"
          });
          return o;
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
            var baseRadius = Number(node.visualSize) || Number(node.size) || 18;
            var radius = id === activeNodeId ? baseRadius * activeNodeRadiusScale : baseRadius;
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

        function drawVisibleNodes(ctx) {
          var positions = network.getPositions();
          nodes.get().forEach(function(node) {
            if (node.hidden) { return; }

            var pos = positions[node.id];
            if (!pos) { return; }

            var baseRadius = Number(node.visualSize) || 18;
            var isActive = node.id === activeNodeId;
            var radius = isActive ? baseRadius * activeNodeRadiusScale : baseRadius;
            var opacity = node.opacity === undefined ? 1 : Number(node.opacity);
            var color = node.visualColor || {};
            var fill = color.background || "#999999";
            var border = color.border || "#333333";
            var concept = getConcept(node.id) || {};
            var svgIcon = concept.svg_icon || concept.svg_graphic || "";
            var svgImage = svgIcon ? getSvgNodeImage(node.id, svgIcon) : null;

            ctx.save();
            ctx.globalAlpha = Number.isFinite(opacity) ? opacity : 1;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, 2 * Math.PI, false);
            ctx.fillStyle = svgImage ? tintHexColour(fill, 0.86) : fill;
            ctx.fill();

            if (svgImage && svgImage.complete && svgImage.naturalWidth > 0) {
              ctx.save();
              ctx.beginPath();
              ctx.arc(pos.x, pos.y, Math.max(1, radius - 3), 0, 2 * Math.PI, false);
              ctx.clip();
              var imagePadding = radius * 0.08;
              var imageSize = Math.max(1, (radius * 2) - (imagePadding * 2));
              var sourceCrop = 36;
              var sourceSize = Math.max(1, 512 - (sourceCrop * 2));
              ctx.drawImage(
                svgImage,
                sourceCrop,
                sourceCrop,
                sourceSize,
                sourceSize,
                pos.x - imageSize / 2,
                pos.y - imageSize / 2,
                imageSize,
                imageSize
              );
              ctx.restore();
            }

            ctx.lineWidth = isActive ? activeNodeBorderWidth : (svgImage ? 4 : 1.5);
            ctx.strokeStyle = isActive ? "#000000" : (svgImage ? fill : border);
            ctx.stroke();
            ctx.restore();
          });
        }

        function getSvgNodeImage(nodeId, svgText) {
          var cached = svgImageCache[nodeId];
          if (cached === null) {
            return null;
          }
          if (cached) {
            return cached;
          }

          var image = new Image();
          image.onload = function() {
            if (network && network.redraw) {
              network.redraw();
            }
          };
          image.onerror = function() {
            svgImageCache[nodeId] = null;
          };
          svgImageCache[nodeId] = image;
          image.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgText);
          return image;
        }

        function tintHexColour(hexColour, amount) {
          var match = String(hexColour || "").trim().match(/^#([0-9a-fA-F]{6})$/);
          if (!match) {
            return "#ffffff";
          }
          var hex = match[1];
          var r = parseInt(hex.slice(0, 2), 16);
          var g = parseInt(hex.slice(2, 4), 16);
          var b = parseInt(hex.slice(4, 6), 16);
          var mix = Math.max(0, Math.min(1, Number(amount)));
          r = Math.round(r + (255 - r) * mix);
          g = Math.round(g + (255 - g) * mix);
          b = Math.round(b + (255 - b) * mix);
          return "rgb(" + r + "," + g + "," + b + ")";
        }

        nodes.update(allNodes.map(applyCollisionNodeStyle));
        allNodes = nodes.get();
        allNodes.forEach(function(n) { originalNodes[n.id] = Object.assign({}, n); });
        allEdges.forEach(function(e) { originalEdges[e.id] = Object.assign({}, e); });
        Object.keys(edgeKey).forEach(function(relation) {
          enabledEdgeRelations[relation] = edgeKey[relation].directed !== false;
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

        function renderCaptionText(s) {
          var html = renderConceptText(s);
          [
            [/partial_mu A\\^mu = 0/g, "\\\\(\\\\partial_\\\\mu A^\\\\mu = 0\\\\)"],
            [/A_mu \\+ partial_mu Lambda/g, "\\\\(A_\\\\mu + \\\\partial_\\\\mu \\\\Lambda\\\\)"],
            [/p_mu - e A_mu/g, "\\\\(p_\\\\mu - e A_\\\\mu\\\\)"],
            [/delta S = 0/g, "\\\\(\\\\delta S = 0\\\\)"],
            [/u\\^mu = dx\\^mu\\/dtau/g, "\\\\(u^\\\\mu = dx^\\\\mu/d\\\\tau\\\\)"],
            [/p\\^mu = m u\\^mu/g, "\\\\(p^\\\\mu = m u^\\\\mu\\\\)"],
            [/F_mu_nu/g, "\\\\(F_{\\\\mu\\\\nu}\\\\)"],
            [/phi\\(x\\)/g, "\\\\(\\\\phi(x)\\\\)"],
            [/A_mu\\(x\\)/g, "\\\\(A_\\\\mu(x)\\\\)"],
            [/A_mu/g, "\\\\(A_\\\\mu\\\\)"],
            [/A\\^mu/g, "\\\\(A^\\\\mu\\\\)"],
            [/J\\^mu/g, "\\\\(J^\\\\mu\\\\)"],
            [/dp\\^mu\\/dtau/g, "\\\\(dp^\\\\mu/d\\\\tau\\\\)"],
            [/p\\^mu/g, "\\\\(p^\\\\mu\\\\)"],
            [/x\\^mu/g, "\\\\(x^\\\\mu\\\\)"],
            [/u\\^mu/g, "\\\\(u^\\\\mu\\\\)"],
            [/dx\\^mu\\/dtau/g, "\\\\(dx^\\\\mu/d\\\\tau\\\\)"],
            [/p_mu/g, "\\\\(p_\\\\mu\\\\)"],
            [/s\\^2/g, "\\\\(s^2\\\\)"],
            [/d\\^4x/g, "\\\\(d^4x\\\\)"],
            [/E=mc\\^2/g, "\\\\(E=mc^2\\\\)"],
            [/T_EM/g, "\\\\(T_{EM}\\\\)"],
            [/T\\^munu/g, "\\\\(T^{\\\\mu\\\\nu}\\\\)"]
          ].forEach(function(replacement) {
            html = html.replace(replacement[0], replacement[1]);
          });
          html = html.replace(/(^|[^\\\\A-Za-z])tau\\b/g, "$1\\\\(\\\\tau\\\\)");
          return html;
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

        function setInfoPanelVisible(visible) {
          var panel = document.getElementById("info_panel");
          var button = document.getElementById("kg_info_toggle");
          panel.classList.toggle("kg-hidden", !visible);
          if (button) {
            button.innerText = visible ? "Hide details" : "Show details";
          }
        }

        function setControlsVisible(visible) {
          var panel = document.getElementById("kg_controls");
          var button = document.getElementById("kg_controls_toggle");
          panel.classList.toggle("kg-hidden", !visible);
          if (button) {
            button.innerText = visible ? "Hide controls" : "Show controls";
          }
        }

        function updateModeButtons() {
          var inNeighbourhood = currentView.mode === "neighbourhood";
          var inDescendants = currentView.mode === "descendants";
          var neighbourhoodButton = document.getElementById("kg_mode_neighbourhood");
          var descendantsButton = document.getElementById("kg_mode_descendants");
          var allButton = document.getElementById("kg_mode_all");
          if (neighbourhoodButton) {
            neighbourhoodButton.classList.toggle("kg-active", inNeighbourhood);
            neighbourhoodButton.setAttribute("aria-pressed", inNeighbourhood ? "true" : "false");
          }
          if (descendantsButton) {
            descendantsButton.classList.toggle("kg-active", inDescendants);
            descendantsButton.setAttribute("aria-pressed", inDescendants ? "true" : "false");
          }
          if (allButton) {
            allButton.classList.toggle("kg-active", !inNeighbourhood && !inDescendants);
            allButton.setAttribute("aria-pressed", (!inNeighbourhood && !inDescendants) ? "true" : "false");
          }
        }

        function getConcept(nodeId) {
          return conceptData[String(nodeId)] || null;
        }

        function conceptHash(nodeId) {
          return "#concept-" + encodeURIComponent(String(nodeId));
        }

        function conceptIdFromHash(hash) {
          var prefix = "#concept-";
          if (!hash || hash.indexOf(prefix) !== 0) { return null; }
          try {
            return decodeURIComponent(hash.slice(prefix.length));
          } catch (e) {
            return null;
          }
        }

        function pushConceptHistory(nodeId, mode) {
          var hash = conceptHash(nodeId);
          var state = {
            nodeId: String(nodeId),
            mode: mode || "highlight"
          };
          var currentState = window.history.state || {};
          if (
            window.location.hash === hash &&
            currentState.nodeId === state.nodeId &&
            currentState.mode === state.mode
          ) {
            return;
          }
          window.history.pushState(state, "", hash);
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

        function nodeLayerValue(nodeId) {
          var node = originalNodes[nodeId] || nodes.get(nodeId) || {};
          var concept = getConcept(nodeId) || {};
          var candidates = [
            node.layerGroup,
            concept.layer,
            String(nodeId).split(".", 1)[0]
          ];
          for (var i = 0; i < candidates.length; i++) {
            var value = parseInt(String(candidates[i] || "").trim(), 10);
            if (Number.isFinite(value) && value > 0) {
              return value;
            }
          }
          return 0;
        }

        function buildCompactLayerPositions(nodeIds) {
          var ids = nodeIds.slice().sort(compareConceptIds);
          var layers = {};
          ids.forEach(function(id) {
            var layer = nodeLayerValue(id);
            if (layer > 0) { layers[layer] = true; }
          });

          var orderedLayers = Object.keys(layers).map(Number).sort(function(a, b) {
            return b - a;
          });
          var layerToLevel = {};
          orderedLayers.forEach(function(layer, index) {
            layerToLevel[layer] = index;
          });

          var fallbackLevel = orderedLayers.length;
          var nodesByLevel = {};
          ids.forEach(function(id) {
            var layer = nodeLayerValue(id);
            var level = layer > 0 && layerToLevel[layer] !== undefined
              ? layerToLevel[layer]
              : fallbackLevel;
            if (!nodesByLevel[level]) { nodesByLevel[level] = []; }
            nodesByLevel[level].push(id);
          });

          var positions = {};
          Object.keys(nodesByLevel).forEach(function(levelKey) {
            var level = Number(levelKey);
            var rowNodes = nodesByLevel[levelKey].sort(compareConceptIds);
            var rowWidth = (rowNodes.length - 1) * layoutXSpacing;
            var rowSlopeHeight = (rowNodes.length - 1) * layoutRowStagger;
            rowNodes.forEach(function(id, index) {
              positions[id] = {
                x: (index * layoutXSpacing) - (rowWidth / 2),
                y: (level * layoutYSpacing) + (rowSlopeHeight / 2) - (index * layoutRowStagger)
              };
            });
          });
          return positions;
        }

        function conceptSearchText(nodeId, node) {
          var concept = getConcept(nodeId) || {};
          return [
            String(nodeId),
            node && node.label ? String(node.label) : "",
            concept.label || "",
            concept.layer || "",
            concept.layer_title || "",
            concept.definition_new || "",
            concept.derivation_new || "",
            concept.explanation_new || ""
          ].join(" ").toLowerCase();
        }

        function edgeRelation(edge) {
          return String(edge.relation || "");
        }

        function edgeRelationEnabled(edge) {
          var relation = edgeRelation(edge);
          return enabledEdgeRelations[relation] !== false;
        }

        function edgeRelationDirected(edge) {
          var relation = edgeRelation(edge);
          var item = edgeKey[relation] || {};
          return item.directed === true;
        }

        function setEdgeHidden(edge, hidden) {
          edge.hidden = hidden;
          if (hidden) {
            edge.title = "";
          } else if (originalEdges[edge.id] && originalEdges[edge.id].title !== undefined) {
            edge.title = originalEdges[edge.id].title;
          }
          return edge;
        }

        function setEdgeTooltipEnabled(edge, enabled) {
          if (enabled && originalEdges[edge.id] && originalEdges[edge.id].title !== undefined) {
            edge.title = originalEdges[edge.id].title;
          } else if (!enabled) {
            edge.title = "";
          }
          return edge;
        }

        function edgeHoverableInCurrentView(edge) {
          if (!edge || edge.hidden || !edgeRelationEnabled(edge)) {
            return false;
          }
          if (currentView.mode === "highlight" && currentView.nodeId !== null) {
            return edge.from == currentView.nodeId || edge.to == currentView.nodeId;
          }
          if (currentView.mode === "descendants") {
            return edgeRelationDirected(edge);
          }
          return true;
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

        function enabledDirectedDescendants(nodeId) {
          var keep = {};
          var queue = [String(nodeId)];
          keep[String(nodeId)] = true;

          while (queue.length > 0) {
            var current = queue.shift();
            allEdges.forEach(function(edge) {
              if (!edgeRelationEnabled(edge) || !edgeRelationDirected(edge)) { return; }
              if (String(edge.from) !== current) { return; }

              var target = String(edge.to);
              if (keep[target]) { return; }
              keep[target] = true;
              queue.push(target);
            });
          }

          return keep;
        }

        function relationColour(relation) {
          var item = edgeKey[relation] || {};
          return item.colour || "#999999";
        }

        function buildEdgeFilters() {
          var relations = Object.keys(edgeKey).sort();
          var html = "";

          if (relations.length === 0) {
            html += '<div style="color:#555;">No edge key loaded.</div>';
            document.getElementById("kg_edge_filters").innerHTML = html;
            return;
          }

          relations.forEach(function(relation) {
            var inputId = "kg_edge_filter_" + relation.replace(/[^a-zA-Z0-9_-]/g, "_");
            var checked = enabledEdgeRelations[relation] !== false ? " checked" : "";
            html += '<label class="kg-edge-filter" for="' + escapeHtml(inputId) + '">' +
              '<input type="checkbox" id="' + escapeHtml(inputId) +
              '" data-edge-relation="' + escapeHtml(relation) + '"' + checked + '>' +
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
          if (currentView.mode === "descendants" && currentView.nodeId !== null) {
            kgApplyDescendants(currentView.nodeId, true);
            return;
          }
          kgReset(true);
        }

        function restoreHoveredEdge() {
          if (hoveredEdgeId === null || hoveredEdgeBeforeHover === null) {
            return;
          }
          if (edges.get(hoveredEdgeId)) {
            edges.update(Object.assign({}, hoveredEdgeBeforeHover));
          }
          hoveredEdgeId = null;
          hoveredEdgeBeforeHover = null;
        }

        function highlightHoveredEdge(edgeId) {
          restoreHoveredEdge();

          var edge = edges.get(edgeId);
          if (!edgeHoverableInCurrentView(edge)) {
            return;
          }

          var currentWidth = Number(edge.width);
          if (!Number.isFinite(currentWidth) || currentWidth <= 0) {
            currentWidth = 1;
          }

          hoveredEdgeId = edgeId;
          hoveredEdgeBeforeHover = Object.assign({}, edge);

          var hoverStyle = Object.assign({}, edge);
          hoverStyle.width = Math.max(currentWidth, edgeHoverWidth);
          hoverStyle.color = Object.assign({}, edge.color || {}, {opacity: 1.0});
          edges.update(hoverStyle);
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
          html += "<h2>" + escapeHtml(nodeId) + " " + renderConceptText(concept.label) + "</h2>";
          if (layerParts.length > 0) {
            html += "<p>" + layerParts.join(" - ") + "</p>";
          }
          var svgDetail = concept.svg_detail || concept.svg_graphic || concept.svg_icon || "";
          if (svgDetail) {
            html += '<figure class="concept-figure">';
            html += '<div class="concept-graphic">' + svgDetail + "</div>";
            var graphicCaption = concept.svg_detail_caption || concept.svg_icon_caption || "";
            if (graphicCaption) {
              html += '<figcaption class="concept-graphic-caption">' + renderCaptionText(graphicCaption) + "</figcaption>";
            }
            html += "</figure>";
          }
          html += "<hr>";
          [
            ["Definition", concept.definition_new],
            ["Derivation", concept.derivation_new],
            ["Explanation", concept.explanation_new]
          ].forEach(function(section) {
            if (!section[1]) { return; }
            html += "<h3>" + section[0] + "</h3>";
            html += '<div class="concept-body">' + renderConceptText(section[1]) + "</div>";
          });
          document.getElementById("info_panel").innerHTML = html;
          typesetInfoPanel();
        }

        window.kgShowEdgeKey = function() {
          setInfoPanelVisible(true);
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

        window.kgToggleInfoPanel = function() {
          var panel = document.getElementById("info_panel");
          setInfoPanelVisible(panel.classList.contains("kg-hidden"));
          if (currentView.mode === "highlight" && activeNodeId !== null) {
            fitHighlightedSelection(activeNodeId);
          } else {
            updateNodeLabelPositions();
          }
        };

        window.kgToggleControls = function() {
          var panel = document.getElementById("kg_controls");
          setControlsVisible(panel.classList.contains("kg-hidden"));
          if (currentView.mode === "highlight" && activeNodeId !== null) {
            fitHighlightedSelection(activeNodeId);
          } else {
            updateNodeLabelPositions();
          }
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

        function panelAdjustedGraphCenter() {
          var containerRect = graphContainer.getBoundingClientRect();
          var leftInset = 0;
          var rightInset = 0;
          var margin = 24;
          var controlsPanel = document.getElementById("kg_controls");
          var infoPanel = document.getElementById("info_panel");

          if (controlsPanel && !controlsPanel.classList.contains("kg-hidden")) {
            var controlsRect = controlsPanel.getBoundingClientRect();
            leftInset = Math.max(
              leftInset,
              Math.min(containerRect.right, controlsRect.right) - containerRect.left + margin
            );
          }

          if (infoPanel && !infoPanel.classList.contains("kg-hidden")) {
            var infoRect = infoPanel.getBoundingClientRect();
            rightInset = Math.max(
              rightInset,
              containerRect.right - Math.max(containerRect.left, infoRect.left) + margin
            );
          }

          leftInset = Math.max(0, Math.min(leftInset, containerRect.width * 0.45));
          rightInset = Math.max(0, Math.min(rightInset, containerRect.width * 0.45));

          if (leftInset + rightInset > containerRect.width * 0.8) {
            leftInset = 0;
            rightInset = 0;
          }

          return {
            x: leftInset + ((containerRect.width - leftInset - rightInset) / 2),
            y: containerRect.height / 2
          };
        }

        function nodeBoundsCenter(nodeIds) {
          var positions = network.getPositions(nodeIds);
          var minX = Infinity;
          var maxX = -Infinity;
          var minY = Infinity;
          var maxY = -Infinity;

          nodeIds.forEach(function(id) {
            var pos = positions[id];
            if (!pos) { return; }
            minX = Math.min(minX, pos.x);
            maxX = Math.max(maxX, pos.x);
            minY = Math.min(minY, pos.y);
            maxY = Math.max(maxY, pos.y);
          });

          if (!Number.isFinite(minX)) {
            return null;
          }

          return {
            x: (minX + maxX) / 2,
            y: (minY + maxY) / 2
          };
        }

        function shiftViewForPanels(nodeIds) {
          var graphCenter = nodeBoundsCenter(nodeIds);
          if (!graphCenter) { return; }

          var desiredDomCenter = panelAdjustedGraphCenter();
          var currentCanvasAtDesiredCenter = network.DOMtoCanvas(desiredDomCenter);
          var viewPosition = network.getViewPosition();
          var targetPosition = {
            x: viewPosition.x + graphCenter.x - currentCanvasAtDesiredCenter.x,
            y: viewPosition.y + graphCenter.y - currentCanvasAtDesiredCenter.y
          };

          network.moveTo({
            position: targetPosition,
            scale: network.getScale(),
            animation: {
              duration: 250,
              easingFunction: "easeInOutQuad"
            }
          });
        }

        function fitHighlightedSelection(nodeId) {
          var fitIds = [String(nodeId)];
          enabledConnectedNodes(nodeId).forEach(function(id) {
            if (originalNodes[id] && fitIds.indexOf(id) === -1) {
              fitIds.push(id);
            }
          });

          network.fit({nodes: fitIds, animation: false});
          if (network.getScale() > 0.7) {
            network.moveTo({scale: 0.7, animation: false});
          }
          shiftViewForPanels(fitIds);
        }

        function focusConcept(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          activeNodeId = nodeId;
          kgHighlight(nodeId, true);
          showConcept(nodeId);
          setActiveConceptItem(nodeId);
          fitHighlightedSelection(nodeId);
          if (!options.skipHistory) {
            pushConceptHistory(nodeId, "highlight");
          }
          if (statusPrefix) {
            document.getElementById("kg_status").innerText = statusPrefix + " " + nodeId + ".";
          }
        }

        function focusNeighbourhood(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          kgApplyNeighbourhood(nodeId, true);
          showConcept(nodeId);
          setActiveConceptItem(nodeId);
          if (!options.skipHistory) {
            pushConceptHistory(nodeId, "neighbourhood");
          }

          var neighbourCount = enabledConnectedNodes(nodeId).length;
          document.getElementById("kg_status").innerText =
            (statusPrefix ? statusPrefix + " " + nodeId + ". " : "") +
            "Neighbourhood mode: " + nodeId + " plus " + neighbourCount +
            " neighbour" + (neighbourCount === 1 ? "" : "s") +
            ". Click a visible node to walk one step.";
        }

        function focusDescendants(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          kgApplyDescendants(nodeId, true);
          showConcept(nodeId);
          setActiveConceptItem(nodeId);
          if (!options.skipHistory) {
            pushConceptHistory(nodeId, "descendants");
          }

          var descendantCount = Math.max(0, Object.keys(enabledDirectedDescendants(nodeId)).length - 1);
          document.getElementById("kg_status").innerText =
            (statusPrefix ? statusPrefix + " " + nodeId + ". " : "") +
            "Descendants mode: " + nodeId + " plus " + descendantCount +
            " reachable node" + (descendantCount === 1 ? "" : "s") +
            ". Click a visible node to walk one step.";
        }

        function buildConceptList(filterText) {
          var q = String(filterText || "").trim().toLowerCase();
          var ids = Object.keys(conceptData).sort(compareConceptIds);
          var html = "";
          var count = 0;

          ids.forEach(function(id) {
            var concept = getConcept(id);
            var haystack = [
              id,
              concept.label || "",
              concept.layer || "",
              concept.layer_title || "",
              concept.definition_new || "",
              concept.derivation_new || "",
              concept.explanation_new || ""
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

        window.kgReset = function(preserveStatus) {
          restoreHoveredEdge();
          network.unselectAll();
          currentView = {mode: "all", nodeId: null};
          activeNodeId = null;
          updateModeButtons();
          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = false;
            o.opacity = 1.0;
            return o;
          }));
          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            return setEdgeHidden(o, !edgeRelationEnabled(e));
          }));
          updateNodeLabelPositions();
          if (!preserveStatus) {
            document.getElementById("kg_status").innerText = "Click a node to highlight its immediate neighbours.";
          }
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
          var concept = getConcept(id) || {};
          focusConcept(id, null);
          document.getElementById("kg_status").innerText =
            "Found " + matches.length + " match(es). Showing first: " + (concept.label || id);
        };

        window.kgHighlight = function(nodeId, preserveStatus) {
          restoreHoveredEdge();
          activeNodeId = nodeId;
          currentView = {mode: "highlight", nodeId: nodeId};
          updateModeButtons();
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
              return setEdgeHidden(o, true);
            } else if (e.from == nodeId || e.to == nodeId) {
              o.color = Object.assign({}, o.color || {}, {opacity: 0.95});
              o.width = Math.max(Number(o.width) || 0, 3.0);
              return setEdgeHidden(o, false);
            } else {
              o.color = {
                color: "#cccccc",
                highlight: "#cccccc",
                hover: "#cccccc",
                opacity: 0.10
              };
              o.width = 0.4;
              o = setEdgeHidden(o, false);
              return setEdgeTooltipEnabled(o, false);
            }
          }));
          network.unselectAll();
          updateNodeLabelPositions();

          if (!preserveStatus) {
            document.getElementById("kg_status").innerText =
              "Selected " + nodeId + ": showing immediate neighbours.";
          }
        };

        function kgApplyNeighbourhood(nodeId, preserveStatus) {
          restoreHoveredEdge();
          activeNodeId = nodeId;
          currentView = {mode: "neighbourhood", nodeId: nodeId};
          updateModeButtons();
          var connected = enabledConnectedNodes(nodeId);
          var keep = {};
          keep[nodeId] = true;
          connected.forEach(function(id) { keep[id] = true; });
          var visibleIds = Object.keys(originalNodes).filter(function(id) {
            return keep[id];
          });
          var compactPositions = buildCompactLayerPositions(visibleIds);

          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = !keep[n.id];
            if (compactPositions[n.id]) {
              o.x = compactPositions[n.id].x;
              o.y = compactPositions[n.id].y;
            }
            return o;
          }));

          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            return setEdgeHidden(o, !(edgeRelationEnabled(e) && keep[e.from] && keep[e.to]));
          }));

          network.fit({animation: false});
          updateNodeLabelPositions();
          if (!preserveStatus) {
            var neighbourCount = Math.max(0, visibleIds.length - 1);
            document.getElementById("kg_status").innerText =
              "Neighbourhood mode: " + nodeId + " plus " + neighbourCount +
              " neighbour" + (neighbourCount === 1 ? "" : "s") +
              ". Click a visible node to walk one step.";
          }
        }

        function kgApplyDescendants(nodeId, preserveStatus) {
          restoreHoveredEdge();
          activeNodeId = nodeId;
          currentView = {mode: "descendants", nodeId: nodeId};
          updateModeButtons();
          var keep = enabledDirectedDescendants(nodeId);
          var visibleIds = Object.keys(originalNodes).filter(function(id) {
            return keep[id];
          });
          var compactPositions = buildCompactLayerPositions(visibleIds);

          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = !keep[n.id];
            if (compactPositions[n.id]) {
              o.x = compactPositions[n.id].x;
              o.y = compactPositions[n.id].y;
            }
            return o;
          }));

          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            return setEdgeHidden(o, !(
              edgeRelationEnabled(e) &&
              edgeRelationDirected(e) &&
              keep[String(e.from)] &&
              keep[String(e.to)]
            ));
          }));

          network.fit({animation: false});
          updateNodeLabelPositions();
          if (!preserveStatus) {
            var descendantCount = Math.max(0, visibleIds.length - 1);
            document.getElementById("kg_status").innerText =
              "Descendants mode: " + nodeId + " plus " + descendantCount +
              " reachable node" + (descendantCount === 1 ? "" : "s") +
              ". Click a visible node to walk one step.";
          }
        }

        window.kgFocusSelected = function() {
          var selected = network.getSelectedNodes();
          var nodeId = activeNodeId || selected[0];
          if (!nodeId) {
            document.getElementById("kg_status").innerText = "Select a node first.";
            return;
          }

          focusNeighbourhood(nodeId);
        };

        window.kgFocusDescendantsSelected = function() {
          var selected = network.getSelectedNodes();
          var nodeId = activeNodeId || selected[0];
          if (!nodeId) {
            document.getElementById("kg_status").innerText = "Select a node first.";
            return;
          }

          focusDescendants(nodeId);
        };

        network.on("click", function(params) {

            if (params.nodes.length === 0)
                return;

            const nodeId = params.nodes[0];

            if (currentView.mode === "neighbourhood") {
              focusNeighbourhood(nodeId);
            } else if (currentView.mode === "descendants") {
              focusDescendants(nodeId);
            } else {
              focusConcept(nodeId, "Selected");
            }
        });

        network.on("hoverEdge", function(params) {
          if (params.edge !== undefined && params.edge !== null) {
            highlightHoveredEdge(params.edge);
          }
        });

        network.on("blurEdge", function(params) {
          if (params.edge === hoveredEdgeId) {
            restoreHoveredEdge();
          }
        });

        network.on("afterDrawing", function(ctx) {
          drawVisibleNodes(ctx);
          updateNodeLabelPositions();
        });
        network.on("dragEnd", updateNodeLabelPositions);
        network.on("zoom", updateNodeLabelPositions);
        network.on("animationFinished", updateNodeLabelPositions);
        window.addEventListener("resize", updateNodeLabelPositions);
        graphContainer.addEventListener("mouseleave", restoreHoveredEdge);

        window.addEventListener("popstate", function(event) {
          var nodeId = event.state && event.state.nodeId;
          var mode = event.state && event.state.mode;
          if (!nodeId) {
            nodeId = conceptIdFromHash(window.location.hash);
          }

          if (nodeId && getConcept(nodeId)) {
            if (mode === "neighbourhood") {
              focusNeighbourhood(nodeId, null, {skipHistory: true});
            } else if (mode === "descendants") {
              focusDescendants(nodeId, null, {skipHistory: true});
            } else {
              focusConcept(nodeId, "Selected", {skipHistory: true});
            }
          } else {
            kgReset(true);
          }
        });

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

          if (currentView.mode === "neighbourhood") {
            focusNeighbourhood(id, "Selected");
          } else if (currentView.mode === "descendants") {
            focusDescendants(id, "Selected");
          } else {
            focusConcept(id, "Selected");
          }
        });

        // Build legend from node groups.
        var groups = {};
        allNodes.forEach(function(n) {
          if (n.layerGroup !== undefined) { groups[n.layerGroup] = true; }
        });
        var legend = document.getElementById("kg_legend");
        var html = "";
        Object.keys(groups).sort(function(a,b){return Number(b)-Number(a);}).forEach(function(g) {
          var sample = allNodes.find(function(n) { return String(n.layerGroup) === String(g); });
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
        edges.update(allEdges.map(function(e) {
          var o = Object.assign({}, e);
          return setEdgeHidden(o, !edgeRelationEnabled(e));
        }));
        allEdges = edges.get();

        var initialNodeId = conceptIdFromHash(window.location.hash);
        if (initialNodeId && getConcept(initialNodeId)) {
          window.history.replaceState(
            {nodeId: String(initialNodeId), mode: "highlight"},
            "",
            conceptHash(initialNodeId)
          );
          focusConcept(initialNodeId, "Selected", {skipHistory: true});
        } else {
          window.history.replaceState({}, "", window.location.href);
        }
      }

      // Wait until pyvis has created network/nodes/edges variables.
      (function waitForKgNetwork() {
        if (
          typeof network !== "undefined" &&
          typeof nodes !== "undefined" &&
          typeof edges !== "undefined"
        ) {
          kgAfterReady();
          return;
        }
        setTimeout(waitForKgNetwork, 20);
      })();
    </script>
    """.replace("__CONCEPT_DATA__", concept_data_json).replace("__EDGE_KEY__", edge_key_json)
    js = js.replace("__EDGE_HOVER_WIDTH__", str(EDGE_HOVER_WIDTH))
    js = js.replace("__NODE_LABEL_WIDTH__", str(NODE_LABEL_WIDTH))
    js = js.replace("__NODE_LABEL_FONT_SIZE__", str(NODE_LABEL_FONT_SIZE))
    js = js.replace("__LAYOUT_X_SPACING__", str(LAYOUT_X_SPACING))
    js = js.replace("__LAYOUT_Y_SPACING__", str(LAYOUT_Y_SPACING))
    js = js.replace("__LAYOUT_ROW_STAGGER__", str(LAYOUT_ROW_STAGGER))

    css = css.replace("__NODE_LABEL_WIDTH__", str(NODE_LABEL_WIDTH))
    css = css.replace("__NODE_LABEL_FONT_SIZE__", str(NODE_LABEL_FONT_SIZE))
    css = css.replace("__NODE_LABEL_FONT_WEIGHT__", str(NODE_LABEL_FONT_WEIGHT))

    for marker in ("</head>", "<body>", "</body>"):
        require_html_marker(html_text, marker)

    html_text = html_text.replace("</head>", mathjax + "\n" + css + "\n</head>")
    html_text = html_text.replace("<body>", "<body>\n" + controls)
    html_text = html_text.replace("</body>", js + "\n</body>")
    return html_text
