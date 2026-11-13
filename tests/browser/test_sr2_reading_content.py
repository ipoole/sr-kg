"""The real mechanics authoring remains readable in both native and tree views."""
import csv

import pytest

from conftest import REPO_ROOT, _open_browser_graph
from test_maths_reading_trees import _reveal_tree
from test_sr1_reading_content import sr1_reading_output


@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_sr2_content_equations_and_rest_energy_routes(sr1_reading_output, playwright_browser, width):
    with (REPO_ROOT / 'domains/sr/data/module_members.csv').open() as source:
        owners = [r['concept_id'] for r in csv.DictReader(source)
                  if r['module_id'] == 'sr.relativistic_mechanics']
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, sr1_reading_output,
                             {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page
        page.locator('#kg_view_select').select_option('details')
        for owner in owners:
            graph.click_concept(owner)
            blocks = page.locator('#info_panel > .content-block')
            assert blocks.locator(':scope > summary .kg-content-statement').count() == blocks.locator(':scope:not(.content-block-graphic)').count()
            assert blocks.locator(':scope > summary .content-block-read-toggle').count() == blocks.count()
            blocks.evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.locator('#info_panel .kg-local-explanation').evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.wait_for_function('window.MathJax && typeof MathJax.typesetPromise==="function"')
            page.evaluate('MathJax.startup.promise')
            page.evaluate('MathJax.typesetPromise([document.getElementById("info_panel")])')
            assert page.locator('#info_panel mjx-merror,#info_panel [data-mjx-error]').count() == 0, owner
            assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1'), owner
            assert blocks.locator('mjx-container[display="true"]').evaluate_all(
                'es=>es.every(e=>!e.clientWidth||e.scrollWidth<=e.clientWidth+2)'), owner
            assert page.locator('#info_panel .concept-graphic').count() == 1
        graph.click_concept('sr.mass_energy_equivalence')
        for recipe, preset in [('derivation', 'derivation'), ('teaching', 'foundations')]:
            card = page.locator(f'details.kg-reading-tree[data-reading-recipe="{recipe}"]')
            _reveal_tree(page, card)
            expected = page.evaluate("""preset=>kgComputeContext({type:'concept',id:'sr.mass_energy_equivalence'},
                {preset,depth:'transitive'})""", preset)
            actual = card.locator('[data-reading-edge]').evaluate_all(
                'es=>[...new Set(es.map(e=>e.dataset.readingEdge))]')
            assert set(actual) == set(expected['edgeIds'])
            assert card.locator('.kg-reading-block[open]').count() == 0
            # The radiation transformation used by the root proof is available on its momentum branch.
            if recipe == 'derivation':
                source = card.locator('[data-content-block-id="sr.momentum_four_vector.energy_transformation"]')
                assert source.count() >= 1
                source.first.locator(':scope > summary').click()
                source.first.locator(':scope > summary .content-block-read-toggle').check()
                source.first.locator(':scope > summary').click(position={'x': 8, 'y': 8})
            card.locator('.kg-reading-block').evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.locator('#info_panel .kg-local-explanation').evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.evaluate('MathJax.typesetPromise([document.getElementById("info_panel")])')
            assert page.locator('#info_panel mjx-merror,#info_panel [data-mjx-error]').count() == 0
            assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
            card.evaluate('e=>e.open=false')
        graph.click_concept('sr.momentum_four_vector')
        assert page.locator('#info_panel > [data-content-block-id="sr.momentum_four_vector.energy_transformation"] '
                            '> summary .content-block-read-toggle').is_checked()
        assert not graph.page_errors
