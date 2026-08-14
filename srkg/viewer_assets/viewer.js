      /* Runtime data injected by srkg.html_injection. */
      var conceptData = __CONCEPT_DATA__;
      var edgeKey = __EDGE_KEY__;
      var kgViewerConfig = __VIEWER_CONFIG__;
      var kgLayoutConfig = kgViewerConfig.layout || {};
      var kgNodeLabelConfig = kgViewerConfig.nodeLabels || {};
      var kgInfoPanelConfig = kgViewerConfig.infoPanel || {};
      var kgStorageKeys = kgViewerConfig.storageKeys || {};
      var layoutXSpacing = kgLayoutConfig.xSpacing;
      var layoutYSpacing = kgLayoutConfig.ySpacing;
      var layoutRowStagger = kgLayoutConfig.rowStagger;
      var edgeHoverWidth = kgViewerConfig.edgeHoverWidth;

      var GraphViewMode = Object.freeze({
        ALL: "all",
        FOCUSED: "focused",
        HIGHLIGHT: "highlight",
        HIDE: "hide",
        NEIGHBOURHOOD: "neighbourhood",
        DESCENDANTS: "descendants",
        DERIVATION_TRACE: "derivation-trace"
      });
      var GraphViewSelectValue = Object.freeze({
        ALL: "all",
        FOCUSED: "focused",
        HIDE: "hide",
        NEIGHBOURHOOD_1: "neighbourhood-1",
        NEIGHBOURHOOD_2: "neighbourhood-2",
        DESCENDANTS: "descendants",
        DERIVATION_TRACE: "derivation-trace"
      });

      function clampNeighbourhoodRadius(radius) {
        return Math.max(1, Math.min(2, Math.floor(Number(radius) || 1)));
      }

      function createGraphView(mode, nodeId, options) {
        options = options || {};
        var view = {
          mode: mode || GraphViewMode.ALL,
          nodeId: nodeId === undefined || nodeId === null ? null : String(nodeId)
        };
        if (view.mode === GraphViewMode.NEIGHBOURHOOD) {
          view.radius = clampNeighbourhoodRadius(options.radius);
        }
        return view;
      }

      function graphViewIs(view, mode) {
        return Boolean(view && view.mode === mode);
      }

      function graphViewHasNode(view) {
        return Boolean(view && view.nodeId !== null && view.nodeId !== undefined);
      }

      function graphViewRadius(view) {
        return clampNeighbourhoodRadius(view && view.radius);
      }

      function graphViewHistoryMode(view) {
        if (!view) { return GraphViewMode.HIGHLIGHT; }
        if (graphViewIs(view, GraphViewMode.FOCUSED)) {
          return GraphViewSelectValue.FOCUSED;
        }
        if (graphViewIs(view, GraphViewMode.NEIGHBOURHOOD)) {
          return "neighbourhood-" + String(graphViewRadius(view));
        }
        return view.mode || GraphViewMode.HIGHLIGHT;
      }

      function graphViewSelectValue(view) {
        if (graphViewIs(view, GraphViewMode.HIDE)) { return GraphViewSelectValue.HIDE; }
        if (graphViewIs(view, GraphViewMode.FOCUSED)) { return GraphViewSelectValue.FOCUSED; }
        return GraphViewSelectValue.ALL;
      }

      function graphViewFromHistoryMode(mode, nodeId) {
        if (mode === GraphViewMode.HIDE) {
          return createGraphView(GraphViewMode.HIDE, nodeId);
        }
        if (mode === GraphViewMode.FOCUSED || mode === GraphViewSelectValue.FOCUSED) {
          return createGraphView(GraphViewMode.FOCUSED, nodeId);
        }
        if (mode === GraphViewMode.NEIGHBOURHOOD || mode === GraphViewSelectValue.NEIGHBOURHOOD_1) {
          return createGraphView(GraphViewMode.FOCUSED, nodeId);
        }
        if (mode === GraphViewSelectValue.NEIGHBOURHOOD_2) {
          return createGraphView(GraphViewMode.FOCUSED, nodeId);
        }
        if (mode === GraphViewMode.DESCENDANTS) {
          return createGraphView(GraphViewMode.FOCUSED, nodeId);
        }
        if (mode === GraphViewMode.DERIVATION_TRACE) {
          return createGraphView(GraphViewMode.FOCUSED, nodeId);
        }
        return createGraphView(GraphViewMode.HIGHLIGHT, nodeId);
      }

      function kgAfterReady() {
        var allNodes = nodes.get();
        var allEdges = edges.get();
        var graphContainer = document.getElementById("mynetwork");
        var nodeLabelLayer = document.createElement("div");
        var nodeTooltip = document.createElement("div");
        var conceptPreview = document.createElement("div");
        var nodeLabelEls = {};
        var defaultViewTitle = document.getElementById("kg_view_title")
          ? document.getElementById("kg_view_title").textContent
          : "";

        nodeLabelLayer.id = "kg_node_labels";
        graphContainer.appendChild(nodeLabelLayer);
        buildWorkspaceShell();
        nodeTooltip.id = "kg_node_tooltip";
        nodeTooltip.setAttribute("role", "tooltip");
        document.body.appendChild(nodeTooltip);
        conceptPreview.id = "kg_concept_preview";
        conceptPreview.setAttribute("role", "dialog");
        conceptPreview.setAttribute("aria-live", "polite");
        document.body.appendChild(conceptPreview);

        var originalNodes = {};
        var originalEdges = {};
        var currentView = createGraphView(GraphViewMode.ALL);
        var activeNodeId = null;
        var hoveredEdgeId = null;
        var hoveredEdgeBeforeHover = null;
        var svgImageCache = {};
        var activeNodeRadiusScale = 1.4;
        var activeNodeBorderWidth = 6;
        var nodeLabelWidth = kgNodeLabelConfig.width;
        var nodeLabelFontSize = kgNodeLabelConfig.fontSize;
        var tooltipTypesetTimer = null;
        var conceptPreviewTypesetTimer = null;
        var conceptPreviewHideTimer = null;
        var conceptPreviewPinned = false;
        var conceptPreviewAnchor = null;
        var defaultStartupConceptId = null;
        var transientConceptHighlight = null;
        var transientEdgeSnapshots = {};
        var userNotesStorageKey = kgStorageKeys.userNotes;
        var noteEditingStorageKey = kgStorageKeys.noteEditing;
        var splashDismissedStorageKey = kgStorageKeys.splashDismissed;
        var userNotesState = loadUserNotes();
        var noteEditingEnabled = loadNoteEditingPreference();
        var openUserNoteId = null;
        var infoPanelPinchState = null;
        var readingMode = "full";
        var activeConceptSectionContext = "neighbourhood";
        var activeConceptSectionTargetId = null;
        var activeConceptSectionLensLabel = "Neighbourhood";
        var currentConceptTocItems = [];
        var detailScrollSyncTimer = null;
        var detailScrollSyncSuppressedUntil = 0;
        var derivedFromFullTreeEnabled = false;
        var backlinksFullTreeEnabled = false;
        var pendingGraphSectionContext = null;
        var focusLensVisible = false;
        var workspaceSplitPercent = 50;
        var workspaceSplitterPointerId = null;

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
          return '<span class="kg-node-label-id">' + escapeHtml(conceptDisplayId(nodeId)) + '</span>' +
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

        function typesetVisibleTooltip() {
          var tooltip = nodeTooltip;
          if (!tooltip || !window.MathJax || !MathJax.typesetPromise) { return; }
          if (MathJax.typesetClear) {
            MathJax.typesetClear([tooltip]);
          }
          MathJax.typesetPromise([tooltip]).catch(function(err) {
            console.warn("MathJax tooltip typesetting failed:", err);
          });
        }

        function scheduleTooltipTypeset() {
          if (tooltipTypesetTimer) {
            clearTimeout(tooltipTypesetTimer);
          }
          tooltipTypesetTimer = setTimeout(function() {
            tooltipTypesetTimer = null;
            typesetVisibleTooltip();
          }, 180);
        }

        function positionNodeTooltip(pointer) {
          if (!nodeTooltip || !pointer || !pointer.DOM) { return; }
          var containerRect = graphContainer.getBoundingClientRect();
          var margin = 10;
          var x = containerRect.left + pointer.DOM.x + 14;
          var y = containerRect.top + pointer.DOM.y + 14;
          var rect = nodeTooltip.getBoundingClientRect();
          var maxX = window.innerWidth - rect.width - margin;
          var maxY = window.innerHeight - rect.height - margin;
          nodeTooltip.style.left = Math.max(margin, Math.min(x, maxX)) + "px";
          nodeTooltip.style.top = Math.max(margin, Math.min(y, maxY)) + "px";
        }

        function showNodeTooltip(nodeId, pointer) {
          if (!nodeTooltip || graphViewIs(currentView, GraphViewMode.HIDE) || !getConcept(nodeId)) { return; }
          nodeTooltip.innerHTML = conceptTooltipHtml(nodeId);
          nodeTooltip.style.display = "block";
          positionNodeTooltip(pointer);
          scheduleTooltipTypeset();
        }

        function hideNodeTooltip() {
          if (tooltipTypesetTimer) {
            clearTimeout(tooltipTypesetTimer);
            tooltipTypesetTimer = null;
          }
          if (nodeTooltip) {
            nodeTooltip.style.display = "none";
            nodeTooltip.innerHTML = "";
          }
        }

        function updateNodeLabelPositions() {
          if (!network || !nodeLabelLayer) { return; }

          var positions = network.getPositions();
          var rawScale = network.getScale ? network.getScale() : 1;
          var labelScale = Math.max(0.25, rawScale);
          var visibleFontSize = nodeLabelFontSize * rawScale;
          Object.keys(nodeLabelEls).forEach(function(id) {
            var el = nodeLabelEls[id];
            var node = nodes.get(id);
            var pos = positions[id];
            if (!node || !pos || node.hidden || visibleFontSize <= kgNodeLabelConfig.hideBelowPx) {
              el.classList.remove("kg-node-label-transient");
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
            var labelWidth = nodeLabelWidth * labelScale;
            el.style.display = "block";
            el.style.width = labelWidth + "px";
            el.style.fontSize = (nodeLabelFontSize * labelScale) + "px";
            el.style.left = (labelCenterX - labelWidth / 2) + "px";
            el.style.top = labelTopY + "px";
            el.style.opacity = node.opacity === undefined ? "1" : String(node.opacity);
            el.classList.toggle(
              "kg-node-label-transient",
              Boolean(transientConceptHighlight && transientConceptHighlight.nodeId === String(id))
            );
          });
        }
        window.kgUpdateNodeLabelPositions = updateNodeLabelPositions;

        function drawVisibleNodes(ctx) {
          var positions = network.getPositions();
          nodes.get().forEach(function(node) {
            if (node.hidden) { return; }

            var pos = positions[node.id];
            if (!pos) { return; }

            var baseRadius = Number(node.visualSize) || 18;
            var isActive = node.id === activeNodeId;
            var radius = isActive ? baseRadius * activeNodeRadiusScale : baseRadius;
            var isTransient = transientConceptHighlight &&
              transientConceptHighlight.nodeId === String(node.id);
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

            if (isTransient) {
              ctx.beginPath();
              ctx.arc(pos.x, pos.y, radius + 6, 0, 2 * Math.PI, false);
              ctx.lineWidth = 4;
              ctx.strokeStyle = "#174ea6";
              ctx.stroke();
            }
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
        refreshNodeTooltips();
        /* Text parsing and concept markup. */
        function escapeHtml(s) {
          return String(s || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
        }

        function cssAttributeValueEscape(s) {
          return String(s || "").replace(/\\/g, "\\\\").replace(/"/g, '\\"');
        }

        function renderSimpleConceptText(s) {
          return escapeHtml(s).replace(
            /\\cref\{([^{}]*)\}\{([^{}]*)\}/g,
            function(match, label, targetId) {
              if (!getConcept(targetId)) {
                return "<strong>" + label + "</strong>";
              }
              return '<a href="' + escapeHtml(conceptHash(targetId)) +
                '" class="concept-link" data-concept-id="' +
                escapeHtml(targetId) +
                '" aria-haspopup="dialog" aria-controls="kg_concept_preview' +
                '"><strong>' + label + "</strong></a>";
            }
          );
        }

        function skipOptionalDetailWhitespace(text, index) {
          while (index < text.length && /\s/.test(text.charAt(index))) {
            index += 1;
          }
          return index;
        }

        function parseBracedArgument(text, openIndex) {
          if (text.charAt(openIndex) !== "{") { return null; }

          var depth = 1;
          var index = openIndex + 1;
          var start = index;
          while (index < text.length) {
            var ch = text.charAt(index);
            if (ch === "\\") {
              index += 2;
              continue;
            }
            if (ch === "{") {
              depth += 1;
            } else if (ch === "}") {
              depth -= 1;
              if (depth === 0) {
                return {
                  value: text.slice(start, index),
                  end: index + 1
                };
              }
            }
            index += 1;
          }
          return null;
        }

        function renderFoldDown(options) {
          var attrs = "";
          if (options.anchorId) {
            attrs += ' id="' + escapeHtml(options.anchorId) + '"';
          }
          if (options.id) {
            attrs += ' data-note-id="' + escapeHtml(options.id) + '"';
          }
          if (options.sectionRole) {
            attrs += ' data-section-role="' + escapeHtml(options.sectionRole) + '"';
            attrs += ' data-graph-context="' +
              escapeHtml(graphContextForSectionRole(options.sectionRole)) + '"';
            attrs += ' data-lens-label="' +
              escapeHtml(lensLabelForSectionRole(options.sectionRole)) + '"';
          }
          if (options.open) {
            attrs += " open";
          }
          var summaryHtml = options.summaryHtml !== undefined
            ? options.summaryHtml
            : renderConceptText(options.title || "");
          var bodyTag = options.bodyTag || "div";
          return '<details class="' + escapeHtml(options.className) + '"' + attrs + ">" +
            "<summary>" + summaryHtml + "</summary>" +
            "<" + bodyTag + ' class="' + escapeHtml(options.bodyClass || "") + '">' +
            (options.bodyHtml || "") +
            "</" + bodyTag + "></details>";
        }

        function renderOptionalDetail(summary, body) {
          return renderFoldDown({
            className: "optional-detail",
            title: summary,
            bodyClass: "concept-body optional-detail-body",
            bodyHtml: renderConceptText(body)
          });
        }

        function renderConceptText(s) {
          var text = String(s || "");
          var macro = "\\optional_details";
          var html = "";
          var cursor = 0;

          while (cursor < text.length) {
            var macroIndex = text.indexOf(macro, cursor);
            if (macroIndex === -1) {
              html += renderSimpleConceptText(text.slice(cursor));
              break;
            }

            html += renderSimpleConceptText(text.slice(cursor, macroIndex));
            var summaryStart = skipOptionalDetailWhitespace(text, macroIndex + macro.length);
            var summary = parseBracedArgument(text, summaryStart);
            if (!summary) {
              html += renderSimpleConceptText(macro);
              cursor = macroIndex + macro.length;
              continue;
            }

            var bodyStart = skipOptionalDetailWhitespace(text, summary.end);
            var body = parseBracedArgument(text, bodyStart);
            if (!body) {
              html += renderSimpleConceptText(text.slice(macroIndex, summary.end));
              cursor = summary.end;
              continue;
            }

            html += renderOptionalDetail(summary.value, body.value);
            cursor = body.end;
          }

          return html;
        }

        /* User notes and local persistence. */
        function safeLocalStorageGet(key) {
          try {
            return window.localStorage.getItem(key);
          } catch (err) {
            return null;
          }
        }

        function safeLocalStorageSet(key, value) {
          try {
            window.localStorage.setItem(key, value);
            return true;
          } catch (err) {
            return false;
          }
        }

        function loadUserNotes() {
          var raw = safeLocalStorageGet(userNotesStorageKey);
          if (!raw) { return {version: 1, notes: []}; }
          try {
            var parsed = JSON.parse(raw);
            if (!parsed || !Array.isArray(parsed.notes)) {
              return {version: 1, notes: []};
            }
            return {
              version: 1,
              notes: parsed.notes.map(normalizeUserNote).filter(Boolean)
            };
          } catch (err) {
            return {version: 1, notes: []};
          }
        }

        function saveUserNotes() {
          var saved = safeLocalStorageSet(userNotesStorageKey, JSON.stringify(userNotesState));
          setNotesStatus(saved ? "Notes saved locally." : "Could not save notes locally.");
          refreshNodeTooltips();
          renderNotesOverview();
          return saved;
        }

        function loadNoteEditingPreference() {
          return safeLocalStorageGet(noteEditingStorageKey) === "true";
        }

        function saveNoteEditingPreference() {
          safeLocalStorageSet(noteEditingStorageKey, noteEditingEnabled ? "true" : "false");
        }

        function splashDismissed() {
          return safeLocalStorageGet(splashDismissedStorageKey) === "true";
        }

        function dismissSplash() {
          safeLocalStorageSet(splashDismissedStorageKey, "true");
          var dialog = document.getElementById("kg_splash_dialog");
          if (!dialog) { return; }
          if (dialog.close) {
            dialog.close();
          } else {
            dialog.removeAttribute("open");
          }
        }

        window.kgShowSplash = function() {
          var dialog = document.getElementById("kg_splash_dialog");
          if (!dialog) { return; }
          if (dialog.showModal && !dialog.open) {
            dialog.showModal();
          } else {
            dialog.setAttribute("open", "open");
          }
        };

        function showSplashOnFirstLoad() {
          if (!splashDismissed()) {
            window.kgShowSplash();
          }
        }

        function setNotesStatus(message) {
          var el = document.getElementById("kg_notes_status");
          if (el) { el.innerText = message || ""; }
        }

        function noteIsDefaultEmpty(note) {
          return note &&
            String(note.title || "").trim() === "Note" &&
            String(note.body || "").trim() === "";
        }

        function normalizeUserNote(note) {
          if (!note || !note.conceptId || !note.section) { return null; }
          var anchor = note.anchor || {};
          var blockIndex = Number(anchor.blockIndex);
          if (!Number.isFinite(blockIndex) || blockIndex < 0) { blockIndex = 0; }
          return {
            id: String(note.id || makeNoteId()),
            conceptId: String(note.conceptId),
            section: String(note.section),
            anchor: {
              blockIndex: Math.floor(blockIndex),
              afterText: String(anchor.afterText || "")
            },
            title: String(note.title || "Untitled note"),
            body: String(note.body || ""),
            createdAt: String(note.createdAt || new Date().toISOString()),
            updatedAt: String(note.updatedAt || note.createdAt || new Date().toISOString())
          };
        }

        function makeNoteId() {
          return "note-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 9);
        }

        function notesForAnchor(conceptId, sectionName, anchorIndex) {
          return userNotesState.notes.filter(function(note) {
            return note.conceptId === String(conceptId) &&
              note.section === String(sectionName) &&
              Number(note.anchor && note.anchor.blockIndex) === Number(anchorIndex);
          }).sort(function(a, b) {
            return String(a.createdAt).localeCompare(String(b.createdAt));
          });
        }

        function findUserNote(noteId) {
          return userNotesState.notes.find(function(note) {
            return note.id === noteId;
          }) || null;
        }

        function noteConceptLabel(note) {
          var concept = getConcept(note.conceptId) || {};
          return note.conceptId + (concept.label ? " " + searchDisplayText(concept.label) : "");
        }

        function sortedUserNotes() {
          return userNotesState.notes.slice().sort(function(a, b) {
            var conceptOrder = compareConceptIds(a.conceptId, b.conceptId);
            if (conceptOrder !== 0) { return conceptOrder; }
            return String(a.createdAt).localeCompare(String(b.createdAt));
          });
        }

        function renderNotesOverview() {
          var countEl = document.getElementById("kg_notes_count");
          var listEl = document.getElementById("kg_notes_list");
          if (!countEl || !listEl) { return; }

          var count = userNotesState.notes.length;
          countEl.innerText = count + " note" + (count === 1 ? "" : "s");
          if (count === 0) {
            listEl.innerHTML = '<div class="kg-note-list-empty">No notes yet.</div>';
            return;
          }

          listEl.innerHTML = sortedUserNotes().map(function(note) {
            return '<button type="button" class="kg-note-list-item" data-note-id="' +
              escapeHtml(note.id) + '" data-concept-id="' + escapeHtml(note.conceptId) + '">' +
              '<span class="kg-note-list-concept">' + escapeHtml(noteConceptLabel(note)) + "</span>" +
              '<span class="kg-note-list-title">' + escapeHtml(note.title || "Untitled note") + "</span>" +
              "</button>";
          }).join("");
        }

        function renderUserNote(note) {
          if (noteEditingEnabled) {
            var shouldOpen = note.id === openUserNoteId;
            var html = '<details class="user-note" data-note-id="' + escapeHtml(note.id) + '"' +
              (shouldOpen ? " open" : "") + ">";
            html += "<summary>" + renderConceptText(note.title || "Untitled note") + "</summary>";
            html += '<div class="user-note-editor">';
            html += '<label>Title<input class="user-note-title-input" data-note-id="' +
              escapeHtml(note.id) + '" value="' + escapeHtml(note.title || "") + '"></label>';
            html += '<label>Note<textarea class="user-note-body-input" data-note-id="' +
              escapeHtml(note.id) + '">' + escapeHtml(note.body || "") + "</textarea></label>";
            html += '<div class="user-note-actions">';
            html += '<button type="button" class="user-note-close" data-note-id="' +
              escapeHtml(note.id) + '">Close</button>';
            html += '<button type="button" class="user-note-delete" data-note-id="' +
              escapeHtml(note.id) + '">Delete</button>';
            html += '<span class="user-note-saved">Saved locally</span>';
            html += "</div></div>";
            html += "</details>";
            return html;
          }
          return renderFoldDown({
            className: "user-note",
            id: note.id,
            title: note.title || "Untitled note",
            bodyClass: "user-note-body",
            bodyHtml: renderConceptText(note.body || "")
          });
        }

        function renderNotesAtAnchor(conceptId, sectionName, anchorIndex, afterText) {
          var html = "";
          notesForAnchor(conceptId, sectionName, anchorIndex).forEach(function(note) {
            html += renderUserNote(note);
          });
          html += '<div class="kg-add-note-row">';
          html += '<button type="button" class="kg-add-note" data-section="' +
            escapeHtml(sectionName) + '" data-anchor-index="' + String(anchorIndex) +
            '" data-anchor-after="' + escapeHtml(afterText || "") + '">+ note</button>';
          html += "</div>";
          return html;
        }

        function findNextOptionalDetailBlock(text, cursor) {
          var macro = "\\optional_details";
          var search = cursor;
          while (search < text.length) {
            var macroIndex = text.indexOf(macro, search);
            if (macroIndex === -1) { return null; }

            var summaryStart = skipOptionalDetailWhitespace(text, macroIndex + macro.length);
            var summary = parseBracedArgument(text, summaryStart);
            if (!summary) {
              search = macroIndex + macro.length;
              continue;
            }

            var bodyStart = skipOptionalDetailWhitespace(text, summary.end);
            var body = parseBracedArgument(text, bodyStart);
            if (!body) {
              search = summary.end;
              continue;
            }

            return {
              kind: "optional",
              start: macroIndex,
              end: body.end
            };
          }
          return null;
        }

        function contentAnchorId(conceptId, title) {
          var slug = String(conceptId || "") + "-" + String(title || "");
          slug = slug.toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");
          return "kg-toc-" + (slug || "section");
        }

        function findNextDisplayMathBlock(text, cursor) {
          var open = "\\[";
          var close = "\\]";
          var start = text.indexOf(open, cursor);
          if (start === -1) { return null; }
          var end = text.indexOf(close, start + open.length);
          if (end === -1) { return null; }
          return {
            kind: "display-math",
            start: start,
            end: end + close.length
          };
        }

        function findNextLineBreakBlock(text, cursor) {
          var lf = text.indexOf("\n", cursor);
          var cr = text.indexOf("\r", cursor);
          if (lf === -1 && cr === -1) { return null; }
          if (cr !== -1 && (lf === -1 || cr < lf)) {
            return {
              kind: "newline",
              start: cr,
              end: text.charAt(cr + 1) === "\n" ? cr + 2 : cr + 1
            };
          }
          return {
            kind: "newline",
            start: lf,
            end: lf + 1
          };
        }

        function splitConceptBlocks(text) {
          var blocks = [];
          var raw = String(text || "");
          var cursor = 0;

          function pushText(value) {
            if (!String(value || "").trim()) { return; }
            blocks.push({kind: "text", text: value});
          }

          while (cursor < raw.length) {
            var newlineBlock = findNextLineBreakBlock(raw, cursor);
            var optionalBlock = findNextOptionalDetailBlock(raw, cursor);
            var displayBlock = findNextDisplayMathBlock(raw, cursor);
            var candidates = [];
            if (newlineBlock) { candidates.push(newlineBlock); }
            if (optionalBlock) { candidates.push(optionalBlock); }
            if (displayBlock) { candidates.push(displayBlock); }

            if (candidates.length === 0) {
              pushText(raw.slice(cursor));
              break;
            }

            candidates.sort(function(a, b) {
              return a.start - b.start || a.end - b.end;
            });
            var next = candidates[0];
            if (next.start > cursor) {
              pushText(raw.slice(cursor, next.start));
            } else if (next.kind === "newline") {
              blocks.push({kind: "text", text: ""});
            }

            if (next.kind !== "newline") {
              blocks.push({
                kind: next.kind,
                text: raw.slice(next.start, next.end)
              });
            }
            cursor = next.end;
          }

          if (raw.length === 0) {
            return [];
          }
          return blocks;
        }

        function renderConceptSection(conceptId, title, text) {
          var raw = String(text || "");
          if (!raw) { return ""; }
          var blocks = splitConceptBlocks(raw);
          var html = '<h3 id="' + escapeHtml(contentAnchorId(conceptId, title)) + '">' +
            escapeHtml(title) + "</h3>";
          html += '<div class="concept-body concept-section" data-section="' + escapeHtml(title) + '">';
          html += renderNotesAtAnchor(conceptId, title, 0, "");
          blocks.forEach(function(block, index) {
            html += '<div class="concept-line">' + (block.text ? renderConceptText(block.text) : "&nbsp;") + "</div>";
            html += renderNotesAtAnchor(conceptId, title, index + 1, block.text.slice(0, 160));
          });
          html += "</div>";
          return html;
        }

        function normalizeStudyText(text) {
          return String(text || "")
            .replace(/\\n\\n/g, "\n")
            .replace(/\\n(?=(?:[A-Z]|[0-9]+)[.)]\s)/g, "\n");
        }

        function renderBodyLines(text, className) {
          var blocks = splitConceptBlocks(text);
          var html = '<div class="' + escapeHtml(className || "concept-body") + '">';
          blocks.forEach(function(block) {
            html += '<div class="concept-line">' +
              (block.text ? renderConceptText(block.text) : "&nbsp;") +
              "</div>";
          });
          html += "</div>";
          return html;
        }

        function renderStudyText(text, className) {
          return renderBodyLines(normalizeStudyText(text), className);
        }

        function createUserNote(conceptId, sectionName, anchorIndex, afterText) {
          var now = new Date().toISOString();
          var note = {
            id: makeNoteId(),
            conceptId: String(conceptId),
            section: String(sectionName),
            anchor: {
              blockIndex: Number(anchorIndex) || 0,
              afterText: String(afterText || "")
            },
            title: "Note",
            body: "",
            createdAt: now,
            updatedAt: now
          };
          userNotesState.notes.push(note);
          openUserNoteId = note.id;
          saveUserNotes();
          return note;
        }

        function deleteUserNote(noteId) {
          userNotesState.notes = userNotesState.notes.filter(function(note) {
            return note.id !== noteId;
          });
          if (openUserNoteId === noteId) { openUserNoteId = null; }
          saveUserNotes();
        }

        function updateUserNote(noteId, fields) {
          var note = findUserNote(noteId);
          if (!note) { return; }
          Object.keys(fields).forEach(function(key) {
            note[key] = String(fields[key]);
          });
          note.updatedAt = new Date().toISOString();
          saveUserNotes();
        }

        function noteEditorField(noteId, selector) {
          var fields = document.querySelectorAll(selector);
          for (var i = 0; i < fields.length; i++) {
            if (fields[i].getAttribute("data-note-id") === noteId) {
              return fields[i];
            }
          }
          return null;
        }

        function syncUserNoteFromEditor(noteId) {
          var note = findUserNote(noteId);
          if (!note) { return null; }
          var titleInput = noteEditorField(noteId, ".user-note-title-input");
          var bodyInput = noteEditorField(noteId, ".user-note-body-input");
          if (titleInput) { note.title = String(titleInput.value || ""); }
          if (bodyInput) { note.body = String(bodyInput.value || ""); }
          note.updatedAt = new Date().toISOString();
          saveUserNotes();
          return note;
        }

        function closeUserNote(noteId) {
          var note = syncUserNoteFromEditor(noteId);
          if (!note) { return; }
          if (noteIsDefaultEmpty(note)) {
            deleteUserNote(noteId);
          } else {
            openUserNoteId = null;
          }
          refreshActiveConcept();
        }

        function refreshActiveConcept() {
          if (activeNodeId && getConcept(activeNodeId)) {
            showConcept(activeNodeId, {preserveSectionContext: true});
          }
        }

        function csvEscape(value) {
          var text = String(value || "");
          if (/[",\r\n]/.test(text)) {
            return '"' + text.replace(/"/g, '""') + '"';
          }
          return text;
        }

        function notesToCsv() {
          var rows = [[
            "note_id",
            "concept_id",
            "concept_label",
            "section",
            "anchor_index",
            "anchor_after",
            "title",
            "body",
            "created_at",
            "updated_at"
          ]];
          userNotesState.notes.forEach(function(note) {
            var concept = getConcept(note.conceptId) || {};
            rows.push([
              note.id,
              note.conceptId,
              concept.label || "",
              note.section,
              String((note.anchor && note.anchor.blockIndex) || 0),
              (note.anchor && note.anchor.afterText) || "",
              note.title || "",
              note.body || "",
              note.createdAt || "",
              note.updatedAt || ""
            ]);
          });
          return rows.map(function(row) {
            return row.map(csvEscape).join(",");
          }).join("\n") + "\n";
        }

        window.kgExportNotes = function() {
          var csv = notesToCsv();
          var blob = new Blob([csv], {type: "text/csv;charset=utf-8"});
          var url = URL.createObjectURL(blob);
          var link = document.createElement("a");
          link.href = url;
          link.download = "srkg-notes.csv";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
          setNotesStatus("Exported " + userNotesState.notes.length + " note(s).");
        };

        function parseCsv(text) {
          var rows = [];
          var row = [];
          var field = "";
          var inQuotes = false;
          for (var index = 0; index < text.length; index += 1) {
            var ch = text.charAt(index);
            if (inQuotes) {
              if (ch === '"') {
                if (text.charAt(index + 1) === '"') {
                  field += '"';
                  index += 1;
                } else {
                  inQuotes = false;
                }
              } else {
                field += ch;
              }
            } else if (ch === '"') {
              inQuotes = true;
            } else if (ch === ",") {
              row.push(field);
              field = "";
            } else if (ch === "\n") {
              row.push(field);
              rows.push(row);
              row = [];
              field = "";
            } else if (ch !== "\r") {
              field += ch;
            }
          }
          if (field || row.length > 0) {
            row.push(field);
            rows.push(row);
          }
          return rows;
        }

        function importNotesCsv(text) {
          var rows = parseCsv(text).filter(function(row) {
            return row.some(function(value) { return String(value || "").trim(); });
          });
          if (rows.length < 2) { return 0; }
          var headers = {};
          rows[0].forEach(function(name, index) {
            headers[String(name).trim()] = index;
          });
          function value(row, name) {
            var index = headers[name];
            return index === undefined ? "" : String(row[index] || "");
          }

          var imported = 0;
          rows.slice(1).forEach(function(row) {
            var conceptId = value(row, "concept_id").trim();
            var section = value(row, "section").trim();
            if (!conceptId || !section) { return; }
            var noteId = value(row, "note_id").trim() || makeNoteId();
            var blockIndex = Number(value(row, "anchor_index"));
            if (!Number.isFinite(blockIndex) || blockIndex < 0) { blockIndex = 0; }
            var note = findUserNote(noteId);
            var payload = {
              id: noteId,
              conceptId: conceptId,
              section: section,
              anchor: {
                blockIndex: Math.floor(blockIndex),
                afterText: value(row, "anchor_after")
              },
              title: value(row, "title") || "Imported note",
              body: value(row, "body"),
              createdAt: value(row, "created_at") || new Date().toISOString(),
              updatedAt: value(row, "updated_at") || new Date().toISOString()
            };
            if (note) {
              Object.assign(note, payload);
            } else {
              userNotesState.notes.push(payload);
            }
            imported += 1;
          });
          saveUserNotes();
          return imported;
        }

        /* Concept details panel rendering and MathJax refresh. */
        function renderCaptionText(s) {
          var html = renderConceptText(s);
          [
            [/partial_mu A\^mu = 0/g, "\\(\\partial_\\mu A^\\mu = 0\\)"],
            [/A_mu \+ partial_mu Lambda/g, "\\(A_\\mu + \\partial_\\mu \\Lambda\\)"],
            [/p_mu - e A_mu/g, "\\(p_\\mu - e A_\\mu\\)"],
            [/delta S = 0/g, "\\(\\delta S = 0\\)"],
            [/u\^mu = dx\^mu\/dtau/g, "\\(u^\\mu = dx^\\mu/d\\tau\\)"],
            [/p\^mu = m u\^mu/g, "\\(p^\\mu = m u^\\mu\\)"],
            [/F_mu_nu/g, "\\(F_{\\mu\\nu}\\)"],
            [/phi\(x\)/g, "\\(\\phi(x)\\)"],
            [/A_mu\(x\)/g, "\\(A_\\mu(x)\\)"],
            [/A_mu/g, "\\(A_\\mu\\)"],
            [/A\^mu/g, "\\(A^\\mu\\)"],
            [/J\^mu/g, "\\(J^\\mu\\)"],
            [/dp\^mu\/dtau/g, "\\(dp^\\mu/d\\tau\\)"],
            [/p\^mu/g, "\\(p^\\mu\\)"],
            [/x\^mu/g, "\\(x^\\mu\\)"],
            [/u\^mu/g, "\\(u^\\mu\\)"],
            [/dx\^mu\/dtau/g, "\\(dx^\\mu/d\\tau\\)"],
            [/p_mu/g, "\\(p_\\mu\\)"],
            [/s\^2/g, "\\(s^2\\)"],
            [/d\^4x/g, "\\(d^4x\\)"],
            [/E=mc\^2/g, "\\(E=mc^2\\)"],
            [/T_EM/g, "\\(T_{EM}\\)"],
            [/T\^munu/g, "\\(T^{\\mu\\nu}\\)"]
          ].forEach(function(replacement) {
            html = html.replace(replacement[0], replacement[1]);
          });
          html = html.replace(/(^|[^\\A-Za-z])tau\b/g, "$1\\(\\tau\\)");
          return html;
        }

        function typesetInfoPanel(options) {
          options = options || {};
          var panel = document.getElementById("info_panel");
          schedulePanelContentRefit();
          if (window.MathJax && MathJax.typesetPromise) {
            if (MathJax.typesetClear) {
              MathJax.typesetClear([panel]);
            }
            MathJax.typesetPromise([panel]).catch(function(err) {
              console.warn("MathJax typesetting failed:", err);
            }).then(function() {
              applyInfoPanelSearchHighlight(options.searchQuery, options.scrollToSearchMatch);
              schedulePanelContentRefit();
            });
          } else if (options.searchQuery) {
            setTimeout(function() {
              applyInfoPanelSearchHighlight(options.searchQuery, options.scrollToSearchMatch);
              schedulePanelContentRefit();
            }, 250);
          }
        }

        function shouldSkipSearchHighlightNode(node) {
          var el = node.parentElement;
          if (!el) { return true; }
          return Boolean(el.closest(
            "mark, .study-questions, .concept-references, svg, mjx-container, script, style"
          ));
        }

        function applyInfoPanelSearchHighlight(query, scrollToMatch) {
          var normalizedQuery = searchDisplayText(query).toLowerCase();
          if (!normalizedQuery) { return; }

          var panel = document.getElementById("info_panel");
          var walker = document.createTreeWalker(panel, NodeFilter.SHOW_TEXT, {
            acceptNode: function(node) {
              if (shouldSkipSearchHighlightNode(node)) {
                return NodeFilter.FILTER_REJECT;
              }
              if (node.nodeValue.toLowerCase().indexOf(normalizedQuery) === -1) {
                return NodeFilter.FILTER_REJECT;
              }
              return NodeFilter.FILTER_ACCEPT;
            }
          });

          var matches = [];
          var node;
          while ((node = walker.nextNode())) {
            matches.push(node);
          }

          var firstMark = null;
          matches.forEach(function(textNode) {
            var value = textNode.nodeValue;
            var lower = value.toLowerCase();
            var fragment = document.createDocumentFragment();
            var cursor = 0;
            var index = lower.indexOf(normalizedQuery);

            while (index !== -1) {
              if (index > cursor) {
                fragment.appendChild(document.createTextNode(value.slice(cursor, index)));
              }

              var mark = document.createElement("mark");
              mark.className = "kg-search-mark kg-detail-search-mark";
              mark.textContent = value.slice(index, index + normalizedQuery.length);
              fragment.appendChild(mark);
              if (!firstMark) { firstMark = mark; }

              cursor = index + normalizedQuery.length;
              index = lower.indexOf(normalizedQuery, cursor);
            }

            if (cursor < value.length) {
              fragment.appendChild(document.createTextNode(value.slice(cursor)));
            }
            textNode.parentNode.replaceChild(fragment, textNode);
          });

          if (scrollToMatch && firstMark) {
            firstMark.scrollIntoView({block: "center", inline: "nearest"});
          }
        }

        function buildWorkspaceShell() {
          if (document.getElementById("kg_workspace")) { return; }
          var panel = document.getElementById("info_panel");
          var focusLens = document.getElementById("kg_focus_lens");
          var originalGraphParent = graphContainer.parentElement;
          var shell = document.createElement("main");
          var graphPane = document.createElement("section");
          var graphSurface = document.createElement("div");
          var splitter = document.createElement("div");
          var detailsPane = document.createElement("section");

          shell.id = "kg_workspace";
          shell.setAttribute("aria-label", "Knowledge graph and concept details");
          graphPane.id = "kg_graph_pane";
          graphPane.className = "kg-workspace-pane";
          graphPane.setAttribute("aria-label", "Graph view");
          graphSurface.id = "kg_graph_surface";
          splitter.id = "kg_pane_splitter";
          splitter.setAttribute("role", "separator");
          splitter.setAttribute("aria-label", "Resize graph and details panes");
          splitter.setAttribute("aria-orientation", "vertical");
          splitter.setAttribute("aria-valuemin", "28");
          splitter.setAttribute("aria-valuemax", "72");
          splitter.setAttribute("tabindex", "0");
          detailsPane.id = "kg_details_pane";
          detailsPane.className = "kg-workspace-pane";
          detailsPane.setAttribute("aria-label", "Details view");

          originalGraphParent.parentNode.insertBefore(shell, originalGraphParent);
          shell.appendChild(graphPane);
          shell.appendChild(splitter);
          shell.appendChild(detailsPane);
          graphPane.appendChild(graphSurface);
          graphSurface.appendChild(graphContainer);
          if (focusLens) {
            graphPane.appendChild(focusLens);
          }
          detailsPane.appendChild(panel);
          if (
            originalGraphParent &&
            originalGraphParent !== graphContainer &&
            originalGraphParent.parentNode &&
            originalGraphParent.children.length === 0
          ) {
            originalGraphParent.parentNode.removeChild(originalGraphParent);
          }
          setupWorkspaceSplitter(splitter);
          applyWorkspaceSplit();
        }

        function clampWorkspaceSplitPercent(value) {
          var numeric = Number(value);
          if (!Number.isFinite(numeric)) { return 50; }
          return Math.max(28, Math.min(72, numeric));
        }

        function applyWorkspaceSplit(value) {
          if (Number.isFinite(Number(value))) {
            workspaceSplitPercent = clampWorkspaceSplitPercent(value);
          } else if (!Number.isFinite(Number(workspaceSplitPercent))) {
            workspaceSplitPercent = 50;
          }
          var splitWidth = workspaceSplitPercent.toFixed(2) + "%";
          var shell = document.getElementById("kg_workspace");
          var splitter = document.getElementById("kg_pane_splitter");
          if (shell) {
            var rect = shell.getBoundingClientRect();
            var splitterWidth = splitter ? splitter.getBoundingClientRect().width : 0;
            var availableWidth = rect.width - splitterWidth;
            if (availableWidth > 0) {
              splitWidth = (availableWidth * workspaceSplitPercent / 100).toFixed(2) + "px";
            }
          }
          document.body.style.setProperty(
            "--kg-graph-pane-width",
            splitWidth
          );
          if (splitter) {
            splitter.setAttribute("aria-valuenow", String(Math.round(workspaceSplitPercent)));
          }
        }

        function setWorkspaceSplitFromClientX(clientX) {
          var shell = document.getElementById("kg_workspace");
          if (!shell) { return; }
          var rect = shell.getBoundingClientRect();
          if (!rect.width) { return; }
          applyWorkspaceSplit(((clientX - rect.left) / rect.width) * 100);
          scheduleViewportRefit();
        }

        function setupWorkspaceSplitter(splitter) {
          if (!splitter) { return; }
          splitter.addEventListener("pointerdown", function(e) {
            if (window.matchMedia("(max-width: 850px)").matches) { return; }
            e.preventDefault();
            workspaceSplitterPointerId = e.pointerId;
            splitter.setPointerCapture(e.pointerId);
            document.body.classList.add("kg-splitter-dragging");
            setWorkspaceSplitFromClientX(e.clientX);
          });
          splitter.addEventListener("pointermove", function(e) {
            if (workspaceSplitterPointerId !== e.pointerId) { return; }
            e.preventDefault();
            setWorkspaceSplitFromClientX(e.clientX);
          });
          function stopDragging(e) {
            if (workspaceSplitterPointerId !== e.pointerId) { return; }
            workspaceSplitterPointerId = null;
            document.body.classList.remove("kg-splitter-dragging");
            if (splitter.hasPointerCapture(e.pointerId)) {
              splitter.releasePointerCapture(e.pointerId);
            }
            scheduleViewportRefit();
          }
          splitter.addEventListener("pointerup", stopDragging);
          splitter.addEventListener("pointercancel", stopDragging);
          splitter.addEventListener("keydown", function(e) {
            if (e.altKey || e.metaKey || e.ctrlKey) { return; }
            if (e.key === "ArrowLeft") {
              e.preventDefault();
              applyWorkspaceSplit(workspaceSplitPercent - 4);
              scheduleViewportRefit();
            } else if (e.key === "ArrowRight") {
              e.preventDefault();
              applyWorkspaceSplit(workspaceSplitPercent + 4);
              scheduleViewportRefit();
            } else if (e.key === "Home") {
              e.preventDefault();
              applyWorkspaceSplit(28);
              scheduleViewportRefit();
            } else if (e.key === "End") {
              e.preventDefault();
              applyWorkspaceSplit(72);
              scheduleViewportRefit();
            }
          });
        }

        function detailsAreVisible() {
          var panel = document.getElementById("info_panel");
          return Boolean(panel && !panel.classList.contains("kg-hidden"));
        }

        function updateSelectedConceptHeader(nodeId) {
          var title = document.getElementById("kg_view_title");
          if (!title) { return; }
          if (nodeId && getConcept(nodeId)) {
            title.textContent = conceptDisplayId(nodeId) + " " + (getConcept(nodeId).label || "");
          } else {
            title.textContent = defaultViewTitle;
          }
        }

        function updateDetailsViewControls() {
          var select = document.getElementById("kg_details_view_select");
          if (!select) { return; }
          select.value = detailsAreVisible() ? readingMode : "hide";
        }

        function setDetailsView(value) {
          value = String(value || "full");
          if (value === "hide") {
            setInfoPanelVisible(false);
            refitCurrentViewForPanels(true);
            return;
          }

          readingMode = readingModeDefinitions[value] ? value : "full";
          setInfoPanelVisible(true);
          activeConceptSectionContext = "neighbourhood";
          activeConceptSectionLensLabel = "Neighbourhood";
          if (activeNodeId && getConcept(activeNodeId)) {
            showConcept(activeNodeId, {preserveSectionContext: true});
            applyCurrentView();
          }
          updateDetailsViewControls();
          document.getElementById("kg_status").innerText =
            "Details mode: " + currentReadingModeDefinition().label + ".";
          refitCurrentViewForPanels(true);
        }

        function setInfoPanelVisible(visible) {
          var panel = document.getElementById("info_panel");
          var button = document.getElementById("kg_info_toggle");
          if (!visible && graphViewIs(currentView, GraphViewMode.HIDE)) {
            visible = true;
            document.getElementById("kg_status").innerText =
              "Details remain visible while the graph is hidden.";
          }
          panel.classList.toggle("kg-hidden", !visible);
          document.body.classList.toggle("kg-details-hidden", !visible);
          if (button) {
            button.innerText = visible ? "Hide details" : "Show details";
          }
          updateDetailsViewControls();
          updateFocusLensDisplay();
          return visible;
        }

        function setControlsVisible(visible) {
          var panel = document.getElementById("kg_controls");
          var button = document.getElementById("kg_controls_toggle");
          panel.classList.toggle("kg-hidden", !visible);
          if (button) {
            button.innerText = visible ? "Hide tools" : "Tools";
          }
        }

        function currentInfoPanelFontSize() {
          var panel = document.getElementById("info_panel");
          var currentSize = parseFloat(window.getComputedStyle(panel).fontSize);
          if (!Number.isFinite(currentSize) || currentSize <= 0) {
            currentSize = kgInfoPanelConfig.fontSizePx;
          }
          return currentSize;
        }

        function currentControlsFontSize() {
          var panel = document.getElementById("kg_controls");
          var currentSize = parseFloat(window.getComputedStyle(panel).fontSize);
          if (!Number.isFinite(currentSize) || currentSize <= 0) {
            currentSize = 13;
          }
          return currentSize;
        }

        function currentGraphView() {
          if (!network || !network.getScale || !network.getViewPosition) {
            return null;
          }
          var position = network.getViewPosition();
          return {
            scale: network.getScale(),
            position: {
              x: position.x,
              y: position.y
            }
          };
        }

        function restoreGraphView(view) {
          if (!view || !network || !network.moveTo) { return; }
          network.moveTo({
            position: view.position,
            scale: view.scale,
            animation: false
          });
          updateNodeLabelPositions();
        }

        function preserveGraphView(view) {
          requestAnimationFrame(function() {
            restoreGraphView(view);
          });
          setTimeout(function() {
            restoreGraphView(view);
          }, 80);
        }

        function setInfoPanelFontSize(sizePx) {
          var graphView = currentGraphView();
          var panel = document.getElementById("info_panel");
          var nextSize = Math.max(
            kgInfoPanelConfig.textZoomMinPx,
            Math.min(kgInfoPanelConfig.textZoomMaxPx, Number(sizePx))
          );
          panel.style.fontSize = nextSize + "px";
          schedulePanelContentRefresh();
          preserveGraphView(graphView);
        }

        function adjustInfoPanelTextZoom(deltaY) {
          var direction = deltaY < 0 ? 1 : -1;
          setInfoPanelFontSize(currentInfoPanelFontSize() + direction);
        }

        function setControlsFontSize(sizePx) {
          var graphView = currentGraphView();
          var panel = document.getElementById("kg_controls");
          var nextSize = Math.max(
            kgInfoPanelConfig.textZoomMinPx,
            Math.min(kgInfoPanelConfig.textZoomMaxPx, Number(sizePx))
          );
          panel.style.fontSize = nextSize + "px";
          preserveGraphView(graphView);
        }

        function adjustControlsTextZoom(deltaY) {
          var direction = deltaY < 0 ? 1 : -1;
          setControlsFontSize(currentControlsFontSize() + direction);
        }

        function touchDistance(touches) {
          if (!touches || touches.length < 2) { return 0; }
          var dx = touches[0].clientX - touches[1].clientX;
          var dy = touches[0].clientY - touches[1].clientY;
          return Math.sqrt(dx * dx + dy * dy);
        }

        function beginInfoPanelPinch(e) {
          if (!e.touches || e.touches.length !== 2) { return; }
          infoPanelPinchState = {
            distance: touchDistance(e.touches),
            fontSize: currentInfoPanelFontSize()
          };
        }

        function updateInfoPanelPinch(e) {
          if (!e.touches || e.touches.length !== 2) {
            infoPanelPinchState = null;
            return;
          }
          e.preventDefault();
          e.stopPropagation();
          if (!infoPanelPinchState) {
            beginInfoPanelPinch(e);
            return;
          }

          var distance = touchDistance(e.touches);
          if (infoPanelPinchState.distance <= 0 || distance <= 0) { return; }
          var deltaPx = (distance - infoPanelPinchState.distance) / 18;
          setInfoPanelFontSize(infoPanelPinchState.fontSize + deltaPx);
        }

        function endInfoPanelPinch(e) {
          if (!e.touches || e.touches.length < 2) {
            infoPanelPinchState = null;
          }
        }

        function shouldStartWithControlsHidden() {
          var visualWidth = window.visualViewport ? window.visualViewport.width : window.innerWidth;
          return visualWidth <= 850 || window.matchMedia("(max-width: 850px)").matches;
        }

        function shouldStartWithConceptTocOpen() {
          var visualWidth = window.visualViewport ? window.visualViewport.width : window.innerWidth;
          return visualWidth > 850 && !window.matchMedia("(max-width: 850px)").matches;
        }

        function shouldStartWithFocusLensHidden() {
          var visualWidth = window.visualViewport ? window.visualViewport.width : window.innerWidth;
          return visualWidth <= 850 || window.matchMedia("(max-width: 850px)").matches;
        }

        function updateFocusLensVisibilityControls() {
          document.body.classList.toggle("kg-focus-lens-hidden", !focusLensVisible);
          var button = document.getElementById("kg_focus_lens_toggle");
          if (!button) { return; }
          button.setAttribute("aria-pressed", focusLensVisible ? "true" : "false");
          button.textContent = focusLensVisible ? "Hide lens" : "Show lens";
          button.title = focusLensVisible ? "Hide focus lens" : "Show focus lens";
        }

        function setFocusLensVisible(visible) {
          focusLensVisible = Boolean(visible);
          updateFocusLensVisibilityControls();
          updateFocusLensDisplay();
        }

        /* Graph view state and compact subgraph layout. */
        function updateGraphViewControls() {
          var select = document.getElementById("kg_graph_view_select");
          if (select) {
            select.value = graphViewSelectValue(currentView);
          }
          document.body.classList.toggle(
            "kg-graph-hidden",
            graphViewIs(currentView, GraphViewMode.HIDE)
          );
        }

        function setCurrentView(view) {
          currentView = view || createGraphView(GraphViewMode.ALL);
          updateGraphViewControls();
        }

        function getConcept(nodeId) {
          return conceptData[String(nodeId)] || null;
        }

        function conceptDisplayId(nodeId) {
          var concept = getConcept(nodeId) || {};
          return String(concept.display_id || nodeId);
        }

        function conceptTitleText(nodeId) {
          var concept = getConcept(nodeId) || {};
          return (conceptDisplayId(nodeId) + " " + String(concept.label || "")).trim();
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
            mode: mode || GraphViewMode.HIGHLIGHT
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

        function browserHistoryShortcutDirection(e) {
          if (!e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) { return 0; }
          if (e.key === "ArrowLeft") { return -1; }
          if (e.key === "ArrowRight") { return 1; }
          return 0;
        }

        function allowBrowserHistoryShortcut(e) {
          var direction = browserHistoryShortcutDirection(e);
          if (!direction || e.defaultPrevented) { return; }
          var beforeUrl = window.location.href;
          window.setTimeout(function() {
            if (window.location.href !== beforeUrl) { return; }
            if (direction < 0) {
              window.history.back();
            } else {
              window.history.forward();
            }
          }, 0);
        }

        function conceptIdParts(id) {
          return String(id).split(".").map(function(part) {
            var n = Number(part);
            return Number.isFinite(n) ? n : part;
          });
        }

        function compareConceptIds(a, b) {
          var aa = conceptIdParts(conceptDisplayId(a));
          var bb = conceptIdParts(conceptDisplayId(b));
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
            String(conceptDisplayId(nodeId)).split(".", 1)[0]
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

        /* Search and tooltip indexing. */
        function searchDisplayText(s) {
          return String(s || "")
            .replace(/\\cref\{([^{}]*)\}\{([^{}]*)\}/g, "$1")
            .replace(/\s+/g, " ")
            .trim();
        }

        function stripOptionalDetailsFromTooltipText(text) {
          var raw = String(text || "");
          var cursor = 0;
          var output = "";

          while (cursor < raw.length) {
            var block = findNextOptionalDetailBlock(raw, cursor);
            if (!block) {
              output += raw.slice(cursor);
              break;
            }
            output += raw.slice(cursor, block.start);
            cursor = block.end;
          }
          return output;
        }

        function renderTooltipText(s) {
          return escapeHtml(searchDisplayText(stripOptionalDetailsFromTooltipText(s)));
        }

        function optionalDetailTitlesFromText(text) {
          var titles = [];
          var cursor = 0;
          var raw = String(text || "");

          while (cursor < raw.length) {
            var block = findNextOptionalDetailBlock(raw, cursor);
            if (!block) { break; }

            var summaryStart = skipOptionalDetailWhitespace(
              raw,
              block.start + "\\optional_details".length
            );
            var summary = parseBracedArgument(raw, summaryStart);
            if (summary) {
              var title = summary.value;
              if (title) { titles.push(title); }
            }
            cursor = block.end;
          }
          return titles;
        }

        function conceptSections(concept) {
          if (concept && Array.isArray(concept.sections) && concept.sections.length > 0) {
            return concept.sections.map(function(section) {
              return {
                key: String(section.key || ""),
                title: String(section.title || ""),
                text: String(section.text || "")
              };
            });
          }
          return [];
        }

        function conceptSectionText(concept, key) {
          var section = conceptSections(concept).find(function(item) {
            return item.key === key;
          });
          return section ? section.text : "";
        }

        var legacyContentBlockKinds = {
          definition: true,
          derivation: true,
          explanation: true
        };

        /*
         * Viewer policy tables.
         *
         * Add new content block kinds in contentBlockKindPolicy, then add any
         * matching CSS and reading-mode membership below. Add new relation
         * display/semantic behaviour in edgeRelationPolicy; edge_key data still
         * supplies direction, colour, category, and explanatory text.
         */
        var contentBlockKindPolicy = Object.freeze({
          overview: {label: "Roadmap", mode: "inline"},
          definition: {label: "Definition", mode: "inline"},
          intuition: {label: "Think", mode: "inline"},
          explanation: {label: "Explanation", mode: "inline"},
          construction: {label: "Build", mode: "inline"},
          derivation: {label: "Derivation", mode: "inline"},
          derivation_step: {label: "Step", mode: "folded"},
          example: {label: "Example", mode: "inline"},
          worked_example: {label: "Worked", mode: "inline"},
          misconception: {label: "Common trap", mode: "folded", note: true},
          warning: {label: "Careful", mode: "folded", note: true},
          historical_note: {label: "Context", mode: "folded", note: true},
          summary: {label: "Takeaway", mode: "inline"}
        });

        var DetailSectionRole = Object.freeze({
          CONTENT: "content",
          DERIVED_FROM: "derived-from",
          WHERE_USED: "where-used",
          STUDY_QUESTIONS: "study-questions",
          REFERENCES: "references"
        });

        var detailSectionGraphPolicy = Object.freeze({
          content: {graphContext: "neighbourhood", lensLabel: "Neighbourhood"},
          "derived-from": {
            graphContext: "derived-from",
            relation: "DERIVES_FROM",
            focusDirection: "outgoing",
            lensLabel: "Derivation step",
            treeLensLabel: "Derivation tree"
          },
          "where-used": {
            graphContext: "where-used",
            relation: "DERIVES_FROM",
            focusDirection: "incoming",
            lensLabel: "Immediate usage",
            treeLensLabel: "Usage tree"
          },
          "study-questions": {graphContext: "neighbourhood", lensLabel: "Neighbourhood"},
          references: {graphContext: "neighbourhood", lensLabel: "Neighbourhood"}
        });

        var edgeRelationPolicy = Object.freeze({
          DERIVES_FROM: {
            abbreviation: "DF",
            sortOrder: 10,
            backlinkTitle: "Derived from this",
            derivationTree: true,
            tracePhrase: "derives from"
          },
          PREREQUISITE: {
            abbreviation: "PR",
            sortOrder: 20,
            backlinkTitle: "Requires this"
          },
          DEPENDS_ON: {
            abbreviation: "DO",
            sortOrder: 30,
            backlinkTitle: "Requires this"
          },
          RELATED: {
            abbreviation: "R",
            sortOrder: 40,
            backlinkTitle: "Related concepts"
          }
        });

        var readingModeDefinitions = Object.freeze({
          full: {
            label: "Full",
            blockKinds: null,
            questionTypes: null
          },
          core: {
            label: "Core",
            blockKinds: {
              overview: true,
              definition: true,
              intuition: true,
              explanation: true,
              construction: true,
              derivation: true,
              example: true,
              summary: true
            },
            questionTypes: {
              short_answer: true
            }
          },
          maths: {
            label: "Maths",
            blockKinds: {
              derivation: true,
              derivation_step: true,
              worked_example: true
            },
            questionTypes: {
              calculation: true
            }
          },
          context: {
            label: "Context",
            blockKinds: {
              misconception: true,
              warning: true,
              historical_note: true
            },
            questionTypes: {
              multiple_choice: true
            }
          },
          practice: {
            label: "Practice",
            blockKinds: {
              example: true,
              worked_example: true,
              derivation_step: true,
              summary: true
            },
            questionTypes: null
          }
        });

        function currentReadingModeDefinition() {
          return readingModeDefinitions[readingMode] || readingModeDefinitions.full;
        }

        function blockVisibleInReadingMode(block) {
          var allowed = currentReadingModeDefinition().blockKinds;
          return !allowed || allowed[block.kind] === true;
        }

        function questionVisibleInReadingMode(question) {
          var allowed = currentReadingModeDefinition().questionTypes;
          if (!allowed) { return true; }
          return allowed[String((question && question.question_type) || "")] === true;
        }

        function filteredStudyQuestions(studyQuestions) {
          return studyQuestions.filter(questionVisibleInReadingMode);
        }

        function filteredContentBlocks(concept) {
          return conceptContentBlocks(concept).filter(blockVisibleInReadingMode);
        }

        function contentBlockPolicyFor(kind) {
          return contentBlockKindPolicy[kind] || {
            label: contentBlockKindLabel(kind),
            mode: "inline"
          };
        }

        function detailSectionGraphPolicyFor(role) {
          return detailSectionGraphPolicy[role] || detailSectionGraphPolicy.content;
        }

        function edgeRelationPolicyFor(relation) {
          return edgeRelationPolicy[relation] || {};
        }

        function graphContextForSectionRole(role) {
          return detailSectionGraphPolicyFor(role).graphContext || "neighbourhood";
        }

        function relationForSectionRole(role) {
          return detailSectionGraphPolicyFor(role).relation || null;
        }

        function focusDirectionForSectionRole(role) {
          return detailSectionGraphPolicyFor(role).focusDirection || null;
        }

        function derivationRelation() {
          return relationForSectionRole(DetailSectionRole.DERIVED_FROM) || "DERIVES_FROM";
        }

        function relationHasDerivationTreeSemantics(relation) {
          return edgeRelationPolicyFor(relation).derivationTree === true;
        }

        function lensLabelForSectionRole(role) {
          var policy = detailSectionGraphPolicyFor(role);
          if (role === DetailSectionRole.DERIVED_FROM && derivedFromFullTreeEnabled) {
            return policy.treeLensLabel || policy.lensLabel;
          }
          if (role === DetailSectionRole.WHERE_USED && backlinksFullTreeEnabled) {
            return policy.treeLensLabel || policy.lensLabel;
          }
          return policy.lensLabel || "Neighbourhood";
        }

        function sectionRoleForGraphContext(context) {
          if (context === "derived-from") { return DetailSectionRole.DERIVED_FROM; }
          if (context === "where-used") { return DetailSectionRole.WHERE_USED; }
          return DetailSectionRole.CONTENT;
        }

        function tocGraphPolicyFields(role) {
          return {
            sectionRole: role,
            graphContext: graphContextForSectionRole(role),
            lensLabel: lensLabelForSectionRole(role)
          };
        }

        function conceptGraphicSvg(concept) {
          return concept.svg_detail || concept.svg_graphic || concept.svg_icon || "";
        }

        function contentBlockClassName(block, policy) {
          var className = "content-block content-block-" + block.kind;
          if (policy.mode === "folded") {
            className += " content-block-fold";
          }
          if (policy.note) {
            className += " content-block-note";
          }
          return className;
        }

        function conceptContentBlocks(concept) {
          if (!concept || !Array.isArray(concept.content_blocks)) { return []; }
          return concept.content_blocks
            .map(function(block) {
              return {
                block_id: String(block.block_id || ""),
                concept_id: String(block.concept_id || ""),
                sequence: Number(block.sequence || 0),
                kind: String(block.kind || ""),
                title: String(block.title || ""),
                body: String(block.body || "")
              };
            })
            .filter(function(block) {
              return block.block_id && block.kind && block.body;
            })
            .sort(function(a, b) {
              if (a.sequence !== b.sequence) { return a.sequence - b.sequence; }
              return a.block_id.localeCompare(b.block_id);
            });
        }

        function isLegacyContentBlock(block, seenKinds) {
          if (!legacyContentBlockKinds[block.kind]) { return false; }
          if (seenKinds[block.kind]) { return false; }
          seenKinds[block.kind] = true;
          return block.block_id === block.concept_id + "." + block.kind;
        }

        function shouldRenderContentBlocks(concept) {
          var blocks = conceptContentBlocks(concept);
          if (blocks.length === 0) { return false; }
          var seenKinds = {};
          return blocks.some(function(block) {
            return !isLegacyContentBlock(block, seenKinds);
          });
        }

        function contentBlockKindLabel(kind) {
          return String(kind || "")
            .replace(/_/g, " ")
            .replace(/\b\w/g, function(ch) { return ch.toUpperCase(); });
        }

        function contentBlockKindClass(kind) {
          return String(kind || "")
            .replace(/[^a-zA-Z0-9_-]/g, "-")
            .replace(/^-+|-+$/g, "") || "unknown";
        }

        function renderContentBlockHeading(block, title) {
          var policy = contentBlockPolicyFor(block.kind);
          return '<span class="content-block-title-line">' +
            '<span class="content-block-kind-mark" aria-hidden="true"></span>' +
            '<span class="content-block-title-text">' +
            renderConceptText(title) +
            "</span>" +
            '<span class="content-block-kind-label" aria-hidden="true" data-label="' +
            escapeHtml(policy.label) +
            '"></span>' +
            "</span>";
        }

        function renderContentBlock(conceptId, block) {
          var title = block.title || contentBlockKindLabel(block.kind);
          var policy = contentBlockPolicyFor(block.kind);
          var anchorId = contentAnchorId(conceptId, title);
          var bodyClass = "concept-body content-block-body";
          if (policy.mode === "folded") {
            bodyClass = "concept-body content-block-fold-body";
            if (policy.note) {
              bodyClass += " content-block-note-body";
            }
            return renderFoldDown({
              anchorId: anchorId,
              className: contentBlockClassName(block, policy),
              sectionRole: DetailSectionRole.CONTENT,
              summaryHtml: renderContentBlockHeading(block, title),
              bodyClass: bodyClass,
              bodyHtml: renderConceptText(block.body)
            });
          }
          var blocks = splitConceptBlocks(block.body);
          var bodyHtml = "";
          bodyHtml += renderNotesAtAnchor(conceptId, title, 0, "");
          blocks.forEach(function(textBlock, index) {
            bodyHtml += '<div class="concept-line">' +
              (textBlock.text ? renderConceptText(textBlock.text) : "&nbsp;") +
              "</div>";
            bodyHtml += renderNotesAtAnchor(
              conceptId,
              title,
              index + 1,
              textBlock.text.slice(0, 160)
            );
          });
          return renderFoldDown({
            anchorId: anchorId,
            className: contentBlockClassName(block, policy),
            sectionRole: DetailSectionRole.CONTENT,
            open: true,
            summaryHtml: renderContentBlockHeading(block, title),
            bodyClass: bodyClass,
            bodyHtml: bodyHtml
          });
        }

        function conceptTocItems(conceptId, concept, studyQuestions, conceptReferences) {
          var items = [];
          if (conceptGraphicSvg(concept)) {
            items.push(Object.assign({
              id: contentAnchorId(conceptId, "Graphic"),
              title: "Graphic"
            }, tocGraphPolicyFields(DetailSectionRole.CONTENT)));
          }
          if (shouldRenderContentBlocks(concept)) {
            filteredContentBlocks(concept).forEach(function(block) {
              var title = block.title || contentBlockKindLabel(block.kind);
              items.push(Object.assign({
                id: contentAnchorId(conceptId, title),
                title: title,
                kind: block.kind
              }, tocGraphPolicyFields(DetailSectionRole.CONTENT)));
            });
          } else {
            conceptSections(concept).forEach(function(section) {
              if (!section.text) { return; }
              items.push(Object.assign({
                id: contentAnchorId(conceptId, section.title),
                title: section.title
              }, tocGraphPolicyFields(DetailSectionRole.CONTENT)));
            });
          }

          if (derivedFromEdgesFor(conceptId).length > 0) {
            items.push(Object.assign({
              id: contentAnchorId(conceptId, "Derived From"),
              title: "Derived from"
            }, tocGraphPolicyFields(DetailSectionRole.DERIVED_FROM)));
          }
          if (backlinkGroupsFor(conceptId).length > 0) {
            items.push(Object.assign({
              id: contentAnchorId(conceptId, "Where This Is Used"),
              title: "Where this is used"
            }, tocGraphPolicyFields(DetailSectionRole.WHERE_USED)));
          }
          if (studyQuestions.length > 0) {
            items.push(Object.assign({
              id: contentAnchorId(conceptId, "Study Questions"),
              title: "Study Questions"
            }, tocGraphPolicyFields(DetailSectionRole.STUDY_QUESTIONS)));
          }
          if (conceptReferences.length > 0) {
            items.push(Object.assign({
              id: contentAnchorId(conceptId, "References"),
              title: "References"
            }, tocGraphPolicyFields(DetailSectionRole.REFERENCES)));
          }
          return items;
        }

        function renderConceptToc(items) {
          if (!Array.isArray(items) || items.length < 2) { return ""; }
          var openAttr = shouldStartWithConceptTocOpen() ? " open" : "";
          var html = '<details class="concept-toc" aria-label="Concept contents"' + openAttr + ">";
          html += '<summary class="concept-toc-title">Contents</summary>';
          html += '<div class="concept-toc-links">';
          items.forEach(function(item) {
            var kindClass = item.kind ? " concept-toc-link-" + contentBlockKindClass(item.kind) : "";
            var sectionRole = item.sectionRole || DetailSectionRole.CONTENT;
            html += '<a href="#' + escapeHtml(item.id) +
              '" class="concept-toc-link' + escapeHtml(kindClass) + '" data-toc-target="' +
              escapeHtml(item.id) + '" data-section-role="' +
              escapeHtml(sectionRole) + '" data-graph-context="' +
              escapeHtml(item.graphContext || "neighbourhood") + '" data-lens-label="' +
              escapeHtml(item.lensLabel || "Neighbourhood") + '">' +
              (item.kind ? '<span class="concept-toc-kind-dot" aria-hidden="true"></span>' : "") +
              renderConceptText(item.title) +
              "</a>";
          });
          html += "</div></details>";
          return html;
        }

        function renderConceptMasthead(nodeId, concept, tocItems) {
          var html = '<div class="concept-sticky-header">';
          html += '<div class="concept-title-row">';
          html += '<h2 class="concept-title">' +
            escapeHtml(conceptDisplayId(nodeId)) + " " + renderConceptText(concept.label) +
            "</h2>";
          html += "</div>";
          html += renderConceptToc(tocItems);
          html += "</div>";
          return html;
        }

        function renderConceptGraphic(conceptId, concept) {
          var svgDetail = conceptGraphicSvg(concept);
          if (!svgDetail) { return ""; }

          var graphicCaption = concept.svg_detail_caption || concept.svg_icon_caption || "";
          var bodyHtml = '<div class="concept-graphic">' + svgDetail + "</div>";
          if (graphicCaption) {
            bodyHtml += '<figcaption class="concept-graphic-caption">' +
              renderCaptionText(graphicCaption) +
              "</figcaption>";
          }
          return renderFoldDown({
            anchorId: contentAnchorId(conceptId, "Graphic"),
            className: "concept-figure",
            sectionRole: DetailSectionRole.CONTENT,
            open: true,
            title: "Graphic",
            bodyTag: "figure",
            bodyClass: "concept-figure-body",
            bodyHtml: bodyHtml
          });
        }

        function openTargetForToc(target) {
          if (!target) { return; }
          if (target.tagName === "DETAILS") {
            target.open = true;
            return;
          }
          var closedDetails = target.closest && target.closest("details:not([open])");
          if (closedDetails) {
            closedDetails.open = true;
          }
        }

        function scrollInfoPanelTargetBelowStickyToc(target) {
          var panel = document.getElementById("info_panel");
          if (!panel || !target) { return; }

          var panelRect = panel.getBoundingClientRect();
          var targetRect = target.getBoundingClientRect();
          var stickyHeader = panel.querySelector(".concept-sticky-header");
          var toc = panel.querySelector(".concept-toc");
          var stickyOffset = 0;
          if (stickyHeader) {
            stickyOffset = stickyHeader.getBoundingClientRect().bottom - panelRect.top + 8;
          } else if (toc) {
            stickyOffset = toc.getBoundingClientRect().bottom - panelRect.top + 8;
          }

          var targetTop = targetRect.top - panelRect.top + panel.scrollTop;
          panel.scrollTo({
            top: Math.max(0, targetTop - stickyOffset),
            behavior: "smooth"
          });
        }

        function updateConceptTocActive(targetId) {
          var panel = document.getElementById("info_panel");
          if (!panel) { return; }
          panel.querySelectorAll(".concept-toc-link.active").forEach(function(link) {
            link.classList.remove("active");
            link.removeAttribute("aria-current");
          });
          if (!targetId) { return; }
          var link = panel.querySelector(
            '.concept-toc-link[data-toc-target="' + cssAttributeValueEscape(targetId) + '"]'
          );
          if (!link) { return; }
          link.classList.add("active");
          link.setAttribute("aria-current", "true");
        }

        function lensLabelForContext(context) {
          return lensLabelForSectionRole(sectionRoleForGraphContext(context));
        }

        function setActiveConceptSection(targetId, context, options) {
          options = options || {};
          var nextTargetId = targetId ? String(targetId) : null;
          var nextContext = context || "neighbourhood";
          var nextLensLabel = options.lensLabel || lensLabelForContext(nextContext);
          var contextChanged = activeConceptSectionContext !== nextContext;
          var targetChanged = activeConceptSectionTargetId !== nextTargetId;
          var labelChanged = activeConceptSectionLensLabel !== nextLensLabel;
          activeConceptSectionTargetId = nextTargetId;
          activeConceptSectionContext = nextContext;
          activeConceptSectionLensLabel = nextLensLabel;
          if (targetChanged) {
            updateConceptTocActive(nextTargetId);
          }
          if (!options.skipGraphUpdate && (contextChanged || options.forceGraphUpdate)) {
            applyCurrentView();
          }
          if (targetChanged || contextChanged || labelChanged || options.forceGraphUpdate) {
            updateFocusLensDisplay();
          }
        }

        function firstTocItemForContext(context) {
          return currentConceptTocItems.find(function(item) {
            return (item.graphContext || "neighbourhood") === context;
          }) || null;
        }

        function initialTocItem(tocItems) {
          if (!Array.isArray(tocItems) || tocItems.length === 0) { return null; }
          if (activeConceptSectionTargetId) {
            var previous = tocItems.find(function(item) {
              return item.id === activeConceptSectionTargetId;
            });
            if (previous) { return previous; }
          }
          return firstTocItemForContext(activeConceptSectionContext) || tocItems[0];
        }

        function activeTocItemFromScroll() {
          var panel = document.getElementById("info_panel");
          if (!panel || currentConceptTocItems.length === 0) { return null; }
          var panelRect = panel.getBoundingClientRect();
          var stickyHeader = panel.querySelector(".concept-sticky-header");
          var stickyBottom = stickyHeader
            ? stickyHeader.getBoundingClientRect().bottom
            : panelRect.top;
          var cursorY = stickyBottom + 12;
          var best = null;
          var bestTop = -Infinity;
          var firstVisible = null;

          currentConceptTocItems.forEach(function(item) {
            var target = document.getElementById(item.id);
            if (!target) { return; }
            var rect = target.getBoundingClientRect();
            if (rect.bottom < panelRect.top || rect.top > panelRect.bottom) { return; }
            if (!firstVisible || rect.top < firstVisible.top) {
              firstVisible = {item: item, top: rect.top};
            }
            if (rect.top <= cursorY && rect.top >= bestTop) {
              best = item;
              bestTop = rect.top;
            }
          });

          return best || (firstVisible && firstVisible.item) || null;
        }

        function updateActiveSectionFromScroll() {
          var item = activeTocItemFromScroll();
          if (!item) { return; }
          setActiveConceptSection(item.id, item.graphContext || "neighbourhood", {
            lensLabel: item.lensLabel
          });
        }

        function scheduleDetailScrollSync() {
          if (Date.now() < detailScrollSyncSuppressedUntil) { return; }
          if (detailScrollSyncTimer !== null) {
            clearTimeout(detailScrollSyncTimer);
          }
          detailScrollSyncTimer = setTimeout(function() {
            detailScrollSyncTimer = null;
            if (Date.now() < detailScrollSyncSuppressedUntil) { return; }
            updateActiveSectionFromScroll();
          }, 80);
        }

        function renderConceptContent(conceptId, concept) {
          if (shouldRenderContentBlocks(concept)) {
            var blocks = filteredContentBlocks(concept);
            if (blocks.length === 0) {
              return '<p class="reading-mode-empty">No content blocks match this reading mode.</p>';
            }
            return blocks.map(function(block) {
              return renderContentBlock(conceptId, block);
            }).join("");
          }
          if (readingMode !== "full" && readingMode !== "core") {
            return '<p class="reading-mode-empty">Legacy content is available in Full and Core modes.</p>';
          }
          return conceptSections(concept).map(function(section) {
            return renderConceptSection(conceptId, section.title, section.text);
          }).join("");
        }

        function optionalDetailTitlesForConcept(concept) {
          return conceptSections(concept).reduce(function(titles, section) {
            return titles.concat(optionalDetailTitlesFromText(section.text));
          }, []);
        }

        function noteTitlesForConcept(nodeId) {
          return userNotesState.notes
            .filter(function(note) { return note.conceptId === String(nodeId); })
            .map(function(note) { return note.title || "Untitled note"; })
            .filter(Boolean);
        }

        function tooltipListHtml(title, values) {
          if (!values.length) { return ""; }
          return '<div class="kg-tooltip-section-title">' + escapeHtml(title) + "</div>" +
            "<ul>" + values.map(function(value) {
              return "<li>" + renderTooltipText(value) + "</li>";
            }).join("") + "</ul>";
        }

        function conceptTooltipHtml(nodeId) {
          var concept = getConcept(nodeId) || {};
          var title = conceptTitleText(nodeId);
          var definition = conceptSectionText(concept, "definition");
          var html = '<div class="kg-tooltip-title">' + renderTooltipText(title) + "</div>";
          if (definition) {
            html += '<div class="kg-tooltip-definition">' + renderTooltipText(definition) + "</div>";
          }
          html += tooltipListHtml("Optional details", optionalDetailTitlesForConcept(concept));
          html += tooltipListHtml("Notes", noteTitlesForConcept(nodeId));
          return html;
        }

        function conceptPreviewSourceText(concept) {
          var blocks = conceptContentBlocks(concept);
          var definitionBlock = blocks.find(function(block) {
            return block.kind === "definition";
          });
          if (definitionBlock) { return definitionBlock.body; }

          var overviewBlock = blocks.find(function(block) {
            return block.kind === "overview";
          });
          if (overviewBlock) { return overviewBlock.body; }
          if (blocks.length > 0) { return blocks[0].body; }

          var definition = conceptSectionText(concept, "definition");
          if (definition) { return definition; }
          var sections = conceptSections(concept);
          return sections.length > 0 ? sections[0].text : "";
        }

        function conceptPreviewExcerpt(text) {
          var excerpt = searchDisplayText(stripOptionalDetailsFromTooltipText(text));
          var maxLength = 280;
          if (excerpt.length <= maxLength) { return excerpt; }
          var cut = excerpt.slice(0, maxLength);
          var lastSpace = cut.lastIndexOf(" ");
          if (lastSpace > 160) {
            cut = cut.slice(0, lastSpace);
          }
          return cut.replace(/[.,;:]*$/, "") + "...";
        }

        function conceptPreviewHtml(nodeId) {
          var concept = getConcept(nodeId) || {};
          var layerParts = [];
          if (concept.layer) { layerParts.push("Layer " + escapeHtml(concept.layer)); }
          if (concept.layer_title) { layerParts.push(escapeHtml(concept.layer_title)); }

          var html = '<div class="concept-preview-header">';
          html += '<div class="concept-preview-title">' + renderTooltipText(conceptTitleText(nodeId)) + "</div>";
          html += '<button type="button" class="concept-preview-close" aria-label="Close preview">Close</button>';
          html += "</div>";
          if (layerParts.length > 0) {
            html += '<div class="concept-preview-layer">' + layerParts.join(" - ") + "</div>";
          }
          var excerpt = conceptPreviewExcerpt(conceptPreviewSourceText(concept));
          if (excerpt) {
            html += '<div class="concept-preview-excerpt">' + renderTooltipText(excerpt) + "</div>";
          }
          html += '<div class="concept-preview-actions">';
          html += '<button type="button" class="concept-preview-go" data-concept-id="' +
            escapeHtml(nodeId) + '">Go to concept</button>';
          html += "</div>";
          return html;
        }

        function typesetConceptPreview() {
          if (!conceptPreview || !window.MathJax || !MathJax.typesetPromise) { return; }
          if (MathJax.typesetClear) {
            MathJax.typesetClear([conceptPreview]);
          }
          MathJax.typesetPromise([conceptPreview]).catch(function(err) {
            console.warn("MathJax concept preview typesetting failed:", err);
          }).then(function() {
            if (conceptPreviewAnchor && conceptPreview.style.display !== "none") {
              positionConceptPreview(conceptPreviewAnchor);
            }
          });
        }

        function scheduleConceptPreviewTypeset() {
          if (conceptPreviewTypesetTimer) {
            clearTimeout(conceptPreviewTypesetTimer);
          }
          conceptPreviewTypesetTimer = setTimeout(function() {
            conceptPreviewTypesetTimer = null;
            typesetConceptPreview();
          }, 120);
        }

        function positionConceptPreview(anchor) {
          if (!conceptPreview || !anchor) { return; }
          var margin = 10;
          var gap = 8;
          var anchorRect = anchor.getBoundingClientRect();
          conceptPreview.style.display = "block";
          conceptPreview.style.left = "0px";
          conceptPreview.style.top = "0px";
          var previewRect = conceptPreview.getBoundingClientRect();

          var x = anchorRect.left;
          var y = anchorRect.bottom + gap;
          if (x + previewRect.width > window.innerWidth - margin) {
            x = window.innerWidth - previewRect.width - margin;
          }
          if (y + previewRect.height > window.innerHeight - margin) {
            y = anchorRect.top - previewRect.height - gap;
          }
          conceptPreview.style.left = Math.max(margin, x) + "px";
          conceptPreview.style.top = Math.max(margin, y) + "px";
        }

        function cancelConceptPreviewHide() {
          if (conceptPreviewHideTimer) {
            clearTimeout(conceptPreviewHideTimer);
            conceptPreviewHideTimer = null;
          }
        }

        function hideConceptPreview(force) {
          if (!conceptPreview || (!force && conceptPreviewPinned)) { return; }
          cancelConceptPreviewHide();
          if (conceptPreviewTypesetTimer) {
            clearTimeout(conceptPreviewTypesetTimer);
            conceptPreviewTypesetTimer = null;
          }
          conceptPreviewPinned = false;
          conceptPreviewAnchor = null;
          conceptPreview.classList.remove("concept-preview-pinned");
          clearTransientConceptHighlight();
          conceptPreview.style.display = "none";
          conceptPreview.innerHTML = "";
        }

        function scheduleConceptPreviewHide() {
          if (conceptPreviewPinned) { return; }
          cancelConceptPreviewHide();
          conceptPreviewHideTimer = setTimeout(function() {
            hideConceptPreview(false);
          }, 180);
        }

        function showConceptPreview(link, options) {
          options = options || {};
          if (!link) { return; }
          var id = link.getAttribute("data-concept-id");
          if (!getConcept(id)) { return; }

          cancelConceptPreviewHide();
          conceptPreviewPinned = Boolean(options.pinned);
          conceptPreviewAnchor = link;
          conceptPreview.innerHTML = conceptPreviewHtml(id);
          conceptPreview.classList.toggle("concept-preview-pinned", conceptPreviewPinned);
          positionConceptPreview(link);
          applyTransientConceptHighlight(id);
          scheduleConceptPreviewTypeset();
        }

        function conceptPreviewTriggerFromEventTarget(target) {
          return target.closest(".concept-link, .edge-detail-concept");
        }

        function refreshNodeTooltips() {
          if (!nodes || !originalNodes) { return; }
          var updates = [];
          Object.keys(conceptData).forEach(function(id) {
            if (originalNodes[id]) {
              originalNodes[id].title = "";
            }
            if (nodes.get(id)) {
              updates.push({id: id, title: ""});
            }
          });
          if (updates.length) {
            nodes.update(updates);
          }
        }

        function searchFieldsForConcept(nodeId) {
          var concept = getConcept(nodeId) || {};
          var fields = [
            {name: "Display ID", value: conceptDisplayId(nodeId)},
            {name: "Concept ID", value: String(nodeId)},
            {name: "Title", value: concept.label || ""}
          ].concat(conceptSections(concept).map(function(section) {
            return {name: section.title || section.key || "Section", value: section.text};
          }));
          return fields.map(function(field) {
            return {
              name: field.name,
              value: searchDisplayText(field.value)
            };
          });
        }

        function fieldContainsQuery(field, query) {
          return field.value.toLowerCase().indexOf(query) !== -1;
        }

        function matchingSearchFields(nodeId, query) {
          return searchFieldsForConcept(nodeId).filter(function(field) {
            return fieldContainsQuery(field, query);
          });
        }

        function matchingSearchIds(query) {
          var ids = Object.keys(conceptData).sort(compareConceptIds);
          if (!query) { return ids; }
          return ids.filter(function(id) {
            return matchingSearchFields(id, query).length > 0;
          });
        }

        function highlightedSearchText(text, query) {
          var value = String(text || "");
          if (!query) { return escapeHtml(value); }

          var lower = value.toLowerCase();
          var html = "";
          var cursor = 0;
          var index = lower.indexOf(query);
          while (index !== -1) {
            html += escapeHtml(value.slice(cursor, index));
            html += '<mark class="kg-search-mark">' +
              escapeHtml(value.slice(index, index + query.length)) +
              "</mark>";
            cursor = index + query.length;
            index = lower.indexOf(query, cursor);
          }
          html += escapeHtml(value.slice(cursor));
          return html;
        }

        function searchSnippet(field, query) {
          var value = field.value;
          var lower = value.toLowerCase();
          var index = lower.indexOf(query);
          if (index === -1) { return ""; }

          var context = 55;
          var start = Math.max(0, index - context);
          var end = Math.min(value.length, index + query.length + context);
          if (start > 0) {
            var previousSpace = value.indexOf(" ", start);
            if (previousSpace !== -1 && previousSpace < index) {
              start = previousSpace + 1;
            }
          }
          if (end < value.length) {
            var nextSpace = value.lastIndexOf(" ", end);
            if (nextSpace > index + query.length) {
              end = nextSpace;
            }
          }

          var snippet = value.slice(start, end);
          return (start > 0 ? "... " : "") +
            highlightedSearchText(snippet, query) +
            (end < value.length ? " ..." : "");
        }

        /* Relation-aware visibility. */
        function edgeRelation(edge) {
          return String(edge.relation || "");
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
          if (!edge || edge.hidden) {
            return false;
          }
          if (graphViewIs(currentView, GraphViewMode.HIGHLIGHT) && graphViewHasNode(currentView)) {
            return edge.from == currentView.nodeId || edge.to == currentView.nodeId;
          }
          if (graphViewIs(currentView, GraphViewMode.DESCENDANTS)) {
            return edgeRelationDirected(edge);
          }
          if (graphViewIs(currentView, GraphViewMode.DERIVATION_TRACE)) {
            return relationHasDerivationTreeSemantics(edgeRelation(edge));
          }
          return true;
        }

        function visibleGraphNode(nodeId) {
          var node = nodes.get(String(nodeId));
          return Boolean(node && !node.hidden);
        }

        function visibleGraphEdge(edge) {
          return Boolean(
            edge &&
            !edge.hidden &&
            visibleGraphNode(edge.from) &&
            visibleGraphNode(edge.to)
          );
        }

        function visibleDirectEdgeIds(sourceId, targetId) {
          sourceId = String(sourceId);
          targetId = String(targetId);
          return edges.get().filter(function(edge) {
            if (!visibleGraphEdge(edge)) { return false; }
            return (
              String(edge.from) === sourceId && String(edge.to) === targetId
            ) || (
              String(edge.from) === targetId && String(edge.to) === sourceId
            );
          }).map(function(edge) {
            return edge.id;
          });
        }

        function visiblePathEdgeIds(sourceId, targetId) {
          sourceId = String(sourceId);
          targetId = String(targetId);
          if (
            !sourceId ||
            !targetId ||
            sourceId === targetId ||
            !visibleGraphNode(sourceId) ||
            !visibleGraphNode(targetId)
          ) {
            return [];
          }

          var direct = visibleDirectEdgeIds(sourceId, targetId);
          if (direct.length > 0) {
            return direct;
          }

          var adjacency = {};
          edges.get().forEach(function(edge) {
            if (!visibleGraphEdge(edge)) { return; }
            var from = String(edge.from);
            var to = String(edge.to);
            if (!adjacency[from]) { adjacency[from] = []; }
            if (!adjacency[to]) { adjacency[to] = []; }
            adjacency[from].push({nodeId: to, edgeId: edge.id});
            adjacency[to].push({nodeId: from, edgeId: edge.id});
          });

          var seen = {};
          var previous = {};
          var queue = [sourceId];
          seen[sourceId] = true;

          while (queue.length > 0) {
            var current = queue.shift();
            if (current === targetId) { break; }

            (adjacency[current] || []).forEach(function(item) {
              if (seen[item.nodeId]) { return; }
              seen[item.nodeId] = true;
              previous[item.nodeId] = {nodeId: current, edgeId: item.edgeId};
              queue.push(item.nodeId);
            });
          }

          if (!seen[targetId]) { return []; }

          var edgeIds = [];
          var cursor = targetId;
          while (cursor !== sourceId && previous[cursor]) {
            edgeIds.unshift(previous[cursor].edgeId);
            cursor = previous[cursor].nodeId;
          }
          return edgeIds;
        }

        function clearTransientConceptHighlight(options) {
          options = options || {};
          var hadHighlight = Boolean(transientConceptHighlight) ||
            Object.keys(transientEdgeSnapshots).length > 0;
          if (!hadHighlight) { return; }

          if (!options.skipEdgeRestore) {
            Object.keys(transientEdgeSnapshots).forEach(function(edgeId) {
              if (edges.get(edgeId)) {
                edges.update(Object.assign({}, transientEdgeSnapshots[edgeId]));
              }
            });
          }
          transientConceptHighlight = null;
          transientEdgeSnapshots = {};
          updateNodeLabelPositions();
          if (network && network.redraw) {
            network.redraw();
          }
        }

        function applyTransientConceptHighlight(nodeId) {
          clearTransientConceptHighlight();
          nodeId = String(nodeId);
          if (!visibleGraphNode(nodeId)) {
            return;
          }

          var edgeIds = activeNodeId && visibleGraphNode(activeNodeId)
            ? visiblePathEdgeIds(activeNodeId, nodeId)
            : [];
          transientConceptHighlight = {
            nodeId: nodeId,
            edgeIds: edgeIds
          };

          edgeIds.forEach(function(edgeId) {
            var edge = edges.get(edgeId);
            if (!edge) { return; }
            if (!Object.prototype.hasOwnProperty.call(transientEdgeSnapshots, edgeId)) {
              transientEdgeSnapshots[edgeId] = Object.assign({}, edge);
            }
            var currentWidth = Number(edge.width);
            if (!Number.isFinite(currentWidth) || currentWidth <= 0) {
              currentWidth = 1;
            }
            edges.update(Object.assign({}, edge, {
              width: Math.max(currentWidth, edgeHoverWidth),
              color: Object.assign({}, edge.color || {}, {
                color: "#174ea6",
                highlight: "#174ea6",
                hover: "#174ea6",
                opacity: 1.0
              })
            }));
          });

          updateNodeLabelPositions();
          if (network && network.redraw) {
            network.redraw();
          }
        }

        function enabledConnectedNodes(nodeId) {
          var connected = {};
          allEdges.forEach(function(edge) {
            if (edge.from == nodeId) { connected[edge.to] = true; }
            if (edge.to == nodeId) { connected[edge.from] = true; }
          });
          return Object.keys(connected);
        }

        function emptySectionGraphContext(nodeId, label) {
          var keep = {};
          keep[String(nodeId)] = true;
          return {
            label: label,
            keep: keep,
            edgeKeep: {},
            showEdgesWithinKeep: false
          };
        }

        function sectionGraphContext(nodeId) {
          nodeId = String(nodeId);

          if (activeConceptSectionContext === "derived-from") {
            var sourceContext = emptySectionGraphContext(nodeId, "derived-from ancestry");
            derivedFromEdgesFor(nodeId, derivedFromFullTreeEnabled).forEach(function(item) {
              sourceContext.keep[String(item.nodeId)] = true;
              sourceContext.edgeKeep[item.edge.id] = true;
            });
            return sourceContext;
          }

          if (activeConceptSectionContext === "where-used") {
            var usedContext = emptySectionGraphContext(nodeId, "derived-from descendants");
            derivedFromThisEntriesFor(nodeId, backlinksFullTreeEnabled).forEach(function(item) {
              usedContext.keep[String(item.nodeId)] = true;
              usedContext.edgeKeep[item.edge.id] = true;
            });
            return usedContext;
          }

          var keep = {};
          keep[nodeId] = true;
          enabledConnectedNodes(nodeId).forEach(function(connectedId) {
            keep[String(connectedId)] = true;
          });
          return {
            label: "immediate neighbours",
            keep: keep,
            edgeKeep: {},
            showEdgesWithinKeep: true
          };
        }

        function sectionContextEdgeHighlighted(edge, context) {
          if (!context || !edge) { return false; }
          if (context.edgeKeep[edge.id]) { return true; }
          return Boolean(
            context.showEdgesWithinKeep &&
            context.keep[String(edge.from)] &&
            context.keep[String(edge.to)]
          );
        }

        function enabledDirectedDescendants(nodeId) {
          var keep = {};
          var queue = [String(nodeId)];
          keep[String(nodeId)] = true;

          while (queue.length > 0) {
            var current = queue.shift();
            allEdges.forEach(function(edge) {
              if (!edgeRelationDirected(edge)) { return; }
              if (String(edge.from) !== current) { return; }

              var target = String(edge.to);
              if (keep[target]) { return; }
              keep[target] = true;
              queue.push(target);
            });
          }

          return keep;
        }

        function derivationTrace(nodeId) {
          var keep = {};
          var traceEdges = {};
          var orderedEdges = [];
          var queue = [String(nodeId)];
          keep[String(nodeId)] = true;

          while (queue.length > 0) {
            var current = queue.shift();
            allEdges
              .filter(function(edge) {
                return String(edge.from) === current &&
                  edgeRelation(edge) === derivationRelation();
              })
              .sort(function(a, b) {
                return compareConceptIds(String(a.to), String(b.to));
              })
              .forEach(function(edge) {
                var target = String(edge.to);
                traceEdges[edge.id] = true;
                orderedEdges.push(edge);
                if (keep[target]) { return; }
                keep[target] = true;
                queue.push(target);
              });
          }

          return {
            nodes: keep,
            edges: traceEdges,
            orderedEdges: orderedEdges
          };
        }

        function relationColour(relation) {
          var item = edgeKey[relation] || {};
          return item.colour || "#999999";
        }

        function relationAbbreviation(relation) {
          relation = String(relation || "");
          var policy = edgeRelationPolicyFor(relation);
          if (policy.abbreviation) { return policy.abbreviation; }

          var parts = relation.split(/[^A-Za-z0-9]+/).filter(Boolean);
          if (parts.length === 0) { return "?"; }
          if (parts.length === 1) {
            return parts[0].slice(0, 2).toUpperCase();
          }
          return parts.slice(0, 2).map(function(part) {
            return part.charAt(0).toUpperCase();
          }).join("");
        }

        function relationSortOrder(relation) {
          var order = Number(edgeRelationPolicyFor(relation).sortOrder);
          return Number.isFinite(order) ? order : 1000;
        }

        function compareRelations(a, b) {
          return relationSortOrder(a) - relationSortOrder(b) || a.localeCompare(b);
        }

        function orderedRelations() {
          return Object.keys(edgeKey).sort(compareRelations);
        }

        function focusLensBackgroundState() {
          if (graphViewIs(currentView, GraphViewMode.HIDE)) { return "graph-hidden"; }
          if (graphViewIs(currentView, GraphViewMode.FOCUSED)) { return "hidden"; }
          return "visible";
        }

        function focusLensBackgroundLabel() {
          var background = focusLensBackgroundState();
          if (background === "graph-hidden") { return "graph hidden"; }
          if (background === "hidden") { return "background hidden"; }
          return "background visible";
        }

        function focusLensContextLabel() {
          return activeConceptSectionLensLabel ||
            lensLabelForContext(activeConceptSectionContext || "neighbourhood");
        }

        function relationIsDirected(relation) {
          return edgeKey[relation] && edgeKey[relation].directed === true;
        }

        function focusLensRelationState(relation, direction) {
          relation = String(relation || "");
          direction = direction || (relationIsDirected(relation) ? "incoming" : "undirected");
          if (activeConceptSectionContext === "derived-from") {
            var derivedFromRelation = relationForSectionRole(DetailSectionRole.DERIVED_FROM);
            var derivedFromDirection = focusDirectionForSectionRole(DetailSectionRole.DERIVED_FROM);
            return {
              state: relation === derivedFromRelation && direction === derivedFromDirection
                ? (derivedFromFullTreeEnabled ? "tree" : "immediate")
                : "none",
              direction: direction
            };
          }
          if (activeConceptSectionContext === "where-used") {
            var whereUsedRelation = relationForSectionRole(DetailSectionRole.WHERE_USED);
            var whereUsedDirection = focusDirectionForSectionRole(DetailSectionRole.WHERE_USED);
            return {
              state: relation === whereUsedRelation && direction === whereUsedDirection
                ? (backlinksFullTreeEnabled ? "tree" : "immediate")
                : "none",
              direction: direction
            };
          }
          return {
            state: "immediate",
            direction: direction
          };
        }

        function focusLensStateLabel(state) {
          if (state === "tree") { return "tree"; }
          if (state === "immediate") { return "1-hop"; }
          return "off";
        }

        function focusLensRelationTitle(relation, lens) {
          var state = lens.state === "tree" ? "tree" :
            lens.state === "immediate" ? "immediate" : "not in focus";
          var direction = lens.direction === "incoming" ? ", incoming" :
            lens.direction === "outgoing" ? ", outgoing" :
            lens.direction === "undirected" ? ", undirected" : "";
          return relation + ": " + state + direction;
        }

        function focusLensRelationHtml(relation, direction) {
          var relationLens = focusLensRelationState(relation, direction);
          return '<div class="kg-focus-lens-relation kg-focus-lens-dir-' +
            escapeHtml(relationLens.direction) + '" data-relation="' +
            escapeHtml(relation) + '" data-state="' +
            escapeHtml(relationLens.state) + '" data-direction="' +
            escapeHtml(relationLens.direction) + '" style="--edge-color:' +
            escapeHtml(relationColour(relation)) + '" title="' +
            escapeHtml(focusLensRelationTitle(relation, relationLens)) + '">' +
            '<span class="kg-focus-lens-abbrev">' +
            escapeHtml(relationAbbreviation(relation)) + '</span>' +
            '<span class="kg-focus-lens-node"></span>' +
            '<span class="kg-focus-lens-edge"></span>' +
            '<span class="kg-focus-lens-state">' +
            escapeHtml(focusLensStateLabel(relationLens.state)) + '</span>' +
            '</div>';
        }

        function focusLensConceptLabel(nodeId) {
          var concept = getConcept(nodeId) || {};
          return concept.label || conceptDisplayId(nodeId);
        }

        function abbreviatedConceptName(nodeId) {
          var label = String(focusLensConceptLabel(nodeId) || "").trim();
          if (!label) { return ""; }
          if (label.length <= 15) { return label; }

          var words = label.split(/[\s/_-]+/).filter(Boolean);
          if (words.length === 0) { return label.slice(0, 14) + "."; }
          if (words.length === 1) { return words[0].slice(0, 14) + "."; }

          var first = words[0];
          var second = words[1];
          var abbreviated = first + " " + second.slice(0, Math.min(5, second.length)) + ".";
          if (abbreviated.length <= 16) { return abbreviated; }
          return words.slice(0, 2).map(function(word) {
            return word.charAt(0).toUpperCase();
          }).join("");
        }

        function updateFocusLensDisplay() {
          var lensEl = document.getElementById("kg_focus_lens");
          if (!lensEl) { return; }

          var selectedId = activeNodeId && getConcept(activeNodeId) ? String(activeNodeId) : "";
          var background = focusLensBackgroundState();
          var lensLabel = focusLensContextLabel();
          lensEl.setAttribute("data-selected-concept", selectedId);
          lensEl.setAttribute("data-lens-context", activeConceptSectionContext || "neighbourhood");
          lensEl.setAttribute("data-lens-label", lensLabel);
          lensEl.setAttribute("data-background", background);

          var html = '<div class="kg-focus-lens-head">' +
            '<span class="kg-focus-lens-title">Focus lens</span>' +
            '<span class="kg-focus-lens-background">' + escapeHtml(focusLensBackgroundLabel()) + '</span>' +
            '</div>';
          html += '<div class="kg-focus-lens-purpose">' + escapeHtml(lensLabel) + '</div>';

          if (!selectedId) {
            lensEl.setAttribute("aria-label", "Focus lens: no concept selected");
            lensEl.innerHTML = html + '<div class="kg-focus-lens-empty">No concept selected</div>';
            return;
          }

          var relations = orderedRelations();
          var directedRelations = relations.filter(relationIsDirected);
          var undirectedRelations = relations.filter(function(relation) {
            return !relationIsDirected(relation);
          });

          html += '<div class="kg-focus-lens-map">';
          html += '<div class="kg-focus-lens-directed kg-focus-lens-incoming" aria-label="Incoming relation states">';
          directedRelations.forEach(function(relation) {
            html += focusLensRelationHtml(relation, "incoming");
          });
          html += '</div>';
          html += '<div class="kg-focus-lens-middle">';
          html += '<div class="kg-focus-lens-center" title="' +
            escapeHtml(focusLensConceptLabel(selectedId)) + '">' +
            '<span class="kg-focus-lens-center-id">' + escapeHtml(conceptDisplayId(selectedId)) + '</span>' +
            '<span class="kg-focus-lens-center-name">' +
            escapeHtml(abbreviatedConceptName(selectedId)) + '</span></div>';
          html += '<div class="kg-focus-lens-undirected" aria-label="Undirected relation states">';
          undirectedRelations.forEach(function(relation) {
            html += focusLensRelationHtml(relation, "undirected");
          });
          html += '</div></div>';
          html += '<div class="kg-focus-lens-directed kg-focus-lens-outgoing" aria-label="Outgoing relation states">';
          directedRelations.forEach(function(relation) {
            html += focusLensRelationHtml(relation, "outgoing");
          });
          html += '</div></div>';
          lensEl.setAttribute(
            "aria-label",
            "Focus lens: " + conceptDisplayId(selectedId) + ", " +
              focusLensContextLabel() + ", " + focusLensBackgroundLabel()
          );
          lensEl.innerHTML = html;
        }

        function applyCurrentView() {
          if (graphViewIs(currentView, GraphViewMode.HIDE)) {
            kgHideGraph(true);
            return;
          }
          if (graphViewIs(currentView, GraphViewMode.HIGHLIGHT) && graphViewHasNode(currentView)) {
            kgHighlight(currentView.nodeId, true);
            return;
          }
          if (graphViewIs(currentView, GraphViewMode.FOCUSED) && graphViewHasNode(currentView)) {
            applySectionGraphView(currentView.nodeId, {compact: true, preserveStatus: true});
            return;
          }
          if (graphViewIs(currentView, GraphViewMode.NEIGHBOURHOOD) && graphViewHasNode(currentView)) {
            kgApplyNeighbourhood(currentView.nodeId, true, graphViewRadius(currentView));
            return;
          }
          if (graphViewIs(currentView, GraphViewMode.DESCENDANTS) && graphViewHasNode(currentView)) {
            kgApplyDescendants(currentView.nodeId, true);
            return;
          }
          if (graphViewIs(currentView, GraphViewMode.DERIVATION_TRACE) && graphViewHasNode(currentView)) {
            kgApplyDerivationTrace(currentView.nodeId, true);
            return;
          }
          kgReset(true);
        }

        function activateConceptSectionContext(context) {
          var item = firstTocItemForContext(context || "neighbourhood");
          setActiveConceptSection(item ? item.id : null, context || "neighbourhood", {
            lensLabel: item ? item.lensLabel : lensLabelForContext(context || "neighbourhood"),
            forceGraphUpdate: true
          });
        }

        function detailSectionRoleForDetailsSection(section) {
          if (!section) { return null; }
          var sectionRole = section.getAttribute("data-section-role");
          if (sectionRole && detailSectionGraphPolicy[sectionRole]) {
            return sectionRole;
          }
          if (section.classList.contains("concept-derived-from")) {
            return DetailSectionRole.DERIVED_FROM;
          }
          if (section.classList.contains("concept-backlinks")) {
            return DetailSectionRole.WHERE_USED;
          }
          return null;
        }

        function graphContextForDetailsSection(section) {
          var sectionRole = detailSectionRoleForDetailsSection(section);
          return sectionRole ? graphContextForSectionRole(sectionRole) : null;
        }

        function markPendingGraphSectionContext(target) {
          var summary = target && target.closest ? target.closest("summary") : null;
          pendingGraphSectionContext = summary
            ? graphContextForDetailsSection(summary.parentElement)
            : null;
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

        function relationshipConceptHtml(nodeId) {
          var concept = getConcept(nodeId);
          var label = concept ? concept.label || "" : "";
          return '<button type="button" class="edge-detail-concept" data-edge-concept-id="' +
            escapeHtml(nodeId) + '" data-concept-id="' +
            escapeHtml(nodeId) +
            '" aria-haspopup="dialog" aria-controls="kg_concept_preview">' +
            escapeHtml(conceptDisplayId(nodeId)) +
            (label ? " " + renderConceptText(label) : "") +
            "</button>";
        }

        function renderDerivationTracePanel(nodeId) {
          var trace = derivationTrace(nodeId);
          var html = '<section class="derivation-trace-panel">';
          html += "<h3>Derivation trace</h3>";

          if (trace.orderedEdges.length === 0) {
            html += '<p class="reading-mode-empty">No ' +
              escapeHtml(derivationRelation()) +
              " links are recorded for this concept.</p>";
            html += "</section>";
            return html;
          }

          html += '<ol class="derivation-trace-list">';
          trace.orderedEdges.forEach(function(edge) {
            html += "<li>";
            html += relationshipConceptHtml(edge.from) +
              ' <span class="derivation-trace-relation">' +
              escapeHtml(edgeRelationPolicyFor(edgeRelation(edge)).tracePhrase || "relates to") +
              "</span> " +
              relationshipConceptHtml(edge.to);
            if (edge.note) {
              html += '<div class="derivation-trace-note">' + renderConceptText(edge.note) + "</div>";
            }
            html += "</li>";
          });
          html += "</ol></section>";
          return html;
        }

        function backlinkGroupTitle(relation) {
          var policy = edgeRelationPolicyFor(relation);
          if (policy.backlinkTitle) { return policy.backlinkTitle; }
          return relation || "Related concepts";
        }

        function derivedFromEdgesFor(nodeId, fullTree) {
          nodeId = String(nodeId);
          var sourceRelation = relationForSectionRole(DetailSectionRole.DERIVED_FROM);
          var entries = [];
          var queue = [{nodeId: nodeId, depth: 0}];
          var visitedNodes = {};
          var seenEdges = {};
          visitedNodes[nodeId] = true;

          while (queue.length > 0) {
            var current = queue.shift();
            allEdges
              .filter(function(edge) {
                return String(edge.from) === current.nodeId &&
                  edgeRelation(edge) === sourceRelation &&
                  getConcept(edge.to);
              })
              .sort(function(a, b) {
                return compareConceptIds(String(a.to), String(b.to));
              })
              .forEach(function(edge) {
                var target = String(edge.to);
                if (!seenEdges[edge.id]) {
                  entries.push({
                    edge: edge,
                    nodeId: target,
                    depth: current.depth + 1
                  });
                  seenEdges[edge.id] = true;
                }
                if (!fullTree || visitedNodes[target]) { return; }
                visitedNodes[target] = true;
                queue.push({nodeId: target, depth: current.depth + 1});
              });
          }

          return entries;
        }

        function derivedFromThisEntriesFor(nodeId, fullTree) {
          nodeId = String(nodeId);
          var usageRelation = relationForSectionRole(DetailSectionRole.WHERE_USED);
          var entries = [];
          var queue = [{nodeId: nodeId, depth: 0}];
          var visitedNodes = {};
          var seenEdges = {};
          visitedNodes[nodeId] = true;

          while (queue.length > 0) {
            var current = queue.shift();
            allEdges
              .filter(function(edge) {
                return String(edge.to) === current.nodeId &&
                  edgeRelation(edge) === usageRelation &&
                  getConcept(edge.from);
              })
              .sort(function(a, b) {
                return compareConceptIds(String(a.from), String(b.from));
              })
              .forEach(function(edge) {
                var source = String(edge.from);
                if (!seenEdges[edge.id]) {
                  entries.push({
                    edge: edge,
                    nodeId: source,
                    depth: current.depth + 1
                  });
                  seenEdges[edge.id] = true;
                }
                if (!fullTree || visitedNodes[source]) { return; }
                visitedNodes[source] = true;
                queue.push({nodeId: source, depth: current.depth + 1});
              });
          }

          return entries;
        }

        function treeIndentStyle(item) {
          var depth = Math.max(0, Number((item && item.depth) || 1) - 1);
          return ' style="--tree-depth:' + String(depth) + '"';
        }

        function fullTreeToggleHtml(className, checked) {
          return '<label class="concept-full-tree-toggle">' +
            '<input type="checkbox" class="' + escapeHtml(className) + '"' +
            (checked ? " checked" : "") + "> Full tree</label>";
        }

        function derivedFromTreeItemHtml(item, noteClassName) {
          var html = "<li" + treeIndentStyle(item) + ">";
          html += relationshipConceptHtml(item.nodeId);
          if (item.edge.note) {
            html += '<div class="' + escapeHtml(noteClassName) + '">' +
              renderConceptText(item.edge.note) + "</div>";
          }
          html += "</li>";
          return html;
        }

        function sortedBacklinkItems(items) {
          return items.sort(function(a, b) {
            var depthDiff = (Number(a.depth) || 1) - (Number(b.depth) || 1);
            if (depthDiff !== 0) { return depthDiff; }
            return compareConceptIds(a.nodeId, b.nodeId);
          });
        }

        function immediateBacklinkEntry(edge, nodeId) {
          return {
            nodeId: String(nodeId),
            edge: edge,
            depth: 1
          };
        }

        function backLinkRelationGroupsObject(nodeId) {
          nodeId = String(nodeId);
          var groups = {};
          var usageRelation = relationForSectionRole(DetailSectionRole.WHERE_USED);
          var derivedEntries = derivedFromThisEntriesFor(nodeId, backlinksFullTreeEnabled);
          if (derivedEntries.length > 0) {
            groups[usageRelation] = derivedEntries;
          }

          allEdges.forEach(function(edge) {
            var relation = edgeRelation(edge);
            var relatedNodeId = null;
            if (relation === usageRelation) { return; }
            if (edgeRelationDirected(edge)) {
              if (String(edge.to) !== nodeId) { return; }
              relatedNodeId = String(edge.from);
            } else {
              if (String(edge.from) === nodeId) {
                relatedNodeId = String(edge.to);
              } else if (String(edge.to) === nodeId) {
                relatedNodeId = String(edge.from);
              } else {
                return;
              }
            }
            if (!getConcept(relatedNodeId)) { return; }

            if (!groups[relation]) { groups[relation] = []; }
            groups[relation].push(immediateBacklinkEntry(edge, relatedNodeId));
          });

          return groups;
        }

        function renderConceptDerivedFrom(nodeId) {
          var sourceEdges = derivedFromEdgesFor(nodeId, derivedFromFullTreeEnabled);
          if (sourceEdges.length === 0) { return ""; }

          var html = '<details id="' + escapeHtml(contentAnchorId(nodeId, "Derived From")) +
            '" class="concept-derived-from" data-section-role="' +
            escapeHtml(DetailSectionRole.DERIVED_FROM) + '" data-graph-context="' +
            escapeHtml(graphContextForSectionRole(DetailSectionRole.DERIVED_FROM)) +
            '" data-lens-label="' +
            escapeHtml(lensLabelForSectionRole(DetailSectionRole.DERIVED_FROM)) + '" open>';
          html += "<summary>Derived from</summary>";
          html += fullTreeToggleHtml(
            "concept-derived-from-full-tree",
            derivedFromFullTreeEnabled
          );
          html += '<ul class="concept-derived-from-list">';
          sourceEdges.forEach(function(item) {
            html += derivedFromTreeItemHtml(item, "concept-derived-from-note");
          });
          html += "</ul></details>";
          return html;
        }

        function backlinkGroupsFor(nodeId) {
          nodeId = String(nodeId);
          var groups = backLinkRelationGroupsObject(nodeId);

          return Object.keys(groups)
            .sort(compareRelations)
            .map(function(relation) {
              return {
                relation: relation,
                title: backlinkGroupTitle(relation),
                items: sortedBacklinkItems(groups[relation])
              };
            });
        }

        function renderConceptBacklinks(nodeId) {
          var groups = backlinkGroupsFor(nodeId);
          if (groups.length === 0) { return ""; }

          var html = '<details id="' + escapeHtml(contentAnchorId(nodeId, "Where This Is Used")) +
            '" class="concept-backlinks" data-section-role="' +
            escapeHtml(DetailSectionRole.WHERE_USED) + '" data-graph-context="' +
            escapeHtml(graphContextForSectionRole(DetailSectionRole.WHERE_USED)) +
            '" data-lens-label="' +
            escapeHtml(lensLabelForSectionRole(DetailSectionRole.WHERE_USED)) + '" open>';
          html += "<summary>Where this is used</summary>";
          html += fullTreeToggleHtml(
            "concept-backlinks-full-tree",
            backlinksFullTreeEnabled
          );
          groups.forEach(function(group) {
            html += '<section class="concept-backlink-group">';
            html += '<div class="concept-backlink-group-title">' + escapeHtml(group.title) + "</div>";
            html += '<ul class="concept-backlink-list">';
            group.items.forEach(function(item) {
              html += derivedFromTreeItemHtml(item, "concept-backlink-note");
            });
            html += "</ul></section>";
          });
          html += "</details>";
          return html;
        }

        function showEdgeDetails(edgeId) {
          var edge = edges.get(edgeId);
          if (!edge || !visibleGraphEdge(edge)) { return; }

          hideConceptPreview(true);
          restoreHoveredEdge();
          setInfoPanelVisible(true);

          var relation = edgeRelation(edge);
          var relationInfo = edgeKey[relation] || {};
          var relationColourValue = relationColour(relation);
          var html = "";
          html += "<h2>Relationship</h2>";
          html += '<section class="edge-detail">';
          html += '<div class="edge-detail-route">' +
            relationshipConceptHtml(edge.from) +
            '<span class="edge-detail-arrow">' + (relationInfo.directed ? "->" : "-") + "</span>" +
            relationshipConceptHtml(edge.to) +
            "</div>";
          html += '<dl class="edge-detail-meta">';
          html += "<dt>Relation</dt><dd>" +
            '<span class="edge-colour-swatch" style="background:' +
            escapeHtml(relationColourValue) + '"></span>' +
            escapeHtml(relation || "Unlabelled") + "</dd>";
          if (relationInfo.category) {
            html += "<dt>Category</dt><dd>" + escapeHtml(relationInfo.category) + "</dd>";
          }
          if (relationInfo.meaning) {
            html += "<dt>Meaning</dt><dd>" + escapeHtml(relationInfo.meaning) + "</dd>";
          }
          if (edge.note) {
            html += "<dt>Note</dt><dd>" + renderConceptText(edge.note) + "</dd>";
          }
          html += "</dl>";
          html += "</section>";

          var panel = document.getElementById("info_panel");
          panel.innerHTML = html;
          panel.classList.toggle("kg-note-editing", noteEditingEnabled);
          typesetInfoPanel();
        }

        function showConcept(nodeId, options) {
          options = options || {};
          hideConceptPreview(true);
          if (!options.preserveSectionContext) {
            activeConceptSectionContext = "neighbourhood";
            activeConceptSectionLensLabel = "Neighbourhood";
          }
          var concept = getConcept(nodeId);
          if (!concept) {
            currentConceptTocItems = [];
            setActiveConceptSection(null, "neighbourhood", {
              lensLabel: "Neighbourhood",
              skipGraphUpdate: true
            });
            var missingPanel = document.getElementById("info_panel");
            missingPanel.innerHTML =
              "<h2>" + escapeHtml(conceptDisplayId(nodeId)) + "</h2>" +
              "<p>No concept data was found for this node.</p>";
            missingPanel.setAttribute("data-concept-id", String(nodeId));
            missingPanel.scrollTop = 0;
            typesetInfoPanel(options);
            return;
          }

          var layerParts = [];
          if (concept.layer) { layerParts.push("Layer " + escapeHtml(concept.layer)); }
          if (concept.layer_title) { layerParts.push(escapeHtml(concept.layer_title)); }

          var studyQuestions = Array.isArray(concept.study_questions) ? concept.study_questions : [];
          studyQuestions = filteredStudyQuestions(studyQuestions);
          var conceptReferences = Array.isArray(concept.references) ? concept.references : [];
          var tocItems = conceptTocItems(
            nodeId,
            concept,
            studyQuestions,
            conceptReferences
          );
          currentConceptTocItems = tocItems.slice();

          var html = "";
          html += renderConceptMasthead(nodeId, concept, tocItems);
          if (layerParts.length > 0) {
            html += '<p class="concept-layer-context">' + layerParts.join(" - ") + "</p>";
          }
          html += renderConceptGraphic(nodeId, concept);
          html += "<hr>";
          if (graphViewIs(currentView, GraphViewMode.DERIVATION_TRACE)) {
            html += renderDerivationTracePanel(nodeId);
          }
          html += renderConceptContent(nodeId, concept);
          html += renderConceptDerivedFrom(nodeId);
          html += renderConceptBacklinks(nodeId);
          if (studyQuestions.length > 0) {
            html += '<details id="' + escapeHtml(contentAnchorId(nodeId, "Study Questions")) +
              '" class="study-questions" data-section-role="' +
              escapeHtml(DetailSectionRole.STUDY_QUESTIONS) + '" data-graph-context="' +
              escapeHtml(graphContextForSectionRole(DetailSectionRole.STUDY_QUESTIONS)) +
              '" data-lens-label="' +
              escapeHtml(lensLabelForSectionRole(DetailSectionRole.STUDY_QUESTIONS)) + '"' +
              (readingMode === "practice" ? " open" : "") + ">";
            html += "<summary>Study Questions</summary>";
            studyQuestions.forEach(function(item, index) {
              var question = item && (item.prompt || item.question) ? (item.prompt || item.question) : "";
              var answer = item && item.answer ? item.answer : "";
              if (!question) { return; }
              html += '<section class="study-question">';
              html += '<div class="study-question-title">Question ' + (index + 1) + "</div>";
              html += renderStudyText(question, "concept-body study-question-prompt");
              if (answer) {
                html += '<details class="study-answer">';
                html += "<summary>Answer</summary>";
                html += renderStudyText(answer, "concept-body study-answer-body");
                html += "</details>";
              }
              html += "</section>";
            });
            html += "</details>";
          }
          if (conceptReferences.length > 0) {
            html += '<details id="' + escapeHtml(contentAnchorId(nodeId, "References")) +
              '" class="concept-references" data-section-role="' +
              escapeHtml(DetailSectionRole.REFERENCES) + '" data-graph-context="' +
              escapeHtml(graphContextForSectionRole(DetailSectionRole.REFERENCES)) +
              '" data-lens-label="' +
              escapeHtml(lensLabelForSectionRole(DetailSectionRole.REFERENCES)) + '">';
            html += "<summary>References</summary>";
            html += '<ul class="concept-reference-list">';
            conceptReferences.forEach(function(item) {
              if (!item || !item.citation) { return; }
              var locator = item.locator ? ", " + escapeHtml(item.locator) : "";
              var note = item.note ? '<div class="concept-reference-note">' + renderConceptText(item.note) + "</div>" : "";
              html += '<li class="concept-reference">';
              if (item.url) {
                html += '<a href="' + escapeHtml(item.url) + '" target="_blank" rel="noopener noreferrer">' + renderConceptText(item.citation) + "</a>";
              } else {
                html += renderConceptText(item.citation);
              }
              html += locator + note + "</li>";
            });
            html += "</ul>";
            html += "</details>";
          }
          var panel = document.getElementById("info_panel");
          var previousPanelConceptId = panel.getAttribute("data-concept-id") || "";
          var conceptChanged = previousPanelConceptId !== String(nodeId);
          panel.innerHTML = html;
          panel.setAttribute("data-concept-id", String(nodeId));
          if (conceptChanged && !options.scrollToSearchMatch) {
            panel.scrollTop = 0;
          }
          detailScrollSyncSuppressedUntil = Date.now() + 350;
          panel.classList.toggle("kg-note-editing", noteEditingEnabled);
          openUserNoteId = null;
          var initialItem = initialTocItem(tocItems);
          if (initialItem) {
            setActiveConceptSection(initialItem.id, initialItem.graphContext || "neighbourhood", {
              lensLabel: initialItem.lensLabel,
              skipGraphUpdate: true
            });
          } else {
            setActiveConceptSection(null, "neighbourhood", {
              lensLabel: "Neighbourhood",
              skipGraphUpdate: true
            });
          }
          if (conceptChanged && !options.scrollToSearchMatch) {
            panel.scrollTop = 0;
          }
          typesetInfoPanel(options);
        }

        window.kgShowEdgeKey = function() {
          setInfoPanelVisible(true);
          var relations = Object.keys(edgeKey).sort();
          var html = "<h2>Edge Key</h2>";

          if (relations.length === 0) {
            html += "<p>No edge key data was loaded.</p>";
            document.getElementById("info_panel").innerHTML = html;
            schedulePanelContentRefit();
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
          schedulePanelContentRefit();
        };

        /* Public UI commands. */
        window.kgToggleInfoPanel = function() {
          var panel = document.getElementById("info_panel");
          setInfoPanelVisible(panel.classList.contains("kg-hidden"));
          refitCurrentViewForPanels(true);
        };

        window.kgToggleControls = function() {
          var panel = document.getElementById("kg_controls");
          setControlsVisible(panel.classList.contains("kg-hidden"));
          refitCurrentViewForPanels(true);
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

        function visualViewportRect() {
          if (window.visualViewport) {
            return {
              left: window.visualViewport.offsetLeft,
              top: window.visualViewport.offsetTop,
              right: window.visualViewport.offsetLeft + window.visualViewport.width,
              bottom: window.visualViewport.offsetTop + window.visualViewport.height,
              width: window.visualViewport.width,
              height: window.visualViewport.height
            };
          }
          return {
            left: 0,
            top: 0,
            right: window.innerWidth,
            bottom: window.innerHeight,
            width: window.innerWidth,
            height: window.innerHeight
          };
        }

        function intersectRects(a, b) {
          var left = Math.max(a.left, b.left);
          var top = Math.max(a.top, b.top);
          var right = Math.min(a.right, b.right);
          var bottom = Math.min(a.bottom, b.bottom);
          if (right <= left || bottom <= top) { return null; }
          return {
            left: left,
            top: top,
            right: right,
            bottom: bottom,
            width: right - left,
            height: bottom - top
          };
        }

        /* Viewport fitting around visible panels. */
        function visiblePanelRects() {
          return ["kg_controls", "info_panel"].map(function(id) {
            var el = document.getElementById(id);
            if (!el || el.classList.contains("kg-hidden")) { return null; }
            return {
              id: id,
              rect: el.getBoundingClientRect()
            };
          }).filter(Boolean);
        }

        function panelOcclusionEdge(panel, baseRect, overlap) {
          if (panel.id === "info_panel" && overlap.width >= baseRect.width * 0.60) {
            return ((overlap.top + overlap.bottom) / 2) >= ((baseRect.top + baseRect.bottom) / 2)
              ? "bottom"
              : "top";
          }
          if (panel.id === "info_panel" && overlap.height >= baseRect.height * 0.45) {
            return ((overlap.left + overlap.right) / 2) >= ((baseRect.left + baseRect.right) / 2)
              ? "right"
              : "left";
          }
          if (panel.id === "kg_controls" && overlap.height >= baseRect.height * 0.35) {
            return ((overlap.left + overlap.right) / 2) >= ((baseRect.left + baseRect.right) / 2)
              ? "right"
              : "left";
          }

          var distances = {
            left: Math.abs(overlap.left - baseRect.left),
            right: Math.abs(baseRect.right - overlap.right),
            top: Math.abs(overlap.top - baseRect.top),
            bottom: Math.abs(baseRect.bottom - overlap.bottom)
          };
          return Object.keys(distances).sort(function(a, b) {
            return distances[a] - distances[b];
          })[0];
        }

        function availableGraphRect() {
          var containerRect = graphContainer.getBoundingClientRect();
          var viewport = visualViewportRect();
          var baseAbs = intersectRects(containerRect, viewport) || containerRect;
          var margin = 28;
          var availableAbs = {
            left: baseAbs.left + margin,
            top: baseAbs.top + margin,
            right: baseAbs.right - margin,
            bottom: baseAbs.bottom - margin
          };
          var availableWidth = availableAbs.right - availableAbs.left;
          var availableHeight = availableAbs.bottom - availableAbs.top;

          var minWidth = Math.min(220, baseAbs.width * 0.65);
          var minHeight = Math.min(180, baseAbs.height * 0.65);
          if (availableWidth < minWidth || availableHeight < minHeight) {
            availableAbs = {
              left: baseAbs.left + margin,
              top: baseAbs.top + margin,
              right: baseAbs.right - margin,
              bottom: baseAbs.bottom - margin
            };
          }

          var left = availableAbs.left - containerRect.left;
          var top = availableAbs.top - containerRect.top;
          var width = Math.max(1, availableAbs.right - availableAbs.left);
          var height = Math.max(1, availableAbs.bottom - availableAbs.top);

          return {
            left: left,
            top: top,
            width: width,
            height: height,
            centerX: left + (width / 2),
            centerY: top + (height / 2)
          };
        }

        function nodeCanvasBounds(nodeIds) {
          var positions = network.getPositions(nodeIds);
          var minX = Infinity;
          var maxX = -Infinity;
          var minY = Infinity;
          var maxY = -Infinity;

          nodeIds.forEach(function(id) {
            var pos = positions[id];
            var node = nodes.get(id);
            if (!pos || !node || node.hidden) { return; }

            var baseRadius = Number(node.visualSize) || Number(node.size) || 18;
            var radius = id === activeNodeId ? baseRadius * activeNodeRadiusScale : baseRadius;
            var halfLabelWidth = nodeLabelWidth / 2;
            var labelHeight = nodeLabelFontSize * 3.2;
            var horizontalExtent = Math.max(radius, halfLabelWidth) + 18;
            var topExtent = radius + 18;
            var bottomExtent = radius + labelHeight + 28;

            minX = Math.min(minX, pos.x - horizontalExtent);
            maxX = Math.max(maxX, pos.x + horizontalExtent);
            minY = Math.min(minY, pos.y - topExtent);
            maxY = Math.max(maxY, pos.y + bottomExtent);
          });

          if (!Number.isFinite(minX)) {
            return null;
          }

          return {
            left: minX,
            top: minY,
            right: maxX,
            bottom: maxY,
            width: Math.max(1, maxX - minX),
            height: Math.max(1, maxY - minY),
            x: (minX + maxX) / 2,
            y: (minY + maxY) / 2
          };
        }

        function fitNodesToAvailableRect(nodeIds, options) {
          options = options || {};
          var fitIds = nodeIds.map(String).filter(function(id, index, ids) {
            var node = nodes.get(id);
            return node && !node.hidden && ids.indexOf(id) === index;
          });
          if (fitIds.length === 0) { return; }

          var bounds = nodeCanvasBounds(fitIds);
          if (!bounds) { return; }

          var available = availableGraphRect();
          var maxScale = options.maxScale === undefined ? 0.7 : Number(options.maxScale);
          var minScale = options.minScale === undefined ? 0.08 : Number(options.minScale);
          if (!Number.isFinite(maxScale) || maxScale <= 0) { maxScale = 0.7; }
          if (!Number.isFinite(minScale) || minScale <= 0) { minScale = 0.08; }

          var scale = Math.min(
            available.width / bounds.width,
            available.height / bounds.height,
            maxScale
          );
          scale = Math.max(minScale, scale);

          var containerCenter = {
            x: graphContainer.clientWidth / 2,
            y: graphContainer.clientHeight / 2
          };
          var targetPosition = {
            x: bounds.x - ((available.centerX - containerCenter.x) / scale),
            y: bounds.y - ((available.centerY - containerCenter.y) / scale)
          };

          network.moveTo({
            position: targetPosition,
            scale: scale,
            animation: options.animation === false ? false : {
              duration: options.duration || 250,
              easingFunction: "easeInOutQuad"
            }
          });
          setTimeout(updateNodeLabelPositions, options.animation === false ? 0 : 260);
        }

        function fitHighlightedSelection(nodeId, options) {
          options = options || {};
          var fitIds = [String(nodeId)];
          enabledConnectedNodes(nodeId).forEach(function(id) {
            if (originalNodes[id] && fitIds.indexOf(id) === -1) {
              fitIds.push(id);
            }
          });

          fitNodesToAvailableRect(fitIds, {
            maxScale: 0.7,
            animation: options.animation
          });
        }

        function visibleNodeIds() {
          return nodes.get().filter(function(node) {
            return !node.hidden;
          }).map(function(node) {
            return String(node.id);
          });
        }

        function refitCurrentViewForPanels() {
          if (graphViewIs(currentView, GraphViewMode.HIGHLIGHT) && activeNodeId !== null) {
            fitHighlightedSelection(activeNodeId);
          } else if (
            (
              graphViewIs(currentView, GraphViewMode.NEIGHBOURHOOD) ||
              graphViewIs(currentView, GraphViewMode.FOCUSED) ||
              graphViewIs(currentView, GraphViewMode.DESCENDANTS) ||
              graphViewIs(currentView, GraphViewMode.DERIVATION_TRACE)
            ) &&
            graphViewHasNode(currentView)
          ) {
            fitNodesToAvailableRect(visibleNodeIds(), {maxScale: 0.85});
          } else {
            updateNodeLabelPositions();
          }
        }

        var viewportRefitTimer = null;
        var viewportRefitSettledTimer = null;
        function scheduleViewportRefit() {
          updateNodeLabelPositions();
          if (viewportRefitTimer !== null) {
            clearTimeout(viewportRefitTimer);
          }
          if (viewportRefitSettledTimer !== null) {
            clearTimeout(viewportRefitSettledTimer);
          }
          viewportRefitTimer = setTimeout(function() {
            viewportRefitTimer = null;
            refitCurrentViewForPanels();
          }, 120);
          viewportRefitSettledTimer = setTimeout(function() {
            viewportRefitSettledTimer = null;
            refitCurrentViewForPanels();
          }, 420);
        }

        function handleViewportResize() {
          applyWorkspaceSplit();
          scheduleViewportRefit();
        }

        var panelContentRefitTimer = null;
        var panelContentRefitSettledTimer = null;
        function schedulePanelContentRefresh() {
          requestAnimationFrame(function() {
            updateNodeLabelPositions();
          });
        }

        function schedulePanelContentRefit() {
          if (panelContentRefitTimer !== null) {
            clearTimeout(panelContentRefitTimer);
          }
          if (panelContentRefitSettledTimer !== null) {
            clearTimeout(panelContentRefitSettledTimer);
          }
          requestAnimationFrame(function() {
            updateNodeLabelPositions();
          });
          panelContentRefitTimer = setTimeout(function() {
            panelContentRefitTimer = null;
            refitCurrentViewForPanels();
          }, 180);
          panelContentRefitSettledTimer = setTimeout(function() {
            panelContentRefitSettledTimer = null;
            refitCurrentViewForPanels();
          }, 520);
        }

        function focusConcept(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          if (graphViewIs(currentView, GraphViewMode.HIDE)) {
            focusHiddenConcept(nodeId, statusPrefix, options);
            return;
          }
          if (activeNodeId !== String(nodeId)) {
            activeConceptSectionContext = "neighbourhood";
            activeConceptSectionTargetId = null;
            activeConceptSectionLensLabel = "Neighbourhood";
          }
          if (graphViewIs(currentView, GraphViewMode.FOCUSED)) {
            activeNodeId = nodeId;
            applySectionGraphView(nodeId, {compact: true, preserveStatus: true});
            showConcept(nodeId, {
              searchQuery: options.searchQuery,
              scrollToSearchMatch: options.scrollToSearchMatch
            });
            setActiveConceptItem(nodeId);
            if (!options.skipHistory) {
              pushConceptHistory(nodeId, graphViewHistoryMode(currentView));
            }
            if (statusPrefix) {
              document.getElementById("kg_status").innerText =
                statusPrefix + " " + conceptDisplayId(nodeId) + ".";
            }
            return;
          }
          activeNodeId = nodeId;
          kgHighlight(nodeId, true);
          showConcept(nodeId, {
            searchQuery: options.searchQuery,
            scrollToSearchMatch: options.scrollToSearchMatch
          });
          setActiveConceptItem(nodeId);
          if (!options.skipHistory) {
            pushConceptHistory(nodeId, graphViewHistoryMode(currentView));
          }
          if (statusPrefix) {
            document.getElementById("kg_status").innerText =
              statusPrefix + " " + conceptDisplayId(nodeId) + ".";
          }
        }

        function focusConceptInGraph(nodeId) {
          if (!getConcept(nodeId)) { return; }
          applySectionGraphView(nodeId, {compact: false, preserveStatus: true});
          showConcept(nodeId);
          setActiveConceptItem(nodeId);
          pushConceptHistory(nodeId, graphViewHistoryMode(currentView));
          document.getElementById("kg_status").innerText =
            "Focused " + conceptDisplayId(nodeId) + " in graph.";
        }

        function focusNeighbourhood(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          var radius = clampNeighbourhoodRadius(options.radius || graphViewRadius(currentView));
          kgApplyNeighbourhood(nodeId, true, radius);
          showConcept(nodeId);
          setActiveConceptItem(nodeId);
          if (!options.skipHistory) {
            pushConceptHistory(nodeId, graphViewHistoryMode(currentView));
          }

          var neighbourCount = Math.max(0, Object.keys(enabledNeighbourhoodNodes(nodeId, radius)).length - 1);
          var displayId = conceptDisplayId(nodeId);
          document.getElementById("kg_status").innerText =
            (statusPrefix ? statusPrefix + " " + displayId + ". " : "") +
            "Neighbourhood (" + radius + ") mode: " + displayId + " plus " + neighbourCount +
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
            pushConceptHistory(nodeId, graphViewHistoryMode(currentView));
          }

          var descendantCount = Math.max(0, Object.keys(enabledDirectedDescendants(nodeId)).length - 1);
          var displayId = conceptDisplayId(nodeId);
          document.getElementById("kg_status").innerText =
            (statusPrefix ? statusPrefix + " " + displayId + ". " : "") +
            "Descendants mode: " + displayId + " plus " + descendantCount +
            " reachable node" + (descendantCount === 1 ? "" : "s") +
            ". Click a visible node to walk one step.";
        }

        function focusDerivationTrace(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          kgApplyDerivationTrace(nodeId, true);
          showConcept(nodeId);
          setActiveConceptItem(nodeId);
          if (!options.skipHistory) {
            pushConceptHistory(nodeId, graphViewHistoryMode(currentView));
          }

          var trace = derivationTrace(nodeId);
          var traceNodeCount = Math.max(0, Object.keys(trace.nodes).length - 1);
          var displayId = conceptDisplayId(nodeId);
          document.getElementById("kg_status").innerText =
            (statusPrefix ? statusPrefix + " " + displayId + ". " : "") +
            "Derivation trace: " + displayId + " plus " + traceNodeCount +
            " derived-from node" + (traceNodeCount === 1 ? "" : "s") +
            ". Click a visible node to trace from it.";
        }

        function buildConceptList(filterText) {
          var q = searchDisplayText(filterText).toLowerCase();
          var ids = matchingSearchIds(q);
          var html = "";
          var count = 0;

          ids.forEach(function(id) {
            var concept = getConcept(id);
            var label = searchDisplayText(concept.label || "");
            var displayId = conceptDisplayId(id);
            var titleHtml = '<span class="kg-search-hit-title">' +
              '<span class="kg-concept-id">' + highlightedSearchText(displayId, q) + "</span> " +
              highlightedSearchText(label, q) +
              "</span>";
            var snippetHtml = "";

            if (q) {
              var snippets = matchingSearchFields(id, q).filter(function(field) {
                return field.name !== "Display ID" &&
                  field.name !== "Concept ID" &&
                  field.name !== "Title";
              }).slice(0, 2);
              if (snippets.length > 0) {
                snippetHtml += '<span class="kg-search-snippets">';
                snippets.forEach(function(field) {
                  snippetHtml += '<span class="kg-search-snippet">' +
                    '<span class="kg-search-field">' + escapeHtml(field.name) + ":</span> " +
                    searchSnippet(field, q) +
                    "</span>";
                });
                snippetHtml += "</span>";
              }
            }

            html += '<button type="button" class="kg-concept-item" data-concept-id="' +
              escapeHtml(id) +
              '">' +
              titleHtml +
              snippetHtml +
              "</button>";
            count += 1;
          });

          if (count === 0) {
            html += '<div style="color:#555; padding:4px 0;">No matching concepts.</div>';
          }
          document.getElementById("kg_concept_list").innerHTML = html;
        }

        window.kgReset = function(preserveStatus) {
          clearTransientConceptHighlight({skipEdgeRestore: true});
          restoreHoveredEdge();
          hideNodeTooltip();
          network.unselectAll();
          setCurrentView(createGraphView(GraphViewMode.ALL));
          activeNodeId = null;
          updateSelectedConceptHeader(null);
          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = false;
            o.opacity = 1.0;
            return o;
          }));
          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            return setEdgeHidden(o, false);
          }));
          updateNodeLabelPositions();
          if (!preserveStatus) {
            document.getElementById("kg_status").innerText = "Click a node to highlight its immediate neighbours.";
          }
          setActiveConceptItem(null);
          updateFocusLensDisplay();
        };

        window.kgShowAll = window.kgReset;

        function selectedOrActiveNodeId() {
          var selected = network.getSelectedNodes();
          return activeNodeId || selected[0] || null;
        }

        window.kgSetGraphView = function(value) {
          var nodeId = selectedOrActiveNodeId();
          if (value === GraphViewSelectValue.HIDE) {
            kgHideGraph();
          } else if (value === GraphViewSelectValue.ALL) {
            if (!nodeId) {
              kgReset();
              return;
            }
            applySectionGraphView(nodeId, {compact: false});
          } else if (value === GraphViewSelectValue.FOCUSED) {
            if (!nodeId) {
              document.getElementById("kg_status").innerText = "Select a node first.";
              updateGraphViewControls();
              return;
            }
            applySectionGraphView(nodeId, {compact: true});
          } else {
            updateGraphViewControls();
          }
        };

        function focusHiddenConcept(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          activeNodeId = nodeId;
          updateSelectedConceptHeader(nodeId);
          setCurrentView(createGraphView(GraphViewMode.HIDE, nodeId));
          kgHideGraph(true);
          showConcept(nodeId, {
            searchQuery: options.searchQuery,
            scrollToSearchMatch: options.scrollToSearchMatch
          });
          setActiveConceptItem(nodeId);
          if (!options.skipHistory) {
            pushConceptHistory(nodeId, graphViewHistoryMode(currentView));
          }
          if (statusPrefix) {
            document.getElementById("kg_status").innerText =
              statusPrefix + " " + conceptDisplayId(nodeId) + ". Graph hidden.";
          }
        }

        function navigateToConcept(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          if (graphViewIs(currentView, GraphViewMode.NEIGHBOURHOOD)) {
            focusNeighbourhood(nodeId, statusPrefix, {
              radius: graphViewRadius(currentView),
              searchQuery: options.searchQuery,
              scrollToSearchMatch: options.scrollToSearchMatch
            });
          } else if (graphViewIs(currentView, GraphViewMode.HIDE)) {
            focusHiddenConcept(nodeId, statusPrefix, options);
          } else if (graphViewIs(currentView, GraphViewMode.DESCENDANTS)) {
            focusDescendants(nodeId, statusPrefix, options);
          } else if (graphViewIs(currentView, GraphViewMode.DERIVATION_TRACE)) {
            focusDerivationTrace(nodeId, statusPrefix, options);
          } else {
            focusConcept(nodeId, statusPrefix, options);
          }
        }

        window.kgHideGraph = function(preserveStatus) {
          clearTransientConceptHighlight({skipEdgeRestore: true});
          restoreHoveredEdge();
          hideNodeTooltip();
          var nodeId = activeNodeId || (currentView && currentView.nodeId) || null;
          if (!detailsAreVisible()) {
            setInfoPanelVisible(true);
          }
          setCurrentView(createGraphView(GraphViewMode.HIDE, nodeId));
          network.unselectAll();
          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = true;
            return o;
          }));
          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            return setEdgeHidden(o, true);
          }));
          updateNodeLabelPositions();
          updateFocusLensDisplay();
          if (!preserveStatus) {
            document.getElementById("kg_status").innerText =
              "Graph hidden. Use the concept list or detail links to browse details.";
          }
        };

        window.kgSearch = function() {
          var q = searchDisplayText(document.getElementById("kg_search").value).toLowerCase();
          if (!q) { return; }

          var matches = matchingSearchIds(q);

          if (matches.length === 0) {
            document.getElementById("kg_status").innerText = "No matching concept found.";
            return;
          }

          buildConceptList(q);
          var id = matches[0];
          var concept = getConcept(id) || {};
          focusConcept(id, null, {
            searchQuery: q,
            scrollToSearchMatch: true
          });
          document.getElementById("kg_status").innerText =
            "Found " + matches.length + " match(es). Showing first: " + (concept.label || id);
        };

        function applySectionGraphView(nodeId, options) {
          options = options || {};
          var compact = options.compact === true;
          clearTransientConceptHighlight({skipEdgeRestore: true});
          restoreHoveredEdge();
          hideNodeTooltip();
          activeNodeId = nodeId;
          updateSelectedConceptHeader(nodeId);
          setCurrentView(createGraphView(compact ? GraphViewMode.FOCUSED : GraphViewMode.HIGHLIGHT, nodeId));
          var context = sectionGraphContext(nodeId);
          var visibleIds = Object.keys(originalNodes).filter(function(id) {
            return context.keep[id];
          });
          var compactPositions = compact ? buildCompactLayerPositions(visibleIds) : {};

          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            var inContext = context.keep[String(n.id)] === true;
            o.hidden = compact && !inContext;
            if (inContext) {
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
            if (compactPositions[n.id]) {
              o.x = compactPositions[n.id].x;
              o.y = compactPositions[n.id].y;
            }
            o = applyCollisionNodeStyle(o);
            return o;
          }));

          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            if (sectionContextEdgeHighlighted(e, context)) {
              o.color = Object.assign({}, o.color || {}, {opacity: 0.95});
              o.width = Math.max(Number(o.width) || 0, 3.0);
              return setEdgeHidden(o, false);
            } else if (compact) {
              return setEdgeHidden(o, true);
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
          if (compact) {
            fitNodesToAvailableRect(visibleIds, {maxScale: 0.85, animation: false});
          } else {
            fitHighlightedSelection(nodeId, {animation: false});
          }
          updateNodeLabelPositions();
          updateFocusLensDisplay();

          if (!options.preserveStatus) {
            document.getElementById("kg_status").innerText =
              (compact ? "Focussed graph: " : "All graph: ") +
              conceptDisplayId(nodeId) + " with " + context.label + ".";
          }
        }

        window.kgHighlight = function(nodeId, preserveStatus) {
          applySectionGraphView(nodeId, {compact: false, preserveStatus: preserveStatus});
        };

        function enabledNeighbourhoodNodes(nodeId, radius) {
          var keep = {};
          var queue = [{id: String(nodeId), depth: 0}];
          var maxDepth = Math.max(1, Math.floor(Number(radius) || 1));
          keep[String(nodeId)] = true;

          while (queue.length > 0) {
            var current = queue.shift();
            if (current.depth >= maxDepth) { continue; }

            enabledConnectedNodes(current.id).forEach(function(connectedId) {
              connectedId = String(connectedId);
              if (keep[connectedId]) { return; }
              keep[connectedId] = true;
              queue.push({id: connectedId, depth: current.depth + 1});
            });
          }
          return keep;
        }

        function kgApplyNeighbourhood(nodeId, preserveStatus, radius) {
          clearTransientConceptHighlight({skipEdgeRestore: true});
          restoreHoveredEdge();
          activeNodeId = nodeId;
          updateSelectedConceptHeader(nodeId);
          radius = clampNeighbourhoodRadius(radius);
          setCurrentView(createGraphView(GraphViewMode.NEIGHBOURHOOD, nodeId, {radius: radius}));
          var keep = enabledNeighbourhoodNodes(nodeId, radius);
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
            return setEdgeHidden(o, !(keep[e.from] && keep[e.to]));
          }));

          fitNodesToAvailableRect(visibleIds, {maxScale: 0.85, animation: false});
          updateNodeLabelPositions();
          if (!preserveStatus) {
            var neighbourCount = Math.max(0, visibleIds.length - 1);
            document.getElementById("kg_status").innerText =
              "Neighbourhood (" + radius + ") mode: " + conceptDisplayId(nodeId) + " plus " + neighbourCount +
              " neighbour" + (neighbourCount === 1 ? "" : "s") +
              ". Click a visible node to walk one step.";
          }
        }

        function kgApplyDescendants(nodeId, preserveStatus) {
          clearTransientConceptHighlight({skipEdgeRestore: true});
          restoreHoveredEdge();
          activeNodeId = nodeId;
          updateSelectedConceptHeader(nodeId);
          setCurrentView(createGraphView(GraphViewMode.DESCENDANTS, nodeId));
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
              edgeRelationDirected(e) &&
              keep[String(e.from)] &&
              keep[String(e.to)]
            ));
          }));

          fitNodesToAvailableRect(visibleIds, {maxScale: 0.85, animation: false});
          updateNodeLabelPositions();
          if (!preserveStatus) {
            var descendantCount = Math.max(0, visibleIds.length - 1);
            document.getElementById("kg_status").innerText =
              "Descendants mode: " + conceptDisplayId(nodeId) + " plus " + descendantCount +
              " reachable node" + (descendantCount === 1 ? "" : "s") +
              ". Click a visible node to walk one step.";
          }
        }

        function kgApplyDerivationTrace(nodeId, preserveStatus) {
          clearTransientConceptHighlight({skipEdgeRestore: true});
          restoreHoveredEdge();
          activeNodeId = nodeId;
          updateSelectedConceptHeader(nodeId);
          setCurrentView(createGraphView(GraphViewMode.DERIVATION_TRACE, nodeId));
          var trace = derivationTrace(nodeId);
          var visibleIds = Object.keys(originalNodes).filter(function(id) {
            return trace.nodes[id];
          });
          var compactPositions = buildCompactLayerPositions(visibleIds);

          nodes.update(allNodes.map(function(n) {
            var o = Object.assign({}, originalNodes[n.id]);
            o.hidden = !trace.nodes[n.id];
            if (compactPositions[n.id]) {
              o.x = compactPositions[n.id].x;
              o.y = compactPositions[n.id].y;
            }
            return o;
          }));

          edges.update(allEdges.map(function(e) {
            var o = Object.assign({}, originalEdges[e.id]);
            var visible = relationHasDerivationTreeSemantics(edgeRelation(e)) && trace.edges[e.id];
            if (visible) {
              o.color = Object.assign({}, o.color || {}, {opacity: 0.95});
              o.width = Math.max(Number(o.width) || 0, 3.0);
            }
            return setEdgeHidden(o, !visible);
          }));

          fitNodesToAvailableRect(visibleIds, {maxScale: 0.85, animation: false});
          updateNodeLabelPositions();
          if (!preserveStatus) {
            var traceNodeCount = Math.max(0, visibleIds.length - 1);
            document.getElementById("kg_status").innerText =
              "Derivation trace: " + conceptDisplayId(nodeId) + " plus " + traceNodeCount +
              " derived-from node" + (traceNodeCount === 1 ? "" : "s") +
              ". Click a visible node to trace from it.";
          }
        }

        /* Browser event wiring. */
        network.on("click", function(params) {
            if (params.nodes.length === 0 && params.edges && params.edges.length > 0) {
                showEdgeDetails(params.edges[0]);
                return;
            }

            if (params.nodes.length === 0)
                return;

            const nodeId = params.nodes[0];

            if (graphViewIs(currentView, GraphViewMode.NEIGHBOURHOOD)) {
              focusNeighbourhood(nodeId, null, {radius: graphViewRadius(currentView)});
            } else if (graphViewIs(currentView, GraphViewMode.DESCENDANTS)) {
              focusDescendants(nodeId);
            } else if (graphViewIs(currentView, GraphViewMode.DERIVATION_TRACE)) {
              focusDerivationTrace(nodeId);
            } else {
              focusConcept(nodeId, "Selected");
            }
        });

        network.on("hoverNode", function(params) {
          showNodeTooltip(params.node, params.pointer);
        });

        network.on("blurNode", hideNodeTooltip);

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
        window.addEventListener("resize", handleViewportResize);
        window.addEventListener("orientationchange", handleViewportResize);
        if (window.visualViewport) {
          window.visualViewport.addEventListener("resize", handleViewportResize);
          window.visualViewport.addEventListener("scroll", scheduleViewportRefit);
        }
        graphContainer.addEventListener("mouseleave", function() {
          restoreHoveredEdge();
          hideNodeTooltip();
        });

        window.addEventListener("popstate", function(event) {
          var nodeId = event.state && event.state.nodeId;
          var mode = event.state && event.state.mode;
          if (!nodeId) {
            nodeId = conceptIdFromHash(window.location.hash);
          }

          if (nodeId && getConcept(nodeId)) {
            var historyView = graphViewFromHistoryMode(mode, nodeId);
            if (graphViewIs(historyView, GraphViewMode.HIDE)) {
              focusHiddenConcept(nodeId, null, {skipHistory: true});
            } else if (graphViewIs(historyView, GraphViewMode.FOCUSED)) {
              applySectionGraphView(nodeId, {compact: true, preserveStatus: true});
              showConcept(nodeId);
              setActiveConceptItem(nodeId);
            } else if (graphViewIs(historyView, GraphViewMode.NEIGHBOURHOOD)) {
              focusNeighbourhood(nodeId, null, {
                skipHistory: true,
                radius: graphViewRadius(historyView)
              });
            } else if (graphViewIs(historyView, GraphViewMode.DESCENDANTS)) {
              focusDescendants(nodeId, null, {skipHistory: true});
            } else if (graphViewIs(historyView, GraphViewMode.DERIVATION_TRACE)) {
              focusDerivationTrace(nodeId, null, {skipHistory: true});
            } else {
              focusConcept(nodeId, "Selected", {skipHistory: true});
            }
          } else {
            kgReset(true);
          }
        });

        document.addEventListener("keydown", allowBrowserHistoryShortcut, true);

        document.getElementById("kg_search").addEventListener("keydown", function(e) {
          if (e.key === "Enter") { kgSearch(); }
        });

        document.getElementById("kg_search").addEventListener("input", function(e) {
          buildConceptList(e.target.value);
        });

        document.getElementById("kg_graph_view_select").addEventListener("change", function(e) {
          kgSetGraphView(e.target.value);
        });

        document.getElementById("kg_details_view_select").addEventListener("change", function(e) {
          setDetailsView(e.target.value);
        });

        document.getElementById("kg_focus_lens_toggle").addEventListener("click", function() {
          setFocusLensVisible(!focusLensVisible);
        });
        updateFocusLensVisibilityControls();

        document.getElementById("kg_splash_dismiss").addEventListener("click", dismissSplash);

        var notesEditToggle = document.getElementById("kg_notes_edit_toggle");
        notesEditToggle.checked = noteEditingEnabled;
        notesEditToggle.addEventListener("change", function(e) {
          noteEditingEnabled = e.target.checked;
          saveNoteEditingPreference();
          setNotesStatus(noteEditingEnabled ? "Note editing enabled." : "Note editing disabled.");
          refreshActiveConcept();
        });

        document.getElementById("kg_notes_list").addEventListener("click", function(e) {
          var item = e.target.closest(".kg-note-list-item");
          if (!item) { return; }

          e.preventDefault();
          var note = findUserNote(item.getAttribute("data-note-id"));
          var conceptId = item.getAttribute("data-concept-id");
          if (!note || !getConcept(conceptId)) { return; }
          openUserNoteId = note.id;
          focusConcept(conceptId, "Selected");
        });

        document.getElementById("kg_notes_import_button").addEventListener("click", function() {
          document.getElementById("kg_notes_import_input").click();
        });

        document.getElementById("kg_notes_import_input").addEventListener("change", function(e) {
          var file = e.target.files && e.target.files[0];
          if (!file) { return; }
          var reader = new FileReader();
          reader.onload = function() {
            try {
              var count = importNotesCsv(String(reader.result || ""));
              setNotesStatus("Imported " + count + " note(s).");
              refreshActiveConcept();
            } catch (err) {
              setNotesStatus("Could not import notes CSV.");
            }
            e.target.value = "";
          };
          reader.readAsText(file);
        });

        document.getElementById("kg_concept_list").addEventListener("click", function(e) {
          var item = e.target.closest(".kg-concept-item");
          if (!item) { return; }

          e.preventDefault();
          focusConcept(item.getAttribute("data-concept-id"), "Selected", {
            searchQuery: document.getElementById("kg_search").value,
            scrollToSearchMatch: true
          });
        });

        conceptPreview.addEventListener("pointerenter", cancelConceptPreviewHide);
        conceptPreview.addEventListener("pointerleave", scheduleConceptPreviewHide);
        conceptPreview.addEventListener("click", function(e) {
          var closeButton = e.target.closest(".concept-preview-close");
          if (closeButton) {
            e.preventDefault();
            hideConceptPreview(true);
            return;
          }

          var goButton = e.target.closest(".concept-preview-go");
          if (!goButton) { return; }

          e.preventDefault();
          var id = goButton.getAttribute("data-concept-id");
          hideConceptPreview(true);
          navigateToConcept(id, "Selected");
        });

        document.getElementById("info_panel").addEventListener("pointerover", function(e) {
          var link = conceptPreviewTriggerFromEventTarget(e.target);
          if (!link || e.pointerType === "touch") { return; }
          showConceptPreview(link, {pinned: false});
        });

        document.getElementById("info_panel").addEventListener("pointerout", function(e) {
          var link = conceptPreviewTriggerFromEventTarget(e.target);
          if (!link || conceptPreviewPinned) { return; }
          var related = e.relatedTarget;
          if (related && (link.contains(related) || conceptPreview.contains(related))) {
            return;
          }
          scheduleConceptPreviewHide();
        });

        document.getElementById("info_panel").addEventListener("focusin", function(e) {
          var link = conceptPreviewTriggerFromEventTarget(e.target);
          if (!link) { return; }
          showConceptPreview(link, {pinned: false});
        });

        document.getElementById("info_panel").addEventListener("focusout", function(e) {
          var link = conceptPreviewTriggerFromEventTarget(e.target);
          if (!link || conceptPreviewPinned) { return; }
          var related = e.relatedTarget;
          if (related && (link.contains(related) || conceptPreview.contains(related))) {
            return;
          }
          scheduleConceptPreviewHide();
        });

        document.addEventListener("click", function(e) {
          if (!conceptPreview || conceptPreview.style.display === "none") { return; }
          if (conceptPreviewTriggerFromEventTarget(e.target) || conceptPreview.contains(e.target)) {
            return;
          }
          hideConceptPreview(true);
        });

        document.addEventListener("keydown", function(e) {
          if (e.key === "Escape") {
            hideConceptPreview(true);
          }
        });

        document.getElementById("info_panel").addEventListener("pointerdown", function(e) {
          markPendingGraphSectionContext(e.target);
        });

        document.getElementById("info_panel").addEventListener("keydown", function(e) {
          if (e.key === "Enter" || e.key === " ") {
            markPendingGraphSectionContext(e.target);
          }
        });

        document.getElementById("info_panel").addEventListener("click", function(e) {
          var tocLink = e.target.closest(".concept-toc-link");
          if (tocLink) {
            e.preventDefault();
            var tocTargetId = tocLink.getAttribute("data-toc-target");
            var target = document.getElementById(tocTargetId);
            if (target) {
              var tocSectionRole = tocLink.getAttribute("data-section-role") ||
                sectionRoleForGraphContext(tocLink.getAttribute("data-graph-context"));
              var tocGraphContext = graphContextForSectionRole(tocSectionRole);
              setActiveConceptSection(
                tocTargetId,
                tocGraphContext,
                {
                  lensLabel: lensLabelForSectionRole(tocSectionRole),
                  forceGraphUpdate: true
                }
              );
              openTargetForToc(target);
              window.requestAnimationFrame(function() {
                scrollInfoPanelTargetBelowStickyToc(target);
              });
            }
            return;
          }

          var addNoteButton = e.target.closest(".kg-add-note");
          if (addNoteButton) {
            e.preventDefault();
            if (!noteEditingEnabled || !activeNodeId) { return; }
            createUserNote(
              activeNodeId,
              addNoteButton.getAttribute("data-section") || "",
              Number(addNoteButton.getAttribute("data-anchor-index")) || 0,
              addNoteButton.getAttribute("data-anchor-after") || ""
            );
            refreshActiveConcept();
            return;
          }

          var closeNoteButton = e.target.closest(".user-note-close");
          if (closeNoteButton) {
            e.preventDefault();
            if (!noteEditingEnabled) { return; }
            closeUserNote(closeNoteButton.getAttribute("data-note-id"));
            return;
          }

          var deleteNoteButton = e.target.closest(".user-note-delete");
          if (deleteNoteButton) {
            e.preventDefault();
            if (!noteEditingEnabled) { return; }
            deleteUserNote(deleteNoteButton.getAttribute("data-note-id"));
            refreshActiveConcept();
            return;
          }

          var edgeConceptButton = e.target.closest(".edge-detail-concept");
          if (edgeConceptButton) {
            e.preventDefault();
            var edgeConceptId = edgeConceptButton.getAttribute("data-edge-concept-id");
            if (!getConcept(edgeConceptId)) { return; }
            navigateToConcept(edgeConceptId, "Selected");
            return;
          }

          var link = e.target.closest(".concept-link");
          if (!link) { return; }

          e.preventDefault();
          var id = link.getAttribute("data-concept-id");
          if (!getConcept(id)) { return; }
          showConceptPreview(link, {pinned: true});
        });

        document.getElementById("info_panel").addEventListener("change", function(e) {
          var derivedFromFullTree = e.target.closest(".concept-derived-from-full-tree");
          if (derivedFromFullTree) {
            var derivedSection = derivedFromFullTree.closest(".concept-derived-from");
            var derivedSectionId = derivedSection ? derivedSection.id : null;
            var derivedSectionRole = DetailSectionRole.DERIVED_FROM;
            var derivedGraphContext = graphContextForSectionRole(derivedSectionRole);
            derivedFromFullTreeEnabled = derivedFromFullTree.checked;
            refreshActiveConcept();
            detailScrollSyncSuppressedUntil = Date.now() + 1000;
            setActiveConceptSection(derivedSectionId, derivedGraphContext, {
              lensLabel: lensLabelForSectionRole(derivedSectionRole),
              forceGraphUpdate: true
            });
            return;
          }

          var backlinksFullTree = e.target.closest(".concept-backlinks-full-tree");
          if (backlinksFullTree) {
            var backlinksSection = backlinksFullTree.closest(".concept-backlinks");
            var backlinksSectionId = backlinksSection ? backlinksSection.id : null;
            var backlinksSectionRole = DetailSectionRole.WHERE_USED;
            var backlinksGraphContext = graphContextForSectionRole(backlinksSectionRole);
            backlinksFullTreeEnabled = backlinksFullTree.checked;
            refreshActiveConcept();
            detailScrollSyncSuppressedUntil = Date.now() + 1000;
            setActiveConceptSection(backlinksSectionId, backlinksGraphContext, {
              lensLabel: lensLabelForSectionRole(backlinksSectionRole),
              forceGraphUpdate: true
            });
          }
        });

        document.getElementById("info_panel").addEventListener("input", function(e) {
          if (!noteEditingEnabled) { return; }
          var titleInput = e.target.closest(".user-note-title-input");
          if (titleInput) {
            updateUserNote(titleInput.getAttribute("data-note-id"), {title: titleInput.value});
            return;
          }
          var bodyInput = e.target.closest(".user-note-body-input");
          if (bodyInput) {
            updateUserNote(bodyInput.getAttribute("data-note-id"), {body: bodyInput.value});
          }
        });

        document.getElementById("info_panel").addEventListener("wheel", function(e) {
          if (!e.ctrlKey && !e.metaKey) { return; }
          e.preventDefault();
          e.stopPropagation();
          adjustInfoPanelTextZoom(e.deltaY);
        }, {passive: false});

        document.getElementById("info_panel").addEventListener("scroll", scheduleDetailScrollSync, {passive: true});

        document.getElementById("kg_controls").addEventListener("wheel", function(e) {
          if (!e.ctrlKey && !e.metaKey) { return; }
          e.preventDefault();
          e.stopPropagation();
          adjustControlsTextZoom(e.deltaY);
        }, {passive: false});

        document.getElementById("info_panel").addEventListener("touchstart", beginInfoPanelPinch, {passive: true});
        document.getElementById("info_panel").addEventListener("touchmove", updateInfoPanelPinch, {passive: false});
        document.getElementById("info_panel").addEventListener("touchend", endInfoPanelPinch, {passive: true});
        document.getElementById("info_panel").addEventListener("touchcancel", endInfoPanelPinch, {passive: true});

        document.getElementById("info_panel").addEventListener("toggle", function(e) {
          if (e.target && e.target.tagName === "DETAILS") {
            if (
              noteEditingEnabled &&
              e.target.classList.contains("user-note") &&
              !e.target.open
            ) {
              closeUserNote(e.target.getAttribute("data-note-id"));
              return;
            }
            var sectionRole = detailSectionRoleForDetailsSection(e.target);
            var graphContext = sectionRole ? graphContextForSectionRole(sectionRole) : null;
            if (graphContext) {
              if (!e.target.open) {
                e.target.setAttribute("data-section-user-closed", "true");
              } else if (
                pendingGraphSectionContext === graphContext ||
                e.target.getAttribute("data-section-user-closed") === "true"
              ) {
                e.target.removeAttribute("data-section-user-closed");
                setActiveConceptSection(e.target.id || null, graphContext, {
                  lensLabel: lensLabelForSectionRole(sectionRole),
                  forceGraphUpdate: true
                });
              }
            }
            if (graphContext) {
              pendingGraphSectionContext = null;
            }
            schedulePanelContentRefit();
          }
        }, true);

        /* Initial render. */
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
        buildConceptList("");
        renderNotesOverview();
        updateGraphViewControls();
        updateDetailsViewControls();
        updateFocusLensDisplay();
        setControlsVisible(!shouldStartWithControlsHidden());
        edges.update(allEdges.map(function(e) {
          var o = Object.assign({}, e);
          return setEdgeHidden(o, false);
        }));
        allEdges = edges.get();

        var initialNodeId = conceptIdFromHash(window.location.hash);
        if (initialNodeId && getConcept(initialNodeId)) {
          window.history.replaceState(
            {nodeId: String(initialNodeId), mode: GraphViewMode.HIGHLIGHT},
            "",
            conceptHash(initialNodeId)
          );
          focusConcept(initialNodeId, "Selected", {skipHistory: true});
        } else {
          var defaultNodeId = defaultStartupConceptId && getConcept(defaultStartupConceptId) ?
            defaultStartupConceptId : null;
          if (defaultNodeId) {
            window.history.replaceState(
              {nodeId: String(defaultNodeId), mode: GraphViewMode.HIGHLIGHT},
              "",
              conceptHash(defaultNodeId)
            );
            focusConcept(defaultNodeId, "Selected", {skipHistory: true});
          } else {
            window.history.replaceState({}, "", window.location.href);
          }
        }
        showSplashOnFirstLoad();
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
    
