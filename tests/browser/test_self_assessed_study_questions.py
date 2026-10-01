import pytest


def _open_self_assessed_question(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_details_view_select").select_option("practice")
    return page.locator('.study-question[data-question-id="2.1.q1"]')


@pytest.mark.browser
def test_self_assessed_question_requires_a_response_before_revealing_answer(browser_graph):
    page = browser_graph.page
    question = _open_self_assessed_question(browser_graph)

    assert question.locator("textarea.study-self-response").count() == 1
    assert question.locator(".study-answer-body").count() == 0
    question.locator(".study-self-check-answer").click()

    assert "Enter an answer" in question.locator(".study-response-validation").inner_text()
    assert question.locator(".study-answer-body").count() == 0
    assert page.evaluate(
        "() => window.kgStudyProgress.getQuestion('2.1.q1')"
    ) is None


@pytest.mark.browser
def test_self_assessed_question_reveals_comparison_then_records_self_mark(browser_graph):
    page = browser_graph.page
    question = _open_self_assessed_question(browser_graph)
    response = question.locator("textarea.study-self-response")

    response.fill("My considered answer")
    question.locator(".study-self-check-answer").click()

    assert "Compare your answer, then mark it honestly." in question.locator(
        ".study-question-feedback"
    ).inner_text()
    assert "My considered answer" in question.locator(".study-your-answer").inner_text()
    assert "Beta answer" in question.locator(".study-answer-body").inner_text()
    assert question.locator(".study-self-mark").count() == 2
    assert page.evaluate(
        "() => window.kgStudyProgress.getQuestion('2.1.q1')"
    ) is None

    question.locator('.study-self-mark[data-outcome="correct"]').click()

    progress = page.evaluate(
        "() => window.kgStudyProgress.getQuestion('2.1.q1')"
    )
    assert progress["attemptCount"] == 1
    assert progress["lastOutcome"] == "correct"
    assert question.locator(".study-question-status").get_attribute("data-outcome") == "correct"
    assert "Correct — nicely done." in question.locator(
        ".study-question-feedback"
    ).inner_text()
    assert question.locator(".study-self-mark").count() == 0
    stored = page.evaluate("() => localStorage.getItem('srkg.studyProgress.v1')")
    assert "My considered answer" not in stored

    question.locator(":scope > summary").click()
    assert not question.evaluate("element => element.open")
    assert question.locator(".study-question-status").is_visible()


@pytest.mark.browser
def test_self_assessed_question_allows_another_changed_response(browser_graph):
    page = browser_graph.page
    question = _open_self_assessed_question(browser_graph)
    response = question.locator("textarea.study-self-response")

    response.fill("First response")
    question.locator(".study-self-check-answer").click()
    question.locator('.study-self-mark[data-outcome="correct"]').click()

    response.fill("Changed response")
    question.locator(".study-self-check-answer").click()
    question.locator('.study-self-mark[data-outcome="incorrect"]').click()

    progress = page.evaluate(
        "() => window.kgStudyProgress.getQuestion('2.1.q1')"
    )
    assert progress["attemptCount"] == 2
    assert progress["lastOutcome"] == "incorrect"


@pytest.mark.browser
def test_self_assessed_unknown_records_immediately_and_restores_after_reload(browser_graph):
    page = browser_graph.page
    question = _open_self_assessed_question(browser_graph)

    question.locator(".study-self-unknown").click()

    assert page.evaluate(
        "() => window.kgStudyProgress.getQuestion('2.1.q1').lastOutcome"
    ) == "unknown"
    assert "Beta answer" in question.locator(".study-answer-body").inner_text()

    page.reload(wait_until="load")
    page.wait_for_function("() => Boolean(window.kgStudyProgress)")
    question = _open_self_assessed_question(browser_graph)

    assert question.locator(".study-question-status").get_attribute("data-outcome") == "unknown"
    assert question.locator(".study-answer-body").is_visible()
    assert question.locator("textarea.study-self-response").input_value() == ""
