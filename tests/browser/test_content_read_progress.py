import pytest


def _open_gamma_blocks(browser_graph):
    browser_graph.click_concept("2.2")
    return browser_graph.page.locator("#info_panel details.content-block")


@pytest.mark.browser
def test_every_content_block_has_an_accessible_read_checkbox(browser_graph):
    blocks = _open_gamma_blocks(browser_graph)

    assert blocks.count() > 1
    assert blocks.locator(":scope > summary .content-block-read-toggle").count() == blocks.count()
    checkbox = blocks.first.locator(":scope > summary .content-block-read-toggle")
    assert checkbox.get_attribute("aria-label") == "Mark Definition as read"


@pytest.mark.browser
def test_read_checkbox_toggles_and_persists_without_folding_block(browser_graph):
    page = browser_graph.page
    _open_gamma_blocks(browser_graph)
    definition = page.locator(
        '#info_panel details.content-block[data-content-block-id="2.2.definition"]'
    )
    checkbox = definition.locator(".content-block-read-toggle")
    was_open = definition.evaluate("element => element.open")

    checkbox.check()

    assert checkbox.is_checked()
    assert definition.evaluate("element => element.open") == was_open
    definition.locator(":scope > summary").click(position={"x": 8, "y": 8})
    assert checkbox.is_visible()
    assert page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.contentReadProgress.v1')).blocks['2.2.definition']"
    ) is True

    page.reload(wait_until="load")
    page.wait_for_function("() => Boolean(window.kgContentReadProgress)")
    _open_gamma_blocks(browser_graph)
    checkbox = page.locator(
        '#info_panel details.content-block[data-content-block-id="2.2.definition"] '
        ".content-block-read-toggle"
    )
    assert checkbox.is_checked()

    checkbox.uncheck()
    assert page.evaluate(
        "() => Object.hasOwn(JSON.parse(localStorage.getItem('srkg.contentReadProgress.v1')).blocks, '2.2.definition')"
    ) is False


@pytest.mark.browser
def test_read_checkbox_is_keyboard_operable_and_visibly_blue(browser_graph):
    page = browser_graph.page
    checkbox = _open_gamma_blocks(browser_graph).first.locator(
        ":scope > summary .content-block-read-toggle"
    )

    checkbox.focus()
    page.keyboard.press("Space")

    assert checkbox.is_checked()
    colour = checkbox.evaluate("element => getComputedStyle(element).color")
    assert colour == "rgb(23, 105, 170)"


@pytest.mark.browser
def test_concept_header_tick_tracks_completion_of_all_its_blocks(browser_graph):
    blocks = _open_gamma_blocks(browser_graph)
    indicator = browser_graph.page.locator(
        '#info_panel .concept-sticky-header .content-read-complete-indicator'
    )

    assert indicator.is_hidden()
    assert indicator.get_attribute("role") == "img"
    assert indicator.get_attribute("aria-label") == "All content blocks read"

    for index in range(blocks.count()):
        blocks.nth(index).locator(":scope > summary .content-block-read-toggle").check()

    assert indicator.is_visible()
    assert indicator.inner_text() == "✓"
    assert indicator.locator('input, button, [role="checkbox"]').count() == 0

    blocks.first.locator(":scope > summary .content-block-read-toggle").uncheck()
    assert indicator.is_hidden()


@pytest.mark.browser
def test_module_header_tick_tracks_completion_of_its_own_blocks(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    indicator = page.locator(
        '#info_panel .module-sticky-header .content-read-complete-indicator'
    )
    checkbox = page.locator(
        '#info_panel details.module-content-block .content-block-read-toggle'
    )

    assert checkbox.count() == 1
    assert indicator.is_hidden()
    checkbox.check()
    assert indicator.is_visible()
    checkbox.uncheck()
    assert indicator.is_hidden()
