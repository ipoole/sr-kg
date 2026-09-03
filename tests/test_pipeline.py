import json
import re

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
        },
        {
            "id": "test.beta",
            "display_id": "2.1",
            "label": "Beta",
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


def _append_gr_concept(root):
    nodes = pd.read_csv(root / "nodes.csv", dtype=str).fillna("")
    nodes = pd.concat([
        nodes,
        pd.DataFrame([
            {
                "id": "gr.gamma",
                "display_id": "3.1",
                "label": "Gamma GR",
            },
        ]),
    ], ignore_index=True)
    nodes.to_csv(root / "nodes.csv", index=False)

    content_blocks = pd.read_csv(root / "content_blocks.csv", dtype=str).fillna("")
    content_blocks = pd.concat([
        content_blocks,
        pd.DataFrame([
            {
                "block_id": "gr.gamma.definition",
                "concept_id": "gr.gamma",
                "sequence": 10,
                "kind": "definition",
                "title": "Definition",
                "body": "Gamma GR definition",
            },
        ]),
    ], ignore_index=True)
    content_blocks.to_csv(root / "content_blocks.csv", index=False)

    edges = pd.read_csv(root / "edges.csv", dtype=str).fillna("")
    edges = pd.concat([
        edges,
        pd.DataFrame([
            {
                "source": "gr.gamma",
                "target": "test.alpha",
                "relation": "EXPLAINS",
                "note": "Gamma links to alpha",
            },
        ]),
    ], ignore_index=True)
    edges.to_csv(root / "edges.csv", index=False)


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
    match = re.search(r"var publishedLayout = (\{.*\});", html_text)
    assert match is not None
    published_layout = json.loads(match.group(1))
    assert published_layout["revision"] == "unpublished"
    assert set(published_layout["concepts"]) == {"test.alpha", "test.beta"}


def test_generate_viewer_resolves_partial_published_layout(tmp_path):
    out_path = tmp_path / "viewer.html"
    _write_minimal_root(tmp_path)
    (tmp_path / "layout.json").write_text(json.dumps({
        "schema_version": 1,
        "revision": "test-4",
        "concepts": {"test.alpha": {"x": 123, "y": 456}},
        "modules": {},
    }), encoding="utf-8")

    generate_viewer_from_root(
        data_root=str(tmp_path),
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="Layout",
    )

    html_text = out_path.read_text(encoding="utf-8")
    match = re.search(r"var publishedLayout = (\{.*\});", html_text)
    assert match is not None
    published_layout = json.loads(match.group(1))
    assert published_layout["revision"] == "test-4"
    assert published_layout["concepts"]["test.alpha"] == {"x": 123.0, "y": 456.0}
    assert set(published_layout["concepts"]) == {"test.alpha", "test.beta"}


def test_generate_viewer_from_root_filters_domains_by_id_prefix(tmp_path):
    out_path = tmp_path / "viewer.html"
    _write_minimal_root(tmp_path)
    _append_gr_concept(tmp_path)

    result = generate_viewer_from_root(
        data_root=str(tmp_path),
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="GR",
        domains=["gr"],
    )

    html_text = out_path.read_text(encoding="utf-8")
    assert result == (out_path, 1, 0, tmp_path / "edges_key.csv", 1)
    assert '"gr.gamma"' in html_text
    assert "Gamma GR definition" in html_text
    assert '"test.alpha"' not in html_text
    assert '"test.beta"' not in html_text
    assert "Gamma links to alpha" not in html_text


def test_generate_viewer_from_root_prefers_explicit_domain_column(tmp_path):
    out_path = tmp_path / "viewer.html"
    _write_minimal_root(tmp_path)

    nodes = pd.read_csv(tmp_path / "nodes.csv", dtype=str).fillna("")
    nodes["domain"] = ["core", "gr"]
    nodes["domain_title"] = ["Core concepts", "General Relativity"]
    nodes.to_csv(tmp_path / "nodes.csv", index=False)

    result = generate_viewer_from_root(
        data_root=str(tmp_path),
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="Explicit domain",
        domains=["gr"],
    )

    html_text = out_path.read_text(encoding="utf-8")
    assert result == (out_path, 1, 0, tmp_path / "edges_key.csv", 1)
    assert '"test.beta"' in html_text
    assert '"domain": "gr"' in html_text
    assert '"domain_title": "General Relativity"' in html_text
    assert '"test.alpha"' not in html_text


def test_generate_viewer_from_root_can_include_domain_linked_concepts(tmp_path):
    out_path = tmp_path / "viewer.html"
    _write_minimal_root(tmp_path)
    _append_gr_concept(tmp_path)

    result = generate_viewer_from_root(
        data_root=str(tmp_path),
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="GR",
        domains=["gr"],
        also_load_linked_concepts=True,
    )

    html_text = out_path.read_text(encoding="utf-8")
    assert result == (out_path, 2, 1, tmp_path / "edges_key.csv", 1)
    assert '"gr.gamma"' in html_text
    assert '"test.alpha"' in html_text
    assert '"test.beta"' not in html_text
    assert "Gamma links to alpha" in html_text


def test_generate_viewer_from_root_filters_relations_and_edge_key(tmp_path):
    out_path = tmp_path / "viewer.html"
    _write_minimal_root(tmp_path)

    result = generate_viewer_from_root(
        data_root=str(tmp_path),
        out_path=str(out_path),
        height="420px",
        width="640px",
        title="Selected relations",
        relations=["EXPLAINS"],
    )

    html_text = out_path.read_text(encoding="utf-8")
    assert result == (out_path, 2, 1, tmp_path / "edges_key.csv", 1)
    assert '"relation": "EXPLAINS"' in html_text
    assert '"relation": "RELATED"' not in html_text


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
