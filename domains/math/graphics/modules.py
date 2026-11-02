"""Domain-owned module motifs and their accessible titles."""
from functools import partial
from pathlib import Path
from srkg.svg_graphics.module_frames import landscape_svg

ASSETS = {}
TITLES = {}


def create_module(module_id, variant="icon"):
    variant = "detail" if variant == "detail" else "icon"
    source = (Path(__file__).with_name("module_assets") / ASSETS[module_id].format(variant=variant)).read_text(encoding="utf-8")
    return landscape_svg(module_id, TITLES[module_id], source, variant)


MODULE_CREATORS = {module_id: partial(create_module, module_id) for module_id in ASSETS}
