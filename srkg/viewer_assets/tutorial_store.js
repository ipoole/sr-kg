/* Independent tutorial records and sync baseline; old viewers never write this database. */
function kgCreateTutorialStore(options) {
  "use strict";
  options = options || {};
  var database = null;
  function clone(value) { return value === undefined ? null : JSON.parse(JSON.stringify(value)); }
  function id(prefix) {
    return prefix + (window.crypto && crypto.randomUUID ? crypto.randomUUID() :
      Date.now().toString(36) + '-' + Math.random().toString(36).slice(2));
  }
  function changed(origin) { window.dispatchEvent(new CustomEvent('kg:tutorials-changed', {detail:{origin:origin}})); }
  function open() {
    if (database) { return database; }
    database = new Promise(function(resolve, reject) {
      if (!window.indexedDB) { reject(new Error('Personal tutorial storage is unavailable.')); return; }
      var abandoned = false, request = indexedDB.open(options.databaseName || 'physicskg.tutorials', 3);
      request.onupgradeneeded = function() {
        var db = request.result;
        if (!db.objectStoreNames.contains('tutorials')) { db.createObjectStore('tutorials', {keyPath:'id'}); }
        if (!db.objectStoreNames.contains('audio')) { db.createObjectStore('audio', {keyPath:'id'}); }
        if (!db.objectStoreNames.contains('meta')) { db.createObjectStore('meta', {keyPath:'key'}); }
      };
      request.onerror = function() { reject(request.error); };
      request.onblocked = function() { abandoned = true; reject(new Error('Close other tutorial editors and retry.')); };
      request.onsuccess = function() {
        var db = request.result;
        if (abandoned) { db.close(); return; }
        db.onversionchange = function() { db.close(); database = null; };
        resolve(db);
      };
    }).catch(function(error) { database = null; throw error; });
    return database;
  }
  function transaction(names, mode, operation) {
    return open().then(function(db) {
      return new Promise(function(resolve, reject) {
        var tx = db.transaction(names, mode), result, failure;
        tx.oncomplete = function() { resolve(result); };
        tx.onabort = tx.onerror = function() { reject(failure || tx.error || new Error('Could not save tutorial.')); };
        function fail(error) { failure = error; tx.abort(); }
        try { operation(tx, function(value) { result = value; }, fail); }
        catch (error) { fail(error); }
      });
    });
  }
  function get(key) {
    return transaction(['tutorials'], 'readonly', function(tx, done) {
      tx.objectStore('tutorials').get(key).onsuccess = function(event) { done(event.target.result); };
    });
  }
  function snapshot() {
    return transaction(['tutorials','meta'], 'readonly', function(tx, done) {
      var result = {records:[], baseline:{}};
      tx.objectStore('tutorials').getAll().onsuccess = function(event) { result.records = event.target.result; done(result); };
      tx.objectStore('meta').get('cloudBaseline').onsuccess = function(event) {
        result.baseline = event.target.result ? event.target.result.value : {}; done(result);
      };
    });
  }
  function list() { return snapshot().then(function(value) { return value.records.filter(function(record) { return !record.deletedAt; }); }); }
  function validRecord(record) {
    return record && typeof record.id === 'string' && record.id.indexOf('personal:') === 0 &&
      record.route && record.route.tutorial_id === record.id && Array.isArray(record.route.steps);
  }
  function save(record, asset) {
    record = clone(record);
    if (!validRecord(record)) { return Promise.reject(new Error('Invalid personal tutorial record.')); }
    return transaction(['tutorials','audio'], 'readwrite', function(tx, done, fail) {
      var store = tx.objectStore('tutorials');
      store.get(record.id).onsuccess = function(event) {
        try {
          var previous = event.target.result;
          if (previous && previous.revisionId !== record.revisionId) {
            fail(new Error('This tutorial changed in another editor. Keep your text before reopening it.')); return;
          }
          var now = new Date(Math.max(Date.now(), previous ? Date.parse(previous.updatedAt) + 1 : 0)).toISOString();
          record.createdAt = previous ? previous.createdAt : now; record.updatedAt = now;
          if (record.deletedAt) { record.deletedAt = now; }
          record.revisionId = id('revision:');
          if (asset) { tx.objectStore('audio').put(asset); }
          (record.route.steps || []).forEach(function(step) {
            if (!step.audio) { return; }
            tx.objectStore('audio').get(step.audio.assetId).onsuccess = function(event) {
              if (!event.target.result) { fail(new Error('Voice asset is missing; recording was not saved.')); }
            };
          });
          store.put(record); done(record);
        } catch (error) { fail(error); }
      };
    }).then(function(result) { changed('edit'); return result; });
  }
  function commitSnapshot(records, baseline, expected, origin) {
    records = clone(records);
    if (!Array.isArray(records) || records.some(function(record) { return !validRecord(record); }) ||
        new Set(records.map(function(record) { return record.id; })).size !== records.length) {
      return Promise.reject(new Error('Invalid tutorial snapshot.'));
    }
    var revisions = {};
    expected.forEach(function(record) { revisions[record.id] = record.revisionId; });
    return transaction(['tutorials','meta'], 'readwrite', function(tx, done, fail) {
      var store = tx.objectStore('tutorials');
      store.getAll().onsuccess = function(event) {
        var current = event.target.result;
        if (current.length !== expected.length || current.some(function(record) { return revisions[record.id] !== record.revisionId; })) {
          var error = new Error('Tutorials changed while synchronising; retrying.'); error.code = 'conflict'; fail(error); return;
        }
        store.clear(); records.forEach(function(record) { store.put(record); });
        if (baseline !== null) { tx.objectStore('meta').put({key:'cloudBaseline', value:baseline}); }
        done(records);
      };
    }).then(function(result) { changed(origin || 'remote'); return result; });
  }
  function create(route, basedOn, metadata) {
    var key = id('personal:');
    route = route ? clone(route) : {title:'New tutorial', summary:'', category:'physics',
      sequence:0, domains:[], steps:[kgTutorialSequence.newCard(id('card:'))]};
    route.tutorial_id = key;
    return save(Object.assign({},metadata || {},{id:key, route:route, basedOn:clone(basedOn), deletedAt:''}));
  }
  function remove(key, revisionId) {
    return get(key).then(function(record) {
      if (!record) { return null; }
      if (revisionId && revisionId !== record.revisionId) { throw new Error('This tutorial changed in another editor. Reopen it before deleting.'); }
      record.deletedAt = new Date().toISOString(); return save(record);
    });
  }
  async function saveVoice(record, stepId, blob, duration, fingerprint) {
    if (!(blob instanceof Blob) || !blob.size || blob.size > 50 * 1024 * 1024 ||
        !/^audio\//.test(blob.type) || !Number.isFinite(duration) || duration <= 0) {
      throw new Error('Choose a non-empty audio recording of at most 50 MB.');
    }
    var bytes = await blob.arrayBuffer(), digest = await crypto.subtle.digest('SHA-256', bytes);
    var assetId = Array.from(new Uint8Array(digest)).map(function(byte) { return byte.toString(16).padStart(2,'0'); }).join('');
    record = clone(record);
    var step = record.route.steps.find(function(item) { return item.step_id === stepId; });
    if (!step) { throw new Error('This card no longer exists.'); }
    step.audio = {assetId:assetId, duration:duration, commentaryHash:await fingerprint(step.commentary || ''),
      actionsHash:await fingerprint(voiceActions(step))};
    return save(record, {id:assetId, mimeType:blob.type, byteLength:blob.size, blob:blob});
  }
  function voiceActions(step) {
    return {prepare:step.prepare || [], actions:step.actions || null, action:step.action || null,
      pointer:step.pointer || null, demonstrate:step.demonstrate !== false};
  }
  function getAudio(assetId) {
    return transaction(['audio'], 'readonly', function(tx, done) {
      tx.objectStore('audio').get(assetId).onsuccess = function(event) { done(event.target.result || null); };
    });
  }
  return {saveVoice:saveVoice, getAudio:getAudio, voiceActions:voiceActions, get:get, list:list, snapshot:snapshot, save:save, create:create, remove:remove, commitSnapshot:commitSnapshot};
}
