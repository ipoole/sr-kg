"""Single-card action capture uses normal controls and reversible presentation checkpoints."""
import pytest
from playwright.sync_api import expect
from test_personal_tutorials import tutorial_graph, _library, _fill_draft, _record


def _idle(page):
    expect(page.locator('#kg_tutorial_recording')).to_have_attribute('data-busy', 'false')


def _start(page, original=None):
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    if original is not None:
        original.append(page.evaluate('kgCaptureTutorialPresentation()'))
    page.locator('#kg_tutorial_editor_record').click()
    expect(page.locator('#kg_tutorial_recording')).to_be_visible()
    _idle(page)
    return tutorial_id


def _control(page, selector, value):
    page.locator(selector).select_option(value)
    _idle(page)


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_record_controls_undo_redo_replay_and_reload(tutorial_graph, width):
    page = _library(tutorial_graph)
    page.set_viewport_size({'width':width, 'height':900})
    original = []
    tutorial_id = _start(page, original)
    before = original[0]
    _control(page, '#kg_view_select', 'graph')
    _control(page, '#kg_display_scope_select', 'full')
    _control(page, '#kg_context_preset_select', 'uses')
    _control(page, '#kg_context_depth_select', 'three-hops')
    state = page.evaluate('kgCaptureTutorialPresentation()')
    page.locator('#kg_tutorial_recording_undo').click()
    _idle(page)
    assert page.evaluate('kgCaptureTutorialPresentation().contextRule.depth') == 'two-hops'
    page.locator('#kg_tutorial_recording_redo').click()
    _idle(page)
    assert page.evaluate('kgCaptureTutorialPresentation().contextRule') == state['contextRule']
    step = _record(page, tutorial_id)['route']['steps'][0]
    page.locator('#kg_tutorial_recording_replay').click()
    _idle(page)
    assert page.evaluate('kgCaptureTutorialPresentation().contextRule') == state['contextRule']
    page.locator('#kg_tutorial_recording_stop').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open', '')
    saved = _record(page, tutorial_id)['route']['steps'][0]
    assert saved == step
    assert saved['prepare'] == [{'command':'home'}]
    assert [item['action']['command'] for item in saved['actions']] == ['set-view', 'set-display-scope', 'set-context', 'set-context']
    restored = page.evaluate('kgCaptureTutorialPresentation()')
    for key in ['selection','contextRule','displayScope','view']:
        assert restored[key] == before[key]
    assert restored['camera']['scale'] == pytest.approx(before['camera']['scale'])
    for axis in ['x','y']:
        assert restored['camera']['position'][axis] == pytest.approx(before['camera']['position'][axis])
    page.locator('#kg_tutorial_editor_play').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.locator('#kg_tutorial_error').is_hidden()
    played = page.evaluate('kgCaptureTutorialPresentation()')
    for key in ['selection','contextRule','displayScope','view']:
        assert played[key] == state[key]
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_record_search_selection_fit_and_redo_branch(tutorial_graph):
    page = _library(tutorial_graph)
    tutorial_id = _start(page)
    page.locator('#kg_search_toggle').click()
    _idle(page)
    page.locator('#kg_search').fill('Beta')
    # Clicking the result flushes a pending query; it need not wait for the debounce.
    page.locator('#kg_concept_list [data-concept-id="2.1"]').click()
    _idle(page)
    page.locator('#kg_search_close').click()
    _idle(page)
    # This fixture's Beta -> Alpha link is REQUIRES, so include it in the context.
    _control(page, '#kg_context_preset_select', 'foundations')
    page.locator('#kg_fit_apply').click()
    _idle(page)
    page.locator('#kg_fit_apply').click()
    _idle(page)
    assert page.evaluate('kgCaptureTutorialPresentation().contextFit.contraction') is not None
    page.locator('#kg_tutorial_recording_undo').click()
    _idle(page)
    assert page.evaluate('kgCaptureTutorialPresentation().contextFit.contraction') is None
    _control(page, '#kg_view_select', 'details')
    assert page.locator('#kg_tutorial_recording_redo').is_disabled()
    page.locator('#kg_tutorial_recording_stop').click()
    step = _record(page, tutorial_id)['route']['steps'][0]
    actions = step['actions']
    queries = [item['action']['query'] for item in actions if item['action']['command']=='search']
    assert queries == ['', 'Beta']
    selection = next(item for item in actions if item['action']['command']=='select')
    assert selection['action']['target'] == 'concept:2.1'
    assert selection['pointer']['target'] == 'search:concept:2.1'
    assert sum(item['action']['command']=='fit' for item in actions) == 1
    assert actions[-1]['action'] == {'command':'set-view','value':'details'}
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_recording_appends_and_capacity_does_not_mutate_view(tutorial_graph):
    page = _library(tutorial_graph)
    tutorial_id = _start(page)
    page.evaluate("""async()=>{
      for(let i=0;i<20;i++)await kgExecuteViewerCommand({command:'set-view',value:'graph'},{origin:'user'});
    }""")
    _idle(page)
    _control(page, '#kg_view_select', 'details')
    assert page.evaluate('kgCaptureTutorialPresentation().view') == 'graph'
    page.locator('#kg_tutorial_recording_stop').click()
    assert len(_record(page,tutorial_id)['route']['steps'][0]['actions']) == 20
    page.locator('#kg_tutorial_editor_record').click()
    _idle(page)
    assert page.locator('#kg_tutorial_recording_undo').is_disabled()
    page.locator('#kg_tutorial_recording_stop').click()
    assert len(_record(page,tutorial_id)['route']['steps'][0]['actions']) == 20


@pytest.mark.browser
def test_record_details_and_reading_controls_without_personal_read_marks(tutorial_graph):
    page = _library(tutorial_graph)
    tutorial_id = _start(page)
    page.evaluate("kgExecuteViewerCommand({command:'select',target:'concept:2.1'},{origin:'user'})")
    _idle(page)
    block = page.locator('#info_panel > details[data-content-block-id="2.1.explanation"]')
    block.locator(':scope > summary').click()
    _idle(page)
    assert block.evaluate('e=>e.open')
    tick = block.locator(':scope > summary .content-block-read-toggle')
    tick.check()
    page.locator('#kg_tutorial_recording_undo').click()
    _idle(page)
    assert not block.evaluate('e=>e.open')
    assert block.locator(':scope > summary .content-block-read-toggle').is_checked()
    page.locator('#kg_tutorial_recording_redo').click()
    _idle(page)
    tree = page.locator('.kg-reading-tree[data-reading-recipe="teaching"]')
    tree.locator(':scope > summary').click()
    _idle(page)
    assert tree.evaluate('e=>e.open')
    depth = tree.locator('[data-reading-depth="teaching"]')
    depth.select_option('three-hops')
    _idle(page)
    tree.locator('[data-reading-toggle]').first.click()
    _idle(page)
    child = tree.locator('.kg-reading-concept[open]').first
    node_id = child.get_attribute('data-reading-node')
    borrowed = child.locator('details[data-content-block-id]').first
    block_id = borrowed.get_attribute('data-content-block-id')
    borrowed.locator(':scope > summary').click()
    _idle(page)
    assert borrowed.evaluate('e=>e.open')
    tree.locator('.kg-reading-sync').check()
    _idle(page)
    tree.locator('.kg-reading-sync').uncheck()
    _idle(page)
    page.locator('#kg_tutorial_recording_stop').click()
    actions = [item['action'] for item in _record(page,tutorial_id)['route']['steps'][0]['actions']]
    assert actions[1] == {'command':'open-details-block','target':'block:2.1.explanation','open':True}
    reading = [item for item in actions if item['command']=='open-reading-tree']
    assert reading == [
        {'command':'open-reading-tree','recipe':'teaching','open':True},
        {'command':'open-reading-tree','recipe':'teaching','depth':'three-hops'},
        {'command':'open-reading-tree','recipe':'teaching','target':'concept:'+node_id,'open':True},
        {'command':'open-reading-tree','recipe':'teaching','target':'concept:'+node_id,'block':'block:'+block_id,'open':True},
        {'command':'open-reading-tree','recipe':'teaching','synchronise':True},
        {'command':'open-reading-tree','recipe':'teaching','synchronise':False}]
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_pending_search_is_undoable_and_enter_records_selection(tutorial_graph):
    page = _library(tutorial_graph)
    tutorial_id = _start(page)
    page.locator('#kg_search_toggle').click()
    _idle(page)
    page.locator('#kg_search').fill('Beta')
    page.locator('#kg_search').press('Enter')
    page.wait_for_function("kgViewerStateSnapshot().selection.id==='2.1'")
    _idle(page)
    page.locator('#kg_tutorial_recording_undo').click()
    _idle(page)
    page.locator('#kg_tutorial_recording_undo').click()
    _idle(page)
    assert page.locator('#kg_search').input_value() == ''
    page.locator('#kg_tutorial_recording_redo').click()
    _idle(page)
    assert page.locator('#kg_search').input_value() == 'Beta'
    page.locator('#kg_tutorial_recording_stop').click()
    actions = _record(page,tutorial_id)['route']['steps'][0]['actions']
    assert [item['action']['command'] for item in actions] == ['search', 'search']


@pytest.mark.browser
def test_recording_preparation_is_visible_and_blocks_other_actions(tutorial_graph):
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    page.locator('#kg_tutorial_editor_setup_section').evaluate('e=>e.open=true')
    setup = page.locator('#kg_tutorial_editor_setup')
    setup.get_by_role('button',name='Add action',exact=True).click()
    setup.get_by_label('Action type',exact=True).select_option('wait')
    setup.locator('[data-field="milliseconds"]').fill('4')
    # Gate just this preparation timer; do not depend on a short wall-clock window.
    page.evaluate('''()=>{
      const schedule=window.setTimeout;
      window.setTimeout=(callback,delay,...args)=>{
        if(delay===4000){window.__finishRecordingPreparation=()=>{window.setTimeout=schedule;schedule(callback,0,...args);};return 0;}
        return schedule(callback,delay,...args);
      };
    }''')
    page.locator('#kg_tutorial_editor_record').click()
    page.wait_for_function("typeof __finishRecordingPreparation==='function'")
    expect(page.locator('#kg_tutorial_recording')).to_be_visible()
    assert page.locator('#kg_tutorial_recording_stop').is_disabled()
    before = page.evaluate('kgCaptureTutorialPresentation().view')
    page.locator('#kg_view_select').evaluate("e=>{e.value='details';e.dispatchEvent(new Event('change',{bubbles:true}));}")
    assert page.evaluate('kgCaptureTutorialPresentation().view') == before
    page.evaluate('__finishRecordingPreparation()')
    _idle(page)
    page.locator('#kg_tutorial_recording_stop').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')


@pytest.mark.browser
def test_recording_cannot_start_during_a_learners_explore(tutorial_graph):
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    page.locator('#kg_tutorial_start').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    page.locator('#kg_tutorial_explore').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().exploring')
    _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    assert page.locator('#kg_tutorial_editor_record').is_disabled()
    assert page.locator('#kg_tutorial_recording').is_hidden()
    page.locator('#kg_tutorial_editor_close').click()
    page.locator('#kg_tutorial_explore').click()
    page.wait_for_function('!kgTutorialPlaybackSnapshot().exploring && !kgTutorialPlaybackSnapshot().transitioning')
    page.locator('#kg_tutorial_exit').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().tutorialId===null')
    page.locator('#kg_tutorial_intro_edit').click()
    assert page.locator('#kg_tutorial_editor_record').is_enabled()
