      /* Runtime data injected by srkg.html_injection. */
      var conceptData = __CONCEPT_DATA__;
      var moduleData = __MODULE_DATA__;
      var publishedLayout = __PUBLISHED_LAYOUT__;
      var edgeKey = __EDGE_KEY__;
      var kgViewerConfig = __VIEWER_CONFIG__;
      var kgNodeLabelConfig = kgViewerConfig.nodeLabels || {};
      var kgInfoPanelConfig = kgViewerConfig.infoPanel || {};
      var kgStorageKeys = kgViewerConfig.storageKeys || {};
      var edgeHoverWidth = kgViewerConfig.edgeHoverWidth;

      var DisplayScope = Object.freeze({
        FULL: "full",
        CONTEXT: "context",
        HIDDEN: "hidden"
      });
      var ContextPreset = Object.freeze({
        CONNECTIONS: "connections",
        PREREQUISITES: "prerequisites",
        DERIVATION: "derivation",
        FOUNDATIONS: "foundations",
        USES: "uses",
        RELATED: "related",
        CUSTOM: "custom"
      });
      var ContextDepth = Object.freeze({
        ONE_HOP: "one-hop",
        TWO_HOPS: "two-hops",
        TRANSITIVE: "transitive"
      });

      function normaliseContextDepth(depth) {
        if (depth === ContextDepth.TWO_HOPS || depth === ContextDepth.TRANSITIVE) {
          return depth;
        }
        return ContextDepth.ONE_HOP;
      }

      function createContextRule(preset, depth, customTraversals) {
        var knownPresets = Object.keys(ContextPreset).map(function(key) {
          return ContextPreset[key];
        });
        return {
          preset: knownPresets.indexOf(preset) === -1 ? ContextPreset.CONNECTIONS : preset,
          depth: normaliseContextDepth(depth),
          customTraversals: Array.isArray(customTraversals)
            ? customTraversals.map(function(item) {
              return {
                relation: String(item.relation || ""),
                direction: String(item.direction || "")
              };
            }).filter(function(item) {
              return item.relation && ["incoming", "outgoing", "undirected"].indexOf(item.direction) !== -1;
            })
            : []
        };
      }

      function contextPresetTraversals(rule, relationDefinitions) {
        rule = createContextRule(rule && rule.preset, rule && rule.depth, rule && rule.customTraversals);
        relationDefinitions = relationDefinitions || {};
        if (rule.preset === ContextPreset.CUSTOM) {
          return rule.customTraversals.slice();
        }

        var specs = [];
        function add(relation, direction) {
          if (!relationDefinitions[relation]) { return; }
          specs.push({relation: relation, direction: direction});
        }
        function addDirectedBoth(relation) {
          add(relation, "incoming");
          add(relation, "outgoing");
        }

        if (rule.preset === ContextPreset.CONNECTIONS) {
          Object.keys(relationDefinitions).sort().forEach(function(relation) {
            if (relationDefinitions[relation].directed === true) {
              addDirectedBoth(relation);
            } else {
              add(relation, "undirected");
            }
          });
        } else if (rule.preset === ContextPreset.PREREQUISITES) {
          add("REQUIRES", "outgoing");
        } else if (rule.preset === ContextPreset.DERIVATION) {
          add("DERIVES_FROM", "outgoing");
          add("CONSTRUCTED_FROM", "outgoing");
        } else if (rule.preset === ContextPreset.FOUNDATIONS) {
          ["DERIVES_FROM", "CONSTRUCTED_FROM", "REQUIRES"].forEach(function(relation) {
            add(relation, "outgoing");
          });
        } else if (rule.preset === ContextPreset.USES) {
          ["REQUIRES", "DERIVES_FROM", "CONSTRUCTED_FROM"].forEach(function(relation) {
            add(relation, "incoming");
          });
        } else if (rule.preset === ContextPreset.RELATED) {
          add("RELATED", "undirected");
        }
        return specs;
      }

      function contextDepthLimit(depth) {
        if (depth === ContextDepth.TWO_HOPS) { return 2; }
        if (depth === ContextDepth.TRANSITIVE) { return Infinity; }
        return 1;
      }

      function computeContextSubgraph(seedIds, rule, graphEdges, relationDefinitions, validConceptIds) {
        var keep = {};
        var edgeKeep = {};
        var valid = validConceptIds || {};
        var traversals = contextPresetTraversals(rule, relationDefinitions);
        var traversalKeys = {};
        traversals.forEach(function(item) {
          traversalKeys[item.relation + "::" + item.direction] = true;
        });
        var queue = [];
        (seedIds || []).forEach(function(id) {
          id = String(id);
          if (Object.keys(valid).length > 0 && !valid[id]) { return; }
          if (!keep[id]) {
            keep[id] = true;
            queue.push({id: id, depth: 0});
          }
        });

        var limit = contextDepthLimit(rule && rule.depth);
        while (queue.length > 0) {
          var current = queue.shift();
          if (current.depth >= limit) { continue; }
          (graphEdges || []).forEach(function(edge) {
            var relation = String(edge.relation || "");
            var from = String(edge.from);
            var to = String(edge.to);
            var next = null;
            if (traversalKeys[relation + "::outgoing"] && from === current.id) {
              next = to;
            } else if (traversalKeys[relation + "::incoming"] && to === current.id) {
              next = from;
            } else if (traversalKeys[relation + "::undirected"]) {
              if (from === current.id) { next = to; }
              else if (to === current.id) { next = from; }
            }
            if (!next || (Object.keys(valid).length > 0 && !valid[next])) { return; }
            edgeKeep[String(edge.id)] = true;
            if (!keep[next]) {
              keep[next] = true;
              queue.push({id: next, depth: current.depth + 1});
            }
          });
        }

        return {
          nodeIds: Object.keys(keep).sort(),
          edgeIds: Object.keys(edgeKeep).sort(),
          keep: keep,
          edgeKeep: edgeKeep
        };
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
        var globalLayoutStorageKey = kgStorageKeys.globalLayout;
        var personalDataStore = window.kgCreatePersonalDataStore({
          storage: window.localStorage,
          storageKeys: kgStorageKeys
        });
        window.kgPersonalData = personalDataStore;
        var personalLayoutState = loadPersonalLayoutState();
        var globalLayout = buildInitialGlobalLayout();
        var personalLayoutSaveTimer = null;
        var activeNodeId = null;
        var activeModuleId = null;
        var viewerState = {
          contextRule: createContextRule(ContextPreset.FOUNDATIONS, ContextDepth.ONE_HOP),
          displayScope: DisplayScope.FULL
        };
        var layoutEditModeEnabled = false;
        var layoutEditPersistence = "temporary";
        var temporaryLayout = {concepts: {}, modules: {}};
        var contextFitPrimedKey = null;
        var contextContractionState = null;
        // Folded modules are a runtime graph projection; source concepts and edges stay unchanged.
        var foldedModules = {};
        var preferredFoldedModules = {};
        var projectedModuleEdgePrefix = "module-edge::";
        var moduleIdByConceptId = null;
        var hoveredEdgeId = null;
        var hoveredEdgeBeforeHover = null;
        var lastGraphNodeClick = null;
        var suppressedNativeDoubleClick = null;
        var pendingContainedConceptModuleSelection = null;
        var svgImageCache = {};
        var activeNodeRadiusScale = 1.4;
        var activeNodeBorderWidth = 6;
        var nodeLabelWidth = kgNodeLabelConfig.width;
        var nodeLabelFontSize = kgNodeLabelConfig.fontSize;
        var tooltipTypesetTimer = null;
        var selectedConceptHeaderTypesetTimer = null;
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
        var studyProgressStorageKey = kgStorageKeys.studyProgress || "srkg.studyProgress.v1";
        var contentReadProgressStorageKey = kgStorageKeys.contentReadProgress ||
          "srkg.contentReadProgress.v1";
        var userNotesState = loadUserNotes();
        var studyQuestionIndex = buildStudyQuestionIndex();
        var studyProgressState = loadStudyProgress();
        var contentBlockIndex = buildContentBlockIndex();
        var contentReadProgressState = loadContentReadProgress();
        var noteEditingEnabled = loadNoteEditingPreference();
        var openUserNoteId = null;
        var infoPanelPinchState = null;
        var infoPanelGraphicZoomBasePx = null;
        var readingMode = "full";
        var activeConceptSectionTargetId = null;
        var currentConceptTocItems = [];
        var detailScrollSyncTimer = null;
        var detailScrollSyncSuppressedUntil = 0;
        var derivedFromFullTreeEnabled = false;
        var backlinksFullTreeEnabled = false;
        var workspaceSplitPercent = 50;
        var workspaceSplitterPointerId = null;
        var contextNoticeTimer = null;
        var pendingPersonalDataImport = null;

        function validLayoutPosition(position) {
          return Boolean(
            position &&
            Number.isFinite(Number(position.x)) &&
            Number.isFinite(Number(position.y))
          );
        }

        function copyLayoutPosition(position) {
          return {x: Number(position.x), y: Number(position.y)};
        }

        function buildInitialGlobalLayout(includePersonal) {
          includePersonal = includePersonal !== false;
          var publishedConcepts = publishedLayout && publishedLayout.concepts
            ? publishedLayout.concepts
            : {};
          var publishedModules = publishedLayout && publishedLayout.modules
            ? publishedLayout.modules
            : {};
          var layout = {
            schema_version: Number(publishedLayout && publishedLayout.schema_version) || 1,
            revision: String(publishedLayout && publishedLayout.revision || "unpublished"),
            concepts: {},
            modules: {}
          };
          allNodes.forEach(function(node) {
            var position = publishedConcepts[String(node.id)];
            if (!validLayoutPosition(position)) {
              position = node;
            }
            if (validLayoutPosition(position)) {
              layout.concepts[String(node.id)] = copyLayoutPosition(position);
            }
          });
          Object.keys(publishedModules).forEach(function(moduleId) {
            var entry = publishedModules[moduleId] || {};
            if (validLayoutPosition(entry.anchor)) {
              layout.modules[String(moduleId)] = {
                anchor: copyLayoutPosition(entry.anchor)
              };
            }
          });
          if (includePersonal && personalLayoutState) {
            Object.keys(personalLayoutState.concepts || {}).forEach(function(conceptId) {
              var position = personalLayoutState.concepts[conceptId];
              if (layout.concepts[conceptId] && validLayoutPosition(position)) {
                layout.concepts[conceptId] = copyLayoutPosition(position);
              }
            });
            Object.keys(personalLayoutState.modules || {}).forEach(function(moduleId) {
              var entry = personalLayoutState.modules[moduleId] || {};
              if (layout.modules[moduleId] && validLayoutPosition(entry.anchor)) {
                layout.modules[moduleId] = {anchor: copyLayoutPosition(entry.anchor)};
              }
            });
          }
          return layout;
        }

        function globalConceptPosition(conceptId) {
          return globalLayout.concepts[String(conceptId)] || null;
        }

        function temporaryConceptPosition(conceptId) {
          return temporaryLayout.concepts[String(conceptId)] || null;
        }

        function effectiveConceptPosition(conceptId) {
          return temporaryConceptPosition(conceptId) || globalConceptPosition(conceptId);
        }

        function setGlobalConceptPosition(conceptId, position) {
          if (!validLayoutPosition(position)) { return; }
          globalLayout.concepts[String(conceptId)] = copyLayoutPosition(position);
          schedulePersonalLayoutSave();
        }

        function setGlobalModuleAnchor(moduleId, position) {
          if (!validLayoutPosition(position)) { return; }
          globalLayout.modules[String(moduleId)] = {
            anchor: copyLayoutPosition(position)
          };
          schedulePersonalLayoutSave();
        }

        function globalModuleAnchor(moduleId) {
          var entry = globalLayout.modules[String(moduleId)] || {};
          return validLayoutPosition(entry.anchor) ? entry.anchor : null;
        }

        function temporaryModuleAnchor(moduleId) {
          return temporaryLayout.modules[String(moduleId)] || null;
        }

        function effectiveModuleAnchor(moduleId) {
          return temporaryModuleAnchor(moduleId) || globalModuleAnchor(moduleId);
        }

        function nodeWithGlobalPosition(node) {
          var result = Object.assign({}, node || {});
          var position = effectiveConceptPosition(result.id);
          if (position) {
            result.x = position.x;
            result.y = position.y;
          }
          return result;
        }

        function baseNodeForRender(nodeId) {
          return nodeWithGlobalPosition(originalNodes[String(nodeId)] || nodes.get(nodeId) || {});
        }

        function globalLayoutSnapshot() {
          return JSON.parse(JSON.stringify(globalLayout));
        }

        function positionsEqual(a, b) {
          return validLayoutPosition(a) && validLayoutPosition(b) &&
            Math.abs(Number(a.x) - Number(b.x)) < 0.000001 &&
            Math.abs(Number(a.y) - Number(b.y)) < 0.000001;
        }

        function loadPersonalLayoutState() {
          var parsed = personalDataStore.getLayoutState();
          if (!parsed || Object.keys(parsed.concepts).length === 0 &&
              Object.keys(parsed.modules).length === 0) { return null; }
          return parsed;
        }

        function personalLayoutOverrides() {
          var concepts = {};
          var modules = {};
          Object.keys(globalLayout.concepts).forEach(function(conceptId) {
            var current = globalLayout.concepts[conceptId];
            var published = publishedLayout.concepts && publishedLayout.concepts[conceptId];
            if (!positionsEqual(current, published)) {
              concepts[conceptId] = copyLayoutPosition(current);
            }
          });
          Object.keys(globalLayout.modules).forEach(function(moduleId) {
            var current = globalLayout.modules[moduleId].anchor;
            var publishedEntry = publishedLayout.modules && publishedLayout.modules[moduleId] || {};
            if (!positionsEqual(current, publishedEntry.anchor)) {
              modules[moduleId] = {anchor: copyLayoutPosition(current)};
            }
          });
          return {concepts: concepts, modules: modules};
        }

        function writePersonalLayoutNow() {
          if (!globalLayoutStorageKey) { return; }
          var overrides = personalLayoutOverrides();
          if (Object.keys(overrides.concepts).length === 0 && Object.keys(overrides.modules).length === 0) {
            personalLayoutState = null;
            personalDataStore.replaceLayout({
              schema_version: 1,
              published_revision: String(publishedLayout.revision),
              concepts: {}, modules: {}
            });
            safeLocalStorageRemove(globalLayoutStorageKey);
            updateLayoutControls();
            return;
          }
          personalLayoutState = {
            schema_version: 1,
            published_revision: personalLayoutState && personalLayoutState.published_revision
              ? String(personalLayoutState.published_revision)
              : String(publishedLayout.revision),
            concepts: overrides.concepts,
            modules: overrides.modules
          };
          personalDataStore.replaceLayout(personalLayoutState);
          safeLocalStorageSet(globalLayoutStorageKey, JSON.stringify(personalLayoutState));
          updateLayoutControls();
        }

        function schedulePersonalLayoutSave() {
          if (!globalLayout || !globalLayoutStorageKey) { return; }
          if (personalLayoutSaveTimer !== null) {
            clearTimeout(personalLayoutSaveTimer);
          }
          personalLayoutSaveTimer = setTimeout(function() {
            personalLayoutSaveTimer = null;
            writePersonalLayoutNow();
          }, 120);
        }

        function personalLayoutStatus() {
          var overrides = personalLayoutOverrides();
          var hasOverrides = Object.keys(overrides.concepts).length > 0 ||
            Object.keys(overrides.modules).length > 0;
          var savedRevision = personalLayoutState && personalLayoutState.published_revision
            ? String(personalLayoutState.published_revision)
            : String(publishedLayout.revision);
          return {
            hasOverrides: hasOverrides,
            publishedRevision: String(publishedLayout.revision),
            savedRevision: savedRevision,
            revisionMismatch: hasOverrides && savedRevision !== String(publishedLayout.revision)
          };
        }

        function keepPersonalLayout() {
          if (!personalLayoutStatus().hasOverrides) { return; }
          personalLayoutState.published_revision = String(publishedLayout.revision);
          writePersonalLayoutNow();
          updateLayoutControls();
        }

        function applyGlobalLayoutPositions() {
          nodes.update(Object.keys(globalLayout.concepts).filter(function(id) {
            return Boolean(nodes.get(id));
          }).map(function(id) {
            var position = globalLayout.concepts[id];
            return {id: id, x: position.x, y: position.y};
          }));
          foldedModuleIdList().forEach(function(moduleId) {
            refreshFoldedModuleGeometry(moduleId, false);
          });
          updateNodeLabelPositions();
        }

        function resetToPublishedLayout() {
          resetContextFitInteraction({restore: false});
          if (personalLayoutSaveTimer !== null) {
            clearTimeout(personalLayoutSaveTimer);
            personalLayoutSaveTimer = null;
          }
          personalLayoutState = null;
          personalDataStore.replaceLayout({
            schema_version: 1,
            published_revision: String(publishedLayout.revision),
            concepts: {}, modules: {}
          });
          safeLocalStorageRemove(globalLayoutStorageKey);
          globalLayout = buildInitialGlobalLayout(false);
          temporaryLayout = {concepts: {}, modules: {}};
          applyGlobalLayoutPositions();
          updateLayoutControls();
        }

        function normalizedExportCoordinate(value) {
          return Number(Number(value).toFixed(6));
        }

        function exportedGlobalLayout() {
          var concepts = {};
          var modules = {};
          Object.keys(globalLayout.concepts).sort().forEach(function(conceptId) {
            var position = globalLayout.concepts[conceptId];
            concepts[conceptId] = {
              x: normalizedExportCoordinate(position.x),
              y: normalizedExportCoordinate(position.y)
            };
          });
          Object.keys(globalLayout.modules).sort().forEach(function(moduleId) {
            var anchor = globalLayout.modules[moduleId].anchor;
            modules[moduleId] = {anchor: {
              x: normalizedExportCoordinate(anchor.x),
              y: normalizedExportCoordinate(anchor.y)
            }};
          });
          return {
            schema_version: Number(publishedLayout.schema_version) || 1,
            revision: String(publishedLayout.revision),
            concepts: concepts,
            modules: modules
          };
        }

        function exportGlobalLayout() {
          var text = JSON.stringify(exportedGlobalLayout(), null, 2) + "\n";
          var blob = new Blob([text], {type: "application/json;charset=utf-8"});
          var url = URL.createObjectURL(blob);
          var link = document.createElement("a");
          link.href = url;
          link.download = "layout.json";
          document.body.appendChild(link);
          link.click();
          link.remove();
          URL.revokeObjectURL(url);
        }

        function updateLayoutControls() {
          var statusElement = document.getElementById("kg_layout_status");
          if (!statusElement) { return; }
          var status = personalLayoutStatus();
          statusElement.textContent = "Published revision " + status.publishedRevision +
            (status.hasOverrides ? " · Personal overrides active" : " · Published layout active");
          document.getElementById("kg_layout_revision_warning").hidden = !status.revisionMismatch;
          document.getElementById("kg_layout_reset").disabled = !status.hasOverrides;
          var toggle = document.getElementById("kg_layout_edit_toggle");
          var persistence = document.getElementById("kg_layout_edit_persistence");
          var message = document.getElementById("kg_layout_edit_message");
          if (toggle) { toggle.checked = layoutEditModeEnabled; }
          if (persistence) { persistence.value = layoutEditPersistence; }
          if (message) {
            if (!layoutEditModeEnabled) {
              message.textContent = "Node dragging is off.";
            } else if (viewerState.displayScope === DisplayScope.HIDDEN) {
              message.textContent = "Layout editing is on. Show the graph to move nodes.";
            } else if (layoutEditPersistence === "temporary") {
              message.textContent = "Moves are temporary and are not saved.";
            } else {
              message.textContent = "Moves are saved to your personal layout in this browser.";
            }
          }
        }

        function globalLayoutEditingEnabled() {
          return layoutEditModeEnabled;
        }

        function persistentLayoutEditingEnabled() {
          return layoutEditModeEnabled && layoutEditPersistence === "personal" &&
            viewerState.displayScope !== DisplayScope.HIDDEN;
        }

        function temporaryLayoutEditingEnabled() {
          return layoutEditModeEnabled && layoutEditPersistence === "temporary" &&
            viewerState.displayScope !== DisplayScope.HIDDEN;
        }

        function layoutDraggingEnabled() {
          return layoutEditModeEnabled && viewerState.displayScope !== DisplayScope.HIDDEN;
        }

        function setLayoutEditingEnabled(enabled) {
          var restoreTemporary = temporaryLayoutEditingEnabled() && !enabled;
          layoutEditModeEnabled = enabled === true;
          updateGraphViewControls();
          if (restoreTemporary) { discardTemporaryLayout(); }
        }

        function setLayoutEditPersistence(value) {
          value = value === "personal" ? "personal" : "temporary";
          var discardTemporary = layoutEditPersistence === "temporary" &&
            value !== "temporary" && Object.keys(temporaryLayout.concepts).concat(
              Object.keys(temporaryLayout.modules)
            ).length > 0;
          layoutEditPersistence = value;
          if (discardTemporary) { discardTemporaryLayout(); }
          updateGraphViewControls();
        }

        function showContextNotice(message, kind) {
          var notice = document.getElementById("kg_context_notice");
          if (!notice) { return; }
          if (contextNoticeTimer !== null) {
            clearTimeout(contextNoticeTimer);
            contextNoticeTimer = null;
          }
          notice.textContent = message || "";
          notice.hidden = !message;
          notice.setAttribute("data-kind", kind || "info");
        }

        function showTransientContextNotice(message, kind, duration) {
          showContextNotice(message, kind);
          contextNoticeTimer = setTimeout(function() {
            var notice = document.getElementById("kg_context_notice");
            if (notice && notice.getAttribute("data-kind") === kind) {
              notice.hidden = true;
              notice.textContent = "";
            }
            contextNoticeTimer = null;
          }, duration || 2800);
        }

        function updateLayoutFromDrag(params) {
          if (!layoutDraggingEnabled()) { return; }
          var draggedIds = params && Array.isArray(params.nodes) ? params.nodes : [];
          if (draggedIds.length === 0) { return; }
          if (contextContractionState) {
            showContextNotice(
              "Contracted context adjusted temporarily — navigating away restores the layout.",
              "context-contracted"
            );
            return;
          }
          var affectedModules = {};
          draggedIds.forEach(function(nodeId) {
            var position = graphPositionForNode(nodeId);
            if (!position) { return; }
            var moduleId = moduleIdFromGraphNodeId(nodeId);
            if (moduleId && selectedModuleIsFolded(moduleId)) {
              var anchor = syncFoldedModulePosition(moduleId);
              if (temporaryLayoutEditingEnabled()) {
                temporaryLayout.modules[String(moduleId)] = copyLayoutPosition(anchor);
              } else {
                setGlobalModuleAnchor(moduleId, anchor);
                restoreFoldedModuleMembers(moduleId);
                affectedModules[moduleId] = true;
              }
              return;
            }
            if (getConcept(nodeId)) {
              if (temporaryLayoutEditingEnabled()) {
                temporaryLayout.concepts[String(nodeId)] = copyLayoutPosition(position);
              } else {
                setGlobalConceptPosition(nodeId, position);
              }
              var owner = moduleIdForConcept(nodeId);
              if (owner) { affectedModules[owner] = true; }
            }
          });
          Object.keys(affectedModules).forEach(function(moduleId) {
            refreshFoldedModuleGeometry(moduleId, false);
          });
          if (temporaryLayoutEditingEnabled()) {
            showContextNotice(
              "Temporary layout adjusted — changes will be discarded when editing is turned off or the page is reloaded.",
              "temporary-layout"
            );
          } else {
            showContextNotice(
              "Personal layout updated — saved in this browser.",
              "personal-layout"
            );
          }
        }

        window.kgGlobalLayoutSnapshot = globalLayoutSnapshot;
        window.kgLayoutEditingEnabled = globalLayoutEditingEnabled;
        window.kgPersistentLayoutEditingEnabled = persistentLayoutEditingEnabled;
        window.kgTemporaryLayoutEditingEnabled = temporaryLayoutEditingEnabled;
        window.kgLayoutDraggingEnabled = layoutDraggingEnabled;
        window.kgPersonalLayoutStatus = personalLayoutStatus;
        window.kgKeepPersonalLayout = keepPersonalLayout;
        window.kgResetToPublishedLayout = resetToPublishedLayout;
        window.kgExportGlobalLayout = exportGlobalLayout;
        window.kgExportedGlobalLayout = exportedGlobalLayout;

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
              refreshModuleFootprints();
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
          if (!nodeTooltip || viewerState.displayScope === DisplayScope.HIDDEN) { return; }
          var moduleId = moduleIdFromGraphNodeId(nodeId);
          if (moduleId && getModule(moduleId)) {
            nodeTooltip.innerHTML = moduleTooltipHtml(moduleId);
          } else if (getConcept(nodeId)) {
            nodeTooltip.innerHTML = conceptTooltipHtml(nodeId);
          } else {
            return;
          }
          nodeTooltip.style.display = "block";
          positionNodeTooltip(pointer);
          scheduleTooltipTypeset();
        }

        function showEdgeTooltip(edgeId, pointer) {
          var edge = edges.get(edgeId);
          if (!nodeTooltip || !edgeHoverableInCurrentView(edge)) { return; }
          hideConceptPreview(true);
          nodeTooltip.innerHTML = edgeTooltipHtml(edge);
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
            var proxy = foldedModuleConceptProxyForConcept(id);
            var pos = proxy ? {x: proxy.x, y: proxy.y} : positions[id];
            var transient = Boolean(
              transientConceptHighlight && transientConceptHighlight.nodeId === String(id)
            );
            if (
              !node || !pos || (node.hidden && !proxy) ||
              (visibleFontSize <= kgNodeLabelConfig.hideBelowPx && !transient && !proxy)
            ) {
              el.classList.remove("kg-node-label-transient");
              el.style.display = "none";
              return;
            }

            var dom = network.canvasToDOM(pos);
            var baseRadius = Number(node.visualSize) || Number(node.size) || 18;
            var radius = proxy
              ? proxy.radius
              : (id === activeNodeId ? baseRadius * activeNodeRadiusScale : baseRadius);
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
              transient
            );
          });
        }
        window.kgUpdateNodeLabelPositions = updateNodeLabelPositions;

        function drawConceptFace(ctx, node, pos, options) {
            options = options || {};
            var baseRadius = Number(node.visualSize) || Number(node.size) || 18;
            var isActive = options.active === true;
            var radius = options.radius ||
              (isActive ? baseRadius * activeNodeRadiusScale : baseRadius);
            var isTransient = options.transient === true;
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
        }

        function drawVisibleNodes(ctx) {
          var positions = network.getPositions();
          nodes.get().forEach(function(node) {
            if (node.hidden) { return; }
            if (node.isModuleNode) { return; }

            var pos = positions[node.id];
            if (!pos) { return; }

            drawConceptFace(ctx, node, pos, {
              active: node.id === activeNodeId,
              transient: Boolean(
                transientConceptHighlight &&
                transientConceptHighlight.nodeId === String(node.id)
              )
            });
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

        nodes.update(allNodes.map(function(node) {
          return applyCollisionNodeStyle(nodeWithGlobalPosition(node));
        }));
        allNodes = nodes.get();
        edges.update(allEdges.map(function(e) {
          return {id: e.id, title: ""};
        }));
        allEdges = edges.get();
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
          if (options.contentBlockId) {
            attrs += ' data-content-block-id="' + escapeHtml(options.contentBlockId) + '"';
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

        function safeLocalStorageRemove(key) {
          if (!key) { return false; }
          try {
            window.localStorage.removeItem(key);
            return true;
          } catch (e) {
            return false;
          }
        }

        function buildStudyQuestionIndex() {
          var index = {};
          Object.keys(conceptData || {}).forEach(function(conceptId) {
            var concept = conceptData[conceptId] || {};
            var questions = Array.isArray(concept.study_questions)
              ? concept.study_questions
              : [];
            questions.forEach(function(question) {
              var questionId = String(question && question.question_id || "");
              if (!questionId) { return; }
              index[questionId] = {
                conceptId: String(conceptId),
                question: question
              };
            });
          });
          return index;
        }

        function buildContentBlockIndex() {
          var index = {};
          function addBlocks(ownerType, ownerId, blocks) {
            (Array.isArray(blocks) ? blocks : []).forEach(function(block) {
              var blockId = String(block && block.block_id || "");
              if (!blockId) { return; }
              index[blockId] = {
                ownerType: ownerType,
                ownerId: String(ownerId),
                title: String(block.title || "")
              };
            });
          }
          Object.keys(conceptData || {}).forEach(function(conceptId) {
            addBlocks("concept", conceptId, conceptData[conceptId].content_blocks);
          });
          Object.keys(moduleData || {}).forEach(function(moduleId) {
            addBlocks("module", moduleId, moduleData[moduleId].content_blocks);
          });
          return index;
        }

        function loadContentReadProgress() {
          return personalDataStore.getReadingState(contentBlockIndex);
        }

        function saveContentReadProgress() {
          return safeLocalStorageSet(
            contentReadProgressStorageKey,
            JSON.stringify(contentReadProgressState)
          );
        }

        function contentOwnerBlockIds(ownerType, ownerId) {
          ownerType = String(ownerType || "");
          ownerId = String(ownerId || "");
          return Object.keys(contentBlockIndex).filter(function(blockId) {
            var block = contentBlockIndex[blockId];
            return block.ownerType === ownerType && block.ownerId === ownerId;
          });
        }

        function contentOwnerReadComplete(ownerType, ownerId) {
          var blockIds = contentOwnerBlockIds(ownerType, ownerId);
          return blockIds.length > 0 && blockIds.every(function(blockId) {
            return contentReadProgressState.blocks[blockId] === true;
          });
        }

        function renderContentReadCompletionIndicator(ownerType, ownerId) {
          var complete = contentOwnerReadComplete(ownerType, ownerId);
          return '<span class="content-read-complete-indicator" role="img"' +
            ' aria-label="All content blocks read" title="All content blocks read"' +
            ' data-content-owner-type="' + escapeHtml(ownerType) + '"' +
            ' data-content-owner-id="' + escapeHtml(ownerId) + '"' +
            (complete ? "" : " hidden") + ">✓</span>";
        }

        function updateContentReadCompletionIndicators() {
          document.querySelectorAll(".content-read-complete-indicator").forEach(
            function(indicator) {
              indicator.hidden = !contentOwnerReadComplete(
                indicator.getAttribute("data-content-owner-type"),
                indicator.getAttribute("data-content-owner-id")
              );
            }
          );
        }

        function setContentBlockRead(blockId, isRead) {
          blockId = String(blockId || "");
          if (!contentBlockIndex[blockId]) { return false; }
          personalDataStore.setRead(blockId, isRead);
          contentReadProgressState = loadContentReadProgress();
          saveContentReadProgress();
          updateContentReadCompletionIndicators();
          return true;
        }

        window.kgContentReadProgress = {
          storageKey: contentReadProgressStorageKey,
          isRead: function(blockId) {
            return contentReadProgressState.blocks[String(blockId || "")] === true;
          },
          setRead: setContentBlockRead
        };

        function loadStudyProgress() {
          return personalDataStore.getStudyState(studyQuestionIndex);
        }

        function copyStudyProgress(value) {
          return JSON.parse(JSON.stringify(value));
        }

        function saveStudyProgress() {
          return safeLocalStorageSet(
            studyProgressStorageKey,
            JSON.stringify(studyProgressState)
          );
        }

        function announceStudyProgressChange(questionId) {
          try {
            window.dispatchEvent(new CustomEvent("kg:study-progress-changed", {
              detail: {questionId: questionId || ""}
            }));
          } catch (err) {
            // Progress remains usable in older browsers without CustomEvent.
          }
        }

        function recordStudyAttempt(questionId, outcome, attemptedAt) {
          questionId = String(questionId || "");
          outcome = String(outcome || "");
          if (!studyQuestionIndex[questionId] ||
              ["correct", "incorrect", "unknown"].indexOf(outcome) === -1) {
            return null;
          }
          var date = attemptedAt ? new Date(attemptedAt) : new Date();
          if (Number.isNaN(date.getTime())) { date = new Date(); }
          personalDataStore.addStudyAttempt(questionId, outcome, date.toISOString());
          studyProgressState = loadStudyProgress();
          saveStudyProgress();
          var entry = studyProgressState.questions[questionId];
          announceStudyProgressChange(questionId);
          return copyStudyProgress(entry);
        }

        function resetStudyQuestion(questionId) {
          questionId = String(questionId || "");
          if (!Object.prototype.hasOwnProperty.call(studyProgressState.questions, questionId)) {
            return false;
          }
          personalDataStore.resetStudy(questionId);
          studyProgressState = loadStudyProgress();
          saveStudyProgress();
          announceStudyProgressChange(questionId);
          return true;
        }

        function resetAllStudyProgress() {
          personalDataStore.resetStudy("");
          studyProgressState = loadStudyProgress();
          saveStudyProgress();
          announceStudyProgressChange("");
          return true;
        }

        window.kgStudyProgress = {
          storageKey: studyProgressStorageKey,
          getState: function() {
            return copyStudyProgress(studyProgressState);
          },
          getQuestion: function(questionId) {
            var entry = studyProgressState.questions[String(questionId || "")];
            return entry ? copyStudyProgress(entry) : null;
          },
          recordAttempt: recordStudyAttempt,
          resetQuestion: resetStudyQuestion,
          resetAll: resetAllStudyProgress
        };

        function loadUserNotes() {
          return {
            version: 2,
            notes: personalDataStore.getNotes().map(normalizeUserNote).filter(Boolean)
          };
        }

        function saveUserNotes() {
          var saved = personalDataStore.replaceNotes(userNotesState.notes);
          safeLocalStorageSet(userNotesStorageKey, JSON.stringify(userNotesState));
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
          if (!note || !note.section) { return null; }
          var targetType = String(note.targetType || (note.moduleId ? "module" : "concept"));
          var targetId = String(note.targetId || note.moduleId || note.conceptId || "");
          if ((targetType !== "concept" && targetType !== "module") || !targetId) {
            return null;
          }
          var anchor = note.anchor || {};
          var blockIndex = Number(anchor.blockIndex);
          if (!Number.isFinite(blockIndex) || blockIndex < 0) { blockIndex = 0; }
          return {
            id: String(note.id || makeNoteId()),
            targetType: targetType,
            targetId: targetId,
            conceptId: targetType === "concept" ? targetId : "",
            section: String(note.section),
            anchor: {
              blockIndex: Math.floor(blockIndex),
              afterText: String(anchor.afterText || ""),
              blockId: String(anchor.blockId || ""),
              sectionKey: String(anchor.sectionKey || ""),
              contextBefore: String(anchor.contextBefore || ""),
              contextAfter: String(anchor.contextAfter || "")
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

        function normalizeNoteAnchorContext(value) {
          return String(value || "").replace(/\s+/g, " ").trim();
        }

        function noteContextBefore(value) {
          var normalized = normalizeNoteAnchorContext(value);
          return normalized.slice(Math.max(0, normalized.length - 160));
        }

        function noteContextAfter(value) {
          return normalizeNoteAnchorContext(value).slice(0, 160);
        }

        function noteAnchorSpecs(blockId, sectionKey, sectionName, text) {
          var blocks = splitConceptBlocks(String(text || ""));
          var specs = [];
          for (var index = 0; index <= blocks.length; index += 1) {
            var before = blocks.slice(0, index).map(function(block) {
              return block.text || "";
            }).join(" ");
            var after = blocks.slice(index).map(function(block) {
              return block.text || "";
            }).join(" ");
            specs.push({
              blockId: String(blockId || ""),
              sectionKey: String(sectionKey || ""),
              section: String(sectionName || ""),
              blockIndex: index,
              contextBefore: index === 0 ? "" : noteContextBefore(before),
              contextAfter: index === blocks.length ? "" : noteContextAfter(after),
              legacyAfter: index === 0 ? "" : String(blocks[index - 1].text || "").slice(0, 160)
            });
          }
          return specs;
        }

        function noteAnchorCandidates(targetType, targetId) {
          var candidates = [];
          if (targetType === "concept") {
            var concept = getConcept(targetId);
            if (!concept) { return candidates; }
            if (conceptGraphicSvg(concept)) {
              candidates = candidates.concat(noteAnchorSpecs("", "graphic", "Graphic", ""));
            }
            if (shouldRenderContentBlocks(concept)) {
              conceptContentBlocks(concept).forEach(function(block) {
                candidates = candidates.concat(noteAnchorSpecs(
                  block.block_id, "", block.title || contentBlockKindLabel(block.kind), block.body
                ));
              });
            } else {
              conceptSections(concept).forEach(function(section) {
                var matchingBlocks = conceptContentBlocks(concept).filter(function(block) {
                  return block.kind === section.key;
                });
                candidates = candidates.concat(noteAnchorSpecs(
                  matchingBlocks.length === 1 ? matchingBlocks[0].block_id : "",
                  "legacy:" + section.key, section.title, section.text
                ));
              });
            }
            if (Array.isArray(concept.study_questions) && concept.study_questions.length > 0) {
              candidates = candidates.concat(
                noteAnchorSpecs("", "study-questions", "Study Questions", "")
              );
            }
          } else if (targetType === "module") {
            var module = getModule(targetId);
            if (!module) { return candidates; }
            if (module.svg_detail || module.svg_icon) {
              candidates = candidates.concat(noteAnchorSpecs("", "graphic", "Graphic", ""));
            }
            moduleContentBlocks(module).forEach(function(block) {
              candidates = candidates.concat(noteAnchorSpecs(
                block.block_id, "", block.title || contentBlockKindLabel(block.kind), block.body
              ));
            });
          }
          return candidates;
        }

        function uniqueBestNoteAnchor(candidates, anchor) {
          var before = normalizeNoteAnchorContext(anchor.contextBefore);
          var after = normalizeNoteAnchorContext(anchor.contextAfter);
          if (!before && !after) {
            var byIndex = candidates.filter(function(candidate) {
              return candidate.blockIndex === Number(anchor.blockIndex || 0);
            });
            return byIndex.length === 1 ? byIndex[0] : null;
          }
          var scored = candidates.map(function(candidate) {
            var score = 0;
            if (before && candidate.contextBefore === before) { score += 2; }
            if (after && candidate.contextAfter === after) { score += 1; }
            return {candidate: candidate, score: score};
          });
          var best = Math.max.apply(null, scored.map(function(item) { return item.score; }));
          if (best <= 0) { return null; }
          var matches = scored.filter(function(item) { return item.score === best; });
          return matches.length === 1 ? matches[0].candidate : null;
        }

        function adoptResolvedNoteAnchor(note, candidate) {
          if (!candidate) { return null; }
          var anchor = note.anchor || (note.anchor = {});
          if (!anchor.blockId && !anchor.sectionKey) {
            anchor.blockId = candidate.blockId;
            anchor.sectionKey = candidate.sectionKey;
            anchor.blockIndex = candidate.blockIndex;
            anchor.contextBefore = candidate.contextBefore;
            anchor.contextAfter = candidate.contextAfter;
          }
          return candidate;
        }

        function resolveNoteAnchor(note) {
          var candidates = noteAnchorCandidates(note.targetType, note.targetId);
          var anchor = note.anchor || {};
          var scoped = [];
          if (anchor.blockId) {
            scoped = candidates.filter(function(candidate) {
              return candidate.blockId === String(anchor.blockId);
            });
          } else if (anchor.sectionKey) {
            scoped = candidates.filter(function(candidate) {
              return candidate.sectionKey === String(anchor.sectionKey);
            });
          }
          if (scoped.length > 0) {
            return uniqueBestNoteAnchor(scoped, anchor);
          }
          if (anchor.blockId || anchor.sectionKey) { return null; }

          // Version-1 notes and CSV rows used a visible title plus local index.
          var legacy = candidates.filter(function(candidate) {
            return candidate.section === String(note.section || "");
          });
          if (anchor.afterText) {
            var afterMatches = legacy.filter(function(candidate) {
              return normalizeNoteAnchorContext(candidate.legacyAfter) ===
                normalizeNoteAnchorContext(anchor.afterText);
            });
            if (afterMatches.length === 1) {
              return adoptResolvedNoteAnchor(note, afterMatches[0]);
            }
            return null;
          }
          var indexMatches = legacy.filter(function(candidate) {
            return candidate.blockIndex === Number(anchor.blockIndex || 0);
          });
          return indexMatches.length === 1
            ? adoptResolvedNoteAnchor(note, indexMatches[0])
            : null;
        }

        function noteAnchorStatus(note) {
          var targetExists = note.targetType === "concept"
            ? Boolean(getConcept(note.targetId))
            : Boolean(getModule(note.targetId));
          if (!targetExists) { return "missing-target"; }
          return resolveNoteAnchor(note) ? "resolved" : "unmatched";
        }

        function unresolvedNoteCount() {
          return userNotesState.notes.filter(function(note) {
            return noteAnchorStatus(note) !== "resolved";
          }).length;
        }

        function migrateUserNotesState() {
          if (!userNotesState || !Array.isArray(userNotesState.notes)) { return; }
          userNotesState.version = 2;
          userNotesState.notes.forEach(function(note) { resolveNoteAnchor(note); });
          safeLocalStorageSet(userNotesStorageKey, JSON.stringify(userNotesState));
        }

        function sameNoteAnchor(left, right) {
          return left && right &&
            left.blockId === right.blockId &&
            left.sectionKey === right.sectionKey &&
            left.blockIndex === right.blockIndex &&
            left.contextBefore === right.contextBefore &&
            left.contextAfter === right.contextAfter;
        }

        function notesForAnchor(targetType, targetId, anchorSpec) {
          return userNotesState.notes.filter(function(note) {
            return note.targetType === String(targetType) &&
              note.targetId === String(targetId) &&
              sameNoteAnchor(resolveNoteAnchor(note), anchorSpec);
          }).sort(function(a, b) {
            return String(a.createdAt).localeCompare(String(b.createdAt));
          });
        }

        function findUserNote(noteId) {
          return userNotesState.notes.find(function(note) {
            return note.id === noteId;
          }) || null;
        }

        function noteTargetLabel(note) {
          if (note.targetType === "module") {
            var module = getModule(note.targetId) || {};
            return "Module " + (module.title || note.targetId);
          }
          var concept = getConcept(note.targetId) || {};
          return conceptDisplayId(note.targetId) +
            (concept.label ? " " + searchDisplayText(concept.label) : "");
        }

        function sortedUserNotes() {
          return userNotesState.notes.slice().sort(function(a, b) {
            var typeOrder = String(a.targetType).localeCompare(String(b.targetType));
            if (typeOrder !== 0) { return typeOrder; }
            var targetOrder = a.targetType === "concept"
              ? compareConceptIds(a.targetId, b.targetId)
              : compareModules(a.targetId, b.targetId);
            if (targetOrder !== 0) { return targetOrder; }
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
            var status = noteAnchorStatus(note);
            var warning = status === "resolved" ? "" :
              '<span class="kg-note-list-warning">' +
              (status === "missing-target" ? "Missing target" : "Needs placement") +
              "</span>";
            return '<button type="button" class="kg-note-list-item" data-note-id="' +
              escapeHtml(note.id) + '" data-target-type="' + escapeHtml(note.targetType) +
              '" data-target-id="' + escapeHtml(note.targetId) + '">' +
              '<span class="kg-note-list-concept">' + escapeHtml(noteTargetLabel(note)) + "</span>" +
              '<span class="kg-note-list-title">' + escapeHtml(note.title || "Untitled note") + "</span>" +
              warning +
              "</button>";
          }).join("");
        }

        function attemptedStudyQuestions() {
          return Object.keys(studyProgressState.questions).map(function(questionId) {
            var indexed = studyQuestionIndex[questionId];
            if (!indexed) { return null; }
            var concept = getConcept(indexed.conceptId) || {};
            var questions = Array.isArray(concept.study_questions)
              ? concept.study_questions
              : [];
            return {
              questionId: questionId,
              conceptId: indexed.conceptId,
              concept: concept,
              question: indexed.question,
              questionNumber: questions.indexOf(indexed.question) + 1,
              progress: studyProgressState.questions[questionId]
            };
          }).filter(Boolean).sort(function(a, b) {
            return String(b.progress.lastAttemptAt).localeCompare(
              String(a.progress.lastAttemptAt)
            );
          });
        }

        function studyQuestionPrompt(question) {
          return searchDisplayText(
            question && (question.prompt || question.question) || "Question"
          );
        }

        function renderStudyScorecard() {
          var summary = document.getElementById("kg_study_summary");
          var list = document.getElementById("kg_study_list");
          var badge = document.getElementById("kg_study_badge");
          var resetAll = document.getElementById("kg_study_reset_all");
          if (!summary || !list || !badge || !resetAll) { return; }

          var entries = attemptedStudyQuestions();
          var correctCount = entries.filter(function(entry) {
            return entry.progress.lastOutcome === "correct";
          }).length;
          if (entries.length === 0) {
            summary.textContent = "No questions attempted yet.";
            list.innerHTML = "";
            badge.textContent = "";
            resetAll.hidden = true;
            return;
          }

          summary.textContent = correctCount + " correct out of " +
            entries.length + " attempted";
          badge.textContent = correctCount + "/" + entries.length;
          resetAll.hidden = false;
          list.innerHTML = entries.map(function(entry) {
            var outcome = entry.progress.lastOutcome;
            var attempts = entry.progress.attemptCount;
            var conceptLabel = conceptDisplayId(entry.conceptId) +
              (entry.concept.label ? " " + searchDisplayText(entry.concept.label) : "");
            var questionLabel = entry.questionNumber > 0
              ? "Question " + entry.questionNumber + ": "
              : "";
            return '<div class="kg-study-row" data-question-id="' +
              escapeHtml(entry.questionId) + '">' +
              '<button type="button" class="kg-study-question-link" data-question-id="' +
              escapeHtml(entry.questionId) + '">' +
              '<span class="kg-study-question-concept">' + escapeHtml(conceptLabel) + "</span>" +
              '<span class="kg-study-question-prompt">' + escapeHtml(
                questionLabel + studyQuestionPrompt(entry.question)
              ) + "</span>" +
              '<span class="kg-study-question-meta" data-outcome="' +
              escapeHtml(outcome) + '"><span aria-hidden="true">' +
              studyOutcomeIcon(outcome) + "</span> " +
              escapeHtml(studyOutcomeText(outcome)) + " · " + attempts + " attempt" +
              (attempts === 1 ? "" : "s") + "</span></button>" +
              '<button type="button" class="kg-study-reset-question" data-question-id="' +
              escapeHtml(entry.questionId) + '" aria-label="Reset progress for ' +
              escapeHtml(conceptLabel) + '">Reset</button></div>';
          }).join("");
        }

        function openScorecardQuestion(questionId) {
          var indexed = studyQuestionIndex[questionId];
          if (!indexed) { return; }
          setDetailsView("practice");
          navigateToConcept(indexed.conceptId, "Selected");
          window.requestAnimationFrame(function() {
            var selector = '.study-question[data-question-id="' +
              cssAttributeValueEscape(questionId) + '"]';
            var questionCard = document.querySelector(selector);
            if (!questionCard) { return; }
            var section = questionCard.closest(".study-questions");
            if (section) { section.open = true; }
            questionCard.open = true;
            document.querySelectorAll('.study-question[data-scorecard-target="true"]').forEach(
              function(card) { card.removeAttribute("data-scorecard-target"); }
            );
            questionCard.setAttribute("data-scorecard-target", "true");
            scrollInfoPanelTargetBelowStickyToc(questionCard);
          });
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

        function renderNotesAtAnchor(targetType, targetId, sectionName, anchorIndex, afterText, anchorSpec) {
          anchorSpec = anchorSpec || {
            blockId: "", sectionKey: "", section: String(sectionName),
            blockIndex: Number(anchorIndex), contextBefore: "", contextAfter: ""
          };
          var html = "";
          notesForAnchor(targetType, targetId, anchorSpec).forEach(function(note) {
            html += renderUserNote(note);
          });
          html += '<div class="kg-add-note-row">';
          html += '<button type="button" class="kg-add-note" data-section="' +
            escapeHtml(sectionName) + '" data-anchor-index="' + String(anchorIndex) +
            '" data-anchor-after="' + escapeHtml(afterText || "") +
            '" data-anchor-block-id="' + escapeHtml(anchorSpec.blockId || "") +
            '" data-anchor-section-key="' + escapeHtml(anchorSpec.sectionKey || "") +
            '" data-anchor-context-before="' + escapeHtml(anchorSpec.contextBefore || "") +
            '" data-anchor-context-after="' + escapeHtml(anchorSpec.contextAfter || "") +
            '" data-target-type="' + escapeHtml(targetType) +
            '" data-target-id="' + escapeHtml(targetId) + '">+ note</button>';
          html += "</div>";
          return html;
        }

        function renderUnmatchedNotes(targetType, targetId) {
          var notes = userNotesState.notes.filter(function(note) {
            return note.targetType === String(targetType) &&
              note.targetId === String(targetId) && noteAnchorStatus(note) === "unmatched";
          });
          if (notes.length === 0) { return ""; }
          var html = '<details class="kg-unmatched-notes" open>' +
            '<summary>Notes needing placement (' + notes.length + ")</summary>" +
            '<p>The original content changed, so these notes were not moved automatically.</p>';
          notes.forEach(function(note) {
            html += '<div class="kg-unmatched-note"><div class="kg-unmatched-note-location">Former section: ' +
              escapeHtml(note.section || "Unknown") + "</div>" + renderUserNote(note) + "</div>";
          });
          return html + "</details>";
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

        function renderConceptSection(conceptId, blockId, sectionKey, title, text) {
          var raw = String(text || "");
          if (!raw) { return ""; }
          var blocks = splitConceptBlocks(raw);
          var specs = noteAnchorSpecs(blockId, "legacy:" + sectionKey, title, raw);
          var html = '<h3 id="' + escapeHtml(contentAnchorId(conceptId, title)) + '">' +
            escapeHtml(title) + "</h3>";
          html += '<div class="concept-body concept-section" data-section="' + escapeHtml(title) + '">';
          html += renderNotesAtAnchor("concept", conceptId, title, 0, "", specs[0]);
          blocks.forEach(function(block, index) {
            html += '<div class="concept-line">' + (block.text ? renderConceptText(block.text) : "&nbsp;") + "</div>";
            html += renderNotesAtAnchor(
              "concept", conceptId, title, index + 1, block.text.slice(0, 160), specs[index + 1]
            );
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

        function createUserNote(targetType, targetId, sectionName, anchorIndex, afterText, stableAnchor) {
          stableAnchor = stableAnchor || {};
          var now = new Date().toISOString();
          var note = {
            id: makeNoteId(),
            targetType: String(targetType),
            targetId: String(targetId),
            conceptId: targetType === "concept" ? String(targetId) : "",
            section: String(sectionName),
            anchor: {
              blockIndex: Number(anchorIndex) || 0,
              afterText: String(afterText || ""),
              blockId: String(stableAnchor.blockId || ""),
              sectionKey: String(stableAnchor.sectionKey || ""),
              contextBefore: String(stableAnchor.contextBefore || ""),
              contextAfter: String(stableAnchor.contextAfter || "")
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
          } else if (activeModuleId && getModule(activeModuleId)) {
            showModule(activeModuleId, {preserveSectionContext: true});
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
            "target_type",
            "target_id",
            "target_label",
            "concept_id",
            "concept_label",
            "section",
            "anchor_index",
            "anchor_after",
            "anchor_block_id",
            "anchor_section_key",
            "anchor_context_before",
            "anchor_context_after",
            "title",
            "body",
            "created_at",
            "updated_at"
          ]];
          userNotesState.notes.forEach(function(note) {
            var concept = note.targetType === "concept" ? (getConcept(note.targetId) || {}) : {};
            rows.push([
              note.id,
              note.targetType,
              note.targetId,
              noteTargetLabel(note),
              note.targetType === "concept" ? note.targetId : "",
              concept.label || "",
              note.section,
              String((note.anchor && note.anchor.blockIndex) || 0),
              (note.anchor && note.anchor.afterText) || "",
              (note.anchor && note.anchor.blockId) || "",
              (note.anchor && note.anchor.sectionKey) || "",
              (note.anchor && note.anchor.contextBefore) || "",
              (note.anchor && note.anchor.contextAfter) || "",
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
            var targetType = value(row, "target_type").trim() || "concept";
            var targetId = value(row, "target_id").trim() || conceptId;
            var section = value(row, "section").trim();
            if (!targetId || !section || (targetType !== "concept" && targetType !== "module")) { return; }
            var noteId = value(row, "note_id").trim() || makeNoteId();
            var blockIndex = Number(value(row, "anchor_index"));
            if (!Number.isFinite(blockIndex) || blockIndex < 0) { blockIndex = 0; }
            var note = findUserNote(noteId);
            var payload = {
              id: noteId,
              targetType: targetType,
              targetId: targetId,
              conceptId: targetType === "concept" ? targetId : "",
              section: section,
              anchor: {
                blockIndex: Math.floor(blockIndex),
                afterText: value(row, "anchor_after"),
                blockId: value(row, "anchor_block_id"),
                sectionKey: value(row, "anchor_section_key"),
                contextBefore: value(row, "anchor_context_before"),
                contextAfter: value(row, "anchor_context_after")
              },
              title: value(row, "title") || "Imported note",
              body: value(row, "body"),
              createdAt: value(row, "created_at") || new Date().toISOString(),
              updatedAt: value(row, "updated_at") || new Date().toISOString()
            };
            resolveNoteAnchor(payload);
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

        function setPersonalDataStatus(message) {
          var status = document.getElementById("kg_personal_data_status");
          if (status) { status.textContent = String(message || ""); }
        }

        function personalDataSummaryText(summary) {
          return [
            summary.notes + " note" + (summary.notes === 1 ? "" : "s"),
            summary.layout + " personal layout position" + (summary.layout === 1 ? "" : "s"),
            summary.study + " study attempt record" + (summary.study === 1 ? "" : "s"),
            summary.reading + " read mark" + (summary.reading === 1 ? "" : "s")
          ].join(", ");
        }

        function exportPersonalData() {
          writePersonalLayoutNow();
          var bytes = window.kgPersonalDataArchive.exportBytes(personalDataStore.getSnapshot());
          var blob = new Blob([bytes], {type: "application/zip"});
          var url = URL.createObjectURL(blob);
          var link = document.createElement("a");
          link.href = url;
          link.download = "srkg-personal-data.zip";
          document.body.appendChild(link);
          link.click();
          link.remove();
          URL.revokeObjectURL(url);
          setPersonalDataStatus("Personal data exported.");
        }

        function showPersonalDataImport(profile) {
          pendingPersonalDataImport = profile;
          var summary = window.kgPersonalDataArchive.summarize(profile);
          document.getElementById("kg_personal_data_import_summary").textContent =
            "This archive contains " + personalDataSummaryText(summary) + ".";
          var merge = document.querySelector(
            'input[name="kg_personal_import_mode"][value="merge"]'
          );
          if (merge) { merge.checked = true; }
          var dialog = document.getElementById("kg_personal_data_import_dialog");
          if (dialog.showModal) { dialog.showModal(); }
          else { dialog.setAttribute("open", ""); }
        }

        function closePersonalDataImport() {
          pendingPersonalDataImport = null;
          var dialog = document.getElementById("kg_personal_data_import_dialog");
          if (dialog.close) { dialog.close(); }
          else { dialog.removeAttribute("open"); }
        }

        function applyPersonalDataImport() {
          if (!pendingPersonalDataImport) { return; }
          var selected = document.querySelector(
            'input[name="kg_personal_import_mode"]:checked'
          );
          var mode = selected ? selected.value : "merge";
          if (mode === "replace" && !window.confirm(
            "Replace all personal data currently stored in this browser?"
          )) { return; }
          var succeeded = mode === "replace"
            ? personalDataStore.replaceSnapshot(pendingPersonalDataImport)
            : personalDataStore.mergeSnapshot(pendingPersonalDataImport);
          if (!succeeded) {
            setPersonalDataStatus("Could not save the imported personal data.");
            return;
          }
          try {
            window.sessionStorage.setItem(
              "srkg.personalData.importStatus",
              "Personal data " + (mode === "replace" ? "replaced" : "merged") + "."
            );
          } catch (err) { /* reload still applies the import */ }
          window.location.reload();
        }

        window.kgExportPersonalData = exportPersonalData;

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
          var contextPanel = document.getElementById("kg_graph_context_panel");
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
          if (contextPanel) {
            graphPane.insertBefore(contextPanel, graphSurface);
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

        function cameraSnapshot() {
          return {
            position: network.getViewPosition(),
            scale: network.getScale()
          };
        }

        var cameraRestoreGeneration = 0;
        function preserveCameraAfterLayout(snapshot) {
          if (!snapshot) { return; }
          cameraRestoreGeneration += 1;
          var generation = cameraRestoreGeneration;
          function restore() {
            if (generation !== cameraRestoreGeneration) { return; }
            network.moveTo({
              position: snapshot.position,
              scale: snapshot.scale,
              animation: false
            });
            updateNodeLabelPositions();
          }
          requestAnimationFrame(function() {
            requestAnimationFrame(restore);
          });
          setTimeout(restore, 180);
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
          setWorkspaceSplitPreservingCamera(((clientX - rect.left) / rect.width) * 100);
        }

        function setWorkspaceSplitPreservingCamera(value) {
          var camera = cameraSnapshot();
          applyWorkspaceSplit(value);
          preserveCameraAfterLayout(camera);
          scheduleViewportRefresh();
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
            scheduleViewportRefresh();
          }
          splitter.addEventListener("pointerup", stopDragging);
          splitter.addEventListener("pointercancel", stopDragging);
          splitter.addEventListener("keydown", function(e) {
            if (e.altKey || e.metaKey || e.ctrlKey) { return; }
            if (e.key === "ArrowLeft") {
              e.preventDefault();
              setWorkspaceSplitPreservingCamera(workspaceSplitPercent - 4);
            } else if (e.key === "ArrowRight") {
              e.preventDefault();
              setWorkspaceSplitPreservingCamera(workspaceSplitPercent + 4);
            } else if (e.key === "Home") {
              e.preventDefault();
              setWorkspaceSplitPreservingCamera(28);
            } else if (e.key === "End") {
              e.preventDefault();
              setWorkspaceSplitPreservingCamera(72);
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
          if (window.MathJax && MathJax.typesetClear) {
            MathJax.typesetClear([title]);
          }
          if (nodeId && getConcept(nodeId)) {
            title.innerHTML = escapeHtml(conceptDisplayId(nodeId)) + " " +
              renderConceptText(getConcept(nodeId).label || "");
            scheduleSelectedConceptHeaderTypeset();
          } else {
            title.textContent = defaultViewTitle;
          }
        }

        function typesetSelectedConceptHeader() {
          var title = document.getElementById("kg_view_title");
          if (!title) { return; }
          if (window.MathJax && MathJax.typesetPromise) {
            if (MathJax.typesetClear) {
              MathJax.typesetClear([title]);
            }
            MathJax.typesetPromise([title]).catch(function(err) {
              console.warn("MathJax title typesetting failed:", err);
            });
          } else {
            scheduleSelectedConceptHeaderTypeset();
          }
        }

        function scheduleSelectedConceptHeaderTypeset() {
          if (selectedConceptHeaderTypesetTimer) {
            clearTimeout(selectedConceptHeaderTypesetTimer);
          }
          selectedConceptHeaderTypesetTimer = setTimeout(function() {
            selectedConceptHeaderTypesetTimer = null;
            typesetSelectedConceptHeader();
          }, 250);
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
            return;
          }

          readingMode = readingModeDefinitions[value] ? value : "full";
          setInfoPanelVisible(true);
          if (activeNodeId && getConcept(activeNodeId)) {
            showConcept(activeNodeId, {preserveSectionContext: true});
          } else if (activeModuleId && getModule(activeModuleId)) {
            showModule(activeModuleId, {preserveSectionContext: true});
          }
          updateDetailsViewControls();
          document.getElementById("kg_status").innerText =
            "Details mode: " + currentReadingModeDefinition().label + ".";
        }

        function setInfoPanelVisible(visible) {
          var panel = document.getElementById("info_panel");
          if (!visible && viewerState.displayScope === DisplayScope.HIDDEN) {
            visible = true;
            document.getElementById("kg_status").innerText =
              "Details remain visible while the graph is hidden.";
          }
          var camera = cameraSnapshot();
          panel.classList.toggle("kg-hidden", !visible);
          document.body.classList.toggle("kg-details-hidden", !visible);
          preserveCameraAfterLayout(camera);
          updateDetailsViewControls();
          updateGraphContextControls();
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
          if (!Number.isFinite(infoPanelGraphicZoomBasePx)) {
            infoPanelGraphicZoomBasePx = currentInfoPanelFontSize();
          }
          var nextSize = Math.max(
            kgInfoPanelConfig.textZoomMinPx,
            Math.min(kgInfoPanelConfig.textZoomMaxPx, Number(sizePx))
          );
          panel.style.fontSize = nextSize + "px";
          panel.style.setProperty(
            "--kg-details-graphic-width",
            String((nextSize / infoPanelGraphicZoomBasePx) * 100) + "%"
          );
          panel.style.setProperty(
            "--kg-details-module-graphic-width",
            String((nextSize / infoPanelGraphicZoomBasePx) * 50) + "%"
          );
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

        /* Display-scope controls and module actions. */
        function updateModuleActionControls() {
          var disabled = viewerState.displayScope === DisplayScope.HIDDEN;
          ["kg_modules_collapse_all", "kg_modules_expand_all"].forEach(function(id) {
            var button = document.getElementById(id);
            if (!button) { return; }
            button.disabled = disabled;
            button.title = disabled
              ? "Show the graph before changing module folding"
              : "";
          });
        }

        function updateGraphViewControls() {
          var select = document.getElementById("kg_display_scope_select");
          if (select) {
            select.value = viewerState.displayScope;
            select.title = "Choose how much of the graph is displayed";
          }
          document.body.classList.toggle(
            "kg-graph-hidden",
            viewerState.displayScope === DisplayScope.HIDDEN
          );
          updateModuleActionControls();
          if (network && network.setOptions) {
            network.setOptions({interaction: {
              dragNodes: layoutDraggingEnabled()
            }});
          }
          updateLayoutControls();
        }

        function discardTemporaryLayout() {
          temporaryLayout = {concepts: {}, modules: {}};
          applyGlobalLayoutPositions();
          renderGraphFromViewerState();
          showContextNotice(
            "Temporary layout discarded — Personal layout restored.",
            "temporary-layout-discarded"
          );
        }

        function getConcept(nodeId) {
          return conceptData[String(nodeId)] || null;
        }

        function getModule(moduleId) {
          return moduleData[String(moduleId)] || null;
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

        function moduleHash(moduleId) {
          return "#module-" + encodeURIComponent(String(moduleId));
        }

        function moduleIdFromHash(hash) {
          var prefix = "#module-";
          if (!hash || hash.indexOf(prefix) !== 0) { return null; }
          try {
            return decodeURIComponent(hash.slice(prefix.length));
          } catch (e) {
            return null;
          }
        }

        function pushConceptHistory(nodeId) {
          var hash = conceptHash(nodeId);
          var state = {
            objectType: "concept",
            nodeId: String(nodeId)
          };
          var currentState = window.history.state || {};
          if (
            window.location.hash === hash &&
            currentState.nodeId === state.nodeId
          ) {
            return;
          }
          window.history.pushState(state, "", hash);
        }

        function pushModuleHistory(moduleId) {
          var hash = moduleHash(moduleId);
          var state = {
            objectType: "module",
            moduleId: String(moduleId)
          };
          var currentState = window.history.state || {};
          if (
            window.location.hash === hash &&
            currentState.moduleId === state.moduleId
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

        function compareModules(a, b) {
          var moduleA = getModule(a) || {};
          var moduleB = getModule(b) || {};
          var domainCompare = String(moduleA.domain || "").localeCompare(String(moduleB.domain || ""));
          if (domainCompare !== 0) { return domainCompare; }

          var sequenceA = Number(moduleA.sequence);
          var sequenceB = Number(moduleB.sequence);
          if (Number.isFinite(sequenceA) && Number.isFinite(sequenceB) && sequenceA !== sequenceB) {
            return sequenceA - sequenceB;
          }
          return String(moduleA.title || a).localeCompare(String(moduleB.title || b));
        }

        function moduleDomainLabel(domain) {
          var value = String(domain || "module").toLowerCase();
          return value === "math" ? "MATHS" : value.toUpperCase();
        }

        function moduleIds() {
          return Object.keys(moduleData || {}).sort(compareModules);
        }

        function moduleIdByConcept() {
          if (moduleIdByConceptId !== null) {
            return moduleIdByConceptId;
          }
          moduleIdByConceptId = {};
          moduleIds().forEach(function(moduleId) {
            moduleMemberIds(getModule(moduleId)).forEach(function(conceptId) {
              moduleIdByConceptId[String(conceptId)] = moduleId;
            });
          });
          return moduleIdByConceptId;
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
          result: {label: "Result", mode: "inline"},
          decomposition: {label: "Parts", mode: "inline"},
          convention: {label: "Convention", mode: "folded"},
          derivation: {label: "Derivation", mode: "inline"},
          derivation_step: {label: "Step", mode: "folded"},
          example: {label: "Example", mode: "inline"},
          worked_example: {label: "Worked", mode: "inline"},
          misconception: {label: "Common trap", mode: "folded", note: true},
          warning: {label: "Careful", mode: "folded", note: true},
          historical_note: {label: "Context", mode: "folded", note: true},
          summary: {label: "Takeaway", mode: "inline"}
        });

        var edgeRelationPolicy = Object.freeze({
          DERIVES_FROM: {
            label: "Derived from",
            phrase: "is derived from",
            abbreviation: "DF",
            sortOrder: 10,
            backlinkTitle: "Derived from this",
            derivationTree: true,
            tracePhrase: "derives from"
          },
          REQUIRES: {
            label: "Requires",
            phrase: "requires",
            abbreviation: "RQ",
            sortOrder: 20,
            backlinkTitle: "Requires this"
          },
          CONSTRUCTED_FROM: {
            label: "Constructed from",
            phrase: "is constructed from",
            abbreviation: "CF",
            sortOrder: 30,
            backlinkTitle: "Built from this",
            derivationTree: true,
            tracePhrase: "is constructed from"
          },
          COMPONENT_OF: {
            label: "Component of",
            phrase: "is a component of",
            abbreviation: "CO",
            sortOrder: 40,
            backlinkTitle: "Parts of this"
          },
          INSTANCE_OF: {
            label: "Instance of",
            phrase: "is an instance of",
            abbreviation: "IO",
            sortOrder: 50,
            backlinkTitle: "Has instance"
          },
          RELATED: {
            label: "Related",
            phrase: "is related to",
            abbreviation: "R",
            sortOrder: 90,
            backlinkTitle: "Related concepts"
          }
        });

        var readingModeDefinitions = Object.freeze({
          full: {
            label: "Full",
            blockKinds: null,
            questionTypes: null
          },
          folded: {
            label: "Folded",
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
              result: true,
              decomposition: true,
              derivation: true,
              example: true,
              warning: true,
              convention: true,
              summary: true
            },
            questionTypes: {
              short_answer: true
            }
          },
          maths: {
            label: "Maths",
            blockKinds: {
              construction: true,
              derivation: true,
              derivation_step: true,
              result: true,
              decomposition: true,
              convention: true,
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
              historical_note: true,
              convention: true
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
              result: true,
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

        function openTopLevelDetailIds(panel) {
          if (!panel || panel.getAttribute("data-reading-mode") !== "folded") {
            return [];
          }
          return Array.prototype.map.call(
            panel.querySelectorAll(":scope > details[open][id]"),
            function(section) { return section.id; }
          );
        }

        function applyReadingModeSectionState(panel, openIds) {
          if (!panel) { return; }
          panel.setAttribute("data-reading-mode", readingMode);
          if (readingMode !== "folded") { return; }
          var retained = {};
          (openIds || []).forEach(function(id) { retained[id] = true; });
          panel.querySelectorAll(":scope > details").forEach(function(section) {
            section.open = Boolean(section.id && retained[section.id]);
          });
        }

        function contentBlockPolicyFor(kind) {
          return contentBlockKindPolicy[kind] || {
            label: contentBlockKindLabel(kind),
            mode: "inline"
          };
        }

        function edgeRelationPolicyFor(relation) {
          return edgeRelationPolicy[relation] || {};
        }

        function relationHasDerivationTreeSemantics(relation) {
          return edgeRelationPolicyFor(relation).derivationTree === true;
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
            '"></span></span>' +
            renderContentBlockReadToggle(block.block_id, title);
        }

        function renderContentBlockReadToggle(blockId, title) {
          var checked = contentReadProgressState.blocks[String(blockId || "")] === true;
          return '<input type="checkbox" class="content-block-read-toggle"' +
            ' aria-label="Mark ' + escapeHtml(title) + ' as read"' +
            ' title="Mark as read"' +
            (checked ? " checked" : "") +
            ">";
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
              contentBlockId: block.block_id,
              className: contentBlockClassName(block, policy),
              summaryHtml: renderContentBlockHeading(block, title),
              bodyClass: bodyClass,
              bodyHtml: renderConceptText(block.body)
            });
          }
          var blocks = splitConceptBlocks(block.body);
          var specs = noteAnchorSpecs(block.block_id, "", title, block.body);
          var bodyHtml = "";
          bodyHtml += renderNotesAtAnchor("concept", conceptId, title, 0, "", specs[0]);
          blocks.forEach(function(textBlock, index) {
            bodyHtml += '<div class="concept-line">' +
              (textBlock.text ? renderConceptText(textBlock.text) : "&nbsp;") +
              "</div>";
            bodyHtml += renderNotesAtAnchor(
              "concept",
              conceptId,
              title,
              index + 1,
              textBlock.text.slice(0, 160),
              specs[index + 1]
            );
          });
          return renderFoldDown({
            anchorId: anchorId,
            contentBlockId: block.block_id,
            className: contentBlockClassName(block, policy),
            open: true,
            summaryHtml: renderContentBlockHeading(block, title),
            bodyClass: bodyClass,
            bodyHtml: bodyHtml
          });
        }

        function conceptTocItems(conceptId, concept, studyQuestions, conceptReferences) {
          var items = [];
          if (conceptGraphicSvg(concept)) {
            items.push({
              id: contentAnchorId(conceptId, "Graphic"),
              title: "Graphic"
            });
          }
          if (shouldRenderContentBlocks(concept)) {
            filteredContentBlocks(concept).forEach(function(block) {
              var title = block.title || contentBlockKindLabel(block.kind);
              items.push({
                id: contentAnchorId(conceptId, title),
                title: title,
                kind: block.kind
              });
            });
          } else {
            conceptSections(concept).forEach(function(section) {
              if (!section.text) { return; }
              items.push({
                id: contentAnchorId(conceptId, section.title),
                title: section.title
              });
            });
          }

          if (derivedFromEdgesFor(conceptId).length > 0) {
            items.push({
              id: contentAnchorId(conceptId, "Derived From"),
              title: "Derived from"
            });
          }
          if (backlinkGroupsFor(conceptId).length > 0) {
            items.push({
              id: contentAnchorId(conceptId, "Where This Is Used"),
              title: "Where this is used"
            });
          }
          if (studyQuestions.length > 0) {
            items.push({
              id: contentAnchorId(conceptId, "Study Questions"),
              title: "Study Questions"
            });
          }
          if (conceptReferences.length > 0) {
            items.push({
              id: contentAnchorId(conceptId, "References"),
              title: "References"
            });
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
            html += '<a href="#' + escapeHtml(item.id) +
              '" class="concept-toc-link' + escapeHtml(kindClass) + '" data-toc-target="' +
              escapeHtml(item.id) + '">' +
              (item.kind ? '<span class="concept-toc-kind-dot" aria-hidden="true"></span>' : "") +
              renderConceptText(item.title) +
              "</a>";
          });
          html += "</div></details>";
          return html;
        }

        function renderConceptMasthead(nodeId, concept, tocItems) {
          var conceptTitleText = conceptDisplayId(nodeId) + " " +
            searchDisplayText(concept.label || "");
          var html = '<div class="concept-sticky-header">';
          html += '<div class="concept-title-row">';
          html += '<h2 class="concept-title" title="' + escapeHtml(conceptTitleText) + '">' +
            escapeHtml(conceptDisplayId(nodeId)) + " " + renderConceptText(concept.label) +
            "</h2>";
          html += renderContentReadCompletionIndicator("concept", nodeId);
          var owningModuleId = moduleIdForConcept(nodeId);
          var owningModule = owningModuleId ? getModule(owningModuleId) : null;
          if (owningModule) {
            var owningModuleTitle = searchDisplayText(owningModule.title || owningModuleId);
            var compactModuleMatch = owningModuleTitle.match(/^(?:SR|GR|MATHS)-\d+/);
            var compactModuleTitle = compactModuleMatch
              ? compactModuleMatch[0]
              : owningModuleTitle;
            html += '<button type="button" class="concept-module-chip module-detail-link" data-module-id="' +
              escapeHtml(owningModuleId) + '" aria-label="Module: ' +
              escapeHtml(owningModuleTitle) + '" title="Module: ' +
              escapeHtml(owningModuleTitle) + '">' +
              '<span class="concept-module-chip-label">Module</span> ' +
              '<span class="concept-module-chip-full">' +
              renderConceptText(owningModule.title || owningModuleId) + "</span>" +
              '<span class="concept-module-chip-compact">' +
              escapeHtml(compactModuleTitle) + "</span>" +
              "</button>";
          }
          html += "</div>";
          html += renderConceptToc(tocItems);
          html += "</div>";
          return html;
        }

        function moduleContentBlocks(module) {
          return Array.isArray(module && module.content_blocks)
            ? module.content_blocks
            : [];
        }

        function filteredModuleContentBlocks(module) {
          // Module orientation remains useful even when a concept filter is active.
          return moduleContentBlocks(module).filter(function(block) {
            return block.kind === "overview" || blockVisibleInReadingMode(block);
          });
        }

        function moduleMemberIds(module) {
          return Array.isArray(module && module.members)
            ? module.members.filter(function(id) { return Boolean(getConcept(id)); })
            : [];
        }

        function viewerSelectionSnapshot() {
          if (activeNodeId && getConcept(activeNodeId)) {
            return {type: "concept", id: String(activeNodeId)};
          }
          if (activeModuleId && getModule(activeModuleId)) {
            return {type: "module", id: String(activeModuleId)};
          }
          return {type: "none", id: null};
        }

        function viewerContextSeedIds(selection) {
          selection = selection || viewerSelectionSnapshot();
          if (selection.type === "concept" && getConcept(selection.id)) {
            return [String(selection.id)];
          }
          if (selection.type === "module" && getModule(selection.id)) {
            return moduleMemberIds(getModule(selection.id)).map(String);
          }
          return [];
        }

        function computeViewerContext(selection, rule) {
          var validConceptIds = {};
          Object.keys(conceptData).forEach(function(id) { validConceptIds[String(id)] = true; });
          return computeContextSubgraph(
            viewerContextSeedIds(selection),
            rule || viewerState.contextRule,
            allEdges,
            edgeKey,
            validConceptIds
          );
        }

        window.kgViewerStateSnapshot = function() {
          return {
            selection: viewerSelectionSnapshot(),
            contextRule: createContextRule(
              viewerState.contextRule.preset,
              viewerState.contextRule.depth,
              viewerState.contextRule.customTraversals
            ),
            displayScope: viewerState.displayScope
          };
        };

        window.kgComputeContext = function(selection, rule) {
          return computeViewerContext(selection, createContextRule(
            rule && rule.preset,
            rule && rule.depth,
            rule && rule.customTraversals
          ));
        };

        function moduleIdForConcept(conceptId) {
          return moduleIdByConcept()[String(conceptId)] || null;
        }

        function moduleVisualColor(moduleId) {
          var members = moduleMemberIds(getModule(moduleId));
          for (var i = 0; i < members.length; i++) {
            var node = originalNodes[String(members[i])] || nodes.get(String(members[i]));
            if (node && node.visualColor) {
              return Object.assign({}, node.visualColor);
            }
          }
          return {background: "#e4e7eb", border: "#59636e"};
        }

        /* Module fold state and geometry. */
        function moduleGraphNodeId(moduleId) {
          return "module::" + String(moduleId);
        }

        function moduleIdFromGraphNodeId(nodeId) {
          var prefix = "module::";
          var value = String(nodeId || "");
          return value.indexOf(prefix) === 0 ? value.slice(prefix.length) : null;
        }

        function selectedModuleIsFolded(moduleId) {
          return Boolean(foldedModules[String(moduleId)]);
        }

        function selectedConceptInFoldedModule(moduleId) {
          if (!activeNodeId || !selectedModuleIsFolded(moduleId)) { return null; }
          return moduleIdForConcept(activeNodeId) === String(moduleId)
            ? String(activeNodeId)
            : null;
        }

        function isProjectedModuleEdge(edge) {
          return Boolean(edge && edge.isModuleEdge === true);
        }

        function foldedModuleIdList() {
          return Object.keys(foldedModules).filter(function(moduleId) {
            return Boolean(foldedModules[moduleId]) && Boolean(getModule(moduleId));
          }).sort(compareModules);
        }

        function graphPositionForNode(nodeId) {
          var id = String(nodeId);
          // getPositions rounds coordinates; retain subpixel offsets during folding.
          var liveNode = network && network.body && network.body.nodes[id];
          if (liveNode && validLayoutPosition(liveNode)) {
            return copyLayoutPosition(liveNode);
          }
          var positions = network && network.getPositions
            ? network.getPositions([id])
            : {};
          var pos = positions[id] || nodes.get(id) || originalNodes[id];
          if (!pos || !Number.isFinite(Number(pos.x)) || !Number.isFinite(Number(pos.y))) {
            return null;
          }
          return {x: Number(pos.x), y: Number(pos.y)};
        }

        function moduleMemberGeometry(moduleId) {
          var memberIds = moduleMemberIds(getModule(moduleId));
          var positions = {};
          var count = 0;
          var totalX = 0;
          var totalY = 0;
          memberIds.forEach(function(id) {
            var pos = effectiveConceptPosition(id) || graphPositionForNode(id);
            if (!pos) { return; }
            positions[String(id)] = pos;
            totalX += pos.x;
            totalY += pos.y;
            count += 1;
          });

          var centre = effectiveModuleAnchor(moduleId) || (count > 0
            ? {x: totalX / count, y: totalY / count}
            : {x: 0, y: 0});
          var offsets = {};
          Object.keys(positions).forEach(function(id) {
            offsets[id] = {
              x: positions[id].x - centre.x,
              y: positions[id].y - centre.y
            };
          });
          return {
            position: centre,
            memberOffsets: offsets,
            footprint: moduleFootprint(moduleId)
          };
        }

        function conceptFootprintExtents(conceptId) {
          var node = originalNodes[String(conceptId)] || nodes.get(conceptId) || {};
          var radius = Number(node.visualSize) || Number(node.size) || 100;
          var labelHeight = nodeLabelFontSize * 3.2;
          var labelWidth = nodeLabelWidth;
          var label = nodeLabelEls[String(conceptId)];
          if (label) {
            // Measure a natural-size copy even when the original is hidden or zoomed.
            var probe = label.cloneNode(true);
            probe.removeAttribute("data-node-id");
            probe.classList.remove("kg-node-label-transient");
            probe.style.cssText = "position:absolute;visibility:hidden;display:block;" +
              "left:-100000px;top:0;width:" + nodeLabelWidth + "px;font-size:" +
              nodeLabelFontSize + "px;";
            nodeLabelLayer.appendChild(probe);
            labelHeight = Math.max(labelHeight, probe.getBoundingClientRect().height);
            labelWidth = Math.max(labelWidth, probe.scrollWidth);
            probe.remove();
          }
          return {
            left: Math.max(radius, labelWidth / 2),
            right: Math.max(radius, labelWidth / 2),
            top: radius,
            bottom: radius + 4 + labelHeight
          };
        }

        function moduleFootprint(moduleId) {
          return kgModuleGeometry.footprint(moduleMemberIds(getModule(moduleId)).map(function(id) {
            return {position: effectiveConceptPosition(id), extents: conceptFootprintExtents(id)};
          }), effectiveModuleAnchor(moduleId));
        }

        window.kgModuleFootprint = moduleFootprint;

        function refreshFoldedModuleGeometry(moduleId, preserveTemporary) {
          var oldState = foldedModules[String(moduleId)];
          if (!oldState) { return; }
          var nodeId = moduleGraphNodeId(moduleId);
          var oldNode = nodes.get(nodeId);
          var oldPosition = preserveTemporary && temporaryModuleAnchor(moduleId) && oldNode
            ? graphPositionForNode(nodeId)
            : null;
          var geometry = moduleMemberGeometry(moduleId);
          if (oldPosition) {
            geometry.position = {
              x: oldPosition.x - geometry.footprint.offset.x,
              y: oldPosition.y - geometry.footprint.offset.y
            };
            temporaryLayout.modules[String(moduleId)] = copyLayoutPosition(geometry.position);
          }
          foldedModules[String(moduleId)] = geometry;
          if (oldNode) {
            var node = moduleGraphNode(moduleId);
            node.hidden = oldNode.hidden;
            nodes.update(node);
            network.moveNode(nodeId, node.x, node.y);
          }
        }

        function refreshModuleFootprints() {
          // Geometry changes never move anchors, members or neighbouring modules.
          foldedModuleIdList().forEach(function(moduleId) {
            refreshFoldedModuleGeometry(moduleId, true);
          });
        }

        function foldModule(moduleId) {
          var geometry = moduleMemberGeometry(moduleId);
          foldedModules[String(moduleId)] = geometry;
          if (!globalModuleAnchor(moduleId)) {
            setGlobalModuleAnchor(moduleId, geometry.position);
          }
        }

        function removeFoldedModuleNode(moduleId) {
          var nodeId = moduleGraphNodeId(moduleId);
          if (nodes.get(nodeId)) {
            nodes.remove(nodeId);
          }
        }

        function clearProjectedModuleEdges() {
          if (hoveredEdgeId && String(hoveredEdgeId).indexOf(projectedModuleEdgePrefix) === 0) {
            hoveredEdgeId = null;
            hoveredEdgeBeforeHover = null;
          }
          var moduleEdgeIds = edges.get().filter(isProjectedModuleEdge).map(function(edge) {
            return edge.id;
          });
          if (moduleEdgeIds.length > 0) {
            edges.remove(moduleEdgeIds);
          }
        }

        function syncFoldedModulePosition(moduleId) {
          moduleId = String(moduleId);
          var state = foldedModules[moduleId];
          if (!state) { return null; }
          var graphNodePosition = graphPositionForNode(moduleGraphNodeId(moduleId));
          if (graphNodePosition) {
            var offset = state.footprint.offset;
            state.position = {x: graphNodePosition.x - offset.x, y: graphNodePosition.y - offset.y};
          }
          return state.position || null;
        }

        function restoreFoldedModuleMembers(moduleId) {
          if (!persistentLayoutEditingEnabled() && !temporaryLayoutEditingEnabled()) { return; }
          moduleId = String(moduleId);
          var state = foldedModules[moduleId];
          if (!state || !state.position || !state.memberOffsets) { return; }
          syncFoldedModulePosition(moduleId);
          if (temporaryLayoutEditingEnabled()) {
            temporaryLayout.modules[moduleId] = copyLayoutPosition(state.position);
          } else {
            setGlobalModuleAnchor(moduleId, state.position);
          }
          var updates = [];
          moduleMemberIds(getModule(moduleId)).forEach(function(id) {
            var offset = state.memberOffsets[String(id)] || {x: 0, y: 0};
            var position = {
              x: state.position.x + offset.x,
              y: state.position.y + offset.y
            };
            if (temporaryLayoutEditingEnabled()) {
              temporaryLayout.concepts[String(id)] = copyLayoutPosition(position);
            } else {
              setGlobalConceptPosition(id, position);
            }
            if (nodes.get(id)) {
              updates.push({id: id, x: position.x, y: position.y});
            }
          });
          if (updates.length > 0) {
            nodes.update(updates);
          }
        }

        function unfoldModule(moduleId, options) {
          options = options || {};
          moduleId = String(moduleId);
          if (!selectedModuleIsFolded(moduleId)) { return; }
          if (options.restoreMembers !== false) {
            restoreFoldedModuleMembers(moduleId);
          }
          delete foldedModules[moduleId];
          removeFoldedModuleNode(moduleId);
        }

        function moduleGraphNodePosition(moduleId) {
          var state = foldedModules[String(moduleId)];
          if (!state) { return moduleFootprint(moduleId); }
          return {
            x: state.position.x + state.footprint.offset.x,
            y: state.position.y + state.footprint.offset.y
          };
        }

        function fittedModuleLabel(title, memberCount, width, height, options) {
          options = options || {};
          var context = document.createElement("canvas").getContext("2d");
          var countLabel = memberCount + " concept" + (memberCount === 1 ? "" : "s");
          var countFontSize = options.countFontSize || 80;
          var lineWidth = width * (options.lineWidthFraction || 0.88);
          function linesAt(size) {
            context.font = "bold " + size + "px Arial";
            var lines = [], line = "";
            String(title).split(/\s+/).forEach(function(word) {
              var candidate = line ? line + " " + word : word;
              if (context.measureText(candidate).width <= lineWidth) {
                line = candidate;
              } else {
                if (line) { lines.push(line); }
                line = word;
              }
            });
            if (line) { lines.push(line); }
            return lines;
          }
          // Cap titles in graph-space units: extra box area need not enlarge text.
          var low = 1, high = Math.min(options.titleFontCap || 160, Math.min(width, height) * 0.3);
          for (var i = 0; i < 16; i += 1) {
            var size = (low + high) / 2;
            var lines = linesAt(size);
            var titleFits = lines.every(function(line) {
              return context.measureText(line).width <= lineWidth;
            });
            context.font = countFontSize + "px Arial";
            var labelHeight = options.availableHeight || height * 0.84;
            var lineHeightFactor = options.lineHeightFactor || 1.25;
            if ((lines.length * size + countFontSize) * lineHeightFactor <= labelHeight && titleFits &&
                context.measureText(countLabel).width <= width * 0.88) {
              low = size;
            } else { high = size; }
          }
          var titleLines = linesAt(low);
          var verticalShift = Number(options.verticalShift) || 0;
          return {
            text: titleLines.map(function(line) {
              return "<b>" + escapeHtml(line) + "</b>";
            }).join("\n") + "\n" + countLabel,
            size: low,
            countSize: countFontSize,
            // vis centres the first baseline using the base (count) font size,
            // even for larger bold title lines. Correct each style's baseline
            // so the combined title/count block is centred inside its box.
            titleOffset: (titleLines.length - 1) * (countFontSize - low) / 2 + verticalShift,
            countOffset: titleLines.length * (countFontSize - low) / 2 + verticalShift
          };
        }

        function moduleGraphicLayout(width, height) {
          var pad = Math.max(18, Math.min(width, height) * 0.055);
          var availableWidth = Math.max(1, width - 2 * pad);
          var availableHeight = Math.max(1, height * 0.62 - 2 * pad);
          var graphicWidth = Math.min(availableWidth, availableHeight * 1.6);
          var graphicHeight = graphicWidth / 1.6;
          var graphicX = (width - graphicWidth) / 2;
          var graphicY = pad;
          var labelTop = graphicY + graphicHeight + pad * 0.55;
          var labelBottom = height - pad * 0.6;
          return {
            graphic: {x: graphicX, y: graphicY, width: graphicWidth, height: graphicHeight},
            labelArea: {
              top: labelTop - height / 2,
              bottom: labelBottom - height / 2,
              height: Math.max(1, labelBottom - labelTop)
            },
            labelCenter: (labelTop + labelBottom) / 2 - height / 2
          };
        }
        window.kgModuleGraphicLayout = moduleGraphicLayout;

        function foldedModuleConceptProxy(moduleId) {
          moduleId = String(moduleId);
          var conceptId = selectedConceptInFoldedModule(moduleId);
          var graphNodeId = moduleGraphNodeId(moduleId);
          var graphNode = nodes.get(graphNodeId);
          var rendered = network && network.body && network.body.nodes[graphNodeId];
          var conceptNode = conceptId ? nodes.get(conceptId) : null;
          if (!conceptId || !graphNode || graphNode.hidden || !rendered || !conceptNode) {
            return null;
          }
          var shape = rendered.shape;
          if (!shape) { return null; }
          var layout = moduleGraphicLayout(shape.width, shape.height);
          var baseRadius = Number(conceptNode.visualSize) || Number(conceptNode.size) || 18;
          var radius = baseRadius * activeNodeRadiusScale;
          return {
            conceptId: conceptId,
            moduleId: moduleId,
            x: shape.left + shape.width / 2,
            y: shape.top + layout.graphic.y + radius,
            radius: radius,
            borderWidth: activeNodeBorderWidth,
            moduleGraphicSuppressed: true,
            graphic: layout.graphic
          };
        }

        function foldedModuleConceptProxyForConcept(conceptId) {
          conceptId = String(conceptId);
          if (conceptId !== String(activeNodeId || "")) { return null; }
          var moduleId = moduleIdForConcept(conceptId);
          return moduleId ? foldedModuleConceptProxy(moduleId) : null;
        }

        window.kgFoldedModuleConceptProxy = foldedModuleConceptProxy;

        function moduleCornerRadius(width, height) {
          return Math.min(width, height) * 0.18;
        }

        function moduleGraphicCornerRadius(width, height, layout) {
          layout = layout || moduleGraphicLayout(width, height);
          var outerRadius = moduleCornerRadius(width, height);
          // Inset a rounded module boundary rather than introducing an
          // unrelated second curve. Averaging the unequal landscape insets
          // keeps the two corner arcs visually close to concentric.
          var inset = (layout.graphic.x + layout.graphic.y) / 2;
          return Math.max(
            0,
            Math.min(
              outerRadius - inset,
              layout.graphic.width / 2,
              layout.graphic.height / 2
            )
          );
        }
        window.kgModuleGraphicCornerRadius = moduleGraphicCornerRadius;

        function moduleGraphNode(moduleId) {
          var module = getModule(moduleId) || {};
          var memberCount = moduleMemberIds(module).length;
          var position = moduleGraphNodePosition(moduleId);
          var footprint = foldedModules[String(moduleId)].footprint;
          var hasGraphic = Boolean(module.svg_icon);
          var selectedConceptProxyId = selectedConceptInFoldedModule(moduleId);
          var usesGraphicLayout = hasGraphic || Boolean(selectedConceptProxyId);
          var graphicLayout = usesGraphicLayout
            ? moduleGraphicLayout(footprint.width, footprint.height)
            : null;
          var fittedLabel = fittedModuleLabel(
            module.title || moduleId,
            memberCount,
            footprint.width,
            footprint.height,
            usesGraphicLayout ? {
              countFontSize: 52,
              titleFontCap: 128,
              verticalShift: graphicLayout.labelCenter,
              availableHeight: graphicLayout.labelArea.height * 0.94,
              lineWidthFraction: 0.72,
              lineHeightFactor: 1.06
            } : {}
          );
          var visualColor = moduleVisualColor(moduleId);
          return {
            id: moduleGraphNodeId(moduleId),
            isModuleNode: true,
            moduleId: String(moduleId),
            hasModuleGraphic: hasGraphic,
            selectedConceptProxyId: selectedConceptProxyId || "",
            // Keep the custom metadata type stable across DataSet updates;
            // vis-network cannot merge a nested object over a previous null.
            moduleGraphicLabelArea: graphicLayout
              ? graphicLayout.labelArea
              : {top: 0, bottom: 0, height: 0},
            moduleGraphicLabelCenter: graphicLayout ? graphicLayout.labelCenter : 0,
            label: fittedLabel.text,
            moduleFootprintWidth: footprint.width,
            moduleFootprintHeight: footprint.height,
            chosen: {label: false},
            // A small secondary count must not trigger vis's whole-label fade-out.
            scaling: {label: {drawThreshold: 0}},
            shape: "box",
            shapeProperties: {
              borderRadius: moduleCornerRadius(footprint.width, footprint.height)
            },
            x: position.x,
            y: position.y,
            physics: false,
            hidden: false,
            margin: {top: 0, right: 0, bottom: 0, left: 0},
            widthConstraint: {minimum: footprint.width, maximum: footprint.width},
            heightConstraint: {minimum: footprint.height, valign: "middle"},
            borderWidth: 2,
            // A selected module keeps the strong outer outline. When this
            // module merely represents a selected contained concept, the
            // concept face carries the selection outline instead.
            borderWidthSelected: selectedConceptProxyId ? 2 : 6,
            color: {
              background: visualColor.background,
              border: visualColor.border,
              highlight: {
                background: visualColor.background,
                border: visualColor.border
              },
              hover: {
                background: visualColor.background,
                border: visualColor.border
              }
            },
            font: {
              color: "#111827",
              size: fittedLabel.countSize,
              vadjust: fittedLabel.countOffset,
              face: "Arial",
              multi: "html",
              bold: {
                color: "#111827",
                size: fittedLabel.size,
                vadjust: fittedLabel.titleOffset,
                face: "Arial"
              }
            }
          };
        }

        function moduleGraphicImage(moduleId) {
          var module = getModule(moduleId) || {};
          return module.svg_icon
            ? getSvgNodeImage(moduleGraphNodeId(moduleId) + "::graphic", module.svg_icon)
            : null;
        }
        window.kgModuleGraphicImage = moduleGraphicImage;

        function roundedRectPath(ctx, x, y, width, height, radius) {
          radius = Math.min(radius, width / 2, height / 2);
          ctx.beginPath();
          ctx.moveTo(x + radius, y);
          ctx.lineTo(x + width - radius, y);
          ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
          ctx.lineTo(x + width, y + height - radius);
          ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
          ctx.lineTo(x + radius, y + height);
          ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
          ctx.lineTo(x, y + radius);
          ctx.quadraticCurveTo(x, y, x + radius, y);
          ctx.closePath();
        }

        function drawFoldedModuleGraphics(ctx) {
          foldedModuleIdList().forEach(function(moduleId) {
            var nodeId = moduleGraphNodeId(moduleId);
            var node = nodes.get(nodeId);
            var rendered = network.body.nodes[nodeId];
            var proxy = foldedModuleConceptProxy(moduleId);
            if (proxy) {
              drawConceptFace(
                ctx,
                nodes.get(proxy.conceptId),
                {x: proxy.x, y: proxy.y},
                {active: true, radius: proxy.radius}
              );
              return;
            }
            var image = moduleGraphicImage(moduleId);
            if (!node || node.hidden || !node.hasModuleGraphic || !rendered ||
                !image || !image.complete || image.naturalWidth <= 0) { return; }
            var shape = rendered.shape;
            var layout = moduleGraphicLayout(shape.width, shape.height);
            var width = layout.graphic.width;
            var height = layout.graphic.height;
            var x = shape.left + layout.graphic.x;
            var y = shape.top + layout.graphic.y;
            var radius = moduleGraphicCornerRadius(shape.width, shape.height, layout);
            ctx.save();
            roundedRectPath(ctx, x, y, width, height, radius);
            ctx.clip();
            ctx.fillStyle = "#fbfcff";
            ctx.fillRect(x, y, width, height);
            ctx.drawImage(image, x, y, width, height);
            ctx.restore();
            ctx.save();
            roundedRectPath(ctx, x, y, width, height, radius);
            ctx.lineWidth = Math.max(2, Math.min(shape.width, shape.height) * 0.006);
            ctx.strokeStyle = (node.color || {}).border || "#64748b";
            ctx.stroke();
            ctx.restore();
          });
        }

        /* Projected boundary edges shown when module members are folded away. */
        function projectedModuleEndpointForConcept(conceptId, hiddenMembers) {
          conceptId = String(conceptId);
          if (hiddenMembers[conceptId]) {
            var owningModuleId = moduleIdForConcept(conceptId);
            var graphNodeId = owningModuleId ? moduleGraphNodeId(owningModuleId) : null;
            var graphNode = graphNodeId ? nodes.get(graphNodeId) : null;
            return graphNode && !graphNode.hidden ? graphNodeId : null;
          }
          return visibleGraphNode(conceptId) ? conceptId : null;
        }

        function moduleEdgeLabelForRelations(relations, relationCounts) {
          return relations.map(function(relation) {
            return relation + " " + String(relationCounts[relation] || 0);
          }).join("\n");
        }

        function moduleEdgeColourForRelations(relations) {
          return relations.length === 1 ? relationColour(relations[0]) : "#4b5563";
        }

        function projectedModuleEdgeFromGroup(group) {
          var relations = Object.keys(group.relationCounts).sort(compareRelations);
          var contextEdge = group.contextEdge === true;
          var overviewEdge = group.overviewEdge === true;
          var colour = contextEdge || overviewEdge
            ? moduleEdgeColourForRelations(relations)
            : "#9ca3af";
          var directed = relations.some(function(relation) {
            return relationIsDirected(relation);
          });
          return {
            id: group.id,
            isModuleEdge: true,
            from: group.from,
            to: group.to,
            relation: relations.length === 1 ? relations[0] : "MODULE_BOUNDARY",
            relationCounts: group.relationCounts,
            edgeIds: group.edgeIds,
            kgContextEdge: contextEdge,
            arrows: directed ? "to" : "",
            title: "",
            kgHoverable: true,
            hidden: false,
            label: moduleEdgeLabelForRelations(relations, group.relationCounts),
            color: {
              color: colour,
              highlight: colour,
              hover: colour,
              opacity: contextEdge
                ? (relations.length === 1 ? 0.95 : 0.85)
                : overviewEdge ? (relations.length === 1 ? 0.78 : 0.68) : 0.30
            },
            dashes: relations.length > 1,
            width: contextEdge
              ? Math.min(6, 2.6 + Math.max(0, group.edgeIds.length - 1) * 0.5)
              : overviewEdge
                ? Math.min(3.5, 1.5 + Math.max(0, group.edgeIds.length - 1) * 0.3)
                : Math.min(3, 1.2 + Math.max(0, group.edgeIds.length - 1) * 0.25),
            kgBaseWidth: contextEdge
              ? Math.min(6, 2.6 + Math.max(0, group.edgeIds.length - 1) * 0.5)
              : overviewEdge
                ? Math.min(3.5, 1.5 + Math.max(0, group.edgeIds.length - 1) * 0.3)
                : Math.min(3, 1.2 + Math.max(0, group.edgeIds.length - 1) * 0.25),
            font: {
              color: "#334155",
              size: 16,
              face: "Arial",
              strokeWidth: 3,
              strokeColor: "#ffffff"
            }
          };
        }

        function projectedModuleEdges(hiddenMembers) {
          var groups = {};
          // These edges summarize visible graph boundaries only; allEdges remains the authored KB.
          allEdges.forEach(function(edge) {
            var current = edges.get(edge.id) || originalEdges[edge.id] || edge;
            if (!current || current.hidden) { return; }
            if (!hiddenMembers[String(edge.from)] && !hiddenMembers[String(edge.to)]) { return; }

            var from = projectedModuleEndpointForConcept(edge.from, hiddenMembers);
            var to = projectedModuleEndpointForConcept(edge.to, hiddenMembers);
            if (!from || !to || from === to) { return; }

            var id = projectedModuleEdgePrefix + from + "::" + to;
            if (!groups[id]) {
              groups[id] = {
                id: id,
                from: from,
                to: to,
                relationCounts: {},
                edgeIds: [],
                contextEdge: false,
                overviewEdge: false
              };
            }
            var relation = edgeRelation(edge);
            groups[id].relationCounts[relation] = (groups[id].relationCounts[relation] || 0) + 1;
            groups[id].edgeIds.push(edge.id);
            groups[id].contextEdge = groups[id].contextEdge || current.kgContextEdge === true;
            groups[id].overviewEdge = groups[id].overviewEdge || current.kgOverviewEdge === true;
          });
          return Object.keys(groups).sort().map(function(id) {
            groups[id].edgeIds.sort();
            return projectedModuleEdgeFromGroup(groups[id]);
          });
        }

        /* Module fold actions. */
        function setSelectedModuleFoldState(moduleId, folded) {
          if (!getModule(moduleId)) { return; }
          resetContextFitInteraction();
          moduleId = String(moduleId);
          preferredFoldedModules[moduleId] = Boolean(folded);
          if (folded) {
            foldModule(moduleId);
          } else {
            unfoldModule(moduleId);
          }

          renderGraphFromViewerState({fit: false});
          if (activeModuleId === moduleId) {
            showModule(moduleId, {preserveSectionContext: true});
          }
          updateGraphContextControls();
          document.getElementById("kg_status").innerText =
            (folded ? "Folded " : "Expanded ") +
            (getModule(moduleId).title || moduleId) + " module in the graph.";
        }

        function moduleIdsWithMembers() {
          return moduleIds().filter(function(moduleId) {
            return moduleMemberIds(getModule(moduleId)).length > 0;
          });
        }

        function applyDefaultModuleFoldState() {
          moduleIdsWithMembers().forEach(function(moduleId) {
            var module = getModule(moduleId);
            var folded = Boolean(module && module.default_collapsed);
            preferredFoldedModules[String(moduleId)] = folded;
            if (folded) {
              foldModule(moduleId);
            }
          });
        }

        function refreshGraphAfterModuleFoldChange() {
          renderGraphFromViewerState({fit: false});
          updateGraphContextControls();
        }

        function foldAllModules() {
          resetContextFitInteraction();
          var ids = moduleIdsWithMembers();
          ids.forEach(function(moduleId) {
            preferredFoldedModules[String(moduleId)] = true;
            if (selectedModuleIsFolded(moduleId)) {
              syncFoldedModulePosition(moduleId);
            } else {
              foldModule(moduleId);
            }
          });
          refreshGraphAfterModuleFoldChange();
          if (activeModuleId && getModule(activeModuleId)) {
            showModule(activeModuleId, {preserveSectionContext: true});
          }
          document.getElementById("kg_status").innerText =
            "Collapsed " + String(ids.length) + " module" + (ids.length === 1 ? "" : "s") +
            " in the graph.";
        }

        function unfoldAllModules() {
          resetContextFitInteraction();
          var ids = moduleIdsWithMembers();
          ids.forEach(function(moduleId) {
            preferredFoldedModules[String(moduleId)] = false;
            unfoldModule(moduleId);
          });
          refreshGraphAfterModuleFoldChange();
          if (activeModuleId && getModule(activeModuleId)) {
            showModule(activeModuleId, {preserveSectionContext: true});
          }
          document.getElementById("kg_status").innerText =
            "Expanded " + String(ids.length) + " module" + (ids.length === 1 ? "" : "s") +
            " in the graph.";
        }

        function toggleModuleFoldForGraphNode(nodeId) {
          nodeId = String(nodeId || "");
          var moduleId = moduleIdFromGraphNodeId(nodeId);
          if (moduleId && selectedModuleIsFolded(moduleId)) {
            setSelectedModuleFoldState(moduleId, false);
            return true;
          }
          if (!getConcept(nodeId)) { return false; }
          var owningModuleId = moduleIdForConcept(nodeId);
          if (!owningModuleId || selectedModuleIsFolded(owningModuleId)) { return false; }
          setSelectedModuleFoldState(owningModuleId, true);
          return true;
        }

        function expandedModuleAtCanvasPoint(point) {
          if (!point || !Number.isFinite(point.x) || !Number.isFinite(point.y)) {
            return null;
          }
          var matches = moduleIdsWithMembers().filter(function(moduleId) {
            if (selectedModuleIsFolded(moduleId)) { return false; }
            var hasVisibleMember = moduleMemberIds(getModule(moduleId)).some(function(conceptId) {
              var node = nodes.get(conceptId);
              return node && !node.hidden;
            });
            if (!hasVisibleMember) { return false; }
            var bounds = moduleFootprint(moduleId);
            return point.x >= bounds.left && point.x <= bounds.right &&
              point.y >= bounds.top && point.y <= bounds.bottom;
          });
          return matches.length === 1 ? matches[0] : null;
        }

        function collapseExpandedModuleAtDomPoint(point) {
          if (!network.DOMtoCanvas) { return false; }
          var moduleId = expandedModuleAtCanvasPoint(network.DOMtoCanvas(point));
          if (!moduleId) { return false; }
          setSelectedModuleFoldState(moduleId, true);
          return true;
        }

        /*
         * Real double-clicks can fire a normal click first. That click may refit
         * the graph and move the target before the browser dblclick arrives, so
         * keep a short-lived recent-node fallback alongside vis-network events.
         */
        function handleGraphNodeDoubleClick(nodeId) {
          cancelPendingContainedConceptModuleSelection();
          if (toggleModuleFoldForGraphNode(nodeId)) {
            suppressedNativeDoubleClick = {
              nodeId: String(nodeId || ""),
              until: Date.now() + 500
            };
            return true;
          }
          return false;
        }

        function cancelPendingContainedConceptModuleSelection() {
          if (!pendingContainedConceptModuleSelection) { return; }
          clearTimeout(pendingContainedConceptModuleSelection.timerId);
          pendingContainedConceptModuleSelection = null;
        }

        function deferModuleSelectionForContainedConcept(moduleId) {
          moduleId = String(moduleId || "");
          if (
            !activeNodeId ||
            moduleIdForConcept(activeNodeId) !== moduleId ||
            !selectedModuleIsFolded(moduleId)
          ) {
            return false;
          }
          pendingContainedConceptModuleSelection = {
            moduleId: moduleId,
            timerId: setTimeout(function() {
              pendingContainedConceptModuleSelection = null;
              focusModule(moduleId, "Selected");
            }, 500)
          };
          return true;
        }

        function graphNodeClickIsDoubleClick(nodeId) {
          var now = Date.now();
          nodeId = String(nodeId || "");
          var isDouble = Boolean(
            lastGraphNodeClick &&
            lastGraphNodeClick.nodeId === nodeId &&
            now - lastGraphNodeClick.time <= 420
          );
          lastGraphNodeClick = {
            nodeId: nodeId,
            time: now
          };
          return isDouble;
        }

        function nativeDoubleClickIsSuppressed(nodeId) {
          return Boolean(
            suppressedNativeDoubleClick &&
            suppressedNativeDoubleClick.nodeId === String(nodeId || "") &&
            Date.now() <= suppressedNativeDoubleClick.until
          );
        }

        function recentGraphClickNodeId(maxAgeMs) {
          if (!lastGraphNodeClick || Date.now() - lastGraphNodeClick.time > maxAgeMs) {
            return null;
          }
          return lastGraphNodeClick.nodeId;
        }

        function renderModuleGraphFoldControl(moduleId) {
          var folded = selectedModuleIsFolded(moduleId);
          return '<div class="module-graph-fold-control" aria-label="Module graph display">' +
            '<span class="module-graph-fold-label">Graph</span>' +
            '<button type="button" class="module-graph-fold-button" data-module-id="' +
            escapeHtml(moduleId) + '" data-module-fold-state="expanded" aria-pressed="' +
            (folded ? "false" : "true") + '">Expanded</button>' +
            '<button type="button" class="module-graph-fold-button" data-module-id="' +
            escapeHtml(moduleId) + '" data-module-fold-state="folded" aria-pressed="' +
            (folded ? "true" : "false") + '">Folded</button>' +
            "</div>";
        }

        function moduleTitleButton(moduleId) {
          var module = getModule(moduleId);
          if (!module) { return escapeHtml(moduleId); }
          return '<button type="button" class="module-detail-link module-boundary-module-link" data-module-id="' +
            escapeHtml(moduleId) + '">' + renderConceptText(module.title || moduleId) + "</button>";
        }

        function moduleBoundaryGroups(moduleId, direction) {
          var groups = {};
          allEdges.forEach(function(edge) {
            var sourceModuleId = moduleIdForConcept(edge.from);
            var targetModuleId = moduleIdForConcept(edge.to);
            if (!sourceModuleId || !targetModuleId || sourceModuleId === targetModuleId) {
              return;
            }

            var otherModuleId = null;
            if (direction === "incoming" && targetModuleId === moduleId) {
              otherModuleId = sourceModuleId;
            } else if (direction === "outgoing" && sourceModuleId === moduleId) {
              otherModuleId = targetModuleId;
            } else {
              return;
            }

            if (!groups[otherModuleId]) {
              groups[otherModuleId] = {
                moduleId: otherModuleId,
                relationCounts: {},
                edges: []
              };
            }
            var relation = edgeRelation(edge);
            groups[otherModuleId].relationCounts[relation] =
              (groups[otherModuleId].relationCounts[relation] || 0) + 1;
            groups[otherModuleId].edges.push(edge);
          });

          return Object.keys(groups).map(function(otherModuleId) {
            var group = groups[otherModuleId];
            group.edges.sort(function(a, b) {
              return compareRelations(edgeRelation(a), edgeRelation(b)) ||
                compareConceptIds(String(a.from), String(b.from)) ||
                compareConceptIds(String(a.to), String(b.to));
            });
            return group;
          }).sort(function(a, b) {
            return b.edges.length - a.edges.length ||
              compareModules(a.moduleId, b.moduleId);
          });
        }

        function moduleBoundaryCountHtml(relationCounts) {
          return Object.keys(relationCounts).sort(compareRelations).map(function(relation) {
            return '<span class="module-boundary-relation-count" style="--edge-color:' +
              escapeHtml(relationColour(relation)) + '">' +
              escapeHtml(relation) + " " + relationCounts[relation] +
              "</span>";
          }).join("");
        }

        function renderModuleBoundarySection(moduleId, direction, title) {
          var groups = moduleBoundaryGroups(moduleId, direction);
          if (groups.length === 0) { return ""; }

          var anchorId = contentAnchorId(moduleId, title);
          var html = '<details id="' + escapeHtml(anchorId) +
            '" class="module-boundary module-boundary-' + escapeHtml(direction) + '" open>';
          html += "<summary>" + escapeHtml(title) + "</summary>";
          html += '<div class="module-boundary-groups">';
          groups.forEach(function(group) {
            html += '<details class="module-boundary-pair" open>';
            html += '<summary><span class="module-boundary-module">' +
              moduleTitleButton(group.moduleId) +
              '</span><span class="module-boundary-counts">' +
              moduleBoundaryCountHtml(group.relationCounts) +
              "</span></summary>";
            html += '<ol class="module-boundary-edge-list">';
            group.edges.forEach(function(edge) {
              html += '<li class="module-boundary-edge">';
              html += relationshipStatementHtml(edge);
              if (edge.note) {
                html += '<div class="module-boundary-note">' +
                  renderConceptText(edge.note) + "</div>";
              }
              html += "</li>";
            });
            html += "</ol></details>";
          });
          html += "</div></details>";
          return html;
        }

        function renderModuleContentBlock(moduleId, block) {
          var title = block.title || contentBlockKindLabel(block.kind);
          var policy = contentBlockPolicyFor(block.kind);
          var anchorId = contentAnchorId(moduleId, title);
          var bodyClass = "concept-body content-block-body";
          var specs = noteAnchorSpecs(block.block_id, "", title, block.body);
          var bodyHtml = renderNotesAtAnchor("module", moduleId, title, 0, "", specs[0]);
          splitConceptBlocks(block.body).forEach(function(textBlock, index) {
            bodyHtml += '<div class="concept-line">' +
              (textBlock.text ? renderConceptText(textBlock.text) : "&nbsp;") +
              "</div>";
            bodyHtml += renderNotesAtAnchor(
              "module",
              moduleId,
              title,
              index + 1,
              String(textBlock.text || "").slice(0, 160),
              specs[index + 1]
            );
          });
          if (policy.mode === "folded") {
            bodyClass = "concept-body content-block-fold-body";
            if (policy.note) {
              bodyClass += " content-block-note-body";
            }
            return renderFoldDown({
              anchorId: anchorId,
              contentBlockId: block.block_id,
              className: contentBlockClassName(block, policy) + " module-content-block",
              summaryHtml: renderContentBlockHeading(block, title),
              bodyClass: bodyClass,
              bodyHtml: bodyHtml
            });
          }

          return renderFoldDown({
            anchorId: anchorId,
            contentBlockId: block.block_id,
            className: contentBlockClassName(block, policy) + " module-content-block",
            open: true,
            summaryHtml: renderContentBlockHeading(block, title),
            bodyClass: bodyClass,
            bodyHtml: bodyHtml
          });
        }

        function moduleTocItems(moduleId, module) {
          var items = [];
          if (module.svg_detail || module.svg_icon) {
            items.push({
              id: contentAnchorId(moduleId, "Graphic"),
              title: "Module graphic"
            });
          }
          filteredModuleContentBlocks(module).forEach(function(block) {
            var title = block.title || contentBlockKindLabel(block.kind);
            items.push({
              id: contentAnchorId(moduleId, title),
              title: title,
              kind: block.kind
            });
          });
          if (moduleMemberIds(module).length > 0) {
            items.push({
              id: contentAnchorId(moduleId, "Concepts"),
              title: "Concepts"
            });
          }
          if (moduleBoundaryGroups(moduleId, "incoming").length > 0) {
            items.push({
              id: contentAnchorId(moduleId, "Incoming Boundary Links"),
              title: "Incoming boundary links"
            });
          }
          if (moduleBoundaryGroups(moduleId, "outgoing").length > 0) {
            items.push({
              id: contentAnchorId(moduleId, "Outgoing Boundary Links"),
              title: "Outgoing boundary links"
            });
          }
          if (Array.isArray(module.supports) && module.supports.length > 0) {
            items.push({
              id: contentAnchorId(moduleId, "Declared Supports"),
              title: "Declared supports"
            });
          }
          return items;
        }

        function renderModuleMasthead(moduleId, module, tocItems) {
          var html = '<div class="concept-sticky-header module-sticky-header">';
          html += '<div class="concept-title-row">';
          html += '<h2 class="concept-title module-title">' + renderConceptText(module.title || moduleId) + "</h2>";
          html += renderContentReadCompletionIndicator("module", moduleId);
          html += '<span class="module-domain-label">' +
            escapeHtml(moduleDomainLabel(module.domain)) +
            "</span>";
          html += renderModuleGraphFoldControl(moduleId);
          html += "</div>";
          html += renderConceptToc(tocItems);
          html += "</div>";
          return html;
        }

        function renderModuleMembers(moduleId, module) {
          var members = moduleMemberIds(module);
          if (members.length === 0) { return ""; }
          var html = '<details id="' + escapeHtml(contentAnchorId(moduleId, "Concepts")) +
            '" class="module-members" open>';
          html += "<summary>Concepts</summary>";
          html += '<ul class="module-member-list">';
          members.forEach(function(conceptId) {
            html += '<li><button type="button" class="edge-detail-concept module-member-concept" data-edge-concept-id="' +
              escapeHtml(conceptId) + '">' +
              escapeHtml(conceptDisplayId(conceptId)) + " " +
              renderConceptText((getConcept(conceptId) || {}).label || conceptId) +
              "</button></li>";
          });
          html += "</ul></details>";
          return html;
        }

        function renderModuleSupportTarget(support) {
          var targetType = String(support.target_type || "");
          var targetId = String(support.target_id || "");
          if (targetType === "concept" && getConcept(targetId)) {
            return '<button type="button" class="edge-detail-concept module-support-target" data-edge-concept-id="' +
              escapeHtml(targetId) + '">' +
              escapeHtml(conceptDisplayId(targetId)) + " " +
              renderConceptText((getConcept(targetId) || {}).label || targetId) +
              "</button>";
          }
          if (targetType === "module" && getModule(targetId)) {
            return '<button type="button" class="module-detail-link module-support-target" data-module-id="' +
              escapeHtml(targetId) + '">' +
              renderConceptText((getModule(targetId) || {}).title || targetId) +
              "</button>";
          }
          return escapeHtml(targetId);
        }

        function renderModuleSupports(moduleId, module) {
          var supports = Array.isArray(module.supports) ? module.supports : [];
          if (supports.length === 0) { return ""; }
          var html = '<details id="' + escapeHtml(contentAnchorId(moduleId, "Declared Supports")) +
            '" class="module-supports">';
          html += "<summary>Declared supports</summary>";
          html += '<ul class="module-support-list">';
          supports.forEach(function(support) {
            html += '<li><strong>' + escapeHtml(support.role || "support") + ":</strong> " +
              renderModuleSupportTarget(support);
            if (support.note) {
              html += '<div class="module-support-note">' + renderConceptText(support.note) + "</div>";
            }
            html += "</li>";
          });
          html += "</ul></details>";
          return html;
        }

        function renderModuleGraphic(moduleId, module) {
          var svgDetail = module.svg_detail || module.svg_icon || "";
          if (!svgDetail) { return ""; }
          var caption = module.svg_detail_caption || module.svg_icon_caption || "";
          var bodyHtml = '<div class="concept-graphic module-graphic">' + svgDetail + "</div>";
          if (caption) {
            bodyHtml += '<figcaption class="concept-graphic-caption module-graphic-caption">' +
              renderCaptionText(caption) + "</figcaption>";
          }
          bodyHtml += renderNotesAtAnchor(
            "module", moduleId, "Graphic", 0, caption,
            noteAnchorSpecs("", "graphic", "Graphic", "")[0]
          );
          return renderFoldDown({
            anchorId: contentAnchorId(moduleId, "Graphic"),
            className: "concept-figure module-figure",
            open: true,
            title: "Module graphic",
            bodyTag: "figure",
            bodyClass: "concept-figure-body module-figure-body",
            bodyHtml: bodyHtml
          });
        }

        function showModule(moduleId, options) {
          options = options || {};
          hideConceptPreview(true);
          var module = getModule(moduleId);
          if (!module) { return; }
          var panel = document.getElementById("info_panel");
          var retainedOpenSections = openTopLevelDetailIds(panel);
          var tocItems = moduleTocItems(moduleId, module);
          currentConceptTocItems = tocItems.slice();

          var html = renderModuleMasthead(moduleId, module, tocItems);
          html += renderModuleGraphic(moduleId, module);
          filteredModuleContentBlocks(module).forEach(function(block) {
            html += renderModuleContentBlock(moduleId, block);
          });
          html += renderModuleMembers(moduleId, module);
          html += renderModuleBoundarySection(moduleId, "incoming", "Incoming boundary links");
          html += renderModuleBoundarySection(moduleId, "outgoing", "Outgoing boundary links");
          html += renderModuleSupports(moduleId, module);
          html += renderUnmatchedNotes("module", moduleId);

          var previousModuleId = panel.getAttribute("data-module-id") || "";
          var moduleChanged = previousModuleId !== String(moduleId);
          panel.innerHTML = html;
          applyReadingModeSectionState(
            panel,
            moduleChanged ? [] : retainedOpenSections
          );
          panel.removeAttribute("data-concept-id");
          panel.setAttribute("data-module-id", String(moduleId));
          if (moduleChanged) {
            panel.scrollTop = 0;
          }
          detailScrollSyncSuppressedUntil = Date.now() + 350;
          panel.classList.toggle("kg-note-editing", noteEditingEnabled);
          renderNotesOverview();
          openUserNoteId = null;
          var initialItem = initialTocItem(tocItems);
          setActiveConceptSection(initialItem ? initialItem.id : null);
          updateGraphContextControls();
          typesetInfoPanel(options);
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
          bodyHtml += renderNotesAtAnchor(
            "concept", conceptId, "Graphic", 0, graphicCaption,
            noteAnchorSpecs("", "graphic", "Graphic", "")[0]
          );
          return renderFoldDown({
            anchorId: contentAnchorId(conceptId, "Graphic"),
            className: "concept-figure",
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
          panel.querySelectorAll(".kg-active-section").forEach(function(section) {
            section.classList.remove("kg-active-section");
          });
          if (!targetId) { return; }
          var link = panel.querySelector(
            '.concept-toc-link[data-toc-target="' + cssAttributeValueEscape(targetId) + '"]'
          );
          if (!link) { return; }
          link.classList.add("active");
          link.setAttribute("aria-current", "true");
          var target = document.getElementById(targetId);
          if (target) { target.classList.add("kg-active-section"); }
        }

        function setActiveConceptSection(targetId) {
          var nextTargetId = targetId ? String(targetId) : null;
          var targetChanged = activeConceptSectionTargetId !== nextTargetId;
          activeConceptSectionTargetId = nextTargetId;
          if (targetChanged) { updateConceptTocActive(nextTargetId); }
        }

        function initialTocItem(tocItems) {
          if (!Array.isArray(tocItems) || tocItems.length === 0) { return null; }
          if (activeConceptSectionTargetId) {
            var previous = tocItems.find(function(item) {
              return item.id === activeConceptSectionTargetId;
            });
            if (previous) { return previous; }
          }
          return tocItems[0];
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
          setActiveConceptSection(item.id);
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
            var matchingBlocks = conceptContentBlocks(concept).filter(function(block) {
              return block.kind === section.key;
            });
            return renderConceptSection(
              conceptId,
              matchingBlocks.length === 1 ? matchingBlocks[0].block_id : "",
              section.key,
              section.title,
              section.text
            );
          }).join("");
        }

        function optionalDetailTitlesForConcept(concept) {
          return conceptSections(concept).reduce(function(titles, section) {
            return titles.concat(optionalDetailTitlesFromText(section.text));
          }, []);
        }

        function noteTitlesForConcept(nodeId) {
          return userNotesState.notes
            .filter(function(note) {
              return note.targetType === "concept" && note.targetId === String(nodeId);
            })
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

        function moduleTooltipSourceText(module) {
          var overviewBlock = moduleContentBlocks(module).find(function(block) {
            return block.kind === "overview";
          });
          if (overviewBlock) { return overviewBlock.body; }
          var blocks = moduleContentBlocks(module);
          return blocks.length > 0 ? blocks[0].body : "";
        }

        function moduleTooltipHtml(moduleId) {
          var module = getModule(moduleId) || {};
          var memberCount = moduleMemberIds(module).length;
          var html = '<div class="kg-tooltip-title">' +
            renderTooltipText(module.title || moduleId) + "</div>";
          html += '<div class="kg-tooltip-definition">' +
            escapeHtml(moduleDomainLabel(module.domain)) + " module - " +
            escapeHtml(String(memberCount)) + " concept" + (memberCount === 1 ? "" : "s") +
            "</div>";
          var overview = conceptPreviewExcerpt(moduleTooltipSourceText(module));
          if (overview) {
            html += '<div class="kg-tooltip-section-title">Overview</div>';
            html += '<div class="kg-tooltip-definition">' + renderTooltipText(overview) + "</div>";
          }
          return html;
        }

        function relationshipConceptNameText(nodeId) {
          var concept = getConcept(nodeId);
          if (concept && concept.label) { return searchDisplayText(concept.label); }
          return conceptDisplayId(nodeId);
        }

        function relationshipPhrase(edge) {
          var relation = edgeRelation(edge);
          var policy = edgeRelationPolicyFor(relation);
          return policy.phrase ||
            (edgeRelationDirected(edge) ? relationDisplayLabel(relation).toLowerCase() : "is related to");
        }

        function graphObjectDisplayText(nodeId) {
          var moduleId = moduleIdFromGraphNodeId(nodeId);
          if (moduleId && getModule(moduleId)) {
            return searchDisplayText(getModule(moduleId).title || moduleId);
          }
          return relationshipConceptNameText(nodeId);
        }

        function moduleEdgeRelationCountLines(edge) {
          var relationCounts = edge && edge.relationCounts ? edge.relationCounts : {};
          return Object.keys(relationCounts).sort(compareRelations).map(function(relation) {
            return relation + " " + String(relationCounts[relation] || 0);
          });
        }

        function moduleEdgeTooltipHtml(edge) {
          var linkCount = (edge.edgeIds || []).length;
          var title = renderTooltipText(graphObjectDisplayText(edge.from)) +
            " -> " + renderTooltipText(graphObjectDisplayText(edge.to));
          var html = '<div class="kg-tooltip-title kg-edge-tooltip-title">' + title + "</div>";
          if (linkCount > 0 && linkCount <= 3) {
            html += '<div class="kg-tooltip-section-title">Concept links</div>';
            html += "<ul>" + concreteEdgesForModuleEdge(edge).map(function(concreteEdge) {
              return "<li>" + relationshipStatementTooltipHtml(concreteEdge) + "</li>";
            }).join("") + "</ul>";
          } else {
            html += '<div class="kg-tooltip-definition kg-edge-tooltip-note">' +
              escapeHtml(String(linkCount)) + " concept link" +
              (linkCount === 1 ? "" : "s") + "</div>";
            moduleEdgeRelationCountLines(edge).forEach(function(line) {
              html += '<div class="kg-tooltip-definition kg-edge-tooltip-note">' +
                escapeHtml(line) + "</div>";
            });
          }
          return html;
        }

        function edgeTooltipHtml(edge) {
          if (isProjectedModuleEdge(edge)) {
            return moduleEdgeTooltipHtml(edge);
          }
          var relation = edgeRelation(edge);
          var phrase = relationshipPhrase(edge);
          var colour = relationColour(relation);
          var title = renderTooltipText(relationshipConceptNameText(edge.from)) +
            ' <span class="kg-tooltip-relation" style="color:' +
            escapeHtml(colour) + '">' + escapeHtml(phrase) + "</span> " +
            renderTooltipText(relationshipConceptNameText(edge.to));
          var html = '<div class="kg-tooltip-title kg-edge-tooltip-title">' + title + "</div>";
          if (edge.note) {
            html += '<div class="kg-tooltip-definition kg-edge-tooltip-note">' +
              renderTooltipText(edge.note) + "</div>";
          }
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
          var owningModuleId = moduleIdForConcept(nodeId);
          var owningModule = owningModuleId ? getModule(owningModuleId) : null;

          var html = '<div class="concept-preview-header">';
          html += '<div class="concept-preview-title">' + renderTooltipText(conceptTitleText(nodeId)) + "</div>";
          html += '<button type="button" class="concept-preview-close" aria-label="Close preview">Close</button>';
          html += "</div>";
          if (owningModule) {
            html += '<div class="concept-preview-module">Module - ' +
              renderConceptText(owningModule.title || owningModuleId) + "</div>";
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

        // Search-only plain text: parse groups before truncating snippets so
        // nested TeX and custom macros cannot leak partial markup into results.
        function searchPlainText(value) {
          var text = String(value || "");
          var symbols = {
            alpha: "α", beta: "β", gamma: "γ", delta: "δ", Delta: "Δ",
            epsilon: "ε", eta: "η", theta: "θ", lambda: "λ", Lambda: "Λ",
            mu: "μ", nu: "ν", pi: "π", rho: "ρ", sigma: "σ", Sigma: "Σ",
            tau: "τ", phi: "φ", Phi: "Φ", omega: "ω", Omega: "Ω",
            nabla: "∇", partial: "∂", infty: "∞", times: "×", cdot: "·",
            equiv: "≡", coloneqq: ":=", leq: "≤", geq: "≥", neq: "≠",
            to: "→", rightarrow: "→", leftarrow: "←", pm: "±"
          };
          var output = "";
          var cursor = 0;
          while (cursor < text.length) {
            var ch = text.charAt(cursor);
            if (ch === "{") {
              var group = parseBracedArgument(text, cursor);
              if (group) {
                output += searchPlainText(group.value);
                cursor = group.end;
                continue;
              }
            }
            if (ch !== "\\") {
              output += ch === "}" ? "" : ch;
              cursor += 1;
              continue;
            }
            var command = /^\\([a-zA-Z_]+|.)/.exec(text.slice(cursor));
            if (!command) { cursor += 1; continue; }
            var name = command[1];
            cursor += command[0].length;
            var arity = /^(frac|dfrac|tfrac|overset|underset|cref|optional_details)$/.test(name) ? 2 :
              /^(sqrt|text|textrm|mathrm|mathbf|mathit|mathcal|mathbb|operatorname|hat|bar|vec)$/.test(name) ? 1 : 0;
            var args = [];
            for (var i = 0; i < arity; i++) {
              var start = skipOptionalDetailWhitespace(text, cursor);
              var argument = parseBracedArgument(text, start);
              if (!argument) { break; }
              args.push(searchPlainText(argument.value));
              cursor = argument.end;
            }
            if (args.length === arity && arity > 0) {
              if (/^(frac|dfrac|tfrac)$/.test(name)) { output += "(" + args[0] + ")/(" + args[1] + ")"; }
              else if (name === "sqrt") { output += "sqrt(" + args[0] + ")"; }
              else if (name === "cref") { output += args[0]; }
              else if (name === "optional_details") { output += args[0] + ": " + args[1]; }
              else if (name === "overset" || name === "underset") { output += args[1] + " (" + args[0] + ")"; }
              else { output += args[0]; }
            } else if (symbols[name]) { output += symbols[name]; }
            else if (/^(left|right|big|Big|bigg|Bigg)$/.test(name)) { /* sizing only */ }
            else if (/^[a-zA-Z_]+$/.test(name)) { output += " " + name + " " + args.join(" "); }
            else if (/^[{}%&#_$]$/.test(name)) { output += name; }
            else { output += " "; }
          }
          return output.replace(/\s+/g, " ").trim();
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
              value: searchPlainText(field.value)
            };
          });
        }

        function searchFieldsForModule(moduleId) {
          var module = getModule(moduleId) || {};
          var fields = [
            {name: "Module ID", value: String(moduleId)},
            {name: "Module", value: module.title || ""},
            {name: "Domain", value: module.domain || ""}
          ];
          moduleContentBlocks(module).forEach(function(block) {
            fields.push({
              name: block.title || contentBlockKindLabel(block.kind),
              value: block.body || ""
            });
          });
          moduleMemberIds(module).forEach(function(conceptId) {
            fields.push({
              name: "Member",
              value: conceptTitleText(conceptId)
            });
          });
          return fields.map(function(field) {
            return {
              name: field.name,
              value: searchPlainText(field.value)
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

        function matchingModuleSearchFields(moduleId, query) {
          return searchFieldsForModule(moduleId).filter(function(field) {
            return fieldContainsQuery(field, query);
          });
        }

        function rankedSearchResults(query) {
          var results = [];
          function addResult(type, id, fields, primaryFields) {
            var matches = fields.filter(function(field) {
              return !query || fieldContainsQuery(field, query);
            });
            if (!matches.length) { return; }
            var rank = query ? 2 : 0;
            matches.forEach(function(field) {
              if (primaryFields.indexOf(field.name) !== -1) {
                rank = Math.min(rank, field.value.toLowerCase() === query ? 0 : 1);
              }
            });
            results.push({type: type, id: id, rank: rank});
          }
          Object.keys(conceptData).forEach(function(id) {
            addResult("concept", id, searchFieldsForConcept(id),
              ["Display ID", "Concept ID", "Title"]);
          });
          if (query) {
            moduleIds().forEach(function(id) {
              addResult("module", id, searchFieldsForModule(id), ["Module ID", "Module"]);
            });
          }
          return results.sort(function(a, b) {
            if (a.rank !== b.rank) { return a.rank - b.rank; }
            if (a.type === b.type) {
              return a.type === "concept" ? compareConceptIds(a.id, b.id) : compareModules(a.id, b.id);
            }
            // Keep concept/module ties stable without overriding relevance.
            return a.type === "concept" ? -1 : 1;
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

        function fullGraphRelationKeep(rule) {
          var keep = {};
          contextPresetTraversals(rule, edgeKey).forEach(function(traversal) {
            keep[String(traversal.relation)] = true;
          });
          return keep;
        }

        function setEdgeHidden(edge, hidden) {
          // In Full graph, the active context's relation set is a global edge
          // filter. Direction and depth only determine the coloured context
          // reached from a selection.
          var fullGraph = viewerState.displayScope === DisplayScope.FULL;
          hidden = hidden || (fullGraph &&
            !fullGraphRelationKeep(viewerState.contextRule)[edgeRelation(edge)]);
          edge.hidden = hidden;
          if (hidden) {
            edge.title = "";
            edge.kgHoverable = false;
          } else if (originalEdges[edge.id] && originalEdges[edge.id].title !== undefined) {
            edge.title = originalEdges[edge.id].title;
            edge.kgHoverable = true;
          }
          return edge;
        }

        function setEdgeTooltipEnabled(edge, enabled) {
          if (enabled && originalEdges[edge.id] && originalEdges[edge.id].title !== undefined) {
            edge.title = originalEdges[edge.id].title;
            edge.kgHoverable = true;
          } else if (!enabled) {
            edge.title = "";
            edge.kgHoverable = false;
          }
          return edge;
        }

        function edgeHoverableInCurrentView(edge) {
          return visibleGraphEdge(edge) && edge.kgHoverable !== false;
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

        function relationColour(relation) {
          var item = edgeKey[relation] || {};
          return item.colour || "#999999";
        }

        function relationDisplayLabel(relation) {
          relation = String(relation || "");
          var policy = edgeRelationPolicyFor(relation);
          if (policy.label) { return policy.label; }
          return contentBlockKindLabel(relation.toLowerCase());
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

        function relationIsDirected(relation) {
          return edgeKey[relation] && edgeKey[relation].directed === true;
        }

        function contextPresetLabel(preset) {
          return {
            connections: "Connections",
            prerequisites: "Prerequisites",
            derivation: "Derivation",
            foundations: "Foundations",
            uses: "Uses",
            related: "Related",
            custom: "Custom"
          }[preset] || "Connections";
        }

        function contextDepthLabel(depth) {
          if (depth === ContextDepth.TWO_HOPS) { return "2 hops"; }
          if (depth === ContextDepth.TRANSITIVE) { return "Transitive"; }
          return "1 hop";
        }

        function phoneViewportActive() {
          var width = window.visualViewport ? window.visualViewport.width : window.innerWidth;
          return width <= 550 || window.matchMedia("(max-width: 550px)").matches;
        }

        function setResponsiveOptionLabels(selectId, labels, compact) {
          var select = document.getElementById(selectId);
          if (!select) { return; }
          Array.prototype.forEach.call(select.options, function(option) {
            var label = labels[option.value];
            if (label) { option.textContent = compact ? label[1] : label[0]; }
          });
        }

        function updateResponsiveControlLabels() {
          var compact = phoneViewportActive();
          setResponsiveOptionLabels("kg_display_scope_select", {
            full: ["Full graph", "Full"],
            context: ["Context only", "Context"],
            hidden: ["Hidden", "Hidden"]
          }, compact);
          setResponsiveOptionLabels("kg_details_view_select", {
            hide: ["Hide details", "Hide"],
            full: ["Full details", "Details"],
            folded: ["Folded", "Folded"],
            core: ["Core", "Core"],
            maths: ["Maths", "Maths"],
            context: ["Context", "Context"],
            practice: ["Practice", "Practice"]
          }, compact);
          setResponsiveOptionLabels("kg_fit_select", {
            reveal: ["Reveal selection", "Reveal"],
            selection: ["Fit selection", "Selection"],
            context: ["Fit context", "Context"],
            displayed: ["Fit displayed graph", "All"]
          }, compact);
          var clearButton = document.getElementById("kg_clear_selection");
          if (clearButton) { clearButton.textContent = compact ? "Clear" : "Clear selection"; }
          var expandSelected = document.getElementById("kg_expand_selected_module");
          if (expandSelected) {
            expandSelected.textContent = compact
              ? "Expand module"
              : "Expand selected concept's module";
          }
        }

        function updateGraphContextControls() {
          var selection = viewerSelectionSnapshot();
          var context = computeViewerContext(selection, viewerState.contextRule);
          var presetSelect = document.getElementById("kg_context_preset_select");
          var depthSelect = document.getElementById("kg_context_depth_select");
          var summary = document.getElementById("kg_context_summary");
          var customEdit = document.getElementById("kg_custom_context_edit");
          var representationActions = document.getElementById("kg_representation_actions");
          var noSelection = selection.type === "none";
          if (presetSelect) {
            presetSelect.value = viewerState.contextRule.preset;
            presetSelect.disabled = false;
          }
          if (depthSelect) {
            depthSelect.value = viewerState.contextRule.depth;
            depthSelect.disabled = noSelection;
          }
          if (customEdit) {
            customEdit.hidden = viewerState.contextRule.preset !== ContextPreset.CUSTOM;
          }
          var representedCount = 0;
          var representedModuleCount = 0;
          foldedModuleIdList().forEach(function(moduleId) {
            var moduleRepresentsContext = false;
            moduleMemberIds(getModule(moduleId)).forEach(function(id) {
              if (!context.keep[String(id)]) { return; }
              representedCount += 1;
              moduleRepresentsContext = true;
            });
            if (moduleRepresentsContext) { representedModuleCount += 1; }
          });
          if (representationActions) {
            var selectedConceptModule = selection.type === "concept"
              ? moduleIdForConcept(selection.id)
              : null;
            var selectedConceptIsFolded = Boolean(
              selectedConceptModule && selectedModuleIsFolded(selectedConceptModule)
            );
            var expandSelected = document.getElementById("kg_expand_selected_module");
            var expandContext = document.getElementById("kg_expand_context_modules");
            var contextCanExpand = !noSelection && representedCount > 0;
            expandSelected.hidden = !selectedConceptIsFolded;
            expandContext.hidden = !contextCanExpand;
            expandContext.textContent = "Expand " + String(representedCount) + " folded";
            var expandContextLabel =
              "Expand " + String(representedCount) + " context concept" +
              (representedCount === 1 ? "" : "s") + " represented by " +
              String(representedModuleCount) + " folded module" +
              (representedModuleCount === 1 ? "" : "s");
            expandContext.setAttribute("aria-label", expandContextLabel);
            expandContext.title = expandContextLabel;
            representationActions.hidden = !selectedConceptIsFolded && !contextCanExpand;
            representationActions.setAttribute(
              "data-selected-module-id",
              selectedConceptIsFolded ? selectedConceptModule : ""
            );
          }
          if (!summary) { return; }

          var selectionLabel = "No selection";
          if (selection.type === "concept") {
            selectionLabel = conceptDisplayId(selection.id) + " " + (getConcept(selection.id).label || "");
          } else if (selection.type === "module") {
            selectionLabel = getModule(selection.id).title || selection.id;
          }
          var scopeLabel = viewerState.displayScope === DisplayScope.CONTEXT
            ? "Context only"
            : viewerState.displayScope === DisplayScope.HIDDEN ? "Graph hidden" : "Full graph";
          summary.setAttribute("data-selection-type", selection.type);
          summary.setAttribute("data-context-preset", viewerState.contextRule.preset);
          summary.setAttribute("data-context-depth", viewerState.contextRule.depth);
          summary.setAttribute("data-display-scope", viewerState.displayScope);
          var fullSummary = selectionLabel + " · " +
            contextPresetLabel(viewerState.contextRule.preset) + " · " +
            contextDepthLabel(viewerState.contextRule.depth) + " · " + scopeLabel +
            " — " + String(context.nodeIds.length) + " context concept" +
            (context.nodeIds.length === 1 ? "" : "s") + ", " +
            String(context.edgeIds.length) + " context edge" +
            (context.edgeIds.length === 1 ? "" : "s") +
            (representedCount ? "; " + String(representedCount) + " represented by folded modules" : "");
          summary.textContent = String(context.nodeIds.length) + " context concept" +
            (context.nodeIds.length === 1 ? "" : "s");
          summary.title = fullSummary;
          summary.setAttribute("aria-label", fullSummary);
        }

        function setViewerContextRule(rule) {
          resetContextFitInteraction();
          viewerState.contextRule = createContextRule(
            rule && rule.preset,
            rule && rule.depth,
            rule && rule.customTraversals
          );
          renderGraphFromViewerState({fit: false});
          updateGraphContextControls();
        }

        function showRelationshipSectionInGraph(preset, fullTree) {
          resetContextFitInteraction();
          viewerState.contextRule = createContextRule(
            preset,
            fullTree ? ContextDepth.TRANSITIVE : ContextDepth.ONE_HOP
          );
          if (viewerState.displayScope === DisplayScope.HIDDEN) {
            viewerState.displayScope = DisplayScope.CONTEXT;
            updateGraphViewControls();
          }
          renderGraphFromViewerState({fit: false});
          updateGraphContextControls();
        }

        function setViewerDisplayScope(scope) {
          resetContextFitInteraction();
          scope = scope === DisplayScope.CONTEXT || scope === DisplayScope.HIDDEN
            ? scope
            : DisplayScope.FULL;
          viewerState.displayScope = scope;
          if (scope === DisplayScope.HIDDEN && !detailsAreVisible()) {
            setInfoPanelVisible(true);
          }
          updateGraphViewControls();
          renderGraphFromViewerState({fit: false});
          updateGraphContextControls();
        }

        function representedNodeIds(conceptIds) {
          var represented = {};
          (conceptIds || []).forEach(function(id) {
            var moduleId = moduleIdForConcept(id);
            var moduleNodeId = moduleId ? moduleGraphNodeId(moduleId) : null;
            if (moduleId && selectedModuleIsFolded(moduleId) && nodes.get(moduleNodeId) &&
                !nodes.get(moduleNodeId).hidden) {
              represented[moduleNodeId] = true;
            } else if (nodes.get(String(id)) && !nodes.get(String(id)).hidden) {
              represented[String(id)] = true;
            }
          });
          return Object.keys(represented);
        }

        function selectionRepresentationNodeIds(selection) {
          selection = selection || viewerSelectionSnapshot();
          if (selection.type === "concept") {
            return representedNodeIds([selection.id]);
          }
          if (selection.type === "module") {
            return selectedModuleIsFolded(selection.id)
              ? [moduleGraphNodeId(selection.id)]
              : representedNodeIds(moduleMemberIds(getModule(selection.id)));
          }
          return [];
        }

        function revealNodeIds(nodeIds, options) {
          options = options || {};
          var ids = (nodeIds || []).map(String).filter(function(id, index, values) {
            var node = nodes.get(id);
            return node && !node.hidden && values.indexOf(id) === index;
          });
          if (ids.length === 0) { return false; }

          var bounds = nodeCanvasBounds(ids);
          if (!bounds) { return false; }
          var available = availableGraphRect();
          var topLeft = network.DOMtoCanvas({x: available.left, y: available.top});
          var bottomRight = network.DOMtoCanvas({
            x: available.left + available.width,
            y: available.top + available.height
          });
          var viewLeft = Math.min(topLeft.x, bottomRight.x);
          var viewRight = Math.max(topLeft.x, bottomRight.x);
          var viewTop = Math.min(topLeft.y, bottomRight.y);
          var viewBottom = Math.max(topLeft.y, bottomRight.y);
          var deltaX = 0;
          var deltaY = 0;

          if (bounds.width > viewRight - viewLeft) {
            deltaX = bounds.x - ((viewLeft + viewRight) / 2);
          } else if (bounds.left < viewLeft) {
            deltaX = bounds.left - viewLeft;
          } else if (bounds.right > viewRight) {
            deltaX = bounds.right - viewRight;
          }
          if (bounds.height > viewBottom - viewTop) {
            deltaY = bounds.y - ((viewTop + viewBottom) / 2);
          } else if (bounds.top < viewTop) {
            deltaY = bounds.top - viewTop;
          } else if (bounds.bottom > viewBottom) {
            deltaY = bounds.bottom - viewBottom;
          }
          if (Math.abs(deltaX) < 0.001 && Math.abs(deltaY) < 0.001) { return false; }

          var position = network.getViewPosition();
          network.moveTo({
            position: {x: position.x + deltaX, y: position.y + deltaY},
            scale: network.getScale(),
            animation: options.animation === true ? {
              duration: options.duration || 180,
              easingFunction: "easeInOutQuad"
            } : false
          });
          updateNodeLabelPositions();
          return true;
        }

        function revealViewerSelection(options) {
          return revealNodeIds(selectionRepresentationNodeIds(), options);
        }

        function updateFitApplyButton() {
          var button = document.getElementById("kg_fit_apply");
          if (!button) { return; }
          var primed = Boolean(contextFitPrimedKey);
          button.textContent = primed ? "Fit++" : "Fit";
          button.setAttribute("data-fit-action", primed ? "contract" : "fit");
          button.setAttribute(
            "aria-label",
            primed ? "Temporarily contract and fit this context" : "Fit selected target"
          );
          button.title = primed
            ? "Temporarily contract this context around the selection"
            : "";
        }

        function clearContextFitPriming() {
          contextFitPrimedKey = null;
          updateFitApplyButton();
        }

        function restoreContextContractionPositions() {
          if (!contextContractionState) { return false; }
          Object.keys(contextContractionState.restorePositions).forEach(function(nodeId) {
            var position = contextContractionState.restorePositions[nodeId];
            if (nodes.get(nodeId) && validLayoutPosition(position)) {
              network.moveNode(nodeId, position.x, position.y);
            }
          });
          contextContractionState = null;
          updateNodeLabelPositions();
          return true;
        }

        function underlyingContextNodePosition(nodeId) {
          var moduleId = moduleIdFromGraphNodeId(nodeId);
          if (moduleId && selectedModuleIsFolded(moduleId)) {
            return moduleGraphNodePosition(moduleId);
          }
          if (getConcept(nodeId)) {
            return effectiveConceptPosition(nodeId);
          }
          return graphPositionForNode(nodeId);
        }

        function resetContextFitInteraction(options) {
          options = options || {};
          if (options.restore !== false) {
            restoreContextContractionPositions();
          } else {
            contextContractionState = null;
          }
          clearContextFitPriming();
        }

        function contextContractionCandidate() {
          var selection = viewerSelectionSnapshot();
          if (
            viewerState.displayScope !== DisplayScope.CONTEXT ||
            selection.type === "none" ||
            !lastGraphRender
          ) {
            return null;
          }
          var anchorIds = selectionRepresentationNodeIds(selection);
          var nodeIds = representedNodeIds(lastGraphRender.contextNodeIds);
          if (anchorIds.length !== 1 || nodeIds.length < 2) { return null; }
          var anchorId = String(anchorIds[0]);
          if (nodeIds.indexOf(anchorId) === -1 || !visibleGraphNode(anchorId)) { return null; }
          nodeIds = nodeIds.map(String).filter(function(id, index, values) {
            return visibleGraphNode(id) && values.indexOf(id) === index;
          });
          if (nodeIds.length < 2) { return null; }
          return {
            anchorId: anchorId,
            nodeIds: nodeIds,
            key: JSON.stringify({
              selection: selection,
              contextRule: viewerState.contextRule,
              nodeIds: nodeIds.slice().sort()
            })
          };
        }

        function contractionNodeExtents(nodeId) {
          nodeId = String(nodeId);
          var node = nodes.get(nodeId) || {};
          if (node.isModuleNode === true || moduleIdFromGraphNodeId(nodeId)) {
            var width = Number(node.moduleFootprintWidth) || 1;
            var height = Number(node.moduleFootprintHeight) || 1;
            return {
              left: width / 2,
              right: width / 2,
              top: height / 2,
              bottom: height / 2,
              width: width,
              height: height
            };
          }
          var baseRadius = Number(node.visualSize) || Number(node.size) || 18;
          var radius = baseRadius;
          if (nodeId === String(activeNodeId || "")) {
            radius *= activeNodeRadiusScale;
          }
          var footprint = conceptFootprintExtents(nodeId);
          var labelVisibilityScale = Number(kgNodeLabelConfig.hideBelowPx) /
            Math.max(1, nodeLabelFontSize);
          var minimumVisibleLabelInflation = labelVisibilityScale > 0
            ? Math.max(1, 0.25 / labelVisibilityScale)
            : 1;
          var left = Math.max(radius, footprint.left * minimumVisibleLabelInflation);
          var right = Math.max(radius, footprint.right * minimumVisibleLabelInflation);
          var top = Math.max(radius, footprint.top);
          var bottom = Math.max(
            radius,
            radius + Math.max(0, footprint.bottom - baseRadius) *
              minimumVisibleLabelInflation
          );
          var label = nodeLabelEls[nodeId];
          var scale = network && network.getScale ? Number(network.getScale()) : 1;
          if (
            label &&
            Number.isFinite(scale) &&
            scale > 0 &&
            window.getComputedStyle(label).display !== "none"
          ) {
            var renderedLabelBounds = label.getBoundingClientRect();
            var renderedLabelWidth = renderedLabelBounds.width / scale;
            var renderedLabelHeight = renderedLabelBounds.height / scale;
            left = Math.max(left, renderedLabelWidth / 2);
            right = Math.max(right, renderedLabelWidth / 2);
            bottom = Math.max(
              bottom,
              radius + (3 / scale) + renderedLabelHeight
            );
          }
          return {
            left: left,
            right: right,
            top: top,
            bottom: bottom,
            width: left + right,
            height: top + bottom
          };
        }

        function contractionClearance(left, right) {
          var characteristicSize = Math.max(
            Math.min(left.width, left.height),
            Math.min(right.width, right.height)
          );
          return Math.max(60, Math.min(240, characteristicSize * 0.18));
        }

        function segmentEntryParameter(start, end, bounds) {
          var delta = {x: end.x - start.x, y: end.y - start.y};
          var entry = 0;
          var exit = 1;
          [
            {origin: start.x, delta: delta.x, min: bounds.left, max: bounds.right},
            {origin: start.y, delta: delta.y, min: bounds.top, max: bounds.bottom}
          ].forEach(function(axis) {
            if (entry > exit) { return; }
            if (Math.abs(axis.delta) < 0.000001) {
              if (axis.origin < axis.min || axis.origin > axis.max) {
                entry = 2;
                exit = 1;
              }
              return;
            }
            var first = (axis.min - axis.origin) / axis.delta;
            var second = (axis.max - axis.origin) / axis.delta;
            if (first > second) {
              var swap = first;
              first = second;
              second = swap;
            }
            entry = Math.max(entry, first);
            exit = Math.min(exit, second);
          });
          if (entry > exit || exit < 0 || entry > 1) { return null; }
          return Math.max(0, entry);
        }

        function contractionObstacleBounds(movingExtents, obstacle) {
          var clearance = contractionClearance(movingExtents, obstacle.extents);
          return {
            left: obstacle.position.x - obstacle.extents.left - clearance - movingExtents.right,
            right: obstacle.position.x + obstacle.extents.right + clearance + movingExtents.left,
            top: obstacle.position.y - obstacle.extents.top - clearance - movingExtents.bottom,
            bottom: obstacle.position.y + obstacle.extents.bottom + clearance + movingExtents.top
          };
        }

        function contractionCollisionEntry(start, end, movingExtents, obstacle) {
          return segmentEntryParameter(
            start,
            end,
            contractionObstacleBounds(movingExtents, obstacle)
          );
        }

        function contractionPositionInsideBounds(position, bounds) {
          return position.x > bounds.left && position.x < bounds.right &&
            position.y > bounds.top && position.y < bounds.bottom;
        }

        function clearInitialContractionCollision(start, anchor, extents, placed) {
          var radial = {x: start.x - anchor.x, y: start.y - anchor.y};
          var length = Math.hypot(radial.x, radial.y);
          if (length < 0.000001) { return copyLayoutPosition(start); }
          var direction = {x: radial.x / length, y: radial.y / length};
          var position = copyLayoutPosition(start);

          for (var iteration = 0; iteration < 24; iteration += 1) {
            var overlapping = placed.map(function(obstacle) {
              return contractionObstacleBounds(extents, obstacle);
            }).filter(function(bounds) {
              return contractionPositionInsideBounds(position, bounds);
            });
            if (overlapping.length === 0) { break; }

            var travel = 0;
            overlapping.forEach(function(bounds) {
              var horizontalExit = Infinity;
              var verticalExit = Infinity;
              if (direction.x > 0.000001) {
                horizontalExit = (bounds.right - position.x) / direction.x;
              } else if (direction.x < -0.000001) {
                horizontalExit = (bounds.left - position.x) / direction.x;
              }
              if (direction.y > 0.000001) {
                verticalExit = (bounds.bottom - position.y) / direction.y;
              } else if (direction.y < -0.000001) {
                verticalExit = (bounds.top - position.y) / direction.y;
              }
              travel = Math.max(travel, Math.min(horizontalExit, verticalExit));
            });
            if (!Number.isFinite(travel) || travel < 0) { break; }
            position = {
              x: position.x + direction.x * (travel + 0.5),
              y: position.y + direction.y * (travel + 0.5)
            };
          }
          return position;
        }

        function contractCurrentContext(candidate) {
          candidate = candidate || contextContractionCandidate();
          if (!candidate) { return false; }
          restoreContextContractionPositions();

          var originalPositions = network.getPositions(candidate.nodeIds);
          var restorePositions = {};
          candidate.nodeIds.forEach(function(nodeId) {
            var position = underlyingContextNodePosition(nodeId);
            if (validLayoutPosition(position)) {
              restorePositions[nodeId] = copyLayoutPosition(position);
            }
          });
          var anchorPosition = originalPositions[candidate.anchorId];
          if (!validLayoutPosition(anchorPosition)) { return false; }
          var ordered = candidate.nodeIds.filter(function(id) {
            return id !== candidate.anchorId && validLayoutPosition(originalPositions[id]);
          }).sort(function(leftId, rightId) {
            var left = originalPositions[leftId];
            var right = originalPositions[rightId];
            var leftDistance = Math.hypot(
              left.x - anchorPosition.x,
              left.y - anchorPosition.y
            );
            var rightDistance = Math.hypot(
              right.x - anchorPosition.x,
              right.y - anchorPosition.y
            );
            return leftDistance - rightDistance || String(leftId).localeCompare(String(rightId));
          });
          var placed = [{
            id: candidate.anchorId,
            position: copyLayoutPosition(anchorPosition),
            extents: contractionNodeExtents(candidate.anchorId)
          }];
          var finalPositions = {};
          finalPositions[candidate.anchorId] = copyLayoutPosition(anchorPosition);

          ordered.forEach(function(nodeId) {
            var start = originalPositions[nodeId];
            var extents = contractionNodeExtents(nodeId);
            var collisionFreeStart = clearInitialContractionCollision(
              start,
              anchorPosition,
              extents,
              placed
            );
            var movedOutward = Math.hypot(
              collisionFreeStart.x - start.x,
              collisionFreeStart.y - start.y
            ) > 0.001;
            var stop = 1;
            if (!movedOutward) {
              placed.forEach(function(obstacle) {
                var entry = contractionCollisionEntry(
                  start,
                  anchorPosition,
                  extents,
                  obstacle
                );
                if (entry !== null) { stop = Math.min(stop, entry); }
              });
              stop = Math.max(0, stop - 0.0001);
            }
            var finalPosition = movedOutward ? collisionFreeStart : {
              x: start.x + (anchorPosition.x - start.x) * stop,
              y: start.y + (anchorPosition.y - start.y) * stop
            };
            network.moveNode(nodeId, finalPosition.x, finalPosition.y);
            finalPositions[nodeId] = finalPosition;
            placed.push({id: nodeId, position: finalPosition, extents: extents});
          });

          contextContractionState = {
            key: candidate.key,
            anchorId: candidate.anchorId,
            originalPositions: originalPositions,
            restorePositions: restorePositions,
            finalPositions: finalPositions
          };
          updateNodeLabelPositions();
          showTransientContextNotice(
            "Context contracted temporarily — navigating away restores the layout.",
            "context-contracted",
            3600
          );
          return true;
        }

        function fitViewerTarget(target) {
          var selection = viewerSelectionSnapshot();
          var ids = [];
          if (target === "reveal") {
            revealViewerSelection({animation: true});
            return;
          } else if (target === "selection") {
            ids = selectionRepresentationNodeIds(selection);
          } else if (target === "displayed") {
            ids = lastGraphRender ? lastGraphRender.fitIds.slice() : [];
          } else {
            ids = representedNodeIds(lastGraphRender ? lastGraphRender.contextNodeIds : []);
          }
          var contractionCandidate = target === "context"
            ? contextContractionCandidate()
            : null;
          if (
            contractionCandidate &&
            contextFitPrimedKey === contractionCandidate.key
          ) {
            clearContextFitPriming();
            if (contractCurrentContext(contractionCandidate)) {
              ids = contractionCandidate.nodeIds;
            }
            fitNodesToAvailableRect(ids, {maxScale: 0.85});
            return;
          }
          clearContextFitPriming();
          fitNodesToAvailableRect(ids, {maxScale: target === "selection" ? 0.75 : 0.85});
          if (contractionCandidate) {
            contextFitPrimedKey = contractionCandidate.key;
            updateFitApplyButton();
          }
        }

        window.kgContextContractionSnapshot = function() {
          return {
            primed: Boolean(contextFitPrimedKey),
            active: Boolean(contextContractionState),
            anchorId: contextContractionState ? contextContractionState.anchorId : null
          };
        };

        function contextTraversalLabelParts(relation, direction) {
          var label = relationDisplayLabel(relation);
          if (!relationIsDirected(relation)) {
            return {prefix: "", relation: label, suffix: ""};
          }
          var labels = {
            DERIVES_FROM: {
              outgoing: {prefix: "Selection is ", relation: "derived from", suffix: ""},
              incoming: {prefix: "", relation: "Derived from", suffix: " selection"}
            },
            REQUIRES: {
              outgoing: {prefix: "Selection ", relation: "requires", suffix: ""},
              incoming: {prefix: "", relation: "Requires", suffix: " selection"}
            },
            CONSTRUCTED_FROM: {
              outgoing: {prefix: "Selection is ", relation: "constructed from", suffix: ""},
              incoming: {prefix: "", relation: "Constructed from", suffix: " selection"}
            },
            COMPONENT_OF: {
              outgoing: {prefix: "Selection is a ", relation: "component of", suffix: ""},
              incoming: {prefix: "", relation: "Component of", suffix: " selection"}
            },
            INSTANCE_OF: {
              outgoing: {prefix: "Selection is an ", relation: "instance of", suffix: ""},
              incoming: {prefix: "", relation: "Instance of", suffix: " selection"}
            }
          };
          var relationLabels = labels[String(relation)] || {};
          return relationLabels[direction] || (direction === "incoming"
            ? {prefix: "", relation: label, suffix: " selection"}
            : {prefix: "Selection: ", relation: label, suffix: ""});
        }

        function contextTraversalLabelHtml(relation, direction) {
          var parts = contextTraversalLabelParts(relation, direction);
          return '<span class="kg-custom-context-label">' + escapeHtml(parts.prefix) +
            '<span class="kg-custom-context-relation" style="color:' +
            escapeHtml(relationColour(relation)) + '">' +
            escapeHtml(parts.relation) + "</span>" + escapeHtml(parts.suffix) + "</span>";
        }

        function openCustomContextEditor() {
          var traversals = viewerState.contextRule.preset === ContextPreset.CUSTOM
            ? viewerState.contextRule.customTraversals
            : contextPresetTraversals(viewerState.contextRule, edgeKey);
          setControlsVisible(false);
          renderCustomContextRules(traversals);
          document.getElementById("kg_custom_context").hidden = false;
        }

        function renderCustomContextRules(traversals) {
          var container = document.getElementById("kg_custom_context_rules");
          if (!container) { return; }
          var enabled = {};
          (traversals || viewerState.contextRule.customTraversals).forEach(function(item) {
            enabled[item.relation + "::" + item.direction] = true;
          });
          var html = "";
          orderedRelations().forEach(function(relation) {
            var directions = relationIsDirected(relation)
              ? ["outgoing", "incoming"]
              : ["undirected"];
            directions.forEach(function(direction) {
              var key = relation + "::" + direction;
              html += '<label class="kg-custom-context-rule"><input type="checkbox" ' +
                'data-relation="' + escapeHtml(relation) + '" data-direction="' +
                escapeHtml(direction) + '"' + (enabled[key] ? " checked" : "") + '> ' +
                contextTraversalLabelHtml(relation, direction) + "</label>";
            });
          });
          container.innerHTML = html;
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

        function relationshipConceptText(nodeId) {
          var concept = getConcept(nodeId);
          var label = concept ? concept.label || "" : "";
          return conceptDisplayId(nodeId) + (label ? " " + label : "");
        }

        function relationshipStatementText(edge) {
          return relationshipConceptText(edge.from) + " " + relationshipPhrase(edge) + " " +
            relationshipConceptText(edge.to) + ".";
        }

        function relationshipStatementTooltipHtml(edge) {
          var relation = edgeRelation(edge);
          var phrase = relationshipPhrase(edge);
          return renderTooltipText(relationshipConceptText(edge.from)) +
            ' <span class="kg-tooltip-relation" style="color:' +
            escapeHtml(relationColour(relation)) + '">' + escapeHtml(phrase) + "</span> " +
            renderTooltipText(relationshipConceptText(edge.to)) + ".";
        }

        function relationshipStatementHtml(edge) {
          var relation = edgeRelation(edge);
          var phrase = relationshipPhrase(edge);
          var sentence = relationshipStatementText(edge);
          return '<div class="edge-detail-statement" aria-label="' +
            escapeHtml(sentence) + '">' +
            relationshipConceptHtml(edge.from) +
            ' <span class="edge-detail-phrase" style="color:' +
            escapeHtml(relationColour(relation)) + '">' + escapeHtml(phrase) + "</span> " +
            relationshipConceptHtml(edge.to) +
            ".</div>";
        }

        function concreteEdgesForModuleEdge(edge) {
          return (edge.edgeIds || []).map(function(edgeId) {
            return originalEdges[edgeId] || allEdges.find(function(item) {
              return item.id === edgeId;
            });
          }).filter(Boolean);
        }

        function renderModuleBoundaryEdgeDetails(edge) {
          var relationGroups = {};
          concreteEdgesForModuleEdge(edge).forEach(function(concreteEdge) {
            var relation = edgeRelation(concreteEdge);
            if (!relationGroups[relation]) { relationGroups[relation] = []; }
            relationGroups[relation].push(concreteEdge);
          });

          var html = "";
          Object.keys(relationGroups).sort(compareRelations).forEach(function(relation) {
            html += '<section class="module-boundary-edge-detail-group">';
            html += '<h3><span class="edge-colour-swatch" style="background:' +
              escapeHtml(relationColour(relation)) + '"></span>' +
              escapeHtml(relation + " " + relationGroups[relation].length) + "</h3>";
            html += '<ul class="module-boundary-edge-detail-list">';
            relationGroups[relation].sort(function(a, b) {
              return compareConceptIds(String(a.from), String(b.from)) ||
                compareConceptIds(String(a.to), String(b.to));
            }).forEach(function(concreteEdge) {
              html += "<li>" + relationshipStatementHtml(concreteEdge);
              if (concreteEdge.note) {
                html += '<div class="module-boundary-note">' +
                  renderConceptText(concreteEdge.note) + "</div>";
              }
              html += "</li>";
            });
            html += "</ul></section>";
          });
          return html;
        }

        function backlinkGroupTitle(relation) {
          var policy = edgeRelationPolicyFor(relation);
          if (policy.backlinkTitle) { return policy.backlinkTitle; }
          return relation || "Related concepts";
        }

        function derivedFromEdgesFor(nodeId, fullTree) {
          nodeId = String(nodeId);
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
                  relationHasDerivationTreeSemantics(edgeRelation(edge)) &&
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
                  relationHasDerivationTreeSemantics(edgeRelation(edge)) &&
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

        function fullTreeToggleHtml(className, checked, label) {
          return '<label class="concept-full-tree-toggle">' +
            '<input type="checkbox" class="' + escapeHtml(className) + '"' +
            (checked ? " checked" : "") + "> " +
            escapeHtml(label || "Full tree") + "</label>";
        }

        function relationshipShowInGraphButtonHtml(className, preset) {
          return '<button type="button" class="concept-relationship-show-graph ' +
            escapeHtml(className) + '" data-context-preset="' +
            escapeHtml(preset) + '">Show in graph</button>';
        }

        function derivedFromTreeItemHtml(item, noteClassName) {
          var html = "<li" + treeIndentStyle(item) + ">";
          html += relationshipConceptHtml(item.nodeId);
          html += ' <span class="concept-tree-relation" style="color:' +
            escapeHtml(relationColour(edgeRelation(item.edge))) + '">' +
            escapeHtml(relationDisplayLabel(edgeRelation(item.edge))) + "</span>";
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
          var derivedEntries = derivedFromThisEntriesFor(nodeId, backlinksFullTreeEnabled);
          derivedEntries.forEach(function(item) {
            var itemRelation = edgeRelation(item.edge);
            if (!groups[itemRelation]) { groups[itemRelation] = []; }
            groups[itemRelation].push(item);
          });

          allEdges.forEach(function(edge) {
            var relation = edgeRelation(edge);
            var relatedNodeId = null;
            if (relationHasDerivationTreeSemantics(relation)) { return; }
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
            '" class="concept-derived-from" open>';
          html += "<summary>Derived from</summary>";
          html += fullTreeToggleHtml(
            "concept-derived-from-full-tree",
            derivedFromFullTreeEnabled
          );
          html += relationshipShowInGraphButtonHtml(
            "concept-derived-from-show-graph",
            ContextPreset.DERIVATION
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
            '" class="concept-backlinks" open>';
          html += "<summary>Where this is used</summary>";
          html += fullTreeToggleHtml(
            "concept-backlinks-full-tree",
            backlinksFullTreeEnabled,
            "Full derivation/construction tree"
          );
          html += relationshipShowInGraphButtonHtml(
            "concept-backlinks-show-graph",
            ContextPreset.USES
          );
          groups.forEach(function(group) {
            html += '<section class="concept-backlink-group">';
            html += '<div class="concept-backlink-group-title">' +
              escapeHtml(group.title) + "</div>";
            html += '<ul class="concept-backlink-list">';
            group.items.forEach(function(item) {
              html += derivedFromTreeItemHtml(item, "concept-backlink-note");
            });
            html += "</ul></section>";
          });
          html += "</details>";
          return html;
        }

        function showModuleEdgeDetails(edge) {
          hideConceptPreview(true);
          restoreHoveredEdge();

          var linkCount = (edge.edgeIds || []).length;
          var html = "";
          html += "<h2>Module Boundary</h2>";
          html += '<section class="edge-detail module-boundary-edge-detail">';
          html += '<div class="edge-detail-statement" aria-label="' +
            escapeHtml(graphObjectDisplayText(edge.from) + " to " + graphObjectDisplayText(edge.to)) +
            '">' + renderConceptText(graphObjectDisplayText(edge.from)) +
            " -> " + renderConceptText(graphObjectDisplayText(edge.to)) + "</div>";
          html += '<dl class="edge-detail-meta">';
          html += "<dt>Links</dt><dd>" + escapeHtml(String(linkCount)) +
            " concept link" + (linkCount === 1 ? "" : "s") + "</dd>";
          html += "<dt>Relations</dt><dd>" +
            moduleEdgeRelationCountLines(edge).map(escapeHtml).join("<br>") + "</dd>";
          html += "</dl>";
          html += renderModuleBoundaryEdgeDetails(edge);
          html += "</section>";

          showInspection(html);
        }

        function showEdgeDetails(edgeId) {
          var edge = edges.get(edgeId);
          if (!edge || !visibleGraphEdge(edge)) { return; }
          if (isProjectedModuleEdge(edge)) {
            showModuleEdgeDetails(edge);
            return;
          }

          hideConceptPreview(true);
          restoreHoveredEdge();

          var relation = edgeRelation(edge);
          var relationInfo = edgeKey[relation] || {};
          var relationColourValue = relationColour(relation);
          var html = "";
          html += "<h2>Relationship</h2>";
          html += '<section class="edge-detail">';
          html += relationshipStatementHtml(edge);
          html += '<dl class="edge-detail-meta">';
          html += "<dt>Relation</dt><dd>" +
            '<span class="edge-colour-swatch" style="background:' +
            escapeHtml(relationColourValue) + '"></span>' +
            escapeHtml(relation) + "</dd>";
          if (relationInfo.meaning) {
            html += "<dt>Meaning</dt><dd>" + escapeHtml(relationInfo.meaning) + "</dd>";
          }
          if (edge.note) {
            html += "<dt>Specific</dt><dd>" + renderConceptText(edge.note) + "</dd>";
          }
          html += "</dl>";
          html += "</section>";

          showInspection(html);
        }

        function closeInspection() {
          var dialog = document.getElementById("kg_inspection_dialog");
          if (dialog && dialog.open) { dialog.close(); }
        }

        function showInspection(html) {
          var dialog = document.getElementById("kg_inspection_dialog");
          var body = document.getElementById("kg_inspection_body");
          if (!dialog || !body) { return; }
          body.innerHTML = html;
          if (!dialog.open) { dialog.showModal(); }
          if (window.MathJax && MathJax.typesetPromise) {
            MathJax.typesetPromise([body]).catch(function(err) {
              console.warn("MathJax inspection typesetting failed:", err);
            });
          }
        }

        function studyOutcomeText(outcome) {
          if (outcome === "correct") { return "Correct"; }
          if (outcome === "unknown") { return "I don’t know"; }
          if (outcome === "incorrect") { return "Incorrect"; }
          return "";
        }

        function studyOutcomeIcon(outcome) {
          return outcome === "correct" ? "✓" : "✕";
        }

        function studyOutcomeFeedbackText(outcome) {
          if (outcome === "correct") { return "Correct — nicely done."; }
          if (outcome === "unknown") {
            return "No problem — review the answer, then try when ready.";
          }
          if (outcome === "incorrect") {
            return "Not quite — review the answer and have another go.";
          }
          return "";
        }

        function studyOptionResultHtml(result) {
          var text = "";
          if (result === "correct") { text = "✓ Correct answer"; }
          if (result === "incorrect") { text = "✕ Your answer"; }
          if (result === "unknown") { text = "✕ I don’t know"; }
          return text
            ? '<span class="study-option-result" data-outcome="' +
              escapeHtml(result) + '">' + escapeHtml(text) + "</span>"
            : "";
        }

        function studyQuestionStatusHtml(progress) {
          var outcome = progress && progress.lastOutcome ? progress.lastOutcome : "";
          if (!outcome) {
            return '<span class="study-question-status" data-outcome=""></span>';
          }
          return '<span class="study-question-status" data-outcome="' +
            escapeHtml(outcome) + '"><span aria-hidden="true">' +
            studyOutcomeIcon(outcome) + "</span> " +
            escapeHtml(studyOutcomeText(outcome)) + "</span>";
        }

        function automaticQuestionCorrectOption(question) {
          var options = Array.isArray(question && question.options) ? question.options : [];
          return options.find(function(option) { return option && option.is_correct === true; }) || null;
        }

        function automaticQuestionFeedbackHtml(question, progress) {
          if (!progress || !progress.lastOutcome) { return ""; }
          var answer = question && question.answer ? question.answer : "";
          var html = '<div class="study-question-feedback">';
          html += '<div class="study-question-result" data-outcome="' +
            escapeHtml(progress.lastOutcome) + '"><span aria-hidden="true">' +
            studyOutcomeIcon(progress.lastOutcome) + "</span> " +
            escapeHtml(studyOutcomeFeedbackText(progress.lastOutcome)) + "</div>";
          if (answer) {
            html += renderStudyText(answer, "concept-body study-answer-body");
          }
          html += "</div>";
          return html;
        }

        function renderAutomaticStudyQuestion(question, index) {
          var questionId = String(question.question_id || "");
          var prompt = question.prompt || question.question || "";
          var options = Array.isArray(question.options) ? question.options : [];
          var progress = studyProgressState.questions[questionId] || null;
          var correctOption = automaticQuestionCorrectOption(question);
          var inputName = "study-response-" + questionId;
          var html = '<details class="study-question study-question-automatic" data-question-id="' +
            escapeHtml(questionId) + '" open>';
          html += '<summary class="study-question-heading"><span class="study-question-title">Question ' +
            (index + 1) + "</span>" + studyQuestionStatusHtml(progress) + "</summary>";
          html += '<div class="study-question-body">';
          html += renderStudyText(prompt, "concept-body study-question-prompt");
          html += '<fieldset class="study-options"><legend class="kg-visually-hidden">Choose one answer</legend>';
          options.forEach(function(option) {
            var optionId = String(option.option_id || "");
            var result = progress && correctOption && optionId === String(correctOption.option_id)
              ? "correct"
              : "";
            html += '<label class="study-option" data-option-id="' + escapeHtml(optionId) + '"' +
              (result ? ' data-result="' + result + '"' : "") + ">";
            html += '<input type="radio" name="' + escapeHtml(inputName) + '" value="' +
              escapeHtml(optionId) + '">';
            html += '<span class="study-option-text">' + renderConceptText(option.text || "") + "</span>";
            html += studyOptionResultHtml(result);
            html += "</label>";
          });
          html += '<label class="study-option study-option-unknown" data-option-id="__unknown__">';
          html += '<input type="radio" name="' + escapeHtml(inputName) + '" value="__unknown__">';
          html += '<span class="study-option-text">? — I don’t know; show me the answer</span>';
          html += "</label></fieldset>";
          html += '<button type="button" class="study-check-answer" disabled>Check answer</button>';
          html += '<div class="study-feedback-host" role="status" aria-live="polite" aria-atomic="true">' +
            automaticQuestionFeedbackHtml(question, progress) + "</div>";
          html += "</div></details>";
          return html;
        }

        function selfAssessedQuestionFeedbackHtml(question, progress, response, pending) {
          if (!pending && (!progress || !progress.lastOutcome)) { return ""; }
          var html = '<div class="study-question-feedback study-self-feedback">';
          if (pending) {
            html += '<div class="study-question-result study-review-prompt">' +
              "Compare your answer, then mark it honestly.</div>";
          } else {
            html += '<div class="study-question-result" data-outcome="' +
              escapeHtml(progress.lastOutcome) + '"><span aria-hidden="true">' +
              studyOutcomeIcon(progress.lastOutcome) + "</span> " +
              escapeHtml(studyOutcomeFeedbackText(progress.lastOutcome)) + "</div>";
          }
          if (response) {
            html += '<div class="study-answer-label">Your answer</div>';
            html += renderStudyText(response, "concept-body study-your-answer");
          }
          html += '<div class="study-answer-label">Model answer</div>';
          html += renderStudyText(question.answer || "", "concept-body study-answer-body");
          if (pending) {
            html += '<div class="study-self-mark-actions" aria-label="Mark your answer">';
            html += '<button type="button" class="study-self-mark" data-outcome="correct">✓ Correct</button>';
            html += '<button type="button" class="study-self-mark" data-outcome="incorrect">✕ Incorrect</button>';
            html += "</div>";
          }
          html += "</div>";
          return html;
        }

        function renderSelfAssessedStudyQuestion(question, index) {
          var questionId = String(question && question.question_id || "");
          var prompt = question && (question.prompt || question.question)
            ? (question.prompt || question.question)
            : "";
          if (!prompt) { return ""; }
          var progress = studyProgressState.questions[questionId] || null;
          var html = '<details class="study-question study-question-self-assessed" data-question-id="' +
            escapeHtml(questionId) + '" open>';
          html += '<summary class="study-question-heading"><span class="study-question-title">Question ' +
            (index + 1) + "</span>" + studyQuestionStatusHtml(progress) + "</summary>";
          html += '<div class="study-question-body">';
          html += renderStudyText(prompt, "concept-body study-question-prompt");
          html += '<label class="study-self-response-label">Your answer';
          html += '<textarea class="study-self-response" rows="3"></textarea></label>';
          html += '<div class="study-self-actions">';
          html += '<button type="button" class="study-self-check-answer">Check answer</button>';
          html += '<button type="button" class="study-self-unknown">? I don’t know — show answer</button>';
          html += "</div>";
          html += '<div class="study-response-validation" role="alert"></div>';
          html += '<div class="study-feedback-host" role="status" aria-live="polite" aria-atomic="true">' +
            selfAssessedQuestionFeedbackHtml(question, progress, "", false) + "</div>";
          html += "</div></details>";
          return html;
        }

        function studyOptionElement(card, optionId) {
          var match = null;
          card.querySelectorAll(".study-option").forEach(function(optionElement) {
            if (!match && optionElement.getAttribute("data-option-id") === optionId) {
              match = optionElement;
            }
          });
          return match;
        }

        function setStudyOptionResult(optionElement, result) {
          if (!optionElement) { return; }
          optionElement.removeAttribute("data-result");
          var oldResult = optionElement.querySelector(".study-option-result");
          if (oldResult) { oldResult.remove(); }
          if (!result) { return; }
          optionElement.setAttribute("data-result", result);
          optionElement.insertAdjacentHTML("beforeend", studyOptionResultHtml(result));
        }

        function applyAutomaticQuestionResult(card, question, progress, selectedOptionId) {
          var correctOption = automaticQuestionCorrectOption(question);
          card.querySelectorAll(".study-option").forEach(function(optionElement) {
            setStudyOptionResult(optionElement, "");
          });
          if (correctOption) {
            var correctElement = studyOptionElement(card, String(correctOption.option_id));
            setStudyOptionResult(correctElement, "correct");
          }
          if (progress.lastOutcome !== "correct") {
            var selectedElement = studyOptionElement(card, selectedOptionId);
            if (selectedElement) {
              setStudyOptionResult(
                selectedElement,
                progress.lastOutcome === "unknown" ? "unknown" : "incorrect"
              );
            }
          }
          var status = card.querySelector(".study-question-status");
          if (status) {
            status.setAttribute("data-outcome", progress.lastOutcome);
            status.innerHTML = '<span aria-hidden="true">' +
              studyOutcomeIcon(progress.lastOutcome) + "</span> " +
              escapeHtml(studyOutcomeText(progress.lastOutcome));
          }
          var feedbackHost = card.querySelector(".study-feedback-host");
          if (feedbackHost) {
            feedbackHost.innerHTML = automaticQuestionFeedbackHtml(question, progress);
          }
          var button = card.querySelector(".study-check-answer");
          if (button) { button.disabled = true; }
          card.setAttribute("data-last-submitted-option-id", selectedOptionId);
          if (window.MathJax && MathJax.typesetPromise) {
            MathJax.typesetPromise([card]).catch(function(err) {
              console.warn("MathJax study feedback typesetting failed:", err);
            });
          }
        }

        function submitAutomaticStudyQuestion(card) {
          if (!card) { return; }
          var questionId = String(card.getAttribute("data-question-id") || "");
          var indexed = studyQuestionIndex[questionId];
          var question = indexed && indexed.question;
          var selected = card.querySelector('input[type="radio"]:checked');
          if (!question || !selected) { return; }
          var selectedOptionId = String(selected.value || "");
          if (card.getAttribute("data-last-submitted-option-id") === selectedOptionId) {
            return;
          }
          var correctOption = automaticQuestionCorrectOption(question);
          var outcome = selectedOptionId === "__unknown__"
            ? "unknown"
            : (correctOption && selectedOptionId === String(correctOption.option_id)
              ? "correct"
              : "incorrect");
          var progress = recordStudyAttempt(questionId, outcome);
          if (!progress) { return; }
          applyAutomaticQuestionResult(card, question, progress, selectedOptionId);
        }

        function setStudyCardStatus(card, outcome) {
          var status = card && card.querySelector(".study-question-status");
          if (!status) { return; }
          status.setAttribute("data-outcome", outcome || "");
          status.innerHTML = outcome
            ? '<span aria-hidden="true">' + studyOutcomeIcon(outcome) + "</span> " +
              escapeHtml(studyOutcomeText(outcome))
            : "";
        }

        function typesetStudyCard(card) {
          if (window.MathJax && MathJax.typesetPromise) {
            MathJax.typesetPromise([card]).catch(function(err) {
              console.warn("MathJax study feedback typesetting failed:", err);
            });
          }
        }

        function renderSelfAssessedFeedback(card, question, progress, response, pending) {
          var feedbackHost = card.querySelector(".study-feedback-host");
          if (feedbackHost) {
            feedbackHost.innerHTML = selfAssessedQuestionFeedbackHtml(
              question,
              progress,
              response,
              pending
            );
          }
          typesetStudyCard(card);
        }

        function submitSelfAssessedQuestion(card) {
          if (!card) { return; }
          var questionId = String(card.getAttribute("data-question-id") || "");
          var indexed = studyQuestionIndex[questionId];
          var question = indexed && indexed.question;
          var textarea = card.querySelector(".study-self-response");
          var response = textarea ? String(textarea.value || "").trim() : "";
          var validation = card.querySelector(".study-response-validation");
          if (!question || !textarea) { return; }
          if (!response) {
            if (validation) { validation.textContent = "Enter an answer, or choose I don’t know."; }
            textarea.focus();
            return;
          }
          if (validation) { validation.textContent = ""; }
          card.setAttribute("data-pending-response", response);
          renderSelfAssessedFeedback(card, question, null, response, true);
          var checkButton = card.querySelector(".study-self-check-answer");
          if (checkButton) { checkButton.disabled = true; }
        }

        function markSelfAssessedQuestion(card, outcome) {
          if (!card || ["correct", "incorrect"].indexOf(outcome) === -1) { return; }
          var questionId = String(card.getAttribute("data-question-id") || "");
          var indexed = studyQuestionIndex[questionId];
          var question = indexed && indexed.question;
          var response = String(card.getAttribute("data-pending-response") || "");
          if (!question || !response) { return; }
          var progress = recordStudyAttempt(questionId, outcome);
          if (!progress) { return; }
          card.removeAttribute("data-pending-response");
          setStudyCardStatus(card, outcome);
          renderSelfAssessedFeedback(card, question, progress, response, false);
          var unknownButton = card.querySelector(".study-self-unknown");
          if (unknownButton) { unknownButton.disabled = true; }
        }

        function submitUnknownSelfAssessedQuestion(card) {
          if (!card) { return; }
          var questionId = String(card.getAttribute("data-question-id") || "");
          var indexed = studyQuestionIndex[questionId];
          var question = indexed && indexed.question;
          if (!question) { return; }
          var progress = recordStudyAttempt(questionId, "unknown");
          if (!progress) { return; }
          card.removeAttribute("data-pending-response");
          setStudyCardStatus(card, "unknown");
          renderSelfAssessedFeedback(card, question, progress, "", false);
          var checkButton = card.querySelector(".study-self-check-answer");
          var unknownButton = card.querySelector(".study-self-unknown");
          if (checkButton) { checkButton.disabled = true; }
          if (unknownButton) { unknownButton.disabled = true; }
        }

        function showConcept(nodeId, options) {
          options = options || {};
          hideConceptPreview(true);
          var concept = getConcept(nodeId);
          if (!concept) {
            currentConceptTocItems = [];
            setActiveConceptSection(null);
            var missingPanel = document.getElementById("info_panel");
            missingPanel.innerHTML =
              "<h2>" + escapeHtml(conceptDisplayId(nodeId)) + "</h2>" +
              "<p>No concept data was found for this node.</p>";
            missingPanel.setAttribute("data-concept-id", String(nodeId));
            missingPanel.removeAttribute("data-module-id");
            missingPanel.scrollTop = 0;
            typesetInfoPanel(options);
            return;
          }

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

          var panel = document.getElementById("info_panel");
          var retainedOpenSections = openTopLevelDetailIds(panel);
          var html = "";
          html += renderConceptMasthead(nodeId, concept, tocItems);
          html += renderConceptGraphic(nodeId, concept);
          html += "<hr>";
          html += renderConceptContent(nodeId, concept);
          html += renderConceptDerivedFrom(nodeId);
          html += renderConceptBacklinks(nodeId);
          if (studyQuestions.length > 0) {
            html += '<details id="' + escapeHtml(contentAnchorId(nodeId, "Study Questions")) +
              '" class="study-questions"' +
              (readingMode === "practice" ? " open" : "") + ">";
            html += "<summary>Study Questions</summary>";
            studyQuestions.forEach(function(item, index) {
              if (item && item.marking_mode === "automatic") {
                html += renderAutomaticStudyQuestion(item, index);
              } else {
                html += renderSelfAssessedStudyQuestion(item, index);
              }
            });
            html += renderNotesAtAnchor(
              "concept", nodeId, "Study Questions", 0, "",
              noteAnchorSpecs("", "study-questions", "Study Questions", "")[0]
            );
            html += "</details>";
          }
          html += renderUnmatchedNotes("concept", nodeId);
          if (conceptReferences.length > 0) {
            html += '<details id="' + escapeHtml(contentAnchorId(nodeId, "References")) +
              '" class="concept-references">';
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
          var previousPanelConceptId = panel.getAttribute("data-concept-id") || "";
          var conceptChanged = previousPanelConceptId !== String(nodeId);
          panel.innerHTML = html;
          applyReadingModeSectionState(
            panel,
            conceptChanged ? [] : retainedOpenSections
          );
          panel.setAttribute("data-concept-id", String(nodeId));
          panel.removeAttribute("data-module-id");
          if (conceptChanged && !options.scrollToSearchMatch) {
            panel.scrollTop = 0;
          }
          detailScrollSyncSuppressedUntil = Date.now() + 350;
          panel.classList.toggle("kg-note-editing", noteEditingEnabled);
          renderNotesOverview();
          openUserNoteId = null;
          var initialItem = initialTocItem(tocItems);
          setActiveConceptSection(initialItem ? initialItem.id : null);
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
            "<th>Direction</th>" +
            "<th>Category</th>" +
            "<th>Meaning</th>" +
            "<th>Example</th>" +
            "</tr></thead><tbody>";

          relations.forEach(function(relation) {
            var item = edgeKey[relation] || {};
            var colour = item.colour || "#999999";
            html += "<tr>" +
              '<td><strong class="edge-key-relation" style="color:' + escapeHtml(colour) + '">' +
              escapeHtml(relation) + "</strong></td>" +
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
        window.kgToggleControls = function() {
          var panel = document.getElementById("kg_controls");
          setControlsVisible(panel.classList.contains("kg-hidden"));
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
          updateLayoutControls();
        }

        function setActiveModuleItem(moduleId) {
          document.querySelectorAll(".kg-module-item.active").forEach(function(el) {
            el.classList.remove("active");
          });
          var item = Array.prototype.find.call(
            document.querySelectorAll(".kg-module-item"),
            function(el) { return el.getAttribute("data-module-id") === String(moduleId); }
          );
          if (item) {
            item.classList.add("active");
            item.scrollIntoView({block: "nearest"});
          }
          updateLayoutControls();
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
          var minWidth = Math.min(220, baseAbs.width * 0.65);
          var minHeight = Math.min(180, baseAbs.height * 0.65);
          visiblePanelRects().forEach(function(panel) {
            var overlap = intersectRects(baseAbs, panel.rect);
            if (!overlap) { return; }
            var edge = panelOcclusionEdge(panel, baseAbs, overlap);
            var candidate = Object.assign({}, availableAbs);
            if (edge === "left") { candidate.left = Math.max(candidate.left, overlap.right + margin); }
            if (edge === "right") { candidate.right = Math.min(candidate.right, overlap.left - margin); }
            if (edge === "top") { candidate.top = Math.max(candidate.top, overlap.bottom + margin); }
            if (edge === "bottom") { candidate.bottom = Math.min(candidate.bottom, overlap.top - margin); }
            if (
              candidate.right - candidate.left >= minWidth &&
              candidate.bottom - candidate.top >= minHeight
            ) {
              availableAbs = candidate;
            }
          });
          var availableWidth = availableAbs.right - availableAbs.left;
          var availableHeight = availableAbs.bottom - availableAbs.top;

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

            if (node.isModuleNode) {
              minX = Math.min(minX, pos.x - node.moduleFootprintWidth / 2);
              maxX = Math.max(maxX, pos.x + node.moduleFootprintWidth / 2);
              minY = Math.min(minY, pos.y - node.moduleFootprintHeight / 2);
              maxY = Math.max(maxY, pos.y + node.moduleFootprintHeight / 2);
              return;
            }

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
          var minScale = options.minScale === undefined ? 0.001 : Number(options.minScale);
          if (!Number.isFinite(maxScale) || maxScale <= 0) { maxScale = 0.7; }
          if (!Number.isFinite(minScale) || minScale <= 0) { minScale = 0.001; }

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

        function scheduleViewportRefresh() {
          requestAnimationFrame(updateNodeLabelPositions);
        }

        function handleViewportResize() {
          updateResponsiveControlLabels();
          updateGraphContextControls();
          applyWorkspaceSplit();
          scheduleViewportRefresh();
        }

        function schedulePanelContentRefresh() {
          requestAnimationFrame(function() {
            updateNodeLabelPositions();
          });
        }

        function schedulePanelContentRefit() {
          schedulePanelContentRefresh();
        }

        function selectViewerObject(type, id, statusPrefix, options) {
          options = options || {};
          type = type === "module" ? "module" : "concept";
          id = String(id);
          if ((type === "concept" && !getConcept(id)) || (type === "module" && !getModule(id))) {
            return;
          }

          var changed = activeNodeId !== (type === "concept" ? id : null) ||
            activeModuleId !== (type === "module" ? id : null);
          if (changed) { resetContextFitInteraction(); }
          closeInspection();
          clearTransientConceptHighlight({skipEdgeRestore: true});
          restoreHoveredEdge();
          hideNodeTooltip();
          if (changed) {
            activeConceptSectionTargetId = null;
          }

          activeNodeId = type === "concept" ? id : null;
          activeModuleId = type === "module" ? id : null;
          updateSelectedConceptHeader(activeNodeId);
          setActiveConceptItem(activeNodeId);
          setActiveModuleItem(activeModuleId);
          renderGraphFromViewerState({fit: false});

          if (type === "concept") {
            showConcept(id, {
              searchQuery: options.searchQuery,
              scrollToSearchMatch: options.scrollToSearchMatch
            });
            if (!options.skipHistory) {
              pushConceptHistory(id);
            }
          } else {
            showModule(id);
            if (!options.skipHistory) {
              pushModuleHistory(id);
            }
          }
          revealViewerSelection();

          if (statusPrefix) {
            var label = type === "concept"
              ? conceptDisplayId(id)
              : ((getModule(id) || {}).title || id) + " module";
            document.getElementById("kg_status").innerText = statusPrefix + " " + label + ".";
          }
          updateGraphContextControls();
        }

        function focusConcept(nodeId, statusPrefix, options) {
          selectViewerObject("concept", nodeId, statusPrefix, options);
        }

        function buildConceptList(filterText) {
          var q = searchDisplayText(filterText).toLowerCase();
          var results = rankedSearchResults(q);
          var html = "";
          var count = 0;

          results.forEach(function(result) {
            if (result.type === "concept") {
              var id = result.id;
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
            } else {
              var moduleId = result.id;
              var module = getModule(moduleId) || {};
              var title = searchDisplayText(module.title || moduleId);
              var titleHtml = '<span class="kg-search-hit-title">' +
                '<span class="kg-search-type-label">Module</span> ' +
                '<span class="kg-module-domain">' +
                escapeHtml(moduleDomainLabel(module.domain)) +
                "</span> " +
                highlightedSearchText(title, q) +
                "</span>";
              var snippetHtml = "";
              var snippets = matchingModuleSearchFields(moduleId, q).filter(function(field) {
                return field.name !== "Module ID" &&
                  field.name !== "Module" &&
                  field.name !== "Domain";
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
              html += '<button type="button" class="kg-module-item kg-module-search-item" data-module-id="' +
              escapeHtml(moduleId) +
              '">' +
              titleHtml +
              snippetHtml +
              "</button>";
            }
            count += 1;
          });

          if (count === 0) {
            html += '<div style="color:#555; padding:4px 0;">No matching concepts or modules.</div>';
          }
          document.getElementById("kg_concept_list").innerHTML = html;
          document.getElementById("kg_search_status").textContent = q ? count + " results" : "Browse all concepts";
        }

        function buildModuleList() {
          var list = document.getElementById("kg_module_list");
          if (!list) { return; }
          var ids = moduleIds();
          if (ids.length === 0) {
            list.innerHTML = '<div style="color:#555; padding:4px 0;">No modules loaded.</div>';
            return;
          }

          var html = "";
          ids.forEach(function(moduleId) {
            var module = getModule(moduleId) || {};
            var count = moduleMemberIds(module).length;
            var visualColor = moduleVisualColor(moduleId);
            html += '<button type="button" class="kg-module-item" data-module-id="' +
              escapeHtml(moduleId) + '" style="--module-background:' +
              escapeHtml(visualColor.background) + ';--module-border:' +
              escapeHtml(visualColor.border) + '">' +
              '<span class="kg-search-hit-title">' +
              '<span class="kg-module-swatch" aria-hidden="true"></span>' +
              '<span class="kg-module-domain">' +
              escapeHtml(moduleDomainLabel(module.domain)) +
              "</span> " +
              renderConceptText(module.title || moduleId) +
              "</span>" +
              '<span class="kg-module-count">' +
              count + " concept" + (count === 1 ? "" : "s") +
              "</span>" +
              "</button>";
          });
          list.innerHTML = html;
        }

        function renderInitialInfoPanel() {
          currentConceptTocItems = [];
          var panel = document.getElementById("info_panel");
          panel.innerHTML = "<h2>" + escapeHtml(defaultViewTitle) + "</h2><p>Select a concept or module, or double-click a module to expand it.</p>";
          panel.removeAttribute("data-concept-id");
          panel.removeAttribute("data-module-id");
          panel.classList.toggle("kg-note-editing", false);
          panel.scrollTop = 0;
        }

        function clearViewerSelection(options) {
          options = options || {};
          resetContextFitInteraction();
          closeInspection();
          clearTransientConceptHighlight({skipEdgeRestore: true});
          restoreHoveredEdge();
          hideNodeTooltip();
          activeNodeId = null;
          activeModuleId = null;
          activeConceptSectionTargetId = null;
          updateSelectedConceptHeader(null);
          setActiveConceptItem(null);
          setActiveModuleItem(null);
          network.unselectAll();
          renderGraphFromViewerState({fit: false});
          renderInitialInfoPanel();
          if (!options.skipHistory) {
            window.history.pushState({}, "", window.location.href.split("#")[0]);
          }
          document.getElementById("kg_status").innerText =
            "Selection cleared.";
        }

        window.kgClearSelection = function() {
          clearViewerSelection();
        };

        function focusModule(moduleId, statusPrefix, options) {
          selectViewerObject("module", moduleId, statusPrefix, options);
        }

        function navigateToConcept(nodeId, statusPrefix, options) {
          focusConcept(nodeId, statusPrefix, options);
        }

        window.kgSearch = function() {
          var q = searchDisplayText(document.getElementById("kg_search").value).toLowerCase();
          if (!q) { return; }

          var results = rankedSearchResults(q);
          var matchCount = results.length;

          if (matchCount === 0) {
            document.getElementById("kg_status").innerText = "No matching concept or module found.";
            return;
          }

          buildConceptList(q);
          if (results[0].type === "concept") {
            var id = results[0].id;
            var concept = getConcept(id) || {};
            focusConcept(id, null, {
              searchQuery: q,
              scrollToSearchMatch: true
            });
            document.getElementById("kg_status").innerText =
              "Found " + matchCount + " match(es). Showing first: " + (concept.label || id);
            return;
          }

          var moduleId = results[0].id;
          var module = getModule(moduleId) || {};
          focusModule(moduleId, null);
          document.getElementById("kg_status").innerText =
            "Found " + matchCount + " match(es). Showing first: " + (module.title || moduleId);
        };

        var lastGraphRender = null;

        function renderGraphFromViewerState() {
          clearProjectedModuleEdges();
          var selection = viewerSelectionSnapshot();
          var scope = viewerState.displayScope;
          var context = computeViewerContext(selection, viewerState.contextRule);
          var included = {};
          if (scope === DisplayScope.FULL) {
            Object.keys(originalNodes).forEach(function(id) { included[String(id)] = true; });
          } else if (scope === DisplayScope.CONTEXT) {
            context.nodeIds.forEach(function(id) { included[String(id)] = true; });
          }

          nodes.update(allNodes.map(function(node) {
            var rendered = baseNodeForRender(node.id);
            var id = String(node.id);
            var inContext = context.keep[id] === true;
            var overview = scope === DisplayScope.FULL && selection.type === "none";
            rendered.hidden = scope === DisplayScope.HIDDEN || !included[id];
            rendered.opacity = inContext || overview ? 1.0 : 0.34;
            rendered.font = Object.assign({}, rendered.font || {}, {
              color: inContext || overview ? "#111111" : "#8a94a3"
            });
            if (!inContext && !overview) {
              rendered.visualColor = {background: "#f2f2f2", border: "#c7cdd4"};
            }
            return applyCollisionNodeStyle(rendered);
          }));

          edges.update(allEdges.map(function(edge) {
            var rendered = Object.assign({}, originalEdges[edge.id]);
            var inContext = context.edgeKeep[String(edge.id)] === true;
            var endpointsIncluded = included[String(edge.from)] && included[String(edge.to)];
            var overview = scope === DisplayScope.FULL && selection.type === "none";
            rendered.kgContextEdge = inContext;
            rendered.kgOverviewEdge = overview;
            if (scope === DisplayScope.HIDDEN || !endpointsIncluded) {
              return setEdgeHidden(rendered, true);
            }
            if (inContext) {
              rendered.color = Object.assign({}, rendered.color || {}, {opacity: 0.95});
              rendered.width = Math.max(Number(rendered.width) || 0, 3.0);
              return setEdgeHidden(rendered, false);
            }
            if (scope === DisplayScope.FULL) {
              if (overview) {
                rendered.color = Object.assign({}, rendered.color || {}, {opacity: 0.78});
                rendered.width = Math.max(Number(rendered.width) || 0, 1.5);
                return setEdgeHidden(rendered, false);
              }
              rendered.color = {
                color: "#aeb5bf",
                highlight: "#aeb5bf",
                hover: "#aeb5bf",
                opacity: 0.16
              };
              rendered.width = 0.5;
              rendered = setEdgeHidden(rendered, false);
              return setEdgeTooltipEnabled(rendered, false);
            }
            return setEdgeHidden(rendered, true);
          }));

          var fitIds = [];
          if (scope !== DisplayScope.HIDDEN) {
            fitIds = applyFoldedModuleOverlay(Object.keys(included), {
              compact: scope === DisplayScope.CONTEXT
            });
          } else {
            foldedModuleIdList().forEach(function(moduleId) {
              var moduleNodeId = moduleGraphNodeId(moduleId);
              if (nodes.get(moduleNodeId)) { nodes.update({id: moduleNodeId, hidden: true}); }
            });
          }

          network.unselectAll();
          if (selection.type === "concept" && visibleGraphNode(selection.id)) {
            network.selectNodes([selection.id]);
          } else if (selection.type === "concept") {
            var containingModuleId = moduleIdForConcept(selection.id);
            var containingModuleNodeId = containingModuleId
              ? moduleGraphNodeId(containingModuleId)
              : null;
            if (
              containingModuleId && selectedModuleIsFolded(containingModuleId) &&
              nodes.get(containingModuleNodeId) && !nodes.get(containingModuleNodeId).hidden
            ) {
              network.selectNodes([containingModuleNodeId]);
            }
          } else if (
            selection.type === "module" &&
            selectedModuleIsFolded(selection.id) &&
            nodes.get(moduleGraphNodeId(selection.id))
          ) {
            network.selectNodes([moduleGraphNodeId(selection.id)]);
          }

          lastGraphRender = {
            selection: selection,
            scope: scope,
            contextNodeIds: context.nodeIds.slice(),
            contextEdgeIds: context.edgeIds.slice(),
            includedNodeIds: Object.keys(included).sort(),
            fitIds: fitIds.slice()
          };
          updateNodeLabelPositions();
          updateGraphContextControls();
          return lastGraphRender;
        }

        window.kgDisplayedGraphSnapshot = function() {
          return lastGraphRender ? JSON.parse(JSON.stringify(lastGraphRender)) : null;
        };

        function applyFoldedModuleOverlay(baseVisibleIds, options) {
          options = options || {};
          var compact = options.compact === true;
          var foldedIds = foldedModuleIdList();
          clearProjectedModuleEdges();
          if (foldedIds.length === 0) {
            return baseVisibleIds.slice();
          }

          var baseVisible = {};
          var hiddenMembers = {};
          var fitIds = [];
          baseVisibleIds.forEach(function(id) {
            baseVisible[String(id)] = true;
          });

          baseVisibleIds.forEach(function(id) {
            var owningModuleId = moduleIdForConcept(id);
            if (!owningModuleId || !selectedModuleIsFolded(owningModuleId)) {
              fitIds.push(String(id));
            }
          });

          foldedIds.forEach(function(moduleId) {
            var memberIds = moduleMemberIds(getModule(moduleId));
            var represented = !compact || activeModuleId === moduleId;
            syncFoldedModulePosition(moduleId);
            memberIds.forEach(function(id) {
              hiddenMembers[String(id)] = true;
              if (baseVisible[String(id)]) {
                represented = true;
              }
            });

            var graphNodeId = moduleGraphNodeId(moduleId);
            if (represented) {
              var moduleNode = moduleGraphNode(moduleId);
              if (nodes.get(graphNodeId)) {
                nodes.update(moduleNode);
              } else {
                nodes.add(moduleNode);
              }
              // DataSet updates truncate x/y in vis-network; dragging does not.
              network.moveNode(graphNodeId, moduleNode.x, moduleNode.y);
              fitIds.push(graphNodeId);
            } else if (nodes.get(graphNodeId)) {
              nodes.update({id: graphNodeId, hidden: true});
            }
          });

          nodes.update(Object.keys(hiddenMembers).filter(function(id) {
            return Boolean(nodes.get(id));
          }).map(function(id) {
            return {id: id, hidden: true};
          }));

          var moduleEdges = projectedModuleEdges(hiddenMembers);
          edges.update(allEdges.filter(function(e) {
            return hiddenMembers[String(e.from)] || hiddenMembers[String(e.to)];
          }).map(function(e) {
            var current = edges.get(e.id) || originalEdges[e.id] || e;
            return setEdgeHidden(Object.assign({}, current), true);
          }));
          if (moduleEdges.length > 0) {
            edges.add(moduleEdges);
          }

          return fitIds.filter(function(id, index, ids) {
            return ids.indexOf(id) === index;
          });
        }

        /* Browser event wiring. */
        network.on("click", function(params) {
            cancelPendingContainedConceptModuleSelection();
            if (params.nodes.length === 0 && params.edges && params.edges.length > 0) {
                showEdgeDetails(params.edges[0]);
                return;
            }

            if (params.nodes.length === 0) {
                var recentNodeId = recentGraphClickNodeId(500);
                if (recentNodeId && handleGraphNodeDoubleClick(recentNodeId)) {
                  return;
                }
                return;
            }

            const nodeId = params.nodes[0];
            if (graphNodeClickIsDoubleClick(nodeId) && handleGraphNodeDoubleClick(nodeId)) {
              return;
            }
            const clickedModuleId = moduleIdFromGraphNodeId(nodeId);
            if (clickedModuleId && getModule(clickedModuleId)) {
              if (deferModuleSelectionForContainedConcept(clickedModuleId)) {
                return;
              }
              focusModule(clickedModuleId, "Selected");
              return;
            }

            focusConcept(nodeId, "Selected");
        });

        network.on("doubleClick", function(params) {
          if (!params.nodes || params.nodes.length === 0) { return; }
          if (nativeDoubleClickIsSuppressed(params.nodes[0])) { return; }
          handleGraphNodeDoubleClick(params.nodes[0]);
        });

        network.on("hoverNode", function(params) {
          showNodeTooltip(params.node, params.pointer);
        });

        network.on("blurNode", hideNodeTooltip);

        network.on("hoverEdge", function(params) {
          if (params.edge !== undefined && params.edge !== null) {
            highlightHoveredEdge(params.edge);
            showEdgeTooltip(params.edge, params.pointer);
          }
        });

        network.on("blurEdge", function(params) {
          if (params.edge === hoveredEdgeId) {
            restoreHoveredEdge();
          }
          hideNodeTooltip();
        });

        function updateRenderedEdgeWidths() {
          var scale = network.getScale();
          if (!isFinite(scale) || scale <= 0) { return; }
          edges.get().forEach(function(edge) {
            var rendered = network.body.edges[edge.id];
            if (!rendered || edge.hidden) { return; }
            var width = Number(edge.width) || 1;
            var base = edge.isModuleEdge ? Number(edge.kgBaseWidth)
              : Number((originalEdges[edge.id] || {}).width);
            base = base > 0 ? base : width;
            // Keep a readable screen-space minimum while retaining hover emphasis.
            // Change only the native drawing options, never the authored DataSet.
            var minimumPixels = edge.isModuleEdge ? 1.8 : 1.5;
            if (String(edge.id) === String(hoveredEdgeId)) {
              minimumPixels *= 2;
            }
            rendered.options.width = scale < 1
              ? Math.max(width, minimumPixels / scale)
              : width;
          });
        }

        network.on("beforeDrawing", updateRenderedEdgeWidths);
        network.on("afterDrawing", function(ctx) {
          drawFoldedModuleGraphics(ctx);
          drawVisibleNodes(ctx);
          updateNodeLabelPositions();
        });
        network.on("dragEnd", function(params) {
          updateLayoutFromDrag(params);
          updateNodeLabelPositions();
        });
        network.on("zoom", updateNodeLabelPositions);
        network.on("animationFinished", updateNodeLabelPositions);
        window.addEventListener("resize", handleViewportResize);
        window.addEventListener("orientationchange", handleViewportResize);
        if (window.visualViewport) {
          window.visualViewport.addEventListener("resize", handleViewportResize);
          window.visualViewport.addEventListener("scroll", scheduleViewportRefresh);
        }
        graphContainer.addEventListener("mouseleave", function() {
          restoreHoveredEdge();
          hideNodeTooltip();
        });

        var graphCanvas = network.canvas && network.canvas.frame
          ? network.canvas.frame.canvas
          : null;
        var lockedDragProbe = null;
        var lockedLayoutNoticeShown = false;
        var touchTapStart = null;
        var lastTouchTap = null;
        function graphNodeAtPointerEvent(e) {
          if (!network.getNodeAt || viewerState.displayScope === DisplayScope.HIDDEN) { return null; }
          var surface = graphCanvas || graphContainer;
          var rect = surface.getBoundingClientRect();
          return network.getNodeAt({x: e.clientX - rect.left, y: e.clientY - rect.top});
        }
        (graphCanvas || graphContainer).addEventListener("pointerdown", function(e) {
          if (layoutDraggingEnabled()) { return; }
          var nodeId = graphNodeAtPointerEvent(e);
          lockedDragProbe = nodeId ? {x: e.clientX, y: e.clientY} : null;
        }, true);
        (graphCanvas || graphContainer).addEventListener("pointermove", function(e) {
          if (!lockedDragProbe || layoutDraggingEnabled()) { return; }
          if (Math.hypot(e.clientX - lockedDragProbe.x, e.clientY - lockedDragProbe.y) < 5) { return; }
          if (!lockedLayoutNoticeShown) {
            lockedLayoutNoticeShown = true;
            showTransientContextNotice(
              "Layout locked — enable editing in Tools → Layouts.",
              "layout-locked",
              2800
            );
          }
          lockedDragProbe = null;
        }, true);
        ["pointerup", "pointercancel", "pointerleave"].forEach(function(eventName) {
          (graphCanvas || graphContainer).addEventListener(eventName, function() {
            lockedDragProbe = null;
          }, true);
        });
        (graphCanvas || graphContainer).addEventListener("pointerdown", function(e) {
          if (e.pointerType !== "touch") { return; }
          touchTapStart = {
            pointerId: e.pointerId,
            x: e.clientX,
            y: e.clientY,
            time: Date.now()
          };
        }, true);
        (graphCanvas || graphContainer).addEventListener("pointerup", function(e) {
          if (e.pointerType !== "touch" || !touchTapStart ||
              touchTapStart.pointerId !== e.pointerId) {
            return;
          }
          var now = Date.now();
          var moved = Math.hypot(e.clientX - touchTapStart.x, e.clientY - touchTapStart.y);
          var duration = now - touchTapStart.time;
          touchTapStart = null;
          if (moved > 14 || duration > 400) {
            lastTouchTap = null;
            return;
          }
          var isDoubleTap = Boolean(
            lastTouchTap &&
            now - lastTouchTap.time <= 500 &&
            Math.hypot(e.clientX - lastTouchTap.x, e.clientY - lastTouchTap.y) <= 28
          );
          lastTouchTap = {x: e.clientX, y: e.clientY, time: now};
          if (!isDoubleTap) { return; }
          lastTouchTap = null;
          var surface = graphCanvas || graphContainer;
          var rect = surface.getBoundingClientRect();
          var nodeId = graphNodeAtPointerEvent(e);
          var handled = nodeId ? handleGraphNodeDoubleClick(nodeId) : false;
          if (!handled) {
            handled = collapseExpandedModuleAtDomPoint({
              x: e.clientX - rect.left,
              y: e.clientY - rect.top
            });
          }
          if (handled) {
            e.preventDefault();
            e.stopImmediatePropagation();
          }
        }, true);
        (graphCanvas || graphContainer).addEventListener("pointercancel", function(e) {
          if (e.pointerType === "touch") {
            touchTapStart = null;
            lastTouchTap = null;
          }
        }, true);
        (graphCanvas || graphContainer).addEventListener("dblclick", function(e) {
          if (viewerState.displayScope === DisplayScope.HIDDEN || !network.getNodeAt) { return; }
          var rect = (graphCanvas || graphContainer).getBoundingClientRect();
          var nodeId = network.getNodeAt({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
          }) || recentGraphClickNodeId(800);
          if (nativeDoubleClickIsSuppressed(nodeId)) {
            e.preventDefault();
            e.stopPropagation();
            return;
          }
          if (toggleModuleFoldForGraphNode(nodeId)) {
            e.preventDefault();
            e.stopPropagation();
            return;
          }
          if (collapseExpandedModuleAtDomPoint({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
          })) {
            e.preventDefault();
            e.stopPropagation();
          }
        }, true);

        window.addEventListener("popstate", function(event) {
          var nodeId = event.state && event.state.nodeId;
          var moduleId = event.state && event.state.moduleId;
          if (!nodeId) {
            nodeId = conceptIdFromHash(window.location.hash);
          }
          if (!moduleId) {
            moduleId = moduleIdFromHash(window.location.hash);
          }

          if (moduleId && getModule(moduleId)) {
            focusModule(moduleId, null, {skipHistory: true});
          } else if (nodeId && getConcept(nodeId)) {
            focusConcept(nodeId, null, {skipHistory: true});
          } else {
            clearViewerSelection({skipHistory: true});
          }
        });

        document.addEventListener("keydown", allowBrowserHistoryShortcut, true);

        function setSearchOpen(open) {
          document.getElementById("kg_search_section").open = open;
          document.getElementById("kg_search_toggle").setAttribute("aria-expanded", String(open));
          document.getElementById(open ? "kg_search" : "kg_search_toggle").focus();
        }

        document.getElementById("kg_search_toggle").addEventListener("click", function() {
          setSearchOpen(!document.getElementById("kg_search_section").open);
        });
        document.getElementById("kg_search_close").addEventListener("click", function() {
          setSearchOpen(false);
        });
        document.getElementById("kg_search_section").addEventListener("toggle", function(e) {
          document.getElementById("kg_search_toggle").setAttribute("aria-expanded", String(e.target.open));
        });
        document.getElementById("kg_search_section").addEventListener("keydown", function(e) {
          if (e.key === "Escape") { e.preventDefault(); setSearchOpen(false); }
        });

        document.getElementById("kg_search").addEventListener("keydown", function(e) {
          if (e.key === "Enter") { kgSearch(); }
          if (e.key === "ArrowDown") {
            var first = document.querySelector("#kg_concept_list button");
            if (first) { e.preventDefault(); first.focus(); }
          }
        });

        document.getElementById("kg_search").addEventListener("input", function(e) {
          buildConceptList(e.target.value);
        });

        document.getElementById("kg_display_scope_select").addEventListener("change", function(e) {
          setViewerDisplayScope(e.target.value);
        });

        document.getElementById("kg_clear_selection").addEventListener("click", function(e) {
          e.preventDefault();
          kgClearSelection();
        });

        document.getElementById("kg_details_view_select").addEventListener("change", function(e) {
          setDetailsView(e.target.value);
        });

        document.getElementById("kg_study_list").addEventListener("click", function(e) {
          var reset = e.target.closest(".kg-study-reset-question");
          if (reset) {
            e.preventDefault();
            var resetQuestionId = reset.getAttribute("data-question-id");
            var resetIndexed = studyQuestionIndex[resetQuestionId];
            if (resetStudyQuestion(resetQuestionId) && resetIndexed &&
                activeNodeId === resetIndexed.conceptId) {
              refreshActiveConcept();
            }
            return;
          }
          var questionLink = e.target.closest(".kg-study-question-link");
          if (!questionLink) { return; }
          e.preventDefault();
          openScorecardQuestion(questionLink.getAttribute("data-question-id"));
        });
        document.getElementById("kg_study_reset_all").addEventListener("click", function() {
          if (!window.confirm("Reset all study progress?")) { return; }
          resetAllStudyProgress();
          refreshActiveConcept();
        });
        window.addEventListener("kg:study-progress-changed", renderStudyScorecard);

        document.getElementById("kg_context_preset_select").addEventListener("change", function(e) {
          var preset = e.target.value;
          var customPanel = document.getElementById("kg_custom_context");
          if (preset === ContextPreset.CUSTOM) {
            openCustomContextEditor();
            return;
          }
          customPanel.hidden = true;
          setViewerContextRule({preset: preset, depth: viewerState.contextRule.depth});
        });
        document.getElementById("kg_context_depth_select").addEventListener("change", function(e) {
          setViewerContextRule({
            preset: viewerState.contextRule.preset,
            depth: e.target.value,
            customTraversals: viewerState.contextRule.customTraversals
          });
        });
        document.getElementById("kg_fit_select").addEventListener("change", function() {
          clearContextFitPriming();
        });
        document.getElementById("kg_fit_apply").addEventListener("click", function() {
          fitViewerTarget(document.getElementById("kg_fit_select").value);
        });
        document.getElementById("kg_custom_context_apply").addEventListener("click", function() {
          var traversals = Array.from(
            document.querySelectorAll("#kg_custom_context_rules input:checked")
          ).map(function(input) {
            return {
              relation: input.getAttribute("data-relation"),
              direction: input.getAttribute("data-direction")
            };
          });
          document.getElementById("kg_custom_context").hidden = true;
          setViewerContextRule({
            preset: ContextPreset.CUSTOM,
            depth: document.getElementById("kg_context_depth_select").value,
            customTraversals: traversals
          });
        });
        document.getElementById("kg_custom_context_edit").addEventListener("click", function() {
          openCustomContextEditor();
        });
        document.getElementById("kg_custom_context_cancel").addEventListener("click", function() {
          document.getElementById("kg_custom_context").hidden = true;
          document.getElementById("kg_context_preset_select").value = viewerState.contextRule.preset;
        });
        document.getElementById("kg_expand_selected_module").addEventListener("click", function() {
          var actions = document.getElementById("kg_representation_actions");
          var moduleId = actions.getAttribute("data-selected-module-id");
          if (moduleId && getModule(moduleId)) {
            setSelectedModuleFoldState(moduleId, false);
          }
        });
        document.getElementById("kg_expand_context_modules").addEventListener("click", function() {
          resetContextFitInteraction();
          var contextIds = lastGraphRender ? lastGraphRender.contextNodeIds : [];
          var changed = false;
          contextIds.forEach(function(conceptId) {
            var moduleId = moduleIdForConcept(conceptId);
            if (!moduleId || !selectedModuleIsFolded(moduleId)) { return; }
            preferredFoldedModules[String(moduleId)] = false;
            unfoldModule(moduleId);
            changed = true;
          });
          if (changed) { refreshGraphAfterModuleFoldChange(); }
        });
        document.getElementById("kg_inspection_close").addEventListener("click", closeInspection);
        document.getElementById("kg_inspection_dialog").addEventListener("click", function(e) {
          if (e.target === this) { closeInspection(); }
        });
        document.getElementById("kg_inspection_body").addEventListener("click", function(e) {
          var conceptButton = e.target.closest(".edge-detail-concept");
          if (!conceptButton) { return; }
          e.preventDefault();
          closeInspection();
          navigateToConcept(conceptButton.getAttribute("data-edge-concept-id"), "Selected");
        });

        document.getElementById("kg_splash_dismiss").addEventListener("click", dismissSplash);

        try {
          var personalImportStatus = window.sessionStorage.getItem(
            "srkg.personalData.importStatus"
          );
          if (personalImportStatus) {
            setPersonalDataStatus(personalImportStatus);
            window.sessionStorage.removeItem("srkg.personalData.importStatus");
          }
        } catch (err) { /* status remains the local-storage default */ }

        document.getElementById("kg_personal_data_export").addEventListener("click", function() {
          exportPersonalData();
        });
        document.getElementById("kg_personal_data_import_button").addEventListener("click", function() {
          document.getElementById("kg_personal_data_import_input").click();
        });
        document.getElementById("kg_personal_data_import_input").addEventListener("change", function(e) {
          var file = e.target.files && e.target.files[0];
          if (!file) { return; }
          file.arrayBuffer().then(function(buffer) {
            showPersonalDataImport(window.kgPersonalDataArchive.importBytes(buffer));
          }).catch(function() {
            setPersonalDataStatus("Could not import this personal-data archive.");
          }).finally(function() {
            e.target.value = "";
          });
        });
        document.getElementById("kg_personal_data_import_cancel").addEventListener(
          "click", closePersonalDataImport
        );
        document.getElementById("kg_personal_data_import_apply").addEventListener(
          "click", applyPersonalDataImport
        );

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
          var targetType = item.getAttribute("data-target-type");
          var targetId = item.getAttribute("data-target-id");
          if (!note) { return; }
          openUserNoteId = note.id;
          if (targetType === "module" && getModule(targetId)) {
            focusModule(targetId, "Selected");
          } else if (targetType === "concept" && getConcept(targetId)) {
            focusConcept(targetId, "Selected");
          }
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
              var unresolved = unresolvedNoteCount();
              setNotesStatus(
                "Imported " + count + " note(s)." +
                (unresolved ? " " + unresolved + " need placement." : "")
              );
              refreshActiveConcept();
            } catch (err) {
              setNotesStatus("Could not import notes CSV.");
            }
            e.target.value = "";
          };
          reader.readAsText(file);
        });

        document.getElementById("kg_concept_list").addEventListener("click", function(e) {
          var moduleItem = e.target.closest(".kg-module-search-item");
          if (moduleItem) {
            e.preventDefault();
            focusModule(moduleItem.getAttribute("data-module-id"), "Selected");
            return;
          }

          var item = e.target.closest(".kg-concept-item");
          if (!item) { return; }

          e.preventDefault();
          focusConcept(item.getAttribute("data-concept-id"), "Selected", {
            searchQuery: document.getElementById("kg_search").value,
            scrollToSearchMatch: true
          });
        });

        document.getElementById("kg_modules_collapse_all").addEventListener("click", function(e) {
          e.preventDefault();
          foldAllModules();
        });

        document.getElementById("kg_modules_expand_all").addEventListener("click", function(e) {
          e.preventDefault();
          unfoldAllModules();
        });

        document.getElementById("kg_layout_edit_toggle").addEventListener("change", function(e) {
          setLayoutEditingEnabled(e.target.checked);
        });

        document.getElementById("kg_layout_edit_persistence").addEventListener("change", function(e) {
          setLayoutEditPersistence(e.target.value);
        });

        document.getElementById("kg_layout_export").addEventListener("click", function(e) {
          e.preventDefault();
          exportGlobalLayout();
        });

        document.getElementById("kg_layout_reset").addEventListener("click", function(e) {
          e.preventDefault();
          resetToPublishedLayout();
        });

        document.getElementById("kg_layout_keep").addEventListener("click", function(e) {
          e.preventDefault();
          keepPersonalLayout();
        });

        document.getElementById("kg_layout_warning_reset").addEventListener("click", function(e) {
          e.preventDefault();
          resetToPublishedLayout();
        });

        document.getElementById("kg_module_list").addEventListener("click", function(e) {
          var item = e.target.closest(".kg-module-item");
          if (!item) { return; }

          e.preventDefault();
          focusModule(item.getAttribute("data-module-id"), "Selected");
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

        document.getElementById("info_panel").addEventListener("click", function(e) {
          var selfCheckButton = e.target.closest(".study-self-check-answer");
          if (selfCheckButton) {
            e.preventDefault();
            submitSelfAssessedQuestion(selfCheckButton.closest(".study-question-self-assessed"));
            return;
          }

          var selfUnknownButton = e.target.closest(".study-self-unknown");
          if (selfUnknownButton) {
            e.preventDefault();
            submitUnknownSelfAssessedQuestion(
              selfUnknownButton.closest(".study-question-self-assessed")
            );
            return;
          }

          var selfMarkButton = e.target.closest(".study-self-mark");
          if (selfMarkButton) {
            e.preventDefault();
            markSelfAssessedQuestion(
              selfMarkButton.closest(".study-question-self-assessed"),
              selfMarkButton.getAttribute("data-outcome")
            );
            return;
          }

          var studyCheckButton = e.target.closest(".study-check-answer");
          if (studyCheckButton) {
            e.preventDefault();
            submitAutomaticStudyQuestion(studyCheckButton.closest(".study-question-automatic"));
            return;
          }

          var relationshipGraphButton = e.target.closest(".concept-relationship-show-graph");
          if (relationshipGraphButton) {
            e.preventDefault();
            var relationshipSection = relationshipGraphButton.closest("details");
            var fullTreeToggle = relationshipSection
              ? relationshipSection.querySelector(".concept-full-tree-toggle input")
              : null;
            showRelationshipSectionInGraph(
              relationshipGraphButton.getAttribute("data-context-preset"),
              Boolean(fullTreeToggle && fullTreeToggle.checked)
            );
            return;
          }

          var tocLink = e.target.closest(".concept-toc-link");
          if (tocLink) {
            e.preventDefault();
            var tocTargetId = tocLink.getAttribute("data-toc-target");
            var target = document.getElementById(tocTargetId);
            if (target) {
              setActiveConceptSection(tocTargetId);
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
            if (!noteEditingEnabled) { return; }
            var enclosingSection = addNoteButton.closest("#info_panel > details");
            var enclosingSectionId = enclosingSection && enclosingSection.open
              ? enclosingSection.id
              : "";
            createUserNote(
              addNoteButton.getAttribute("data-target-type") || "concept",
              addNoteButton.getAttribute("data-target-id") || activeNodeId,
              addNoteButton.getAttribute("data-section") || "",
              Number(addNoteButton.getAttribute("data-anchor-index")) || 0,
              addNoteButton.getAttribute("data-anchor-after") || "",
              {
                blockId: addNoteButton.getAttribute("data-anchor-block-id") || "",
                sectionKey: addNoteButton.getAttribute("data-anchor-section-key") || "",
                contextBefore: addNoteButton.getAttribute("data-anchor-context-before") || "",
                contextAfter: addNoteButton.getAttribute("data-anchor-context-after") || ""
              }
            );
            refreshActiveConcept();
            if (enclosingSectionId) {
              var refreshedSection = document.getElementById(enclosingSectionId);
              if (refreshedSection) { refreshedSection.open = true; }
            }
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

          var moduleFoldButton = e.target.closest(".module-graph-fold-button");
          if (moduleFoldButton) {
            e.preventDefault();
            var foldModuleId = moduleFoldButton.getAttribute("data-module-id");
            var foldState = moduleFoldButton.getAttribute("data-module-fold-state");
            if (!getModule(foldModuleId)) { return; }
            setSelectedModuleFoldState(foldModuleId, foldState === "folded");
            return;
          }

          var moduleButton = e.target.closest(".module-detail-link");
          if (moduleButton) {
            e.preventDefault();
            var moduleId = moduleButton.getAttribute("data-module-id");
            if (!getModule(moduleId)) { return; }
            focusModule(moduleId, "Selected");
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
          var readToggle = e.target.closest(".content-block-read-toggle");
          if (readToggle) {
            var contentBlock = readToggle.closest("[data-content-block-id]");
            if (contentBlock) {
              setContentBlockRead(
                contentBlock.getAttribute("data-content-block-id"),
                readToggle.checked
              );
            }
            return;
          }

          var studyResponse = e.target.closest(
            '.study-question-automatic input[type="radio"]'
          );
          if (studyResponse) {
            var studyCard = studyResponse.closest(".study-question-automatic");
            var studyButton = studyCard ? studyCard.querySelector(".study-check-answer") : null;
            if (studyButton) { studyButton.disabled = false; }
            if (studyCard) {
              studyCard.querySelectorAll(
                '.study-option[data-result="incorrect"], .study-option[data-result="unknown"]'
              ).forEach(function(optionElement) {
                optionElement.removeAttribute("data-result");
              });
            }
            return;
          }

          var derivedFromFullTree = e.target.closest(".concept-derived-from-full-tree");
          if (derivedFromFullTree) {
            var derivedSection = derivedFromFullTree.closest(".concept-derived-from");
            var derivedSectionId = derivedSection ? derivedSection.id : null;
            derivedFromFullTreeEnabled = derivedFromFullTree.checked;
            refreshActiveConcept();
            detailScrollSyncSuppressedUntil = Date.now() + 1000;
            setActiveConceptSection(derivedSectionId);
            return;
          }

          var backlinksFullTree = e.target.closest(".concept-backlinks-full-tree");
          if (backlinksFullTree) {
            var backlinksSection = backlinksFullTree.closest(".concept-backlinks");
            var backlinksSectionId = backlinksSection ? backlinksSection.id : null;
            backlinksFullTreeEnabled = backlinksFullTree.checked;
            refreshActiveConcept();
            detailScrollSyncSuppressedUntil = Date.now() + 1000;
            setActiveConceptSection(backlinksSectionId);
          }
        });

        document.getElementById("info_panel").addEventListener("input", function(e) {
          var studyResponse = e.target.closest(".study-self-response");
          if (studyResponse) {
            var studyCard = studyResponse.closest(".study-question-self-assessed");
            var questionId = studyCard
              ? String(studyCard.getAttribute("data-question-id") || "")
              : "";
            var indexed = studyQuestionIndex[questionId];
            var question = indexed && indexed.question;
            var progress = studyProgressState.questions[questionId] || null;
            var checkButton = studyCard
              ? studyCard.querySelector(".study-self-check-answer")
              : null;
            var unknownButton = studyCard
              ? studyCard.querySelector(".study-self-unknown")
              : null;
            var validation = studyCard
              ? studyCard.querySelector(".study-response-validation")
              : null;
            if (checkButton) { checkButton.disabled = false; }
            if (unknownButton) { unknownButton.disabled = false; }
            if (validation) { validation.textContent = ""; }
            if (studyCard && question && studyCard.hasAttribute("data-pending-response")) {
              studyCard.removeAttribute("data-pending-response");
              renderSelfAssessedFeedback(studyCard, question, progress, "", false);
            }
            return;
          }

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
            schedulePanelContentRefit();
          }
        }, true);

        /* Initial render. */
        applyDefaultModuleFoldState();
        buildNodeLabels();
        refreshModuleFootprints();
        if (document.fonts && document.fonts.addEventListener) {
          document.fonts.addEventListener("loadingdone", refreshModuleFootprints);
        }
        buildConceptList("");
        buildModuleList();
        migrateUserNotesState();
        renderNotesOverview();
        renderStudyScorecard();
        updateResponsiveControlLabels();
        updateGraphViewControls();
        updateDetailsViewControls();
        renderCustomContextRules();
        updateGraphContextControls();
        setControlsVisible(!shouldStartWithControlsHidden());
        edges.update(allEdges.map(function(e) {
          var o = Object.assign({}, e);
          return setEdgeHidden(o, false);
        }));
        // Context computation and relationship details retain the complete
        // authored edge set; rendering applies the selected display policy.
        renderGraphFromViewerState();

        var initialModuleId = moduleIdFromHash(window.location.hash);
        var initialNodeId = conceptIdFromHash(window.location.hash);
        if (initialModuleId && getModule(initialModuleId)) {
          window.history.replaceState(
            {
              objectType: "module",
              moduleId: String(initialModuleId)
            },
            "",
            moduleHash(initialModuleId)
          );
          focusModule(initialModuleId, "Selected", {skipHistory: true});
        } else if (initialNodeId && getConcept(initialNodeId)) {
          window.history.replaceState(
            {
              objectType: "concept",
              nodeId: String(initialNodeId)
            },
            "",
            conceptHash(initialNodeId)
          );
          focusConcept(initialNodeId, "Selected", {skipHistory: true});
        } else {
          var defaultNodeId = defaultStartupConceptId && getConcept(defaultStartupConceptId) ?
            defaultStartupConceptId : null;
          if (defaultNodeId) {
            window.history.replaceState(
              {
                objectType: "concept",
                nodeId: String(defaultNodeId)
              },
              "",
              conceptHash(defaultNodeId)
            );
            focusConcept(defaultNodeId, "Selected", {skipHistory: true});
          } else {
            window.history.replaceState({}, "", window.location.href);
          }
        }
        requestAnimationFrame(function() {
          requestAnimationFrame(function() {
            if (lastGraphRender && lastGraphRender.fitIds.length > 0) {
              fitNodesToAvailableRect(lastGraphRender.fitIds, {
                maxScale: viewerState.displayScope === DisplayScope.CONTEXT ? 0.85 : 0.72,
                animation: false
              });
            }
          });
        });
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
    
