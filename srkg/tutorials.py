"""Authored tutorial-route loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


TUTORIAL_SCHEMA_VERSION = 1
TUTORIAL_CATEGORIES = frozenset({"interface", "physics"})
TUTORIAL_COMMANDS = frozenset({
    "select",
    "clear-selection",
    "set-display-scope",
    "set-context",
    "set-details-mode",
    "set-module-representation",
    "set-all-module-representations",
    "fit",
    "open-details-block",
    "open-details-relationship",
    "show-relationship-in-graph",
    "show-graph-concept-hover",
    "show-graph-edge-hover",
    "show-tools-section",
    "search",
    "close-search",
    "wait",
})
DISPLAY_SCOPES = frozenset({"full", "context", "hidden"})
CONTEXT_PRESETS = frozenset({
    "connections",
    "prerequisites",
    "derivation",
    "foundations",
    "uses",
    "related",
})
CONTEXT_DEPTHS = frozenset({"one-hop", "two-hops", "transitive"})
DETAILS_MODES = frozenset({"full", "folded", "hidden"})
MODULE_REPRESENTATIONS = frozenset({"folded", "expanded"})
FIT_TARGETS = frozenset({"reveal", "selection", "context", "displayed"})
TOOLS_SECTIONS = frozenset({
    "tutorials",
    "modules",
    "layouts",
    "study",
    "personal-data",
    "notes",
})
DETAILS_RELATIONSHIP_SECTIONS = frozenset({"derived-from", "where-used"})
TUTORIAL_EDGE_RELATIONS = frozenset({
    "REQUIRES",
    "DERIVES_FROM",
    "CONSTRUCTED_FROM",
    "COMPONENT_OF",
    "INSTANCE_OF",
    "RELATED",
})
CONTROL_TARGETS = frozenset({
    "context",
    "depth",
    "fit",
    "display-scope",
    "details-mode",
    "search",
    "search-input",
    "tools",
    "clear-selection",
})


class TutorialLoadError(ValueError):
    """Raised when authored tutorial data is not safe to load."""


@dataclass(frozen=True)
class TutorialStep:
    """One narrated semantic action in a tutorial route."""

    step_id: str
    title: str
    commentary: str
    action: dict[str, object]
    prepare: tuple[dict[str, object], ...] = ()
    pointer_target: str | None = None

    def to_viewer_data(self) -> dict[str, object]:
        data: dict[str, object] = {
            "step_id": self.step_id,
            "title": self.title,
            "commentary": self.commentary,
            "action": dict(self.action),
        }
        if self.prepare:
            data["prepare"] = [dict(command) for command in self.prepare]
        if self.pointer_target:
            data["pointer"] = {"target": self.pointer_target}
        return data


@dataclass(frozen=True)
class Tutorial:
    """One validated authored tutorial route."""

    tutorial_id: str
    title: str
    category: str
    summary: str
    sequence: int
    domains: tuple[str, ...]
    steps: tuple[TutorialStep, ...]

    def to_viewer_data(self) -> dict[str, object]:
        return {
            "tutorial_id": self.tutorial_id,
            "title": self.title,
            "category": self.category,
            "summary": self.summary,
            "sequence": self.sequence,
            "domains": list(self.domains),
            "steps": [step.to_viewer_data() for step in self.steps],
        }


def load_tutorials(
    path: Path | None,
    *,
    concept_ids: Iterable[str],
    module_ids: Iterable[str],
    block_ids: Iterable[str],
    domain_ids: Iterable[str] | None = None,
) -> tuple[Tutorial, ...]:
    """Load and validate tutorials from one YAML source file."""
    if path is None or not path.exists():
        return ()

    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise TutorialLoadError(f"Could not read tutorial data {path}: {exc}") from exc
    if document is None:
        document = {}
    if not isinstance(document, dict):
        raise TutorialLoadError("tutorials.yaml must contain a mapping")
    if document.get("schema_version") != TUTORIAL_SCHEMA_VERSION:
        raise TutorialLoadError(
            "tutorials.yaml has unsupported schema_version: "
            f"{document.get('schema_version')!r}"
        )
    rows = document.get("tutorials", [])
    if not isinstance(rows, list):
        raise TutorialLoadError("tutorials.yaml tutorials must be a list")

    known_concepts = {str(item) for item in concept_ids}
    known_modules = {str(item) for item in module_ids}
    known_blocks = {str(item) for item in block_ids}
    known_domains = {str(item) for item in domain_ids or ()}
    tutorials: list[Tutorial] = []
    tutorial_ids: set[str] = set()
    for index, row in enumerate(rows):
        context = f"tutorials[{index}]"
        mapping = _mapping(row, context)
        tutorial_id = _required_text(mapping, "tutorial_id", context)
        if tutorial_id in tutorial_ids:
            raise TutorialLoadError(f"Duplicate tutorial id in tutorials.yaml: {tutorial_id}")
        tutorial_ids.add(tutorial_id)
        category = _required_text(mapping, "category", context)
        if category not in TUTORIAL_CATEGORIES:
            raise TutorialLoadError(
                f"{context} has invalid category {category!r}"
            )
        sequence = _integer(mapping.get("sequence"), f"{context}.sequence")
        domains = _text_list(mapping.get("domains"), f"{context}.domains")
        if not domains:
            raise TutorialLoadError(f"{context}.domains must not be empty")
        unknown_domains = sorted(set(domains) - known_domains) if known_domains else []
        if unknown_domains:
            raise TutorialLoadError(
                f"{context}.domains references unknown domain(s): "
                + ", ".join(unknown_domains)
            )
        step_rows = mapping.get("steps")
        if not isinstance(step_rows, list) or not step_rows:
            raise TutorialLoadError(f"{context}.steps must be a non-empty list")
        steps = _load_steps(
            step_rows,
            context=context,
            concept_ids=known_concepts,
            module_ids=known_modules,
            block_ids=known_blocks,
        )
        tutorials.append(Tutorial(
            tutorial_id=tutorial_id,
            title=_required_text(mapping, "title", context),
            category=category,
            summary=_required_text(mapping, "summary", context),
            sequence=sequence,
            domains=tuple(domains),
            steps=steps,
        ))
    return tuple(sorted(tutorials, key=lambda item: (item.sequence, item.tutorial_id)))


def tutorials_for_domains(
    tutorials: Iterable[Tutorial],
    available_domains: Iterable[str],
) -> tuple[Tutorial, ...]:
    """Return tutorials whose declared domain requirements are available."""
    available = {str(domain) for domain in available_domains}
    return tuple(
        tutorial
        for tutorial in tutorials
        if set(tutorial.domains).issubset(available)
    )


def _load_steps(
    rows: list[object],
    *,
    context: str,
    concept_ids: set[str],
    module_ids: set[str],
    block_ids: set[str],
) -> tuple[TutorialStep, ...]:
    steps: list[TutorialStep] = []
    step_ids: set[str] = set()
    for index, row in enumerate(rows):
        step_context = f"{context}.steps[{index}]"
        mapping = _mapping(row, step_context)
        step_id = _required_text(mapping, "step_id", step_context)
        if step_id in step_ids:
            raise TutorialLoadError(f"Duplicate step id in {context}: {step_id}")
        step_ids.add(step_id)
        prepare_rows = mapping.get("prepare", [])
        if not isinstance(prepare_rows, list):
            raise TutorialLoadError(f"{step_context}.prepare must be a list")
        prepare = tuple(
            _validate_command(
                _mapping(command, f"{step_context}.prepare[{command_index}]"),
                context=f"{step_context}.prepare[{command_index}]",
                concept_ids=concept_ids,
                module_ids=module_ids,
                block_ids=block_ids,
            )
            for command_index, command in enumerate(prepare_rows)
        )
        action = _validate_command(
            _mapping(mapping.get("action"), f"{step_context}.action"),
            context=f"{step_context}.action",
            concept_ids=concept_ids,
            module_ids=module_ids,
            block_ids=block_ids,
        )
        pointer_target = None
        if "pointer" in mapping:
            pointer = _mapping(mapping["pointer"], f"{step_context}.pointer")
            pointer_target = _required_text(pointer, "target", f"{step_context}.pointer")
            _validate_pointer_target(
                pointer_target,
                context=f"{step_context}.pointer target",
                concept_ids=concept_ids,
                module_ids=module_ids,
                block_ids=block_ids,
            )
        steps.append(TutorialStep(
            step_id=step_id,
            title=_required_text(mapping, "title", step_context),
            commentary=_required_text(mapping, "commentary", step_context),
            action=action,
            prepare=prepare,
            pointer_target=pointer_target,
        ))
    return tuple(steps)


def _validate_command(
    command: dict[str, object],
    *,
    context: str,
    concept_ids: set[str],
    module_ids: set[str],
    block_ids: set[str],
) -> dict[str, object]:
    name = _required_text(command, "command", context)
    if name not in TUTORIAL_COMMANDS:
        raise TutorialLoadError(f"{context} has unsupported command: {name}")

    if name == "select":
        target = _required_text(command, "target", context)
        _validate_object_target(target, context, concept_ids, module_ids)
    elif name == "set-display-scope":
        _enum(command, "value", DISPLAY_SCOPES, context)
    elif name == "set-context":
        _enum(command, "preset", CONTEXT_PRESETS, context)
        _enum(command, "depth", CONTEXT_DEPTHS, context)
    elif name == "set-details-mode":
        _enum(command, "value", DETAILS_MODES, context)
    elif name == "set-module-representation":
        target = _required_text(command, "target", context)
        _validate_prefixed_known(target, "module:", module_ids, "module", context)
        _enum(command, "value", MODULE_REPRESENTATIONS, context)
    elif name == "set-all-module-representations":
        _enum(command, "value", MODULE_REPRESENTATIONS, context)
    elif name == "fit":
        _enum(command, "value", FIT_TARGETS, context)
    elif name == "open-details-block":
        target = _required_text(command, "target", context)
        _validate_prefixed_known(target, "block:", block_ids, "block", context)
    elif name == "open-details-relationship":
        _enum(command, "value", DETAILS_RELATIONSHIP_SECTIONS, context)
    elif name == "show-relationship-in-graph":
        _enum(command, "preset", CONTEXT_PRESETS, context)
        if not isinstance(command.get("full_tree"), bool):
            raise TutorialLoadError(f"{context}.full_tree must be a boolean")
    elif name == "show-graph-concept-hover":
        target = _required_text(command, "target", context)
        _validate_prefixed_known(target, "concept:", concept_ids, "concept", context)
    elif name == "show-graph-edge-hover":
        target = _required_text(command, "target", context)
        _validate_edge_target(target, "edge:", context, concept_ids)
    elif name == "show-tools-section":
        _enum(command, "value", TOOLS_SECTIONS, context)
    elif name == "search":
        query = _required_text(command, "query", context)
        if len(query) > 200:
            raise TutorialLoadError(f"{context}.query must be at most 200 characters")
    elif name == "wait":
        milliseconds = _integer(command.get("milliseconds"), f"{context}.milliseconds")
        if not 0 <= milliseconds <= 5000:
            raise TutorialLoadError(
                f"{context}.milliseconds must be between 0 and 5000"
            )
    return {str(key): value for key, value in command.items()}


def _validate_pointer_target(
    target: str,
    *,
    context: str,
    concept_ids: set[str],
    module_ids: set[str],
    block_ids: set[str],
) -> None:
    if target == "narration" or target in {
        "details:heading",
        "details:contents",
        "details:derived-from-show-graph",
        "details:where-used-show-graph",
    }:
        return
    if target.startswith("control:module-fold:"):
        module_id = target.removeprefix("control:module-fold:")
        if module_id not in module_ids:
            raise TutorialLoadError(
                f"{context} references unknown module: {module_id}"
            )
        return
    if target.startswith("control:"):
        control = target.removeprefix("control:")
        if control not in CONTROL_TARGETS:
            raise TutorialLoadError(f"{context} has unknown control: {control}")
        return
    if target.startswith("graph:concept:"):
        concept_id = target.removeprefix("graph:concept:")
        if concept_id not in concept_ids:
            raise TutorialLoadError(
                f"{context} references unknown concept: {concept_id}"
            )
        return
    if target.startswith("graph:module:"):
        module_id = target.removeprefix("graph:module:")
        if module_id not in module_ids:
            raise TutorialLoadError(
                f"{context} references unknown module: {module_id}"
            )
        return
    if target.startswith("graph:edge:"):
        _validate_edge_target(target, "graph:edge:", context, concept_ids)
        return
    if target.startswith("search:concept:"):
        concept_id = target.removeprefix("search:concept:")
        if concept_id not in concept_ids:
            raise TutorialLoadError(
                f"{context} references unknown concept: {concept_id}"
            )
        return
    if target.startswith("search:module:"):
        module_id = target.removeprefix("search:module:")
        if module_id not in module_ids:
            raise TutorialLoadError(
                f"{context} references unknown module: {module_id}"
            )
        return
    if target.startswith("details:block:"):
        block_id = target.removeprefix("details:block:")
        if block_id not in block_ids:
            raise TutorialLoadError(
                f"{context} references unknown block: {block_id}"
            )
        return
    if target.startswith("tools:section:"):
        section = target.removeprefix("tools:section:")
        if section not in TOOLS_SECTIONS:
            raise TutorialLoadError(f"{context} has unknown Tools section: {section}")
        return
    raise TutorialLoadError(f"{context} is unsupported: {target}")


def _validate_object_target(
    target: str,
    context: str,
    concept_ids: set[str],
    module_ids: set[str],
) -> None:
    if target.startswith("concept:"):
        _validate_prefixed_known(target, "concept:", concept_ids, "concept", context)
        return
    if target.startswith("module:"):
        _validate_prefixed_known(target, "module:", module_ids, "module", context)
        return
    raise TutorialLoadError(f"{context}.target must identify a concept or module")


def _validate_edge_target(
    target: str,
    prefix: str,
    context: str,
    concept_ids: set[str],
) -> None:
    if not target.startswith(prefix):
        raise TutorialLoadError(f"{context}.target must start with {prefix}")
    parts = target.removeprefix(prefix).split("|")
    if len(parts) != 3 or any(not part for part in parts):
        raise TutorialLoadError(
            f"{context}.target must identify source|RELATION|target"
        )
    source_id, relation, target_id = parts
    if source_id not in concept_ids:
        raise TutorialLoadError(f"{context} references unknown concept: {source_id}")
    if target_id not in concept_ids:
        raise TutorialLoadError(f"{context} references unknown concept: {target_id}")
    if relation not in TUTORIAL_EDGE_RELATIONS:
        raise TutorialLoadError(f"{context} references unknown relation: {relation}")


def _validate_prefixed_known(
    target: str,
    prefix: str,
    known: set[str],
    kind: str,
    context: str,
) -> None:
    if not target.startswith(prefix):
        raise TutorialLoadError(f"{context}.target must start with {prefix}")
    identifier = target.removeprefix(prefix)
    if identifier not in known:
        raise TutorialLoadError(f"{context} references unknown {kind}: {identifier}")


def _mapping(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TutorialLoadError(f"{context} must be a mapping")
    return {str(key): item for key, item in value.items()}


def _required_text(mapping: dict[str, object], key: str, context: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise TutorialLoadError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def _text_list(value: object, context: str) -> list[str]:
    if not isinstance(value, list):
        raise TutorialLoadError(f"{context} must be a list")
    result = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise TutorialLoadError(f"{context} must contain non-empty strings")
        result.append(item.strip())
    if len(result) != len(set(result)):
        raise TutorialLoadError(f"{context} contains duplicate values")
    return result


def _integer(value: object, context: str) -> int:
    if isinstance(value, bool):
        raise TutorialLoadError(f"{context} must be an integer")
    try:
        integer = int(value)
    except (TypeError, ValueError) as exc:
        raise TutorialLoadError(f"{context} must be an integer") from exc
    if str(value).strip() != str(integer):
        raise TutorialLoadError(f"{context} must be an integer")
    return integer


def _enum(
    mapping: dict[str, object],
    key: str,
    allowed: frozenset[str],
    context: str,
) -> str:
    value = _required_text(mapping, key, context)
    if value not in allowed:
        raise TutorialLoadError(
            f"{context}.{key} has unsupported value {value!r}"
        )
    return value
