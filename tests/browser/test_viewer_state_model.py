import pytest


def _context(page, concept_id, preset, depth="one-hop", custom=None):
    return page.evaluate(
        """args => kgComputeContext(
          {type: "concept", id: args.conceptId},
          {preset: args.preset, depth: args.depth, customTraversals: args.custom || []}
        )""",
        {
            "conceptId": concept_id,
            "preset": preset,
            "depth": depth,
            "custom": custom or [],
        },
    )


@pytest.mark.browser
def test_viewer_state_snapshot_adapts_existing_selection_and_scope(browser_graph):
    page = browser_graph.page

    assert page.evaluate("() => kgViewerStateSnapshot()") == {
        "selection": {"type": "none", "id": None},
        "contextRule": {
            "preset": "foundations",
            "depth": "one-hop",
            "customTraversals": [],
        },
        "displayScope": "full",
    }

    browser_graph.click_concept("2.1")
    assert page.evaluate("() => kgViewerStateSnapshot().selection") == {
        "type": "concept",
        "id": "2.1",
    }

    page.locator("#kg_display_scope_select").select_option("context")
    assert page.evaluate("() => kgViewerStateSnapshot().displayScope") == "context"


@pytest.mark.browser
def test_prerequisite_context_respects_direction_and_depth(browser_graph):
    page = browser_graph.page

    one_hop = _context(page, "3.1", "prerequisites")
    two_hops = _context(page, "3.1", "prerequisites", "two-hops")

    assert one_hop["nodeIds"] == ["2.1", "2.2", "3.1"]
    assert len(one_hop["edgeIds"]) == 2
    assert two_hops["nodeIds"] == ["1.1", "2.1", "2.2", "3.1"]
    assert len(two_hops["edgeIds"]) == 3


@pytest.mark.browser
def test_derivation_and_use_contexts_follow_opposite_directions(browser_graph):
    page = browser_graph.page

    derivation = _context(page, "3.1", "derivation", "transitive")
    uses = _context(page, "1.1", "uses", "transitive")

    assert derivation["nodeIds"] == ["1.1", "2.2", "3.1"]
    assert len(derivation["edgeIds"]) == 2
    assert uses["nodeIds"] == ["1.1", "2.1", "2.2", "3.1"]
    assert len(uses["edgeIds"]) == 5


@pytest.mark.browser
def test_foundations_combines_prerequisite_construction_and_derivation(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_context_preset_select").select_option("foundations")
    assert page.evaluate("() => kgViewerStateSnapshot().contextRule.preset") == "foundations"
    foundations = _context(page, "3.1", "foundations", "one-hop")

    assert foundations["nodeIds"] == ["2.1", "2.2", "3.1"]
    relations = page.evaluate(
        """edgeIds => edgeIds.map(id => edges.get(id).relation).sort()""",
        foundations["edgeIds"],
    )
    assert relations == ["DERIVES_FROM", "REQUIRES", "REQUIRES"]


@pytest.mark.browser
def test_custom_context_uses_only_selected_relation_direction(browser_graph):
    page = browser_graph.page

    custom = _context(
        page,
        "1.1",
        "custom",
        "one-hop",
        [{"relation": "RELATED", "direction": "undirected"}],
    )

    assert custom["nodeIds"] == ["1.1", "2.1"]
    assert len(custom["edgeIds"]) == 1


@pytest.mark.browser
def test_custom_derived_from_directions_match_their_labels(browser_graph):
    page = browser_graph.page

    selection_is_derived_from = _context(
        page,
        "2.2",
        "custom",
        custom=[{"relation": "DERIVES_FROM", "direction": "outgoing"}],
    )
    derived_from_selection = _context(
        page,
        "1.1",
        "custom",
        custom=[{"relation": "DERIVES_FROM", "direction": "incoming"}],
    )

    assert selection_is_derived_from["nodeIds"] == ["1.1", "2.2"]
    assert derived_from_selection["nodeIds"] == ["1.1", "2.2"]


@pytest.mark.browser
def test_module_context_starts_from_every_member(browser_graph):
    page = browser_graph.page

    context = page.evaluate(
        """() => kgComputeContext(
          {type: "module", id: "test.m02_applications"},
          {preset: "prerequisites", depth: "one-hop"}
        )"""
    )

    assert context["nodeIds"] == ["1.1", "2.1", "2.2", "3.1"]
    assert len(context["edgeIds"]) == 3


@pytest.mark.browser
def test_unified_renderer_separates_context_background_and_scope(browser_graph):
    page = browser_graph.page

    initial = page.evaluate("() => kgDisplayedGraphSnapshot()")
    assert initial["contextNodeIds"] == []
    assert initial["includedNodeIds"] == ["1.1", "2.1", "2.2", "3.1"]
    assert page.evaluate(
        "() => edges.get().filter(edge => !edge.hidden).map(edge => edge.relation).sort()"
    ) == ["DERIVES_FROM", "DERIVES_FROM", "REQUIRES", "REQUIRES", "REQUIRES"]
    colours = page.evaluate(
        """() => [...new Set(edges.get().filter(edge => !edge.hidden)
          .map(edge => edge.color.color))].sort()"""
    )
    assert len(colours) >= 2
    assert "#aeb5bf" not in colours

    page.locator("#kg_context_preset_select").select_option("prerequisites")
    assert page.evaluate(
        "() => [...new Set(edges.get().filter(edge => !edge.hidden).map(edge => edge.relation))]"
    ) == ["REQUIRES"]
    assert page.evaluate(
        """() => edges.get().filter(edge => !edge.hidden)
          .every(edge => edge.color.color !== "#aeb5bf")"""
    )

    browser_graph.click_concept("3.1")
    full = page.evaluate("() => kgDisplayedGraphSnapshot()")
    assert full["scope"] == "full"
    assert full["contextNodeIds"] == ["2.1", "2.2", "3.1"]
    assert full["includedNodeIds"] == ["1.1", "2.1", "2.2", "3.1"]
    assert page.evaluate(
        "() => [...new Set(edges.get().filter(edge => !edge.hidden).map(edge => edge.relation))]"
    ) == ["REQUIRES"]
    edge_colours = page.evaluate(
        """() => Object.fromEntries(edges.get().filter(edge => !edge.hidden).map(edge => [
          `${edge.from}->${edge.to}`,
          edge.color.color
        ]))"""
    )
    assert edge_colours["3.1->2.1"] != "#aeb5bf"
    assert edge_colours["3.1->2.2"] != "#aeb5bf"
    assert edge_colours["2.1->1.1"] == "#aeb5bf"

    page.locator("#kg_display_scope_select").select_option("context")
    context_only = page.evaluate("() => kgDisplayedGraphSnapshot()")
    assert context_only["scope"] == "context"
    assert context_only["includedNodeIds"] == ["2.1", "2.2", "3.1"]

    page.locator("#kg_display_scope_select").select_option("hidden")
    hidden = page.evaluate("() => kgDisplayedGraphSnapshot()")
    assert hidden["scope"] == "hidden"
    assert hidden["includedNodeIds"] == []


@pytest.mark.browser
def test_custom_context_filters_full_graph_edges_with_and_without_selection(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("1.1")
    page.locator("#kg_context_preset_select").select_option("custom")
    custom = page.locator("#kg_custom_context")
    custom.locator("input").evaluate_all(
        "inputs => inputs.forEach(input => { input.checked = false; })"
    )
    custom.locator(
        'input[data-relation="RELATED"][data-direction="undirected"]'
    ).check()
    page.locator("#kg_custom_context_apply").click()

    assert page.evaluate(
        "() => edges.get().filter(edge => !edge.hidden).map(edge => edge.relation)"
    ) == ["RELATED"]
    assert page.evaluate(
        "() => edges.get().find(edge => !edge.hidden).color.color !== '#aeb5bf'"
    )

    page.locator("#kg_clear_selection").click()
    assert page.evaluate(
        "() => edges.get().filter(edge => !edge.hidden).map(edge => edge.relation)"
    ) == ["RELATED"]
    assert page.evaluate(
        "() => edges.get().find(edge => !edge.hidden).color.color !== '#aeb5bf'"
    )


@pytest.mark.browser
def test_explicit_context_controls_replace_focus_lens(browser_graph):
    page = browser_graph.page

    assert page.locator("#kg_display_scope_select").count() == 1
    assert page.locator("#kg_context_preset_select").count() == 1
    assert page.locator("#kg_context_preset_select option").evaluate_all(
        "options => options.map(option => option.value)"
    ) == [
        "connections",
        "prerequisites",
        "derivation",
        "foundations",
        "uses",
        "related",
        "custom",
    ]
    assert page.locator("#kg_context_depth_select").count() == 1
    assert page.locator("#kg_fit_apply").count() == 1
    assert page.locator("#kg_graph_view_select").count() == 0
    assert page.locator("#kg_focus_lens").count() == 0
    assert not page.locator("#kg_context_preset_select").is_disabled()
    assert page.locator("#kg_context_depth_select").is_disabled()

    browser_graph.click_concept("3.1")
    page.locator("#kg_context_preset_select").select_option("prerequisites")
    page.locator("#kg_context_depth_select").select_option("two-hops")

    state = page.evaluate("() => kgViewerStateSnapshot()")
    assert state["contextRule"] == {
        "preset": "prerequisites",
        "depth": "two-hops",
        "customTraversals": [],
    }
    assert page.locator("#kg_context_summary").get_attribute("data-context-preset") == "prerequisites"
    assert page.locator("#kg_context_summary").get_attribute("data-context-depth") == "two-hops"

    browser_graph.click_concept("2.1")
    assert page.evaluate("() => kgViewerStateSnapshot().contextRule") == state["contextRule"]


@pytest.mark.browser
def test_custom_context_has_one_shared_depth(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("1.1")

    page.locator("#kg_context_preset_select").select_option("custom")
    custom = page.locator("#kg_custom_context")
    assert custom.is_visible()
    custom.locator("input").evaluate_all(
        "inputs => inputs.forEach(input => { input.checked = false; })"
    )
    custom.locator(
        'input[data-relation="RELATED"][data-direction="undirected"]'
    ).check()
    page.locator("#kg_context_depth_select").select_option("two-hops")
    page.locator("#kg_custom_context_apply").click()

    state = page.evaluate("() => kgViewerStateSnapshot()")
    assert state["contextRule"] == {
        "preset": "custom",
        "depth": "two-hops",
        "customTraversals": [{"relation": "RELATED", "direction": "undirected"}],
    }
    assert page.evaluate("() => kgDisplayedGraphSnapshot().contextNodeIds") == ["1.1", "2.1"]
    assert page.locator("#kg_custom_context_edit").is_visible()

    page.locator("#kg_custom_context_edit").click()
    assert custom.is_visible()
    labels = custom.locator(".kg-custom-context-rule").all_inner_texts()
    assert "Selection is derived from" in labels
    assert "Derived from selection" in labels
    assert "Derived from from selection" not in labels
    derived_outgoing = custom.locator(
        '.kg-custom-context-rule:has(input[data-relation="DERIVES_FROM"]'
        '[data-direction="outgoing"]) .kg-custom-context-relation'
    )
    assert derived_outgoing.inner_text() == "derived from"
    assert custom.locator(".kg-custom-context-rule").evaluate_all(
        """labels => labels.every(label => {
          const input = label.querySelector('input');
          const relationText = label.querySelector('.kg-custom-context-relation');
          const probe = document.createElement('span');
          probe.style.color = edgeKey[input.dataset.relation].colour;
          return relationText && relationText.style.color === probe.style.color;
        })"""
    )


@pytest.mark.browser
def test_detail_navigation_does_not_change_context_rule(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("3.1")
    page.locator("#kg_context_preset_select").select_option("prerequisites")
    page.locator("#kg_context_depth_select").select_option("two-hops")
    before = page.evaluate("() => kgViewerStateSnapshot().contextRule")

    page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-3-1-derived-from"]'
    ).click()

    assert page.evaluate("() => kgViewerStateSnapshot().contextRule") == before


@pytest.mark.browser
def test_selecting_concept_preserves_folded_representation_and_view_axes(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("3.1")
    browser_graph.open_control_section("kg_modules_section")
    page.locator("#kg_modules_collapse_all").click()
    page.locator("#kg_display_scope_select").select_option("context")
    page.locator("#kg_context_preset_select").select_option("prerequisites")
    page.locator("#kg_context_depth_select").select_option("two-hops")

    browser_graph.click_concept("2.1")

    state = page.evaluate("() => kgViewerStateSnapshot()")
    assert state["selection"] == {"type": "concept", "id": "2.1"}
    assert state["displayScope"] == "context"
    assert state["contextRule"]["preset"] == "prerequisites"
    assert state["contextRule"]["depth"] == "two-hops"
    assert page.evaluate("() => nodes.get('module::test.m02_applications').hidden") is False
    assert page.evaluate("() => nodes.get('2.1').hidden") is True
    assert page.evaluate("() => network.getSelectedNodes()") == [
        "module::test.m02_applications"
    ]
    assert page.locator("#kg_expand_selected_module").is_visible()


@pytest.mark.browser
def test_clear_selection_preserves_context_scope_and_representation(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_modules_section")
    page.locator("#kg_modules_collapse_all").click()
    browser_graph.click_concept("2.1")
    page.locator("#kg_context_preset_select").select_option("uses")
    page.locator("#kg_context_depth_select").select_option("transitive")
    page.locator("#kg_display_scope_select").select_option("context")
    page.locator("#kg_clear_selection").click()

    state = page.evaluate("() => kgViewerStateSnapshot()")
    assert state["selection"] == {"type": "none", "id": None}
    assert state["displayScope"] == "context"
    assert state["contextRule"]["preset"] == "uses"
    assert state["contextRule"]["depth"] == "transitive"
    assert page.evaluate("() => nodes.get('module::test.m02_applications') !== null")


@pytest.mark.browser
def test_edge_inspection_does_not_replace_selection_details(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    edge_id = page.evaluate(
        """() => edges.get().find(edge =>
          !edge.hidden && edge.from === '2.1' && edge.to === '1.1' &&
          edge.relation === 'REQUIRES').id"""
    )

    page.evaluate(
        """edgeId => network.emit('click', {
          nodes: [], edges: [edgeId], pointer: {DOM: {x: 20, y: 20}}
        })""",
        edge_id,
    )

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.evaluate("() => kgViewerStateSnapshot().selection") == {
        "type": "concept",
        "id": "2.1",
    }
    assert page.locator("#kg_inspection_dialog").get_attribute("open") is not None
    assert "Relationship" in page.locator("#kg_inspection_body").inner_text()
