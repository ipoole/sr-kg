from srkg.model import Concept, ConceptSection, StudyQuestion


def test_concept_serializes_sections_and_legacy_text_fields():
    concept = Concept(
        id="1.1",
        label="Inertial frames",
        layer="1",
        layer_title="Foundations",
        sections=[
            ConceptSection(key="definition", title="Definition", text="Definition text"),
            ConceptSection(key="derivation", title="Derivation", text=""),
            ConceptSection(key="explanation", title="Explanation", text="Explanation text"),
        ],
        study_questions=[
            StudyQuestion(question="Question?", answer="Answer."),
        ],
    )

    data = concept.to_viewer_data()

    assert data["definition_new"] == "Definition text"
    assert data["derivation_new"] == ""
    assert data["explanation_new"] == "Explanation text"
    assert data["sections"] == [
        {"key": "definition", "title": "Definition", "text": "Definition text"},
        {"key": "derivation", "title": "Derivation", "text": ""},
        {"key": "explanation", "title": "Explanation", "text": "Explanation text"},
    ]
    assert data["study_questions"] == [
        {"question": "Question?", "answer": "Answer."},
    ]


def test_concept_uses_explicit_legacy_text_when_present():
    concept = Concept(
        id="1.1",
        label="Inertial frames",
        legacy_text={
            "definition_new": "Legacy definition",
            "derivation_new": "Legacy derivation",
            "explanation_new": "Legacy explanation",
        },
    )

    data = concept.to_viewer_data()

    assert data["definition_new"] == "Legacy definition"
    assert data["derivation_new"] == "Legacy derivation"
    assert data["explanation_new"] == "Legacy explanation"
    assert data["sections"] == []
