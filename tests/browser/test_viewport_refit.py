import math

import pytest


def _disable_camera_animation(page):
    page.evaluate(
        """() => Object.defineProperty(navigator, "hardwareConcurrency", {
          configurable: true,
          get: () => 2
        })"""
    )


def _fit_then_contract(page):
    _disable_camera_animation(page)
    fit_button = page.locator("#kg_fit_apply")
    fit_button.click()
    assert fit_button.inner_text() == "Fit++"
    fit_button.click()
    page.wait_for_function(
        "() => Boolean(window.kgContextContractionSnapshot().active)"
    )


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


def _close_tools_overlay(page):
    page.evaluate(
        """() => {
          const controls = document.getElementById("kg_controls");
          if (controls && !controls.classList.contains("kg-hidden")) {
            kgToggleControls();
          }
        }"""
    )


def _enter_browsing_mode(browser_graph, mode):
    page = browser_graph.page
    browser_graph.click_concept("3.1")

    if mode == "full":
        return
    if mode == "context":
        page.locator("#kg_display_scope_select").select_option("context")
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
@pytest.mark.parametrize("mode", ["full", "context"])
def test_panel_visibility_preserves_camera_in_browsing_modes(
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
    page.wait_for_function(
        """before => {
          const position = network.getViewPosition();
          return Math.abs(network.getScale() - before.scale) < 1e-6 &&
            Math.hypot(position.x - before.position.x, position.y - before.position.y) < 0.1;
        }""",
        arg=panes_visible,
    )
    details_hidden = _view_state(page)

    assert page.locator("body").evaluate("el => el.classList.contains('kg-details-hidden')")
    assert graph_pane_visible["width"] < shell["width"] * 0.55
    assert graph_pane_expanded["width"] > shell["width"] * 0.95
    assert math.isclose(details_hidden["scale"], panes_visible["scale"], abs_tol=1e-6)
    assert _view_distance(details_hidden, panes_visible) < 0.1

    if mode == "full":
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
def test_splitter_and_context_changes_preserve_camera(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("3.1")
    before = _view_state(page)

    page.locator("#kg_context_depth_select").select_option("two-hops")
    page.locator("#kg_pane_splitter").press("End")
    page.wait_for_function(
        """before => {
          const position = network.getViewPosition();
          return Math.abs(network.getScale() - before.scale) < 1e-6 &&
            Math.hypot(position.x - before.position.x, position.y - before.position.y) < 0.1;
        }""",
        arg=before,
    )
    after = _view_state(page)

    assert math.isclose(after["scale"], before["scale"], abs_tol=1e-6)
    assert _view_distance(after, before) < 0.1


@pytest.mark.browser
def test_offscreen_selection_is_revealed_without_zooming_or_recentering(browser_graph):
    page = browser_graph.page
    page.evaluate(
        """() => network.moveTo({
          position: {x: 10000, y: 10000},
          scale: 0.4,
          animation: false
        })"""
    )
    page.wait_for_timeout(50)

    browser_graph.click_concept("3.1")
    page.wait_for_timeout(50)

    result = page.evaluate(
        """() => {
          const point = network.canvasToDOM(network.getPositions(["3.1"])["3.1"]);
          return {
            point,
            width: document.getElementById("mynetwork").clientWidth,
            height: document.getElementById("mynetwork").clientHeight,
            scale: network.getScale()
          };
        }"""
    )
    assert math.isclose(result["scale"], 0.4, abs_tol=1e-6)
    assert 28 <= result["point"]["x"] <= result["width"] - 28
    assert 28 <= result["point"]["y"] <= result["height"] - 28
    assert abs(result["point"]["x"] - result["width"] / 2) > 50


@pytest.mark.browser
def test_fit_controls_are_explicit_camera_actions(browser_graph):
    page = browser_graph.page
    assert page.locator("#kg_fit_select option").evaluate_all(
        "options => options.map(option => option.value)"
    ) == ["reveal", "selection", "context", "displayed"]

    page.evaluate(
        """() => network.moveTo({
          position: {x: 5000, y: 5000},
          scale: 0.2,
          animation: false
        })"""
    )
    before = _view_state(page)
    page.locator("#kg_fit_select").select_option("displayed")
    _disable_camera_animation(page)
    page.locator("#kg_fit_apply").click()
    after = _view_state(page)

    assert not math.isclose(after["scale"], before["scale"], abs_tol=1e-3)
    assert _view_distance(after, before) > 100


@pytest.mark.browser
def test_fit_skips_animation_on_low_capability_devices(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("3.1")
    page.locator("#kg_fit_select").select_option("context")
    animation = page.evaluate("""() => {
      Object.defineProperty(navigator, "hardwareConcurrency", {
        configurable: true,
        get: () => 2
      });
      const original = network.moveTo.bind(network);
      let captured = null;
      network.moveTo = options => {
        captured = options.animation;
        return original(options);
      };
      document.getElementById("kg_fit_apply").click();
      network.moveTo = original;
      return {
        enabled: window.kgCameraAnimationEnabled(),
        animation: captured
      };
    }""")

    assert animation == {"enabled": False, "animation": False}


@pytest.mark.browser
def test_fit_is_disabled_exactly_when_its_frame_target_is_empty(browser_graph):
    page = browser_graph.page
    fit_select = page.locator("#kg_fit_select")
    fit_button = page.locator("#kg_fit_apply")
    scope_select = page.locator("#kg_display_scope_select")

    expected_without_selection = {
        "full": {
            "reveal": True,
            "selection": True,
            "context": True,
            "displayed": False,
        },
        "context": {
            "reveal": True,
            "selection": True,
            "context": True,
            "displayed": True,
        },
    }
    for scope, expected in expected_without_selection.items():
        scope_select.select_option(scope)
        for frame, disabled in expected.items():
            fit_select.select_option(frame)
            assert fit_button.is_disabled() is disabled, (scope, frame, "clear")

    browser_graph.click_concept("3.1")
    for scope in ("full", "context"):
        scope_select.select_option(scope)
        for frame in ("reveal", "selection", "context", "displayed"):
            fit_select.select_option(frame)
            assert fit_button.is_enabled(), (scope, frame, "selected")


@pytest.mark.browser
def test_empty_context_graph_offers_search_and_full_graph_recovery(browser_graph):
    page = browser_graph.page
    empty_state = page.locator("#kg_empty_graph_state")

    assert empty_state.is_hidden()
    page.locator("#kg_display_scope_select").select_option("context")
    assert empty_state.is_visible()
    assert "No context to display" in empty_state.inner_text()
    assert "Search" in empty_state.inner_text()
    assert "Full graph" in empty_state.inner_text()

    empty_state.locator("#kg_empty_graph_search").click()
    assert page.locator("#kg_search_section").get_attribute("open") is not None
    page.locator("#kg_search_close").click()

    empty_state.locator("#kg_empty_graph_show_full").click()
    assert page.locator("#kg_display_scope_select").input_value() == "full"
    assert empty_state.is_hidden()
    assert page.evaluate("() => kgDisplayedGraphSnapshot().fitIds.length") > 0


@pytest.mark.browser
def test_second_context_fit_contracts_around_selection_until_navigation(browser_graph):
    page = browser_graph.page
    _close_tools_overlay(page)
    published = page.evaluate("() => kgGlobalLayoutSnapshot()")
    browser_graph.click_concept("3.1")
    page.locator("#kg_context_depth_select").select_option("two-hops")
    page.locator("#kg_display_scope_select").select_option("context")
    page.evaluate(
        """() => {
          network.moveNode("3.1", 0, 0);
          network.moveNode("2.1", -1200, 0);
          network.moveNode("2.2", 0, -1400);
          network.moveNode("1.1", -2600, 0);
        }"""
    )
    ids = ["1.1", "2.1", "2.2", "3.1"]
    before = page.evaluate("ids => network.getPositions(ids)", ids)

    fit_button = page.locator("#kg_fit_apply")
    _disable_camera_animation(page)
    assert fit_button.inner_text() == "Fit"
    fit_button.click()
    assert fit_button.inner_text() == "Fit++"
    assert page.evaluate("ids => network.getPositions(ids)", ids) == before

    fit_button.click()
    page.wait_for_function(
        "() => Boolean(window.kgContextContractionSnapshot().active)"
    )
    after = page.evaluate("ids => network.getPositions(ids)", ids)
    assert fit_button.inner_text() == "Fit"
    assert after["3.1"] == before["3.1"]
    before_distances = {
        node_id: math.hypot(position["x"], position["y"])
        for node_id, position in before.items()
        if node_id != "3.1"
    }
    after_distances = {
        node_id: math.hypot(position["x"], position["y"])
        for node_id, position in after.items()
        if node_id != "3.1"
    }
    assert all(after_distances[node_id] < before_distances[node_id] for node_id in after_distances)
    assert "temporary" in page.locator("#kg_context_notice").inner_text().lower()
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == published
    assert page.evaluate("() => kgContextContractionSnapshot()") == {
        "primed": False,
        "active": True,
        "anchorId": "3.1",
        "depthByNode": {"1.1": 2, "2.1": 1, "2.2": 1, "3.1": 0},
        "parentByNode": {"1.1": "2.1", "2.1": "3.1", "2.2": "3.1"},
    }
    assert after["1.1"]["x"] < after["2.1"]["x"] < after["3.1"]["x"]

    bounds = page.evaluate(
        """ids => Object.fromEntries(ids.map(id => [id, network.getBoundingBox(id)]))""",
        ids,
    )
    for index, left_id in enumerate(ids):
        for right_id in ids[index + 1 :]:
            left = bounds[left_id]
            right = bounds[right_id]
            assert (
                left["right"] <= right["left"]
                or right["right"] <= left["left"]
                or left["bottom"] <= right["top"]
                or right["bottom"] <= left["top"]
            )

    page.evaluate("() => kgToggleControls()")
    browser_graph.open_control_section("kg_layouts_section")
    assert page.locator("#kg_layout_edit_toggle").is_disabled()
    assert page.evaluate("() => kgLayoutDraggingEnabled()") is True
    page.evaluate(
        """() => {
          network.moveNode("2.1", 777, 888);
          network.emit("dragEnd", {nodes: ["2.1"]});
        }"""
    )
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == published
    assert page.evaluate("() => kgContextContractionSnapshot().active") is True
    assert "navigating away" in page.locator("#kg_context_notice").inner_text().lower()

    browser_graph.click_concept("2.1")
    restored = page.evaluate("ids => network.getPositions(ids)", ids)
    for node_id in ids:
        assert math.isclose(
            restored[node_id]["x"], published["concepts"][node_id]["x"], abs_tol=2
        )
        assert math.isclose(
            restored[node_id]["y"], published["concepts"][node_id]["y"], abs_tol=2
        )
    assert fit_button.inner_text() == "Fit"
    assert page.evaluate("() => kgContextContractionSnapshot().active") is False


@pytest.mark.browser
def test_contraction_graph_plan_walks_arbitrary_depth_and_keeps_shortest_parents(
    browser_graph,
):
    plan = browser_graph.page.evaluate(
        """() => kgContractionGraphPlan({
          anchorId: "root",
          nodeIds: ["root", "near", "left", "right", "leaf"],
          adjacency: {
            root: ["near"],
            near: ["root", "left", "right"],
            left: ["near", "leaf"],
            right: ["near", "leaf"],
            leaf: ["left", "right"]
          }
        })"""
    )

    assert plan["maximumDepth"] == 3
    assert plan["depthByNode"] == {
        "root": 0,
        "near": 1,
        "left": 2,
        "right": 2,
        "leaf": 3,
    }
    assert plan["parentCandidates"]["leaf"] == ["left", "right"]


@pytest.mark.browser
def test_full_graph_fit_plus_moves_only_context_nodes(browser_graph):
    page = browser_graph.page
    _close_tools_overlay(page)
    browser_graph.click_concept("3.1")
    assert page.locator("#kg_display_scope_select").input_value() == "full"
    page.locator("#kg_context_depth_select").select_option("one-hop")
    page.evaluate(
        """() => {
          network.moveNode("3.1", 0, 0);
          network.moveNode("2.1", -1200, 0);
          network.moveNode("2.2", 0, -1400);
          network.moveNode("1.1", 1800, 1600);
        }"""
    )
    context_ids = ["2.1", "2.2", "3.1"]
    all_ids = ["1.1", *context_ids]
    before = page.evaluate("ids => network.getPositions(ids)", all_ids)

    _fit_then_contract(page)
    after = page.evaluate("ids => network.getPositions(ids)", all_ids)

    assert after["1.1"] == before["1.1"]
    assert after["3.1"] == before["3.1"]
    assert math.hypot(after["2.1"]["x"], after["2.1"]["y"]) < math.hypot(
        before["2.1"]["x"], before["2.1"]["y"]
    )
    assert math.hypot(after["2.2"]["x"], after["2.2"]["y"]) < math.hypot(
        before["2.2"]["x"], before["2.2"]["y"]
    )
    assert page.evaluate("() => kgContextContractionSnapshot().active") is True


@pytest.mark.browser
def test_fit_plus_unlocks_only_context_and_suspends_personal_editing(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_layouts_section")
    assert page.locator("#kg_layout_edit_persistence").count() == 0
    personal_toggle = page.locator("#kg_layout_edit_toggle")
    personal_toggle.check()
    assert page.evaluate("() => kgPersistentLayoutEditingEnabled()") is True

    before_layout = page.evaluate("() => kgGlobalLayoutSnapshot()")
    browser_graph.click_concept("3.1")
    page.locator("#kg_context_depth_select").select_option("one-hop")
    _close_tools_overlay(page)
    _fit_then_contract(page)

    page.evaluate("() => kgToggleControls()")
    browser_graph.open_control_section("kg_layouts_section")
    assert personal_toggle.is_checked()
    assert personal_toggle.is_disabled()
    assert "suspended" in page.locator("#kg_layout_edit_message").inner_text().lower()
    assert page.evaluate("() => kgPersistentLayoutEditingEnabled()") is False
    assert page.evaluate("() => kgLayoutDraggingEnabled()") is True
    assert page.evaluate("() => nodes.get('2.1').fixed.x") is False
    assert page.evaluate("() => nodes.get('1.1').fixed.x") is True

    page.evaluate(
        """() => {
          network.moveNode("2.1", 777, 888);
          network.emit("dragEnd", {nodes: ["2.1"]});
        }"""
    )
    assert page.evaluate("() => network.getPositions(['2.1'])['2.1']") == {
        "x": 777,
        "y": 888,
    }
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before_layout
    assert "navigating away" in page.locator("#kg_context_notice").inner_text().lower()

    browser_graph.click_concept("2.1")
    assert personal_toggle.is_enabled()
    assert personal_toggle.is_checked()
    assert page.evaluate("() => kgPersistentLayoutEditingEnabled()") is True
    restored = page.evaluate("() => network.getPositions(['2.1'])['2.1']")
    expected = before_layout["concepts"]["2.1"]
    assert restored["x"] == pytest.approx(expected["x"], abs=2)
    assert restored["y"] == pytest.approx(expected["y"], abs=2)


@pytest.mark.browser
def test_context_contraction_uses_folded_module_as_selection_anchor(browser_graph):
    page = browser_graph.page
    module_id = "test.m02_applications"
    module_node_id = f"module::{module_id}"

    browser_graph.open_control_section("kg_modules_section")
    page.locator(f'.kg-module-item[data-module-id="{module_id}"]').click()
    page.locator(
        '#info_panel .module-graph-fold-button[data-module-fold-state="folded"]'
    ).click()
    browser_graph.click_concept("3.1")
    page.locator("#kg_context_depth_select").select_option("two-hops")
    page.locator("#kg_display_scope_select").select_option("context")
    persistent_anchor = page.evaluate(
        "id => network.getPositions([id])[id]", module_node_id
    )
    page.evaluate(
        """([moduleNodeId]) => {
          network.moveNode(moduleNodeId, 0, 0);
          network.moveNode("1.1", -3200, 0);
        }""",
        [module_node_id],
    )
    before = page.evaluate(
        "ids => network.getPositions(ids)", [module_node_id, "1.1"]
    )

    _close_tools_overlay(page)
    _fit_then_contract(page)
    after = page.evaluate(
        "ids => network.getPositions(ids)", [module_node_id, "1.1"]
    )

    assert after[module_node_id] == before[module_node_id]
    assert abs(after["1.1"]["x"]) < abs(before["1.1"]["x"])
    assert page.evaluate("() => kgGlobalLayoutSnapshot().modules") == page.evaluate(
        "() => publishedLayout.modules"
    )
    assert page.evaluate("id => nodes.get(id).fixed.x", module_node_id) is False
    page.evaluate(
        """id => {
          network.moveNode(id, 444, 555);
          network.emit("dragEnd", {nodes: [id]});
        }""",
        module_node_id,
    )
    assert page.evaluate(
        "id => network.getPositions([id])[id]", module_node_id
    ) == {"x": 444, "y": 555}
    assert page.evaluate("() => kgGlobalLayoutSnapshot().modules") == page.evaluate(
        "() => publishedLayout.modules"
    )

    # Navigating to another concept represented by the same folded module still
    # discards the contracted presentation.
    browser_graph.click_concept("2.1")
    restored_anchor = page.evaluate(
        "id => network.getPositions([id])[id]", module_node_id
    )
    assert math.isclose(restored_anchor["x"], persistent_anchor["x"], abs_tol=2)
    assert math.isclose(restored_anchor["y"], persistent_anchor["y"], abs_tol=2)


@pytest.mark.browser
def test_real_graph_context_contraction_reduces_spread(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator("#kg_modules_expand_all").click()
    repo_browser_graph.click_concept("gr.metric_tensor")
    page.locator("#kg_context_preset_select").select_option("uses")
    page.locator("#kg_display_scope_select").select_option("context")

    node_ids = page.evaluate("() => kgDisplayedGraphSnapshot().fitIds")
    anchor_id = "gr.metric_tensor"
    before = page.evaluate("ids => network.getPositions(ids)", node_ids)
    _close_tools_overlay(page)
    _fit_then_contract(page)
    after = page.evaluate("ids => network.getPositions(ids)", node_ids)

    assert len(node_ids) >= 5
    assert after[anchor_id] == before[anchor_id]
    before_distances = {
        node_id: math.hypot(
            position["x"] - before[anchor_id]["x"],
            position["y"] - before[anchor_id]["y"],
        )
        for node_id, position in before.items()
        if node_id != anchor_id
    }
    after_distances = {
        node_id: math.hypot(
            position["x"] - after[anchor_id]["x"],
            position["y"] - after[anchor_id]["y"],
        )
        for node_id, position in after.items()
        if node_id != anchor_id
    }
    assert sum(after_distances.values()) < sum(before_distances.values())
    assert any(
        after_distances[node_id] < before_distances[node_id] - 10
        for node_id in after_distances
    )


@pytest.mark.browser
def test_context_contraction_keeps_nodes_out_of_visible_concept_labels(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator("#kg_modules_expand_all").click()
    repo_browser_graph.click_concept("sr.radiation_reaction")
    page.locator("#kg_context_preset_select").select_option("derivation")
    page.locator("#kg_context_depth_select").select_option("transitive")
    page.locator("#kg_display_scope_select").select_option("context")
    _close_tools_overlay(page)
    _fit_then_contract(page)

    overlaps = page.evaluate(
        """() => {
          const canvas = network.canvas.frame.canvas;
          const canvasRect = canvas.getBoundingClientRect();
          const scale = network.getScale();
          const visibleIds = nodes.get().filter(node => !node.hidden && conceptData[node.id])
            .map(node => String(node.id));
          const circles = Object.fromEntries(visibleIds.map(id => {
            const node = nodes.get(id);
            const position = network.canvasToDOM(network.getPositions([id])[id]);
            const radius = (Number(node.visualSize) || Number(node.size) || 18) *
              (id === "sr.radiation_reaction" ? 1.4 : 1) * scale;
            const x = canvasRect.left + position.x;
            const y = canvasRect.top + position.y;
            return [id, {left:x-radius, right:x+radius, top:y-radius, bottom:y+radius}];
          }));
          const labels = Object.fromEntries(visibleIds.map(id => {
            const element = document.querySelector('.kg-node-label[data-node-id="' + id + '"]');
            if (!element || getComputedStyle(element).display === "none") return [id, null];
            const rect = element.getBoundingClientRect();
            return [id, {left:rect.left, right:rect.right, top:rect.top, bottom:rect.bottom}];
          }));
          const result = [];
          visibleIds.forEach(labelId => visibleIds.forEach(circleId => {
            if (labelId === circleId || !labels[labelId]) return;
            const label = labels[labelId];
            const circle = circles[circleId];
            const separated = label.right <= circle.left || circle.right <= label.left ||
              label.bottom <= circle.top || circle.bottom <= label.top;
            if (!separated) result.push([labelId, circleId]);
          }));
          return result;
        }"""
    )

    assert overlaps == []


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
