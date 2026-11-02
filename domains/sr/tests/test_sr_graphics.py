from xml.etree import ElementTree
from srkg.concept_svg_graphics import createSvgGraphic
SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse_svg(svg_text: str):
    root = ElementTree.fromstring(svg_text)
    title = root.find(f"{SVG_NS}title")
    return root, title


def test_principle_of_locality_currently_uses_same_icon_and_detail_graphic():
    assert createSvgGraphic("sr.principle_of_locality", variant="detail") == createSvgGraphic(
        "sr.principle_of_locality",
        variant="icon",
    )
