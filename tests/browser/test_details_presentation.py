"""Reading controls act on local blocks without unfolding whole reading DAGs."""
import pytest
from playwright.sync_api import expect


@pytest.mark.browser
def test_folded_unread_blocks_require_opening_but_allow_clearing_read(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept('2.2')
    block = page.locator('[data-content-block-id="2.2.definition"]').first
    tick = block.locator(':scope > summary .content-block-read-toggle')
    assert not block.evaluate('e=>e.open')
    expect(tick).to_be_disabled()
    block.locator(':scope > summary').click()
    expect(tick).to_be_enabled()
    tick.check()
    block.locator(':scope > summary').click(position={'x': 8, 'y': 8})
    expect(tick).to_be_enabled()
    tick.uncheck()
    expect(tick).to_be_disabled()
    assert not block.evaluate('e=>e.open')


@pytest.mark.browser
def test_bulk_fold_is_local_and_keeps_progress_unchanged(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept('2.2')
    blocks = page.locator('#info_panel > details.content-block')
    before = page.evaluate("localStorage.getItem('srkg.contentReadProgress.v1')")
    page.locator('#kg_content_unfold_all').click()
    assert blocks.evaluate_all('es=>es.every(e=>e.open)')
    assert page.locator('.optional-detail[open], .kg-reading-tree[open], .study-answer[open]').count() == 0
    page.locator('#kg_content_fold_all').click()
    assert blocks.evaluate_all('es=>es.every(e=>!e.open)')
    assert page.evaluate("localStorage.getItem('srkg.contentReadProgress.v1')") == before
