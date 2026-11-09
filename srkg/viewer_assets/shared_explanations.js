/* Canonical authored sources and transient, independently folded reading paths. */
function kgCreateSharedExplanations(options) {
  "use strict";
  var markup = options.markup, escape = markup.escapeHtml;
  var sources = Object.create(null), currentPage = "", entries = new Map();
  var nativeState = new Map(), nextId = 0, graphicSerial = 0;

  function index(owners, type) {
    Object.keys(owners).forEach(function(id) {
      (owners[id].content_blocks || []).forEach(function(block) {
        sources[block.block_id] = {block: block, ownerType: type, ownerId: id, owner: owners[id]};
      });
    });
  }
  index(options.concepts, "concept");
  index(options.modules, "module");

  function beginPage(type, id, panel) {
    var key = type + ":" + id;
    if (key !== currentPage) {
      currentPage = key; entries.clear(); nativeState.clear(); nextId = 0;
      return;
    }
    panel.querySelectorAll("details").forEach(function(element) {
      var occurrence = element.getAttribute("data-content-occurrence");
      if (occurrence && entries.has(occurrence)) { entries.get(occurrence).open = element.open; }
      else if (element.id) { nativeState.set(element.id, element.open); }
    });
  }

  function rootContext(sourceId, anchorId) {
    return {origin: "authored", rootId: sourceId, steps: [],
      ancestors: [{sourceId: sourceId, id: anchorId}]};
  }

  function disclosure(context) {
    var key = markup.occurrenceKey(context);
    if (!key) { return {}; }
    if (!entries.has(key)) { entries.set(key, {id: "kg-explanation-" + (++nextId), open: false}); }
    return entries.get(key);
  }

  function statement(source) {
    return source.block.statement
      ? markup.renderBodyLines(source.block.statement, "kg-content-statement") : "";
  }

  function graphic(source) {
    if (source.block.graphic !== "detail") { return ""; }
    var owner = source.owner;
    var svg = owner.svg_detail || owner.svg_icon || "";
    if (!svg) { return '<p class="kg-shared-unavailable">Illustration unavailable in this edition.</p>'; }
    // A shared illustration may occur several times in one document. Its SVG
    // definitions/labels must remain local to that occurrence.
    var prefix = "kg-source-graphic-" + (++graphicSerial) + "-", ids = new Map();
    svg = svg.replace(/\bid=(["'])([^"']+)\1/g, function(_match, quote, id) {
      ids.set(id, prefix + id); return "id=" + quote + prefix + id + quote;
    }).replace(/url\(#([^)]*)\)/g, function(match, id) {
      return ids.has(id) ? "url(#" + ids.get(id) + ")" : match;
    }).replace(/\b((?:xlink:)?href)=(["'])#([^"']+)\2/g, function(match, attr, quote, id) {
      return ids.has(id) ? attr + "=" + quote + "#" + ids.get(id) + quote : match;
    }).replace(/\b(aria-labelledby|aria-describedby)=(["'])([^"']+)\2/g, function(_match, attr, quote, value) {
      return attr + "=" + quote + value.split(/\s+/).map(function(id) { return ids.get(id) || id; }).join(" ") + quote;
    });
    var moduleClass = source.ownerType === "module" ? " module-graphic" : "";
    var caption = owner.svg_detail_caption || owner.svg_icon_caption || "";
    return '<figure class="kg-shared-figure"><div class="concept-graphic' + moduleClass + '">' + svg + '</div>' +
      (caption ? '<figcaption class="concept-graphic-caption">' + markup.renderCaptionText(caption) + '</figcaption>' : "") + '</figure>';
  }

  function renderReference(reference, context) {
    // Tooltips/preview summaries must not build a reading tree or gain controls.
    if (!context || !context.rootId) { return markup.renderConceptText(reference.target_label); }
    var source = sources[reference.target_id];
    if (!source) {
      return '<div class="kg-shared-unavailable">' + markup.renderConceptText(reference.target_label) +
        ' — ' + markup.renderConceptText(reference.hook) +
        '<small>Explanation unavailable in this edition.</small></div>';
    }
    var html = '<div class="kg-shared-reference">' + statement(source);
    var ancestor = (context.ancestors || []).slice().reverse().find(function(item) {
      return item.sourceId === reference.target_id;
    });
    if (ancestor) {
      return html + '<button type="button" class="kg-content-return" data-content-return-id="' +
        escape(ancestor.id) + '">Already explained above</button></div>';
    }
    var child = markup.childContext(context, reference.slot, reference.target_id);
    var entry = disclosure(child);
    entry.source = source; entry.context = child;
    var ownerTitle = source.ownerType === "module" ? source.owner.title :
      ((source.owner.display_id || source.ownerId) + " " + (source.owner.label || ""));
    return html + markup.renderContentUnit({
      origin: "authored", level: "inline", className: "optional-detail kg-shared-explanation",
      title: reference.hook, labelHtml: '<span class="kg-shared-source">' +
        escape(ownerTitle + " · " + source.block.title) + '</span>',
      anchorId: entry.id, occurrenceKey: markup.occurrenceKey(child), slot: reference.slot,
      sourceId: reference.target_id, open: entry.open,
      actions: [{position: "heading", html: options.readToggle(source.block.block_id, ownerTitle + " · " + source.block.title)}],
      bodyClass: "optional-detail-body kg-shared-body", bodyHtml: ""
    }) + '</div>';
  }

  function hydrate(element) {
    if (!element.open || !element.classList.contains("kg-shared-explanation") ||
        element.hasAttribute("data-shared-loaded")) { return false; }
    var entry = entries.get(element.getAttribute("data-content-occurrence"));
    if (!entry || !entry.source) { return false; }
    var source = entry.source;
    var context = Object.assign({}, entry.context, {ancestors: entry.context.ancestors.concat([
      {sourceId: source.block.block_id, id: entry.id}
    ])});
    element.querySelector(":scope > .kg-shared-body").innerHTML = graphic(source) +
      markup.renderBodyLines(source.block.body, "", context);
    element.setAttribute("data-shared-loaded", "true");
    return true;
  }

  function afterRender(panel) {
    nativeState.forEach(function(open, id) {
      var element = document.getElementById(id);
      if (element && panel.contains(element)) { element.open = open; }
    });
    // Rebuild only branches previously opened on this page, never the whole DAG.
    var changed;
    do {
      changed = false;
      panel.querySelectorAll("details.kg-shared-explanation[open]").forEach(function(element) {
        if (hydrate(element)) { changed = true; }
      });
    } while (changed);
  }

  function toggled(element) {
    if (!element.isConnected) { return; }
    var entry = entries.get(element.getAttribute("data-content-occurrence"));
    if (entry) { entry.open = element.open; }
    if (hydrate(element)) {
      // Hydrate only this subtree: another open sibling must receive its own
      // toggle/typeset pass rather than being marked loaded outside this one.
      afterRender(element);
      options.typeset(element);
    }
  }

  function nativeStatement(id) { return sources[id] ? statement(sources[id]) : ""; }
  function nativeGraphic(id) { return sources[id] ? graphic(sources[id]) : ""; }
  function hasGraphicBlock(owner) {
    return (owner.content_blocks || []).some(function(block) { return block.kind === "graphic"; });
  }

  return {beginPage: beginPage, afterRender: afterRender, toggled: toggled,
    rootContext: rootContext, disclosure: disclosure, renderReference: renderReference,
    nativeStatement: nativeStatement, nativeGraphic: nativeGraphic, hasGraphicBlock: hasGraphicBlock};
}
