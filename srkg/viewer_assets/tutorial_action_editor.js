/* One compact command form, reused for visible actions and silent setup. */
function kgCreateTutorialActionEditor(options) {
  "use strict";
  var root = options.root, model = options.model, silent = options.silent;
  var items = [], selected = 0;
  function node(tag, text) { var element = document.createElement(tag); if (text) { element.textContent = text; } return element; }
  function select(values, value, blank) {
    var input = node('select');
    if (blank !== undefined) { input.add(new Option(blank, '')); }
    Object.keys(values).forEach(function(key) { input.add(new Option(values[key], key)); });
    if (value && !Object.prototype.hasOwnProperty.call(values, value)) { input.add(new Option('Unavailable: ' + value, value)); }
    input.value = value === undefined ? '' : String(value); return input;
  }
  function field(label, input) { input.setAttribute('aria-label', label); var wrapper = node('label', label); wrapper.appendChild(input); root.appendChild(wrapper); }
  function currentCommand() { return silent ? items[selected] : items[selected].action; }
  function change(repaint) { options.changed(model.clone(items)); if (repaint) { render(); } }
  function toolbarButton(label, operation, disabled) {
    var button = node('button', label); button.type = 'button'; button.disabled = disabled;
    button.addEventListener('click', operation); toolbar.appendChild(button);
  }
  var toolbar;
  function render() {
    root.replaceChildren();
    var list = node('select'); list.setAttribute('aria-label', silent ? 'Setup action' : 'Viewer action');
    items.forEach(function(item, index) {
      var command = silent ? item : item.action, spec = model.contract.commands[command.command];
      list.add(new Option((index + 1) + '. ' + (spec ? spec.label : command.command), index));
    });
    selected = Math.max(0, Math.min(selected, items.length - 1)); list.value = selected;
    list.disabled = !items.length;
    list.addEventListener('change', function() { selected = Number(list.value); render(); });
    field(silent ? 'Setup action' : 'Viewer action', list);
    toolbar = node('div'); toolbar.className = 'kg-tutorial-editor-actions'; root.appendChild(toolbar);
    toolbarButton('Add action', function() {
      var command = model.newCommand('select');
      items.push(silent ? command : {action:command, pointer:{target:model.pointer(command)}, pause_ms:500});
      selected = items.length - 1; change(true);
    }, items.length >= model.contract.max_actions);
    toolbarButton('Duplicate action', function() { items.splice(selected + 1, 0, model.clone(items[selected])); selected += 1; change(true); },
      !items.length || items.length >= model.contract.max_actions);
    toolbarButton('Delete action', function() { items.splice(selected, 1); change(true); }, !items.length);
    toolbarButton('Move action up', function() { var item = items.splice(selected, 1)[0]; selected -= 1; items.splice(selected, 0, item); change(true); }, selected <= 0 || !items.length);
    toolbarButton('Move action down', function() { var item = items.splice(selected, 1)[0]; selected += 1; items.splice(selected, 0, item); change(true); }, selected >= items.length - 1);
    if (!items.length) { root.appendChild(node('p', silent ? 'No silent setup.' : 'No viewer actions — this card shows narration only.')); return; }
    var command = currentCommand(), names = {};
    Object.keys(model.contract.commands).forEach(function(key) { names[key] = model.contract.commands[key].label; });
    var commandSelect = select(names, command.command);
    commandSelect.addEventListener('change', function() {
      var replacement = model.newCommand(commandSelect.value);
      if (silent) { items[selected] = replacement; }
      else { items[selected].action = replacement; items[selected].pointer = {target:model.pointer(replacement)}; }
      change(true);
    }); field('Action type', commandSelect);
    var descriptor = model.contract.commands[command.command];
    if (!descriptor) { return; }
    descriptor.fields.forEach(function(spec) {
      var value = command[spec.name], input;
      if (spec.type === 'integer' || spec.type === 'text') {
        input = node('input'); input.type = spec.type === 'integer' ? 'number' : 'text';
        if (spec.type === 'integer') {
          input.min = spec.min / (spec.scale || 1); input.max = spec.max / (spec.scale || 1);
          input.step = spec.scale ? '0.1' : '1';
          input.value = value === undefined ? '' : value / (spec.scale || 1);
        } else { input.value = value || ''; input.maxLength = spec.max_length; }
      } else {
        var values = spec.type === 'boolean' ? {'true':'Yes', 'false':'No'} : model.choices(spec);
        input = select(values, value, spec.optional ? 'Leave unchanged' : (value === '' || value === undefined ? 'Choose…' : undefined));
      }
      input.dataset.field = spec.name;
      input.addEventListener(spec.type === 'integer' || spec.type === 'text' ? 'input' : 'change', function() {
        var previousPointer = model.pointer(command);
        if (spec.optional && input.value === '') { delete command[spec.name]; }
        else if (spec.type === 'integer') { command[spec.name] = input.value === '' ? null : Number(input.value) * (spec.scale || 1); }
        else if (spec.type === 'boolean') { command[spec.name] = input.value === 'true'; }
        else { command[spec.name] = input.value; }
        if (!silent && items[selected].pointer && items[selected].pointer.target === previousPointer && model.pointer(command) !== previousPointer) {
          items[selected].pointer.target = model.pointer(command); change(true);
        } else { change(false); }
      }); field(spec.label, input);
    });
    if (silent) { return; }
    var item = items[selected], target = item.pointer ? item.pointer.target : 'narration';
    var group = select(model.groups, model.pointerGroup(target));
    field('Pointer area', group);
    var pointerInput;
    function renderPointer() {
      var replacement = select(model.pointerChoices(group.value), target, 'Choose…');
      replacement.setAttribute('aria-label', 'Pointer target');
      replacement.addEventListener('change', function() { target = replacement.value; item.pointer = {target:target}; change(false); });
      if (pointerInput) { pointerInput.replaceWith(replacement); }
      else { field('Pointer target', replacement); }
      pointerInput = replacement;
    }
    group.addEventListener('change', function() { target = ''; item.pointer = {target:''}; change(false); renderPointer(); }); renderPointer();
    var suggestion = node('button', 'Use suggested pointer'); suggestion.type = 'button';
    suggestion.addEventListener('click', function() { item.pointer = {target:model.pointer(command)}; change(true); }); root.appendChild(suggestion);
    var pause = node('input'); pause.type = 'number'; pause.min = 0; pause.max = 5; pause.step = '0.1';
    pause.value = (item.pause_ms === undefined ? 500 : item.pause_ms) / 1000;
    pause.addEventListener('input', function() { item.pause_ms = pause.value === '' ? null : Math.round(Number(pause.value) * 1000); change(false); });
    field('Pause before the next action (seconds)', pause);
  }
  return {show:function(value) { items = model.clone(value); selected = 0; render(); }};
}
