from pathlib import Path

import pytest

from srkg.tutorials import TutorialLoadError, load_tutorials


CONCEPT_IDS = {"sr.alpha", "gr.beta"}
MODULE_IDS = {"sr.foundations", "gr.curvature"}
BLOCK_IDS = {"sr.alpha.definition", "gr.beta.explanation"}


def _write_tutorials(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_load_tutorials_returns_ordered_viewer_data(tmp_path):
    path = _write_tutorials(
        tmp_path / "tutorials.yaml",
        """
schema_version: 1
tutorials:
  - tutorial_id: spacetime-route
    title: From spacetime onwards
    category: physics
    summary: Follow one short route.
    sequence: 20
    domains: [sr]
    steps:
      - step_id: select-alpha
        title: Begin with Alpha
        commentary: Start with the first concept.
        action:
          command: select
          target: concept:sr.alpha
        pointer:
          target: graph:concept:sr.alpha
      - step_id: show-definition
        title: Read its definition
        commentary: The details pane contains authored blocks.
        prepare:
          - command: set-details-mode
            value: full
        action:
          command: open-details-block
          target: block:sr.alpha.definition
        pointer:
          target: details:block:sr.alpha.definition
      - step_id: find-alpha
        title: Search for Alpha
        commentary: Search locates concepts and modules.
        action:
          command: search
          query: Alpha
        pointer:
          target: control:search
      - step_id: choose-alpha
        title: Choose Alpha
        commentary: Choose the matching result.
        action:
          command: select
          target: concept:sr.alpha
        pointer:
          target: search:concept:sr.alpha
      - step_id: close-search
        title: Return to Details
        commentary: Close Search to see the selected concept.
        action:
          command: close-search
        pointer:
          target: control:search-input
  - tutorial_id: viewer-tour
    title: Using PhysicsKG
    category: interface
    summary: Learn the main controls.
    sequence: 10
    domains: [sr, gr]
    steps:
      - step_id: foundations
        title: Choose a context
        commentary: Foundations follows the supporting relationships.
        action:
          command: set-context
          preset: foundations
          depth: one-hop
        pointer:
          target: control:context
""",
    )

    tutorials = load_tutorials(
        path,
        concept_ids=CONCEPT_IDS,
        module_ids=MODULE_IDS,
        block_ids=BLOCK_IDS,
    )

    assert [tutorial.tutorial_id for tutorial in tutorials] == [
        "viewer-tour",
        "spacetime-route",
    ]
    assert tutorials[1].steps[0].action == {
        "command": "select",
        "target": "concept:sr.alpha",
    }
    assert tutorials[1].to_viewer_data()["steps"][1]["prepare"] == [
        {"command": "set-details-mode", "value": "full"},
    ]


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("schema_version: 2\ntutorials: []\n", "unsupported schema_version"),
        (
            """
schema_version: 1
tutorials:
  - tutorial_id: duplicate
    title: One
    category: interface
    summary: First.
    sequence: 10
    domains: [sr]
    steps:
      - step_id: start
        title: Start
        commentary: Start here.
        action: {command: clear-selection}
  - tutorial_id: duplicate
    title: Two
    category: interface
    summary: Second.
    sequence: 20
    domains: [sr]
    steps:
      - step_id: start
        title: Start
        commentary: Start here.
        action: {command: clear-selection}
""",
            "Duplicate tutorial id.*duplicate",
        ),
        (
            """
schema_version: 1
tutorials:
  - tutorial_id: bad-concept
    title: Bad concept
    category: physics
    summary: Invalid target.
    sequence: 10
    domains: [sr]
    steps:
      - step_id: start
        title: Start
        commentary: Start here.
        action: {command: select, target: concept:missing}
""",
            "unknown concept.*missing",
        ),
        (
            """
schema_version: 1
tutorials:
  - tutorial_id: bad-command
    title: Bad command
    category: interface
    summary: Invalid command.
    sequence: 10
    domains: [sr]
    steps:
      - step_id: start
        title: Start
        commentary: Start here.
        action: {command: click-anywhere, target: concept:sr.alpha}
""",
            "unsupported command.*click-anywhere",
        ),
        (
            """
schema_version: 1
tutorials:
  - tutorial_id: duplicate-step
    title: Duplicate step
    category: interface
    summary: Duplicate step ids.
    sequence: 10
    domains: [sr]
    steps:
      - step_id: same
        title: First
        commentary: First step.
        action: {command: clear-selection}
      - step_id: same
        title: Second
        commentary: Second step.
        action: {command: clear-selection}
""",
            "Duplicate step id.*same",
        ),
        (
            """
schema_version: 1
tutorials:
  - tutorial_id: bad-pointer
    title: Bad pointer
    category: interface
    summary: Invalid pointer target.
    sequence: 10
    domains: [sr]
    steps:
      - step_id: start
        title: Start
        commentary: Start here.
        action: {command: clear-selection}
        pointer: {target: graph:concept:missing}
""",
            "pointer target references unknown concept.*missing",
        ),
    ],
)
def test_load_tutorials_rejects_invalid_routes(tmp_path, body, message):
    path = _write_tutorials(tmp_path / "tutorials.yaml", body)

    with pytest.raises(TutorialLoadError, match=message):
        load_tutorials(
            path,
            concept_ids=CONCEPT_IDS,
            module_ids=MODULE_IDS,
            block_ids=BLOCK_IDS,
        )


def test_load_tutorials_returns_empty_tuple_when_file_is_absent(tmp_path):
    tutorials = load_tutorials(
        tmp_path / "missing.yaml",
        concept_ids=CONCEPT_IDS,
        module_ids=MODULE_IDS,
        block_ids=BLOCK_IDS,
    )

    assert tutorials == ()
