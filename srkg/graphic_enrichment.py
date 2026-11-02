"""Attach generated graphics to typed records without altering authored content.

This bridge accepts a domain collection dispatcher. Legacy callers use the
public compatibility APIs, which discover the repository collection lazily.
"""

from dataclasses import replace

from srkg.model import Concept, Module



def createSvgGraphic(concept_id, variant="icon"):
    from srkg.concept_svg_graphics import createSvgGraphic as create
    return create(concept_id, variant=variant)


def createModuleSvgGraphic(module_id, variant="icon"):
    from srkg.module_svg_graphics import createModuleSvgGraphic as create
    return create(module_id, variant=variant)


def enrich_concepts(concepts: list[Concept], *, graphic=None) -> list[Concept]:
    """Return new records with icon/detail SVGs; missing designs stay empty."""
    create = graphic or createSvgGraphic
    return [replace(
        concept,
        svg_icon=create(concept.id, variant="icon") or "",
        svg_detail=create(concept.id, variant="detail") or "",
    ) for concept in concepts]


def enrich_modules(modules: list[Module], *, graphic=None) -> list[Module]:
    """Return new module records, retaining optional graphics and captions."""
    create = graphic or createModuleSvgGraphic
    return [replace(
        module,
        svg_icon=create(module.module_id, "icon") or "",
        svg_detail=create(module.module_id, "detail") or "",
    ) for module in modules]
