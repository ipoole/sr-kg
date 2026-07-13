import pandas as pd

from srkg.validation import (
    format_validation_issues,
    has_validation_errors,
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
            "label": "Alpha",
            "layer": "1",
            "layer_title": "Foundations",
            "definition_new": "Alpha definition.",
            "derivation_new": "",
            "explanation_new": "",
            "study_question_1": "",
            "study_answer_1": "",
        },
        {
            "id": "2.1",
            "label": "Beta",
            "layer": "2",
            "layer_title": "Applications",
            "definition_new": "Beta references \\cref{Alpha}{1.1}.",
            "derivation_new": (
                "\\optional_details{Why this works}{The body may contain "
                "\\(x^2\\) and \\cref{Alpha}{1.1}.}"
            ),
            "explanation_new": "",
            "study_question_1": "Question?",
            "study_answer_1": "Answer.",
        },
    ])


def _edges_df():
    return pd.DataFrame([
        {"source": "2.1", "target": "1.1", "relation": "DEPENDS_ON", "note": ""},
    ])


def test_validate_graph_data_accepts_well_formed_fixture():
    issues = validate_graph_data(_nodes_df(), _edges_df(), _edge_key())

    assert issues == []


def test_validate_graph_data_reports_required_values_and_macro_syntax_errors():
    nodes_df = _nodes_df()
    nodes_df.loc[1, "definition_new"] = ""
    nodes_df.loc[1, "derivation_new"] = (
        "\\optional_details{Missing body} "
        "and bad math \\(x+y "
        "and missing cref \\cref{Nope}{9.9}"
    )

    issues = validate_graph_data(nodes_df, _edges_df(), _edge_key())

    assert ("error", "node-required-value") in {
        (issue.severity, issue.code) for issue in issues
    }
    assert ("error", "optional_details-syntax") in {
        (issue.severity, issue.code) for issue in issues
    }
    assert ("error", "math-delimiter") in {
        (issue.severity, issue.code) for issue in issues
    }
    assert ("error", "cref-target") in {
        (issue.severity, issue.code) for issue in issues
    }


def test_validate_graph_data_warns_when_crefs_and_edges_do_not_match():
    nodes_df = _nodes_df()
    nodes_df.loc[1, "definition_new"] = "Beta mentions no other concepts."
    nodes_df.loc[1, "derivation_new"] = ""
    edges_df = pd.DataFrame([
        {"source": "2.1", "target": "1.1", "relation": "DEPENDS_ON", "note": ""},
        {"source": "1.1", "target": "2.1", "relation": "RELATED", "note": ""},
    ])

    issues = validate_graph_data(nodes_df, edges_df, _edge_key())

    assert all(issue.severity == "warning" for issue in issues)
    assert [issue.code for issue in issues] == [
        "edge-cref-missing",
        "edge-cref-missing",
    ]
    assert has_validation_errors(issues) is False
    assert has_validation_errors(issues, strict=True) is True


def test_validate_graph_data_warns_for_cref_without_corresponding_edge():
    nodes_df = pd.concat([
        _nodes_df(),
        pd.DataFrame([
            {
                "id": "3.1",
                "label": "Gamma",
                "layer": "3",
                "layer_title": "Synthesis",
                "definition_new": "Gamma definition.",
                "derivation_new": "",
                "explanation_new": "",
                "study_question_1": "",
                "study_answer_1": "",
            },
        ]),
    ], ignore_index=True)
    nodes_df.loc[0, "definition_new"] = "Alpha points at \\cref{Gamma}{3.1}."
    edges_df = pd.DataFrame([
        {"source": "2.1", "target": "1.1", "relation": "DEPENDS_ON", "note": ""},
    ])

    issues = validate_graph_data(nodes_df, edges_df, _edge_key())

    assert any(issue.code == "cref-edge-missing" for issue in issues)
    assert all(issue.severity == "warning" for issue in issues)


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
