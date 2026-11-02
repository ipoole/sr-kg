/* Semantic graph/details/control targets and hover demonstrations; resolves current geometry. */
function kgCreateTutorialTargets(options) {
  "use strict";
  var network = options.network, nodes = options.nodes, edges = options.edges, visAdapter = options.adapter;
  var graphContainer = options.container, activeNodeRadiusScale = options.activeRadiusScale;
  var cssAttributeValueEscape = options.markup.cssAttributeValueEscape;
  var tutorialDetailsRelationshipForTarget = options.relationshipTarget;
  var edgeHoverableInCurrentView = options.graph.edgeHoverableInCurrentView;
  var edgeRelation = options.graph.edgeRelation;
  var expandedModuleGeometrySnapshot = options.graph.expandedModuleGeometrySnapshot;
  var foldedModuleConceptProxyForConcept = options.graph.foldedModuleConceptProxyForConcept;
  var graphObjectDisplayText = options.graph.graphObjectDisplayText;
  var graphPositionForNode = options.graph.graphPositionForNode;
  var highlightHoveredEdge = options.graph.highlightHoveredEdge;
  var moduleGraphNodeId = options.graph.moduleGraphNodeId;
  var moduleIdForConcept = options.graph.moduleIdForConcept;
  var relationshipPhrase = options.graph.relationshipPhrase;
  var showEdgeTooltip = options.graph.showEdgeTooltip;
  var showNodeTooltip = options.graph.showNodeTooltip;
  var conceptDisplayId = options.content.conceptDisplayId;
  var getConcept = options.content.getConcept;
  var getModule = options.content.getModule;
  var searchDisplayText = options.content.searchDisplayText;

  function tutorialElementTarget(element, label) {
    if (!element) { return null; }
    var rect = element.getBoundingClientRect();
    if (!rect.width || !rect.height) { return null; }
    return {
      rect: {x: rect.left, y: rect.top, width: rect.width, height: rect.height},
      label: label
    };
  }

  function tutorialGraphBoundsTarget(bounds, label) {
    var canvas = visAdapter.canvasElement();
    if (!bounds || !canvas) { return null; }
    var canvasRect = canvas.getBoundingClientRect();
    var topLeft = network.canvasToDOM({x: bounds.left, y: bounds.top});
    var bottomRight = network.canvasToDOM({x: bounds.right, y: bounds.bottom});
    return {
      rect: {
        x: canvasRect.left + Math.min(topLeft.x, bottomRight.x),
        y: canvasRect.top + Math.min(topLeft.y, bottomRight.y),
        width: Math.max(1, Math.abs(bottomRight.x - topLeft.x)),
        height: Math.max(1, Math.abs(bottomRight.y - topLeft.y))
      },
      label: label
    };
  }

  function tutorialGraphNodeTarget(nodeId, label) {
    nodeId = String(nodeId);
    var node = nodes.get(nodeId);
    var shape = visAdapter.nodeGeometry(nodeId);
    if (!node || node.hidden || !shape) { return null; }
    return tutorialGraphBoundsTarget({
      left: shape.left,
      right: shape.left + shape.width,
      top: shape.top,
      bottom: shape.top + shape.height
    }, label);
  }

  function tutorialEdgeReference(target, prefix) {
    target = String(target || "");
    if (target.indexOf(prefix) !== 0) {
      throw new Error("Tutorial edge target must begin with " + prefix);
    }
    var parts = target.slice(prefix.length).split("|");
    if (parts.length !== 3 || parts.some(function(part) { return !part; })) {
      throw new Error("Tutorial edge target must identify source|RELATION|target");
    }
    return {from: parts[0], relation: parts[1], to: parts[2]};
  }

  function tutorialVisibleEdge(reference) {
    return edges.get().find(function(edge) {
      return String(edge.from) === reference.from &&
        edgeRelation(edge) === reference.relation &&
        String(edge.to) === reference.to &&
        edgeHoverableInCurrentView(edge);
    }) || null;
  }

  function tutorialGraphEdgeTarget(reference) {
    var edge = tutorialVisibleEdge(reference);
    if (!edge) { return null; }
    var point = visAdapter.edgePoint(edge.id, 0.5);
    if (!point) {
      var from = graphPositionForNode(edge.from);
      var to = graphPositionForNode(edge.to);
      if (from && to) {
        point = {x: (from.x + to.x) / 2, y: (from.y + to.y) / 2};
      }
    }
    if (!point) { return null; }
    var label = graphObjectDisplayText(edge.from) + " " +
      relationshipPhrase(edge) + " " + graphObjectDisplayText(edge.to);
    var target = tutorialGraphBoundsTarget({
      left: point.x - 12,
      right: point.x + 12,
      top: point.y - 12,
      bottom: point.y + 12
    }, label);
    if (target) { target.edgeId = edge.id; }
    return target;
  }

  function tutorialConceptTarget(conceptId) {
    conceptId = String(conceptId);
    var concept = getConcept(conceptId);
    if (!concept) { return null; }
    var label = conceptDisplayId(conceptId) + " " + searchDisplayText(concept.label || "");
    var node = nodes.get(conceptId);
    var proxy = foldedModuleConceptProxyForConcept(conceptId);
    if (proxy) {
      return tutorialGraphBoundsTarget({
        left: proxy.x - proxy.radius,
        right: proxy.x + proxy.radius,
        top: proxy.y - proxy.radius,
        bottom: proxy.y + proxy.radius
      }, label);
    }
    var position = graphPositionForNode(conceptId);
    var direct = null;
    if (node && !node.hidden && position) {
      var radius = (Number(node.visualSize) || Number(node.size) || 18) *
        (conceptId === String(options.selectedConceptId() || "") ? activeNodeRadiusScale : 1);
      direct = tutorialGraphBoundsTarget({
        left: position.x - radius,
        right: position.x + radius,
        top: position.y - radius,
        bottom: position.y + radius
      }, label);
    }
    if (direct) { return direct; }
    var moduleId = moduleIdForConcept(conceptId);
    if (!moduleId) { return null; }
    return tutorialGraphNodeTarget(
      moduleGraphNodeId(moduleId),
      ((getModule(moduleId) || {}).title || moduleId) + " module containing " + label
    );
  }

  function tutorialModuleTarget(moduleId) {
    moduleId = String(moduleId);
    var module = getModule(moduleId);
    if (!module) { return null; }
    var label = (module.title || moduleId) + " module";
    var folded = tutorialGraphNodeTarget(moduleGraphNodeId(moduleId), label);
    if (folded) { return folded; }
    var outline = expandedModuleGeometrySnapshot().find(function(item) {
      return String(item.moduleId) === moduleId;
    });
    return outline ? tutorialGraphBoundsTarget(outline, label) : null;
  }

  function tutorialTooltipPointer(resolved) {
    if (!resolved || !graphContainer) { return null; }
    var containerRect = graphContainer.getBoundingClientRect();
    return {
      DOM: {
        x: resolved.rect.x + resolved.rect.width / 2 - containerRect.left,
        y: resolved.rect.y + resolved.rect.height / 2 - containerRect.top
      }
    };
  }

  function showTutorialConceptHover(conceptId) {
    conceptId = String(conceptId);
    var resolved = tutorialConceptTarget(conceptId);
    var pointer = tutorialTooltipPointer(resolved);
    if (!getConcept(conceptId) || !resolved || !pointer) {
      throw new Error("Tutorial concept hover is unavailable: " + conceptId);
    }
    showNodeTooltip(conceptId, pointer);
  }

  function showTutorialEdgeHover(reference) {
    var resolved = tutorialGraphEdgeTarget(reference);
    var pointer = tutorialTooltipPointer(resolved);
    if (!resolved || !pointer || resolved.edgeId === undefined) {
      throw new Error("Tutorial edge hover is unavailable");
    }
    highlightHoveredEdge(resolved.edgeId);
    showEdgeTooltip(resolved.edgeId, pointer);
  }

  function resolveTutorialPointerTarget(target) {
    target = String(target || "narration");
    var controlTargets = {
      context: ["kg_context_preset_select", "Context rule"],
      depth: ["kg_context_depth_select", "Context depth"],
      fit: ["kg_fit_apply", "Fit"],
      "display-scope": ["kg_display_scope_select", "Graph display"],
      "view": ["kg_view_select", "Workspace view"],
      search: ["kg_search_toggle", "Search"],
      "search-input": ["kg_search", "Search query"],
      tools: ["kg_controls_toggle", "Tools"],
      "expand-context": ["kg_expand_context_modules", "Expand context modules"]
    };
    if (target === "narration") {
      return tutorialElementTarget(
        document.getElementById("kg_tutorial_narration"), "Tutorial narration"
      );
    }
    if (target.indexOf("control:module-fold:") === 0) {
      var foldModuleId = target.slice("control:module-fold:".length);
      var foldControl = options.foldControls()[foldModuleId];
      return tutorialElementTarget(
        foldControl,
        foldControl ? foldControl.getAttribute("aria-label") : "Module representation"
      );
    }
    if (target.indexOf("control:") === 0) {
      var control = controlTargets[target.slice("control:".length)];
      return control
        ? tutorialElementTarget(document.getElementById(control[0]), control[1])
        : null;
    }
    if (target.indexOf("graph:concept:") === 0) {
      return tutorialConceptTarget(target.slice("graph:concept:".length));
    }
    if (target.indexOf("graph:module:") === 0) {
      return tutorialModuleTarget(target.slice("graph:module:".length));
    }
    if (target.indexOf("graph:edge:") === 0) {
      return tutorialGraphEdgeTarget(tutorialEdgeReference(target, "graph:edge:"));
    }
    if (target.indexOf("search:concept:") === 0) {
      var searchConceptId = target.slice("search:concept:".length);
      return tutorialElementTarget(
        document.querySelector(
          '#kg_concept_list [data-concept-id="' +
          cssAttributeValueEscape(searchConceptId) + '"]'
        ),
        "Search result " + conceptDisplayId(searchConceptId) + " " +
          searchDisplayText((getConcept(searchConceptId) || {}).label || "")
      );
    }
    if (target.indexOf("search:module:") === 0) {
      var searchModuleId = target.slice("search:module:".length);
      return tutorialElementTarget(
        document.querySelector(
          '#kg_concept_list [data-module-id="' +
          cssAttributeValueEscape(searchModuleId) + '"]'
        ),
        "Search result " + ((getModule(searchModuleId) || {}).title || searchModuleId)
      );
    }
    if (target.indexOf("details:block:") === 0) {
      var blockId = target.slice("details:block:".length);
      var block = document.querySelector(
        '#info_panel [data-content-block-id="' + cssAttributeValueEscape(blockId) + '"]'
      );
      return tutorialElementTarget(block, "Details block " + blockId);
    }
    if (target === "details:heading") {
      return tutorialElementTarget(
        document.querySelector("#info_panel .concept-title"), "Details heading"
      );
    }
    if (target === "details:contents") {
      return tutorialElementTarget(
        document.querySelector("#info_panel .concept-toc"), "Details contents"
      );
    }
    if (target === "details:study-questions") {
      return tutorialElementTarget(
        document.querySelector("#info_panel .study-questions"), "Study Questions"
      );
    }
    if (target === "details:graphic") {
      return tutorialElementTarget(
        document.querySelector("#info_panel .concept-figure"), "Details graphic"
      );
    }
    if (target === "details:derived-from-full-tree" || target === "details:where-used-full-tree") {
      var fullTreeSelector = target === "details:derived-from-full-tree"
        ? ".concept-derived-from-full-tree" : ".concept-backlinks-full-tree";
      return tutorialElementTarget(
        document.querySelector("#info_panel " + fullTreeSelector), "Full tree"
      );
    }
    var relationship = tutorialDetailsRelationshipForTarget(target);
    if (relationship) {
      return tutorialElementTarget(
        document.querySelector("#info_panel " + relationship.showGraphSelector),
        relationship.label + ": Show in graph"
      );
    }
    if (target.indexOf("tools:section:") === 0) {
      var toolsSectionName = target.slice("tools:section:".length);
      var sectionIds = {
        tutorials: "kg_tutorials_section",
        modules: "kg_modules_section",
        layouts: "kg_layouts_section",
        study: "kg_study_section",
        "personal-data": "kg_personal_data_section",
        notes: "kg_notes_section"
      };
      return tutorialElementTarget(
        document.getElementById(sectionIds[toolsSectionName]),
        toolsSectionName + " Tools section"
      );
    }
    return null;
  }

  return {
    tutorialEdgeReference: tutorialEdgeReference,
    showTutorialConceptHover: showTutorialConceptHover,
    showTutorialEdgeHover: showTutorialEdgeHover,
    resolveTutorialPointerTarget: resolveTutorialPointerTarget
  };
}
