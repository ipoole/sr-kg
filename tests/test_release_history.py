import json
from datetime import date

from srkg.branding import PRODUCT_VERSION
from srkg import html_injection


def test_release_history_has_ordered_unique_versions_and_publication_dates():
    entries = json.loads((html_injection.ASSET_DIR / 'release_history.json').read_text())
    versions = [tuple(int(part) for part in entry['version'].split('.')) for entry in entries]
    assert versions == sorted(set(versions), reverse=True)
    assert entries[0]['version'] == PRODUCT_VERSION
    assert entries[-1]['version'] == '4.0.0'
    dates = [date.fromisoformat(entry['date']) for entry in entries]
    assert dates == sorted(dates, reverse=True)
    assert all(isinstance(entry['summary'], str) and entry['summary'].strip() for entry in entries)


def test_release_history_escapes_content(monkeypatch):
    entries = [{'version': '4.4.0', 'date': '2026-11-03', 'summary': '<script>alert("x")</script>'}]
    monkeypatch.setattr(html_injection, '_asset_text', lambda name: json.dumps(entries))
    rendered = html_injection._release_history_html()
    assert '<script>' not in rendered
    assert '&lt;script&gt;' in rendered
    assert '<time datetime="2026-11-03">' in rendered
