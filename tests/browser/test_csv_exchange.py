"""CSV exchange contracts shared by notes and personal-data archives."""
from pathlib import Path
import pytest


@pytest.mark.browser
def test_csv_round_trip_preserves_quoted_math_unicode_and_line_endings(playwright_browser):
    _, browser = playwright_browser
    page = browser.new_page()
    try:
        page.add_script_tag(path=str(Path(__file__).resolve().parents[2] / 'srkg/viewer_assets/csv.js'))
        rows = [['id', 'note'], ['01', 'A comma, a "quote" and \\(E=mc^2\\)'],
                ['02', 'Two\nparagraphs\r\nwith café']]
        assert page.evaluate('rows => kgCsv.parse(kgCsv.encode(rows))', rows) == rows
        assert page.evaluate("() => {try {kgCsv.parse('id,\"unfinished');return false;} catch(e){return true;}}")
        # Old standalone notes imports accepted an unfinished last quoted field.
        assert page.evaluate("() => kgCsv.parse('id,\"unfinished',{allowUnclosedQuotes:true})") == [['id', 'unfinished']]
    finally:
        page.close()
