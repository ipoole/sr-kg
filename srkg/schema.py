"""Authored table contracts and the shared loading exception.

Independent of file I/O, graphic generators and application orchestration.
"""

CONTENT_BLOCK_COLUMNS = (
    "block_id",
    "concept_id",
    "sequence",
    "kind",
    "title",
    "body",
)
CONTENT_BLOCK_KIND_DESCRIPTIONS = {
    "overview": "A short orientation block stating what the concept will do.",
    "definition": "A precise statement of what the concept is.",
    "intuition": "A qualitative mental model or physical interpretation.",
    "explanation": "General explanatory prose that develops the concept.",
    "construction": "A setup or construction that builds an object or argument.",
    "result": "A central result, formula, theorem statement, or named conclusion.",
    "decomposition": "A breakdown of an object into components, frame splits, or parts.",
    "convention": "A notation, sign, unit, coordinate, or gauge convention used locally.",
    "derivation": "A coherent mathematical derivation or proof.",
    "derivation_step": "A smaller algebraic or logical step inside a derivation.",
    "example": "A short illustrative example.",
    "worked_example": "A worked problem or calculation with solution details.",
    "misconception": "A common mistake, ambiguity, or misleading intuition.",
    "warning": "A caveat, domain restriction, or notation trap.",
    "historical_note": "Historical context about discovery, attribution, or influence.",
    "summary": "A concise recap of the main result or takeaway.",
    "graphic": "An addressable explanation wrapping its owner's registered detail graphic.",
}
CONTENT_BLOCK_KINDS = frozenset(CONTENT_BLOCK_KIND_DESCRIPTIONS)
STUDY_QUESTION_COLUMNS = (
    "question_id",
    "concept_id",
    "sequence",
    "question_type",
    "marking_mode",
    "prompt",
    "answer",
)
STUDY_QUESTION_TYPES = {
    "short_answer",
    "multiple_choice",
    "calculation",
}
STUDY_QUESTION_MARKING_MODES = {
    "automatic",
    "self_assessed",
}
STUDY_QUESTION_OPTION_COLUMNS = (
    "question_id",
    "option_id",
    "sequence",
    "text",
    "is_correct",
)
REFERENCE_COLUMNS = (
    "reference_id",
    "reference_type",
    "citation",
    "authors",
    "title",
    "year",
    "url",
    "note",
)
REFERENCE_LINK_COLUMNS = (
    "source_type",
    "source_id",
    "reference_id",
    "locator",
    "note",
)
REFERENCE_LINK_SOURCE_TYPES = {
    "concept",
    "content_block",
    "study_question",
}
MODULE_COLUMNS = (
    "module_id",
    "domain",
    "title",
    "sequence",
    "default_collapsed",
)
MODULE_MEMBER_COLUMNS = (
    "module_id",
    "concept_id",
    "sequence",
)
MODULE_SUPPORT_COLUMNS = (
    "module_id",
    "target_type",
    "target_id",
    "role",
    "note",
)
MODULE_SUPPORT_TARGET_TYPES = {
    "concept",
    "module",
}
MODULE_CONTENT_BLOCK_COLUMNS = (
    "block_id",
    "module_id",
    "sequence",
    "kind",
    "title",
    "body",
)
MODULE_GRAPHIC_DESIGN_COLUMNS = (
    "module_id",
    "icon_caption",
    "detail_caption",
)


class KnowledgeBaseLoadError(ValueError):
    """Raised when a knowledge-base data root cannot be loaded safely."""


