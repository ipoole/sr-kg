import pytest


MODULE = "test.m02_applications"
NODE = "module::" + MODULE


def fold_applications(graph):
    graph.open_control_section("kg_modules_section")
    graph.page.locator(f'.kg-module-item[data-module-id="{MODULE}"]').click()
    graph.page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()


@pytest.mark.browser
def test_footprint_geometry_uses_extents_padding_and_anchor_offset(browser_graph):
    result = browser_graph.page.evaluate("""() => kgModuleGeometry.footprint([
      {position: {x: 100, y: 200}, extents: {left: 20, right: 30, top: 40, bottom: 70}},
      {position: {x: 400, y: 100}, extents: {left: 50, right: 60, top: 10, bottom: 20}}
    ], {x: 0, y: 0}, 10)""")
    assert result == {
        "left": 70, "right": 470, "top": 80, "bottom": 280,
        "width": 400, "height": 200, "x": 270, "y": 180,
        "offset": {"x": 270, "y": 180},
    }


@pytest.mark.browser
def test_footprint_geometry_handles_single_missing_and_invalid_members(browser_graph):
    page = browser_graph.page
    result = page.evaluate("""() => kgModuleGeometry.footprint([
      {position: {x: 10, y: 20}}, {position: {x: NaN, y: 1}}, {}
    ], {x: 10, y: 20}, 0)""")
    assert result["width"] == 250
    assert result["height"] == 300
    assert result["offset"] == {"x": 0, "y": 50}
    empty = page.evaluate("() => kgModuleGeometry.footprint([], {x: 20, y: 30})")
    assert empty["x"] == 20
    assert empty["y"] == 30
    assert empty["width"] > 0 and empty["height"] > 0


@pytest.mark.browser
def test_runtime_footprint_uses_global_positions_independent_of_zoom(browser_graph):
    page = browser_graph.page
    before = page.evaluate("() => kgModuleFootprint('test.m02_applications')")
    page.evaluate("""() => {
      network.moveNode('2.1', 9000, 9000);
      network.moveTo({scale: 0.15, animation: false});
    }""")
    assert page.evaluate("() => kgModuleFootprint('test.m02_applications')") == before


@pytest.mark.browser
def test_expanded_modules_show_faint_outlines_matching_folded_geometry(browser_graph):
    page = browser_graph.page
    outlines = page.evaluate("() => kgExpandedModuleOutlineSnapshot()")

    assert {outline["moduleId"] for outline in outlines} == {
        "test.m01_foundations",
        "test.m02_applications",
    }
    for outline in outlines:
        footprint = page.evaluate("id => kgModuleFootprint(id)", outline["moduleId"])
        for key in ("left", "right", "top", "bottom", "width", "height"):
            assert outline[key] == pytest.approx(footprint[key])
        assert outline["radius"] == pytest.approx(
            min(footprint["width"], footprint["height"]) * 0.18
        )
        assert outline["opacity"] == pytest.approx(0.3)
        assert outline["lineWidth"] == pytest.approx(1.75)

    fold_applications(browser_graph)
    remaining = page.evaluate("() => kgExpandedModuleOutlineSnapshot()")
    assert [outline["moduleId"] for outline in remaining] == [
        "test.m01_foundations"
    ]


@pytest.mark.browser
def test_context_only_scope_suppresses_expanded_module_outlines_but_keeps_controls(
    browser_graph,
):
    page = browser_graph.page
    browser_graph.click_concept("2.2")
    page.locator("#kg_display_scope_select").select_option("context")

    assert page.evaluate("() => kgExpandedModuleOutlineSnapshot()") == []
    assert page.locator(
        '.kg-module-corner-control[data-module-id="test.m02_applications"]'
    ).is_visible()


@pytest.mark.browser
def test_folded_box_matches_footprint_and_scales_its_label(browser_graph):
    page = browser_graph.page
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    footprint = page.evaluate("id => kgModuleFootprint(id)", MODULE)
    fold_applications(browser_graph)
    page.evaluate("() => network.redraw()")
    node = page.evaluate("id => nodes.get(id)", NODE)
    bounds = browser_graph.drawn_module_bounds(NODE)
    for side in ("left", "right", "top", "bottom"):
        assert bounds[side] == pytest.approx(footprint[side], abs=1), page.evaluate("""id => {
          const n = network.body.nodes[id];
          return {x:n.x,y:n.y,width:n.shape.width,height:n.shape.height,
            margin:n.shape.margin, bounds:n.shape.boundingBox,options:n.options.shapeProperties};
        }""", NODE)
    assert node["font"]["bold"]["size"] > 28
    assert page.evaluate("""id => {
      const n = network.body.nodes[id], s = n.shape;
      const radius = n.options.shapeProperties.borderRadius;
      return network.getNodeAt(network.canvasToDOM({x:s.left + radius + 10, y:s.top + 10}));
    }""", NODE) == NODE
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before


@pytest.mark.browser
def test_box_drag_translates_anchor_and_members_without_expansion_jump(browser_graph):
    page = browser_graph.page
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_toggle").check()
    fold_applications(browser_graph)
    page.evaluate("""id => {
      const p = network.body.nodes[id];
      network.moveNode(id, p.x + 700, p.y - 450);
      network.emit('dragEnd', {nodes: [id]});
    }""", NODE)
    after = page.evaluate("() => kgGlobalLayoutSnapshot()")
    assert after["modules"][MODULE]["anchor"]["x"] == pytest.approx(before["modules"][MODULE]["anchor"]["x"] + 700)
    assert after["modules"][MODULE]["anchor"]["y"] == pytest.approx(before["modules"][MODULE]["anchor"]["y"] - 450)
    for cid in ("2.1", "2.2", "3.1"):
        assert after["concepts"][cid]["x"] == pytest.approx(before["concepts"][cid]["x"] + 700)
        assert after["concepts"][cid]["y"] == pytest.approx(before["concepts"][cid]["y"] - 450)
    assert after["concepts"]["1.1"] == before["concepts"]["1.1"]
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="expanded"]').click()
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == after
