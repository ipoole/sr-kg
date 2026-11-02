from xml.etree import ElementTree
from srkg.concept_svg_graphics import createSvgGraphic
SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse_svg(svg_text: str):
    root = ElementTree.fromstring(svg_text)
    title = root.find(f"{SVG_NS}title")
    return root, title


def test_tangent_space_basis_follows_the_plane_axes_and_label_is_contiguous():
    root, _ = _parse_svg(createSvgGraphic("math.tangent_space", variant="detail"))
    lines = root.findall(f"{SVG_NS}line")
    guides = [
        line for line in lines
        if line.attrib.get("stroke") == "#555555"
        and line.attrib.get("opacity") == "0.55"
    ]
    basis = [line for line in lines if line.attrib.get("stroke") == "#248a3d"]

    assert len(guides) == 2
    assert len(basis) == 2

    def vector(line):
        return (
            float(line.attrib["x2"]) - float(line.attrib["x1"]),
            float(line.attrib["y2"]) - float(line.attrib["y1"]),
        )

    # Both basis arrows start where the two plane guide axes intersect.
    assert {(line.attrib["x1"], line.attrib["y1"]) for line in basis} == {
        ("260.0", "184.0")
    }
    # Each basis direction is parallel to one of the plane guide axes.
    guide_vectors = [vector(line) for line in guides]
    for basis_line in basis:
        bx, by = vector(basis_line)
        assert any(abs(bx * gy - by * gx) < 1e-6 for gx, gy in guide_vectors)

    labels = [
        "".join(text.itertext())
        for text in root.findall(f"{SVG_NS}text")
    ]
    assert "TpM" in labels
    assert "M" not in labels
