/* Personal-data connection/import UI and sync scheduling; feature controllers apply merged state. */
function kgCreatePersonalDataController(options) {
  "use strict";
  var personalDataStore = options.store;
  var writePersonalLayoutNow = options.flushLayout;
  var pendingPersonalDataImport = null, googleDriveAuthorizer = null, personalDataSyncEngine = null;
  var tutorialSyncEngine = null, synchronizing = null, importing = false;
  var cloudSyncAutoTimer = null, cloudSyncPeriodicTimer = null, cloudSyncLastSuccessfulAt = 0;
  var cloudSyncAutoDelayMs = 15000, cloudSyncPeriodicDelayMs = 5 * 60 * 1000;

  function onVisibilityChange() {
    if (document.visibilityState === "visible" && personalDataSyncEngine &&
        (!cloudSyncLastSuccessfulAt ||
         Date.now() - cloudSyncLastSuccessfulAt >= cloudSyncPeriodicDelayMs)) {
      syncPersonalDataNow();
    }
  }

  function setPersonalDataStatus(message) {
    var status = document.getElementById("kg_personal_data_status");
    if (status) { status.textContent = String(message || ""); }
  }

  function setCloudSyncStatus(message) {
    var status = document.getElementById("kg_cloud_sync_status");
    if (status) { status.textContent = String(message || ""); }
  }

  function showCloudSyncConnected(connected, paused) {
    var connect = document.getElementById("kg_cloud_sync_connect");
    connect.hidden = connected;
    connect.textContent = paused ? "Reconnect" : "Connect Google Drive";
    document.getElementById("kg_cloud_sync_now").hidden = !connected;
    document.getElementById("kg_cloud_sync_disconnect").hidden = !connected && !paused;
  }

  function showCloudSyncAttention(show) {
    document.getElementById("kg_cloud_sync_attention").hidden = !show;
  }

  function cloudSyncTimeText(timestamp) {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  function clearCloudSyncTimers() {
    if (cloudSyncAutoTimer !== null) {
      clearTimeout(cloudSyncAutoTimer);
      cloudSyncAutoTimer = null;
    }
    if (cloudSyncPeriodicTimer !== null) {
      clearInterval(cloudSyncPeriodicTimer);
      cloudSyncPeriodicTimer = null;
    }
  }

  function startCloudSyncPeriodicChecks() {
    if (cloudSyncPeriodicTimer !== null) { clearInterval(cloudSyncPeriodicTimer); }
    cloudSyncPeriodicTimer = setInterval(function() {
      if (document.visibilityState === "visible" && personalDataSyncEngine) {
        syncPersonalDataNow();
      }
    }, cloudSyncPeriodicDelayMs);
  }

  function schedulePersonalDataAutoSync(delayMs) {
    if (!personalDataSyncEngine) { return false; }
    if (cloudSyncAutoTimer !== null) { clearTimeout(cloudSyncAutoTimer); }
    var delay = Number.isFinite(Number(delayMs))
      ? Math.max(0, Number(delayMs))
      : cloudSyncAutoDelayMs;
    cloudSyncAutoTimer = setTimeout(function() {
      cloudSyncAutoTimer = null;
      syncPersonalDataNow();
    }, delay);
    return true;
  }

  function initialiseGoogleDriveSync() {
    var clientId = String(options.clientId() || "");
    var connect = document.getElementById("kg_cloud_sync_connect");
    if (!clientId) {
      connect.disabled = true;
      showCloudSyncAttention(false);
      setCloudSyncStatus("Not configured in this copy of PhysicsKG.");
      return;
    }
    connect.disabled = false;
    showCloudSyncAttention(false);
    googleDriveAuthorizer = window.kgCreateGoogleDriveAuthorizer({clientId: clientId});
    setCloudSyncStatus("Not connected. Personal data remains in this browser.");
  }

  function connectGoogleDrive() {
    if (!googleDriveAuthorizer) { return; }
    setCloudSyncStatus("Connecting to Google Drive…");
    return googleDriveAuthorizer.connect().then(function() {
      var provider = window.kgCreateGoogleDrivePersonalDataProvider({
        token: googleDriveAuthorizer.token
      });
      personalDataSyncEngine = window.kgCreatePersonalDataSyncEngine({
        store: personalDataStore,
        archive: window.kgPersonalDataArchive,
        provider: provider,
        onStatus: function(status) {
          setCloudSyncStatus(status.state === 'synced' ? 'Notes and progress synced; checking tutorials…' : status.detail);
        }
      });
      tutorialSyncEngine = kgCreateTutorialSync({portable:kgTutorialPortable,store:personalDataStore.tutorials,
        legacyProvider:window.kgCreateGoogleDrivePersonalDataProvider({token:googleDriveAuthorizer.token,
          fileName:'PhysicsKG tutorials.zip',allMatches:true}),
        provider:window.kgCreateGoogleDrivePersonalDataProvider({token:googleDriveAuthorizer.token,
          fileName:'PhysicsKG tutorial library v2.json',mimeType:'application/json',allMatches:true,appendOnly:true}),
        prepare:options.prepareTutorials,updated:options.tutorialsChanged});
      showCloudSyncConnected(true);
      showCloudSyncAttention(false);
      startCloudSyncPeriodicChecks();
      setCloudSyncStatus("Connected — syncing personal data…");
      return syncPersonalDataNow();
    }).catch(function(error) {
      setCloudSyncStatus(error && error.message || "Could not connect to Google Drive.");
    });
  }

  function syncPersonalDataNow() {
    if (!personalDataSyncEngine) { return Promise.resolve(false); }
    if (synchronizing) { return synchronizing; }
    if (cloudSyncAutoTimer !== null) { clearTimeout(cloudSyncAutoTimer); cloudSyncAutoTimer = null; }
    var engine = personalDataSyncEngine, tutorials = tutorialSyncEngine;
    synchronizing = (async function() {
      var legacyComplete = false;
      try {
        writePersonalLayoutNow(); await options.prepareTutorials();
        await engine.synchronize(); legacyComplete = true;
        if (engine !== personalDataSyncEngine) { return false; }
        options.onMerged();
        var result = await tutorials.synchronize();
        if (engine !== personalDataSyncEngine) { return false; }
        cloudSyncLastSuccessfulAt = Date.now(); showCloudSyncAttention(false);
        setCloudSyncStatus(result.pending ? 'Notes and progress synced; new tutorial edits are pending automatic sync.' :
          'Personal data synced. Last synced at ' + cloudSyncTimeText(cloudSyncLastSuccessfulAt) +
          (result.legacyChanged ? '. Changes from an older viewer were found and synced' : '') +
          (result.conflicts ? '. Tutorial conflicts were kept as separate copies.' : '.'));
        if (result.pending) { schedulePersonalDataAutoSync(1500); }
        return true;
      } catch (error) {
        if (engine !== personalDataSyncEngine) { return false; }
        setCloudSyncStatus((legacyComplete ? 'Notes, layouts and progress synced; tutorials are still pending. ' : 'Sync did not complete. ') + error.message);
        if (error && error.code === 'auth_required') {
          clearCloudSyncTimers(); showCloudSyncConnected(false,true); showCloudSyncAttention(true);
          personalDataSyncEngine = null; tutorialSyncEngine = null;
        }
        return false;
      }
    })().finally(function() { synchronizing = null; });
    return synchronizing;
  }

  function disconnectGoogleDrive() {
    clearCloudSyncTimers();
    personalDataSyncEngine = null; tutorialSyncEngine = null;
    cloudSyncLastSuccessfulAt = 0;
    showCloudSyncConnected(false);
    showCloudSyncAttention(false);
    setCloudSyncStatus("Disconnected. Personal data remains in this browser and Google Drive.");
    if (googleDriveAuthorizer) { googleDriveAuthorizer.disconnect(); }
  }

  function personalDataSummaryText(summary) {
    return [
      summary.notes + " note" + (summary.notes === 1 ? "" : "s"),
      summary.layout + " personal layout position" + (summary.layout === 1 ? "" : "s"),
      summary.study + " question result" + (summary.study === 1 ? "" : "s"),
      summary.reading + " read mark" + (summary.reading === 1 ? "" : "s")
    ].join(", ");
  }

  async function exportPersonalData() {
    try {
      writePersonalLayoutNow(); await options.prepareTutorials();
      var records, warning = '';
      try { records = (await personalDataStore.tutorials.snapshot()).records; }
      catch (error) { warning = 'Notes, layouts and progress exported; tutorial storage was unavailable, so tutorials are not included.'; }
      var bytes = window.kgPersonalDataArchive.exportBytes(personalDataStore.getSnapshot(),records);
      var url = URL.createObjectURL(new Blob([bytes],{type:'application/zip'})), link = document.createElement('a');
      link.href = url; link.download = 'srkg-personal-data.zip'; document.body.appendChild(link); link.click(); link.remove();
      setTimeout(function() { URL.revokeObjectURL(url); },1000);
      setPersonalDataStatus(warning || 'Personal data, including tutorials, exported.');
    } catch (error) { setPersonalDataStatus('Could not export personal data: ' + error.message); }
  }

  function showPersonalDataImport(bundle) {
    if (importing) { return; }
    if (!bundle.profile) { bundle = {profile:bundle,tutorials:null}; }
    pendingPersonalDataImport = bundle;
    document.getElementById('kg_personal_data_import_status').textContent = '';
    var summary = window.kgPersonalDataArchive.summarize(bundle.profile);
    document.getElementById("kg_personal_data_import_summary").textContent =
      "This archive contains " + personalDataSummaryText(summary) +
      (bundle.tutorials === null ? '. Tutorials are not included; existing tutorials will be retained.' :
        ', ' + bundle.tutorials.filter(function(record) { return !record.deletedAt; }).length + ' tutorials.');
    var merge = document.querySelector(
      'input[name="kg_personal_import_mode"][value="merge"]'
    );
    if (merge) { merge.checked = true; }
    var dialog = document.getElementById("kg_personal_data_import_dialog");
    if (dialog.showModal) { dialog.showModal(); }
    else { dialog.setAttribute("open", ""); }
  }

  function closePersonalDataImport() {
    if (importing) { return; }
    pendingPersonalDataImport = null;
    var dialog = document.getElementById("kg_personal_data_import_dialog");
    if (dialog.close) { dialog.close(); }
    else { dialog.removeAttribute("open"); }
  }

  async function applyPersonalDataImport() {
    if (importing || !pendingPersonalDataImport) { return; }
    var mode = document.querySelector('input[name="kg_personal_import_mode"]:checked').value;
    if (mode === 'replace' && !window.confirm('Replace all personal data currently stored in this browser?')) { return; }
    var bundle = pendingPersonalDataImport, beforeProfile = personalDataStore.getSnapshot(), writtenProfile = null;
    var apply = document.getElementById('kg_personal_data_import_apply');
    var cancel = document.getElementById('kg_personal_data_import_cancel');
    importing = true; apply.disabled = cancel.disabled = true;
    document.getElementById('kg_personal_data_import_status').textContent = 'Importing…';
    function failed(message) {
      setPersonalDataStatus(message);
      document.getElementById('kg_personal_data_import_status').textContent = message;
    }
    try {
      await options.prepareTutorials();
      var beforeTutorials = bundle.tutorials === null ? null : await personalDataStore.tutorials.snapshot();
      var merged = null;
      if (beforeTutorials) {
        if (mode === 'merge') {
          merged = await kgCreateTutorialSync({portable:kgTutorialPortable}).merge(beforeTutorials.records,bundle.tutorials,{});
        } else {
          var imported = new Set(bundle.tutorials.map(function(record) { return record.id; }));
          var now = new Date().toISOString();
          var deleted = beforeTutorials.records.filter(function(record) { return !imported.has(record.id); }).map(function(record) {
            record = kgTutorialPortable.clone(record); record.deletedAt = now; record.updatedAt = now;
            record.revisionId = 'revision:' + (window.crypto && crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2)); return record;
          });
          merged = {records:bundle.tutorials.concat(deleted),relocations:{}};
        }
      }
      var success = mode === 'replace' ? personalDataStore.replaceSnapshot(bundle.profile) : personalDataStore.mergeSnapshot(bundle.profile);
      if (!success) { throw new Error('Could not save the imported personal data.'); }
      writtenProfile = personalDataStore.getSnapshot();
      if (merged) { await personalDataStore.tutorials.commitSnapshot(merged.records,null,beforeTutorials.records,'import'); }
      try { sessionStorage.setItem('srkg.personalData.importStatus','Personal data ' + (mode === 'replace' ? 'replaced' : 'merged') + '.'); }
      catch (error) { /* The data has already been saved. */ }
      window.location.reload();
    } catch (error) {
      if (writtenProfile && JSON.stringify(personalDataStore.getSnapshot()) !== JSON.stringify(writtenProfile)) {
        failed('Import partly completed: profile data changed during import and has been retained; tutorials were not imported. Export your data before retrying.'); return;
      }
      if (writtenProfile && JSON.stringify(personalDataStore.getSnapshot()) === JSON.stringify(writtenProfile)) {
        if (!personalDataStore.replaceSnapshot(beforeProfile)) { failed('Import partly completed; profile rollback failed. Export your data before retrying.'); return; }
      }
      failed('Import did not complete: ' + error.message);
    } finally { importing = false; apply.disabled = cancel.disabled = false; }
  }

  document.getElementById('kg_personal_data_import_dialog').addEventListener('cancel',function(event) {
    if (importing) { event.preventDefault(); }
    else { closePersonalDataImport(); }
  });

  return {
    onVisibilityChange: onVisibilityChange,
    setPersonalDataStatus: setPersonalDataStatus,
    schedulePersonalDataAutoSync: schedulePersonalDataAutoSync,
    initialiseGoogleDriveSync: initialiseGoogleDriveSync,
    connectGoogleDrive: connectGoogleDrive,
    syncPersonalDataNow: syncPersonalDataNow,
    disconnectGoogleDrive: disconnectGoogleDrive,
    exportPersonalData: exportPersonalData,
    showPersonalDataImport: showPersonalDataImport,
    closePersonalDataImport: closePersonalDataImport,
    applyPersonalDataImport: applyPersonalDataImport
  };
}
