"""Published graph-layout loading, validation, and deterministic completion."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
from pathlib import Path
from typing import Iterable, Mapping

from srkg.model import LayoutPosition, Module

PUBLISHED_LAYOUT_SCHEMA_VERSION = 1
UNPUBLISHED_LAYOUT_REVISION = "unpublished"


class PublishedLayoutError(ValueError):
    """Raised when a published layout cannot be read or validated."""


@dataclass(frozen=True)
class PublishedLayout:
    """Repository-backed defaults for concept positions and module anchors."""

    schema_version: int = PUBLISHED_LAYOUT_SCHEMA_VERSION
    revision: str = UNPUBLISHED_LAYOUT_REVISION
    concepts: Mapping[str, LayoutPosition] = field(default_factory=dict)
    modules: Mapping[str, LayoutPosition] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "concepts", dict(self.concepts or {}))
        object.__setattr__(self, "modules", dict(self.modules or {}))

    def to_viewer_data(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "revision": self.revision,
            "concepts": {
                concept_id: position.to_viewer_data()
                for concept_id, position in sorted(self.concepts.items())
            },
            "modules": {
                module_id: {"anchor": position.to_viewer_data()}
                for module_id, position in sorted(self.modules.items())
            },
        }


def load_published_layout(
    path: Path | None,
    *,
    concept_ids: Iterable[str],
    module_ids: Iterable[str],
) -> PublishedLayout:
    """Load an optional partial published layout and validate all authored IDs."""
    if path is None or not path.exists():
        return PublishedLayout()

    try:
        raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except PublishedLayoutError:
        raise
    except Exception as exc:
        raise PublishedLayoutError(f"Could not read published layout {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise PublishedLayoutError("layout.json must contain a JSON object")
    schema_version = raw.get("schema_version")
    if schema_version != PUBLISHED_LAYOUT_SCHEMA_VERSION:
        raise PublishedLayoutError(
            f"layout.json has unsupported schema_version: {schema_version!r}"
        )
    revision = raw.get("revision")
    if not isinstance(revision, str) or not revision.strip():
        raise PublishedLayoutError("layout.json must have a non-empty string revision")

    raw_concepts = _mapping(raw.get("concepts"), "concepts")
    raw_modules = _mapping(raw.get("modules"), "modules")
    concepts = {
        str(concept_id): _position(value, f"concept {concept_id}")
        for concept_id, value in raw_concepts.items()
    }
    modules = {
        str(module_id): _module_anchor(value, str(module_id))
        for module_id, value in raw_modules.items()
    }

    unknown_concepts = sorted(set(concepts) - {str(value) for value in concept_ids})
    if unknown_concepts:
        raise PublishedLayoutError(
            "layout.json references unknown concept id(s): " + ", ".join(unknown_concepts)
        )
    unknown_modules = sorted(set(modules) - {str(value) for value in module_ids})
    if unknown_modules:
        raise PublishedLayoutError(
            "layout.json references unknown module id(s): " + ", ".join(unknown_modules)
        )
    return PublishedLayout(
        schema_version=schema_version,
        revision=revision.strip(),
        concepts=concepts,
        modules=modules,
    )


def resolve_published_layout(
    published: PublishedLayout,
    *,
    generated_concept_positions: Mapping[str, tuple[float, float]],
    modules: Iterable[Module],
) -> PublishedLayout:
    """Fill missing concepts and module anchors from deterministic graph geometry."""
    concepts = {
        str(concept_id): published.concepts.get(
            str(concept_id), LayoutPosition(float(position[0]), float(position[1]))
        )
        for concept_id, position in generated_concept_positions.items()
    }
    module_positions: dict[str, LayoutPosition] = {}
    for module in modules:
        module_id = str(module.module_id)
        authored_anchor = published.modules.get(module_id)
        if authored_anchor is not None:
            module_positions[module_id] = authored_anchor
            continue
        member_positions = [
            concepts[concept_id]
            for concept_id in map(str, module.members)
            if concept_id in concepts
        ]
        if member_positions:
            module_positions[module_id] = LayoutPosition(
                sum(position.x for position in member_positions) / len(member_positions),
                sum(position.y for position in member_positions) / len(member_positions),
            )
        else:
            module_positions[module_id] = LayoutPosition(0, 0)
    return PublishedLayout(
        schema_version=published.schema_version,
        revision=published.revision,
        concepts=concepts,
        modules=module_positions,
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise PublishedLayoutError(f"layout.json has duplicate key: {key}")
        result[key] = value
    return result


def _mapping(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise PublishedLayoutError(f"layout.json {name} must be an object")
    return value


def _position(value: object, owner: str) -> LayoutPosition:
    if not isinstance(value, dict) or set(value) != {"x", "y"}:
        raise PublishedLayoutError(
            f"layout.json {owner} position must contain finite numeric x and y"
        )
    x = value.get("x")
    y = value.get("y")
    if (
        isinstance(x, bool) or isinstance(y, bool)
        or not isinstance(x, (int, float)) or not isinstance(y, (int, float))
        or not math.isfinite(float(x)) or not math.isfinite(float(y))
    ):
        raise PublishedLayoutError(
            f"layout.json {owner} position must contain finite numeric x and y"
        )
    return LayoutPosition(float(x), float(y))


def _module_anchor(value: object, module_id: str) -> LayoutPosition:
    if not isinstance(value, dict) or set(value) != {"anchor"}:
        raise PublishedLayoutError(
            f"layout.json module {module_id} must contain an anchor"
        )
    return _position(value["anchor"], f"module {module_id} anchor")
