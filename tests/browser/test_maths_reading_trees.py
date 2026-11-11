"""Read actual Maths-only content, canonical notes and generated graph routes."""
import pytest

from conftest import REPO_ROOT, _prepare_browser_output, _open_browser_graph


@pytest.fixture(scope='session')
def maths_pilot_output(tmp_path_factory):
    root = tmp_path_factory.mktemp('maths-reading')
    return _prepare_browser_output(root, REPO_ROOT / 'data', 'Maths reading trees', domains=['math'])


def _block(page, id):
    block = page.locator(f'#info_panel > [data-content-block-id="{id}"]')
    block.evaluate('e=>e.open=true')
    return block


def _reveal_tree(page, card):
    card.evaluate('e=>e.open=true')
    page.wait_for_function("id=>document.getElementById(id).hasAttribute('data-reading-loaded')",
                           arg=card.get_attribute('id'))
    for _ in range(12):
        closed = card.locator('.kg-reading-concept:not([open])')
        if not closed.count():
            return
        closed.evaluate_all('es=>es.forEach(e=>e.open=true)')
        page.wait_for_function("""selector=>[...document.querySelectorAll(selector)]
            .filter(e=>e.open).every(e=>e.hasAttribute('data-reading-loaded'))""",
            arg=f'#{card.get_attribute("id")} .kg-reading-concept')
    pytest.fail('Maths reading route did not terminate')


@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_real_maths_routes_equations_and_pane_bounds(maths_pilot_output, playwright_browser, width):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, maths_pilot_output,
                             {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page
        page.locator('#kg_view_select').select_option('details')
        assert page.evaluate('Object.keys(conceptData).every(id=>id.startsWith("math."))')
        for concept in ('manifold', 'coordinate_chart', 'coordinate_transformation',
                        'worldline', 'tangent_space', 'cotangent_space',
                        'tensor_field', 'index_notation', 'tensor_transformation_law'):
            id = 'math.' + concept
            graph.click_concept(id)
            assert page.locator('#info_panel > .content-block[open]').count() == 0
            # Open every real canonical body, including nested local clarifications.
            page.locator('#info_panel > .content-block').evaluate_all('es=>es.forEach(e=>e.open=true)')
            for recipe, preset in [('derivation', 'derivation'), ('teaching', 'foundations')]:
                card = page.locator(f'details.kg-reading-tree[data-reading-recipe="{recipe}"]')
                _reveal_tree(page, card)
                expected = page.evaluate("""a=>kgComputeContext({type:'concept',id:a.id},
                    {preset:a.preset,depth:'transitive'})""", {'id': id, 'preset': preset})
                actual = card.locator('[data-reading-edge]').evaluate_all(
                    'es=>[...new Set(es.map(e=>e.dataset.readingEdge))]')
                assert set(actual) == set(expected['edgeIds'])
                assert card.locator('.kg-reading-block[open]').count() == 0
                card.locator('.kg-reading-block').evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.locator('#info_panel .kg-local-explanation').evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.wait_for_function('window.MathJax && typeof MathJax.typesetPromise==="function"')
            page.evaluate('MathJax.startup.promise')
            page.evaluate('MathJax.typesetPromise([document.getElementById("info_panel")])')
            assert page.locator('#info_panel mjx-merror,#info_panel [data-mjx-error]').count() == 0
            assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
            assert page.locator('#info_panel [id]').evaluate_all(
                'es=>new Set(es.map(e=>e.id)).size===es.length')
        assert not graph.page_errors


@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_maths_migration_preserves_canonical_notes_read_ticks_and_local_slots(
        maths_pilot_output, playwright_browser, width):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, maths_pilot_output,
                             {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page
        page.evaluate("""() => {
          const now='2026-11-08T12:00:00Z';
          kgPersonalData.replaceNotes([{
            id:'old-calculation-note',targetType:'concept',targetId:'math.cotangent_space',
            conceptId:'math.cotangent_space',placement:'anchor',
            section:'The same temperature change on two grids',
            anchor:{blockId:'math.cotangent_space.units_example',sectionKey:'',blockIndex:0},
            title:'Saved note',body:'A personal observation.',createdAt:now,updatedAt:now
          }]);
          kgContentReadProgress.setRead('math.tangent_space.directional_derivative',true);
        }""")
        page.reload(wait_until='load')
        graph.click_concept('math.cotangent_space')
        page.locator('#kg_view_select').select_option('details')
        assert _block(page, 'math.cotangent_space.units_example').locator(
            '.user-note[data-note-id="old-calculation-note"]').count() == 1
        assert page.locator('#info_panel .kg-unmatched-notes').count() == 0
        for source, slot in [('gradient_example','linearity'),('basis','algebra'),
                             ('terrain_survey','centimetres')]:
            local = _block(page, 'math.cotangent_space.' + source).locator(
                f'details[data-content-slot="{slot}"]')
            local.locator(':scope > summary').click()
            assert local.evaluate('e=>e.open')
        card = page.locator('details.kg-reading-tree[data-reading-recipe="teaching"]')
        _reveal_tree(page, card)
        copies = card.locator('[data-content-block-id="math.tangent_space.directional_derivative"]')
        assert copies.count() > 0
        copies.first.locator(':scope > summary .content-block-read-toggle').uncheck()
        graph.click_concept('math.tangent_space')
        native = _block(page, 'math.tangent_space.directional_derivative')
        assert not native.locator(':scope > summary .content-block-read-toggle').is_checked()
        page.reload(wait_until='load')
        graph.click_concept('math.cotangent_space')
        assert _block(page, 'math.cotangent_space.units_example').locator(
            '.user-note[data-note-id="old-calculation-note"]').count() == 1
        assert not graph.page_errors
