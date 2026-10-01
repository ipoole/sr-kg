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
from srkg.module_svg_graphics import createModuleSvgGraphic
from srkg.model import (
    Concept,
    ConceptReference,
    ConceptSection,
    ContentBlock,
    Module,
    ModuleContentBlock,
    ModuleSupport,
    StudyQuestion,
    StudyQuestionOption,
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
    study_question_options_df: pd.DataFrame | None = None,
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
            study_question_options_df,
        )
    }


def build_concepts(
    nodes_df: pd.DataFrame,
    graphic_designs_df: pd.DataFrame | None = None,
    content_blocks_df: pd.DataFrame | None = None,
    study_questions_df: pd.DataFrame | None = None,
    references_df: pd.DataFrame | None = None,
    reference_links_df: pd.DataFrame | None = None,
    study_question_options_df: pd.DataFrame | None = None,
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
        build_study_questions_from_df(study_questions_df, study_question_options_df)
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
        svg_icon = createSvgGraphic(cid, variant="icon")
        svg_detail = createSvgGraphic(cid, variant="detail")
        captions = graphic_captions.get(cid, {})
        concepts.append(Concept(
            id=cid,
            label=str(row.get("label", "")).strip(),
            display_id=display_id,
            domain=str(row.get("domain", "")).strip(),
            domain_title=str(row.get("domain_title", "")).strip(),
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


def build_module_content_blocks_from_df(
    module_content_blocks_df: pd.DataFrame,
) -> list[ModuleContentBlock]:
    """Build module content blocks from a module_content_blocks.csv-style frame."""
    blocks: list[ModuleContentBlock] = []
    for _, row in module_content_blocks_df.iterrows():
        block_id = str(row.get("block_id", "")).strip()
        module_id = str(row.get("module_id", "")).strip()
        kind = str(row.get("kind", "")).strip()
        body = str(row.get("body", "")).strip()
        if not block_id or not module_id or not kind or not body:
            continue
        blocks.append(ModuleContentBlock(
            block_id=block_id,
            module_id=module_id,
            sequence=_parse_int(row.get("sequence", ""), default=0),
            kind=kind,
            title=str(row.get("title", "")).strip(),
            body=body,
        ))
    return sorted(blocks, key=lambda block: (block.module_id, block.sequence, block.block_id))


def build_module_supports_from_df(
    module_supports_df: pd.DataFrame | None,
) -> list[ModuleSupport]:
    """Build module support references from a module_supports.csv-style frame."""
    if module_supports_df is None:
        return []

    supports: list[ModuleSupport] = []
    for _, row in module_supports_df.iterrows():
        module_id = str(row.get("module_id", "")).strip()
        target_type = str(row.get("target_type", "")).strip()
        target_id = str(row.get("target_id", "")).strip()
        role = str(row.get("role", "")).strip()
        if not module_id or not target_type or not target_id or not role:
            continue
        supports.append(ModuleSupport(
            module_id=module_id,
            target_type=target_type,
            target_id=target_id,
            role=role,
            note=str(row.get("note", "")).strip(),
        ))
    return sorted(
        supports,
        key=lambda support: (
            support.module_id,
            support.target_type,
            support.target_id,
            support.role,
        ),
    )


def build_modules_from_dfs(
    modules_df: pd.DataFrame | None,
    module_members_df: pd.DataFrame | None,
    module_supports_df: pd.DataFrame | None,
    module_content_blocks_df: pd.DataFrame | None,
    module_graphic_designs_df: pd.DataFrame | None = None,
) -> list[Module]:
    """Build flat authored modules from optional module source data frames."""
    if modules_df is None or module_members_df is None or module_content_blocks_df is None:
        return []

    members_by_module: dict[str, list[tuple[int, str]]] = {}
    for _, row in module_members_df.iterrows():
        module_id = str(row.get("module_id", "")).strip()
        concept_id = str(row.get("concept_id", "")).strip()
        if not module_id or not concept_id:
            continue
        members_by_module.setdefault(module_id, []).append((
            _parse_int(row.get("sequence", ""), default=0),
            concept_id,
        ))

    supports_by_module = _module_supports_by_module(
        build_module_supports_from_df(module_supports_df)
    )
    blocks_by_module = _module_content_blocks_by_module(
        build_module_content_blocks_from_df(module_content_blocks_df)
    )
    graphic_captions = _graphic_captions_by_id(
        module_graphic_designs_df, id_column="module_id"
    )

    modules: list[Module] = []
    for _, row in modules_df.iterrows():
        module_id = str(row.get("module_id", "")).strip()
        if not module_id:
            continue
        members = [
            concept_id
            for _, concept_id in sorted(
                members_by_module.get(module_id, []),
                key=lambda item: (item[0], item[1]),
            )
        ]
        modules.append(Module(
            module_id=module_id,
            domain=str(row.get("domain", "")).strip(),
            title=str(row.get("title", "")).strip(),
            sequence=_parse_int(row.get("sequence", ""), default=0),
            default_collapsed=parse_bool(row.get("default_collapsed", ""), default=False),
            members=members,
            supports=supports_by_module.get(module_id, []),
            content_blocks=blocks_by_module.get(module_id, []),
            svg_icon=createModuleSvgGraphic(module_id, "icon") or "",
            svg_detail=createModuleSvgGraphic(module_id, "detail") or "",
            svg_icon_caption=graphic_captions.get(module_id, {}).get("icon_caption", ""),
            svg_detail_caption=graphic_captions.get(module_id, {}).get("detail_caption", ""),
        ))
    return sorted(modules, key=lambda module: (module.domain, module.sequence, module.module_id))


def build_study_question_options_from_df(
    study_question_options_df: pd.DataFrame,
) -> list[StudyQuestionOption]:
    """Build authored response options from their CSV-style data frame."""
    options: list[StudyQuestionOption] = []
    for _, row in study_question_options_df.iterrows():
        question_id = str(row.get("question_id", "")).strip()
        option_id = str(row.get("option_id", "")).strip()
        text = str(row.get("text", "")).strip()
        if not question_id or not option_id or not text:
            continue
        options.append(StudyQuestionOption(
            question_id=question_id,
            option_id=option_id,
            sequence=_parse_int(row.get("sequence", ""), default=0),
            text=text,
            is_correct=parse_bool(row.get("is_correct", ""), default=False),
        ))
    return sorted(options, key=lambda option: (
        option.question_id,
        option.sequence,
        option.option_id,
    ))


def build_study_questions_from_df(
    study_questions_df: pd.DataFrame,
    study_question_options_df: pd.DataFrame | None = None,
) -> list[StudyQuestion]:
    """Build study questions from a study_questions.csv-style data frame."""
    options_by_question: dict[str, list[StudyQuestionOption]] = {}
    if study_question_options_df is not None:
        for option in build_study_question_options_from_df(study_question_options_df):
            options_by_question.setdefault(option.question_id, []).append(option)
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
            marking_mode=str(row.get("marking_mode", "")).strip() or "self_assessed",
            prompt=prompt,
            answer=str(row.get("answer", "")).strip(),
            options=tuple(options_by_question.get(question_id, [])),
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


def _module_supports_by_module(
    supports: list[ModuleSupport],
) -> dict[str, list[ModuleSupport]]:
    supports_by_module: dict[str, list[ModuleSupport]] = {}
    for support in supports:
        supports_by_module.setdefault(support.module_id, []).append(support)
    return supports_by_module


def _module_content_blocks_by_module(
    blocks: list[ModuleContentBlock],
) -> dict[str, list[ModuleContentBlock]]:
    blocks_by_module: dict[str, list[ModuleContentBlock]] = {}
    for block in blocks:
        blocks_by_module.setdefault(block.module_id, []).append(block)
    for module_blocks in blocks_by_module.values():
        module_blocks.sort(key=lambda block: (block.sequence, block.block_id))
    return blocks_by_module


def _parse_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _graphic_captions_by_id(
    graphic_designs_df: pd.DataFrame | None,
    *,
    id_column: str = "id",
) -> dict[str, dict[str, str]]:
    """Return optional SVG caption metadata keyed by concept id."""
    if graphic_designs_df is None or graphic_designs_df.empty:
        return {}

    captions = {}
    for _, row in graphic_designs_df.iterrows():
        cid = str(row.get(id_column, "")).strip()
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
