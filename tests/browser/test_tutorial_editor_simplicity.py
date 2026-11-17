"""The ordinary editor stays focused on narration and always-visible recording/playback."""
import pytest
from playwright.sync_api import expect
from test_personal_tutorials import tutorial_graph, _library, _fill_draft, _saved


@pytest.mark.browser
@pytest.mark.parametrize('width,height',[(390,700),(1280,900)])
def test_editor_footer_stays_visible_and_advanced_is_last(tutorial_graph,width,height):
    page=_library(tutorial_graph)
    page.set_viewport_size({'width':width,'height':height})
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    footer=page.locator('#kg_tutorial_editor_footer')
    initial=footer.bounding_box()
    assert initial['y']>=0 and initial['y']+initial['height']<=height
    assert not page.locator('#kg_tutorial_editor_author').is_visible()
    assert not page.locator('#kg_tutorial_editor_domains').is_visible()
    assert page.locator('#kg_tutorial_editor_preview').count()==0
    assert page.locator('#kg_tutorial_editor_order').count()==0
    assert page.locator('#kg_tutorial_editor_card_controls [data-card-action]').count()==3
    assert not page.locator('[data-card-action="up"]').is_visible()
    advanced=page.locator('#kg_tutorial_editor_advanced')
    advanced.locator('summary').click()
    assert page.locator('#kg_tutorial_editor_author').is_visible()
    assert page.locator('#kg_tutorial_editor_domains').is_visible()
    assert page.locator('[data-card-action="up"]').is_visible()
    assert advanced.evaluate('e=>e===document.getElementById("kg_tutorial_editor_fields").lastElementChild')
    pinned=footer.bounding_box()
    body=page.locator('#kg_tutorial_editor_body')
    for fraction in [0,1,0.5]:
        body.evaluate('(e,f)=>{e.scrollTop=e.scrollHeight*f;}',fraction)
        bounds=footer.bounding_box()
        assert bounds['y']==pytest.approx(pinned['y'],abs=1)
        assert bounds['y']+bounds['height']<=height
    assert page.locator('#kg_tutorial_editor').evaluate('e=>e.scrollWidth<=e.clientWidth')
    if width==390:
        page.set_viewport_size({'width':width,'height':500})
        bounds=footer.bounding_box()
        assert bounds['y']>=0 and bounds['y']+bounds['height']<=500
    rows=footer.locator(':scope > .kg-tutorial-editor-actions')
    assert rows.count()==2
    assert [rows.nth(i).locator('button').count() for i in range(2)]==[3,3]


@pytest.mark.browser
def test_intro_uses_start_for_playable_routes_and_edit_draft_for_incomplete_ones(tutorial_graph):
    page=_library(tutorial_graph)
    page.locator('#kg_tutorial_new').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    draft_id=page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.locator('#kg_tutorial_editor_close').click()
    expect(page.locator('#kg_tutorial_intro_edit')).to_be_visible()
    assert page.locator('#kg_tutorial_start').is_disabled()
    page.get_by_role('button',name='Edit draft',exact=True).click()
    _fill_draft(page)
    page.locator('#kg_tutorial_editor_close').click()
    expect(page.locator('#kg_tutorial_intro_edit')).to_be_hidden()
    assert page.locator('#kg_tutorial_start').is_enabled()
    page.locator('#kg_tutorial_start').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0&&!kgTutorialPlaybackSnapshot().transitioning')
    page.get_by_role('button',name='Edit card',exact=True).click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('data-tutorial-id',draft_id)
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    page.locator('#kg_tutorial_editor_summary').fill('')
    _saved(page)
    page.locator('#kg_tutorial_editor_close').click()
    expect(page.locator('#kg_tutorial_intro_edit')).to_be_visible()
    page.locator('#kg_tutorial_list [data-tutorial-id="viewer-tour"]').click()
    expect(page.locator('#kg_tutorial_intro_edit')).to_be_hidden()
    assert page.locator('#kg_tutorial_start').is_enabled()
