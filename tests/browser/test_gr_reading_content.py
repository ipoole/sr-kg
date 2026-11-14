"""Real GR statements, local explanations and mathematics render in both pane widths."""
import csv
import pytest
from conftest import REPO_ROOT, _prepare_browser_output, _open_browser_graph


@pytest.fixture(scope='session')
def gr_reading_output(tmp_path_factory):
    return _prepare_browser_output(tmp_path_factory.mktemp('gr-reading'),
                                   REPO_ROOT/'data', 'GR teaching revision')


@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('number', [1, 2, 3, 4, 5, 6])
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_gr_module_math_and_canonical_blocks(gr_reading_output, playwright_browser, number, width):
    with (REPO_ROOT/'domains/gr/data/modules.csv').open() as f:
        module = list(csv.DictReader(f))[number-1]['module_id']
    with (REPO_ROOT/'domains/gr/data/module_members.csv').open() as f:
        owners = [r['concept_id'] for r in csv.DictReader(f) if r['module_id'] == module]
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, gr_reading_output,
                             {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page
        page.locator('#kg_view_select').select_option('details')
        overflows = []
        for owner in owners:
            graph.click_concept(owner)
            blocks = page.locator('#info_panel > .content-block')
            assert blocks.locator(':scope > summary .kg-content-statement').count() == blocks.locator(':scope:not(.content-block-graphic)').count(), owner
            blocks.evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.locator('#info_panel .kg-local-explanation').evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.wait_for_function('window.MathJax && typeof MathJax.typesetPromise==="function"')
            page.evaluate('MathJax.startup.promise')
            page.evaluate('MathJax.typesetPromise([document.getElementById("info_panel")])')
            assert not page.locator('#info_panel mjx-merror,#info_panel [data-mjx-error]').count(), owner
            assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1'), owner
            overflows.extend((owner, text) for text in blocks.locator('mjx-container[display="true"]').evaluate_all('es=>es.filter(e=>e.clientWidth && e.scrollWidth>e.clientWidth+2).map(e=>e.textContent)'))
            assert page.locator('#info_panel > .content-block-graphic .concept-graphic').count() == 1
        assert not overflows, overflows
        assert not graph.page_errors


@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('root', ['gr.einstein_field_equations', 'gr.gravitational_waves', 'gr.effective_potential_orbits'])
def test_gr_reading_routes_follow_registered_dependencies(gr_reading_output, playwright_browser, root):
    from test_maths_reading_trees import _reveal_tree
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, gr_reading_output) as graph:
        page = graph.page
        page.locator('#kg_view_select').select_option('details')
        graph.click_concept(root)
        for recipe, preset in [('derivation', 'derivation'), ('teaching', 'foundations')]:
            card = page.locator(f'details.kg-reading-tree[data-reading-recipe="{recipe}"]')
            _reveal_tree(page, card, max_depth=page.evaluate('Object.keys(conceptData).length'),
                         unique_concepts=True)
            expected = page.evaluate('(a)=>kgComputeContext({type:"concept",id:a.root},{preset:a.preset,depth:"transitive"})',
                                    {'root': root, 'preset': preset})
            actual = card.locator('[data-reading-edge]').evaluate_all('es=>[...new Set(es.map(e=>e.dataset.readingEdge))]')
            assert set(actual) == set(expected['edgeIds'])
            assert not card.locator('.kg-reading-block[open]').count()
            card.evaluate('e=>e.open=false')
        assert not graph.page_errors
