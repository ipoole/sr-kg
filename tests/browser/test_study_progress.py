import pytest


@pytest.mark.browser
def test_study_progress_records_latest_outcome_and_attempt_count(browser_graph):
    page = browser_graph.page

    assert page.evaluate("() => window.kgStudyProgress.getState()") == {
        "version": 1,
        "questions": {},
    }

    first = page.evaluate(
        """() => window.kgStudyProgress.recordAttempt(
          "2.1.q1", "incorrect", "2026-09-30T09:00:00.000Z"
        )"""
    )
    second = page.evaluate(
        """() => window.kgStudyProgress.recordAttempt(
          "2.1.q1", "correct", "2026-09-30T09:01:00.000Z"
        )"""
    )

    assert first == {
        "attemptCount": 1,
        "lastOutcome": "incorrect",
        "lastAttemptAt": "2026-09-30T09:00:00.000Z",
    }
    assert second == {
        "attemptCount": 2,
        "lastOutcome": "correct",
        "lastAttemptAt": "2026-09-30T09:01:00.000Z",
    }
    assert page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.studyProgress.v1'))"
    ) == {
        "version": 1,
        "questions": {"2.1.q1": second},
    }


@pytest.mark.browser
def test_study_progress_discards_malformed_and_unknown_stored_entries(browser_graph):
    page = browser_graph.page
    page.evaluate(
        """() => localStorage.setItem("srkg.studyProgress.v1", JSON.stringify({
          version: 1,
          questions: {
            "2.1.q1": {
              attemptCount: 3,
              lastOutcome: "unknown",
              lastAttemptAt: "2026-09-30T09:02:00.000Z"
            },
            "missing.q1": {
              attemptCount: 2,
              lastOutcome: "correct",
              lastAttemptAt: "2026-09-30T09:03:00.000Z"
            },
            "2.2.q1": {
              attemptCount: 0,
              lastOutcome: "maybe",
              lastAttemptAt: ""
            }
          }
        }))"""
    )
    page.reload(wait_until="load")
    page.wait_for_function("() => Boolean(window.kgStudyProgress)")

    assert page.evaluate("() => window.kgStudyProgress.getState()") == {
        "version": 1,
        "questions": {
            "2.1.q1": {
                "attemptCount": 3,
                "lastOutcome": "unknown",
                "lastAttemptAt": "2026-09-30T09:02:00.000Z",
            }
        },
    }


@pytest.mark.browser
def test_study_progress_reset_operations_and_invalid_attempts(browser_graph):
    page = browser_graph.page
    page.evaluate(
        """() => {
          window.kgStudyProgress.recordAttempt("2.1.q1", "correct");
          window.kgStudyProgress.recordAttempt("2.2.q1", "incorrect");
        }"""
    )

    assert page.evaluate(
        "() => window.kgStudyProgress.recordAttempt('missing.q1', 'correct')"
    ) is None
    assert page.evaluate(
        "() => window.kgStudyProgress.recordAttempt('2.1.q1', 'maybe')"
    ) is None

    page.evaluate("() => window.kgStudyProgress.resetQuestion('2.1.q1')")
    assert page.evaluate("() => window.kgStudyProgress.getQuestion('2.1.q1')") is None
    assert page.evaluate("() => window.kgStudyProgress.getQuestion('2.2.q1')")[
        "attemptCount"
    ] == 1

    page.evaluate("() => window.kgStudyProgress.resetAll()")
    assert page.evaluate("() => window.kgStudyProgress.getState().questions") == {}
    assert page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.studyProgress.v1'))"
    ) == {"version": 1, "questions": {}}
