/* Shared route sequencing. UI presentation and persistence remain with their owners. */
var kgTutorialSequence = (function() {
  "use strict";
  function actions(step) {
    return step.actions || (step.action ? [{action:step.action, pointer:step.pointer, pause_ms:0}] : []);
  }
  function commandsThrough(route, index) {
    var commands = [];
    route.steps.slice(0, index + 1).forEach(function(step) {
      // Legacy setup remains executable; main-action waits are playback-only.
      (step.prepare || []).forEach(function(command) { commands.push(command); });
      actions(step).forEach(function(item) {
        if (item.action.command !== 'wait') { commands.push(item.action); }
      });
    });
    return commands;
  }
  function pointerTarget(item) { return item.pointer ? item.pointer.target : 'narration'; }
  function finalAction(step) {
    var items = actions(step);
    for (var index = items.length - 1; index >= 0; index -= 1) {
      if (!isPause(items[index])) { return items[index]; }
    }
    return null;
  }
  function newCard(id) {
    return {step_id:id, title:'New card', commentary:'', demonstrate:true,
      action:{command:'wait', milliseconds:0}, pointer:{target:'narration'}};
  }
  function isPause(item) { return item.action.command === 'wait' && item.action.milliseconds > 0; }
  return {actions:actions, commandsThrough:commandsThrough, newCard:newCard, isPause:isPause, pointerTarget:pointerTarget, finalAction:finalAction};
})();
