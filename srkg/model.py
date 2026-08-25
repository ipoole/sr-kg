"""Internal knowledge model used between CSV loading and viewer generation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConceptSection:
    """A typed content section within a concept page."""

    key: str
    title: str
    text: str

    def to_viewer_data(self) -> dict[str, str]:
        return {
            "key": self.key,
            "title": self.title,
            "text": self.text,
        }


@dataclass(frozen=True)
class ContentBlock:
    """A smaller authored teaching unit attached to a concept."""

    block_id: str
    concept_id: str
    sequence: int
    kind: str
    title: str
    body: str

    def to_viewer_data(self) -> dict[str, object]:
        return {
            "block_id": self.block_id,
            "concept_id": self.concept_id,
            "sequence": self.sequence,
            "kind": self.kind,
            "title": self.title,
            "body": self.body,
        }


@dataclass(frozen=True)
class StudyQuestion:
    """A question/answer pair attached to a concept."""

    question_id: str
    concept_id: str
    sequence: int
    prompt: str
    answer: str = ""
    question_type: str = ""

    def to_viewer_data(self) -> dict[str, object]:
        return {
            "question_id": self.question_id,
            "concept_id": self.concept_id,
            "sequence": self.sequence,
            "question_type": self.question_type,
            "prompt": self.prompt,
            "question": self.prompt,
            "answer": self.answer,
        }


@dataclass(frozen=True)
class ConceptReference:
    """A bibliographic/source reference attached to KB content."""

    reference_id: str
    reference_type: str
    citation: str
    title: str
    authors: str = ""
    year: str = ""
    url: str = ""
    locator: str = ""
    note: str = ""
    source_type: str = ""
    source_id: str = ""

    def to_viewer_data(self) -> dict[str, object]:
        return {
            "reference_id": self.reference_id,
            "reference_type": self.reference_type,
            "citation": self.citation,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "url": self.url,
            "locator": self.locator,
            "note": self.note,
            "source_type": self.source_type,
            "source_id": self.source_id,
        }


@dataclass(frozen=True)
class Concept:
    """A physics concept with display metadata and structured content."""

    id: str
    label: str
    display_id: str = ""
    layer: str = ""
    layer_title: str = ""
    domain: str = ""
    domain_title: str = ""
    authoring_status: str = ""
    sections: list[ConceptSection] = field(default_factory=list)
    content_blocks: list[ContentBlock] = field(default_factory=list)
    study_questions: list[StudyQuestion] = field(default_factory=list)
    references: list[ConceptReference] = field(default_factory=list)
    svg_icon: str = ""
    svg_detail: str = ""
    svg_icon_caption: str = ""
    svg_detail_caption: str = ""

    def to_viewer_data(self) -> dict[str, object]:
        """Return the JSON-compatible shape consumed by the static viewer."""
        svg_detail = self.svg_detail or self.svg_icon
        return {
            "display_id": self.display_id or self.id,
            "label": self.label,
            "layer": self.layer,
            "layer_title": self.layer_title,
            "domain": self.domain,
            "domain_title": self.domain_title,
            "authoring_status": self.authoring_status,
            "sections": [section.to_viewer_data() for section in self.sections],
            "content_blocks": [
                block.to_viewer_data() for block in self.content_blocks
            ],
            "svg_icon": self.svg_icon,
            "svg_detail": svg_detail,
            "svg_graphic": svg_detail,
            "svg_icon_caption": self.svg_icon_caption,
            "svg_detail_caption": self.svg_detail_caption or self.svg_icon_caption,
            "study_questions": [
                question.to_viewer_data() for question in self.study_questions
            ],
            "references": [
                reference.to_viewer_data() for reference in self.references
            ],
        }
