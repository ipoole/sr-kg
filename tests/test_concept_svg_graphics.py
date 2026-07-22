from xml.etree import ElementTree

import pytest

from srkg.concept_svg_graphics import createSvgGraphic, saveSvgGraphics
from srkg.svg_graphics.registry import IMPLEMENTED_NODE_IDS, create_svg_graphic


GRAPHIC_NODE_IDS = [
    "1.1", "1.2", "1.3",
    "2.2", "2.3",
    "3.1", "3.2", "3.3", "3.4", "3.5",
    "4.1", "4.2", "4.3", "4.4", "4.5", "4.6",
    "5.1", "5.2", "5.3", "5.4", "5.5", "5.6",
    "6.1", "6.2", "6.3", "6.4",
    "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7",
    "8.1", "8.3", "8.4", "8.5", "8.6",
    "9.1", "9.2", "9.3", "9.4",
    "10.1", "10.2", "10.3",
    "11.1", "11.2",
]
SVG_NS = "{http://www.w3.org/2000/svg}"


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
    assert createSvgGraphic(" 1.1 ") == createSvgGraphic("1.1")


def test_public_svg_api_delegates_to_registry():
    assert createSvgGraphic("1.1") == create_svg_graphic("1.1")
    assert list(IMPLEMENTED_NODE_IDS) == GRAPHIC_NODE_IDS


@pytest.mark.parametrize(
    ("node_id", "expected_title"),
    [
        ("1.1", "Inertial frames"),
        ("7.7", "Maxwell's equations"),
        ("8.6", "Lorenz gauge"),
        ("11.2", "Gauge fixing"),
    ],
)
def test_create_svg_graphic_uses_expected_accessible_titles(node_id, expected_title):
    _, title = _parse_svg(createSvgGraphic(node_id))

    assert title.text == expected_title


@pytest.mark.parametrize("node_id", [
    node_id
    for node_id in GRAPHIC_NODE_IDS
    if node_id != "2.3"
])
def test_detail_variant_adds_or_changes_graphic_content_for_most_nodes(node_id):
    assert createSvgGraphic(node_id, variant="detail") != createSvgGraphic(
        node_id,
        variant="icon",
    )


def test_principle_of_locality_currently_uses_same_icon_and_detail_graphic():
    assert createSvgGraphic("2.3", variant="detail") == createSvgGraphic(
        "2.3",
        variant="icon",
    )


def test_save_svg_graphics_writes_current_icon_set(tmp_path):
    saveSvgGraphics(tmp_path)

    saved_files = {path.name for path in tmp_path.glob("image_*.svg")}
    assert saved_files == {
        f"image_{node_id.replace('.', '_')}.svg"
        for node_id in GRAPHIC_NODE_IDS
    }
    assert (tmp_path / "image_1_1.svg").read_text(encoding="utf-8") == createSvgGraphic(
        "1.1",
        variant="icon",
    )
