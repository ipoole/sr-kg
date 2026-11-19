"""Fit++ drags are portable commands, not persistent layout edits."""
import pytest
from playwright.sync_api import expect
from test_personal_tutorials import tutorial_graph, _library, _record, _saved
from test_tutorial_recording import _start, _idle


def _positions(page, ids):
    return page.evaluate('ids=>Object.fromEntries(ids.map(id=>[id,{x:network.body.nodes[id].x,y:network.body.nodes[id].y}]))', ids)


def _mouse_drag(page, node, dx, dy):
    point = page.evaluate("""id=>{
      const node=network.body.nodes[id],p=network.canvasToDOM({x:node.x,y:node.y});
      const r=document.querySelector('#mynetwork canvas').getBoundingClientRect();
      return {x:r.left+p.x,y:r.top+p.y};
    }""", node)
    page.mouse.move(point['x'], point['y'])
    page.mouse.down()
    page.mouse.move(point['x'] + dx, point['y'] + dy, steps=5)
    page.mouse.up()
    _idle(page)
    return _positions(page, [node])[node]


@pytest.mark.browser
@pytest.mark.parametrize('width,kind', [(390, 'concept'), (1280, 'module'), (1280, 'anchor'), (390, 'folded-anchor')])
def test_recorded_fitpp_drag_replays_undoes_and_round_trips(tutorial_graph, width, kind):
    page = _library(tutorial_graph)
    page.set_viewport_size({'width': width, 'height': 900})
    personal = page.evaluate('kgPersonalData.getSnapshot()')
    layout = page.evaluate('kgGlobalLayoutSnapshot()')
    tutorial_id = _start(page)
    commands = [
        {'command': 'set-view', 'value': 'graph'},
        {'command': 'set-all-module-representations', 'value': 'expanded'},
        {'command': 'select', 'target': 'concept:3.1'},
        {'command': 'set-context', 'preset': 'foundations', 'depth': 'two-hops'},
        {'command': 'set-display-scope', 'value': 'context'},
    ]
    if kind == 'module':
        commands.append({'command': 'set-module-representation', 'target': 'module:test.m01_foundations', 'value': 'folded'})
    if kind == 'folded-anchor':
        commands.append({'command': 'set-module-representation', 'target': 'module:test.m02_applications', 'value': 'folded'})
    commands += [{'command': 'fit', 'value': 'context'}] * 2
    for command in commands:
        page.evaluate('c=>kgExecuteViewerCommand(c,{pointer:"narration"})', command)
        _idle(page)
    anchor = page.evaluate('kgContextContractionSnapshot().anchorId')
    node = {'concept': '2.1', 'module': 'module::test.m01_foundations', 'anchor': anchor, 'folded-anchor': '1.1'}[kind]
    original = _positions(page, [node, anchor])
    destination = {axis: original[node][axis] + delta for axis, delta in [('x', 83.25), ('y', -47.5)]}
    for _ in range(2):
        # A duplicate drop without movement must not add an action.
        page.evaluate('id=>network.emit("dragEnd",{nodes:[id]})', node)
        _idle(page)
    if kind == 'concept':
        destination = _mouse_drag(page, node, 24, -18)
        assert destination != original[node]
    else:
        page.evaluate('''({node,destination})=>{
          network.moveNode(node,destination.x,destination.y);
          network.emit('dragEnd',{nodes:[node]});
        }''', {'node': node, 'destination': destination})
        _idle(page)
    assert _positions(page, [node])[node] == pytest.approx(destination)
    page.locator('#kg_tutorial_recording_undo').click(); _idle(page)
    assert _positions(page, [node])[node] == pytest.approx(original[node])
    page.locator('#kg_tutorial_recording_redo').click(); _idle(page)
    assert _positions(page, [node])[node] == pytest.approx(destination)
    if kind == 'concept':
        previous = destination
        destination = _mouse_drag(page, node, -15, 12)
        assert destination != previous
        page.locator('#kg_tutorial_recording_undo').click(); _idle(page)
        assert _positions(page, [node])[node] == pytest.approx(previous)
        page.locator('#kg_tutorial_recording_redo').click(); _idle(page)
        assert _positions(page, [node])[node] == pytest.approx(destination)
    page.locator('#kg_tutorial_recording_finish').click()
    record = _record(page, tutorial_id)
    moves = [i['action'] for i in record['route']['steps'][0]['actions'] if i['action']['command'] == 'place-context-node']
    assert len(moves) == (2 if kind == 'concept' else 1)
    move = moves[-1]
    assert move['target'] == ('module:test.m01_foundations' if kind == 'module' else 'concept:' + node)
    assert move['anchor'] == ('module:test.m02_applications' if kind == 'folded-anchor' else 'concept:3.1')
    for axis in ['x', 'y']:
        assert move[axis] == pytest.approx(destination[axis] - original[anchor][axis])
    assert page.evaluate('''id=>{
      const p=kgTutorialPortable,r=kgPersonalData.tutorials;
      return r.get(id).then(record=>[p.importSingle(p.exportSingle(record,true)),p.importSingle(p.exportSingle(record,false))]);
    }''', tutorial_id) == [record, record]
    if kind == 'concept':
        page.locator('#kg_tutorial_editor_card_controls [data-card-action="add"]').click()
        page.locator('#kg_tutorial_editor_card_title').fill('Inspect the arrangement')
        page.locator('#kg_tutorial_editor_commentary').fill('The preceding card has arranged this context.')
        _saved(page)
    # A new viewport changes the camera, not the recorded graph coordinates.
    page.set_viewport_size({'width': 1280 if width == 390 else 390, 'height': 844})
    page.locator('#kg_tutorial_editor_from').click()
    page.wait_for_function('i=>kgTutorialPlaybackSnapshot().stepIndex===i&&!kgTutorialPlaybackSnapshot().transitioning',arg=1 if kind=='concept' else 0)
    expect(page.locator('#kg_tutorial_error')).to_be_hidden()
    assert _positions(page, [node])[node] == pytest.approx(destination)
    assert page.evaluate('kgGlobalLayoutSnapshot()') == layout
    if kind == 'concept':
        page.locator('#kg_tutorial_back').click()
        page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===0&&!kgTutorialPlaybackSnapshot().transitioning')
        assert _positions(page, [node])[node] == pytest.approx(destination)
        expect(page.locator('#kg_tutorial_error')).to_be_hidden()
        page.locator('#kg_tutorial_next').click()
        page.wait_for_function('kgTutorialPlaybackSnapshot().stepIndex===1&&!kgTutorialPlaybackSnapshot().transitioning')
    page.locator('#kg_tutorial_explore').click()
    page.evaluate("kgExecuteViewerCommand({command:'select',target:'concept:2.2'})")
    page.locator('#kg_tutorial_explore').click()
    page.wait_for_function('!kgTutorialPlaybackSnapshot().transitioning')
    assert _positions(page, [node])[node] == pytest.approx(destination)
    page.locator('#kg_tutorial_exit').click()
    assert page.evaluate('kgGlobalLayoutSnapshot()') == layout
    assert page.evaluate('kgPersonalData.getSnapshot()') == personal
    assert not tutorial_graph.page_errors


@pytest.mark.browser
def test_placement_requires_matching_active_fitpp_context(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async()=>{
      const before=kgGlobalLayoutSnapshot();
      try { await kgExecuteViewerCommand({command:'place-context-node',target:'concept:2.1',anchor:'concept:3.1',x:4,y:5}); }
      catch(error) { return {rejected:true,unchanged:JSON.stringify(before)===JSON.stringify(kgGlobalLayoutSnapshot())}; }
      return {rejected:false};
    }''')
    assert result == {'rejected': True, 'unchanged': True}


@pytest.mark.browser
def test_active_placement_rejects_wrong_anchor_outside_nodes_and_invalid_offsets(tutorial_graph):
    page = _library(tutorial_graph)
    result = page.evaluate('''async()=>{
      for(const command of [
        {command:'set-all-module-representations',value:'expanded'},
        {command:'select',target:'concept:3.1'},
        {command:'set-context',preset:'derivation',depth:'one-hop'},
        {command:'fit',value:'context'}, {command:'fit',value:'context'}
      ]) await kgExecuteViewerCommand(command);
      const before=kgCaptureTutorialPresentation(),layout=kgGlobalLayoutSnapshot();
      let rejected=0;
      for(const fields of [
        {anchor:'concept:2.2'}, {target:'concept:2.1'}, {x:NaN}, {y:10000001}
      ]) {
        try { await kgExecuteViewerCommand(Object.assign({command:'place-context-node',
          target:'concept:2.2',anchor:'concept:3.1',x:10,y:20},fields)); }
        catch(error) { rejected++; }
      }
      return {rejected,positionsUnchanged:JSON.stringify(before.contextFit)===JSON.stringify(kgCaptureTutorialPresentation().contextFit),
        layoutUnchanged:JSON.stringify(layout)===JSON.stringify(kgGlobalLayoutSnapshot())};
    }''')
    assert result == {'rejected': 4, 'positionsUnchanged': True, 'layoutUnchanged': True}
