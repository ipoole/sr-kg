/* Content escaping, optional details, math-aware paragraph splitting and shared markup. */
function kgCreateContentMarkup(options) {
  "use strict";
  var getConcept = options.concept, conceptHash = options.hash;

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function cssAttributeValueEscape(s) {
    return String(s || "").replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  }

  function renderSimpleConceptText(s) {
    var text = String(s || ""), html = "", cursor = 0;
    var macro = "\\cref";
    while (cursor < text.length) {
      var start = text.indexOf(macro, cursor);
      if (start === -1) { return html + escapeHtml(text.slice(cursor)); }
      html += escapeHtml(text.slice(cursor, start));
      var after = start + macro.length;
      if (/[A-Za-z0-9_]/.test(text.charAt(after))) {
        html += escapeHtml(macro);
        cursor = after;
        continue;
      }
      var label = parseBracedArgument(text, skipOptionalDetailWhitespace(text, after));
      var target = label && parseBracedArgument(text, skipOptionalDetailWhitespace(text, label.end));
      if (!target) {
        html += escapeHtml(macro);
        cursor = after;
        continue;
      }
      var targetId = target.value.trim();
      var labelHtml = escapeHtml(label.value);
      if (!getConcept(targetId)) {
        html += labelHtml;
      } else {
        html += '<a href="' + escapeHtml(conceptHash(targetId)) +
          '" class="concept-link" data-concept-id="' + escapeHtml(targetId) +
          '" aria-haspopup="dialog" aria-controls="kg_concept_preview"><strong>' +
          labelHtml + "</strong></a>";
      }
      cursor = target.end;
    }
    return html;
  }

  function skipOptionalDetailWhitespace(text, index) {
    while (index < text.length && /\s/.test(text.charAt(index))) {
      index += 1;
    }
    return index;
  }

  function parseBracedArgument(text, openIndex) {
    if (text.charAt(openIndex) !== "{") { return null; }

    var depth = 1;
    var index = openIndex + 1;
    var start = index;
    while (index < text.length) {
      var ch = text.charAt(index);
      if (ch === "\\") {
        index += 2;
        continue;
      }
      if (ch === "{") {
        depth += 1;
      } else if (ch === "}") {
        depth -= 1;
        if (depth === 0) {
          return {
            value: text.slice(start, index),
            end: index + 1
          };
        }
      }
      index += 1;
    }
    return null;
  }

  function renderFoldDown(options) {
    var attrs = ' data-content-origin="' + (options.origin === "personal" ? "personal" : "authored") + '"';
    if (options.anchorId) {
      attrs += ' id="' + escapeHtml(options.anchorId) + '"';
    }
    if (options.id) {
      attrs += ' data-note-id="' + escapeHtml(options.id) + '"';
    }
    if (options.contentBlockId) {
      attrs += ' data-content-block-id="' + escapeHtml(options.contentBlockId) + '"';
    }
    if (options.noteBlock) {
      attrs += ' data-note-block="true"';
    }
    if (options.occurrenceKey) {
      attrs += ' data-content-occurrence="' + escapeHtml(options.occurrenceKey) + '"';
    }
    if (options.slot) { attrs += ' data-content-slot="' + escapeHtml(options.slot) + '"'; }
    if (options.sourceId) { attrs += ' data-content-source-id="' + escapeHtml(options.sourceId) + '"'; }
    if (options.open) {
      attrs += " open";
    }
    var summaryHtml = options.summaryHtml !== undefined
      ? options.summaryHtml
      : renderConceptText(options.title || "");
    var bodyTag = options.bodyTag || "div";
    var levelClass = options.level === "block" ? " kg-content-block"
      : options.level === "inline" ? " kg-content-inline" : "";
    return '<details class="' + escapeHtml(options.className + ' kg-content-unit' + levelClass) + '"' + attrs + ">" +
      "<summary>" + summaryHtml + "</summary>" +
      "<" + bodyTag + ' class="' + escapeHtml(options.bodyClass || "") + '">' +
      (options.bodyHtml || "") +
      "</" + bodyTag + "></details>";
  }

  // A content unit is recursive. Origin, placement and capabilities are independent:
  // callers adapt storage records and supply actions; this renderer owns the shell.
  // bodyHtml is trusted renderer output, never unescaped user input.
  function renderContentUnit(unit) {
    var capabilities = unit.capabilities || {};
    var level = unit.level === "block" ? "block" : "inline";
    function renderActions(position) {
      return (unit.actions || []).filter(function(action) {
        return (action.position || "body") === position &&
          (!action.capability || capabilities[action.capability] === true);
      }).map(function(action) { return action.html || ""; }).join("");
    }
    var heading = '<span class="content-block-title-line">' +
      (unit.markHtml || "") + '<span class="content-block-title-text">' +
      renderConceptText(unit.title || "") + '</span>' + (unit.labelHtml || "") + '</span>' +
      renderActions("heading");
    var body = unit.bodyHtml !== undefined ? unit.bodyHtml : renderBodyLines(unit.body || "", "", {origin: unit.origin});
    (unit.children || []).forEach(function(child) {
      // Children are explanations unless explicitly placed at block level. Their
      // origin/capabilities are their own, not inherited from a containing unit.
      body += renderContentUnit(child);
    });
    body += renderActions("body");
    return renderFoldDown({
      origin: unit.origin, level: level, anchorId: unit.anchorId,
      id: unit.id, contentBlockId: unit.contentBlockId,
      noteBlock: capabilities.annotate === true,
      occurrenceKey: unit.occurrenceKey, slot: unit.slot, sourceId: unit.sourceId,
      open: unit.open,
      className: (unit.className || "") + " kg-content-framed" +
        (capabilities.edit ? " kg-content-editable" : "") +
        (capabilities.trackRead ? " kg-content-trackable" : ""),
      summaryHtml: heading,
      bodyClass: "kg-content-body concept-body " + (unit.bodyClass || ""),
      bodyHtml: body
    });
  }

  function childContext(context, slot, targetId) {
    context = context || {};
    return {origin: context.origin, rootId: context.rootId,
      steps: (context.steps || []).concat([[slot, targetId || ""]]),
      ancestors: context.ancestors || [], sourceId: targetId || context.sourceId,
      localSlots: targetId ? [] : (context.localSlots || []).concat([slot])};
  }

  function occurrenceKey(context) {
    return context && context.rootId ? JSON.stringify([context.rootId].concat(context.steps || [])) : "";
  }

  // This browser adapter preserves the verbatim wire body (and note anchors),
  // producing the same text/explanation/reference parts as the Python loader.
  function findNextOptionalDetailBlock(text, cursor) {
    var found = [];
    [ ["optional_details", 2], ["explanation", 3], ["explain", 4] ].forEach(function(spec) {
      var macro = "\\" + spec[0], search = cursor;
      while (search < text.length) {
        var start = text.indexOf(macro, search);
        if (start === -1) { break; }
        var end = start + macro.length;
        if (/[A-Za-z0-9_]/.test(text.charAt(end))) { search = end; continue; }
        var args = [], arg;
        for (var i = 0; i < spec[1]; i++) {
          arg = parseBracedArgument(text, skipOptionalDetailWhitespace(text, end));
          if (!arg) { break; }
          args.push(arg.value); end = arg.end;
        }
        if (args.length === spec[1]) {
          found.push({kind: "optional", name: spec[0], args: args, start: start, end: end});
          break;
        }
        search = start + macro.length;
      }
    });
    found.sort(function(a, b) { return a.start - b.start; });
    return found[0] || null;
  }

  function parseContent(text) {
    text = String(text || "");
    var parts = [], cursor = 0, legacy = 0, call;
    while ((call = findNextOptionalDetailBlock(text, cursor))) {
      if (call.start > cursor) { parts.push({type: "text", text: text.slice(cursor, call.start)}); }
      var args = call.args;
      if (call.name === "explain") {
        parts.push({type: "reference", slot: args[0].trim(), target_id: args[1].trim(),
          target_label: args[2].trim(), hook: args[3].trim()});
      } else {
        var old = call.name === "optional_details";
        parts.push({type: "explanation", slot: old ? "~legacy-" + (++legacy) : args[0].trim(),
          title: args[old ? 0 : 1].trim(), parts: parseContent(args[old ? 1 : 2])});
      }
      cursor = call.end;
    }
    if (cursor < text.length) { parts.push({type: "text", text: text.slice(cursor)}); }
    return parts;
  }

  function contentText(parts) {
    return parts.map(function(part) {
      if (part.type === "text") { return part.text; }
      if (part.type === "reference") {
        return "\\explain{" + part.slot + "}{" + part.target_id + "}{" + part.target_label + "}{" + part.hook + "}";
      }
      return "\\explanation{" + part.slot + "}{" + part.title + "}{" + contentText(part.parts) + "}";
    }).join("");
  }

  function localScopeKey(slots) { return "explanation:" + JSON.stringify(slots); }

  function renderParts(parts, context, paragraphs) {
    return parts.map(function(part) {
      if (part.type === "text") {
        return paragraphs ? renderBodyLines(part.text, "", context) : renderSimpleConceptText(part.text);
      }
      if (part.type === "reference") {
        return options.reference ? options.reference(part, context) : renderSimpleConceptText(part.target_label);
      }
      var slot = part.slot;
      // Native note placement splits the original body into paragraph blocks.
      // Anonymous legacy slots need that paragraph position to stay distinct.
      if (slot.indexOf("~legacy-") === 0 && context && context.legacyPrefix) {
        slot = context.legacyPrefix + slot;
      }
      var child = childContext(context, slot);
      var state = options.disclosure ? options.disclosure(child) : {};
      if (options.explanation && context && context.sourceId &&
          child.localSlots.every(function(id) { return id.indexOf("~legacy-") === -1; })) {
        return options.explanation(part, child, state);
      }
      return renderContentUnit({
        className: "optional-detail", level: "inline", title: part.title,
        origin: context && context.origin,
        anchorId: state.id, occurrenceKey: occurrenceKey(child), slot: part.slot,
        open: state.open, bodyClass: "optional-detail-body",
        bodyHtml: renderParts(part.parts, child, true)
      });
    }).join("");
  }

  function renderConceptText(s, context) {
    if (!/\\(?:optional_details|explanation|explain)\b/.test(String(s || ""))) {
      return renderSimpleConceptText(s);
    }
    return renderParts(parseContent(s), context);
  }

  function findNextDisplayMathBlock(text, cursor) {
    var open = "\\[";
    var close = "\\]";
    var start = text.indexOf(open, cursor);
    if (start === -1) { return null; }
    var end = text.indexOf(close, start + open.length);
    if (end === -1) { return null; }
    return {
      kind: "display-math",
      start: start,
      end: end + close.length
    };
  }

  function findNextLineBreakBlock(text, cursor) {
    var lf = text.indexOf("\n", cursor);
    var cr = text.indexOf("\r", cursor);
    if (lf === -1 && cr === -1) { return null; }
    if (cr !== -1 && (lf === -1 || cr < lf)) {
      return {
        kind: "newline",
        start: cr,
        end: text.charAt(cr + 1) === "\n" ? cr + 2 : cr + 1
      };
    }
    return {
      kind: "newline",
      start: lf,
      end: lf + 1
    };
  }

  function splitConceptBlocks(text) {
    var blocks = [];
    var raw = String(text || "");
    var cursor = 0;

    function pushText(value) {
      if (!String(value || "").trim()) { return; }
      blocks.push({kind: "text", text: value});
    }

    while (cursor < raw.length) {
      var newlineBlock = findNextLineBreakBlock(raw, cursor);
      var optionalBlock = findNextOptionalDetailBlock(raw, cursor);
      var displayBlock = findNextDisplayMathBlock(raw, cursor);
      var candidates = [];
      if (newlineBlock) { candidates.push(newlineBlock); }
      if (optionalBlock) { candidates.push(optionalBlock); }
      if (displayBlock) { candidates.push(displayBlock); }

      if (candidates.length === 0) {
        pushText(raw.slice(cursor));
        break;
      }

      candidates.sort(function(a, b) {
        return a.start - b.start || a.end - b.end;
      });
      var next = candidates[0];
      if (next.start > cursor) {
        pushText(raw.slice(cursor, next.start));
      } else if (next.kind === "newline") {
        blocks.push({kind: "text", text: ""});
      }

      if (next.kind !== "newline") {
        blocks.push({
          kind: next.kind,
          text: raw.slice(next.start, next.end)
        });
      }
      cursor = next.end;
    }

    if (raw.length === 0) {
      return [];
    }
    return blocks;
  }

  function normalizeStudyText(text) {
    return String(text || "")
      .replace(/\\n\\n/g, "\n")
      .replace(/\\n(?=(?:[A-Z]|[0-9]+)[.)]\s)/g, "\n");
  }

  function renderBodyLines(text, className, context) {
    var blocks = splitConceptBlocks(text);
    var html = '<div class="' + escapeHtml(className || "concept-body") + '">';
    blocks.forEach(function(block, index) {
      html += '<div class="concept-line">' +
        (block.text ? renderConceptText(block.text, Object.assign({}, context,
          {legacyPrefix: "paragraph-" + index})) : "&nbsp;") +
        "</div>";
    });
    html += "</div>";
    return html;
  }

  function renderStudyText(text, className) {
    return renderBodyLines(normalizeStudyText(text), className);
  }

  function renderCaptionText(s) {
    var html = renderConceptText(s);
    [
      [/partial_mu A\^mu = 0/g, "\\(\\partial_\\mu A^\\mu = 0\\)"],
      [/A_mu \+ partial_mu Lambda/g, "\\(A_\\mu + \\partial_\\mu \\Lambda\\)"],
      [/p_mu - e A_mu/g, "\\(p_\\mu - e A_\\mu\\)"],
      [/delta S = 0/g, "\\(\\delta S = 0\\)"],
      [/u\^mu = dx\^mu\/dtau/g, "\\(u^\\mu = dx^\\mu/d\\tau\\)"],
      [/p\^mu = m u\^mu/g, "\\(p^\\mu = m u^\\mu\\)"],
      [/F_mu_nu/g, "\\(F_{\\mu\\nu}\\)"],
      [/phi\(x\)/g, "\\(\\phi(x)\\)"],
      [/A_mu\(x\)/g, "\\(A_\\mu(x)\\)"],
      [/A_mu/g, "\\(A_\\mu\\)"],
      [/A\^mu/g, "\\(A^\\mu\\)"],
      [/J\^mu/g, "\\(J^\\mu\\)"],
      [/dp\^mu\/dtau/g, "\\(dp^\\mu/d\\tau\\)"],
      [/p\^mu/g, "\\(p^\\mu\\)"],
      [/x\^mu/g, "\\(x^\\mu\\)"],
      [/u\^mu/g, "\\(u^\\mu\\)"],
      [/dx\^mu\/dtau/g, "\\(dx^\\mu/d\\tau\\)"],
      [/p_mu/g, "\\(p_\\mu\\)"],
      [/s\^2/g, "\\(s^2\\)"],
      [/d\^4x/g, "\\(d^4x\\)"],
      [/E=mc\^2/g, "\\(E=mc^2\\)"],
      [/T_EM/g, "\\(T_{EM}\\)"],
      [/T\^munu/g, "\\(T^{\\mu\\nu}\\)"]
    ].forEach(function(replacement) {
      html = html.replace(replacement[0], replacement[1]);
    });
    html = html.replace(/(^|[^\\A-Za-z])tau\b/g, "$1\\(\\tau\\)");
    return html;
  }

  return {
    escapeHtml: escapeHtml,
    cssAttributeValueEscape: cssAttributeValueEscape,
    skipOptionalDetailWhitespace: skipOptionalDetailWhitespace,
    parseBracedArgument: parseBracedArgument,
    renderFoldDown: renderFoldDown,
    renderContentUnit: renderContentUnit,
    parseContent: parseContent,
    childContext: childContext, contentText: contentText, localScopeKey: localScopeKey,
    occurrenceKey: occurrenceKey,
    renderBodyLines: renderBodyLines,
    renderConceptText: renderConceptText,
    findNextOptionalDetailBlock: findNextOptionalDetailBlock,
    splitConceptBlocks: splitConceptBlocks,
    renderStudyText: renderStudyText,
    renderCaptionText: renderCaptionText
  };
}
