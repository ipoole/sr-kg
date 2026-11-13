import pytest


@pytest.mark.browser
def test_incorrect_badge_retries_without_erasing_latest_result(browser_graph):
    page = browser_graph.page
    question = _open_automatic_question(browser_graph)
    wrong = question.locator('input[value="2.2.q3.a"]')
    wrong.check()
    question.locator('.study-check-answer').click()
    before = page.evaluate("kgPersonalData.getSnapshot()")
    question.locator(':scope > summary').click()
    badge = question.locator('button.study-question-status[data-outcome="incorrect"]')
    badge.focus()
    page.keyboard.press('Enter')
    assert question.evaluate('el => el.open')
    assert question.locator('.study-answer-body').count() == 0
    assert question.locator('.study-option-result').count() == 0
    assert question.locator('input:checked').count() == 0
    assert question.locator('.study-check-answer').is_disabled()
    assert page.evaluate('kgPersonalData.getSnapshot()') == before
    assert question.locator('input').first.evaluate('el => el === document.activeElement')
    # Navigation must not redisclose an answer while a retry is in progress.
    browser_graph.click_concept('2.1')
    question = _open_automatic_question(browser_graph)
    assert question.locator('.study-answer-body').count() == 0
    question.locator('input[value="2.2.q3.a"]').check()
    question.locator('.study-check-answer').click()
    progress = page.evaluate("kgStudyProgress.getQuestion('2.2.q3')")
    assert progress['lastOutcome'] == 'incorrect'
    assert question.locator('.study-answer-body').is_visible()


def _open_automatic_question(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.2")
    questions = page.locator("#info_panel details.study-questions")
    if not questions.evaluate("element => element.open"):
        questions.locator(":scope > summary").click()
    return page.locator('.study-question[data-question-id="2.2.q3"]')


@pytest.mark.browser
def test_automatic_question_hides_answer_until_a_response(mathjax_browser_graph):
    page = mathjax_browser_graph.page
    question = _open_automatic_question(mathjax_browser_graph)

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

    assert question.locator(".study-question-feedback").is_visible()
    assert question.locator('.study-option[data-option-id="2.2.q3.a"]').get_attribute(
        "data-result"
    ) == "incorrect"
    assert question.locator('.study-option[data-option-id="2.2.q3.b"]').get_attribute(
        "data-result"
    ) == "correct"
    assert question.locator(".study-option-result").count() == 2
    assert question.locator(".study-answer-body").is_visible()
    assert check.is_disabled()
    assert page.evaluate("kgStudyProgress.getQuestion('2.2.q3').lastOutcome") == "incorrect"

    correct.check()
    assert not check.is_disabled()
    check.click()

    assert question.locator(".study-question-feedback").is_visible()
    assert question.locator(".study-question-status").get_attribute("data-outcome") == "correct"
    assert page.evaluate("kgStudyProgress.getQuestion('2.2.q3').lastOutcome") == "correct"

    question.locator(":scope > summary").click()
    assert not question.evaluate("element => element.open")
    assert question.locator(".study-question-status").is_visible()


@pytest.mark.browser
def test_automatic_question_unknown_response_records_unknown(browser_graph):
    page = browser_graph.page
    question = _open_automatic_question(browser_graph)

    question.locator('input[value="__unknown__"]').check()
    question.locator(".study-check-answer").click()

    assert question.locator(".study-question-feedback").is_visible()
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
    page.locator("#info_panel details.study-questions > summary").click()

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
    page.locator("#info_panel details.study-questions > summary").click()

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
