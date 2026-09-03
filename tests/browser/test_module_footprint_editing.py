import json

import pytest

from srkg.layout_persistence import load_published_layout


MODULE = "test.m02_applications"
NODE = "module::" + MODULE


def _fold(graph):
    graph.open_control_section("kg_modules_section")
    graph.page.locator(f'.kg-module-item[data-module-id="{MODULE}"]').click()
    graph.page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()


def _assert_box(page):
    page.evaluate("() => network.redraw()")
    footprint = page.evaluate("id => kgModuleFootprint(id)", MODULE)
    bounds = page.evaluate("""id => {
      const s = network.body.nodes[id].shape;
      return {left:s.left, right:s.left+s.width, top:s.top, bottom:s.top+s.height};
    }""", NODE)
    for side in ("left", "right", "top", "bottom"):
        assert bounds[side] == pytest.approx(footprint[side], abs=1)


@pytest.mark.browser
def test_reset_while_folded_restores_footprint_without_moving_other_modules(browser_graph):
    page = browser_graph.page
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    page.evaluate("""() => {
      network.moveNode('2.1', 8000, 3000);
      network.emit('dragEnd', {nodes:['2.1']});
    }""")
    _fold(browser_graph)
    page.evaluate("() => kgResetToPublishedLayout()")
    _assert_box(page)
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="expanded"]').click()
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before


@pytest.mark.browser
@pytest.mark.parametrize("position", [{"x": 4000, "y": 0}, {"x": 0, "y": -6000}])
def test_concept_edits_change_footprint_not_anchors_or_neighbours(browser_graph, position):
    page = browser_graph.page
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    old_footprint = page.evaluate("id => kgModuleFootprint(id)", MODULE)
    page.evaluate("""p => {
      network.moveNode('2.1', p.x, p.y);
      network.emit('dragEnd', {nodes:['2.1']});
    }""", position)
    _fold(browser_graph)
    _assert_box(page)
    after = page.evaluate("() => kgGlobalLayoutSnapshot()")
    assert after["modules"] == before["modules"]
    assert after["concepts"]["1.1"] == before["concepts"]["1.1"]
    assert page.evaluate("id => kgModuleFootprint(id)", MODULE) != old_footprint


@pytest.mark.browser
def test_focused_adjustments_do_not_change_persistent_footprint(browser_graph):
    page = browser_graph.page
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    footprint = page.evaluate("id => kgModuleFootprint(id)", MODULE)
    browser_graph.click_concept("3.1")
    page.locator('#kg_graph_view_select').select_option('focused')
    page.evaluate("""() => {
      network.moveNode('2.1', 5000, 5000);
      network.emit('dragEnd', {nodes:['2.1']});
    }""")
    assert page.evaluate("id => kgModuleFootprint(id)", MODULE) == footprint
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before
    page.locator('#kg_graph_view_select').select_option('all')
    _fold(browser_graph)
    _assert_box(page)


@pytest.mark.browser
def test_late_label_measurement_resizes_box_without_changing_layout(browser_graph):
    page = browser_graph.page
    _fold(browser_graph)
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    old_height = page.evaluate("id => nodes.get(id).moduleFootprintHeight", NODE)
    page.evaluate("""() => {
      document.querySelector('.kg-node-label[data-node-id="3.1"]').innerHTML +=
        '<div style="height:1400px">A late-rendered mathematical label</div>';
      document.fonts.dispatchEvent(new Event('loadingdone'));
    }""")
    page.wait_for_function("""([id, height]) => nodes.get(id).moduleFootprintHeight > height""", arg=[NODE, old_height])
    _assert_box(page)
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before


@pytest.mark.browser
def test_temporary_folded_move_then_expansion_does_not_save_positions(browser_graph):
    page = browser_graph.page
    _fold(browser_graph)
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    page.locator('#kg_graph_view_select').select_option('focused')
    page.evaluate("""id => {
      network.moveNode(id, 7000, 8000);
      network.emit('dragEnd', {nodes:[id]});
      document.fonts.dispatchEvent(new Event('loadingdone'));
    }""", NODE)
    assert page.evaluate("id => network.getPositions([id])[id]", NODE) == {"x": 7000, "y": 8000}
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="expanded"]').click()
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before
    page.locator('#kg_graph_view_select').select_option('all')
    _fold(browser_graph)
    _assert_box(page)


@pytest.mark.browser
def test_export_reload_and_repeated_folding_preserve_geometry(browser_graph, tmp_path):
    page = browser_graph.page
    _fold(browser_graph)
    page.evaluate("""id => {
      const p = network.body.nodes[id];
      network.moveNode(id, p.x + 375.25, p.y - 225.5);
      network.emit('dragEnd', {nodes:[id]});
    }""", NODE)
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    exported = page.evaluate("() => kgExportedGlobalLayout()")
    path = tmp_path / 'layout.json'
    path.write_text(json.dumps(exported), encoding='utf-8')
    restored = load_published_layout(path, concept_ids=exported['concepts'], module_ids=exported['modules'])
    assert restored.to_viewer_data() == exported
    page.wait_for_function("() => localStorage.getItem('srkg.layout.global.v1') !== null")
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function("() => typeof kgModuleFootprint === 'function'")
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before
    for _ in range(3):
        _fold(browser_graph)
        _assert_box(page)
        page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="expanded"]').click()
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before


@pytest.mark.browser
def test_full_dataset_module_boxes_fit_their_labels_and_contents(repo_browser_graph):
    page = repo_browser_graph.page
    # MathJax can finish label typesetting just after the splash is dismissed.
    # Wait for its footprint refresh, rather than checking a transitional box.
    page.wait_for_function("""() => {
      network.redraw();
      return Object.keys(moduleData).every(id => {
        const f = kgModuleFootprint(id), s = network.body.nodes['module::' + id].shape;
        return Math.abs(s.left-f.left) <= 1 && Math.abs(s.top-f.top) <= 1 &&
          Math.abs(s.left+s.width-f.right) <= 1 && Math.abs(s.top+s.height-f.bottom) <= 1;
      });
    }""")
    results = page.evaluate("""() => {
      network.redraw();
      return Object.keys(moduleData).map(id => ({
        id, footprint: kgModuleFootprint(id),
        bounds: (() => {
          const s = network.body.nodes['module::' + id].shape;
          return {left:s.left, right:s.left+s.width, top:s.top, bottom:s.top+s.height};
        })()
      }));
    }""")
    assert len(results) == 13
    for result in results:
        for side in ('left', 'right', 'top', 'bottom'):
            assert result['bounds'][side] == pytest.approx(result['footprint'][side], abs=1), result['id']
    assert repo_browser_graph.page_errors == []
