"""Shared prose spacing is independent of source ownership and reading placement."""
import re

import pytest

from test_reading_trees import reading_tree_output, reading_graph


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_text_paragraphs_have_a_gap_without_doubling_authored_blanks(reading_graph, width):
    page = reading_graph.page
    page.set_viewport_size({'width': width, 'height': 950})
    text = 'First paragraph.\nSecond paragraph.\n\nThird paragraph.'
    page.evaluate(r'''text => {
        conceptData['3.1'].content_blocks.find(b=>b.block_id==='3.1.definition').body =
            text + '\n' + String.raw`\explanation{closer}{A closer look}{${text}}`;
    }''', text)
    reading_graph.click_concept('2.1')
    reading_graph.click_concept('3.1')
    native = page.locator('#info_panel > [data-content-block-id="3.1.definition"]')
    native.locator(':scope > summary').click()
    clarification = native.locator('.kg-local-explanation').first
    clarification.locator(':scope > summary').click()
    card = page.locator('.kg-reading-tree[data-reading-recipe="teaching"]')
    card.locator(':scope > summary').click()
    borrowed = card.locator('[data-content-block-id="3.1.definition"]').first
    borrowed.locator(':scope > summary').click()
    page.locator('#info_panel .kg-owner-notes .user-note > summary').click()
    page.locator('#info_panel .kg-owner-notes .user-note-edit').click()
    note = page.locator('#info_panel .kg-owner-notes .user-note')
    note.locator('.user-note-body-input').fill(text)
    note.locator('.user-note-close').click()

    for unit in [native, clarification, borrowed, note]:
        lines = [unit.locator('.concept-line').filter(has_text=re.compile('^'+label+r'\.$')).first
                 for label in ['First paragraph', 'Second paragraph', 'Third paragraph']]
        height = lines[0].evaluate('e=>parseFloat(getComputedStyle(e).lineHeight)')
        def gap(a, b):
            first, second = a.bounding_box(), b.bounding_box()
            return (second['y']-first['y']-first['height'])/height
        assert gap(lines[0], lines[1]) == pytest.approx(0.6, abs=0.03)
        assert gap(lines[1], lines[2]) == pytest.approx(1.0, abs=0.03)
