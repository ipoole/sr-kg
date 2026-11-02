"""Compatibility API for discovered domain-owned module graphics."""
from srkg.graphic_providers import default_graphics

IMPLEMENTED_MODULE_IDS = tuple(default_graphics().modules)


def createModuleSvgGraphic(module_id: str, variant: str = "icon") -> str | None:
    return default_graphics().module(module_id, variant)


__all__ = ["IMPLEMENTED_MODULE_IDS", "createModuleSvgGraphic"]
