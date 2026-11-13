/* Graph-generated reading views. Canonical content/personal data stay in the
 * shared block renderer; this controller owns only transient occurrences. */
function kgCreateReadingTrees(options) {
  "use strict";
  var escape = options.markup.escapeHtml;
  var recipes = {
    derivation: {title: "Full derivation tree", preset: "derivation",
      statement: "Trace the derivation of {concept} through its supporting concepts, recursively.",
      kinds: ["definition", "derivation"], relations: ["DERIVES_FROM", "CONSTRUCTED_FROM"]},
    teaching: {title: "Detailed teaching tree", preset: "foundations",
      statement: "Explore {concept} through definitions, explanations, intuition and examples, following its foundational dependencies.",
      kinds: ["definition", "explanation", "intuition", "example"],
      relations: ["DERIVES_FROM", "CONSTRUCTED_FROM", "REQUIRES"]}
  };
  var root = null, entries = new Map(), entryIds = new Map(), quietToggles = new WeakMap(), serial = 0, trees = {};
  var synchronised = null, position = null, activeRecipe = null;
  var focusStack = [], resumeFocus = [];
  var blockOwners = {};
  Object.keys(options.concepts).forEach(function(id) {
    options.blocks(options.concepts[id]).forEach(function(block) { blockOwners[block.block_id] = id; });
  });
  function tag(name, attrs, body) {
    return "<" + name + Object.keys(attrs || {}).map(function(key) {
      var value = attrs[key];
      return value === undefined || value === null || value === false ? "" :
        " " + key + (value === true ? "" : '="' + escape(value) + '"');
    }).join("") + ">" + (body || "") + "</" + name + ">";
  }
  function label(id) { return options.label(id); }
  function entry(key, spec) {
    var encoded = JSON.stringify(key);
    if (!entries.has(encoded)) {
      var found = Object.assign({id: "kg-reading-" + (++serial), open: false}, spec);
      entries.set(encoded, found); entryIds.set(found.id, found);
    }
    return entries.get(encoded);
  }
  function treeRule(tree) { return {preset: recipes[tree.recipe].preset, depth: tree.depth}; }
  function plan(tree) {
    if (!tree.plan) { tree.plan = options.context(root, treeRule(tree)); }
    return tree.plan;
  }
  function matchingBlocks(id, tree) {
    var blocks = options.blocks(options.concepts[id]);
    return recipes[tree.recipe].kinds.reduce(function(result, kind) {
      return result.concat(blocks.filter(function(block) { return block.kind === kind; }));
    }, []);
  }
  function visit(tree, id) {
    if (synchronised && synchronised !== tree.recipe) { detach(); }
    activeRecipe = tree.recipe; position = id;
    updateControls();
    options.onPosition();
  }
  function updateControls() {
    document.querySelectorAll(".kg-reading-sync").forEach(function(input) {
      input.checked = input.getAttribute("data-reading-recipe") === synchronised;
    });
    document.querySelectorAll(".kg-reading-position").forEach(function(status) {
      status.textContent = status.getAttribute("data-reading-recipe") === activeRecipe && position
        ? "Reading: " + label(position) : "";
    });
  }
  function detach() {
    synchronised = null; updateControls(); options.onPosition();
  }
  function synchronise(tree) {
    synchronised = tree.recipe; activeRecipe = tree.recipe; position = position || root;
    options.onSynchronise(root, treeRule(tree));
    updateControls(); options.onPosition();
  }
  function beginPage(id, panel) {
    resumeFocus = focusStack.map(function(item) { return item.targetId; });
    leaveFocus(true);
    if (root !== id) {
      detach(); root = id; entries.clear(); entryIds.clear(); serial = 0; trees = {};
      position = null; activeRecipe = null; resumeFocus = [];
      return;
    }
    panel.querySelectorAll("details[data-reading-entry]").forEach(function(element) {
      var found = entryIds.get(element.id);
      if (found) { found.open = element.open; }
    });
  }
  function focusButton(targetId, context) {
    if (!context.readingTree || Number(context.readingDepth || 0) < 2) { return ""; }
    return tag("button", {type: "button", "class": "kg-reading-focus-button",
      "data-reading-focus": targetId}, "Read at full width");
  }
  function ownedBlock(id, block, tree, path, depth) {
    var found = entry([root, tree.recipe, path, "block", block.block_id], {kind: "block"});
    var context = options.shared.rootContext(block.block_id, found.id);
    context.rootId = "reading-tree:" + root + ":" + tree.recipe;
    context.steps = path.map(function(edgeId) { return ["edge", edgeId]; }).concat([["block", block.block_id]]);
    context.readingTree = true; context.readingDepth = depth;
    return options.renderBlock(id, block, {id: found.id, context: context, reading: true});
  }
  function justification(edge) {
    var source = String(edge.from);
    var verb = {DERIVES_FROM: "derives from", CONSTRUCTED_FROM: "is constructed from", REQUIRES: "requires"}[options.relation(edge)];
    return tag("div", {"class": "justification"},
      tag("div", {"class": "kg-reading-edge-intro"},
        escape(options.concepts[source].display_id || source) +
        tag("span", {"class": "kg-reading-wide-name"}, " " + options.markup.renderConceptText(options.concepts[source].label || "")) +
        " " + verb + " this concept because:") +
      (edge.note ? options.markup.renderConceptText(edge.note) :
        tag("span", {"class": "kg-reading-gap"}, "No justification has been authored yet.")));
  }
  function branch(edge, tree, path, ancestors, depth) {
    var id = String(edge.to), cyclic = ancestors.indexOf(id) >= 0;
    var found = entry([root, tree.recipe, path.concat([String(edge.id)]), "concept"],
      {kind: "concept", tree: tree, node: id, path: path.concat([String(edge.id)]),
        ancestors: ancestors.concat([id]), depth: depth});
    var title = cyclic ? escape(label(id)) : tag("button", {type: "button",
      "class": "kg-reading-concept-toggle", "data-reading-toggle": found.id,
      "aria-expanded": found.open ? "true" : "false", "aria-controls": found.id + "-body"},
      tag("span", {"class": "kg-reading-chevron", "aria-hidden": "true"}, found.open ? "▾" : "▸") +
      tag("span", {}, escape(label(id))) + tag("small", {}, "Concept"));
    var body = cyclic ? tag("p", {"class": "kg-reading-boundary"}, "Already on this reading path; cycle stops here.") :
      tag("details", {"class": "kg-reading-concept", id: found.id,
        "data-reading-entry": "concept", "data-reading-node": id, open: found.open},
        tag("summary", {hidden: true}, escape(label(id))) +
        tag("div", {"class": "kg-reading-concept-body", id: found.id + "-body",
          "data-reading-node": id, style: "--reading-indent:" + (depth < 3 ? "0.6em" : "0.15em")},
          focusButton(found.id, {readingTree: true, readingDepth: depth}) +
          tag("div", {"class": "kg-reading-source"})));
    return tag("section", {"class": "kg-reading-concept-container", "data-reading-concept": id,
      "data-reading-edge": String(edge.id)},
      tag("h3", {"class": "kg-reading-concept-title"}, title) + justification(edge) + body);
  }
  function content(id, tree, path, ancestors, depth) {
    var blocks = matchingBlocks(id, tree);
    var html = blocks.map(function(block) { return ownedBlock(id, block, tree, path, depth); }).join("");
    if (!blocks.length) { html += tag("p", {"class": "kg-reading-gap"}, "No matching blocks are available; dependencies remain below."); }
    var eligible = options.edges.filter(function(edge) {
      return String(edge.from) === id && recipes[tree.recipe].relations.indexOf(options.relation(edge)) >= 0;
    });
    var allowedIds = plan(tree).edgeIds;
    var allowed = eligible.filter(function(edge) { return allowedIds.indexOf(String(edge.id)) >= 0; });
    html += allowed.map(function(edge) { return branch(edge, tree, path, ancestors, depth + 1); }).join("");
    if (eligible.length > allowed.length) {
      html += tag("p", {"class": "kg-reading-boundary"}, "Further support is beyond this tree’s depth. " +
        tag("button", {type: "button", "data-reading-extend": tree.recipe}, "Extend to full tree"));
    }
    return html;
  }
  function controls(tree) {
    var depths = [["one-hop", "1 hop"], ["two-hops", "2 hops"], ["three-hops", "3 hops"], ["transitive", "Full tree"]];
    return tag("div", {"class": "kg-reading-controls"},
      tag("label", {}, "Depth " + tag("select", {"data-reading-depth": tree.recipe,
        "aria-label": recipes[tree.recipe].title + " depth"},
        depths.map(function(item) { return tag("option", {value: item[0], selected: tree.depth === item[0]}, item[1]); }).join(""))) +
      tag("label", {}, tag("input", {type: "checkbox", "class": "kg-reading-sync",
        "data-reading-recipe": tree.recipe, checked: synchronised === tree.recipe}) + " Synchronise graph") +
      tag("button", {type: "button", "data-reading-fold": tree.recipe}, "Fold supports") +
      tag("span", {"class": "kg-reading-position", "data-reading-recipe": tree.recipe, "aria-live": "polite"}));
  }
  function render(id) {
    if (!root || root !== id) { return ""; }
    var cards = Object.keys(recipes).map(function(recipe) {
      var tree = trees[recipe] || (trees[recipe] = {recipe: recipe, depth: "transitive", plan: null});
      var found = entry([root, recipe, "tree"], {kind: "tree", tree: tree});
      tree.entry = found;
      return tag("details", {id: found.id, "class": "kg-reading-tree kg-reading-" + recipe,
        "data-reading-entry": "tree", "data-reading-recipe": recipe, open: found.open},
        tag("summary", {}, tag("span", {"class": "kg-content-statement"},
          escape(recipes[recipe].statement.replace("{concept}", options.concepts[id].label || id))) +
          tag("span", {"class": "content-block-title-line"}, escape(recipes[recipe].title) +
            tag("small", {"class": "kg-reading-badge"}, "Reading tree"))) +
        tag("div", {"class": "kg-reading-tree-body"}, controls(tree) +
          tag("div", {"class": "kg-reading-root"})));
    }).join("");
    return tag("section", {"class": "kg-reading-trees"},
      tag("h3", {}, "Explore through connected concepts") + cards);
  }
  function hydrate(element) {
    if (!element.open || element.hasAttribute("data-reading-loaded")) { return; }
    var found = entryIds.get(element.id);
    if (!found) { return; }
    if (found.kind === "tree") {
      element.querySelector(":scope > .kg-reading-tree-body > .kg-reading-root").innerHTML =
        content(root, found.tree, [], [root], 0);
    } else if (found.kind === "concept") {
      element.querySelector(":scope > .kg-reading-concept-body > .kg-reading-source").innerHTML =
        content(found.node, found.tree, found.path, found.ancestors, found.depth);
    }
    element.setAttribute("data-reading-loaded", "true");
  }
  function afterRender(panel) {
    var changed;
    do {
      changed = false;
      panel.querySelectorAll("details[data-reading-entry][open]").forEach(function(element) {
        if (!element.hasAttribute("data-reading-loaded")) { hydrate(element); changed = true; }
      });
    } while (changed);
    updateControls();
  }
  function restored(panel) {
    panel.querySelectorAll(".kg-reading-trees details, #kg-reading-focus details").forEach(function(element) {
      quietToggles.set(element, element.open);
    });
  }
  function treeFor(element) {
    var host = element.closest("[data-reading-recipe]");
    return host ? trees[host.getAttribute("data-reading-recipe")] : null;
  }
  function toggled(element) {
    if (!element.isConnected) { return; }
    var tree = treeFor(element);
    if (!tree) { return; }
    var quiet = quietToggles.has(element) && quietToggles.get(element) === element.open;
    quietToggles.delete(element);
    var found = entryIds.get(element.id);
    if (found) {
      found.open = element.open;
      if (found.kind === "concept") {
        var toggle = element.parentElement.querySelector(":scope > .kg-reading-concept-title > button");
        if (toggle) {
          toggle.setAttribute("aria-expanded", String(element.open));
          toggle.querySelector(".kg-reading-chevron").textContent = element.open ? "▾" : "▸";
        }
      }
    }
    if (quiet) { return; }
    if (element.classList.contains("kg-reading-tree") && !element.open) {
      if (synchronised === tree.recipe) { detach(); }
      return;
    }
    hydrate(element); afterRender(element); restored(element);
    var owner = blockOwners[element.getAttribute("data-content-block-id") || element.getAttribute("data-content-source-id")];
    var enclosing = element.open && element.hasAttribute("data-reading-node") ? element :
      element.parentElement.closest(".kg-reading-concept[open], .kg-reading-concept-body");
    visit(tree, owner || (enclosing && enclosing.getAttribute("data-reading-node")) || root);
    options.typeset(element);
  }
  function setDepth(tree, depth) {
    leaveFocus(true);
    options.shared.beginPage("concept", root, document.getElementById("info_panel"));
    tree.depth = depth; tree.plan = null;
    var element = document.getElementById(tree.entry.id);
    options.clearMath(element.querySelector(".kg-reading-root"));
    element.removeAttribute("data-reading-loaded");
    hydrate(element); afterRender(element);
    visit(tree, root);
    if (synchronised === tree.recipe) { synchronise(tree); }
    options.shared.afterRender(element); restored(element); options.typeset(element);
  }
  function focus(targetId, silent) {
    var target = document.getElementById(targetId);
    if (!target) { return; }
    var tree = treeFor(target), panel = document.getElementById("info_panel");
    if (!tree) { return; }
    // Keep a local clarification's canonical note scope and heading/actions
    // together when focusing it; a concept body already contains its blocks.
    var body = target.classList.contains("kg-local-explanation") ? target :
      target.querySelector(":scope > .kg-reading-concept-body, :scope > .kg-content-body");
    if (!body) { return; }
    var marker = document.createComment("reading return");
    body.replaceWith(marker);
    focusStack.push({body: body, marker: marker, targetId: targetId, tree: tree});
    var host = document.getElementById("kg-reading-focus");
    if (!host) {
      host = document.createElement("section"); host.id = "kg-reading-focus";
      host.innerHTML = '<button type="button" class="kg-reading-return">← Return to enclosing reading</button><div class="kg-reading-focus-host"></div>';
      panel.appendChild(host);
    }
    host.setAttribute("data-reading-recipe", tree.recipe);
    host.querySelector(".kg-reading-focus-host").replaceChildren(body);
    panel.classList.add("kg-reading-focus-active");
    if (!silent) { host.querySelector("button").focus(); }
    visit(tree, body.getAttribute("data-reading-node") || blockOwners[target.getAttribute("data-content-source-id")] || root);
    options.typeset(body);
  }
  function returnFocus(silent) {
    var found = focusStack.pop();
    if (!found) { return; }
    found.marker.replaceWith(found.body);
    var host = document.getElementById("kg-reading-focus");
    if (focusStack.length) {
      var previous = focusStack[focusStack.length - 1];
      host.setAttribute("data-reading-recipe", previous.tree.recipe);
      host.querySelector(".kg-reading-focus-host").replaceChildren(previous.body);
    } else {
      if (host) { host.remove(); }
      document.getElementById("info_panel").classList.remove("kg-reading-focus-active");
    }
    if (!silent) {
      var control = document.querySelector('[data-reading-focus="' + options.markup.cssAttributeValueEscape(found.targetId) + '"]');
      if (control) { control.focus(); }
    }
  }
  function leaveFocus(silent) { while (focusStack.length) { returnFocus(silent); } }
  function prepareFold(target) {
    var index = focusStack.findIndex(function(item) {
      return item.targetId === target.id || target.contains(item.marker);
    });
    if (index >= 0) {
      while (focusStack.length > index) { returnFocus(true); }
    }
  }
  function restoreFocus() {
    var saved = resumeFocus.slice(); resumeFocus = [];
    var savedPosition = position, savedRecipe = activeRecipe;
    saved.forEach(function(id) { focus(id, true); });
    position = savedPosition; activeRecipe = savedRecipe; updateControls();
  }
  function click(event) {
    var toggle = event.target.closest("[data-reading-toggle]");
    if (toggle) {
      var element = document.getElementById(toggle.getAttribute("data-reading-toggle"));
      element.open = !element.open;
      toggle.setAttribute("aria-expanded", String(element.open));
      return true;
    }
    var button = event.target.closest("[data-reading-focus]");
    if (button) { focus(button.getAttribute("data-reading-focus")); return true; }
    if (event.target.closest(".kg-reading-return")) { returnFocus(); return true; }
    button = event.target.closest("[data-reading-extend]");
    if (button) {
      var tree = trees[button.getAttribute("data-reading-extend")];
      setDepth(tree, "transitive");
      document.getElementById(tree.entry.id).querySelector("select").value = "transitive";
      return true;
    }
    button = event.target.closest("[data-reading-fold]");
    if (button) {
      leaveFocus(true);
      var card = document.getElementById(trees[button.getAttribute("data-reading-fold")].entry.id);
      card.querySelectorAll("details").forEach(function(item) { item.open = false; });
      return true;
    }
    return false;
  }
  function change(event) {
    var target = event.target;
    if (target.hasAttribute("data-reading-depth")) {
      setDepth(trees[target.getAttribute("data-reading-depth")], target.value); return true;
    }
    if (target.classList.contains("kg-reading-sync")) {
      var tree = trees[target.getAttribute("data-reading-recipe")];
      if (target.checked) { visit(tree, root); synchronise(tree); } else { detach(); }
      return true;
    }
    return false;
  }
  return {beginPage: beginPage, render: render, afterRender: afterRender, restored: restored, toggled: toggled,
    restoreFocus: restoreFocus, prepareFold: prepareFold, focusButton: focusButton, click: click, change: change, detach: detach,
    reset: function() {
      leaveFocus(true); detach(); root = null; position = null; activeRecipe = null;
      entries.clear(); entryIds.clear(); trees = {}; resumeFocus = [];
    },
    snapshot: function() { return {root: root, synchronised: synchronised, position: position,
      activeRecipe: activeRecipe, focusDepth: focusStack.length}; }};
}
