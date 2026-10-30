import pytest


pytestmark = pytest.mark.browser


def test_history_button_keeps_keyboard_focus_between_selections(browser_graph):
    page = browser_graph.page
    for concept_id in ("1.1", "2.2", "3.1"):
        browser_graph.click_concept(concept_id)
    page.locator("#kg_history_back").focus()
    page.keyboard.press("Enter")
    page.wait_for_function("location.hash === '#concept-2.2'")
    assert page.locator("#kg_history_back").evaluate("el => el === document.activeElement")
    page.keyboard.press("Enter")
    page.wait_for_function("location.hash === '#concept-1.1'")


def test_selection_history_buttons_follow_native_history_and_branching(browser_graph):
    page = browser_graph.page
    back = page.locator("#kg_history_back")
    forward = page.locator("#kg_history_forward")
    assert back.is_disabled()
    assert forward.is_disabled()
    browser_graph.click_concept("1.1")
    browser_graph.click_concept("2.2")
    page.evaluate("kgExecuteViewerCommand({command:'select',target:'module:test.m01_foundations'})")
    back.click()
    page.wait_for_function("location.hash === '#concept-2.2'")
    assert page.locator("#info_panel").get_attribute("data-concept-id") == "2.2"
    assert forward.is_enabled()
    page.go_back()
    page.wait_for_function("location.hash === '#concept-1.1'")
    forward.click()
    page.wait_for_function("location.hash === '#concept-2.2'")
    browser_graph.click_concept("3.1")
    assert forward.is_disabled()
    browser_graph.open_control_section("kg_modules_section")
    page.locator('#kg_module_list [data-module-id="test.m02_applications"]').click()
    assert page.locator("#info_panel").get_attribute("data-module-id") == "test.m02_applications"
    back.click()
    page.wait_for_function("location.hash === '#concept-3.1'")
    back.click()
    page.wait_for_function("location.hash === '#concept-2.2'")
    back.click()
    page.wait_for_function("location.hash === '#concept-1.1'")
    back.click()
    page.wait_for_function("location.hash === '#module-test.m01_foundations'")
    assert back.is_disabled()
    assert forward.is_enabled()


@pytest.mark.parametrize("width", [390, 1280])
def test_history_controls_take_no_layout_space_and_work_with_graph_hidden(browser_graph, width):
    page = browser_graph.page
    page.set_viewport_size({"width": width, "height": 844})
    browser_graph.click_concept("2.2")
    before = page.locator("#kg_workspace").bounding_box()
    controls = page.locator("#kg_history_controls")
    controls.evaluate("el => { el.hidden = true; }")
    assert page.locator("#kg_workspace").bounding_box() == before
    controls.evaluate("el => { el.hidden = false; }")
    page.locator("#kg_view_select").select_option("details")
    assert controls.is_visible()
    box = controls.bounding_box()
    assert box["x"] >= 0 and box["x"] + box["width"] <= width
    assert box["y"] + box["height"] <= 844
    page.locator("#kg_history_back").click()
    page.wait_for_function("location.hash === '#module-test.m01_foundations'")
    assert page.locator("#kg_view_select").input_value() == "details"


def test_history_boundary_resets_on_reload_and_survives_tutorial_exploration(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("1.1")
    page.reload()
    page.wait_for_function("typeof kgStartTutorial === 'function'")
    assert page.locator("#kg_history_back").is_disabled()
    browser_graph.click_concept("2.2")
    page.evaluate("kgStartTutorial('viewer-tour')")
    page.wait_for_function("kgTutorialPlaybackSnapshot().active && !kgTutorialPlaybackSnapshot().transitioning")
    assert page.locator("#kg_history_controls").is_hidden()
    page.locator("#kg_tutorial_explore").click()
    assert page.locator("#kg_history_controls").is_visible()
    browser_graph.click_concept("3.1")
    page.locator("#kg_tutorial_explore").click()
    page.wait_for_function("!kgTutorialPlaybackSnapshot().transitioning")
    page.locator("#kg_tutorial_exit").click()
    page.wait_for_function("!kgTutorialPlaybackSnapshot().active")
    assert page.locator("#kg_history_back").is_enabled()
    page.locator("#kg_history_back").click()
    page.wait_for_function("location.hash === '#concept-2.2'")
    page.locator("#kg_history_back").click()
    page.wait_for_function("location.hash === '#concept-1.1'")
    assert page.locator("#kg_history_back").is_disabled()
