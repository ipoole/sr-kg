/* Tutorial editing data rules. The command contract also drives the build-time validator. */
function kgCreateTutorialEditorModel(options) {
  "use strict";
  var contract = options.contract, concepts = options.concepts, modules = options.modules;
  var catalog = {concept: {}, module: {}, block: {}, edge: {}};
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function id() { return window.crypto && crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2); }
  function label(item, fallback) { return (item.display_id || fallback) + " — " + (item.title || item.label || item.name || ""); }
  Object.keys(concepts).forEach(function(key) { catalog.concept['concept:' + key] = label(concepts[key], key); });
  Object.keys(modules).forEach(function(key) { catalog.module['module:' + key] = label(modules[key], key); });
  [concepts, modules].forEach(function(owners) {
    Object.keys(owners).forEach(function(key) {
      (owners[key].content_blocks || []).forEach(function(block) {
        catalog.block['block:' + block.block_id] = label(owners[key], key) + ': ' + block.title;
      });
    });
  });
  (options.edges || []).forEach(function(edge) {
    if (!concepts[edge.from] || !concepts[edge.to]) { return; }
    var relation = options.relation(edge);
    catalog.edge['edge:' + edge.from + '|' + relation + '|' + edge.to] =
      label(concepts[edge.from], edge.from) + ' → ' + relation + ' → ' + label(concepts[edge.to], edge.to);
  });
  catalog.object = Object.assign({}, catalog.concept, catalog.module);
  function choices(spec) { return spec.choices || catalog[spec.type] || {}; }
  function newCommand(name) {
    var result = {command: name};
    contract.commands[name].fields.forEach(function(spec) {
      if (!spec.optional) { result[spec.name] = spec.default !== undefined ? spec.default : ''; }
    });
    return result;
  }
  function pointer(command) {
    var spec = contract.commands[command.command];
    if (!spec) { return 'narration'; }
    var result = spec.pointer.replace(/\{([^}]+)\}/g, function(match, key) {
      return key === 'target_id' ? String(command.target || '').replace(/^[^:]+:/, '') : command[key] || '';
    });
    return result;
  }
  var pointerCatalog = {};
  function pointerChoices(group) {
    if (Object.prototype.hasOwnProperty.call(pointerCatalog, group)) { return pointerCatalog[group]; }
    var result = {};
    function add(prefix, values) { Object.keys(values).forEach(function(key) { result[prefix + key] = values[key]; }); }
    if (group === 'general') { return contract.pointer_base; }
    if (group === 'controls') { contract.controls.forEach(function(key) { result['control:' + key] = key; }); }
    if (group === 'module-controls') { Object.keys(modules).forEach(function(key) { result['control:module-fold:' + key] = label(modules[key], key); }); }
    if (group === 'graph') { add('graph:', catalog.object); }
    if (group === 'edges') { add('graph:', catalog.edge); }
    if (group === 'search') { add('search:', catalog.object); }
    if (group === 'blocks') { add('details:', catalog.block); }
    if (group === 'tools') { contract.tools.forEach(function(key) { result['tools:section:' + key] = key; }); }
    if (group === 'reading') {
      contract.recipes.forEach(function(recipe) {
        result['details:reading-tree:' + recipe] = recipe + ' tree';
        result['details:reading-sync:' + recipe] = recipe + ' synchronisation';
      });
    }
    if (group === 'reading-concepts') {
      contract.recipes.forEach(function(recipe) {
        Object.keys(concepts).forEach(function(key) { result['details:reading-concept:' + recipe + ':' + key] = recipe + ': ' + label(concepts[key], key); });
      });
    }
    pointerCatalog[group] = result;
    return result;
  }
  var groups = {general:'Narration and Details', controls:'Toolbar controls', 'module-controls':'Module fold controls',
    graph:'Graph concepts and modules', edges:'Graph edges', search:'Search results', blocks:'Content blocks',
    reading:'Reading tree controls', 'reading-concepts':'Reading tree concepts', tools:'Tools sections'};
  function pointerGroup(target) {
    target = String(target || "");
    if (contract.pointer_base[target]) { return 'general'; }
    if (target.indexOf('control:module-fold:') === 0) { return 'module-controls'; }
    if (target.indexOf('control:') === 0) { return 'controls'; }
    if (target.indexOf('graph:edge:') === 0) { return 'edges'; }
    if (target.indexOf('graph:') === 0) { return 'graph'; }
    if (target.indexOf('search:') === 0) { return 'search'; }
    if (target.indexOf('details:block:') === 0) { return 'blocks'; }
    if (target.indexOf('details:reading-concept:') === 0) { return 'reading-concepts'; }
    if (target.indexOf('details:reading-') === 0) { return 'reading'; }
    if (target.indexOf('tools:') === 0) { return 'tools'; }
    return 'general';
  }
  function commandProblem(command) {
    var spec = command && contract.commands[command.command];
    if (!spec) { return 'Choose a supported action.'; }
    for (var index = 0; index < spec.fields.length; index += 1) {
      var field = spec.fields[index], value = command[field.name];
      if (field.optional && value === undefined) { continue; }
      var valid;
      if (field.type === 'number') { valid = typeof value === 'number' && Number.isFinite(value) && value >= field.min && value <= field.max; }
      else if (field.type === 'integer') { valid = Number.isInteger(value) && value >= field.min && value <= field.max; }
      else if (field.type === 'boolean') { valid = typeof value === 'boolean'; }
      else if (field.type === 'text') { valid = typeof value === 'string' && (field.allow_empty || value.trim()) && value.length <= field.max_length; }
      else if (field.type === 'edge') {
        var parts = typeof value === 'string' ? value.replace(/^edge:/, '').split('|') : [];
        valid = typeof value === 'string' && value.indexOf('edge:') === 0 && parts.length === 3 &&
          catalog.concept['concept:' + parts[0]] && catalog.concept['concept:' + parts[2]] && contract.relations.indexOf(parts[1]) >= 0;
      } else { valid = Object.prototype.hasOwnProperty.call(choices(field), value); }
      if (!valid) { return 'Check ' + field.label.toLowerCase() + '.'; }
    }
    return '';
  }
  function actions(step) {
    var items = kgTutorialSequence.actions(step);
    if (!step.actions && (!items.length || (step.action.command === 'wait' && step.action.milliseconds === 0 &&
        (!step.pointer || step.pointer.target === 'narration')))) { return []; }
    return clone(items);
  }
  function setActions(step, items) {
    delete step.actions; delete step.action; delete step.pointer;
    if (items.length) { step.actions = clone(items); }
    else { step.action = {command:'wait', milliseconds:0}; step.pointer = {target:'narration'}; }
  }
  function stepProblem(step) {
    if (!step || !String(step.title || '').trim() || !String(step.commentary || '').trim()) { return 'Add a title and written narration.'; }
    if (step.demonstrate !== undefined && typeof step.demonstrate !== 'boolean') { return 'Check Action visibility.'; }
    var list = actions(step);
    if (list.length > contract.max_actions) { return 'Too many actions.'; }
    var setup = step.prepare || [];
    for (var index = 0; index < setup.length + list.length; index += 1) {
      var silent = index < setup.length, item = silent ? {action:setup[index]} : list[index - setup.length];
      var problem = commandProblem(item.action);
      if (!problem && !silent) {
        var target = kgTutorialSequence.pointerTarget(item);
        if (!pointerChoices(pointerGroup(target))[target]) { problem = 'Choose an available pointer target.'; }
        var pause = item.pause_ms === undefined ? 500 : item.pause_ms;
        if (!Number.isInteger(pause) || pause < 0 || pause > contract.max_pause_ms) { problem = 'Pause must be between 0 and 5 seconds.'; }
      }
      if (problem) { return (silent ? 'Setup ' : 'Action ') + (silent ? index + 1 : index - setup.length + 1) + ': ' + problem; }
    }
    return '';
  }
  var domains = new Set(Object.keys(concepts).map(function(key) { return concepts[key].domain; }));
  function routeProblems(route) {
    if (!route || !String(route.title || "").trim()) { return ["Add a tutorial title."]; }
    if (!String(route.summary || "").trim()) { return ["Add a tutorial summary."]; }
    if (!Array.isArray(route.steps) || !route.steps.length) { return ["Add a card."]; }
    var ids = new Set();
    for (var index = 0; index < route.steps.length; index += 1) {
      var step = route.steps[index], problem = stepProblem(step);
      if (problem) { return ["Card " + (index + 1) + ": " + problem]; }
      if (!step.step_id || ids.has(step.step_id)) { return ["Each card needs a unique identifier."]; }
      ids.add(step.step_id);
    }
    var missing = (route.domains || []).filter(function(domain) { return !domains.has(domain); });
    return missing.length ? ["This tutorial needs these domains: " + missing.join(", ") + "."] : [];
  }
  function newCard() { return kgTutorialSequence.newCard(id()); }
  return {clone:clone, id:id, catalog:catalog, contract:contract, choices:choices, newCommand:newCommand,
    pointer:pointer, pointerChoices:pointerChoices, pointerGroup:pointerGroup, groups:groups,
    commandProblem:commandProblem, actions:actions, setActions:setActions, stepProblem:stepProblem, routeProblems:routeProblems, newCard:newCard};
}
