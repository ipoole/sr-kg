"""Public dispatch over discovered domain-owned concept graphic registries."""
from pathlib import Path

from srkg.graphic_providers import default_graphics

CREATORS = default_graphics().concepts
IMPLEMENTED_NODE_IDS = tuple(CREATORS)


def _svg_filename_id(node_id: str) -> str:
    return node_id.replace(" ", "_").replace(".", "_")


def create_svg_graphic(node_id: str, variant: str = "icon") -> str | None:
    creator = CREATORS.get(str(node_id).strip())
    return creator(variant) if creator else None


def save_svg_graphics(output_dir: str | Path = ".") -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for node_id in IMPLEMENTED_NODE_IDS:
        svg = create_svg_graphic(node_id, variant="icon")
        if svg is not None:
            (output / f"image_{_svg_filename_id(node_id)}.svg").write_text(svg, encoding="utf-8")


__all__ = ["CREATORS", "IMPLEMENTED_NODE_IDS", "create_svg_graphic", "save_svg_graphics"]
