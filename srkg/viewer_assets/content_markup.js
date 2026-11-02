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
    var attrs = "";
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
    if (options.open) {
      attrs += " open";
    }
    var summaryHtml = options.summaryHtml !== undefined
      ? options.summaryHtml
      : renderConceptText(options.title || "");
    var bodyTag = options.bodyTag || "div";
    return '<details class="' + escapeHtml(options.className) + '"' + attrs + ">" +
      "<summary>" + summaryHtml + "</summary>" +
      "<" + bodyTag + ' class="' + escapeHtml(options.bodyClass || "") + '">' +
      (options.bodyHtml || "") +
      "</" + bodyTag + "></details>";
  }

  function renderOptionalDetail(summary, body) {
    return renderFoldDown({
      className: "optional-detail",
      title: summary,
      bodyClass: "concept-body optional-detail-body",
      bodyHtml: renderConceptText(body)
    });
  }

  function renderConceptText(s) {
    var text = String(s || "");
    var macro = "\\optional_details";
    var html = "";
    var cursor = 0;

    while (cursor < text.length) {
      var macroIndex = text.indexOf(macro, cursor);
      if (macroIndex === -1) {
        html += renderSimpleConceptText(text.slice(cursor));
        break;
      }

      html += renderSimpleConceptText(text.slice(cursor, macroIndex));
      var summaryStart = skipOptionalDetailWhitespace(text, macroIndex + macro.length);
      var summary = parseBracedArgument(text, summaryStart);
      if (!summary) {
        html += renderSimpleConceptText(macro);
        cursor = macroIndex + macro.length;
        continue;
      }

      var bodyStart = skipOptionalDetailWhitespace(text, summary.end);
      var body = parseBracedArgument(text, bodyStart);
      if (!body) {
        html += renderSimpleConceptText(text.slice(macroIndex, summary.end));
        cursor = summary.end;
        continue;
      }

      html += renderOptionalDetail(summary.value, body.value);
      cursor = body.end;
    }

    return html;
  }

  function findNextOptionalDetailBlock(text, cursor) {
    var macro = "\\optional_details";
    var search = cursor;
    while (search < text.length) {
      var macroIndex = text.indexOf(macro, search);
      if (macroIndex === -1) { return null; }

      var summaryStart = skipOptionalDetailWhitespace(text, macroIndex + macro.length);
      var summary = parseBracedArgument(text, summaryStart);
      if (!summary) {
        search = macroIndex + macro.length;
        continue;
      }

      var bodyStart = skipOptionalDetailWhitespace(text, summary.end);
      var body = parseBracedArgument(text, bodyStart);
      if (!body) {
        search = summary.end;
        continue;
      }

      return {
        kind: "optional",
        start: macroIndex,
        end: body.end
      };
    }
    return null;
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

  function renderBodyLines(text, className) {
    var blocks = splitConceptBlocks(text);
    var html = '<div class="' + escapeHtml(className || "concept-body") + '">';
    blocks.forEach(function(block) {
      html += '<div class="concept-line">' +
        (block.text ? renderConceptText(block.text) : "&nbsp;") +
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
    renderConceptText: renderConceptText,
    findNextOptionalDetailBlock: findNextOptionalDetailBlock,
    splitConceptBlocks: splitConceptBlocks,
    renderStudyText: renderStudyText,
    renderCaptionText: renderCaptionText
  };
}
