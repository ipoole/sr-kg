from pathlib import Path

import pytest

from srkg.tutorials import TutorialLoadError, load_tutorials


CONCEPT_IDS = {"sr.alpha", "gr.beta"}
MODULE_IDS = {"sr.foundations", "gr.curvature"}
BLOCK_IDS = {"sr.alpha.definition", "gr.beta.explanation"}


def test_physics_routes_start_with_quiet_introduction():
    from srkg.kb import load_knowledge_base
    routes = load_knowledge_base(Path(__file__).parents[1] / "data", include_graphics=False).tutorials
    physics = [route for route in routes if route.category == "physics"]
    assert physics
    for route in physics:
        intro = route.steps[0]
        assert intro.action == {"command": "wait", "milliseconds": 0}
        assert not intro.actions
        assert not intro.prepare
        assert not intro.pointer_target


def test_built_in_cards_use_explicit_whole_card_visibility():
    from srkg.kb import load_knowledge_base
    routes = load_knowledge_base(Path(__file__).parents[1] / "data", include_graphics=False).tutorials
    for route in routes:
        for step in route.steps:
            assert isinstance(step.demonstrate, bool), (route.tutorial_id, step.step_id)
            assert not step.prepare, (route.tutorial_id, step.step_id)
        if route.category == "physics":
            assert all(step.demonstrate is False for step in route.steps)


def test_built_in_reading_cards_target_the_selected_concept():
    from srkg.kb import load_knowledge_base
    routes = load_knowledge_base(Path(__file__).parents[1] / "data", include_graphics=False).tutorials
    for route in routes:
        selected = None
        for step in route.steps:
            commands = [item["action"] for item in step.actions] if step.actions else [step.action]
            for command in commands:
                if command["command"] == "select":
                    selected = command["target"]
                elif command["command"] == "open-details-block":
                    owner = command["target"].removeprefix("block:").rsplit(".", 1)[0]
                    assert selected == f"concept:{owner}", (route.tutorial_id, step.step_id)


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
          depth: three-hops
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
    assert tutorials[0].steps[0].action["depth"] == "three-hops"
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


@pytest.mark.parametrize('recipe,target,depth', [('teaching','sr.alpha','three-hops'), ('derivation','gr.beta','transitive')])
def test_reading_tree_action_validation(tmp_path, recipe, target, depth):
    action = f'{{command: open-reading-tree, recipe: {recipe}, target: "concept:{target}", depth: {depth}, synchronise: true}}'
    path = _write_tutorials(tmp_path/'reading.yaml', _sequence_route('[{action: '+action+', pointer: {target: "details:reading-tree:'+recipe+'"}}]'))
    routes = load_tutorials(path,concept_ids=CONCEPT_IDS,module_ids=MODULE_IDS,block_ids=BLOCK_IDS)
    assert routes[0].steps[0].actions[0]['action']['synchronise'] is True
    path.write_text(path.read_text().replace('recipe: '+recipe, 'recipe: unknown'))
    with pytest.raises(TutorialLoadError):
        load_tutorials(path,concept_ids=CONCEPT_IDS,module_ids=MODULE_IDS,block_ids=BLOCK_IDS)


def test_editor_command_contract_and_python_validator_accept_the_same_fields(tmp_path):
    """Exercise every editor command, including optional fields, through the public loader."""
    import yaml
    from srkg.tutorial_contract import authoring_contract

    contract = authoring_contract()
    target = {'object':'concept:sr.alpha', 'concept':'concept:sr.alpha',
              'module':'module:sr.foundations', 'block':'block:sr.alpha.definition',
              'edge':'edge:sr.alpha|DERIVES_FROM|gr.beta', 'text':'Alpha'}
    steps = []
    for name, spec in contract['commands'].items():
        command = {'command':name}
        for field in spec['fields']:
            kind = field['type']
            if kind == 'enum':
                command[field['name']] = next(iter(field['choices']))
            elif kind == 'boolean':
                command[field['name']] = False
            elif kind in {'integer', 'number'}:
                command[field['name']] = field['min']
            else:
                command[field['name']] = target[kind]
        steps.append({'step_id':name, 'title':name, 'commentary':'Read this card.', 'action':command})
    document = {'schema_version':1, 'tutorials':[{'tutorial_id':'commands', 'title':'Commands',
                'summary':'A contract exercise.', 'category':'interface', 'sequence':1,
                'domains':['sr'], 'steps':steps}]}
    path = tmp_path / 'tutorials.yaml'
    path.write_text(yaml.safe_dump(document))
    route = load_tutorials(path, concept_ids=CONCEPT_IDS, module_ids=MODULE_IDS, block_ids=BLOCK_IDS)[0]
    assert [step.action for step in route.steps] == [step['action'] for step in steps]
    for index, step in enumerate(steps):
        descriptor = contract['commands'][step['action']['command']]
        for field in descriptor['fields']:
            original = step['action'][field['name']]
            step['action'][field['name']] = {'enum':'unknown', 'boolean':0, 'integer':-1, 'number':10000001, 'text':'x' * 201}.get(field['type'], '')
            path.write_text(yaml.safe_dump(document))
            with pytest.raises(TutorialLoadError):
                load_tutorials(path, concept_ids=CONCEPT_IDS, module_ids=MODULE_IDS, block_ids=BLOCK_IDS)
            step['action'][field['name']] = original


@pytest.mark.parametrize('demonstrate',[False,True])
def test_optional_card_demonstration_flag_survives_loading(tmp_path,demonstrate):
    path=_write_tutorials(tmp_path/'tutorials.yaml',_sequence_route('[{action: {command: wait, milliseconds: 0}}]',extra='demonstrate: '+str(demonstrate).lower()))
    route=load_tutorials(path,concept_ids=CONCEPT_IDS,module_ids=MODULE_IDS,block_ids=BLOCK_IDS)[0]
    assert route.to_viewer_data()['steps'][0]['demonstrate'] is demonstrate


@pytest.mark.parametrize('value',['"false"','1','null'])
def test_card_demonstration_flag_rejects_non_booleans(tmp_path,value):
    path=_write_tutorials(tmp_path/'tutorials.yaml',_sequence_route('[{action: {command: wait, milliseconds: 0}}]',extra='demonstrate: '+value))
    with pytest.raises(TutorialLoadError):
        load_tutorials(path,concept_ids=CONCEPT_IDS,module_ids=MODULE_IDS,block_ids=BLOCK_IDS)


@pytest.mark.parametrize('coordinate', [float('nan'), float('inf'), -float('inf'), True, '12', 10000001])
def test_reject_invalid_node_placement_coordinates(tmp_path, coordinate):
    import yaml
    action = {'command': 'place-context-node', 'target': 'concept:sr.alpha',
              'anchor': 'module:sr.foundations', 'x': coordinate, 'y': -12.5}
    path = _write_tutorials(tmp_path / 'tutorials.yaml', _sequence_route(yaml.safe_dump([{'action': action}], default_flow_style=True)))
    with pytest.raises(TutorialLoadError):
        load_tutorials(path, concept_ids=CONCEPT_IDS, module_ids=MODULE_IDS, block_ids=BLOCK_IDS)


def test_node_placement_preserves_signed_fractional_graph_offsets(tmp_path):
    import yaml
    action = {'command': 'place-context-node', 'target': 'concept:sr.alpha',
              'anchor': 'module:sr.foundations', 'x': 83.25, 'y': -47.5}
    path = _write_tutorials(tmp_path / 'tutorials.yaml', _sequence_route(yaml.safe_dump([{'action': action}], default_flow_style=True)))
    route = load_tutorials(path, concept_ids=CONCEPT_IDS, module_ids=MODULE_IDS, block_ids=BLOCK_IDS)[0]
    assert route.steps[0].actions[0]['action'] == action


@pytest.mark.parametrize('omit', [False, True])
def test_summary_and_narration_are_optional(tmp_path, omit):
    import yaml
    document = yaml.safe_load(_sequence_route('[{action: {command: wait, milliseconds: 0}}]'))
    route = document['tutorials'][0]
    if omit:
        route.pop('summary')
        route['steps'][0].pop('commentary')
    else:
        route['summary'] = ''
        route['steps'][0]['commentary'] = ''
    path = _write_tutorials(tmp_path / 'tutorials.yaml', yaml.safe_dump(document))
    loaded = load_tutorials(path, concept_ids=CONCEPT_IDS, module_ids=MODULE_IDS, block_ids=BLOCK_IDS)[0]
    assert loaded.summary == ''
    assert loaded.steps[0].commentary == ''
