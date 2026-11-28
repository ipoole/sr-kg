/* Shared notation, definition and search rendering for the symbols glossary. */
function kgCreateSymbolGlossary(options) {
  "use strict";
  var entries = options.entries;
  var entriesById = new Map(entries.map(function(entry) { return [entry.symbol_id, entry]; }));
  var escapeHtml = options.markup.escapeHtml;
  var table = options.table;
  var searchRows;

  function mathTokens(value) {
    var tokens = (value || "").match(/[0-9]+|./gu) || [];
    var html = tokens.map(function(token) {
      var tag = /^[0-9]+$/.test(token) ? "mn" : token === "∗" ? "mo" : "mi";
      return "<" + tag + ">" + escapeHtml(token) + "</" + tag + ">";
    }).join("");
    return tokens.length > 1 ? "<mrow>" + html + "</mrow>" : html;
  }

  function renderSymbol(entry) {
    if (!entry.subscript && !entry.superscript) { return escapeHtml(entry.symbol); }
    var base = mathTokens(entry.symbol);
    var sub = mathTokens(entry.subscript);
    var sup = mathTokens(entry.superscript);
    var indexed = entry.subscript && entry.superscript ? "<msubsup>" + base + sub + sup + "</msubsup>"
      : entry.subscript ? "<msub>" + base + sub + "</msub>" : "<msup>" + base + sup + "</msup>";
    return "<math>" + indexed + mathTokens(entry.suffix) + "</math>";
  }

  function renderDefinition(entry, className) {
    var source = options.source(entry.definition_block_id);
    var definition = entry.definition || (source && source.block.statement);
    return definition ? options.markup.renderBodyLines(definition, className) : "";
  }

  function renderLink(entry, className, content, opensPreview) {
    return '<a class="concept-link ' + className + '" href="' + escapeHtml(options.conceptHash(entry.concept_id)) +
      '" data-symbol-id="' + escapeHtml(entry.symbol_id) + '" data-concept-id="' + escapeHtml(entry.concept_id) +
      '" data-block-id="' + escapeHtml(entry.definition_block_id) + '"' +
      (opensPreview ? ' aria-label="' + escapeHtml(entry.name) + '" aria-haspopup="dialog" aria-controls="kg_concept_preview"' : '') +
      '>' + content + '</a>';
  }

  function renderBlock(block) {
    var symbols = (block.symbol_ids || []).map(function(id) { return entriesById.get(id); }).filter(Boolean);
    if (!symbols.length) { return ""; }
    var links = symbols.map(function(entry) {
      return renderLink(entry, "kg-block-symbol", renderSymbol(entry), true);
    });
    return '<div class="kg-block-symbols"><span>Symbols:</span> ' + links.join(', ') + '</div>';
  }

  function normalize(value) { return value.normalize("NFKC").toLowerCase(); }

  function buildRows() {
    var body = table.tBodies[0];
    body.innerHTML = entries.map(function(entry) {
      return "<tr><td>" + renderSymbol(entry) + "</td><td>" +
        renderLink(entry, "kg-symbol-name", escapeHtml(entry.name), false) + "</td><td>" +
        renderDefinition(entry, "kg-symbol-definition") + "</td></tr>";
    }).join("");
    searchRows = entries.map(function(entry, index) {
      return {element: body.rows[index], searchable: normalize([entry.symbol, entry.name, entry.search_terms].join(" "))};
    });
    options.typeset(body);
  }

  function filter(query) {
    if (!searchRows) { buildRows(); }
    var terms = normalize(query).trim().split(/\s+/).filter(Boolean);
    var count = 0;
    searchRows.forEach(function(row) {
      var matches = terms.every(function(term) { return row.searchable.includes(term); });
      row.element.hidden = !matches;
      if (matches) { count++; }
    });
    table.hidden = !count;
    return count;
  }

  return {
    get: function(id) { return entriesById.get(id); },
    renderBlock: renderBlock,
    renderDefinition: renderDefinition,
    filter: filter
  };
}
