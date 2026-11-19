"""Move from personal playback to the current card, revise and continue."""
import pytest
from playwright.sync_api import expect
from test_personal_tutorials import tutorial_graph, _library, _saved


def _at_card(page, index):
    page.wait_for_function('(index)=>kgTutorialPlaybackSnapshot().stepIndex===index && !kgTutorialPlaybackSnapshot().transitioning',arg=index)


@pytest.mark.browser
@pytest.mark.parametrize('width,from_editor',[(390,False),(1280,True)])
def test_edit_current_personal_card_replays_revision_and_preserves_return_view(tutorial_graph,width,from_editor):
    page=_library(tutorial_graph)
    page.set_viewport_size({'width':width,'height':900})
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    page.locator('#kg_tutorial_intro_copy').click()
    editor=page.locator('#kg_tutorial_editor')
    expect(editor).to_have_attribute('open','')
    tutorial_id=editor.get_attribute('data-tutorial-id')
    original=page.evaluate('(id)=>kgPersonalData.tutorials.get(id)',tutorial_id)
    if not from_editor:
        page.keyboard.press('Escape')
    before=page.evaluate('kgCaptureTutorialPresentation()')
    page.locator('#kg_tutorial_editor_from' if from_editor else '#kg_tutorial_start').click()
    _at_card(page,0)
    page.locator('#kg_tutorial_next').click()
    _at_card(page,1)
    edit=page.get_by_role('button',name='Edit card',exact=True)
    expect(edit).to_be_visible()
    edit.click()
    expect(editor).to_have_attribute('open','')
    assert page.locator('#kg_tutorial_editor_card').input_value()=='1'
    assert page.locator('#kg_tutorial_editor_card_title').input_value()==original['route']['steps'][1]['title']
    assert page.locator('#kg_tutorial_editor_commentary').evaluate('e=>e===document.activeElement')
    page.locator('#kg_tutorial_editor_commentary').fill('My improved explanation of this step.')
    _saved(page)
    page.locator('#kg_tutorial_editor_from').click()
    _at_card(page,1)
    expect(page.locator('#kg_tutorial_commentary')).to_have_text('My improved explanation of this step.')
    page.locator('#kg_tutorial_next').click()
    _at_card(page,2)
    edit.click()
    expect(editor).to_have_attribute('open','')
    assert page.locator('#kg_tutorial_editor_card').input_value()=='2'
    page.locator('#kg_tutorial_editor_from').click()
    _at_card(page,2)
    page.locator('#kg_tutorial_exit').click()
    expect(editor).not_to_have_attribute('open','')
    after=page.evaluate('kgCaptureTutorialPresentation()')
    for key in ['selection','contextRule','displayScope','view','moduleRepresentation','camera']:
        assert after[key]==before[key]
    assert page.evaluate('tutorialData.find(t=>t.tutorial_id==="viewer-tour").steps[1].commentary')==original['route']['steps'][1]['commentary']
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_builtin_playback_has_no_edit_card_action(tutorial_graph):
    page=_library(tutorial_graph)
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    page.locator('#kg_tutorial_start').click()
    _at_card(page,0)
    expect(page.locator('#kg_tutorial_edit')).to_be_hidden()
    page.evaluate('document.getElementById("kg_tutorial_edit").click()')
    assert page.evaluate('kgTutorialPlaybackSnapshot().tutorialId')=='viewer-tour'
    assert not page.locator('#kg_tutorial_editor').evaluate('e=>e.open')


@pytest.mark.browser
def test_edit_deleted_personal_tutorial_reports_error_without_losing_playback(tutorial_graph):
    page=_library(tutorial_graph)
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    page.locator('#kg_tutorial_intro_copy').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    tutorial_id=page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.keyboard.press('Escape')
    page.locator('#kg_tutorial_start').click()
    _at_card(page,0)
    page.evaluate('async id=>{const r=await kgPersonalData.tutorials.get(id);await kgPersonalData.tutorials.remove(id,r.revisionId);}',tutorial_id)
    page.get_by_role('button',name='Edit card',exact=True).click()
    expect(page.locator('#kg_tutorial_error')).to_be_visible()
    assert page.evaluate('kgTutorialPlaybackSnapshot().tutorialId')==tutorial_id
    assert not page.locator('#kg_tutorial_exit').is_disabled()
    assert not page.locator('#kg_tutorial_editor').evaluate('e=>e.open')


@pytest.mark.browser
def test_edit_finds_current_card_by_identity_after_library_reordering(tutorial_graph):
    page=_library(tutorial_graph)
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    page.locator('#kg_tutorial_intro_copy').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    tutorial_id=page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.keyboard.press('Escape')
    page.locator('#kg_tutorial_start').click()
    _at_card(page,0)
    page.locator('#kg_tutorial_next').click()
    _at_card(page,1)
    page.evaluate('''async id=>{
      const r=await kgPersonalData.tutorials.get(id);
      r.route.steps[1].commentary='Latest narration for the current card.';
      r.route.steps.unshift({step_id:'new-opening',title:'Added opening',commentary:'A newly inserted card.',action:{command:'wait',milliseconds:0},pointer:{target:'narration'}});
      await kgPersonalData.tutorials.save(r);
    }''',tutorial_id)
    page.get_by_role('button',name='Edit card',exact=True).click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    assert page.locator('#kg_tutorial_editor_card').input_value()=='2'
    expect(page.locator('#kg_tutorial_editor_commentary')).to_have_value('Latest narration for the current card.')
    page.locator('#kg_tutorial_editor_from').click()
    _at_card(page,2)
    expect(page.locator('#kg_tutorial_commentary')).to_have_text('Latest narration for the current card.')
