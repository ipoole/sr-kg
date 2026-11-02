"""Directory-backed knowledge-base loading and query helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

# Schema names remain re-exported for existing library callers.
from srkg.schema import (
    CONTENT_BLOCK_COLUMNS,
    CONTENT_BLOCK_KIND_DESCRIPTIONS,
    CONTENT_BLOCK_KINDS,
    STUDY_QUESTION_COLUMNS,
    STUDY_QUESTION_TYPES,
    STUDY_QUESTION_MARKING_MODES,
    STUDY_QUESTION_OPTION_COLUMNS,
    REFERENCE_COLUMNS,
    REFERENCE_LINK_COLUMNS,
    REFERENCE_LINK_SOURCE_TYPES,
    MODULE_COLUMNS,
    MODULE_MEMBER_COLUMNS,
    MODULE_SUPPORT_COLUMNS,
    MODULE_SUPPORT_TARGET_TYPES,
    MODULE_CONTENT_BLOCK_COLUMNS,
    MODULE_GRAPHIC_DESIGN_COLUMNS,
    KnowledgeBaseLoadError,
)
from srkg.table_validation import (
    validate_unique_concept_ids,
    validate_display_ids,
    validate_content_blocks,
    validate_study_questions,
    validate_references,
    validate_reference_links,
    validate_module_graphic_designs,
    validate_modules,
)
from srkg.data import (
    build_concepts,
    concept_domain,
    build_modules_from_dfs,
    load_edge_key,
    normalise_edges,
    validate_edge_endpoints,
)
from srkg.layout_persistence import (
    PublishedLayout,
    PublishedLayoutError,
    load_published_layout,
)
from srkg.model import Concept, ConceptSection, ContentBlock, Module, ModuleContentBlock
from srkg.tutorials import Tutorial, TutorialLoadError, load_tutorials

DEFAULT_KB_FILES = {
    "nodes": "nodes.csv",
    "edges": "edges.csv",
    "edge_key": "edges_key.csv",
    "content_blocks": "content_blocks.csv",
    "study_questions": "study_questions.csv",
    "study_question_options": "study_question_options.csv",
    "references": "references.csv",
    "reference_links": "reference_links.csv",
    "graphic_designs": "concept_graphic_designs.csv",
    "module_graphic_designs": "module_graphic_designs.csv",
    "modules": "modules.csv",
    "module_members": "module_members.csv",
    "module_supports": "module_supports.csv",
    "module_content_blocks": "module_content_blocks.csv",
    "layout": "layout.json",
    "tutorials": "tutorials.yaml",
}


@dataclass(frozen=True)
class KnowledgeBasePaths:
    """Resolved source-file paths for a directory-backed knowledge base."""

    root: Path | None
    nodes: Path
    edges: Path
    edge_key: Path | None = None
    content_blocks: Path | None = None
    study_questions: Path | None = None
    study_question_options: Path | None = None
    references: Path | None = None
    reference_links: Path | None = None
    graphic_designs: Path | None = None
    module_graphic_designs: Path | None = None
    modules: Path | None = None
    module_members: Path | None = None
    module_supports: Path | None = None
    module_content_blocks: Path | None = None
    layout: Path | None = None
    tutorials: Path | None = None


@dataclass(frozen=True)
class KnowledgeBase:
    """Loaded knowledge-base data with stable query methods."""

    paths: KnowledgeBasePaths
    nodes_df: pd.DataFrame
    edges_df: pd.DataFrame
    edge_key: dict[str, dict[str, str | bool]]
    concepts: tuple[Concept, ...]
    modules: tuple[Module, ...] = ()
    published_layout: PublishedLayout = field(default_factory=PublishedLayout)
    tutorials: tuple[Tutorial, ...] = ()

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

    @property
    def module_index(self) -> dict[str, Module]:
        return {module.module_id: module for module in self.modules}

    def module(self, module_id: str) -> Module | None:
        """Return a module by id, or None if it is not present."""
        return self.module_index.get(str(module_id))

    def module_content_blocks_for(self, module_id: str) -> tuple[ModuleContentBlock, ...]:
        """Return ordered content blocks for one module."""
        module = self.module(module_id)
        return tuple(module.content_blocks) if module else ()

    def module_data(self) -> dict[str, dict[str, object]]:
        """Return the JSON-compatible module mapping consumed by the viewer."""
        return {module.module_id: module.to_viewer_data() for module in self.modules}

    def tutorial_data(self) -> list[dict[str, object]]:
        """Return validated tutorial routes in their browser representation."""
        return [tutorial.to_viewer_data() for tutorial in self.tutorials]


def load_knowledge_base(
    data_root: str | Path, *, include_graphics: bool = True,
) -> KnowledgeBase:
    """Load a data root; text/diagnostic callers can skip generated SVGs."""
    return load_knowledge_base_from_paths(
        resolve_knowledge_base_paths(data_root), include_graphics=include_graphics,
    )


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
        study_question_options=_resolve_manifest_path(root, files["study_question_options"]),
        references=_resolve_manifest_path(root, files["references"]),
        reference_links=_resolve_manifest_path(root, files["reference_links"]),
        graphic_designs=_resolve_existing_optional_manifest_path(root, files.get("graphic_designs")),
        module_graphic_designs=_resolve_existing_optional_manifest_path(root, files.get("module_graphic_designs")),
        modules=_resolve_existing_optional_manifest_path(root, files.get("modules")),
        module_members=_resolve_existing_optional_manifest_path(root, files.get("module_members")),
        module_supports=_resolve_existing_optional_manifest_path(root, files.get("module_supports")),
        module_content_blocks=_resolve_existing_optional_manifest_path(root, files.get("module_content_blocks")),
        layout=_resolve_optional_manifest_path(root, files.get("layout")),
        tutorials=_resolve_optional_manifest_path(root, files.get("tutorials")),
    )


def load_knowledge_base_from_paths(
    paths: KnowledgeBasePaths, *, include_graphics: bool = True,
) -> KnowledgeBase:
    """Load a knowledge base from resolved KB paths."""
    _require_file(paths.nodes, "nodes")
    _require_file(paths.edges, "edges")
    _require_file(paths.content_blocks, "content_blocks")
    _require_file(paths.study_questions, "study_questions")
    _require_file(paths.study_question_options, "study_question_options")
    _require_file(paths.references, "references")
    _require_file(paths.reference_links, "reference_links")

    nodes_df = _read_csv(paths.nodes)
    edges_df = normalise_edges(_read_csv(paths.edges))
    content_blocks_df = _read_optional_csv(paths.content_blocks)
    study_questions_df = _read_optional_csv(paths.study_questions)
    study_question_options_df = _read_optional_csv(paths.study_question_options)
    references_df = _read_optional_csv(paths.references)
    reference_links_df = _read_optional_csv(paths.reference_links)
    graphic_designs_df = _read_optional_csv(paths.graphic_designs)
    module_graphic_designs_df = _read_optional_csv(paths.module_graphic_designs)
    modules_df = _read_optional_csv(paths.modules)
    module_members_df = _read_optional_csv(paths.module_members)
    module_supports_df = _read_optional_csv(paths.module_supports)
    module_content_blocks_df = _read_optional_csv(paths.module_content_blocks)
    edge_key = load_edge_key(paths.edge_key)

    validate_unique_concept_ids(nodes_df)
    nodes_df["id"] = nodes_df["id"].astype(str).str.strip()
    if "display_id" in nodes_df.columns:
        nodes_df["display_id"] = nodes_df["display_id"].astype(str).str.strip()
    if paths.root is not None:
        validate_display_ids(nodes_df)
    edges_df["source"] = edges_df["source"].astype(str).str.strip()
    edges_df["target"] = edges_df["target"].astype(str).str.strip()
    edges_df["relation"] = edges_df["relation"].astype(str).str.strip()

    validate_edge_endpoints(nodes_df, edges_df)
    validate_content_blocks(nodes_df, content_blocks_df)
    validate_study_questions(nodes_df, study_questions_df, study_question_options_df)
    validate_references(references_df)
    validate_reference_links(
        nodes_df,
        content_blocks_df,
        study_questions_df,
        references_df,
        reference_links_df,
    )
    validate_modules(
        nodes_df,
        modules_df,
        module_members_df,
        module_supports_df,
        module_content_blocks_df,
    )
    validate_module_graphic_designs(modules_df, module_graphic_designs_df)

    concepts = tuple(build_concepts(
        nodes_df,
        graphic_designs_df,
        content_blocks_df,
        study_questions_df,
        references_df,
        reference_links_df,
        study_question_options_df,
        include_graphics=include_graphics,
    ))
    modules = tuple(build_modules_from_dfs(
        modules_df,
        module_members_df,
        module_supports_df,
        module_content_blocks_df,
        module_graphic_designs_df,
        include_graphics=include_graphics,
    ))
    content_block_ids = set(content_blocks_df["block_id"].astype(str).str.strip())
    if module_content_blocks_df is not None and "block_id" in module_content_blocks_df.columns:
        content_block_ids.update(
            module_content_blocks_df["block_id"].astype(str).str.strip()
        )
    known_domains = {
        concept_domain(row)
        for _, row in nodes_df.iterrows()
        if concept_domain(row)
    }
    try:
        tutorials = load_tutorials(
            paths.tutorials,
            concept_ids=nodes_df["id"].astype(str),
            module_ids=(module.module_id for module in modules),
            block_ids=content_block_ids,
            domain_ids=known_domains,
        )
    except TutorialLoadError as exc:
        raise KnowledgeBaseLoadError(str(exc)) from exc
    try:
        published_layout = load_published_layout(
            paths.layout,
            concept_ids=nodes_df["id"].astype(str),
            module_ids=(module.module_id for module in modules),
        )
    except PublishedLayoutError as exc:
        raise KnowledgeBaseLoadError(str(exc)) from exc
    return KnowledgeBase(
        paths=paths,
        nodes_df=nodes_df,
        edges_df=edges_df,
        edge_key=edge_key,
        concepts=concepts,
        modules=modules,
        published_layout=published_layout,
        tutorials=tutorials,
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
