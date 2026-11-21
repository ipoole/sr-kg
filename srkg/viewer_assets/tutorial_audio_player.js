/* Per-card listening. Each navigation invalidates pending asset and media requests. */
function kgCreateTutorialAudioPlayer(options) {
  'use strict';
  function el(name) { return document.getElementById('kg_tutorial_listen_' + name); }
  var enabled = false, visible = false, ready = false, step = null;
  var media = null, url = null, loading = false, wanted = false, serial = 0, request = 0, message = '';
  try { enabled = localStorage.getItem('srkg.tutorial.voice') === 'true'; } catch (error) { /* Local preference is optional. */ }
  function render() {
    el('controls').hidden = !visible;
    el('enabled').checked = enabled;
    el('enabled').disabled = !ready;
    var available = ready && enabled && step && step.audio;
    el('play').disabled = !available || loading;
    el('replay').disabled = !available || loading;
    el('play').textContent = media && !media.paused && !media.ended ? 'Pause voice' : 'Play voice';
    el('status').textContent = message;
    if (options.changed) { options.changed(); }
  }
  function release() {
    serial += 1; request += 1; wanted = false; loading = false;
    if (media) { media.pause(); media.removeAttribute('src'); media.load(); media = null; }
    if (url) { URL.revokeObjectURL(url); url = null; }
  }
  function preference(value) {
    enabled = Boolean(value);
    try { localStorage.setItem('srkg.tutorial.voice', String(enabled)); } catch (error) { /* Keep the session preference. */ }
  }
  function startRoute(hasAudio, choice) {
    release(); step = null; ready = false; visible = hasAudio; message = '';
    if (hasAudio && choice !== undefined) { preference(choice); }
    render();
  }
  function prepare(card) {
    release(); step = card; ready = false;
    message = card && card.audio ? 'Voice is preparing.' : 'No voice for this card.';
    render();
  }
  async function play(replay) {
    if (!ready || !enabled || !step || !step.audio || loading) { return; }
    var token = serial, attempt = ++request;
    wanted = true;
    try {
      if (!media) {
        loading = true; message = 'Loading voice…'; render();
        var asset = await options.getAudio(step.audio.assetId);
        if (token !== serial) { return; }
        if (!asset || !(asset.blob instanceof Blob) || !asset.blob.size) { throw new Error('Recording is missing from this browser.'); }
        var current = new Audio(); media = current;
        url = URL.createObjectURL(asset.blob); current.preload = 'metadata'; current.src = url;
        ['play','pause','ended'].forEach(function(event) {
          current.addEventListener(event, function() {
            if (token !== serial) { return; }
            if (event === 'ended') { wanted = false; message = 'Voice finished. Use Next step when ready.'; }
            else if (event === 'play') { message = 'Playing voice.'; }
            else { message = 'Voice paused.'; }
            render();
          });
        });
        current.addEventListener('error',function() {
          if (token !== serial) { return; }
          wanted = false; message = 'This recording could not be played. Read the text or retry Play voice.'; render();
        });
        loading = false;
      }
      var playing = media;
      if (replay || playing.ended) { playing.currentTime = 0; }
      message = 'Starting voice…'; render();
      await playing.play();
      if (token !== serial || !wanted) { playing.pause(); return; }
      if (attempt === request) { message = 'Playing voice.'; render(); }
    } catch (error) {
      if (token !== serial || attempt !== request) { return; }
      wanted = false; loading = false;
      message = 'Voice unavailable: ' + error.message + ' Read the text or press Play voice to retry.';
      render();
    }
  }
  function settled(success, autoplay) {
    ready = Boolean(success);
    message = !success ? 'Voice stopped because the card could not finish.' :
      !step || !step.audio ? 'No voice for this card.' : enabled ? 'Voice ready.' : 'Voice is off.';
    render();
    if (ready && enabled && autoplay) { play(false); }
  }
  function suspend() { release(); ready = false; message = ''; render(); }
  function stop() { release(); ready = false; visible = false; step = null; message = ''; render(); }
  el('enabled').addEventListener('change',function() {
    preference(this.checked);
    if (!enabled) { release(); message = 'Voice is off.'; render(); }
    else { render(); play(false); }
  });
  el('play').addEventListener('click',function() {
    if (media && !media.paused && !media.ended) {
      wanted = false; request += 1; media.pause(); message = 'Voice paused.'; render();
    } else { play(false); }
  });
  el('replay').addEventListener('click',function() { play(true); });
  window.addEventListener('pagehide',stop);
  return {startRoute:startRoute, prepare:prepare, settled:settled, suspend:suspend, stop:stop};
}
