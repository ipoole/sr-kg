import json
from pathlib import Path

import pytest


def _visible_content_block_kinds(page):
    return page.locator("#info_panel .content-block").evaluate_all(
        """nodes => nodes.map(node =>
          [...node.classList].find(name =>
            name.startsWith("content-block-") &&
            !["content-block-fold", "content-block-note"].includes(name)
          ).replace("content-block-", "")
        )"""
    )


def _toc_titles(page):
    return page.locator("#info_panel .concept-toc .concept-toc-link").all_inner_texts()


def _statement_concept_ids(locator):
    return locator.locator(".edge-detail-concept").evaluate_all(
        "nodes => nodes.map(node => node.getAttribute('data-edge-concept-id'))"
    )


@pytest.mark.browser
def test_generated_viewer_boots_and_initializes_in_browser(shared_browser_graph):
    page = shared_browser_graph.page

    assert shared_browser_graph.page_errors == []
    assert shared_browser_graph.console_errors == []
    assert page.locator("#kg_app_header").count() == 1
    assert page.locator("#kg_workspace").count() == 1
    assert page.locator("#kg_graph_pane").count() == 1
    assert page.locator("#kg_details_pane").count() == 1
    assert page.locator("#kg_controls").count() == 1
    assert page.locator("#info_panel").count() == 1
    assert page.locator("#kg_graph_context_panel").count() == 1
    assert page.locator("#kg_node_labels .kg-node-label").count() == 4
    assert page.locator("#kg_concept_list .kg-concept-item").count() == 4
    assert page.locator("#kg_edge_filters_section").count() == 0
    assert page.locator("#kg_edge_filters").count() == 0
    assert page.locator("#kg_legend_section").count() == 0
    assert not page.locator("#kg_notes_section").evaluate("el => el.open")
    assert not page.locator("#kg_search_section").evaluate("el => el.open")
    assert page.locator("#kg_view_title").inner_text() == "Browser Harness"
    assert page.evaluate("() => nodes.length") == 4
    assert page.evaluate("() => edges.length") == 6
    assert page.locator("#kg_display_scope_select").input_value() == "full"
    assert page.locator("#kg_details_view_select").input_value() == "full"


@pytest.mark.browser
def test_node_builtin_title_is_disabled_for_custom_tooltips(shared_browser_graph):
    page = shared_browser_graph.page

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
def test_concept_list_click_populates_details_and_hash(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.1")

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert "Applications" in page.locator("#info_panel .concept-module-chip").inner_text()
    assert "Layer" not in page.locator("#info_panel").inner_text()
    assert "Beta definition" in page.locator("#info_panel").inner_text()
    assert "Beta explains alpha." in page.locator("#info_panel").inner_text()
    assert page.locator('.kg-concept-item[data-concept-id="2.1"]').evaluate(
        "el => el.classList.contains('active')"
    )
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"


@pytest.mark.browser
def test_clear_selection_preserves_folded_full_graph(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator("#kg_modules_collapse_all").click()
    browser_graph.click_concept("2.1")

    page.locator("#kg_clear_selection").click()

    assert page.evaluate("() => window.location.hash") == ""
    assert page.locator("#kg_display_scope_select").input_value() == "full"
    assert page.locator(".kg-concept-item.active").count() == 0
    assert page.locator(".kg-module-item.active").count() == 0
    assert "Select a concept" in page.locator("#info_panel").inner_text()
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get(["1.1", "2.1", "2.2", "3.1"])
          .map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": True,
        "2.1": True,
        "2.2": True,
        "3.1": True,
    }
    assert page.evaluate(
        """() => nodes.get().filter(node => node.isModuleNode && !node.hidden).length"""
    ) == 2


@pytest.mark.browser
def test_module_list_click_populates_details_and_focuses_graph(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()

    assert page.locator("#info_panel h2").inner_text() == "Foundations"
    panel_text = page.locator("#info_panel").inner_text()
    assert "Start with Alpha as the foundation." in panel_text
    assert "Concepts" in panel_text
    assert "1.1 Alpha" in panel_text
    assert page.evaluate("() => window.location.hash") == "#module-test.m01_foundations"
    assert page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').evaluate(
        "el => el.classList.contains('active')"
    )
    summary = page.locator("#kg_context_summary")
    assert summary.get_attribute("data-selection-type") == "module"
    assert "Foundations" in summary.get_attribute("aria-label")

    page.locator("#kg_context_preset_select").select_option("connections")
    page.locator("#kg_display_scope_select").select_option("context")
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": False,
        "3.1": True,
    }


@pytest.mark.browser
def test_module_all_mode_highlights_members_and_keeps_background_visible(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()

    assert page.locator("#kg_display_scope_select").input_value() == "full"
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": False,
        "3.1": False,
    }
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, node.opacity]))"""
    ) == {
        "1.1": 1,
        "2.1": 1,
        "2.2": 1,
        "3.1": 1,
    }
    assert "Applications" in page.locator("#kg_context_summary").get_attribute("aria-label")
    assert page.locator("#kg_context_summary").get_attribute("data-display-scope") == "full"


@pytest.mark.browser
def test_module_focussed_mode_keeps_members_and_boundary_concepts(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator("#kg_context_preset_select").select_option("connections")
    page.locator("#kg_display_scope_select").select_option("context")

    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": False,
        "3.1": True,
    }
    assert page.evaluate(
        """() => edges.get()
          .filter(edge => !edge.hidden)
          .map(edge => `${edge.from}->${edge.to}::${edge.relation}`)
          .sort()
        """
    ) == [
        "1.1->2.1::RELATED",
        "2.1->1.1::REQUIRES",
        "2.2->1.1::DERIVES_FROM",
    ]
    assert page.locator("#kg_context_summary").get_attribute("data-display-scope") == "context"


@pytest.mark.browser
def test_selected_module_can_be_folded_into_distinct_graph_node(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    assert page.locator("#info_panel .module-graph-fold-button[aria-pressed=true]").inner_text() == "Folded"
    assert page.locator("#kg_context_summary").get_attribute("data-selection-type") == "module"
    assert page.evaluate(
        """moduleNodeId => {
          const moduleNode = nodes.get(moduleNodeId);
          return moduleNode &&
            moduleNode.isModuleNode === true &&
            moduleNode.hidden === false &&
            moduleNode.shape === "box" &&
            moduleNode.widthConstraint.minimum === moduleNode.moduleFootprintWidth &&
            moduleNode.heightConstraint.minimum === moduleNode.moduleFootprintHeight &&
            moduleNode.borderWidth <= 2 &&
            moduleNode.font.bold.size >= 28 &&
            moduleNode.font.size === 80 &&
            moduleNode.label === "<b>Applications</b>\\n3 concepts";
        }""",
        module_node_id,
    )
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get(["1.1", "2.1", "2.2", "3.1"])
          .map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": True,
        "2.2": True,
        "3.1": True,
    }

    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="expanded"]').click()

    assert page.evaluate("""moduleNodeId => nodes.get(moduleNodeId) === null""", module_node_id)
    assert page.evaluate("""() => edges.get().filter(edge => edge.isModuleEdge).length === 0""")
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get(["1.1", "2.1", "2.2", "3.1"])
          .map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": False,
        "3.1": False,
    }
    assert "Applications" in page.locator("#kg_context_summary").get_attribute("aria-label")


@pytest.mark.browser
def test_folded_module_graph_node_selects_module(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m01_foundations"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    page.evaluate(
        """moduleNodeId => {
          network.emit("click", {
            nodes: [moduleNodeId],
            edges: [],
            pointer: {DOM: {x: 0, y: 0}, canvas: {x: 0, y: 0}}
          });
        }""",
        module_node_id,
    )

    assert page.locator("#info_panel h2").inner_text() == "Foundations"
    assert page.evaluate("() => window.location.hash") == "#module-test.m01_foundations"
    assert page.locator("#kg_context_summary").get_attribute("data-selection-type") == "module"
    assert page.evaluate("""moduleNodeId => nodes.get(moduleNodeId).hidden === false""", module_node_id)


@pytest.mark.browser
def test_selecting_member_concept_keeps_selected_module_folded(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()
    page.locator('#info_panel .module-member-concept[data-edge-concept-id="2.1"]').click()

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"
    assert page.evaluate("""moduleNodeId => nodes.get(moduleNodeId).hidden === false""", module_node_id)
    assert page.evaluate("""() => nodes.get("2.1").hidden === true""")
    assert page.locator("#kg_context_summary").get_attribute("data-selection-type") == "concept"
    assert "2.1 Beta" in page.locator("#kg_context_summary").get_attribute("aria-label")

    page.evaluate("() => kgToggleControls()")
    page.locator("#kg_expand_selected_module").click()
    assert page.evaluate("""moduleNodeId => nodes.get(moduleNodeId) === null""", module_node_id)
    assert page.evaluate("""() => nodes.get("2.1").hidden === false""")


@pytest.mark.browser
def test_expand_context_is_offered_for_context_represented_by_other_folded_module(
    browser_graph,
):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator(
        '#info_panel .module-graph-fold-button[data-module-fold-state="folded"]'
    ).click()
    browser_graph.click_concept("2.1")

    assert page.locator("#kg_expand_selected_module").is_hidden()
    context_action = page.locator("#kg_expand_context_modules")
    assert context_action.is_visible()
    assert context_action.inner_text() == "Expand 1 folded"
    assert context_action.get_attribute("aria-label") == (
        "Expand 1 context concept represented by 1 folded module"
    )

    context_action.click()
    assert page.evaluate(
        "() => nodes.get('module::test.m01_foundations') === null"
    )
    assert context_action.is_hidden()


@pytest.mark.browser
def test_expand_context_is_offered_for_selected_folded_module(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator(
        '#info_panel .module-graph-fold-button[data-module-fold-state="folded"]'
    ).click()

    context_action = page.locator("#kg_expand_context_modules")
    assert page.locator("#kg_expand_selected_module").is_hidden()
    assert context_action.is_visible()
    assert context_action.inner_text() == "Expand 3 folded"

    context_action.click()
    assert page.evaluate(
        "() => nodes.get('module::test.m02_applications') === null"
    )
    assert context_action.is_hidden()


@pytest.mark.browser
def test_manual_expansion_replaces_temporary_collapsed_preference(browser_graph):
    page = browser_graph.page
    module_id = "test.m02_applications"
    module_node_id = "module::" + module_id

    browser_graph.open_control_section("kg_modules_section")
    page.locator(f'.kg-module-item[data-module-id="{module_id}"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()
    page.locator('#info_panel .module-member-concept[data-edge-concept-id="2.1"]').click()

    page.locator(f'.kg-module-item[data-module-id="{module_id}"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="expanded"]').click()
    browser_graph.click_concept("1.1")

    assert page.evaluate("""nodeId => nodes.get(nodeId) === null""", module_node_id)
    assert page.evaluate("""() => nodes.get("2.1").hidden === false""")


@pytest.mark.browser
def test_selecting_another_module_preserves_existing_folded_module(browser_graph):
    page = browser_graph.page
    foundations_node_id = "module::test.m01_foundations"
    applications_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()

    assert page.evaluate("""nodeId => nodes.get(nodeId).hidden === false""", foundations_node_id)
    assert page.evaluate("""() => nodes.get("1.1").hidden === true""")
    assert page.evaluate("""() => nodes.get("2.1").hidden === false""")
    assert page.locator("#info_panel h2").inner_text() == "Applications"
    assert "Applications" in page.locator("#kg_context_summary").get_attribute("aria-label")

    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    assert page.evaluate(
        """ids => ids.every(id => nodes.get(id) && nodes.get(id).hidden === false)""",
        [foundations_node_id, applications_node_id],
    )
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get(["1.1", "2.1", "2.2", "3.1"])
          .map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": True,
        "2.1": True,
        "2.2": True,
        "3.1": True,
    }


@pytest.mark.browser
def test_focused_folded_module_projects_all_boundary_relations(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator("#kg_context_preset_select").select_option("connections")
    page.locator("#kg_display_scope_select").select_option("context")
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    module_edges = page.evaluate(
        """() => edges.get()
          .filter(edge => edge.isModuleEdge && !edge.hidden)
          .map(edge => ({
            from: edge.from,
            to: edge.to,
            relations: Object.fromEntries(Object.entries(edge.relationCounts).sort()),
            underlying: edge.edgeIds.length,
            arrows: edge.arrows
          }))
          .sort((a, b) => `${a.from}->${a.to}`.localeCompare(`${b.from}->${b.to}`))
        """
    )

    assert module_edges == [
        {
            "from": "2.1",
            "to": "module::test.m01_foundations",
            "relations": {"REQUIRES": 1},
            "underlying": 1,
            "arrows": "to",
        },
        {
            "from": "2.2",
            "to": "module::test.m01_foundations",
            "relations": {"DERIVES_FROM": 1},
            "underlying": 1,
            "arrows": "to",
        },
        {
            "from": "module::test.m01_foundations",
            "to": "2.1",
            "relations": {"RELATED": 1},
            "underlying": 1,
            "arrows": "",
        },
    ]
    assert page.evaluate(
        """() => edges.get()
          .filter(edge => !edge.isModuleEdge && !edge.hidden)
          .every(edge => edge.from !== "1.1" && edge.to !== "1.1")
        """
    )


@pytest.mark.browser
def test_focused_folded_modules_aggregate_boundary_edges_by_relation(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator("#kg_context_preset_select").select_option("connections")
    page.locator("#kg_display_scope_select").select_option("context")
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    module_edges = page.evaluate(
        """() => edges.get()
          .filter(edge => edge.isModuleEdge && !edge.hidden)
          .map(edge => ({
            id: edge.id,
            from: edge.from,
            to: edge.to,
            label: edge.label,
            relations: Object.fromEntries(Object.entries(edge.relationCounts).sort()),
            underlying: edge.edgeIds.length,
            arrows: edge.arrows
          }))
          .sort((a, b) => `${a.from}->${a.to}`.localeCompare(`${b.from}->${b.to}`))
        """
    )

    assert module_edges == [
        {
            "id": "module-edge::module::test.m01_foundations::module::test.m02_applications",
            "from": "module::test.m01_foundations",
            "to": "module::test.m02_applications",
            "label": "RELATED 1",
            "relations": {"RELATED": 1},
            "underlying": 1,
            "arrows": "",
        },
        {
            "id": "module-edge::module::test.m02_applications::module::test.m01_foundations",
            "from": "module::test.m02_applications",
            "to": "module::test.m01_foundations",
            "label": "DERIVES_FROM 1\nREQUIRES 1",
            "relations": {"REQUIRES": 1, "DERIVES_FROM": 1},
            "underlying": 2,
            "arrows": "to",
        },
    ]

    page.evaluate(
        """edgeId => {
          network.emit("click", {
            nodes: [],
            edges: [edgeId],
            pointer: {DOM: {x: 0, y: 0}, canvas: {x: 0, y: 0}}
          });
        }""",
        "module-edge::module::test.m02_applications::module::test.m01_foundations",
    )

    panel_text = page.locator("#kg_inspection_body").inner_text()
    assert page.locator("#kg_inspection_body h2").inner_text() == "Module Boundary"
    assert "Applications -> Foundations" in panel_text
    assert "REQUIRES 1" in panel_text
    assert "DERIVES_FROM 1" in panel_text
    statements = page.locator("#kg_inspection_body .module-boundary-edge-detail-list .edge-detail-statement")
    assert statements.count() == 2
    assert [_statement_concept_ids(statements.nth(index)) for index in range(2)] == [
        ["2.2", "1.1"],
        ["2.1", "1.1"],
    ]
    assert statements.locator(".edge-detail-phrase").count() == 2
    page.locator("#kg_inspection_close").click()


@pytest.mark.browser
def test_module_boundary_hover_lists_short_underlying_relationships(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    page.evaluate(
        """edgeId => {
          network.emit("hoverEdge", {
            edge: edgeId,
            pointer: {DOM: {x: 120, y: 90}, canvas: {x: 0, y: 0}}
          });
        }""",
        "module-edge::module::test.m02_applications::module::test.m01_foundations",
    )

    page.wait_for_selector("#kg_node_tooltip", state="visible")
    tooltip_text = page.locator("#kg_node_tooltip").inner_text()
    assert "Applications -> Foundations" in tooltip_text
    assert "2 concept links" not in tooltip_text
    assert "REQUIRES 1" not in tooltip_text
    assert "DERIVES_FROM 1" not in tooltip_text
    assert page.locator("#kg_node_tooltip .kg-tooltip-relation").count() == 2
    assert page.locator("#kg_node_tooltip .kg-tooltip-relation").first.evaluate(
        "el => getComputedStyle(el).color !== 'rgb(34, 34, 34)'"
    )


@pytest.mark.browser
def test_module_controls_can_collapse_and_expand_all_modules(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator("#kg_modules_collapse_all").click()

    assert page.evaluate(
        """() => Object.fromEntries(
          ["module::test.m01_foundations", "module::test.m02_applications"]
            .map(id => [id, Boolean(nodes.get(id)) && nodes.get(id).hidden === false])
        )"""
    ) == {
        "module::test.m01_foundations": True,
        "module::test.m02_applications": True,
    }
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get(["1.1", "2.1", "2.2", "3.1"])
          .map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": True,
        "2.1": True,
        "2.2": True,
        "3.1": True,
    }
    assert page.evaluate("""() => edges.get().filter(edge => edge.isModuleEdge && !edge.hidden).length""") == 1
    assert "Collapsed 2 modules" in page.locator("#kg_status").inner_text()

    page.locator("#kg_modules_expand_all").click()

    assert page.evaluate("""() => edges.get().filter(edge => edge.isModuleEdge).length""") == 0
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get(["1.1", "2.1", "2.2", "3.1"])
          .map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": False,
        "3.1": False,
    }
    assert page.evaluate(
        """() => ["module::test.m01_foundations", "module::test.m02_applications"]
          .every(id => nodes.get(id) === null)
        """
    )
    assert "Expanded 2 modules" in page.locator("#kg_status").inner_text()


@pytest.mark.browser
def test_expand_all_restores_members_around_moved_module_node(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator("#kg_modules_collapse_all").click()
    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_persistence").select_option("personal")
    page.locator("#kg_layout_edit_toggle").check()
    offset = page.evaluate("() => kgModuleFootprint('test.m02_applications').offset")
    page.evaluate("""moduleNodeId => network.moveNode(moduleNodeId, 900, 600)""", module_node_id)
    page.locator("#kg_modules_expand_all").click()

    positions = page.evaluate(
        """() => network.getPositions(["2.1", "2.2", "3.1"])"""
    )
    centre_x = sum(positions[node_id]["x"] for node_id in ["2.1", "2.2", "3.1"]) / 3
    centre_y = sum(positions[node_id]["y"] for node_id in ["2.1", "2.2", "3.1"]) / 3
    assert abs(centre_x - (900 - offset["x"])) < 2
    assert abs(centre_y - (600 - offset["y"])) < 2


@pytest.mark.browser
def test_module_controls_are_disabled_when_graph_is_hidden(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator("#kg_display_scope_select").select_option("hidden")

    assert page.locator("#kg_modules_collapse_all").is_disabled()
    assert page.locator("#kg_modules_expand_all").is_disabled()

    page.locator("#kg_display_scope_select").select_option("full")

    assert not page.locator("#kg_modules_collapse_all").is_disabled()
    assert not page.locator("#kg_modules_expand_all").is_disabled()


@pytest.mark.browser
def test_double_clicking_folded_module_node_expands_it(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    point = page.evaluate(
        """moduleNodeId => {
          const position = network.getPositions([moduleNodeId])[moduleNodeId];
          const dom = network.canvasToDOM(position);
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          return {x: rect.left + dom.x, y: rect.top + dom.y};
        }""",
        module_node_id,
    )
    page.mouse.dblclick(point["x"], point["y"])

    assert page.evaluate("""moduleNodeId => nodes.get(moduleNodeId) === null""", module_node_id)
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get(["2.1", "2.2", "3.1"])
          .map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "2.1": False,
        "2.2": False,
        "3.1": False,
    }
    assert page.locator("#info_panel .module-graph-fold-button[aria-pressed=true]").inner_text() == "Expanded"
    assert "Expanded Applications module" in page.locator("#kg_status").inner_text()


@pytest.mark.browser
def test_expanding_folded_module_preserves_its_selected_concept(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    browser_graph.click_concept("2.1")
    concept_point = page.evaluate(
        """() => {
          const position = network.getPositions(["2.1"])["2.1"];
          const dom = network.canvasToDOM(position);
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          return {x: rect.left + dom.x, y: rect.top + dom.y};
        }"""
    )
    page.mouse.dblclick(concept_point["x"], concept_point["y"])
    assert page.evaluate("id => nodes.get(id).hidden === false", module_node_id)

    module_point = page.evaluate(
        """moduleNodeId => {
          const position = network.getPositions([moduleNodeId])[moduleNodeId];
          const dom = network.canvasToDOM(position);
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          return {x: rect.left + dom.x, y: rect.top + dom.y};
        }""",
        module_node_id,
    )
    page.mouse.dblclick(module_point["x"], module_point["y"])

    assert page.evaluate("() => kgViewerStateSnapshot().selection") == {
        "type": "concept",
        "id": "2.1",
    }
    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"
    assert page.evaluate("id => nodes.get(id) === null", module_node_id)


@pytest.mark.browser
def test_double_clicking_concept_node_collapses_owning_module(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    point = page.evaluate(
        """() => {
          const position = network.getPositions(["2.1"])["2.1"];
          const dom = network.canvasToDOM(position);
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          return {x: rect.left + dom.x, y: rect.top + dom.y};
        }"""
    )
    page.mouse.dblclick(point["x"], point["y"])

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.evaluate("""moduleNodeId => nodes.get(moduleNodeId).hidden === false""", module_node_id)
    assert page.evaluate("""() => nodes.get("2.1").hidden === true""")


@pytest.mark.browser
def test_double_tapping_concept_node_collapses_owning_module_on_phone(browser_graph):
    page = browser_graph.page
    page.set_viewport_size({"width": 390, "height": 800})
    point = page.evaluate(
        """() => {
          const position = network.getPositions(["2.1"])["2.1"];
          const dom = network.canvasToDOM(position);
          const canvas = network.canvas.frame.canvas;
          const rect = canvas.getBoundingClientRect();
          return {x: rect.left + dom.x, y: rect.top + dom.y};
        }"""
    )

    page.evaluate(
        """async point => {
          const canvas = network.canvas.frame.canvas;
          const fire = type => canvas.dispatchEvent(new PointerEvent(type, {
            bubbles: true,
            cancelable: true,
            clientX: point.x,
            clientY: point.y,
            pointerId: 7,
            pointerType: "touch",
            isPrimary: true
          }));
          fire("pointerdown");
          fire("pointerup");
          await new Promise(resolve => setTimeout(resolve, 120));
          fire("pointerdown");
          fire("pointerup");
        }""",
        point,
    )

    assert page.evaluate(
        "() => nodes.get('module::test.m02_applications').hidden === false"
    )
    assert page.evaluate("() => nodes.get('2.1').hidden === true")


@pytest.mark.browser
def test_double_clicking_empty_space_inside_expanded_module_collapses_it(browser_graph):
    page = browser_graph.page
    module_id = "test.m02_applications"
    module_node_id = "module::" + module_id

    point = page.evaluate(
        """moduleId => {
          const bounds = kgModuleFootprint(moduleId);
          const canvas = network.canvas.frame.canvas;
          const rect = canvas.getBoundingClientRect();
          const steps = 12;
          for (let row = 1; row < steps; row += 1) {
            for (let column = 1; column < steps; column += 1) {
              const canvasPoint = {
                x: bounds.left + bounds.width * column / steps,
                y: bounds.top + bounds.height * row / steps
              };
              const dom = network.canvasToDOM(canvasPoint);
              if (!network.getNodeAt(dom)) {
                return {x: rect.left + dom.x, y: rect.top + dom.y};
              }
            }
          }
          return null;
        }""",
        module_id,
    )
    assert point is not None

    page.mouse.dblclick(point["x"], point["y"])

    assert page.evaluate("id => nodes.get(id).hidden === false", module_node_id)
    assert page.evaluate("() => nodes.get('2.1').hidden === true")
    assert page.locator("#info_panel h2").inner_text() == "Browser Harness"
    assert "Folded Applications module" in page.locator("#kg_status").inner_text()


@pytest.mark.browser
def test_module_node_hover_shows_module_overview(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()
    page.evaluate(
        """moduleNodeId => {
          network.emit("hoverNode", {
            node: moduleNodeId,
            pointer: {DOM: {x: 120, y: 90}, canvas: {x: 0, y: 0}}
          });
        }""",
        module_node_id,
    )

    page.wait_for_selector("#kg_node_tooltip", state="visible")
    tooltip_text = page.locator("#kg_node_tooltip").inner_text()
    assert "Applications" in tooltip_text
    assert "TEST module" in tooltip_text
    assert "3 concepts" in tooltip_text
    assert "Apply the foundation through Beta, Gamma, and Delta." in tooltip_text


@pytest.mark.browser
def test_selecting_concept_preserves_all_folded_modules(browser_graph):
    page = browser_graph.page
    foundations_node_id = "module::test.m01_foundations"
    applications_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()
    page.locator('#info_panel .module-member-concept[data-edge-concept-id="2.1"]').click()

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.evaluate("""nodeId => nodes.get(nodeId).hidden === false""", applications_node_id)
    assert page.evaluate("""nodeId => nodes.get(nodeId).hidden === false""", foundations_node_id)
    assert page.evaluate("""() => nodes.get("1.1").hidden === true""")
    assert page.evaluate("""() => nodes.get("2.1").hidden === true""")


@pytest.mark.browser
def test_folded_module_hides_in_unrelated_focussed_context(browser_graph):
    page = browser_graph.page
    foundations_node_id = "module::test.m01_foundations"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    browser_graph.click_concept("3.1")
    page.locator("#kg_display_scope_select").select_option("context")

    assert page.locator("#info_panel h2").inner_text() == "3.1 Delta"
    assert page.evaluate("""nodeId => nodes.get(nodeId).hidden === true""", foundations_node_id)
    assert page.evaluate("""() => nodes.get("1.1").hidden === true""")
    assert page.evaluate("""() => nodes.get("3.1").hidden === false""")

    page.locator("#kg_display_scope_select").select_option("full")

    assert page.evaluate("""nodeId => nodes.get(nodeId).hidden === false""", foundations_node_id)


@pytest.mark.browser
def test_folding_module_preserves_anchor_with_offset_box_centre(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_persistence").select_option("personal")
    page.locator("#kg_layout_edit_toggle").check()
    anchor = page.evaluate(
        """() => window.kgGlobalLayoutSnapshot().modules["test.m02_applications"].anchor"""
    )
    page.evaluate(
        """() => {
          network.moveNode("2.1", 120, 150);
          network.moveNode("2.2", 420, 450);
          network.moveNode("3.1", 720, 750);
          network.emit("dragEnd", {nodes: ["2.1", "2.2", "3.1"]});
        }"""
    )
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()

    position = page.evaluate(
        """moduleNodeId => network.getPositions([moduleNodeId])[moduleNodeId]""",
        module_node_id,
    )
    footprint = page.evaluate("() => kgModuleFootprint('test.m02_applications')")
    assert abs(position["x"] - footprint["x"]) < 2
    assert abs(position["y"] - footprint["y"]) < 2
    assert page.evaluate("() => kgGlobalLayoutSnapshot().modules['test.m02_applications'].anchor") == anchor


@pytest.mark.browser
def test_all_mode_drag_updates_authoritative_global_layout(browser_graph):
    page = browser_graph.page

    assert page.evaluate("() => window.kgLayoutEditingEnabled()") is False
    assert page.evaluate("() => window.kgLayoutDraggingEnabled()") is False
    before = page.evaluate("() => window.kgGlobalLayoutSnapshot().concepts['2.1']")
    page.evaluate(
        """() => {
          network.moveNode("2.1", 111, 222);
          network.emit("dragEnd", {nodes: ["2.1"]});
        }"""
    )
    assert page.evaluate(
        """() => window.kgGlobalLayoutSnapshot().concepts["2.1"]"""
    ) == before

    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_persistence").select_option("personal")
    page.locator("#kg_layout_edit_toggle").check()

    page.evaluate(
        """() => {
          network.moveNode("2.1", 321, 654);
          network.emit("dragEnd", {nodes: ["2.1"]});
        }"""
    )

    assert page.evaluate(
        """() => window.kgGlobalLayoutSnapshot().concepts["2.1"]"""
    ) == {"x": 321, "y": 654}

    browser_graph.click_concept("3.1")
    browser_graph.click_concept("2.1")

    position = page.evaluate("""() => network.getPositions(["2.1"])["2.1"]""")
    assert abs(position["x"] - 321) < 2
    assert abs(position["y"] - 654) < 2


@pytest.mark.browser
def test_personal_global_layout_overrides_survive_reload(browser_graph):
    page = browser_graph.page
    storage_key = "srkg.layout.global.v1"
    page.evaluate("key => localStorage.removeItem(key)", storage_key)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("() => typeof window.kgGlobalLayoutSnapshot === 'function'")
    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_persistence").select_option("personal")
    page.locator("#kg_layout_edit_toggle").check()

    page.evaluate(
        """() => {
          network.moveNode("2.1", 432, 765);
          network.emit("dragEnd", {nodes: ["2.1"]});
        }"""
    )
    page.wait_for_function(
        """key => Boolean(JSON.parse(localStorage.getItem(key) || "null"))""",
        arg=storage_key,
    )
    stored = page.evaluate("key => JSON.parse(localStorage.getItem(key))", storage_key)
    assert stored["concepts"] == {"2.1": {"x": 432, "y": 765}}
    assert stored["modules"] == {}
    assert "camera" not in stored

    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("() => typeof window.kgGlobalLayoutSnapshot === 'function'")
    position = page.evaluate("""() => network.getPositions(["2.1"])["2.1"]""")
    assert abs(position["x"] - 432) < 2
    assert abs(position["y"] - 765) < 2


@pytest.mark.browser
def test_stale_personal_layout_can_be_kept_or_reset(browser_graph):
    page = browser_graph.page
    storage_key = "srkg.layout.global.v1"
    page.evaluate(
        """([key, revision]) => {
          localStorage.removeItem("srkg.personalData.v1");
          localStorage.setItem(key, JSON.stringify({
          schema_version: 1,
          published_revision: revision + "-old",
          concepts: {"2.1": {x: 222, y: 333}},
          modules: {}
        }));
        }""",
        [storage_key, "unpublished"],
    )
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("() => typeof window.kgPersonalLayoutStatus === 'function'")

    assert page.evaluate("""() => window.kgPersonalLayoutStatus().revisionMismatch""") is True
    browser_graph.open_control_section("kg_layouts_section")
    assert page.locator("#kg_layout_revision_warning").is_visible()
    assert page.evaluate("""() => network.getPositions(["2.1"])["2.1"]""") == {
        "x": 222,
        "y": 333,
    }

    page.locator("#kg_layout_keep").click()
    assert page.evaluate("""() => window.kgPersonalLayoutStatus().revisionMismatch""") is False
    assert not page.locator("#kg_layout_revision_warning").is_visible()

    page.evaluate("""() => window.kgResetToPublishedLayout()""")
    assert page.evaluate("key => localStorage.getItem(key)", storage_key) is None
    assert page.evaluate("""() => window.kgGlobalLayoutSnapshot()""") == page.evaluate(
        """() => publishedLayout"""
    )


@pytest.mark.browser
def test_layout_controls_report_export_and_reset_state(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_layouts_section")

    assert "Published revision unpublished" in page.locator("#kg_layout_status").inner_text()
    assert "Published layout active" in page.locator("#kg_layout_status").inner_text()
    assert page.locator("#kg_layout_reset").is_disabled()
    assert page.locator("#kg_layout_recenter_module").count() == 0
    assert not page.locator("#kg_layout_edit_toggle").is_checked()
    anchors = page.evaluate("() => kgGlobalLayoutSnapshot().modules")

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator("#kg_display_scope_select").select_option("context")
    page.locator("#kg_display_scope_select").select_option("full")
    page.locator("#kg_layout_edit_persistence").select_option("personal")
    page.locator("#kg_layout_edit_toggle").check()

    page.evaluate(
        """() => {
          network.moveNode("2.1", 543.1234567, 876.7654321);
          network.emit("dragEnd", {nodes: ["2.1"]});
        }"""
    )
    page.wait_for_function(
        """() => document.getElementById("kg_layout_status").textContent.includes("Personal overrides active")"""
    )
    assert not page.locator("#kg_layout_reset").is_disabled()
    assert page.evaluate("() => kgGlobalLayoutSnapshot().modules") == anchors

    with page.expect_download() as download_info:
        page.locator("#kg_layout_export").click()
    exported = json.loads(Path(download_info.value.path()).read_text(encoding="utf-8"))
    assert exported["schema_version"] == 1
    assert exported["revision"] == "unpublished"
    assert exported["concepts"]["2.1"] == {"x": 543.123457, "y": 876.765432}
    assert set(exported) == {"schema_version", "revision", "concepts", "modules"}
    assert list(exported["concepts"]) == sorted(exported["concepts"])
    assert list(exported["modules"]) == sorted(exported["modules"])

    page.locator("#kg_layout_reset").click()
    assert "Published layout active" in page.locator("#kg_layout_status").inner_text()
    assert page.locator("#kg_layout_reset").is_disabled()


@pytest.mark.browser
def test_layout_editing_defaults_to_temporary_and_reports_move_consequences(browser_graph):
    page = browser_graph.page
    original = page.evaluate("() => kgGlobalLayoutSnapshot().concepts['2.1']")

    browser_graph.open_control_section("kg_layouts_section")
    assert page.locator("#kg_layout_edit_persistence").input_value() == "temporary"
    page.locator("#kg_layout_edit_toggle").check()
    page.evaluate(
        """() => {
          network.moveNode("2.1", 777, 888);
          network.emit("dragEnd", {nodes: ["2.1"]});
        }"""
    )

    assert page.evaluate("() => kgGlobalLayoutSnapshot().concepts['2.1']") == original
    assert "Temporary layout adjusted" in page.locator("#kg_context_notice").inner_text()
    page.locator("#kg_layout_edit_toggle").uncheck()
    assert page.evaluate("() => network.getPositions(['2.1'])['2.1']") == original
    assert "Personal layout restored" in page.locator("#kg_context_notice").inner_text()

    page.locator("#kg_layout_edit_persistence").select_option("personal")
    page.locator("#kg_layout_edit_toggle").check()
    page.evaluate(
        """() => {
          network.moveNode("2.1", 333, 444);
          network.emit("dragEnd", {nodes: ["2.1"]});
        }"""
    )
    assert page.evaluate("() => kgGlobalLayoutSnapshot().concepts['2.1']") == {
        "x": 333,
        "y": 444,
    }
    assert "Personal layout updated" in page.locator("#kg_context_notice").inner_text()


@pytest.mark.browser
def test_drag_attempt_while_layout_is_locked_shows_context_notice_once(browser_graph):
    page = browser_graph.page
    point = page.evaluate(
        """() => {
          const canvas = network.canvas.frame.canvas;
          const rect = canvas.getBoundingClientRect();
          const position = network.canvasToDOM(network.getPositions(["2.1"])["2.1"]);
          return {x: rect.left + position.x, y: rect.top + position.y};
        }"""
    )

    page.mouse.move(point["x"], point["y"])
    page.mouse.down()
    page.mouse.move(point["x"] + 12, point["y"] + 8)
    page.mouse.up()

    assert "Layout locked" in page.locator("#kg_context_notice").inner_text()
    page.wait_for_function(
        "() => document.getElementById('kg_context_notice').hidden",
        timeout=4000,
    )

    page.mouse.move(point["x"], point["y"])
    page.mouse.down()
    page.mouse.move(point["x"] + 12, point["y"] + 8)
    page.mouse.up()
    page.wait_for_timeout(200)
    assert page.locator("#kg_context_notice").is_hidden()


@pytest.mark.browser
def test_focussed_mode_allows_temporary_concept_layout_adjustments(browser_graph):
    page = browser_graph.page
    before = page.evaluate("""() => window.kgGlobalLayoutSnapshot()""")
    published = page.evaluate("""() => publishedLayout""")
    assert before == published

    browser_graph.click_concept("3.1")
    page.locator("#kg_display_scope_select").select_option("context")

    during = page.evaluate("""() => window.kgGlobalLayoutSnapshot()""")
    assert during == before
    visible_positions = page.evaluate(
        """() => network.getPositions(nodes.get().filter(node => !node.hidden).map(node => node.id))"""
    )
    for concept_id, position in visible_positions.items():
        assert abs(position["x"] - before["concepts"][concept_id]["x"]) < 2
        assert abs(position["y"] - before["concepts"][concept_id]["y"]) < 2
    assert page.evaluate("""() => window.kgLayoutEditingEnabled()""") is False
    assert page.evaluate("""() => window.kgTemporaryLayoutEditingEnabled()""") is False
    assert page.evaluate("() => window.kgLayoutDraggingEnabled()") is False

    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_toggle").check()
    assert page.evaluate("""() => window.kgLayoutEditingEnabled()""") is True
    assert page.evaluate("""() => window.kgTemporaryLayoutEditingEnabled()""") is True
    assert page.evaluate("() => window.kgLayoutDraggingEnabled()") is True
    assert "temporary" in page.locator("#kg_layout_edit_message").inner_text().lower()

    page.evaluate(
        """() => {
          network.moveNode("3.1", 777, 888);
          network.emit("dragEnd", {nodes: ["3.1"]});
        }"""
    )
    assert page.evaluate("""() => network.getPositions(["3.1"])["3.1"]""") == {
        "x": 777,
        "y": 888,
    }
    assert page.evaluate("""() => window.kgGlobalLayoutSnapshot()""") == before

    page.locator("#kg_display_scope_select").select_option("full")
    assert page.evaluate("""() => window.kgLayoutEditingEnabled()""") is True
    assert page.evaluate("""() => window.kgTemporaryLayoutEditingEnabled()""") is True
    assert "temporary" in page.locator("#kg_layout_edit_message").inner_text().lower()
    assert page.evaluate("""() => network.getPositions(["3.1"])["3.1"]""") == {
        "x": 777,
        "y": 888,
    }
    page.locator("#kg_layout_edit_toggle").uncheck()
    positions = page.evaluate("""() => network.getPositions(Object.keys(publishedLayout.concepts))""")
    for concept_id, expected in before["concepts"].items():
        assert abs(positions[concept_id]["x"] - expected["x"]) < 2
        assert abs(positions[concept_id]["y"] - expected["y"]) < 2


@pytest.mark.browser
def test_focussed_mode_allows_temporary_folded_module_adjustments(browser_graph):
    page = browser_graph.page
    module_id = "test.m02_applications"
    module_node_id = f"module::{module_id}"
    before = page.evaluate("""() => window.kgGlobalLayoutSnapshot()""")
    footprint = page.evaluate("id => kgModuleFootprint(id)", module_id)

    browser_graph.open_control_section("kg_modules_section")
    page.locator(f'.kg-module-item[data-module-id="{module_id}"]').click()
    page.locator(
        '#info_panel .module-graph-fold-button[data-module-fold-state="folded"]'
    ).click()
    page.locator("#kg_display_scope_select").select_option("context")
    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_toggle").check()

    page.evaluate(
        """moduleNodeId => {
          network.moveNode(moduleNodeId, 777, 888);
          network.emit("dragEnd", {nodes: [moduleNodeId]});
        }""",
        module_node_id,
    )
    assert page.evaluate(
        """moduleNodeId => network.getPositions([moduleNodeId])[moduleNodeId]""",
        module_node_id,
    ) == {"x": 777, "y": 888}
    assert page.evaluate("""() => window.kgGlobalLayoutSnapshot()""") == before

    page.locator("#kg_display_scope_select").select_option("full")
    assert page.evaluate(
        """moduleNodeId => network.getPositions([moduleNodeId])[moduleNodeId]""",
        module_node_id,
    ) == {"x": 777, "y": 888}
    page.locator("#kg_layout_edit_toggle").uncheck()
    restored = page.evaluate(
        """moduleNodeId => network.getPositions([moduleNodeId])[moduleNodeId]""",
        module_node_id,
    )
    assert abs(restored["x"] - footprint["x"]) < 2
    assert abs(restored["y"] - footprint["y"]) < 2


@pytest.mark.browser
def test_expanding_moved_module_preserves_member_offsets(browser_graph):
    page = browser_graph.page
    module_node_id = "module::test.m02_applications"

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    browser_graph.open_control_section("kg_layouts_section")
    page.locator("#kg_layout_edit_toggle").check()
    before = page.evaluate("""() => network.getPositions(["2.1", "2.2", "3.1"])""")
    anchor = page.evaluate(
        """() => window.kgGlobalLayoutSnapshot().modules["test.m02_applications"].anchor"""
    )
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="folded"]').click()
    page.evaluate(
        """moduleNodeId => {
          network.moveNode(moduleNodeId, 900, 600);
          network.emit("dragEnd", {nodes: [moduleNodeId]});
        }""",
        module_node_id,
    )
    page.locator('#info_panel .module-graph-fold-button[data-module-fold-state="expanded"]').click()

    positions = page.evaluate(
        """() => network.getPositions(["2.1", "2.2", "3.1"])"""
    )
    offset = page.evaluate("() => kgModuleFootprint('test.m02_applications').offset")
    delta_x = 900 - offset["x"] - anchor["x"]
    delta_y = 600 - offset["y"] - anchor["y"]
    for concept_id in before:
        assert abs(positions[concept_id]["x"] - before[concept_id]["x"] - delta_x) < 2
        assert abs(positions[concept_id]["y"] - before[concept_id]["y"] - delta_y) < 2


@pytest.mark.browser
def test_module_details_show_boundary_link_sections(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()

    panel_text = page.locator("#info_panel").inner_text()
    assert "Incoming boundary links" in panel_text
    assert "Outgoing boundary links" in panel_text
    assert "Applications" in panel_text
    assert "REQUIRES 1" in panel_text
    assert "DERIVES_FROM 1" in panel_text
    assert "RELATED 1" in panel_text

    incoming = page.locator("#info_panel .module-boundary-incoming")
    incoming_text = incoming.inner_text()
    assert "2.1 Beta" in incoming_text
    assert "requires" in incoming_text
    assert "2.2 Gamma" in incoming_text
    assert "is derived from" in incoming_text
    assert "1.1 Alpha" in incoming_text

    outgoing = page.locator("#info_panel .module-boundary-outgoing")
    outgoing_text = outgoing.inner_text()
    assert "1.1 Alpha" in outgoing_text
    assert "is related to" in outgoing_text
    assert "2.1 Beta" in outgoing_text


@pytest.mark.browser
def test_module_details_omit_redundant_domain_line(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()

    assert page.locator("#info_panel .module-domain-label").inner_text() == "TEST"
    assert page.locator("#info_panel .concept-module-context").count() == 0


@pytest.mark.browser
def test_edge_key_omits_redundant_category_and_can_be_dismissed(browser_graph):
    page = browser_graph.page

    page.evaluate("() => kgShowEdgeKey()")

    headings = page.locator("#info_panel .edge-key-table th").all_inner_texts()
    assert headings == ["Relation", "Direction", "Meaning", "Example"]
    relation = page.locator("#info_panel .edge-key-relation").first
    assert relation.inner_text()
    assert relation.evaluate("el => getComputedStyle(el).color") != "rgb(0, 0, 0)"

    close = page.locator("#kg_edge_key_close")
    assert close.is_visible()
    close.click()
    assert not page.locator("#info_panel").is_visible()
    assert page.locator("#kg_details_view_select").input_value() == "hide"


@pytest.mark.browser
def test_concept_masthead_module_chip_opens_module(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#info_panel .concept-module-chip").click()

    assert page.locator("#info_panel h2").inner_text() == "Applications"
    assert page.evaluate("() => window.location.hash") == "#module-test.m02_applications"
    assert page.locator('.kg-module-item[data-module-id="test.m02_applications"]').evaluate(
        "el => el.classList.contains('active')"
    )


@pytest.mark.browser
def test_search_can_select_module_results(browser_graph):
    page = browser_graph.page

    browser_graph.open_search()
    page.locator("#kg_search").fill("Applications")
    page.locator('#kg_concept_list .kg-module-search-item[data-module-id="test.m02_applications"]').click()

    assert page.locator("#info_panel h2").inner_text() == "Applications"
    assert page.evaluate("() => window.location.hash") == "#module-test.m02_applications"


@pytest.mark.browser
def test_browser_back_moves_from_module_to_concept(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#info_panel .concept-module-chip").click()
    page.go_back(wait_until="domcontentloaded")

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"


@pytest.mark.browser
def test_legacy_concept_uses_coarse_details_sections(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.1")

    assert page.locator("#info_panel h3").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    ) == ["Definition", "Explanation"]
    assert page.locator("#info_panel .content-block").count() == 0


@pytest.mark.browser
def test_revised_concept_renders_ordered_content_blocks(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    assert page.locator(
        "#info_panel .content-block:not(.content-block-fold) "
        "> summary .content-block-title-text"
    ).evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    ) == ["Definition", "Gamma intuition"]
    assert "Gamma definition" in page.locator("#info_panel").inner_text()
    assert "Gamma intuition body" in page.locator("#info_panel").inner_text()
    assert page.locator("#info_panel .concept-section h3").count() == 0


@pytest.mark.browser
def test_revised_concept_renders_note_block_kinds_folded(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    notes = page.locator("#info_panel details.content-block-note")
    assert notes.count() == 2
    assert notes.locator("summary").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    ) == ["Gamma warning", "Gamma history"]
    assert not notes.nth(0).locator(".content-block-note-body").is_visible()

    notes.nth(0).locator("summary").click()

    assert notes.nth(0).locator(".content-block-note-body").is_visible()
    assert "Gamma warning body" in notes.nth(0).inner_text()


@pytest.mark.browser
def test_folded_content_blocks_use_compact_callout_spacing(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    spacing = page.locator("#info_panel details.content-block-note").first.evaluate(
        """el => {
          const style = getComputedStyle(el);
          return {
            paddingTop: parseFloat(style.paddingTop),
            paddingBottom: parseFloat(style.paddingBottom),
            marginBottom: parseFloat(style.marginBottom)
          };
        }"""
    )

    assert spacing["paddingTop"] <= 8
    assert spacing["paddingBottom"] <= 9
    assert spacing["marginBottom"] <= 16


@pytest.mark.browser
def test_revised_concept_renders_derivation_steps_folded(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    step = page.locator("#info_panel details.content-block-derivation_step")
    assert step.count() == 1
    assert step.locator("summary").inner_text() == "Gamma algebra step"
    assert not step.locator(".content-block-fold-body").is_visible()

    step.locator("summary").click()

    assert step.locator(".content-block-fold-body").is_visible()
    assert "Gamma derivation-step body" in step.inner_text()


@pytest.mark.browser
def test_content_block_kind_policy_renders_labels_and_fold_state(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    labels = page.locator("#info_panel .content-block-kind-label").evaluate_all(
        "nodes => nodes.map(node => node.getAttribute('data-label'))"
    )
    assert labels == ["Definition", "Think", "Careful", "Step", "Context"]
    assert page.locator("#info_panel .content-block-definition").evaluate(
        "el => el.tagName"
    ) == "DETAILS"
    assert page.locator("#info_panel .content-block-intuition").evaluate(
        "el => el.tagName"
    ) == "DETAILS"
    assert page.locator("#info_panel details.content-block-warning").count() == 1
    assert page.locator("#info_panel details.content-block-derivation_step").count() == 1
    assert page.locator("#info_panel details.content-block-historical_note").count() == 1


@pytest.mark.browser
def test_graphic_and_inline_content_sections_are_foldable(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    graphic = page.locator("#info_panel details.concept-figure")
    definition = page.locator("#info_panel details.content-block-definition")
    intuition = page.locator("#info_panel details.content-block-intuition")

    assert graphic.count() == 1
    assert definition.count() == 1
    assert intuition.count() == 1
    assert graphic.evaluate("el => el.open")
    assert definition.evaluate("el => el.open")
    assert intuition.evaluate("el => el.open")
    assert graphic.locator(".concept-graphic svg").count() == 1

    definition.locator("summary").click()

    assert not definition.evaluate("el => el.open")
    assert not definition.locator(".content-block-body").is_visible()


@pytest.mark.browser
def test_detail_toc_omits_obsolete_graph_policy_metadata(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    links = page.locator("#info_panel .concept-toc-link")
    assert links.evaluate_all(
        "links => links.every(link => !link.hasAttribute('data-section-role') && "
        "!link.hasAttribute('data-graph-context') && "
        "!link.hasAttribute('data-context-label'))"
    )


@pytest.mark.browser
def test_revised_concept_renders_sticky_masthead_and_content_toc(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    masthead = page.locator("#info_panel .concept-sticky-header")
    assert masthead.count() == 1
    assert masthead.evaluate("el => getComputedStyle(el).position") == "sticky"
    assert "2.2 Gamma" in masthead.inner_text()
    assert "Layer 2" not in masthead.inner_text()
    assert "Reading" not in masthead.inner_text()
    assert page.locator("#kg_details_view_select").input_value() == "full"

    toc = page.locator("#info_panel .concept-toc")
    assert toc.count() == 1
    assert toc.evaluate("el => el.tagName") == "DETAILS"
    assert toc.evaluate("el => el.open")
    toc.locator("summary").click()
    assert not toc.evaluate("el => el.open")
    toc.locator("summary").click()
    assert toc.evaluate("el => el.open")
    assert toc.locator(".concept-toc-link").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    ) == [
        "Graphic",
        "Definition",
        "Gamma intuition",
        "Gamma warning",
        "Gamma algebra step",
        "Gamma history",
        "Derived from",
        "Where this is used",
        "Study Questions",
    ]
    assert page.locator("#info_panel #kg-toc-2-2-gamma-history").count() == 1


@pytest.mark.browser
def test_concept_toc_starts_closed_on_phone_viewport(browser_graph):
    page = browser_graph.page

    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(
        browser_graph.output_path.as_uri() + "?phone-toc#concept-2.2",
        wait_until="domcontentloaded",
    )
    page.wait_for_selector("#info_panel .concept-toc")

    toc = page.locator("#info_panel .concept-toc")
    assert not toc.evaluate("el => el.open")


@pytest.mark.browser
def test_concept_toc_scroll_places_target_below_sticky_masthead(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#info_panel").evaluate(
        """panel => {
          panel.style.height = "170px";
          panel.scrollTop = 0;
        }"""
    )

    page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-2-2-gamma-warning"]'
    ).click()
    page.wait_for_function(
        """() => {
          const panel = document.getElementById("info_panel");
          const masthead = panel.querySelector(".concept-sticky-header");
          const target = document.getElementById("kg-toc-2-2-gamma-warning");
          return panel.scrollTop > 0 &&
            target.getBoundingClientRect().top >= masthead.getBoundingClientRect().bottom + 4;
        }"""
    )

    metrics = page.evaluate(
        """() => {
          const panel = document.getElementById("info_panel");
          const masthead = panel.querySelector(".concept-sticky-header");
          const target = document.getElementById("kg-toc-2-2-gamma-warning");
          return {
            mastheadBottom: masthead.getBoundingClientRect().bottom,
            targetTop: target.getBoundingClientRect().top
          };
        }"""
    )

    assert metrics["targetTop"] >= metrics["mastheadBottom"] + 4


@pytest.mark.browser
def test_concept_toc_opens_folded_target(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    warning = page.locator("#info_panel #kg-toc-2-2-gamma-warning")
    assert warning.evaluate("el => el.tagName") == "DETAILS"
    assert not warning.evaluate("el => el.open")

    page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-2-2-gamma-warning"]'
    ).click()

    assert warning.evaluate("el => el.open")


@pytest.mark.browser
def test_concept_toc_marks_active_detail_section(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

    graphic_link = page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-2-2-graphic"]'
    )
    warning_link = page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-2-2-gamma-warning"]'
    )
    assert graphic_link.evaluate("el => el.classList.contains('active')")
    graphic = page.locator("#info_panel #kg-toc-2-2-graphic")
    assert graphic.evaluate("el => el.classList.contains('kg-active-section')")

    warning_link.click()

    assert warning_link.evaluate("el => el.classList.contains('active')")
    assert warning_link.evaluate("el => el.getAttribute('aria-current')") == "true"
    assert not graphic_link.evaluate("el => el.classList.contains('active')")
    warning = page.locator("#info_panel #kg-toc-2-2-gamma-warning")
    assert warning.evaluate("el => el.classList.contains('kg-active-section')")
    assert not graphic.evaluate("el => el.classList.contains('kg-active-section')")


@pytest.mark.browser
def test_concept_masthead_no_longer_contains_graph_focus_button(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

    assert page.locator("#info_panel .concept-graph-focus").count() == 0


@pytest.mark.browser
def test_workspace_header_controls_are_centered_over_their_panes(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

    metrics = page.evaluate(
        """() => {
          const graph = document.getElementById("kg_graph_pane").getBoundingClientRect();
          const details = document.getElementById("kg_details_pane").getBoundingClientRect();
          const graphControl = document.querySelector(".kg-shell-graph-control").getBoundingClientRect();
          const detailsControl = document.querySelector(".kg-shell-details-control").getBoundingClientRect();
          return {graph, details, graphControl, detailsControl};
        }"""
    )

    graph_center = metrics["graph"]["x"] + metrics["graph"]["width"] / 2
    details_center = metrics["details"]["x"] + metrics["details"]["width"] / 2
    graph_control_center = metrics["graphControl"]["x"] + metrics["graphControl"]["width"] / 2
    details_control_center = metrics["detailsControl"]["x"] + metrics["detailsControl"]["width"] / 2

    assert abs(graph_control_center - graph_center) <= 6
    assert abs(details_control_center - details_center) <= 6
    assert page.locator("#kg_controls_toggle").bounding_box()["x"] <= 16


@pytest.mark.browser
def test_phone_header_fits_all_primary_controls_on_one_row(browser_graph):
    page = browser_graph.page

    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(browser_graph.output_path.as_uri() + "?phone-header", wait_until="domcontentloaded")
    page.wait_for_selector("#kg_workspace")

    header = page.locator("#kg_app_header").bounding_box()
    workspace = page.locator("#kg_workspace").bounding_box()
    assert header["height"] <= 48
    assert abs(workspace["y"] - header["height"]) <= 1
    assert page.locator(".kg-shell-graph-control label").inner_text() == "Graph"
    assert page.locator(".kg-shell-graph-control label").is_visible()
    assert page.locator(".kg-shell-details-control label").inner_text() == "Details"
    assert page.locator(".kg-shell-details-control label").is_visible()
    assert page.locator("#kg_display_scope_select option:checked").inner_text() == "Full"
    assert page.locator("#kg_details_view_select option:checked").inner_text() == "Full"
    assert page.locator("#kg_clear_selection").inner_text() == "Clear"

    metrics = page.evaluate(
        """() => {
          const ids = [
            "kg_controls_toggle",
            "kg_search_toggle",
            "kg_display_scope_select",
            "kg_clear_selection",
            "kg_details_view_select"
          ];
          return Object.fromEntries(ids.map(id => {
            const rect = document.getElementById(id).getBoundingClientRect();
            return [id, {
              x: rect.x,
              y: rect.y,
              right: rect.right,
              bottom: rect.bottom
            }];
          }));
        }"""
    )
    overlaps = []
    ids = list(metrics)
    for index, first in enumerate(ids):
        for second in ids[index + 1:]:
            a = metrics[first]
            b = metrics[second]
            if max(a["x"], b["x"]) < min(a["right"], b["right"]) and max(
                a["y"], b["y"]
            ) < min(a["bottom"], b["bottom"]):
                overlaps.append((first, second))

    assert not overlaps
    assert all(rect["x"] >= 0 and rect["right"] <= 390 for rect in metrics.values())
    assert max(rect["y"] for rect in metrics.values()) - min(
        rect["y"] for rect in metrics.values()
    ) <= 2

    page.set_viewport_size({"width": 900, "height": 800})
    page.wait_for_function(
        "() => document.querySelector('#kg_display_scope_select option:checked').textContent === 'Full graph'"
    )
    assert page.locator("#kg_details_view_select option:checked").inner_text() == "Full details"
    assert page.locator("#kg_clear_selection").inner_text() == "Clear selection"
    assert page.locator("#kg_fit_select option:checked").inner_text() == "Fit context"


@pytest.mark.browser
def test_phone_text_controls_avoid_ios_focus_zoom(browser_graph):
    page = browser_graph.page

    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(browser_graph.output_path.as_uri() + "?phone-form-fonts", wait_until="domcontentloaded")

    controls = page.locator(
        'select, textarea, input[type="text"], input[type="search"], '
        'input[type="email"], input[type="url"], input[type="tel"], '
        'input[type="number"], input:not([type])'
    )
    font_sizes = controls.evaluate_all(
        "elements => elements.map(element => parseFloat(getComputedStyle(element).fontSize))"
    )

    assert font_sizes
    assert min(font_sizes) >= 16


@pytest.mark.browser
def test_phone_context_controls_and_compact_summary_use_one_row(browser_graph):
    page = browser_graph.page

    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(browser_graph.output_path.as_uri() + "?phone-context", wait_until="domcontentloaded")
    page.wait_for_selector("#kg_graph_context_panel")

    ids = [
        "kg_context_preset_select",
        "kg_context_depth_select",
        "kg_fit_select",
        "kg_fit_apply",
    ]
    boxes = [page.locator(f"#{control_id}").bounding_box() for control_id in ids]
    centres = [box["y"] + box["height"] / 2 for box in boxes]
    assert max(centres) - min(centres) <= 2
    assert all(box["x"] >= 0 and box["x"] + box["width"] <= 390 for box in boxes)
    visible_labels = page.locator(".kg-graph-context-controls .kg-group-label")
    assert visible_labels.count() == 2
    assert visible_labels.nth(0).inner_text() == "Context"
    assert visible_labels.nth(1).inner_text() == "Frame"
    assert visible_labels.nth(0).is_visible()
    assert visible_labels.nth(1).is_visible()
    assert page.locator("#kg_fit_select option:checked").inner_text() == "Context"

    summary = page.locator("#kg_context_summary")
    assert "Foundations" not in summary.inner_text()
    assert "Full graph" not in summary.inner_text()
    assert summary.evaluate("element => element.scrollWidth <= element.clientWidth")
    assert page.locator("#kg_graph_context_panel").bounding_box()["height"] <= 70


@pytest.mark.browser
def test_phone_context_status_and_representation_actions_share_one_row(browser_graph):
    page = browser_graph.page
    page.set_viewport_size({"width": 390, "height": 800})
    browser_graph.click_concept("2.1")
    point = page.evaluate(
        """() => {
          const position = network.getPositions(["2.1"])["2.1"];
          const dom = network.canvasToDOM(position);
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          return {x: rect.left + dom.x, y: rect.top + dom.y};
        }"""
    )
    page.evaluate(
        """async point => {
          const canvas = network.canvas.frame.canvas;
          const fire = type => canvas.dispatchEvent(new PointerEvent(type, {
            bubbles: true,
            cancelable: true,
            clientX: point.x,
            clientY: point.y,
            pointerId: 8,
            pointerType: "touch",
            isPrimary: true
          }));
          fire("pointerdown");
          fire("pointerup");
          await new Promise(resolve => setTimeout(resolve, 120));
          fire("pointerdown");
          fire("pointerup");
        }""",
        point,
    )

    summary = page.locator("#kg_context_summary")
    selected_action = page.locator("#kg_expand_selected_module")
    context_action = page.locator("#kg_expand_context_modules")
    selected_action.wait_for(state="visible")
    context_action.wait_for(state="visible")
    boxes = [item.bounding_box() for item in (summary, selected_action, context_action)]

    assert summary.inner_text().endswith("context concepts")
    assert "·" not in summary.inner_text()
    assert selected_action.inner_text() == "Expand module"
    assert context_action.inner_text().startswith("Expand ")
    assert context_action.inner_text().endswith(" folded")
    assert max(box["y"] for box in boxes) - min(box["y"] for box in boxes) <= 6


@pytest.mark.browser
def test_phone_concept_masthead_shares_one_row_until_contents_open(repo_browser_graph):
    page = repo_browser_graph.page
    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(
        repo_browser_graph.output_path.as_uri() + "#concept-sr.wave_equation",
        wait_until="domcontentloaded",
    )
    page.wait_for_selector("#info_panel .concept-title")

    title = page.locator("#info_panel .concept-title")
    module_chip = page.locator("#info_panel .concept-module-chip")
    toc = page.locator("#info_panel .concept-toc")
    toc_summary = toc.locator(":scope > summary")
    boxes = [item.bounding_box() for item in (title, module_chip, toc_summary)]

    assert max(box["y"] for box in boxes) - min(box["y"] for box in boxes) <= 6
    assert module_chip.inner_text() == "SR-5"
    assert module_chip.get_attribute("aria-label") == "Module: SR-5 Field Dynamics and Radiation"
    assert not toc.evaluate("element => element.open")

    title_row_bottom = page.locator("#info_panel .concept-title-row").bounding_box()["y"] + (
        page.locator("#info_panel .concept-title-row").bounding_box()["height"]
    )
    toc_summary.click()
    assert toc.evaluate("element => element.open")
    assert toc.locator(".concept-toc-links").bounding_box()["y"] >= title_row_bottom


@pytest.mark.browser
def test_phone_module_masthead_places_contents_to_right_until_open(repo_browser_graph):
    page = repo_browser_graph.page
    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(
        repo_browser_graph.output_path.as_uri() + "#module-sr.spacetime_foundations",
        wait_until="domcontentloaded",
    )
    page.wait_for_selector("#info_panel .module-sticky-header .module-title")

    masthead = page.locator("#info_panel .module-sticky-header")
    title = masthead.locator(".module-title")
    title_row = masthead.locator(".concept-title-row")
    toc = masthead.locator(".concept-toc")
    toc_summary = toc.locator(":scope > summary")
    title_box = title.bounding_box()
    toc_box = toc_summary.bounding_box()

    assert not toc.evaluate("element => element.open")
    assert toc_box["x"] >= title_box["x"] + title_box["width"]
    assert abs(toc_box["y"] - title_box["y"]) <= 6

    title_row_bottom = title_row.bounding_box()["y"] + title_row.bounding_box()["height"]
    toc_summary.click()
    assert toc.evaluate("element => element.open")
    assert toc.locator(".concept-toc-links").bounding_box()["y"] >= title_row_bottom


@pytest.mark.browser
def test_default_startup_has_no_selected_concept(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page

    page.wait_for_function("""() => window.location.hash === ''""")

    assert "Select a concept" in page.locator("#info_panel").inner_text()
    assert page.locator(".kg-concept-item.active").count() == 0


@pytest.mark.browser
def test_repo_starts_with_every_module_folded(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page

    page.wait_for_function(
        """() => Object.keys(moduleData).every(moduleId =>
          nodes.get("module::" + moduleId) &&
          (moduleData[moduleId].members || []).every(conceptId => nodes.get(conceptId).hidden)
        )"""
    )

    assert page.evaluate(
        """() => Object.keys(moduleData).filter(moduleId =>
          Boolean(nodes.get("module::" + moduleId))
        ).length"""
    ) == 13


@pytest.mark.browser
def test_explicit_startup_hash_overrides_default_concept(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page

    page.goto(
        shared_repo_browser_graph.output_path.as_uri() + "#concept-sr.electric_field",
        wait_until="domcontentloaded",
    )
    page.wait_for_function("""() => window.location.hash === '#concept-sr.electric_field'""")

    assert page.locator("#info_panel h2").inner_text() == "SR-4.3 Electric field"
    assert page.locator("#kg_view_title").inner_text() == "SR-4.3 Electric field"


@pytest.mark.browser
def test_masthead_title_typesets_concept_label_equations(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page

    page.goto(
        shared_repo_browser_graph.output_path.as_uri() + "#concept-sr.field_tensor",
        wait_until="domcontentloaded",
    )
    page.wait_for_function("""() => window.location.hash === '#concept-sr.field_tensor'""")
    page.wait_for_selector("#kg_view_title mjx-container")

    masthead_text = page.locator("#kg_view_title").inner_text()
    assert masthead_text.startswith("SR-4.2 Field tensor")
    assert "\\(" not in masthead_text
    assert "\\)" not in masthead_text


@pytest.mark.browser
def test_gr_covariant_derivative_equations_are_typeset(shared_repo_browser_graph):
    page = shared_repo_browser_graph.page

    page.goto(
        shared_repo_browser_graph.output_path.as_uri()
        + "#concept-gr.covariant_derivative",
        wait_until="domcontentloaded",
    )
    page.wait_for_function(
        "() => window.location.hash === '#concept-gr.covariant_derivative'"
    )
    page.wait_for_selector("#info_panel mjx-container")

    details_text = page.locator("#info_panel").inner_text()
    assert "\\(" not in details_text
    assert "\\nabla" not in details_text


@pytest.mark.browser
def test_workspace_splitter_resizes_graph_and_details_panes(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    splitter = page.locator("#kg_pane_splitter")
    before = page.evaluate(
        """() => {
          const graph = document.getElementById("kg_graph_pane").getBoundingClientRect();
          const details = document.getElementById("kg_details_pane").getBoundingClientRect();
          return {graphWidth: graph.width, detailsWidth: details.width};
        }"""
    )
    box = splitter.bounding_box()

    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.mouse.move(box["x"] + box["width"] / 2 + 120, box["y"] + box["height"] / 2)
    page.mouse.up()
    page.wait_for_function(
        """before => {
          const graph = document.getElementById("kg_graph_pane").getBoundingClientRect();
          const details = document.getElementById("kg_details_pane").getBoundingClientRect();
          return graph.width > before.graphWidth + 70 &&
            details.width < before.detailsWidth - 70;
        }""",
        arg=before,
    )

    after = page.evaluate(
        """() => {
          const graph = document.getElementById("kg_graph_pane").getBoundingClientRect();
          const details = document.getElementById("kg_details_pane").getBoundingClientRect();
          const graphControl = document.querySelector(".kg-shell-graph-control").getBoundingClientRect();
          return {
            graphWidth: graph.width,
            detailsWidth: details.width,
            graphCenter: graph.x + graph.width / 2,
            graphControlCenter: graphControl.x + graphControl.width / 2
          };
        }"""
    )

    assert after["graphWidth"] > before["graphWidth"] + 70
    assert after["detailsWidth"] < before["detailsWidth"] - 70
    assert abs(after["graphControlCenter"] - after["graphCenter"]) <= 6


@pytest.mark.browser
def test_alt_left_arrow_is_not_intercepted(browser_graph):
    page = browser_graph.page

    default_prevented = page.evaluate(
        """() => {
          const event = new KeyboardEvent("keydown", {
            key: "ArrowLeft",
            altKey: true,
            bubbles: true,
            cancelable: true
          });
          document.dispatchEvent(event);
          return event.defaultPrevented;
        }"""
    )

    assert not default_prevented


@pytest.mark.browser
def test_alt_left_arrow_navigates_browser_history(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("1.1")
    browser_graph.click_concept("2.1")
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"

    page.keyboard.press("Alt+ArrowLeft")

    page.wait_for_function("""() => window.location.hash === '#concept-1.1'""")
    assert page.locator("#info_panel h2").inner_text() == "1.1 Alpha"


@pytest.mark.browser
def test_details_panel_scrolls_to_top_when_new_concept_selected(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#info_panel").evaluate("panel => { panel.scrollTop = 400; }")
    assert page.locator("#info_panel").evaluate("panel => panel.scrollTop") > 0

    browser_graph.click_concept("3.1")

    page.wait_for_function("""() => document.getElementById("info_panel").scrollTop < 25""")


@pytest.mark.browser
def test_workspace_presents_graph_and_details_as_peer_panes(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

    metrics = page.evaluate(
        """() => {
          const shell = document.getElementById("kg_workspace").getBoundingClientRect();
          const graph = document.getElementById("kg_graph_pane").getBoundingClientRect();
          const details = document.getElementById("kg_details_pane").getBoundingClientRect();
          return {shell, graph, details};
        }"""
    )

    assert page.locator("#kg_view_title").inner_text() == "2.2 Gamma"
    assert abs(metrics["graph"]["width"] - metrics["details"]["width"]) <= 2
    assert abs(metrics["graph"]["x"] - metrics["shell"]["x"]) <= 1
    assert metrics["details"]["x"] > metrics["graph"]["x"]
    assert abs(metrics["graph"]["y"] - metrics["details"]["y"]) <= 1

    page.locator("#kg_details_view_select").select_option("hide")

    assert page.locator("body").evaluate("el => el.classList.contains('kg-details-hidden')")
    graph_only = page.locator("#kg_graph_pane").bounding_box()
    assert graph_only["width"] > metrics["shell"]["width"] * 0.95

    page.locator("#kg_details_view_select").select_option("full")
    page.locator("#kg_display_scope_select").select_option("hidden")

    assert page.locator("body").evaluate("el => el.classList.contains('kg-graph-hidden')")
    details_only = page.locator("#kg_details_pane").bounding_box()
    assert details_only["width"] > metrics["shell"]["width"] * 0.95


@pytest.mark.browser
def test_details_hide_does_not_blank_workspace_when_graph_is_hidden(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_display_scope_select").select_option("hidden")
    page.locator("#kg_details_view_select").select_option("hide")

    assert page.locator("body").evaluate("el => el.classList.contains('kg-graph-hidden')")
    assert not page.locator("body").evaluate("el => el.classList.contains('kg-details-hidden')")
    assert page.locator("#kg_details_view_select").input_value() == "full"
    assert page.locator("#info_panel").is_visible()


@pytest.mark.browser
def test_reading_mode_core_filters_blocks_and_study_questions(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_details_view_select").select_option("core")

    assert page.locator("#info_panel").get_attribute("data-reading-mode") == "core"
    block_kinds = _visible_content_block_kinds(page)
    assert "definition" in block_kinds
    assert "intuition" in block_kinds
    assert "warning" in block_kinds
    assert "derivation_step" not in block_kinds
    assert "historical_note" not in block_kinds
    questions = page.locator("#info_panel details.study-questions")
    assert not questions.evaluate("node => node.open")
    questions.locator(":scope > summary").click()
    assert questions.locator(".study-question").count() == 1


@pytest.mark.browser
def test_real_lorentz_maths_mode_keeps_boost_context(clean_repo_browser_graph):
    page = clean_repo_browser_graph.page

    clean_repo_browser_graph.click_concept("sr.lorentz_transformations")
    page.locator("#kg_details_view_select").select_option("maths")

    assert page.locator("#info_panel").get_attribute("data-reading-mode") == "maths"
    block_kinds = _visible_content_block_kinds(page)
    assert "construction" in block_kinds
    assert "Standard boost setup" in page.locator("#info_panel").inner_text()
    questions = page.locator("#info_panel details.study-questions")
    questions.locator(":scope > summary").click()
    prompts = questions.locator(".study-question-prompt").all_inner_texts()
    assert not any("q3" in prompt.lower() for prompt in prompts)


@pytest.mark.browser
def test_folded_reading_mode_keeps_full_content_and_closes_top_level_sections(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_details_view_select").select_option("folded")

    assert page.locator("#info_panel").get_attribute("data-reading-mode") == "folded"
    panel = page.locator("#info_panel")
    assert panel.locator(":scope > details").count() > 4
    assert panel.locator(":scope > details[open]").count() == 0
    assert "warning" in _visible_content_block_kinds(page)

    definition = page.locator("#info_panel #kg-toc-2-2-definition")
    definition.locator(":scope > summary").click()
    assert definition.evaluate("el => el.open")

    page.locator("#kg_notes_edit_toggle").evaluate(
        "el => { el.checked = true; el.dispatchEvent(new Event('change', {bubbles:true})); }"
    )
    assert page.locator("#info_panel #kg-toc-2-2-definition").evaluate("el => el.open")


@pytest.mark.browser
def test_folded_reading_mode_closes_module_sections(browser_graph):
    page = browser_graph.page

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    page.locator("#kg_details_view_select").select_option("folded")

    panel = page.locator("#info_panel")
    assert panel.locator(":scope > details").count() > 1
    assert panel.locator(":scope > details[open]").count() == 0


@pytest.mark.browser
def test_reading_mode_maths_filters_blocks_and_study_questions(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_details_view_select").select_option("maths")

    assert page.locator("#info_panel").get_attribute("data-reading-mode") == "maths"
    assert _toc_titles(page) == [
        "Graphic",
        "Gamma algebra step",
        "Derived from",
        "Where this is used",
        "Study Questions",
    ]
    block_kinds = _visible_content_block_kinds(page)
    assert "definition" not in block_kinds
    assert "intuition" not in block_kinds
    assert "derivation_step" in block_kinds
    step = page.locator("#info_panel details.content-block-derivation_step")
    assert step.count() == 1
    step.locator("summary").click()
    assert step.locator(".content-block-fold-body").is_visible()
    questions = page.locator("#info_panel details.study-questions")
    assert not questions.evaluate("node => node.open")
    questions.locator(":scope > summary").click()
    assert questions.locator(".study-question").count() == 1


@pytest.mark.browser
def test_legacy_concept_toc_includes_sections_and_study_questions(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")

    assert _toc_titles(page) == [
        "Definition",
        "Explanation",
        "Where this is used",
        "Study Questions",
    ]


@pytest.mark.browser
def test_practice_reading_mode_opens_study_questions_by_default(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_details_view_select").select_option("practice")

    questions = page.locator("#info_panel details.study-questions")
    assert questions.count() == 1
    assert questions.evaluate("node => node.open")
    assert questions.locator(".study-question").first.is_visible()


@pytest.mark.browser
def test_optional_details_render_inline_and_can_contain_concept_links(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    optional = page.locator("#info_panel details.optional-detail")
    assert optional.count() == 1
    assert optional.locator("summary").inner_text() == "Why this matters"
    assert not optional.locator(".optional-detail-body").is_visible()

    optional.locator("summary").click()

    assert optional.locator(".optional-detail-body").is_visible()
    optional.locator(".concept-link").click()
    assert page.locator("#kg_concept_preview").is_visible()
    assert page.locator("#kg_concept_preview .concept-preview-go").get_attribute("data-concept-id") == "1.1"

    page.locator("#kg_concept_preview .concept-preview-go").click()

    assert page.locator("#info_panel h2").inner_text() == "1.1 Alpha"
    assert page.evaluate("() => window.location.hash") == "#concept-1.1"


@pytest.mark.browser
def test_concept_link_hover_shows_preview_without_navigating(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#info_panel details.optional-detail summary").click()
    link = page.locator("#info_panel .optional-detail-body .concept-link")

    link.hover()

    preview = page.locator("#kg_concept_preview")
    assert preview.is_visible()
    assert preview.locator(".concept-preview-go").get_attribute("data-concept-id") == "1.1"
    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"


@pytest.mark.browser
def test_concept_link_preview_highlights_visible_graph_target(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#info_panel details.optional-detail summary").click()
    link = page.locator("#info_panel .optional-detail-body .concept-link")

    link.hover()

    assert page.locator(
        '#kg_node_labels .kg-node-label[data-node-id="1.1"]'
    ).evaluate("el => el.classList.contains('kg-node-label-transient')")
    assert page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            String(item.from) === "2.1" &&
            String(item.to) === "1.1" &&
            item.relation === "REQUIRES"
          );
          return edge && edge.color && edge.color.color === "#174ea6" && edge.width >= 4;
        }"""
    )


@pytest.mark.browser
def test_concept_link_preview_does_not_highlight_hidden_graph_target(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#kg_display_scope_select").select_option("hidden")
    page.locator("#info_panel details.optional-detail summary").click()
    page.locator("#info_panel .optional-detail-body .concept-link").click()

    assert page.locator("#kg_concept_preview").is_visible()
    assert not page.locator(
        '#kg_node_labels .kg-node-label[data-node-id="1.1"]'
    ).evaluate("el => el.classList.contains('kg-node-label-transient')")


@pytest.mark.browser
def test_edge_click_opens_relationship_inspection(shared_browser_graph):
    page = shared_browser_graph.page

    page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            String(item.from) === "2.1" &&
            String(item.to) === "1.1" &&
            item.relation === "REQUIRES"
          );
          network.emit("click", {
            nodes: [],
            edges: [edge.id],
            pointer: {DOM: {x: 0, y: 0}, canvas: {x: 0, y: 0}}
          });
        }"""
    )

    assert page.locator("#kg_inspection_dialog").is_visible()
    assert page.locator("#kg_inspection_body .edge-detail").count() == 1
    panel_text = page.locator("#kg_inspection_body").inner_text()
    statement = page.locator("#kg_inspection_body .edge-detail-statement")
    assert _statement_concept_ids(statement) == ["2.1", "1.1"]
    assert statement.locator(".edge-detail-phrase").count() == 1
    assert page.locator("#kg_inspection_body .edge-detail-route").count() == 0
    assert "REQUIRES" in panel_text
    assert "knowledge" not in panel_text
    assert "Note" not in panel_text
    assert page.locator("#kg_inspection_body .edge-detail-meta mjx-container").count() >= 1
    page.locator("#kg_inspection_close").click()


@pytest.mark.browser
def test_edge_hover_tooltip_typesets_mathjax_and_uses_relationship_heading(browser_graph):
    page = browser_graph.page

    page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            String(item.from) === "2.1" &&
            String(item.to) === "1.1" &&
            item.relation === "REQUIRES"
          );
          network.emit("hoverEdge", {
            edge: edge.id,
            pointer: {DOM: {x: 120, y: 90}, canvas: {x: 0, y: 0}}
          });
        }"""
    )

    page.wait_for_selector("#kg_node_tooltip", state="visible")
    page.wait_for_selector("#kg_node_tooltip mjx-container")
    tooltip = page.locator("#kg_node_tooltip")
    assert tooltip.locator(".kg-tooltip-title").count() == 1
    assert tooltip.locator(".kg-tooltip-relation").count() == 1
    assert tooltip.locator(".kg-tooltip-relation").evaluate(
        "el => getComputedStyle(el).color !== 'rgb(34, 34, 34)'"
    )
    tooltip_text = tooltip.inner_text()
    assert "Noether's theorem" in tooltip_text
    assert "REQUIRES" not in tooltip_text
    assert "\\(" not in tooltip_text


@pytest.mark.browser
def test_edge_hover_ignores_dimmed_background_edges(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    before = page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            String(item.from) === "2.1" &&
            String(item.to) === "1.1" &&
            item.relation === "REQUIRES"
          );
          return {
            width: edge.width,
            color: edge.color && edge.color.color,
            opacity: edge.color && edge.color.opacity
          };
        }"""
    )
    page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            String(item.from) === "2.1" &&
            String(item.to) === "1.1" &&
            item.relation === "REQUIRES"
          );
          network.emit("hoverEdge", {
            edge: edge.id,
            pointer: {DOM: {x: 140, y: 100}, canvas: {x: 0, y: 0}}
          });
        }"""
    )

    page.wait_for_timeout(100)
    after = page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            String(item.from) === "2.1" &&
            String(item.to) === "1.1" &&
            item.relation === "REQUIRES"
          );
          return {
            width: edge.width,
            color: edge.color && edge.color.color,
            opacity: edge.color && edge.color.opacity
          };
        }"""
    )

    assert after == before
    assert not page.locator("#kg_node_tooltip").is_visible()


@pytest.mark.browser
def test_constructed_from_edge_click_shows_readable_relationship_sentence(clean_repo_browser_graph):
    page = clean_repo_browser_graph.page

    clean_repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="sr.electromagnetic_structure_gauge_and_stress_energy"]'
    ).click()
    page.locator(
        '#info_panel .module-graph-fold-button[data-module-fold-state="expanded"]'
    ).click()

    page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            String(item.from) === "sr.field_tensor" &&
            String(item.to) === "sr.vector_potential" &&
            item.relation === "CONSTRUCTED_FROM"
          );
          network.emit("click", {
            nodes: [],
            edges: [edge.id],
            pointer: {DOM: {x: 0, y: 0}, canvas: {x: 0, y: 0}}
          });
        }"""
    )

    assert page.locator("#kg_inspection_dialog").is_visible()
    assert page.locator("#kg_inspection_body .edge-detail").count() == 1
    statement = page.locator("#kg_inspection_body .edge-detail-statement")
    assert _statement_concept_ids(statement) == ["sr.field_tensor", "sr.vector_potential"]
    assert statement.locator(".edge-detail-phrase").count() == 1
    panel_text = page.locator("#kg_inspection_body").inner_text()
    assert "CONSTRUCTED_FROM" in panel_text
    page.locator("#kg_inspection_close").click()


@pytest.mark.browser
def test_concept_details_show_backlinks_grouped_by_relation(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("1.1")

    backlinks = page.locator("#info_panel .concept-backlinks")
    assert backlinks.count() == 1
    assert backlinks.evaluate("el => el.open")
    assert backlinks.locator(".concept-backlink-group").count() == 3
    assert backlinks.locator(".edge-detail-concept").evaluate_all(
        "nodes => nodes.map(node => node.getAttribute('data-edge-concept-id'))"
    ) == ["2.2", "2.1", "2.1"]
    assert "Auto graph highlights" not in backlinks.inner_text()
    assert backlinks.locator(".concept-backlink-group-scope").count() == 0


@pytest.mark.browser
def test_concept_details_show_derived_from_links_only(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    derived_from = page.locator("#info_panel .concept-derived-from")
    assert derived_from.count() == 1
    assert derived_from.evaluate("el => el.open")
    assert derived_from.locator(".edge-detail-concept").evaluate_all(
        "nodes => nodes.map(node => node.getAttribute('data-edge-concept-id'))"
    ) == ["1.1"]


@pytest.mark.browser
def test_details_relationship_sections_explicitly_set_graph_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_display_scope_select").select_option("hidden")
    page.locator("#info_panel .concept-derived-from-show-graph").click()

    assert page.evaluate("() => kgViewerStateSnapshot()") == {
        "selection": {"type": "concept", "id": "2.2"},
        "contextRule": {
            "preset": "derivation",
            "depth": "one-hop",
            "customTraversals": [],
        },
        "displayScope": "context",
    }
    assert page.locator("#kg_context_preset_select").input_value() == "derivation"
    assert page.locator("#kg_context_depth_select").input_value() == "one-hop"

    browser_graph.click_concept("1.1")
    backlinks = page.locator("#info_panel .concept-backlinks")
    backlinks.locator(".concept-backlinks-full-tree").check()
    backlinks.locator(".concept-backlinks-show-graph").click()

    assert page.evaluate("() => kgViewerStateSnapshot().contextRule") == {
        "preset": "uses",
        "depth": "transitive",
        "customTraversals": [],
    }
    assert page.evaluate("() => kgViewerStateSnapshot().displayScope") == "context"


@pytest.mark.browser
def test_derived_from_full_tree_expands_only_derives_from_ancestry(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")

    derived_from = page.locator("#info_panel .concept-derived-from")
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="2.2"]').count() == 1
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="1.1"]').count() == 0

    derived_from.locator(".concept-derived-from-full-tree").check()

    derived_from = page.locator("#info_panel .concept-derived-from")
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="2.2"]').count() == 1
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="1.1"]').count() == 1
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="2.1"]').count() == 0


@pytest.mark.browser
def test_derived_from_full_tree_includes_constructed_from_ancestry(constructed_browser_graph):
    page = constructed_browser_graph.page

    constructed_browser_graph.click_concept("3.1")

    derived_from = page.locator("#info_panel .concept-derived-from")
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="2.2"]').count() == 1
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="2.1"]').count() == 0

    derived_from.locator(".concept-derived-from-full-tree").check()

    derived_from = page.locator("#info_panel .concept-derived-from")
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="2.2"]').count() == 1
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="1.1"]').count() == 1
    assert derived_from.locator('.edge-detail-concept[data-edge-concept-id="2.1"]').count() == 1
    assert "Constructed from" in derived_from.locator(".concept-tree-relation").evaluate_all(
        "nodes => nodes.map(node => node.textContent).join('\\n')"
    )


@pytest.mark.browser
def test_derived_from_concept_hover_shows_preview(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator('#info_panel .concept-derived-from .edge-detail-concept[data-edge-concept-id="1.1"]').hover()

    preview = page.locator("#kg_concept_preview")
    assert preview.is_visible()
    assert preview.locator(".concept-preview-go").get_attribute("data-concept-id") == "1.1"
    assert page.locator("#info_panel h2").inner_text() == "2.2 Gamma"


@pytest.mark.browser
def test_backlinks_full_tree_expands_only_derives_from_descendants(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("1.1")

    backlinks = page.locator("#info_panel .concept-backlinks")
    assert backlinks.locator('.edge-detail-concept[data-edge-concept-id="2.2"]').count() == 1
    assert backlinks.locator('.edge-detail-concept[data-edge-concept-id="3.1"]').count() == 0

    backlinks.locator(".concept-backlinks-full-tree").check()

    backlinks = page.locator("#info_panel .concept-backlinks")
    assert backlinks.locator('.edge-detail-concept[data-edge-concept-id="2.2"]').count() == 1
    assert backlinks.locator('.edge-detail-concept[data-edge-concept-id="3.1"]').count() == 1
    assert backlinks.locator('.edge-detail-concept[data-edge-concept-id="2.1"]').count() >= 1


@pytest.mark.browser
def test_backlinks_full_tree_includes_constructed_from_descendants(constructed_browser_graph):
    page = constructed_browser_graph.page

    constructed_browser_graph.click_concept("2.1")

    backlinks = page.locator("#info_panel .concept-backlinks")
    assert backlinks.locator('.edge-detail-concept[data-edge-concept-id="2.2"]').count() == 1
    assert "Built from this" in backlinks.inner_text()

    backlinks.locator(".concept-backlinks-full-tree").check()

    backlinks = page.locator("#info_panel .concept-backlinks")
    assert backlinks.locator('.edge-detail-concept[data-edge-concept-id="2.2"]').count() == 1
    assert backlinks.locator('.edge-detail-concept[data-edge-concept-id="3.1"]').count() >= 1
    assert "Constructed from" in backlinks.locator(".concept-tree-relation").evaluate_all(
        "nodes => nodes.map(node => node.textContent).join('\\n')"
    )


@pytest.mark.browser
def test_backlink_concept_hover_shows_preview(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("1.1")
    page.locator('#info_panel .concept-backlinks .edge-detail-concept[data-edge-concept-id="2.2"]').hover()

    preview = page.locator("#kg_concept_preview")
    assert preview.is_visible()
    assert preview.locator(".concept-preview-go").get_attribute("data-concept-id") == "2.2"
    assert page.locator("#info_panel h2").inner_text() == "1.1 Alpha"


@pytest.mark.browser
def test_optional_details_do_not_create_whitespace_only_lines(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.1")

    whitespace_lines = page.locator("#info_panel .concept-line").evaluate_all(
        """lines => lines
          .map(line => line.textContent)
          .filter(text => text && text.trim() === "")
        """
    )
    assert whitespace_lines == []


@pytest.mark.browser
def test_search_finds_definition_text_and_highlights_detail_match(browser_graph):
    page = browser_graph.page

    browser_graph.open_search()
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
def test_edge_type_tools_section_is_removed_in_integrated_mode(browser_graph):
    page = browser_graph.page

    assert page.locator("#kg_edge_filters_section").count() == 0
    assert page.locator("#kg_edge_filters").count() == 0
    assert "Edge types" not in page.locator("#kg_controls").inner_text()


@pytest.mark.browser
def test_focussed_mode_hides_non_neighbourhood_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#kg_context_preset_select").select_option("connections")
    page.locator("#kg_display_scope_select").select_option("context")

    assert page.locator("#kg_display_scope_select").input_value() == "context"
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": True,
        "3.1": False,
    }
    assert page.evaluate(
        """() => edges.get().filter(edge => !edge.hidden).length"""
    ) > 0

    assert page.locator("#kg_context_summary").get_attribute("data-display-scope") == "context"


@pytest.mark.browser
def test_hovering_section_context_edge_does_not_move_or_zoom_graph(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_display_scope_select").select_option("context")
    page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-3-1-derived-from"]'
    ).click()

    before = page.evaluate(
        """() => ({
          position: network.getViewPosition(),
          scale: network.getScale()
        })"""
    )
    page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            !item.hidden &&
            String(item.from) === "3.1" &&
            String(item.to) === "2.2" &&
            item.relation === "DERIVES_FROM"
          );
          network.emit("hoverEdge", {edge: edge.id});
        }"""
    )
    page.wait_for_timeout(250)
    after = page.evaluate(
        """() => ({
          position: network.getViewPosition(),
          scale: network.getScale()
        })"""
    )

    assert abs(after["scale"] - before["scale"]) < 0.0001
    assert abs(after["position"]["x"] - before["position"]["x"]) < 0.1
    assert abs(after["position"]["y"] - before["position"]["y"]) < 0.1


@pytest.mark.browser
def test_graph_view_selector_hides_derivation_trace_mode(browser_graph):
    page = browser_graph.page

    assert page.locator('#kg_display_scope_select option[value="derivation-trace"]').count() == 0
    assert "Derivation trace" not in page.locator("#kg_display_scope_select").inner_text()
    assert page.evaluate(
        """() => ["kgSetGraphView", "kgHideGraph", "kgHighlight", "kgReset"]
          .every(name => typeof window[name] === "undefined")"""
    )


@pytest.mark.browser
def test_context_controls_group_semantics_and_default_fit_target(browser_graph):
    page = browser_graph.page

    groups = page.locator("#kg_graph_context_panel .kg-context-control-group")
    assert groups.count() == 2
    assert groups.nth(0).get_attribute("aria-label") == "Context rule"
    assert groups.nth(1).get_attribute("aria-label") == "Camera framing"
    assert groups.nth(0).locator("#kg_context_preset_select").count() == 1
    assert groups.nth(0).locator("#kg_context_depth_select").count() == 1
    assert groups.nth(1).locator("#kg_fit_select").count() == 1
    assert groups.nth(1).locator("#kg_fit_apply").count() == 1
    assert page.locator("#kg_fit_select").input_value() == "context"


@pytest.mark.browser
def test_graph_view_selector_hides_graph_and_supports_focussed_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_context_preset_select").select_option("connections")
    page.locator("#kg_display_scope_select").select_option("hidden")

    assert page.locator("#kg_display_scope_select").input_value() == "hidden"
    assert page.locator("body").evaluate("el => el.classList.contains('kg-graph-hidden')")
    assert page.evaluate("""() => nodes.get().every(node => node.hidden)""")
    assert page.evaluate("""() => edges.get().every(edge => edge.hidden)""")
    assert "Delta definition" in page.locator("#info_panel").inner_text()

    browser_graph.click_concept("2.1")
    assert page.locator("#kg_display_scope_select").input_value() == "hidden"
    assert "Beta definition" in page.locator("#info_panel").inner_text()
    assert page.evaluate("""() => nodes.get().every(node => node.hidden)""")

    page.locator("#kg_display_scope_select").select_option("context")
    assert page.locator("#kg_display_scope_select").input_value() == "context"
    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": False,
        "2.2": True,
        "3.1": False,
    }


@pytest.mark.browser
def test_splash_dialog_shows_once_and_can_be_reopened(browser_graph):
    page = browser_graph.page

    page.evaluate("""() => localStorage.removeItem("srkg.splash.dismissed.v1")""")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_splash_dialog[open]")

    dialog = page.locator("#kg_splash_dialog")
    assert dialog.get_attribute("open") is not None
    assert dialog.locator("#kg_splash_title").inner_text() == "PhysicsKG quick start"
    assert dialog.locator(".kg-splash-feature-grid section").count() == 7
    assert dialog.locator(".kg-splash-feature-grid section h3").count() == 7
    assert dialog.locator(".kg-splash-feature-grid section").evaluate_all(
        "nodes => nodes.every(node => node.textContent.trim().length > 0)"
    )
    assert page.locator("#kg_splash_dialog .kg-splash-feature-grid section").count() == 7
    assert (
        "The user model has been simplified and the UI space optimised for phones"
        in dialog.inner_text()
    )
    assert "Study" in dialog.inner_text()
    assert dialog.locator(".kg-status-badge", has_text="NEW").count() == 4
    assert "Covers Special Relativity and General Relativity" in dialog.inner_text()
    assert "General Relativity remains work in progress" not in dialog.inner_text()
    assert "tracks attempts and latest results locally" in dialog.inner_text()
    assert "Edit layout" in dialog.inner_text()
    assert "temporary by default" in dialog.inner_text().lower()

    credit = page.locator("#kg_splash_dialog .kg-splash-credit")
    assert credit.locator("a").get_attribute("href") == "https://www.linkedin.com/in/ipoole/"
    grid_box = page.locator(".kg-splash-feature-grid").bounding_box()
    credit_box = credit.bounding_box()
    assert abs(credit_box["width"] - grid_box["width"]) < 1
    assert credit_box["y"] >= grid_box["y"] + grid_box["height"]
    assert page.locator("#kg_info_toggle").count() == 0

    page.locator("#kg_splash_dismiss").click()
    assert page.evaluate("""() => localStorage.getItem("srkg.splash.dismissed.v1")""") == "true"
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_controls", state="attached")
    assert page.locator("#kg_splash_dialog[open]").count() == 0

    page.locator("#kg_features_button").click()
    assert page.locator("#kg_splash_dialog[open]").count() == 1
    assert page.locator("#kg_features_button").inner_text() == "Quick start"
