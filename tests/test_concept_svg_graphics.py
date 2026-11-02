from xml.etree import ElementTree
import json
from pathlib import Path
import pytest
from srkg.concept_svg_graphics import createSvgGraphic, saveSvgGraphics
from srkg.svg_graphics.registry import IMPLEMENTED_NODE_IDS, create_svg_graphic
from srkg.kb import load_knowledge_base, resolve_knowledge_base_paths
from srkg.domain_sources import discover_domains

GRAPHIC_NODE_IDS = list(IMPLEMENTED_NODE_IDS)
SVG_NS = "{http://www.w3.org/2000/svg}"
EXPECTATIONS = [json.loads((package.root / "tests/graphics_expectations.json").read_text())
                for package in discover_domains(resolve_knowledge_base_paths(Path(__file__).parents[1]/"data"))
                if (package.root / "tests/graphics_expectations.json").exists()]
TITLES = {key: title for spec in EXPECTATIONS for key, title in spec["titles"].items()}
SAME_VARIANTS = {key for spec in EXPECTATIONS for key in spec["same_variants"]}


def _parse_svg(svg_text: str):
    root = ElementTree.fromstring(svg_text)
    title = root.find(f"{SVG_NS}title")
    return root, title


@pytest.mark.parametrize("node_id", GRAPHIC_NODE_IDS)
@pytest.mark.parametrize("variant", ["icon", "detail"])
def test_create_svg_graphic_returns_valid_accessible_square_svg(node_id, variant):
    svg_text = createSvgGraphic(node_id, variant=variant)

    assert svg_text is not None
    assert svg_text.strip().startswith("<svg")
    root, title = _parse_svg(svg_text)
    assert root.tag == f"{SVG_NS}svg"
    assert root.attrib["width"] == "512"
    assert root.attrib["height"] == "512"
    assert root.attrib["viewBox"] == "0 0 512 512"
    assert root.attrib["role"] == "img"
    assert title is not None
    assert root.attrib["aria-labelledby"] == title.attrib["id"]
    assert title.text


def test_create_svg_graphic_returns_none_for_unknown_node_id():
    assert createSvgGraphic("99.99") is None


def test_create_svg_graphic_trims_node_id_whitespace():
    assert createSvgGraphic(" " + GRAPHIC_NODE_IDS[0] + " ") == createSvgGraphic(GRAPHIC_NODE_IDS[0])


def test_public_svg_api_delegates_to_registry():
    assert createSvgGraphic(GRAPHIC_NODE_IDS[0]) == create_svg_graphic(GRAPHIC_NODE_IDS[0])
    assert list(IMPLEMENTED_NODE_IDS) == GRAPHIC_NODE_IDS


@pytest.mark.parametrize(("node_id", "expected_title"), list(TITLES.items()))
def test_create_svg_graphic_uses_expected_accessible_titles(node_id, expected_title):
    _, title = _parse_svg(createSvgGraphic(node_id))

    assert title.text == expected_title


@pytest.mark.parametrize("node_id", [key for key in GRAPHIC_NODE_IDS if key not in SAME_VARIANTS])
def test_detail_variant_adds_or_changes_graphic_content_for_most_nodes(node_id):
    assert createSvgGraphic(node_id, variant="detail") != createSvgGraphic(
        node_id,
        variant="icon",
    )


def test_save_svg_graphics_writes_current_icon_set(tmp_path):
    saveSvgGraphics(tmp_path)

    saved_files = {path.name for path in tmp_path.glob("image_*.svg")}
    assert saved_files == {
        f"image_{node_id.replace(' ', '_').replace('.', '_')}.svg"
        for node_id in GRAPHIC_NODE_IDS
    }
    assert (tmp_path / f"image_{GRAPHIC_NODE_IDS[0].replace(chr(46), chr(95))}.svg").read_text(encoding="utf-8") == createSvgGraphic(
        GRAPHIC_NODE_IDS[0],
        variant="icon",
    )


def test_registered_graphics_cover_the_authored_concepts():
    kb = load_knowledge_base(Path(__file__).parents[1]/"data", include_graphics=False)
    assert set(GRAPHIC_NODE_IDS) == set(kb.concept_data())
