import pytest


@pytest.mark.browser
def test_generated_viewer_boots_and_initializes_in_browser(browser_graph):
    page = browser_graph.page

    assert browser_graph.page_errors == []
    assert browser_graph.console_errors == []
    assert page.locator("#kg_controls").count() == 1
    assert page.locator("#info_panel").count() == 1
    assert page.locator("#kg_node_labels .kg-node-label").count() == 4
    assert page.locator("#kg_concept_list .kg-concept-item").count() == 4
    assert page.locator("#kg_edge_filters input[data-edge-relation]").count() == 2
    assert page.locator("#kg_view_title").inner_text() == "Browser Harness"
    assert page.evaluate("() => nodes.length") == 4
    assert page.evaluate("() => edges.length") == 4
    assert page.locator("#kg_graph_view_select").input_value() == "all"


@pytest.mark.browser
def test_node_builtin_title_is_disabled_for_custom_tooltips(browser_graph):
    page = browser_graph.page

    title = page.evaluate("""() => nodes.get("2.1").title""")

    assert title == ""


@pytest.mark.browser
def test_node_hover_tooltip_typesets_mathjax(browser_graph):
    page = browser_graph.page

    point = page.evaluate(
        """() => {
          const position = network.getPositions(["2.1"])["2.1"];
          const dom = network.canvasToDOM(position);
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          return {x: rect.left + dom.x, y: rect.top + dom.y};
        }"""
    )
    page.mouse.move(point["x"], point["y"])

    page.wait_for_selector("#kg_node_tooltip", state="visible")
    page.wait_for_selector("#kg_node_tooltip mjx-container")
    tooltip_text = page.locator("#kg_node_tooltip").inner_text()
    assert "2.1 Beta" in tooltip_text
    assert "Beta definition" in tooltip_text
    assert "Optional details" in tooltip_text
    assert "Why this matters" in tooltip_text
    assert "The optional body can include" not in tooltip_text
    assert "<div" not in tooltip_text


@pytest.mark.browser
def test_concept_list_click_populates_details_and_hash(browser_graph):
    page = browser_graph.page

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert "Layer 2 - Applications" in page.locator("#info_panel").inner_text()
    assert "Beta definition" in page.locator("#info_panel").inner_text()
    assert "Beta explains alpha." in page.locator("#info_panel").inner_text()
    assert page.locator('.kg-concept-item[data-concept-id="2.1"]').evaluate(
        "el => el.classList.contains('active')"
    )
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"


@pytest.mark.browser
def test_optional_details_render_inline_and_can_contain_concept_links(browser_graph):
    page = browser_graph.page

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    optional = page.locator("#info_panel details.optional-detail")
    assert optional.count() == 1
    assert optional.locator("summary").inner_text() == "Why this matters"
    assert not optional.locator(".optional-detail-body").is_visible()

    optional.locator("summary").click()

    assert optional.locator(".optional-detail-body").is_visible()
    assert "The optional body can include" in optional.locator(".optional-detail-body").inner_text()
    optional.locator(".concept-link").click()
    assert page.locator("#info_panel h2").inner_text() == "1.1 Alpha"
    assert page.evaluate("() => window.location.hash") == "#concept-1.1"


@pytest.mark.browser
def test_search_finds_definition_text_and_highlights_detail_match(browser_graph):
    page = browser_graph.page

    page.locator("#kg_search").fill("explains")
    page.locator("button", has_text="Find").click()

    assert page.locator("#kg_status").inner_text() == (
        "Found 1 match(es). Showing first: Beta"
    )
    assert page.locator("#kg_concept_list .kg-concept-item").count() == 1
    assert page.locator('.kg-concept-item[data-concept-id="2.1"]').count() == 1
    assert page.locator("#kg_concept_list .kg-search-mark").inner_text() == "explains"
    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.locator("#info_panel .kg-detail-search-mark").inner_text() == "explains"


@pytest.mark.browser
def test_edge_filter_hides_and_restores_relation_edges(browser_graph):
    page = browser_graph.page

    assert page.locator('input[data-edge-relation="DEPENDS_ON"]').is_checked()
    assert page.evaluate(
        """() => edges.get().find(edge => edge.relation === "DEPENDS_ON").hidden === false"""
    )

    page.locator('input[data-edge-relation="DEPENDS_ON"]').uncheck()
    assert page.evaluate(
        """() => edges.get().find(edge => edge.relation === "DEPENDS_ON").hidden === true"""
    )

    page.locator('input[data-edge-relation="DEPENDS_ON"]').check()
    assert page.evaluate(
        """() => edges.get().find(edge => edge.relation === "DEPENDS_ON").hidden === false"""
    )


@pytest.mark.browser
def test_descendants_mode_follows_enabled_directed_edges_only(browser_graph):
    page = browser_graph.page

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    page.locator("#kg_graph_view_select").select_option("descendants")

    assert page.locator("#kg_status").inner_text() == (
        "Descendants mode: 2.1 plus 1 reachable node. Click a visible node to walk one step."
    )
    assert page.locator("#kg_graph_view_select").input_value() == "descendants"
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": True,
        "3.1": True,
    }
    assert page.evaluate(
        """() => edges.get().filter(edge => !edge.hidden).map(edge => [edge.from, edge.to, edge.relation])"""
    ) == [["2.1", "1.1", "DEPENDS_ON"]]

    page.locator('input[data-edge-relation="DEPENDS_ON"]').uncheck()
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": True,
        "2.1": False,
        "2.2": True,
        "3.1": True,
    }
    assert page.evaluate(
        """() => edges.get().every(edge => edge.hidden)"""
    )


@pytest.mark.browser
def test_graph_view_selector_hides_graph_and_supports_two_hop_neighbourhood(browser_graph):
    page = browser_graph.page

    page.locator('.kg-concept-item[data-concept-id="3.1"]').click()
    page.locator("#kg_graph_view_select").select_option("hide")

    assert page.locator("#kg_graph_view_select").input_value() == "hide"
    assert page.locator("body").evaluate("el => el.classList.contains('kg-graph-hidden')")
    assert page.evaluate("""() => nodes.get().every(node => node.hidden)""")
    assert page.evaluate("""() => edges.get().every(edge => edge.hidden)""")
    assert "Delta definition" in page.locator("#info_panel").inner_text()

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    assert page.locator("#kg_graph_view_select").input_value() == "hide"
    assert "Beta definition" in page.locator("#info_panel").inner_text()
    assert page.evaluate("""() => nodes.get().every(node => node.hidden)""")

    page.locator("#kg_graph_view_select").select_option("neighbourhood-2")
    assert page.locator("#kg_status").inner_text() == (
        "Neighbourhood (2) mode: 2.1 plus 3 neighbours. Click a visible node to walk one step."
    )
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": False,
        "3.1": False,
    }


@pytest.mark.browser
def test_splash_dialog_shows_once_and_can_be_reopened(browser_graph):
    page = browser_graph.page

    page.evaluate("""() => localStorage.removeItem("srkg.splash.dismissed.v1")""")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_splash_dialog[open]")

    assert "Knowledge graph browser" in page.locator("#kg_splash_dialog").inner_text()
    assert page.locator("#kg_splash_dialog .kg-new-badge").count() >= 3

    page.locator("#kg_splash_dismiss").click()
    assert page.evaluate("""() => localStorage.getItem("srkg.splash.dismissed.v1")""") == "true"
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_controls", state="attached")
    assert page.locator("#kg_splash_dialog[open]").count() == 0

    page.locator("#kg_features_button").click()
    assert page.locator("#kg_splash_dialog[open]").count() == 1
