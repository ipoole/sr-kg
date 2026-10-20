import pytest


@pytest.mark.browser
def test_next_concept_action_follows_module_member_order_and_wraps(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    next_button = page.locator("#info_panel .concept-next-button")

    assert next_button.inner_text() == "Next: 2.2 Gamma"
    next_button.click()
    assert page.locator("#info_panel").get_attribute("data-concept-id") == "2.2"
    assert page.url.endswith("#concept-2.2")

    browser_graph.click_concept("3.1")
    assert next_button.inner_text() == "Start again: 1.1 Alpha"


@pytest.mark.browser
def test_repo_reading_order_runs_from_sr_through_maths_to_gr(repo_browser_graph):
    page = repo_browser_graph.page
    order = page.evaluate("() => kgSequentialConceptIds()")

    assert order[0] == "sr.inertial_frames"
    assert page.evaluate("id => conceptData[id].display_id", order[0]) == "SR-1.1"
    domains = [page.evaluate("id => conceptData[id].domain", concept_id) for concept_id in order]
    transitions = [domains[index] for index in range(len(domains)) if index == 0 or domains[index] != domains[index - 1]]
    assert transitions == ["sr", "math", "gr"]
