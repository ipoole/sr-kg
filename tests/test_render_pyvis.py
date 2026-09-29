import json
import re

import pandas as pd

from srkg.config import EDGE_WIDTH
from srkg.render_pyvis import write_pyvis_html


def _dataset(html_text: str, name: str):
    match = re.search(
        rf"{name} = new vis\.DataSet\((\[.*?\])\);",
        html_text,
        flags=re.DOTALL,
    )
    assert match is not None
    return json.loads(match.group(1))


def test_write_pyvis_html_creates_output_and_serializes_node_attributes(tmp_path):
    out_path = tmp_path / "nested" / "graph.html"
    nodes_df = pd.DataFrame([
        {"id": "1.1", "label": "Alpha <A>"},
        {"id": "2.1", "label": "Beta"},
    ])
    edges_df = pd.DataFrame([
        {"source": "2.1", "target": "1.1", "relation": "REQUIRES", "note": ""},
    ])

    write_pyvis_html(
        nodes_df=nodes_df,
        edges_df=edges_df,
        edge_key={"REQUIRES": {"directed": True}},
        edge_colour_map={"REQUIRES": "#123456"},
        hierarchy_levels={"1.1": 1, "2.1": 0},
        hierarchy_positions={"1.1": (10, 20), "2.1": (30, 40)},
        module_visuals_by_concept={
            "1.1": {"module_id": "test.foundations", "background": "#ddeeff", "border": "#224466"},
            "2.1": {"module_id": "test.applications", "background": "#ffeedd", "border": "#664422"},
        },
        out_path=out_path,
        height="400px",
        width="500px",
    )

    html_text = out_path.read_text(encoding="utf-8")
    nodes = {node["id"]: node for node in _dataset(html_text, "nodes")}

    assert out_path.exists()
    assert nodes["1.1"]["title"] == "1.1 Alpha &lt;A&gt;"
    assert nodes["1.1"]["moduleGroup"] == "test.foundations"
    assert nodes["1.1"]["level"] == 1
    assert nodes["1.1"]["x"] == 10
    assert nodes["1.1"]["y"] == 20
    assert nodes["1.1"]["visualColor"] == {"background": "#ddeeff", "border": "#224466"}
    assert nodes["2.1"]["moduleGroup"] == "test.applications"
    assert nodes["2.1"]["level"] == 0
    assert nodes["2.1"]["x"] == 30
    assert nodes["2.1"]["y"] == 40
    assert nodes["2.1"]["visualColor"] == {"background": "#ffeedd", "border": "#664422"}


def test_write_pyvis_html_serializes_directed_and_undirected_edge_attributes(tmp_path):
    out_path = tmp_path / "graph.html"
    nodes_df = pd.DataFrame([
        {"id": "1.1", "label": "Alpha"},
        {"id": "2.1", "label": "Beta"},
    ])
    edges_df = pd.DataFrame([
        {
            "source": "2.1",
            "target": "1.1",
            "relation": "REQUIRES",
            "note": "Use <carefully>",
        },
        {
            "source": "1.1",
            "target": "2.1",
            "relation": "RELATED",
            "note": "",
        },
    ])

    write_pyvis_html(
        nodes_df=nodes_df,
        edges_df=edges_df,
        edge_key={
            "REQUIRES": {"directed": True},
            "RELATED": {"directed": False},
        },
        edge_colour_map={
            "REQUIRES": "#123456",
            "RELATED": "#abcdef",
        },
        hierarchy_levels={"1.1": 1, "2.1": 0},
        hierarchy_positions={"1.1": (10, 20), "2.1": (30, 40)},
        out_path=out_path,
        height="400px",
        width="500px",
    )

    html_text = out_path.read_text(encoding="utf-8")
    edges = {
        (edge["from"], edge["to"], edge["relation"]): edge
        for edge in _dataset(html_text, "edges")
    }

    directed = edges[("2.1", "1.1", "REQUIRES")]
    undirected = edges[("1.1", "2.1", "RELATED")]
    assert directed["arrows"] == "to"
    assert directed["color"] == {
        "color": "#123456",
        "highlight": "#123456",
        "hover": "#123456",
    }
    assert directed["title"] == "Beta REQUIRES Alpha\n\nUse &lt;carefully&gt;"
    assert directed["width"] == EDGE_WIDTH
    assert undirected["arrows"] == ""
    assert undirected["color"]["color"] == "#abcdef"
    assert undirected["title"] == ""
    assert '"endPointOffset"' in html_text


def test_write_pyvis_html_does_not_enable_graph_keyboard_capture(tmp_path):
    out_path = tmp_path / "graph.html"
    nodes_df = pd.DataFrame([
        {"id": "1.1", "label": "Alpha"},
        {"id": "2.1", "label": "Beta"},
    ])
    edges_df = pd.DataFrame([
        {"source": "2.1", "target": "1.1", "relation": "REQUIRES", "note": ""},
    ])

    write_pyvis_html(
        nodes_df=nodes_df,
        edges_df=edges_df,
        edge_key={"REQUIRES": {"directed": True}},
        edge_colour_map={"REQUIRES": "#123456"},
        hierarchy_levels={"1.1": 1, "2.1": 0},
        hierarchy_positions={"1.1": (10, 20), "2.1": (30, 40)},
        out_path=out_path,
        height="400px",
        width="500px",
    )

    html_text = out_path.read_text(encoding="utf-8")

    assert '"keyboard": false' in html_text
    assert '"keyboard": true' not in html_text


def test_write_pyvis_html_uses_fallbacks_for_unknown_module_position_and_relation(tmp_path):
    out_path = tmp_path / "graph.html"
    nodes_df = pd.DataFrame([
        {"id": "appendix", "label": "Appendix"},
        {"id": "1.1", "label": "Alpha"},
    ])
    edges_df = pd.DataFrame([
        {
            "source": "appendix",
            "target": "1.1",
            "relation": "UNKNOWN",
            "note": "",
        },
    ])

    write_pyvis_html(
        nodes_df=nodes_df,
        edges_df=edges_df,
        edge_key={},
        edge_colour_map={},
        hierarchy_levels={"1.1": 0},
        hierarchy_positions={"1.1": (25, 50)},
        out_path=out_path,
        height="400px",
        width="500px",
    )

    html_text = out_path.read_text(encoding="utf-8")
    nodes = {node["id"]: node for node in _dataset(html_text, "nodes")}
    edges = _dataset(html_text, "edges")

    assert nodes["appendix"]["moduleGroup"] == ""
    assert nodes["appendix"]["level"] == 0
    assert nodes["appendix"]["x"] == 0
    assert nodes["appendix"]["y"] == 0
    assert nodes["appendix"]["visualColor"] == {
        "background": "#e4e7eb",
        "border": "#59636e",
    }
    assert edges[0]["arrows"] == "to"
    assert re.fullmatch(r"#[0-9a-f]{6}", edges[0]["color"]["color"])
