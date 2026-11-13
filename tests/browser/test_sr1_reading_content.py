"""Actual SR-1 authoring renders and follows its physical-postulate graph."""
import csv

import pytest

from conftest import REPO_ROOT, _prepare_browser_output, _open_browser_graph
from test_maths_reading_trees import _block, _reveal_tree


@pytest.fixture(scope='session')
def sr1_reading_output(tmp_path_factory):
    return _prepare_browser_output(tmp_path_factory.mktemp('sr1-reading'),
                                   REPO_ROOT / 'data', 'SR-1 reading', domains=['sr', 'math'])


@pytest.mark.browser
@pytest.mark.browser_full
@pytest.mark.parametrize('width', [390, 1280], ids=['phone', 'desktop'])
def test_sr1_native_content_and_generated_routes(sr1_reading_output, playwright_browser, width):
    members = csv.DictReader((REPO_ROOT / 'domains/sr/data/module_members.csv').open())
    owners = [r['concept_id'] for r in members if r['module_id'] == 'sr.spacetime_foundations']
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, sr1_reading_output,
                             {'viewport': {'width': width, 'height': 900}}) as graph:
        page = graph.page
        page.locator('#kg_view_select').select_option('details')
        for owner in owners:
            graph.click_concept(owner)
            assert page.locator('#info_panel > .content-block:not(.content-block-graphic)[open]').count() == 0
            blocks = page.locator('#info_panel > .content-block')
            assert blocks.locator(':scope > summary .kg-content-statement').count() == blocks.locator(':scope:not(.content-block-graphic)').count()
            blocks.evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.locator('#info_panel .kg-local-explanation').evaluate_all('es=>es.forEach(e=>e.open=true)')
            page.wait_for_function('window.MathJax && typeof MathJax.typesetPromise==="function"')
            page.evaluate('MathJax.startup.promise')
            page.evaluate('MathJax.typesetPromise([document.getElementById("info_panel")])')
            assert page.locator('#info_panel mjx-merror,#info_panel [data-mjx-error]').count() == 0, owner
            assert page.locator('#info_panel').evaluate('e=>e.scrollWidth<=e.clientWidth+1'), owner
            assert page.locator('#info_panel .concept-graphic').count() == 1
        graph.click_concept('sr.time_dilation')
        for recipe, preset in [('derivation', 'derivation'), ('teaching', 'foundations')]:
            card = page.locator(f'details.kg-reading-tree[data-reading-recipe="{recipe}"]')
            _reveal_tree(page, card)
            expected = page.evaluate("""preset=>kgComputeContext({type:'concept',id:'sr.time_dilation'},
                {preset,depth:'transitive'})""", preset)
            actual = card.locator('[data-reading-edge]').evaluate_all(
                'es=>[...new Set(es.map(e=>e.dataset.readingEdge))]')
            assert set(actual) == set(expected['edgeIds'])
            assert card.locator('.kg-reading-block[open]').count() == 0
        assert not graph.page_errors


@pytest.mark.browser
@pytest.mark.browser_full
def test_sr1_saved_figure_note_and_shared_read_tick(sr1_reading_output, playwright_browser):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, sr1_reading_output) as graph:
        page = graph.page
        page.evaluate("""() => {
          const now='2026-11-12T12:00:00Z';
          kgPersonalData.replaceNotes([{
            id:'old-event-figure',targetType:'concept',targetId:'sr.spacetime_event',
            conceptId:'sr.spacetime_event',placement:'anchor',section:'Graphic',
            anchor:{blockId:'',sectionKey:'graphic',blockIndex:0},
            title:'Saved figure note',body:'A personal observation.',createdAt:now,updatedAt:now
          }]);
          kgContentReadProgress.setRead('sr.lorentz_transformations.definition',true);
        }""")
        page.reload(wait_until='load')
        graph.click_concept('sr.spacetime_event')
        page.locator('#kg_view_select').select_option('details')
        assert _block(page, 'sr.spacetime_event.graphic').locator(
            '.user-note[data-note-id="old-event-figure"]').count() == 1
        assert page.locator('#info_panel .kg-unmatched-notes').count() == 0
        graph.click_concept('sr.time_dilation')
        card = page.locator('details.kg-reading-tree[data-reading-recipe="derivation"]')
        _reveal_tree(page, card)
        copies = card.locator('[data-content-block-id="sr.lorentz_transformations.definition"]')
        assert copies.count() > 0
        copies.first.locator(':scope > summary .content-block-read-toggle').uncheck()
        graph.click_concept('sr.lorentz_transformations')
        assert not _block(page, 'sr.lorentz_transformations.definition').locator(
            ':scope > summary .content-block-read-toggle').is_checked()
        assert not graph.page_errors


@pytest.mark.browser_full
@pytest.mark.browser
def test_native_graphic_is_open_and_caption_only(sr1_reading_output, playwright_browser):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, sr1_reading_output) as graph:
        graph.click_concept('sr.spacetime_event')
        graphic = _block(graph.page, 'sr.spacetime_event.graphic')
        assert graphic.evaluate('e=>e.open')
        assert graphic.locator(':scope > summary .kg-content-statement').count() == 0
        assert graphic.locator('.kg-shared-figure').count() == 1
        assert graphic.locator(':scope > .content-block-body > .concept-line').count() == 0
