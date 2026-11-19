"""Personal tutorial drafts are independent of built-ins and the legacy profile."""
import pytest
from playwright.sync_api import expect
from conftest import _open_browser_graph


@pytest.fixture
def tutorial_graph(fast_browser_fixture_output, playwright_browser):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, fast_browser_fixture_output) as graph:
        yield graph


def _library(graph):
    page = graph.page
    if not page.locator('#kg_controls').is_visible():
        page.locator('#kg_controls_toggle').click()
    graph.open_control_section('kg_tutorials_section')
    page.wait_for_selector('#kg_tutorial_library_status[data-ready="true"]', state='attached')
    return page


def _edit_selected_tutorial(page):
    if page.locator('#kg_tutorial_intro_edit').is_visible():
        page.locator('#kg_tutorial_intro_edit').click()
    else:
        page.locator('#kg_tutorial_start').click()
        page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0&&!kgTutorialPlaybackSnapshot().transitioning')
        page.locator('#kg_tutorial_edit').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')


def _saved(page):
    expect(page.locator('#kg_tutorial_editor_status')).to_have_attribute('data-state', 'saved')


def _fill_draft(page):
    page.locator('#kg_tutorial_editor_title').fill('My learning route')
    page.locator('#kg_tutorial_editor_summary').fill('A short personal introduction.')
    advanced=page.locator('#kg_tutorial_editor_advanced')
    was_open=advanced.evaluate('e=>e.open')
    advanced.evaluate('e=>e.open=true')
    page.locator('#kg_tutorial_editor_author').fill('A learner')
    advanced.evaluate('(e,open)=>e.open=open',was_open)
    page.locator('#kg_tutorial_editor_card_title').fill('First result')
    page.locator('#kg_tutorial_editor_commentary').fill(r'Read this result: \(x^2=1\).')
    _saved(page)


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_new_tutorial_is_one_saved_card_and_reopens_in_the_same_editor(tutorial_graph, width):
    page = _library(tutorial_graph)
    page.set_viewport_size({'width': width, 'height': 900})
    before = page.evaluate('kgPersonalData.getSnapshot()')
    page.locator('#kg_tutorial_new').click()
    editor = page.locator('#kg_tutorial_editor')
    expect(editor).to_have_attribute('open', '')
    tutorial_id = editor.get_attribute('data-tutorial-id')
    assert tutorial_id.startswith('personal:')
    assert page.locator('#kg_tutorial_editor_card option').count() == 1
    assert page.locator('#kg_tutorial_editor_commentary').input_value() == ''
    assert page.locator('#kg_tutorial_editor_from').is_enabled()
    _fill_draft(page)
    page.keyboard.press('Escape')
    # An old-profile archive round trip must not erase the separate tutorials.
    page.evaluate('''()=>kgPersonalData.replaceSnapshot(kgPersonalDataArchive.importBytes(
        kgPersonalDataArchive.exportBytes(kgPersonalData.getSnapshot())))''')
    page.reload(wait_until='domcontentloaded')
    _library(tutorial_graph)
    page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]').click()
    _edit_selected_tutorial(page)
    assert page.locator('#kg_tutorial_editor_title').input_value() == 'My learning route'
    assert page.locator('#kg_tutorial_editor_card_title').input_value() == 'First result'
    assert page.locator('#kg_tutorial_editor_author').input_value() == 'A learner'
    assert page.locator('#kg_tutorial_editor_commentary').input_value() == r'Read this result: \(x^2=1\).'
    assert page.locator('#kg_tutorial_editor_card option').count() == 1
    after = page.evaluate('kgPersonalData.getSnapshot()')
    for name in ['notes', 'layout', 'studyResults', 'studyResets', 'readingProgress']:
        assert after[name] == before[name]
    assert editor.evaluate('e=>e.scrollWidth<=e.clientWidth+1')
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_builtin_copy_keeps_actions_and_can_be_edited_and_deleted_independently(tutorial_graph):
    page = _library(tutorial_graph)
    source = page.evaluate('tutorialData.find(t=>t.tutorial_id==="viewer-tour")')
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    page.locator('#kg_tutorial_intro_copy').click()
    editor = page.locator('#kg_tutorial_editor')
    expect(editor).to_have_attribute('open', '')
    tutorial_id = editor.get_attribute('data-tutorial-id')
    page.locator('#kg_tutorial_editor_title').fill('My revised orientation')
    page.locator('#kg_tutorial_editor_card').select_option(index=1)
    page.locator('#kg_tutorial_editor_card_title').fill('A revised second card')
    page.locator('#kg_tutorial_editor_commentary').fill('Pay attention to the context controls.')
    _saved(page)
    page.keyboard.press('Escape')
    record = page.evaluate('(id)=>kgPersonalData.tutorials.get(id)', tutorial_id)
    assert record['basedOn']['tutorialId'] == 'viewer-tour'
    assert record['route']['steps'][1]['step_id'] == source['steps'][1]['step_id']
    for original, copied in zip(source['steps'], record['route']['steps']):
        for name in ['action', 'actions', 'prepare', 'pointer']:
            assert copied.get(name) == original.get(name)
    assert page.evaluate('tutorialData.find(t=>t.tutorial_id==="viewer-tour")') == source
    page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]').click()
    page.locator('#kg_tutorial_start').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    page.locator('#kg_tutorial_next').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===1 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.locator('#kg_tutorial_step_title').inner_text() == 'A revised second card'
    assert page.locator('#kg_tutorial_error').is_hidden()
    page.locator('#kg_tutorial_exit').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().tutorialId === null')
    page.once('dialog', lambda dialog: dialog.dismiss())
    page.locator('#kg_tutorial_intro_delete').click()
    assert page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]').count() == 1
    page.once('dialog', lambda dialog: dialog.accept())
    page.locator('#kg_tutorial_intro_delete').click()
    expect(page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]')).to_have_count(0)
    assert page.evaluate('(id)=>kgPersonalData.tutorials.get(id)', tutorial_id)['deletedAt']
    assert page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').count() == 1


@pytest.mark.browser
def test_personal_playback_is_frozen_and_exit_leaves_the_editor_closed(tutorial_graph):
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    before = page.evaluate('kgCaptureTutorialPresentation()')
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.evaluate('kgTutorialPlaybackSnapshot().tutorialId') == tutorial_id
    assert page.locator('#kg_tutorial_error').is_hidden()
    expect(page.locator('#kg_tutorial_editor')).not_to_have_attribute('open', '')
    commentary = page.locator('#kg_tutorial_commentary').inner_text()
    page.evaluate('''async id=>{
        const record=await kgPersonalData.tutorials.get(id);
        record.route.steps[0].commentary='A later library revision.';
        await kgPersonalData.tutorials.save(record);
    }''', tutorial_id)
    assert page.locator('#kg_tutorial_commentary').inner_text() == commentary
    page.locator('#kg_tutorial_exit').click()
    expect(page.locator('#kg_tutorial_editor')).not_to_have_attribute('open', '')
    assert page.locator('#kg_tutorial_editor_title').input_value() == 'My learning route'
    after = page.evaluate('kgCaptureTutorialPresentation()')
    for name in ['selection', 'contextRule', 'displayScope', 'view', 'camera']:
        assert after[name] == before[name]
    assert not tutorial_graph.page_errors


@pytest.mark.browser
@pytest.mark.parametrize('handoff', ['close', 'continue', 'record'])
def test_failed_save_retains_the_draft_and_retry_persists_it(tutorial_graph, handoff):
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.evaluate('''()=>{
        window.__tutorialSave=kgPersonalData.tutorials.save;
        kgPersonalData.tutorials.save=()=>Promise.reject(new Error('Storage full'));
    }''')
    page.locator('#kg_tutorial_editor_title').fill('Keep my unsaved title')
    expect(page.locator('#kg_tutorial_editor_status')).to_have_attribute('data-state', 'error')
    if handoff == 'close':
        page.get_by_role('button',name='Done editing',exact=True).click()
    else:
        page.locator('#kg_tutorial_editor_' + ('from' if handoff == 'continue' else 'record')).click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open', '')
    assert page.locator('#kg_tutorial_editor_title').input_value() == 'Keep my unsaved title'
    assert page.evaluate('kgTutorialPlaybackSnapshot().tutorialId') is None
    assert page.locator('#kg_tutorial_recording').is_hidden()
    assert page.evaluate('(id)=>kgPersonalData.tutorials.get(id)', tutorial_id)['route']['title'] != 'Keep my unsaved title'
    page.evaluate('()=>{kgPersonalData.tutorials.save=window.__tutorialSave;}')
    page.locator('#kg_tutorial_editor_retry').click()
    _saved(page)
    assert page.evaluate('(id)=>kgPersonalData.tutorials.get(id)', tutorial_id)['route']['title'] == 'Keep my unsaved title'


@pytest.mark.browser
def test_tutorial_store_rejects_stale_edits_without_overwriting(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async ()=>{
        const store=kgPersonalData.tutorials, first=await store.create();
        const stale=JSON.parse(JSON.stringify(first));
        first.route.title='Saved newer title';
        const newer=await store.save(first);
        stale.route.title='Stale title';
        let rejected=false, deleteRejected=false;
        try { await store.save(stale); } catch(error) { rejected=true; }
        try { await store.remove(first.id, stale.revisionId); } catch(error) { deleteRejected=true; }
        return {rejected, deleteRejected, stored:await store.get(first.id), newer};
    }''')
    assert result['rejected'] and result['deleteRejected']
    assert result['stored'] == result['newer']


@pytest.mark.browser
def test_unavailable_personal_storage_leaves_builtin_playback_usable(tutorial_graph):
    page = tutorial_graph.page
    page.add_init_script("Object.defineProperty(window,'indexedDB',{value:null})")
    page.reload(wait_until='domcontentloaded')
    tutorial_graph.open_control_section('kg_tutorials_section')
    expect(page.locator('#kg_tutorial_library_retry')).to_be_visible()
    assert page.locator('#kg_tutorial_new').is_disabled()
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    page.locator('#kg_tutorial_start').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.evaluate('kgTutorialPlaybackSnapshot().tutorialId') == 'viewer-tour'
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_personal_tutorial_launch_url_waits_for_saved_library(tutorial_graph):
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.keyboard.press('Escape')
    page.goto(tutorial_graph.output_path.as_uri()+'?tutorial='+tutorial_id, wait_until='domcontentloaded')
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.evaluate('kgTutorialPlaybackSnapshot().tutorialId') == tutorial_id
    assert page.locator('#kg_tutorial_error').is_hidden()
    assert page.locator('#kg_tutorial_intro_author').inner_text() == 'By A learner'
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_done_waits_for_pending_save_and_keeps_later_typing(tutorial_graph):
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _saved(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.evaluate('''()=>{
        const original=kgPersonalData.tutorials.save;
        let delay=true;
        kgPersonalData.tutorials.save=async record=>{
            const result=await original(record);
            if(delay){delay=false;await new Promise(resolve=>{window.__finishTutorialSave=resolve;});}
            return result;
        };
    }''')
    page.locator('#kg_tutorial_editor_title').fill('Earlier edit')
    page.wait_for_function("typeof window.__finishTutorialSave==='function'")
    page.locator('#kg_tutorial_editor_title').fill('Latest edit')
    page.locator('#kg_tutorial_editor_summary').fill('Keep this later summary.')
    page.keyboard.press('Escape')
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open', '')
    page.evaluate('()=>window.__finishTutorialSave()')
    expect(page.locator('#kg_tutorial_editor')).not_to_have_attribute('open', '')
    saved = page.evaluate('(id)=>kgPersonalData.tutorials.get(id)', tutorial_id)
    assert saved['route']['title'] == 'Latest edit'
    assert saved['route']['summary'] == 'Keep this later summary.'


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_long_tutorial_library_keeps_start_reachable(tutorial_graph, width):
    page = _library(tutorial_graph)
    page.set_viewport_size({'width': width, 'height': 800})
    page.evaluate('''async()=>{
        for(let i=0;i<8;i++)await kgPersonalData.tutorials.create();
    }''')
    page.reload(wait_until='domcontentloaded')
    _library(tutorial_graph)
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    bounds = page.locator('#kg_controls').bounding_box()
    assert bounds['y'] + bounds['height'] <= 800
    assert page.locator('#kg_controls').evaluate('e=>e.scrollHeight>e.clientHeight')
    page.locator('#kg_tutorial_start').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.locator('#kg_tutorial_error').is_hidden()


def _copy_editor(page):
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    page.locator('#kg_tutorial_intro_copy').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open', '')
    return page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')


def _record(page, tutorial_id):
    # Finish restores the viewer before committing the replacement draft.
    expect(page.locator('#kg_tutorial_recording')).not_to_have_attribute('data-busy','true')
    _saved(page)
    return page.evaluate('(id)=>kgPersonalData.tutorials.get(id)', tutorial_id)


@pytest.mark.browser
def test_card_operations_keep_identity_and_allow_an_empty_draft(tutorial_graph):
    page = _library(tutorial_graph)
    tutorial_id = _copy_editor(page)
    original = _record(page, tutorial_id)['route']['steps']
    controls = page.locator('#kg_tutorial_editor_card_controls')
    controls.get_by_role('button', name='Duplicate card', exact=True).click()
    copied = _record(page, tutorial_id)['route']['steps']
    assert copied[1]['step_id'] != original[0]['step_id']
    assert {k:v for k,v in copied[1].items() if k != 'step_id'} == {k:v for k,v in original[0].items() if k != 'step_id'}
    page.locator('#kg_tutorial_editor_advanced').evaluate('e=>e.open=true')
    page.locator('[data-card-action="down"]').click()
    assert _record(page, tutorial_id)['route']['steps'][2]['step_id'] == copied[1]['step_id']
    page.locator('[data-card-action="up"]').click()
    page.locator('[data-card-action="up"]').click()
    assert _record(page, tutorial_id)['route']['steps'][0]['step_id'] == copied[1]['step_id']
    page.once('dialog', lambda dialog: dialog.dismiss())
    controls.get_by_role('button', name='Delete card', exact=True).click()
    assert len(_record(page, tutorial_id)['route']['steps']) == 7
    page.on('dialog', lambda dialog: dialog.accept())
    for _ in range(7):
        controls.get_by_role('button', name='Delete card', exact=True).click()
    assert not _record(page, tutorial_id)['route']['steps']
    assert page.locator('#kg_tutorial_editor_card_title').is_disabled()
    assert page.locator('#kg_tutorial_editor_from').is_disabled()
    controls.get_by_role('button', name='Add card', exact=True).click()
    assert len(_record(page, tutorial_id)['route']['steps']) == 1
    assert page.locator('#kg_tutorial_editor_commentary').input_value() == ''
    assert page.locator('#kg_tutorial_editor_from').is_enabled()


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_edit_action_sequence_preserves_legacy_setup_pointers_and_pause(tutorial_graph, width):
    page = _library(tutorial_graph)
    page.set_viewport_size({'width':width, 'height':900})
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.keyboard.press('Escape')
    page.evaluate('''async id=>{
      const r=await kgPersonalData.tutorials.get(id);r.route.steps[0].prepare=[{command:'set-view',value:'graph'}];
      await kgPersonalData.tutorials.save(r);
    }''',tutorial_id)
    page.reload(wait_until='domcontentloaded');_library(tutorial_graph)
    page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]').click()
    _edit_selected_tutorial(page)
    page.locator('#kg_tutorial_editor_advanced').evaluate('e=>e.open=true')
    actions = page.locator('#kg_tutorial_editor_actions')
    actions.get_by_role('button', name='Add action', exact=True).click()
    actions.locator('[data-field="target"]').select_option('concept:2.1')
    actions.get_by_label('Pause before the next action (seconds)', exact=True).fill('1.2')
    actions.get_by_role('button', name='Add action', exact=True).click()
    actions.get_by_label('Action type', exact=True).select_option('set-context')
    actions.locator('[data-field="preset"]').select_option('uses')
    actions.locator('[data-field="depth"]').select_option('three-hops')
    actions.get_by_label('Pointer area', exact=True).select_option('controls')
    actions.get_by_label('Pointer target', exact=True).select_option('control:depth')
    actions.get_by_role('button', name='Move action up', exact=True).click()
    page.locator('#kg_tutorial_editor_advanced').evaluate('e=>e.open=true')
    step = _record(page, tutorial_id)['route']['steps'][0]
    assert step['prepare'] == [{'command':'set-view', 'value':'graph'}]
    assert 'action' not in step and 'pointer' not in step
    assert step['actions'][0]['action'] == {'command':'set-context', 'preset':'uses', 'depth':'three-hops'}
    assert step['actions'][0]['pointer'] == {'target':'control:depth'}
    assert step['actions'][1]['action'] == {'command':'select', 'target':'concept:2.1'}
    assert step['actions'][1]['pause_ms'] == 1200
    assert step['actions'][1]['pointer'] == {'target':'graph:concept:2.1'}
    assert page.locator('#kg_tutorial_editor').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
    page.keyboard.press('Escape')
    page.reload(wait_until='domcontentloaded')
    _library(tutorial_graph)
    page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]').click()
    _edit_selected_tutorial(page)
    assert _record(page, tutorial_id)['route']['steps'][0] == step
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.locator('#kg_tutorial_error').is_hidden()
    state = page.evaluate('kgCaptureTutorialPresentation()')
    assert state['selection'] == {'type':'concept', 'id':'2.1'}
    assert state['view'] == 'graph'
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_play_from_here_rebuilds_prefix_and_continues(tutorial_graph):
    page = _library(tutorial_graph)
    _copy_editor(page)
    before = page.evaluate('kgCaptureTutorialPresentation()')
    page.locator('#kg_tutorial_editor_card').select_option(index=2)
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===2 && !kgTutorialPlaybackSnapshot().transitioning')
    state = page.evaluate('kgCaptureTutorialPresentation()')
    assert state['selection'] == {'type':'concept', 'id':'2.1'}
    assert state['contextRule']['preset'] == 'uses'
    assert state['displayScope'] == 'context'
    assert page.locator('#kg_tutorial_back').is_enabled()
    assert page.locator('#kg_tutorial_next').is_enabled()
    assert page.locator('#kg_tutorial_error').is_hidden()
    page.locator('#kg_tutorial_exit').click()
    expect(page.locator('#kg_tutorial_editor')).not_to_have_attribute('open', '')
    assert page.locator('#kg_tutorial_editor_card').input_value() == '2'
    restored = page.evaluate('kgCaptureTutorialPresentation()')
    for key in ['selection', 'contextRule', 'view', 'displayScope', 'camera']:
        assert restored[key] == before[key]
    page.locator('#kg_tutorial_start').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    page.locator('#kg_tutorial_edit').click()
    page.locator('#kg_tutorial_editor_card').select_option(index=2)
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===2 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.locator('#kg_tutorial_next').is_enabled()
    page.locator('#kg_tutorial_next').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===3 && !kgTutorialPlaybackSnapshot().transitioning')
    assert page.locator('#kg_search').input_value() == 'Alpha'
    assert page.locator('#kg_tutorial_error').is_hidden()


@pytest.mark.browser
def test_incomplete_routes_block_playback_but_remain_editable(tutorial_graph):
    page = _library(tutorial_graph)
    tutorial_id = _copy_editor(page)
    page.locator('#kg_tutorial_editor_card').select_option(index=5)
    page.locator('#kg_tutorial_editor_card_title').fill('')
    _saved(page)
    page.locator('#kg_tutorial_editor_card').select_option(index=0)
    assert page.locator('#kg_tutorial_editor_from').is_disabled()
    page.locator('#kg_tutorial_editor_card').select_option(index=5)
    page.locator('#kg_tutorial_editor_card_title').fill('Repaired final card.')
    _saved(page)
    page.locator('#kg_tutorial_editor_card').select_option(index=0)
    page.locator('#kg_tutorial_editor_advanced').evaluate('e=>e.open=true')
    actions = page.locator('#kg_tutorial_editor_actions')
    actions.get_by_label('Action type', exact=True).select_option('select')
    assert page.locator('#kg_tutorial_editor_from').is_disabled()
    assert _record(page, tutorial_id)['route']['steps'][0]['actions'][0]['action']['target'] == ''
    actions.get_by_label('Action type', exact=True).select_option('search')
    actions.locator('[data-field="query"]').fill('Beta')
    assert page.locator('#kg_tutorial_editor_from').is_enabled()
    # Text entry must keep focus through each keystroke, rather than rebuilding the form.
    actions.locator('[data-field="query"]').press('End')
    actions.locator('[data-field="query"]').press_sequentially(' route')
    assert actions.locator('[data-field="query"]').input_value() == 'Beta route'


@pytest.mark.browser
def test_rehearsal_error_keeps_exit_and_current_card_edit_available(tutorial_graph):
    page = _library(tutorial_graph)
    _copy_editor(page)
    # A known block can still be unavailable in the selected concept. Do not silently fix the route.
    page.locator('#kg_tutorial_editor_advanced').evaluate('e=>e.open=true')
    actions = page.locator('#kg_tutorial_editor_actions')
    actions.get_by_label('Action type', exact=True).select_option('open-details-block')
    actions.locator('[data-field="target"]').select_option('block:1.1.definition')
    actions.get_by_label('Pointer area', exact=True).select_option('general')
    actions.get_by_label('Pointer target', exact=True).select_option('narration')
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0 && !kgTutorialPlaybackSnapshot().transitioning')
    expect(page.locator('#kg_tutorial_error')).to_be_visible()
    assert page.locator('#kg_tutorial_exit').is_enabled()
    page.locator('#kg_tutorial_edit').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open', '')
