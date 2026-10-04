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
    page.wait_for_timeout(500)
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
    page.wait_for_timeout(500)
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
    page.locator("#kg_fit_apply").click()
    page.wait_for_timeout(300)
    after = _view_state(page)

    assert not math.isclose(after["scale"], before["scale"], abs_tol=1e-3)
    assert _view_distance(after, before) > 100


@pytest.mark.browser
def test_second_context_fit_contracts_around_selection_until_navigation(browser_graph):
    page = browser_graph.page
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
    assert fit_button.inner_text() == "Fit"
    fit_button.click()
    page.wait_for_timeout(300)
    assert fit_button.inner_text() == "Fit++"
    assert page.evaluate("ids => network.getPositions(ids)", ids) == before

    fit_button.click()
    page.wait_for_timeout(300)
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
    assert "temporarily" in page.locator("#kg_context_notice").inner_text().lower()
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == published
    assert page.evaluate("() => kgContextContractionSnapshot()") == {
        "primed": False,
        "active": True,
        "anchorId": "3.1",
    }

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

    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_toggle").check()
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

    page.locator("#kg_fit_apply").click()
    page.wait_for_timeout(300)
    assert page.locator("#kg_fit_apply").inner_text() == "Fit++"
    page.locator("#kg_fit_apply").click()
    page.wait_for_timeout(300)
    after = page.evaluate(
        "ids => network.getPositions(ids)", [module_node_id, "1.1"]
    )

    assert after[module_node_id] == before[module_node_id]
    assert abs(after["1.1"]["x"]) < abs(before["1.1"]["x"])
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
    page.locator("#kg_fit_apply").click()
    page.wait_for_timeout(300)
    page.locator("#kg_fit_apply").click()
    page.wait_for_timeout(300)
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
    page.locator("#kg_fit_apply").click()
    page.wait_for_timeout(300)
    page.locator("#kg_fit_apply").click()
    page.wait_for_timeout(300)

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
