const siteOrigin = 'https://physicskg.org';
const pages = new Map([
  ['/pageview/home', 'home'],
  ['/pageview/atlas', 'atlas'],
  ['/pageview/guide', 'guide'],
]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const page = pages.get(url.pathname);
    if (!page || url.search) return new Response(null, {status: 404});
    if (request.method !== 'POST') {
      return new Response(null, {status: 405, headers: {Allow: 'POST'}});
    }
    if (request.headers.get('Origin') !== siteOrigin ||
        request.headers.get('Sec-GPC') === '1') {
      return new Response(null, {status: 403});
    }
    // Workers can expose an empty POST as a stream rather than null.
    if (request.body) {
      const reader = request.body.getReader();
      const {done} = await reader.read();
      if (!done) {
        await reader.cancel();
        return new Response(null, {status: 400});
      }
    }

    const day = new Date().toISOString().slice(0, 10);
    await env.COUNTS.prepare(`
      INSERT INTO daily_pageviews (day, page, views) VALUES (?, ?, 1)
      ON CONFLICT (day, page) DO UPDATE SET views = views + 1
    `).bind(day, page).run();
    return new Response(null, {status: 204});
  },
};
