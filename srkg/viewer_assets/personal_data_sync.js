(function(global) {
  "use strict";

  function conflictError(message) {
    var error = new Error(message || "The cloud copy changed during synchronisation");
    error.code = "conflict";
    return error;
  }

  function createSyncEngine(options) {
    options = options || {};
    var store = options.store;
    var archive = options.archive;
    var provider = options.provider;
    var onStatus = typeof options.onStatus === "function" ? options.onStatus : function() {};
    var maxAttempts = Math.max(1, Number(options.maxAttempts) || 3);
    var activeSync = null;

    if (!store || !archive || !provider) {
      throw new Error("Personal-data sync needs a store, archive and provider");
    }

    function status(state, detail) {
      onStatus({state: state, detail: String(detail || "")});
    }

    async function run() {
      status("syncing", "Reading cloud data…");
      for (var attempt = 1; attempt <= maxAttempts; attempt += 1) {
        var remote = await provider.read();
        if (remote && remote.bytes) {
          var remoteProfile = archive.importBytes(remote.bytes);
          if (!store.mergeSnapshot(remoteProfile)) {
            throw new Error("Could not save merged personal data locally");
          }
        }

        var snapshot = store.getSnapshot();
        var bytes = archive.exportBytes(snapshot);
        try {
          var written = await provider.write(bytes, {
            revision: remote ? remote.revision : null,
            create: !remote,
            profileId: snapshot.profileId
          });
          var summary = archive.summarize(snapshot);
          status("synced", "Personal data synced.");
          return {
            profile: snapshot,
            summary: summary,
            remoteCreated: !remote,
            revision: written && written.revision ? written.revision : ""
          };
        } catch (error) {
          if (!error || error.code !== "conflict" || attempt === maxAttempts) {
            throw error;
          }
          status("syncing", "Cloud data changed; merging again…");
        }
      }
      throw conflictError();
    }

    function synchronize() {
      if (activeSync) { return activeSync; }
      activeSync = run().catch(function(error) {
        status("error", error && error.message ? error.message : "Cloud sync failed.");
        throw error;
      }).finally(function() {
        activeSync = null;
      });
      return activeSync;
    }

    return {
      synchronize: synchronize,
      isSynchronizing: function() { return Boolean(activeSync); }
    };
  }

  global.kgCreatePersonalDataSyncEngine = createSyncEngine;
  global.kgPersonalDataSyncConflictError = conflictError;
})(window);
