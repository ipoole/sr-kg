import pandas as pd
import pytest

from srkg.data import (
    build_concept_references_from_dfs,
    build_study_questions_from_df,
    build_concepts,
    build_concept_data,
    load_edge_key,
    normalise_edges,
    parse_bool,
    validate_edge_endpoints,
)


def test_build_concept_data_trims_fields_adds_graphics_and_study_questions():
    nodes_df = pd.DataFrame([
        {
            "id": " sr.inertial_frames ",
            "display_id": " 1.1 ",
            "label": " Inertial frames ",
            "domain": " sr ",
            "domain_title": " Special Relativity and Classical Fields ",
            "authoring_status": " seed ",
        },
        {
            "id": "   ",
            "label": "Skipped",
        },
    ])
    graphic_designs_df = pd.DataFrame([
        {
            "id": " sr.inertial_frames ",
            "icon_caption": " Icon caption ",
            "detail_caption": " ",
        },
    ])
    content_blocks_df = pd.DataFrame([
        {
            "block_id": "sr.inertial_frames.definition",
            "concept_id": "sr.inertial_frames",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": " Definition text ",
        },
        {
            "block_id": "sr.inertial_frames.derivation",
            "concept_id": "sr.inertial_frames",
            "sequence": 20,
            "kind": "derivation",
            "title": "Derivation",
            "body": " Derivation text ",
        },
        {
            "block_id": "sr.inertial_frames.explanation",
            "concept_id": "sr.inertial_frames",
            "sequence": 30,
            "kind": "explanation",
            "title": "Explanation",
            "body": " Explanation text ",
        },
    ])
    study_questions_df = pd.DataFrame([
        {
            "question_id": " sr.inertial_frames.q2 ",
            "concept_id": " sr.inertial_frames ",
            "sequence": 20,
            "question_type": " short_answer ",
            "prompt": " Second question? ",
            "answer": " Second answer. ",
        },
        {
            "question_id": " sr.inertial_frames.q1 ",
            "concept_id": " sr.inertial_frames ",
            "sequence": 10,
            "question_type": " short_answer ",
            "prompt": " First question? ",
            "answer": " First answer. ",
        },
    ])
    references_df = pd.DataFrame([
        {
            "reference_id": " ttm.sr_cf ",
            "reference_type": " book ",
            "citation": " Citation text. ",
            "authors": " Author ",
            "title": " Title ",
            "year": " 2017 ",
            "url": " ",
            "note": "",
        },
    ])
    reference_links_df = pd.DataFrame([
        {
            "source_type": " content_block ",
            "source_id": " sr.inertial_frames.derivation ",
            "reference_id": " ttm.sr_cf ",
            "locator": " p. 12 ",
            "note": " See derivation. ",
        },
    ])

    concept_data = build_concept_data(
        nodes_df,
        graphic_designs_df,
        content_blocks_df,
        study_questions_df,
        references_df,
        reference_links_df,
    )

    assert set(concept_data) == {"sr.inertial_frames"}
    assert concept_data["sr.inertial_frames"]["display_id"] == "1.1"
    assert concept_data["sr.inertial_frames"]["label"] == "Inertial frames"
    assert "layer" not in concept_data["sr.inertial_frames"]
    assert "layer_title" not in concept_data["sr.inertial_frames"]
    assert concept_data["sr.inertial_frames"]["domain"] == "sr"
    assert (
        concept_data["sr.inertial_frames"]["domain_title"]
        == "Special Relativity and Classical Fields"
    )
    assert concept_data["sr.inertial_frames"]["authoring_status"] == "seed"
    assert concept_data["sr.inertial_frames"]["sections"] == [
        {"key": "definition", "title": "Definition", "text": "Definition text"},
        {"key": "derivation", "title": "Derivation", "text": "Derivation text"},
        {"key": "explanation", "title": "Explanation", "text": "Explanation text"},
    ]
    assert concept_data["sr.inertial_frames"]["content_blocks"] == [
        {
            "block_id": "sr.inertial_frames.definition",
            "concept_id": "sr.inertial_frames",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Definition text",
        },
        {
            "block_id": "sr.inertial_frames.derivation",
            "concept_id": "sr.inertial_frames",
            "sequence": 20,
            "kind": "derivation",
            "title": "Derivation",
            "body": "Derivation text",
        },
        {
            "block_id": "sr.inertial_frames.explanation",
            "concept_id": "sr.inertial_frames",
            "sequence": 30,
            "kind": "explanation",
            "title": "Explanation",
            "body": "Explanation text",
        },
    ]
    assert concept_data["sr.inertial_frames"]["svg_icon"].startswith("<svg")
    assert concept_data["sr.inertial_frames"]["svg_detail"].startswith("<svg")
    assert (
        concept_data["sr.inertial_frames"]["svg_graphic"]
        == concept_data["sr.inertial_frames"]["svg_detail"]
    )
    assert concept_data["sr.inertial_frames"]["svg_icon_caption"] == "Icon caption"
    assert concept_data["sr.inertial_frames"]["svg_detail_caption"] == "Icon caption"
    assert concept_data["sr.inertial_frames"]["study_questions"] == [
        {
            "question_id": "sr.inertial_frames.q1",
            "concept_id": "sr.inertial_frames",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "First question?",
            "question": "First question?",
            "answer": "First answer.",
        },
        {
            "question_id": "sr.inertial_frames.q2",
            "concept_id": "sr.inertial_frames",
            "sequence": 20,
            "question_type": "short_answer",
            "prompt": "Second question?",
            "question": "Second question?",
            "answer": "Second answer.",
        },
    ]
    assert concept_data["sr.inertial_frames"]["references"] == [
        {
            "reference_id": "ttm.sr_cf",
            "reference_type": "book",
            "citation": "Citation text.",
            "title": "Title",
            "authors": "Author",
            "year": "2017",
            "url": "",
            "locator": "p. 12",
            "note": "See derivation.",
            "source_type": "content_block",
            "source_id": "sr.inertial_frames.derivation",
        },
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
    assert concept_data["99.99"]["references"] == []


def test_build_concepts_returns_structured_model():
    nodes_df = pd.DataFrame([
        {
            "id": "1.1",
            "label": "Inertial frames",
        },
    ])
    content_blocks_df = pd.DataFrame([
        {
            "block_id": "1.1.definition",
            "concept_id": "1.1",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Definition text",
        },
        {
            "block_id": "1.1.explanation",
            "concept_id": "1.1",
            "sequence": 30,
            "kind": "explanation",
            "title": "Explanation",
            "body": "Explanation text",
        },
    ])
    study_questions_df = pd.DataFrame([
        {
            "question_id": "1.1.q1",
            "concept_id": "1.1",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "Question?",
            "answer": "Answer.",
        },
    ])

    concepts = build_concepts(
        nodes_df,
        content_blocks_df=content_blocks_df,
        study_questions_df=study_questions_df,
    )

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
    assert [block.block_id for block in concepts[0].content_blocks] == [
        "1.1.definition",
        "1.1.explanation",
    ]
    assert concepts[0].study_questions[0].prompt == "Question?"


def test_build_study_questions_from_df_uses_non_empty_prompts_only():
    study_questions_df = pd.DataFrame([
        {
            "question_id": " q2 ",
            "concept_id": " c1 ",
            "sequence": 20,
            "question_type": " calculation ",
            "prompt": " Second? ",
            "answer": " Second answer. ",
        },
        {
            "question_id": " q1 ",
            "concept_id": " c1 ",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": " First? ",
            "answer": "",
        },
        {
            "question_id": " skipped ",
            "concept_id": " c1 ",
            "sequence": 30,
            "question_type": "short_answer",
            "prompt": "",
            "answer": "No prompt.",
        },
    ])

    questions = build_study_questions_from_df(study_questions_df)

    assert [question.to_viewer_data() for question in questions] == [
        {
            "question_id": "q1",
            "concept_id": "c1",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "First?",
            "question": "First?",
            "answer": "",
        },
        {
            "question_id": "q2",
            "concept_id": "c1",
            "sequence": 20,
            "question_type": "calculation",
            "prompt": "Second?",
            "question": "Second?",
            "answer": "Second answer.",
        },
    ]


def test_build_concept_references_from_dfs_links_to_concepts_blocks_and_questions():
    references_df = pd.DataFrame([
        {
            "reference_id": "ref.a",
            "reference_type": "book",
            "citation": "A citation.",
            "authors": "",
            "title": "Reference A",
            "year": "",
            "url": "",
            "note": "",
        },
    ])
    reference_links_df = pd.DataFrame([
        {
            "source_type": "concept",
            "source_id": "concept.a",
            "reference_id": "ref.a",
            "locator": "",
            "note": "Concept-level note.",
        },
        {
            "source_type": "content_block",
            "source_id": "concept.b.definition",
            "reference_id": "ref.a",
            "locator": "section 2",
            "note": "",
        },
        {
            "source_type": "study_question",
            "source_id": "concept.c.q1",
            "reference_id": "ref.a",
            "locator": "",
            "note": "",
        },
    ])
    content_blocks = [
        build_concepts(
            pd.DataFrame([{"id": "concept.b", "label": "B"}]),
            content_blocks_df=pd.DataFrame([
                {
                    "block_id": "concept.b.definition",
                    "concept_id": "concept.b",
                    "sequence": 10,
                    "kind": "definition",
                    "title": "Definition",
                    "body": "Body",
                },
            ]),
        )[0].content_blocks[0],
    ]
    study_questions = build_study_questions_from_df(pd.DataFrame([
        {
            "question_id": "concept.c.q1",
            "concept_id": "concept.c",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "Question?",
            "answer": "",
        },
    ]))

    references = build_concept_references_from_dfs(
        references_df,
        reference_links_df,
        content_blocks,
        study_questions,
    )

    assert [(concept_id, ref.source_type, ref.source_id) for concept_id, ref in references] == [
        ("concept.a", "concept", "concept.a"),
        ("concept.b", "content_block", "concept.b.definition"),
        ("concept.c", "study_question", "concept.c.q1"),
    ]


def test_build_concepts_groups_content_blocks_into_legacy_viewer_sections():
    nodes_df = pd.DataFrame([
        {
            "id": "1.1",
            "label": "Inertial frames",
        },
    ])
    content_blocks_df = pd.DataFrame([
        {
            "block_id": "1.1.definition.1",
            "concept_id": "1.1",
            "sequence": 20,
            "kind": "definition",
            "title": "Definition",
            "body": "Second definition block",
        },
        {
            "block_id": "1.1.definition.0",
            "concept_id": "1.1",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "First definition block",
        },
        {
            "block_id": "1.1.explanation",
            "concept_id": "1.1",
            "sequence": 30,
            "kind": "explanation",
            "title": "Explanation",
            "body": "Explanation block",
        },
    ])

    concepts = build_concepts(nodes_df, content_blocks_df=content_blocks_df)

    assert [section.to_viewer_data() for section in concepts[0].sections] == [
        {
            "key": "definition",
            "title": "Definition",
            "text": "First definition block\n\nSecond definition block",
        },
        {"key": "derivation", "title": "Derivation", "text": ""},
        {"key": "explanation", "title": "Explanation", "text": "Explanation block"},
    ]


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
