/* Release pageview gate and aggregate counter adapter. */
(function (window) {
  'use strict';

  const production = 'https://physicskg.org';
  const pages = new Map([
    ['/', 'home'],
    ['/output/PhysicsKG.html', 'atlas'],
    ['/user-guide.html', 'guide'],
  ]);
  const {origin, pathname} = window.location;
  let sent = false;

  window.recordPhysicsKGPageview = function ({channel, enabled, allowed, collect} = {}) {
    if (sent || origin !== production || !pages.has(pathname) ||
        channel !== 'release' || enabled !== true || allowed !== true ||
        window.navigator.globalPrivacyControl === true ||
        typeof collect !== 'function') {
      return false;
    }

    sent = true;
    collect({event: 'pageview', path: pathname});
    return true;
  };

  function collectPageview({path}) {
    window.fetch(counterOrigin + '/pageview/' + pages.get(path), {
      method: 'POST',
      mode: 'no-cors',
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
      keepalive: true,
    }).catch(() => {
      // Analytics failures must not interrupt the page.
    });
  }

  // Set the deployed Worker origin and enable in a coordinated release.
  const counterOrigin = '';
  const enabled = false;
  if (!enabled || !counterOrigin || origin !== production ||
      (!pages.has(pathname) && pathname !== '/privacy.html')) return;

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
    channel: 'release',
    enabled,
    allowed,
    collect: collectPageview,
  });
})(window);
