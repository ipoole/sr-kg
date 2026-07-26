import pandas as pd

from srkg.validation import (
    format_validation_issues,
    has_validation_errors,
    load_validation_issues_from_root,
    validate_graph_data,
)


def _edge_key():
    return {
        "DEPENDS_ON": {
            "relation": "DEPENDS_ON",
            "directed": True,
            "category": "dependency",
            "meaning": "source depends on target",
            "example": "Beta depends on Alpha",
        },
        "RELATED": {
            "relation": "RELATED",
            "directed": False,
            "category": "association",
            "meaning": "source is related to target",
            "example": "Alpha is related to Beta",
        },
    }


def _nodes_df():
    return pd.DataFrame([
        {
            "id": "1.1",
            "display_id": "1.1",
            "label": "Alpha",
            "layer": "1",
            "layer_title": "Foundations",
        },
        {
            "id": "2.1",
            "display_id": "2.1",
            "label": "Beta",
            "layer": "2",
            "layer_title": "Applications",
        },
    ])


def _edges_df():
    return pd.DataFrame([
        {"source": "2.1", "target": "1.1", "relation": "DEPENDS_ON", "note": ""},
    ])


def test_validate_graph_data_accepts_well_formed_fixture():
    issues = validate_graph_data(_nodes_df(), _edges_df(), _edge_key())

    assert issues == []


def test_validate_graph_data_reports_required_values():
    nodes_df = _nodes_df()
    nodes_df.loc[1, "label"] = ""

    issues = validate_graph_data(nodes_df, _edges_df(), _edge_key())

    assert ("error", "node-required-value") in {
        (issue.severity, issue.code) for issue in issues
    }


def test_validate_graph_data_reports_directed_cycles_as_errors():
    nodes_df = _nodes_df()
    edges_df = pd.DataFrame([
        {"source": "2.1", "target": "1.1", "relation": "DEPENDS_ON", "note": ""},
        {"source": "1.1", "target": "2.1", "relation": "DEPENDS_ON", "note": ""},
    ])

    issues = validate_graph_data(nodes_df, edges_df, _edge_key())

    assert any(
        issue.severity == "error" and issue.code == "directed-cycle"
        for issue in issues
    )
    assert has_validation_errors(issues) is True


def test_format_validation_issues_summarizes_counts_and_locations():
    issues = validate_graph_data(
        _nodes_df(),
        pd.DataFrame([
            {"source": "2.1", "target": "missing", "relation": "DEPENDS_ON", "note": ""},
        ]),
        _edge_key(),
    )

    text = format_validation_issues(issues)

    assert "Validation diagnostics" in text
    assert "Errors: 1; warnings: 0" in text
    assert "ERROR edge-endpoint edges.csv row 2: 2.1->missing" in text


def _write_root_kb(tmp_path, *, content_body: str, question_prompt: str = "Question?", question_answer: str = "Answer."):
    (tmp_path / "manifest.yaml").write_text(
        "\n".join([
            "name: test-kb",
            "files:",
            "  nodes: nodes.csv",
            "  edges: edges.csv",
            "  content_blocks: content_blocks.csv",
            "  study_questions: study_questions.csv",
            "  references: references.csv",
            "  reference_links: reference_links.csv",
            "",
        ]),
        encoding="utf-8",
    )
    _nodes_df().to_csv(tmp_path / "nodes.csv", index=False)
    _edges_df().to_csv(tmp_path / "edges.csv", index=False)
    pd.DataFrame([
        {
            "block_id": "1.1.definition",
            "concept_id": "1.1",
            "sequence": 10,
            "kind": "definition",
            "pedagogical_level": "",
            "title": "Definition",
            "body": "Alpha definition.",
        },
        {
            "block_id": "2.1.definition",
            "concept_id": "2.1",
            "sequence": 10,
            "kind": "definition",
            "pedagogical_level": "",
            "title": "Definition",
            "body": content_body,
        },
    ]).to_csv(tmp_path / "content_blocks.csv", index=False)
    pd.DataFrame([
        {
            "question_id": "2.1.q1",
            "concept_id": "2.1",
            "sequence": 10,
            "pedagogical_level": "",
            "question_type": "short_answer",
            "prompt": question_prompt,
            "answer": question_answer,
        },
    ]).to_csv(tmp_path / "study_questions.csv", index=False)
    pd.DataFrame(columns=[
        "reference_id",
        "reference_type",
        "citation",
        "authors",
        "title",
        "year",
        "url",
        "note",
    ]).to_csv(tmp_path / "references.csv", index=False)
    pd.DataFrame(columns=[
        "source_type",
        "source_id",
        "reference_id",
        "locator",
        "note",
    ]).to_csv(tmp_path / "reference_links.csv", index=False)


def test_load_validation_issues_from_root_reports_content_block_text_errors(tmp_path):
    _write_root_kb(
        tmp_path,
        content_body=(
            "\\optional_details{Missing body} "
            "and bad math \\(x+y "
            "and missing cref \\cref{Nope}{9.9}"
        ),
    )

    issues = load_validation_issues_from_root(tmp_path)

    assert ("error", "optional_details-syntax") in {
        (issue.severity, issue.code) for issue in issues
    }
    assert ("error", "math-delimiter") in {
        (issue.severity, issue.code) for issue in issues
    }
    assert ("error", "cref-target") in {
        (issue.severity, issue.code) for issue in issues
    }


def test_load_validation_issues_from_root_warns_when_crefs_and_edges_do_not_match(tmp_path):
    _write_root_kb(tmp_path, content_body="Beta mentions no other concepts.")

    issues = load_validation_issues_from_root(tmp_path)

    assert all(issue.severity == "warning" for issue in issues)
    assert [issue.code for issue in issues] == ["edge-cref-missing"]
    assert has_validation_errors(issues) is False
    assert has_validation_errors(issues, strict=True) is True


def test_load_validation_issues_from_root_validates_study_question_text(tmp_path):
    _write_root_kb(
        tmp_path,
        content_body="Beta references \\cref{Alpha}{1.1}.",
        question_prompt="Question with \\cref{Nope}{9.9}",
        question_answer="",
    )

    issues = load_validation_issues_from_root(tmp_path)

    assert ("error", "cref-target") in {
        (issue.severity, issue.code) for issue in issues
    }
    assert ("warning", "study-answer-missing") in {
        (issue.severity, issue.code) for issue in issues
    }


def test_load_validation_issues_from_root_reports_content_block_integrity(tmp_path):
    (tmp_path / "manifest.yaml").write_text(
        "\n".join([
            "name: test-kb",
            "files:",
            "  nodes: nodes.csv",
            "  edges: edges.csv",
            "  content_blocks: content_blocks.csv",
            "  study_questions: study_questions.csv",
            "  references: references.csv",
            "  reference_links: reference_links.csv",
            "",
        ]),
        encoding="utf-8",
    )
    _nodes_df().to_csv(tmp_path / "nodes.csv", index=False)
    _edges_df().to_csv(tmp_path / "edges.csv", index=False)
    pd.DataFrame([
        {
            "question_id": "1.1.q1",
            "concept_id": "1.1",
            "sequence": 10,
            "pedagogical_level": "",
            "question_type": "short_answer",
            "prompt": "Question?",
            "answer": "",
        },
    ]).to_csv(tmp_path / "study_questions.csv", index=False)
    pd.DataFrame([
        {
            "block_id": "missing.definition",
            "concept_id": "missing",
            "sequence": 10,
            "kind": "definition",
            "pedagogical_level": "",
            "title": "Definition",
            "body": "No matching concept.",
        },
    ]).to_csv(tmp_path / "content_blocks.csv", index=False)
    pd.DataFrame(columns=[
        "reference_id",
        "reference_type",
        "citation",
        "authors",
        "title",
        "year",
        "url",
        "note",
    ]).to_csv(tmp_path / "references.csv", index=False)
    pd.DataFrame(columns=[
        "source_type",
        "source_id",
        "reference_id",
        "locator",
        "note",
    ]).to_csv(tmp_path / "reference_links.csv", index=False)

    issues = load_validation_issues_from_root(tmp_path)

    assert [(issue.severity, issue.code, issue.message) for issue in issues] == [
        (
            "error",
            "kb-load",
            "content_blocks.csv references unknown concept id(s): missing",
        )
    ]
