"""Existing actions form the redo queue; explicit pauses and card mode remain editable."""
import pytest
from playwright.sync_api import expect
from test_personal_tutorials import tutorial_graph, _library, _fill_draft, _record
from test_tutorial_recording import _idle, _control
from test_tutorial_record_replacement import _editable_card, _open_existing


@pytest.mark.browser
def test_record_seeds_redo_and_allows_appending_with_undo(tutorial_graph):
    page=_library(tutorial_graph)
    tutorial_id,original=_editable_card(page)
    page=_open_existing(tutorial_graph,tutorial_id)
    page.locator('#kg_tutorial_editor_record').click();_idle(page)
    redo=page.locator('#kg_tutorial_recording_redo')
    expect(redo).to_be_enabled()
    assert page.evaluate('kgCaptureTutorialPresentation().view')!='details'
    redo.click();_idle(page)
    assert page.evaluate('kgCaptureTutorialPresentation().view')=='details'
    page.locator('#kg_tutorial_recording_undo').click();_idle(page)
    assert page.evaluate('kgCaptureTutorialPresentation().view')!='details'
    redo.click();_idle(page)
    _control(page,'#kg_view_select','graph')
    assert redo.is_disabled()
    assert page.evaluate('id=>kgPersonalData.tutorials.get(id)',tutorial_id)==original
    page.locator('#kg_tutorial_recording_finish').click()
    actions=_record(page,tutorial_id)['route']['steps'][0]['actions']
    assert [item['action'] for item in actions]==[{'command':'set-view','value':'details'},{'command':'set-view','value':'graph'}]


@pytest.mark.browser
def test_pause_double_click_adds_two_seconds_and_undo_removes_only_one(tutorial_graph):
    page=_library(tutorial_graph)
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#kg_tutorial_new').click();_fill_draft(page)
    tutorial_id=page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.locator('#kg_tutorial_editor_record').click();_idle(page)
    buttons=page.locator('#kg_tutorial_recording button').evaluate_all('buttons=>buttons.map(b=>b.getBoundingClientRect().top)')
    assert len({round(top) for top in buttons})==1
    assert page.evaluate('parseFloat(getComputedStyle(document.getElementById("info_panel")).paddingBottom)>=document.getElementById("kg_tutorial_recording").offsetHeight')
    _control(page,'#kg_view_select','graph')
    page.get_by_role('button',name='Pause +1s',exact=True).dblclick()
    _idle(page)
    page.locator('#kg_tutorial_recording_undo').click();_idle(page)
    assert page.evaluate('kgCaptureTutorialPresentation().view')=='graph'
    page.locator('#kg_tutorial_recording_finish').click()
    actions=_record(page,tutorial_id)['route']['steps'][0]['actions']
    assert [item['action'] for item in actions]==[{'command':'set-view','value':'graph'},{'command':'wait','milliseconds':1000}]
    assert actions[-1]['pause_ms']==0
    # Existing pauses are queued with the actions and can be undone and restored again.
    page.locator('#kg_tutorial_editor_record').click();_idle(page)
    for _ in range(2):page.locator('#kg_tutorial_recording_redo').click();_idle(page)
    page.locator('#kg_tutorial_recording_undo').click();_idle(page)
    page.locator('#kg_tutorial_recording_redo').click();_idle(page)
    page.locator('#kg_tutorial_recording_finish').click()
    assert _record(page,tutorial_id)['route']['steps'][0]['actions']==actions


@pytest.mark.browser
@pytest.mark.parametrize('demonstrate',[False,True])
def test_card_mode_preserves_state_and_explicit_pause_without_moving_pointer(tutorial_graph,demonstrate):
    page=_library(tutorial_graph)
    page.locator('#kg_tutorial_new').click();_fill_draft(page)
    toggle=page.get_by_label('Action visibility',exact=True)
    expect(toggle).to_have_value('show')
    toggle.select_option('show' if demonstrate else 'hide')
    tutorial_id=page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.keyboard.press('Escape')
    page.evaluate('''async id=>{
      const r=await kgPersonalData.tutorials.get(id);
      delete r.route.steps[0].action;delete r.route.steps[0].pointer;
      r.route.steps[0].actions=[
        {action:{command:'select',target:'concept:2.1'},pointer:{target:'graph:concept:2.1'},pause_ms:0},
        {action:{command:'wait',milliseconds:1000},pause_ms:0}
      ];await kgPersonalData.tutorials.save(r);
    }''',tutorial_id)
    page.reload(wait_until='domcontentloaded');_library(tutorial_graph)
    page.locator(f'#kg_tutorial_personal_list [data-tutorial-id="{tutorial_id}"]').click()
    page.evaluate('''()=>{
      const schedule=window.setTimeout;window.setTimeout=(callback,delay,...args)=>{
        if(delay===1000){window.__releasePause=()=>{window.setTimeout=schedule;schedule(callback,0,...args);};return 0;}
        return schedule(callback,delay,...args);
      };
    }''')
    page.locator('#kg_tutorial_start').click()
    page.wait_for_function('typeof __releasePause==="function"')
    assert page.evaluate('kgViewerStateSnapshot().selection.id')=='2.1'
    pointer=page.evaluate('kgTutorialPointerSnapshot()')
    assert pointer['visible']==demonstrate
    if demonstrate:assert pointer['target']=='graph:concept:2.1'
    page.evaluate('__releasePause()')
    page.wait_for_function('!kgTutorialPlaybackSnapshot().transitioning')
    page.locator('#kg_tutorial_explore').click()
    page.locator('#kg_tutorial_explore').click()
    page.wait_for_function('!kgTutorialPlaybackSnapshot().exploring&&!kgTutorialPlaybackSnapshot().transitioning')
    assert page.evaluate('kgTutorialPointerSnapshot().visible')==demonstrate
    page.locator('#kg_tutorial_edit').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    assert toggle.input_value()==('show' if demonstrate else 'hide')
    toggle.select_option('hide' if demonstrate else 'show')
    saved=_record(page,tutorial_id)
    assert saved['route']['steps'][0]['demonstrate']==(not demonstrate)
    exported=page.evaluate('''id=>kgPersonalData.tutorials.get(id).then(r=>kgTutorialPortable.importSingle(kgTutorialPortable.exportSingle(r,true)))''',tutorial_id)
    assert exported['route']['steps'][0]['demonstrate']==(not demonstrate)
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0&&!kgTutorialPlaybackSnapshot().transitioning')
    assert page.evaluate('kgTutorialPointerSnapshot().visible')==(not demonstrate)
    assert page.evaluate('kgViewerStateSnapshot().selection.id')=='2.1'
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_play_from_here_reconstructs_earlier_cards_without_waiting_out_pauses(tutorial_graph):
    page=_library(tutorial_graph)
    tutorial_id,_=_editable_card(page)
    page.evaluate('''async id=>{
      const r=await kgPersonalData.tutorials.get(id);r.route.steps=[
        {step_id:'first',title:'First card',commentary:'Read the result.',demonstrate:false,actions:[
          {action:{command:'select',target:'concept:2.1'},pause_ms:0},
          {action:{command:'wait',milliseconds:1000},pause_ms:0}]},
        {step_id:'second',title:'Continue here',commentary:'Read the explanation.',demonstrate:false,action:{command:'set-view',value:'details'}}
      ];await kgPersonalData.tutorials.save(r);
    }''',tutorial_id)
    page.reload(wait_until='domcontentloaded')
    page=_open_existing(tutorial_graph,tutorial_id)
    page.locator('#kg_tutorial_editor_card').select_option(index=1)
    page.evaluate('''()=>{
      const schedule=window.setTimeout;window.setTimeout=(callback,delay,...args)=>{
        if(delay===1000)throw new Error('Earlier card pause replayed during reconstruction');
        return schedule(callback,delay,...args);
      };
    }''')
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===1&&!kgTutorialPlaybackSnapshot().transitioning')
    expect(page.locator('#kg_tutorial_error')).to_be_hidden()
    assert page.evaluate('kgViewerStateSnapshot().selection.id')=='2.1'
    assert page.evaluate('kgCaptureTutorialPresentation().view')=='details'
