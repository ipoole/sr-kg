import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import { test } from 'node:test';
import worker from './worker.mjs';

test('the Worker stores only atomic daily totals for the three eligible pages', async () => {
  const database = new DatabaseSync(':memory:');
  database.exec(readFileSync(new URL('./migrations/0001_daily_pageviews.sql', import.meta.url), 'utf8'));
  const env = {
    COUNTS: {
      prepare(sql) {
        const statement = database.prepare(sql);
        return { bind: (...values) => ({ run: () => statement.run(...values) }) };
      },
    },
  };
  const headers = { Origin: 'https://physicskg.org' };
  const send = (path, options) => worker.fetch(new Request('https://counter.example' + path, {
    method: 'POST', headers, ...options,
  }), env);

  try {
    const rejected = [
      await send('/pageview/home?private=yes'),
      await send('/pageview/preview'),
      await send('/pageview/home', { method: 'GET' }),
      await send('/pageview/home', { headers: {} }),
      await send('/pageview/home', { headers: { Origin: 'https://example.org' } }),
      await send('/pageview/home', { headers: { ...headers, 'Sec-GPC': '1' } }),
      await send('/pageview/home', { body: 'unexpected' }),
    ];
    assert.deepEqual(rejected.map(response => response.status), [404, 404, 405, 403, 403, 403, 400]);
    assert.equal(database.prepare('SELECT COUNT(*) AS rows FROM daily_pageviews').get().rows, 0);

    const results = await Promise.all([
      send('/pageview/home'),
      send('/pageview/home', {
        body: new ReadableStream({ start: controller => controller.close() }),
        duplex: 'half',
      }),
      send('/pageview/atlas'),
      send('/pageview/guide'),
    ]);
    assert.deepEqual(results.map(response => response.status), [204, 204, 204, 204]);
    const rows = database.prepare('SELECT * FROM daily_pageviews ORDER BY page').all();
    assert.deepEqual(rows.map(row => [row.page, row.views]), [['atlas', 1], ['guide', 1], ['home', 2]]);
    for (const row of rows) {
      assert.deepEqual(Object.keys(row), ['day', 'page', 'views']);
      assert.match(row.day, /^\d{4}-\d{2}-\d{2}$/);
    }
  } finally {
    database.close();
  }
});
