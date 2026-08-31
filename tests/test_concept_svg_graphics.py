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
    "M 1.1", "M 1.2", "M 1.3", "M 1.4", "M 1.5", "M 1.6", "M 2.1",
    "M 2.2", "M 2.3",
    "GR 1.1", "GR 1.2", "GR 1.3", "GR 1.4", "GR 1.5",
    "GR 2.1", "GR 2.2", "GR 2.3",
    "GR 3.1", "GR 3.2", "GR 3.3", "GR 3.4", "GR 3.5", "GR 3.6",
    "GR 4.1", "GR 4.2", "GR 4.3", "GR 4.4", "GR 4.5", "GR 4.6",
    "GR 5.1", "GR 5.2", "GR 5.3", "GR 5.4", "GR 5.5", "GR 5.6",
    "GR 6.1", "GR 6.2", "GR 6.3", "GR 6.4", "GR 6.5", "GR 6.6",
    "GR 7.1", "GR 7.2", "GR 7.3", "GR 7.4", "GR 7.5",
    "GR 8.1", "GR 8.2", "GR 8.3", "GR 8.4", "GR 8.5", "GR 8.6",
    "GR 9.1", "GR 9.2", "GR 9.3", "GR 9.4", "GR 9.5", "GR 9.6",
    "GR 10.1", "GR 10.2", "GR 10.3", "GR 10.4", "GR 10.5", "GR 10.6",
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
        ("M 1.1", "Manifold"),
        ("M 1.2", "Coordinate chart"),
        ("M 1.3", "Coordinate transformation"),
        ("M 1.4", "Worldline"),
        ("M 1.5", "Tangent space"),
        ("M 1.6", "Cotangent space"),
        ("M 2.1", "Tensor field"),
        ("M 2.2", "Abstract and component indices"),
        ("M 2.3", "Tensor transformation law"),
        ("GR 1.1", "Gravity as geometry"),
        ("GR 1.2", "Equivalence principle"),
        ("GR 1.3", "Local inertial frame"),
        ("GR 1.4", "Freely falling observer"),
        ("GR 1.5", "Tidal gravity"),
        ("GR 2.1", "Spacetime metric"),
        ("GR 2.2", "Inverse metric"),
        ("GR 2.3", "Volume element"),
        ("GR 3.1", "Line element"),
        ("GR 3.2", "Proper time in curved spacetime"),
        ("GR 3.3", "Null curve"),
        ("GR 3.4", "Causal structure"),
        ("GR 3.5", "Local flatness"),
        ("GR 3.6", "Metric signature convention"),
        ("GR 4.1", "Connection"),
        ("GR 4.2", "Christoffel symbols"),
        ("GR 4.3", "Covariant derivative"),
        ("GR 4.4", "Metric compatibility"),
        ("GR 4.5", "Torsion-free connection"),
        ("GR 4.6", "Parallel transport"),
        ("GR 5.1", "Geodesic"),
        ("GR 5.2", "Geodesic equation"),
        ("GR 5.3", "Geodesic action"),
        ("GR 5.4", "Four-velocity in curved spacetime"),
        ("GR 5.5", "Four-acceleration"),
        ("GR 5.6", "Geodesic deviation"),
        ("GR 6.1", "Riemann curvature tensor"),
        ("GR 6.2", "Ricci tensor"),
        ("GR 6.3", "Ricci scalar"),
        ("GR 6.4", "Einstein tensor"),
        ("GR 6.5", "Bianchi identity"),
        ("GR 6.6", "Curvature invariants"),
        ("GR 7.1", "Stress-energy tensor in GR"),
        ("GR 7.2", "Perfect fluid"),
        ("GR 7.3", "Energy conditions"),
        ("GR 7.4", "Covariant conservation"),
        ("GR 7.5", "Equation of state"),
        ("GR 8.1", "Einstein field equations"),
        ("GR 8.2", "Cosmological constant"),
        ("GR 8.3", "Einstein-Hilbert action"),
        ("GR 8.4", "Stress-energy from action variation"),
        ("GR 8.5", "Trace-reversed equations"),
        ("GR 8.6", "Vacuum field equations"),
        ("GR 9.1", "Weak-field metric"),
        ("GR 9.2", "Newtonian limit"),
        ("GR 9.3", "Gravitational redshift"),
        ("GR 9.4", "Light deflection"),
        ("GR 9.5", "Perihelion precession"),
        ("GR 9.6", "Post-Newtonian approximation"),
        ("GR 10.1", "Schwarzschild metric"),
        ("GR 10.2", "Schwarzschild radius"),
        ("GR 10.3", "Event horizon"),
        ("GR 10.4", "Coordinate singularity"),
        ("GR 10.5", "Black hole singularity"),
        ("GR 10.6", "Effective potential for orbits"),
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
        f"image_{node_id.replace(' ', '_').replace('.', '_')}.svg"
        for node_id in GRAPHIC_NODE_IDS
    }
    assert (tmp_path / "image_1_1.svg").read_text(encoding="utf-8") == createSvgGraphic(
        "1.1",
        variant="icon",
    )
