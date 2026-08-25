from srkg.model import (
    Concept,
    ConceptReference,
    ConceptSection,
    ContentBlock,
    StudyQuestion,
)


def test_concept_serializes_sections_and_study_questions():
    concept = Concept(
        id="sr.inertial_frames",
        display_id="1.1",
        label="Inertial frames",
        layer="1",
        layer_title="Foundations",
        domain="sr",
        domain_title="Special Relativity and Classical Fields",
        authoring_status="authored",
        sections=[
            ConceptSection(key="definition", title="Definition", text="Definition text"),
            ConceptSection(key="derivation", title="Derivation", text=""),
            ConceptSection(key="explanation", title="Explanation", text="Explanation text"),
        ],
        study_questions=[
            StudyQuestion(
                question_id="sr.inertial_frames.q1",
                concept_id="sr.inertial_frames",
                sequence=10,
                prompt="Question?",
                answer="Answer.",
                question_type="short_answer",
            ),
        ],
        references=[
            ConceptReference(
                reference_id="ttm.sr_cf",
                reference_type="book",
                citation="Citation.",
                title="Title",
                locator="chapter 1",
            ),
        ],
    )

    data = concept.to_viewer_data()

    assert data["display_id"] == "1.1"
    assert data["domain"] == "sr"
    assert data["domain_title"] == "Special Relativity and Classical Fields"
    assert data["authoring_status"] == "authored"
    assert "definition_new" not in data
    assert "derivation_new" not in data
    assert "explanation_new" not in data
    assert data["sections"] == [
        {"key": "definition", "title": "Definition", "text": "Definition text"},
        {"key": "derivation", "title": "Derivation", "text": ""},
        {"key": "explanation", "title": "Explanation", "text": "Explanation text"},
    ]
    assert data["study_questions"] == [
        {
            "question_id": "sr.inertial_frames.q1",
            "concept_id": "sr.inertial_frames",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "Question?",
            "question": "Question?",
            "answer": "Answer.",
        },
    ]
    assert data["references"] == [
        {
            "reference_id": "ttm.sr_cf",
            "reference_type": "book",
            "citation": "Citation.",
            "title": "Title",
            "authors": "",
            "year": "",
            "url": "",
            "locator": "chapter 1",
            "note": "",
            "source_type": "",
            "source_id": "",
        },
    ]


def test_concept_serializes_content_blocks_alongside_viewer_sections():
    concept = Concept(
        id="1.1",
        label="Inertial frames",
        sections=[
            ConceptSection(key="definition", title="Definition", text="Definition text"),
        ],
        content_blocks=[
            ContentBlock(
                block_id="1.1.definition",
                concept_id="1.1",
                sequence=10,
                kind="definition",
                title="Definition",
                body="Definition text",
            ),
        ],
    )

    data = concept.to_viewer_data()

    assert data["content_blocks"] == [
        {
            "block_id": "1.1.definition",
            "concept_id": "1.1",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Definition text",
        },
    ]
