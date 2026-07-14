import math

import pytest


def _view_state(page):
    return page.evaluate(
        """() => ({
          position: network.getViewPosition(),
          scale: network.getScale(),
          hiddenNodes: Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)])),
          hiddenEdges: edges.get().map(edge => ({
            from: String(edge.from),
            to: String(edge.to),
            relation: String(edge.relation),
            hidden: Boolean(edge.hidden)
          }))
        })"""
    )


def _view_distance(left, right):
    return math.hypot(
        left["position"]["x"] - right["position"]["x"],
        left["position"]["y"] - right["position"]["y"],
    )


def _wait_for_refit(page):
    page.wait_for_timeout(700)


def _enter_browsing_mode(page, mode):
    page.locator('.kg-concept-item[data-concept-id="3.1"]').click()
    _wait_for_refit(page)

    if mode == "all":
        return
    if mode == "neighbourhood":
        page.locator("#kg_graph_view_select").select_option("neighbourhood-1")
    elif mode == "descendants":
        page.locator("#kg_graph_view_select").select_option("descendants")
    else:
        raise AssertionError(f"unknown mode: {mode}")
    _wait_for_refit(page)


@pytest.mark.browser
@pytest.mark.parametrize("mode", ["all", "neighbourhood", "descendants"])
def test_panel_visibility_changes_automatic_fit_space_in_browsing_modes(
    browser_graph,
    mode,
):
    page = browser_graph.page
    _enter_browsing_mode(page, mode)

    panels_visible = _view_state(page)
    page.locator("#kg_info_toggle").click()
    _wait_for_refit(page)
    details_hidden = _view_state(page)
    page.locator("#kg_controls_toggle").click()
    _wait_for_refit(page)
    both_hidden = _view_state(page)

    assert page.locator("#info_panel").evaluate("el => el.classList.contains('kg-hidden')")
    assert page.locator("#kg_controls").evaluate("el => el.classList.contains('kg-hidden')")
    assert _view_distance(panels_visible, details_hidden) > 10
    assert _view_distance(details_hidden, both_hidden) > 10
    assert abs(panels_visible["scale"] - details_hidden["scale"]) > 0.001 or (
        _view_distance(panels_visible, details_hidden) > 25
    )

    if mode == "all":
        assert panels_visible["hiddenNodes"] == {
            "1.1": False,
            "2.1": False,
            "2.2": False,
            "3.1": False,
        }
    elif mode == "neighbourhood":
        assert panels_visible["hiddenNodes"] == {
            "1.1": True,
            "2.1": False,
            "2.2": False,
            "3.1": False,
        }
    else:
        assert panels_visible["hiddenNodes"] == {
            "1.1": False,
            "2.1": False,
            "2.2": False,
            "3.1": False,
        }
        assert [
            (edge["from"], edge["to"], edge["relation"])
            for edge in panels_visible["hiddenEdges"]
            if not edge["hidden"]
        ] == [
            ("3.1", "2.1", "DEPENDS_ON"),
            ("2.1", "1.1", "DEPENDS_ON"),
            ("3.1", "2.2", "DEPENDS_ON"),
        ]


@pytest.mark.browser
def test_phone_portrait_and_landscape_use_different_panel_layouts(browser_graph):
    page = browser_graph.page

    page.set_viewport_size({"width": 390, "height": 800})
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_controls", state="attached")
    page.wait_for_function(
        """() =>
          typeof network !== "undefined" &&
          typeof nodes !== "undefined" &&
          typeof edges !== "undefined" &&
          document.querySelector("#kg_node_labels")
        """
    )
    portrait_info = page.locator("#info_panel").bounding_box()
    assert page.locator("#kg_controls").evaluate("el => el.classList.contains('kg-hidden')")
    assert portrait_info["width"] > 340
    assert portrait_info["x"] < 20
    assert portrait_info["y"] > 380

    page.set_viewport_size({"width": 800, "height": 390})
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_controls", state="attached")
    page.wait_for_function(
        """() =>
          typeof network !== "undefined" &&
          typeof nodes !== "undefined" &&
          typeof edges !== "undefined" &&
          document.querySelector("#kg_node_labels")
        """
    )
    landscape_info = page.locator("#info_panel").bounding_box()
    assert page.locator("#kg_controls").evaluate("el => el.classList.contains('kg-hidden')")
    assert landscape_info["width"] < 390
    assert landscape_info["x"] > 430
    assert landscape_info["y"] < 20
    assert landscape_info["height"] > 340
