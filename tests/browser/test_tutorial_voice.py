"""Voice takes are transactional, cancellable and independent of text portability."""
import pytest
from playwright.sync_api import expect
from test_personal_tutorials import tutorial_graph, _library, _fill_draft, _saved, _edit_selected_tutorial


FAKE_MIC = r'''() => {
 window.voiceTracksStopped = 0;
 window.voiceRecorders = [];
 const stream = () => {const track={enabled:true,readyState:'live',stop(){this.readyState='ended';window.voiceTracksStopped++;}};return {getTracks:()=>[track]};};
 Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:async()=>stream()}});
 window.MediaRecorder = class {
   static isTypeSupported(type) { return type === 'audio/webm;codecs=opus'; }
   constructor() { this.state='inactive'; this.mimeType='audio/webm'; voiceRecorders.push(this); }
   start() { this.state='recording'; }
   stop() {
     this.state='inactive';
     setTimeout(()=>{this.ondataavailable({data:new Blob(['take-'+Math.random()],{type:'audio/webm'})});this.onstop();},10);
   }
 };
}'''


def setup_voice(graph):
    page = _library(graph)
    page.evaluate(FAKE_MIC)
    page.locator('#kg_tutorial_new').click()
    _fill_draft(page)
    return page


def record_take(page):
    page.locator('#kg_tutorial_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_stop')).to_be_enabled()
    page.locator('#kg_tutorial_voice_stop').click()
    expect(page.locator('#kg_tutorial_voice_finish')).to_be_enabled()


def audio_ref(page):
    return page.evaluate('''async()=>{
      const store=kgCreateTutorialStore();
      const record=await store.get(document.getElementById('kg_tutorial_editor').dataset.tutorialId);
      return record.route.steps[0].audio || null;
    }''')


@pytest.mark.browser
@pytest.mark.parametrize('width', [390,1280])
def test_voice_record_cancel_replace_reload_and_review(tutorial_graph,width):
    page=setup_voice(tutorial_graph)
    page.set_viewport_size({'width':width,'height':700})
    page.locator('#kg_tutorial_editor_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_script')).to_contain_text('Read this result')
    assert page.locator('#kg_tutorial_voice_dialog').evaluate('e=>e.scrollWidth<=e.clientWidth')
    record_take(page)
    assert audio_ref(page) is None
    page.locator('#kg_tutorial_voice_finish').click()
    expect(page.locator('#kg_tutorial_voice_dialog')).not_to_have_attribute('open','')
    first=audio_ref(page)
    assert len(first['assetId'])==64 and first['duration']>0
    assert page.evaluate('voiceTracksStopped')==0
    page.locator('#kg_tutorial_editor_voice_record').click()
    record_take(page)
    page.locator('#kg_tutorial_voice_cancel').click()
    assert audio_ref(page)==first
    page.locator('#kg_tutorial_editor_voice_record').click()
    record_take(page)
    page.locator('#kg_tutorial_voice_finish').click()
    expect(page.locator('#kg_tutorial_voice_dialog')).not_to_have_attribute('open','')
    replacement=audio_ref(page)
    assert replacement['assetId']!=first['assetId']
    page.locator('#kg_tutorial_editor_commentary').fill('Revised explanation')
    expect(page.locator('#kg_tutorial_editor_voice_status')).to_contain_text('Voice needs review')
    _saved(page)
    tutorial_id=page.locator('#kg_tutorial_editor').get_attribute('data-tutorial-id')
    page.reload(wait_until='domcontentloaded')
    _library(tutorial_graph)
    page.locator(f'[data-tutorial-id="{tutorial_id}"]').click()
    _edit_selected_tutorial(page)
    assert audio_ref(page)==replacement
    expect(page.locator('#kg_tutorial_editor_voice_status')).to_contain_text('Voice needs review')
    page.locator('#kg_tutorial_editor_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_dialog')).to_be_visible()
    expect(page.locator('#kg_tutorial_voice_play')).to_be_enabled()
    page.keyboard.press('Escape')
    expect(page.locator('#kg_tutorial_voice_dialog')).not_to_have_attribute('open','')
    assert page.locator('#kg_tutorial_editor').is_visible()


@pytest.mark.browser
def test_late_microphone_permission_and_active_recording_cancel_release_tracks(tutorial_graph):
    page=setup_voice(tutorial_graph)
    page.evaluate("()=>{navigator.mediaDevices.getUserMedia=()=>new Promise(resolve=>window.allowMic=()=>resolve({getTracks:()=>[{stop:()=>voiceTracksStopped++}]}));}")
    page.locator('#kg_tutorial_editor_voice_record').click()
    page.locator('#kg_tutorial_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_status')).to_contain_text('permission')
    page.keyboard.press('Escape')
    page.evaluate('allowMic()')
    page.wait_for_function('voiceTracksStopped===1')
    assert audio_ref(page) is None
    page.evaluate(FAKE_MIC)
    page.locator('#kg_tutorial_editor_voice_record').click()
    page.locator('#kg_tutorial_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_stop')).to_be_enabled()
    page.keyboard.press('Escape')
    assert page.evaluate('voiceTracksStopped')==0
    page.locator('#kg_tutorial_editor_close').click()
    page.wait_for_function('voiceTracksStopped===1')


@pytest.mark.browser
def test_voice_storage_atomic_conflict_duplicate_and_portability_guards(tutorial_graph):
    page=setup_voice(tutorial_graph)
    result=page.evaluate('''async()=>{
      const store=kgCreateTutorialStore(), p=kgTutorialPortable;
      const id=document.getElementById('kg_tutorial_editor').dataset.tutorialId;
      const old=await store.get(id), stepId=old.route.steps[0].step_id;
      const blob=new Blob(['original'],{type:'audio/wav'});
      const saved=await store.saveVoice(old,stepId,blob,2,p.fingerprint);
      let conflict='';
      try { await store.saveVoice(old,stepId,new Blob(['rejected'],{type:'audio/wav'}),3,p.fingerprint); }
      catch(e) { conflict=e.message; }
      const copy=await store.create(saved.route,null);
      const asset=await store.getAudio(copy.route.steps[0].audio.assetId);
      let exportError='', backupError='', syncError='', reads=0;
      try { p.exportSingle(saved,false); } catch(e) { exportError=e.message; }
      try { p.collectionDocument([saved]); } catch(e) { backupError=e.message; }
      const sync=kgCreateTutorialSync({store,portable:p,provider:{read:async()=>{reads++;return null;}}});
      try { await sync.synchronize(); } catch(e) { syncError=e.message; }
      return {conflict, original:(await store.get(id)).route.steps[0].audio.assetId,
        expected:saved.route.steps[0].audio.assetId, bytes:await asset.blob.text(),exportError,backupError,syncError,reads};
    }''')
    assert 'another editor' in result['conflict']
    assert result['original']==result['expected']
    assert result['bytes']=='original'
    assert result['reads']==0
    for key in ['exportError','backupError','syncError']:
        assert 'not available yet' in result[key]


@pytest.mark.browser
def test_import_real_audio_listen_save_remove_and_permission_error(tutorial_graph):
    import io
    import wave
    page=setup_voice(tutorial_graph)
    data=io.BytesIO()
    with wave.open(data,'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(8000)
        wav.writeframes(b'\0\0'*8000)
    page.locator('#kg_tutorial_editor_voice_file').set_input_files({'name':'voice.wav','mimeType':'audio/wav','buffer':data.getvalue()})
    expect(page.locator('#kg_tutorial_voice_finish')).to_be_enabled()
    page.locator('#kg_tutorial_voice_play').click()
    expect(page.locator('#kg_tutorial_voice_play')).to_have_text('Pause')
    page.locator('#kg_tutorial_voice_finish').click()
    expect(page.locator('#kg_tutorial_voice_dialog')).not_to_have_attribute('open','')
    assert audio_ref(page)['duration']==pytest.approx(1)
    page.on('dialog',lambda d:d.accept())
    page.locator('#kg_tutorial_editor_voice_remove').click()
    expect(page.locator('#kg_tutorial_editor_voice_status')).to_have_text('No voice recording.')
    assert audio_ref(page) is None
    page.evaluate("()=>{navigator.mediaDevices.getUserMedia=async()=>{throw new Error('Permission denied');};}")
    page.locator('#kg_tutorial_editor_voice_record').click()
    page.locator('#kg_tutorial_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_status')).to_contain_text('Permission denied')
    expect(page.locator('#kg_tutorial_voice_record')).to_be_enabled()


@pytest.mark.browser
def test_failed_finish_keeps_take_for_retry_and_old_asset(tutorial_graph):
    page=setup_voice(tutorial_graph)
    page.locator('#kg_tutorial_editor_voice_record').click()
    record_take(page)
    page.locator('#kg_tutorial_voice_finish').click()
    expect(page.locator('#kg_tutorial_voice_dialog')).not_to_have_attribute('open','')
    first=audio_ref(page)
    page.locator('#kg_tutorial_editor_voice_record').click()
    record_take(page)
    page.evaluate('''()=>{
      window.originalPut=IDBObjectStore.prototype.put;
      IDBObjectStore.prototype.put=function(...args) {
        if(this.name==='audio') throw new DOMException('Storage full','QuotaExceededError');
        return window.originalPut.apply(this,args);
      };
    }''')
    page.locator('#kg_tutorial_voice_finish').click()
    expect(page.locator('#kg_tutorial_voice_status')).to_contain_text('Not saved')
    assert audio_ref(page)==first
    expect(page.locator('#kg_tutorial_voice_download')).to_be_enabled()
    page.evaluate('()=>{IDBObjectStore.prototype.put=window.originalPut;}')
    page.locator('#kg_tutorial_voice_finish').click()
    expect(page.locator('#kg_tutorial_voice_dialog')).not_to_have_attribute('open','')
    assert audio_ref(page)['assetId']!=first['assetId']


@pytest.mark.browser
def test_old_database_migrates_and_previous_clients_cannot_write_voice(tutorial_graph):
    page=_library(tutorial_graph)
    result=page.evaluate('''async()=>{
      const name='voice-migration-test';
      const old=await new Promise((resolve,reject)=>{
        const r=indexedDB.open(name,2);
        r.onupgradeneeded=()=>{r.result.createObjectStore('tutorials',{keyPath:'id'});r.result.createObjectStore('meta',{keyPath:'key'});};
        r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);
      });
      old.onversionchange=()=>old.close();
      const store=kgCreateTutorialStore({databaseName:name});
      await store.create(null,null);
      const error=await new Promise(resolve=>{
        const r=indexedDB.open(name,2);r.onerror=()=>resolve(r.error.name);
        r.onsuccess=()=>{r.result.close();resolve('unexpected success');};
      });
      return {count:(await store.list()).length,error};
    }''')
    assert result=={'count':1,'error':'VersionError'}


@pytest.mark.browser
def test_cancelled_recorder_error_does_not_interrupt_a_new_take(tutorial_graph):
    page=setup_voice(tutorial_graph)
    page.locator('#kg_tutorial_editor_voice_record').click()
    page.locator('#kg_tutorial_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_stop')).to_be_enabled()
    page.locator('#kg_tutorial_voice_cancel').click()
    page.locator('#kg_tutorial_editor_voice_record').click()
    page.locator('#kg_tutorial_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_stop')).to_be_enabled()
    page.evaluate('()=>{voiceRecorders[0].onerror();}')
    expect(page.locator('#kg_tutorial_voice_stop')).to_be_enabled()
    assert page.evaluate('voiceTracksStopped')==0
    page.locator('#kg_tutorial_voice_cancel').click()
    assert page.evaluate('voiceTracksStopped')==0


@pytest.mark.browser
def test_microphone_reused_muted_across_cards_until_done(tutorial_graph):
    page=setup_voice(tutorial_graph)
    page.evaluate('''()=>{
      window.micRequests=0;
      window.micTrack={enabled:true,readyState:'live',stop(){this.readyState='ended';}};
      navigator.mediaDevices.getUserMedia=async()=>{micRequests++;return {getTracks:()=>[micTrack]};};
    }''')
    for _ in range(2):
        page.locator('#kg_tutorial_editor_voice_record').click()
        for _ in range(2):
            page.locator('#kg_tutorial_voice_record').click()
            expect(page.locator('#kg_tutorial_voice_stop')).to_be_enabled()
            assert page.evaluate('micTrack.enabled')
            page.locator('#kg_tutorial_voice_stop').click()
            expect(page.locator('#kg_tutorial_voice_finish')).to_be_enabled()
            assert page.evaluate('!micTrack.enabled && micTrack.readyState==="live"')
        page.locator('#kg_tutorial_voice_finish').click()
        expect(page.locator('#kg_tutorial_voice_dialog')).not_to_have_attribute('open','')
        page.locator('#kg_tutorial_editor_card_controls [data-card-action="add"]').click()
    assert page.evaluate('micRequests')==1
    page.locator('#kg_tutorial_editor_close').click()
    expect(page.locator('#kg_tutorial_editor')).not_to_have_attribute('open','')
    assert page.evaluate('micTrack.readyState')=='ended'


@pytest.mark.browser
def test_microphone_session_survives_rehearsal_and_ends_on_exit(tutorial_graph):
    page=setup_voice(tutorial_graph)
    page.locator('#kg_tutorial_editor_voice_record').click()
    record_take(page)
    page.locator('#kg_tutorial_voice_finish').click()
    expect(page.locator('#kg_tutorial_voice_dialog')).not_to_have_attribute('open','')
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0&&!kgTutorialPlaybackSnapshot().transitioning')
    assert page.evaluate('voiceTracksStopped')==0
    page.locator('#kg_tutorial_edit').click()
    expect(page.locator('#kg_tutorial_editor')).to_have_attribute('open','')
    assert page.evaluate('voiceTracksStopped')==0
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0&&!kgTutorialPlaybackSnapshot().transitioning')
    page.locator('#kg_tutorial_exit').click()
    page.wait_for_function('voiceTracksStopped===1')


@pytest.mark.browser
def test_iphone_releases_microphone_before_take_can_be_played(tutorial_graph):
    page=tutorial_graph.page
    page.add_init_script("""
      Object.defineProperty(navigator, 'userAgent', {value:'iPhone'});
      Object.defineProperty(navigator, 'audioSession', {value:{type:'auto'}});
    """)
    page.reload(wait_until='domcontentloaded')
    page=setup_voice(tutorial_graph)
    page.locator('#kg_tutorial_editor_voice_record').click()
    record_take(page)
    assert page.evaluate('voiceTracksStopped')==1
    expect(page.locator('#kg_tutorial_voice_play')).to_be_enabled()
    expect(page.locator('#kg_tutorial_voice_microphone_note')).to_contain_text('released')
    assert page.evaluate('navigator.audioSession.type')=='playback'
    page.locator('#kg_tutorial_voice_record').click()
    expect(page.locator('#kg_tutorial_voice_stop')).to_be_enabled()
    assert page.evaluate('navigator.audioSession.type')=='play-and-record'
    page.locator('#kg_tutorial_voice_cancel').click()
    assert page.evaluate('navigator.audioSession.type')=='auto'
