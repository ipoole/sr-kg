/* Release pageview gate and Plausible adapter. */
(function (window) {
  'use strict';

  const production = 'https://physicskg.org';
  const paths = new Set(['/', '/output/PhysicsKG.html', '/user-guide.html']);
  const {origin, pathname} = window.location;
  let sent = false;

  window.recordPhysicsKGPageview = function ({channel, enabled, allowed, collect} = {}) {
    if (sent || origin !== production || !paths.has(pathname) ||
        channel !== 'release' || enabled !== true || allowed !== true ||
        window.navigator.globalPrivacyControl === true ||
        typeof collect !== 'function') {
      return false;
    }

    sent = true;
    collect({event: 'pageview', path: pathname});
    return true;
  };

  function collectWithPlausible({event, path}) {
    window.fetch('https://plausible.io/api/event', {
      method: 'POST',
      mode: 'no-cors',
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
      keepalive: true,
      headers: {'Content-Type': 'text/plain'},
      body: JSON.stringify({
        name: event,
        url: production + path,
        domain: 'physicskg.org',
      }),
    }).catch(() => {
      // Analytics failures must not interrupt the page.
    });
  }

  // Activation and a visitor preference interface require a separate release.
  const enabled = false;
  const allowed = false;
  window.recordPhysicsKGPageview({
    channel: paths.has(pathname) ? 'release' : 'preview',
    enabled,
    allowed,
    collect: collectWithPlausible,
  });
})(window);
