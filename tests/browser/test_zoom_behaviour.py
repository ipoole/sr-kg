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
def test_node_labels_hide_when_zoomed_out_below_readable_size(browser_graph):
    page = browser_graph.page

    assert page.locator("#kg_node_labels .kg-node-label").first.is_visible()

    page.evaluate(
        """() => {
          network.moveTo({scale: 0.2, animation: false});
          kgUpdateNodeLabelPositions();
        }"""
    )

    assert page.locator("#kg_node_labels .kg-node-label:visible").count() == 0
    assert page.evaluate("""() => nodes.get().some(node => !node.hidden)""")

    page.evaluate(
        """() => {
          network.moveTo({scale: 0.6, animation: false});
          kgUpdateNodeLabelPositions();
        }"""
    )

    assert page.locator("#kg_node_labels .kg-node-label:visible").count() > 0


@pytest.mark.browser
def test_ctrl_wheel_over_details_zooms_details_text_without_graph_zoom(browser_graph):
    page = browser_graph.page
    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    page.wait_for_timeout(700)
    page.evaluate(
        """() => {
          network.moveTo({
            position: {x: 130, y: -90},
            scale: 0.42,
            animation: false
          });
          kgUpdateNodeLabelPositions();
        }"""
    )
    initial_view = page.evaluate(
        """() => ({
          position: network.getViewPosition(),
          scale: network.getScale()
        })"""
    )
    initial_font_size = page.locator("#info_panel").evaluate(
        "el => parseFloat(getComputedStyle(el).fontSize)"
    )

    page.locator("#info_panel").evaluate(
        """panel => panel.dispatchEvent(new WheelEvent("wheel", {
          bubbles: true,
          cancelable: true,
          ctrlKey: true,
          deltaY: -600
        }))"""
    )
    page.wait_for_timeout(250)

    zoomed_view = page.evaluate(
        """() => ({
          position: network.getViewPosition(),
          scale: network.getScale()
        })"""
    )
    zoomed_font_size = page.locator("#info_panel").evaluate(
        "el => parseFloat(getComputedStyle(el).fontSize)"
    )
    assert abs(zoomed_view["scale"] - initial_view["scale"]) < 0.001
    assert abs(zoomed_view["position"]["x"] - initial_view["position"]["x"]) < 0.001
    assert abs(zoomed_view["position"]["y"] - initial_view["position"]["y"]) < 0.001
    assert zoomed_font_size > initial_font_size


@pytest.mark.browser
def test_touch_pinch_over_details_zooms_details_text_without_graph_zoom(browser_graph):
    page = browser_graph.page
    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    page.wait_for_timeout(250)

    if not page.evaluate("""() => Boolean(window.TouchEvent && window.Touch)"""):
        pytest.skip("Browser does not support synthetic TouchEvent construction")

    initial_scale = page.evaluate("() => network.getScale()")
    initial_font_size = page.locator("#info_panel").evaluate(
        "el => parseFloat(getComputedStyle(el).fontSize)"
    )

    move_was_cancelled = page.locator("#info_panel").evaluate(
        """panel => {
          const rect = panel.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;

          function makeTouch(id, x, y) {
            return new Touch({
              identifier: id,
              target: panel,
              clientX: x,
              clientY: y,
              screenX: x,
              screenY: y,
              pageX: x,
              pageY: y
            });
          }

          function dispatch(type, touches) {
            return panel.dispatchEvent(new TouchEvent(type, {
              bubbles: true,
              cancelable: true,
              touches,
              targetTouches: touches,
              changedTouches: touches
            }));
          }

          const startTouches = [
            makeTouch(1, cx - 50, cy),
            makeTouch(2, cx + 50, cy)
          ];
          const widerTouches = [
            makeTouch(1, cx - 90, cy),
            makeTouch(2, cx + 90, cy)
          ];
          dispatch("touchstart", startTouches);
          const moveResult = dispatch("touchmove", widerTouches);
          dispatch("touchend", []);
          return moveResult === false;
        }"""
    )
    page.wait_for_timeout(250)

    zoomed_scale = page.evaluate("() => network.getScale()")
    zoomed_font_size = page.locator("#info_panel").evaluate(
        "el => parseFloat(getComputedStyle(el).fontSize)"
    )
    assert move_was_cancelled
    assert abs(zoomed_scale - initial_scale) < 0.001
    assert zoomed_font_size > initial_font_size

    page.locator("#info_panel").evaluate(
        """panel => {
          const rect = panel.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;

          function makeTouch(id, x, y) {
            return new Touch({
              identifier: id,
              target: panel,
              clientX: x,
              clientY: y,
              screenX: x,
              screenY: y,
              pageX: x,
              pageY: y
            });
          }

          function dispatch(type, touches) {
            panel.dispatchEvent(new TouchEvent(type, {
              bubbles: true,
              cancelable: true,
              touches,
              targetTouches: touches,
              changedTouches: touches
            }));
          }

          dispatch("touchstart", [
            makeTouch(1, cx - 90, cy),
            makeTouch(2, cx + 90, cy)
          ]);
          dispatch("touchmove", [
            makeTouch(1, cx - 50, cy),
            makeTouch(2, cx + 50, cy)
          ]);
          dispatch("touchend", []);
        }"""
    )
    page.wait_for_timeout(250)

    reduced_font_size = page.locator("#info_panel").evaluate(
        "el => parseFloat(getComputedStyle(el).fontSize)"
    )
    assert reduced_font_size < zoomed_font_size
