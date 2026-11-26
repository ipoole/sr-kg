# Website analytics for issue #13

Measure how often visitors open three public pages. These are document loads,
so a reload can count again. The totals do not represent unique visitors or
links clicked. Browser blocking and visitor choices can reduce the counts.

| Total | Exact path |
| --- | --- |
| Home pageviews | `/` |
| Atlas opens | `/output/PhysicsKG.html` |
| Guide pageviews | `/user-guide.html` |

## Collection gate

The provider-neutral gate in `website/page-analytics.js` accepts an injected
collector. It captures the origin and path when loaded and hands off at most
one event per document. A call must supply all of the following:

- exact origin `https://physicskg.org` and an allowlisted path;
- channel `release` and an explicitly enabled release setting;
- affirmative visitor choice, with Global Privacy Control overriding it.

The PhysicsKG adapter sends the pageview and its fixed canonical URL to
Plausible. It omits query strings, fragments, HTTP and event referrers
and credentials. The provider still receives ordinary browser request
metadata such as the IP address and User-Agent.

The home and user guide load the packaged script. The viewer embeds it at
generation to preserve standalone use and exact build packaging. The privacy
page holds the opt-in, which takes effect on subsequent page loads and
defaults off. PhysicsKG stores only the value `allow` in this browser's
local storage and removes it on withdrawal. The owner can leave analytics
off on each browser profile to exclude their visits. Preview pages never
read the preference or send events.

Chromium tests use an intercepted production origin and check that disabled
builds are silent. They also simulate activation and verify default-off
behaviour, opt-in, withdrawal, Global Privacy Control and preview exclusion.

## Provider review

| Option | Fit for this scope |
| --- | --- |
| [Plausible Events API](https://plausible.io/docs/events-api) | A PhysicsKG-owned adapter can send a canonical URL built from the fixed path, omit event referrer and disable optional metrics. Its [data policy](https://plausible.io/data-policy) says it derives device, location and a daily visitor identifier from request metadata, retains individual event and session records, and does not store raw IP addresses or User-Agent strings. Use it only if this additional processing is acceptable. |
| [Cloudflare Web Analytics](https://developers.cloudflare.com/web-analytics/get-started/) | Can be manually installed with GitHub Pages, but the [beacon](https://developers.cloudflare.com/speed/observatory/rum-beacon/) also sends performance and referral data. That is beyond the proposed three counts. |
| [Betterloop ingest](https://betterloopai.com/docs/api#ingest) | The issue commenter discloses maintaining the service. The [provider's data notes](https://betterloopai.com/docs/privacy) document per-event User-Agent storage and a session ID. Those fields do not help these totals. The comment and vendor documentation do not independently establish the collector's behaviour. |
| Aggregate-only counter | Store only a day, one of the three fixed page labels, and a count. Requires running a service alongside GitHub Pages. Request metadata may still be present in hosting or abuse logs, so verify retention there too. |

Plausible is the selected provider. Use the three pageview totals for
reporting, especially while traffic is low.

## Production activation

Register `physicskg.org` in the owner's Plausible account before enabling
the integration. The Events API uses that site domain and needs no tracking
snippet or browser API key. Review the provider's retention terms and the
disclosure on the PhysicsKG privacy page before activating the release flag.

The preference and its disclosure appear on the privacy page only when
the feature is enabled. Verify the enabled release and excluded preview
against intercepted requests before publishing. After publication, check
the Plausible dashboard with an explicitly opted-in browser profile and
turn analytics back off in that profile if it was used for verification.
