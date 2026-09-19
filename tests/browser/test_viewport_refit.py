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


def _enter_browsing_mode(browser_graph, mode):
    page = browser_graph.page
    browser_graph.click_concept("3.1")

    if mode == "all":
        return
    if mode == "focused":
        page.locator("#kg_graph_view_select").select_option("focused")
        page.wait_for_function(
            """() => {
              const hidden = Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]));
              return hidden["1.1"] === true &&
                hidden["2.1"] === false &&
                hidden["2.2"] === false &&
                hidden["3.1"] === false;
            }"""
        )
    else:
        raise AssertionError(f"unknown mode: {mode}")


@pytest.mark.browser
@pytest.mark.parametrize("mode", ["all", "focused"])
def test_panel_visibility_changes_automatic_fit_space_in_browsing_modes(
    browser_graph,
    mode,
):
    page = browser_graph.page
    _enter_browsing_mode(browser_graph, mode)

    panes_visible = _view_state(page)
    graph_pane_visible = page.locator("#kg_graph_pane").bounding_box()
    shell = page.locator("#kg_workspace").bounding_box()
    page.locator("#kg_details_view_select").select_option("hide")
    page.wait_for_function(
        """() => {
          const bodyReady = document.body.classList.contains("kg-details-hidden");
          const graph = document.getElementById("kg_graph_pane").getBoundingClientRect();
          const shell = document.getElementById("kg_workspace").getBoundingClientRect();
          return bodyReady && graph.width > shell.width * 0.95;
        }"""
    )
    graph_pane_expanded = page.locator("#kg_graph_pane").bounding_box()

    assert page.locator("body").evaluate("el => el.classList.contains('kg-details-hidden')")
    assert graph_pane_visible["width"] < shell["width"] * 0.55
    assert graph_pane_expanded["width"] > shell["width"] * 0.95

    if mode == "all":
        assert panes_visible["hiddenNodes"] == {
            "1.1": False,
            "2.1": False,
            "2.2": False,
            "3.1": False,
        }
    else:
        assert panes_visible["hiddenNodes"] == {
            "1.1": True,
            "2.1": False,
            "2.2": False,
            "3.1": False,
        }
        assert sorted([
            (edge["from"], edge["to"], edge["relation"])
            for edge in panes_visible["hiddenEdges"]
            if not edge["hidden"]
        ]) == [
            ("3.1", "2.1", "REQUIRES"),
            ("3.1", "2.2", "DERIVES_FROM"),
            ("3.1", "2.2", "REQUIRES"),
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
    portrait_graph = page.locator("#kg_graph_pane").bounding_box()
    portrait_details = page.locator("#kg_details_pane").bounding_box()
    assert page.locator("#kg_controls").evaluate("el => el.classList.contains('kg-hidden')")
    assert portrait_graph["width"] > 360
    assert portrait_details["width"] > 360
    assert portrait_details["y"] > portrait_graph["y"]

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
    landscape_graph = page.locator("#kg_graph_pane").bounding_box()
    landscape_details = page.locator("#kg_details_pane").bounding_box()
    assert page.locator("#kg_controls").evaluate("el => el.classList.contains('kg-hidden')")
    assert landscape_details["x"] > landscape_graph["x"]
    assert abs(landscape_graph["width"] - landscape_details["width"]) <= 2
    assert landscape_graph["height"] > 290
    assert landscape_details["height"] > 290
