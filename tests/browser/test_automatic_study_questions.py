import pytest


def _open_automatic_question(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.2")
    page.locator("#kg_details_view_select").select_option("practice")
    return page.locator('.study-question[data-question-id="2.2.q3"]')


@pytest.mark.browser
def test_automatic_question_hides_answer_until_a_response(browser_graph):
    page = browser_graph.page
    question = _open_automatic_question(browser_graph)

    assert question.count() == 1
    assert question.locator('input[type="radio"]').count() == 4
    assert "I don’t know" in question.locator(".study-option-unknown").inner_text()
    assert question.locator(".study-answer-body").count() == 0
    assert question.locator(".study-question-feedback").count() == 0
    assert question.locator(".study-check-answer").is_disabled()
    page.wait_for_function(
        """() => document.querySelector(
          '.study-question[data-question-id="2.2.q3"] .study-option mjx-container'
        ) !== null"""
    )


@pytest.mark.browser
def test_automatic_question_marks_answers_and_prevents_duplicate_submission(browser_graph):
    page = browser_graph.page
    question = _open_automatic_question(browser_graph)
    wrong = question.locator('input[value="2.2.q3.a"]')
    correct = question.locator('input[value="2.2.q3.b"]')
    check = question.locator(".study-check-answer")

    wrong.check()
    assert not check.is_disabled()
    check.click()

    assert "Not quite — review the answer and have another go." in question.locator(
        ".study-question-feedback"
    ).inner_text()
    assert question.locator('.study-option[data-option-id="2.2.q3.a"]').get_attribute(
        "data-result"
    ) == "incorrect"
    assert question.locator('.study-option[data-option-id="2.2.q3.b"]').get_attribute(
        "data-result"
    ) == "correct"
    assert question.locator(
        '.study-option[data-option-id="2.2.q3.a"] .study-option-result'
    ).inner_text() == "✕ Your answer"
    assert question.locator(
        '.study-option[data-option-id="2.2.q3.b"] .study-option-result'
    ).inner_text() == "✓ Correct answer"
    assert question.locator(".study-answer-body").is_visible()
    assert check.is_disabled()
    assert page.evaluate(
        "() => window.kgStudyProgress.getQuestion('2.2.q3').attemptCount"
    ) == 1

    correct.check()
    assert not check.is_disabled()
    check.click()

    assert "Correct — nicely done." in question.locator(
        ".study-question-feedback"
    ).inner_text()
    assert question.locator(".study-question-status").get_attribute("data-outcome") == "correct"
    assert page.evaluate(
        "() => window.kgStudyProgress.getQuestion('2.2.q3')"
    )["attemptCount"] == 2

    question.locator(":scope > summary").click()
    assert not question.evaluate("element => element.open")
    assert question.locator(".study-question-status").is_visible()


@pytest.mark.browser
def test_automatic_question_unknown_response_records_unknown(browser_graph):
    page = browser_graph.page
    question = _open_automatic_question(browser_graph)

    question.locator('input[value="__unknown__"]').check()
    question.locator(".study-check-answer").click()

    assert "No problem — review the answer, then try when ready." in question.locator(
        ".study-question-feedback"
    ).inner_text()
    assert page.evaluate(
        "() => window.kgStudyProgress.getQuestion('2.2.q3').lastOutcome"
    ) == "unknown"
    assert question.locator('.study-option[data-option-id="2.2.q3.b"]').get_attribute(
        "data-result"
    ) == "correct"


@pytest.mark.browser
def test_automatic_question_can_be_answered_with_the_keyboard(browser_graph):
    page = browser_graph.page
    question = _open_automatic_question(browser_graph)
    correct = question.locator('input[value="2.2.q3.b"]')
    check = question.locator(".study-check-answer")

    correct.focus()
    page.keyboard.press("Space")
    check.focus()
    page.keyboard.press("Enter")

    assert question.locator(".study-question-status").get_attribute("data-outcome") == "correct"
    feedback_host = question.locator(".study-feedback-host")
    assert feedback_host.get_attribute("role") == "status"
    assert feedback_host.get_attribute("aria-atomic") == "true"


@pytest.mark.browser
def test_automatic_question_restores_attempted_state_after_reload(browser_graph):
    page = browser_graph.page
    question = _open_automatic_question(browser_graph)
    question.locator('input[value="2.2.q3.b"]').check()
    question.locator(".study-check-answer").click()

    page.reload(wait_until="load")
    page.wait_for_function("() => Boolean(window.kgStudyProgress)")
    question = _open_automatic_question(browser_graph)

    assert question.locator(".study-question-status").get_attribute("data-outcome") == "correct"
    assert question.locator(".study-answer-body").is_visible()
    assert question.locator('.study-option[data-option-id="2.2.q3.b"]').get_attribute(
        "data-result"
    ) == "correct"


@pytest.mark.browser
def test_real_authored_multiple_choice_question_uses_automatic_card(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.click_concept("sr.principle_of_relativity")
    page.locator("#kg_details_view_select").select_option("practice")

    question = page.locator(
        '.study-question-automatic[data-question-id="sr.principle_of_relativity.q1"]'
    )
    assert question.count() == 1
    assert question.locator(".study-option").count() == 5
    assert question.locator(".study-answer-body").count() == 0


@pytest.mark.browser
def test_real_authored_calculation_is_automatically_marked(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.click_concept("sr.time_dilation")
    page.locator("#kg_details_view_select").select_option("practice")

    question = page.locator(
        '.study-question-automatic[data-question-id="sr.time_dilation.q2"]'
    )
    assert question.count() == 1
    assert question.locator(".study-option").count() == 5
    assert question.locator(".study-answer-body").count() == 0

    question.locator('input[value="sr.time_dilation.q2.a"]').check()
    question.locator(".study-check-answer").click()

    assert question.locator(".study-question-status").get_attribute(
        "data-outcome"
    ) == "correct"
    assert question.locator(".study-answer-body").is_visible()
