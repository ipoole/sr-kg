/* Translate local DOM controls into semantic commands; never persist selectors or pixels. */
function kgCreateTutorialCaptureTargets(options) {
  "use strict";
  function disclosure(element, open) {
    if (!element) { return null; }
    var tree = options.reading.commandFor(element, open);
    if (element.closest('.kg-reading-tree')) { return tree; }
    if (tree) { return tree; }
    if (element.classList.contains('user-note')) { return null; }
    var block = element.getAttribute('data-content-block-id');
    if (block) { return {command:'open-details-block', target:'block:' + block, open:open}; }
    if (element.classList.contains('study-questions')) { return {command:'open-study-questions', open:open}; }
    if (element.matches('.content-block-graphic, .concept-figure')) { return {command:'open-details-graphic', open:open}; }
    if (element.classList.contains('concept-derived-from')) { return {command:'open-details-relationship', value:'derived-from', open:open}; }
    if (element.classList.contains('concept-backlinks')) { return {command:'open-details-relationship', value:'where-used', open:open}; }
    return null;
  }
  return function(event) {
    var target = event.target, command = null, pointer = null;
    if (target.closest('#kg_tutorials_section, #kg_splash_start_tutorial')) {
      return {warning:'Stop recording before opening another tutorial.', block:true};
    }
    if (event.type === 'click') {
      var hit = target.closest('#kg_concept_list [data-concept-id], #kg_concept_list [data-module-id]');
      if (hit) {
        var object = hit.hasAttribute('data-concept-id') ? 'concept:' + hit.dataset.conceptId : 'module:' + hit.dataset.moduleId;
        return {command:{command:'select', target:object}, pointer:'search:' + object};
      }
      if (target.closest('#kg_brand_home')) { command = {command:'home'}; }
      if (target.closest('#kg_graph_selection')) { command = {command:'set-view', value:'both'}; }
      if (target.closest('#kg_search_close') || (target.closest('#kg_search_toggle') && document.getElementById('kg_search_section').open)) { command = {command:'close-search'}; }
      else if (target.closest('#kg_search_toggle')) { command = {command:'search', query:document.getElementById('kg_search').value}; pointer = 'control:search'; }
      var summary = target.closest('#info_panel summary');
      if (summary && target.closest('button, input, a, label, select, textarea')) { summary = null; }
      if (summary) { command = disclosure(summary.parentElement, !summary.parentElement.open); }
      var toggle = target.closest('[data-reading-toggle]');
      if (toggle) { var entry = document.getElementById(toggle.dataset.readingToggle); command = disclosure(entry, !entry.open); }
      var toc = target.closest('.concept-toc-link');
      if (toc) { command = disclosure(document.getElementById(toc.dataset.tocTarget), true); }
      var fold = target.closest('.kg-content-refold');
      if (fold) {
        var footer = fold.closest('.kg-content-footer');
        var owner = footer && footer.parentElement;
        command = disclosure(owner && (owner.tagName === 'DETAILS' ? owner : owner.closest('details')), false);
      }
      var show = target.closest('.concept-relationship-show-graph');
      if (show) {
        var full = show.closest('details').querySelector('.concept-full-tree-toggle input');
        command = {command:'show-relationship-in-graph', preset:show.dataset.contextPreset, full_tree:Boolean(full && full.checked)};
        pointer = command.preset === 'uses' ? 'details:where-used-show-graph' : 'details:derived-from-show-graph';
      }
      if (target.closest('#kg_modules_collapse_all, #kg_modules_expand_all')) {
        command = {command:'set-all-module-representations', value:target.closest('#kg_modules_collapse_all') ? 'folded' : 'expanded'};
      }
    } else {
      command = options.reading.commandFor(target);
      if (target.matches('.concept-derived-from-full-tree, .concept-backlinks-full-tree')) {
        command = {command:'set-relationship-full-tree', value:target.matches('.concept-derived-from-full-tree') ? 'derived-from' : 'where-used', full_tree:target.checked};
      }
    }
    if (command) { return {command:command, pointer:pointer}; }
    if (target.closest('.kg-add-note, .kg-note-block-action, .kg-note-owner-action, .user-note, .content-block-read-toggle, .study-question, #kg_personal_data_section, #kg_layouts_section')) {
      return {warning:'Personal data and layout edits are not recorded. Undo only restores the viewer.'};
    }
    if (target.closest('#info_panel summary, [data-reading-toggle], [data-reading-focus], .kg-reading-return, [data-reading-extend], #kg_content_unfold_all, #kg_content_fold_all, .concept-link, #kg_history_back, #kg_history_forward')) {
      return {warning:'This operation is not recorded yet. Use supported controls or edit the card afterwards.'};
    }
    return null;
  };
}
