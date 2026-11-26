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

  // Enable in a coordinated release after the Plausible site is ready.
  const enabled = false;
  if (!enabled || origin !== production ||
      (!paths.has(pathname) && pathname !== '/privacy.html')) return;

  const preferenceKey = 'srkg.websiteAnalytics.v1';
  const gpc = window.navigator.globalPrivacyControl === true;
  let allowed = false;
  try {
    allowed = window.localStorage.getItem(preferenceKey) === 'allow';
  } catch {
    // An unavailable preference store defaults to no collection.
  }

  if (pathname === '/privacy.html') {
    const settings = window.document.getElementById('website-analytics-settings');
    const control = window.document.getElementById('website-analytics-allow');
    const status = window.document.getElementById('website-analytics-status');
    settings.hidden = false;
    control.checked = allowed && !gpc;
    control.disabled = gpc;
    if (gpc) status.textContent = 'Global Privacy Control keeps analytics off.';

    control.addEventListener('change', () => {
      try {
        if (control.checked) window.localStorage.setItem(preferenceKey, 'allow');
        else window.localStorage.removeItem(preferenceKey);
        allowed = control.checked;
        status.textContent = allowed ? 'Analytics allowed on this browser.' : 'Analytics off.';
      } catch {
        control.checked = allowed;
        status.textContent = 'This browser could not save the change.';
      }
    });
    window.addEventListener('storage', (event) => {
      if ((event.key === preferenceKey || event.key === null) && !gpc) {
        allowed = event.newValue === 'allow';
        control.checked = allowed;
        status.textContent = '';
      }
    });
    return;
  }

  window.recordPhysicsKGPageview({
    channel: paths.has(pathname) ? 'release' : 'preview',
    enabled,
    allowed,
    collect: collectWithPlausible,
  });
})(window);
