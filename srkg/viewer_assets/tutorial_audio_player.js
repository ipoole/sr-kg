/* Per-card listening. Each navigation invalidates pending asset and media requests. */
function kgCreateTutorialAudioPlayer(options) {
  'use strict';
  function el(name) { return document.getElementById('kg_tutorial_listen_' + name); }
  var enabled = false, ready = false, step = null;
  var media = null, url = null, serial = 0, message = '';
  try { enabled = localStorage.getItem('srkg.tutorial.voice') === 'true'; } catch (error) { /* Local preference is optional. */ }
  function render() {
    el('controls').hidden = !(step && step.audio);
    el('controls').parentElement.classList.toggle('kg-has-voice', !el('controls').hidden);
    el('enabled').checked = enabled;
    el('enabled').disabled = !ready;
    el('status').textContent = message;
    el('status').title = message;
    if (options.changed) { options.changed(); }
  }
  function release() {
    serial += 1;
    if (media) { media.pause(); media.removeAttribute('src'); media.load(); media = null; }
    if (url) { URL.revokeObjectURL(url); url = null; }
  }
  function preference(value) {
    enabled = Boolean(value);
    try { localStorage.setItem('srkg.tutorial.voice', String(enabled)); } catch (error) { /* Keep the session preference. */ }
  }
  function startRoute(hasAudio, choice) {
    release(); step = null; ready = false; message = '';
    if (hasAudio && choice !== undefined) { preference(choice); }
    render();
  }
  function prepare(card) {
    release(); step = card; ready = false;
    message = card && card.audio ? 'Voice is preparing.' : '';
    render();
  }
  async function play() {
    if (!ready || !enabled || !step || !step.audio) { return; }
    var token = serial, current;
    try {
      message = 'Loading voice…'; render();
      var asset = await options.getAudio(step.audio.assetId);
      if (token !== serial) { return; }
      if (!asset || !(asset.blob instanceof Blob) || !asset.blob.size) {
        throw new Error('Recording is missing from this browser.');
      }
      current = new Audio(); media = current;
      url = URL.createObjectURL(asset.blob); current.src = url;
      current.addEventListener('ended', function() {
        if (token !== serial) { return; }
        message = 'Voice finished.'; render();
      });
      await current.play();
      if (token !== serial) { current.pause(); return; }
      message = 'Playing voice.'; render();
    } catch (error) {
      if (token !== serial) { return; }
      release();
      message = 'Voice unavailable: ' + error.message + ' Turn Voice off and on to retry.';
      render();
    }
  }
  function settled(success, autoplay) {
    ready = Boolean(success);
    message = !success ? 'Voice stopped because the card could not finish.' :
      !step || !step.audio ? '' : enabled && !autoplay ? 'Turn Voice off and on to listen again.' : '';
    render();
    if (ready && enabled && autoplay) { play(); }
  }
  function suspend() { release(); ready = false; message = ''; render(); }
  function stop() { release(); ready = false; step = null; message = ''; render(); }
  el('enabled').addEventListener('change',function() {
    preference(this.checked);
    if (!enabled) { release(); message = ''; render(); }
    else { render(); play(); }
  });
  window.addEventListener('pagehide',stop);
  return {startRoute:startRoute, prepare:prepare, settled:settled, suspend:suspend, stop:stop};
}
