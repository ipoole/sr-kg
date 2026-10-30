import pytest


pytestmark = pytest.mark.browser


def test_context_controls_have_accessible_help_and_fit_help_tracks_action(browser_graph):
    page = browser_graph.page
    for control_id in ("kg_context_preset_select", "kg_context_depth_select", "kg_fit_select", "kg_fit_apply"):
        control = page.locator("#" + control_id)
        description = page.locator("#" + control.get_attribute("aria-describedby"))
        assert description.text_content().strip()
        assert control.get_attribute("title") == description.text_content()

    browser_graph.click_concept("2.2")
    page.locator("#kg_fit_select").select_option("context")
    page.locator("#kg_fit_apply").click()
    page.wait_for_function("document.getElementById('kg_fit_apply').textContent === 'Fit++'")
    assert "restore" in page.locator("#kg_fit_apply").get_attribute("title")
    browser_graph.click_concept("1.1")
    assert page.locator("#kg_fit_apply").get_attribute("title") == page.locator("#kg_fit_help").text_content()
