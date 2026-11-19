/* Explicit single-card capture. Checkpoints are session-only; stored cards contain commands. */
function kgCreateTutorialRecorder(options) {
  "use strict";
  var model = options.model, session = null, busy = false, searchTimer = null, searchQuery = null;
  var strip = document.getElementById('kg_tutorial_recording'), notice = document.getElementById('kg_tutorial_recording_status');
  function render(message) {
    strip.hidden = !session;
    document.body.classList.toggle('kg-tutorial-recording', Boolean(session));
    strip.dataset.busy = String(busy);
    if (!session) { document.body.style.removeProperty('--kg-recording-height'); return; }
    document.getElementById('kg_tutorial_recording_title').textContent = session.title + ' · ' + session.items.length + '/' + model.contract.max_actions + ' actions';
    ['undo', 'redo', 'pause', 'finish', 'cancel'].forEach(function(key) {
      var disabled = busy || (key === 'pause' && session.items.length >= model.contract.max_actions) || (key === 'undo' && !session.undo.length) || (key === 'redo' && !session.redo.length);
      document.getElementById('kg_tutorial_recording_' + key).disabled = disabled;
    });
    if (message !== undefined) { session.message = message; }
    var next = session.redo[session.redo.length - 1];
    notice.textContent = (session.message || '') + (next ? ' Next: ' + describe(next.item) + '.' : '');
    var last = session.undo[session.undo.length - 1];
    document.getElementById('kg_tutorial_recording_undo').title = last ? 'Undo: ' + describe(last.item) : 'Nothing to undo';
    document.getElementById('kg_tutorial_recording_redo').title = next ? 'Redo: ' + describe(next.item) : 'Nothing to redo';
    document.body.style.setProperty('--kg-recording-height',Math.ceil(strip.offsetHeight + 12) + 'px');
  }
  function describe(item) {
    var command = item.action, spec = model.contract.commands[command.command];
    if (kgTutorialSequence.isPause(item)) { return 'Pause ' + command.milliseconds / 1000 + 's'; }
    var target = command.target;
    var value = target ? model.catalog.object[target] || model.catalog.block[target] || target : command.value || command.preset || command.recipe || command.query;
    return (spec ? spec.label : command.command) + (value ? ' — ' + value : '');
  }
  function remember(item, before, after) {
    session.checkpoint = after; session.items.push(item);
    session.undo.push({before:before, item:item}); session.redo = [];
  }
  function warn(message) { if (session) { render(message); } }
  async function start(route, index) {
    if (session || busy) { throw new Error('Recording is already active.'); }
    busy = true;
    var original = options.presentation.capture(), card = route.steps[index], commands = [];
    session = {title:card.title, original:original, items:[], undo:[],
      redo:model.actions(card).reverse().map(function(item) { return {item:item}; })};
    render('Preparing this card…');
    try {
      commands = kgTutorialSequence.commandsThrough(route, index - 1);
      await options.presentation.replay(original, commands);
      for (var command of (card.prepare || [])) {
        var problem = model.commandProblem(command);
        if (problem) { throw new Error(problem); }
        await options.execute(command, {origin:'rehearsal'});
      }
      await options.settle();
      session.checkpoint = options.presentation.capture();
      render('Redo keeps old actions; a new action replaces the remaining tail.');
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
      var result = await execute(); await options.settle();
      var item = {action:model.clone(command), pointer:{target:metadata && metadata.pointer || model.pointer(command)}, pause_ms:0};
      var after = options.presentation.capture();
      remember(item,before,after);
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
    var record = source[source.length - 1], before = options.presentation.capture();
    try {
      if (redo) {
        var problem = model.commandProblem(record.item.action);
        if (problem) { throw new Error(problem); }
        // Redo performs the semantic action, including transient effects such as hover.
        if (!kgTutorialSequence.isPause(record.item)) { await options.execute(record.item.action,{origin:'rehearsal'}); }
        await options.settle(); record.before = before;
      } else { await options.presentation.restore(record.before); }
      session.checkpoint = options.presentation.capture(); source.pop();
      if (redo) { session.items.push(record.item); session.undo.push(record); }
      else { session.items.pop(); session.redo.push(record); }
      render((redo ? 'Restored: ' : 'Undone: ') + describe(record.item) + '.');
    } catch (error) {
      await options.presentation.restore(before); render('Could not restore the action: ' + error.message);
    } finally { busy = false; render(); }
  }
  async function pause() {
    await flushSearch(); if (!session || busy) { return; }
    if (session.items.length >= model.contract.max_actions) { warn('Finish recording and add another card.'); return; }
    var view = options.presentation.capture();
    remember({action:{command:'wait',milliseconds:1000},pause_ms:0},view,view);
    var seconds = 0;
    for (var i = session.items.length - 1; i >= 0 && kgTutorialSequence.isPause(session.items[i]); i -= 1) {
      seconds += session.items[i].action.milliseconds / 1000;
    }
    render('Pause at end: ' + seconds + 's. Undo removes the last pause.');
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
  ['undo', 'redo', 'pause', 'finish', 'cancel'].forEach(function(key) {
    document.getElementById('kg_tutorial_recording_' + key).addEventListener('click', function() {
      if (key === 'undo' || key === 'redo') { travel(key === 'redo'); }
      else if (key === 'pause') { pause(); }
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
  window.addEventListener('resize',function() { if (session) { render(); } });
  return {start:start, perform:perform, warn:warn, active:function() { return Boolean(session); },
    busy:function() { return busy; }, flushSearch:flushSearch};
}
