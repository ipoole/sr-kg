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
        HIGHLIGHT: "highlight",
        HIDE: "hide",
        NEIGHBOURHOOD: "neighbourhood",
        DESCENDANTS: "descendants"
      });
      var GraphViewSelectValue = Object.freeze({
        ALL: "all",
        HIDE: "hide",
        NEIGHBOURHOOD_1: "neighbourhood-1",
        NEIGHBOURHOOD_2: "neighbourhood-2",
        DESCENDANTS: "descendants"
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
        if (graphViewIs(view, GraphViewMode.NEIGHBOURHOOD)) {
          return "neighbourhood-" + String(graphViewRadius(view));
        }
        return view.mode || GraphViewMode.HIGHLIGHT;
      }

      function graphViewSelectValue(view) {
        if (graphViewIs(view, GraphViewMode.HIDE)) { return GraphViewSelectValue.HIDE; }
        if (graphViewIs(view, GraphViewMode.NEIGHBOURHOOD)) {
          return graphViewRadius(view) === 2
            ? GraphViewSelectValue.NEIGHBOURHOOD_2
            : GraphViewSelectValue.NEIGHBOURHOOD_1;
        }
        if (graphViewIs(view, GraphViewMode.DESCENDANTS)) {
          return GraphViewSelectValue.DESCENDANTS;
        }
        return GraphViewSelectValue.ALL;
      }

      function graphViewFromHistoryMode(mode, nodeId) {
        if (mode === GraphViewMode.HIDE) {
          return createGraphView(GraphViewMode.HIDE, nodeId);
        }
        if (mode === GraphViewMode.NEIGHBOURHOOD || mode === GraphViewSelectValue.NEIGHBOURHOOD_1) {
          return createGraphView(GraphViewMode.NEIGHBOURHOOD, nodeId, {radius: 1});
        }
        if (mode === GraphViewSelectValue.NEIGHBOURHOOD_2) {
          return createGraphView(GraphViewMode.NEIGHBOURHOOD, nodeId, {radius: 2});
        }
        if (mode === GraphViewMode.DESCENDANTS) {
          return createGraphView(GraphViewMode.DESCENDANTS, nodeId);
        }
        return createGraphView(GraphViewMode.HIGHLIGHT, nodeId);
      }

      function kgAfterReady() {
        var allNodes = nodes.get();
        var allEdges = edges.get();
        var graphContainer = document.getElementById("mynetwork");
        var nodeLabelLayer = document.createElement("div");
        var nodeTooltip = document.createElement("div");
        var nodeLabelEls = {};

        nodeLabelLayer.id = "kg_node_labels";
        graphContainer.appendChild(nodeLabelLayer);
        nodeTooltip.id = "kg_node_tooltip";
        nodeTooltip.setAttribute("role", "tooltip");
        document.body.appendChild(nodeTooltip);

        var originalNodes = {};
        var originalEdges = {};
        var enabledEdgeRelations = {};
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
        var userNotesStorageKey = kgStorageKeys.userNotes;
        var noteEditingStorageKey = kgStorageKeys.noteEditing;
        var splashDismissedStorageKey = kgStorageKeys.splashDismissed;
        var userNotesState = loadUserNotes();
        var noteEditingEnabled = loadNoteEditingPreference();
        var openUserNoteId = null;
        var infoPanelPinchState = null;

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
        refreshNodeTooltips();
        Object.keys(edgeKey).forEach(function(relation) {
          enabledEdgeRelations[relation] = edgeKey[relation].directed !== false;
        });

        /* Text parsing and concept markup. */
        function escapeHtml(s) {
          return String(s || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
        }

        function renderSimpleConceptText(s) {
          return escapeHtml(s).replace(
            /\\cref\{([^{}]*)\}\{([^{}]*)\}/g,
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
          if (options.id) {
            attrs += ' data-note-id="' + escapeHtml(options.id) + '"';
          }
          if (options.open) {
            attrs += " open";
          }
          return '<details class="' + escapeHtml(options.className) + '"' + attrs + ">" +
            "<summary>" + renderConceptText(options.title || "") + "</summary>" +
            '<div class="' + escapeHtml(options.bodyClass || "") + '">' +
            (options.bodyHtml || "") +
            "</div></details>";
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
              pushText("");
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
          var html = "<h3>" + escapeHtml(title) + "</h3>";
          html += '<div class="concept-body concept-section" data-section="' + escapeHtml(title) + '">';
          html += renderNotesAtAnchor(conceptId, title, 0, "");
          blocks.forEach(function(block, index) {
            html += '<div class="concept-line">' + (block.text ? renderConceptText(block.text) : "&nbsp;") + "</div>";
            html += renderNotesAtAnchor(conceptId, title, index + 1, block.text.slice(0, 160));
          });
          html += "</div>";
          return html;
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
            showConcept(activeNodeId);
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
            "mark, .study-questions, svg, mjx-container, script, style"
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

        function currentInfoPanelFontSize() {
          var panel = document.getElementById("info_panel");
          var currentSize = parseFloat(window.getComputedStyle(panel).fontSize);
          if (!Number.isFinite(currentSize) || currentSize <= 0) {
            currentSize = kgInfoPanelConfig.fontSizePx;
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

        function legacyConceptSections(concept) {
          return [
            {key: "definition", title: "Definition", text: concept.definition_new || ""},
            {key: "derivation", title: "Derivation", text: concept.derivation_new || ""},
            {key: "explanation", title: "Explanation", text: concept.explanation_new || ""}
          ];
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
          return legacyConceptSections(concept || {});
        }

        function conceptSectionText(concept, key) {
          var section = conceptSections(concept).find(function(item) {
            return item.key === key;
          });
          return section ? section.text : "";
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
          var title = String(nodeId) + " " + String(concept.label || "");
          var definition = conceptSectionText(concept, "definition");
          var html = '<div class="kg-tooltip-title">' + renderTooltipText(title) + "</div>";
          if (definition) {
            html += '<div class="kg-tooltip-definition">' + renderTooltipText(definition) + "</div>";
          }
          html += tooltipListHtml("Optional details", optionalDetailTitlesForConcept(concept));
          html += tooltipListHtml("Notes", noteTitlesForConcept(nodeId));
          return html;
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
            {name: "ID", value: String(nodeId)},
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

        /* Edge filtering and relation-aware visibility. */
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
          if (graphViewIs(currentView, GraphViewMode.HIGHLIGHT) && graphViewHasNode(currentView)) {
            return edge.from == currentView.nodeId || edge.to == currentView.nodeId;
          }
          if (graphViewIs(currentView, GraphViewMode.DESCENDANTS)) {
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
          if (graphViewIs(currentView, GraphViewMode.HIDE)) {
            kgHideGraph(true);
            return;
          }
          if (graphViewIs(currentView, GraphViewMode.HIGHLIGHT) && graphViewHasNode(currentView)) {
            kgHighlight(currentView.nodeId, true);
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

        function showConcept(nodeId, options) {
          options = options || {};
          var concept = getConcept(nodeId);
          if (!concept) {
            document.getElementById("info_panel").innerHTML =
              "<h2>" + escapeHtml(nodeId) + "</h2>" +
              "<p>No concept data was found for this node.</p>";
            typesetInfoPanel(options);
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
          conceptSections(concept).forEach(function(section) {
            html += renderConceptSection(nodeId, section.title, section.text);
          });
          var studyQuestions = Array.isArray(concept.study_questions) ? concept.study_questions : [];
          if (studyQuestions.length > 0) {
            html += '<details class="study-questions">';
            html += "<summary>Study Questions</summary>";
            studyQuestions.forEach(function(item, index) {
              var question = item && item.question ? item.question : "";
              var answer = item && item.answer ? item.answer : "";
              if (!question) { return; }
              html += '<section class="study-question">';
              html += '<div class="study-question-title">Question ' + (index + 1) + "</div>";
              html += '<div class="concept-body">' + renderConceptText(question) + "</div>";
              if (answer) {
                html += '<details class="study-answer">';
                html += "<summary>Answer</summary>";
                html += '<div class="study-answer-body">' + renderConceptText(answer) + "</div>";
                html += "</details>";
              }
              html += "</section>";
            });
            html += "</details>";
          }
          var panel = document.getElementById("info_panel");
          panel.innerHTML = html;
          panel.classList.toggle("kg-note-editing", noteEditingEnabled);
          openUserNoteId = null;
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
          var insets = {
            left: margin,
            top: margin,
            right: margin,
            bottom: margin
          };

          visiblePanelRects().forEach(function(panel) {
            var overlap = intersectRects(baseAbs, panel.rect);
            if (!overlap) { return; }

            var edge = panelOcclusionEdge(panel, baseAbs, overlap);
            if (edge === "left") {
              insets.left = Math.max(insets.left, overlap.right - baseAbs.left + margin);
            } else if (edge === "right") {
              insets.right = Math.max(insets.right, baseAbs.right - overlap.left + margin);
            } else if (edge === "top") {
              insets.top = Math.max(insets.top, overlap.bottom - baseAbs.top + margin);
            } else if (edge === "bottom") {
              insets.bottom = Math.max(insets.bottom, baseAbs.bottom - overlap.top + margin);
            }
          });

          var availableAbs = {
            left: baseAbs.left + insets.left,
            top: baseAbs.top + insets.top,
            right: baseAbs.right - insets.right,
            bottom: baseAbs.bottom - insets.bottom
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

        function fitHighlightedSelection(nodeId) {
          var fitIds = [String(nodeId)];
          enabledConnectedNodes(nodeId).forEach(function(id) {
            if (originalNodes[id] && fitIds.indexOf(id) === -1) {
              fitIds.push(id);
            }
          });

          fitNodesToAvailableRect(fitIds, {maxScale: 0.7});
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
              graphViewIs(currentView, GraphViewMode.DESCENDANTS)
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
          activeNodeId = nodeId;
          kgHighlight(nodeId, true);
          showConcept(nodeId, {
            searchQuery: options.searchQuery,
            scrollToSearchMatch: options.scrollToSearchMatch
          });
          setActiveConceptItem(nodeId);
          fitHighlightedSelection(nodeId);
          if (!options.skipHistory) {
            pushConceptHistory(nodeId, graphViewHistoryMode(currentView));
          }
          if (statusPrefix) {
            document.getElementById("kg_status").innerText = statusPrefix + " " + nodeId + ".";
          }
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
          document.getElementById("kg_status").innerText =
            (statusPrefix ? statusPrefix + " " + nodeId + ". " : "") +
            "Neighbourhood (" + radius + ") mode: " + nodeId + " plus " + neighbourCount +
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
          document.getElementById("kg_status").innerText =
            (statusPrefix ? statusPrefix + " " + nodeId + ". " : "") +
            "Descendants mode: " + nodeId + " plus " + descendantCount +
            " reachable node" + (descendantCount === 1 ? "" : "s") +
            ". Click a visible node to walk one step.";
        }

        function buildConceptList(filterText) {
          var q = searchDisplayText(filterText).toLowerCase();
          var ids = matchingSearchIds(q);
          var html = "";
          var count = 0;

          ids.forEach(function(id) {
            var concept = getConcept(id);
            var label = searchDisplayText(concept.label || "");
            var titleHtml = '<span class="kg-search-hit-title">' +
              '<span class="kg-concept-id">' + highlightedSearchText(id, q) + "</span> " +
              highlightedSearchText(label, q) +
              "</span>";
            var snippetHtml = "";

            if (q) {
              var snippets = matchingSearchFields(id, q).filter(function(field) {
                return field.name !== "ID" && field.name !== "Title";
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
          restoreHoveredEdge();
          hideNodeTooltip();
          network.unselectAll();
          setCurrentView(createGraphView(GraphViewMode.ALL));
          activeNodeId = null;
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

        function selectedOrActiveNodeId() {
          var selected = network.getSelectedNodes();
          return activeNodeId || selected[0] || null;
        }

        window.kgSetGraphView = function(value) {
          var nodeId = selectedOrActiveNodeId();
          if (value === GraphViewSelectValue.HIDE) {
            kgHideGraph();
          } else if (value === GraphViewSelectValue.ALL) {
            kgReset();
          } else if (
            value === GraphViewSelectValue.NEIGHBOURHOOD_1 ||
            value === GraphViewSelectValue.NEIGHBOURHOOD_2
          ) {
            if (!nodeId) {
              document.getElementById("kg_status").innerText = "Select a node first.";
              updateGraphViewControls();
              return;
            }
            focusNeighbourhood(
              nodeId,
              null,
              {radius: value === GraphViewSelectValue.NEIGHBOURHOOD_2 ? 2 : 1}
            );
          } else if (value === GraphViewSelectValue.DESCENDANTS) {
            if (!nodeId) {
              document.getElementById("kg_status").innerText = "Select a node first.";
              updateGraphViewControls();
              return;
            }
            focusDescendants(nodeId);
          } else {
            updateGraphViewControls();
          }
        };

        function focusHiddenConcept(nodeId, statusPrefix, options) {
          options = options || {};
          if (!getConcept(nodeId)) { return; }
          activeNodeId = nodeId;
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
              statusPrefix + " " + nodeId + ". Graph hidden.";
          }
        }

        window.kgHideGraph = function(preserveStatus) {
          restoreHoveredEdge();
          hideNodeTooltip();
          var nodeId = activeNodeId || (currentView && currentView.nodeId) || null;
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

        window.kgHighlight = function(nodeId, preserveStatus) {
          restoreHoveredEdge();
          activeNodeId = nodeId;
          setCurrentView(createGraphView(GraphViewMode.HIGHLIGHT, nodeId));
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
          restoreHoveredEdge();
          activeNodeId = nodeId;
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
            return setEdgeHidden(o, !(edgeRelationEnabled(e) && keep[e.from] && keep[e.to]));
          }));

          fitNodesToAvailableRect(visibleIds, {maxScale: 0.85, animation: false});
          updateNodeLabelPositions();
          if (!preserveStatus) {
            var neighbourCount = Math.max(0, visibleIds.length - 1);
            document.getElementById("kg_status").innerText =
              "Neighbourhood (" + radius + ") mode: " + nodeId + " plus " + neighbourCount +
              " neighbour" + (neighbourCount === 1 ? "" : "s") +
              ". Click a visible node to walk one step.";
          }
        }

        function kgApplyDescendants(nodeId, preserveStatus) {
          restoreHoveredEdge();
          activeNodeId = nodeId;
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
              edgeRelationEnabled(e) &&
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
              "Descendants mode: " + nodeId + " plus " + descendantCount +
              " reachable node" + (descendantCount === 1 ? "" : "s") +
              ". Click a visible node to walk one step.";
          }
        }

        window.kgFocusSelected = function() {
          var nodeId = selectedOrActiveNodeId();
          if (!nodeId) {
            document.getElementById("kg_status").innerText = "Select a node first.";
            return;
          }

          focusNeighbourhood(nodeId, null, {radius: graphViewRadius(currentView)});
        };

        window.kgFocusDescendantsSelected = function() {
          var nodeId = selectedOrActiveNodeId();
          if (!nodeId) {
            document.getElementById("kg_status").innerText = "Select a node first.";
            return;
          }

          focusDescendants(nodeId);
        };

        /* Browser event wiring. */
        network.on("click", function(params) {

            if (params.nodes.length === 0)
                return;

            const nodeId = params.nodes[0];

            if (graphViewIs(currentView, GraphViewMode.NEIGHBOURHOOD)) {
              focusNeighbourhood(nodeId, null, {radius: graphViewRadius(currentView)});
            } else if (graphViewIs(currentView, GraphViewMode.DESCENDANTS)) {
              focusDescendants(nodeId);
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
        window.addEventListener("resize", scheduleViewportRefit);
        window.addEventListener("orientationchange", scheduleViewportRefit);
        if (window.visualViewport) {
          window.visualViewport.addEventListener("resize", scheduleViewportRefit);
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
            } else if (graphViewIs(historyView, GraphViewMode.NEIGHBOURHOOD)) {
              focusNeighbourhood(nodeId, null, {
                skipHistory: true,
                radius: graphViewRadius(historyView)
              });
            } else if (graphViewIs(historyView, GraphViewMode.DESCENDANTS)) {
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

        document.getElementById("kg_graph_view_select").addEventListener("change", function(e) {
          kgSetGraphView(e.target.value);
        });

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
          focusConcept(item.getAttribute("data-concept-id"), "Selected", {
            searchQuery: document.getElementById("kg_search").value,
            scrollToSearchMatch: true
          });
        });

        document.getElementById("info_panel").addEventListener("click", function(e) {
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

          var link = e.target.closest(".concept-link");
          if (!link) { return; }

          e.preventDefault();
          var id = link.getAttribute("data-concept-id");
          if (!getConcept(id)) { return; }

          if (graphViewIs(currentView, GraphViewMode.NEIGHBOURHOOD)) {
            focusNeighbourhood(id, "Selected", {radius: graphViewRadius(currentView)});
          } else if (graphViewIs(currentView, GraphViewMode.HIDE)) {
            focusHiddenConcept(id, "Selected");
          } else if (graphViewIs(currentView, GraphViewMode.DESCENDANTS)) {
            focusDescendants(id, "Selected");
          } else {
            focusConcept(id, "Selected");
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
        buildEdgeFilters();
        buildConceptList("");
        renderNotesOverview();
        updateGraphViewControls();
        if (shouldStartWithControlsHidden()) {
          setControlsVisible(false);
        }
        edges.update(allEdges.map(function(e) {
          var o = Object.assign({}, e);
          return setEdgeHidden(o, !edgeRelationEnabled(e));
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
          window.history.replaceState({}, "", window.location.href);
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
    
