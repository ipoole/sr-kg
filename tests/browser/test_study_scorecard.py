import pytest


def _open_scorecard(browser_graph):
    browser_graph.open_control_section("kg_study_section")
    return browser_graph.page.locator("#kg_study_section")


@pytest.mark.browser
def test_study_scorecard_starts_empty_and_summarises_attempted_questions(browser_graph):
    page = browser_graph.page
    scorecard = _open_scorecard(browser_graph)

    assert scorecard.locator("#kg_study_summary").inner_text() == "No questions attempted yet."
    assert scorecard.locator(".kg-study-row").count() == 0

    page.evaluate(
        """() => {
          window.kgStudyProgress.recordAttempt(
            "2.1.q1", "incorrect", "2026-09-30T10:00:00.000Z"
          );
          window.kgStudyProgress.recordAttempt(
            "2.2.q3", "correct", "2026-09-30T10:01:00.000Z"
          );
        }"""
    )

    assert scorecard.locator("#kg_study_summary").inner_text() == (
        "1 correct out of 2 attempted"
    )
    rows = scorecard.locator(".kg-study-row")
    assert rows.count() == 2
    assert rows.nth(0).get_attribute("data-question-id") == "2.2.q3"
    assert "Correct" in rows.nth(0).inner_text()
    assert "Incorrect" in rows.nth(1).inner_text()
    assert "1 attempt" in rows.nth(1).inner_text()


@pytest.mark.browser
def test_study_scorecard_navigates_to_practice_question(browser_graph):
    page = browser_graph.page
    page.evaluate(
        "() => window.kgStudyProgress.recordAttempt('2.1.q1', 'correct')"
    )
    scorecard = _open_scorecard(browser_graph)

    scorecard.locator('.kg-study-question-link[data-question-id="2.1.q1"]').click()

    assert page.locator("#info_panel").get_attribute("data-concept-id") == "2.1"
    assert page.locator("#kg_details_view_select").input_value() == "practice"
    question = page.locator('.study-question[data-question-id="2.1.q1"]')
    assert question.evaluate("element => element.open")
    assert question.get_attribute("data-scorecard-target") == "true"


@pytest.mark.browser
def test_study_scorecard_resets_one_question_or_all_progress(browser_graph):
    page = browser_graph.page
    page.evaluate(
        """() => {
          window.kgStudyProgress.recordAttempt("2.1.q1", "correct");
          window.kgStudyProgress.recordAttempt("2.2.q3", "incorrect");
        }"""
    )
    scorecard = _open_scorecard(browser_graph)

    scorecard.locator('.kg-study-reset-question[data-question-id="2.1.q1"]').click()
    assert scorecard.locator('.kg-study-row[data-question-id="2.1.q1"]').count() == 0
    assert scorecard.locator(".kg-study-row").count() == 1

    page.once("dialog", lambda dialog: dialog.accept())
    scorecard.locator("#kg_study_reset_all").click()

    assert scorecard.locator(".kg-study-row").count() == 0
    assert scorecard.locator("#kg_study_summary").inner_text() == "No questions attempted yet."
