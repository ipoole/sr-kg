import pytest


@pytest.mark.browser
def test_semantic_commands_drive_existing_viewer_transitions_without_history(browser_graph):
    page = browser_graph.page
    initial_url = page.url

    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "select", target: "concept:2.1"},
          {origin: "tutorial"}
        )"""
    )
    assert page.evaluate("() => kgViewerStateSnapshot().selection") == {
        "type": "concept",
        "id": "2.1",
    }
    assert page.url == initial_url

    page.evaluate(
        """() => kgExecuteViewerCommand({
          command: "set-context", preset: "uses", depth: "two-hops"
        }, {origin: "tutorial"})"""
    )
    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "set-display-scope", value: "context"},
          {origin: "tutorial"}
        )"""
    )
    state = page.evaluate("() => kgViewerStateSnapshot()")
    assert state["contextRule"]["preset"] == "uses"
    assert state["contextRule"]["depth"] == "two-hops"
    assert state["displayScope"] == "context"

    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "set-details-mode", value: "folded"},
          {origin: "tutorial"}
        )"""
    )
    assert page.locator("#kg_details_view_select").input_value() == "folded"


@pytest.mark.browser
def test_semantic_commands_control_module_representation_and_details_blocks(browser_graph):
    page = browser_graph.page

    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "select", target: "module:test.m02_applications"},
          {origin: "tutorial"}
        )"""
    )
    page.evaluate(
        """() => kgExecuteViewerCommand({
          command: "set-module-representation",
          target: "module:test.m02_applications",
          value: "folded"
        }, {origin: "tutorial"})"""
    )
    assert page.locator(
        '.module-graph-fold-button[data-module-id="test.m02_applications"]'
        '[data-module-fold-state="folded"]'
    ).get_attribute("aria-pressed") == "true"

    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "select", target: "concept:2.1"},
          {origin: "tutorial"}
        )"""
    )
    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "set-details-mode", value: "folded"},
          {origin: "tutorial"}
        )"""
    )
    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "open-details-block", target: "block:2.1.explanation"},
          {origin: "tutorial"}
        )"""
    )
    block = page.locator('[data-content-block-id="2.1.explanation"]')
    assert block.is_visible()

    page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "show-tools-section", value: "study"},
          {origin: "tutorial"}
        )"""
    )
    assert page.locator("#kg_controls").evaluate("el => !el.classList.contains('kg-hidden')")
    assert page.locator("#kg_study_section").evaluate("el => el.open")


@pytest.mark.browser
def test_semantic_command_controls_all_module_representations(browser_graph):
    page = browser_graph.page

    page.evaluate(
        """() => kgExecuteViewerCommand({
          command: "set-all-module-representations", value: "folded"
        }, {origin: "tutorial"})"""
    )
    representations = page.evaluate(
        "() => kgCaptureTutorialPresentation().moduleRepresentation"
    )
    assert representations
    assert set(representations.values()) == {"folded"}

    page.evaluate(
        """() => kgExecuteViewerCommand({
          command: "set-all-module-representations", value: "expanded"
        }, {origin: "tutorial"})"""
    )
    representations = page.evaluate(
        "() => kgCaptureTutorialPresentation().moduleRepresentation"
    )
    assert representations
    assert set(representations.values()) == {"expanded"}


@pytest.mark.browser
def test_semantic_commands_show_a_details_relationship_in_the_graph(browser_graph):
    page = browser_graph.page
    page.evaluate(
        """async () => {
          await kgExecuteViewerCommand(
            {command: "select", target: "concept:2.2"}, {origin: "tutorial"}
          );
          await kgExecuteViewerCommand(
            {command: "open-details-relationship", value: "derived-from"},
            {origin: "tutorial"}
          );
        }"""
    )
    assert page.locator("#info_panel .concept-derived-from").evaluate("el => el.open")

    page.evaluate(
        """() => kgExecuteViewerCommand({
          command: "show-relationship-in-graph",
          preset: "derivation",
          full_tree: false
        }, {origin: "tutorial"})"""
    )
    state = page.evaluate("kgViewerStateSnapshot()")
    assert state["contextRule"]["preset"] == "derivation"
    assert state["contextRule"]["depth"] == "one-hop"


@pytest.mark.browser
def test_semantic_command_previews_a_graph_concept_without_selecting(browser_graph):
    page = browser_graph.page
    selection_before = page.evaluate("kgViewerStateSnapshot().selection")

    page.evaluate(
        """() => kgExecuteViewerCommand({
          command: "show-graph-concept-hover", target: "concept:2.1"
        }, {origin: "tutorial"})"""
    )

    assert page.locator("#kg_node_tooltip").is_visible()
    assert "Beta" in page.locator("#kg_node_tooltip").inner_text()
    assert page.evaluate("kgViewerStateSnapshot().selection") == selection_before


@pytest.mark.browser
def test_semantic_command_previews_a_visible_graph_edge(browser_graph):
    page = browser_graph.page
    page.evaluate(
        """async () => {
          await kgExecuteViewerCommand({
            command: "set-all-module-representations", value: "expanded"
          }, {origin: "tutorial"});
          await kgExecuteViewerCommand({
            command: "show-graph-edge-hover", target: "edge:2.1|REQUIRES|1.1"
          }, {origin: "tutorial"});
        }"""
    )

    assert page.locator("#kg_node_tooltip").is_visible()
    assert "requires" in page.locator("#kg_node_tooltip").inner_text().lower()
    assert page.evaluate("kgContextContractionSnapshot().active") is False


@pytest.mark.browser
def test_semantic_command_rejects_unknown_or_invalid_targets(browser_graph):
    page = browser_graph.page

    message = page.evaluate(
        """() => kgExecuteViewerCommand(
          {command: "select", target: "concept:missing"},
          {origin: "tutorial"}
        ).then(() => "resolved", error => error.message)"""
    )

    assert "Unknown concept" in message
