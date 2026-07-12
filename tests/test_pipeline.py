import pandas as pd
import pytest

from srkg.pipeline import generate_viewer


def _write_minimal_nodes(path):
    pd.DataFrame([
        {
            "id": "1.1",
            "label": "Alpha",
            "layer": "1",
            "layer_title": "Foundations",
            "definition_new": "Definition with </script> marker",
            "derivation_new": "",
            "explanation_new": "",
        },
        {
            "id": "2.1",
            "label": "Beta",
            "layer": "2",
            "layer_title": "Next",
            "definition_new": "",
            "derivation_new": "",
            "explanation_new": "",
        },
    ]).to_csv(path, index=False)


def test_generate_viewer_runs_full_pipeline_and_injects_controls(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    out_path = tmp_path / "out" / "viewer.html"
    _write_minimal_nodes(nodes_path)
    pd.DataFrame([
        {
            "source": "2.1",
            "target": "1.1",
            "relation": "EXPLAINS",
            "note": "Read after Alpha",
        },
        {
            "source": "1.1",
            "target": "2.1",
            "relation": "",
            "note": "",
        },
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {
            "relation": "EXPLAINS",
            "directed": "false",
            "category": "teaching",
            "meaning": "source explains target",
            "example": "B explains A",
        },
    ]).to_csv(edge_key_path, index=False)

    result = generate_viewer(
        nodes_path=str(nodes_path),
        edges_path=str(edges_path),
        edge_key_path=None,
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="SR <Graph>",
    )

    html_text = out_path.read_text(encoding="utf-8")
    assert result == (out_path, 2, 2, edge_key_path, 1)
    assert '<div id="kg_view_title">SR &lt;Graph&gt;</div>' in html_text
    assert 'id="kg_controls"' in html_text
    assert "var conceptData = " in html_text
    assert "Definition with <\\/script> marker" in html_text
    assert '"relation": "REFERENCE"' in html_text
    assert '"relation": "EXPLAINS"' in html_text
    assert '"directed": false' in html_text
    assert '"colour":' in html_text
    assert '"arrows": ""' in html_text


def test_generate_viewer_loads_optional_graphic_design_captions(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    out_path = tmp_path / "viewer.html"
    _write_minimal_nodes(nodes_path)
    pd.DataFrame([
        {
            "source": "2.1",
            "target": "1.1",
            "relation": "EXPLAINS",
            "note": "",
        },
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {
            "relation": "EXPLAINS",
            "directed": "true",
            "category": "",
            "meaning": "",
            "example": "",
        },
    ]).to_csv(edge_key_path, index=False)
    pd.DataFrame([
        {
            "id": "1.1",
            "icon_caption": "Icon caption",
            "detail_caption": "Detail caption",
        },
    ]).to_csv(tmp_path / "concept_graphic_designs.csv", index=False)

    generate_viewer(
        nodes_path=str(nodes_path),
        edges_path=str(edges_path),
        edge_key_path=str(edge_key_path),
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="Title",
    )

    html_text = out_path.read_text(encoding="utf-8")
    assert '"svg_icon_caption": "Icon caption"' in html_text
    assert '"svg_detail_caption": "Detail caption"' in html_text


def test_generate_viewer_rejects_edges_with_unknown_endpoints(tmp_path):
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    out_path = tmp_path / "viewer.html"
    _write_minimal_nodes(nodes_path)
    pd.DataFrame([
        {
            "source": "2.1",
            "target": "missing",
            "relation": "EXPLAINS",
            "note": "",
        },
    ]).to_csv(edges_path, index=False)

    with pytest.raises(ValueError) as exc:
        generate_viewer(
            nodes_path=str(nodes_path),
            edges_path=str(edges_path),
            edge_key_path=None,
            out_path=str(out_path),
            height="420px",
            width="640px",
            title="Title",
        )

    assert str(exc.value) == (
        "edges.csv contains edges with endpoints not present in nodes.csv: "
        "2.1->missing"
    )
    assert not out_path.exists()
