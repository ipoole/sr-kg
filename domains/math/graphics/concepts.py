"""Domain-owned deterministic concept illustrations."""
from __future__ import annotations
from srkg.svg_graphics.motifs import _axis_arrow_defs, _draw_axes, _draw_chart_plane, _draw_manifold_patch, _draw_tangent_basis, _draw_tangent_plane, _draw_tensor_glyph, _paren_matrix
from srkg.svg_graphics.primitives import AMBER, BLACK, BLUE, FONT, GREEN, GREY, LIGHT_GREY, RED, _arrow_marker, _circle, _line, _math_text, _path, _rect, _sid, _svg, _text, _tick


def create_m_1_1_manifold(variant: str = "icon") -> str:
    """Node: M 1.1. Title: Manifold."""
    node_id = "M 1.1"
    body: list[str] = []
    body.extend(_draw_manifold_patch(62, 156, 388, 214))
    body.append(_circle(244, 260, 9, fill=RED, stroke=BLACK, stroke_width=2))
    body.append(_text(266, 254, "p", font_size=30, font_family=FONT,
                      font_style="italic", fill=RED))

    if variant == "detail":
        body.append(_circle(244, 260, 58, fill="#ffffff", stroke=BLUE,
                            stroke_width=4, opacity="0.62"))
        body.append(_text(244, 344, "local patch", font_size=29,
                          font_family=FONT, fill=BLACK, text_anchor="middle"))
        body.append(_text(368, 168, "M", font_size=42, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))
    else:
        body.append(_text(364, 178, "M", font_size=46, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Manifold", body)


def create_m_1_2_coordinate_chart(variant: str = "icon") -> str:
    """Node: M 1.2. Title: Coordinate chart."""
    node_id = "M 1.2"
    arrow = f"{_sid(node_id)}_chart_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []

    body.extend(_draw_manifold_patch(46, 138, 210, 164, stroke=BLUE,
                                     stroke_width=4))
    body.append(_circle(144, 222, 8, fill=RED, stroke=BLACK, stroke_width=2))
    if variant == "detail":
        body.append(_text(116, 158, "U", font_size=33, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))

    body.append(_line(264, 236, 324, 236, stroke=BLUE, stroke_width=6,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(294, 212, "φ", font_size=36, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))

    body.extend(_draw_chart_plane(334, 148, 132, 164))
    body.append(_circle(394, 232, 7, fill=RED, stroke=BLACK, stroke_width=2))
    if variant == "detail":
        body.append(_text(404, 338, "ℝⁿ", font_size=31, font_family=FONT,
                          fill=BLACK, text_anchor="middle"))
        body.append(_math_text(394, 122, "x", sup="μ", font_size=32,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))
    else:
        body.append(_math_text(402, 344, "x", sup="μ", font_size=34,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))

    return _svg(node_id, "Coordinate chart", body, defs)


def create_m_1_3_coordinate_transformation(variant: str = "icon") -> str:
    """Node: M 1.3. Title: Coordinate transformation."""
    node_id = "M 1.3"
    arrow = f"{_sid(node_id)}_coord_arrow"
    point_arrow = f"{_sid(node_id)}_point_arrow"
    defs = [
        _arrow_marker(arrow, colour=BLUE, size=6),
        _arrow_marker(point_arrow, colour=RED, size=5),
    ]
    body: list[str] = []

    body.extend(_draw_chart_plane(58, 142, 142, 170, stroke=BLUE))
    body.extend(_draw_chart_plane(314, 142, 142, 170, stroke=GREEN))
    body.append(_circle(136, 226, 7, fill=RED, stroke=BLACK, stroke_width=2))
    body.append(_circle(392, 214, 7, fill=RED, stroke=BLACK, stroke_width=2))

    body.append(_line(216, 226, 296, 218, stroke=BLUE, stroke_width=6,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(256, 200, "x′(x)", font_size=31, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))

    body.append(_line(136, 226, 392, 214, stroke=RED, stroke_width=3,
                      stroke_dasharray="7 7", opacity="0.68",
                      marker_end=f"url(#{point_arrow})"))

    body.append(_math_text(128, 342, "x", sup="μ", font_size=34,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))
    body.append(_math_text(386, 342, "x′", sup="μ", font_size=34,
                           font_family=FONT, font_style="italic",
                           fill=GREEN, text_anchor="middle"))

    if variant == "detail":
        body.append(_text(256, 86, "same point", font_size=30,
                          font_family=FONT, fill=BLACK, text_anchor="middle"))
        body.append(_text(130, 126, "chart 1", font_size=25,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
        body.append(_text(386, 126, "chart 2", font_size=25,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
        body.append(_text(256, 392, "new labels", font_size=28,
                          font_family=FONT, fill=GREY, text_anchor="middle"))

    return _svg(node_id, "Coordinate transformation", body, defs)


def create_m_1_4_worldline(variant: str = "icon") -> str:
    """Node: M 1.4. Title: Worldline."""
    node_id = "M 1.4"
    marker, defs = _axis_arrow_defs(node_id, BLACK)
    path_marker = f"{_sid(node_id)}_worldline_arrow"
    defs.append(_arrow_marker(path_marker, colour=BLUE, size=6))
    body: list[str] = []

    body.extend(_draw_axes(94, 414, 314, 304, marker,
                           x_label="x", y_label="ct", stroke_width=5))
    worldline = "M144,368 C166,306 226,286 246,224 C266,164 322,150 368,92"
    body.append(_path(worldline, fill="none", stroke=BLUE, stroke_width=8,
                      stroke_linecap="round", marker_end=f"url(#{path_marker})"))
    for x, y, label in [(144, 368, "A"), (246, 224, "p"), (368, 92, "B")]:
        body.append(_circle(x, y, 10, fill=RED, stroke=BLACK, stroke_width=2))
        if variant == "detail":
            body.append(_text(x + 16, y - 10, label, font_size=26,
                              font_family=FONT, font_style="italic", fill=RED))

    if variant == "detail":
        for x, y, angle in [(178, 314, -62), (266, 184, -52), (326, 128, -44)]:
            body.append(_tick(x, y, angle, 28, stroke=GREY, stroke_width=3,
                              stroke_linecap="round", opacity="0.72"))
        body.append(_text(268, 456, "curve of events", font_size=28,
                          font_family=FONT, fill=BLACK, text_anchor="middle"))
    else:
        body.append(_text(288, 342, "worldline", font_size=32,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Worldline", body, defs)


def create_m_1_5_tangent_space(variant: str = "icon") -> str:
    """Node: M 1.5. Title: Tangent space."""
    node_id = "M 1.5"
    body: list[str] = []
    defs: list[str] = []

    body.extend(_draw_manifold_patch(70, 222, 360, 160, stroke=BLUE,
                                     stroke_width=4, grid_opacity="0.42"))
    body.append(_circle(250, 300, 9, fill=RED, stroke=BLACK, stroke_width=2))
    body.append(_text(270, 294, "p", font_size=29, font_family=FONT,
                      font_style="italic", fill=RED))

    body.extend(_draw_tangent_plane(260, 184, 274, 108, fill="#fbfbfb"))
    basis_body, basis_defs = _draw_tangent_basis(260, 184)
    body.extend(basis_body)
    defs.extend(basis_defs)
    body.append(_line(250, 300, 260, 236, stroke=GREY, stroke_width=3,
                      stroke_dasharray="6 7", opacity="0.68"))

    if variant == "detail":
        body.append(_math_text(346, 148, "T", sub="p", suffix="M", font_size=35,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))
    else:
        body.append(_math_text(340, 150, "T", sub="p", suffix="M", font_size=36,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))

    return _svg(node_id, "Tangent space", body, defs)


def create_m_1_6_cotangent_space(variant: str = "icon") -> str:
    """Node: M 1.6. Title: Cotangent space."""
    node_id = "M 1.6"
    covector_marker = f"{_sid(node_id)}_covector_arrow"
    defs = [_arrow_marker(covector_marker, colour=AMBER, size=6)]
    body: list[str] = []

    body.extend(_draw_manifold_patch(70, 226, 360, 156, stroke=BLUE,
                                     stroke_width=4, grid_opacity="0.34"))
    body.append(_circle(250, 302, 9, fill=RED, stroke=BLACK, stroke_width=2))
    body.append(_text(270, 296, "p", font_size=29, font_family=FONT,
                      font_style="italic", fill=RED))

    body.extend(_draw_tangent_plane(260, 184, 274, 108, fill="#fbfbfb"))
    # Level-set lines make a covector feel like a gradient/one-form acting on
    # tangent directions, without teaching the full differential-form formalism.
    for offset in (-46, -22, 2, 26, 50):
        body.append(_line(146, 190 + offset, 344, 132 + offset,
                          stroke=AMBER, stroke_width=3, opacity="0.55",
                          stroke_linecap="round"))
    body.append(_line(218, 210, 314, 172, stroke=AMBER, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{covector_marker})"))
    body.append(_text(324, 170, "ω", font_size=38, font_family=FONT,
                      font_style="italic", fill=AMBER))

    if variant == "detail":
        body.append(_math_text(360, 144, "T", sub="p", sup="*", font_size=35,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))
        body.append(_text(396, 144, "M", font_size=34, font_family=FONT,
                          font_style="italic", fill=BLACK))
        body.append(_text(256, 418, "covector acts on tangents", font_size=27,
                          font_family=FONT, fill=BLACK, text_anchor="middle"))
    else:
        body.append(_math_text(344, 146, "T", sub="p", sup="*", font_size=36,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))

    return _svg(node_id, "Cotangent space", body, defs)


def create_m_2_1_tensor_field(variant: str = "icon") -> str:
    """Node: M 2.1. Title: Tensor field."""
    node_id = "M 2.1"
    body: list[str] = []
    body.extend(_draw_manifold_patch(58, 132, 394, 246, stroke=BLUE,
                                     stroke_width=4))

    glyphs = [
        (156, 226, "T"),
        (244, 184, "T"),
        (312, 282, "T"),
        (386, 222, "T"),
    ]
    for x, y, label in glyphs:
        body.extend(_draw_tensor_glyph(x, y, label=label))

    if variant == "detail":
        for x, y, _ in glyphs:
            body.append(_circle(x, y + 42, 5, fill=RED, stroke="none",
                                opacity="0.75"))
        body.append(_text(254, 410, "tensor at each point", font_size=30,
                          font_family=FONT, fill=BLACK, text_anchor="middle"))
    else:
        body.append(_math_text(256, 416, "T", font_size=42,
                               font_family=FONT, font_style="italic",
                               fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Tensor field", body)


def create_m_2_2_index_notation(variant: str = "icon") -> str:
    node_id = "M 2.2"
    body = [_math_text(150, 246, "T", sup="ab", font_size=72, font_family=FONT,
                       font_style="italic", fill=BLUE, text_anchor="middle"),
            _text(256, 246, "↔", font_size=58, font_family=FONT, fill=GREEN,
                  text_anchor="middle")]
    body.extend(_paren_matrix(350, 184, [["T00", "T01"], ["T10", "T11"]],
                              col_gap=66, row_gap=70, font_size=27))
    if variant == "detail":
        body += [_text(150, 330, "abstract", font_size=28, font_family=FONT,
                       fill=BLUE, text_anchor="middle"),
                 _text(382, 330, "components", font_size=28, font_family=FONT,
                       fill=GREY, text_anchor="middle"),
                 _text(256, 410, "same tensor • chosen basis", font_size=27,
                       font_family=FONT, fill=GREEN, text_anchor="middle")]
    return _svg(node_id, "Abstract and component indices", body)


def create_m_2_3_tensor_transformation_law(variant: str = "icon") -> str:
    node_id = "M 2.3"
    arrow = f"{_sid(node_id)}_transform"
    defs = [_arrow_marker(arrow, colour=GREEN, size=6)]
    body: list[str] = []
    for ox, colour, label in [(72, BLUE, "T"), (324, AMBER, "T′")]:
        body.append(_rect(ox, 150, 116, 190, rx=12, fill="#ffffff",
                          stroke=colour, stroke_width=5))
        for d in [38, 76]:
            body.append(_line(ox+d, 164, ox+d, 326, stroke=LIGHT_GREY, stroke_width=3))
        body.append(_text(ox+58, 254, label, font_size=48, font_family=FONT,
                          font_style="italic", fill=colour, text_anchor="middle"))
    body.append(_line(196, 244, 308, 244, stroke=GREEN, stroke_width=8,
                      marker_end=f"url(#{arrow})"))
    body.append(_text(252, 214, "Λ", font_size=38, font_family=FONT,
                      font_style="italic", fill=GREEN, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(256, 398, "components change • tensor does not",
                          font_size=27, font_family=FONT, fill=GREY,
                          text_anchor="middle"))
    return _svg(node_id, "Tensor transformation law", body, defs)
