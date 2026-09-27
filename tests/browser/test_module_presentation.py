import pytest


@pytest.mark.browser
def test_authored_module_detail_graphic_is_optional_and_captioned(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page
    shared_repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="sr.spacetime_foundations"]'
    ).click()

    figure = page.locator('#info_panel .module-figure')
    assert figure.count() == 1
    assert figure.locator('svg[viewBox="0 0 768 480"]').count() == 1
    assert figure.locator('summary').inner_text().strip() == "Module graphic"
    caption = figure.locator("figcaption")
    assert "light cone" in caption.inner_text().lower()
    svg_box = figure.locator('svg[viewBox="0 0 768 480"]').bounding_box()
    caption_box = caption.bounding_box()
    assert caption_box['y'] >= svg_box['y'] + svg_box['height'] + 4
    assert page.locator('#info_panel .concept-toc a').filter(has_text="Module graphic").count() == 1

    page.locator(
        '.kg-module-item[data-module-id="math.m01_manifolds_and_coordinates"]'
    ).click()
    assert page.locator('#info_panel .module-figure').count() == 0
    assert page.locator('#info_panel .concept-toc a').filter(has_text="Module graphic").count() == 0


@pytest.mark.browser
def test_real_module_label_ink_stays_inside_boxes(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page
    result = page.evaluate("""() => {
      const ctx = network.canvas.frame.canvas.getContext('2d');
      const original = ctx.fillText, failures = [];
      const modules = nodes.get().filter(n => n.isModuleNode && !n.hidden);
      let painted = 0;
      ctx.fillText = function(text, x, y, ...args) {
        // Module labels use the distinctive foreground colour; ignore edge labels.
        if (this.fillStyle === '#111827' && text.trim()) {
          const metrics = this.measureText(text), matrix = this.getTransform();
          const left = matrix.a * (x-metrics.actualBoundingBoxLeft) + matrix.e;
          const right = matrix.a * (x+metrics.actualBoundingBoxRight) + matrix.e;
          const top = matrix.d * (y-metrics.actualBoundingBoxAscent) + matrix.f;
          const bottom = matrix.d * (y+metrics.actualBoundingBoxDescent) + matrix.f;
          const inside = modules.some(node => {
            const n = network.body.nodes[node.id], s = n.shape;
            const a = network.canvasToDOM({x:s.left,y:s.top});
            const b = network.canvasToDOM({x:s.left+s.width,y:s.top+s.height});
            const ratio = network.canvas.frame.canvas.width / network.canvas.frame.canvas.clientWidth;
            return left >= a.x*ratio-1 && right <= b.x*ratio+1 &&
              top >= a.y*ratio-1 && bottom <= b.y*ratio+1;
          });
          painted += 1;
          if (!inside) failures.push({text,left,right,top,bottom});
        }
        return original.call(this, text, x, y, ...args);
      };
      try { network.redraw(); } finally { ctx.fillText = original; }
      return {painted, failures};
    }""")
    assert result['painted'] >= 26
    assert result['failures'] == []


@pytest.mark.browser
def test_graphical_folded_module_places_rounded_landscape_above_smaller_text(
    shared_repo_browser_graph,
):
    page = shared_repo_browser_graph.page
    page.wait_for_function("""() => {
      const image = window.kgModuleGraphicImage &&
        window.kgModuleGraphicImage('sr.spacetime_foundations');
      return image && image.complete && image.naturalWidth === 768;
    }""")
    node = page.evaluate("() => nodes.get('module::sr.spacetime_foundations')")
    maths = page.evaluate("() => nodes.get('module::math.m01_manifolds_and_coordinates')")

    assert node['hasModuleGraphic'] is True
    assert 96 <= node['font']['bold']['size'] <= 128
    assert node['font']['size'] == 52
    assert node['font']['vadjust'] > 0
    assert node['label'].count('<b>') >= 2
    assert node['moduleGraphicLabelArea']['top'] < node['moduleGraphicLabelCenter']
    assert node['moduleGraphicLabelCenter'] < node['moduleGraphicLabelArea']['bottom']
    # vis applies separate baseline corrections to mixed-size title/count lines.
    assert abs(node['font']['vadjust'] - node['moduleGraphicLabelCenter']) < 160
    assert maths.get('hasModuleGraphic') is not True
    assert maths['font']['size'] == 80

    sr4 = page.evaluate(
        "() => nodes.get('module::sr.electromagnetic_structure_gauge_and_stress_energy')"
    )
    assert sr4['font']['bold']['size'] >= 112
    assert sr4['font']['size'] == 52

    result = page.evaluate("""() => {
      const ctx = network.canvas.frame.canvas.getContext('2d');
      const original = ctx.drawImage, calls = [];
      ctx.drawImage = function(...args) {
        if (args.length === 5 && args[0].naturalWidth === 768) {
          calls.push({x:args[1], y:args[2], width:args[3], height:args[4]});
        }
        return original.apply(this, args);
      };
      try { network.redraw(); } finally { ctx.drawImage = original; }
      const shape = network.body.nodes['module::sr.spacetime_foundations'].shape;
      return {calls, box:{left:shape.left, top:shape.top, width:shape.width, height:shape.height}};
    }""")
    box = result['box']
    assert len(result['calls']) == 11  # Every SR and GR module has artwork.
    sr1 = next(call for call in result['calls'] if (
        call['x'] >= box['left'] and call['y'] >= box['top'] and
        call['x'] + call['width'] <= box['left'] + box['width'] and
        call['y'] + call['height'] <= box['top'] + box['height']
    ))
    assert sr1['x'] >= box['left']
    assert sr1['y'] >= box['top']
    assert sr1['x'] + sr1['width'] <= box['left'] + box['width']
    assert sr1['y'] + sr1['height'] < box['top'] + box['height'] * 0.72
    assert sr1['width'] / sr1['height'] == pytest.approx(1.6)


def test_graphic_corner_rounding_tracks_the_inset_module_boundary(
    shared_repo_browser_graph,
):
    page = shared_repo_browser_graph.page
    result = page.evaluate("""() => {
      const node = nodes.get('module::gr.schwarzschild_geometry_and_black_holes');
      const layout = kgModuleGraphicLayout(
        node.moduleFootprintWidth, node.moduleFootprintHeight
      );
      const outer = Math.min(
        node.moduleFootprintWidth, node.moduleFootprintHeight
      ) * 0.18;
      return {
        actual: kgModuleGraphicCornerRadius(
          node.moduleFootprintWidth, node.moduleFootprintHeight, layout
        ),
        expected: outer - (layout.graphic.x + layout.graphic.y) / 2,
        oldIndependentRadius: Math.min(
          layout.graphic.width, layout.graphic.height
        ) * 0.11
      };
    }""")
    assert result['actual'] == pytest.approx(result['expected'])
    assert result['actual'] > result['oldIndependentRadius']


@pytest.mark.browser
def test_module_corners_and_secondary_count_scale_with_box(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section('kg_modules_section')
    page.locator('#kg_modules_collapse_all').click()
    node = page.evaluate("() => nodes.get('module::test.m02_applications')")
    shorter_side = min(node['moduleFootprintWidth'], node['moduleFootprintHeight'])
    assert node['shapeProperties']['borderRadius'] == pytest.approx(shorter_side * 0.18)
    assert node['font']['size'] == 80
    assert '<b>Applications</b>' in node['label']
    assert node['label'].endswith('\n3 concepts')
    assert node['scaling']['label']['drawThreshold'] == 0
    assert page.evaluate("""() => {
      network.moveTo({scale:0.01, animation:false});
      network.redraw();
      return network.body.nodes['module::test.m02_applications'].labelModule.visible();
    }""")


@pytest.mark.browser
def test_large_module_title_font_is_capped_without_changing_footprint(browser_graph):
    page = browser_graph.page
    page.evaluate("""() => {
      network.moveNode('2.1', 15000, 18000);
      network.emit('dragEnd', {nodes:['2.1']});
    }""")
    before = page.evaluate("() => kgGlobalLayoutSnapshot()")
    browser_graph.open_control_section('kg_modules_section')
    page.locator('#kg_modules_collapse_all').click()
    node = page.evaluate("() => nodes.get('module::test.m02_applications')")
    assert node['font']['bold']['size'] <= 160
    assert node['moduleFootprintWidth'] > 10000
    assert page.evaluate("() => kgGlobalLayoutSnapshot()") == before


@pytest.mark.browser
def test_module_counts_keep_fixed_font_size_after_footprint_changes(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section('kg_modules_section')
    page.locator('#kg_modules_collapse_all').click()
    before = page.evaluate("() => nodes.get().filter(n => n.isModuleNode).map(n => n.font.size)")
    assert before == [80, 80]
    page.locator('#kg_modules_expand_all').click()
    page.evaluate("""() => {
      network.moveNode('2.1', 15000, 18000);
      network.emit('dragEnd', {nodes:['2.1']});
    }""")
    page.locator('#kg_modules_collapse_all').click()
    assert page.evaluate("() => nodes.get().filter(n => n.isModuleNode).map(n => n.font.size)") == before


@pytest.mark.browser
def test_initial_prompt_includes_modules_and_unnecessary_recenter_control_is_absent(browser_graph):
    page = browser_graph.page
    assert page.locator('#info_panel').get_attribute('data-concept-id') is None
    assert page.locator('#info_panel').get_attribute('data-module-id') is None
    assert page.locator('#kg_layout_recenter_module').count() == 0
    browser_graph.click_concept('2.1')
    page.locator('#kg_clear_selection').click()
    assert page.locator('#info_panel').get_attribute('data-concept-id') is None
    assert page.locator('#info_panel').get_attribute('data-module-id') is None


@pytest.mark.browser
@pytest.mark.parametrize('folded', [False, True])
def test_edges_remain_visible_at_low_zoom_without_changing_authored_styles(browser_graph, folded):
    page = browser_graph.page
    if folded:
        browser_graph.open_control_section('kg_modules_section')
        page.locator('#kg_modules_collapse_all').click()
    result = page.evaluate("""() => {
      const edge = edges.get().find(e => !e.hidden && e.kgHoverable);
      const original = JSON.stringify(edges.get(edge.id));
      const samples = [1, 0.05, 0.02, 1].map(scale => {
        network.moveTo({scale, animation:false});
        network.redraw();
        return {scale, width:network.body.edges[edge.id].options.width};
      });
      return {original, after:JSON.stringify(edges.get(edge.id)), samples, base:edge.width};
    }""")
    assert result['original'] == result['after']
    assert result['samples'][0]['width'] == pytest.approx(result['base'])
    assert result['samples'][-1]['width'] == pytest.approx(result['base'])
    for sample in result['samples'][1:3]:
        assert sample['width'] * sample['scale'] >= 1.49


@pytest.mark.browser
@pytest.mark.parametrize('folded', [False, True])
def test_zoomed_out_edge_hover_still_emphasises_and_restores(browser_graph, folded):
    if folded:
        browser_graph.open_control_section('kg_modules_section')
        browser_graph.page.locator('#kg_modules_collapse_all').click()
    result = browser_graph.page.evaluate("""() => {
      const edge = edges.get().find(e => !e.hidden && e.kgHoverable);
      network.moveTo({scale:0.02, animation:false});
      network.redraw();
      const before = network.body.edges[edge.id].options.width;
      network.emit('hoverEdge', {edge:edge.id});
      network.redraw();
      const hovered = network.body.edges[edge.id].options.width;
      network.emit('blurEdge', {edge:edge.id});
      network.redraw();
      return {before, hovered, after:network.body.edges[edge.id].options.width};
    }""")
    assert result['hovered'] > result['before']
    assert result['after'] == pytest.approx(result['before'])
