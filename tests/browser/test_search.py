import pytest

pytestmark = pytest.mark.browser


def test_exact_title_search_opens_real_concept_first(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_search()
    page.locator('#kg_search').fill('Lorentz transformations')
    page.locator('#kg_search').press('Enter')
    assert page.locator('#kg_concept_list button').first.get_attribute('data-concept-id') == 'sr.lorentz_transformations'
    assert 'Lorentz transformations' in page.locator('#info_panel h2').inner_text()
    assert page.url.endswith('#concept-sr.lorentz_transformations')


def test_exact_module_beats_partial_concept_title(browser_graph):
    page = browser_graph.page
    page.evaluate("conceptData['1.1'].label = 'Applications overview'")
    browser_graph.open_search()
    page.locator('#kg_search').fill('Applications')
    page.locator('#kg_search').press('Enter')
    assert page.locator('#kg_concept_list button').first.get_attribute('data-module-id') == 'test.m02_applications'
    assert page.locator('#info_panel h2').inner_text() == 'Applications'


def test_search_ties_empty_and_no_results(browser_graph):
    page = browser_graph.page
    browser_graph.open_search()
    page.locator('#kg_search').fill('definition')
    assert page.locator('#kg_concept_list .kg-concept-item').evaluate_all(
        "els => els.map(el => el.dataset.conceptId)"
    ) == ['1.1', '2.1', '2.2', '3.1']
    page.locator('#kg_search').fill('2.2')
    page.locator('#kg_search').press('Enter')
    assert page.url.endswith('#concept-2.2')
    page.locator('#kg_search').fill('unmatchedxyz')
    page.locator('#kg_search').press('Enter')
    assert 'No matching' in page.locator('#kg_concept_list').inner_text()
    assert page.url.endswith('#concept-2.2')
    page.locator('#kg_search').fill('')
    assert page.locator('#kg_concept_list .kg-concept-item').count() == 4


@pytest.mark.parametrize('width', [1024, 1440, 390])
def test_header_search_keyboard_and_panel_fit(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({'width': width, 'height': 844})
    assert page.evaluate("""() => {
      const search = document.getElementById('kg_search_toggle').getBoundingClientRect();
      return [...document.querySelectorAll('#kg_app_header button, #kg_app_header select')]
        .filter(el => el.id !== 'kg_search_toggle').every(el => {
          const r = el.getBoundingClientRect();
          return Math.max(r.left, search.left) >= Math.min(r.right, search.right) ||
            Math.max(r.top, search.top) >= Math.min(r.bottom, search.bottom);
        });
    }""")
    page.locator('#kg_search_toggle').click()
    assert page.locator('#kg_search').evaluate('el => el === document.activeElement')
    assert page.locator('#kg_controls #kg_search').count() == 0
    panel = page.locator('#kg_search_section')
    box = panel.bounding_box()
    assert 0 <= box['x'] and box['x'] + box['width'] <= width
    assert panel.evaluate('el => el.scrollWidth <= el.clientWidth + 1')
    page.locator('#kg_search').fill('Beta')
    page.locator('#kg_search').press('ArrowDown')
    assert page.locator('#kg_concept_list button').first.evaluate('el => el === document.activeElement')
    page.keyboard.press('Enter')
    assert page.url.endswith('#concept-2.1')
    page.keyboard.press('Escape')
    assert not panel.is_visible()
    assert page.locator('#kg_search_toggle').evaluate('el => el === document.activeElement')


def test_search_snippets_normalise_nested_markup(browser_graph):
    page = browser_graph.page
    page.evaluate(r"""() => {
      conceptData['2.1'].sections[0].text = String.raw`A ratio \(\frac{1}{\sqrt{1-\beta^2}}\) with \overset{boost}{=} and \cref{Alpha}{1.1}. \optional_details{Extra}{A ratio \(x^2\) <script>alert(1)</script>}`;
    }""")
    browser_graph.open_search()
    page.locator('#kg_search').fill('ratio')
    snippets = page.locator('#kg_concept_list .kg-search-snippets').inner_text()
    assert 'ratio' in snippets and 'Alpha' in snippets
    assert '\\' not in snippets and '{' not in snippets
    assert 'sqrt' in snippets and 'β' in snippets
    assert page.locator('#kg_concept_list script').count() == 0
    assert page.locator('#kg_concept_list .kg-search-mark').count() > 0
