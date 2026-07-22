"""Compatibility wrapper for deterministic concept SVG graphics.

The implementation lives in ``srkg.svg_graphics``. Existing callers can
continue importing ``createSvgGraphic`` and ``saveSvgGraphics`` from this
module while the graphics package evolves.
"""

from __future__ import annotations

from pathlib import Path

from srkg.svg_graphics.registry import create_svg_graphic, save_svg_graphics


def createSvgGraphic(node_id: str, variant: str = "icon") -> str | None:
    """Return an SVG XML string for a KG node id and variant, if known."""
    return create_svg_graphic(node_id, variant)


def saveSvgGraphics(output_dir: str | Path = ".") -> None:
    """Write all currently implemented icon SVGs to files."""
    save_svg_graphics(output_dir)


if __name__ == "__main__":
    saveSvgGraphics()
