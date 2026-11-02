from pathlib import Path
import pytest

ASSETS = Path(__file__).resolve().parents[2] / "srkg/viewer_assets"


@pytest.fixture
def algorithms_page(playwright_browser):
    _, browser = playwright_browser
    page = browser.new_page()
    page.add_script_tag(path=str(ASSETS / "graph_model.js"))
    page.add_script_tag(path=str(ASSETS / "vis_network_adapter.js"))
    yield page
    page.close()


@pytest.mark.browser
@pytest.mark.parametrize("depth,expected", [
    ("one-hop", ["a", "b"]),
    ("two-hops", ["a", "b", "c"]),
    ("transitive", ["a", "b", "c"]),
])
def test_context_depth_handles_cycles_and_invalid_endpoints(algorithms_page, depth, expected):
    result = algorithms_page.evaluate("""depth => {
      const graph = [
        {id:'ab',from:'a',to:'b',relation:'REQUIRES'},
        {id:'bc',from:'b',to:'c',relation:'REQUIRES'},
        {id:'ca',from:'c',to:'a',relation:'REQUIRES'},
        {id:'bad',from:'a',to:'missing',relation:'REQUIRES'}
      ];
      const before = JSON.stringify(graph);
      const result = kgGraphModel.computeContextSubgraph(['a','a'],
        {preset:'prerequisites',depth}, graph, {REQUIRES:{directed:true}},
        {a:true,b:true,c:true});
      return {result,unchanged:before===JSON.stringify(graph)};
    }""", depth)
    assert result["result"]["nodeIds"] == expected
    assert "bad" not in result["result"]["edgeIds"]
    assert result["unchanged"]


@pytest.mark.browser
def test_custom_traversal_supports_reverse_and_undirected_relations(algorithms_page):
    assert algorithms_page.evaluate("""() => kgGraphModel.computeContextSubgraph(['b'],
      {preset:'custom',depth:'one-hop',customTraversals:[
        {relation:'DERIVES_FROM',direction:'incoming'},
        {relation:'RELATED',direction:'undirected'}]},
      [{id:'ab',from:'a',to:'b',relation:'DERIVES_FROM'},
       {id:'bc',from:'b',to:'c',relation:'RELATED'},
       {id:'db',from:'d',to:'b',relation:'REQUIRES'}],
      {DERIVES_FROM:{directed:true},RELATED:{directed:false}}, {})
      .nodeIds""") == ["a", "b", "c"]


@pytest.mark.browser
def test_folded_boundary_groups_preserve_directions_counts_and_flags(algorithms_page):
    groups = algorithms_page.evaluate("""() => {
      const graph = [
        {id:'e2',from:'a',to:'c',relation:'REQUIRES'},
        {id:'e1',from:'b',to:'c',relation:'DERIVES_FROM'},
        {id:'internal',from:'a',to:'b',relation:'REQUIRES'},
        {id:'hidden',from:'a',to:'d',relation:'REQUIRES'},
        {id:'reverse',from:'c',to:'a',relation:'REQUIRES'},
        {id:'ordinary',from:'c',to:'d',relation:'RELATED'}];
      const rendered = Object.fromEntries(graph.map(edge=>[edge.id,{...edge}]));
      rendered.hidden.hidden=true;
      rendered.e2.kgContextEdge=true;
      rendered.e1.kgOverviewEdge=true;
      return kgGraphModel.groupBoundaryEdges(graph,rendered,
        {a:'module::m',b:'module::m',c:'c',d:'d'}, {a:true,b:true},'boundary::');
    }""")
    assert len(groups) == 2
    forward = next(group for group in groups if group["from"] == "module::m")
    reverse = next(group for group in groups if group["from"] == "c")
    assert forward["edgeIds"] == ["e1", "e2"]
    assert forward["relationCounts"] == {"REQUIRES": 1, "DERIVES_FROM": 1}
    assert forward["contextEdge"] and forward["overviewEdge"]
    assert reverse["edgeIds"] == ["reverse"]


@pytest.mark.browser
def test_contraction_hops_keep_all_shortest_parent_candidates(algorithms_page):
    result = algorithms_page.evaluate("""() => kgGraphModel.contractionGraphPlan({
      anchorId:'a',adjacency:{a:['c','b'],b:['a','d'],c:['a','d'],d:['b','c'],z:[]}
    })""")
    assert result["depthByNode"] == {"a": 0, "b": 1, "c": 1, "d": 2}
    assert result["parentCandidates"]["d"] == ["b", "c"]
    assert result["maximumDepth"] == 2


@pytest.mark.browser
def test_vis_adapter_preserves_precise_positions_and_draw_only_widths(algorithms_page):
    result = algorithms_page.evaluate("""() => {
      const node={x:1.125,y:-2.875,shape:{left:-5,top:-6,width:12,height:14}};
      const edge={options:{width:1},edgeType:{getPoint:t=>({x:t,y:4})}};
      const network={body:{nodes:{a:node},edges:{e:edge}},
        canvas:{frame:{canvas:{id:'surface'}}},getPositions:()=>({fallback:{x:5,y:6}})};
      const adapter=kgCreateVisNetworkAdapter(network);
      adapter.setDrawnEdgeWidth('e',3);
      return {position:adapter.precisePosition('a'),fallback:adapter.precisePosition('fallback'),
        geometry:adapter.nodeGeometry('a'),point:adapter.edgePoint('e',0.5),
        width:edge.options.width,canvas:adapter.canvasElement().id,
        missing:adapter.nodeGeometry('missing'),missingEdge:adapter.edgePoint('missing',0.5)};
    }""")
    assert result["position"] == {"x": 1.125, "y": -2.875}
    assert result["fallback"] == {"x": 5, "y": 6}
    assert result["geometry"] == {"left": -5, "top": -6, "width": 12, "height": 14}
    assert result["point"] == {"x": 0.5, "y": 4}
    assert result["width"] == 3
    assert result["canvas"] == "surface"
    assert result["missing"] is None and result["missingEdge"] is None
