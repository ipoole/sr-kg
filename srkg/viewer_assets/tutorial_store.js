/* Independent personal-tutorial records; old viewers never write this database. */
function kgCreateTutorialStore(options) {
  "use strict";
  options = options || {};
  var database = null;
  function clone(value) { return value === undefined ? null : JSON.parse(JSON.stringify(value)); }
  function id(prefix) {
    return prefix + (window.crypto && crypto.randomUUID ? crypto.randomUUID() :
      Date.now().toString(36) + "-" + Math.random().toString(36).slice(2));
  }
  function open() {
    if (database) { return database; }
    database = new Promise(function(resolve, reject) {
      if (!window.indexedDB) { reject(new Error("Personal tutorial storage is unavailable.")); return; }
      var request = indexedDB.open(options.databaseName || "physicskg.tutorials", 1);
      request.onupgradeneeded = function() {
        request.result.createObjectStore("tutorials", {keyPath: "id"});
      };
      request.onerror = function() { reject(request.error); };
      request.onblocked = function() { reject(new Error("Close other tutorial editors and retry.")); };
      request.onsuccess = function() {
        var db = request.result;
        db.onversionchange = function() { db.close(); database = null; };
        resolve(db);
      };
    }).catch(function(error) { database = null; throw error; });
    return database;
  }
  function transaction(mode, operation) {
    return open().then(function(db) {
      return new Promise(function(resolve, reject) {
        var tx = db.transaction("tutorials", mode), result, failure;
        tx.oncomplete = function() { resolve(clone(result)); };
        tx.onabort = tx.onerror = function() { reject(failure || tx.error || new Error("Could not save tutorial.")); };
        operation(tx.objectStore("tutorials"), function(value) { result = value; }, function(error) {
          failure = error; tx.abort();
        });
      });
    });
  }
  function get(key) {
    return transaction("readonly", function(store, done) {
      store.get(key).onsuccess = function(event) { done(event.target.result); };
    });
  }
  function list() {
    return transaction("readonly", function(store, done) {
      store.getAll().onsuccess = function(event) {
        done(event.target.result.filter(function(record) { return !record.deletedAt; }));
      };
    });
  }
  function save(record) {
    record = clone(record);
    if (!record || typeof record.id !== "string" || record.id.indexOf("personal:") !== 0 ||
        !record.route || record.route.tutorial_id !== record.id || !Array.isArray(record.route.steps)) {
      return Promise.reject(new Error("Invalid personal tutorial record."));
    }
    return transaction("readwrite", function(store, done, fail) {
      store.get(record.id).onsuccess = function(event) {
        var previous = event.target.result;
        if (previous && previous.revisionId !== record.revisionId) {
          fail(new Error("This tutorial changed in another editor. Keep your text before reopening it."));
          return;
        }
        var now = new Date(Math.max(Date.now(), previous ? Date.parse(previous.updatedAt) + 1 : 0)).toISOString();
        record.createdAt = previous ? previous.createdAt : now;
        record.updatedAt = now;
        if (record.deletedAt) { record.deletedAt = now; }
        record.revisionId = id("revision:");
        store.put(record); done(record);
      };
    });
  }
  function create(route, basedOn) {
    var key = id("personal:");
    route = route ? clone(route) : {title: "New tutorial", summary: "", category: "physics",
      sequence: 0, domains: [], steps: [kgTutorialSequence.newCard(id("card:"))]};
    route.tutorial_id = key;
    return save({id: key, route: route, basedOn: clone(basedOn), deletedAt: ""});
  }
  function remove(key, revisionId) {
    return get(key).then(function(record) {
      if (!record) { return null; }
      if (revisionId && revisionId !== record.revisionId) {
        throw new Error("This tutorial changed in another editor. Reopen it before deleting.");
      }
      record.deletedAt = new Date().toISOString();
      return save(record);
    });
  }
  return {get: get, list: list, save: save, create: create, remove: remove};
}
