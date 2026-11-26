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

The payload is just `{"event":"pageview","path":"<fixed path>"}`. Query strings,
fragments, referrers, tutorial IDs, study actions and personal data are outside
the event. The gate has no URL or storage-based enable switch. No production
page loads the module in this phase. It has no endpoint, SDK, preference
storage or automatic network request. The future release integration must
supply its channel from reviewed build configuration and keep the default off.
It must not alter the HTML after the exact build has been tested.

Browser tests intercept navigation to synthetic pages and use an in-memory
collector. The production-origin preview URLs, local URLs, unlisted routes,
disabled collection, declined or unset choice, and Global Privacy Control all
send zero events. Repeated calls and in-document navigation do not add events.

## Provider review

| Option | Fit for this scope |
| --- | --- |
| [Plausible Events API](https://plausible.io/docs/events-api) | A PhysicsKG-owned adapter can send a canonical URL built from the fixed path, omit event referrer and disable optional metrics. Its [data policy](https://plausible.io/data-policy) says it derives device, location and a daily visitor identifier from request metadata, retains individual event and session records, and does not store raw IP addresses or User-Agent strings. Use it only if this additional processing is acceptable. |
| [Cloudflare Web Analytics](https://developers.cloudflare.com/web-analytics/get-started/) | Can be manually installed with GitHub Pages, but the [beacon](https://developers.cloudflare.com/speed/observatory/rum-beacon/) also sends performance and referral data. That is beyond the proposed three counts. |
| [Betterloop ingest](https://betterloopai.com/docs/api#ingest) | The issue commenter discloses maintaining the service. The [provider's data notes](https://betterloopai.com/docs/privacy) document per-event User-Agent storage and a session ID. Those fields do not help these totals. The comment and vendor documentation do not independently establish the collector's behaviour. |
| Aggregate-only counter | Store only a day, one of the three fixed page labels, and a count. Requires running a service alongside GitHub Pages. Request metadata may still be present in hosting or abuse logs, so verify retention there too. |

Shortlist Plausible if its extra processing is acceptable. Choose a minimal
counter if stored data must be limited to aggregate totals. Before choosing,
confirm hosting, retention, deletion, processor terms and any subprocessor use.
Inspect a candidate adapter's actual request against a fake endpoint before
a live trial. Omit the HTTP Referer with an explicit no-referrer policy and omit
credentials where the API permits. The JSON allowlist alone does not control
network metadata such as source IP and User-Agent.

## Privacy wording and release decision

Keep the current public policy unchanged while collection is disabled. Before
activation, add a short website analytics section that names the provider,
explains the three totals and their purpose, describes request metadata and
retention, and links to a way to decline or withdraw. Suggested core wording:

> If you allow website analytics, PhysicsKG counts opens of the home page,
> atlas and user guide to understand how the site is used. The analytics
> event contains the page path. It does not contain your tutorial selection,
> reading or study activity, notes or recordings. You can change your choice
> at any time.

Complete that text with the chosen provider and the verified processing and
retention details before publishing it. The planned gate requires affirmative
choice. The [ICO's statistical purposes guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/what-are-the-exceptions/)
describes a conditional UK exception, including clear information and a simple,
free means to object. Treat any move to opt-out as a separate decision.

Provider, visitor preference interface and release activation are unresolved.
Test the eventual wiring through both archive channels before enabling it.
