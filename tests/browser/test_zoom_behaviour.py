import pytest


@pytest.mark.browser
@pytest.mark.parametrize('width', [390, 1280])
def test_graphic_caption_stays_below_svg_at_details_zoom(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({'width': width, 'height': 932})
    browser_graph.click_concept('2.2')
    figure = page.locator('#info_panel .concept-figure')
    figure.locator('.concept-figure-body').evaluate('''body => {
      const caption = document.createElement('figcaption');
      caption.className = 'concept-graphic-caption';
      caption.textContent = 'A caption long enough to wrap on a narrow phone screen.';
      body.querySelector('.concept-graphic').after(caption);
    }''')
    for size in [18, 30]:
        page.locator('#info_panel').evaluate('(el, size) => el.style.fontSize = size + "px"', size)
        page.evaluate('window.dispatchEvent(new Event("resize"))')
        page.wait_for_function('''() => parseFloat(getComputedStyle(
          document.querySelector('#info_panel .concept-graphic')).marginBottom) < 0''')
        ink_bottom = figure.locator('svg').evaluate('''svg => {
          const box = svg.getBBox();
          return new DOMPoint(0, box.y + box.height).matrixTransform(svg.getScreenCTM()).y;
        }''')
        caption = figure.locator('figcaption').bounding_box()
        assert caption['y'] >= ink_bottom + 4
        reclaimed, line_height = figure.locator('.concept-graphic').evaluate('''el => [
          -parseFloat(getComputedStyle(el).marginBottom),
          parseFloat(getComputedStyle(el.nextElementSibling).lineHeight)]''')
        assert 0 < reclaimed <= 2 * line_height + 1
    # A drawing that fills the canvas must keep all of its space.
    figure.locator('svg').evaluate('''svg => {
      const full = svg.cloneNode(false), box = svg.viewBox.baseVal;
      full.innerHTML = `<rect x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}"/>`;
      svg.replaceWith(full);
    }''')
    page.evaluate('window.dispatchEvent(new Event("resize"))')
    page.wait_for_function('''() => parseFloat(getComputedStyle(
      document.querySelector('#info_panel .concept-graphic')).marginBottom) === 0''')
    svg = figure.locator('svg').bounding_box()
    assert figure.locator('figcaption').bounding_box()['y'] >= svg['y'] + svg['height'] + 4


def _center(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def _font_size(page, selector):
    return page.locator(selector).evaluate("el => parseFloat(getComputedStyle(el).fontSize)")


def _wait_for_font_size_above(page, selector, initial_size):
    page.wait_for_function(
        """arg => {
          const element = document.querySelector(arg.selector);
          return element && parseFloat(getComputedStyle(element).fontSize) > arg.initialSize;
        }""",
        arg={"selector": selector, "initialSize": initial_size},
    )


def _wait_for_font_size_below(page, selector, initial_size):
    page.wait_for_function(
        """arg => {
          const element = document.querySelector(arg.selector);
          return element && parseFloat(getComputedStyle(element).fontSize) < arg.initialSize;
        }""",
        arg={"selector": selector, "initialSize": initial_size},
    )


@pytest.mark.browser
def test_mouse_wheel_over_graph_changes_network_zoom(browser_graph):
    page = browser_graph.page
    graph_box = page.locator("#mynetwork").bounding_box()
    x, y = _center(graph_box)
    initial_scale = page.evaluate("() => network.getScale()")

    page.mouse.move(x, y)
    page.mouse.wheel(0, -600)
    page.wait_for_function("scale => network.getScale() > scale + 0.01", arg=initial_scale)

    zoomed_scale = page.evaluate("() => network.getScale()")
    assert zoomed_scale > initial_scale + 0.01


@pytest.mark.browser
def test_node_labels_hide_when_zoomed_out_below_readable_size(browser_graph):
    page = browser_graph.page

    page.evaluate(
        """() => {
          network.moveTo({scale: 0.6, animation: false});
          kgUpdateNodeLabelPositions();
        }"""
    )
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
    browser_graph.click_concept("2.1")
    page.wait_for_selector('#info_panel[data-concept-id="2.1"]')
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
    initial_font_size = _font_size(page, "#info_panel")

    page.locator("#info_panel").evaluate(
        """panel => panel.dispatchEvent(new WheelEvent("wheel", {
          bubbles: true,
          cancelable: true,
          ctrlKey: true,
          deltaY: -600
        }))"""
    )
    _wait_for_font_size_above(page, "#info_panel", initial_font_size)

    zoomed_view = page.evaluate(
        """() => ({
          position: network.getViewPosition(),
          scale: network.getScale()
        })"""
    )
    zoomed_font_size = _font_size(page, "#info_panel")
    assert abs(zoomed_view["scale"] - initial_view["scale"]) < 0.001
    assert abs(zoomed_view["position"]["x"] - initial_view["position"]["x"]) < 0.001
    assert abs(zoomed_view["position"]["y"] - initial_view["position"]["y"]) < 0.001
    assert zoomed_font_size > initial_font_size


@pytest.mark.browser
def test_ctrl_wheel_over_details_zooms_concept_graphic(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.2")
    graphic = page.locator("#info_panel .concept-graphic svg")
    initial_box = graphic.bounding_box()

    page.locator("#info_panel").evaluate(
        """panel => panel.dispatchEvent(new WheelEvent("wheel", {
          bubbles: true,
          cancelable: true,
          ctrlKey: true,
          deltaY: -600
        }))"""
    )

    page.wait_for_function(
        """initialWidth => {
          const graphic = document.querySelector("#info_panel .concept-graphic svg");
          return graphic && graphic.getBoundingClientRect().width > initialWidth * 1.03;
        }""",
        arg=initial_box["width"],
    )
    assert graphic.bounding_box()["height"] > initial_box["height"] * 1.03


@pytest.mark.browser
def test_ctrl_wheel_over_details_zooms_module_graphic(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="sr.spacetime_foundations"]'
    ).click()
    graphic = page.locator("#info_panel .module-graphic > svg")
    initial_box = graphic.bounding_box()

    page.locator("#info_panel").evaluate(
        """panel => panel.dispatchEvent(new WheelEvent("wheel", {
          bubbles: true,
          cancelable: true,
          ctrlKey: true,
          deltaY: -600
        }))"""
    )

    page.wait_for_function(
        """initialWidth => {
          const graphic = document.querySelector("#info_panel .module-graphic > svg");
          return graphic && graphic.getBoundingClientRect().width > initialWidth * 1.03;
        }""",
        arg=initial_box["width"],
    )
    assert graphic.bounding_box()["height"] > initial_box["height"] * 1.03


@pytest.mark.browser
def test_ctrl_wheel_over_controls_zooms_controls_text_without_graph_zoom(browser_graph):
    page = browser_graph.page
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
    initial_font_size = _font_size(page, "#kg_controls")
    initial_status_font_size = _font_size(page, "#kg_status")
    initial_list_font_size = _font_size(page, "#kg_module_list")

    wheel_was_cancelled = page.locator("#kg_controls").evaluate(
        """panel => panel.dispatchEvent(new WheelEvent("wheel", {
          bubbles: true,
          cancelable: true,
          ctrlKey: true,
          deltaY: -600
        })) === false"""
    )
    _wait_for_font_size_above(page, "#kg_controls", initial_font_size)

    zoomed_view = page.evaluate(
        """() => ({
          position: network.getViewPosition(),
          scale: network.getScale()
        })"""
    )
    zoomed_font_size = _font_size(page, "#kg_controls")
    zoomed_status_font_size = _font_size(page, "#kg_status")
    zoomed_list_font_size = _font_size(page, "#kg_module_list")
    assert wheel_was_cancelled
    assert abs(zoomed_view["scale"] - initial_view["scale"]) < 0.001
    assert abs(zoomed_view["position"]["x"] - initial_view["position"]["x"]) < 0.001
    assert abs(zoomed_view["position"]["y"] - initial_view["position"]["y"]) < 0.001
    assert zoomed_font_size > initial_font_size
    assert zoomed_status_font_size > initial_status_font_size
    assert zoomed_list_font_size > initial_list_font_size


@pytest.mark.browser
def test_touch_pinch_over_details_zooms_text_and_graphic_without_graph_zoom(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.2")
    page.wait_for_selector('#info_panel[data-concept-id="2.2"]')

    if not page.evaluate("""() => Boolean(window.TouchEvent && window.Touch)"""):
        pytest.skip("Browser does not support synthetic TouchEvent construction")

    initial_scale = page.evaluate("() => network.getScale()")
    initial_font_size = _font_size(page, "#info_panel")
    graphic = page.locator("#info_panel .concept-graphic > svg")
    initial_graphic_box = graphic.bounding_box()

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
    _wait_for_font_size_above(page, "#info_panel", initial_font_size)

    zoomed_scale = page.evaluate("() => network.getScale()")
    zoomed_font_size = _font_size(page, "#info_panel")
    assert move_was_cancelled
    assert abs(zoomed_scale - initial_scale) < 0.001
    assert zoomed_font_size > initial_font_size
    assert graphic.bounding_box()["width"] > initial_graphic_box["width"]

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
    _wait_for_font_size_below(page, "#info_panel", zoomed_font_size)

    reduced_font_size = _font_size(page, "#info_panel")
    assert reduced_font_size < zoomed_font_size
    assert graphic.bounding_box()["width"] < initial_graphic_box["width"] * 1.01
