"""Normalised authored content and shared-reference contracts, independent of HTML.

Sources are stored once. References are never expanded while loading: recursion
and transient reading occurrences belong to the renderer, not the KB graph.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
import json
import re
from types import MappingProxyType

from srkg.domain_references import BuildWarning, domain_namespace
from srkg.schema import KnowledgeBaseLoadError
from srkg.text_macros import parse_macro_calls


@dataclass(frozen=True)
class ContentText:
    text: str

    def to_viewer_data(self):
        return {"type": "text", "text": self.text}


@dataclass(frozen=True)
class ContentReference:
    slot: str
    target_id: str
    target_label: str
    hook: str

    def to_viewer_data(self):
        return {"type": "reference", "slot": self.slot, "target_id": self.target_id,
                "target_label": self.target_label, "hook": self.hook}


@dataclass(frozen=True)
class ContentFigure:
    slot: str
    figure_id: str

    def to_viewer_data(self):
        return {"type": "figure", "slot": self.slot, "figure_id": self.figure_id}


@dataclass(frozen=True)
class ContentExplanation:
    slot: str
    title: str
    parts: tuple[ContentPart, ...]

    def to_viewer_data(self):
        return {"type": "explanation", "slot": self.slot, "title": self.title,
                "parts": [part.to_viewer_data() for part in self.parts]}


ContentPart = ContentText | ContentReference | ContentExplanation | ContentFigure
_MACROS = {"optional_details": 2, "explanation": 3, "explain": 4, "figure": 2}
_SLOT = re.compile(r"[a-z][a-z0-9_-]*\Z")


def _calls(text, location, *, legacy_errors_as_text=False):
    calls = []
    for name, count in _MACROS.items():
        found, errors = parse_macro_calls(text, name, count)
        if errors and not (legacy_errors_as_text and name == "optional_details"):
            raise KnowledgeBaseLoadError(f"{location}: \\{name}: {errors[0]}")
        calls.extend(found)
    return sorted(calls, key=lambda call: call.start)


def _inline(text, location):
    if not text.strip():
        raise KnowledgeBaseLoadError(f"{location}: value must not be empty")
    if _calls(text, location):
        raise KnowledgeBaseLoadError(f"{location}: disclosures/references are not allowed here")
    return text.strip()


def parse_content(text: str, location: str = "content", *,
                  _depth=0, _legacy_errors_as_text=False) -> tuple[ContentPart, ...]:
    """Split text into recursive local explanations and unexpanded references.

    Preserve ordinary text, MathJax and existing inline macros byte-for-byte.
    Legacy anonymous disclosures receive page-local positional slots only.
    """
    if _depth > 100:
        raise KnowledgeBaseLoadError(f"{location}: local explanation nesting exceeds 100")
    parts = []
    pos = 0
    slots = set()
    legacy_index = 0
    for call in _calls(text, location, legacy_errors_as_text=_legacy_errors_as_text):
        if call.start < pos:
            continue  # A child is parsed inside its parent, never a second time.
        if call.start > pos:
            parts.append(ContentText(text[pos:call.start]))
        if call.name == "optional_details":
            legacy_index += 1
            slot = f"~legacy-{legacy_index}"
            title, body = call.args
            if _legacy_errors_as_text and (not title.strip() or not body.strip()):
                parts.append(ContentText(text[call.start:call.end]))
                pos = call.end
                continue
        else:
            slot = call.args[0].strip()
            if not _SLOT.fullmatch(slot):
                raise KnowledgeBaseLoadError(f"{location}: invalid content slot {slot!r}")
        if slot in slots:
            raise KnowledgeBaseLoadError(f"{location}: duplicate content slot {slot!r}")
        slots.add(slot)
        child_location = f"{location}/{slot}"
        if call.name == "figure":
            target = call.args[1].strip()
            domain_namespace(target, child_location)
            parts.append(ContentFigure(slot, target))
        elif call.name == "explain":
            _, target, label, hook = call.args
            target = target.strip()
            domain_namespace(target, child_location)
            parts.append(ContentReference(slot, target, _inline(label, child_location),
                                          _inline(hook, child_location)))
        else:
            if call.name == "explanation":
                _, title, body = call.args
            title = _inline(title, child_location)
            if not body.strip():
                raise KnowledgeBaseLoadError(f"{child_location}: explanation body must not be empty")
            parts.append(ContentExplanation(slot, title,
                parse_content(body, child_location, _depth=_depth + 1,
                              _legacy_errors_as_text=_legacy_errors_as_text)))
        pos = call.end
    if pos < len(text):
        parts.append(ContentText(text[pos:]))
    return tuple(parts)


@dataclass(frozen=True)
class ContentUnit:
    source_id: str
    owner_type: str
    owner_id: str
    kind: str
    title: str
    statement: str
    parts: tuple[ContentPart, ...]
    graphic: str = ""
    preview_figure: str = ""

    def to_viewer_data(self):
        data = {"source_id": self.source_id, "owner_type": self.owner_type,
                "owner_id": self.owner_id, "kind": self.kind, "title": self.title,
                "statement": self.statement,
                "parts": [part.to_viewer_data() for part in self.parts]}
        if self.graphic:
            data["graphic"] = {"owner_type": self.owner_type, "owner_id": self.owner_id,
                               "variant": self.graphic}
        if self.preview_figure:
            data['preview_figure'] = self.preview_figure
        return data


@dataclass(frozen=True)
class OccurrencePath:
    """A transient reading path, never a new note/read-mark or source identity."""
    root_id: str
    steps: tuple[tuple[str, str], ...] = ()

    def child(self, slot: str, target_id: str = "") -> OccurrencePath:
        return OccurrencePath(self.root_id, self.steps + ((slot, target_id),))

    @property
    def key(self) -> str:
        return json.dumps([self.root_id, *self.steps], ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class ReferenceResolution:
    state: str  # available | cycle | unavailable
    unit: ContentUnit | None


class ContentRegistry(Mapping[str, ContentUnit]):
    """One source map with path-local cycle detection and no eager expansion."""
    def __init__(self, units=(), *, domains=(), figures=None):
        sources = {}
        for unit in units:
            if unit.source_id in sources:
                raise KnowledgeBaseLoadError(f"Duplicate content source ID: {unit.source_id}")
            sources[unit.source_id] = unit
        self._sources = MappingProxyType(sources)
        self.domains = frozenset(domains)
        self.figures = MappingProxyType(dict(figures or {}))
        warnings = []
        for unit in sources.values():
            if unit.preview_figure and (not unit.statement or not any(
                isinstance(part, ContentFigure) and part.slot == unit.preview_figure for part in unit.parts
            )):
                raise KnowledgeBaseLoadError(f'{unit.source_id}: preview figure needs a statement and a main-body figure slot')
            for figure, path in _figures(unit.parts):
                location = f"content block {unit.source_id}/{'/'.join(path)}"
                namespace = domain_namespace(figure.figure_id, location)
                if namespace not in self.domains:
                    warnings.append(BuildWarning('figure-reference', namespace,
                        figure.figure_id, location, unit.source_id))
                elif figure.figure_id not in self.figures:
                    raise KnowledgeBaseLoadError(f'{location}: unresolved figure {figure.figure_id}')
            for reference, path in _references(unit.parts):
                location = f"content block {unit.source_id}/{'/'.join(path)}"
                namespace = domain_namespace(reference.target_id, location)
                if namespace not in self.domains:
                    warnings.append(BuildWarning('content-reference', namespace,
                        reference.target_id, location, unit.source_id))
                elif reference.target_id not in sources:
                    raise KnowledgeBaseLoadError(f"{location}: {reference.target_id} is unresolved within loaded domain {namespace}")
                elif not sources[reference.target_id].statement:
                    raise KnowledgeBaseLoadError(f"{location}: borrowed source {reference.target_id} needs an explicit statement")
        self.warnings = tuple(warnings)

    def __getitem__(self, source_id: str) -> ContentUnit:
        return self._sources[source_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self._sources)

    def __len__(self) -> int:
        return len(self._sources)

    def resolve(self, reference: ContentReference, *, ancestors=()) -> ReferenceResolution:
        unit = self._sources.get(reference.target_id)
        if unit is None:
            namespace = domain_namespace(reference.target_id)
            if namespace in self.domains:
                raise KnowledgeBaseLoadError(f"Unknown content source: {reference.target_id}")
            return ReferenceResolution('unavailable', None)
        return ReferenceResolution('cycle' if unit.source_id in ancestors else 'available', unit)

    def to_viewer_data(self):
        return {source_id: unit.to_viewer_data() for source_id, unit in self.items()}


def _references(parts, path=()):
    for part in parts:
        if isinstance(part, ContentReference):
            yield part, path + (part.slot,)
        elif isinstance(part, ContentExplanation):
            yield from _references(part.parts, path + (part.slot,))


def _figures(parts, path=()):
    for part in parts:
        if isinstance(part, ContentFigure):
            yield part, path + (part.slot,)
        elif isinstance(part, ContentExplanation):
            yield from _figures(part.parts, path + (part.slot,))


def build_content_registry(concepts, modules, *, domains, figures=None) -> ContentRegistry:
    """Normalise existing concept and module blocks through one source contract."""
    units = []
    for owner_type, owners, key in [('concept', concepts, 'id'), ('module', modules, 'module_id')]:
        for owner in owners:
            for block in owner.content_blocks:
                location = f"content block {block.block_id}"
                statement = _inline(block.statement, location + ' statement') if block.statement.strip() else ''
                if (block.kind == 'graphic') != (block.graphic == 'detail') or block.graphic not in {'', 'detail'}:
                    raise KnowledgeBaseLoadError(f"{location}: graphic blocks require graphic=detail; other kinds must leave graphic empty")
                units.append(ContentUnit(block.block_id, owner_type, getattr(owner, key),
                    block.kind, block.title, statement,
                    # Existing editorial validation reports malformed legacy
                    # macros alongside other text errors, rather than failing
                    # loading before it can collect those diagnostics.
                    parse_content(block.body, location, _legacy_errors_as_text=True), block.graphic,
                    block.preview_figure))
    return ContentRegistry(units, domains=domains, figures=figures)
