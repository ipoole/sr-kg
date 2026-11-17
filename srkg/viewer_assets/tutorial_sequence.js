/* Shared route sequencing. UI presentation and persistence remain with their owners. */
var kgTutorialSequence = (function() {
  "use strict";
  function actions(step) {
    return step.actions || (step.action ? [{action:step.action, pointer:step.pointer, pause_ms:0}] : []);
  }
  function commandsThrough(route, index) {
    return route.steps.slice(0, index + 1).reduce(function(commands, step) {
      // Reconstruct view state, omitting playback-only waits from earlier cards.
      return commands.concat(step.prepare || [], actions(step).map(function(item) { return item.action; }).filter(function(command) { return command.command !== 'wait'; }));
    }, []);
  }
  function newCard(id) {
    return {step_id:id, title:'New card', commentary:'', demonstrate:false,
      action:{command:'wait', milliseconds:0}, pointer:{target:'narration'}};
  }
  function isPause(item) { return item.action.command === 'wait' && item.action.milliseconds > 0; }
  return {actions:actions, commandsThrough:commandsThrough, newCard:newCard, isPause:isPause};
})();
