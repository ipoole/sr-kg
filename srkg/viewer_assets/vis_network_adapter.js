/* Private vis-network access belongs here; callers use graph-space geometry.
 * Geometry is borrowed for synchronous reads, not mutated or retained by callers.
 * Draw-only width changes deliberately avoid DataSet updates and redraw loops.
 */
function kgCreateVisNetworkAdapter(network) {
  "use strict";
  function nativeNode(id) {
    return network.body && network.body.nodes[String(id)];
  }
  function nativeEdge(id) {
    return network.body && network.body.edges[String(id)];
  }
  var layeredEdges = [];
  function position(value) {
    return value && Number.isFinite(Number(value.x)) && Number.isFinite(Number(value.y))
      ? {x: Number(value.x), y: Number(value.y)} : null;
  }
  return {
    // Keep vis's curves, arrows, hover widths and labels, but paint these edges
    // before module backgrounds rather than in the normal foreground pass.
    setLayeredEdges: function(ids) {
      layeredEdges.forEach(function(item) {
        item.edge.draw = item.draw;
        item.edge.drawArrows = item.drawArrows;
      });
      layeredEdges = [];
      (ids || []).forEach(function(id) {
        var edge = nativeEdge(id);
        if (!edge) { return; }
        layeredEdges.push({edge: edge, draw: edge.draw, drawArrows: edge.drawArrows});
        edge.draw = function() {};
        edge.drawArrows = function() {};
      });
    },
    drawLayeredEdges: function(ctx, clipEndpoints) {
      layeredEdges.forEach(function(item) {
        if (item.edge.connected === false) { return; }
        ctx.save();
        try {
          clipEndpoints(ctx, item.edge);
          item.draw.call(item.edge, ctx);
          item.drawArrows.call(item.edge, ctx);
        } finally { ctx.restore(); }
      });
    },
    canvasElement: function() {
      return network.canvas && network.canvas.frame ? network.canvas.frame.canvas : null;
    },
    // Boundary-only endpoints must not obstruct selection, dragging or hover.
    disableNodeHitTesting: function(id) {
      var node = nativeNode(id);
      if (!node) { return; }
      node.isOverlappingWith = function() { return false; };
      node.getItemsOnPoint = function() { return []; };
    },
    nodeGeometry: function(id) {
      var node = nativeNode(id);
      return node && node.shape || null;
    },
    precisePosition: function(id) {
      var live = position(nativeNode(id));
      if (live) { return live; }
      var positions = network.getPositions ? network.getPositions([String(id)]) : {};
      return position(positions[String(id)]);
    },
    edgePoint: function(id, fraction) {
      var edge = nativeEdge(id);
      try {
        return edge && edge.edgeType && edge.edgeType.getPoint
          ? edge.edgeType.getPoint(fraction) : null;
      } catch (error) { return null; }
    },
    setDrawnEdgeWidth: function(id, width) {
      var edge = nativeEdge(id);
      if (edge) { edge.options.width = width; }
    }
  };
}
