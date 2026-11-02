/* CSV mechanics shared by portable archives and legacy notes exchange. */
var kgCsv = (function() {
  "use strict";

  function csvEscape(value) {
    var text = String(value === undefined || value === null ? "" : value);
    return /[",\r\n]/.test(text) ? '"' + text.replace(/"/g, '""') + '"' : text;
  }

  function encodeCsv(rows) {
    return rows.map(function(row) { return row.map(csvEscape).join(","); }).join("\r\n") + "\r\n";
  }

  function parseCsv(text, options) {
    var rows = [], row = [], field = "", quoted = false;
    for (var i = 0; i < text.length; i += 1) {
      var ch = text.charAt(i);
      if (quoted) {
        if (ch === '"' && text.charAt(i + 1) === '"') { field += '"'; i += 1; }
        else if (ch === '"') { quoted = false; }
        else { field += ch; }
      } else if (ch === '"') { quoted = true; }
      else if (ch === ",") { row.push(field); field = ""; }
      else if (ch === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
      else if (ch !== "\r") { field += ch; }
    }
    if (quoted && !(options && options.allowUnclosedQuotes)) { throw new Error("CSV has an unterminated quoted field"); }
    if (field || row.length) { row.push(field); rows.push(row); }
    return rows.filter(function(item) {
      return item.some(function(value) { return value !== ""; });
    });
  }

  return {escape: csvEscape, encode: encodeCsv, parse: parseCsv};
})();
