      /* Runtime data injected by srkg.html_injection. */
      var conceptData = __CONCEPT_DATA__;
      var moduleData = __MODULE_DATA__;
      var publishedLayout = __PUBLISHED_LAYOUT__;
      var tutorialData = __TUTORIAL_DATA__;
      var edgeKey = __EDGE_KEY__;
      var kgViewerConfig = __VIEWER_CONFIG__;
      var kgNodeLabelConfig = kgViewerConfig.nodeLabels || {};
      var kgInfoPanelConfig = kgViewerConfig.infoPanel || {};
      var kgStorageKeys = kgViewerConfig.storageKeys || {};
      var kgCloudSyncConfig = kgViewerConfig.cloudSync || {};
      var edgeHoverWidth = kgViewerConfig.edgeHoverWidth;

      var DisplayScope = Object.freeze({
        OVERVIEW: "overview",
        FULL: "full",
        CONTEXT: "context"
      });
      var ContextPreset = kgGraphModel.ContextPreset;
      var ContextDepth = kgGraphModel.ContextDepth;
      var createContextRule = kgGraphModel.createContextRule;
      var contextPresetTraversals = kgGraphModel.contextPresetTraversals;
      var computeContextSubgraph = kgGraphModel.computeContextSubgraph;
      var contractionGraphPlan = kgGraphModel.contractionGraphPlan;

      function kgAfterReady() {
        var visAdapter = kgCreateVisNetworkAdapter(network);
        var allNodes = nodes.get();
        var allEdges = edges.get();
        var graphContainer = document.getElementById("mynetwork");
        var nodeLabelLayer = document.createElement("div");
        var moduleFoldControlLayer = document.createElement("div");
        var nodeTooltip = document.createElement("div");
        var conceptPreview = document.createElement("div");
        var nodeLabelEls = {};
        var moduleFoldControlEls = {};
        var defaultViewTitle = document.getElementById("kg_view_title")
          ? document.getElementById("kg_view_title").textContent
          : "";

        nodeLabelLayer.id = "kg_node_labels";
        graphContainer.appendChild(nodeLabelLayer);
        moduleFoldControlLayer.id = "kg_module_fold_controls";
        graphContainer.appendChild(moduleFoldControlLayer);
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

        var activeNodeId = null;
        var activeModuleId = null;
        var viewerState = {
          contextRule: createContextRule(ContextPreset.DERIVATION, ContextDepth.TWO_HOPS),
          displayScope: DisplayScope.FULL,
          view: "both"
        };
        var layoutEditModeEnabled = false;

        // Folded modules are a runtime graph projection; source concepts and edges stay unchanged.
        var foldedModules = {};
        var preferredFoldedModules = {};
        var moduleFootprintCache = {};
        var conceptFootprintExtentsCache = {};

        var projectedModuleEdgePrefix = "module-edge::";
        var moduleIdByConceptId = null;
        var hoveredEdgeId = null;
        var hoveredEdgeBeforeHover = null;
        var renderedEdgeWidthsDirty = true;
        var renderedEdgeWidthScale = null;
        var renderedEdgeWidthHoverId = null;

        var initialGraphProjectionReady = false;
        var activeNodeRadiusScale = 1.4;
        var activeNodeBorderWidth = 6;
        var detailedConceptRenderMinRadiusPx = 12;
        var nodeLabelWidth = kgNodeLabelConfig.width;
        var nodeLabelFontSize = kgNodeLabelConfig.fontSize;
        var tooltipTypesetTimer = null;
        var selectedConceptHeaderTypesetTimer = null;
        var conceptPreviewTypesetTimer = null;
        var conceptPreviewHideTimer = null;
        var conceptPreviewPinned = false;
        var conceptPreviewAnchor = null;
        var transientConceptHighlight = null;
        var transientEdgeSnapshots = {};
        var userNotesStorageKey = kgStorageKeys.userNotes;
        var splashDismissedStorageKey = kgStorageKeys.splashDismissed;
        var studyProgressStorageKey = kgStorageKeys.studyProgress || "srkg.studyProgress.v1";
        var contentReadProgressStorageKey = kgStorageKeys.contentReadProgress ||
          "srkg.contentReadProgress.v1";
        var graphCompletionMarkersStorageKey = "srkg.graphCompletionMarkers.v1";

        var graphCompletionMarkersEnabled =
          safeLocalStorageGet(graphCompletionMarkersStorageKey) !== "false";

        var notePlacementSuppressClickUntil = 0;
        var notePlacementPointerStart = null;
        var infoPanelPinchState = null;
        var infoPanelGraphicZoomBasePx = null;
        var panelContentRefreshPending = false;
        var userGuideLink = document.getElementById("kg_user_guide_link");
        if (userGuideLink && window.location.pathname.indexOf("/preview/") === 0) {
          userGuideLink.href = "https://physicskg.org/preview/user-guide.html";
        }

        var derivedFromFullTreeEnabled = false;
        var backlinksFullTreeEnabled = false;
        var workspaceSplitPercent = 50;
        var workspaceSplitterPointerId = null;
        var contextNoticeTimer = null;

        var sharedExplanations;
        var contentMarkup = kgCreateContentMarkup({concept: getConcept, hash: conceptHash,
          reference: function(reference, context) { return sharedExplanations.renderReference(reference, context); },
          disclosure: function(context) { return sharedExplanations.disclosure(context); }
        });
        sharedExplanations = kgCreateSharedExplanations({
          markup: contentMarkup, concepts: conceptData, modules: moduleData,
          readToggle: function(id, title) { return renderContentBlockReadToggle(id, title); },
          typeset: function(element) { typesetInfoPanel({element: element}); }
        });
        var escapeHtml = contentMarkup.escapeHtml;
        var cssAttributeValueEscape = contentMarkup.cssAttributeValueEscape;
        var skipOptionalDetailWhitespace = contentMarkup.skipOptionalDetailWhitespace;
        var parseBracedArgument = contentMarkup.parseBracedArgument;
        var renderFoldDown = contentMarkup.renderFoldDown;
        var renderConceptText = contentMarkup.renderConceptText;
        var findNextOptionalDetailBlock = contentMarkup.findNextOptionalDetailBlock;
        var renderCaptionText = contentMarkup.renderCaptionText;
        var contentModel = {
          getConcept: getConcept,
          getModule: getModule,
          conceptDisplayId: conceptDisplayId,
          conceptGraphicSvg: conceptGraphicSvg,
          conceptContentBlocks: conceptContentBlocks,
          moduleContentBlocks: moduleContentBlocks,
          conceptSections: conceptSections,
          contentBlockKindLabel: contentBlockKindLabel,
          compareConceptIds: compareConceptIds,
          compareModules: compareModules,
          searchDisplayText: searchDisplayText,
          moduleMemberIds: moduleMemberIds
        };
        var detailsView = kgCreateDetailsView({
          markup: contentMarkup, content: contentModel, onContentChange: schedulePanelContentRefit
        });
        var replaceTypesetContent = detailsView.replaceTypesetContent;
        var typesetInfoPanel = detailsView.typesetInfoPanel;
        var openTargetForToc = detailsView.openTargetForToc;
        var scrollInfoPanelTargetBelowStickyToc = detailsView.scrollInfoPanelTargetBelowStickyToc;
        var updateConceptTocActive = detailsView.updateConceptTocActive;
        var setActiveConceptSection = detailsView.setActiveConceptSection;
        var initialTocItem = detailsView.initialTocItem;
        var scheduleDetailScrollSync = detailsView.scheduleDetailScrollSync;
        var studyController = kgCreateStudyController({
          store: personalDataStore, concepts: conceptData, modules: moduleData,
          content: contentModel, markup: contentMarkup,
          storageKeys: {study: studyProgressStorageKey, read: contentReadProgressStorageKey},
          writeStorage: safeLocalStorageSet, network: network, replaceContent: replaceTypesetContent,
          onSave: function() { schedulePersonalDataAutoSync(); }
        });
        var renderContentReadCompletionIndicator = studyController.renderContentReadCompletionIndicator;
        var renderStudyQuestionCompletionIndicator = studyController.renderStudyQuestionCompletionIndicator;
        var updateContentReadCompletionIndicators = studyController.updateContentReadCompletionIndicators;
        var setContentBlockRead = studyController.setContentBlockRead;
        var recordStudyAttempt = studyController.recordStudyAttempt;
        var resetStudyQuestion = studyController.resetStudyQuestion;
        var resetAllStudyProgress = studyController.resetAllStudyProgress;
        var graphCompletionState = studyController.graphCompletionState;
        var renderStudyScorecard = studyController.renderStudyScorecard;
        var renderAutomaticStudyQuestion = studyController.renderAutomaticStudyQuestion;
        var renderSelfAssessedStudyQuestion = studyController.renderSelfAssessedStudyQuestion;
        var submitAutomaticStudyQuestion = studyController.submitAutomaticStudyQuestion;
        var renderSelfAssessedFeedback = studyController.renderSelfAssessedFeedback;
        var submitSelfAssessedQuestion = studyController.submitSelfAssessedQuestion;
        var markSelfAssessedQuestion = studyController.markSelfAssessedQuestion;
        var submitUnknownSelfAssessedQuestion = studyController.submitUnknownSelfAssessedQuestion;
        var renderContentBlockReadToggle = studyController.renderContentBlockReadToggle;
        var notesController = kgCreateNotesController({
          store: personalDataStore, storageKey: userNotesStorageKey,
          content: contentModel, markup: contentMarkup, writeStorage: safeLocalStorageSet,
          onSave: function() { schedulePersonalDataAutoSync(); },
          onContentChange: refreshActiveConcept, onSummariesChange: refreshNodeTooltips,
          onGeometryChange: schedulePanelContentRefit,
          onReveal: function(target) { scrollInfoPanelTargetBelowStickyToc(target, {immediate: true}); }
        });
        var setNotesStatus = notesController.setNotesStatus;
        var noteAnchorSpecs = notesController.noteAnchorSpecs;
        var canonicalNoteAnchor = notesController.canonicalNoteAnchor;
        var unresolvedNoteCount = notesController.unresolvedNoteCount;
        var migrateUserNotesState = notesController.migrateUserNotesState;
        var renderNoteBlockAction = notesController.renderNoteBlockAction;
        var findUserNote = notesController.findUserNote;
        var renderNotesOverview = notesController.renderNotesOverview;
        var renderNotesAtAnchor = notesController.renderNotesAtAnchor;
        var renderNoteAnchoredBody = notesController.renderNoteAnchoredBody;
        var renderUnmatchedNotes = notesController.renderUnmatchedNotes;
        var createUserNote = notesController.createUserNote;
        var deleteUserNote = notesController.deleteUserNote;
        var updateUserNote = notesController.updateUserNote;
        var noteEditorField = notesController.noteEditorField;
        var closeUserNote = notesController.closeUserNote;
        var importNotesCsv = notesController.importNotesCsv;
        var noteTitlesForConcept = notesController.noteTitlesForConcept;
        var exportNotes = notesController.exportNotes;
        var personalDataController = kgCreatePersonalDataController({
          store: personalDataStore, clientId: function() { return kgCloudSyncConfig.googleDriveClientId; },
          flushLayout: function() { writePersonalLayoutNow(); },
          onMerged: function() {
            globalLayoutStore.reload(); applyGlobalLayoutPositions(); updateLayoutControls();
            notesController.reload(); studyController.reload(); refreshNodeTooltips();
            renderNotesOverview(); renderStudyScorecard(); updateContentReadCompletionIndicators();
            if (network && network.redraw) { network.redraw(); }
          }
        });
        var setPersonalDataStatus = personalDataController.setPersonalDataStatus;
        var schedulePersonalDataAutoSync = personalDataController.schedulePersonalDataAutoSync;
        var initialiseGoogleDriveSync = personalDataController.initialiseGoogleDriveSync;
        var connectGoogleDrive = personalDataController.connectGoogleDrive;
        var syncPersonalDataNow = personalDataController.syncPersonalDataNow;
        var disconnectGoogleDrive = personalDataController.disconnectGoogleDrive;
        var exportPersonalData = personalDataController.exportPersonalData;
        var showPersonalDataImport = personalDataController.showPersonalDataImport;
        var closePersonalDataImport = personalDataController.closePersonalDataImport;
        var applyPersonalDataImport = personalDataController.applyPersonalDataImport;

        var globalLayoutStore = kgCreateGlobalLayout({
          publishedLayout: publishedLayout, nodes: nodes, store: personalDataStore,
          storageKey: globalLayoutStorageKey, getNodes: function() { return allNodes; },
          storage: {set: safeLocalStorageSet, remove: safeLocalStorageRemove},
          onStatusChange: updateLayoutControls,
          onSave: function() { schedulePersonalDataAutoSync(); },
          beforeReset: function(options) { resetContextFitInteraction(options); },
          onPositionsApplied: function() { refreshModuleFootprints(); updateNodeLabelPositions(); }
        });
        var effectiveConceptPosition = globalLayoutStore.effectiveConceptPosition;
        var setGlobalConceptPosition = globalLayoutStore.setGlobalConceptPosition;
        var setGlobalModuleAnchor = globalLayoutStore.setGlobalModuleAnchor;
        var globalModuleAnchor = globalLayoutStore.globalModuleAnchor;
        var effectiveModuleAnchor = globalLayoutStore.effectiveModuleAnchor;
        var globalLayoutSnapshot = globalLayoutStore.globalLayoutSnapshot;
        var writePersonalLayoutNow = globalLayoutStore.writePersonalLayoutNow;
        var personalLayoutStatus = globalLayoutStore.personalLayoutStatus;
        var keepPersonalLayout = globalLayoutStore.keepPersonalLayout;
        var applyGlobalLayoutPositions = globalLayoutStore.applyGlobalLayoutPositions;
        var resetToPublishedLayout = globalLayoutStore.resetToPublishedLayout;
        var exportedGlobalLayout = globalLayoutStore.exportedGlobalLayout;
        var exportGlobalLayout = globalLayoutStore.exportGlobalLayout;
        var graphCamera = kgCreateGraphCamera({
          network: network, nodes: nodes, container: graphContainer,
          labels: {width: nodeLabelWidth, fontSize: nodeLabelFontSize, activeRadiusScale: activeNodeRadiusScale},
          selectedConceptId: function() { return activeNodeId; }, onChange: updateNodeLabelPositions,
          additionalBounds: function(nodeIds) {
            var included = {};
            nodeIds.forEach(function(id) { included[String(id)] = true; });
            return expandedModuleOutlineSnapshot().filter(function(box) {
              return moduleMemberIds(getModule(box.moduleId)).every(function(id) {
                return included[String(id)];
              });
            });
          }
        });
        var cameraSnapshot = graphCamera.cameraSnapshot;
        var preserveCameraAfterLayout = graphCamera.preserveCameraAfterLayout;
        var currentGraphView = graphCamera.currentGraphView;
        var preserveGraphView = graphCamera.preserveGraphView;
        var fitNodesToAvailableRect = graphCamera.fitNodesToAvailableRect;
        var revealNodeIds = graphCamera.revealNodeIds;
        var cameraAnimationEnabled = graphCamera.cameraAnimationEnabled;
        var contextLayout = kgCreateContextLayout({
          network: network, nodes: nodes, edges: edges, originalEdges: originalEdges, camera: graphCamera,
          renderedGraph: function() { return lastGraphRender; },
          contextRule: function() { return viewerState.contextRule; },
          selectedConceptId: function() { return activeNodeId; }, readLabels: function() { return nodeLabelEls; },
          labels: {activeRadiusScale: activeNodeRadiusScale, fontSize: nodeLabelFontSize, hideBelowPx: kgNodeLabelConfig.hideBelowPx},
          revealSelection: revealViewerSelection, onControlsChange: updateGraphViewControls,
          onPositionsChange: updateNodeLabelPositions, notice: showContextNotice,
          fixedObstacles: function() {
            return expandedModuleOutlineSnapshot().map(function(box) {
              return {left: box.left, right: box.right, top: box.contentBottom,
                bottom: box.bottom, width: box.width, height: box.footerHeight};
            });
          },
          graph: {
            viewerSelectionSnapshot: viewerSelectionSnapshot,
            representedNodeIds: representedNodeIds,
            selectionRepresentationNodeIds: selectionRepresentationNodeIds,
            visibleGraphNode: visibleGraphNode,
            graphPositionForNode: graphPositionForNode,
            moduleIdFromGraphNodeId: moduleIdFromGraphNodeId,
            selectedModuleIsFolded: selectedModuleIsFolded,
            moduleGraphNodePosition: moduleGraphNodePosition,
            getConcept: getConcept,
            effectiveConceptPosition: effectiveConceptPosition,
            conceptFootprintExtents: conceptFootprintExtents
          }
        });
        var updateFitApplyButton = contextLayout.updateFitApplyButton;
        var clearContextFitPriming = contextLayout.clearContextFitPriming;
        var resetContextFitInteraction = contextLayout.resetContextFitInteraction;
        var fitViewerTarget = contextLayout.fitViewerTarget;

        var graphPresentation = kgCreateGraphPresentation({
          network: network, nodes: nodes, adapter: visAdapter, concept: getConcept, module: getModule,
          completionMarkers: graphCompletionMarkersSnapshot, expandedOutlines: expandedModuleOutlineSnapshot,
          moduleBoundary: function(nodeId) {
            var moduleId = moduleIdFromGraphNodeId(nodeId);
            if (!moduleId) { return null; }
            var bounds = selectedModuleIsFolded(moduleId)
              ? visAdapter.nodeGeometry(nodeId) : moduleFootprintCache[moduleId];
            if (!bounds || !(bounds.width > 0) || !(bounds.height > 0)) {
              bounds = moduleFootprint(moduleId);
            }
            return {left: bounds.left, top: bounds.top, width: bounds.width, height: bounds.height,
              radius: moduleCornerRadius(bounds.width, bounds.height)};
          },
          foldedModuleIds: foldedModuleIdList, moduleNodeId: moduleGraphNodeId,
          selectedConceptProxy: foldedModuleConceptProxy, escapeHtml: escapeHtml,
          selectedConceptId: function() { return activeNodeId; },
          selectedModuleId: function() { return activeModuleId; },
          transientHighlight: function() { return transientConceptHighlight; },
          activeRadiusScale: activeNodeRadiusScale, activeBorderWidth: activeNodeBorderWidth,
          detailThreshold: detailedConceptRenderMinRadiusPx,
          moduleFooterHeight: kgModuleGeometry.footerHeight
        });
        var drawVisibleNodes = graphPresentation.drawVisibleNodes;
        var drawGraphCompletionMarkers = graphPresentation.drawGraphCompletionMarkers;
        var fittedModuleLabel = graphPresentation.fittedModuleLabel;
        var moduleGraphicLayout = graphPresentation.moduleGraphicLayout;
        var moduleCornerRadius = graphPresentation.moduleCornerRadius;
        var drawExpandedModuleOutlines = graphPresentation.drawExpandedModuleOutlines;
        var moduleGraphicCornerRadius = graphPresentation.moduleGraphicCornerRadius;
        var moduleGraphicImage = graphPresentation.moduleGraphicImage;
        var drawFoldedModuleGraphics = graphPresentation.drawFoldedModuleGraphics;
        window.kgExpandedModuleLabelSnapshot = graphPresentation.expandedModuleLabelSnapshot;

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

        function updateLayoutControls() {
          var statusElement = document.getElementById("kg_layout_status");
          if (!statusElement) { return; }
          var status = personalLayoutStatus();
          statusElement.textContent = "Published revision " + status.publishedRevision +
            (status.hasOverrides ? " · Personal overrides active" : " · Published layout active");
          document.getElementById("kg_layout_revision_warning").hidden = !status.revisionMismatch;
          document.getElementById("kg_layout_reset").disabled = !status.hasOverrides;
          var toggle = document.getElementById("kg_layout_edit_toggle");
          var message = document.getElementById("kg_layout_edit_message");
          if (toggle) {
            toggle.checked = layoutEditModeEnabled;
            toggle.disabled = Boolean(contextLayout.isActive());
            toggle.title = contextLayout.isActive()
              ? "Personal layout editing resumes when the Fit++ arrangement ends"
              : "";
          }
          if (message) {
            if (contextLayout.isActive() && layoutEditModeEnabled) {
              message.textContent =
                "Personal editing is suspended during this temporary Fit++ arrangement.";
            } else if (contextLayout.isActive()) {
              message.textContent =
                "Fit++ is temporary; drag context nodes to adjust this arrangement.";
            } else if (!layoutEditModeEnabled) {
              message.textContent = "Node dragging is off.";
            } else if (viewerState.view === "details") {
              message.textContent = "Personal editing is on. Show the graph to move nodes.";
            } else {
              message.textContent = "Moves are saved to your personal layout in this browser.";
            }
          }
        }

        function globalLayoutEditingEnabled() {
          return layoutEditModeEnabled;
        }

        function persistentLayoutEditingEnabled() {
          return layoutEditModeEnabled && !contextLayout.isActive() &&
            viewerState.view !== "details";
        }

        function layoutDraggingEnabled() {
          return viewerState.view !== "details" &&
            (Boolean(contextLayout.isActive()) || persistentLayoutEditingEnabled());
        }

        function nodeDraggingEnabled(nodeId) {
          var node = nodes.get(String(nodeId));
          if (!node || node.hidden || node.isOverviewAnchor || viewerState.view === "details") {
            return false;
          }
          if (contextLayout.isActive()) {
            return contextLayout.canMove(nodeId);
          }
          return persistentLayoutEditingEnabled();
        }

        function updateNodeDragLocks() {
          if (!nodes) { return; }
          nodes.update(nodes.get().map(function(node) {
            var enabled = nodeDraggingEnabled(node.id);
            return {id: node.id, fixed: {x: !enabled, y: !enabled}};
          }));
        }

        function setLayoutEditingEnabled(enabled) {
          layoutEditModeEnabled = enabled === true;
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
          if (contextLayout.isActive()) {
            draggedIds.forEach(function(nodeId) {
              contextLayout.recordDrag(nodeId, graphPositionForNode(nodeId));
            });
            contextLayout.showTemporaryNotice();
            return;
          }
          var affectedModules = {};
          draggedIds.forEach(function(nodeId) {
            var position = graphPositionForNode(nodeId);
            if (!position) { return; }
            var moduleId = moduleIdFromGraphNodeId(nodeId);
            if (moduleId && selectedModuleIsFolded(moduleId)) {
              var anchor = syncFoldedModulePosition(moduleId);
              setGlobalModuleAnchor(moduleId, anchor);
              restoreFoldedModuleMembers(moduleId);
              affectedModules[moduleId] = true;
              return;
            }
            if (getConcept(nodeId)) {
              setGlobalConceptPosition(nodeId, position);
              var owner = moduleIdForConcept(nodeId);
              if (owner) { affectedModules[owner] = true; }
            }
          });
          Object.keys(affectedModules).forEach(function(moduleId) {
            refreshModuleFootprintGeometry(moduleId);
          });
          showContextNotice(
            "Personal layout updated — saved in this browser.",
            "personal-layout"
          );
        }

        window.kgGlobalLayoutSnapshot = globalLayoutSnapshot;
        window.kgLayoutEditingEnabled = globalLayoutEditingEnabled;
        window.kgPersistentLayoutEditingEnabled = persistentLayoutEditingEnabled;
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
          conceptFootprintExtentsCache = {};
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

        function buildModuleFoldControls() {
          moduleFoldControlLayer.innerHTML = "";
          moduleFoldControlEls = {};
          moduleIdsWithMembers().forEach(function(moduleId) {
            var button = document.createElement("button");
            button.type = "button";
            button.className = "kg-module-corner-control";
            button.setAttribute("data-module-id", moduleId);
            button.innerHTML = '<span aria-hidden="true"></span>';
            moduleFoldControlLayer.appendChild(button);
            moduleFoldControlEls[String(moduleId)] = button;
          });
          updateModuleFoldControlPositions();
          if (guidedTutorial) {
            refreshTutorialPointerPosition();
          }
        }

        function updateModuleFoldControlPositions() {
          if (!network || !moduleFoldControlLayer) { return; }
          var canvasEl = visAdapter.canvasElement();
          if (!canvasEl) { return; }
          var canvasRect = canvasEl.getBoundingClientRect();
          var layerRect = moduleFoldControlLayer.getBoundingClientRect();
          var expandedOutlines = {};
          expandedModuleGeometrySnapshot().forEach(function(outline) {
            expandedOutlines[String(outline.moduleId)] = outline;
          });
          moduleIdsWithMembers().forEach(function(moduleId) {
            var button = moduleFoldControlEls[String(moduleId)];
            if (!button) { return; }
            var folded = selectedModuleIsFolded(moduleId);
            var corner = null;
            if (folded) {
              var nodeId = moduleGraphNodeId(moduleId);
              var node = nodes.get(nodeId);
              var shape = visAdapter.nodeGeometry(nodeId);
              if (node && !node.hidden && shape) {
                corner = {x: shape.left + shape.width, y: shape.top};
              }
            } else {
              var outline = expandedOutlines[String(moduleId)];
              if (outline) {
                corner = {x: outline.right, y: outline.top};
              }
            }
            if (!corner || viewerState.view === "details") {
              button.style.display = "none";
              return;
            }
            var dom = network.canvasToDOM(corner);
            var title = (getModule(moduleId) || {}).title || moduleId;
            button.style.display = "block";
            button.style.left = (canvasRect.left - layerRect.left + dom.x - 20) + "px";
            button.style.top = (canvasRect.top - layerRect.top + dom.y - 20) + "px";
            button.setAttribute("data-fold-state", folded ? "folded" : "expanded");
            button.setAttribute("aria-label", (folded ? "Expand " : "Collapse ") + title + " module");
            button.querySelector("span").textContent = folded ? "+" : "−";
          });
        }

        function typesetNodeLabels() {
          if (window.MathJax && MathJax.typesetPromise) {
            if (MathJax.typesetClear) {
              MathJax.typesetClear([nodeLabelLayer]);
            }
            MathJax.typesetPromise([nodeLabelLayer]).catch(function(err) {
              console.warn("MathJax label typesetting failed:", err);
            }).then(function() {
              conceptFootprintExtentsCache = {};
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
          if (!nodeTooltip || viewerState.view === "details") { return; }
          var moduleId = moduleIdFromGraphNodeId(nodeId);
          if (moduleId && getModule(moduleId)) {
            replaceTypesetContent(nodeTooltip, moduleTooltipHtml(moduleId));
          } else if (getConcept(nodeId)) {
            replaceTypesetContent(nodeTooltip, conceptTooltipHtml(nodeId));
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
          replaceTypesetContent(nodeTooltip, edgeTooltipHtml(edge));
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
            replaceTypesetContent(nodeTooltip, "");
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
            var canvasEl = visAdapter.canvasElement();
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
          updateModuleFoldControlPositions();
        }
        window.kgUpdateNodeLabelPositions = updateNodeLabelPositions;

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

        window.kgContentReadProgress = {
          storageKey: contentReadProgressStorageKey, isRead: studyController.isRead, setRead: setContentBlockRead
        };

        window.kgStudyProgress = {
          storageKey: studyProgressStorageKey, getState: studyController.getState,
          getQuestion: studyController.getQuestion, recordAttempt: recordStudyAttempt,
          resetQuestion: resetStudyQuestion, resetAll: resetAllStudyProgress
        };

        function graphCompletionMarkerAnchor(node, positions) {
          var nodeId = String(node.id);
          var position = positions[nodeId];
          if (!position) { return null; }
          if (node.isModuleNode) {
            var shape = visAdapter.nodeGeometry(nodeId);
            var width = shape ? Number(shape.width) : Number(node.moduleFootprintWidth);
            var height = shape ? Number(shape.height) : Number(node.moduleFootprintHeight);
            var left = shape ? Number(shape.left) : position.x - width / 2;
            var top = shape ? Number(shape.top) : position.y - height / 2;
            if (![width, height, left, top].every(Number.isFinite)) { return null; }
            var moduleRadius = Math.max(16, Math.min(42, Math.min(width, height) * 0.025));
            var cornerRadius = moduleCornerRadius(width, height);
            return {
              kind: "module",
              // Keep the glyph row just above the rounded-corner arc. This
              // remains visibly bottom-right without clipping either tick.
              x: left + width - moduleRadius * 1.5,
              y: top + height - cornerRadius - moduleRadius * 1.4,
              radius: moduleRadius
            };
          }
          var baseRadius = Number(node.visualSize) || Number(node.size) || 18;
          var conceptRadius = nodeId === String(activeNodeId || "")
            ? baseRadius * activeNodeRadiusScale
            : baseRadius;
          var markerRadius = Math.max(4, conceptRadius * 0.13);
          return {
            kind: "concept",
            x: position.x + conceptRadius * 0.78 / Math.sqrt(2),
            y: position.y + conceptRadius * 0.78 / Math.sqrt(2),
            radius: markerRadius,
            nodeX: position.x,
            nodeY: position.y,
            nodeRadius: conceptRadius
          };
        }

        function graphCompletionSymbolLayout(marker) {
          var completions = [];
          if (marker.read) { completions.push({kind: "read", colour: "#1267c4"}); }
          if (marker.questions) {
            completions.push({kind: "questions", colour: "#238636"});
          }
          return completions.map(function(completion, index) {
            if (marker.anchor.kind === "concept") {
              var angle = completions.length === 1
                ? Math.PI / 4
                : (completion.kind === "read" ? Math.PI / 6 : Math.PI / 3);
              var radialDistance = marker.anchor.nodeRadius * 0.88;
              return {
                kind: completion.kind,
                colour: completion.colour,
                x: marker.anchor.nodeX + Math.cos(angle) * radialDistance,
                y: marker.anchor.nodeY + Math.sin(angle) * radialDistance,
                radius: marker.anchor.radius
              };
            }
            var reverseIndex = completions.length - index - 1;
            var offset = reverseIndex * marker.anchor.radius * 1.45;
            return {
              kind: completion.kind,
              colour: completion.colour,
              x: marker.anchor.x - offset,
              y: marker.anchor.y,
              radius: marker.anchor.radius
            };
          });
        }

        function graphCompletionMarkersSnapshot() {
          var result = {enabled: graphCompletionMarkersEnabled, markers: []};
          if (!graphCompletionMarkersEnabled || !network || !nodes) { return result; }
          var candidates = nodes.get().map(function(node) {
            if (node.hidden || node.isOverviewAnchor) { return; }
            var ownerType = node.isModuleNode ? "module" : "concept";
            var ownerId = node.isModuleNode
              ? moduleIdFromGraphNodeId(node.id)
              : String(node.id);
            if (!ownerId || (ownerType === "concept" && !getConcept(ownerId))) { return; }
            var state = graphCompletionState(ownerType, ownerId);
            if (!state.read && !state.questions) { return; }
            return {
              node: node,
              ownerType: ownerType,
              ownerId: ownerId,
              state: state
            };
          }).filter(Boolean);
          if (!candidates.length) { return result; }
          var positions = network.getPositions(candidates.map(function(candidate) {
            return candidate.node.id;
          }));
          candidates.forEach(function(candidate) {
            var node = candidate.node;
            var anchor = graphCompletionMarkerAnchor(node, positions);
            if (!anchor) { return; }
            var marker = {
              nodeId: String(node.id),
              ownerType: candidate.ownerType,
              ownerId: candidate.ownerId,
              read: candidate.state.read,
              questions: candidate.state.questions,
              opacity: node.opacity === undefined ? 1 : Number(node.opacity),
              anchor: anchor
            };
            marker.symbols = graphCompletionSymbolLayout(marker);
            result.markers.push(marker);
          });
          return result;
        }

        function setGraphCompletionMarkersEnabled(enabled) {
          graphCompletionMarkersEnabled = enabled !== false;
          safeLocalStorageSet(
            graphCompletionMarkersStorageKey,
            graphCompletionMarkersEnabled ? "true" : "false"
          );
          var toggle = document.getElementById("kg_graph_completion_markers");
          if (toggle) { toggle.checked = graphCompletionMarkersEnabled; }
          if (network && network.redraw) { network.redraw(); }
        }

        window.kgGraphCompletionMarkersSnapshot = graphCompletionMarkersSnapshot;
        window.kgSetGraphCompletionMarkersEnabled = setGraphCompletionMarkersEnabled;

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

        function openScorecardQuestion(questionId) {
          var indexed = studyController.indexedQuestion(questionId);
          if (!indexed) { return; }
          setViewerView(viewerState.view === "graph" ? "both" : viewerState.view);
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

        function contentAnchorId(conceptId, title) {
          var slug = String(conceptId || "") + "-" + String(title || "");
          slug = slug.toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");
          return "kg-toc-" + (slug || "section");
        }

        function refreshActiveConcept() {
          if (activeNodeId && getConcept(activeNodeId)) {
            showConcept(activeNodeId, {preserveSectionContext: true});
          } else if (activeModuleId && getModule(activeModuleId)) {
            showModule(activeModuleId, {preserveSectionContext: true});
          }
        }

        window.kgExportNotes = exportNotes;

        window.kgInitialiseGoogleDriveSync = initialiseGoogleDriveSync;
        window.kgSchedulePersonalDataAutoSync = schedulePersonalDataAutoSync;

        window.kgExportPersonalData = exportPersonalData;

        /* Concept details panel rendering and MathJax refresh. */

        function buildWorkspaceShell() {
          if (document.getElementById("kg_workspace")) { return; }
          var panel = document.getElementById("info_panel");
          var contextPanel = document.getElementById("kg_graph_context_panel");
          var tutorialNarration = document.getElementById("kg_tutorial_narration");
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
          shell.appendChild(document.getElementById("kg_history_controls"));
          graphPane.appendChild(graphSurface);
          graphSurface.appendChild(graphContainer);
          if (tutorialNarration) {
            document.body.appendChild(tutorialNarration);
          }
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

        function updateWorkspaceViewControl() {
          var select = document.getElementById("kg_view_select");
          if (select) { select.value = viewerState.view; }
        }

        function setViewerView(value) {
          if (["both", "graph", "details"].indexOf(value) === -1) { value = "both"; }
          var camera = cameraSnapshot();
          viewerState.view = value;
          document.getElementById("info_panel").classList.toggle("kg-hidden", value === "graph");
          document.body.classList.toggle("kg-details-hidden", value === "graph");
          document.body.classList.toggle("kg-graph-hidden", value === "details");
          updateWorkspaceViewControl();
          updateGraphViewControls();
          preserveCameraAfterLayout(camera);
          schedulePanelContentRefresh();
          updateGraphContextControls();
        }

        function setInfoPanelVisible(visible) {
          setViewerView(visible ? (viewerState.view === "details" ? "details" : "both") : "graph");
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
          var disabled = viewerState.view === "details";
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
            select.title = "Overview: internal concept edges and module summaries. Context + background: emphasise the selected context. Context only: omit the background.";
          }
          document.body.classList.toggle(
            "kg-graph-hidden",
            viewerState.view === "details"
          );
          updateModuleActionControls();
          if (network && network.setOptions) {
            network.setOptions({interaction: {
              dragNodes: layoutDraggingEnabled()
            }});
          }
          updateNodeDragLocks();
          updateLayoutControls();
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

        // Bound the in-app buttons to this document session. Native browser
        // history still works normally, including selections made before reload.
        var navigationSession = "";
        var navigationIndex = 0;
        var navigationEnd = 0;
        var navigationMoving = false;

        function navigationHistoryState(state) {
          return Object.assign({}, state || {}, {kgNavigation: {
            session: navigationSession, index: navigationIndex
          }});
        }

        function presentationHistoryState() {
          var state = cloneSerializable(window.history.state);
          if (state) { delete state.kgNavigation; }
          return state;
        }

        function updateHistoryControls() {
          var back = document.getElementById("kg_history_back");
          var forward = document.getElementById("kg_history_forward");
          if (!back || !forward) { return; }
          // Do not drop keyboard focus while waiting for popstate. The click
          // handler guards repeated requests until navigation completes.
          back.disabled = navigationIndex <= 0;
          forward.disabled = navigationIndex >= navigationEnd;
        }

        function initialiseSelectionHistory() {
          navigationSession = String(Date.now()) + ":" + String(Math.random());
          navigationIndex = navigationEnd = 0;
          navigationMoving = false;
          window.history.replaceState(navigationHistoryState(window.history.state), "", window.location.href);
          updateHistoryControls();
        }

        function pushSelectionHistory(state, url) {
          navigationIndex += 1;
          navigationEnd = navigationIndex;
          window.history.pushState(navigationHistoryState(state), "", url);
          updateHistoryControls();
        }

        function navigateSelectionHistory(direction) {
          if (guidedTutorial && guidedTutorial.isGuiding()) { return; }
          if (navigationMoving || (direction < 0 ? navigationIndex <= 0 : navigationIndex >= navigationEnd)) { return; }
          navigationMoving = true;
          updateHistoryControls();
          window.history.go(direction);
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
          pushSelectionHistory(state, hash);
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
          pushSelectionHistory(state, hash);
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
          var metadata = (kgViewerConfig.domains || []).find(function(item) { return item.id === value; });
          return metadata && metadata.label ? metadata.label : value.toUpperCase();
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

            var title = block.args[block.name === "optional_details" ? 0 : block.name === "explanation" ? 1 : 3];
            if (title) { titles.push(title); }
            cursor = block.end;
          }
          return titles;
        }

        // Summary views are derived from canonical blocks; no duplicate section payload.
        function conceptSections(concept) {
          if (!concept) { return []; }
          var blocks = conceptContentBlocks(concept);
          return ["definition", "derivation", "explanation"].map(function(kind) {
            return {
              key: kind, title: kind.charAt(0).toUpperCase() + kind.slice(1),
              text: blocks.filter(function(block) { return block.kind === kind; })
                .map(function(block) { return [block.statement, block.body].filter(Boolean).join("\n"); }).join("\n\n")
            };
          });
        }

        function conceptSectionText(concept, key) {
          var section = conceptSections(concept).find(function(item) {
            return item.key === key;
          });
          return section ? section.text : "";
        }

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
          summary: {label: "Takeaway", mode: "inline"},
          graphic: {label: "Graphic", mode: "inline"}
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
                body: String(block.body || ""),
                statement: String(block.statement || ""),
                graphic: String(block.graphic || "")
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

        function renderNoteableHeading(targetType, targetId, title, sectionKey) {
          return '<span class="kg-noteable-title">' + renderConceptText(title) + "</span>" +
            renderNoteBlockAction(targetType, targetId, title, "", sectionKey, false);
        }

        function renderOwnerContentBlock(ownerType, ownerId, block) {
          var title = block.title || contentBlockKindLabel(block.kind);
          var policy = contentBlockPolicyFor(block.kind);
          var context = sharedExplanations.rootContext(block.block_id, contentAnchorId(ownerId, title));
          var graphic = sharedExplanations.nativeGraphic(block.block_id);
          if (graphic) {
            graphic += renderNotesAtAnchor(ownerType, ownerId, "Graphic", 0, "",
              noteAnchorSpecs("", "graphic", "Graphic", "")[0]);
          }
          return contentMarkup.renderContentUnit({
            origin: "authored", level: "block", anchorId: contentAnchorId(ownerId, title),
            contentBlockId: block.block_id,
            capabilities: {annotate: true, trackRead: true, edit: false},
            className: contentBlockClassName(block, policy) + (ownerType === "module" ? " module-content-block" : ""),
            open: policy.mode !== "folded", title: title,
            markHtml: '<span class="content-block-kind-mark" aria-hidden="true"></span>',
            labelHtml: '<span class="content-block-kind-label" aria-hidden="true" data-label="' +
              escapeHtml(policy.label) + '"></span>',
            actions: [
              {position: "heading", capability: "annotate",
                html: renderNoteBlockAction(ownerType, ownerId, title, block.block_id, "", true)},
              {position: "heading", capability: "trackRead",
                html: renderContentBlockReadToggle(block.block_id, title)}
            ],
            bodyClass: "content-block-body",
            bodyHtml: sharedExplanations.nativeStatement(block.block_id) + graphic +
              renderNoteAnchoredBody(ownerType, ownerId, title, block.block_id, "", block.body, context)
          });
        }

        function renderContentBlock(conceptId, block) {
          return renderOwnerContentBlock("concept", conceptId, block);
        }

        function conceptTocItems(conceptId, concept, studyQuestions, conceptReferences) {
          var items = [];
          if (conceptGraphicSvg(concept) && !sharedExplanations.hasGraphicBlock(concept)) {
            items.push({
              id: contentAnchorId(conceptId, "Graphic"),
              title: "Graphic"
            });
          }
          conceptContentBlocks(concept).forEach(function(block) {
            var title = block.title || contentBlockKindLabel(block.kind);
            items.push({id: contentAnchorId(conceptId, title), title: title, kind: block.kind});
          });

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
          html += notesController.renderOwnerNoteAction("concept", nodeId);
          html += renderContentReadCompletionIndicator("concept", nodeId);
          html += renderStudyQuestionCompletionIndicator("concept", nodeId);
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
            displayScope: viewerState.displayScope,
            view: viewerState.view
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
          var precisePosition = visAdapter.precisePosition(id);
          if (precisePosition) { return precisePosition; }
          var pos = nodes.get(id) || originalNodes[id];
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
          conceptId = String(conceptId);
          if (conceptFootprintExtentsCache[conceptId]) {
            return Object.assign({}, conceptFootprintExtentsCache[conceptId]);
          }
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
          var extents = {
            left: Math.max(radius, labelWidth / 2),
            right: Math.max(radius, labelWidth / 2),
            top: radius,
            bottom: radius + 4 + labelHeight
          };
          conceptFootprintExtentsCache[conceptId] = extents;
          return Object.assign({}, extents);
        }

        function moduleFootprint(moduleId) {
          return kgModuleGeometry.withFooter(kgModuleGeometry.footprint(moduleMemberIds(getModule(moduleId)).map(function(id) {
            return {position: effectiveConceptPosition(id), extents: conceptFootprintExtents(id)};
          }), effectiveModuleAnchor(moduleId)));
        }

        window.kgModuleFootprint = moduleFootprint;

        function refreshFoldedModuleGeometry(moduleId) {
          var oldState = foldedModules[String(moduleId)];
          if (!oldState) { return; }
          var nodeId = moduleGraphNodeId(moduleId);
          var oldNode = nodes.get(nodeId);
          var geometry = moduleMemberGeometry(moduleId);
          moduleFootprintCache[String(moduleId)] = geometry.footprint;
          foldedModules[String(moduleId)] = geometry;
          if (oldNode) {
            var node = moduleGraphNode(moduleId);
            node.hidden = oldNode.hidden;
            nodes.update(node);
            network.moveNode(nodeId, node.x, node.y);
          }
        }

        function refreshModuleFootprintGeometry(moduleId) {
          if (selectedModuleIsFolded(moduleId)) {
            refreshFoldedModuleGeometry(moduleId);
          } else {
            moduleFootprintCache[String(moduleId)] = moduleFootprint(moduleId);
            var anchor = nodes.get(moduleGraphNodeId(moduleId));
            if (anchor && anchor.isOverviewAnchor) {
              var footprint = moduleFootprintCache[String(moduleId)];
              nodes.update(Object.assign({id: anchor.id}, moduleBoxShape(footprint)));
              network.moveNode(anchor.id, footprint.x, footprint.y);
            }
          }
        }

        function refreshModuleFootprints() {
          // Geometry changes never move anchors, members or neighbouring modules.
          moduleIds().forEach(function(moduleId) {
            refreshModuleFootprintGeometry(moduleId);
          });
        }

        function refreshModuleFootprintsAfterFontLoad() {
          conceptFootprintExtentsCache = {};
          refreshModuleFootprints();
        }

        function foldModule(moduleId) {
          var geometry = moduleMemberGeometry(moduleId);
          moduleFootprintCache[String(moduleId)] = geometry.footprint;
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
          visAdapter.setLayeredEdges([]);
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
          if (!persistentLayoutEditingEnabled()) { return; }
          moduleId = String(moduleId);
          var state = foldedModules[moduleId];
          if (!state || !state.position || !state.memberOffsets) { return; }
          syncFoldedModulePosition(moduleId);
          setGlobalModuleAnchor(moduleId, state.position);
          var updates = [];
          moduleMemberIds(getModule(moduleId)).forEach(function(id) {
            var offset = state.memberOffsets[String(id)] || {x: 0, y: 0};
            var position = {
              x: state.position.x + offset.x,
              y: state.position.y + offset.y
            };
            setGlobalConceptPosition(id, position);
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

        window.kgModuleGraphicLayout = moduleGraphicLayout;

        function foldedModuleConceptProxy(moduleId) {
          moduleId = String(moduleId);
          var conceptId = selectedConceptInFoldedModule(moduleId);
          var graphNodeId = moduleGraphNodeId(moduleId);
          var graphNode = nodes.get(graphNodeId);
          var shape = visAdapter.nodeGeometry(graphNodeId);
          var conceptNode = conceptId ? nodes.get(conceptId) : null;
          if (!conceptId || !graphNode || graphNode.hidden || !shape || !conceptNode) {
            return null;
          }
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

        function expandedModuleGeometrySnapshot() {
          return moduleIds().filter(function(moduleId) {
            if (selectedModuleIsFolded(moduleId)) { return false; }
            return moduleMemberIds(getModule(moduleId)).some(function(conceptId) {
              var node = nodes.get(conceptId);
              return node && !node.hidden;
            });
          }).map(function(moduleId) {
            var footprint = moduleFootprintCache[String(moduleId)] || moduleFootprint(moduleId);
            moduleFootprintCache[String(moduleId)] = footprint;
            return {
              moduleId: moduleId,
              left: footprint.left,
              right: footprint.right,
              top: footprint.top,
              bottom: footprint.bottom,
              contentBottom: footprint.contentBottom,
              footerHeight: footprint.footerHeight,
              width: footprint.width,
              height: footprint.height,
              radius: moduleCornerRadius(footprint.width, footprint.height),
              colour: "#6b7280",
              opacity: 0.3,
              lineWidth: 1.75
            };
          });
        }

        function expandedModuleOutlineSnapshot() {
          return viewerState.displayScope !== DisplayScope.CONTEXT
            ? expandedModuleGeometrySnapshot()
            : [];
        }

        window.kgExpandedModuleOutlineSnapshot = expandedModuleOutlineSnapshot;

        window.kgModuleGraphicCornerRadius = moduleGraphicCornerRadius;

        function moduleBoxShape(footprint) {
          return {
            shape: "box",
            shapeProperties: {borderRadius: moduleCornerRadius(footprint.width, footprint.height)},
            margin: {top: 0, right: 0, bottom: 0, left: 0},
            widthConstraint: {minimum: footprint.width, maximum: footprint.width},
            heightConstraint: {minimum: footprint.height, valign: "middle"}
          };
        }

        function moduleGraphNode(moduleId) {
          var module = getModule(moduleId) || {};
          var memberCount = moduleMemberIds(module).length;
          var position = moduleGraphNodePosition(moduleId);
          var footprint = foldedModules[String(moduleId)].footprint;
          var hasGraphic = Boolean(module.svg_icon);
          var selectedConceptProxyId = selectedConceptInFoldedModule(moduleId);
          var usesGraphicLayout = hasGraphic || Boolean(selectedConceptProxyId);
          var graphicLayout = moduleGraphicLayout(footprint.width, footprint.height);
          var labelArea = usesGraphicLayout ? graphicLayout.labelArea : {
            top: -footprint.height * 0.42, bottom: footprint.height * 0.42,
            height: footprint.height * 0.84
          };
          var labelCenter = (labelArea.top + labelArea.bottom) / 2;
          var fittedLabel = fittedModuleLabel(
            module.title || moduleId,
            memberCount,
            footprint.width,
            footprint.height,
            {
              countFontSize: usesGraphicLayout ? 52 : 80,
              titleFontCap: 128,
              verticalShift: labelCenter,
              availableHeight: labelArea.height * 0.94,
              lineWidthFraction: 0.72,
              lineHeightFactor: 1.06
            }
          );
          var visualColor = moduleVisualColor(moduleId);
          return Object.assign(moduleBoxShape(footprint), {
            id: moduleGraphNodeId(moduleId),
            isModuleNode: true,
            moduleId: String(moduleId),
            hasModuleGraphic: hasGraphic,
            selectedConceptProxyId: selectedConceptProxyId || "",
            // Keep the custom metadata type stable across DataSet updates;
            // vis-network cannot merge a nested object over a previous null.
            moduleGraphicLabelArea: labelArea,
            moduleGraphicLabelCenter: labelCenter,
            label: fittedLabel.text,
            moduleFootprintWidth: footprint.width,
            moduleFootprintHeight: footprint.height,
            chosen: {label: false},
            // A small secondary count must not trigger vis's whole-label fade-out.
            scaling: {label: {drawThreshold: 0}},
            x: position.x,
            y: position.y,
            physics: false,
            hidden: false,
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
          });
        }

        window.kgModuleGraphicImage = moduleGraphicImage;

        /* Projected boundary edges shown when module members are folded away. */
        function projectedModuleEndpointForConcept(conceptId, moduleEndpointMembers) {
          conceptId = String(conceptId);
          if (moduleEndpointMembers[conceptId]) {
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

        function projectedModuleEdges(moduleEndpointMembers) {
          var representedByConcept = {};
          var renderedEdges = {};
          var boundaryEdges = allEdges.filter(function(edge) {
            var current = edges.get(edge.id) || originalEdges[edge.id] || edge;
            if (!current || current.hidden ||
                (!moduleEndpointMembers[String(edge.from)] && !moduleEndpointMembers[String(edge.to)])) { return false; }
            renderedEdges[edge.id] = current;
            [edge.from, edge.to].forEach(function(id) {
              if (!Object.prototype.hasOwnProperty.call(representedByConcept, id)) {
                representedByConcept[id] = projectedModuleEndpointForConcept(id, moduleEndpointMembers);
              }
            });
            return true;
          });
          return kgGraphModel.groupBoundaryEdges(
            boundaryEdges, renderedEdges, representedByConcept, moduleEndpointMembers, projectedModuleEdgePrefix
          ).map(projectedModuleEdgeFromGroup);
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

          renderGraphFromViewerState();
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
          renderGraphFromViewerState();
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
          return renderOwnerContentBlock("module", moduleId, block);
        }

        function moduleTocItems(moduleId, module) {
          var items = [];
          if ((module.svg_detail || module.svg_icon) && !sharedExplanations.hasGraphicBlock(module)) {
            items.push({
              id: contentAnchorId(moduleId, "Graphic"),
              title: "Module graphic"
            });
          }
          moduleContentBlocks(module).forEach(function(block) {
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
          html += notesController.renderOwnerNoteAction("module", moduleId);
          html += renderContentReadCompletionIndicator("module", moduleId);
          html += renderStudyQuestionCompletionIndicator("module", moduleId);
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
          if (sharedExplanations.hasGraphicBlock(module)) { return ""; }
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
            noteBlock: true,
            className: "concept-figure module-figure",
            open: true,
            summaryHtml: renderNoteableHeading(
              "module", moduleId, "Module graphic", "graphic"
            ),
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
          sharedExplanations.beginPage("module", moduleId, panel);
          var tocItems = moduleTocItems(moduleId, module);
          detailsView.setItems(tocItems);

          var html = renderModuleMasthead(moduleId, module, tocItems);
          html += renderModuleGraphic(moduleId, module);
          moduleContentBlocks(module).forEach(function(block) {
            html += renderModuleContentBlock(moduleId, block);
          });
          html += notesController.renderOwnerNotes("module", moduleId);
          html += renderModuleMembers(moduleId, module);
          html += renderModuleBoundarySection(moduleId, "incoming", "Incoming boundary links");
          html += renderModuleBoundarySection(moduleId, "outgoing", "Outgoing boundary links");
          html += renderModuleSupports(moduleId, module);
          html += renderUnmatchedNotes("module", moduleId);

          var previousModuleId = panel.getAttribute("data-module-id") || "";
          var moduleChanged = previousModuleId !== String(moduleId);
          replaceTypesetContent(panel, html);
          sharedExplanations.afterRender(panel);
          panel.removeAttribute("data-concept-id");
          panel.setAttribute("data-module-id", String(moduleId));
          if (moduleChanged) {
            panel.scrollTop = 0;
          }
          detailsView.suppressScrollSync(350);
          renderNotesOverview();
          var initialItem = initialTocItem(tocItems);
          setActiveConceptSection(initialItem ? initialItem.id : null);
          updateGraphContextControls();
          typesetInfoPanel(options);
        }

        function renderConceptGraphic(conceptId, concept) {
          if (sharedExplanations.hasGraphicBlock(concept)) { return ""; }
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
            noteBlock: true,
            className: "concept-figure",
            open: true,
            summaryHtml: renderNoteableHeading("concept", conceptId, "Graphic", "graphic"),
            bodyTag: "figure",
            bodyClass: "concept-figure-body",
            bodyHtml: bodyHtml
          });
        }

        function cancelNotePlacement(block, restoreFocus) {
          block = block || document.querySelector('#info_panel [data-note-placement="active"]');
          if (!block) { return; }
          var action = block.querySelector(
            ":scope > summary .kg-note-block-action, " +
            ":scope > .kg-noteable-heading .kg-note-block-action"
          );
          block.removeAttribute("data-note-placement");
          block.querySelectorAll(".kg-note-placement-target").forEach(function(line) {
            line.classList.remove("kg-note-placement-target");
            line.removeAttribute("tabindex");
            line.removeAttribute("aria-label");
          });
          if (action) { action.setAttribute("aria-pressed", "false"); }
          if (restoreFocus && action) {
            window.requestAnimationFrame(function() { action.focus(); });
          }
        }

        function beginNotePlacement(action) {
          var block = action && action.closest("#info_panel > [data-note-block]");
          if (!block) { return; }
          cancelNotePlacement();
          if (block.tagName === "DETAILS") { block.open = true; }
          var lines = Array.from(block.querySelectorAll(".concept-line")).filter(function(line) {
            return !line.closest(".user-note, .kg-content-inline, .kg-shared-reference, .kg-content-statement");
          });
          if (block.matches(".concept-figure, .study-questions") || lines.length === 0) {
            var blockNoteButton = block.querySelector(".kg-add-note");
            if (blockNoteButton) { blockNoteButton.click(); }
            return;
          }
          block.setAttribute("data-note-placement", "active");
          action.setAttribute("aria-pressed", "true");
          lines.forEach(function(line) {
            line.classList.add("kg-note-placement-target");
            line.setAttribute("tabindex", "0");
            line.setAttribute("aria-label", "Place note after this paragraph");
          });
          if (lines.length > 0) {
            window.requestAnimationFrame(function() { lines[0].focus(); });
          }
        }

        function renderConceptContent(conceptId, concept) {
          return conceptContentBlocks(concept).map(function(block) {
            return renderContentBlock(conceptId, block);
          }).join("");
        }

        function optionalDetailTitlesForConcept(concept) {
          return conceptSections(concept).reduce(function(titles, section) {
            return titles.concat(optionalDetailTitlesFromText(section.text));
          }, []);
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
          var noteTitles = noteTitlesForConcept(nodeId);
          html += tooltipListHtml("Notes", noteTitles.slice(0, 3));
          if (noteTitles.length > 3) {
            html += '<div class="kg-tooltip-section-title">' +
              (noteTitles.length - 3) + " more notes</div>";
          }
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
          replaceTypesetContent(conceptPreview, "");
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
          replaceTypesetContent(conceptPreview, conceptPreviewHtml(id));
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
            var arity = name === "explain" ? 4 : name === "explanation" ? 3 :
              /^(frac|dfrac|tfrac|overset|underset|cref|optional_details)$/.test(name) ? 2 :
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
              else if (name === "explanation") { output += args[1] + ": " + args[2]; }
              else if (name === "explain") { output += args[2] + ": " + args[3]; }
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
              value: [block.statement, block.body].filter(Boolean).join("\n")
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
          var fullGraph = viewerState.displayScope !== DisplayScope.CONTEXT;
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
          if (viewerState.view === "details") { return; }
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
          if (depth === ContextDepth.THREE_HOPS) { return "3 hops"; }
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
            overview: ["Overview", "Overview"],
            full: ["Context + background", "Context + bg"],
            context: ["Context only", "Context"]
          }, compact);
          setResponsiveOptionLabels("kg_view_select", {
            both: ["Both", "Both"], graph: ["Graph", "Graph"], details: ["Details", "Details"]
          }, compact);
          setResponsiveOptionLabels("kg_fit_select", {
            reveal: ["Reveal selection", "Reveal"],
            selection: ["Fit selection", "Selection"],
            context: ["Fit context", "Context"],
            displayed: ["Fit displayed graph", "All"]
          }, compact);
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
          if (presetSelect) {
            presetSelect.value = viewerState.contextRule.preset;
            presetSelect.disabled = false;
          }
          if (depthSelect) {
            depthSelect.value = viewerState.contextRule.depth;
            depthSelect.disabled = false;
          }
          if (customEdit) {
            customEdit.hidden = viewerState.contextRule.preset !== ContextPreset.CUSTOM;
          }
          updateFitApplyButton();
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
            var contextCanExpand = representedCount > 0;
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

          var selectionLabel = "";
          if (selection.type === "concept") {
            selectionLabel = conceptDisplayId(selection.id) + " " + (getConcept(selection.id).label || "");
          } else if (selection.type === "module") {
            selectionLabel = getModule(selection.id).title || selection.id;
          }
          var graphSelection = document.getElementById("kg_graph_selection");
          graphSelection.hidden = viewerState.view !== "graph" || !selectionLabel;
          graphSelection.textContent = selectionLabel;
          graphSelection.title = "Open details for " + selectionLabel;
          graphSelection.setAttribute("aria-label", graphSelection.title);
          summary.parentElement.setAttribute("data-context-can-expand", representedCount > 0 ? "true" : "false");
          var scopeLabel = viewerState.displayScope === DisplayScope.CONTEXT
            ? "Context only"
            : viewerState.displayScope === DisplayScope.OVERVIEW ? "Overview" : "Context + background";
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
          renderGraphFromViewerState();
        }

        async function showRelationshipSectionInGraph(preset, fullTree) {
          var selected = JSON.stringify(viewerSelectionSnapshot());
          resetContextFitInteraction();
          viewerState.contextRule = createContextRule(
            preset,
            fullTree ? ContextDepth.TRANSITIVE : ContextDepth.ONE_HOP
          );
          if (viewerState.view === "details") { setViewerView("both"); }
          renderGraphFromViewerState();
          document.getElementById("kg_fit_select").value = "context";
          updateGraphContextControls();
          await nextAnimationFrames(2);
          if (selected !== JSON.stringify(viewerSelectionSnapshot()) ||
              viewerState.contextRule.preset !== preset || viewerState.view === "details") { return; }
          clearContextFitPriming();
          fitViewerTarget("context");
        }

        function setViewerDisplayScope(scope) {
          resetContextFitInteraction();
          viewerState.displayScope = [DisplayScope.OVERVIEW, DisplayScope.FULL, DisplayScope.CONTEXT].indexOf(scope) !== -1 ? scope : DisplayScope.OVERVIEW;
          updateGraphViewControls();
          renderGraphFromViewerState();
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

        function revealViewerSelection(options) {
          return revealNodeIds(selectionRepresentationNodeIds(), options);
        }

        window.kgCameraAnimationEnabled = cameraAnimationEnabled;

        window.kgContractionGraphPlan = contractionGraphPlan;

        window.kgContextContractionSnapshot = contextLayout.snapshot;

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
            '" class="concept-derived-from">';
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
            '" class="concept-backlinks">';
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
          replaceTypesetContent(body, html);
          if (!dialog.open) { dialog.showModal(); }
          if (window.MathJax && MathJax.typesetPromise) {
            MathJax.typesetPromise([body]).catch(function(err) {
              console.warn("MathJax inspection typesetting failed:", err);
            });
          }
        }

        function sequentialConceptIds() {
          var preferredDomains = (kgViewerConfig.domains || []).map(function(item) { return item.id; });
          var seen = {};
          var result = [];
          function domainRank(domain) {
            var index = preferredDomains.indexOf(String(domain || ""));
            return index === -1 ? preferredDomains.length : index;
          }
          moduleIds().slice().sort(function(leftId, rightId) {
            var left = getModule(leftId) || {};
            var right = getModule(rightId) || {};
            var domainDifference = domainRank(left.domain) - domainRank(right.domain);
            if (domainDifference) { return domainDifference; }
            var domainNameDifference = String(left.domain || "").localeCompare(
              String(right.domain || "")
            );
            if (domainNameDifference) { return domainNameDifference; }
            var sequenceDifference = Number(left.sequence || 0) - Number(right.sequence || 0);
            if (sequenceDifference) { return sequenceDifference; }
            return String(leftId).localeCompare(String(rightId));
          }).forEach(function(moduleId) {
            moduleMemberIds(getModule(moduleId)).forEach(function(conceptId) {
              conceptId = String(conceptId);
              if (!seen[conceptId] && getConcept(conceptId)) {
                seen[conceptId] = true;
                result.push(conceptId);
              }
            });
          });
          Object.keys(conceptData || {}).filter(function(conceptId) {
            return !seen[conceptId];
          }).sort(function(leftId, rightId) {
            return conceptDisplayId(leftId).localeCompare(
              conceptDisplayId(rightId), undefined, {numeric: true}
            );
          }).forEach(function(conceptId) { result.push(conceptId); });
          return result;
        }

        function renderSequentialConceptNavigation(conceptId) {
          var order = sequentialConceptIds();
          var index = order.indexOf(String(conceptId));
          if (index === -1 || order.length < 2) { return ""; }
          var wraps = index === order.length - 1;
          var nextId = order[(index + 1) % order.length];
          var next = getConcept(nextId) || {};
          var label = conceptDisplayId(nextId) + " " + searchDisplayText(next.label || nextId);
          return '<nav class="concept-sequential-navigation" aria-label="Sequential reading">' +
            '<button type="button" class="concept-next-button" data-next-concept-id="' +
            escapeHtml(nextId) + '">' + (wraps ? "Start again: " : "Next: ") +
            escapeHtml(label) + "</button></nav>";
        }

        window.kgSequentialConceptIds = sequentialConceptIds;

        function showConcept(nodeId, options) {
          options = options || {};
          hideConceptPreview(true);
          var concept = getConcept(nodeId);
          if (!concept) {
            detailsView.setItems([]);
            setActiveConceptSection(null);
            var missingPanel = document.getElementById("info_panel");
            replaceTypesetContent(missingPanel,
              "<h2>" + escapeHtml(conceptDisplayId(nodeId)) + "</h2>" +
              "<p>No concept data was found for this node.</p>");
            missingPanel.setAttribute("data-concept-id", String(nodeId));
            missingPanel.removeAttribute("data-module-id");
            missingPanel.scrollTop = 0;
            typesetInfoPanel(options);
            return;
          }

          var studyQuestions = Array.isArray(concept.study_questions) ? concept.study_questions : [];
          var conceptReferences = Array.isArray(concept.references) ? concept.references : [];
          var tocItems = conceptTocItems(
            nodeId,
            concept,
            studyQuestions,
            conceptReferences
          );
          detailsView.setItems(tocItems);

          var panel = document.getElementById("info_panel");
          sharedExplanations.beginPage("concept", nodeId, panel);
          var html = "";
          html += renderConceptMasthead(nodeId, concept, tocItems);
          html += renderConceptGraphic(nodeId, concept);
          html += "<hr>";
          html += renderConceptContent(nodeId, concept);
          html += notesController.renderOwnerNotes("concept", nodeId);
          html += renderConceptDerivedFrom(nodeId);
          html += renderConceptBacklinks(nodeId);
          if (studyQuestions.length > 0) {
            html += '<details id="' + escapeHtml(contentAnchorId(nodeId, "Study Questions")) +
              '" class="study-questions" data-note-block="true">';
            html += "<summary>" + renderNoteableHeading(
              "concept", nodeId, "Study Questions", "study-questions"
            ) + "</summary>";
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
          html += renderSequentialConceptNavigation(nodeId);
          var previousPanelConceptId = panel.getAttribute("data-concept-id") || "";
          var conceptChanged = previousPanelConceptId !== String(nodeId);
          replaceTypesetContent(panel, html);
          sharedExplanations.afterRender(panel);
          panel.setAttribute("data-concept-id", String(nodeId));
          panel.removeAttribute("data-module-id");
          if (conceptChanged && !options.scrollToSearchMatch) {
            panel.scrollTop = 0;
          }
          detailsView.suppressScrollSync(350);
          renderNotesOverview();
          var initialItem = initialTocItem(tocItems);
          setActiveConceptSection(initialItem ? initialItem.id : null);
          if (conceptChanged && !options.scrollToSearchMatch) {
            panel.scrollTop = 0;
          }
          typesetInfoPanel(options);
        }

        window.kgCloseEdgeKey = function() {
          setInfoPanelVisible(false);
        };

        window.kgShowEdgeKey = function() {
          setInfoPanelVisible(true);
          var relations = Object.keys(edgeKey).sort();
          var html = '<div class="edge-key-header">' +
            "<h2>Edge Key</h2>" +
            '<button id="kg_edge_key_close" type="button" ' +
            'aria-label="Close edge key" onclick="kgCloseEdgeKey()">Close</button>' +
            "</div>";

          if (relations.length === 0) {
            html += "<p>No edge key data was loaded.</p>";
            replaceTypesetContent(document.getElementById("info_panel"), html);
            schedulePanelContentRefit();
            return;
          }

          html += '<table class="edge-key-table">';
          html += "<thead><tr>" +
            "<th>Relation</th>" +
            "<th>Direction</th>" +
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
              "<td>" + escapeHtml(item.meaning || "") + "</td>" +
              "<td>" + escapeHtml(item.example || "") + "</td>" +
              "</tr>";
          });

          html += "</tbody></table>";
          replaceTypesetContent(document.getElementById("info_panel"), html);
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

        /* Viewport fitting around visible panels. */

        function scheduleViewportRefresh() {
          requestAnimationFrame(updateNodeLabelPositions);
        }

        function updatePhoneOrientation() {
          // CSS orientation describes viewport shape, which a keyboard can change.
          var orientation = window.screen && window.screen.orientation;
          var landscape;
          if (orientation && typeof orientation.type === "string") {
            landscape = orientation.type.indexOf("landscape") === 0;
          } else if (typeof window.orientation === "number") {
            landscape = Math.abs(window.orientation) === 90;
          } else {
            var active = document.activeElement;
            var typing = active && active.matches("input, textarea, [contenteditable='true']");
            landscape = window.innerWidth > window.innerHeight && !typing;
          }
          document.body.classList.toggle("kg-device-landscape", landscape);
        }

        function handleViewportResize() {
          updatePhoneOrientation();
          updateResponsiveControlLabels();
          updateGraphContextControls();
          applyWorkspaceSplit();
          schedulePanelContentRefresh();
          positionTutorialNarration();
        }

        function schedulePanelContentRefresh() {
          if (panelContentRefreshPending) { return; }
          panelContentRefreshPending = true;
          requestAnimationFrame(function() {
            panelContentRefreshPending = false;
            detailsView.compactGraphicSpacing();
            detailsView.refreshEquationOverflow();
            if (guidedTutorial) {
              guidedTutorial.refreshReadingControls();
              refreshTutorialPointerPosition();
            }
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
            detailsView.restoreTarget(null);
          }

          activeNodeId = type === "concept" ? id : null;
          activeModuleId = type === "module" ? id : null;
          updateSelectedConceptHeader(activeNodeId);
          setActiveConceptItem(activeNodeId);
          setActiveModuleItem(activeModuleId);
          renderGraphFromViewerState();

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

          if (statusPrefix === "Selected") {
            document.getElementById("kg_status").textContent = "";
          } else if (statusPrefix) {
            var label = type === "concept"
              ? conceptDisplayId(id)
              : ((getModule(id) || {}).title || id) + " module";
            document.getElementById("kg_status").innerText = statusPrefix + " " + label + ".";
          }
          updateGraphContextControls();
        }

        function commandTargetId(target, prefix, label) {
          target = String(target || "");
          if (target.indexOf(prefix) !== 0 || target.length === prefix.length) {
            throw new Error("Expected " + label + " target beginning with " + prefix);
          }
          return target.slice(prefix.length);
        }

        function commandEnumValue(command, key, allowed) {
          var value = String(command && command[key] || "");
          if (allowed.indexOf(value) === -1) {
            throw new Error(
              "Unsupported " + key + " for " + String(command && command.command || "command") +
              ": " + value
            );
          }
          return value;
        }

        function openTutorialDetailsBlock(blockId) {
          var panel = document.getElementById("info_panel");
          var target = panel.querySelector(
            '[data-content-block-id="' + cssAttributeValueEscape(blockId) + '"]'
          );
          if (!target) { throw new Error("Unknown or unavailable details block: " + blockId); }
          if (!detailsAreVisible()) { setViewerView(viewerState.view === "graph" ? "both" : viewerState.view); }
          openTargetForToc(target);
          if (target.id) { setActiveConceptSection(target.id); }
          scrollInfoPanelTargetBelowStickyToc(target, {immediate: true});
        }

        function expandContextModules() {
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
        }

        var tutorialDetailsRelationships = {
          "derived-from": {
            sectionSelector: ".concept-derived-from",
            showGraphTarget: "details:derived-from-show-graph",
            showGraphSelector: ".concept-derived-from-show-graph",
            label: "Derived from"
          },
          "where-used": {
            sectionSelector: ".concept-backlinks",
            showGraphTarget: "details:where-used-show-graph",
            showGraphSelector: ".concept-backlinks-show-graph",
            label: "Where this is used"
          }
        };

        function tutorialDetailsRelationshipForTarget(target) {
          return Object.keys(tutorialDetailsRelationships).map(function(key) {
            return tutorialDetailsRelationships[key];
          }).find(function(relationship) {
            return relationship.showGraphTarget === target;
          }) || null;
        }

        function openTutorialDetailsRelationship(sectionName) {
          var relationship = tutorialDetailsRelationships[String(sectionName || "")];
          var panel = document.getElementById("info_panel");
          var target = relationship
            ? panel.querySelector(relationship.sectionSelector)
            : null;
          if (!target) {
            throw new Error("Unknown or unavailable Details relationship: " + sectionName);
          }
          if (!detailsAreVisible()) { setViewerView(viewerState.view === "graph" ? "both" : viewerState.view); }
          target.open = true;
          if (target.id) { setActiveConceptSection(target.id); }
          scrollInfoPanelTargetBelowStickyToc(target, {immediate: true});
        }

        function showTutorialToolsSection(sectionName) {
          var sectionIds = {
            tutorials: "kg_tutorials_section",
            modules: "kg_modules_section",
            layouts: "kg_layouts_section",
            study: "kg_study_section",
            "personal-data": "kg_personal_data_section",
            notes: "kg_notes_section"
          };
          var sectionId = sectionIds[sectionName];
          var section = sectionId ? document.getElementById(sectionId) : null;
          if (!section) { throw new Error("Unknown Tools section: " + sectionName); }
          setControlsVisible(true);
          section.open = true;
        }

        function showTutorialSearch(query) {
          query = String(query || "");
          var input = document.getElementById("kg_search");
          input.value = query;
          buildConceptList(query);
          setSearchOpen(true);
        }

        async function executeViewerCommand(command, options) {
          options = options || {};
          command = command || {};
          var name = String(command.command || "");
          try {
            if (name === "select") {
              var target = String(command.target || "");
              var type;
              var id;
              if (target.indexOf("concept:") === 0) {
                type = "concept";
                id = commandTargetId(target, "concept:", "concept");
                if (!getConcept(id)) { throw new Error("Unknown concept: " + id); }
              } else if (target.indexOf("module:") === 0) {
                type = "module";
                id = commandTargetId(target, "module:", "module");
                if (!getModule(id)) { throw new Error("Unknown module: " + id); }
              } else {
                throw new Error("Select requires a concept: or module: target");
              }
              var selectionOptions = Object.assign({}, options.selectionOptions || {});
              if (options.origin === "tutorial") { selectionOptions.skipHistory = true; }
              selectViewerObject(type, id, options.statusPrefix || null, selectionOptions);
            } else if (name === "set-display-scope") {
              setViewerDisplayScope(commandEnumValue(
                command, "value", [DisplayScope.OVERVIEW, DisplayScope.FULL, DisplayScope.CONTEXT]
              ));
            } else if (name === "set-context") {
              var preset = commandEnumValue(command, "preset", Object.keys(ContextPreset).map(function(key) {
                return ContextPreset[key];
              }));
              var depth = commandEnumValue(command, "depth", Object.keys(ContextDepth).map(function(key) {
                return ContextDepth[key];
              }));
              setViewerContextRule({
                preset: preset,
                depth: depth,
                customTraversals: command.customTraversals || []
              });
            } else if (name === "set-view") {
              setViewerView(commandEnumValue(command, "value", ["both", "graph", "details"]));
            } else if (name === "set-module-representation") {
              var moduleId = commandTargetId(command.target, "module:", "module");
              if (!getModule(moduleId)) { throw new Error("Unknown module: " + moduleId); }
              var representation = commandEnumValue(
                command, "value", ["folded", "expanded"]
              );
              setSelectedModuleFoldState(moduleId, representation === "folded");
            } else if (name === "set-all-module-representations") {
              var allRepresentation = commandEnumValue(
                command, "value", ["folded", "expanded"]
              );
              if (allRepresentation === "folded") {
                foldAllModules();
              } else {
                unfoldAllModules();
              }
            } else if (name === "expand-context-modules") {
              expandContextModules();
            } else if (name === "fit") {
              fitViewerTarget(commandEnumValue(
                command, "value", ["reveal", "selection", "context", "displayed"]
              ));
            } else if (name === "open-details-block") {
              openTutorialDetailsBlock(commandTargetId(command.target, "block:", "block"));
            } else if (name === "open-study-questions") {
              var questions = document.querySelector("#info_panel .study-questions");
              if (!questions) { throw new Error("Study Questions are unavailable"); }
              if (!detailsAreVisible()) { setViewerView(viewerState.view === "graph" ? "both" : viewerState.view); }
              questions.open = true;
              scrollInfoPanelTargetBelowStickyToc(questions, {immediate: true});
            } else if (name === "open-details-graphic") {
              var graphic = document.querySelector("#info_panel .concept-figure");
              if (!graphic) { throw new Error("Details graphic is unavailable"); }
              if (!detailsAreVisible()) { setViewerView(viewerState.view === "graph" ? "both" : viewerState.view); }
              graphic.open = true;
              scrollInfoPanelTargetBelowStickyToc(graphic, {immediate: true});
            } else if (name === "open-details-relationship") {
              openTutorialDetailsRelationship(commandEnumValue(
                command, "value", ["derived-from", "where-used"]
              ));
            } else if (name === "set-relationship-full-tree") {
              var sectionName = commandEnumValue(command, "value", ["derived-from", "where-used"]);
              if (typeof command.full_tree !== "boolean") {
                throw new Error("set-relationship-full-tree requires full_tree boolean");
              }
              if (sectionName === "derived-from") { derivedFromFullTreeEnabled = command.full_tree; }
              else { backlinksFullTreeEnabled = command.full_tree; }
              refreshActiveConcept();
              openTutorialDetailsRelationship(sectionName);
            } else if (name === "show-relationship-in-graph") {
              var relationshipPreset = commandEnumValue(
                command, "preset", Object.keys(ContextPreset).map(function(key) {
                  return ContextPreset[key];
                })
              );
              if (typeof command.full_tree !== "boolean") {
                throw new Error("show-relationship-in-graph requires full_tree boolean");
              }
              await showRelationshipSectionInGraph(relationshipPreset, command.full_tree);
            } else if (name === "show-graph-concept-hover") {
              showTutorialConceptHover(
                commandTargetId(command.target, "concept:", "concept")
              );
            } else if (name === "show-graph-edge-hover") {
              showTutorialEdgeHover(tutorialEdgeReference(command.target, "edge:"));
            } else if (name === "show-tools-section") {
              showTutorialToolsSection(String(command.value || ""));
            } else if (name === "search") {
              var searchQuery = String(command.query || "").trim();
              if (!searchQuery || searchQuery.length > 200) {
                throw new Error("Search query must contain between 1 and 200 characters");
              }
              showTutorialSearch(searchQuery);
            } else if (name === "close-search") {
              setSearchOpen(false);
            } else if (name === "wait") {
              var milliseconds = Number(command.milliseconds);
              if (!Number.isFinite(milliseconds) || milliseconds < 0 || milliseconds > 5000) {
                throw new Error("Wait milliseconds must be between 0 and 5000");
              }
              return new Promise(function(resolve) {
                setTimeout(function() {
                  resolve({ok: true, command: name, origin: options.origin || "user"});
                }, milliseconds);
              });
            } else {
              throw new Error("Unsupported viewer command: " + name);
            }
          } catch (error) {
            return Promise.reject(error);
          }
          return Promise.resolve({ok: true, command: name, origin: options.origin || "user"});
        }

        window.kgExecuteViewerCommand = executeViewerCommand;

        function cloneSerializable(value) {
          if (value === undefined) { return null; }
          return JSON.parse(JSON.stringify(value));
        }

        function tutorialToolsSnapshot() {
          var controls = document.getElementById("kg_controls");
          var sectionIds = [
            "kg_tutorials_section",
            "kg_modules_section",
            "kg_layouts_section",
            "kg_study_section",
            "kg_personal_data_section",
            "kg_notes_section"
          ];
          var sections = {};
          sectionIds.forEach(function(id) {
            var section = document.getElementById(id);
            sections[id] = Boolean(section && section.open);
          });
          return {
            visible: Boolean(controls && !controls.classList.contains("kg-hidden")),
            sections: sections
          };
        }

        function tutorialDetailsSnapshot() {
          var panel = document.getElementById("info_panel");
          var active = panel.querySelector(".kg-active-section[data-content-block-id]");
          var sections = {};
          panel.querySelectorAll("details[id]").forEach(function(section) {
            sections[section.id] = section.open;
          });
          return {
            sections: sections,
            activeTargetId: detailsView.activeTargetId(),
            blockId: active ? active.getAttribute("data-content-block-id") : null,
            derivedFromFullTree: derivedFromFullTreeEnabled,
            whereUsedFullTree: backlinksFullTreeEnabled,
            scrollTop: panel.scrollTop
          };
        }

        function tutorialSearchSnapshot() {
          return {
            open: Boolean(document.getElementById("kg_search_section").open),
            query: document.getElementById("kg_search").value
          };
        }

        function captureTutorialPresentation() {
          var moduleRepresentation = {};
          moduleIdsWithMembers().forEach(function(moduleId) {
            moduleRepresentation[String(moduleId)] = selectedModuleIsFolded(moduleId)
              ? "folded"
              : "expanded";
          });
          return {
            schemaVersion: 1,
            selection: viewerSelectionSnapshot(),
            contextRule: createContextRule(
              viewerState.contextRule.preset,
              viewerState.contextRule.depth,
              viewerState.contextRule.customTraversals
            ),
            displayScope: viewerState.displayScope,
            view: viewerState.view,
            moduleRepresentation: moduleRepresentation,
            details: tutorialDetailsSnapshot(),
            contextFit: contextLayout.capture(),
            search: tutorialSearchSnapshot(),
            workspaceSplitPercent: workspaceSplitPercent,
            tools: tutorialToolsSnapshot(),
            camera: cameraSnapshot(),
            url: window.location.href,
            historyState: presentationHistoryState()
          };
        }

        function nextAnimationFrames(count) {
          count = Math.max(1, Number(count) || 1);
          return new Promise(function(resolve) {
            function next() {
              count -= 1;
              if (count <= 0) {
                resolve();
              } else {
                requestAnimationFrame(next);
              }
            }
            requestAnimationFrame(next);
          });
        }

        function restoreTutorialModuleRepresentations(representations) {
          resetContextFitInteraction();
          moduleIdsWithMembers().forEach(function(moduleId) {
            var folded = representations && representations[moduleId] === "folded";
            preferredFoldedModules[String(moduleId)] = folded;
            if (folded) {
              if (selectedModuleIsFolded(moduleId)) {
                syncFoldedModulePosition(moduleId);
              } else {
                foldModule(moduleId);
              }
            } else {
              unfoldModule(moduleId);
            }
          });
        }

        async function restoreTutorialPresentation(snapshot) {
          if (!snapshot || Number(snapshot.schemaVersion) !== 1) {
            throw new Error("Unsupported tutorial presentation snapshot");
          }
          resetContextFitInteraction();
          var details = snapshot.details || {};
          derivedFromFullTreeEnabled = Boolean(details.derivedFromFullTree);
          backlinksFullTreeEnabled = Boolean(details.whereUsedFullTree);
          viewerState.contextRule = createContextRule(
            snapshot.contextRule && snapshot.contextRule.preset,
            snapshot.contextRule && snapshot.contextRule.depth,
            snapshot.contextRule && snapshot.contextRule.customTraversals
          );
          viewerState.displayScope = [
            DisplayScope.OVERVIEW,
            DisplayScope.FULL,
            DisplayScope.CONTEXT
          ].indexOf(snapshot.displayScope) === -1
            ? DisplayScope.OVERVIEW
            : snapshot.displayScope;
          restoreTutorialModuleRepresentations(snapshot.moduleRepresentation || {});

          var selection = snapshot.selection || {type: "none", id: null};
          if (selection.type === "concept" && getConcept(selection.id)) {
            await executeViewerCommand(
              {command: "select", target: "concept:" + selection.id},
              {origin: "tutorial"}
            );
          } else if (selection.type === "module" && getModule(selection.id)) {
            await executeViewerCommand(
              {command: "select", target: "module:" + selection.id},
              {origin: "tutorial"}
            );
          } else {
            selectDefaultViewerObject();
          }

          setViewerView(snapshot.view || "both");

          var search = snapshot.search || {};
          var searchInput = document.getElementById("kg_search");
          searchInput.value = String(search.query || "");
          buildConceptList(searchInput.value);
          setSearchOpen(Boolean(search.open));

          applyWorkspaceSplit(snapshot.workspaceSplitPercent);
          var tools = snapshot.tools || {};
          setControlsVisible(Boolean(tools.visible));
          Object.keys(tools.sections || {}).forEach(function(id) {
            var section = document.getElementById(id);
            if (section) { section.open = Boolean(tools.sections[id]); }
          });

          await nextAnimationFrames(2);
          if (details.blockId) {
            var block = document.querySelector(
              '#info_panel [data-content-block-id="' +
              cssAttributeValueEscape(details.blockId) + '"]'
            );
            if (block) { openTargetForToc(block); }
          }
          detailsView.restoreTarget(details.activeTargetId);
          Object.keys(details.sections || {}).forEach(function(id) {
            var section = document.getElementById(id);
            if (section && section.tagName === "DETAILS") { section.open = details.sections[id]; }
          });
          updateConceptTocActive(detailsView.activeTargetId());
          document.getElementById("info_panel").scrollTop = Math.max(
            0, Number(details.scrollTop) || 0
          );

          if (snapshot.url) {
            window.history.replaceState(
              navigationHistoryState(cloneSerializable(snapshot.historyState)),
              "",
              snapshot.url
            );
          }
          graphCamera.cancelPendingRestore();
          contextLayout.restoreCheckpoint(snapshot.contextFit || {});
          if (snapshot.camera && snapshot.camera.position) {
            network.moveTo({
              position: snapshot.camera.position,
              scale: snapshot.camera.scale,
              animation: false
            });
            updateNodeLabelPositions();
          }
          updateGraphViewControls();
          updateGraphContextControls();
          return captureTutorialPresentation();
        }

        async function replayTutorialCommands(baseline, commands) {
          await restoreTutorialPresentation(baseline);
          for (var index = 0; index < (commands || []).length; index += 1) {
            await executeViewerCommand(commands[index], {origin: "tutorial"});
          }
          return captureTutorialPresentation();
        }

        window.kgCaptureTutorialPresentation = captureTutorialPresentation;
        window.kgRestoreTutorialPresentation = restoreTutorialPresentation;
        window.kgReplayTutorialCommands = replayTutorialCommands;

        var tutorialTargets = kgCreateTutorialTargets({
          network: network, nodes: nodes, edges: edges, adapter: visAdapter, container: graphContainer,
          activeRadiusScale: activeNodeRadiusScale, markup: contentMarkup, content: contentModel,
          selectedConceptId: function() { return activeNodeId; },
          foldControls: function() { return moduleFoldControlEls; },
          relationshipTarget: tutorialDetailsRelationshipForTarget,
          graph: {
            edgeHoverableInCurrentView: edgeHoverableInCurrentView,
            edgeRelation: edgeRelation,
            expandedModuleGeometrySnapshot: expandedModuleGeometrySnapshot,
            foldedModuleConceptProxyForConcept: foldedModuleConceptProxyForConcept,
            graphObjectDisplayText: graphObjectDisplayText,
            graphPositionForNode: graphPositionForNode,
            highlightHoveredEdge: highlightHoveredEdge,
            moduleGraphNodeId: moduleGraphNodeId,
            moduleIdForConcept: moduleIdForConcept,
            relationshipPhrase: relationshipPhrase,
            showEdgeTooltip: showEdgeTooltip,
            showNodeTooltip: showNodeTooltip
          }
        });
        var tutorialEdgeReference = tutorialTargets.tutorialEdgeReference;
        var showTutorialConceptHover = tutorialTargets.showTutorialConceptHover;
        var showTutorialEdgeHover = tutorialTargets.showTutorialEdgeHover;
        var guidedTutorial = kgCreateGuidedTutorial({
          routes: tutorialData, targets: tutorialTargets, execute: executeViewerCommand,
          presentation: {capture: captureTutorialPresentation, restore: restoreTutorialPresentation, replay: replayTutorialCommands},
          settle: nextAnimationFrames, hover: {hide: hideNodeTooltip, restore: restoreHoveredEdge},
          workspace: {dismissSplash: dismissSplash, setControlsVisible: setControlsVisible},
          camera: graphCamera, details: detailsView, markup: contentMarkup
        });
        var refreshTutorialPointerPosition = guidedTutorial.refreshTutorialPointerPosition;
        var tutorialPointerSnapshot = guidedTutorial.tutorialPointerSnapshot;
        var tutorialRouteById = guidedTutorial.tutorialRouteById;
        var positionTutorialNarration = guidedTutorial.positionTutorialNarration;
        var startTutorialById = guidedTutorial.startTutorialById;
        var requestedTutorialId = guidedTutorial.requestedTutorialId;
        var tutorialPlaybackSnapshot = guidedTutorial.tutorialPlaybackSnapshot;
        var initialiseTutorialPlayback = guidedTutorial.initialiseTutorialPlayback;

        window.kgTutorialPointerSnapshot = tutorialPointerSnapshot;

        window.kgTutorialPlaybackSnapshot = tutorialPlaybackSnapshot;
        window.kgStartTutorial = startTutorialById;

        function focusConcept(nodeId, statusPrefix, options) {
          return executeViewerCommand(
            {command: "select", target: "concept:" + String(nodeId)},
            {origin: "user", statusPrefix: statusPrefix, selectionOptions: options}
          );
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

        function defaultViewerSelection() {
          var preferences = kgViewerConfig.domains || [];
          for (var index = 0; index < preferences.length; index += 1) {
            var target = String(preferences[index].initialSelection || "").split(":");
            if (target[0] === "module" && getModule(target[1])) { return {type: "module", id: target[1]}; }
            if (target[0] === "concept" && getConcept(target[1])) { return {type: "concept", id: target[1]}; }
          }
          var moduleId = Object.keys(moduleData).sort()[0];
          if (moduleId) { return {type: "module", id: moduleId}; }
          var conceptId = Object.keys(conceptData).sort(compareConceptIds)[0];
          return conceptId ? {type: "concept", id: conceptId} : null;
        }

        function selectDefaultViewerObject() {
          var selection = defaultViewerSelection();
          if (!selection) { return; }
          selectViewerObject(selection.type, selection.id, null, {skipHistory: true});
          var state = selection.type === "module"
            ? {objectType: "module", moduleId: selection.id}
            : {objectType: "concept", nodeId: selection.id};
          window.history.replaceState(navigationHistoryState(state), "",
            selection.type === "module" ? moduleHash(selection.id) : conceptHash(selection.id));
        }

        function focusModule(moduleId, statusPrefix, options) {
          return executeViewerCommand(
            {command: "select", target: "module:" + String(moduleId)},
            {origin: "user", statusPrefix: statusPrefix, selectionOptions: options}
          );
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
          var anchorIds = nodes.get().filter(function(node) {
            return node.isOverviewAnchor;
          }).map(function(node) { return node.id; });
          if (anchorIds.length) { nodes.remove(anchorIds); }
          var selection = viewerSelectionSnapshot();
          var scope = viewerState.displayScope;
          var context = computeViewerContext(selection, viewerState.contextRule);
          var included = {};
          if (scope !== DisplayScope.CONTEXT) {
            Object.keys(originalNodes).forEach(function(id) { included[String(id)] = true; });
          } else {
            context.nodeIds.forEach(function(id) { included[String(id)] = true; });
          }

          nodes.update(allNodes.map(function(node) {
            var rendered = baseNodeForRender(node.id);
            var id = String(node.id);
            var inContext = context.keep[id] === true;
            var overview = scope === DisplayScope.OVERVIEW;
            rendered.hidden = !included[id];
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
            var overview = scope === DisplayScope.OVERVIEW;
            rendered.kgContextEdge = inContext && !overview;
            rendered.kgOverviewEdge = overview;
            if (!endpointsIncluded) {
              return setEdgeHidden(rendered, true);
            }
            if (inContext && !overview) {
              rendered.color = Object.assign({}, rendered.color || {}, {opacity: 0.95});
              rendered.width = Math.max(Number(rendered.width) || 0, 3.0);
              return setEdgeHidden(rendered, false);
            }
            if (scope !== DisplayScope.CONTEXT) {
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

          var fitIds = applyFoldedModuleOverlay(Object.keys(included), {
            compact: scope === DisplayScope.CONTEXT
          });

          // Cross-module edges pass below expanded module backgrounds. Within-
          // module edges remain in the normal foreground pass in both map modes.
          visAdapter.setLayeredEdges(scope === DisplayScope.CONTEXT ? [] : edges.get().filter(function(edge) {
            if (!visibleGraphEdge(edge)) { return false; }
            var fromModule = moduleIdFromGraphNodeId(edge.from) || moduleIdForConcept(edge.from);
            var toModule = moduleIdFromGraphNodeId(edge.to) || moduleIdForConcept(edge.to);
            return fromModule && toModule && fromModule !== toModule;
          }).map(function(edge) { return edge.id; }));

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
          updateNodeDragLocks();
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
          if (foldedIds.length === 0 && viewerState.displayScope !== DisplayScope.OVERVIEW) {
            return baseVisibleIds.slice();
          }

          var baseVisible = {};
          var hiddenMembers = {};
          var fitIds = [];
          var moduleNodeAdds = [];
          var moduleNodeUpdates = [];
          var moduleNodeMoves = [];
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
                moduleNodeUpdates.push(moduleNode);
              } else {
                moduleNodeAdds.push(moduleNode);
              }
              moduleNodeMoves.push(moduleNode);
              fitIds.push(graphNodeId);
            } else if (nodes.get(graphNodeId)) {
              moduleNodeUpdates.push({id: graphNodeId, hidden: true});
            }
          });

          if (moduleNodeAdds.length > 0) {
            nodes.add(moduleNodeAdds);
          }
          if (moduleNodeUpdates.length > 0) {
            nodes.update(moduleNodeUpdates);
          }
          // DataSet updates truncate x/y in vis-network; dragging does not.
          moduleNodeMoves.forEach(function(moduleNode) {
            network.moveNode(moduleNode.id, moduleNode.x, moduleNode.y);
          });

          nodes.update(Object.keys(hiddenMembers).filter(function(id) {
            return Boolean(nodes.get(id));
          }).map(function(id) {
            return {id: id, hidden: true};
          }));

          // Expanded modules use transparent, non-interactive boxes only as
          // boundary endpoints. They never replace member concepts or enter fitIds.
          var moduleEndpointMembers = Object.assign({}, hiddenMembers);
          if (viewerState.displayScope === DisplayScope.OVERVIEW) {
            moduleIdsWithMembers().forEach(function(moduleId) {
              moduleMemberIds(getModule(moduleId)).forEach(function(id) {
                moduleEndpointMembers[String(id)] = true;
              });
              if (selectedModuleIsFolded(moduleId)) { return; }
              var footprint = moduleFootprint(moduleId);
              var anchor = Object.assign(moduleBoxShape(footprint), {
                id: moduleGraphNodeId(moduleId), moduleId: moduleId,
                isModuleNode: true, isOverviewAnchor: true,
                x: footprint.x, y: footprint.y, physics: false, fixed: true,
                hidden: false, label: "", opacity: 0,
                font: {size: 1, face: "Arial", vadjust: 0},
                borderWidth: 0, chosen: false
              });
              nodes.add(anchor);
              network.moveNode(anchor.id, anchor.x, anchor.y);
              visAdapter.disableNodeHitTesting(anchor.id);
            });
          }
          var moduleEdges = projectedModuleEdges(moduleEndpointMembers);
          edges.update(allEdges.filter(function(e) {
            var crossesModules = viewerState.displayScope === DisplayScope.OVERVIEW &&
              moduleIdForConcept(e.from) !== moduleIdForConcept(e.to);
            return crossesModules || hiddenMembers[String(e.from)] || hiddenMembers[String(e.to)];
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
            if (params.nodes.length === 0 && params.edges && params.edges.length > 0) {
                showEdgeDetails(params.edges[0]);
                return;
            }

            if (params.nodes.length === 0) { return; }

            const nodeId = params.nodes[0];
            const clickedModuleId = moduleIdFromGraphNodeId(nodeId);
            if (clickedModuleId && getModule(clickedModuleId)) {
              focusModule(clickedModuleId, "Selected");
              return;
            }

            focusConcept(nodeId, "Selected");
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
          if (
            !renderedEdgeWidthsDirty &&
            renderedEdgeWidthScale === scale &&
            renderedEdgeWidthHoverId === hoveredEdgeId
          ) {
            return;
          }
          edges.get().forEach(function(edge) {
            if (edge.hidden) { return; }
            var width = Number(edge.width) || 1;
            var base = edge.isModuleEdge ? Number(edge.kgBaseWidth)
              : Number((originalEdges[edge.id] || {}).width);
            base = base > 0 ? base : width;
            // Keep a readable screen-space minimum while retaining hover emphasis.
            // Change only the native drawing options, never the authored DataSet.
            var minimumPixels = edge.isModuleEdge ? 2.8 : 1.5;
            if (String(edge.id) === String(hoveredEdgeId)) {
              minimumPixels *= 2;
            }
            visAdapter.setDrawnEdgeWidth(edge.id, scale < 1
              ? Math.max(width, minimumPixels / scale)
              : width);
          });
          renderedEdgeWidthsDirty = false;
          renderedEdgeWidthScale = scale;
          renderedEdgeWidthHoverId = hoveredEdgeId;
        }

        edges.on("*", function() {
          renderedEdgeWidthsDirty = true;
        });

        var expandedModulesForFrame = [];
        network.on("beforeDrawing", function(ctx) {
          expandedModulesForFrame = expandedModuleOutlineSnapshot();
          updateRenderedEdgeWidths();
          if (viewerState.displayScope !== DisplayScope.CONTEXT) {
            visAdapter.drawLayeredEdges(ctx, graphPresentation.clipModuleEdgeEndpoints);
            graphPresentation.drawExpandedModuleBackgrounds(ctx, expandedModulesForFrame);
          }
        });
        network.on("afterDrawing", function(ctx) {
          if (!initialGraphProjectionReady) { return; }
          graphPresentation.drawExpandedModuleFooters(ctx, expandedModulesForFrame);
          drawExpandedModuleOutlines(ctx, expandedModulesForFrame);
          drawFoldedModuleGraphics(ctx);
          drawVisibleNodes(ctx);
          drawGraphCompletionMarkers(ctx);
          graphPresentation.drawExpandedModuleLabels(ctx, expandedModulesForFrame);
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
        if (window.screen && window.screen.orientation && window.screen.orientation.addEventListener) {
          window.screen.orientation.addEventListener("change", handleViewportResize);
        }
        if (window.visualViewport) {
          window.visualViewport.addEventListener("resize", handleViewportResize);
          window.visualViewport.addEventListener("scroll", scheduleViewportRefresh);
        }
        graphContainer.addEventListener("mouseleave", function() {
          restoreHoveredEdge();
          hideNodeTooltip();
        });

        var graphCanvas = visAdapter.canvasElement();
        var lockedDragProbe = null;
        var lockedLayoutNoticeShown = false;
        function graphNodeAtPointerEvent(e) {
          if (!network.getNodeAt || viewerState.view === "details") { return null; }
          var surface = graphCanvas || graphContainer;
          var rect = surface.getBoundingClientRect();
          return network.getNodeAt({x: e.clientX - rect.left, y: e.clientY - rect.top});
        }
        (graphCanvas || graphContainer).addEventListener("pointerdown", function(e) {
          var nodeId = graphNodeAtPointerEvent(e);
          if (!nodeId || nodeDraggingEnabled(nodeId)) {
            lockedDragProbe = null;
            return;
          }
          lockedDragProbe = {x: e.clientX, y: e.clientY};
        }, true);
        (graphCanvas || graphContainer).addEventListener("pointermove", function(e) {
          if (!lockedDragProbe) { return; }
          if (Math.hypot(e.clientX - lockedDragProbe.x, e.clientY - lockedDragProbe.y) < 5) { return; }
          if (!lockedLayoutNoticeShown) {
            lockedLayoutNoticeShown = true;
            showTransientContextNotice(
              contextLayout.isActive()
                ? "Only context nodes can be adjusted in this temporary Fit++ arrangement."
                : "Layout locked — enable editing in Tools → Layouts.",
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

        moduleFoldControlLayer.addEventListener("click", function(e) {
          var button = e.target.closest(".kg-module-corner-control");
          if (!button) { return; }
          e.preventDefault();
          e.stopPropagation();
          var moduleId = button.getAttribute("data-module-id");
          executeViewerCommand({
            command: "set-module-representation",
            target: "module:" + moduleId,
            value: selectedModuleIsFolded(moduleId) ? "expanded" : "folded"
          }, {origin: "user"});
        });

        window.addEventListener("popstate", function(event) {
          var marker = event.state && event.state.kgNavigation;
          if (marker && marker.session === navigationSession) {
            navigationIndex = marker.index;
            navigationMoving = false;
          } else {
            initialiseSelectionHistory();
          }
          updateHistoryControls();
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
            selectDefaultViewerObject();
          }
        });

        document.addEventListener("keydown", allowBrowserHistoryShortcut, true);
        document.getElementById("kg_history_back").addEventListener("click", function() {
          navigateSelectionHistory(-1);
        });
        document.getElementById("kg_history_forward").addEventListener("click", function() {
          navigateSelectionHistory(1);
        });

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
          executeViewerCommand(
            {command: "set-display-scope", value: e.target.value},
            {origin: "user"}
          );
        });

        document.getElementById("kg_view_select").addEventListener("change", function(e) {
          executeViewerCommand({command: "set-view", value: e.target.value}, {origin: "user"});
        });

        document.getElementById("kg_study_list").addEventListener("click", function(e) {
          var reset = e.target.closest(".kg-study-reset-question");
          if (reset) {
            e.preventDefault();
            var resetQuestionId = reset.getAttribute("data-question-id");
            var resetIndexed = studyController.indexedQuestion(resetQuestionId);
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
        document.getElementById("kg_graph_completion_markers").addEventListener(
          "change",
          function(e) { setGraphCompletionMarkersEnabled(e.target.checked); }
        );
        window.addEventListener("kg:study-progress-changed", renderStudyScorecard);

        document.getElementById("kg_context_preset_select").addEventListener("change", function(e) {
          var preset = e.target.value;
          var customPanel = document.getElementById("kg_custom_context");
          if (preset === ContextPreset.CUSTOM) {
            openCustomContextEditor();
            return;
          }
          customPanel.hidden = true;
          executeViewerCommand({
            command: "set-context",
            preset: preset,
            depth: viewerState.contextRule.depth
          }, {origin: "user"});
        });
        document.getElementById("kg_context_depth_select").addEventListener("change", function(e) {
          executeViewerCommand({
            command: "set-context",
            preset: viewerState.contextRule.preset,
            depth: e.target.value,
            customTraversals: viewerState.contextRule.customTraversals
          }, {origin: "user"});
        });
        document.getElementById("kg_fit_select").addEventListener("change", function() {
          clearContextFitPriming();
        });
        document.getElementById("kg_fit_apply").addEventListener("click", function() {
          executeViewerCommand({
            command: "fit",
            value: document.getElementById("kg_fit_select").value
          }, {origin: "user"});
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
          executeViewerCommand({
            command: "set-context",
            preset: ContextPreset.CUSTOM,
            depth: document.getElementById("kg_context_depth_select").value,
            customTraversals: traversals
          }, {origin: "user"});
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
            executeViewerCommand({
              command: "set-module-representation",
              target: "module:" + moduleId,
              value: "expanded"
            }, {origin: "user"});
          }
        });
        document.getElementById("kg_expand_context_modules").addEventListener("click", function() {
          executeViewerCommand({command: "expand-context-modules"}, {origin: "user"});
        });
        document.getElementById("kg_graph_selection").addEventListener("click", function() {
          setViewerView("both");
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
        initialiseGoogleDriveSync();
        document.getElementById("kg_cloud_sync_connect").addEventListener(
          "click", connectGoogleDrive
        );
        document.getElementById("kg_cloud_sync_now").addEventListener(
          "click", syncPersonalDataNow
        );
        document.getElementById("kg_cloud_sync_disconnect").addEventListener(
          "click", disconnectGoogleDrive
        );
        document.getElementById("kg_cloud_sync_attention").addEventListener(
          "click",
          function() {
            setControlsVisible(true);
            document.getElementById("kg_personal_data_section").open = true;
          }
        );
        document.addEventListener("visibilitychange", personalDataController.onVisibilityChange);

        document.getElementById("kg_notes_list").addEventListener("click", function(e) {
          var item = e.target.closest(".kg-note-list-item");
          if (!item) { return; }

          e.preventDefault();
          var note = findUserNote(item.getAttribute("data-note-id"));
          var targetType = item.getAttribute("data-target-type");
          var targetId = item.getAttribute("data-target-id");
          if (!note) { return; }
          notesController.openNote(note.id);
          if (targetType === "module" && getModule(targetId)) {
            focusModule(targetId, "Selected");
          } else if (targetType === "concept" && getConcept(targetId)) {
            focusConcept(targetId, "Selected");
          }
          notesController.revealNote(note.id, false);
        });

        document.getElementById("kg_notes_delete_all").addEventListener("click", function() {
          if (!window.confirm("Delete all your notes in all domains, including missing targets? Deletions will also synchronise to your other devices.")) { return; }
          notesController.deleteAllNotes();
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
          var explanationReturn = e.target.closest(".kg-content-return");
          if (explanationReturn) {
            e.preventDefault();
            var explanationAncestor = document.getElementById(explanationReturn.getAttribute("data-content-return-id"));
            if (explanationAncestor) {
              scrollInfoPanelTargetBelowStickyToc(explanationAncestor, {immediate: true});
              var explanationHeading = explanationAncestor.querySelector(":scope > summary");
              if (explanationHeading) { explanationHeading.focus({preventScroll: true}); }
            }
            return;
          }
          var nextConceptButton = e.target.closest(".concept-next-button");
          if (nextConceptButton) {
            e.preventDefault();
            navigateToConcept(
              nextConceptButton.getAttribute("data-next-concept-id"),
              "Selected"
            );
            return;
          }

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

          var retryButton = e.target.closest(".study-retry");
          if (retryButton) {
            e.preventDefault();
            studyController.retryStudyQuestion(retryButton.closest(".study-question"));
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

          var ownerNoteButton = e.target.closest(".kg-note-owner-action");
          if (ownerNoteButton) {
            e.preventDefault();
            var ownerNote = notesController.createOwnerNote(
              ownerNoteButton.getAttribute("data-target-type"), ownerNoteButton.getAttribute("data-target-id")
            );
            refreshActiveConcept();
            notesController.revealNote(ownerNote.id, true);
            return;
          }

          var addNoteButton = e.target.closest(".kg-add-note");
          if (addNoteButton) {
            e.preventDefault();
            var noteTargetType = addNoteButton.getAttribute("data-target-type") || "concept";
            var noteTargetId = addNoteButton.getAttribute("data-target-id") || activeNodeId;
            var noteBlockId = addNoteButton.getAttribute("data-anchor-block-id") || "";
            var noteSectionKey = addNoteButton.getAttribute("data-anchor-section-key") || "";
            var noteAnchorIndex = Number(addNoteButton.getAttribute("data-anchor-index")) || 0;
            var canonicalAnchor = canonicalNoteAnchor(
              noteTargetType, noteTargetId, noteBlockId, noteSectionKey, noteAnchorIndex
            );
            var enclosingSection = addNoteButton.closest("#info_panel > details");
            var enclosingSectionId = enclosingSection && enclosingSection.open
              ? enclosingSection.id
              : "";
            cancelNotePlacement(addNoteButton.closest('[data-note-placement="active"]'));
            var createdNote = createUserNote(
              noteTargetType,
              noteTargetId,
              addNoteButton.getAttribute("data-section") || "",
              noteAnchorIndex,
              addNoteButton.getAttribute("data-anchor-after") || "",
              canonicalAnchor || {
                blockId: noteBlockId,
                sectionKey: noteSectionKey,
                contextBefore: addNoteButton.getAttribute("data-anchor-context-before") || "",
                contextAfter: addNoteButton.getAttribute("data-anchor-context-after") || ""
              }
            );
            refreshActiveConcept();
            if (enclosingSectionId) {
              var refreshedSection = document.getElementById(enclosingSectionId);
              if (refreshedSection) { refreshedSection.open = true; }
            }
            window.requestAnimationFrame(function() {
              var titleInput = noteEditorField(createdNote.id, ".user-note-title-input");
              if (titleInput) {
                titleInput.focus();
                titleInput.select();
              }
            });
            return;
          }

          var noteBlockAction = e.target.closest(".kg-note-block-action");
          if (noteBlockAction) {
            e.preventDefault();
            e.stopPropagation();
            beginNotePlacement(noteBlockAction);
            return;
          }

          var notePlacementCancel = e.target.closest(".kg-note-placement-cancel");
          if (notePlacementCancel) {
            e.preventDefault();
            e.stopPropagation();
            cancelNotePlacement(
              notePlacementCancel.closest('[data-note-placement="active"]'),
              true
            );
            return;
          }

          var placementBlock = e.target.closest('[data-note-placement="active"]');
          var placementLine = e.target.closest(".kg-note-placement-target");
          if (
            placementBlock && placementLine &&
            Date.now() >= notePlacementSuppressClickUntil &&
            !e.target.closest("a, button, input, textarea, select, label")
          ) {
            e.preventDefault();
            var placementRow = placementLine.nextElementSibling;
            var placementButton = placementRow && placementRow.querySelector(".kg-add-note");
            if (placementButton) { placementButton.click(); }
            return;
          }

          var insertMathsButton = e.target.closest(".user-note-insert-maths");
          if (insertMathsButton) {
            e.preventDefault();
            notesController.insertMaths(insertMathsButton.getAttribute("data-note-id"));
            return;
          }

          var editNoteButton = e.target.closest(".user-note-edit");
          if (editNoteButton) {
            e.preventDefault();
            notesController.editNote(editNoteButton.getAttribute("data-note-id"));
            return;
          }

          var closeNoteButton = e.target.closest(".user-note-close");
          if (closeNoteButton) {
            e.preventDefault();
            closeUserNote(closeNoteButton.getAttribute("data-note-id"));
            return;
          }

          var deleteNoteButton = e.target.closest(".user-note-delete");
          if (deleteNoteButton) {
            e.preventDefault();
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
            executeViewerCommand({
              command: "set-module-representation",
              target: "module:" + foldModuleId,
              value: foldState === "folded" ? "folded" : "expanded"
            }, {origin: "user"});
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
            var blockId = readToggle.getAttribute("data-read-block-id");
            if (blockId) {
              setContentBlockRead(
                blockId,
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
            var refreshedDerivedSection = document.getElementById(derivedSectionId);
            if (refreshedDerivedSection) { refreshedDerivedSection.open = true; }
            detailsView.suppressScrollSync(1000);
            setActiveConceptSection(derivedSectionId);
            return;
          }

          var backlinksFullTree = e.target.closest(".concept-backlinks-full-tree");
          if (backlinksFullTree) {
            var backlinksSection = backlinksFullTree.closest(".concept-backlinks");
            var backlinksSectionId = backlinksSection ? backlinksSection.id : null;
            backlinksFullTreeEnabled = backlinksFullTree.checked;
            refreshActiveConcept();
            var refreshedBacklinksSection = document.getElementById(backlinksSectionId);
            if (refreshedBacklinksSection) { refreshedBacklinksSection.open = true; }
            detailsView.suppressScrollSync(1000);
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
            var indexed = studyController.indexedQuestion(questionId);
            var question = indexed && indexed.question;
            var progress = studyController.getQuestion(questionId) || null;
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

        document.getElementById("info_panel").addEventListener("keydown", function(e) {
          var placementBlock = e.target.closest('[data-note-placement="active"]') ||
            document.querySelector('#info_panel [data-note-placement="active"]');
          if (!placementBlock) { return; }
          if (e.key === "Escape") {
            e.preventDefault();
            cancelNotePlacement(placementBlock, true);
            return;
          }
          if (e.key !== "Enter" && e.key !== " ") { return; }
          var placementLine = e.target.closest(".kg-note-placement-target");
          if (!placementLine) { return; }
          e.preventDefault();
          var placementRow = placementLine.nextElementSibling;
          var placementButton = placementRow && placementRow.querySelector(".kg-add-note");
          if (placementButton) { placementButton.click(); }
        });

        document.getElementById("info_panel").addEventListener("pointerdown", function(e) {
          if (!e.target.closest('[data-note-placement="active"] .kg-note-placement-target')) {
            notePlacementPointerStart = null;
            return;
          }
          notePlacementPointerStart = {x: e.clientX, y: e.clientY};
        }, {passive: true});

        document.getElementById("info_panel").addEventListener("pointermove", function(e) {
          if (!notePlacementPointerStart) { return; }
          var dx = e.clientX - notePlacementPointerStart.x;
          var dy = e.clientY - notePlacementPointerStart.y;
          if ((dx * dx) + (dy * dy) > 64) {
            notePlacementSuppressClickUntil = Date.now() + 400;
          }
        }, {passive: true});

        document.getElementById("info_panel").addEventListener("pointerup", function() {
          notePlacementPointerStart = null;
        }, {passive: true});

        document.getElementById("info_panel").addEventListener("pointercancel", function() {
          notePlacementPointerStart = null;
          notePlacementSuppressClickUntil = Date.now() + 400;
        }, {passive: true});

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
            sharedExplanations.toggled(e.target);
            if (
              e.target.classList.contains("user-note")
            ) {
              notesController.noteToggled(e.target);
              schedulePanelContentRefit();
              return;
            }
            schedulePanelContentRefit();
          }
        }, true);

        /* Initial render. */
        updatePhoneOrientation();
        initialiseTutorialPlayback();
        applyDefaultModuleFoldState();
        buildModuleFoldControls();
        buildNodeLabels();
        refreshModuleFootprints();
        if (document.fonts && document.fonts.addEventListener) {
          document.fonts.addEventListener("loadingdone", refreshModuleFootprintsAfterFontLoad);
        }
        buildConceptList("");
        buildModuleList();
        migrateUserNotesState();
        renderNotesOverview();
        renderStudyScorecard();
        document.getElementById("kg_graph_completion_markers").checked =
          graphCompletionMarkersEnabled;
        updateResponsiveControlLabels();
        updateGraphViewControls();
        updateWorkspaceViewControl();
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
        initialGraphProjectionReady = true;
        network.redraw();

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
          selectDefaultViewerObject();
        }
        initialiseSelectionHistory();
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
        var directTutorialId = requestedTutorialId();
        if (directTutorialId && tutorialRouteById(directTutorialId)) {
          requestAnimationFrame(function() {
            requestAnimationFrame(function() {
              setTimeout(function() { startTutorialById(directTutorialId); }, 0);
            });
          });
        } else {
          showSplashOnFirstLoad();
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
    
