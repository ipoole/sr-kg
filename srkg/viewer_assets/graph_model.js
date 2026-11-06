/* Pure graph computations: no DOM, storage, vis-network or viewer state. */
var kgGraphModel = (function() {
  "use strict";

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
    THREE_HOPS: "three-hops",
    TRANSITIVE: "transitive"
  });

  function normaliseContextDepth(depth) {
    if (depth === ContextDepth.TWO_HOPS || depth === ContextDepth.THREE_HOPS || depth === ContextDepth.TRANSITIVE) {
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
    if (depth === ContextDepth.THREE_HOPS) { return 3; }
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


  function contractionGraphPlan(candidate) {
    var depthByNode = {};
    var parentCandidates = {};
    var queue = [candidate.anchorId];
    depthByNode[candidate.anchorId] = 0;

    while (queue.length > 0) {
      var current = queue.shift();
      var nextDepth = depthByNode[current] + 1;
      (candidate.adjacency[current] || []).forEach(function(neighbour) {
        if (depthByNode[neighbour] === undefined) {
          depthByNode[neighbour] = nextDepth;
          parentCandidates[neighbour] = [current];
          queue.push(neighbour);
        } else if (
          depthByNode[neighbour] === nextDepth &&
          parentCandidates[neighbour].indexOf(current) === -1
        ) {
          parentCandidates[neighbour].push(current);
        }
      });
    }
    Object.keys(parentCandidates).forEach(function(nodeId) {
      parentCandidates[nodeId].sort();
    });
    return {
      depthByNode: depthByNode,
      parentCandidates: parentCandidates,
      maximumDepth: Object.keys(depthByNode).reduce(function(maximum, nodeId) {
        return Math.max(maximum, depthByNode[nodeId]);
      }, 0)
    };
  }


  // Group the visible boundaries of a graph projection. Inputs remain unchanged.
  function groupBoundaryEdges(graphEdges, renderedEdges, representedByConcept, moduleEndpointMembers, prefix) {
    var groups = {};
    graphEdges.forEach(function(edge) {
      var current = renderedEdges[edge.id];
      if (!current || current.hidden) { return; }
      if (!moduleEndpointMembers[String(edge.from)] && !moduleEndpointMembers[String(edge.to)]) { return; }
      var from = representedByConcept[String(edge.from)];
      var to = representedByConcept[String(edge.to)];
      if (!from || !to || from === to) { return; }
      var id = prefix + from + "::" + to;
      if (!groups[id]) {
        groups[id] = {id: id, from: from, to: to, relationCounts: {}, edgeIds: [],
          contextEdge: false, overviewEdge: false};
      }
      var relation = String(edge.relation || "");
      groups[id].relationCounts[relation] = (groups[id].relationCounts[relation] || 0) + 1;
      groups[id].edgeIds.push(edge.id);
      groups[id].contextEdge = groups[id].contextEdge || current.kgContextEdge === true;
      groups[id].overviewEdge = groups[id].overviewEdge || current.kgOverviewEdge === true;
    });
    return Object.keys(groups).sort().map(function(id) {
      groups[id].edgeIds.sort();
      return groups[id];
    });
  }

  return {
    ContextPreset: ContextPreset, ContextDepth: ContextDepth,
    createContextRule: createContextRule,
    contextPresetTraversals: contextPresetTraversals,
    computeContextSubgraph: computeContextSubgraph,
    contractionGraphPlan: contractionGraphPlan,
    groupBoundaryEdges: groupBoundaryEdges
  };
})();
