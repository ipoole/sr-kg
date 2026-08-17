import pytest


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
    assert page.locator("#kg_focus_lens").count() == 1
    assert page.locator("#kg_node_labels .kg-node-label").count() == 4
    assert page.locator("#kg_concept_list .kg-concept-item").count() == 4
    assert page.locator("#kg_edge_filters_section").count() == 0
    assert page.locator("#kg_edge_filters").count() == 0
    assert not page.locator("#kg_legend_section").evaluate("el => el.open")
    assert not page.locator("#kg_notes_section").evaluate("el => el.open")
    assert not page.locator("#kg_search_section").evaluate("el => el.open")
    assert page.locator("#kg_view_title").inner_text() == "Browser Harness"
    assert page.evaluate("() => nodes.length") == 4
    assert page.evaluate("() => edges.length") == 6
    assert page.locator("#kg_graph_view_select").input_value() == "all"
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
    assert "Layer 2 - Applications" in page.locator("#info_panel").inner_text()
    assert "Beta definition" in page.locator("#info_panel").inner_text()
    assert "Beta explains alpha." in page.locator("#info_panel").inner_text()
    assert page.locator('.kg-concept-item[data-concept-id="2.1"]').evaluate(
        "el => el.classList.contains('active')"
    )
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
def test_detail_section_graph_policy_marks_toc_sections(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

    assert page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-2-2-definition"]'
    ).evaluate(
        """el => ({
          role: el.getAttribute("data-section-role"),
          context: el.getAttribute("data-graph-context"),
          label: el.getAttribute("data-lens-label")
        })"""
    ) == {
        "role": "content",
        "context": "neighbourhood",
        "label": "Neighbourhood",
    }
    assert page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-2-2-derived-from"]'
    ).evaluate(
        """el => ({
          role: el.getAttribute("data-section-role"),
          context: el.getAttribute("data-graph-context"),
          label: el.getAttribute("data-lens-label")
        })"""
    ) == {
        "role": "derived-from",
        "context": "derived-from",
        "label": "Derivation step",
    }
    assert page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-2-2-where-this-is-used"]'
    ).evaluate(
        """el => ({
          role: el.getAttribute("data-section-role"),
          context: el.getAttribute("data-graph-context"),
          label: el.getAttribute("data-lens-label")
        })"""
    ) == {
        "role": "where-used",
        "context": "where-used",
        "label": "Immediate usage",
    }
    assert page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-2-2-study-questions"]'
    ).evaluate(
        """el => ({
          role: el.getAttribute("data-section-role"),
          context: el.getAttribute("data-graph-context"),
          label: el.getAttribute("data-lens-label")
        })"""
    ) == {
        "role": "study-questions",
        "context": "neighbourhood",
        "label": "Neighbourhood",
    }


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
        browser_graph.output_path.as_uri() + "?phone-lens#concept-2.2",
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

    warning_link.click()

    assert warning_link.evaluate("el => el.classList.contains('active')")
    assert warning_link.evaluate("el => el.getAttribute('aria-current')") == "true"
    assert not graphic_link.evaluate("el => el.classList.contains('active')")


@pytest.mark.browser
def test_scrolling_details_updates_focussed_graph_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_graph_view_select").select_option("focused")

    page.locator("#info_panel").evaluate(
        """panel => {
          panel.style.height = "170px";
          panel.scrollTop = 0;
        }"""
    )
    page.wait_for_timeout(400)
    page.evaluate(
        """() => {
          const panel = document.getElementById("info_panel");
          const target = document.getElementById("kg-toc-3-1-derived-from");
          panel.scrollTop = target.offsetTop - 40;
          panel.dispatchEvent(new Event("scroll"));
        }"""
    )

    page.wait_for_function(
        """() => {
          const hidden = Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]));
          const link = document.querySelector(
            '#info_panel .concept-toc-link[data-toc-target="kg-toc-3-1-derived-from"]'
          );
          return hidden["1.1"] === true &&
            hidden["2.1"] === true &&
            hidden["2.2"] === false &&
            hidden["3.1"] === false &&
            link &&
            link.classList.contains("active");
        }"""
    )


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
def test_focus_lens_toggle_hides_and_shows_focus_lens(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    lens = page.locator("#kg_focus_lens")
    toggle = page.locator("#kg_focus_lens_toggle")

    assert not lens.is_visible()
    assert toggle.get_attribute("aria-pressed") == "false"
    assert toggle.inner_text() == "Show lens"

    toggle.click()

    assert lens.is_visible()
    assert toggle.get_attribute("aria-pressed") == "true"
    assert toggle.inner_text() == "Hide lens"

    toggle.click()

    assert not lens.is_visible()
    assert toggle.get_attribute("aria-pressed") == "false"
    assert toggle.inner_text() == "Show lens"


@pytest.mark.browser
def test_phone_starts_with_focus_lens_hidden(browser_graph):
    page = browser_graph.page

    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(
        browser_graph.output_path.as_uri() + "?phone-lens#concept-2.2",
        wait_until="domcontentloaded",
    )
    page.wait_for_selector("#kg_workspace")

    lens = page.locator("#kg_focus_lens")
    toggle = page.locator("#kg_focus_lens_toggle")

    assert page.locator("body").evaluate("el => el.classList.contains('kg-focus-lens-hidden')")
    assert not lens.is_visible()
    assert toggle.get_attribute("aria-pressed") == "false"
    assert toggle.inner_text() == "Show lens"

    toggle.click()

    assert not page.locator("body").evaluate("el => el.classList.contains('kg-focus-lens-hidden')")
    assert lens.is_visible()
    assert toggle.get_attribute("aria-pressed") == "true"
    assert toggle.inner_text() == "Hide lens"


@pytest.mark.browser
def test_phone_header_uses_single_row_compact_controls(browser_graph):
    page = browser_graph.page

    page.set_viewport_size({"width": 390, "height": 800})
    page.goto(browser_graph.output_path.as_uri() + "?phone-header", wait_until="domcontentloaded")
    page.wait_for_selector("#kg_workspace")

    header = page.locator("#kg_app_header").bounding_box()
    workspace = page.locator("#kg_workspace").bounding_box()
    assert header["height"] <= 58
    assert abs(workspace["y"] - header["height"]) <= 1
    assert not page.locator(".kg-shell-graph-control label").is_visible()
    assert not page.locator(".kg-shell-details-control label").is_visible()
    assert page.locator("#kg_graph_view_select option:checked").inner_text() == "Full graph"
    assert page.locator("#kg_details_view_select option:checked").inner_text() == "Full details"

    metrics = page.evaluate(
        """() => {
          const ids = [
            "kg_controls_toggle",
            "kg_graph_view_select",
            "kg_focus_lens_toggle",
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


@pytest.mark.browser
def test_default_startup_has_no_selected_concept(repo_browser_graph):
    page = repo_browser_graph.page

    page.wait_for_function("""() => window.location.hash === ''""")

    assert "Select a concept" in page.locator("#info_panel").inner_text()
    assert page.locator(".kg-concept-item.active").count() == 0


@pytest.mark.browser
def test_explicit_startup_hash_overrides_default_concept(repo_browser_graph):
    page = repo_browser_graph.page

    page.goto(
        repo_browser_graph.output_path.as_uri() + "#concept-sr.electric_field",
        wait_until="domcontentloaded",
    )
    page.wait_for_function("""() => window.location.hash === '#concept-sr.electric_field'""")

    assert page.locator("#info_panel h2").inner_text() == "7.3 Electric field"
    assert page.locator("#kg_view_title").inner_text() == "7.3 Electric field"


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
    page.locator("#kg_graph_view_select").select_option("hide")

    assert page.locator("body").evaluate("el => el.classList.contains('kg-graph-hidden')")
    details_only = page.locator("#kg_details_pane").bounding_box()
    assert details_only["width"] > metrics["shell"]["width"] * 0.95


@pytest.mark.browser
def test_details_hide_does_not_blank_workspace_when_graph_is_hidden(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_graph_view_select").select_option("hide")
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

    panel_text = page.locator("#info_panel").inner_text()
    assert "Gamma definition" in panel_text
    assert "Gamma intuition body" in panel_text
    assert "Gamma warning body" not in panel_text
    assert "Gamma derivation-step body" not in panel_text
    assert "Gamma history body" not in panel_text
    questions = page.locator("#info_panel details.study-questions")
    assert not questions.evaluate("node => node.open")
    questions.locator(":scope > summary").click()
    questions_text = questions.inner_text()
    assert "Gamma short-answer question?" in questions_text
    assert "Gamma calculation question?" not in questions_text
    assert "Gamma multiple-choice question?" not in questions_text


@pytest.mark.browser
def test_reading_mode_maths_filters_blocks_and_study_questions(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_details_view_select").select_option("maths")

    toc_titles = page.locator("#info_panel .concept-toc .concept-toc-link").evaluate_all(
        "nodes => nodes.map(node => node.textContent)"
    )
    assert toc_titles == [
        "Graphic",
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
    questions = page.locator("#info_panel details.study-questions")
    assert not questions.evaluate("node => node.open")
    questions.locator(":scope > summary").click()
    questions_text = questions.inner_text()
    assert "Gamma calculation question?" in questions_text
    assert "Gamma short-answer question?" not in questions_text
    assert "Gamma multiple-choice question?" not in questions_text


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
    assert not questions.evaluate("node => node.open")
    assert not questions.locator(".study-question").is_visible()

    questions.locator(":scope > summary").click()

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
def test_practice_reading_mode_opens_study_questions_by_default(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.2")
    page.locator("#kg_details_view_select").select_option("practice")

    questions = page.locator("#info_panel details.study-questions")
    assert questions.count() == 1
    assert questions.evaluate("node => node.open")
    assert questions.locator(".study-question").first.is_visible()
    assert "Gamma short-answer question?" in questions.inner_text()


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
def test_edge_click_shows_relationship_detail_panel(shared_browser_graph):
    page = shared_browser_graph.page

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
    assert page.locator("#info_panel .edge-detail-statement").get_attribute(
        "aria-label"
    ) == "2.1 Beta depends on 1.1 Alpha."
    assert "Depends on" in panel_text
    assert "DEPENDS_ON" in panel_text
    assert "Beta depends on alpha" in panel_text


@pytest.mark.browser
def test_constructed_from_edge_click_shows_readable_relationship_sentence(repo_browser_graph):
    page = repo_browser_graph.page

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

    assert page.locator("#info_panel h2").inner_text() == "Relationship"
    panel_text = page.locator("#info_panel").inner_text()
    assert page.locator("#info_panel .edge-detail-statement").get_attribute(
        "aria-label"
    ) == "7.2 Field tensor \\(F_{\\mu\\nu}\\) is constructed from 7.1 Vector potential \\(A_\\mu\\)."
    assert "Constructed from" in panel_text
    assert "CONSTRUCTED_FROM" in panel_text


@pytest.mark.browser
def test_concept_details_show_backlinks_grouped_by_relation(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("1.1")

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
def test_concept_details_show_derived_from_links_only(shared_browser_graph):
    page = shared_browser_graph.page

    shared_browser_graph.click_concept("2.2")

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

    assert page.locator("#kg_focus_lens").get_attribute("data-background") == "hidden"


@pytest.mark.browser
def test_focus_lens_display_tracks_active_detail_section(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_graph_view_select").select_option("focused")

    lens = page.locator("#kg_focus_lens")
    assert lens.get_attribute("data-selected-concept") == "3.1"
    assert lens.get_attribute("data-lens-context") == "neighbourhood"
    assert lens.get_attribute("data-lens-label") == "Neighbourhood"
    assert lens.get_attribute("data-background") == "hidden"
    assert "Delta" in page.locator("#kg_focus_lens .kg-focus-lens-center").inner_text()
    assert page.locator(
        '#kg_focus_lens .kg-focus-lens-incoming '
        '.kg-focus-lens-relation[data-relation="DEPENDS_ON"][data-direction="incoming"]'
    ).get_attribute("data-state") == "immediate"
    assert page.locator(
        '#kg_focus_lens .kg-focus-lens-outgoing '
        '.kg-focus-lens-relation[data-relation="DEPENDS_ON"][data-direction="outgoing"]'
    ).get_attribute("data-state") == "immediate"

    page.locator(
        '#info_panel .concept-toc-link[data-toc-target="kg-toc-3-1-derived-from"]'
    ).click()

    derived_incoming = page.locator(
        '#kg_focus_lens .kg-focus-lens-incoming '
        '.kg-focus-lens-relation[data-relation="DERIVES_FROM"][data-direction="incoming"]'
    )
    derived_outgoing = page.locator(
        '#kg_focus_lens .kg-focus-lens-outgoing '
        '.kg-focus-lens-relation[data-relation="DERIVES_FROM"][data-direction="outgoing"]'
    )
    related = page.locator(
        '#kg_focus_lens .kg-focus-lens-undirected '
        '.kg-focus-lens-relation[data-relation="RELATED"][data-direction="undirected"]'
    )
    assert lens.get_attribute("data-lens-context") == "derived-from"
    assert lens.get_attribute("data-lens-label") == "Derivation step"
    assert derived_incoming.get_attribute("data-state") == "none"
    assert derived_outgoing.get_attribute("data-state") == "immediate"
    assert related.get_attribute("data-state") == "none"

    page.locator("#info_panel .concept-derived-from-full-tree").check()

    assert lens.get_attribute("data-lens-label") == "Derivation tree"
    assert derived_outgoing.get_attribute("data-state") == "tree"


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
def test_opening_derived_from_section_drives_focussed_derivation_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("3.1")
    page.locator("#kg_graph_view_select").select_option("focused")

    derived_from = page.locator("#info_panel .concept-derived-from")
    derived_from.locator("summary").click()
    assert not derived_from.evaluate("el => el.open")

    derived_from.locator("summary").click()

    page.wait_for_function(
        """() => {
          const hidden = Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]));
          return hidden["1.1"] === true &&
            hidden["2.1"] === true &&
            hidden["2.2"] === false &&
            hidden["3.1"] === false;
        }"""
    )


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
def test_opening_where_used_section_drives_focussed_descendant_context(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("1.1")
    page.locator("#kg_graph_view_select").select_option("focused")

    backlinks = page.locator("#info_panel .concept-backlinks")
    backlinks.locator("summary").click()
    assert not backlinks.evaluate("el => el.open")

    backlinks.locator("summary").click()

    page.wait_for_function(
        """() => {
          const hidden = Object.fromEntries(nodes.get().map(node => [node.id, Boolean(node.hidden)]));
          return hidden["1.1"] === false &&
            hidden["2.1"] === true &&
            hidden["2.2"] === false &&
            hidden["3.1"] === true;
        }"""
    )


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
    assert "two linked views" in splash_text
    assert "focus lens summarises how the graph focus is being chosen" in splash_text
    assert "Drag the divider" in splash_text
    assert "Coming soon: General Relativity!" in splash_text
    assert page.locator("#kg_splash_dialog .kg-new-badge").count() == 0

    page.locator("#kg_splash_dismiss").click()
    assert page.evaluate("""() => localStorage.getItem("srkg.splash.dismissed.v1")""") == "true"
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_controls", state="attached")
    assert page.locator("#kg_splash_dialog[open]").count() == 0

    page.locator("#kg_features_button").click()
    assert page.locator("#kg_splash_dialog[open]").count() == 1
