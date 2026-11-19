/* Shared route sequencing. UI presentation and persistence remain with their owners. */
var kgTutorialSequence = (function() {
  "use strict";
  function actions(step) {
    return step.actions || (step.action ? [{action:step.action, pointer:step.pointer, pause_ms:0}] : []);
  }
  function commandsThrough(route, index) {
    return route.steps.slice(0, index + 1).reduce(function(commands, step) {
      return commands.concat(step.prepare || [], actions(step).map(function(item) { return item.action; }));
    }, []);
  }
  function newCard(id) {
    return {step_id:id, title:'New card', commentary:'',
      action:{command:'wait', milliseconds:0}, pointer:{target:'narration'}};
  }
  return {actions:actions, commandsThrough:commandsThrough, newCard:newCard};
})();
