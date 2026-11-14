/* Canonical authored sources and transient, independently folded reading paths. */
function kgCreateSharedExplanations(options) {
  "use strict";
  var markup = options.markup, escape = markup.escapeHtml;
  var sources = Object.create(null), currentPage = "", entries = new Map();
  var nativeState = new Map(), nextId = 0;

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
    return {origin: "authored", rootId: sourceId, sourceId: sourceId, localSlots: [], steps: [],
      ancestors: [{sourceId: sourceId, id: anchorId}]};
  }

  function disclosure(context) {
    var key = markup.occurrenceKey(context);
    if (!key) { return {}; }
    if (!entries.has(key)) { entries.set(key, {id: "kg-explanation-" + (++nextId), open: false}); }
    return entries.get(key);
  }

  function statement(source) {
    return (source.block.statement
      ? markup.renderBodyLines(source.block.statement, "kg-content-statement") : "") + markup.previewFigure(source.block);
  }

  function graphic(source) {
    if (source.block.graphic !== "detail") { return ""; }
    var owner = source.owner;
    var svg = owner.svg_detail || owner.svg_icon || "";
    if (!svg) { return '<p class="kg-shared-unavailable">Illustration unavailable in this edition.</p>'; }
    svg = markup.scopedSvg(svg);
    var moduleClass = source.ownerType === "module" ? " module-graphic" : "";
    var caption = owner.svg_detail_caption || owner.svg_icon_caption || "";
    return '<figure class="kg-shared-figure"><div class="concept-graphic' + moduleClass + '">' + svg + '</div>' +
      (caption ? '<figcaption class="concept-graphic-caption">' + markup.renderCaptionText(caption) + '</figcaption>' : "") + '</figure>';
  }

  // Placement changes the shell, not the source body or its capabilities.
  function actions(id, capabilities, readLabel) {
    var source = sources[id];
    return source ? options.actions(source, capabilities, readLabel || source.block.title) : [];
  }

  function body(id, context, capabilities) {
    var source = sources[id];
    if (!source) { return ""; }
    return graphic(source) + options.body(source, context,
      Object.assign({}, capabilities, {hideProse: source.block.kind === "graphic"}));
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
    // Unconverted authored borrowing must not create extra graph branches in a
    // generated tree. Keep its contribution and an ordinary source preview.
    if (context.readingTree) {
      return '<div class="kg-reading-legacy-reference">' + statement(source) +
        '<a href="#" class="concept-link" data-concept-id="' + escape(source.ownerId) +
        '">' + escape(reference.target_label || source.block.title) + '</a></div>';
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
      capabilities: {trackRead: true, annotate: true},
      actions: actions(reference.target_id, {trackRead: true, annotate: true}, ownerTitle + " · " + source.block.title),
      bodyClass: "optional-detail-body kg-shared-body", bodyHtml: ""
    }) + '</div>';
  }

  function local(part, context, state) {
    var source = sources[context.sourceId];
    var localSource = Object.assign({}, source, {
      sectionKey: markup.localScopeKey(context.localSlots),
      block: Object.assign({}, source.block, {title: part.title,
        body: markup.contentText(part.parts), graphic: ""})
    });
    var capabilities = {annotate: true, trackRead: false};
    return markup.renderContentUnit({
      origin: "authored", level: "inline", className: "optional-detail kg-local-explanation",
      title: part.title, anchorId: state.id, occurrenceKey: markup.occurrenceKey(context),
      sourceId: context.sourceId,
      slot: part.slot, open: state.open, capabilities: capabilities,
      actions: options.actions(localSource, capabilities, part.title),
      bodyClass: "optional-detail-body", bodyHtml:
        (options.readingFocus ? options.readingFocus(state.id, context) : "") +
        options.body(localSource, context, capabilities)
    });
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
    element.querySelector(":scope > .kg-shared-body").innerHTML = body(source.block.block_id, context, {annotate: true});
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
  function hasGraphicBlock(owner) {
    return (owner.content_blocks || []).some(function(block) { return block.kind === "graphic"; });
  }

  function source(id) { return sources[id] || null; }
  function preview(id) {
    var found = source(id);
    // Shared artwork/prose rendering, without notes, ticks or reading paths.
    return found ? graphic(found) + markup.renderBodyLines(found.block.body) : "";
  }

  return {reset: function() { currentPage = ""; entries.clear(); nativeState.clear(); }, beginPage: beginPage, afterRender: afterRender, toggled: toggled,
    rootContext: rootContext, disclosure: disclosure, renderReference: renderReference, local: local,
    nativeStatement: nativeStatement, body: body, actions: actions, hasGraphicBlock: hasGraphicBlock,
    source: source, preview: preview};
}
