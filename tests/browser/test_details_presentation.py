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
    expect(page.locator('#kg_content_unfold_all')).to_be_hidden()
    page.locator('#info_panel .concept-toc > summary').click()
    page.locator('#kg_content_unfold_all').click()
    assert blocks.evaluate_all('es=>es.every(e=>e.open)')
    assert page.locator('.optional-detail[open], .kg-reading-tree[open], .study-answer[open]').count() == 0
    page.locator('#kg_content_fold_all').click()
    assert blocks.evaluate_all('es=>es.every(e=>!e.open)')
    assert page.evaluate("localStorage.getItem('srkg.contentReadProgress.v1')") == before


@pytest.mark.browser
@pytest.mark.parametrize("view", ["concept:2.2", "module:test.m01_foundations"])
def test_details_masthead_does_not_inherit_content_zoom(browser_graph, view):
    page = browser_graph.page
    page.evaluate("target => kgExecuteViewerCommand({command: 'select', target})", view)
    masthead = page.locator("#info_panel .concept-sticky-header")
    title = masthead.locator(".concept-title")
    contents = masthead.locator(".concept-toc > summary")
    font_size = "el => getComputedStyle(el).fontSize"
    header_sizes = [item.evaluate(font_size) for item in (title, contents)]
    heights = []
    for size in (6, 40):
        page.locator("#info_panel").evaluate(
            "(panel, size) => { panel.style.fontSize = size + 'px'; }", size
        )
        assert [item.evaluate(font_size) for item in (title, contents)] == header_sizes
        assert page.locator("#info_panel .concept-body").first.evaluate(font_size) == f"{size}px"
        heights.append(masthead.bounding_box()["height"])
    assert heights[0] == heights[1]


@pytest.mark.browser
@pytest.mark.parametrize("width", [390, 960], ids=["phone", "narrow-desktop-pane"])
def test_long_details_title_wraps_without_covering_contents(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({"width": width, "height": 844})
    page.locator("#kg_view_select").select_option("both")
    if width > 850:
        page.locator("#kg_pane_splitter").press("End")
    browser_graph.click_concept("2.2")
    masthead = page.locator("#info_panel .concept-sticky-header")
    title = masthead.locator(".concept-title")
    title.evaluate(
        "el => { el.textContent = 'Gamma and the geometry of accelerated motion in special relativity'; }"
    )
    contents = masthead.locator(".concept-toc > summary")
    title_box = title.bounding_box()
    assert title_box["height"] > 1.5 * title.evaluate(
        "el => parseFloat(getComputedStyle(el).lineHeight)"
    )
    assert title_box["x"] + title_box["width"] <= contents.bounding_box()["x"]
    assert title.evaluate("el => el.scrollWidth <= el.clientWidth + 1")
    assert masthead.evaluate("el => el.scrollWidth <= el.clientWidth + 1")
