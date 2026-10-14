import pytest


def _study_controls(browser_graph):
    browser_graph.open_control_section("kg_study_section")
    return browser_graph.page.locator("#kg_study_section")


@pytest.mark.browser
def test_graph_completion_markers_are_on_by_default_and_preference_persists(browser_graph):
    page = browser_graph.page
    study = _study_controls(browser_graph)
    toggle = study.locator("#kg_graph_completion_markers")

    assert toggle.is_checked()
    assert page.evaluate("() => kgGraphCompletionMarkersSnapshot().enabled") is True

    toggle.uncheck()
    assert page.evaluate("() => kgGraphCompletionMarkersSnapshot().enabled") is False
    assert page.evaluate(
        "() => localStorage.getItem('srkg.graphCompletionMarkers.v1')"
    ) == "false"

    page.reload(wait_until="load")
    page.wait_for_function("() => typeof kgGraphCompletionMarkersSnapshot === 'function'")
    study = _study_controls(browser_graph)
    assert not study.locator("#kg_graph_completion_markers").is_checked()


@pytest.mark.browser
def test_concept_and_folded_module_markers_follow_read_and_question_completion(browser_graph):
    page = browser_graph.page
    initial = page.evaluate("() => kgGraphCompletionMarkersSnapshot()")
    assert initial["markers"] == []

    page.evaluate(
        """() => {
          conceptData['2.2'].content_blocks.forEach(block =>
            kgContentReadProgress.setRead(block.block_id, true)
          );
          ['2.2.q1', '2.2.q2', '2.2.q3'].forEach(questionId =>
            kgStudyProgress.recordAttempt(questionId, 'correct')
          );
        }"""
    )
    concept_marker = page.evaluate(
        """() => kgGraphCompletionMarkersSnapshot().markers.find(
          marker => marker.nodeId === '2.2'
        )"""
    )
    assert concept_marker["read"] is True
    assert concept_marker["questions"] is True
    assert concept_marker["anchor"]["kind"] == "concept"
    assert len(concept_marker["symbols"]) == 2
    blue, green = concept_marker["symbols"]
    assert blue["kind"] == "read"
    assert blue["colour"] == "#1267c4"
    assert green["kind"] == "questions"
    assert green["colour"] == "#238636"
    assert blue["x"] > green["x"]
    assert blue["y"] < green["y"]
    for symbol in concept_marker["symbols"]:
        dx = symbol["x"] - concept_marker["anchor"]["nodeX"]
        dy = symbol["y"] - concept_marker["anchor"]["nodeY"]
        radius_fraction = (dx * dx + dy * dy) ** 0.5 / concept_marker["anchor"]["nodeRadius"]
        assert radius_fraction == pytest.approx(0.88, abs=0.02)

    page.evaluate(
        """() => {
          kgContentReadProgress.setRead('test.m02_applications.overview', true);
          kgStudyProgress.recordAttempt('2.1.q1', 'correct');
        }"""
    )
    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m02_applications"]').click()
    page.locator(
        '#info_panel .module-graph-fold-button[data-module-fold-state="folded"]'
    ).click()
    module_marker = page.evaluate(
        """() => kgGraphCompletionMarkersSnapshot().markers.find(
          marker => marker.nodeId === 'module::test.m02_applications'
        )"""
    )
    assert module_marker["read"] is False
    assert module_marker["questions"] is True
    assert module_marker["anchor"]["kind"] == "module"

    page.evaluate(
        """() => {
          moduleData['test.m02_applications'].members.forEach(conceptId =>
            conceptData[conceptId].content_blocks.forEach(block =>
              kgContentReadProgress.setRead(block.block_id, true)
            )
          );
        }"""
    )
    module_marker = page.evaluate(
        """() => kgGraphCompletionMarkersSnapshot().markers.find(
          marker => marker.nodeId === 'module::test.m02_applications'
        )"""
    )
    assert module_marker["read"] is True

    page.evaluate("() => kgStudyProgress.recordAttempt('2.2.q2', 'incorrect')")
    module_marker = page.evaluate(
        """() => kgGraphCompletionMarkersSnapshot().markers.find(
          marker => marker.nodeId === 'module::test.m02_applications'
        )"""
    )
    assert module_marker["questions"] is False


@pytest.mark.browser
def test_completion_marker_snapshot_batches_graph_position_reads(browser_graph):
    page = browser_graph.page
    page.evaluate(
        """() => {
          ['2.1', '2.2'].forEach(conceptId =>
            conceptData[conceptId].content_blocks.forEach(block =>
              kgContentReadProgress.setRead(block.block_id, true)
            )
          );
        }"""
    )

    result = page.evaluate(
        """() => {
          const original = network.getPositions.bind(network);
          let calls = 0;
          network.getPositions = (...args) => {
            calls += 1;
            return original(...args);
          };
          try {
            const snapshot = kgGraphCompletionMarkersSnapshot();
            return {calls, markerCount: snapshot.markers.length};
          } finally {
            network.getPositions = original;
          }
        }"""
    )

    assert result["markerCount"] >= 2
    assert result["calls"] == 1
