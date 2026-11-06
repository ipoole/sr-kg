/* Canvas presentation; owns SVG images and fitted module-label caches. */
function kgCreateGraphPresentation(options) {
  "use strict";
  var network = options.network, nodes = options.nodes, visAdapter = options.adapter;
  var getConcept = options.concept, getModule = options.module;
  var graphCompletionMarkersSnapshot = options.completionMarkers;
  var expandedModuleOutlineSnapshot = options.expandedOutlines;
  var foldedModuleIdList = options.foldedModuleIds;
  var moduleGraphNodeId = options.moduleNodeId;
  var foldedModuleConceptProxy = options.selectedConceptProxy;
  var escapeHtml = options.escapeHtml;
  var activeNodeRadiusScale = options.activeRadiusScale, activeNodeBorderWidth = options.activeBorderWidth;
  var detailedConceptRenderMinRadiusPx = options.detailThreshold;
  var svgImageCache = {}, fittedModuleLabelCache = {};
  var expandedLabelCache = {}, expandedLabelContext = null;

  function expandedModuleLabelSnapshot() {
    return expandedModuleOutlineSnapshot().map(function(outline) {
      var module = getModule(outline.moduleId) || {};
      var title = module.title || outline.moduleId;
      var selected = options.selectedModuleId() === outline.moduleId;
      var fontSize = 48, lineHeight = 58, gap = 24;
      var maxWidth = Math.min(1000, Math.max(400, outline.width));
      var font = (selected ? "bold " : "") + fontSize + "px Arial";
      var key = JSON.stringify([title, maxWidth, font]);
      var measured = expandedLabelCache[key];
      if (!measured) {
        if (!expandedLabelContext) {
          expandedLabelContext = document.createElement("canvas").getContext("2d");
        }
        expandedLabelContext.font = font;
        var lines = [], line = "";
        String(title).split(/\s+/).forEach(function(word) {
          var next = line ? line + " " + word : word;
          if (line && expandedLabelContext.measureText(next).width > maxWidth) {
            lines.push(line); line = word;
          } else { line = next; }
        });
        if (line) { lines.push(line); }
        measured = {lines: lines, width: Math.max.apply(null, lines.map(function(text) {
          return expandedLabelContext.measureText(text).width;
        }).concat([1]))};
        expandedLabelCache[key] = measured;
      }
      var x = outline.left + outline.width / 2;
      var top = outline.bottom + gap;
      return {moduleId: outline.moduleId, lines: measured.lines.slice(), selected: selected,
        fontSize: fontSize, font: font, lineHeight: lineHeight, x: x,
        top: top, bottom: top + measured.lines.length * lineHeight,
        left: x - measured.width / 2, right: x + measured.width / 2,
        width: measured.width, height: measured.lines.length * lineHeight};
    });
  }

  function drawExpandedModuleLabels(ctx) {
    expandedModuleLabelSnapshot().forEach(function(label) {
      ctx.save();
      ctx.font = label.font;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = label.selected ? "#1f2937" : "#5b6471";
      ctx.strokeStyle = "rgba(255,255,255,0.9)";
      ctx.lineWidth = 3;
      label.lines.forEach(function(line, index) {
        var y = label.top + index * label.lineHeight;
        ctx.strokeText(line, label.x, y);
        ctx.fillText(line, label.x, y);
      });
      ctx.restore();
    });
  }

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
      var svgIcon = options.renderGraphic === false
        ? ""
        : (concept.svg_icon || concept.svg_graphic || "");
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
    var scale = network.getScale();
    var activeNodeId = options.selectedConceptId();
    var transientConceptHighlight = options.transientHighlight();
    nodes.get().forEach(function(node) {
      if (node.hidden) { return; }
      if (node.isModuleNode) { return; }

      var pos = positions[node.id];
      if (!pos) { return; }

      drawConceptFace(ctx, node, pos, {
        active: node.id === activeNodeId,
        renderGraphic: (
          (Number(node.visualSize) || Number(node.size) || 18) *
          (node.id === activeNodeId ? activeNodeRadiusScale : 1) * scale
        ) >= detailedConceptRenderMinRadiusPx,
        transient: Boolean(
          transientConceptHighlight &&
          transientConceptHighlight.nodeId === String(node.id)
        )
      });
    });
  }

  function drawGraphCompletionTick(ctx, x, y, radius, colour, opacity) {
    ctx.save();
    ctx.globalAlpha = (Number.isFinite(opacity) ? opacity : 1) * 0.94;
    ctx.fillStyle = colour;
    ctx.strokeStyle = "rgba(255,255,255,0.78)";
    ctx.lineWidth = Math.max(0.8, radius * 0.09);
    ctx.font = "bold " + String(radius * 2.5) + "px Arial, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.strokeText("✓", x, y + radius * 0.08);
    ctx.fillText("✓", x, y + radius * 0.08);
    ctx.restore();
  }

  function drawGraphCompletionMarkers(ctx) {
    var scale = network.getScale();
    graphCompletionMarkersSnapshot().markers.forEach(function(marker) {
      marker.symbols.forEach(function(symbol) {
        if (symbol.radius * scale < 2.5) { return; }
        drawGraphCompletionTick(
          ctx,
          symbol.x,
          symbol.y,
          symbol.radius,
          symbol.colour,
          marker.opacity
        );
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

  function fittedModuleLabel(title, memberCount, width, height, options) {
    options = options || {};
    var cacheKey = JSON.stringify([
      String(title), Number(memberCount), Number(width), Number(height),
      Number(options.countFontSize || 80),
      Number(options.lineWidthFraction || 0.88),
      Number(options.titleFontCap || 160),
      Number(options.availableHeight || 0),
      Number(options.lineHeightFactor || 1.25),
      Number(options.verticalShift || 0)
    ]);
    if (fittedModuleLabelCache[cacheKey]) {
      return Object.assign({}, fittedModuleLabelCache[cacheKey]);
    }
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
    var result = {
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
    fittedModuleLabelCache[cacheKey] = result;
    return Object.assign({}, result);
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

  function moduleCornerRadius(width, height) {
    return Math.min(width, height) * 0.18;
  }

  function drawExpandedModuleOutlines(ctx) {
    var scale = network && network.getScale ? Number(network.getScale()) : 1;
    if (!Number.isFinite(scale) || scale <= 0) { scale = 1; }
    expandedModuleOutlineSnapshot().forEach(function(outline) {
      ctx.save();
      ctx.globalAlpha = outline.opacity;
      ctx.strokeStyle = outline.colour;
      ctx.lineWidth = outline.lineWidth / scale;
      roundedRectPath(
        ctx,
        outline.left,
        outline.top,
        outline.width,
        outline.height,
        outline.radius
      );
      ctx.stroke();
      ctx.restore();
    });
  }

  function drawExpandedModuleBackgrounds(ctx) {
    expandedModuleOutlineSnapshot().forEach(function(outline) {
      ctx.save();
      ctx.fillStyle = "rgba(248, 250, 252, 0.90)";
      roundedRectPath(ctx, outline.left, outline.top, outline.width, outline.height, outline.radius);
      ctx.fill();
      ctx.restore();
    });
  }

  function clipModuleEdgeEndpoints(ctx, edge) {
    var canvas = ctx.canvas;
    var topLeft = network.DOMtoCanvas({x: 0, y: 0});
    var bottomRight = network.DOMtoCanvas({
      x: canvas.clientWidth || canvas.width, y: canvas.clientHeight || canvas.height
    });
    [edge.fromId, edge.toId].forEach(function(id) {
      var bounds = options.moduleBoundary(id);
      if (bounds) {
        ctx.beginPath();
        ctx.rect(topLeft.x, topLeft.y, bottomRight.x - topLeft.x, bottomRight.y - topLeft.y);
        roundedRectPath(ctx, bounds.left, bounds.top, bounds.width, bounds.height, bounds.radius, true);
        ctx.clip("evenodd");
      }
    });
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

  function moduleGraphicImage(moduleId) {
    var module = getModule(moduleId) || {};
    return module.svg_icon
      ? getSvgNodeImage(moduleGraphNodeId(moduleId) + "::graphic", module.svg_icon)
      : null;
  }

  function roundedRectPath(ctx, x, y, width, height, radius, append) {
    radius = Math.min(radius, width / 2, height / 2);
    if (!append) { ctx.beginPath(); }
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
      var shape = visAdapter.nodeGeometry(nodeId);
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
      if (!node || node.hidden || !node.hasModuleGraphic || !shape ||
          !image || !image.complete || image.naturalWidth <= 0) { return; }
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

  return {
    expandedModuleLabelSnapshot: expandedModuleLabelSnapshot,
    drawExpandedModuleLabels: drawExpandedModuleLabels,
    drawVisibleNodes: drawVisibleNodes,
    drawGraphCompletionMarkers: drawGraphCompletionMarkers,
    fittedModuleLabel: fittedModuleLabel,
    moduleGraphicLayout: moduleGraphicLayout,
    moduleCornerRadius: moduleCornerRadius,
    drawExpandedModuleOutlines: drawExpandedModuleOutlines,
    drawExpandedModuleBackgrounds: drawExpandedModuleBackgrounds,
    clipModuleEdgeEndpoints: clipModuleEdgeEndpoints,
    moduleGraphicCornerRadius: moduleGraphicCornerRadius,
    moduleGraphicImage: moduleGraphicImage,
    drawFoldedModuleGraphics: drawFoldedModuleGraphics
  };
}
