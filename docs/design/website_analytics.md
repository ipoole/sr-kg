# Website analytics for issue #13

PhysicsKG measures document loads of three public pages. A reload can count
again. The totals describe pageviews, and will be lower when visitors leave
analytics off or block the request.

| Total | Exact path | Counter label |
| --- | --- | --- |
| Home pageviews | `/` | `home` |
| Atlas opens | `/output/PhysicsKG.html` | `atlas` |
| Guide pageviews | `/user-guide.html` | `guide` |

## Visitor choice and data flow

The browser sends at most one request per eligible document on
`https://physicskg.org`. The release must enable collection and the visitor
must enable it on the Privacy page. Global Privacy Control overrides that
choice. The preference takes effect on subsequent page loads and defaults
off. PhysicsKG stores only the value `allow` in local storage and removes it
on withdrawal. The site owner can leave analytics off in each browser
profile to exclude their own visits.

The home and guide load the packaged script. The generator embeds the same
script in the standalone atlas. Preview routes are ineligible even when
served from the production origin. The browser posts to a fixed counter
path with an empty body and omits credentials and the HTTP Referer.
No page URL, query string, fragment, tutorial or study activity is sent.

The Worker accepts the three fixed paths and checks the browser Origin
and Global Privacy Control header. One atomic D1 statement increments
the total for that page and the current UTC day. The database stores only
the day, page label and count. Cloudflare receives ordinary request
metadata when serving the Worker. Worker observability is disabled.
The Origin check limits which sites can send requests through ordinary
browsers. A scripted client can forge that header, so these totals are
indicative and can be affected by automated traffic.

## Hosting and operation

Use Cloudflare Workers and D1 on the Free plan. The site can stay on
GitHub Pages. Cloudflare serves only the counting endpoint.
At free-tier limits, requests can fail and totals can undercount.
See the [Workers limits](https://developers.cloudflare.com/workers/platform/limits/)
and [D1 free-tier limits](https://developers.cloudflare.com/d1/reference/faq/).
The earlier Plausible Cloud draft was replaced after reviewing its
recurring subscription price.

Run the local Worker tests with `node --test analytics/worker.test.mjs`
using Node 24 or later. The tests run the same migration and increment
statement against SQLite. The focused Chromium tests intercept requests
from both packaged channels and verify the payload and privacy gate.

For a future activation, sign in to the intended Cloudflare account on
the Free plan and create a D1 database named `physicskg-page-counts`.
Replace the local placeholder ID in `analytics/wrangler.toml` with the
database ID. From `analytics/`, apply the migration with
`npx wrangler d1 migrations apply COUNTS --remote`, then deploy with
`npx wrangler deploy`. See the [D1 setup guide](https://developers.cloudflare.com/d1/get-started/)
and [D1 migrations guide](https://developers.cloudflare.com/d1/reference/migrations/).

Set `counterOrigin` to the deployed Worker origin and enable the website
flag in a coordinated public release. Verify the privacy wording, the
opt-in in an isolated browser profile, and preview exclusion. The site
can remain disabled independently of the Worker.

Read results in the Cloudflare D1 console, without a public report
endpoint. For example, the following gives totals over the current UTC
day and the previous 29 days:

```sql
SELECT page, SUM(views) AS views
FROM daily_pageviews
WHERE day >= date('now', '-29 days')
GROUP BY page
ORDER BY page;
```
