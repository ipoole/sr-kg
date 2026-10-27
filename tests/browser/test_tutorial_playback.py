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
    page.locator("#kg_tutorial_start").click()
    for index in range(3):
        page.wait_for_function(
            "index => !kgTutorialPlaybackSnapshot().transitioning && kgTutorialPlaybackSnapshot().stepIndex === index",
            arg=index,
        )
        if index < 2:
            page.locator("#kg_tutorial_next").click()
    page.wait_for_function("""() => {
      const bounds = kgModuleFootprint('sr.spacetime_foundations');
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
    page.locator("#kg_tutorial_start").click()
    page.wait_for_function(
        "() => kgTutorialPointerSnapshot().target === 'control:expand-context'",
        timeout=30000,
    )
    assert page.evaluate("kgTutorialPlaybackSnapshot().stepIndex") == 0
    assert page.locator("#kg_tutorial_next").is_disabled()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && kgTutorialPlaybackSnapshot().stepIndex === 0",
        timeout=30000,
    )
    for step_index in range(1, 6):
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
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 6"
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
    page.locator("#kg_clear_selection").click(force=True)

    after = page.evaluate("window.kgCaptureTutorialPresentation()")
    assert after["selection"] == before["selection"]
    assert after["moduleRepresentation"] == before["moduleRepresentation"]
    assert page.locator("#kg_clear_selection").evaluate(
        "el => getComputedStyle(el).cursor"
    ) == "not-allowed"
    assert page.locator("#kg_tutorial_next").evaluate(
        "el => getComputedStyle(el).cursor"
    ) == "pointer"


def test_explore_here_releases_interaction_and_resume_restores_the_step(browser_graph):
    page = _open_tutorial(browser_graph)
    page.locator("#kg_tutorial_start").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 0"
    )
    checkpoint = page.evaluate("window.kgCaptureTutorialPresentation()")
    pointer_target = page.evaluate("window.kgTutorialPointerSnapshot().target")

    page.locator("#kg_tutorial_explore").click()
    assert page.evaluate("kgTutorialPlaybackSnapshot().exploring") is True
    assert page.locator("#kg_tutorial_explore").inner_text() == "Resume tutorial"
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


def test_authored_interface_tutorial_completes(repo_browser_graph):
    page = _open_tutorial(repo_browser_graph, "using-physicskg")
    page.locator("#kg_tutorial_start").click()

    expected_targets = [
        "control:fit",
        "graph:module:sr.spacetime_foundations",
        "control:fit",
        "graph:concept:sr.spacetime_event",
        "graph:concept:sr.spacetime_event",
        "control:context",
        "control:display-scope",
        "control:fit",
        "graph:edge:sr.spacetime_event|REQUIRES|sr.inertial_frames",
        "control:display-scope",
        "control:search",
        "search:concept:sr.lorentz_transformations",
        "details:block:sr.lorentz_transformations.overview",
        "control:tools",
    ]
    for index, expected_target in enumerate(expected_targets):
        page.wait_for_function(
            "index => !kgTutorialPlaybackSnapshot().transitioning && "
            "kgTutorialPlaybackSnapshot().stepIndex === index",
            arg=index,
        )
        assert page.evaluate("kgTutorialPointerSnapshot().target") == expected_target
        if index == 3:
            assert page.locator("#kg_node_tooltip").is_visible()
            assert "Spacetime event" in page.locator("#kg_node_tooltip").inner_text()
            _assert_elements_do_not_overlap(
                page, "#kg_tutorial_narration", "#kg_node_tooltip"
            )
            page.locator("#kg_tutorial_explore").click()
            assert page.locator("#kg_node_tooltip").is_hidden()
            page.locator("#kg_tutorial_explore").click()
            page.wait_for_function(
                "() => !kgTutorialPlaybackSnapshot().transitioning && "
                "!kgTutorialPlaybackSnapshot().exploring"
            )
            assert page.locator("#kg_node_tooltip").is_visible()
            assert "Spacetime event" in page.locator("#kg_node_tooltip").inner_text()
        if index == 4:
            assert page.locator("#kg_node_tooltip").is_hidden()
        if index == 8:
            assert page.locator("#kg_node_tooltip").is_visible()
            assert "requires" in page.locator("#kg_node_tooltip").inner_text().lower()
            _assert_elements_do_not_overlap(
                page, "#kg_tutorial_narration", "#kg_node_tooltip"
            )
        if index == 9:
            assert page.locator("#kg_node_tooltip").is_hidden()
        _assert_block_pointer_matches(page, expected_target, index)
        if index < len(expected_targets) - 1:
            page.locator("#kg_tutorial_next").click()

    assert page.locator("#kg_tutorial_next").is_disabled()
    page.locator("#kg_tutorial_back").click()
    page.wait_for_function(
        "() => !kgTutorialPlaybackSnapshot().transitioning && "
        "kgTutorialPlaybackSnapshot().stepIndex === 12"
    )
    assert not page.locator("#kg_search_section").evaluate("el => el.open")
    assert page.evaluate("kgTutorialPointerSnapshot().target") == (
        "details:block:sr.lorentz_transformations.overview"
    )
    page.locator("#kg_tutorial_exit").click()
    page.wait_for_function("() => !kgTutorialPlaybackSnapshot().active")


@pytest.mark.browser_full
@pytest.mark.parametrize("graph_fixture", ["repo_browser_graph", "mobile_repo_browser_graph"])
@pytest.mark.parametrize("tutorial_id", ["rest-energy-to-sr-foundations", "time-dilation"])
def test_authored_physics_tutorial_completes(request, graph_fixture, tutorial_id):
    graph = request.getfixturevalue(graph_fixture)
    page = _open_tutorial(graph, tutorial_id)
    study_before = page.evaluate("kgStudyProgress.getState()")
    baseline = page.evaluate("kgCaptureTutorialPresentation()")
    personal_before = page.evaluate("kgPersonalData.getSnapshot()")
    original_workspace = page.locator("#kg_workspace").bounding_box()
    page.locator("#kg_tutorial_start").click()

    expected_targets = [
        "details:block:sr.mass_energy_equivalence.overview",
        "details:block:sr.mass_energy_equivalence.heated_box",
        "details:block:sr.mass_energy_equivalence.three_energies",
        "details:block:sr.mass_energy_equivalence.definition",
        "narration",
        "control:fit",
        "graph:concept:sr.momentum_four_vector",
        "details:block:sr.momentum_four_vector.overview",
        "details:block:sr.momentum_four_vector.invariant_norm",
        "details:block:sr.velocity_four_vector.overview",
        "details:block:sr.velocity_four_vector.fixed_norm",
        "details:block:sr.proper_time.definition",
        "graph:concept:sr.spacetime_interval",
        "control:fit",
        "details:block:sr.spacetime_interval.definition",
        "graph:concept:sr.lorentz_transformations",
        "control:fit",
        "details:block:sr.lorentz_transformations.overview",
        "details:block:sr.lorentz_transformations.interval_condition",
        "details:block:sr.principle_of_relativity.definition",
        "details:block:sr.constancy_of_speed_of_light.definition",
        "details:block:sr.velocity_four_vector.fixed_norm",
        "details:block:sr.momentum_four_vector.components",
        "details:block:sr.momentum_four_vector.work_energy",
        "details:block:sr.momentum_four_vector.kinetic_limit",
        "details:block:sr.momentum_four_vector.energy_physical_input",
        "details:block:sr.momentum_four_vector.invariant_norm",
        "graph:concept:sr.mass_energy_equivalence",
        "control:fit",
        "control:fit",
        "details:block:sr.mass_energy_equivalence.rest_frame",
        "details:block:sr.mass_energy_equivalence.systems",
        "details:block:sr.mass_energy_equivalence.heated_box",
        "details:block:sr.mass_energy_equivalence.heating_calculation",
        "details:block:sr.mass_energy_equivalence.not_substance_conversion",
        "details:study-questions",
    ]
    if tutorial_id == "time-dilation":
        expected_targets = [
            "details:block:sr.time_dilation.overview",
            "details:block:sr.time_dilation.measurement",
            "details:block:sr.time_dilation.light_clock_setup",
            "details:graphic",
            "details:block:sr.time_dilation.light_clock_triangle",
            "details:block:sr.time_dilation.light_clock_derivation",
            "details:block:sr.time_dilation.definition",
            "details:block:sr.time_dilation.ideal_clocks",
            "details:block:sr.time_dilation.worked_comparison",
            "details:block:sr.lorentz_transformations.boost_formula",
            "details:block:sr.time_dilation.lorentz_derivation",
            "details:block:sr.proper_time.coordinate_time",
            "details:block:sr.proper_time.rate",
            "details:block:sr.time_dilation.interval_derivation",
            "details:block:sr.time_dilation.reciprocal",
            "details:block:sr.time_dilation.not_signal_delay",
            "details:study-questions",
        ]
    for index, expected_target in enumerate(expected_targets):
        page.wait_for_function(
            "index => !kgTutorialPlaybackSnapshot().transitioning && "
            "kgTutorialPlaybackSnapshot().stepIndex === index",
            arg=index,
            timeout=30000,
        )
        assert page.locator("#kg_tutorial_error").is_hidden(), page.locator("#kg_tutorial_error").inner_text()
        assert page.evaluate("kgTutorialPointerSnapshot().target") == expected_target
        if index == 0:
            assert page.evaluate("kgContextContractionSnapshot().active") is True
            assert page.locator("#kg_expand_context_modules").is_hidden()
            assert page.locator(".concept-derived-from-full-tree").is_checked()
            checkpoint = page.evaluate("kgCaptureTutorialPresentation()")
            assert checkpoint["contextRule"]["preset"] == "derivation"
            assert checkpoint["contextRule"]["depth"] == "transitive"
            if graph_fixture == "mobile_repo_browser_graph":
                card = page.locator("#kg_tutorial_narration").bounding_box()
                graph_pane = page.locator("#kg_graph_pane").bounding_box()
                details_pane = page.locator("#kg_details_pane").bounding_box()
                assert graph_pane["y"] + graph_pane["height"] <= card["y"]
                assert details_pane["y"] + details_pane["height"] <= card["y"]
                assert page.locator("#kg_context_notice").is_hidden()
            page.locator("#kg_tutorial_explore").click()
            assert page.locator("#kg_context_notice").is_visible()
            page.evaluate("() => kgExecuteViewerCommand({command: 'clear-selection'})")
            page.locator("#kg_tutorial_explore").click()
            page.wait_for_function("() => !kgTutorialPlaybackSnapshot().transitioning")
            restored = page.evaluate("kgCaptureTutorialPresentation()")
            assert restored["contextFit"] == checkpoint["contextFit"]
            assert restored["contextRule"] == checkpoint["contextRule"]
            assert restored["moduleRepresentation"] == checkpoint["moduleRepresentation"]
        if index == 1:
            page.locator("#kg_tutorial_back").click()
            page.wait_for_function(
                "() => !kgTutorialPlaybackSnapshot().transitioning && kgTutorialPlaybackSnapshot().stepIndex === 0",
                timeout=30000,
            )
            assert page.evaluate("kgContextContractionSnapshot().active") is True
            page.locator("#kg_tutorial_next").click()
            page.wait_for_function(
                "() => !kgTutorialPlaybackSnapshot().transitioning && kgTutorialPlaybackSnapshot().stepIndex === 1"
            )
        _assert_block_pointer_matches(page, expected_target, index)
        if index < len(expected_targets) - 1:
            page.locator("#kg_tutorial_next").click()

    assert page.locator("#info_panel .study-questions").evaluate("el => el.open")
    assert page.locator("#info_panel .study-answer-body").count() == 0
    assert page.evaluate("kgStudyProgress.getState()") == study_before
    assert page.evaluate("kgPersonalData.getSnapshot()") == personal_before
    assert page.evaluate("kgContextContractionSnapshot().active") is True
    page.locator("#kg_tutorial_exit").click()
    page.wait_for_function("() => !kgTutorialPlaybackSnapshot().active")
    restored = page.evaluate("kgCaptureTutorialPresentation()")
    assert restored["details"]["derivedFromFullTree"] == baseline["details"]["derivedFromFullTree"]
    assert restored["contextFit"] == baseline["contextFit"]
    assert not page.locator("body").evaluate("el => el.classList.contains('kg-tutorial-phone-docked')")
    workspace = page.locator("#kg_workspace").bounding_box()
    assert workspace["height"] == pytest.approx(original_workspace["height"], abs=2)


def test_revised_physics_equations_render_with_real_mathjax(repo_browser_graph, repo_browser_output):
    page = repo_browser_graph.page
    page.goto(repo_browser_output.as_uri(), wait_until="domcontentloaded")
    page.wait_for_function("() => typeof kgExecuteViewerCommand === 'function'")
    for concept, blocks in {
        "sr.momentum_four_vector": ["work_energy", "kinetic_limit"],
        "sr.mass_energy_equivalence": ["three_energies", "systems", "heated_box", "heating_calculation"],
        "sr.time_dilation": ["light_clock_setup", "light_clock_derivation", "worked_comparison", "interval_derivation", "reciprocal"],
    }.items():
        page.evaluate(
            "id => kgExecuteViewerCommand({command: 'select', target: 'concept:' + id})",
            concept,
        )
        for block_id in blocks:
            block = page.locator(f'[data-content-block-id="{concept}.{block_id}"]')
            block.locator("mjx-container").first.wait_for(state="attached")
            assert block.locator("mjx-merror, [data-mjx-error]").count() == 0
