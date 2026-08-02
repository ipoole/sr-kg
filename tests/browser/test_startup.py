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
    assert page.locator("#kg_edge_filters input[data-edge-relation]").count() == 3
    assert not page.locator("#kg_edge_filters_section").evaluate("el => el.open")
    assert not page.locator("#kg_legend_section").evaluate("el => el.open")
    assert not page.locator("#kg_notes_section").evaluate("el => el.open")
    assert not page.locator("#kg_search_section").evaluate("el => el.open")
    assert page.locator("#kg_view_title").inner_text() == "Browser Harness"
    assert page.evaluate("() => nodes.length") == 4
    assert page.evaluate("() => edges.length") == 6
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

    browser_graph.click_concept("2.1")

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert "Layer 2 - Applications" in page.locator("#info_panel").inner_text()
    assert "Beta definition" in page.locator("#info_panel").inner_text()
    assert "Beta explains alpha." in page.locator("#info_panel").inner_text()
    assert page.locator('.kg-concept-item[data-concept-id="2.1"]').evaluate(
        "el => el.classList.contains('active')"
    )
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"


@pytest.mark.browser
def test_legacy_concept_uses_coarse_details_sections(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")

    assert page.locator("#info_panel h3").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    ) == ["Definition", "Explanation"]
    assert page.locator("#info_panel .content-block").count() == 0


@pytest.mark.browser
def test_revised_concept_renders_ordered_content_blocks(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

    assert page.locator("#info_panel .content-block h3").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    ) == ["Definition", "Gamma intuition"]
    assert "Gamma definition" in page.locator("#info_panel").inner_text()
    assert "Gamma intuition body" in page.locator("#info_panel").inner_text()
    assert page.locator("#info_panel .concept-section h3").count() == 0


@pytest.mark.browser
def test_revised_concept_renders_note_block_kinds_folded(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

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
def test_revised_concept_renders_derivation_steps_folded(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

    step = page.locator("#info_panel details.content-block-derivation_step")
    assert step.count() == 1
    assert step.locator("summary").inner_text() == "Gamma algebra step"
    assert not step.locator(".content-block-fold-body").is_visible()

    step.locator("summary").click()

    assert step.locator(".content-block-fold-body").is_visible()
    assert "Gamma derivation-step body" in step.inner_text()


@pytest.mark.browser
def test_revised_concept_renders_sticky_masthead_and_content_toc(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

    masthead = page.locator("#info_panel .concept-sticky-header")
    assert masthead.count() == 1
    assert masthead.evaluate("el => getComputedStyle(el).position") == "sticky"
    assert "2.2 Gamma" in masthead.inner_text()
    assert "Layer 2" not in masthead.inner_text()
    assert "Reading" in masthead.inner_text()
    assert masthead.locator(".concept-reading-mode-select").input_value() == "full"

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
    page.wait_for_function("""() => document.getElementById("info_panel").scrollTop > 0""")
    page.wait_for_timeout(450)

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
def test_concept_masthead_graph_focus_reveals_hidden_graph(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_graph_view_select").select_option("hide")
    assert page.locator("body").evaluate("el => el.classList.contains('kg-graph-hidden')")

    page.locator("#info_panel .concept-graph-focus").click()

    assert not page.locator("body").evaluate("el => el.classList.contains('kg-graph-hidden')")
    assert page.locator("#kg_graph_view_select").input_value() == "all"
    assert page.locator("#info_panel h2").inner_text() == "2.2 Gamma"


@pytest.mark.browser
def test_reading_mode_core_filters_blocks_and_study_questions(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#info_panel .concept-reading-mode-select").select_option("core")

    panel_text = page.locator("#info_panel").inner_text()
    assert "Gamma definition" in panel_text
    assert "Gamma intuition body" in panel_text
    assert "Gamma warning body" not in panel_text
    assert "Gamma derivation-step body" not in panel_text
    assert "Gamma history body" not in panel_text
    assert "Gamma short-answer question?" in panel_text
    assert "Gamma calculation question?" not in panel_text
    assert "Gamma multiple-choice question?" not in panel_text


@pytest.mark.browser
def test_reading_mode_maths_filters_blocks_and_study_questions(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#info_panel .concept-reading-mode-select").select_option("maths")

    toc_titles = page.locator("#info_panel .concept-toc .concept-toc-link").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    )
    assert toc_titles == [
        "Gamma algebra step",
        "Derived from",
        "Where this is used",
        "Study Questions",
    ]
    panel_text = page.locator("#info_panel").inner_text()
    assert "Gamma definition" not in panel_text
    assert "Gamma intuition body" not in panel_text
    step = page.locator("#info_panel details.content-block-derivation_step")
    assert step.locator("summary").inner_text() == "Gamma algebra step"
    step.locator("summary").click()
    assert "Gamma derivation-step body" in step.inner_text()
    assert "Gamma calculation question?" in panel_text
    assert "Gamma short-answer question?" not in panel_text
    assert "Gamma multiple-choice question?" not in panel_text


@pytest.mark.browser
def test_legacy_concept_toc_includes_sections_and_study_questions(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")

    assert page.locator("#info_panel .concept-toc .concept-toc-link").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    ) == ["Definition", "Explanation", "Where this is used", "Study Questions"]


@pytest.mark.browser
def test_study_questions_show_prompts_but_keep_answers_closed(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")

    questions = page.locator("#info_panel details.study-questions")
    assert questions.count() == 1
    assert questions.evaluate("node => node.open")
    assert "Beta question?" in questions.inner_text()
    assert "\\n" not in questions.inner_text()
    assert questions.locator(".study-question .concept-line").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    )[:3] == ["Beta question?", "A. First option", "B. Second option"]

    answer = questions.locator("details.study-answer")
    assert answer.count() == 1
    assert not answer.locator(".study-answer-body").is_visible()

    answer.locator("summary").click()

    assert answer.locator(".study-answer-body").is_visible()
    assert "Beta answer." in answer.inner_text()


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
    assert "The optional body can include" in optional.locator(".optional-detail-body").inner_text()
    optional.locator(".concept-link").click()
    assert page.locator("#kg_concept_preview").is_visible()
    assert "1.1 Alpha" in page.locator("#kg_concept_preview").inner_text()
    assert "Layer 1 - Foundations" in page.locator("#kg_concept_preview").inner_text()
    assert "Alpha definition" in page.locator("#kg_concept_preview").inner_text()
    assert page.locator("#kg_concept_preview .concept-preview-go").inner_text() == "Go to concept"

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
    assert "1.1 Alpha" in preview.inner_text()
    assert "Layer 1 - Foundations" in preview.inner_text()
    assert "Alpha definition" in preview.inner_text()
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
            item.relation === "DEPENDS_ON"
          );
          return edge && edge.color && edge.color.color === "#174ea6" && edge.width >= 4;
        }"""
    )


@pytest.mark.browser
def test_concept_link_preview_does_not_highlight_hidden_graph_target(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#kg_graph_view_select").select_option("hide")
    page.locator("#info_panel details.optional-detail summary").click()
    page.locator("#info_panel .optional-detail-body .concept-link").click()

    assert page.locator("#kg_concept_preview").is_visible()
    assert not page.locator(
        '#kg_node_labels .kg-node-label[data-node-id="1.1"]'
    ).evaluate("el => el.classList.contains('kg-node-label-transient')")


@pytest.mark.browser
def test_edge_click_shows_relationship_detail_panel(browser_graph):
    page = browser_graph.page

    page.evaluate(
        """() => {
          const edge = edges.get().find(item =>
            String(item.from) === "2.1" &&
            String(item.to) === "1.1" &&
            item.relation === "DEPENDS_ON"
          );
          network.emit("click", {
            nodes: [],
            edges: [edge.id],
            pointer: {DOM: {x: 0, y: 0}, canvas: {x: 0, y: 0}}
          });
        }"""
    )

    assert page.locator("#info_panel h2").inner_text() == "Relationship"
    panel_text = page.locator("#info_panel").inner_text()
    assert "2.1 Beta" in panel_text
    assert "1.1 Alpha" in panel_text
    assert "DEPENDS_ON" in panel_text
    assert "Beta depends on alpha" in panel_text


@pytest.mark.browser
def test_concept_details_show_backlinks_grouped_by_relation(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("1.1")

    backlinks = page.locator("#info_panel .concept-backlinks")
    assert backlinks.count() == 1
    assert backlinks.evaluate("el => el.open")
    assert backlinks.locator(".concept-backlink-group-title").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    ) == ["Derived from this", "Requires this", "Related concepts"]

    section_text = backlinks.inner_text()
    assert "2.2 Gamma" in section_text
    assert "Gamma derives from alpha" in section_text
    assert "2.1 Beta" in section_text
    assert "Beta depends on alpha" in section_text
    assert "Bidirectional teaching relation" in section_text


@pytest.mark.browser
def test_concept_details_show_derived_from_links_only(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")

    derived_from = page.locator("#info_panel .concept-derived-from")
    assert derived_from.count() == 1
    assert derived_from.evaluate("el => el.open")
    section_text = derived_from.inner_text()
    assert "1.1 Alpha" in section_text
    assert "Gamma derives from alpha" in section_text
    assert "Delta depends on gamma" not in section_text
    assert "3.1 Delta" not in section_text


@pytest.mark.browser
def test_derived_from_full_tree_expands_only_derives_from_ancestry(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")

    derived_from = page.locator("#info_panel .concept-derived-from")
    assert "2.2 Gamma" in derived_from.inner_text()
    assert "1.1 Alpha" not in derived_from.inner_text()

    derived_from.locator(".concept-derived-from-full-tree").check()

    section_text = page.locator("#info_panel .concept-derived-from").inner_text()
    assert "2.2 Gamma" in section_text
    assert "Delta derives from gamma" in section_text
    assert "1.1 Alpha" in section_text
    assert "Gamma derives from alpha" in section_text
    assert "2.1 Beta" not in section_text


@pytest.mark.browser
def test_derived_from_concept_hover_shows_preview(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator('#info_panel .concept-derived-from .edge-detail-concept[data-edge-concept-id="1.1"]').hover()

    preview = page.locator("#kg_concept_preview")
    assert preview.is_visible()
    assert "1.1 Alpha" in preview.inner_text()
    assert "Alpha definition" in preview.inner_text()
    assert page.locator("#info_panel h2").inner_text() == "2.2 Gamma"


@pytest.mark.browser
def test_backlinks_full_tree_expands_only_derives_from_descendants(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("1.1")

    backlinks = page.locator("#info_panel .concept-backlinks")
    assert "2.2 Gamma" in backlinks.inner_text()
    assert "3.1 Delta" not in backlinks.inner_text()

    backlinks.locator(".concept-backlinks-full-tree").check()

    section_text = page.locator("#info_panel .concept-backlinks").inner_text()
    assert "2.2 Gamma" in section_text
    assert "Gamma derives from alpha" in section_text
    assert "3.1 Delta" in section_text
    assert "Delta derives from gamma" in section_text
    assert "2.1 Beta" in section_text
    assert "Beta depends on alpha" in section_text


@pytest.mark.browser
def test_backlink_concept_hover_shows_preview(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("1.1")
    page.locator('#info_panel .concept-backlinks .edge-detail-concept[data-edge-concept-id="2.2"]').hover()

    preview = page.locator("#kg_concept_preview")
    assert preview.is_visible()
    assert "2.2 Gamma" in preview.inner_text()
    assert "Gamma definition" in preview.inner_text()
    assert page.locator("#info_panel h2").inner_text() == "1.1 Alpha"


@pytest.mark.browser
def test_optional_details_do_not_create_whitespace_only_lines(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")

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
def test_edge_filter_hides_and_restores_relation_edges(browser_graph):
    page = browser_graph.page

    browser_graph.open_edge_filters()
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
def test_focussed_mode_hides_non_neighbourhood_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#kg_graph_view_select").select_option("focused")

    assert page.locator("#kg_graph_view_select").input_value() == "focused"
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

    browser_graph.open_edge_filters()
    page.locator('input[data-edge-relation="DEPENDS_ON"]').uncheck()
    assert page.evaluate(
        """() => edges.get().filter(edge => !edge.hidden).every(edge => edge.relation !== "DEPENDS_ON")"""
    )


@pytest.mark.browser
def test_toc_sections_drive_focussed_derivation_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_graph_view_select").select_option("focused")
    page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-3-1-derived-from"]'
    ).click()

    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": True,
        "2.1": True,
        "2.2": False,
        "3.1": False,
    }

    page.locator("#info_panel .concept-derived-from-full-tree").check()

    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": True,
        "2.2": False,
        "3.1": False,
    }


@pytest.mark.browser
def test_hovering_section_context_edge_does_not_move_or_zoom_graph(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_graph_view_select").select_option("focused")
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
def test_toc_sections_drive_focussed_where_used_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("1.1")
    page.locator("#kg_graph_view_select").select_option("focused")
    page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-1-1-where-this-is-used"]'
    ).click()

    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": True,
        "2.2": False,
        "3.1": True,
    }

    page.locator("#info_panel .concept-backlinks-full-tree").check()

    assert page.evaluate(
        """() => Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]))"""
    ) == {
        "1.1": False,
        "2.1": True,
        "2.2": False,
        "3.1": False,
    }


@pytest.mark.browser
def test_graph_view_selector_hides_derivation_trace_mode(browser_graph):
    page = browser_graph.page

    assert page.locator('#kg_graph_view_select option[value="derivation-trace"]').count() == 0
    assert "Derivation trace" not in page.locator("#kg_graph_view_select").inner_text()


@pytest.mark.browser
def test_graph_view_selector_hides_graph_and_supports_focussed_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_graph_view_select").select_option("hide")

    assert page.locator("#kg_graph_view_select").input_value() == "hide"
    assert page.locator("body").evaluate("el => el.classList.contains('kg-graph-hidden')")
    assert page.evaluate("""() => nodes.get().every(node => node.hidden)""")
    assert page.evaluate("""() => edges.get().every(edge => edge.hidden)""")
    assert "Delta definition" in page.locator("#info_panel").inner_text()

    browser_graph.click_concept("2.1")
    assert page.locator("#kg_graph_view_select").input_value() == "hide"
    assert "Beta definition" in page.locator("#info_panel").inner_text()
    assert page.evaluate("""() => nodes.get().every(node => node.hidden)""")

    page.locator("#kg_graph_view_select").select_option("focused")
    assert page.locator("#kg_graph_view_select").input_value() == "focused"
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

    splash_text = page.locator("#kg_splash_dialog").inner_text()
    assert "Knowledge graph browser" in splash_text
    assert "deeper block-based content for all layers" in splash_text
    assert "Preview linked concepts" in splash_text
    assert "Study questions are visible with answers folded closed" in splash_text
    assert page.locator("#kg_splash_dialog .kg-new-badge").count() >= 3

    page.locator("#kg_splash_dismiss").click()
    assert page.evaluate("""() => localStorage.getItem("srkg.splash.dismissed.v1")""") == "true"
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_controls", state="attached")
    assert page.locator("#kg_splash_dialog[open]").count() == 0

    page.locator("#kg_features_button").click()
    assert page.locator("#kg_splash_dialog[open]").count() == 1
