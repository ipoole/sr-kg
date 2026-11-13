"""Block references inspect canonical content without navigating until requested."""
from unittest.mock import patch

import pandas as pd
import pytest
from test_maths_reading_trees import _reveal_tree
from conftest import (_write_browser_fixture, _prepare_browser_output,
                      _create_fixture_svg_graphic, _open_browser_graph)


@pytest.fixture(scope='session')
def block_cref_output(tmp_path_factory):
    root = tmp_path_factory.mktemp('block-crefs')
    _write_browser_fixture(root)
    path = root / 'content_blocks.csv'
    rows = pd.read_csv(path).fillna('')
    rows['statement'] = ''
    rows.loc[rows.block_id == '2.1.explanation', 'body'] = (
        r'Given \cref{this particular argument}{2.2.intuition}, continue here. '
        r'\cref{own definition}{2.1.definition} '
        r'\cref{unavailable}{absent.example.block}')
    rows.loc[rows.block_id == '2.2.intuition', 'statement'] = r'The pairing is \(x^2\).'
    rows.loc[rows.block_id == '2.1.definition', 'body'] = (
        r'Beta definition. \cref{module overview}{test.m01_foundations.overview}')
    rows.loc[rows.block_id == '2.2.intuition', 'body'] = (
        r'A canonical explanation \(x^2+y^2\). '
        r'\explanation{detail}{More detail}{A local clarification.} '
        r'See \cref{earlier definition}{2.1.definition}.' +
        '\nA further paragraph gives enough content to exercise a long block preview.' * 12)
    advanced = rows.iloc[0].copy()
    advanced['block_id'], advanced['concept_id'], advanced['sequence'] = '2.2.deeper', '2.2', 90
    advanced['kind'], advanced['title'] = 'advanced', 'A deeper consequence'
    advanced['statement'], advanced['body'] = 'A further result.', 'The extended argument.'
    rows = pd.concat([rows, advanced.to_frame().T], ignore_index=True)
    rows.to_csv(path, index=False)
    with patch('srkg.graphic_enrichment.createSvgGraphic', side_effect=_create_fixture_svg_graphic):
        return _prepare_browser_output(root, root, 'Block references')


@pytest.mark.browser
@pytest.mark.parametrize('phone', [False, True], ids=['desktop', 'phone'])
def test_block_cref_preview_and_explicit_navigation(block_cref_output, playwright_browser, phone):
    api, browser = playwright_browser
    viewport = {'width': 390 if phone else 1280, 'height': 900}
    with _open_browser_graph(api, browser, block_cref_output,
                             {'viewport': viewport, 'has_touch': phone, 'is_mobile': phone}) as graph:
        page = graph.page
        graph.click_concept('2.1')
        page.locator('#kg_view_select').select_option('details')
        source = page.locator('#info_panel > [data-content-block-id="2.1.explanation"]')
        source.evaluate('e=>e.open=true')
        before = page.evaluate('kgViewerStateSnapshot()')
        personal = page.evaluate('kgPersonalData.getSnapshot()')
        link = source.locator('a[data-block-id="2.2.intuition"]')
        assert link.count() == 1
        if phone:
            link.tap()
        else:
            link.hover()
        popup = page.locator('#kg_concept_preview')
        assert popup.is_visible()
        assert popup.locator('[data-preview-block-id="2.2.intuition"]').count() == 1
        assert popup.locator('.kg-content-statement').count() == 1
        popup.locator('mjx-container').first.wait_for(state='attached')
        body = popup.locator('details.kg-block-preview-body')
        body.locator(':scope > summary').click()
        assert body.evaluate('e=>e.open')
        page.wait_for_function("document.querySelector('.kg-block-preview-body').hasAttribute('data-preview-loaded')")
        page.wait_for_function('''() => {
            const r=document.getElementById('kg_concept_preview').getBoundingClientRect();
            return r.top>=0 && r.bottom<=innerHeight && r.left>=0 && r.right<=innerWidth;
        }''')
        assert popup.locator('mjx-merror,[data-mjx-error]').count() == 0
        assert body.locator('details.kg-local-explanation, details.optional-detail').count() == 1
        assert popup.locator('.kg-note-block-action,.content-block-read-toggle').count() == 0
        assert page.evaluate('kgViewerStateSnapshot()') == before
        assert page.evaluate('kgPersonalData.getSnapshot()') == personal
        assert source.locator('a').count() == 2  # Missing target remains readable plain text.
        popup.locator('.concept-preview-go').click()
        assert page.evaluate('kgViewerStateSnapshot().selection.id') == '2.2'
        native = page.locator('#info_panel > [data-content-block-id="2.2.intuition"]')
        assert native.evaluate('e=>e.open')
        assert page.locator('#kg_concept_preview').is_hidden()
        assert not graph.page_errors


@pytest.mark.browser
def test_advanced_kind_renders_locally_and_is_not_silently_added_to_recipes(block_cref_output, playwright_browser):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, block_cref_output) as graph:
        page = graph.page
        graph.click_concept('2.2')
        page.locator('#kg_view_select').select_option('details')
        advanced = page.locator('#info_panel > .content-block-advanced')
        assert advanced.count() == 1 and not advanced.evaluate('e=>e.open')
        assert advanced.locator('.content-block-kind-label').get_attribute('data-label') == 'Advanced'
        assert advanced.evaluate('e=>getComputedStyle(e).borderLeftColor') != page.locator(
            '#info_panel > .content-block-definition'
        ).evaluate('e=>getComputedStyle(e).borderLeftColor')
        advanced.locator(':scope > summary').click()
        assert advanced.evaluate('e=>e.open')
        for recipe in ('derivation','teaching'):
            card = page.locator(f'details.kg-reading-tree[data-reading-recipe="{recipe}"]')
            _reveal_tree(page, card)
            assert card.locator('[data-content-block-id="2.2.deeper"]').count() == 0
        assert not graph.page_errors


@pytest.mark.browser
def test_block_reference_in_reading_tree_preserves_position_and_camera(block_cref_output, playwright_browser):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, block_cref_output) as graph:
        page = graph.page
        graph.click_concept('3.1')
        page.locator('#kg_view_select').select_option('details')
        card = page.locator('details.kg-reading-tree[data-reading-recipe="teaching"]')
        _reveal_tree(page, card)
        card.locator('.kg-reading-sync').check()
        page.wait_for_timeout(500)  # Explicit sync now fits before preview invariance is measured.
        block = card.locator('[data-content-block-id="2.1.explanation"]').first
        block.evaluate('e=>e.open=true')
        link = block.locator('a[data-block-id="2.2.intuition"]')
        link.focus()
        before = page.evaluate('({state:kgViewerStateSnapshot(),reading:kgReadingTrees.snapshot(),'
                               'camera:network.getViewPosition(),scale:network.getScale(),hash:location.hash})')
        link.press('Enter')
        popup = page.locator('#kg_concept_preview')
        popup.locator('details.kg-block-preview-body > summary').click()
        popup.locator('a[data-block-id="2.1.definition"]').click()
        assert popup.locator('[data-preview-block-id="2.1.definition"]').count() == 1
        assert popup.locator('.kg-content-statement').count() == 0  # Legacy source has none.
        page.keyboard.press('Escape')
        assert popup.is_hidden()
        after = page.evaluate('({state:kgViewerStateSnapshot(),reading:kgReadingTrees.snapshot(),'
                              'camera:network.getViewPosition(),scale:network.getScale(),hash:location.hash})')
        assert after == before
        assert block.evaluate('e=>e.open')
        assert not graph.page_errors


@pytest.mark.browser
def test_same_concept_and_module_block_navigation(block_cref_output, playwright_browser):
    api, browser = playwright_browser
    with _open_browser_graph(api, browser, block_cref_output) as graph:
        page = graph.page
        graph.click_concept('2.1')
        page.locator('#kg_view_select').select_option('details')
        block = page.locator('#info_panel > [data-content-block-id="2.1.explanation"]')
        block.evaluate('e=>e.open=true')
        block.locator('a[data-block-id="2.1.definition"]').click()
        page.locator('#kg_concept_preview .concept-preview-go').click()
        assert page.locator('#info_panel > [data-content-block-id="2.1.definition"]').evaluate('e=>e.open')
        # A module owns canonical authored blocks through the same registry.
        page.locator('#info_panel a[data-block-id="test.m01_foundations.overview"]').click()
        page.locator('#kg_concept_preview .concept-preview-go').click()
        assert page.evaluate('kgViewerStateSnapshot().selection') == {'type': 'module', 'id': 'test.m01_foundations'}
        assert page.locator('#info_panel [data-content-block-id="test.m01_foundations.overview"]').evaluate('e=>e.open')
        assert not graph.page_errors
