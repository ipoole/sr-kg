import pandas as pd
import pytest

from srkg.pipeline import generate_viewer_from_root


def _write_manifest(root):
    (root / "manifest.yaml").write_text(
        "\n".join([
            "name: test-kb",
            "files:",
            "  nodes: nodes.csv",
            "  edges: edges.csv",
            "  edge_key: edges_key.csv",
            "  content_blocks: content_blocks.csv",
            "  study_questions: study_questions.csv",
            "  references: references.csv",
            "  reference_links: reference_links.csv",
            "  graphic_designs: concept_graphic_designs.csv",
            "",
        ]),
        encoding="utf-8",
    )


def _write_minimal_root(root, *, alpha_body="Definition with </script> marker"):
    _write_manifest(root)
    pd.DataFrame([
        {
            "id": "test.alpha",
            "display_id": "1.1",
            "label": "Alpha",
            "layer": "1",
            "layer_title": "Foundations",
        },
        {
            "id": "test.beta",
            "display_id": "2.1",
            "label": "Beta",
            "layer": "2",
            "layer_title": "Next",
        },
    ]).to_csv(root / "nodes.csv", index=False)
    pd.DataFrame([
        {
            "source": "test.beta",
            "target": "test.alpha",
            "relation": "EXPLAINS",
            "note": "Read after Alpha",
        },
        {
            "source": "test.alpha",
            "target": "test.beta",
            "relation": "",
            "note": "",
        },
    ]).to_csv(root / "edges.csv", index=False)
    pd.DataFrame([
        {
            "relation": "EXPLAINS",
            "directed": "false",
            "category": "teaching",
            "meaning": "source explains target",
            "example": "B explains A",
        },
    ]).to_csv(root / "edges_key.csv", index=False)
    pd.DataFrame([
        {
            "block_id": "test.alpha.definition",
            "concept_id": "test.alpha",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": alpha_body,
        },
        {
            "block_id": "test.beta.definition",
            "concept_id": "test.beta",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Beta definition",
        },
    ]).to_csv(root / "content_blocks.csv", index=False)
    pd.DataFrame([
        {
            "question_id": "test.alpha.q1",
            "concept_id": "test.alpha",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "Alpha question?",
            "answer": "Alpha answer.",
        },
    ]).to_csv(root / "study_questions.csv", index=False)
    pd.DataFrame([
        {
            "reference_id": "ref.alpha",
            "reference_type": "book",
            "citation": "Alpha reference.",
            "authors": "",
            "title": "Reference Alpha",
            "year": "",
            "url": "",
            "note": "",
        },
    ]).to_csv(root / "references.csv", index=False)
    pd.DataFrame([
        {
            "source_type": "content_block",
            "source_id": "test.alpha.definition",
            "reference_id": "ref.alpha",
            "locator": "section 1",
            "note": "",
        },
    ]).to_csv(root / "reference_links.csv", index=False)
    pd.DataFrame([
        {
            "id": "test.alpha",
            "icon_caption": "Icon caption",
            "detail_caption": "Detail caption",
        },
    ]).to_csv(root / "concept_graphic_designs.csv", index=False)


def test_generate_viewer_from_root_runs_full_pipeline_and_injects_controls(tmp_path):
    out_path = tmp_path / "out" / "viewer.html"
    _write_minimal_root(tmp_path)

    result = generate_viewer_from_root(
        data_root=str(tmp_path),
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="SR <Graph>",
    )

    html_text = out_path.read_text(encoding="utf-8")
    assert result == (out_path, 2, 2, tmp_path / "edges_key.csv", 1)
    assert '<div id="kg_view_title">SR &lt;Graph&gt;</div>' in html_text
    assert 'id="kg_controls"' in html_text
    assert "var conceptData = " in html_text
    assert "Definition with <\\/script> marker" in html_text
    assert '"references": [' in html_text
    assert "Alpha reference." in html_text
    assert '"relation": "REFERENCE"' in html_text
    assert '"relation": "EXPLAINS"' in html_text
    assert '"directed": false' in html_text
    assert '"colour":' in html_text
    assert '"arrows": ""' in html_text


def test_generate_viewer_from_root_loads_graphic_design_captions(tmp_path):
    out_path = tmp_path / "viewer.html"
    _write_minimal_root(tmp_path)

    generate_viewer_from_root(
        data_root=str(tmp_path),
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="Title",
    )

    html_text = out_path.read_text(encoding="utf-8")
    assert '"svg_icon_caption": "Icon caption"' in html_text
    assert '"svg_detail_caption": "Detail caption"' in html_text


def test_generate_viewer_from_root_rejects_edges_with_unknown_endpoints(tmp_path):
    out_path = tmp_path / "viewer.html"
    _write_minimal_root(tmp_path)
    pd.DataFrame([
        {
            "source": "test.beta",
            "target": "missing",
            "relation": "EXPLAINS",
            "note": "",
        },
    ]).to_csv(tmp_path / "edges.csv", index=False)

    with pytest.raises(ValueError) as exc:
        generate_viewer_from_root(
            data_root=str(tmp_path),
            out_path=str(out_path),
            height="420px",
            width="640px",
            title="Title",
        )

    assert str(exc.value) == (
        "edges.csv contains edges with endpoints not present in nodes.csv: "
        "test.beta->missing"
    )
    assert not out_path.exists()
