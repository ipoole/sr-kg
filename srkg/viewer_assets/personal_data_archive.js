(function(global) {
  "use strict";

  var FILES = [
    "manifest.csv", "notes.csv", "layout.csv", "study_attempts.csv",
    "study_resets.csv", "reading_progress.csv"
  ];

  function csvEscape(value) {
    var text = String(value === undefined || value === null ? "" : value);
    return /[",\r\n]/.test(text) ? '"' + text.replace(/"/g, '""') + '"' : text;
  }

  function csv(rows) {
    return rows.map(function(row) { return row.map(csvEscape).join(","); }).join("\r\n") + "\r\n";
  }

  function parseCsv(text) {
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
    if (quoted) { throw new Error("CSV has an unterminated quoted field"); }
    if (field || row.length) { row.push(field); rows.push(row); }
    return rows.filter(function(item) {
      return item.some(function(value) { return value !== ""; });
    });
  }

  function records(text, requiredHeaders) {
    var rows = parseCsv(text);
    if (!rows.length) { throw new Error("CSV is missing its header row"); }
    var header = {};
    rows[0].forEach(function(name, index) { header[String(name)] = index; });
    requiredHeaders.forEach(function(name) {
      if (header[name] === undefined) { throw new Error("CSV is missing column " + name); }
    });
    return rows.slice(1).map(function(row) {
      var result = {};
      Object.keys(header).forEach(function(name) { result[name] = String(row[header[name]] || ""); });
      return result;
    });
  }

  function tablesFor(profile) {
    var manifest = [
      ["key", "value"],
      ["schema_version", "1"],
      ["profile_id", profile.profileId],
      ["profile_created_at", profile.createdAt],
      ["profile_updated_at", profile.updatedAt],
      ["exported_at", new Date().toISOString()],
      ["format", "srkg-personal-data-csv"]
    ];
    var notes = [[
      "note_id", "target_type", "target_id", "concept_id", "section", "anchor_index",
      "anchor_after", "anchor_block_id", "anchor_section_key", "anchor_context_before",
      "anchor_context_after", "title", "body", "created_at", "updated_at", "deleted_at"
    ]];
    profile.notes.forEach(function(note) {
      var anchor = note.anchor || {};
      notes.push([
        note.id, note.targetType, note.targetId, note.conceptId, note.section,
        Number(anchor.blockIndex) || 0, anchor.afterText, anchor.blockId, anchor.sectionKey,
        anchor.contextBefore, anchor.contextAfter, note.title, note.body,
        note.createdAt, note.updatedAt, note.deletedAt
      ]);
    });
    var layout = [[
      "object_type", "object_id", "x", "y", "published_revision",
      "updated_at", "deleted_at", "device_id"
    ]];
    Object.keys(profile.layout.records).sort().forEach(function(key) {
      var item = profile.layout.records[key];
      layout.push([
        item.objectType, item.objectId, item.x, item.y, profile.layout.publishedRevision,
        item.updatedAt, item.deletedAt, item.deviceId
      ]);
    });
    var attempts = [[
      "attempt_id", "question_id", "outcome", "attempted_at", "device_id", "attempt_count"
    ]];
    profile.studyAttempts.forEach(function(item) {
      attempts.push([
        item.id, item.questionId, item.outcome, item.attemptedAt,
        item.deviceId, item.attemptCount
      ]);
    });
    var resets = [["reset_id", "question_id", "reset_at", "device_id"]];
    profile.studyResets.forEach(function(item) {
      resets.push([item.id, item.questionId, item.resetAt, item.deviceId]);
    });
    var reading = [["block_id", "is_read", "updated_at", "device_id"]];
    Object.keys(profile.readingProgress).sort().forEach(function(blockId) {
      var item = profile.readingProgress[blockId];
      reading.push([blockId, item.isRead ? "true" : "false", item.updatedAt, item.deviceId]);
    });
    return {
      "manifest.csv": csv(manifest),
      "notes.csv": csv(notes),
      "layout.csv": csv(layout),
      "study_attempts.csv": csv(attempts),
      "study_resets.csv": csv(resets),
      "reading_progress.csv": csv(reading)
    };
  }

  var crcTable = null;
  function crc32(bytes) {
    if (!crcTable) {
      crcTable = [];
      for (var n = 0; n < 256; n += 1) {
        var c = n;
        for (var k = 0; k < 8; k += 1) { c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; }
        crcTable[n] = c >>> 0;
      }
    }
    var crc = 0xffffffff;
    for (var i = 0; i < bytes.length; i += 1) {
      crc = crcTable[(crc ^ bytes[i]) & 0xff] ^ (crc >>> 8);
    }
    return (crc ^ 0xffffffff) >>> 0;
  }

  function u16(value) { return [value & 255, value >>> 8 & 255]; }
  function u32(value) { return [value & 255, value >>> 8 & 255, value >>> 16 & 255, value >>> 24 & 255]; }
  function join(parts) {
    var length = parts.reduce(function(total, item) { return total + item.length; }, 0);
    var result = new Uint8Array(length), offset = 0;
    parts.forEach(function(item) { result.set(item, offset); offset += item.length; });
    return result;
  }

  function makeZip(files) {
    var encoder = new TextEncoder(), locals = [], centrals = [], offset = 0, count = 0;
    Object.keys(files).forEach(function(name) {
      var nameBytes = encoder.encode(name), data = encoder.encode(files[name]);
      var crc = crc32(data), size = data.length;
      var local = new Uint8Array([
        0x50,0x4b,0x03,0x04].concat(u16(20),u16(0x0800),u16(0),u16(0),u16(0),
          u32(crc),u32(size),u32(size),u16(nameBytes.length),u16(0)));
      locals.push(local, nameBytes, data);
      var central = new Uint8Array([
        0x50,0x4b,0x01,0x02].concat(u16(20),u16(20),u16(0x0800),u16(0),u16(0),u16(0),
          u32(crc),u32(size),u32(size),u16(nameBytes.length),u16(0),u16(0),u16(0),u16(0),
          u32(0),u32(offset)));
      centrals.push(central, nameBytes);
      offset += local.length + nameBytes.length + data.length;
      count += 1;
    });
    var centralBytes = join(centrals);
    var end = new Uint8Array([
      0x50,0x4b,0x05,0x06].concat(u16(0),u16(0),u16(count),u16(count),
        u32(centralBytes.length),u32(offset),u16(0)));
    return join(locals.concat([centralBytes, end]));
  }

  function readZip(buffer) {
    var bytes = new Uint8Array(buffer), view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    function d16(at) { return view.getUint16(at, true); }
    function d32(at) { return view.getUint32(at, true); }
    var end = -1;
    for (var i = bytes.length - 22; i >= Math.max(0, bytes.length - 65557); i -= 1) {
      if (d32(i) === 0x06054b50) { end = i; break; }
    }
    if (end < 0) { throw new Error("Not a supported ZIP archive"); }
    var count = d16(end + 10), cursor = d32(end + 16), decoder = new TextDecoder("utf-8"), files = {};
    for (var entry = 0; entry < count; entry += 1) {
      if (d32(cursor) !== 0x02014b50) { throw new Error("Invalid ZIP directory"); }
      var method = d16(cursor + 10), size = d32(cursor + 24);
      var nameLength = d16(cursor + 28), extraLength = d16(cursor + 30), commentLength = d16(cursor + 32);
      var localOffset = d32(cursor + 42);
      var name = decoder.decode(bytes.slice(cursor + 46, cursor + 46 + nameLength));
      if (method !== 0 || d32(localOffset) !== 0x04034b50) {
        throw new Error("Archive must use uncompressed ZIP entries");
      }
      var localNameLength = d16(localOffset + 26), localExtraLength = d16(localOffset + 28);
      var start = localOffset + 30 + localNameLength + localExtraLength;
      if (start + size > bytes.length) { throw new Error("ZIP entry is truncated"); }
      files[name] = decoder.decode(bytes.slice(start, start + size));
      cursor += 46 + nameLength + extraLength + commentLength;
    }
    return files;
  }

  function required(value, label) {
    if (!String(value || "")) { throw new Error(label + " is required"); }
    return String(value);
  }

  function validTime(value, label) {
    value = required(value, label);
    if (Number.isNaN(Date.parse(value))) { throw new Error(label + " is invalid"); }
    return new Date(value).toISOString();
  }

  function profileFromTables(files) {
    FILES.forEach(function(name) {
      if (typeof files[name] !== "string") { throw new Error("Archive is missing " + name); }
    });
    var manifestRows = records(files["manifest.csv"], ["key", "value"]), manifest = {};
    manifestRows.forEach(function(row) { manifest[row.key] = row.value; });
    if (manifest.schema_version !== "1" || manifest.format !== "srkg-personal-data-csv") {
      throw new Error("Unsupported personal-data archive version");
    }
    var profile = {
      schemaVersion: 1,
      profileId: required(manifest.profile_id, "profile_id"),
      createdAt: validTime(manifest.profile_created_at, "profile_created_at"),
      updatedAt: validTime(manifest.profile_updated_at, "profile_updated_at"),
      notes: [], layout: {publishedRevision: "", records: {}},
      studyAttempts: [], studyResets: [], readingProgress: {}
    };
    records(files["notes.csv"], ["note_id", "target_type", "target_id", "section", "updated_at"]).forEach(function(row) {
      var note = {
        id: required(row.note_id, "note_id"), targetType: row.target_type,
        targetId: row.target_id, conceptId: row.concept_id, section: row.section,
        anchor: {
          blockIndex: Math.max(0, Number(row.anchor_index) || 0), afterText: row.anchor_after,
          blockId: row.anchor_block_id, sectionKey: row.anchor_section_key,
          contextBefore: row.anchor_context_before, contextAfter: row.anchor_context_after
        },
        title: row.title, body: row.body,
        createdAt: validTime(row.created_at, "created_at"),
        updatedAt: validTime(row.updated_at, "updated_at"), deletedAt: ""
      };
      if (row.deleted_at) { note.deletedAt = validTime(row.deleted_at, "deleted_at"); }
      profile.notes.push(note);
    });
    records(files["layout.csv"], ["object_type", "object_id", "x", "y", "updated_at"]).forEach(function(row) {
      if (["concept", "module"].indexOf(row.object_type) === -1) { throw new Error("Invalid layout object type"); }
      var x = Number(row.x), y = Number(row.y);
      if (!Number.isFinite(x) || !Number.isFinite(y)) { throw new Error("Invalid layout coordinates"); }
      var item = {
        objectType: row.object_type, objectId: required(row.object_id, "object_id"),
        x: x, y: y, updatedAt: validTime(row.updated_at, "updated_at"),
        deletedAt: "", deviceId: row.device_id
      };
      if (row.deleted_at) { item.deletedAt = validTime(row.deleted_at, "deleted_at"); }
      profile.layout.records[item.objectType + ":" + item.objectId] = item;
      if (row.published_revision) { profile.layout.publishedRevision = row.published_revision; }
    });
    records(files["study_attempts.csv"], ["attempt_id", "question_id", "outcome", "attempted_at", "attempt_count"]).forEach(function(row) {
      var count = Number(row.attempt_count);
      if (["correct", "incorrect", "unknown"].indexOf(row.outcome) === -1 ||
          !Number.isInteger(count) || count < 1) { throw new Error("Invalid study attempt"); }
      profile.studyAttempts.push({
        id: required(row.attempt_id, "attempt_id"), questionId: required(row.question_id, "question_id"),
        outcome: row.outcome, attemptedAt: validTime(row.attempted_at, "attempted_at"),
        deviceId: row.device_id, attemptCount: count
      });
    });
    records(files["study_resets.csv"], ["reset_id", "question_id", "reset_at"]).forEach(function(row) {
      profile.studyResets.push({
        id: required(row.reset_id, "reset_id"), questionId: required(row.question_id, "question_id"),
        resetAt: validTime(row.reset_at, "reset_at"), deviceId: row.device_id
      });
    });
    records(files["reading_progress.csv"], ["block_id", "is_read", "updated_at"]).forEach(function(row) {
      if (["true", "false"].indexOf(row.is_read) === -1) { throw new Error("Invalid reading mark"); }
      profile.readingProgress[row.block_id] = {
        blockId: required(row.block_id, "block_id"), isRead: row.is_read === "true",
        updatedAt: validTime(row.updated_at, "updated_at"), deviceId: row.device_id
      };
    });
    return profile;
  }

  function summary(profile) {
    return {
      notes: profile.notes.filter(function(item) { return !item.deletedAt; }).length,
      layout: Object.keys(profile.layout.records).filter(function(key) {
        return !profile.layout.records[key].deletedAt;
      }).length,
      study: profile.studyAttempts.length,
      reading: Object.keys(profile.readingProgress).filter(function(key) {
        return profile.readingProgress[key].isRead;
      }).length
    };
  }

  global.kgPersonalDataArchive = {
    exportBytes: function(profile) { return makeZip(tablesFor(profile)); },
    importBytes: function(buffer) { return profileFromTables(readZip(buffer)); },
    summarize: summary,
    fileNames: FILES.slice()
  };
})(window);
