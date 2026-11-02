/* Graph framing and deferred camera restoration; layout positions are not changed here. */
function kgCreateGraphCamera(options) {
  "use strict";
  var network = options.network, nodes = options.nodes, graphContainer = options.container;
  var updateNodeLabelPositions = options.onChange;
  var activeNodeRadiusScale = options.labels.activeRadiusScale;
  var nodeLabelWidth = options.labels.width, nodeLabelFontSize = options.labels.fontSize;
  var cameraRestoreGeneration = 0;
  function cancelPendingRestore() { cameraRestoreGeneration += 1; }

  function cameraSnapshot() {
    return {
      position: network.getViewPosition(),
      scale: network.getScale()
    };
  }

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

  function cameraAnimationEnabled() {
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      return false;
    }
    var memory = Number(navigator.deviceMemory);
    if (Number.isFinite(memory) && memory > 0 && memory <= 4) {
      return false;
    }
    var processors = Number(navigator.hardwareConcurrency);
    if (Number.isFinite(processors) && processors > 0 && processors <= 4) {
      return false;
    }
    return true;
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

  function visiblePanelRects() {
    return ["kg_controls", "info_panel", "kg_tutorial_narration"].map(function(id) {
      var el = document.getElementById(id);
      if (!el || el.hidden || el.classList.contains("kg-hidden")) { return null; }
      return {
        id: id,
        rect: el.getBoundingClientRect()
      };
    }).filter(Boolean);
  }

  function panelOcclusionEdge(panel, baseRect, overlap) {
    if (panel.id === "kg_tutorial_narration") {
      return (overlap.top + overlap.bottom) / 2 >= (baseRect.top + baseRect.bottom) / 2
        ? "bottom" : "top";
    }
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
    var panels = visiblePanelRects();
    panels.forEach(function(panel) {
      if (panel.id !== "kg_tutorial_narration") { return; }
      var overlap = intersectRects(baseAbs, panel.rect);
      if (overlap) {
        minHeight = Math.min(minHeight, Math.max(24, baseAbs.height - overlap.height - margin * 3));
      }
    });
    panels.forEach(function(panel) {
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
      var radius = id === options.selectedConceptId() ? baseRadius * activeNodeRadiusScale : baseRadius;
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
    var animate = options.animation === undefined
      ? cameraAnimationEnabled()
      : options.animation !== false;

    network.moveTo({
      position: targetPosition,
      scale: scale,
      animation: animate ? {
        duration: options.duration || 250,
        easingFunction: "easeInOutQuad"
      } : false
    });
    setTimeout(updateNodeLabelPositions, animate ? 260 : 0);
  }

  return {
    cameraSnapshot: cameraSnapshot,
    preserveCameraAfterLayout: preserveCameraAfterLayout,
    currentGraphView: currentGraphView,
    preserveGraphView: preserveGraphView,
    visualViewportRect: visualViewportRect,
    intersectRects: intersectRects,
    fitNodesToAvailableRect: fitNodesToAvailableRect,
    revealNodeIds: revealNodeIds,
    cameraAnimationEnabled: cameraAnimationEnabled,
    cancelPendingRestore: cancelPendingRestore
  };
}
