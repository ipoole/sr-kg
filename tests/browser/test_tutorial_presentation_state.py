import pytest


@pytest.mark.browser
def test_tutorial_presentation_snapshot_restores_view_without_personal_data_changes(browser_graph):
    page = browser_graph.page

    page.evaluate(
        """async () => {
          await kgExecuteViewerCommand(
            {command: "select", target: "concept:2.1"}, {origin: "user"}
          );
          await kgExecuteViewerCommand({
            command: "set-context", preset: "uses", depth: "two-hops"
          }, {origin: "user"});
          await kgExecuteViewerCommand(
            {command: "set-display-scope", value: "context"}, {origin: "user"}
          );
          await kgExecuteViewerCommand({
            command: "set-module-representation",
            target: "module:test.m02_applications",
            value: "folded"
          }, {origin: "user"});
          await kgExecuteViewerCommand(
            {command: "set-details-mode", value: "folded"}, {origin: "user"}
          );
          await kgExecuteViewerCommand(
            {command: "show-tools-section", value: "study"}, {origin: "user"}
          );
          network.moveTo({position: {x: 140, y: -90}, scale: 0.61, animation: false});
          document.getElementById("info_panel").scrollTop = 37;
        }"""
    )
    baseline = page.evaluate("() => kgCaptureTutorialPresentation()")
    personal_before = page.evaluate("() => kgPersonalData.getSnapshot()")

    page.evaluate(
        """async snapshot => {
          await kgExecuteViewerCommand({command: "clear-selection"}, {origin: "tutorial"});
          await kgExecuteViewerCommand(
            {command: "set-display-scope", value: "full"}, {origin: "tutorial"}
          );
          await kgExecuteViewerCommand({
            command: "set-module-representation",
            target: "module:test.m02_applications",
            value: "expanded"
          }, {origin: "tutorial"});
          await kgExecuteViewerCommand(
            {command: "set-details-mode", value: "full"}, {origin: "tutorial"}
          );
          network.moveTo({position: {x: -500, y: 300}, scale: 1.2, animation: false});
          await kgRestoreTutorialPresentation(snapshot);
        }""",
        baseline,
    )

    restored = page.evaluate("() => kgCaptureTutorialPresentation()")
    personal_after = page.evaluate("() => kgPersonalData.getSnapshot()")
    assert restored["selection"] == baseline["selection"]
    assert restored["contextRule"] == baseline["contextRule"]
    assert restored["displayScope"] == baseline["displayScope"]
    assert restored["moduleRepresentation"] == baseline["moduleRepresentation"]
    assert restored["details"]["mode"] == baseline["details"]["mode"]
    assert restored["tools"] == baseline["tools"]
    assert restored["url"] == baseline["url"]
    assert restored["camera"]["scale"] == pytest.approx(baseline["camera"]["scale"])
    assert restored["camera"]["position"]["x"] == pytest.approx(
        baseline["camera"]["position"]["x"]
    )
    assert restored["camera"]["position"]["y"] == pytest.approx(
        baseline["camera"]["position"]["y"]
    )
    assert personal_after == personal_before


@pytest.mark.browser
def test_tutorial_command_replay_reconstructs_checkpoint_from_baseline(browser_graph):
    page = browser_graph.page
    baseline = page.evaluate("() => kgCaptureTutorialPresentation()")
    commands = [
        {"command": "select", "target": "concept:3.1"},
        {"command": "set-context", "preset": "foundations", "depth": "two-hops"},
        {"command": "set-display-scope", "value": "context"},
        {
            "command": "set-module-representation",
            "target": "module:test.m02_applications",
            "value": "folded",
        },
    ]

    expected = page.evaluate(
        """async args => {
          for (const command of args.commands) {
            await kgExecuteViewerCommand(command, {origin: "tutorial"});
          }
          return kgCaptureTutorialPresentation();
        }""",
        {"commands": commands},
    )
    page.evaluate(
        """async () => {
          await kgExecuteViewerCommand(
            {command: "select", target: "concept:1.1"}, {origin: "tutorial"}
          );
          await kgExecuteViewerCommand(
            {command: "set-display-scope", value: "full"}, {origin: "tutorial"}
          );
        }"""
    )

    replayed = page.evaluate(
        "args => kgReplayTutorialCommands(args.baseline, args.commands)",
        {"baseline": baseline, "commands": commands},
    )

    assert replayed["selection"] == expected["selection"]
    assert replayed["contextRule"] == expected["contextRule"]
    assert replayed["displayScope"] == expected["displayScope"]
    assert replayed["moduleRepresentation"] == expected["moduleRepresentation"]
