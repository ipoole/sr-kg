import pandas as pd
import pytest

from srkg.kb import KnowledgeBaseLoadError, load_knowledge_base


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


def _write_minimal_kb(root):
    _write_manifest(root)
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
            "relation": "PREREQUISITE",
            "note": "",
        },
    ]).to_csv(root / "edges.csv", index=False)
    pd.DataFrame([
        {
            "relation": "PREREQUISITE",
            "directed": "true",
            "category": "knowledge",
            "meaning": "source requires target",
            "example": "",
        },
    ]).to_csv(root / "edges_key.csv", index=False)
    pd.DataFrame([
        {
            "block_id": "test.alpha.definition",
            "concept_id": "test.alpha",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Block alpha definition",
        },
        {
            "block_id": "test.alpha.explanation",
            "concept_id": "test.alpha",
            "sequence": 30,
            "kind": "explanation",
            "title": "Explanation",
            "body": "Block alpha explanation",
        },
        {
            "block_id": "test.beta.definition",
            "concept_id": "test.beta",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Block beta definition",
        },
    ]).to_csv(root / "content_blocks.csv", index=False)
    pd.DataFrame([
        {
            "id": "test.alpha",
            "icon_caption": "Icon caption",
            "detail_caption": "Detail caption",
        },
    ]).to_csv(root / "concept_graphic_designs.csv", index=False)
    pd.DataFrame([
        {
            "reference_id": "ref.alpha",
            "reference_type": "book",
            "citation": "Alpha reference.",
            "authors": "A. Author",
            "title": "Reference Alpha",
            "year": "2026",
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
            "note": "Reference note.",
        },
    ]).to_csv(root / "reference_links.csv", index=False)


def test_load_knowledge_base_from_root_exposes_query_api(tmp_path):
    _write_minimal_kb(tmp_path)

    kb = load_knowledge_base(tmp_path)

    assert kb.paths.root == tmp_path
    assert kb.concept("test.alpha").label == "Alpha"
    assert kb.concept("test.alpha").display_id == "1.1"
    assert kb.content_blocks_for("test.alpha")[0].body == "Block alpha definition"
    assert [section.to_viewer_data() for section in kb.sections_for_viewer("test.alpha")] == [
        {"key": "definition", "title": "Definition", "text": "Block alpha definition"},
        {"key": "derivation", "title": "Derivation", "text": ""},
        {"key": "explanation", "title": "Explanation", "text": "Block alpha explanation"},
    ]
    assert kb.neighbours("test.alpha") == ("test.beta",)
    assert kb.concept_data()["test.alpha"]["display_id"] == "1.1"
    assert kb.concept_data()["test.alpha"]["study_questions"][0]["prompt"] == "Alpha question?"
    assert kb.concept_data()["test.alpha"]["references"][0]["citation"] == "Alpha reference."
    assert kb.concept_data()["test.alpha"]["references"][0]["locator"] == "section 1"
    assert kb.concept_data()["test.alpha"]["svg_detail_caption"] == "Detail caption"


def test_load_knowledge_base_requires_manifest(tmp_path):
    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert "Knowledge-base manifest not found" in str(exc.value)


def test_load_knowledge_base_requires_nodes_file(tmp_path):
    _write_minimal_kb(tmp_path)
    (tmp_path / "nodes.csv").unlink()

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert "Required KB file 'nodes' not found" in str(exc.value)


def test_load_knowledge_base_requires_content_blocks_file(tmp_path):
    _write_minimal_kb(tmp_path)
    (tmp_path / "content_blocks.csv").unlink()

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert "Required KB file 'content_blocks' not found" in str(exc.value)


def test_load_knowledge_base_requires_study_questions_file(tmp_path):
    _write_minimal_kb(tmp_path)
    (tmp_path / "study_questions.csv").unlink()

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert "Required KB file 'study_questions' not found" in str(exc.value)


def test_load_knowledge_base_requires_references_file(tmp_path):
    _write_minimal_kb(tmp_path)
    (tmp_path / "references.csv").unlink()

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert "Required KB file 'references' not found" in str(exc.value)


def test_load_knowledge_base_requires_reference_links_file(tmp_path):
    _write_minimal_kb(tmp_path)
    (tmp_path / "reference_links.csv").unlink()

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert "Required KB file 'reference_links' not found" in str(exc.value)


def test_load_knowledge_base_rejects_duplicate_concept_ids(tmp_path):
    _write_minimal_kb(tmp_path)
    pd.DataFrame([
        {
            "id": "test.alpha",
            "display_id": "1.1",
            "label": "Alpha",
            "layer": "1",
            "layer_title": "Foundations",
        },
        {
            "id": "test.alpha",
            "display_id": "1.2",
            "label": "Alpha again",
            "layer": "1",
            "layer_title": "Foundations",
        },
    ]).to_csv(tmp_path / "nodes.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == "Duplicate concept id(s) in nodes.csv: test.alpha"


def test_load_knowledge_base_rejects_missing_display_id_column(tmp_path):
    _write_minimal_kb(tmp_path)
    nodes = pd.read_csv(tmp_path / "nodes.csv", dtype=str).fillna("")
    nodes = nodes.drop(columns=["display_id"])
    nodes.to_csv(tmp_path / "nodes.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == "nodes.csv must contain a 'display_id' column"


def test_load_knowledge_base_rejects_duplicate_display_ids(tmp_path):
    _write_minimal_kb(tmp_path)
    nodes = pd.read_csv(tmp_path / "nodes.csv", dtype=str).fillna("")
    nodes.loc[1, "display_id"] = "1.1"
    nodes.to_csv(tmp_path / "nodes.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == "Duplicate display_id value(s) in nodes.csv: 1.1"


def test_load_knowledge_base_rejects_missing_content_block_columns(tmp_path):
    _write_minimal_kb(tmp_path)
    pd.DataFrame([
        {
            "block_id": "test.alpha.definition",
            "concept_id": "test.alpha",
            "sequence": 10,
            "kind": "definition",
        },
    ]).to_csv(tmp_path / "content_blocks.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "content_blocks.csv is missing columns: body, title"
    )


def test_load_knowledge_base_rejects_duplicate_content_block_ids(tmp_path):
    _write_minimal_kb(tmp_path)
    pd.DataFrame([
        {
            "block_id": "test.alpha.definition",
            "concept_id": "test.alpha",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "First",
        },
        {
            "block_id": "test.alpha.definition",
            "concept_id": "test.alpha",
            "sequence": 20,
            "kind": "explanation",
            "title": "Explanation",
            "body": "Second",
        },
    ]).to_csv(tmp_path / "content_blocks.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "Duplicate content block id(s) in content_blocks.csv: test.alpha.definition"
    )


def test_load_knowledge_base_rejects_invalid_content_block_kind(tmp_path):
    _write_minimal_kb(tmp_path)
    blocks = pd.read_csv(tmp_path / "content_blocks.csv").fillna("")
    blocks.loc[0, "kind"] = "sidebar"
    blocks.to_csv(tmp_path / "content_blocks.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "content_blocks.csv has invalid kind value(s): sidebar"
    )


def test_load_knowledge_base_rejects_non_numeric_content_block_sequence(tmp_path):
    _write_minimal_kb(tmp_path)
    blocks = pd.read_csv(tmp_path / "content_blocks.csv", dtype=str).fillna("")
    blocks.loc[0, "sequence"] = "first"
    blocks.to_csv(tmp_path / "content_blocks.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "content_blocks.csv has non-numeric sequence value(s): first"
    )


def test_load_knowledge_base_rejects_content_blocks_for_unknown_concepts(tmp_path):
    _write_minimal_kb(tmp_path)
    pd.DataFrame([
        {
            "block_id": "missing.definition",
            "concept_id": "missing",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "No matching concept",
        },
    ]).to_csv(tmp_path / "content_blocks.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "content_blocks.csv references unknown concept id(s): missing"
    )


def test_load_knowledge_base_requires_content_for_each_concept(tmp_path):
    _write_minimal_kb(tmp_path)
    blocks = pd.read_csv(tmp_path / "content_blocks.csv", dtype=str).fillna("")
    blocks = blocks[blocks["concept_id"] != "test.alpha"]
    blocks.to_csv(tmp_path / "content_blocks.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "content_blocks.csv has no blocks for concept id(s): test.alpha"
    )


def test_load_knowledge_base_rejects_missing_study_question_columns(tmp_path):
    _write_minimal_kb(tmp_path)
    pd.DataFrame([
        {
            "question_id": "test.alpha.q1",
            "concept_id": "test.alpha",
            "sequence": 10,
            "prompt": "Question?",
        },
    ]).to_csv(tmp_path / "study_questions.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "study_questions.csv is missing columns: answer, question_type"
    )


def test_load_knowledge_base_rejects_duplicate_study_question_ids(tmp_path):
    _write_minimal_kb(tmp_path)
    pd.DataFrame([
        {
            "question_id": "test.alpha.q1",
            "concept_id": "test.alpha",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "First?",
            "answer": "",
        },
        {
            "question_id": "test.alpha.q1",
            "concept_id": "test.alpha",
            "sequence": 20,
            "question_type": "short_answer",
            "prompt": "Second?",
            "answer": "",
        },
    ]).to_csv(tmp_path / "study_questions.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "Duplicate study question id(s) in study_questions.csv: test.alpha.q1"
    )


def test_load_knowledge_base_rejects_study_questions_for_unknown_concepts(tmp_path):
    _write_minimal_kb(tmp_path)
    pd.DataFrame([
        {
            "question_id": "missing.q1",
            "concept_id": "missing",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "Question?",
            "answer": "",
        },
    ]).to_csv(tmp_path / "study_questions.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "study_questions.csv references unknown concept id(s): missing"
    )


def test_load_knowledge_base_rejects_invalid_study_question_type(tmp_path):
    _write_minimal_kb(tmp_path)
    questions = pd.read_csv(tmp_path / "study_questions.csv", dtype=str).fillna("")
    questions.loc[0, "question_type"] = "essay"
    questions.to_csv(tmp_path / "study_questions.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "study_questions.csv has invalid question_type value(s): essay"
    )


def test_load_knowledge_base_rejects_duplicate_reference_ids(tmp_path):
    _write_minimal_kb(tmp_path)
    pd.DataFrame([
        {
            "reference_id": "ref.alpha",
            "reference_type": "book",
            "citation": "First.",
            "authors": "",
            "title": "First",
            "year": "",
            "url": "",
            "note": "",
        },
        {
            "reference_id": "ref.alpha",
            "reference_type": "book",
            "citation": "Second.",
            "authors": "",
            "title": "Second",
            "year": "",
            "url": "",
            "note": "",
        },
    ]).to_csv(tmp_path / "references.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == "Duplicate reference id(s) in references.csv: ref.alpha"


def test_load_knowledge_base_rejects_unknown_reference_link_reference(tmp_path):
    _write_minimal_kb(tmp_path)
    links = pd.read_csv(tmp_path / "reference_links.csv", dtype=str).fillna("")
    links.loc[0, "reference_id"] = "ref.missing"
    links.to_csv(tmp_path / "reference_links.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "reference_links.csv references unknown reference id(s): ref.missing"
    )


def test_load_knowledge_base_rejects_unknown_reference_link_source(tmp_path):
    _write_minimal_kb(tmp_path)
    links = pd.read_csv(tmp_path / "reference_links.csv", dtype=str).fillna("")
    links.loc[0, "source_id"] = "test.missing.definition"
    links.to_csv(tmp_path / "reference_links.csv", index=False)

    with pytest.raises(KnowledgeBaseLoadError) as exc:
        load_knowledge_base(tmp_path)

    assert str(exc.value) == (
        "reference_links.csv references unknown source id(s): "
        "content_block:test.missing.definition"
    )
