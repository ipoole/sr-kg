(function(global) {
  "use strict";

  var FILES = [
    "manifest.csv", "notes.csv", "layout.csv", "study_attempts.csv",
    "study_resets.csv", "reading_progress.csv"
  ];

  function records(text, requiredHeaders) {
    var rows = kgCsv.parse(text);
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
      ["study_model", "latest-result"],
      ["profile_id", profile.profileId],
      ["profile_created_at", profile.createdAt],
      ["profile_updated_at", profile.updatedAt],
      ["exported_at", new Date().toISOString()],
      ["format", "srkg-personal-data-csv"]
    ];
    var notes = [[
      "note_id", "target_type", "target_id", "concept_id", "section", "placement", "anchor_index",
      "anchor_after", "anchor_block_id", "anchor_section_key", "anchor_context_before",
      "anchor_context_after", "title", "body", "created_at", "updated_at", "deleted_at"
    ]];
    profile.notes.forEach(function(note) {
      var anchor = note.anchor || {};
      notes.push([
        note.id, note.targetType, note.targetId, note.conceptId, note.section, note.placement || "anchor",
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
    var results = [["attempt_id", "question_id", "outcome", "attempted_at", "device_id", "attempt_count"]];
    kgCompatiblePersonalDataProfile(profile).studyAttempts.forEach(function(item) {
      results.push([item.id, item.questionId, item.outcome, item.attemptedAt, item.deviceId, 1]);
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
      "manifest.csv": kgCsv.encode(manifest),
      "notes.csv": kgCsv.encode(notes),
      "layout.csv": kgCsv.encode(layout),
      "study_attempts.csv": kgCsv.encode(results),
      "study_resets.csv": kgCsv.encode(resets),
      "reading_progress.csv": kgCsv.encode(reading)
    };
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
    var manifestRows = records(files["manifest.csv"], ["key", "value"]), manifest = {};
    manifestRows.forEach(function(row) { manifest[row.key] = row.value; });
    if (["1", "2"].indexOf(manifest.schema_version) < 0 || manifest.format !== "srkg-personal-data-csv") {
      throw new Error("Unsupported personal-data archive version");
    }
    FILES.map(function(name) {
      return manifest.schema_version === "2" && name === "study_attempts.csv" ? "study_results.csv" : name;
    }).forEach(function(name) {
      if (typeof files[name] !== "string") { throw new Error("Archive is missing " + name); }
    });
    var profile = {
      schemaVersion: Number(manifest.schema_version),
      profileId: required(manifest.profile_id, "profile_id"),
      createdAt: validTime(manifest.profile_created_at, "profile_created_at"),
      updatedAt: validTime(manifest.profile_updated_at, "profile_updated_at"),
      notes: [], layout: {publishedRevision: "", records: {}},
      studyResults: {}, studyResets: [], readingProgress: {}
    };
    records(files["notes.csv"], ["note_id", "target_type", "target_id", "section", "updated_at"]).forEach(function(row) {
      var note = {
        id: required(row.note_id, "note_id"), targetType: row.target_type,
        targetId: row.target_id, conceptId: row.concept_id, section: row.section,
        placement: row.placement === "owner" ? "owner" : "anchor",
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
    if (manifest.schema_version === "1") {
      profile.studyAttempts = [];
      records(files["study_attempts.csv"], ["attempt_id", "question_id", "outcome", "attempted_at"]).forEach(function(row) {
        if (["correct", "incorrect", "unknown"].indexOf(row.outcome) < 0) { throw new Error("Invalid question result"); }
        profile.studyAttempts.push({
          id: required(row.attempt_id, "attempt_id"), questionId: required(row.question_id, "question_id"),
          outcome: row.outcome, attemptedAt: validTime(row.attempted_at, "attempted_at"), deviceId: row.device_id
        });
      });
    } else {
      records(files["study_results.csv"], ["question_id", "outcome", "updated_at"]).forEach(function(row) {
        if (["correct", "incorrect", "unknown"].indexOf(row.outcome) < 0) { throw new Error("Invalid question result"); }
        var id = required(row.question_id, "question_id");
        if (profile.studyResults[id]) { throw new Error("Duplicate question result"); }
        profile.studyResults[id] = {questionId: id, outcome: row.outcome,
          updatedAt: validTime(row.updated_at, "updated_at"), deviceId: row.device_id};
      });
    }
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
    return kgNormalizePersonalDataProfile(profile, new Date().toISOString());
  }

  function summary(profile) {
    return {
      notes: profile.notes.filter(function(item) { return !item.deletedAt; }).length,
      layout: Object.keys(profile.layout.records).filter(function(key) {
        return !profile.layout.records[key].deletedAt;
      }).length,
      study: Object.keys(profile.studyResults).length,
      reading: Object.keys(profile.readingProgress).filter(function(key) {
        return profile.readingProgress[key].isRead;
      }).length
    };
  }

  global.kgPersonalDataArchive = {
    exportBytes: function(profile, tutorials) {
      var files = tablesFor(profile);
      if (tutorials !== undefined) {
        var document = kgTutorialPortable.collectionDocument(tutorials);
        kgTutorialPortable.collection(document); files['tutorials.json'] = kgTutorialPortable.json(document);
      }
      return kgTextZip.encode(files);
    },
    unpack: function(buffer) {
      var files = kgTextZip.decode(buffer), profile = profileFromTables(files);
      return {profile:profile,tutorials:files['tutorials.json'] === undefined ? null :
        kgTutorialPortable.collection(kgTutorialPortable.parse(files['tutorials.json']))};
    },
    importBytes: function(buffer) { return global.kgPersonalDataArchive.unpack(buffer).profile; },
    summarize: summary,
    fileNames: FILES.slice()
  };
})(window);
