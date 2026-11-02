"""Attach generated graphics to typed records without altering authored content.

This is the single bridge from generic record construction to the existing SVG
registries. Domain-specific generator separation is deferred to issue 7.3.
"""

from dataclasses import replace

from srkg.concept_svg_graphics import createSvgGraphic
from srkg.module_svg_graphics import createModuleSvgGraphic
from srkg.model import Concept, Module


def enrich_concepts(concepts: list[Concept]) -> list[Concept]:
    """Return new records with icon/detail SVGs; missing designs stay empty."""
    return [replace(
        concept,
        svg_icon=createSvgGraphic(concept.id, variant="icon") or "",
        svg_detail=createSvgGraphic(concept.id, variant="detail") or "",
    ) for concept in concepts]


def enrich_modules(modules: list[Module]) -> list[Module]:
    """Return new module records, retaining optional graphics and captions."""
    return [replace(
        module,
        svg_icon=createModuleSvgGraphic(module.module_id, "icon") or "",
        svg_detail=createModuleSvgGraphic(module.module_id, "detail") or "",
    ) for module in modules]
