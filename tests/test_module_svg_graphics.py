from xml.etree import ElementTree

import pytest

from srkg.module_svg_graphics import IMPLEMENTED_MODULE_IDS, createModuleSvgGraphic


SVG_NS = "{http://www.w3.org/2000/svg}"


@pytest.mark.parametrize("module_id", IMPLEMENTED_MODULE_IDS)
@pytest.mark.parametrize("variant", ["icon", "detail"])
def test_module_graphics_are_accessible_landscape_svgs(module_id, variant):
    svg = createModuleSvgGraphic(module_id, variant)
    root = ElementTree.fromstring(svg)
    title = root.find(f"{SVG_NS}title")

    assert root.attrib["viewBox"] == "0 0 768 480"
    assert root.attrib["role"] == "img"
    assert title is not None and title.text
    assert root.attrib["aria-labelledby"] == title.attrib["id"]


def test_module_graphics_are_optional_and_use_stable_semantic_ids():
    assert createModuleSvgGraphic("math.m01_manifolds_and_coordinates") is None
    assert createModuleSvgGraphic(" sr.spacetime_foundations ") == createModuleSvgGraphic(
        "sr.spacetime_foundations"
    )


def test_module_detail_variants_enrich_the_icon_motif():
    for module_id in IMPLEMENTED_MODULE_IDS:
        assert createModuleSvgGraphic(module_id, "detail") != createModuleSvgGraphic(
            module_id, "icon"
        )


def test_module_detail_graphics_have_one_landscape_framing_border():
    for module_id in IMPLEMENTED_MODULE_IDS:
        root = ElementTree.fromstring(createModuleSvgGraphic(module_id, "detail"))
        framing_rects = [
            rect for rect in root.iter(f"{SVG_NS}rect")
            if rect.attrib.get("stroke") == "#dbe3f3"
        ]
        assert len(framing_rects) == 1


def test_module_icon_graphics_leave_framing_to_the_viewer():
    for module_id in IMPLEMENTED_MODULE_IDS:
        root = ElementTree.fromstring(createModuleSvgGraphic(module_id, "icon"))
        framing_rects = [
            rect for rect in root.iter(f"{SVG_NS}rect")
            if rect.attrib.get("stroke") == "#dbe3f3"
        ]
        assert framing_rects == []
