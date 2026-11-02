/* Personal-data connection/import UI and sync scheduling; feature controllers apply merged state. */
function kgCreatePersonalDataController(options) {
  "use strict";
  var personalDataStore = options.store;
  var writePersonalLayoutNow = options.flushLayout;
  var pendingPersonalDataImport = null, googleDriveAuthorizer = null, personalDataSyncEngine = null;
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
        onStatus: function(status) { setCloudSyncStatus(status.detail); }
      });
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
    if (cloudSyncAutoTimer !== null) {
      clearTimeout(cloudSyncAutoTimer);
      cloudSyncAutoTimer = null;
    }
    writePersonalLayoutNow();
    return personalDataSyncEngine.synchronize().then(function() {
      cloudSyncLastSuccessfulAt = Date.now();
      options.onMerged();
      setCloudSyncStatus(
        "Personal data synced. Last synced at " +
        cloudSyncTimeText(cloudSyncLastSuccessfulAt) + "."
      );
      showCloudSyncAttention(false);
      return true;
    }).catch(function(error) {
      if (error && error.code === "auth_required") {
        clearCloudSyncTimers();
        showCloudSyncConnected(false, true);
        showCloudSyncAttention(true);
        personalDataSyncEngine = null;
        setCloudSyncStatus("Google sign-in expired. Connect again to sync.");
      }
      return false;
    });
  }

  function disconnectGoogleDrive() {
    clearCloudSyncTimers();
    personalDataSyncEngine = null;
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
      summary.study + " study attempt record" + (summary.study === 1 ? "" : "s"),
      summary.reading + " read mark" + (summary.reading === 1 ? "" : "s")
    ].join(", ");
  }

  function exportPersonalData() {
    writePersonalLayoutNow();
    var bytes = window.kgPersonalDataArchive.exportBytes(personalDataStore.getSnapshot());
    var blob = new Blob([bytes], {type: "application/zip"});
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "srkg-personal-data.zip";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setPersonalDataStatus("Personal data exported.");
  }

  function showPersonalDataImport(profile) {
    pendingPersonalDataImport = profile;
    var summary = window.kgPersonalDataArchive.summarize(profile);
    document.getElementById("kg_personal_data_import_summary").textContent =
      "This archive contains " + personalDataSummaryText(summary) + ".";
    var merge = document.querySelector(
      'input[name="kg_personal_import_mode"][value="merge"]'
    );
    if (merge) { merge.checked = true; }
    var dialog = document.getElementById("kg_personal_data_import_dialog");
    if (dialog.showModal) { dialog.showModal(); }
    else { dialog.setAttribute("open", ""); }
  }

  function closePersonalDataImport() {
    pendingPersonalDataImport = null;
    var dialog = document.getElementById("kg_personal_data_import_dialog");
    if (dialog.close) { dialog.close(); }
    else { dialog.removeAttribute("open"); }
  }

  function applyPersonalDataImport() {
    if (!pendingPersonalDataImport) { return; }
    var selected = document.querySelector(
      'input[name="kg_personal_import_mode"]:checked'
    );
    var mode = selected ? selected.value : "merge";
    if (mode === "replace" && !window.confirm(
      "Replace all personal data currently stored in this browser?"
    )) { return; }
    var succeeded = mode === "replace"
      ? personalDataStore.replaceSnapshot(pendingPersonalDataImport)
      : personalDataStore.mergeSnapshot(pendingPersonalDataImport);
    if (!succeeded) {
      setPersonalDataStatus("Could not save the imported personal data.");
      return;
    }
    try {
      window.sessionStorage.setItem(
        "srkg.personalData.importStatus",
        "Personal data " + (mode === "replace" ? "replaced" : "merged") + "."
      );
    } catch (err) { /* reload still applies the import */ }
    window.location.reload();
  }

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
