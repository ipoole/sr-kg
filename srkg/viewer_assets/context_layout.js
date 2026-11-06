/* Temporary Fit++ state, drag membership and checkpoint ownership; never persists personal layout. */
function kgCreateContextLayout(options) {
  "use strict";
  var network = options.network, nodes = options.nodes, edges = options.edges;
  var originalEdges = options.originalEdges;
  var graphCamera = options.camera;
  var fitNodesToAvailableRect = graphCamera.fitNodesToAvailableRect;
  var cameraAnimationEnabled = graphCamera.cameraAnimationEnabled;
  var revealViewerSelection = options.revealSelection;
  var updateGraphViewControls = options.onControlsChange, updateNodeLabelPositions = options.onPositionsChange;
  var showContextNotice = options.notice;
  function showTemporaryNotice() {
    showContextNotice("Temporary draggable layout", "context-contracted");
  }

  var activeNodeRadiusScale = options.labels.activeRadiusScale, nodeLabelFontSize = options.labels.fontSize;
  var kgNodeLabelConfig = {hideBelowPx: options.labels.hideBelowPx};
  var contextFitPrimedKey = null, contextContractionState = null;
  var contractionGraphPlan = kgGraphModel.contractionGraphPlan;
  var viewerSelectionSnapshot = options.graph.viewerSelectionSnapshot;
  var representedNodeIds = options.graph.representedNodeIds;
  var selectionRepresentationNodeIds = options.graph.selectionRepresentationNodeIds;
  var visibleGraphNode = options.graph.visibleGraphNode;
  var graphPositionForNode = options.graph.graphPositionForNode;
  var moduleIdFromGraphNodeId = options.graph.moduleIdFromGraphNodeId;
  var selectedModuleIsFolded = options.graph.selectedModuleIsFolded;
  var moduleGraphNodePosition = options.graph.moduleGraphNodePosition;
  var getConcept = options.graph.getConcept;
  var effectiveConceptPosition = options.graph.effectiveConceptPosition;
  var conceptFootprintExtents = options.graph.conceptFootprintExtents;
  var validLayoutPosition = kgLayoutGeometry.validLayoutPosition;
  var copyLayoutPosition = kgLayoutGeometry.copyLayoutPosition;
  var reducedContractionExtents = kgLayoutGeometry.reducedContractionExtents;
  var clearInitialContractionCollision = kgLayoutGeometry.clearInitialContractionCollision;
  var contractionCollisionEntry = kgLayoutGeometry.contractionCollisionEntry;

  function isActive() { return Boolean(contextContractionState); }
  function canMove(id) {
    return Boolean(contextContractionState && Object.prototype.hasOwnProperty.call(contextContractionState.finalPositions, String(id)));
  }
  function recordDrag(id, position) {
    if (canMove(id) && validLayoutPosition(position)) {
      contextContractionState.finalPositions[String(id)] = copyLayoutPosition(position);
    }
  }
  function capture() {
    return {primedKey: contextFitPrimedKey, contraction: contextContractionState
      ? Object.assign(JSON.parse(JSON.stringify(contextContractionState)), {
          finalPositions: network.getPositions(Object.keys(contextContractionState.finalPositions))}) : null};
  }
  function restoreCheckpoint(checkpoint) {
    contextFitPrimedKey = checkpoint.primedKey || null;
    contextContractionState = checkpoint.contraction ? JSON.parse(JSON.stringify(checkpoint.contraction)) : null;
    if (!contextContractionState) { return; }
    Object.keys(contextContractionState.finalPositions).forEach(function(id) {
      var position = contextContractionState.finalPositions[id];
      if (nodes.get(id) && validLayoutPosition(position)) { network.moveNode(id, position.x, position.y); }
    });
    showTemporaryNotice();
  }
  function snapshot() {
    return {primed: Boolean(contextFitPrimedKey), active: isActive(),
      anchorId: contextContractionState ? contextContractionState.anchorId : null,
      depthByNode: contextContractionState ? Object.assign({},contextContractionState.depthByNode) : {},
      parentByNode: contextContractionState ? Object.assign({},contextContractionState.parentByNode) : {}};
  }

  function updateFitApplyButton() {
    var lastGraphRender = options.renderedGraph();
    var button = document.getElementById("kg_fit_apply");
    if (!button) { return; }
    var fitSelect = document.getElementById("kg_fit_select");
    var target = fitSelect ? fitSelect.value : "context";
    var selection = viewerSelectionSnapshot();
    var hasTarget = false;
    if (target === "reveal" || target === "selection") {
      hasTarget = selection.type !== "none" &&
        selectionRepresentationNodeIds(selection).length > 0;
    } else if (target === "displayed") {
      hasTarget = Boolean(lastGraphRender && lastGraphRender.fitIds.length > 0);
    } else {
      hasTarget = selection.type !== "none" && representedNodeIds(
        lastGraphRender ? lastGraphRender.contextNodeIds : []
      ).length > 0;
    }
    var primed = hasTarget && Boolean(contextFitPrimedKey);
    button.disabled = !hasTarget;
    button.textContent = primed ? "Fit++" : "Fit";
    button.setAttribute("data-fit-action", primed ? "contract" : "fit");
    button.setAttribute(
      "aria-label",
      !hasTarget
        ? "No available objects to fit"
        : primed ? "Temporarily contract and fit this context" : "Fit selected target"
    );
    button.title = !hasTarget
      ? (target === "displayed"
        ? "Nothing is displayed to fit"
        : "Select a concept or module to use this frame")
      : primed
        ? "Temporarily compact the context around the selection, then fit it into view. Navigate away to restore the layout."
        : "Adjust the camera to the chosen frame. Fitting the context enables Fit++.";
    document.getElementById("kg_fit_help").textContent = button.title;
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
    var notice = document.getElementById("kg_context_notice");
    if (notice && notice.getAttribute("data-kind") === "context-contracted") {
      showContextNotice("", "context-contracted");
    }
    updateGraphViewControls();
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
      var notice = document.getElementById("kg_context_notice");
      if (notice && notice.getAttribute("data-kind") === "context-contracted") {
        showContextNotice("", "context-contracted");
      }
      updateGraphViewControls();
    }
    clearContextFitPriming();
  }

  function contextContractionCandidate() {
    var lastGraphRender = options.renderedGraph();
    var selection = viewerSelectionSnapshot();
    if (
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
    var nodeKeep = {};
    var adjacency = {};
    nodeIds.forEach(function(nodeId) {
      nodeKeep[nodeId] = true;
      adjacency[nodeId] = [];
    });
    (lastGraphRender.contextEdgeIds || []).forEach(function(edgeId) {
      var edge = originalEdges[String(edgeId)] || edges.get(String(edgeId));
      if (!edge) { return; }
      var fromIds = representedNodeIds([String(edge.from)]);
      var toIds = representedNodeIds([String(edge.to)]);
      var from = fromIds.length === 1 ? String(fromIds[0]) : null;
      var to = toIds.length === 1 ? String(toIds[0]) : null;
      if (!from || !to || from === to || !nodeKeep[from] || !nodeKeep[to]) {
        return;
      }
      if (adjacency[from].indexOf(to) === -1) { adjacency[from].push(to); }
      if (adjacency[to].indexOf(from) === -1) { adjacency[to].push(from); }
    });
    Object.keys(adjacency).forEach(function(nodeId) {
      adjacency[nodeId].sort();
    });
    return {
      anchorId: anchorId,
      nodeIds: nodeIds,
      adjacency: adjacency,
      key: JSON.stringify({
        selection: selection,
        contextRule: options.contextRule(),
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
      return reducedContractionExtents({
        left: width / 2,
        right: width / 2,
        top: height / 2,
        bottom: height / 2,
        width: width,
        height: height
      });
    }
    var baseRadius = Number(node.visualSize) || Number(node.size) || 18;
    var radius = baseRadius;
    if (nodeId === String(options.selectedConceptId() || "")) {
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
    var label = options.readLabels()[nodeId];
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
    return reducedContractionExtents({
      left: left,
      right: right,
      top: top,
      bottom: bottom,
      width: left + right,
      height: top + bottom
    });
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
    var plan = contractionGraphPlan(candidate);
    var placed = [{
      id: candidate.anchorId,
      position: copyLayoutPosition(anchorPosition),
      extents: contractionNodeExtents(candidate.anchorId)
    }];
    // Expanded-module footers stay with the authored module boundary while
    // Fit++ temporarily moves context nodes. Keep these reserved areas clear.
    (options.fixedObstacles ? options.fixedObstacles() : []).forEach(function(bounds) {
      placed.push({position: {x: (bounds.left + bounds.right) / 2,
        y: (bounds.top + bounds.bottom) / 2}, extents: {
        left: bounds.width / 2, right: bounds.width / 2,
        top: bounds.height / 2, bottom: bounds.height / 2,
        width: bounds.width, height: bounds.height
      }});
    });
    var finalPositions = {};
    var parentByNode = {};
    finalPositions[candidate.anchorId] = copyLayoutPosition(anchorPosition);

    for (var depth = 1; depth <= plan.maximumDepth; depth += 1) {
      var layer = candidate.nodeIds.filter(function(nodeId) {
        return plan.depthByNode[nodeId] === depth &&
          validLayoutPosition(originalPositions[nodeId]);
      }).map(function(nodeId) {
        var start = originalPositions[nodeId];
        var candidates = (plan.parentCandidates[nodeId] || []).filter(function(parentId) {
          return validLayoutPosition(finalPositions[parentId]);
        });
        var parentId = candidates.sort(function(leftId, rightId) {
          var left = finalPositions[leftId];
          var right = finalPositions[rightId];
          var leftDistance = Math.hypot(start.x - left.x, start.y - left.y);
          var rightDistance = Math.hypot(start.x - right.x, start.y - right.y);
          return leftDistance - rightDistance ||
            String(leftId).localeCompare(String(rightId));
        })[0];
        var parentPosition = parentId ? finalPositions[parentId] : null;
        return {
          nodeId: nodeId,
          parentId: parentId,
          parentPosition: parentPosition,
          distance: parentPosition
            ? Math.hypot(start.x - parentPosition.x, start.y - parentPosition.y)
            : Infinity
        };
      }).filter(function(item) {
        return Boolean(item.parentId && item.parentPosition);
      }).sort(function(left, right) {
        return left.distance - right.distance ||
          String(left.nodeId).localeCompare(String(right.nodeId));
      });

      layer.forEach(function(item) {
        var nodeId = item.nodeId;
        var start = originalPositions[nodeId];
        var target = item.parentPosition;
        var extents = contractionNodeExtents(nodeId);
        var collisionFreeStart = clearInitialContractionCollision(
          start,
          target,
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
              target,
              extents,
              obstacle
            );
            if (entry !== null) { stop = Math.min(stop, entry); }
          });
          stop = Math.max(0, stop - 0.0001);
        }
        var finalPosition = movedOutward ? collisionFreeStart : {
          x: start.x + (target.x - start.x) * stop,
          y: start.y + (target.y - start.y) * stop
        };
        network.moveNode(nodeId, finalPosition.x, finalPosition.y);
        finalPositions[nodeId] = finalPosition;
        parentByNode[nodeId] = item.parentId;
        placed.push({id: nodeId, position: finalPosition, extents: extents});
      });
    }

    contextContractionState = {
      key: candidate.key,
      anchorId: candidate.anchorId,
      originalPositions: originalPositions,
      restorePositions: restorePositions,
      finalPositions: finalPositions,
      depthByNode: plan.depthByNode,
      parentByNode: parentByNode
    };
    updateGraphViewControls();
    updateNodeLabelPositions();
    showTemporaryNotice();
    return true;
  }

  function fitViewerTarget(target) {
    var lastGraphRender = options.renderedGraph();
    // An explicit fit supersedes any pending pane-resize restoration.
    graphCamera.cancelPendingRestore();
    var selection = viewerSelectionSnapshot();
    var ids = [];
    if (target === "reveal") {
      revealViewerSelection({animation: cameraAnimationEnabled()});
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

  return {
    updateFitApplyButton: updateFitApplyButton,
    clearContextFitPriming: clearContextFitPriming,
    resetContextFitInteraction: resetContextFitInteraction,
    fitViewerTarget: fitViewerTarget,
    isActive: isActive,
    showTemporaryNotice: showTemporaryNotice,
    canMove: canMove,
    recordDrag: recordDrag,
    capture: capture,
    restoreCheckpoint: restoreCheckpoint,
    snapshot: snapshot
  };
}
