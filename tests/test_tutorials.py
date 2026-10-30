from pathlib import Path

import pytest

from srkg.tutorials import TutorialLoadError, load_tutorials


CONCEPT_IDS = {"sr.alpha", "gr.beta"}
MODULE_IDS = {"sr.foundations", "gr.curvature"}
BLOCK_IDS = {"sr.alpha.definition", "gr.beta.explanation"}


def test_physics_routes_start_with_quiet_introduction():
    import yaml

    routes = yaml.safe_load((Path(__file__).parents[1] / "data/tutorials.yaml").read_text())["tutorials"]
    for route in routes:
        if route["category"] != "physics":
            continue
        intro = route["steps"][0]
        assert intro["action"] == {"command": "wait", "milliseconds": 0}
        assert not intro.get("actions")
        assert not intro.get("prepare")
        assert not intro.get("pointer")


def _sequence_route(actions, extra=""):
    return f"""schema_version: 1
tutorials:
  - tutorial_id: sequence
    title: A sequence
    category: interface
    summary: One card with several visible actions.
    sequence: 1
    domains: [sr]
    steps:
      - step_id: overview
        title: Set up an overview
        commentary: Watch the controls.
        {extra}
        actions: {actions}
"""


def test_load_visible_action_sequence(tmp_path):
    path = _write_tutorials(tmp_path / "tutorials.yaml", _sequence_route("""
          - action: {command: select, target: 'concept:sr.alpha'}
            pointer: {target: 'graph:concept:sr.alpha'}
            pause_ms: 3000
          - action: {command: expand-context-modules}
            pointer: {target: 'control:expand-context'}
          - action: {command: fit, value: context}
            pointer: {target: 'control:fit'}
    """))
    route = load_tutorials(path, concept_ids=CONCEPT_IDS,
                           module_ids=MODULE_IDS, block_ids=BLOCK_IDS)[0].to_viewer_data()
    actions = route["steps"][0]["actions"]
    assert len(actions) == 3
    assert actions[0]["pause_ms"] == 3000
    assert actions[1]["pause_ms"] == 500
    assert actions[1]["action"]["command"] == "expand-context-modules"
    assert "action" not in route["steps"][0]


@pytest.mark.parametrize("actions,extra", [
    ("[]", ""),
    ("[{action: {command: select, target: concept:sr.alpha}, pause_ms: -1}]", ""),
    ("[{action: {command: select, target: concept:sr.alpha}, pause_ms: 5001}]", ""),
    ("[{action: {command: select, target: concept:sr.alpha}}]", "action: {command: select, target: concept:sr.alpha}"),
    ("[{action: {command: select, target: 'concept:missing'}}]", ""),
    ("[{action: {command: select, target: concept:sr.alpha}, pointer: {target: 'control:missing'}}]", ""),
])
def test_reject_invalid_visible_action_sequence(tmp_path, actions, extra):
    path = _write_tutorials(tmp_path / "tutorials.yaml", _sequence_route(actions, extra))
    with pytest.raises(TutorialLoadError):
        load_tutorials(path, concept_ids=CONCEPT_IDS,
                       module_ids=MODULE_IDS, block_ids=BLOCK_IDS)


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
          - command: set-view
            value: both
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
      - step_id: questions
        title: Check your understanding
        commentary: Explore to attempt a question.
        action:
          command: open-study-questions
        pointer:
          target: details:study-questions
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
        {"command": "set-view", "value": "both"},
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
        action: {command: select, target: concept:sr.alpha}
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
        action: {command: select, target: concept:sr.alpha}
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
        action: {command: select, target: concept:sr.alpha}
      - step_id: same
        title: Second
        commentary: Second step.
        action: {command: select, target: concept:sr.alpha}
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
        action: {command: select, target: concept:sr.alpha}
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
