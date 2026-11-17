"""Recording replaces a card deliberately; cancellation keeps its saved sequence."""
import pytest
from playwright.sync_api import expect
from test_personal_tutorials import tutorial_graph, _library, _fill_draft, _record, _edit_selected_tutorial
from test_tutorial_recording import _idle, _control


def _editable_card(page):
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    tutorial_id=page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.locator('#kg_tutorial_editor_close').click()
    original=page.evaluate('''async id=>{
      const r=await kgPersonalData.tutorials.get(id);
      r.route.steps[0].prepare=[{command:'select',target:'concept:2.1'}];
      r.route.steps[0].action={command:'set-view',value:'details'};
      return kgPersonalData.tutorials.save(r);
    }''',tutorial_id)
    # Refresh the library so its ordinary Edit action opens this known saved sequence.
    page.reload(wait_until='domcontentloaded')
    return tutorial_id,original


def _open_existing(graph,tutorial_id):
    page=_library(graph)
    page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]').click()
    _edit_selected_tutorial(page)
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    return page


@pytest.mark.browser
@pytest.mark.parametrize('cancel',[False,True])
def test_record_replaces_only_on_finish_and_cancel_retains_original(tutorial_graph,cancel):
    page=_library(tutorial_graph)
    tutorial_id,original=_editable_card(page)
    page=_open_existing(tutorial_graph,tutorial_id)
    page.locator('#kg_tutorial_editor_record').click()
    _idle(page)
    state=page.evaluate('kgCaptureTutorialPresentation()')
    assert state['selection']['id']=='2.1'  # Silent setup still runs.
    assert state['view']!='details'  # Existing card actions must not run.
    assert page.evaluate('id=>kgPersonalData.tutorials.get(id)',tutorial_id)==original
    _control(page,'#kg_view_select','graph')
    assert page.evaluate('id=>kgPersonalData.tutorials.get(id)',tutorial_id)==original
    page.locator('#kg_tutorial_recording_cancel' if cancel else '#kg_tutorial_recording_finish').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    saved=_record(page,tutorial_id)
    if cancel:
        assert saved==original
    else:
        assert [item['action'] for item in saved['route']['steps'][0]['actions']]==[{'command':'set-view','value':'graph'}]
        assert saved['route']['steps'][0]['prepare']==[{'command':'home'},{'command':'select','target':'concept:2.1'}]
        page.locator('#kg_tutorial_editor_from').click()
        page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0&&!kgTutorialPlaybackSnapshot().transitioning')
        assert page.evaluate('kgCaptureTutorialPresentation().view')=='graph'
    assert not tutorial_graph.page_errors


@pytest.mark.browser
@pytest.mark.parametrize('width',[390,1280])
def test_tutorial_editor_groups_primary_controls_in_two_rows(tutorial_graph,width):
    page=_library(tutorial_graph)
    page.set_viewport_size({'width':width,'height':900})
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    advanced=page.locator('#kg_tutorial_editor_advanced')
    assert not advanced.evaluate('e=>e.open')
    assert not page.locator('#kg_tutorial_editor_actions').is_visible()
    assert not page.locator('#kg_tutorial_editor_setup').is_visible()
    rows=page.locator('#kg_tutorial_editor_footer > .kg-tutorial-editor-actions')
    assert rows.count()==2
    assert [rows.nth(i).locator('button').count() for i in range(2)]==[3,3]
    assert page.locator('#kg_tutorial_editor_preview').count()==0
    assert page.get_by_role('button',name='Play from start',exact=True).is_enabled()
    boxes=rows.evaluate_all('rows=>rows.map(row=>Array.from(row.querySelectorAll("button"),b=>{const r=b.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right};}))')
    for row in boxes:
        assert len({round(box['top']) for box in row})==1
        for a,b in zip(row,row[1:]):assert a['right']<=b['left']
    assert boxes[0][0]['bottom']<boxes[1][0]['top']
    assert page.locator('#kg_tutorial_editor').evaluate('e=>e.scrollWidth<=e.clientWidth')
    advanced.locator('summary').click()
    assert page.locator('#kg_tutorial_editor_actions').is_visible()
    assert page.locator('#kg_tutorial_editor_setup').is_visible()


@pytest.mark.browser
def test_rerecord_repairs_broken_actions_and_empty_finish_can_clear_them(tutorial_graph):
    page=_library(tutorial_graph)
    tutorial_id,_=_editable_card(page)
    page.evaluate('''async id=>{
      const r=await kgPersonalData.tutorials.get(id);r.route.steps[0].action={command:'select',target:'concept:missing.target'};
      await kgPersonalData.tutorials.save(r);
    }''',tutorial_id)
    page.reload(wait_until='domcontentloaded')
    page=_open_existing(tutorial_graph,tutorial_id)
    assert page.locator('#kg_tutorial_editor_play').is_disabled()
    page.locator('#kg_tutorial_editor_record').click()
    _idle(page)
    assert page.locator('#kg_tutorial_recording_undo').is_disabled()
    page.locator('#kg_tutorial_recording_finish').click()
    saved=_record(page,tutorial_id)
    assert saved['route']['steps'][0]['action']=={'command':'wait','milliseconds':0}
    assert 'actions' not in saved['route']['steps'][0]
    assert page.locator('#kg_tutorial_editor_play').is_enabled()


@pytest.mark.browser
def test_finish_recording_save_failure_retains_draft_for_retry(tutorial_graph):
    page=_library(tutorial_graph)
    tutorial_id,original=_editable_card(page)
    page=_open_existing(tutorial_graph,tutorial_id)
    page.locator('#kg_tutorial_editor_record').click()
    _idle(page)
    _control(page,'#kg_view_select','graph')
    page.evaluate("()=>{window.__saveTutorial=kgPersonalData.tutorials.save;kgPersonalData.tutorials.save=()=>Promise.reject(new Error('Storage full'));}")
    page.locator('#kg_tutorial_recording_finish').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    expect(page.locator('#kg_tutorial_editor_status')).to_have_attribute('data-state','error')
    assert page.evaluate('id=>kgPersonalData.tutorials.get(id)',tutorial_id)==original
    page.evaluate('()=>{kgPersonalData.tutorials.save=window.__saveTutorial;}')
    page.locator('#kg_tutorial_editor_retry').click()
    saved=_record(page,tutorial_id)
    assert [item['action'] for item in saved['route']['steps'][0]['actions']]==[{'command':'set-view','value':'graph'}]


@pytest.mark.browser
def test_record_later_card_replays_prefix_and_preserves_silent_setup(tutorial_graph):
    page=_library(tutorial_graph)
    tutorial_id,_=_editable_card(page)
    page.evaluate('''async id=>{
      const r=await kgPersonalData.tutorials.get(id);
      r.route.steps=[
        {step_id:'first',title:'Select Beta',commentary:'Begin here.',action:{command:'select',target:'concept:2.1'},pointer:{target:'graph:concept:2.1'}},
        {step_id:'second',title:'Revise the next card',commentary:'Inspect the foundations.',prepare:[{command:'set-context',preset:'foundations',depth:'two-hops'}],action:{command:'set-view',value:'details'},pointer:{target:'narration'}}
      ];await kgPersonalData.tutorials.save(r);
    }''',tutorial_id)
    page.reload(wait_until='domcontentloaded')
    page=_open_existing(tutorial_graph,tutorial_id)
    page.locator('#kg_tutorial_editor_card').select_option(index=1)
    page.locator('#kg_tutorial_editor_record').click()
    _idle(page)
    before=page.evaluate('kgCaptureTutorialPresentation()')
    assert before['selection']['id']=='2.1'
    assert before['contextRule']['preset']=='foundations'
    assert before['view']!='details'
    _control(page,'#kg_view_select','graph')
    page.locator('#kg_tutorial_recording_finish').click()
    steps=_record(page,tutorial_id)['route']['steps']
    assert steps[0]['action']=={'command':'select','target':'concept:2.1'}
    assert steps[0]['prepare']==[{'command':'home'}]
    assert steps[1]['prepare']==[{'command':'set-context','preset':'foundations','depth':'two-hops'}]
    assert [item['action'] for item in steps[1]['actions']]==[{'command':'set-view','value':'graph'}]
    assert page.locator('#kg_tutorial_editor_card').input_value()=='1'
