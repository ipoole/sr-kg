/* Details DOM/MathJax lifecycle, section navigation and scroll state. */
function kgCreateDetailsView(options) {
  "use strict";
  var cssAttributeValueEscape = options.markup.cssAttributeValueEscape;
  var searchDisplayText = options.content.searchDisplayText;
  var schedulePanelContentRefit = options.onContentChange;
  var activeConceptSectionTargetId = null, currentConceptTocItems = [];
  var detailScrollSyncTimer = null, detailScrollSyncSuppressedUntil = 0;
  function setItems(items) { currentConceptTocItems = items.slice(); }
  function suppressScrollSync(duration) { detailScrollSyncSuppressedUntil = Date.now() + duration; }
  function activeTargetId() { return activeConceptSectionTargetId; }
  function restoreTarget(id) { activeConceptSectionTargetId = id || null; }

  var graphicSpacingMeasurements = new WeakMap();
  var equationAccessibility = new WeakMap();
  var foldFooters = new WeakMap(), foldTargets = new WeakMap();

  function refreshFoldControls(scope) {
    var panel = document.getElementById("info_panel");
    scope = scope || panel;
    if (!scope || !panel || !panel.contains(scope)) { return; }
    var items = Array.from(scope.querySelectorAll("details"));
    if (scope.matches("details")) { items.unshift(scope); }
    items.forEach(function(item) {
      if (item.closest(".concept-toc")) { return; }
      var heading = item.querySelector(":scope > summary");
      if (!heading) { return; }
      var footer = foldFooters.get(item);
      if (!footer) {
        footer = document.createElement("div");
        footer.className = "kg-content-footer";
        footer.innerHTML = '<label class="kg-footer-read-slot"></label>' +
          '<button type="button" class="kg-content-refold">Fold ↑</button>';
        var title = heading.querySelector(".content-block-title-text, .content-block-title-line") || heading;
        footer.querySelector("button").setAttribute("aria-label", "Fold " + title.textContent.trim());
        foldFooters.set(item, footer); foldTargets.set(footer, item);
      }
      // Lazy hydration can replace a body; full-width focus merely moves it.
      if (!footer.isConnected) {
        var body = item.querySelector(":scope > .kg-content-body, :scope > .kg-reading-concept-body, :scope > .kg-reading-tree-body");
        (body || item).appendChild(footer);
      }
      var slot = footer.querySelector(".kg-footer-read-slot");
      var tick = heading.querySelector(".content-block-read-toggle");
      if (tick && item.open && !slot.querySelector("input")) {
        var bottomTick = tick.cloneNode(true);
        bottomTick.removeAttribute("id");
        slot.appendChild(bottomTick);
      } else if (!item.open && slot.firstChild) {
        slot.replaceChildren();
      }
    });
  }

  function foldFromFooter(event) {
    var button = event.target.closest(".kg-content-refold");
    if (!button) { return false; }
    var item = foldTargets.get(button.closest(".kg-content-footer"));
    if (!item) { return false; }
    if (options.beforeFold) { options.beforeFold(item); }
    var noteId = item.getAttribute("data-note-id"), occurrence = item.getAttribute("data-content-occurrence");
    item.open = false;
    refreshFoldControls(item);
    requestAnimationFrame(function() {
      // Folding an edited note replaces its shell after saving the draft.
      if (!item.isConnected && noteId) {
        item = Array.from(document.querySelectorAll("#info_panel .user-note")).find(function(note) {
          return note.getAttribute("data-note-id") === noteId &&
            note.getAttribute("data-content-occurrence") === occurrence;
        });
      }
      if (!item || !item.isConnected) { return; }
      var heading = item.classList.contains("kg-reading-concept")
        ? item.parentElement.querySelector(":scope > .kg-reading-concept-title > button")
        : item.querySelector(":scope > summary");
      if (!heading) { return; }
      var panel = document.getElementById("info_panel"), bounds = panel.getBoundingClientRect();
      var sticky = panel.querySelector(".concept-sticky-header");
      var top = sticky ? sticky.getBoundingClientRect().bottom : bounds.top;
      var rect = heading.getBoundingClientRect();
      if (rect.top < top + 8 || rect.bottom > bounds.bottom - 8) {
        scrollInfoPanelTargetBelowStickyToc(heading, {immediate: true});
      }
      heading.focus({preventScroll: true});
    });
    return true;
  }

  function refreshEquationOverflow() {
    var equations = Array.from(document.querySelectorAll('#info_panel mjx-container[display="true"]'));
    equations.forEach(function(equation) {
      var wrapper = equation.parentElement;
      if (!wrapper.classList.contains("kg-equation-scroll")) {
        wrapper = document.createElement("div");
        wrapper.className = "kg-equation-scroll";
        equation.before(wrapper);
        wrapper.appendChild(equation);
        var hint = document.createElement("span");
        hint.className = "kg-equation-scroll-hint";
        hint.textContent = "↔";
        hint.hidden = true;
        hint.setAttribute("aria-hidden", "true");
        wrapper.appendChild(hint);
      }
    });
    // Batch layout reads before visual updates, including after a zoom or resize.
    var overflow = equations.map(function(equation) {
      var width = equation.clientWidth;
      return width > 0 && equation.scrollWidth > width + 2;
    });
    equations.forEach(function(equation, index) {
      var wrapper = equation.parentElement, overflowing = overflow[index];
      var saved = equationAccessibility.get(equation);
      // Only update the DOM when overflow changes; preserve MathJax's own
      // accessibility attributes while temporarily making wide maths focusable.
      if (overflowing === Boolean(saved)) { return; }
      wrapper.classList.toggle("kg-equation-overflow", overflowing);
      wrapper.querySelector(".kg-equation-scroll-hint").hidden = !overflowing;
      if (overflowing) {
        var original = {};
        ["tabindex", "role", "aria-label"].forEach(function(name) {
          original[name] = equation.getAttribute(name);
        });
        equationAccessibility.set(equation, original);
        equation.setAttribute("tabindex", "0");
        equation.setAttribute("role", "region");
        equation.setAttribute("aria-label", "Wide equation; scroll horizontally to read the rest");
      } else {
        Object.keys(saved).forEach(function(name) {
          if (saved[name] === null) { equation.removeAttribute(name); }
          else { equation.setAttribute(name, saved[name]); }
        });
        equationAccessibility.delete(equation);
      }
    });
  }

  function compactGraphicSpacing() {
    document.querySelectorAll("#info_panel .concept-graphic").forEach(function(graphic) {
      var svg = graphic.querySelector(":scope > svg");
      var caption = graphic.nextElementSibling;
      if (!svg || !caption || !caption.matches("figcaption")) { return; }
      var rect = svg.getBoundingClientRect();
      if (!rect.width || !rect.height) { return; }
      var lineHeight = parseFloat(getComputedStyle(caption).lineHeight);
      var signature = [rect.width, rect.height, lineHeight].join(":");
      if (graphicSpacingMeasurements.get(svg) === signature) { return; }
      var transform = svg.getScreenCTM();
      if (!transform || !Number.isFinite(lineHeight)) { return; }
      var ink = svg.getBBox();
      var point = svg.createSVGPoint();
      point.y = ink.y + ink.height;
      var inkBottom = point.matrixTransform(transform).y;
      // Reclaim only empty canvas, leaving stroke/marker clearance. Fixed negative
      // margins caused the old overlap; this amount is bounded by measured ink.
      var clearance = Math.max(8, rect.height * 0.04);
      var trim = Math.min(2 * lineHeight, Math.max(0, rect.bottom - inkBottom - clearance));
      graphic.style.marginBottom = String(-trim) + "px";
      graphicSpacingMeasurements.set(svg, signature);
    });
  }

  function clearMathTypesetting(element) {
    if (element && window.MathJax && MathJax.typesetClear) {
      MathJax.typesetClear([element]);
    }
  }

  function replaceTypesetContent(element, html) {
    if (!element) { return; }
    clearMathTypesetting(element);
    element.innerHTML = html;
  }

  function typesetInfoPanel(options) {
    options = options || {};
    var panel = options.element || document.getElementById("info_panel");
    refreshFoldControls(panel);
    schedulePanelContentRefit();
    if (window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise([panel]).catch(function(err) {
        console.warn("MathJax typesetting failed:", err);
      }).then(function() {
        applyInfoPanelSearchHighlight(options.searchQuery, options.scrollToSearchMatch);
        schedulePanelContentRefit();
      });
    } else if (options.searchQuery) {
      setTimeout(function() {
        applyInfoPanelSearchHighlight(options.searchQuery, options.scrollToSearchMatch);
        schedulePanelContentRefit();
      }, 250);
    }
  }

  function shouldSkipSearchHighlightNode(node) {
    var el = node.parentElement;
    if (!el) { return true; }
    return Boolean(el.closest(
      "mark, .study-questions, .concept-references, svg, mjx-container, script, style"
    ));
  }

  function applyInfoPanelSearchHighlight(query, scrollToMatch) {
    var normalizedQuery = searchDisplayText(query).toLowerCase();
    if (!normalizedQuery) { return; }

    var panel = document.getElementById("info_panel");
    var walker = document.createTreeWalker(panel, NodeFilter.SHOW_TEXT, {
      acceptNode: function(node) {
        if (shouldSkipSearchHighlightNode(node)) {
          return NodeFilter.FILTER_REJECT;
        }
        if (node.nodeValue.toLowerCase().indexOf(normalizedQuery) === -1) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });

    var matches = [];
    var node;
    while ((node = walker.nextNode())) {
      matches.push(node);
    }

    var firstMark = null;
    matches.forEach(function(textNode) {
      var value = textNode.nodeValue;
      var lower = value.toLowerCase();
      var fragment = document.createDocumentFragment();
      var cursor = 0;
      var index = lower.indexOf(normalizedQuery);

      while (index !== -1) {
        if (index > cursor) {
          fragment.appendChild(document.createTextNode(value.slice(cursor, index)));
        }

        var mark = document.createElement("mark");
        mark.className = "kg-search-mark kg-detail-search-mark";
        mark.textContent = value.slice(index, index + normalizedQuery.length);
        fragment.appendChild(mark);
        if (!firstMark) { firstMark = mark; }

        cursor = index + normalizedQuery.length;
        index = lower.indexOf(normalizedQuery, cursor);
      }

      if (cursor < value.length) {
        fragment.appendChild(document.createTextNode(value.slice(cursor)));
      }
      textNode.parentNode.replaceChild(fragment, textNode);
    });

    if (scrollToMatch && firstMark) {
      var ancestor = firstMark.parentElement;
      while (ancestor && ancestor !== panel) {
        if (ancestor.tagName === "DETAILS") { ancestor.open = true; }
        ancestor = ancestor.parentElement;
      }
      firstMark.scrollIntoView({block: "center", inline: "nearest"});
    }
  }

  function openTargetForToc(target) {
    if (!target) { return; }
    if (target.tagName === "DETAILS") {
      target.open = true;
      return;
    }
    var closedDetails = target.closest && target.closest("details:not([open])");
    if (closedDetails) {
      closedDetails.open = true;
    }
  }

  function scrollInfoPanelTargetBelowStickyToc(target, options) {
    options = options || {};
    var panel = document.getElementById("info_panel");
    if (!panel || !target) { return; }

    var panelRect = panel.getBoundingClientRect();
    var targetRect = target.getBoundingClientRect();
    var stickyHeader = panel.querySelector(".concept-sticky-header");
    var toc = panel.querySelector(".concept-toc");
    var stickyOffset = 0;
    if (stickyHeader) {
      stickyOffset = stickyHeader.getBoundingClientRect().bottom - panelRect.top + 8;
    } else if (toc) {
      stickyOffset = toc.getBoundingClientRect().bottom - panelRect.top + 8;
    }

    var targetTop = targetRect.top - panelRect.top + panel.scrollTop;
    panel.scrollTo({
      top: Math.max(0, targetTop - stickyOffset),
      behavior: options.immediate ? "auto" : "smooth"
    });
  }

  function updateConceptTocActive(targetId) {
    var panel = document.getElementById("info_panel");
    if (!panel) { return; }
    panel.querySelectorAll(".concept-toc-link.active").forEach(function(link) {
      link.classList.remove("active");
      link.removeAttribute("aria-current");
    });
    panel.querySelectorAll(".kg-active-section").forEach(function(section) {
      section.classList.remove("kg-active-section");
    });
    if (!targetId) { return; }
    var link = panel.querySelector(
      '.concept-toc-link[data-toc-target="' + cssAttributeValueEscape(targetId) + '"]'
    );
    if (!link) { return; }
    link.classList.add("active");
    link.setAttribute("aria-current", "true");
    var target = document.getElementById(targetId);
    if (target) { target.classList.add("kg-active-section"); }
  }

  function setActiveConceptSection(targetId) {
    var nextTargetId = targetId ? String(targetId) : null;
    var targetChanged = activeConceptSectionTargetId !== nextTargetId;
    activeConceptSectionTargetId = nextTargetId;
    if (targetChanged) { updateConceptTocActive(nextTargetId); }
  }

  function initialTocItem(tocItems) {
    if (!Array.isArray(tocItems) || tocItems.length === 0) { return null; }
    if (activeConceptSectionTargetId) {
      var previous = tocItems.find(function(item) {
        return item.id === activeConceptSectionTargetId;
      });
      if (previous) { return previous; }
    }
    return tocItems[0];
  }

  function activeTocItemFromScroll() {
    var panel = document.getElementById("info_panel");
    if (!panel || currentConceptTocItems.length === 0) { return null; }
    var panelRect = panel.getBoundingClientRect();
    var stickyHeader = panel.querySelector(".concept-sticky-header");
    var stickyBottom = stickyHeader
      ? stickyHeader.getBoundingClientRect().bottom
      : panelRect.top;
    var cursorY = stickyBottom + 12;
    var best = null;
    var bestTop = -Infinity;
    var firstVisible = null;

    currentConceptTocItems.forEach(function(item) {
      var target = document.getElementById(item.id);
      if (!target) { return; }
      var rect = target.getBoundingClientRect();
      if (rect.bottom < panelRect.top || rect.top > panelRect.bottom) { return; }
      if (!firstVisible || rect.top < firstVisible.top) {
        firstVisible = {item: item, top: rect.top};
      }
      if (rect.top <= cursorY && rect.top >= bestTop) {
        best = item;
        bestTop = rect.top;
      }
    });

    return best || (firstVisible && firstVisible.item) || null;
  }

  function updateActiveSectionFromScroll() {
    var item = activeTocItemFromScroll();
    if (!item) { return; }
    setActiveConceptSection(item.id);
  }

  function scheduleDetailScrollSync() {
    if (Date.now() < detailScrollSyncSuppressedUntil) { return; }
    if (detailScrollSyncTimer !== null) {
      clearTimeout(detailScrollSyncTimer);
    }
    detailScrollSyncTimer = setTimeout(function() {
      detailScrollSyncTimer = null;
      if (Date.now() < detailScrollSyncSuppressedUntil) { return; }
      updateActiveSectionFromScroll();
    }, 80);
  }

  return {
    refreshFoldControls: refreshFoldControls,
    foldFromFooter: foldFromFooter,
    clearMathTypesetting: clearMathTypesetting,
    replaceTypesetContent: replaceTypesetContent,
    compactGraphicSpacing: compactGraphicSpacing,
    refreshEquationOverflow: refreshEquationOverflow,
    typesetInfoPanel: typesetInfoPanel,
    openTargetForToc: openTargetForToc,
    scrollInfoPanelTargetBelowStickyToc: scrollInfoPanelTargetBelowStickyToc,
    updateConceptTocActive: updateConceptTocActive,
    setActiveConceptSection: setActiveConceptSection,
    initialTocItem: initialTocItem,
    scheduleDetailScrollSync: scheduleDetailScrollSync,
    setItems: setItems,
    suppressScrollSync: suppressScrollSync,
    activeTargetId: activeTargetId,
    restoreTarget: restoreTarget
  };
}
