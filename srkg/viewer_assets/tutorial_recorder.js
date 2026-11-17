/* Explicit single-card capture. Checkpoints are session-only; stored cards contain commands. */
function kgCreateTutorialRecorder(options) {
  "use strict";
  var model = options.model, session = null, busy = false, searchTimer = null, searchQuery = null;
  var strip = document.getElementById('kg_tutorial_recording'), notice = document.getElementById('kg_tutorial_recording_status');
  function render(message) {
    strip.hidden = !session;
    document.body.classList.toggle('kg-tutorial-recording', Boolean(session));
    strip.dataset.busy = String(busy);
    if (!session) { return; }
    document.getElementById('kg_tutorial_recording_title').textContent = session.title + ' · ' + session.items.length + '/' + model.contract.max_actions + ' actions';
    ['undo', 'redo', 'finish', 'cancel'].forEach(function(key) {
      var disabled = busy || (key === 'undo' && !session.undo.length) || (key === 'redo' && !session.redo.length);
      document.getElementById('kg_tutorial_recording_' + key).disabled = disabled;
    });
    if (message !== undefined) { notice.textContent = message; }
  }
  function warn(message) { if (session) { render(message); } }
  async function settled() { await options.settle(); }
  async function start(route, index) {
    if (session || busy) { throw new Error('Recording is already active.'); }
    busy = true;
    var original = options.presentation.capture(), card = route.steps[index], commands = [];
    session = {title:card.title, original:original, items:[], undo:[], redo:[]};
    render('Preparing this card…');
    try {
      commands = kgTutorialSequence.commandsThrough(route, index - 1);
      await options.presentation.replay(original, commands);
      for (var command of (card.prepare || [])) {
        var problem = model.commandProblem(command);
        if (problem) { throw new Error(problem); }
        await options.execute(command, {origin:'rehearsal'});
      }
      await settled();
      session.checkpoint = options.presentation.capture();
      render('Recording. Prefer Fit/Fit++; manual pan/zoom are not recorded.');
    } catch (error) {
      try { await options.presentation.restore(original); }
      finally { session = null; }
      throw error;
    }
    finally { busy = false; render(); }
  }
  async function perform(command, execute, metadata) {
    if (!session) { return execute(); }
    if (busy) { warn('Please wait for the current action.'); return {ok:false}; }
    var problem = model.commandProblem(command);
    if (problem) { warn('Not recorded: ' + problem); return execute(); }
    if (session.items.length >= model.contract.max_actions) {
      busy = true; render();
      try { await options.presentation.restore(options.presentation.capture()); }
      finally { busy = false; render('This card has 20 actions. Finish recording and add another card.'); }
      return {ok:false};
    }
    busy = true; render('Recording…');
    var before = options.presentation.capture();
    // Search input is already changed when its debounced intention is submitted.
    if (command.command === 'search') { before.search = model.clone(session.checkpoint.search); }
    try {
      var result = await execute(); await settled();
      var item = {action:model.clone(command), pointer:{target:metadata && metadata.pointer || model.pointer(command)}, pause_ms:500};
      var after = options.presentation.capture();
      session.checkpoint = after;
      session.items.push(item); session.undo.push({before:before, after:after, item:item}); session.redo = [];
      render('Recorded.'); return result;
    } catch (error) {
      await options.presentation.restore(before); render('Action not recorded: ' + error.message); return {ok:false};
    } finally { busy = false; render(); }
  }
  function flushSearch() {
    if (searchTimer !== null) { clearTimeout(searchTimer); searchTimer = null; }
    if (session && busy && searchQuery !== null) { searchTimer = setTimeout(flushSearch, 100); return Promise.resolve(); }
    var query = searchQuery; searchQuery = null;
    if (session && query !== null) { return options.dispatch({command:'search', query:query}); }
    return Promise.resolve();
  }
  async function travel(redo) {
    await flushSearch(); if (!session || busy) { return; }
    var source = redo ? session.redo : session.undo;
    if (!source.length) { return; }
    busy = true; render();
    var record = source[source.length - 1];
    try {
      await options.presentation.restore(redo ? record.after : record.before);
      session.checkpoint = options.presentation.capture();
      source.pop();
      if (redo) { session.items.push(record.item); session.undo.push(record); }
      else { session.items.pop(); session.redo.push(record); }
      render(redo ? 'Action restored.' : 'Last recorded action undone.');
    } catch (error) { render('Could not restore the view: ' + error.message); }
    finally { busy = false; render(); }
  }
  function clearSearch() {
    if (searchTimer !== null) { clearTimeout(searchTimer); searchTimer = null; }
    searchQuery = null;
  }
  async function finish(cancelled) {
    if (!session || busy) { return; }
    try {
      if (cancelled) { clearSearch(); }
      else { await flushSearch(); }
      if (!session || busy) { return; }
      busy = true; render(cancelled ? 'Cancelling…' : 'Finishing recording…');
      var items = cancelled ? null : model.clone(session.items);
      await options.presentation.restore(session.original);
      session = null; render(); await options.stopped(items);
    } catch (error) { render('Could not finish recording: ' + error.message + '. You can retry or Cancel.'); }
    finally { busy = false; render(); }
  }
  ['undo', 'redo', 'finish', 'cancel'].forEach(function(key) {
    document.getElementById('kg_tutorial_recording_' + key).addEventListener('click', function() {
      if (key === 'undo' || key === 'redo') { travel(key === 'redo'); }
      else { finish(key === 'cancel'); }
    });
  });
  // Capture semantic controls before native disclosure toggles or older local handlers.
  function gesture(event) {
    if (!session || strip.contains(event.target)) { return; }
    if (busy) { event.preventDefault(); event.stopImmediatePropagation(); warn('Please wait for the current action.'); return; }
    var result = options.gesture(event);
    if (!result) { return; }
    if (result.warning) {
      if (result.block) { event.preventDefault(); event.stopImmediatePropagation(); }
      warn(result.warning); return;
    }
    event.preventDefault(); event.stopImmediatePropagation();
    flushSearch().then(function() { return options.dispatch(result.command, {pointer:result.pointer}); });
  }
  document.addEventListener('click', gesture, true);
  document.addEventListener('change', gesture, true);
  document.getElementById('kg_search').addEventListener('keydown', function(event) {
    if (!session || event.key !== 'Enter' || busy) { return; }
    event.preventDefault(); event.stopImmediatePropagation();
    flushSearch().then(function() {
      var result = document.querySelector('#kg_concept_list button');
      if (session && result && document.getElementById('kg_search').value.trim()) { result.click(); }
    });
  }, true);
  document.getElementById('kg_search').addEventListener('input', function(event) {
    if (!session) { return; }
    searchQuery = event.target.value;
    if (searchTimer !== null) { clearTimeout(searchTimer); }
    searchTimer = setTimeout(flushSearch, 350);
  });
  window.addEventListener('beforeunload', function(event) {
    if (session || busy) { event.preventDefault(); event.returnValue = ''; }
  });
  return {start:start, perform:perform, warn:warn, active:function() { return Boolean(session); },
    busy:function() { return busy; }, flushSearch:flushSearch};
}
