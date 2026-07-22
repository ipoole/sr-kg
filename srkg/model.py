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
class StudyQuestion:
    """A question/answer pair attached to a concept."""

    question: str
    answer: str = ""

    def to_viewer_data(self) -> dict[str, str]:
        return {
            "question": self.question,
            "answer": self.answer,
        }


@dataclass(frozen=True)
class Concept:
    """A physics concept with display metadata and structured content."""

    id: str
    label: str
    layer: str = ""
    layer_title: str = ""
    sections: list[ConceptSection] = field(default_factory=list)
    study_questions: list[StudyQuestion] = field(default_factory=list)
    svg_icon: str = ""
    svg_detail: str = ""
    svg_icon_caption: str = ""
    svg_detail_caption: str = ""
    legacy_text: dict[str, str] = field(default_factory=dict)

    def section_text(self, key: str) -> str:
        for section in self.sections:
            if section.key == key:
                return section.text
        return ""

    def legacy_field_text(self, field_name: str) -> str:
        if field_name in self.legacy_text:
            return self.legacy_text[field_name]
        section_key = {
            "definition_new": "definition",
            "derivation_new": "derivation",
            "explanation_new": "explanation",
        }.get(field_name)
        return self.section_text(section_key or "")

    def to_viewer_data(self) -> dict[str, object]:
        """Return the JSON-compatible shape consumed by the static viewer."""
        svg_detail = self.svg_detail or self.svg_icon
        return {
            "label": self.label,
            "layer": self.layer,
            "layer_title": self.layer_title,
            "definition_new": self.legacy_field_text("definition_new"),
            "derivation_new": self.legacy_field_text("derivation_new"),
            "explanation_new": self.legacy_field_text("explanation_new"),
            "sections": [section.to_viewer_data() for section in self.sections],
            "svg_icon": self.svg_icon,
            "svg_detail": svg_detail,
            "svg_graphic": svg_detail,
            "svg_icon_caption": self.svg_icon_caption,
            "svg_detail_caption": self.svg_detail_caption or self.svg_icon_caption,
            "study_questions": [
                question.to_viewer_data() for question in self.study_questions
            ],
        }
