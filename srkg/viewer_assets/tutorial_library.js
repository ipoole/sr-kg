/* Personal tutorial library, autosave and card-editor orchestration. */
function kgCreateTutorialLibrary(options) {
  "use strict";
  var store = options.store, escape = options.markup.escapeHtml;
  var records = new Map(), editing = null, cardIndex = 0, edited = 0, saved = 0;
  var saveTimer = null, pendingSave = null, returningToEditor = false, busy = false;
  var model = options.model, portable = options.portable, reconciliation = null;
  var dialog = document.getElementById("kg_tutorial_editor");
  function element(id) { return document.getElementById("kg_tutorial_" + id); }
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  var problems = model.routeProblems;
  function routeById(id) { var record = records.get(id); return record ? record.route : null; }
  function status(state, text) {
    element("editor_status").dataset.state = state;
    element("editor_status").textContent = text;
    if (options.recorder) { options.recorder.saveStatus(text); }
    element("editor_retry").hidden = state !== "error";
  }
  function updatePlay() {
    var errors = editing ? problems(editing.route) : [];
    element("editor_play").disabled = busy || Boolean(errors.length);
    element("editor_export").disabled = element("editor_json").disabled = busy;
    var canRecord = !options.canRecord || options.canRecord();
    element("editor_record").disabled = busy || !editing || !editing.route.steps.length || !canRecord;
    element("editor_record").title = canRecord ? '' : 'Exit the playing tutorial before recording.';
    element("editor_from").disabled = busy || Boolean(errors.length);
    element("editor_preview").disabled = busy || !editing || Boolean(problems(editing.route, {singleStep:true, startIndex:cardIndex}).length);
    element("editor_validation").textContent = errors.join(" ");
  }
  function renderList() {
    var items = Array.from(records.values()).sort(function(a, b) { return b.updatedAt.localeCompare(a.updatedAt); });
    element("personal_list").innerHTML = items.length ? items.map(function(record) {
      var route = record.route;
      return '<button type="button" class="kg-tutorial-select" data-tutorial-id="' + escape(record.id) +
        '" aria-current="false"><span class="kg-tutorial-list-title">' + escape(route.title || "Untitled tutorial") +
        '</span><span class="kg-tutorial-list-summary">' +
        (record.conflictOf ? "Conflict copy · " : "") + (problems(route).length ? "Draft · " : "") + route.steps.length +
        (route.steps.length === 1 ? ' card' : ' cards') + '</span></button>';
    }).join("") : '<p class="kg-muted-label">No personal tutorials yet.</p>';
  }
  async function refresh() {
    var list = await store.list();
    records = new Map(list.map(function(record) { return [record.id, record]; }));
    renderList();
  }
  async function initialise() {
    element("new").disabled = element("import").disabled = true;
    try {
      await refresh();
      element("library_status").textContent = "Tutorials save in this browser. Export to share; Personal data includes backup and optional Google Drive sync.";
      element("library_status").dataset.ready = "true";
      element("new").disabled = element("import").disabled = false;
      element("library_retry").hidden = true;
      if (options.selectedId()) { options.select(options.selectedId()); }
    } catch (error) {
      element("library_status").textContent = "Personal tutorials unavailable: " + error.message;
      element("library_retry").hidden = false;
    }
  }
  function showIntroduction(route) {
    var personal = records.has(route.tutorial_id);
    element("intro_copy").hidden = element("new").disabled;
    element("intro_copy").textContent = personal ? "Duplicate" : "Make editable copy";
    element("intro_edit").hidden = element("intro_delete").hidden = !personal;
    var errors = problems(route);
    element("start").disabled = Boolean(errors.length);
    element("launch_link").hidden = Boolean(errors.length);
    element("intro_author").textContent = route.author ? "By " + route.author : "";
    element("intro_author").hidden = !route.author;
    element("intro_status").textContent = errors.join(" ");
  }
  var actionEditor = kgCreateTutorialActionEditor({root:element("editor_actions"), model:model,
    changed:function(items) { model.setActions(editing.route.steps[cardIndex], items); markChanged(); }});
  var setupEditor = kgCreateTutorialActionEditor({root:element("editor_setup"), model:model, silent:true,
    changed:function(items) {
      if (items.length) { editing.route.steps[cardIndex].prepare = items; }
      else { delete editing.route.steps[cardIndex].prepare; }
      markChanged();
    }});
  function renderCardList() {
    element("editor_card").replaceChildren(); element("editor_order").replaceChildren();
    editing.route.steps.forEach(function(step, index) {
      element("editor_card").add(new Option((index + 1) + ". " + step.title, index));
      var item = document.createElement('li'); item.textContent = (index + 1) + '. ' + step.title;
      item.draggable = true; item.dataset.cardId = step.step_id;
      element("editor_order").appendChild(item);
    });
    element("editor_card").value = cardIndex;
  }
  function renderCard() {
    var step = editing.route.steps[cardIndex];
    element("editor_card_title").value = step ? step.title : "";
    element("editor_commentary").value = step ? step.commentary : "";
    ["editor_card_title", "editor_commentary", "editor_card"].forEach(function(key) { element(key).disabled = !step; });
    element("editor_action_section").hidden = element("editor_setup_section").hidden = !step;
    element("editor_card_controls").querySelectorAll('button').forEach(function(button) {
      var action = button.dataset.cardAction;
      button.disabled = action !== 'add' && (!step || (action === 'up' && cardIndex === 0) ||
        (action === 'down' && cardIndex === editing.route.steps.length - 1));
    });
    actionEditor.show(step ? model.actions(step) : []); setupEditor.show(step ? step.prepare || [] : []);
    updatePlay();
  }
  function moveCard(from, to) {
    var steps = editing.route.steps, selectedId = steps[cardIndex].step_id;
    steps.splice(to, 0, steps.splice(from, 1)[0]);
    cardIndex = steps.findIndex(function(step) { return step.step_id === selectedId; });
    markChanged(); renderCardList(); renderCard();
  }
  function showEditor() {
    if (!dialog.open) { dialog.showModal(); }
  }
  function openEditor(record) {
    editing = clone(record); edited = saved = 0; cardIndex = 0;
    dialog.dataset.tutorialId = record.id;
    element("editor_heading").textContent = record.conflictOf ? "Edit tutorial — conflict copy" : "Edit tutorial";
    element("editor_title").value = editing.route.title;
    element("editor_summary").value = editing.route.summary;
    element("editor_author").value = editing.route.author || "";
    element("editor_domains").value = (editing.route.domains || []).join(", ");
    renderCardList();
    renderCard(); updatePlay(); status("saved", "Saved in this browser."); showEditor();
    element("editor_title").focus();
  }
  function saveFailed(error) { status("error", "Not saved: " + error.message); }
  async function flush() {
    if (reconciliation) { await reconciliation; }
    if (saveTimer !== null) { clearTimeout(saveTimer); saveTimer = null; }
    if (pendingSave) { await pendingSave; return flush(); }
    if (!editing || edited === saved) { return; }
    var serial = edited, snapshot = clone(editing);
    status("saving", "Saving…");
    pendingSave = store.save(snapshot);
    try {
      var record = await pendingSave;
      editing.revisionId = record.revisionId;
      editing.createdAt = record.createdAt; editing.updatedAt = record.updatedAt;
      records.set(record.id, record); saved = serial; renderList();
    } catch (error) { saveFailed(error); throw error; }
    finally { pendingSave = null; }
    if (edited !== saved) { return flush(); }
    status("saved", "Saved in this browser.");
  }
  function changed() {
    if (!editing) { return; }
    editing.route.title = element("editor_title").value;
    editing.route.summary = element("editor_summary").value;
    editing.route.author = element("editor_author").value;
    editing.route.domains = element("editor_domains").value.split(/[,\s]+/).filter(Boolean);
    var step = editing.route.steps[cardIndex];
    if (step) {
      step.title = element("editor_card_title").value;
      step.commentary = element("editor_commentary").value;
      element("editor_card").options[cardIndex].textContent = (cardIndex + 1) + ". " + step.title;
    }
    element("editor_order").querySelectorAll('li').forEach(function(item, index) {
      item.textContent = (index + 1) + '. ' + editing.route.steps[index].title;
    });
    markChanged();
  }
  function markChanged() {
    edited += 1; updatePlay(); status("saving", "Saving…");
    if (saveTimer !== null) { clearTimeout(saveTimer); }
    saveTimer = setTimeout(function() { flush().catch(function() {}); }, 250);
  }
  async function closeEditor() {
    if (busy) { return; }
    setBusy(true);
    try {
      await flush(); dialog.close();
      options.select(editing.id); editing = null;
    } catch (error) { saveFailed(error); }
    finally { setBusy(false); }
  }
  async function create(route) {
    element("new").disabled = element("intro_copy").disabled = true;
    try {
      var basedOn = route ? {tutorialId: route.tutorial_id, version: options.version} : null;
      if (route) { route = clone(route); route.title += " (copy)"; }
      var record = await store.create(route, basedOn);
      records.set(record.id, record); renderList(); openEditor(record);
    } catch (error) { element("library_status").textContent = "Could not create tutorial: " + error.message; }
    finally { element("new").disabled = element("intro_copy").disabled = false; }
  }
  function setBusy(value) {
    busy = value; element("editor_fields").disabled = value;
    element("editor_close").disabled = value; updatePlay();
  }
  async function playEditor(mode) {
    var playOptions = {startIndex:mode === 'all' ? 0 : cardIndex, singleStep:mode === 'preview'};
    if (busy || !editing || problems(editing.route, playOptions).length) { return; }
    setBusy(true);
    try {
      await flush(); dialog.close(); returningToEditor = true;
      var started = await options.play(editing.id, playOptions);
      if (!started) { returningToEditor = false; showEditor(); element("editor_validation").textContent = "Could not start this tutorial."; }
    } catch (error) { returningToEditor = false; showEditor(); element("editor_validation").textContent = error.message; }
    finally { setBusy(false); }
  }
  function playbackExited() {
    if (returningToEditor) { returningToEditor = false; setBusy(false); showEditor(); element("editor_preview").focus(); }
  }
  async function recordActions() {
    if (busy || !editing || !editing.route.steps.length || (options.canRecord && !options.canRecord())) { return; }
    setBusy(true);
    try {
      // A portable semantic baseline, once per route, rather than saved device coordinates.
      var first = editing.route.steps[0];
      first.prepare = first.prepare || [];
      if (!first.prepare.length || first.prepare[0].command !== 'home') {
        first.prepare.unshift({command:'home'}); markChanged();
      }
      await flush(); dialog.close();
      await options.recorder.start(clone(editing.route), cardIndex);
    } catch (error) { showEditor(); element("editor_validation").textContent = 'Could not record: ' + error.message; }
    finally { setBusy(false); }
  }
  function recordingChanged(items) {
    model.setActions(editing.route.steps[cardIndex], items); markChanged();
  }
  async function recordingStopped() {
    renderCard(); showEditor(); element("editor_record").focus();
    try { await flush(); } catch (error) { saveFailed(error); }
  }
  function download(bytes, name, type) {
    var url = URL.createObjectURL(new Blob([bytes],{type:type})), link = document.createElement('a');
    link.href = url; link.download = name; document.body.appendChild(link); link.click(); link.remove();
    setTimeout(function() { URL.revokeObjectURL(url); },1000);
  }
  async function exportTutorial(asJson) {
    try {
      var saveError = '';
      try { await flush(); } catch (error) { if (!editing) { throw error; } saveError = ' Local save still needs Retry.'; }
      var source = editing || records.get(selected());
      if (!source) {
        var route = options.routeById(selected()), now = new Date().toISOString();
        source = {id:route.tutorial_id,route:route,basedOn:{tutorialId:route.tutorial_id,version:options.version},
          revisionId:'builtin:' + options.version,createdAt:now,updatedAt:now,deletedAt:''};
      }
      var name = (source.route.title || 'tutorial').replace(/[^a-zA-Z0-9_-]+/g,'-').slice(0,80);
      download(portable.exportSingle(source,asJson),name + (asJson ? '.json' : '.zip'),asJson ? 'application/json' : 'application/zip');
      if (editing) { element('editor_validation').textContent = 'Tutorial exported.' + saveError; }
      else { element('library_status').textContent = 'Tutorial exported.'; }
    } catch (error) {
      element(editing ? 'editor_validation' : 'library_status').textContent = 'Could not export: ' + error.message;
    }
  }
  element('intro_export').addEventListener('click',function() { exportTutorial(false); });
  element('editor_export').addEventListener('click',function() { exportTutorial(false); });
  element('editor_json').addEventListener('click',function() { exportTutorial(true); });
  element('import').addEventListener('click',function() { element('import_file').click(); });
  var pendingImport = null;
  element('import_file').addEventListener('change',async function(event) {
    var file = event.target.files && event.target.files[0];
    if (!file) { return; }
    try {
      if (file.size > 10 * 1024 * 1024) { throw new Error('Tutorial package exceeds 10 MB.'); }
      var source = portable.importSingle(await file.arrayBuffer()), existing = await store.get(source.id);
      pendingImport = {source:source,revision:existing ? existing.revisionId : null};
      element('import_summary').textContent = (source.route.title || 'Untitled tutorial') + ' · ' + source.route.steps.length +
        ' cards. ' + problems(source.route).join(' ');
      document.querySelector('input[name="kg_tutorial_import_mode"][value="copy"]').checked = true;
      element('import_replace').disabled = !existing;
      element('import_status').textContent = '';
      element('import_dialog').showModal();
    } catch (error) { element('library_status').textContent = 'Could not import: ' + error.message; }
    finally { event.target.value = ''; }
  });
  element('import_cancel').addEventListener('click',function() { pendingImport = null; element('import_dialog').close(); });
  element('import_dialog').addEventListener('cancel',function(event) {
    if (element('import_apply').disabled) { event.preventDefault(); return; }
    pendingImport = null;
  });
  element('import_apply').addEventListener('click',async function() {
    if (!pendingImport) { return; }
    element('import_apply').disabled = element('import_cancel').disabled = true;
    try {
      await flush();
      var source = pendingImport.source, record;
      if (document.querySelector('input[name="kg_tutorial_import_mode"]:checked').value === 'replace') {
        var snapshot = await store.snapshot(), existing = snapshot.records.find(function(item) { return item.id === source.id; });
        if (!existing || existing.revisionId !== pendingImport.revision) { throw new Error('This tutorial changed since the import was reviewed. Reopen the import before replacing it.'); }
        var now = new Date(Math.max(Date.now(),Date.parse(existing.updatedAt) + 1)).toISOString();
        var previous = clone(existing), previousId = 'personal:' + model.id();
        previous.id = previousId; previous.route.tutorial_id = previousId;
        previous.route.title += ' (before import)'; previous.deletedAt = ''; previous.updatedAt = now;
        previous.revisionId = 'revision:' + model.id(); previous.basedOn = {tutorialId:existing.id,version:'before import'};
        record = Object.assign({},existing,{route:clone(source.route),basedOn:source.basedOn || existing.basedOn,
          updatedAt:now,deletedAt:'',revisionId:'revision:' + model.id()});
        record.route.tutorial_id = existing.id;
        var revised = snapshot.records.filter(function(item) { return item.id !== existing.id; }).concat([record,previous]);
        await store.commitSnapshot(revised,null,snapshot.records,'import');
      } else {
        record = await store.create(source.route,source.basedOn || {tutorialId:source.id,version:'imported'});
      }
      await refresh(); pendingImport = null; element('import_dialog').close(); openEditor(record);
      element('library_status').textContent = 'Tutorial imported.';
    } catch (error) { element('import_status').textContent = 'Could not import: ' + error.message; }
    finally { element('import_apply').disabled = element('import_cancel').disabled = false; }
  });
  function reconcile(merged) {
    reconciliation = (async function() {
      if (editing) {
        var previousId = editing.id, previous = records.get(previousId);
        var targetId = (merged.relocations || {})[previousId] || previousId;
        var incoming = merged.records.find(function(record) { return record.id === targetId && !record.deletedAt; });
        var compatible = incoming && (targetId !== previousId || (previous &&
          await portable.fingerprint(previous.route) === await portable.fingerprint(incoming.route)));
        var currentRoute = editing.route;
        if (!compatible) {
          var serial = edited;
          incoming = await store.create(currentRoute,{tutorialId:previousId,version:options.version},
            {conflictOf:previousId,sourceRevision:await portable.fingerprint(previous || editing)});
          saved = serial;
        }
        Object.assign(editing,clone(incoming)); editing.route = currentRoute; editing.route.tutorial_id = incoming.id;
        dialog.dataset.tutorialId = editing.id;
        element('editor_heading').textContent = editing.conflictOf ? 'Edit tutorial — conflict copy' : 'Edit tutorial';
        status(edited === saved ? 'saved' : 'saving',editing.conflictOf ? 'Cloud changes kept separately; this editor remains your draft.' : 'Saved in this browser.');
      }
      await refresh();
      if (!editing) {
        var route = routeById(selected());
        if (route) { options.select(selected()); }
        else if (String(selected()).indexOf('personal:') === 0) { element('intro').hidden = true; }
      }
    })().finally(function() { reconciliation = null; });
    return reconciliation;
  }
  function selected() { return options.selectedId(); }
  element("new").addEventListener("click", function() { create(null); });
  element("library_retry").addEventListener("click", initialise);
  element("intro_copy").addEventListener("click", function() { create(options.routeById(selected())); });
  element("intro_edit").addEventListener("click", function() {
    var record = records.get(selected()); if (record) { openEditor(record); }
  });
  element("intro_delete").addEventListener("click", async function() {
    var record = records.get(selected());
    if (!record || !window.confirm('Delete “' + record.route.title + '”?')) { return; }
    try {
      await store.remove(record.id, record.revisionId); records.delete(record.id); renderList(); element("intro").hidden = true;
    } catch (error) { element("library_status").textContent = "Could not delete tutorial: " + error.message; }
  });
  dialog.addEventListener("input", function(event) {
    if (["editor_title", "editor_summary", "editor_author", "editor_domains", "editor_card_title", "editor_commentary"].some(function(key) {
      return event.target === element(key);
    })) { changed(); }
  });
  element("editor_card").addEventListener("change", function() {
    cardIndex = Number(this.value); renderCard();
  });
  element("editor_close").addEventListener("click", closeEditor);
  element("editor_retry").addEventListener("click", function() { flush().catch(function() {}); });
  element("editor_record").addEventListener("click", recordActions);
  element("editor_play").addEventListener("click", function() { playEditor('all'); });
  element("editor_preview").addEventListener("click", function() { playEditor('preview'); });
  element("editor_from").addEventListener("click", function() { playEditor('from'); });
  element("editor_card_controls").addEventListener("click", function(event) {
    var action = event.target.dataset.cardAction, steps = editing.route.steps;
    if (!action || busy) { return; }
    if (action === 'up' || action === 'down') { moveCard(cardIndex, cardIndex + (action === 'up' ? -1 : 1)); return; }
    if (action === 'add') { steps.splice(cardIndex + 1, 0, model.newCard()); cardIndex = Math.min(cardIndex + 1, steps.length - 1); }
    if (action === 'duplicate') { var copy = clone(steps[cardIndex]); copy.step_id = model.id(); steps.splice(cardIndex + 1, 0, copy); cardIndex += 1; }
    if (action === 'delete') {
      if (!window.confirm('Delete this card?')) { return; }
      steps.splice(cardIndex, 1); cardIndex = Math.max(0, Math.min(cardIndex, steps.length - 1));
    }
    markChanged(); renderCardList(); renderCard();
  });
  var draggedCard = null;
  element("editor_order").addEventListener('dragstart', function(event) {
    var item = event.target.closest('li'); if (!item || busy) { event.preventDefault(); return; }
    draggedCard = item.dataset.cardId; event.dataTransfer.setData('text/plain', draggedCard);
  });
  element("editor_order").addEventListener('dragover', function(event) { if (draggedCard) { event.preventDefault(); } });
  element("editor_order").addEventListener('drop', function(event) {
    event.preventDefault(); var item = event.target.closest('li');
    var steps = editing.route.steps, from = steps.findIndex(function(step) { return step.step_id === draggedCard; });
    var to = item ? steps.findIndex(function(step) { return step.step_id === item.dataset.cardId; }) : -1;
    if (!busy && from >= 0 && to >= 0 && from !== to) { moveCard(from, to); }
    draggedCard = null;
  });
  element("editor_order").addEventListener('dragend', function() { draggedCard = null; });
  dialog.addEventListener("cancel", function(event) { event.preventDefault(); closeEditor(); });
  dialog.addEventListener("keydown", function(event) {
    if (event.key === "Escape") { event.stopPropagation(); }
  });
  window.addEventListener("beforeunload", function(event) {
    if (editing && edited !== saved) { event.preventDefault(); event.returnValue = ""; }
  });
  var ready = initialise();
  return {ready: ready, routeById: routeById, problems: problems,
    showIntroduction: showIntroduction, playbackExited: playbackExited,
    recordingChanged:recordingChanged, recordingStopped:recordingStopped, flush:flush, reconcile:reconcile};
}
