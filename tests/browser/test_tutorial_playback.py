import pytest


def _tutorial_state(page):
    return page.evaluate("""() => ({
      playback: window.kgTutorialPlaybackSnapshot(),
      presentation: window.kgCaptureTutorialPresentation()
    })""")


def _open_tutorial(graph, tutorial_id="viewer-tour"):
    page = graph.page
    if page.locator("#kg_controls").evaluate("el => el.classList.contains('kg-hidden')"):
        page.locator("#kg_controls_toggle").click()
    graph.open_control_section("kg_tutorials_section")
    page.locator(f'[data-tutorial-id="{tutorial_id}"]').click()
    return page


def _assert_block_pointer_matches(page, expected_target, index):
    if not expected_target.startswith("details:block:"):
        return
    block_id = expected_target.removeprefix("details:block:")
    geometry = page.evaluate(
        """blockId => {
          const block = document.querySelector(
            '#info_panel [data-content-block-id="' + CSS.escape(blockId) + '"]'
          );
          const rect = block.getBoundingClientRect();
          return {block: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                  halo: kgTutorialPointerSnapshot().halo};
        }""",
        block_id,
    )
    for key in ["x", "y", "width", "height"]:
        assert geometry["halo"][key] == pytest.approx(
            geometry["block"][key], abs=2
        ), (index, expected_target, key, geometry)


def _assert_elements_do_not_overlap(page, first_selector, second_selector):
    overlap = page.evaluate(
        """selectors => {
          const first = document.querySelector(selectors[0]).getBoundingClientRect();
          const second = document.querySelector(selectors[1]).getBoundingClientRect();
          return Math.max(0, Math.min(first.right, second.right) - Math.max(first.left, second.left)) *
            Math.max(0, Math.min(first.bottom, second.bottom) - Math.max(first.top, second.top));
        }""",
        [first_selector, second_selector],
    )
    assert overlap == 0


def test_tutorial_introduction_does_not_change_the_view(browser_graph):
    page = browser_graph.page
    baseline = page.evaluate("window.kgCaptureTutorialPresentation()")

    _open_tutorial(browser_graph)

    assert page.locator("#kg_tutorial_intro_title").inner_text() == "Using PhysicsKG"
    assert "selection" in page.locator("#kg_tutorial_intro_summary").inner_text()
    assert page.locator("#kg_tutorial_start").is_visible()
    assert "guided tour" in page.locator("#kg_tutorial_guidance").inner_text().lower()
    assert "operate the viewer" in page.locator("#kg_tutorial_guidance").inner_text().lower()
    assert "press start, then next step" in page.locator(
        "#kg_tutorial_guidance"
    ).inner_text().lower()
    after = page.evaluate("window.kgCaptureTutorialPresentation()")
    assert after["selection"] == baseline["selection"]
    assert after["contextRule"] == baseline["contextRule"]
    assert after["displayScope"] == baseline["displayScope"]
    assert after["moduleRepresentation"] == baseline["moduleRepresentation"]


def test_quick_start_can_launch_the_guided_tutorial(browser_graph):
    page = browser_graph.page
    page.evaluate("window.kgShowSplash()")

    page.locator("#kg_splash_start_tutorial").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )

    assert page.locator("#kg_splash_dialog").evaluate("dialog => !dialog.open")
    assert page.evaluate("kgTutorialPlaybackSnapshot().tutorialId") == "viewer-tour"
    assert page.locator("#kg_tutorial_first_step_guidance").is_visible()


def test_tutorial_query_parameter_starts_playback_directly(browser_graph):
    page = browser_graph.page
    page.evaluate("localStorage.removeItem('srkg.splash.dismissed.v1')")
    page.goto(
        browser_graph.output_path.as_uri() + "?tutorial=viewer-tour",
        wait_until="domcontentloaded",
    )
    page.wait_for_function(
        "() => typeof kgTutorialPlaybackSnapshot === 'function' && "
        "!kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )

    assert page.locator("#kg_splash_dialog").evaluate("dialog => !dialog.open")
    assert page.evaluate("new URL(location.href).searchParams.get('tutorial')") == "viewer-tour"
    assert page.locator("#kg_tutorial_first_step_guidance").is_visible()


def test_named_tutorial_exposes_a_direct_launch_link(repo_browser_graph):
    page = _open_tutorial(repo_browser_graph, "rest-energy-to-sr-foundations")
    url = page.locator("#kg_tutorial_launch_link").get_attribute("href")
    assert "tutorial=rest-energy-to-sr-foundations" in url
    assert "#" not in url
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_function(
        "() => typeof kgTutorialPlaybackSnapshot === 'function' && "
        "!kgTutorialPlaybackSnapshot().transitioning && kgTutorialPlaybackSnapshot().stepIndex === 0",
        timeout=30000,
    )
    assert page.evaluate("kgTutorialPlaybackSnapshot().tutorialId") == "rest-energy-to-sr-foundations"


def test_phone_expanded_tutorial_module_stays_above_narration(mobile_repo_browser_graph):
    page = _open_tutorial(mobile_repo_browser_graph, "using-physicskg")
    reveal_index = page.evaluate("""() => tutorialData.find(t => t.tutorial_id === 'using-physicskg')
      .steps.findIndex(s => s.step_id === 'reveal-the-concepts')""")
    page.locator("#kg_tutorial_start").click()
    for index in range(reveal_index + 1):
        page.wait_for_function(
            "index => !kgTutorialPlaybackSnapshot().transitioning && kgTutorialPlaybackSnapshot().stepIndex === index",
            arg=index,
        )
        if index < reveal_index:
            page.locator("#kg_tutorial_next").click()
    page.wait_for_function("""() => {
      const bounds = kgModuleFootprint('sr.relativistic_mechanics');
      const canvas = document.querySelector('#mynetwork canvas').getBoundingClientRect();
      const bottom = network.canvasToDOM({x: bounds.x, y: bounds.bottom}).y + canvas.top;
      const top = network.canvasToDOM({x: bounds.x, y: bounds.top}).y + canvas.top;
      const card = document.querySelector('#kg_tutorial_narration').getBoundingClientRect();
      const controls = document.querySelector('#kg_graph_context_panel').getBoundingClientRect();
      return bottom <= card.top && top >= controls.bottom;
    }""")


def test_phone_landscape_requests_portrait(mobile_repo_browser_graph):
    page = mobile_repo_browser_graph.page
    page.emulate_media(media="screen")
    page.set_viewport_size({"width": 844, "height": 390})
    assert page.locator("#kg_portrait_notice").is_visible()
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.locator("#kg_portrait_notice").is_hidden()


def test_tutorial_next_back_and_exit_restore_the_baseline(browser_graph):
    page = browser_graph.page
    page.evaluate("""async () => {
      await window.kgExecuteViewerCommand({command: 'select', target: 'concept:1.1'});
      await window.kgExecuteViewerCommand({
        command: 'set-context', preset: 'prerequisites', depth: 'one-hop'
      });
    }""")
    baseline = page.evaluate("window.kgCaptureTutorialPresentation()")
    _open_tutorial(browser_graph)

    page.locator("#kg_tutorial_start").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )
    state = _tutorial_state(page)
    assert state["playback"]["active"] is True
    assert state["playback"]["stepIndex"] == 0
    assert state["presentation"]["selection"] == {"type": "concept", "id": "2.1"}
    assert page.locator("#kg_tutorial_progress").inner_text() == "1 / 6"
    assert page.locator("#kg_tutorial_next").inner_text() == "Next step"
    assert page.locator("body").evaluate("el => el.classList.contains('kg-tutorial-active')")
    assert page.locator("#kg_app_header").evaluate("el => el.inert")
    pointer = page.evaluate("window.kgTutorialPointerSnapshot()")
    assert pointer["visible"] is True
    assert pointer["target"] == "graph:concept:2.1"
    assert "Beta" in pointer["label"]

    page.locator("#kg_tutorial_next").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 1"
    )
    state = _tutorial_state(page)
    assert state["presentation"]["contextRule"]["preset"] == "uses"
    assert state["presentation"]["contextRule"]["depth"] == "two-hops"
    pointer = page.evaluate("window.kgTutorialPointerSnapshot()")
    assert pointer["target"] == "control:context"
    context_box = page.locator("#kg_context_preset_select").bounding_box()
    assert context_box is not None
    assert context_box["x"] <= pointer["x"] <= context_box["x"] + context_box["width"]
    assert context_box["y"] <= pointer["y"] <= context_box["y"] + context_box["height"]

    page.locator("#kg_tutorial_next").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 2"
    )
    assert _tutorial_state(page)["presentation"]["displayScope"] == "context"

    page.locator("#kg_tutorial_back").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 1"
    )
    state = _tutorial_state(page)
    assert state["presentation"]["displayScope"] == baseline["displayScope"]
    assert state["presentation"]["selection"] == {"type": "concept", "id": "2.1"}
    assert state["presentation"]["contextRule"]["preset"] == "uses"

    page.locator("#kg_tutorial_exit").click()
    page.wait_for_function("() => !kgTutorialPlaybackSnapshot().active")
    restored = page.evaluate("window.kgCaptureTutorialPresentation()")
    for key in [
        "selection", "contextRule", "displayScope", "moduleRepresentation",
        "workspaceSplitPercent", "search", "url", "historyState",
    ]:
        assert restored[key] == baseline[key]
    assert page.locator("#kg_tutorial_narration").is_hidden()
    assert page.locator("#kg_tutorial_pointer").is_hidden()
    assert not page.locator("body").evaluate("el => el.classList.contains('kg-tutorial-active')")
    assert not page.locator("#kg_app_header").evaluate("el => el.inert")


def test_tutorial_ignores_rapid_next_presses(browser_graph):
    page = _open_tutorial(browser_graph)
    page.locator("#kg_tutorial_start").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )

    page.locator("#kg_tutorial_next").evaluate("button => { button.click(); button.click(); }")
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 1"
    )

    assert page.locator("#kg_tutorial_progress").inner_text() == "2 / 6"
    assert page.locator("#kg_tutorial_step_title").inner_text() == "Choose a Context"


def test_tutorial_hides_the_previous_pointer_during_step_preparation(browser_graph):
    page = _open_tutorial(browser_graph)
    page.locator("#kg_tutorial_start").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )
    assert page.evaluate("kgTutorialPointerSnapshot().visible") is True

    page.locator("#kg_tutorial_next").click()
    page.wait_for_function("() => kgTutorialPlaybackSnapshot().transitioning")
    assert page.evaluate("kgTutorialPointerSnapshot().visible") is False

    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 1"
    )
    assert page.evaluate("kgTutorialPointerSnapshot().target") == "control:context"


def test_completed_fit_pointer_does_not_linger_over_fit_plus(repo_browser_graph):
    page = _open_tutorial(repo_browser_graph, "rest-energy-to-sr-foundations")
    frame_index = page.evaluate("""() => tutorialData
      .find(t => t.tutorial_id === 'rest-energy-to-sr-foundations')
      .steps.findIndex(s => s.step_id === 'expose-the-foundations')""")
    page.locator("#kg_tutorial_start").click()
    page.wait_for_function("() => !kgTutorialPlaybackSnapshot().transitioning")
    page.locator("#kg_tutorial_next").click()
    page.wait_for_function(
        "() => kgTutorialPointerSnapshot().target === 'control:expand-context'",
        timeout=30000,
    )
    assert page.evaluate("kgTutorialPlaybackSnapshot().stepIndex") == 1
    assert page.locator("#kg_tutorial_next").is_disabled()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && kgTutorialPlaybackSnapshot().stepIndex === 1",
        timeout=30000,
    )
    for step_index in range(2, frame_index + 1):
        page.locator("#kg_tutorial_next").click()
        page.wait_for_function(
            "index => !kgTutorialPlaybackSnapshot().transitioning && "
            "kgTutorialPlaybackSnapshot().stepIndex === index",
            arg=step_index,
        )

    pointer = page.evaluate("kgTutorialPointerSnapshot()")
    assert pointer["target"] == "control:fit"
    assert pointer["visible"] is False
    assert page.evaluate("kgViewerStateSnapshot().selection.id") == (
        "sr.mass_energy_equivalence"
    )

    page.locator("#kg_tutorial_next").click()
    page.wait_for_function(
        "index => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === index",
        arg=frame_index + 1,
    )
    pointer = page.evaluate("kgTutorialPointerSnapshot()")
    assert pointer["target"] == "graph:concept:sr.momentum_four_vector"
    assert pointer["visible"] is True
    assert page.evaluate("kgViewerStateSnapshot().selection.id") == "sr.momentum_four_vector"


def test_tutorial_pointer_halo_tracks_a_resolved_target(browser_graph):
    page = _open_tutorial(browser_graph)
    page.locator("#kg_tutorial_start").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )

    pointer = page.evaluate("window.kgTutorialPointerSnapshot()")
    assert pointer["visible"] is True
    assert pointer["halo"]["width"] > 0
    assert pointer["halo"]["height"] > 0
    assert page.locator("#kg_tutorial_target_description").inner_text().startswith("Target:")

    page.evaluate("network.moveTo({scale: network.getScale() * 1.1, animation: false})")
    page.wait_for_timeout(50)
    moved = page.evaluate("window.kgTutorialPointerSnapshot()")
    assert moved["target"] == pointer["target"]
    assert moved["visible"] is True


def test_guided_playback_blocks_viewer_interaction_centrally(browser_graph):
    page = _open_tutorial(browser_graph)
    page.locator("#kg_tutorial_start").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )
    before = page.evaluate("window.kgCaptureTutorialPresentation()")

    page.locator(".kg-module-corner-control:visible").first.click(force=True)
    page.locator("#kg_view_select").click(force=True)

    after = page.evaluate("window.kgCaptureTutorialPresentation()")
    assert after["selection"] == before["selection"]
    assert after["moduleRepresentation"] == before["moduleRepresentation"]
    assert page.locator("#kg_view_select").evaluate(
        "el => getComputedStyle(el).cursor"
    ) == "not-allowed"
    assert page.locator("#kg_tutorial_next").evaluate(
        "el => getComputedStyle(el).cursor"
    ) == "pointer"


@pytest.mark.parametrize("viewport", [(1280, 900), (390, 844)])
def test_explore_here_releases_interaction_and_resume_restores_the_step(browser_graph, viewport):
    browser_graph.page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    page = _open_tutorial(browser_graph)
    workspace_bottom = page.locator("#kg_workspace").bounding_box()["y"] + page.locator("#kg_workspace").bounding_box()["height"]
    page.locator("#kg_tutorial_start").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )
    checkpoint = page.evaluate("window.kgCaptureTutorialPresentation()")
    pointer_target = page.evaluate("window.kgTutorialPointerSnapshot().target")

    page.locator("#kg_tutorial_explore").click()
    assert page.evaluate("kgTutorialPlaybackSnapshot().exploring") is True
    assert page.locator("#kg_tutorial_explore").is_visible()
    for selector in ["#kg_tutorial_commentary", "#kg_tutorial_back", "#kg_tutorial_next", "#kg_tutorial_exit"]:
        assert page.locator(selector).is_hidden()
    assert not page.locator("body").evaluate("el => el.classList.contains('kg-tutorial-phone-docked')")
    page.wait_for_function("bottom => Math.abs(document.querySelector('#kg_workspace').getBoundingClientRect().bottom - bottom) < 2", arg=workspace_bottom)
    assert not page.locator("#kg_app_header").evaluate("el => el.inert")
    assert page.locator("#kg_tutorial_pointer").is_hidden()

    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "select", target: "concept:1.1"}, {origin: "user"}
        )"""
    )
    assert page.evaluate("kgViewerStateSnapshot().selection.id") == "1.1"

    page.locator("#kg_tutorial_explore").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "!kgTutorialPlaybackSnapshot().exploring"
    )
    restored = page.evaluate("window.kgCaptureTutorialPresentation()")
    assert restored["selection"] == checkpoint["selection"]
    assert restored["contextRule"] == checkpoint["contextRule"]
    assert restored["displayScope"] == checkpoint["displayScope"]
    assert page.evaluate("window.kgTutorialPointerSnapshot().target") == pointer_target
    assert page.locator("#kg_app_header").evaluate("el => el.inert")


def test_details_step_spotlights_the_whole_authored_block(browser_graph):
    page = _open_tutorial(browser_graph)
    page.locator("#kg_tutorial_start").click()
    for step_index in range(1, 6):
        page.locator("#kg_tutorial_next").click()
        page.wait_for_function(
            "index => !kgTutorialPlaybackSnapshot().transitioning && "
            "kgTutorialPlaybackSnapshot().stepIndex === index",
            arg=step_index,
        )

    block = page.locator('[data-content-block-id="1.1.definition"]')
    assert block.evaluate("el => el.classList.contains('kg-tutorial-block-spotlight')")
    assert page.locator(".kg-tutorial-block-spotlight").count() == 1
    page.wait_for_function("() => Number(getComputedStyle(document.querySelector('#kg_tutorial_pointer')).opacity) <= 0.15")

    page.locator("#kg_tutorial_explore").click()
    assert page.locator(".kg-tutorial-block-spotlight").count() == 0


def test_tutorial_card_remains_operable_above_mobile_search(browser_graph):
    page = browser_graph.page
    page.set_viewport_size({"width": 390, "height": 844})
    _open_tutorial(browser_graph)
    page.locator("#kg_tutorial_start").click()

    for index in range(4):
        page.wait_for_function(
            "index => !kgTutorialPlaybackSnapshot().transitioning && "
            "kgTutorialPlaybackSnapshot().stepIndex === index",
            arg=index,
        )
        if index < 3:
            page.locator("#kg_tutorial_next").click()

    assert page.locator("#kg_search_section").evaluate("el => el.open")
    next_button = page.locator("#kg_tutorial_next")
    box = next_button.bounding_box()
    assert box is not None
    receiving_element = page.evaluate(
        """point => {
          const element = document.elementFromPoint(point.x, point.y);
          return element && element.closest('#kg_tutorial_next')
            ? 'tutorial-next'
            : element && (element.id || element.className || element.tagName);
        }""",
        {"x": box["x"] + box["width"] / 2, "y": box["y"] + box["height"] / 2},
    )
    assert receiving_element == "tutorial-next"
    next_button.click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 4"
    )






def test_revised_physics_equations_render_with_real_mathjax(repo_browser_graph, repo_browser_output):
    page = repo_browser_graph.page
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(repo_browser_output.as_uri(), wait_until="domcontentloaded")
    page.wait_for_function("() => typeof kgExecuteViewerCommand === 'function'")
    page.evaluate("kgExecuteViewerCommand({command:'set-view',value:'details'})")
    for concept, blocks in {
        "sr.momentum_four_vector": ["work_energy", "kinetic_limit"],
        "sr.mass_energy_equivalence": ["three_energies", "systems", "heated_box", "heating_calculation", "light_emission", "light_inertia"],
        "sr.time_dilation": ["light_clock_setup", "light_clock_derivation", "worked_comparison", "interval_derivation", "reciprocal"],
        "sr.proper_time": ["rate"],
        "sr.lorentz_transformations": ["boost_formula", "interval_condition", "interval_check"],
    }.items():
        page.evaluate(
            "id => kgExecuteViewerCommand({command: 'select', target: 'concept:' + id})",
            concept,
        )
        for block_id in blocks:
            block = page.locator(f'[data-content-block-id="{concept}.{block_id}"]')
            block.locator("mjx-container").first.wait_for(state="attached")
            assert block.locator("mjx-merror, [data-mjx-error]").count() == 0
            assert block.locator('mjx-container[display="true"]').evaluate_all(
                "elements => elements.every(e => !e.clientWidth || e.scrollWidth <= e.clientWidth + 2)"
            ), block_id


@pytest.mark.browser_full  # Dynamic fixture lookup bypasses automatic fixture classification.
@pytest.mark.parametrize("graph_fixture", ["repo_browser_graph", "mobile_repo_browser_graph"])
@pytest.mark.parametrize("tutorial_id", ["using-physicskg", "rest-energy-to-sr-foundations", "time-dilation"])
def test_authored_route_walkthrough(request, graph_fixture, tutorial_id):
    graph = request.getfixturevalue(graph_fixture)
    page = _open_tutorial(graph, tutorial_id)
    baseline = page.evaluate("kgCaptureTutorialPresentation()")
    personal = page.evaluate("kgPersonalData.getSnapshot()")
    steps = page.evaluate("id => tutorialData.find(t => t.tutorial_id === id).steps", tutorial_id)
    previous_selection = baseline["selection"]
    page.locator("#kg_tutorial_start").click()
    for index, step in enumerate(steps):
        page.wait_for_function("i => !kgTutorialPlaybackSnapshot().transitioning && kgTutorialPlaybackSnapshot().stepIndex === i", arg=index, timeout=30000)
        assert page.locator("#kg_tutorial_error").is_hidden(), (step["step_id"], page.locator("#kg_tutorial_error").inner_text())
        assert page.evaluate("kgViewerStateSnapshot().selection.type") != "none"
        selection = page.evaluate("kgViewerStateSnapshot().selection")
        if tutorial_id != "using-physicskg":
            final_action = (step.get("actions") or [step])[-1]["action"]
            if final_action["command"] in {
                "open-details-block", "open-details-graphic", "open-details-relationship", "open-study-questions"
            }:
                assert page.evaluate("kgCaptureTutorialPresentation().view") == "details", step["step_id"]
            elif final_action["command"] in {"fit", "select"}:
                assert page.evaluate("kgCaptureTutorialPresentation().view") == "graph", step["step_id"]
        if tutorial_id == "using-physicskg":
            graph_steps = {
                "see-the-whole-map", "overview-across-subjects", "return-to-one-module", "select-a-module",
                "choose-the-pane", "choose-graph-emphasis", "reveal-the-concepts",
                "preview-a-concept", "select-a-concept", "choose-connections",
                "show-the-context", "frame-the-result", "preview-a-relationship",
                "return-to-the-map", "show-the-derivation-in-graph", "show-a-derivation-tree",
            }
            if step["step_id"] in graph_steps:
                assert page.evaluate("kgCaptureTutorialPresentation().view") == "graph", step["step_id"]
            if step["step_id"] == "overview-across-subjects":
                presentation = page.evaluate("kgCaptureTutorialPresentation()")
                assert presentation["displayScope"] == "overview"
                assert presentation["contextRule"]["preset"] == "derivation"
                for module_id, representation in presentation["moduleRepresentation"].items():
                    assert representation == ("expanded" if module_id.startswith(("sr.", "math.")) else "folded")
            if step["step_id"] in {"inspect-details", "inspect-a-derivation-tree"}:
                assert page.evaluate("kgCaptureTutorialPresentation().view") == "details"
        if tutorial_id == "using-physicskg" and step["step_id"] == "select-a-module":
            assert selection != previous_selection
        if tutorial_id == "using-physicskg" and step["step_id"] == "show-a-derivation-tree":
            assert selection == {"type": "concept", "id": "sr.mass_energy_equivalence"}
            assert page.evaluate("kgViewerStateSnapshot().contextRule.preset") == "derivation"
            assert page.evaluate("kgViewerStateSnapshot().contextRule.depth") == "transitive"
            assert page.evaluate("kgViewerStateSnapshot().displayScope") == "context"
            assert page.evaluate("kgContextContractionSnapshot().active")
        previous_selection = selection
        pointer = (step.get("actions") or [step])[-1].get("pointer", {}).get("target", "narration")
        assert page.evaluate("kgTutorialPointerSnapshot().target") == pointer, step["step_id"]
        _assert_block_pointer_matches(page, pointer, step["step_id"])
        if step["step_id"] in {"begin-with-rest-energy", "begin-with-two-ticks"}:
            assert page.evaluate("kgContextContractionSnapshot().active")
            checkpoint = page.evaluate("kgCaptureTutorialPresentation()")
            page.locator("#kg_tutorial_explore").click()
            page.evaluate("kgExecuteViewerCommand({command:'set-view',value:'graph'})")
            page.locator("#kg_tutorial_explore").click()
            page.wait_for_function("!kgTutorialPlaybackSnapshot().transitioning")
            restored = page.evaluate("kgCaptureTutorialPresentation()")
            for key in ("selection", "contextRule", "view", "displayScope", "contextFit", "moduleRepresentation"):
                assert restored[key] == checkpoint[key], key
        if index + 1 < len(steps):
            page.locator("#kg_tutorial_next").click()
    assert page.locator("#kg_tutorial_next").is_disabled()
    assert page.evaluate("kgPersonalData.getSnapshot()") == personal
    page.locator("#kg_tutorial_exit").click()
    page.wait_for_function("!kgTutorialPlaybackSnapshot().active")
    restored = page.evaluate("kgCaptureTutorialPresentation()")
    for key in ("selection", "contextRule", "displayScope", "view", "moduleRepresentation", "details"):
        assert restored[key] == baseline[key], key


@pytest.mark.parametrize('width', [1280, 390])
def test_guided_details_allow_reading_without_navigation_or_hover(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({'width': width, 'height': 932})
    _open_tutorial(browser_graph)
    page.locator('#kg_tutorial_start').click()
    page.wait_for_function('!kgTutorialPlaybackSnapshot().transitioning')
    panel = page.locator('#info_panel')
    assert not panel.evaluate('e=>e.inert')
    before = page.evaluate('kgPersonalData.getSnapshot()')
    selection = page.evaluate('kgViewerStateSnapshot().selection')
    clarification = page.locator('#info_panel details.optional-detail').first
    clarification.locator(':scope > summary').click()
    assert clarification.evaluate('e=>e.open')
    link = clarification.locator('.concept-link').first
    link.hover(force=True)
    assert page.locator('#kg_concept_preview').is_hidden()
    link.click(force=True)
    assert page.evaluate('kgViewerStateSnapshot().selection') == selection
    checkbox = panel.locator('.content-block-read-toggle').first
    assert checkbox.is_disabled()
    checkbox.click(force=True)
    assert page.evaluate('kgPersonalData.getSnapshot()') == before
    initial_font = panel.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')
    graph_scale = page.evaluate('network.getScale()')
    panel.evaluate('''e=>e.dispatchEvent(new WheelEvent('wheel', {
      bubbles:true, cancelable:true, ctrlKey:true, deltaY:-100
    }))''')
    assert panel.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)') > initial_font
    wheel_font = panel.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')
    panel.evaluate('''panel=>{
      function touches(distance) {
        return [0,1].map(i=>new Touch({identifier:i, target:panel,
          clientX:100+i*distance, clientY:200}));
      }
      panel.dispatchEvent(new TouchEvent('touchstart', {
        bubbles:true, cancelable:true, touches:touches(100)}));
      panel.dispatchEvent(new TouchEvent('touchmove', {
        bubbles:true, cancelable:true, touches:touches(150)}));
      panel.dispatchEvent(new TouchEvent('touchend', {
        bubbles:true, cancelable:true, touches:[]}));
    }''')
    assert panel.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)') > wheel_font
    assert page.evaluate('network.getScale()') == pytest.approx(graph_scale)
    panel.evaluate('''e=>{
      e.querySelector('.concept-sticky-header').insertAdjacentHTML('afterend',
        '<p id="tutorial-select-text">Readable tutorial paragraph.</p>' +
        '<mjx-container id="tutorial-wide-equation" display="true"><svg style="width:1400px;height:40px"></svg></mjx-container>');
      window.dispatchEvent(new Event('resize'));
    }''')
    page.locator('#tutorial-select-text').dblclick(position={'x':40,'y':10})
    assert page.evaluate('getSelection().toString().length') > 0
    equation = page.locator('#tutorial-wide-equation')
    equation.scroll_into_view_if_needed()
    box = equation.bounding_box()
    page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
    page.mouse.wheel(160, 0)
    page.wait_for_function('document.querySelector("#tutorial-wide-equation").scrollLeft > 0')
    old_top = panel.evaluate('e=>e.scrollTop')
    page.mouse.wheel(0, 160)
    page.wait_for_function('top=>document.querySelector("#info_panel").scrollTop>top', arg=old_top)
    assert page.evaluate('kgViewerStateSnapshot().selection') == selection
    page.locator('#kg_tutorial_explore').click()
    assert not checkbox.is_disabled()
