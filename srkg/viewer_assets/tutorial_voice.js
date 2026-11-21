/* A take remains private to this dialogue until Finish commits it with its card. */
function kgCreateTutorialVoice(options) {
  'use strict';
  function el(name) { return document.getElementById('kg_tutorial_voice_' + name); }
  var dialog = el('dialog'), session = null, generation = 0;
  var recorder = null, stream = null, timer = null, started = 0;
  var clip = null, duration = 0, dirty = false, phase = 'idle', url = null;
  var player = el('audio');
  function message(text) { el('status').textContent = text; }
  function controls() {
    var locked = phase !== 'idle';
    el('record').disabled = locked || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder;
    el('record').textContent = clip ? 'Re-record' : 'Record';
    el('stop').disabled = phase !== 'recording';
    el('play').disabled = locked || !clip;
    el('play').textContent = player.paused ? 'Play' : 'Pause';
    el('finish').disabled = locked || !dirty;
    el('cancel').disabled = phase === 'saving';
    el('download').disabled = locked || !clip;
    el('time').textContent = (phase === 'recording' ? 'Recording · ' : 'Duration · ') +
      Math.floor(duration / 60) + ':' + String(Math.floor(duration % 60)).padStart(2,'0');
  }
  function stopTracks() {
    if (stream) { stream.getTracks().forEach(function(track) { track.stop(); }); stream = null; }
    clearInterval(timer); timer = null;
  }
  function muteTracks() {
    if (stream) { stream.getTracks().forEach(function(track) { track.enabled = false; }); }
    clearInterval(timer); timer = null;
  }
  function endAuthoring() { generation += 1; stopTracks(); }
  function stopPlayback() { player.pause(); player.removeAttribute('src'); player.load(); if (url) { URL.revokeObjectURL(url); url = null; } }
  function useClip(blob, seconds) {
    stopPlayback(); clip = blob; duration = seconds;
    url = URL.createObjectURL(blob); player.src = url; controls();
  }
  function cancel() {
    if (phase === 'saving') { return; }
    generation += 1;
    if (recorder && recorder.state !== 'inactive') { recorder.stop(); }
    recorder = null; muteTracks(); stopPlayback(); session = null; clip = null; dirty = false; phase = 'idle';
    if (dialog.open) { dialog.close(); }
    options.closed();
  }
  async function start() {
    if (!session || phase !== 'idle') { return; }
    var token = ++generation, oldDuration = duration;
    phase = 'permission'; player.pause(); controls(); message('Waiting for microphone permission…');
    try {
      if (stream && !stream.getTracks().every(function(track) { return track.readyState === 'live'; })) { stopTracks(); }
      var acquired = stream || await navigator.mediaDevices.getUserMedia({audio:true});
      if (token !== generation) { acquired.getTracks().forEach(function(track) { track.stop(); }); return; }
      stream = acquired;
      stream.getTracks().forEach(function(track) { track.enabled = true; });
      var mime = ['audio/webm;codecs=opus','audio/mp4','audio/ogg;codecs=opus'].find(function(type) {
        return MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(type);
      });
      recorder = mime ? new MediaRecorder(stream,{mimeType:mime}) : new MediaRecorder(stream);
      var current = recorder, chunks = [], bytes = 0, failed = false;
      current.ondataavailable = function(event) {
        if (event.data.size) { chunks.push(event.data); bytes += event.data.size; }
        if (bytes > 50 * 1024 * 1024 && current.state !== 'inactive') {
          failed = true; message('Recording exceeds 50 MB. Previous take kept.'); current.stop(); stopTracks();
        }
      };
      current.onerror = function() {
        if (token !== generation) { return; }
        failed = true; message('Recording failed. Previous take kept.');
        if (current.state !== 'inactive') { current.stop(); }
        stopTracks(); phase = 'stopping'; duration = oldDuration; controls();
      };
      current.onstop = function() {
        if (token !== generation) { return; }
        muteTracks(); recorder = null; phase = 'idle';
        var blob = new Blob(chunks,{type:current.mimeType || (chunks[0] && chunks[0].type) || mime || 'audio/webm'});
        if (!failed && blob.size && blob.size <= 50 * 1024 * 1024) {
          useClip(blob, Math.max(0.001,(performance.now() - started) / 1000)); dirty = true;
          message('Take ready. Listen, re-record, or Finish recording to save.');
        } else { duration = oldDuration; if (!failed) { message('No audio captured. Previous take kept.'); } }
        controls();
      };
      current.start(1000); started = performance.now(); phase = 'recording'; duration = 0;
      timer = setInterval(function() { duration = (performance.now() - started) / 1000; controls(); },250);
      message('Microphone recording. Press Stop when finished.'); controls();
    } catch (error) {
      if (token !== generation) { return; }
      stopTracks(); recorder = null; phase = 'idle'; duration = oldDuration;
      message('Could not record: ' + error.message + ' You can also import an audio file from the card editor.'); controls();
    }
  }
  function stop() {
    if (phase !== 'recording') { return; }
    phase = 'stopping'; recorder.stop(); muteTracks(); message('Preparing take…'); controls();
  }
  el('record').addEventListener('click',start);
  el('stop').addEventListener('click',stop);
  el('cancel').addEventListener('click',cancel);
  el('play').addEventListener('click',async function() {
    if (!clip || phase !== 'idle') { return; }
    var token = generation;
    if (!player.paused) { player.pause(); controls(); return; }
    try { if (player.ended) { player.currentTime = 0; } await player.play(); }
    catch (error) { if (token === generation) { message('Cannot play this audio on this device: ' + error.message); } }
    if (token === generation) { controls(); }
  });
  ['play','pause','ended'].forEach(function(event) { player.addEventListener(event,controls); });
  player.addEventListener('error',function() { if (clip && session) { message('This device cannot play this audio. Import a supported audio file or re-record.'); } });
  el('download').addEventListener('click',function() {
    if (!clip || !url) { return; }
    var link = document.createElement('a'); link.href = url;
    var type = clip.type.split(';')[0], extension = {'audio/mp4':'m4a','audio/webm':'webm','audio/ogg':'ogg','audio/wav':'wav','audio/x-wav':'wav','audio/mpeg':'mp3'}[type] || 'audio';
    link.download = 'narration.' + extension; link.click();
  });
  el('finish').addEventListener('click',async function() {
    if (phase !== 'idle' || !dirty) { return; }
    phase = 'saving'; player.pause(); controls(); message('Saving recording…');
    try { await options.save(clip,duration); phase = 'idle'; cancel(); }
    catch (error) { phase = 'idle'; message('Not saved: ' + error.message + ' Your take is still here; retry Finish or download it.'); controls(); }
  });
  dialog.addEventListener('cancel',function(event) { event.preventDefault(); cancel(); });
  dialog.addEventListener('close',function() { if (session && !dialog.open) { cancel(); } });
  dialog.addEventListener('keydown',function(event) { if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); cancel(); } });
  // Concept links in the script must not change the graph while recording.
  el('script').addEventListener('click',function(event) { event.preventDefault(); event.stopPropagation(); });
  window.addEventListener('pagehide',function() { phase = 'idle'; cancel(); endAuthoring(); });
  window.addEventListener('beforeunload',function(event) {
    if (session && (dirty || phase !== 'idle')) { event.preventDefault(); event.returnValue = ''; }
    if (phase === 'recording') { stop(); }
    stopTracks();
  });
  function open(step, asset) {
    generation += 1; session = step; phase = 'idle'; dirty = false; clip = null; duration = 0;
    el('heading').textContent = 'Voice narration — ' + (step.title || 'Untitled card');
    if (window.MathJax && MathJax.typesetClear) { MathJax.typesetClear([el('script')]); }
    el('script').innerHTML = options.markup.renderConceptText(step.commentary || '') || '<p>No written narration yet.</p>';
    el('script').querySelectorAll('a, button').forEach(function(item) { item.tabIndex = -1; });
    if (window.MathJax && MathJax.typesetPromise) { MathJax.typesetPromise([el('script')]).catch(function() {}); }
    if (asset) { useClip(asset.blob,step.audio.duration); }
    message(asset ? 'Saved recording. Re-record to make a new take.' : 'Record your narration, or cancel to return to the editor.');
    if (step.audio && !asset) { message('Saved audio is missing. Import a file or record a replacement.'); }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
      message('Microphone recording is unavailable here. Use Import audio file in the card editor.');
    }
    controls(); dialog.showModal();
  }
  async function importFile(file) {
    if (!session) { return; }
    var token = generation;
    if (!file.size || file.size > 50 * 1024 * 1024 || !/^audio\//.test(file.type)) {
      message('Choose an audio file of at most 50 MB.'); return;
    }
    phase = 'loading'; controls(); message('Checking audio file…');
    var media = new Audio(), source = URL.createObjectURL(file);
    try {
      var seconds = await new Promise(function(resolve,reject) {
        var timeout = setTimeout(function() { reject(new Error('Could not read audio duration.')); },10000);
        media.onloadedmetadata = function() { clearTimeout(timeout); resolve(media.duration); };
        media.onerror = function() { clearTimeout(timeout); reject(new Error('This device cannot read that audio format.')); };
        media.src = source;
      });
      if (token !== generation) { return; }
      if (!Number.isFinite(seconds) || seconds <= 0) { throw new Error('Audio needs a finite, positive duration.'); }
      phase = 'idle'; useClip(file,seconds); dirty = true;
      message('File ready. Listen, then Finish recording to save.');
    } catch (error) { if (token === generation) { message('Could not import: ' + error.message); } }
    finally {
      media.removeAttribute('src'); media.load(); URL.revokeObjectURL(source);
      if (token === generation) { phase = 'idle'; controls(); }
    }
  }
  return {endAuthoring:endAuthoring, open:open, importFile:importFile, cancel:cancel};
}
