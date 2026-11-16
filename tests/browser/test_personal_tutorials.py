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


def _saved(page):
    expect(page.locator('#kg_tutorial_editor_status')).to_have_attribute('data-state', 'saved')


def _fill_draft(page):
    page.locator('#kg_tutorial_editor_title').fill('My learning route')
    page.locator('#kg_tutorial_editor_summary').fill('A short personal introduction.')
    page.locator('#kg_tutorial_editor_author').fill('A learner')
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
    assert page.locator('#kg_tutorial_editor_play').is_disabled()
    _fill_draft(page)
    page.locator('#kg_tutorial_editor_close').click()
    # An old-profile archive round trip must not erase the separate tutorials.
    page.evaluate('''()=>kgPersonalData.replaceSnapshot(kgPersonalDataArchive.importBytes(
        kgPersonalDataArchive.exportBytes(kgPersonalData.getSnapshot())))''')
    page.reload(wait_until='domcontentloaded')
    _library(tutorial_graph)
    page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]').click()
    page.locator('#kg_tutorial_intro_edit').click()
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
    page.locator('#kg_tutorial_editor_close').click()
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
def test_personal_playback_is_frozen_and_exit_returns_to_the_editor(tutorial_graph):
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    before = page.evaluate('kgCaptureTutorialPresentation()')
    page.locator('#kg_tutorial_editor_play').click()
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
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open', '')
    assert page.locator('#kg_tutorial_editor_title').input_value() == 'My learning route'
    after = page.evaluate('kgCaptureTutorialPresentation()')
    for name in ['selection', 'contextRule', 'displayScope', 'view', 'camera']:
        assert after[name] == before[name]
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_failed_save_retains_the_draft_and_retry_persists_it(tutorial_graph):
    page = _library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    _saved(page)
    tutorial_id = page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.evaluate('''()=>{
        window.__tutorialSave=kgPersonalData.tutorials.save;
        kgPersonalData.tutorials.save=()=>Promise.reject(new Error('Storage full'));
    }''')
    page.locator('#kg_tutorial_editor_title').fill('Keep my unsaved title')
    expect(page.locator('#kg_tutorial_editor_status')).to_have_attribute('data-state', 'error')
    page.locator('#kg_tutorial_editor_close').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open', '')
    assert page.locator('#kg_tutorial_editor_title').input_value() == 'Keep my unsaved title'
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
    page.locator('#kg_tutorial_editor_close').click()
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
    page.locator('#kg_tutorial_editor_close').click()
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
