import math

import pytest


@pytest.mark.browser
def test_legacy_touch_events_can_double_tap_a_folded_module(mobile_repo_browser_graph):
    page = mobile_repo_browser_graph.page
    target = page.evaluate("""() => {
      const node = nodes.get().find(item => item.isModuleNode && !item.hidden);
      const position = network.getPositions([node.id])[node.id];
      const dom = network.canvasToDOM(position);
      const rect = network.canvas.frame.canvas.getBoundingClientRect();
      return {id: node.id, x: rect.left + dom.x, y: rect.top + dom.y};
    }""")

    page.evaluate(
        """target => {
          const canvas = network.canvas.frame.canvas;
          function dispatch(name, touches, changedTouches) {
            const event = new Event(name, {bubbles: true, cancelable: true});
            Object.defineProperties(event, {
              touches: {value: touches},
              changedTouches: {value: changedTouches}
            });
            canvas.dispatchEvent(event);
          }
          function tap(identifier) {
            const touch = {
              identifier,
              clientX: target.x,
              clientY: target.y
            };
            dispatch("touchstart", [touch], [touch]);
            dispatch("touchend", [], [touch]);
          }
          tap(1);
          tap(2);
        }""",
        target,
    )

    page.wait_for_function(
        "nodeId => !nodes.get(nodeId) || nodes.get(nodeId).hidden",
        arg=target["id"],
    )


@pytest.mark.browser
def test_phone_touch_can_select_pan_and_pinch_zoom_graph(mobile_repo_browser_graph):
    page = mobile_repo_browser_graph.page

    assert page.locator("#mynetwork canvas").evaluate(
        "element => getComputedStyle(element).touchAction"
    ) == "none"

    target = page.evaluate(
        """() => {
          const node = nodes.get().find(item => !item.hidden);
          const position = network.getPositions([node.id])[node.id];
          const dom = network.canvasToDOM(position);
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          return {id: node.id, x: rect.left + dom.x, y: rect.top + dom.y};
        }"""
    )
    page.evaluate(
        """() => {
          const redraw = network.redraw.bind(network);
          network.redraw = () => {};
          try {
            Object.values(conceptData).forEach(concept =>
              (concept.content_blocks || []).forEach(block =>
                kgContentReadProgress.setRead(block.block_id, true)
              )
            );
            Object.values(moduleData).forEach(module =>
              (module.content_blocks || []).forEach(block =>
                kgContentReadProgress.setRead(block.block_id, true)
              )
            );
          } finally {
            network.redraw = redraw;
          }
          network.redraw();
        }"""
    )
    assert page.evaluate(
        "() => kgGraphCompletionMarkersSnapshot().markers.length"
    ) >= 10
    propagated_pointerups = page.evaluate(
        """target => {
          const canvas = network.canvas.frame.canvas;
          let pointerups = 0;
          canvas.addEventListener('pointerup', () => { pointerups += 1; });
          function tap(pointerId) {
            const options = {
              bubbles: true,
              cancelable: true,
              clientX: target.x,
              clientY: target.y,
              pointerId,
              pointerType: 'touch',
              isPrimary: true
            };
            canvas.dispatchEvent(new PointerEvent('pointerdown', options));
            canvas.dispatchEvent(new PointerEvent('pointerup', options));
          }
          tap(1);
          tap(2);
          return pointerups;
        }""",
        target,
    )
    assert propagated_pointerups == 2
    page.wait_for_function(
        "nodeId => !nodes.get(nodeId) || nodes.get(nodeId).hidden",
        arg=target["id"],
    )

    gesture = page.evaluate(
        """() => {
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          const candidates = [
            [0.18, 0.72], [0.82, 0.72], [0.18, 0.42], [0.82, 0.42]
          ];
          for (const [rx, ry] of candidates) {
            const x = rect.left + rect.width * rx;
            const y = rect.top + rect.height * ry;
            if (!network.getNodeAt({x: x - rect.left, y: y - rect.top})) {
              return {x, y};
            }
          }
          return {x: rect.left + 24, y: rect.bottom - 24};
        }"""
    )
    before_pan = page.evaluate("() => network.getViewPosition()")
    client = page.context.new_cdp_session(page)
    client.send(
        "Input.dispatchTouchEvent",
        {"type": "touchStart", "touchPoints": [{**gesture, "id": 1}]},
    )
    page.wait_for_timeout(50)
    for fraction in (0.3, 0.65, 1):
        client.send(
            "Input.dispatchTouchEvent",
            {
                "type": "touchMove",
                "touchPoints": [
                    {
                        "x": gesture["x"] + 70 * fraction,
                        "y": gesture["y"] + 45 * fraction,
                        "id": 1,
                    }
                ],
            },
        )
        page.wait_for_timeout(35)
    client.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.wait_for_timeout(150)
    after_pan = page.evaluate("() => network.getViewPosition()")
    assert math.hypot(
        after_pan["x"] - before_pan["x"],
        after_pan["y"] - before_pan["y"],
    ) > 1

    canvas = page.locator("#mynetwork canvas").bounding_box()
    centre_x = canvas["x"] + canvas["width"] / 2
    centre_y = canvas["y"] + canvas["height"] / 2
    before_scale = page.evaluate("() => network.getScale()")
    client.send(
        "Input.dispatchTouchEvent",
        {
            "type": "touchStart",
            "touchPoints": [
                {"x": centre_x - 25, "y": centre_y, "id": 1},
                {"x": centre_x + 25, "y": centre_y, "id": 2},
            ],
        },
    )
    client.send(
        "Input.dispatchTouchEvent",
        {
            "type": "touchMove",
            "touchPoints": [
                {"x": centre_x - 75, "y": centre_y, "id": 1},
                {"x": centre_x + 75, "y": centre_y, "id": 2},
            ],
        },
    )
    client.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.wait_for_timeout(150)
    after_scale = page.evaluate("() => network.getScale()")
    assert after_scale > before_scale

