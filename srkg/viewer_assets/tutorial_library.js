/* Personal library and minimal text editor; cards play through the shared player. */
function kgCreateTutorialLibrary(options) {
  "use strict";
  var store = options.store, escape = options.markup.escapeHtml;
  var records = new Map(), editing = null, cardIndex = 0, edited = 0, saved = 0;
  var saveTimer = null, pendingSave = null, returningToEditor = false;
  var dialog = document.getElementById("kg_tutorial_editor");
  function element(id) { return document.getElementById("kg_tutorial_" + id); }
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function problems(route) {
    if (!route || !String(route.title || "").trim()) { return ["Add a tutorial title."]; }
    if (!String(route.summary || "").trim()) { return ["Add a tutorial summary."]; }
    if (!Array.isArray(route.steps) || !route.steps.length) { return ["Add a card."]; }
    for (var index = 0; index < route.steps.length; index += 1) {
      var step = route.steps[index];
      if (!step || !String(step.title || "").trim() || !String(step.commentary || "").trim()) {
        return ["Add a title and written narration to card " + (index + 1) + "."];
      }
    }
    var missing = (route.domains || []).filter(function(domain) { return !options.hasDomain(domain); });
    return missing.length ? ["This tutorial needs these domains: " + missing.join(", ") + "."] : [];
  }
  function routeById(id) { var record = records.get(id); return record ? record.route : null; }
  function status(state, text) {
    element("editor_status").dataset.state = state;
    element("editor_status").textContent = text;
    element("editor_retry").hidden = state !== "error";
  }
  function updatePlay() {
    var errors = editing ? problems(editing.route) : [];
    element("editor_play").disabled = Boolean(errors.length);
    element("editor_validation").textContent = errors.join(" ");
  }
  function renderList() {
    var items = Array.from(records.values()).sort(function(a, b) { return b.updatedAt.localeCompare(a.updatedAt); });
    element("personal_list").innerHTML = items.length ? items.map(function(record) {
      var route = record.route;
      return '<button type="button" class="kg-tutorial-select" data-tutorial-id="' + escape(record.id) +
        '" aria-current="false"><span class="kg-tutorial-list-title">' + escape(route.title || "Untitled tutorial") +
        '</span><span class="kg-tutorial-list-summary">' +
        (problems(route).length ? "Draft · " : "") + route.steps.length +
        (route.steps.length === 1 ? ' card' : ' cards') + '</span></button>';
    }).join("") : '<p class="kg-muted-label">No personal tutorials yet.</p>';
  }
  async function refresh() {
    var list = await store.list();
    records = new Map(list.map(function(record) { return [record.id, record]; }));
    renderList();
  }
  async function initialise() {
    element("new").disabled = true;
    try {
      await refresh();
      element("library_status").textContent = "Tutorials currently stay in this browser; backup and Google sync do not include them yet.";
      element("library_status").dataset.ready = "true";
      element("new").disabled = false;
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
  function renderCard() {
    var step = editing.route.steps[cardIndex];
    element("editor_card_title").value = step ? step.title : "";
    element("editor_commentary").value = step ? step.commentary : "";
    var actions = step ? (step.actions || [{action: step.action}]) : [];
    var count = actions.filter(function(item) { return item.action && item.action.command !== "wait"; }).length;
    element("editor_actions").textContent = count ? count + " viewer actions in this card." : "Commentary-only card.";
  }
  function showEditor() {
    if (!dialog.open) { dialog.showModal(); }
  }
  function openEditor(record) {
    editing = clone(record); edited = saved = 0; cardIndex = 0;
    dialog.dataset.tutorialId = record.id;
    element("editor_title").value = editing.route.title;
    element("editor_summary").value = editing.route.summary;
    element("editor_author").value = editing.route.author || "";
    element("editor_card").replaceChildren();
    editing.route.steps.forEach(function(step, index) {
      var option = document.createElement("option");
      option.value = index; option.textContent = (index + 1) + ". " + step.title;
      element("editor_card").appendChild(option);
    });
    renderCard(); updatePlay(); status("saved", "Saved in this browser."); showEditor();
    element("editor_title").focus();
  }
  function saveFailed(error) { status("error", "Not saved: " + error.message); }
  async function flush() {
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
    var step = editing.route.steps[cardIndex];
    if (step) {
      step.title = element("editor_card_title").value;
      step.commentary = element("editor_commentary").value;
      element("editor_card").options[cardIndex].textContent = (cardIndex + 1) + ". " + step.title;
    }
    edited += 1; updatePlay(); status("saving", "Saving…");
    if (saveTimer !== null) { clearTimeout(saveTimer); }
    saveTimer = setTimeout(function() { flush().catch(function() {}); }, 250);
  }
  async function closeEditor() {
    try {
      await flush(); dialog.close();
      options.select(editing.id); editing = null;
    } catch (error) { saveFailed(error); }
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
  async function playEditor() {
    if (!editing || problems(editing.route).length) { return; }
    try {
      await flush(); dialog.close(); returningToEditor = true;
      var started = await options.play(editing.id);
      if (!started) { returningToEditor = false; showEditor(); status("error", "Could not start this tutorial."); }
    } catch (error) { returningToEditor = false; showEditor(); saveFailed(error); }
  }
  function playbackExited() {
    if (returningToEditor) { returningToEditor = false; showEditor(); element("editor_play").focus(); }
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
    if (event.target !== element("editor_card")) { changed(); }
  });
  element("editor_card").addEventListener("change", function() {
    cardIndex = Number(this.value); renderCard();
  });
  element("editor_close").addEventListener("click", closeEditor);
  element("editor_retry").addEventListener("click", function() { flush().catch(function() {}); });
  element("editor_play").addEventListener("click", playEditor);
  dialog.addEventListener("cancel", function(event) { event.preventDefault(); closeEditor(); });
  dialog.addEventListener("keydown", function(event) {
    if (event.key === "Escape") { event.stopPropagation(); }
  });
  window.addEventListener("beforeunload", function(event) {
    if (editing && edited !== saved) { event.preventDefault(); event.returnValue = ""; }
  });
  var ready = initialise();
  return {ready: ready, routeById: routeById, problems: problems,
    showIntroduction: showIntroduction, playbackExited: playbackExited};
}
