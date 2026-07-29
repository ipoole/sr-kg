"""CSV-adjacent data helpers for the SR knowledge graph.

This module owns validation and lightweight normalization of tabular inputs,
plus conversion of node rows into the concept-data mapping used by the injected
viewer. It deliberately does not know about PyVis, HTML generation, physics, or
layout. Callers are responsible for reading the primary CSV files and passing
``pandas`` data frames in.

Dependencies should stay limited to ``srkg.config`` and general-purpose parsing
libraries.
"""

from pathlib import Path

import pandas as pd

from srkg.config import EDGE_COLUMNS, EDGE_KEY_COLUMNS
from srkg.concept_svg_graphics import createSvgGraphic
from srkg.model import (
    Concept,
    ConceptReference,
    ConceptSection,
    ContentBlock,
    StudyQuestion,
)

CONTENT_SECTION_COLUMNS = (
    ("definition", "Definition"),
    ("derivation", "Derivation"),
    ("explanation", "Explanation"),
)


def build_concept_data(
    nodes_df: pd.DataFrame,
    graphic_designs_df: pd.DataFrame | None = None,
    content_blocks_df: pd.DataFrame | None = None,
    study_questions_df: pd.DataFrame | None = None,
    references_df: pd.DataFrame | None = None,
    reference_links_df: pd.DataFrame | None = None,
) -> dict[str, dict[str, object]]:
    """Build panel data directly from nodes.csv, independent of PyVis metadata."""
    return {
        concept.id: concept.to_viewer_data()
        for concept in build_concepts(
            nodes_df,
            graphic_designs_df,
            content_blocks_df,
            study_questions_df,
            references_df,
            reference_links_df,
        )
    }


def build_concepts(
    nodes_df: pd.DataFrame,
    graphic_designs_df: pd.DataFrame | None = None,
    content_blocks_df: pd.DataFrame | None = None,
    study_questions_df: pd.DataFrame | None = None,
    references_df: pd.DataFrame | None = None,
    reference_links_df: pd.DataFrame | None = None,
) -> list[Concept]:
    """Build internal concept models from source CSV data."""
    concepts = []
    graphic_captions = _graphic_captions_by_id(graphic_designs_df)
    content_blocks = (
        build_content_blocks_from_df(content_blocks_df)
        if content_blocks_df is not None
        else []
    )
    study_questions = (
        build_study_questions_from_df(study_questions_df)
        if study_questions_df is not None
        else []
    )
    blocks_by_concept = _content_blocks_by_concept(content_blocks)
    questions_by_concept = _study_questions_by_concept(study_questions)
    references_by_concept = _references_by_concept(
        build_concept_references_from_dfs(
            references_df,
            reference_links_df,
            content_blocks,
            study_questions,
        )
    )

    for _, row in nodes_df.iterrows():
        cid = str(row.get("id", "")).strip()
        if not cid:
            continue
        display_id = str(row.get("display_id", "")).strip() or cid
        svg_icon = createSvgGraphic(display_id, variant="icon")
        svg_detail = createSvgGraphic(display_id, variant="detail")
        captions = graphic_captions.get(cid, {})
        concepts.append(Concept(
            id=cid,
            label=str(row.get("label", "")).strip(),
            display_id=display_id,
            layer=str(row.get("layer", "")).strip(),
            layer_title=str(row.get("layer_title", "")).strip(),
            sections=_sections_from_content_blocks(blocks_by_concept.get(cid, [])),
            content_blocks=blocks_by_concept.get(cid, []),
            svg_icon=svg_icon or "",
            svg_detail=svg_detail or "",
            svg_icon_caption=captions.get("icon_caption", ""),
            svg_detail_caption=captions.get("detail_caption", ""),
            study_questions=questions_by_concept.get(cid, []),
            references=references_by_concept.get(cid, []),
        ))
    return concepts


def build_content_blocks_from_df(content_blocks_df: pd.DataFrame) -> list[ContentBlock]:
    """Build content blocks from a content_blocks.csv-style data frame."""
    blocks: list[ContentBlock] = []
    for _, row in content_blocks_df.iterrows():
        block_id = str(row.get("block_id", "")).strip()
        concept_id = str(row.get("concept_id", "")).strip()
        kind = str(row.get("kind", "")).strip()
        body = str(row.get("body", "")).strip()
        if not block_id or not concept_id or not kind or not body:
            continue
        blocks.append(ContentBlock(
            block_id=block_id,
            concept_id=concept_id,
            sequence=_parse_int(row.get("sequence", ""), default=0),
            kind=kind,
            title=str(row.get("title", "")).strip(),
            body=body,
        ))
    return sorted(blocks, key=lambda block: (block.concept_id, block.sequence, block.block_id))


def build_study_questions_from_df(study_questions_df: pd.DataFrame) -> list[StudyQuestion]:
    """Build study questions from a study_questions.csv-style data frame."""
    questions: list[StudyQuestion] = []
    for _, row in study_questions_df.iterrows():
        question_id = str(row.get("question_id", "")).strip()
        concept_id = str(row.get("concept_id", "")).strip()
        prompt = str(row.get("prompt", "")).strip()
        if not question_id or not concept_id or not prompt:
            continue
        questions.append(StudyQuestion(
            question_id=question_id,
            concept_id=concept_id,
            sequence=_parse_int(row.get("sequence", ""), default=0),
            question_type=str(row.get("question_type", "")).strip(),
            prompt=prompt,
            answer=str(row.get("answer", "")).strip(),
        ))
    return sorted(questions, key=lambda question: (
        question.concept_id,
        question.sequence,
        question.question_id,
    ))


def build_concept_references_from_dfs(
    references_df: pd.DataFrame | None,
    reference_links_df: pd.DataFrame | None,
    content_blocks: list[ContentBlock],
    study_questions: list[StudyQuestion],
) -> list[tuple[str, ConceptReference]]:
    """Build concept-scoped references from references and link data frames."""
    if references_df is None or reference_links_df is None:
        return []

    references_by_id = {}
    for _, row in references_df.iterrows():
        reference_id = str(row.get("reference_id", "")).strip()
        if not reference_id:
            continue
        references_by_id[reference_id] = {
            "reference_type": str(row.get("reference_type", "")).strip(),
            "citation": str(row.get("citation", "")).strip(),
            "title": str(row.get("title", "")).strip(),
            "authors": str(row.get("authors", "")).strip(),
            "year": str(row.get("year", "")).strip(),
            "url": str(row.get("url", "")).strip(),
        }

    block_concepts = {block.block_id: block.concept_id for block in content_blocks}
    question_concepts = {
        question.question_id: question.concept_id for question in study_questions
    }

    concept_references: list[tuple[str, ConceptReference]] = []
    for _, row in reference_links_df.iterrows():
        source_type = str(row.get("source_type", "")).strip()
        source_id = str(row.get("source_id", "")).strip()
        reference_id = str(row.get("reference_id", "")).strip()
        reference = references_by_id.get(reference_id)
        if not source_type or not source_id or reference is None:
            continue

        if source_type == "concept":
            concept_id = source_id
        elif source_type == "content_block":
            concept_id = block_concepts.get(source_id, "")
        elif source_type == "study_question":
            concept_id = question_concepts.get(source_id, "")
        else:
            concept_id = ""

        if not concept_id:
            continue

        concept_references.append((
            concept_id,
            ConceptReference(
                reference_id=reference_id,
                reference_type=reference["reference_type"],
                citation=reference["citation"],
                title=reference["title"],
                authors=reference["authors"],
                year=reference["year"],
                url=reference["url"],
                locator=str(row.get("locator", "")).strip(),
                note=str(row.get("note", "")).strip(),
                source_type=source_type,
                source_id=source_id,
            ),
        ))

    return sorted(
        concept_references,
        key=lambda item: (
            item[0],
            item[1].source_type,
            item[1].source_id,
            item[1].reference_id,
            item[1].locator,
        ),
    )


def _sections_from_content_blocks(blocks: list[ContentBlock]) -> list[ConceptSection]:
    """Group fine-grained content blocks into the current viewer sections."""
    blocks_by_kind: dict[str, list[ContentBlock]] = {}
    for block in sorted(blocks, key=lambda item: (item.sequence, item.block_id)):
        blocks_by_kind.setdefault(block.kind, []).append(block)

    sections = []
    for key, title in CONTENT_SECTION_COLUMNS:
        bodies = [block.body for block in blocks_by_kind.get(key, []) if block.body]
        sections.append(ConceptSection(
            key=key,
            title=title,
            text="\n\n".join(bodies),
        ))
    return sections


def _content_blocks_by_concept(
    content_blocks: list[ContentBlock],
) -> dict[str, list[ContentBlock]]:
    blocks_by_concept: dict[str, list[ContentBlock]] = {}
    for block in content_blocks:
        blocks_by_concept.setdefault(block.concept_id, []).append(block)
    for concept_blocks in blocks_by_concept.values():
        concept_blocks.sort(key=lambda block: (block.sequence, block.block_id))
    return blocks_by_concept


def _study_questions_by_concept(
    study_questions: list[StudyQuestion],
) -> dict[str, list[StudyQuestion]]:
    questions_by_concept: dict[str, list[StudyQuestion]] = {}
    for question in study_questions:
        questions_by_concept.setdefault(question.concept_id, []).append(question)
    for concept_questions in questions_by_concept.values():
        concept_questions.sort(key=lambda question: (question.sequence, question.question_id))
    return questions_by_concept


def _references_by_concept(
    concept_references: list[tuple[str, ConceptReference]],
) -> dict[str, list[ConceptReference]]:
    references_by_concept: dict[str, list[ConceptReference]] = {}
    for concept_id, reference in concept_references:
        references_by_concept.setdefault(concept_id, []).append(reference)
    return references_by_concept


def _parse_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _graphic_captions_by_id(
    graphic_designs_df: pd.DataFrame | None,
) -> dict[str, dict[str, str]]:
    """Return optional SVG caption metadata keyed by concept id."""
    if graphic_designs_df is None or graphic_designs_df.empty:
        return {}

    captions = {}
    for _, row in graphic_designs_df.iterrows():
        cid = str(row.get("id", "")).strip()
        if not cid:
            continue
        captions[cid] = {
            "icon_caption": str(row.get("icon_caption", "")).strip(),
            "detail_caption": str(row.get("detail_caption", "")).strip(),
        }
    return captions


def normalise_edges(edges_df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean the knowledge edge data."""
    missing = set(EDGE_COLUMNS) - set(edges_df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"edges.csv must contain columns: {missing_cols}")

    edges_df = edges_df.copy()
    edges_df["relation"] = edges_df["relation"].replace("", "REFERENCE")

    return edges_df


def validate_edge_endpoints(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> None:
    """Raise if any edge endpoint does not refer to a known node id."""
    if "id" not in nodes_df.columns:
        raise ValueError("nodes.csv must contain an 'id' column")

    node_ids = set(nodes_df["id"].astype(str))
    sources = edges_df["source"].astype(str)
    targets = edges_df["target"].astype(str)
    invalid_edges = edges_df[~sources.isin(node_ids) | ~targets.isin(node_ids)]
    if invalid_edges.empty:
        return

    examples = "; ".join(
        f"{row.source}->{row.target}"
        for row in invalid_edges[["source", "target"]].head(5).itertuples(index=False)
    )
    more = "" if len(invalid_edges) <= 5 else f"; ... {len(invalid_edges) - 5} more"
    raise ValueError(
        "edges.csv contains edges with endpoints not present in nodes.csv: "
        f"{examples}{more}"
    )


def parse_bool(value, default: bool = True) -> bool:
    """Parse common CSV boolean spellings."""
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"true", "t", "yes", "y", "1"}:
        return True
    if text in {"false", "f", "no", "n", "0"}:
        return False
    return default


def load_edge_key(path: Path | None) -> dict[str, dict[str, str | bool]]:
    """Load relation metadata that controls edge direction and help text."""
    if path is None or not path.exists():
        return {}

    edge_key_df = pd.read_csv(path).fillna("")
    missing = set(EDGE_KEY_COLUMNS) - set(edge_key_df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"{path} must contain columns: {missing_cols}")

    edge_key = {}
    for _, row in edge_key_df.iterrows():
        relation = str(row.get("relation", "")).strip()
        if not relation:
            continue
        edge_key[relation] = {
            "relation": relation,
            "directed": parse_bool(row.get("directed", ""), default=True),
            "category": str(row.get("category", "")).strip(),
            "meaning": str(row.get("meaning", "")).strip(),
            "example": str(row.get("example", "")).strip(),
        }
    return edge_key
