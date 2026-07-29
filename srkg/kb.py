"""Directory-backed knowledge-base loading and query helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from srkg.data import (
    build_concepts,
    load_edge_key,
    normalise_edges,
    validate_edge_endpoints,
)
from srkg.model import Concept, ConceptSection, ContentBlock

DEFAULT_KB_FILES = {
    "nodes": "nodes.csv",
    "edges": "edges.csv",
    "edge_key": "edges_key.csv",
    "content_blocks": "content_blocks.csv",
    "study_questions": "study_questions.csv",
    "references": "references.csv",
    "reference_links": "reference_links.csv",
    "graphic_designs": "concept_graphic_designs.csv",
}

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
    "derivation": "A coherent mathematical derivation or proof.",
    "derivation_step": "A smaller algebraic or logical step inside a derivation.",
    "example": "A short illustrative example.",
    "worked_example": "A worked problem or calculation with solution details.",
    "misconception": "A common mistake, ambiguity, or misleading intuition.",
    "warning": "A caveat, domain restriction, or notation trap.",
    "historical_note": "Historical context about discovery, attribution, or influence.",
    "summary": "A concise recap of the main result or takeaway.",
}
CONTENT_BLOCK_KINDS = frozenset(CONTENT_BLOCK_KIND_DESCRIPTIONS)
STUDY_QUESTION_COLUMNS = (
    "question_id",
    "concept_id",
    "sequence",
    "question_type",
    "prompt",
    "answer",
)
STUDY_QUESTION_TYPES = {
    "short_answer",
    "multiple_choice",
    "calculation",
}
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


class KnowledgeBaseLoadError(ValueError):
    """Raised when a knowledge-base data root cannot be loaded safely."""


@dataclass(frozen=True)
class KnowledgeBasePaths:
    """Resolved source-file paths for a directory-backed knowledge base."""

    root: Path | None
    nodes: Path
    edges: Path
    edge_key: Path | None = None
    content_blocks: Path | None = None
    study_questions: Path | None = None
    references: Path | None = None
    reference_links: Path | None = None
    graphic_designs: Path | None = None


@dataclass(frozen=True)
class KnowledgeBase:
    """Loaded knowledge-base data with stable query methods."""

    paths: KnowledgeBasePaths
    nodes_df: pd.DataFrame
    edges_df: pd.DataFrame
    edge_key: dict[str, dict[str, str | bool]]
    concepts: tuple[Concept, ...]

    @property
    def concept_index(self) -> dict[str, Concept]:
        return {concept.id: concept for concept in self.concepts}

    def concept(self, concept_id: str) -> Concept | None:
        """Return a concept by id, or None if it is not present."""
        return self.concept_index.get(str(concept_id))

    def content_blocks_for(self, concept_id: str) -> tuple[ContentBlock, ...]:
        """Return ordered content blocks for one concept."""
        concept = self.concept(concept_id)
        return tuple(concept.content_blocks) if concept else ()

    def sections_for_viewer(self, concept_id: str) -> tuple[ConceptSection, ...]:
        """Return content grouped into the current viewer section shape."""
        concept = self.concept(concept_id)
        return tuple(concept.sections) if concept else ()

    def neighbours(self, concept_id: str) -> tuple[str, ...]:
        """Return concept ids directly connected to the requested concept."""
        cid = str(concept_id)
        neighbours: set[str] = set()
        for row in self.edges_df.itertuples(index=False):
            source = str(row.source)
            target = str(row.target)
            if source == cid:
                neighbours.add(target)
            if target == cid:
                neighbours.add(source)
        return tuple(sorted(neighbours))

    def concept_data(self) -> dict[str, dict[str, object]]:
        """Return the JSON-compatible concept mapping consumed by the viewer."""
        return {concept.id: concept.to_viewer_data() for concept in self.concepts}


def load_knowledge_base(data_root: str | Path) -> KnowledgeBase:
    """Load a knowledge base from a data-root directory containing a manifest."""
    return load_knowledge_base_from_paths(resolve_knowledge_base_paths(data_root))


def resolve_knowledge_base_paths(data_root: str | Path) -> KnowledgeBasePaths:
    """Resolve source files from a data root and its manifest.yaml file."""
    root = Path(data_root)
    manifest_path = root / "manifest.yaml"
    if not manifest_path.exists():
        raise KnowledgeBaseLoadError(f"Knowledge-base manifest not found: {manifest_path}")

    manifest = _read_manifest(manifest_path)
    files = dict(DEFAULT_KB_FILES)
    files.update(manifest.get("files", {}))

    return KnowledgeBasePaths(
        root=root,
        nodes=_resolve_manifest_path(root, files["nodes"]),
        edges=_resolve_manifest_path(root, files["edges"]),
        edge_key=_resolve_existing_optional_manifest_path(root, files.get("edge_key")),
        content_blocks=_resolve_manifest_path(root, files["content_blocks"]),
        study_questions=_resolve_manifest_path(root, files["study_questions"]),
        references=_resolve_manifest_path(root, files["references"]),
        reference_links=_resolve_manifest_path(root, files["reference_links"]),
        graphic_designs=_resolve_existing_optional_manifest_path(root, files.get("graphic_designs")),
    )


def load_knowledge_base_from_paths(paths: KnowledgeBasePaths) -> KnowledgeBase:
    """Load a knowledge base from resolved KB paths."""
    _require_file(paths.nodes, "nodes")
    _require_file(paths.edges, "edges")
    _require_file(paths.content_blocks, "content_blocks")
    _require_file(paths.study_questions, "study_questions")
    _require_file(paths.references, "references")
    _require_file(paths.reference_links, "reference_links")

    nodes_df = _read_csv(paths.nodes)
    edges_df = normalise_edges(_read_csv(paths.edges))
    content_blocks_df = _read_optional_csv(paths.content_blocks)
    study_questions_df = _read_optional_csv(paths.study_questions)
    references_df = _read_optional_csv(paths.references)
    reference_links_df = _read_optional_csv(paths.reference_links)
    graphic_designs_df = _read_optional_csv(paths.graphic_designs)
    edge_key = load_edge_key(paths.edge_key)

    _validate_unique_concept_ids(nodes_df)
    nodes_df["id"] = nodes_df["id"].astype(str).str.strip()
    if "display_id" in nodes_df.columns:
        nodes_df["display_id"] = nodes_df["display_id"].astype(str).str.strip()
    if paths.root is not None:
        _validate_display_ids(nodes_df)
    edges_df["source"] = edges_df["source"].astype(str).str.strip()
    edges_df["target"] = edges_df["target"].astype(str).str.strip()
    edges_df["relation"] = edges_df["relation"].astype(str).str.strip()

    validate_edge_endpoints(nodes_df, edges_df)
    _validate_content_blocks(nodes_df, content_blocks_df)
    _validate_study_questions(nodes_df, study_questions_df)
    _validate_references(references_df)
    _validate_reference_links(
        nodes_df,
        content_blocks_df,
        study_questions_df,
        references_df,
        reference_links_df,
    )

    concepts = tuple(build_concepts(
        nodes_df,
        graphic_designs_df,
        content_blocks_df,
        study_questions_df,
        references_df,
        reference_links_df,
    ))
    return KnowledgeBase(
        paths=paths,
        nodes_df=nodes_df,
        edges_df=edges_df,
        edge_key=edge_key,
        concepts=concepts,
    )


def _read_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, dtype=str).fillna("")
    except Exception as exc:
        raise KnowledgeBaseLoadError(f"Could not read CSV {path}: {exc}") from exc


def _read_optional_csv(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None
    return _read_csv(path)


def _require_file(path: Path | None, key: str) -> None:
    if path is None or not path.exists():
        raise KnowledgeBaseLoadError(f"Required KB file '{key}' not found: {path}")


def _validate_unique_concept_ids(nodes_df: pd.DataFrame) -> None:
    if "id" not in nodes_df.columns:
        raise KnowledgeBaseLoadError("nodes.csv must contain an 'id' column")
    ids = nodes_df["id"].astype(str).str.strip()
    duplicates = sorted(id_ for id_ in ids[ids.duplicated()].unique() if id_)
    if duplicates:
        raise KnowledgeBaseLoadError(
            "Duplicate concept id(s) in nodes.csv: " + ", ".join(duplicates)
        )


def _validate_display_ids(nodes_df: pd.DataFrame) -> None:
    if "display_id" not in nodes_df.columns:
        raise KnowledgeBaseLoadError("nodes.csv must contain a 'display_id' column")

    display_ids = nodes_df["display_id"].astype(str).str.strip()
    if display_ids.eq("").any():
        raise KnowledgeBaseLoadError("nodes.csv has empty display_id value(s)")

    duplicates = sorted(id_ for id_ in display_ids[display_ids.duplicated()].unique() if id_)
    if duplicates:
        raise KnowledgeBaseLoadError(
            "Duplicate display_id value(s) in nodes.csv: " + ", ".join(duplicates)
        )


def _validate_content_blocks(
    nodes_df: pd.DataFrame,
    content_blocks_df: pd.DataFrame | None,
) -> None:
    if content_blocks_df is None or content_blocks_df.empty:
        if content_blocks_df is not None:
            raise KnowledgeBaseLoadError("content_blocks.csv must contain at least one row")
        return

    missing = set(CONTENT_BLOCK_COLUMNS) - set(content_blocks_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv is missing columns: " + ", ".join(sorted(missing))
        )

    block_ids = content_blocks_df["block_id"].astype(str).str.strip()
    duplicate_block_ids = sorted(id_ for id_ in block_ids[block_ids.duplicated()].unique() if id_)
    if duplicate_block_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate content block id(s) in content_blocks.csv: "
            + ", ".join(duplicate_block_ids)
        )

    for column in ("block_id", "concept_id", "sequence", "kind", "title", "body"):
        values = content_blocks_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"content_blocks.csv has empty {column} value(s)")

    sequence_values = content_blocks_df["sequence"].astype(str).str.strip()
    non_numeric_sequences = sorted(
        value for value in sequence_values.unique() if not _is_integer(value)
    )
    if non_numeric_sequences:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv has non-numeric sequence value(s): "
            + ", ".join(non_numeric_sequences)
        )

    kinds = content_blocks_df["kind"].astype(str).str.strip()
    invalid_kinds = sorted(kind for kind in kinds.unique() if kind not in CONTENT_BLOCK_KINDS)
    if invalid_kinds:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv has invalid kind value(s): "
            + ", ".join(invalid_kinds)
        )

    concept_ids = set(nodes_df["id"].astype(str).str.strip())
    block_concept_ids = content_blocks_df["concept_id"].astype(str).str.strip()
    unknown_ids = sorted(id_ for id_ in block_concept_ids.unique() if id_ and id_ not in concept_ids)
    if unknown_ids:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv references unknown concept id(s): "
            + ", ".join(unknown_ids)
        )

    concepts_without_blocks = sorted(
        concept_id for concept_id in concept_ids if concept_id and concept_id not in set(block_concept_ids)
    )
    if concepts_without_blocks:
        raise KnowledgeBaseLoadError(
            "content_blocks.csv has no blocks for concept id(s): "
            + ", ".join(concepts_without_blocks)
        )


def _validate_study_questions(
    nodes_df: pd.DataFrame,
    study_questions_df: pd.DataFrame | None,
) -> None:
    if study_questions_df is None:
        return

    missing = set(STUDY_QUESTION_COLUMNS) - set(study_questions_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "study_questions.csv is missing columns: " + ", ".join(sorted(missing))
        )

    question_ids = study_questions_df["question_id"].astype(str).str.strip()
    duplicate_question_ids = sorted(
        id_ for id_ in question_ids[question_ids.duplicated()].unique() if id_
    )
    if duplicate_question_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate study question id(s) in study_questions.csv: "
            + ", ".join(duplicate_question_ids)
        )

    for column in ("question_id", "concept_id", "sequence", "question_type", "prompt"):
        values = study_questions_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"study_questions.csv has empty {column} value(s)")

    sequence_values = study_questions_df["sequence"].astype(str).str.strip()
    non_numeric_sequences = sorted(
        value for value in sequence_values.unique() if not _is_integer(value)
    )
    if non_numeric_sequences:
        raise KnowledgeBaseLoadError(
            "study_questions.csv has non-numeric sequence value(s): "
            + ", ".join(non_numeric_sequences)
        )

    question_types = study_questions_df["question_type"].astype(str).str.strip()
    invalid_question_types = sorted(
        question_type
        for question_type in question_types.unique()
        if question_type not in STUDY_QUESTION_TYPES
    )
    if invalid_question_types:
        raise KnowledgeBaseLoadError(
            "study_questions.csv has invalid question_type value(s): "
            + ", ".join(invalid_question_types)
        )

    concept_ids = set(nodes_df["id"].astype(str).str.strip())
    question_concept_ids = study_questions_df["concept_id"].astype(str).str.strip()
    unknown_ids = sorted(
        id_ for id_ in question_concept_ids.unique() if id_ and id_ not in concept_ids
    )
    if unknown_ids:
        raise KnowledgeBaseLoadError(
            "study_questions.csv references unknown concept id(s): "
            + ", ".join(unknown_ids)
        )


def _validate_references(references_df: pd.DataFrame | None) -> None:
    if references_df is None:
        return

    missing = set(REFERENCE_COLUMNS) - set(references_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "references.csv is missing columns: " + ", ".join(sorted(missing))
        )

    if references_df.empty:
        return

    reference_ids = references_df["reference_id"].astype(str).str.strip()
    duplicate_reference_ids = sorted(
        id_ for id_ in reference_ids[reference_ids.duplicated()].unique() if id_
    )
    if duplicate_reference_ids:
        raise KnowledgeBaseLoadError(
            "Duplicate reference id(s) in references.csv: "
            + ", ".join(duplicate_reference_ids)
        )

    for column in ("reference_id", "reference_type", "citation", "title"):
        values = references_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"references.csv has empty {column} value(s)")


def _validate_reference_links(
    nodes_df: pd.DataFrame,
    content_blocks_df: pd.DataFrame | None,
    study_questions_df: pd.DataFrame | None,
    references_df: pd.DataFrame | None,
    reference_links_df: pd.DataFrame | None,
) -> None:
    if reference_links_df is None:
        return

    missing = set(REFERENCE_LINK_COLUMNS) - set(reference_links_df.columns)
    if missing:
        raise KnowledgeBaseLoadError(
            "reference_links.csv is missing columns: " + ", ".join(sorted(missing))
        )

    if reference_links_df.empty:
        return

    for column in ("source_type", "source_id", "reference_id"):
        values = reference_links_df[column].astype(str).str.strip()
        if values.eq("").any():
            raise KnowledgeBaseLoadError(f"reference_links.csv has empty {column} value(s)")

    source_types = reference_links_df["source_type"].astype(str).str.strip()
    invalid_source_types = sorted(
        source_type
        for source_type in source_types.unique()
        if source_type not in REFERENCE_LINK_SOURCE_TYPES
    )
    if invalid_source_types:
        raise KnowledgeBaseLoadError(
            "reference_links.csv has invalid source_type value(s): "
            + ", ".join(invalid_source_types)
        )

    reference_ids = (
        set(references_df["reference_id"].astype(str).str.strip())
        if references_df is not None and "reference_id" in references_df.columns
        else set()
    )
    linked_reference_ids = reference_links_df["reference_id"].astype(str).str.strip()
    unknown_reference_ids = sorted(
        id_ for id_ in linked_reference_ids.unique() if id_ and id_ not in reference_ids
    )
    if unknown_reference_ids:
        raise KnowledgeBaseLoadError(
            "reference_links.csv references unknown reference id(s): "
            + ", ".join(unknown_reference_ids)
        )

    concept_ids = set(nodes_df["id"].astype(str).str.strip())
    content_block_ids = (
        set(content_blocks_df["block_id"].astype(str).str.strip())
        if content_blocks_df is not None and "block_id" in content_blocks_df.columns
        else set()
    )
    study_question_ids = (
        set(study_questions_df["question_id"].astype(str).str.strip())
        if study_questions_df is not None and "question_id" in study_questions_df.columns
        else set()
    )
    known_sources = {
        "concept": concept_ids,
        "content_block": content_block_ids,
        "study_question": study_question_ids,
    }
    unknown_sources = []
    for row in reference_links_df.itertuples(index=False):
        source_type = str(getattr(row, "source_type")).strip()
        source_id = str(getattr(row, "source_id")).strip()
        if source_id and source_id not in known_sources.get(source_type, set()):
            unknown_sources.append(f"{source_type}:{source_id}")

    if unknown_sources:
        raise KnowledgeBaseLoadError(
            "reference_links.csv references unknown source id(s): "
            + ", ".join(sorted(set(unknown_sources)))
        )


def _is_integer(value: str) -> bool:
    try:
        int(value)
    except ValueError:
        return False
    return True


def _resolve_manifest_path(root: Path, value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else root / path


def _resolve_optional_manifest_path(root: Path, value: Any) -> Path | None:
    if value is None or str(value).strip() == "":
        return None
    return _resolve_manifest_path(root, value)


def _resolve_existing_optional_manifest_path(root: Path, value: Any) -> Path | None:
    path = _resolve_optional_manifest_path(root, value)
    if path is None or not path.exists():
        return None
    return path


def _read_manifest(path: Path) -> dict[str, Any]:
    """Read the small manifest subset used by the KB loader.

    The project intentionally avoids a YAML dependency for now. This accepts
    simple top-level key/value pairs plus one level of nested mappings.
    """
    data: dict[str, Any] = {}
    current_mapping: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not raw_line.startswith((" ", "\t")):
            current_mapping = None
            key, value = _split_manifest_pair(line, path)
            if value == "":
                data[key] = {}
                current_mapping = key
            else:
                data[key] = _unquote_manifest_value(value)
            continue
        if current_mapping is None:
            raise KnowledgeBaseLoadError(f"Unexpected manifest indentation in {path}: {raw_line}")
        key, value = _split_manifest_pair(line.strip(), path)
        mapping = data.setdefault(current_mapping, {})
        if not isinstance(mapping, dict):
            raise KnowledgeBaseLoadError(f"Manifest key is not a mapping: {current_mapping}")
        mapping[key] = _unquote_manifest_value(value)
    return data


def _split_manifest_pair(line: str, path: Path) -> tuple[str, str]:
    if ":" not in line:
        raise KnowledgeBaseLoadError(f"Invalid manifest line in {path}: {line}")
    key, value = line.split(":", 1)
    key = key.strip()
    if not key:
        raise KnowledgeBaseLoadError(f"Invalid manifest key in {path}: {line}")
    return key, value.strip()


def _unquote_manifest_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
