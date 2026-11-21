"""Optional voice plays alongside actions and never owns tutorial navigation."""
import base64
import io
import wave

import pytest
from playwright.sync_api import expect
from test_personal_tutorials import tutorial_graph, _library


FAKE_AUDIO = '''() => {
  window.voiceMedia=[]; window.voicePlays=[];
  window.Audio=class extends EventTarget {
    constructor(){super();this.paused=true;this.ended=false;this.currentTime=0;this.src='';voiceMedia.push(this);}
    play(){voicePlays.push({time:this.currentTime,...kgTutorialPlaybackSnapshot()});
      if(window.rejectVoice){window.rejectVoice=false;return Promise.reject(new Error('Autoplay blocked'));}
      this.paused=false;this.ended=false;this.dispatchEvent(new Event('play'));return Promise.resolve();}
    pause(){this.paused=true;this.dispatchEvent(new Event('pause'));}
    removeAttribute(name){if(name==='src')this.src='';}
    load(){this.currentTime=0;}
  };
}'''


def voice_route(graph, fake=True):
    page=_library(graph)
    data=io.BytesIO()
    with wave.open(data,'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(8000)
        wav.writeframes(b'\0\0'*8000*3)
    tutorial_id=page.evaluate('''async(encoded)=>{
      const store=kgPersonalData.tutorials;
      const route={tutorial_id:'seed',title:'Voice route',category:'physics',sequence:0,domains:[],steps:
        [0,1,2].map(i=>({step_id:'card-'+i,title:'Card '+i,commentary:'Written explanation '+i,
          demonstrate:false,actions:Array.from({length:6},()=>({action:{command:'wait',milliseconds:150}}))}))};
      let record=await store.create(route,null);
      const blob=new Blob([Uint8Array.from(atob(encoded),c=>c.charCodeAt(0))],{type:'audio/wav'});
      for(const step of record.route.steps.slice(0,2)) record=await store.saveVoice(record,step.step_id,blob,3,kgTutorialPortable.fingerprint);
      return record.id;
    }''',base64.b64encode(data.getvalue()).decode())
    page.reload(wait_until='domcontentloaded')
    _library(graph)
    page.locator(f'[data-tutorial-id="{tutorial_id}"]').click()
    if fake: page.evaluate(FAKE_AUDIO)
    return page,tutorial_id


def restart_voice(page):
    checkbox=page.locator('#kg_tutorial_listen_enabled')
    checkbox.uncheck()
    checkbox.check()


def settled(page,index):
    page.wait_for_function('(i)=>kgTutorialPlaybackSnapshot().stepIndex===i&&!kgTutorialPlaybackSnapshot().transitioning',arg=index)


@pytest.mark.browser
@pytest.mark.parametrize('width',[390,1280])
def test_voice_overlaps_actions_toggle_restart_and_manual_navigation(tutorial_graph,width):
    page,_=voice_route(tutorial_graph)
    page.set_viewport_size({'width':width,'height':800})
    page.locator('#kg_tutorial_start_voice').click()
    page.wait_for_function('voicePlays.length===1')
    assert page.evaluate('voicePlays[0].transitioning') is True
    settled(page,0)
    assert page.evaluate('voicePlays[0].stepIndex')==0
    expect(page.locator('#kg_tutorial_commentary')).to_have_text('Written explanation 0')
    assert page.locator('#kg_tutorial_listen_play, #kg_tutorial_listen_replay').count()==0
    page.evaluate('()=>{voiceMedia[0].currentTime=1.25;}')
    baseline=page.evaluate('kgCaptureTutorialPresentation()')
    restart_voice(page)
    page.wait_for_function('voicePlays.length===2')
    assert page.evaluate('voicePlays[1].time')==0
    assert page.evaluate('voiceMedia[0].paused && !voiceMedia[0].src')
    assert page.evaluate('kgCaptureTutorialPresentation()')==baseline
    page.evaluate("()=>{voiceMedia[1].ended=true;voiceMedia[1].paused=true;voiceMedia[1].dispatchEvent(new Event('ended'));}")
    expect(page.locator('#kg_tutorial_listen_status')).to_contain_text('Voice finished')
    assert page.evaluate('kgTutorialPlaybackSnapshot().stepIndex')==0
    page.locator('#kg_tutorial_next').click()
    page.wait_for_function('voicePlays.length===3')
    assert page.evaluate('voiceMedia[0].paused && !voiceMedia[0].src')
    assert page.evaluate('voicePlays[2].stepIndex')==1
    settled(page,1)
    page.locator('#kg_tutorial_back').click()
    page.wait_for_function('voicePlays.length===4')
    assert page.evaluate('voicePlays[3].time')==0
    settled(page,0)
    page.locator('#kg_tutorial_explore').click()
    assert page.evaluate('voiceMedia.every(m=>m.paused)')
    page.locator('#kg_tutorial_explore').click()
    settled(page,0)
    assert page.evaluate('voicePlays.length')==4
    restart_voice(page)
    page.wait_for_function('voicePlays.length===5')
    page.locator('#kg_tutorial_next').click(); settled(page,1)
    page.locator('#kg_tutorial_next').click(); settled(page,2)
    expect(page.locator('#kg_tutorial_listen_enabled')).to_be_hidden()
    assert page.evaluate("localStorage.getItem('srkg.tutorial.voice')")=='true'
    expect(page.locator('#kg_tutorial_commentary')).to_have_text('Written explanation 2')
    assert page.evaluate('voiceMedia.every(m=>m.paused)')
    assert page.locator('#kg_tutorial_narration').evaluate('e=>e.scrollWidth<=e.clientWidth')
    page.locator('#kg_tutorial_exit').click()
    expect(page.locator('#kg_tutorial_narration')).to_be_hidden()


@pytest.mark.browser
@pytest.mark.parametrize('navigation',['next','explore','exit','edit'])
def test_navigation_cancels_late_voice_load(tutorial_graph,navigation):
    page,_=voice_route(tutorial_graph)
    page.evaluate('''()=>{
      const original=kgPersonalData.tutorials.getAudio;let first=true;
      kgPersonalData.tutorials.getAudio=async(id)=>{
        const asset=await original(id);
        if(!first)return asset;first=false;
        return new Promise(resolve=>{window.finishLateVoice=()=>resolve(asset);});
      };
    }''')
    page.locator('#kg_tutorial_start_voice').click()
    page.wait_for_function('typeof finishLateVoice==="function"')
    settled(page,0)
    expect(page.locator('#kg_tutorial_next')).to_be_enabled()
    settled(page,0)
    page.locator('#kg_tutorial_'+navigation).click()
    page.evaluate('async()=>{finishLateVoice();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}')
    if navigation=='next':
        page.wait_for_function('voicePlays.length===1')
        assert page.evaluate('voicePlays[0].stepIndex')==1
    else:
        assert page.evaluate('voicePlays.length')==0


@pytest.mark.browser
@pytest.mark.parametrize('failure',['missing','blocked'])
def test_voice_failure_keeps_text_navigation_and_retry(tutorial_graph,failure):
    page,_=voice_route(tutorial_graph)
    if failure=='missing':
        page.evaluate('()=>{window.originalAudio=kgPersonalData.tutorials.getAudio;kgPersonalData.tutorials.getAudio=async()=>null;}')
    else:
        page.evaluate('()=>{window.rejectVoice=true;}')
    page.locator('#kg_tutorial_start_voice').click()
    expect(page.locator('#kg_tutorial_listen_status')).to_contain_text('Voice unavailable')
    expect(page.locator('#kg_tutorial_commentary')).to_be_visible()
    settled(page,0)
    expect(page.locator('#kg_tutorial_next')).to_be_enabled()
    if failure=='missing':
        page.evaluate('()=>{kgPersonalData.tutorials.getAudio=originalAudio;}')
    restart_voice(page)
    expect(page.locator('#kg_tutorial_listen_status')).to_have_text('Playing voice.')
    page.locator('#kg_tutorial_exit').click()
    assert page.evaluate('voiceMedia.every(m=>m.paused)')


@pytest.mark.browser
def test_plain_start_voice_toggle_preference_and_real_wav_playback(tutorial_graph):
    page,tutorial_id=voice_route(tutorial_graph,fake=False)
    page.locator('#kg_tutorial_start').click()
    settled(page,0)
    expect(page.locator('#kg_tutorial_listen_enabled')).not_to_be_checked()
    page.locator('#kg_tutorial_listen_enabled').check()
    expect(page.locator('#kg_tutorial_listen_status')).to_have_text('Playing voice.')
    assert page.evaluate("localStorage.getItem('srkg.tutorial.voice')")=='true'
    page.locator('#kg_tutorial_exit').click()
    page.reload(wait_until='domcontentloaded');_library(tutorial_graph)
    page.evaluate('(id)=>kgStartTutorial(id)',tutorial_id)
    settled(page,0)
    expect(page.locator('#kg_tutorial_listen_enabled')).to_be_checked()
    page.locator('#kg_tutorial_listen_enabled').uncheck()
    assert page.evaluate("localStorage.getItem('srkg.tutorial.voice')")=='false'


@pytest.mark.browser
@pytest.mark.parametrize('navigation',['next','exit'])
def test_late_play_promise_cannot_restart_old_card_or_pause_new_one(tutorial_graph,navigation):
    page,_=voice_route(tutorial_graph)
    page.evaluate('''()=>{
      const play=Audio.prototype.play;let first=true;
      Audio.prototype.play=function(){
        if(!first)return play.call(this);first=false;
        return new Promise(resolve=>{window.finishLatePlay=()=>{this.paused=false;this.dispatchEvent(new Event('play'));resolve();};});
      };
    }''')
    page.locator('#kg_tutorial_start_voice').click()
    page.wait_for_function('typeof finishLatePlay==="function"')
    settled(page,0)
    page.locator('#kg_tutorial_'+navigation).click()
    if navigation=='next': page.wait_for_function('voicePlays.length===1')
    page.evaluate('async()=>{finishLatePlay();await new Promise(r=>requestAnimationFrame(r));}')
    assert page.evaluate('voiceMedia[0].paused')
    if navigation=='next':
        assert page.evaluate('!voiceMedia[1].paused')
        expect(page.locator('#kg_tutorial_listen_status')).to_have_text('Playing voice.')


@pytest.mark.browser
def test_voice_disabled_during_load_does_not_start_later(tutorial_graph):
    page,_=voice_route(tutorial_graph)
    page.evaluate('''()=>{
      const original=kgPersonalData.tutorials.getAudio;
      kgPersonalData.tutorials.getAudio=async(id)=>{
        const asset=await original(id);return new Promise(resolve=>window.finishLateVoice=()=>resolve(asset));
      };
    }''')
    page.locator('#kg_tutorial_start_voice').click()
    page.wait_for_function('typeof finishLateVoice==="function"')
    page.locator('#kg_tutorial_listen_enabled').uncheck()
    page.evaluate('async()=>{finishLateVoice();await new Promise(r=>requestAnimationFrame(r));}')
    assert page.evaluate('voicePlays.length')==0
    expect(page.locator('#kg_tutorial_listen_enabled')).not_to_be_checked()
