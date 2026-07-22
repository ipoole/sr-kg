from pathlib import Path

import pandas as pd
import pytest

from srkg.data import (
    build_concepts,
    build_concept_data,
    find_edge_key_path,
    load_edge_key,
    normalise_edges,
    parse_bool,
    validate_edge_endpoints,
)


def test_build_concept_data_trims_fields_adds_graphics_and_study_questions():
    nodes_df = pd.DataFrame([
        {
            "id": " 1.1 ",
            "label": " Inertial frames ",
            "layer": " 1 ",
            "layer_title": " Foundations ",
            "definition_new": " Definition text ",
            "derivation_new": " Derivation text ",
            "explanation_new": " Explanation text ",
            "study_question_2": " Second question? ",
            "study_answer_2": " Second answer. ",
            "study_question_1": " First question? ",
            "study_answer_1": " First answer. ",
            "study_answer_3": " Ignored because there is no question. ",
        },
        {
            "id": "   ",
            "label": "Skipped",
        },
    ])
    graphic_designs_df = pd.DataFrame([
        {
            "id": " 1.1 ",
            "icon_caption": " Icon caption ",
            "detail_caption": " ",
        },
    ])

    concept_data = build_concept_data(nodes_df, graphic_designs_df)

    assert set(concept_data) == {"1.1"}
    assert concept_data["1.1"]["label"] == "Inertial frames"
    assert concept_data["1.1"]["layer"] == "1"
    assert concept_data["1.1"]["layer_title"] == "Foundations"
    assert concept_data["1.1"]["definition_new"] == "Definition text"
    assert concept_data["1.1"]["derivation_new"] == "Derivation text"
    assert concept_data["1.1"]["explanation_new"] == "Explanation text"
    assert concept_data["1.1"]["sections"] == [
        {"key": "definition", "title": "Definition", "text": "Definition text"},
        {"key": "derivation", "title": "Derivation", "text": "Derivation text"},
        {"key": "explanation", "title": "Explanation", "text": "Explanation text"},
    ]
    assert concept_data["1.1"]["svg_icon"].startswith("<svg")
    assert concept_data["1.1"]["svg_detail"].startswith("<svg")
    assert concept_data["1.1"]["svg_graphic"] == concept_data["1.1"]["svg_detail"]
    assert concept_data["1.1"]["svg_icon_caption"] == "Icon caption"
    assert concept_data["1.1"]["svg_detail_caption"] == "Icon caption"
    assert concept_data["1.1"]["study_questions"] == [
        {"question": "First question?", "answer": "First answer."},
        {"question": "Second question?", "answer": "Second answer."},
    ]


def test_build_concept_data_uses_empty_graphics_for_unknown_node_ids():
    nodes_df = pd.DataFrame([
        {
            "id": "99.99",
            "label": "Unknown",
        },
    ])

    concept_data = build_concept_data(nodes_df)

    assert concept_data["99.99"]["svg_icon"] == ""
    assert concept_data["99.99"]["svg_detail"] == ""
    assert concept_data["99.99"]["svg_graphic"] == ""
    assert concept_data["99.99"]["study_questions"] == []


def test_build_concepts_returns_structured_model():
    nodes_df = pd.DataFrame([
        {
            "id": "1.1",
            "label": "Inertial frames",
            "definition_new": "Definition text",
            "derivation_new": "",
            "explanation_new": "Explanation text",
            "study_question_1": "Question?",
            "study_answer_1": "Answer.",
        },
    ])

    concepts = build_concepts(nodes_df)

    assert len(concepts) == 1
    assert concepts[0].id == "1.1"
    assert [section.key for section in concepts[0].sections] == [
        "definition",
        "derivation",
        "explanation",
    ]
    assert [section.text for section in concepts[0].sections] == [
        "Definition text",
        "",
        "Explanation text",
    ]
    assert concepts[0].study_questions[0].question == "Question?"


def test_normalise_edges_requires_expected_columns():
    edges_df = pd.DataFrame([
        {
            "source": "1.1",
            "relation": "USES",
        },
    ])

    with pytest.raises(ValueError) as exc:
        normalise_edges(edges_df)

    assert str(exc.value) == "edges.csv must contain columns: note, target"


def test_normalise_edges_replaces_blank_relation_without_mutating_input():
    edges_df = pd.DataFrame([
        {
            "source": "1.1",
            "target": "1.2",
            "relation": "",
            "note": "Implicit reference",
        },
        {
            "source": "1.2",
            "target": "1.3",
            "relation": "DEPENDS_ON",
            "note": "",
        },
    ])

    normalised = normalise_edges(edges_df)

    assert normalised["relation"].tolist() == ["REFERENCE", "DEPENDS_ON"]
    assert edges_df["relation"].tolist() == ["", "DEPENDS_ON"]


def test_validate_edge_endpoints_accepts_known_stringified_node_ids():
    nodes_df = pd.DataFrame([{"id": 1}, {"id": 2}])
    edges_df = pd.DataFrame([
        {"source": "1", "target": "2", "relation": "USES", "note": ""},
    ])

    validate_edge_endpoints(nodes_df, edges_df)


def test_validate_edge_endpoints_requires_id_column():
    nodes_df = pd.DataFrame([{"label": "Node"}])
    edges_df = pd.DataFrame([
        {"source": "1", "target": "2", "relation": "USES", "note": ""},
    ])

    with pytest.raises(ValueError) as exc:
        validate_edge_endpoints(nodes_df, edges_df)

    assert str(exc.value) == "nodes.csv must contain an 'id' column"


def test_validate_edge_endpoints_reports_invalid_examples_and_overflow_count():
    nodes_df = pd.DataFrame([{"id": "1.1"}])
    edges_df = pd.DataFrame([
        {"source": "bad-1", "target": "1.1", "relation": "USES", "note": ""},
        {"source": "bad-2", "target": "1.1", "relation": "USES", "note": ""},
        {"source": "bad-3", "target": "1.1", "relation": "USES", "note": ""},
        {"source": "bad-4", "target": "1.1", "relation": "USES", "note": ""},
        {"source": "bad-5", "target": "1.1", "relation": "USES", "note": ""},
        {"source": "bad-6", "target": "missing", "relation": "USES", "note": ""},
    ])

    with pytest.raises(ValueError) as exc:
        validate_edge_endpoints(nodes_df, edges_df)

    assert str(exc.value) == (
        "edges.csv contains edges with endpoints not present in nodes.csv: "
        "bad-1->1.1; bad-2->1.1; bad-3->1.1; bad-4->1.1; bad-5->1.1; "
        "... 1 more"
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        ("true", True),
        (" T ", True),
        ("yes", True),
        ("Y", True),
        ("1", True),
        ("false", False),
        (" F ", False),
        ("no", False),
        ("N", False),
        ("0", False),
    ],
)
def test_parse_bool_accepts_common_csv_spellings(value, expected):
    assert parse_bool(value) is expected


def test_parse_bool_returns_default_for_unknown_values():
    assert parse_bool("", default=True) is True
    assert parse_bool("unknown", default=False) is False


def test_load_edge_key_returns_empty_mapping_for_missing_path(tmp_path):
    assert load_edge_key(None) == {}
    assert load_edge_key(tmp_path / "missing.csv") == {}


def test_load_edge_key_validates_required_columns(tmp_path):
    edge_key_path = tmp_path / "edges_key.csv"
    edge_key_path.write_text("relation,directed\nUSES,true\n", encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        load_edge_key(edge_key_path)

    assert str(exc.value) == (
        f"{edge_key_path} must contain columns: category, example, meaning"
    )


def test_load_edge_key_parses_metadata_and_skips_blank_relations(tmp_path):
    edge_key_path = tmp_path / "edges_key.csv"
    edge_key_path.write_text(
        "\n".join([
            "relation,directed,category,meaning,example",
            "DEPENDS_ON,false,dependency,source depends on target,A depends on B",
            ",true,ignored,ignored,ignored",
            "USES,yes,usage,source uses target,A uses B",
        ]),
        encoding="utf-8",
    )

    edge_key = load_edge_key(edge_key_path)

    assert edge_key == {
        "DEPENDS_ON": {
            "relation": "DEPENDS_ON",
            "directed": False,
            "category": "dependency",
            "meaning": "source depends on target",
            "example": "A depends on B",
        },
        "USES": {
            "relation": "USES",
            "directed": True,
            "category": "usage",
            "meaning": "source uses target",
            "example": "A uses B",
        },
    }


def test_find_edge_key_path_prefers_configured_existing_path(tmp_path):
    edges_path = tmp_path / "data" / "edges.csv"
    sibling_key_path = edges_path.parent / "edges_key.csv"
    configured_key_path = tmp_path / "configured.csv"
    edges_path.parent.mkdir()
    sibling_key_path.write_text("", encoding="utf-8")
    configured_key_path.write_text("", encoding="utf-8")

    assert find_edge_key_path(edges_path, str(configured_key_path)) == configured_key_path


def test_find_edge_key_path_rejects_missing_configured_path(tmp_path):
    edges_path = tmp_path / "edges.csv"
    configured_key_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError) as exc:
        find_edge_key_path(edges_path, str(configured_key_path))

    assert str(exc.value) == (
        f"Configured edge key file does not exist: {configured_key_path}"
    )


def test_find_edge_key_path_uses_sibling_when_present(tmp_path):
    edges_path = tmp_path / "edges.csv"
    sibling_key_path = tmp_path / "edges_key.csv"
    sibling_key_path.write_text("", encoding="utf-8")

    assert find_edge_key_path(edges_path, None) == sibling_key_path


def test_find_edge_key_path_returns_none_without_configured_or_sibling_key(tmp_path):
    assert find_edge_key_path(Path(tmp_path / "edges.csv"), None) is None
