"""Bottom controls preserve canonical read state and the surrounding reading path."""
import pytest
from playwright.sync_api import expect
from test_reading_trees import reading_tree_output, reading_graph
from test_maths_reading_trees import _reveal_tree


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_matching_top_and_bottom_read_controls_share_one_record(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({'width': width, 'height': 900})
    browser_graph.click_concept('2.2')
    page.locator('#kg_view_select').select_option('details')
    block = page.locator('[data-content-block-id="2.2.definition"]').first
    tick = block.locator(':scope > summary .content-block-read-toggle')
    assert block.locator(':scope > summary .content-block-read-toggle').count() == 1
    page.wait_for_timeout(500)  # Settle the preceding pane/viewport resize, not the fold.
    camera = page.evaluate('({pos:network.getViewPosition(),scale:network.getScale()})')
    block.locator(':scope > summary').click()
    expect(block.locator(':scope > .kg-content-body > .kg-content-footer .content-block-read-toggle')).to_have_count(1)
    expect(tick).to_be_visible()
    bottom = block.locator(':scope > .kg-content-body > .kg-content-footer .content-block-read-toggle')
    appearance = 'e=>{const s=getComputedStyle(e);return [s.width,s.height,s.fontSize,s.borderRadius,s.borderWidth,s.backgroundColor,s.color]}'
    assert tick.evaluate(appearance) == bottom.evaluate(appearance)
    tick.check()
    expect(bottom).to_be_checked()
    bottom.uncheck()
    expect(tick).not_to_be_checked()
    bottom.check()
    expect(tick).to_be_checked()
    block.locator('.kg-content-footer').evaluate("e=>e.insertAdjacentHTML('beforebegin','<div style=\"height:1300px\"></div>')")
    block.locator(':scope > .kg-content-body > .kg-content-footer .kg-content-refold').click()
    expect(block).not_to_have_attribute('open', '')
    expect(block.locator(':scope > summary .content-block-read-toggle')).to_be_checked()
    expect(block.locator(':scope > summary')).to_be_focused()
    assert block.locator(':scope > summary').bounding_box()['y'] >= page.locator('.concept-sticky-header').bounding_box()['y'] + page.locator('.concept-sticky-header').bounding_box()['height']
    assert page.evaluate('({pos:network.getViewPosition(),scale:network.getScale()})') == camera
    tick.uncheck()
    expect(tick).to_be_disabled()
    assert not browser_graph.page_errors


@pytest.mark.browser
def test_folding_focused_concept_returns_and_preserves_descendants(reading_graph):
    page = reading_graph.page
    card = page.locator('details.kg-reading-tree[data-reading-recipe="teaching"]')
    _reveal_tree(page, card)
    branch = card.locator('.kg-reading-concept-container[data-reading-concept="1.1"]').first
    block = branch.locator('[data-content-block-id="1.1.definition"]').first
    block.locator(':scope > summary').click()
    clarification = block.locator('.kg-local-explanation').first
    clarification.locator(':scope > summary').click()
    branch.locator(':scope > details > .kg-reading-concept-body > .kg-reading-focus-button').click()
    assert page.evaluate('kgReadingTrees.snapshot().focusDepth') == 1
    page.locator('#kg-reading-focus .kg-reading-focus-host > .kg-reading-concept-body > .kg-content-footer .kg-content-refold').click()
    assert page.evaluate('kgReadingTrees.snapshot().focusDepth') == 0
    assert not branch.locator(':scope > details').evaluate('e=>e.open')
    branch.locator(':scope > .kg-reading-concept-title > button').click()
    assert block.evaluate('e=>e.open')
    assert clarification.evaluate('e=>e.open')
    assert page.evaluate('kgViewerStateSnapshot().selection.id') == '3.1'
    assert not reading_graph.page_errors


@pytest.mark.browser
def test_personal_note_folds_without_losing_its_draft(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept('2.2')
    page.locator('#info_panel .kg-note-owner-action').click()
    note = page.locator('#info_panel .kg-owner-notes .user-note')
    note.locator('.user-note-body-input').fill('Keep this draft when folding.')
    note.locator('.kg-content-refold').click()
    expect(note).not_to_have_attribute('open', '')
    note.locator(':scope > summary').click()
    expect(note.locator('.user-note-reading')).to_contain_text('Keep this draft when folding.')
    assert note.locator('.content-block-read-toggle').count() == 0


@pytest.mark.browser
def test_folding_a_synchronised_tree_detaches_only_the_reading_marker(reading_graph):
    page = reading_graph.page
    card = page.locator('details.kg-reading-tree[data-reading-recipe="teaching"]')
    _reveal_tree(page, card)
    card.locator('.kg-reading-sync').check()
    page.wait_for_timeout(500)
    before = page.evaluate('({view:kgViewerStateSnapshot(),camera:network.getViewPosition(),scale:network.getScale()})')
    button = card.locator(':scope > .kg-reading-tree-body > .kg-content-footer .kg-content-refold')
    button.focus()
    button.press('Enter')
    expect(card).not_to_have_attribute('open', '')
    assert page.evaluate('kgReadingTrees.snapshot().synchronised') is None
    assert page.evaluate('({view:kgViewerStateSnapshot(),camera:network.getViewPosition(),scale:network.getScale()})') == before


@pytest.mark.browser
def test_native_and_reading_occurrences_share_kind_colours(reading_graph):
    page = reading_graph.page
    card = page.locator('details.kg-reading-tree[data-reading-recipe="teaching"]')
    _reveal_tree(page, card)
    native = page.locator('#info_panel > [data-content-block-id="3.1.definition"]')
    borrowed = card.locator('[data-content-block-id="3.1.definition"]').first
    appearance = 'e=>{const s=getComputedStyle(e);return {bg:s.backgroundColor,border:s.borderLeftColor}}'
    assert native.evaluate(appearance) == borrowed.evaluate(appearance)
    assert 'gradient' in card.evaluate('e=>getComputedStyle(e).backgroundImage')
    assert card.evaluate('e=>getComputedStyle(e).boxShadow') != 'none'


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_titles_precede_folded_statements_and_statements_hide_when_open(reading_graph, width):
    page = reading_graph.page
    page.set_viewport_size({'width': width, 'height': 950})
    items = [page.locator('#info_panel > [data-content-block-id="3.1.definition"]')]
    items += [page.locator(f'details.kg-reading-tree[data-reading-recipe="{kind}"]')
              for kind in ['derivation', 'teaching']]
    for item in items:
        summary = item.locator(':scope > summary')
        title = summary.locator(':scope > .content-block-title-line')
        statement = summary.locator(':scope > .kg-content-statement')
        expect(statement).to_be_visible()
        assert title.bounding_box()['y'] + title.bounding_box()['height'] <= statement.bounding_box()['y'] + 1
        summary.click()
        expect(statement).to_be_hidden()
        expect(title).to_be_visible()
        summary.click()
        expect(statement).to_be_visible()
    assert not reading_graph.page_errors
