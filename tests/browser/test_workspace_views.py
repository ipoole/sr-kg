import pytest

pytestmark = pytest.mark.browser


def test_version_history_is_folded_and_available_in_tools(browser_graph):
    import json
    from srkg.html_injection import ASSET_DIR
    page = browser_graph.page
    assert not page.locator('#kg_version_history').evaluate('el => el.open')
    browser_graph.open_control_section('kg_version_history')
    section = page.locator('#kg_version_history')
    entries = json.loads((ASSET_DIR / 'release_history.json').read_text())
    assert section.locator('li').count() == len(entries)
    assert section.locator('time').evaluate_all('nodes => nodes.map(n => n.dateTime)') == [entry['date'] for entry in entries]
    section.locator(':scope > summary').click()
    assert not section.evaluate('el => el.open')
    assert not section.locator('ol').is_visible()


def test_selection_does_not_leave_a_stray_status_below_version_history(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept('2.1')
    if not page.locator('#kg_controls').is_visible():
        page.locator('#kg_controls_toggle').click()
    assert not page.locator('#kg_status').is_visible()
    for _ in range(2):
        page.locator('#kg_version_history > summary').click()
        assert not page.locator('#kg_status').is_visible()


@pytest.mark.parametrize('width', [360, 430])
def test_phone_graph_only_selection_shares_context_row(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({'width': width, 'height': 932})
    browser_graph.click_concept('2.1')
    title = page.locator('#kg_graph_selection')
    assert not title.is_visible()
    page.locator('#kg_view_select').select_option('graph')
    assert title.is_visible()
    assert title.inner_text() == page.locator('#info_panel h2').inner_text()
    assert title.bounding_box()['height'] < 24
    page.evaluate("document.getElementById('kg_modules_collapse_all').click()")
    expand = page.locator('#kg_expand_context_modules')
    assert expand.is_visible()
    assert not page.locator('#kg_context_summary').is_visible()
    row = page.locator('.kg-context-meta-row').bounding_box()
    assert row['height'] < 32
    assert title.bounding_box()['x'] + title.bounding_box()['width'] <= expand.bounding_box()['x']
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    before = page.evaluate('kgViewerStateSnapshot()')
    if page.locator('#kg_controls').is_visible():
        page.locator('#kg_controls_toggle').click()
    title.click()
    assert page.locator('#kg_view_select').input_value() == 'both'
    assert not title.is_visible()
    assert page.evaluate('kgViewerStateSnapshot().selection') == before['selection']
    assert page.evaluate('kgViewerStateSnapshot().contextRule') == before['contextRule']
    page.evaluate("kgExecuteViewerCommand({command:'select',target:'module:test.m02_applications'})")
    page.locator('#kg_view_select').select_option('graph')
    assert title.inner_text() == page.locator('#info_panel h2').inner_text()
    page.evaluate("document.getElementById('kg_modules_expand_all').click()")
    assert page.locator('#kg_context_summary').is_visible()
    assert title.is_visible()


@pytest.mark.parametrize("view", ["both", "graph", "details"])
@pytest.mark.parametrize("scope", ["overview", "full", "context"])
def test_pane_choice_is_independent_of_graph_scope(browser_graph, view, scope):
    page = browser_graph.page
    browser_graph.click_concept("2.2")
    page.locator("#kg_display_scope_select").select_option(scope)
    before = page.evaluate("kgViewerStateSnapshot()")
    page.locator("#kg_view_select").select_option(view)
    assert page.locator("#kg_graph_pane").is_visible() == (view != "details")
    assert page.locator("#kg_details_pane").is_visible() == (view != "graph")
    assert page.evaluate("kgViewerStateSnapshot().selection") == before["selection"]
    assert page.evaluate("kgViewerStateSnapshot().contextRule") == before["contextRule"]
    assert page.locator("#kg_display_scope_select").input_value() == scope
    page.locator("#kg_view_select").select_option("both")
    assert page.locator("#kg_graph_pane").is_visible()
    assert page.locator("#kg_details_pane").is_visible()


def test_selection_is_permanent_and_does_not_choose_graph_mode(browser_graph):
    page = browser_graph.page
    assert page.evaluate("kgViewerStateSnapshot().selection") == {"type": "module", "id": "test.m01_foundations"}
    assert page.locator("#kg_display_scope_select").input_value() == "full"
    assert page.locator("#kg_fit_select").input_value() == "context"
    assert page.locator("#kg_clear_selection").count() == 0
    browser_graph.click_concept("2.2")
    assert page.locator("#kg_display_scope_select").input_value() == "full"
    page.evaluate("network.emit('click', {nodes:[], edges:[], pointer:{DOM:{x:1,y:1}}})")
    assert page.evaluate("kgViewerStateSnapshot().selection.id") == "2.2"
    page.goto(page.url.split("#")[0] + "#concept-missing")
    page.wait_for_function("typeof kgViewerStateSnapshot === 'function'")
    assert page.evaluate("kgViewerStateSnapshot().selection.id") == "test.m01_foundations"


def test_hidden_graph_updates_before_returning_to_both(browser_graph):
    page = browser_graph.page
    page.locator("#kg_view_select").select_option("details")
    page.evaluate("kgExecuteViewerCommand({command:'set-display-scope',value:'context'})")
    page.evaluate("kgExecuteViewerCommand({command:'select',target:'concept:2.2'})")
    page.locator("#kg_view_select").select_option("both")
    assert page.evaluate("nodes.get().some(n => !n.hidden)")
    assert page.evaluate("kgViewerStateSnapshot().selection.id") == "2.2"


@pytest.mark.parametrize("width", [320, 390, 1280])
def test_show_in_graph_fits_context_without_unfolding_or_contracting(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({"width": width, "height": 844})
    browser_graph.click_concept("2.2")
    page.locator("#kg_view_select").select_option("details")
    before = page.evaluate("kgCaptureTutorialPresentation().moduleRepresentation")
    page.evaluate("kgExecuteViewerCommand({command:'show-relationship-in-graph',preset:'derivation',full_tree:true})")
    assert page.locator("#kg_view_select").input_value() == "both"
    assert page.locator("#kg_fit_select").input_value() == "context"
    assert page.evaluate("kgViewerStateSnapshot().contextRule.depth") == "transitive"
    assert page.evaluate("kgCaptureTutorialPresentation().moduleRepresentation") == before
    assert page.evaluate("kgContextContractionSnapshot().active") is False
    assert page.locator("#kg_fit_apply").text_content() == "Fit++"
    boxes = page.locator("#kg_app_header select, #kg_app_header button").evaluate_all("els => els.filter(e => e.getBoundingClientRect().width).map(e => {let r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};})")
    assert all(b["left"] >= 0 and b["right"] <= width for b in boxes), boxes


@pytest.mark.parametrize("scope", ["overview", "full", "context"])
@pytest.mark.parametrize("frame", ["reveal", "selection", "context", "displayed"])
def test_frame_choices_have_targets_with_permanent_selection(browser_graph, scope, frame):
    page = browser_graph.page
    browser_graph.click_concept("2.2")
    page.locator("#kg_display_scope_select").select_option(scope)
    page.locator("#kg_fit_select").select_option(frame)
    assert page.locator("#kg_fit_apply").is_enabled()
    before = page.evaluate("kgGlobalLayoutSnapshot()")
    page.locator("#kg_fit_apply").click()
    assert page.evaluate("kgViewerStateSnapshot().selection.id") == "2.2"
    assert page.evaluate("kgGlobalLayoutSnapshot()") == before
    assert page.locator("#kg_fit_apply").text_content() == ("Fit++" if frame == "context" else "Fit")


@pytest.mark.parametrize("width", [390, 1280])
def test_view_changes_preserve_camera_reading_state_and_layout(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({"width": width, "height": 844})
    browser_graph.click_concept("2.2")
    page.evaluate("""() => {
      network.moveTo({position:{x:123,y:456}, scale:0.6, animation:false});
      document.querySelectorAll('#info_panel details[id]').forEach((el, i) => {
        el.open = i % 2 === 0;
      });
    }""")
    before = page.evaluate("""() => ({
      camera:{position:network.getViewPosition(), scale:network.getScale()},
      sections:[...document.querySelectorAll('#info_panel details[id]')].map(el => [el.id, el.open]),
      layout:kgGlobalLayoutSnapshot()
    })""")
    for view in ["graph", "both", "details", "both"]:
        page.locator("#kg_view_select").select_option(view)
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        after = page.evaluate("""() => ({
          camera:{position:network.getViewPosition(), scale:network.getScale()},
          sections:[...document.querySelectorAll('#info_panel details[id]')].map(el => [el.id, el.open]),
          layout:kgGlobalLayoutSnapshot()
        })""")
        assert after["camera"]["scale"] == pytest.approx(before["camera"]["scale"])
        assert after["camera"]["position"] == pytest.approx(before["camera"]["position"])
        assert after["sections"] == before["sections"]
        assert after["layout"] == before["layout"]


def test_show_in_graph_fit_is_not_undone_by_pane_camera_restore(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.2")
    page.evaluate("""() => Object.defineProperty(navigator, 'hardwareConcurrency', {
      configurable:true, get:() => 2
    })""")
    page.locator("#kg_view_select").select_option("details")
    result = page.evaluate("""async () => {
      await new Promise(resolve => setTimeout(resolve, 200));
      network.moveTo({position:{x:12345,y:6789},scale:0.1,animation:false});
      await kgExecuteViewerCommand({command:'show-relationship-in-graph',preset:'derivation',full_tree:true});
      const fitted = {position:network.getViewPosition(),scale:network.getScale()};
      await new Promise(resolve => setTimeout(resolve, 250));
      return {fitted, settled:{position:network.getViewPosition(),scale:network.getScale()}};
    }""")
    # vis may slightly adjust scale as its resized canvas settles; it must not
    # return to the deliberately distant, zoomed-out pre-shortcut camera.
    assert result["settled"]["scale"] > 0.15
    assert result["settled"]["position"]["x"] < 1000
