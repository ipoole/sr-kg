import pytest


def _center(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


@pytest.mark.browser
def test_mouse_wheel_over_graph_changes_network_zoom(browser_graph):
    page = browser_graph.page
    graph_box = page.locator("#mynetwork").bounding_box()
    x, y = _center(graph_box)
    initial_scale = page.evaluate("() => network.getScale()")

    page.mouse.move(x, y)
    page.mouse.wheel(0, -600)
    page.wait_for_timeout(250)

    zoomed_scale = page.evaluate("() => network.getScale()")
    assert zoomed_scale > initial_scale + 0.01


@pytest.mark.browser
def test_ctrl_wheel_over_details_zooms_details_text_without_graph_zoom(browser_graph):
    page = browser_graph.page
    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    page.wait_for_timeout(250)
    panel_box = page.locator("#info_panel").bounding_box()
    x, y = _center(panel_box)
    initial_scale = page.evaluate("() => network.getScale()")
    initial_font_size = page.locator("#info_panel").evaluate(
        "el => parseFloat(getComputedStyle(el).fontSize)"
    )

    page.mouse.move(x, y)
    page.keyboard.down("Control")
    page.mouse.wheel(0, -600)
    page.keyboard.up("Control")
    page.wait_for_timeout(250)

    zoomed_scale = page.evaluate("() => network.getScale()")
    zoomed_font_size = page.locator("#info_panel").evaluate(
        "el => parseFloat(getComputedStyle(el).fontSize)"
    )
    assert abs(zoomed_scale - initial_scale) < 0.001
    assert zoomed_font_size > initial_font_size
