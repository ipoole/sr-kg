/* Published/personal layout ownership; temporary graph arrangements never enter this store. */
function kgCreateGlobalLayout(options) {
  "use strict";
  var publishedLayout = options.publishedLayout;
  var nodes = options.nodes;
  var personalDataStore = options.store;
  var globalLayoutStorageKey = options.storageKey;
  var safeLocalStorageSet = options.storage.set;
  var safeLocalStorageRemove = options.storage.remove;
  var updateLayoutControls = options.onStatusChange;
  var schedulePersonalDataAutoSync = options.onSave;
  var resetContextFitInteraction = options.beforeReset;
  var validLayoutPosition = kgLayoutGeometry.validLayoutPosition;
  var copyLayoutPosition = kgLayoutGeometry.copyLayoutPosition;
  var personalLayoutState = loadPersonalLayoutState();
  var globalLayout = buildInitialGlobalLayout();
  var personalLayoutSaveTimer = null;

  function reload() {
    personalLayoutState = loadPersonalLayoutState();
    globalLayout = buildInitialGlobalLayout();
  }

  function buildInitialGlobalLayout(includePersonal) {
    includePersonal = includePersonal !== false;
    var publishedConcepts = publishedLayout && publishedLayout.concepts
      ? publishedLayout.concepts
      : {};
    var publishedModules = publishedLayout && publishedLayout.modules
      ? publishedLayout.modules
      : {};
    var layout = {
      schema_version: Number(publishedLayout && publishedLayout.schema_version) || 1,
      revision: String(publishedLayout && publishedLayout.revision || "unpublished"),
      concepts: {},
      modules: {}
    };
    options.getNodes().forEach(function(node) {
      var position = publishedConcepts[String(node.id)];
      if (!validLayoutPosition(position)) {
        position = node;
      }
      if (validLayoutPosition(position)) {
        layout.concepts[String(node.id)] = copyLayoutPosition(position);
      }
    });
    Object.keys(publishedModules).forEach(function(moduleId) {
      var entry = publishedModules[moduleId] || {};
      if (validLayoutPosition(entry.anchor)) {
        layout.modules[String(moduleId)] = {
          anchor: copyLayoutPosition(entry.anchor)
        };
      }
    });
    if (includePersonal && personalLayoutState) {
      Object.keys(personalLayoutState.concepts || {}).forEach(function(conceptId) {
        var position = personalLayoutState.concepts[conceptId];
        if (layout.concepts[conceptId] && validLayoutPosition(position)) {
          layout.concepts[conceptId] = copyLayoutPosition(position);
        }
      });
      Object.keys(personalLayoutState.modules || {}).forEach(function(moduleId) {
        var entry = personalLayoutState.modules[moduleId] || {};
        if (layout.modules[moduleId] && validLayoutPosition(entry.anchor)) {
          layout.modules[moduleId] = {anchor: copyLayoutPosition(entry.anchor)};
        }
      });
    }
    return layout;
  }

  function globalConceptPosition(conceptId) {
    return globalLayout.concepts[String(conceptId)] || null;
  }

  function effectiveConceptPosition(conceptId) {
    return globalConceptPosition(conceptId);
  }

  function setGlobalConceptPosition(conceptId, position) {
    if (!validLayoutPosition(position)) { return; }
    globalLayout.concepts[String(conceptId)] = copyLayoutPosition(position);
    schedulePersonalLayoutSave();
  }

  function setGlobalModuleAnchor(moduleId, position) {
    if (!validLayoutPosition(position)) { return; }
    globalLayout.modules[String(moduleId)] = {
      anchor: copyLayoutPosition(position)
    };
    schedulePersonalLayoutSave();
  }

  function globalModuleAnchor(moduleId) {
    var entry = globalLayout.modules[String(moduleId)] || {};
    return validLayoutPosition(entry.anchor) ? entry.anchor : null;
  }

  function effectiveModuleAnchor(moduleId) {
    return globalModuleAnchor(moduleId);
  }

  function globalLayoutSnapshot() {
    return JSON.parse(JSON.stringify(globalLayout));
  }

  function positionsEqual(a, b) {
    return validLayoutPosition(a) && validLayoutPosition(b) &&
      Math.abs(Number(a.x) - Number(b.x)) < 0.000001 &&
      Math.abs(Number(a.y) - Number(b.y)) < 0.000001;
  }

  function loadPersonalLayoutState() {
    var parsed = personalDataStore.getLayoutState();
    if (!parsed || Object.keys(parsed.concepts).length === 0 &&
        Object.keys(parsed.modules).length === 0) { return null; }
    return parsed;
  }

  function personalLayoutOverrides() {
    var concepts = {};
    var modules = {};
    Object.keys(globalLayout.concepts).forEach(function(conceptId) {
      var current = globalLayout.concepts[conceptId];
      var published = publishedLayout.concepts && publishedLayout.concepts[conceptId];
      if (!positionsEqual(current, published)) {
        concepts[conceptId] = copyLayoutPosition(current);
      }
    });
    Object.keys(globalLayout.modules).forEach(function(moduleId) {
      var current = globalLayout.modules[moduleId].anchor;
      var publishedEntry = publishedLayout.modules && publishedLayout.modules[moduleId] || {};
      if (!positionsEqual(current, publishedEntry.anchor)) {
        modules[moduleId] = {anchor: copyLayoutPosition(current)};
      }
    });
    return {concepts: concepts, modules: modules};
  }

  function writePersonalLayoutNow() {
    if (!globalLayoutStorageKey) { return; }
    var overrides = personalLayoutOverrides();
    if (Object.keys(overrides.concepts).length === 0 && Object.keys(overrides.modules).length === 0) {
      personalLayoutState = null;
      personalDataStore.replaceLayout({
        schema_version: 1,
        published_revision: String(publishedLayout.revision),
        concepts: {}, modules: {}
      });
      safeLocalStorageRemove(globalLayoutStorageKey);
      updateLayoutControls();
      return;
    }
    personalLayoutState = {
      schema_version: 1,
      published_revision: personalLayoutState && personalLayoutState.published_revision
        ? String(personalLayoutState.published_revision)
        : String(publishedLayout.revision),
      concepts: overrides.concepts,
      modules: overrides.modules
    };
    personalDataStore.replaceLayout(personalLayoutState);
    safeLocalStorageSet(globalLayoutStorageKey, JSON.stringify(personalLayoutState));
    updateLayoutControls();
  }

  function schedulePersonalLayoutSave() {
    if (!globalLayout || !globalLayoutStorageKey) { return; }
    if (personalLayoutSaveTimer !== null) {
      clearTimeout(personalLayoutSaveTimer);
    }
    personalLayoutSaveTimer = setTimeout(function() {
      personalLayoutSaveTimer = null;
      writePersonalLayoutNow();
      schedulePersonalDataAutoSync();
    }, 120);
  }

  function personalLayoutStatus() {
    var overrides = personalLayoutOverrides();
    var hasOverrides = Object.keys(overrides.concepts).length > 0 ||
      Object.keys(overrides.modules).length > 0;
    var savedRevision = personalLayoutState && personalLayoutState.published_revision
      ? String(personalLayoutState.published_revision)
      : String(publishedLayout.revision);
    return {
      hasOverrides: hasOverrides,
      publishedRevision: String(publishedLayout.revision),
      savedRevision: savedRevision,
      revisionMismatch: hasOverrides && savedRevision !== String(publishedLayout.revision)
    };
  }

  function keepPersonalLayout() {
    if (!personalLayoutStatus().hasOverrides) { return; }
    personalLayoutState.published_revision = String(publishedLayout.revision);
    writePersonalLayoutNow();
    schedulePersonalDataAutoSync();
    updateLayoutControls();
  }

  function applyGlobalLayoutPositions() {
    nodes.update(Object.keys(globalLayout.concepts).filter(function(id) {
      return Boolean(nodes.get(id));
    }).map(function(id) {
      var position = globalLayout.concepts[id];
      return {id: id, x: position.x, y: position.y};
    }));
    options.onPositionsApplied();
  }

  function resetToPublishedLayout() {
    resetContextFitInteraction({restore: false});
    if (personalLayoutSaveTimer !== null) {
      clearTimeout(personalLayoutSaveTimer);
      personalLayoutSaveTimer = null;
    }
    personalLayoutState = null;
    personalDataStore.replaceLayout({
      schema_version: 1,
      published_revision: String(publishedLayout.revision),
      concepts: {}, modules: {}
    });
    safeLocalStorageRemove(globalLayoutStorageKey);
    globalLayout = buildInitialGlobalLayout(false);
    applyGlobalLayoutPositions();
    schedulePersonalDataAutoSync();
    updateLayoutControls();
  }

  function normalizedExportCoordinate(value) {
    return Number(Number(value).toFixed(6));
  }

  function exportedGlobalLayout() {
    var concepts = {};
    var modules = {};
    Object.keys(globalLayout.concepts).sort().forEach(function(conceptId) {
      var position = globalLayout.concepts[conceptId];
      concepts[conceptId] = {
        x: normalizedExportCoordinate(position.x),
        y: normalizedExportCoordinate(position.y)
      };
    });
    Object.keys(globalLayout.modules).sort().forEach(function(moduleId) {
      var anchor = globalLayout.modules[moduleId].anchor;
      modules[moduleId] = {anchor: {
        x: normalizedExportCoordinate(anchor.x),
        y: normalizedExportCoordinate(anchor.y)
      }};
    });
    return {
      schema_version: Number(publishedLayout.schema_version) || 1,
      revision: String(publishedLayout.revision),
      concepts: concepts,
      modules: modules
    };
  }

  function exportGlobalLayout() {
    var text = JSON.stringify(exportedGlobalLayout(), null, 2) + "\n";
    var blob = new Blob([text], {type: "application/json;charset=utf-8"});
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "layout.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  return {
    effectiveConceptPosition: effectiveConceptPosition,
    setGlobalConceptPosition: setGlobalConceptPosition,
    setGlobalModuleAnchor: setGlobalModuleAnchor,
    globalModuleAnchor: globalModuleAnchor,
    effectiveModuleAnchor: effectiveModuleAnchor,
    globalLayoutSnapshot: globalLayoutSnapshot,
    writePersonalLayoutNow: writePersonalLayoutNow,
    personalLayoutStatus: personalLayoutStatus,
    keepPersonalLayout: keepPersonalLayout,
    applyGlobalLayoutPositions: applyGlobalLayoutPositions,
    resetToPublishedLayout: resetToPublishedLayout,
    exportedGlobalLayout: exportedGlobalLayout,
    exportGlobalLayout: exportGlobalLayout,
    reload: reload
  };
}
