"""Exercise the release gate in Chromium without loading a real collector."""
from urllib.parse import urlsplit

import pytest

from conftest import REPO_ROOT
from srkg.html_injection import inject_controls
from srkg.site_deployment import assemble


@pytest.mark.browser
@pytest.mark.parametrize(
    "url,channel,enabled,allowed,gpc,expected",
    [
        ("https://physicskg.org/?utm_source=example#top", "release", True, True, False, "/"),
        ("https://physicskg.org/output/PhysicsKG.html?tutorial=secret#step-2", "release", True, True, False,
         "/output/PhysicsKG.html"),
        ("https://physicskg.org/user-guide.html#reading-trees", "release", True, True, False, "/user-guide.html"),
        ("https://physicskg.org/preview/PhysicsKG.html", "release", True, True, False, None),
        ("https://physicskg.org/preview/user-guide.html", "release", True, True, False, None),
        ("https://physicskg.org/index.html", "release", True, True, False, None),
        ("https://physicskg.org/output/PhysicsKG.html/", "release", True, True, False, None),
        ("https://www.physicskg.org/", "release", True, True, False, None),
        ("https://physicskg.org:8443/", "release", True, True, False, None),
        ("http://physicskg.org/", "release", True, True, False, None),
        ("http://localhost:8765/", "release", True, True, False, None),
        ("https://physicskg.org/", "preview", True, True, False, None),
        ("https://physicskg.org/", None, True, True, False, None),
        ("https://physicskg.org/", "release", False, True, False, None),
        ("https://physicskg.org/", "release", True, False, False, None),
        ("https://physicskg.org/", "release", True, None, False, None),
        ("https://physicskg.org/", "release", True, True, True, None),
    ],
)
def test_pageview_gate(playwright_browser, url, channel, enabled, allowed, gpc, expected):
    _, browser = playwright_browser
    page = browser.new_page()
    try:
        page.route("**/*", lambda route: route.fulfill(
            content_type="text/html", body="<!doctype html><title>Analytics test</title>"
        ))
        page.add_init_script(
            "Object.defineProperty(navigator, 'globalPrivacyControl', {value: "
            + ("true" if gpc else "false") + "});"
        )
        page.goto(url)
        page.add_script_tag(path=REPO_ROOT / "website" / "page-analytics.js")
        events = page.evaluate(
            """options => {
              const events = [];
              options.collect = event => events.push(event);
              recordPhysicsKGPageview(); // Default configuration sends nothing.
              recordPhysicsKGPageview(options);
              history.pushState({}, '', '/user-guide.html?private=value#next');
              recordPhysicsKGPageview(options);
              return events;
            }""",
            dict(channel=channel, enabled=enabled, allowed=allowed),
        )
        assert events == ([{"event": "pageview", "path": expected}] if expected else [])
    finally:
        page.close()


@pytest.mark.browser
def test_packaged_site_analytics(playwright_browser, tmp_path):
    _, browser = playwright_browser
    viewer = tmp_path / "PhysicsKG.html"
    viewer.write_text(inject_controls(
        "<html><head></head><body></body></html>", {}, {}, "Analytics test"
    ), encoding="utf-8")
    release = assemble(REPO_ROOT, viewer, "release")
    files = assemble(REPO_ROOT, viewer, "preview", previous=release)
    endpoint = "https://counter.example/pageview/"
    routes = {
        "/": "index.html",
        "/user-guide.html": "user-guide.html",
        "/output/PhysicsKG.html": "output/PhysicsKG.html",
        "/preview/user-guide.html": "preview/user-guide.html",
        "/preview/PhysicsKG.html": "preview/PhysicsKG.html",
    }
    for simulate_activation in (False, True):
        page = browser.new_page()
        requests = []

        def serve(route):
            url = urlsplit(route.request.url)
            if route.request.url.startswith(endpoint):
                requests.append(route.request)
                route.fulfill(status=204)
                return
            name = routes.get(url.path, url.path.lstrip("/"))
            if url.netloc != "physicskg.org" or name not in files:
                route.abort()
                return
            data = files[name]
            if not name.endswith((".html", ".js")):
                route.abort()
                return
            if simulate_activation:
                data = data.replace(b"const enabled = false;", b"const enabled = true;")
                data = data.replace(
                    b"const counterOrigin = '';", b"const counterOrigin = 'https://counter.example';"
                )
            route.fulfill(
                content_type="text/html" if name.endswith(".html") else "text/javascript",
                body=data,
            )

        try:
            page.context.add_cookies([{"name": "test", "value": "private", "url": endpoint}])
            page.route("**/*", serve)
            page.goto("https://physicskg.org/?allow=true")
            assert requests == []
            privacy = "https://physicskg.org/privacy.html"
            page.goto(privacy)
            control = page.get_by_role("checkbox", name="Allow website analytics")
            if simulate_activation:
                assert not control.is_checked()
                control.check()
                page.reload()
                assert control.is_checked()
            else:
                assert not control.is_visible()
            for path in routes:
                url = "https://physicskg.org" + path + "?tutorial=private#step-2"
                if simulate_activation and not path.startswith("/preview/"):
                    with page.expect_request(lambda request: request.url.startswith(endpoint), timeout=5000):
                        page.goto(url)
                else:
                    page.goto(url)
                assert page.evaluate("typeof recordPhysicsKGPageview") == "function"
            expected = [endpoint + page for page in ("home", "guide", "atlas")]
            assert [request.url for request in requests] == (expected if simulate_activation else [])
            for request in requests:
                assert request.method == "POST"
                headers = request.all_headers()
                assert request.post_data is None
                assert headers["origin"] == "https://physicskg.org"
                assert "referer" not in headers
                assert "cookie" not in headers
            if simulate_activation:
                page.goto(privacy)
                control.uncheck()
                page.goto("https://physicskg.org/")
                assert len(requests) == len(expected)

                page.goto(privacy)
                control.check()
                page.add_init_script(
                    "Object.defineProperty(navigator, 'globalPrivacyControl', {value: true});"
                )
                page.goto("https://physicskg.org/")
                page.goto(privacy)
                assert not control.is_checked()
                assert control.is_disabled()
                assert len(requests) == len(expected)
        finally:
            page.close()
