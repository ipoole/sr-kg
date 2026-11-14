"""Discover domain-owned sources and compose them without combined source files."""
from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import re

import pandas as pd

from srkg.layout_persistence import PublishedLayout, load_published_layout
from srkg.schema import KnowledgeBaseLoadError
from srkg.text_macros import parse_two_arg_macro_calls
from srkg.domain_references import domain_namespace, ReferenceResolver


@dataclass(frozen=True)
class DomainPackage:
    id: str
    title: str
    sequence: int
    root: Path
    paths: object
    graphics: str = ""
    display_name: str = ""
    initial_selection: str = ""
    palette: tuple[tuple[str, str], ...] = ()


def discover_domains(paths, *, domains=None) -> tuple[DomainPackage, ...]:
    """Only explicit manifests register packages; no subject-name switch."""
    from srkg.kb import _read_manifest, _paths_from_manifest
    root = paths.domains_root
    if root is None or not root.is_dir():
        raise KnowledgeBaseLoadError(f"Domain directory not found: {root}")
    requested = set(domains or ())
    if requested:
        for domain_id in sorted(requested):
            if not re.fullmatch(r"[a-z][a-z0-9_]*", str(domain_id)):
                raise KnowledgeBaseLoadError(f"Invalid requested domain: {domain_id!r}")
        manifests = [root / domain_id / "domain.yaml" for domain_id in sorted(requested)]
        missing = [path.parent.name for path in manifests if not path.is_file()]
        if missing:
            raise KnowledgeBaseLoadError("Unknown domain(s): " + ", ".join(missing))
    else:
        manifests = sorted(root.glob("*/domain.yaml"))
    packages = []
    for manifest_path in manifests:
        manifest = _read_manifest(manifest_path)
        domain_id = str(manifest.get("id", "")).strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", domain_id):
            raise KnowledgeBaseLoadError(f"{manifest_path}: invalid domain id {domain_id!r}")
        if domain_id != manifest_path.parent.name:
            raise KnowledgeBaseLoadError(f"{manifest_path}: manifest id must match directory name {manifest_path.parent.name}")
        try:
            sequence = int(manifest.get("sequence", 0))
        except ValueError as exc:
            raise KnowledgeBaseLoadError(f"{manifest_path}: sequence must be an integer") from exc
        package_paths = _paths_from_manifest(manifest_path.parent, manifest)
        # Package metadata must stay within its owning directory.
        for role in ("nodes", "edges", "content_blocks", "study_questions", "study_question_options",
                     "references", "reference_links", "graphic_designs", "module_graphic_designs",
                     "modules", "module_members", "module_supports", "module_content_blocks", "layout", "tutorials", "figures"):
            file = getattr(package_paths, role)
            if file is not None and not file.resolve().is_relative_to(manifest_path.parent.resolve()):
                raise KnowledgeBaseLoadError(f"{manifest_path}: {role} escapes the owning domain directory")
        packages.append(DomainPackage(domain_id, str(manifest.get("title", domain_id)), sequence,
                                      manifest_path.parent, package_paths, str(manifest.get("graphics", "")),
                                      str(manifest.get("display_name", domain_id.upper())),
                                      str(manifest.get("initial_selection", "")),
                                      _read_palette(manifest_path.parent, manifest.get("module_palette"))))
    if not packages:
        raise KnowledgeBaseLoadError(f"No domain.yaml packages found in {root}")
    ids = [package.id for package in packages]
    if len(set(ids)) != len(ids):
        raise KnowledgeBaseLoadError(f"Duplicate domain id in {root}")
    return tuple(sorted(packages, key=lambda package: (package.sequence, package.id)))


def _read_palette(root, value):
    if not value:
        return ()
    path = root / str(value)
    if not path.resolve().is_relative_to(root.resolve()):
        raise KnowledgeBaseLoadError(f"{path}: palette escapes owning domain")
    try:
        palette = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(palette, list) or not palette or any(
            not isinstance(pair, list) or len(pair) != 2 or
            any(not isinstance(colour, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", colour) for colour in pair)
            for pair in palette
        ):
            raise ValueError("expected non-empty [background, border] hex-colour pairs")
        return tuple(tuple(pair) for pair in palette)
    except (OSError, ValueError) as exc:
        raise KnowledgeBaseLoadError(f"{path}: invalid module palette: {exc}") from exc


def read_domain_tables(package):
    from srkg.kb import _require_file, read_source_tables
    for role in ("nodes", "edges", "content_blocks", "study_questions", "study_question_options", "references", "reference_links"):
        _require_file(getattr(package.paths, role), role)
    return read_source_tables(package.paths)


def _ids(frame, column):
    return set(frame[column].astype(str).str.strip()) if frame is not None and column in frame else set()


def _owned(package, tables):
    """Check storage ownership before global referential validation."""
    identity_columns = {"nodes": "id", "modules": "module_id",
                        "figures": "figure_id",
                        "content_blocks": "block_id", "module_content_blocks": "block_id",
                        "study_questions": "question_id", "study_question_options": "option_id"}
    for role, column in identity_columns.items():
        frame = tables.get(role)
        if frame is None or column not in frame:
            continue
        for index, semantic_id in enumerate(frame[column], 2):
            location = f"{getattr(package.paths, role)} row {index} {column}"
            if domain_namespace(semantic_id, location) != package.id:
                raise KnowledgeBaseLoadError(f"{location}: namespace must be {package.id}: {semantic_id}")
    nodes, modules, questions = (_ids(tables.get(role), key) for role, key in
                                (("nodes", "id"), ("modules", "module_id"), ("study_questions", "question_id")))
    for role in ("nodes", "modules"):
        frame = tables.get(role)
        if frame is not None and "domain" in frame:
            bad = frame[frame["domain"].astype(str).str.strip() != package.id]
            if not bad.empty:
                raise KnowledgeBaseLoadError(f"{getattr(package.paths, role)}: records do not belong to domain {package.id}")
    checks = {"edges": ("source", nodes), "content_blocks": ("concept_id", nodes),
              "study_questions": ("concept_id", nodes), "study_question_options": ("question_id", questions),
              "graphic_designs": ("id", nodes), "module_graphic_designs": ("module_id", modules),
              "module_members": ("module_id", modules), "module_supports": ("module_id", modules),
              "module_content_blocks": ("module_id", modules)}
    for role, (column, allowed) in checks.items():
        invalid = _ids(tables.get(role), column) - allowed
        if invalid:
            raise KnowledgeBaseLoadError(f"{getattr(package.paths, role)}: foreign {column} owner(s): {', '.join(sorted(invalid))}")
    links = tables.get("reference_links")
    block_ids = _ids(tables.get("content_blocks"), "block_id")
    if links is not None:
        for row in links.itertuples(index=False):
            allowed = {"concept": nodes, "content_block": block_ids, "study_question": questions}.get(row.source_type, set())
            if row.source_id not in allowed:
                raise KnowledgeBaseLoadError(f"{package.paths.reference_links}: foreign reference source {row.source_id}")


def _resolve_targets(package, tables, resolver):
    from srkg.data import normalise_edges
    from srkg.table_validation import validate_module_support_rows
    edges = normalise_edges(tables["edges"])
    keep = []
    for index, row in edges.iterrows():
        location = f"{package.paths.edges} row {index + 2}"
        if resolver.available(row["target"], kind="edge", location=location, source=str(row["source"])):
            keep.append(index)
    tables["edges"] = edges.loc[keep].copy()
    supports = tables.get("module_supports")
    validate_module_support_rows(supports)
    if supports is not None:
        keep = []
        for index, row in supports.iterrows():
            location = f"{package.paths.module_supports} row {index + 2}"
            if resolver.available(row["target_id"], target_type=str(row["target_type"]).strip(),
                                  kind="module-support", location=location, source=str(row["module_id"])):
                keep.append(index)
        tables["module_supports"] = supports.loc[keep].copy()
    for role, frame in tables.items():
        if frame is None:
            continue
        for column in ("title", "statement", "body", "prompt", "answer", "text", "icon_caption", "detail_caption", "note"):
            if column not in frame:
                continue
            for index, text in frame[column].astype(str).items():
                location = f"{getattr(package.paths, role)} row {index + 2} {column}"
                if "\\cref" not in text:
                    continue
                calls, errors = parse_two_arg_macro_calls(text, "cref")
                if errors:
                    raise KnowledgeBaseLoadError(errors[0] + ": " + location)
                for call in calls:
                    resolver.available(call.args[1], target_type="prose", kind="prose-reference", location=location)


def collection_tables(packages):
    """Read owned frames once; bibliography keys remain scoped to each package."""
    package_tables = [(package, read_domain_tables(package)) for package in packages]
    concept_ids = set().union(*(_ids(tables["nodes"], "id") for _, tables in package_tables))
    module_ids = set().union(*(_ids(tables.get("modules"), "module_id") for _, tables in package_tables))
    block_ids = set().union(*(_ids(tables.get(role), "block_id")
                             for _, tables in package_tables
                             for role in ("content_blocks", "module_content_blocks")))
    resolver = ReferenceResolver([package.id for package in packages], concept_ids, module_ids, block_ids)
    for package, tables in package_tables:
        _owned(package, tables)
        _resolve_targets(package, tables, resolver)
    roles = package_tables[0][1]
    combined = {}
    for role in roles:
        frames = [tables[role] for _, tables in package_tables if tables[role] is not None]
        combined[role] = pd.concat(frames, ignore_index=True) if frames else None
    # These are deliberately resolved locally, not a global citation registry.
    combined["references"] = combined["reference_links"] = None
    scopes = [(tables["references"], tables["reference_links"]) for _, tables in package_tables]
    block_ids = list(combined["content_blocks"]["block_id"])
    if combined["module_content_blocks"] is not None:
        block_ids.extend(combined["module_content_blocks"]["block_id"])
    if len(set(block_ids)) != len(block_ids):
        raise KnowledgeBaseLoadError("Duplicate block_id across domain content/module tables")
    return combined, scopes, resolver


def _layouts(paths, packages, tables):
    concepts, modules, revisions = {}, {}, []
    for package in packages:
        own_nodes = tables["nodes"][tables["nodes"]["domain"] == package.id]
        own_modules = tables["modules"]
        if own_modules is not None:
            own_modules = own_modules[own_modules["domain"] == package.id]
        layout = load_published_layout(package.paths.layout, concept_ids=_ids(own_nodes, "id"),
                                       module_ids=_ids(own_modules, "module_id"))
        concepts.update(layout.concepts)
        modules.update(layout.modules)
        revisions.append((package.id, layout.revision))
    base = paths.layout_revision
    revision = base if base and all(value == base for _, value in revisions) else hashlib.sha256(
        json.dumps(revisions).encode()).hexdigest()[:16]
    return PublishedLayout(revision=revision, concepts=concepts, modules=modules)


def _tutorial_files(paths, packages):
    return [package.paths.tutorials for package in packages] + [(paths.tutorials, True)]


def load_collection(paths, *, domains=None, include_graphics=True):
    from srkg.kb import _assemble_knowledge_base
    from srkg.figures import load_figures
    selected = discover_domains(paths, domains=domains)
    try:
        tables, scopes, resolver = collection_tables(selected)
        kb = _assemble_knowledge_base(paths, tables, include_graphics=False,
            reference_scopes=scopes, tutorial_paths=_tutorial_files(paths, selected),
            reference_warnings=resolver.warnings,
            published_layout=_layouts(paths, selected, tables), domain_packages=selected,
            figures=load_figures(tables.get('figures'), include_svg=include_graphics))
        for package in selected:
            if package.initial_selection:
                kind, separator, target = package.initial_selection.partition(":")
                allowed = {"concept": {concept.id for concept in kb.concepts if concept.domain == package.id},
                           "module": {module.module_id for module in kb.modules if module.domain == package.id}}
                if not separator or target not in allowed.get(kind, set()):
                    raise KnowledgeBaseLoadError(f"{package.root}/domain.yaml: initial_selection must name an owned concept/module")
        seen_edges = set()
        for row in kb.edges_df.itertuples(index=False):
            endpoints = (str(row.source), str(row.target))
            if not kb.edge_key.get(str(row.relation), {}).get("directed", True):
                endpoints = tuple(sorted(endpoints))
            key = (str(row.relation), *endpoints)
            if key in seen_edges:
                raise KnowledgeBaseLoadError(f"Duplicate domain edge: {row.source} {row.relation} {row.target}")
            seen_edges.add(key)
        if include_graphics:
            from srkg.graphic_providers import collect_graphics
            from srkg.graphic_enrichment import enrich_concepts, enrich_modules
            for package in selected:
                owned_graphics = collect_graphics([package])
                known_concepts = {concept.id for concept in kb.concepts if concept.domain == package.id}
                known_modules = {module.module_id for module in kb.modules if module.domain == package.id}
                unknown = (owned_graphics.concepts.keys() - known_concepts) | (owned_graphics.modules.keys() - known_modules)
                if unknown:
                    raise KnowledgeBaseLoadError(f"{package.root}: graphics registry has foreign/unknown IDs: {', '.join(sorted(unknown))}")
            graphics = collect_graphics(selected)
            kb = replace(kb, concepts=tuple(enrich_concepts(list(kb.concepts), graphic=graphics.concept)),
                         modules=tuple(enrich_modules(list(kb.modules), graphic=graphics.module)))
        return replace(kb, build_warnings=tuple(resolver.warnings))
    except (ValueError, KeyError) as exc:
        sources = ", ".join(str(package.root) for package in selected)
        raise KnowledgeBaseLoadError(f"Domain sources [{sources}]: {exc}") from exc


def read_authored_table(data_root, table: str, *, domain: str | None = None):
    """Read a table role across packages; rows are not deduplicated or rewritten.

    Bibliography keys are local: consumers needing resolved references should use
    KnowledgeBase rather than treating this raw concatenation as a global index.
    """
    from srkg.kb import DEFAULT_KB_FILES, resolve_knowledge_base_paths, _read_optional_csv
    role = next((key for key, value in DEFAULT_KB_FILES.items() if value == table), table)
    if role not in DEFAULT_KB_FILES or role in {"layout", "tutorials", "edge_key"}:
        raise KnowledgeBaseLoadError(f"Not an authored table role: {table}")
    paths = resolve_knowledge_base_paths(data_root)
    if paths.domains_root is None:
        return _read_optional_csv(getattr(paths, role))
    packages = discover_domains(paths, domains=[domain] if domain is not None else None)
    frames = [frame for package in packages
              if (frame := _read_optional_csv(getattr(package.paths, role))) is not None]
    return pd.concat(frames, ignore_index=True) if frames else None


def owning_source_paths(data_root, domain: str | None = None):
    """Writing tools require one explicit package in a collection."""
    from srkg.kb import resolve_knowledge_base_paths
    paths = resolve_knowledge_base_paths(data_root)
    if paths.domains_root is None:
        return paths
    if not domain:
        raise KnowledgeBaseLoadError("Select --domain explicitly before modifying a domain collection")
    for package in discover_domains(paths, domains=[domain]):
        if package.id == domain:
            return package.paths
    raise KnowledgeBaseLoadError(f"Unknown domain: {domain}")
