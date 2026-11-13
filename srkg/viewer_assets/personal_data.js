(function(global) {
  "use strict";

  var SCHEMA_VERSION = 2;

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function iso(value, fallback) {
    var date = value ? new Date(value) : null;
    return date && !Number.isNaN(date.getTime()) ? date.toISOString() : fallback;
  }

  function randomId(prefix) {
    if (global.crypto && typeof global.crypto.randomUUID === "function") {
      return prefix + global.crypto.randomUUID();
    }
    return prefix + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 12);
  }

  function validPosition(value) {
    return Boolean(value && Number.isFinite(Number(value.x)) && Number.isFinite(Number(value.y)));
  }

  function createEmptyProfile(now) {
    return {
      schemaVersion: SCHEMA_VERSION,
      profileId: randomId("profile-"),
      createdAt: now,
      updatedAt: now,
      legacyMigratedAt: "",
      notes: [],
      layout: {publishedRevision: "", records: {}},
      studyResults: {},
      studyResets: [],
      readingProgress: {}
    };
  }

  // Keep the shared storage/cloud envelope readable by the published viewer.
  // A wire count of one denotes this single retained result, never a total.
  function compatibleProfile(profile) {
    var wire = Object.assign({}, profile);
    wire.schemaVersion = 1;
    wire.studyResultsVersion = 2;
    wire.studyAttempts = Object.keys(profile.studyResults).sort().map(function(id) {
      var result = profile.studyResults[id];
      return {id: "result-" + id, questionId: id, outcome: result.outcome,
        attemptedAt: result.updatedAt, deviceId: result.deviceId, attemptCount: 1};
    });
    delete wire.studyResults;
    return wire;
  }

  function hasPersonalRecords(profile) {
    return Boolean(
      profile && (
        profile.notes.length ||
        Object.keys(profile.layout.records).length ||
        Object.keys(profile.studyResults).length ||
        profile.studyResets.length ||
        Object.keys(profile.readingProgress).length
      )
    );
  }

  function parseObject(storage, key) {
    if (!key) { return null; }
    try {
      var raw = storage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (err) {
      return null;
    }
  }

  function normalizeProfile(value, now) {
    if (!value || [1, SCHEMA_VERSION].indexOf(Number(value.schemaVersion)) === -1) { return null; }
    var profile = createEmptyProfile(now);
    profile.profileId = String(value.profileId || profile.profileId);
    profile.createdAt = iso(value.createdAt, now);
    profile.updatedAt = iso(value.updatedAt, profile.createdAt);
    profile.legacyMigratedAt = iso(value.legacyMigratedAt, "");
    profile.notes = Array.isArray(value.notes) ? value.notes.filter(function(note) {
      return note && note.id;
    }).map(clone) : [];
    if (value.layout && typeof value.layout === "object") {
      profile.layout.publishedRevision = String(value.layout.publishedRevision || "");
      profile.layout.records = value.layout.records && typeof value.layout.records === "object"
        ? clone(value.layout.records) : {};
    }
    var results = Number(value.schemaVersion) === 1
      ? (Array.isArray(value.studyAttempts) ? value.studyAttempts : [])
      : Object.keys(value.studyResults || {}).map(function(id) { return value.studyResults[id]; });
    results.forEach(function(item) {
      if (!item || !item.questionId || ["correct", "incorrect", "unknown"].indexOf(item.outcome) < 0) { return; }
      var updatedAt = iso(item.updatedAt || item.attemptedAt, "");
      if (!updatedAt) { return; }
      var result = {questionId: String(item.questionId), outcome: String(item.outcome),
        updatedAt: updatedAt, deviceId: String(item.deviceId || "")};
      var current = profile.studyResults[result.questionId];
      profile.studyResults[result.questionId] = current ? latestStudyResult(current, result) : result;
    });
    profile.studyResets = Array.isArray(value.studyResets)
      ? value.studyResets.filter(function(item) { return item && item.id; }).map(clone) : [];
    profile.readingProgress = value.readingProgress && typeof value.readingProgress === "object"
      ? clone(value.readingProgress) : {};
    pruneResetResults(profile);
    return profile;
  }

  function latestStudyResult(left, right) {
    var delta = Date.parse(left.updatedAt) - Date.parse(right.updatedAt);
    if (delta) { return delta > 0 ? left : right; }
    return (left.deviceId + ":" + left.outcome) >= (right.deviceId + ":" + right.outcome) ? left : right;
  }

  function resetTime(profile, questionId) {
    return profile.studyResets.reduce(function(latest, reset) {
      return reset.questionId === "*" || reset.questionId === questionId
        ? Math.max(latest, Date.parse(reset.resetAt) || 0) : latest;
    }, 0);
  }

  function pruneResetResults(profile) {
    Object.keys(profile.studyResults).forEach(function(id) {
      if (Date.parse(profile.studyResults[id].updatedAt) <= resetTime(profile, id)) {
        delete profile.studyResults[id];
      }
    });
  }

  function migrateLegacy(storage, keys, now, deviceId) {
    var profile = createEmptyProfile(now);
    profile.legacyMigratedAt = now;
    var notes = parseObject(storage, keys.userNotes);
    if (notes && Array.isArray(notes.notes)) {
      profile.notes = notes.notes.filter(function(note) { return note && note.id; }).map(function(note) {
        var result = clone(note);
        result.createdAt = iso(result.createdAt, now);
        result.updatedAt = iso(result.updatedAt || result.createdAt, now);
        result.deletedAt = "";
        return result;
      });
    }

    var layout = parseObject(storage, keys.globalLayout);
    if (layout && Number(layout.schema_version) === 1) {
      profile.layout.publishedRevision = String(layout.published_revision || "");
      Object.keys(layout.concepts || {}).forEach(function(id) {
        if (!validPosition(layout.concepts[id])) { return; }
        profile.layout.records["concept:" + id] = {
          objectType: "concept", objectId: id,
          x: Number(layout.concepts[id].x), y: Number(layout.concepts[id].y),
          updatedAt: now, deletedAt: "", deviceId: deviceId
        };
      });
      Object.keys(layout.modules || {}).forEach(function(id) {
        var position = layout.modules[id] && layout.modules[id].anchor;
        if (!validPosition(position)) { return; }
        profile.layout.records["module:" + id] = {
          objectType: "module", objectId: id,
          x: Number(position.x), y: Number(position.y),
          updatedAt: now, deletedAt: "", deviceId: deviceId
        };
      });
    }

    var study = parseObject(storage, keys.studyProgress);
    Object.keys(study && study.questions || {}).forEach(function(questionId) {
      var entry = study.questions[questionId] || {};
      var outcome = String(entry.lastOutcome || "");
      var attemptedAt = iso(entry.lastAttemptAt, "");
      if (!attemptedAt ||
          ["correct", "incorrect", "unknown"].indexOf(outcome) === -1) { return; }
      profile.studyResults[questionId] = {questionId: questionId, outcome: outcome,
        updatedAt: attemptedAt, deviceId: deviceId};
    });

    var reading = parseObject(storage, keys.contentReadProgress);
    Object.keys(reading && reading.blocks || {}).forEach(function(blockId) {
      if (reading.blocks[blockId] !== true) { return; }
      profile.readingProgress[blockId] = {
        blockId: blockId, isRead: true, updatedAt: now, deviceId: deviceId
      };
    });
    return profile;
  }

  function createStore(options) {
    options = options || {};
    var storage = options.storage || global.localStorage;
    var keys = options.storageKeys || {};
    var personalKey = keys.personalData || "srkg.personalData.v1";
    var deviceKey = keys.personalDataDevice || "srkg.personalData.device.v1";
    var now = new Date().toISOString();
    var deviceId = "";
    try { deviceId = String(storage.getItem(deviceKey) || ""); } catch (err) { deviceId = ""; }
    if (!deviceId) {
      deviceId = randomId("device-");
      try { storage.setItem(deviceKey, deviceId); } catch (err) { /* local-only fallback */ }
    }
    var stored = parseObject(storage, personalKey);
    var profile = normalizeProfile(stored, now);
    var migrated = Boolean(profile && Number(stored.studyResultsVersion) !== 2);
    if (!profile) {
      profile = migrateLegacy(storage, keys, now, deviceId);
      migrated = true;
    }

    function save() {
      profile.updatedAt = new Date().toISOString();
      try {
        storage.setItem(personalKey, JSON.stringify(compatibleProfile(profile)));
        return true;
      } catch (err) {
        return false;
      }
    }
    if (migrated) {
      save();
      // Retire counts in the old projection too, including unloaded questions.
      if (keys.studyProgress) {
        try { storage.setItem(keys.studyProgress, JSON.stringify(studyState())); }
        catch (err) { /* the canonical profile remains the source of truth */ }
      }
    }

    function activeNotes() {
      return profile.notes.filter(function(note) { return !note.deletedAt; }).map(clone);
    }

    function replaceNotes(notes) {
      var nowValue = new Date().toISOString();
      var incoming = {};
      (notes || []).forEach(function(note) {
        if (!note || !note.id) { return; }
        var copy = clone(note);
        copy.deletedAt = "";
        incoming[String(copy.id)] = copy;
      });
      profile.notes.forEach(function(note) {
        if (!note.deletedAt && !incoming[String(note.id)]) {
          note.updatedAt = nowValue;
          note.deletedAt = nowValue;
        }
      });
      Object.keys(incoming).forEach(function(id) {
        var index = profile.notes.findIndex(function(note) { return String(note.id) === id; });
        if (index === -1) { profile.notes.push(incoming[id]); }
        else { profile.notes[index] = incoming[id]; }
      });
      return save();
    }

    function layoutState() {
      var state = {
        schema_version: 1,
        published_revision: profile.layout.publishedRevision,
        concepts: {}, modules: {}
      };
      Object.keys(profile.layout.records).forEach(function(key) {
        var record = profile.layout.records[key];
        if (!record || record.deletedAt || !validPosition(record)) { return; }
        if (record.objectType === "concept") {
          state.concepts[record.objectId] = {x: Number(record.x), y: Number(record.y)};
        } else if (record.objectType === "module") {
          state.modules[record.objectId] = {anchor: {x: Number(record.x), y: Number(record.y)}};
        }
      });
      return state;
    }

    function replaceLayout(state) {
      state = state || {};
      var nowValue = new Date().toISOString();
      var incoming = {};
      Object.keys(state.concepts || {}).forEach(function(id) {
        if (!validPosition(state.concepts[id])) { return; }
        incoming["concept:" + id] = {
          objectType: "concept", objectId: id,
          x: Number(state.concepts[id].x), y: Number(state.concepts[id].y)
        };
      });
      Object.keys(state.modules || {}).forEach(function(id) {
        var position = state.modules[id] && state.modules[id].anchor;
        if (!validPosition(position)) { return; }
        incoming["module:" + id] = {
          objectType: "module", objectId: id, x: Number(position.x), y: Number(position.y)
        };
      });
      Object.keys(profile.layout.records).forEach(function(key) {
        var old = profile.layout.records[key];
        if (!incoming[key] && !old.deletedAt) {
          old.updatedAt = nowValue;
          old.deletedAt = nowValue;
          old.deviceId = deviceId;
        }
      });
      Object.keys(incoming).forEach(function(key) {
        var next = incoming[key];
        var old = profile.layout.records[key];
        if (!old || old.deletedAt || Number(old.x) !== next.x || Number(old.y) !== next.y) {
          next.updatedAt = nowValue;
          next.deletedAt = "";
          next.deviceId = deviceId;
          profile.layout.records[key] = next;
        }
      });
      profile.layout.publishedRevision = String(state.published_revision || "");
      return save();
    }

    function studyState(validQuestions) {
      var questions = {};
      Object.keys(profile.studyResults).forEach(function(id) {
        if (validQuestions && !validQuestions[id]) { return; }
        var result = profile.studyResults[id];
        questions[id] = {lastOutcome: result.outcome, lastAttemptAt: result.updatedAt};
      });
      return {version: 1, questions: questions};
    }

    function setStudyResult(questionId, outcome, updatedAt) {
      questionId = String(questionId);
      if (["correct", "incorrect", "unknown"].indexOf(outcome) < 0) { return false; }
      var result = {questionId: questionId, outcome: outcome,
        updatedAt: iso(updatedAt, new Date().toISOString()), deviceId: deviceId};
      // Local answers follow the observed result/reset even within one clock
      // tick. Imported records keep their original timestamps on merge.
      var current = profile.studyResults[questionId];
      result.updatedAt = new Date(Math.max(Date.parse(result.updatedAt),
        resetTime(profile, questionId) + 1,
        current ? Date.parse(current.updatedAt) + 1 : 0)).toISOString();
      profile.studyResults[questionId] = result;
      return save();
    }

    function resetStudy(questionId) {
      var resetAt = Date.now();
      Object.keys(profile.studyResults).forEach(function(id) {
        if (!questionId || String(questionId) === id) {
          resetAt = Math.max(resetAt, Date.parse(profile.studyResults[id].updatedAt));
        }
      });
      profile.studyResets.push({
        id: randomId("reset-"), questionId: questionId ? String(questionId) : "*",
        resetAt: new Date(resetAt + 1).toISOString(), deviceId: deviceId
      });
      pruneResetResults(profile);
      save();
    }

    function readingState(validBlocks) {
      var blocks = {};
      Object.keys(profile.readingProgress).forEach(function(blockId) {
        if (validBlocks && !validBlocks[blockId]) { return; }
        if (profile.readingProgress[blockId].isRead === true) { blocks[blockId] = true; }
      });
      return {version: 1, blocks: blocks};
    }

    function setRead(blockId, isRead) {
      profile.readingProgress[String(blockId)] = {
        blockId: String(blockId), isRead: isRead === true,
        updatedAt: new Date().toISOString(), deviceId: deviceId
      };
      return save();
    }

    function recordTimestamp(record) {
      return Date.parse(record && (record.deletedAt || record.updatedAt ||
        record.resetAt || record.attemptedAt)) || 0;
    }

    function recordTie(record) {
      return String(record && (record.deviceId || record.id || ""));
    }

    function newerRecord(left, right) {
      var leftTime = recordTimestamp(left);
      var rightTime = recordTimestamp(right);
      if (leftTime !== rightTime) { return leftTime > rightTime ? left : right; }
      return recordTie(left) >= recordTie(right) ? left : right;
    }

    function mergeById(current, incoming) {
      var byId = {};
      (current || []).concat(incoming || []).forEach(function(record) {
        if (!record || !record.id) { return; }
        var id = String(record.id);
        byId[id] = byId[id] ? clone(newerRecord(byId[id], record)) : clone(record);
      });
      return Object.keys(byId).sort().map(function(id) { return byId[id]; });
    }

    function mergeSnapshot(value) {
      var incoming = normalizeProfile(value, new Date().toISOString());
      if (!incoming) { return false; }
      var localWasEmpty = !hasPersonalRecords(profile);
      profile.notes = mergeById(profile.notes, incoming.notes);
      Object.keys(incoming.layout.records).forEach(function(key) {
        var current = profile.layout.records[key];
        profile.layout.records[key] = current
          ? clone(newerRecord(current, incoming.layout.records[key]))
          : clone(incoming.layout.records[key]);
      });
      if (incoming.layout.publishedRevision) {
        profile.layout.publishedRevision = incoming.layout.publishedRevision;
      }
      Object.keys(incoming.studyResults).forEach(function(id) {
        var current = profile.studyResults[id];
        profile.studyResults[id] = current
          ? latestStudyResult(current, incoming.studyResults[id]) : incoming.studyResults[id];
      });
      profile.studyResets = mergeById(profile.studyResets, incoming.studyResets);
      pruneResetResults(profile);
      Object.keys(incoming.readingProgress).forEach(function(blockId) {
        var current = profile.readingProgress[blockId];
        profile.readingProgress[blockId] = current
          ? clone(newerRecord(current, incoming.readingProgress[blockId]))
          : clone(incoming.readingProgress[blockId]);
      });
      if (localWasEmpty) {
        profile.profileId = incoming.profileId;
        profile.createdAt = incoming.createdAt;
      }
      return save();
    }

    function replaceSnapshot(value) {
      var incoming = normalizeProfile(value, new Date().toISOString());
      if (!incoming) { return false; }
      profile = incoming;
      return save();
    }

    return {
      schemaVersion: SCHEMA_VERSION,
      storageKey: personalKey,
      deviceId: deviceId,
      getSnapshot: function() { return clone(profile); },
      getNotes: activeNotes,
      replaceNotes: replaceNotes,
      getLayoutState: layoutState,
      replaceLayout: replaceLayout,
      getStudyState: studyState,
      setStudyResult: setStudyResult,
      addStudyAttempt: setStudyResult, // Compatibility API; stores no history.
      resetStudy: resetStudy,
      getReadingState: readingState,
      setRead: setRead,
      mergeSnapshot: mergeSnapshot,
      replaceSnapshot: replaceSnapshot
    };
  }

  global.kgNormalizePersonalDataProfile = normalizeProfile;
  global.kgCompatiblePersonalDataProfile = compatibleProfile;
  global.kgCreatePersonalDataStore = createStore;
})(window);
