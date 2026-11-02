"""Domain-owned deterministic concept illustrations."""
from __future__ import annotations
from math import cos, radians, sin
from srkg.svg_graphics.motifs import _axis_arrow_defs, _draw_axes, _draw_chart_plane, _draw_grid, _draw_manifold_patch, _draw_tangent_plane, _draw_tensor_glyph, _label_tile, _paren_matrix
from srkg.svg_graphics.primitives import AMBER, BLACK, BLUE, CX, CY, FONT, GREEN, GREY, LIGHT_GREY, RED, _arrow_marker, _circle, _line, _math_text, _path, _polygon, _rect, _sid, _svg, _text, _tick


def create_gr_1_1_gravity_as_geometry(variant: str = "icon") -> str:
    """Node: GR 1.1. Title: Gravity as geometry."""
    node_id = "GR 1.1"
    arrow = f"{_sid(node_id)}_path_arrow"
    red_arrow = f"{_sid(node_id)}_force_arrow"
    defs = [
        _arrow_marker(arrow, colour=AMBER, size=6),
        _arrow_marker(red_arrow, colour=RED, size=6),
    ]
    body: list[str] = []

    if variant == "detail":
        body.extend(_draw_grid(42, 92, 156, 286, 39, colour="#d8d8d8"))
        body.append(_rect(42, 92, 156, 286, rx=10, fill="none",
                          stroke=LIGHT_GREY, stroke_width=3))
        body.append(_line(88, 244, 154, 244, stroke=RED, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{red_arrow})"))
        body.append(_text(120, 82, "force", font_size=28, font_family=FONT,
                          fill=GREY, text_anchor="middle"))
        body.append(_line(212, 244, 262, 244, stroke=BLUE, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.append(_text(238, 220, "→", font_size=42, font_family=FONT,
                          fill=BLUE, text_anchor="middle"))
        body.extend(_draw_manifold_patch(278, 120, 182, 260, stroke=BLUE,
                                         stroke_width=4))
        body.append(_text(370, 82, "geometry", font_size=28,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
        path = "M310,330 C332,258 374,262 408,184"
    else:
        body.extend(_draw_manifold_patch(62, 120, 390, 260, stroke=BLUE,
                                         stroke_width=5))
        path = "M132,342 C172,236 292,292 384,154"

    body.append(_path(path, fill="none", stroke=AMBER, stroke_width=9,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_circle(384 if variant == "icon" else 408,
                        154 if variant == "icon" else 184,
                        10, fill=AMBER, stroke=BLACK, stroke_width=2))
    if variant == "icon":
        body.append(_text(264, 420, "geometry", font_size=34,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Gravity as geometry", body, defs)


def create_gr_1_2_equivalence_principle(variant: str = "icon") -> str:
    """Node: GR 1.2. Title: Equivalence principle."""
    node_id = "GR 1.2"
    arrow = f"{_sid(node_id)}_eq_arrow"
    defs = [_arrow_marker(arrow, colour=GREEN, size=6)]
    body: list[str] = []

    cabins = [(92, 150, "a"), (292, 150, "g")]

    for x, y, label in cabins:
        body.append(_rect(x, y, 128, 198, rx=12, fill="#f8f8f8",
                          stroke=BLACK, stroke_width=4))
        body.append(_line(x + 22, y + 154, x + 106, y + 154,
                          stroke=LIGHT_GREY, stroke_width=4))
        body.append(_circle(x + 64, y + 76, 16, fill=AMBER,
                            stroke=BLACK, stroke_width=3))
        body.append(_line(x + 64, y + 96, x + 64, y + 144,
                          stroke=GREY, stroke_width=3,
                          stroke_dasharray="5 6", opacity="0.55"))
        if label == "a":
            body.append(_line(x + 64, y + 218, x + 64, y + 250,
                              stroke=GREEN, stroke_width=6,
                              stroke_linecap="round",
                              marker_end=f"url(#{arrow})"))
            body.append(_text(x + 90, y + 248, "a", font_size=31,
                              font_family=FONT, font_style="italic",
                              fill=GREEN))
        else:
            body.append(_line(x + 64, y - 16, x + 64, y + 20,
                              stroke=GREEN, stroke_width=6,
                              stroke_linecap="round",
                              marker_end=f"url(#{arrow})"))
            body.append(_text(x + 90, y + 12, "g", font_size=31,
                              font_family=FONT, font_style="italic",
                              fill=GREEN))

    body.append(_line(236, 246, 276, 246, stroke=BLUE, stroke_width=5,
                      stroke_linecap="round"))
    body.append(_line(236, 264, 276, 264, stroke=BLUE, stroke_width=5,
                      stroke_linecap="round"))
    if variant == "detail":
        body.append(_text(256, 116, "local", font_size=28,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Equivalence principle", body, defs)


def create_gr_1_3_local_inertial_frame(variant: str = "icon") -> str:
    """Node: GR 1.3. Title: Local inertial frame."""
    node_id = "GR 1.3"
    marker_id, defs = _axis_arrow_defs(node_id, BLACK)
    body: list[str] = []

    body.extend(_draw_manifold_patch(62, 210, 386, 166, stroke=BLUE,
                                     stroke_width=4, grid_opacity="0.42"))
    body.append(_circle(250, 296, 9, fill=RED, stroke=BLACK, stroke_width=2))
    body.extend(_draw_tangent_plane(260, 190, 278, 116, fill="#fbfbfb"))

    body.append(_line(196, 210, 318, 210, stroke=BLACK, stroke_width=5,
                      stroke_linecap="round", marker_end=f"url(#{marker_id})"))
    body.append(_line(204, 228, 204, 144, stroke=BLACK, stroke_width=5,
                      stroke_linecap="round", marker_end=f"url(#{marker_id})"))
    body.append(_text(326, 220, "x", font_size=30, font_family=FONT,
                      font_style="italic", fill=BLACK))
    body.append(_text(190, 132, "ct", font_size=30, font_family=FONT,
                      font_style="italic", fill=BLACK, text_anchor="middle"))

    if variant == "detail":
        body.append(_text(256, 92, "SR locally", font_size=33,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
        body.append(_line(250, 296, 260, 248, stroke=GREY, stroke_width=3,
                          stroke_dasharray="6 7", opacity="0.70"))
    else:
        body.append(_text(350, 162, "local", font_size=31,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Local inertial frame", body, defs)


def create_gr_1_4_freely_falling_observer(variant: str = "icon") -> str:
    """Node: GR 1.4. Title: Freely falling observer."""
    node_id = "GR 1.4"
    arrow = f"{_sid(node_id)}_fall_arrow"
    red_arrow = f"{_sid(node_id)}_support_arrow"
    defs = [
        _arrow_marker(arrow, colour=BLUE, size=6),
        _arrow_marker(red_arrow, colour=RED, size=6),
    ]
    body: list[str] = []

    body.extend(_draw_manifold_patch(66, 146, 378, 250, stroke=BLUE,
                                     stroke_width=4))
    path = "M132,346 C178,274 236,292 294,224 C330,184 372,172 414,132"
    body.append(_path(path, fill="none", stroke=BLUE, stroke_width=8,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_circle(276, 238, 15, fill=AMBER, stroke=BLACK, stroke_width=3))
    body.append(_line(260, 254, 242, 286, stroke=AMBER, stroke_width=6,
                      stroke_linecap="round"))
    body.append(_line(292, 254, 310, 286, stroke=AMBER, stroke_width=6,
                      stroke_linecap="round"))

    if variant == "detail":
        body.append(_rect(74, 296, 82, 16, rx=4, fill=GREY, stroke=BLACK,
                          stroke_width=2, opacity="0.82"))
        body.append(_circle(116, 270, 12, fill=RED, stroke=BLACK,
                            stroke_width=2))
        body.append(_line(116, 294, 116, 270, stroke=RED, stroke_width=5,
                          stroke_linecap="round",
                          marker_end=f"url(#{red_arrow})"))
        body.append(_text(122, 372, "supported", font_size=24,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(320, 342, "no thrust", font_size=27,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
    else:
        body.append(_text(316, 334, "free fall", font_size=32,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Freely falling observer", body, defs)


def create_gr_1_5_tidal_gravity(variant: str = "icon") -> str:
    """Node: GR 1.5. Title: Tidal gravity."""
    node_id = "GR 1.5"
    arrow = f"{_sid(node_id)}_tidal_arrow"
    red_arrow = f"{_sid(node_id)}_relative_arrow"
    defs = [
        _arrow_marker(arrow, colour=BLUE, size=6),
        _arrow_marker(red_arrow, colour=RED, size=6),
    ]
    body: list[str] = []

    body.extend(_draw_manifold_patch(62, 118, 388, 286, stroke=BLUE,
                                     stroke_width=4, grid_opacity="0.40"))
    paths = [
        "M142,360 C168,292 204,234 244,158",
        "M238,370 C246,296 256,232 266,148",
        "M334,360 C316,294 298,232 286,158",
    ]
    for path in paths:
        body.append(_path(path, fill="none", stroke=BLUE, stroke_width=7,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))

    for x, y in [(142, 360), (238, 370), (334, 360)]:
        body.append(_circle(x, y, 9, fill=AMBER, stroke=BLACK, stroke_width=2))

    body.append(_line(210, 318, 166, 334, stroke=RED, stroke_width=5,
                      stroke_linecap="round", marker_end=f"url(#{red_arrow})"))
    body.append(_line(266, 318, 312, 334, stroke=RED, stroke_width=5,
                      stroke_linecap="round", marker_end=f"url(#{red_arrow})"))
    if variant == "detail":
        body.append(_line(246, 286, 246, 236, stroke=RED, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{red_arrow})"))
        body.append(_text(256, 92, "relative free fall", font_size=30,
                          font_family=FONT, fill=BLACK, text_anchor="middle"))
    else:
        body.append(_text(256, 92, "tidal", font_size=34,
                          font_family=FONT, fill=RED, text_anchor="middle"))

    return _svg(node_id, "Tidal gravity", body, defs)


def create_gr_9_1_weak_field_metric(variant: str = "icon") -> str:
    """Weak-field metric: a small perturbation of an almost-flat grid."""
    node_id = "GR 9.1"
    body: list[str] = []
    body.append(_rect(58, 76, 396, 348, rx=22, fill="#f8faff",
                      stroke=LIGHT_GREY, stroke_width=3))
    for offset in [-120, -60, 0, 60, 120]:
        body.append(_path(
            f"M{256 + offset},92 C{238 + offset},174 {238 + offset},326 {256 + offset},408",
            fill="none", stroke="#9eb4df", stroke_width=4,
            stroke_linecap="round",
        ))
        body.append(_path(
            f"M74,{250 + offset} C156,{232 + offset} 356,{232 + offset} 438,{250 + offset}",
            fill="none", stroke="#9eb4df", stroke_width=4,
            stroke_linecap="round",
        ))
    body.append(_circle(CX, CY, 38, fill=AMBER, stroke=BLACK, stroke_width=4))
    if variant == "detail":
        body.extend(_label_tile(118, 438, 276, 54, "g = η + h", fill="#ffffff",
                                stroke=BLUE, text_colour=BLUE, font_size=31))
        body.append(_text(316, 194, "|h| ≪ 1", font_size=29, font_family=FONT,
                          font_style="italic", fill=GREY))
    else:
        body.append(_text(336, 174, "h", font_size=44, font_family=FONT,
                          font_style="italic", fill=BLUE))
    return _svg(node_id, "Weak-field metric", body)


def create_gr_9_2_newtonian_limit(variant: str = "icon") -> str:
    """Newtonian limit: a shallow potential produces familiar acceleration."""
    node_id = "GR 9.2"
    arrow = f"{_sid(node_id)}_acceleration"
    defs = [_arrow_marker(arrow, colour=RED, size=6)]
    body: list[str] = []
    body.append(_line(70, 382, 442, 382, stroke=BLACK, stroke_width=5,
                      stroke_linecap="round"))
    body.append(_line(82, 104, 82, 398, stroke=BLACK, stroke_width=5,
                      stroke_linecap="round"))
    body.append(_path("M86,174 C172,178 176,346 256,346 C336,346 340,178 430,174",
                      fill="#edf3ff", stroke=BLUE, stroke_width=8,
                      stroke_linejoin="round"))
    body.append(_circle(256, 322, 24, fill=AMBER, stroke=BLACK, stroke_width=3))
    body.append(_line(256, 206, 256, 286, stroke=RED, stroke_width=8,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(276, 244, "g", font_size=42, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(48, 116, "Φ", font_size=42, font_family=FONT,
                      font_style="italic", fill=BLUE))
    if variant == "detail":
        body.append(_text(256, 448, "slow motion • weak field", font_size=27,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(256, 164, "g = −∇Φ", font_size=32, font_family=FONT,
                          font_style="italic", fill=RED, text_anchor="middle"))
    return _svg(node_id, "Newtonian limit", body, defs)


def create_gr_9_3_gravitational_redshift(variant: str = "icon") -> str:
    """Gravitational redshift: climbing light emerges at lower frequency."""
    node_id = "GR 9.3"
    arrow = f"{_sid(node_id)}_photon"
    defs = [_arrow_marker(arrow, colour=AMBER, size=6)]
    body: list[str] = []
    body.append(_circle(256, 462, 292, fill="#f4f6fa", stroke=LIGHT_GREY,
                        stroke_width=4))
    body.append(_line(154, 372, 354, 372, stroke=GREY, stroke_width=7,
                      stroke_linecap="round"))
    body.append(_line(154, 130, 354, 130, stroke=GREY, stroke_width=7,
                      stroke_linecap="round"))
    body.append(_path("M214,350 C246,332 182,306 214,286 C246,266 182,242 214,220 C246,196 182,176 214,150",
                      fill="none", stroke=AMBER, stroke_width=8,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_circle(214, 372, 18, fill=BLUE, stroke=BLACK, stroke_width=3))
    body.append(_circle(214, 130, 18, fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_text(246, 352, "νₑ", font_size=38, font_family=FONT,
                      font_style="italic", fill=BLUE))
    body.append(_text(246, 116, "νᵣ", font_size=38, font_family=FONT,
                      font_style="italic", fill=RED))
    if variant == "detail":
        body.append(_text(350, 222, "νᵣ &lt; νₑ", font_size=32, font_family=FONT,
                          font_style="italic", fill=GREY, text_anchor="middle"))
        body.append(_line(390, 350, 390, 152, stroke=GREY, stroke_width=4,
                          stroke_dasharray="8 8"))
        body.append(_text(408, 286, "up", font_size=27, font_family=FONT,
                          fill=GREY))
    return _svg(node_id, "Gravitational redshift", body, defs)


def create_gr_9_4_light_deflection(variant: str = "icon") -> str:
    """Light deflection: a null ray bends around a compact mass."""
    node_id = "GR 9.4"
    arrow = f"{_sid(node_id)}_light"
    defs = [_arrow_marker(arrow, colour=AMBER, size=6)]
    body: list[str] = []
    body.append(_circle(288, 276, 76, fill="#f7e5b8", stroke=BLACK,
                        stroke_width=5))
    for r in ([114, 150] if variant == "detail" else [124]):
        body.append(_circle(288, 276, r, fill="none", stroke=LIGHT_GREY,
                            stroke_width=3, stroke_dasharray="8 10"))
    body.append(_line(54, 154, 454, 154, stroke=LIGHT_GREY, stroke_width=4,
                      stroke_dasharray="10 9"))
    body.append(_path("M54,154 C180,154 248,160 292,184 C340,210 386,230 454,258",
                      fill="none", stroke=AMBER, stroke_width=10,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(94, 132, "light", font_size=32, font_family=FONT,
                      font_style="italic", fill=AMBER))
    if variant == "detail":
        body.append(_path("M310,172 A74,74 0 0 1 350,216", fill="none",
                          stroke=RED, stroke_width=4))
        body.append(_text(350, 174, "α", font_size=38, font_family=FONT,
                          font_style="italic", fill=RED))
        body.append(_text(288, 286, "M", font_size=42, font_family=FONT,
                          font_style="italic", fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Light deflection", body, defs)


def create_gr_9_5_perihelion_precession(variant: str = "icon") -> str:
    """Perihelion precession: successive elliptical orbits rotate."""
    node_id = "GR 9.5"
    arrow = f"{_sid(node_id)}_advance"
    defs = [_arrow_marker(arrow, colour=RED, size=6)]
    body: list[str] = []
    body.append(_circle(CX, CY, 35, fill=AMBER, stroke=BLACK, stroke_width=4))
    # Two osculating ellipses share the mass as their focus.
    for angle, colour in [(0, BLUE), (-30, GREEN)]:
        points = []
        for step in range(121):
            phi = radians(step * 3)
            radius = 120 / (1 + 0.5 * cos(phi))
            direction = phi + radians(angle)
            points.append((CX + radius * cos(direction),
                           CY + radius * sin(direction)))
        path = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in points) + " Z"
        body.append(_path(path, fill="none", stroke=colour, stroke_width=6))
        px, py = points[0]
        body.append(_circle(px, py, 12, fill=colour, stroke=BLACK, stroke_width=2))
        if variant == "detail":
            body.append(_line(CX, CY, px, py, stroke=LIGHT_GREY,
                              stroke_width=3, stroke_dasharray="7 8"))
    body.append(_path("M360,256 A104,104 0 0 0 346,204", fill="none",
                      stroke=RED, stroke_width=6, marker_end=f"url(#{arrow})"))
    if variant == "detail":
        body.append(_text(370, 228, "Δϖ", font_size=32, font_family=FONT,
                          font_style="italic", fill=RED))
        body.append(_text(CX, CY + 10, "M", font_size=30, font_family=FONT,
                          font_style="italic", fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Perihelion precession", body, defs)


def create_gr_9_6_post_newtonian_approximation(variant: str = "icon") -> str:
    """Post-Newtonian approximation: ordered corrections beyond Newton."""
    node_id = "GR 9.6"
    arrow = f"{_sid(node_id)}_order"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []
    tiles = [
        (72, 338, 116, 78, "0PN", GREY),
        (198, 258, 116, 78, "1PN", BLUE),
        (324, 178, 116, 78, "2PN", GREEN),
    ]
    body.append(_line(116, 402, 394, 216, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    for x, y, width, height, label, colour in tiles:
        body.extend(_label_tile(x, y, width, height, label, fill="#ffffff",
                                stroke=colour, text_colour=colour, font_size=34))
    if variant == "detail":
        body.append(_text(130, 322, "Newton", font_size=25, font_family=FONT,
                          fill=GREY, text_anchor="middle"))
        body.append(_text(256, 242, "+ c⁻²", font_size=25, font_family=FONT,
                          fill=BLUE, text_anchor="middle"))
        body.append(_text(382, 162, "+ c⁻⁴", font_size=25, font_family=FONT,
                          fill=GREEN, text_anchor="middle"))
        body.append(_text(256, 468, "controlled relativistic corrections",
                          font_size=26, font_family=FONT, fill=GREY,
                          text_anchor="middle"))
    return _svg(node_id, "Post-Newtonian approximation", body, defs)


def create_gr_9_7_gravitational_waves(variant: str = "icon") -> str:
    """Gravitational waves: travelling tidal strain in weak geometry."""
    node_id = "GR 9.7"
    wave_arrow = f"{_sid(node_id)}_wave"
    defs = [_arrow_marker(wave_arrow, colour=BLUE, size=6)]
    body: list[str] = []

    # A travelling perturbation: keep it geometric and field-like, not a
    # material water/sound wave.
    body.append(_path("M54,152 C94,108 134,196 174,152 C214,108 254,196 294,152 C334,108 374,196 414,152",
                      fill="none", stroke=BLUE, stroke_width=8,
                      stroke_linecap="round", marker_end=f"url(#{wave_arrow})"))
    body.append(_text(70, 118, "h", font_size=38, font_family=FONT,
                      font_style="italic", fill=BLUE))

    # Dashed neutral ring and current plus-polarization deformation.
    cx, cy = 256, 314
    body.append(_circle(cx, cy, 92, fill="none", stroke=LIGHT_GREY,
                        stroke_width=4, stroke_dasharray="8 9"))
    for x, y in [(cx - 92, cy), (cx + 92, cy), (cx, cy - 92), (cx, cy + 92)]:
        body.append(_circle(x, y, 8, fill=LIGHT_GREY, stroke="none"))

    current = [(cx - 132, cy), (cx + 132, cy), (cx, cy - 58), (cx, cy + 58)]
    for x, y in current:
        body.append(_circle(x, y, 17, fill=RED, stroke=BLACK, stroke_width=2.5))
    body.append(_line(cx - 112, cy, cx + 112, cy, stroke=AMBER, stroke_width=5,
                      stroke_linecap="round", opacity="0.72"))
    body.append(_line(cx, cy - 44, cx, cy + 44, stroke=AMBER, stroke_width=5,
                      stroke_linecap="round", opacity="0.72"))

    if variant == "detail":
        body.append(_text(cx, 248, "+ polarization strain", font_size=27,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(cx, 452, "freely falling test masses", font_size=27,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(420, 118, "wave zone", font_size=25,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
        body.append(_line(cx - 70, cy - 70, cx + 70, cy + 70, stroke=GREEN,
                          stroke_width=3, stroke_dasharray="6 8",
                          stroke_linecap="round", opacity="0.55"))
        body.append(_line(cx - 70, cy + 70, cx + 70, cy - 70, stroke=GREEN,
                          stroke_width=3, stroke_dasharray="6 8",
                          stroke_linecap="round", opacity="0.55"))
        body.append(_text(352, 402, "×", font_size=34, font_family=FONT,
                          fill=GREEN, text_anchor="middle"))
    else:
        body.append(_text(cx, 454, "strain", font_size=34,
                          font_family=FONT, fill=AMBER, text_anchor="middle"))

    return _svg(node_id, "Gravitational waves", body, defs)


def create_gr_10_1_schwarzschild_metric(variant: str = "icon") -> str:
    """Schwarzschild metric: static spherical exterior geometry."""
    node_id = "GR 10.1"
    body: list[str] = []
    for r in [58, 106, 154, 202]:
        body.append(_circle(CX, CY, r, fill="none", stroke="#91a9d6",
                            stroke_width=4))
    for angle in range(0, 360, 30):
        a = radians(angle)
        body.append(_line(CX + 48 * cos(a), CY + 48 * sin(a),
                          CX + 210 * cos(a), CY + 210 * sin(a),
                          stroke="#b1c1df", stroke_width=3))
    body.append(_circle(CX, CY, 46, fill=BLACK, stroke=AMBER, stroke_width=6))
    if variant == "detail":
        body.append(_rect(112, 430, 288, 58, rx=12, fill="#ffffff",
                          stroke=BLUE, stroke_width=3))
        body.append(_text(256, 468, "static • spherical • vacuum",
                          font_size=27, font_family=FONT, fill=BLUE,
                          text_anchor="middle"))
        body.append(_text(346, 112, "r", font_size=34, font_family=FONT,
                          font_style="italic", fill=GREY))
    else:
        body.append(_text(354, 112, "r", font_size=38, font_family=FONT,
                          font_style="italic", fill=BLUE))
    return _svg(node_id, "Schwarzschild metric", body)


def create_gr_10_2_schwarzschild_radius(variant: str = "icon") -> str:
    """Schwarzschild radius: the mass-defined radial scale r_s."""
    node_id = "GR 10.2"
    arrow_out = f"{_sid(node_id)}_radius"
    defs = [_arrow_marker(arrow_out, colour=RED, size=6)]
    body: list[str] = []
    body.append(_circle(CX, CY, 82, fill="#f1c96d", stroke=BLACK, stroke_width=5))
    body.append(_circle(CX, CY, 176, fill="none", stroke=RED, stroke_width=8))
    body.append(_line(CX, CY, 424, CY, stroke=RED, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow_out})"))
    body.append(_circle(CX, CY, 8, fill=BLACK, stroke="none"))
    body.append(_text(352, 236, "rₛ", font_size=46, font_family=FONT,
                      font_style="italic", fill=RED, text_anchor="middle"))
    body.append(_text(CX, CY + 14, "M", font_size=46, font_family=FONT,
                      font_style="italic", fill=BLACK, text_anchor="middle"))
    if variant == "detail":
        body.extend(_label_tile(134, 438, 244, 52, "rₛ = 2GM/c²",
                                fill="#ffffff", stroke=RED,
                                text_colour=RED, font_size=30))
        body.append(_text(256, 70, "mass sets the scale", font_size=27,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
    return _svg(node_id, "Schwarzschild radius", body, defs)


def create_gr_10_3_event_horizon(variant: str = "icon") -> str:
    """Event horizon: a one-way causal boundary."""
    node_id = "GR 10.3"
    inward = f"{_sid(node_id)}_inward"
    outward = f"{_sid(node_id)}_outward"
    defs = [
        _arrow_marker(inward, colour=RED, size=6),
        _arrow_marker(outward, colour=GREEN, size=6),
    ]
    body: list[str] = []
    body.append(_circle(CX, CY, 158, fill="#e9edf5", stroke=BLACK,
                        stroke_width=10))
    body.append(_circle(CX, CY, 104, fill=BLACK, stroke="none"))
    for angle in [35, 145, 235, 325]:
        a = radians(angle)
        body.append(_line(CX + 184 * cos(a), CY + 184 * sin(a),
                          CX + 122 * cos(a), CY + 122 * sin(a),
                          stroke=RED, stroke_width=7, stroke_linecap="round",
                          marker_end=f"url(#{inward})"))
    body.append(_line(340, 166, 406, 102, stroke=GREEN, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{outward})"))
    if variant == "detail":
        body.append(_text(256, 60, "one-way causal boundary", font_size=28,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(256, 454, "r = rₛ", font_size=34, font_family=FONT,
                          font_style="italic", fill=BLACK, text_anchor="middle"))
        body.append(_text(384, 150, "out", font_size=25, font_family=FONT,
                          fill=GREEN))
    return _svg(node_id, "Event horizon", body, defs)


def create_gr_10_4_coordinate_singularity(variant: str = "icon") -> str:
    """Coordinate singularity: chart lines fail while paths remain regular."""
    node_id = "GR 10.4"
    crossing = f"{_sid(node_id)}_crossing"
    defs = [_arrow_marker(crossing, colour=GREEN, size=6)]
    body: list[str] = []
    horizon_x = 256
    body.append(_rect(58, 82, 396, 344, rx=18, fill="#fafafa",
                      stroke=LIGHT_GREY, stroke_width=3))
    body.append(_line(horizon_x, 94, horizon_x, 414, stroke=RED,
                      stroke_width=8, stroke_dasharray="12 9"))
    for x in [92, 142, 188, 220, 238, 246]:
        body.append(_line(x, 112, x, 396, stroke="#aebbd4", stroke_width=3))
    body.append(_path("M90,346 C172,324 222,284 252,246 C292,198 354,172 430,150",
                      fill="none", stroke=GREEN, stroke_width=9,
                      stroke_linecap="round", marker_end=f"url(#{crossing})"))
    body.append(_text(270, 122, "rₛ", font_size=34, font_family=FONT,
                      font_style="italic", fill=RED))
    if variant == "detail":
        body.append(_text(156, 458, "chart bunches", font_size=26,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(356, 458, "path crosses", font_size=26,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
        body.append(_text(352, 352, "finite curvature", font_size=24,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
    return _svg(node_id, "Coordinate singularity", body, defs)


def create_gr_10_5_black_hole_singularity(variant: str = "icon") -> str:
    """Black-hole singularity: interior causal paths end at r = 0."""
    node_id = "GR 10.5"
    inward = f"{_sid(node_id)}_inward"
    defs = [_arrow_marker(inward, colour=RED, size=6)]
    body: list[str] = []
    body.append(_rect(82, 112, 348, 296, fill="#e8ecf4", stroke=BLACK, stroke_width=4))
    body.append(_line(82, 112, 430, 112, stroke=BLUE, stroke_width=10))
    for x in [126, 196, 266, 336, 406]:
        body.append(_path(f"M{x},132 C{x-18},220 {x+12},306 {x},382",
                          fill="none", stroke=RED, stroke_width=6,
                          marker_end=f"url(#{inward})"))
    body.append(_path("M82,402 L110,390 L138,414 L166,390 L194,414 L222,390 L250,414 L278,390 L306,414 L334,390 L362,414 L390,390 L430,402",
                      fill="none", stroke=RED, stroke_width=7))
    body.append(_text(256, 452, "r = 0", font_size=32, font_family=FONT,
                      fill=RED, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(256, 78, "horizon", font_size=28, font_family=FONT,
                          fill=BLUE, text_anchor="middle"))
        body.append(_text(256, 262, "K → ∞", font_size=34, font_family=FONT,
                          fill=RED, text_anchor="middle"))
        body.append(_text(256, 486, "spacelike future boundary", font_size=25,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
    return _svg(node_id, "Black hole singularity", body, defs)


def create_gr_10_6_effective_potential_orbits(variant: str = "icon") -> str:
    """Effective potential: orbital turning points and circular extrema."""
    node_id = "GR 10.6"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    body: list[str] = []
    ox, oy = 78, 414
    body.extend(_draw_axes(ox, oy, 360, 322, axis_marker,
                           x_label="r", y_label="V", stroke_width=5.5))
    # Timelike Schwarzschild potential for L/m = 4; axes are r/m and V_eff.
    def position(radius):
        potential = (1 - 2 / radius) * (1 + 16 / radius ** 2)
        return 90 + (radius - 3) * 14, 388 - (potential - 0.9) * 2400
    points = [position(3 + i * 0.05) for i in range(501)]
    curve = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in points)
    body.append(_path(curve, fill="none", stroke=BLUE, stroke_width=7))
    level = 0.94
    energy_y = 388 - (level - 0.9) * 2400
    body.append(_line(90, energy_y, 440, energy_y, stroke=AMBER,
                      stroke_width=4, stroke_dasharray="10 9"))
    # Locate all intersections with the energy line, including the inner region.
    previous_r, previous_v = 3.0, (1 - 2 / 3) * (1 + 16 / 9) - level
    for i in range(1, 501):
        radius = 3 + i * 0.05
        value = (1 - 2 / radius) * (1 + 16 / radius ** 2) - level
        if value * previous_v < 0:
            root = previous_r + (radius - previous_r) * (-previous_v) / (value - previous_v)
            x, y = position(root)
            body.append(_circle(x, y, 9, fill=AMBER, stroke=BLACK, stroke_width=2))
        previous_r, previous_v = radius, value
    stable_x, stable_y = position(12)
    body.append(_circle(stable_x, stable_y, 13, fill=GREEN, stroke=BLACK, stroke_width=2))
    if variant == "detail":
        unstable_x, unstable_y = position(4)
        body.append(_circle(unstable_x, unstable_y, 13, fill=RED, stroke=BLACK, stroke_width=2))
        body.append(_text(stable_x, stable_y + 38, "stable", font_size=25,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
        body.append(_text(unstable_x + 24, unstable_y - 24, "unstable", font_size=25,
                          font_family=FONT, fill=RED))
        body.append(_text(340, energy_y - 14, "ℰ²", font_size=29,
                          font_family=FONT, fill=AMBER))
    return _svg(node_id, "Effective potential for orbits", body, defs)


def create_gr_7_1_stress_energy_tensor(variant: str = "icon") -> str:
    """Stress-energy in GR: density, flux, and stress in one tensor."""
    node_id = "GR 7.1"
    arrow = f"{_sid(node_id)}_flux"
    defs = [_arrow_marker(arrow, colour=AMBER, size=6)]
    body: list[str] = []
    body.append(_rect(122, 126, 268, 258, rx=22, fill="#f4f7fc",
                      stroke=BLACK, stroke_width=5))
    body.extend(_paren_matrix(194, 180, [["ε", "S"], ["S", "σ"]],
                              col_gap=112, row_gap=92, font_size=40))
    for y in [180, 256, 332]:
        body.append(_line(390, y, 454, y, stroke=AMBER, stroke_width=7,
                          marker_end=f"url(#{arrow})"))
    body.append(_math_text(256, 92, "T", sub="μν", font_size=48,
                           font_family=FONT, font_style="italic", fill=BLUE,
                           text_anchor="middle"))
    if variant == "detail":
        body.append(_text(256, 442, "density • flux • stress", font_size=28,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_path("M102,132 C74,216 78,306 104,382", fill="none",
                          stroke="#9eb4df", stroke_width=4))
    return _svg(node_id, "Stress-energy tensor in GR", body, defs)


def create_gr_7_2_perfect_fluid(variant: str = "icon") -> str:
    """Perfect fluid: density carried by u with isotropic pressure."""
    node_id = "GR 7.2"
    pressure = f"{_sid(node_id)}_pressure"
    flow = f"{_sid(node_id)}_flow"
    defs = [
        _arrow_marker(pressure, colour=BLUE, size=6),
        _arrow_marker(flow, colour=GREEN, size=6),
    ]
    body: list[str] = []
    body.append(_circle(CX, CY, 138, fill="#eaf2ff", stroke=BLUE, stroke_width=5))
    for x, y in [(208, 206), (282, 196), (184, 280), (270, 286), (326, 248)]:
        body.append(_circle(x, y, 18, fill=AMBER, stroke=BLACK, stroke_width=2))
    for angle in [0, 60, 120, 180, 240, 300]:
        a = radians(angle)
        body.append(_line(CX + 112 * cos(a), CY + 112 * sin(a),
                          CX + 184 * cos(a), CY + 184 * sin(a),
                          stroke=BLUE, stroke_width=7,
                          marker_end=f"url(#{pressure})"))
    body.append(_line(150, 390, 348, 110, stroke=GREEN, stroke_width=9,
                      stroke_linecap="round", marker_end=f"url(#{flow})"))
    body.append(_math_text(344, 112, "u", sup="μ", font_size=40,
                           font_family=FONT, font_style="italic", fill=GREEN))
    if variant == "detail":
        body.append(_text(256, 468, "same pressure in every direction",
                          font_size=26, font_family=FONT, fill=BLUE,
                          text_anchor="middle"))
        body.append(_text(210, 246, "ε", font_size=36, font_family=FONT,
                          font_style="italic", fill=AMBER))
    return _svg(node_id, "Perfect fluid", body, defs)


def create_gr_7_3_energy_conditions(variant: str = "icon") -> str:
    """Energy conditions: observer contractions tested against inequalities."""
    node_id = "GR 7.3"
    arrow = f"{_sid(node_id)}_test"
    defs = [_arrow_marker(arrow, colour=GREEN, size=6)]
    body: list[str] = []
    body.extend(_label_tile(70, 186, 152, 132, "Tμν", fill="#edf3ff",
                            stroke=BLUE, text_colour=BLUE, font_size=48))
    body.append(_line(230, 252, 310, 252, stroke=GREEN, stroke_width=8,
                      marker_end=f"url(#{arrow})"))
    body.extend(_label_tile(326, 174, 116, 156, "≥ 0", fill="#eef8f0",
                            stroke=GREEN, text_colour=GREEN, font_size=46))
    body.append(_math_text(270, 224, "u", sup="μ", font_size=32,
                           font_family=FONT, font_style="italic", fill=BLACK))
    body.append(_math_text(270, 292, "k", sup="μ", font_size=32,
                           font_family=FONT, font_style="italic", fill=AMBER))
    if variant == "detail":
        body.append(_text(256, 108, "measured energy", font_size=30,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(256, 402, "classical assumption — not an identity",
                          font_size=25, font_family=FONT, fill=RED,
                          text_anchor="middle"))
    return _svg(node_id, "Energy conditions", body, defs)


def create_gr_7_4_covariant_conservation(variant: str = "icon") -> str:
    """Covariant conservation: balanced local flux on curved spacetime."""
    node_id = "GR 7.4"
    outward = f"{_sid(node_id)}_outward"
    defs = [_arrow_marker(outward, colour=AMBER, size=6)]
    body: list[str] = []
    body.append(_path("M116,142 C192,112 328,124 396,166 L374,370 C290,396 184,388 104,350 Z",
                      fill="#f4f7fc", stroke=BLUE, stroke_width=5))
    for x1, y1, x2, y2 in [(166, 180, 96, 118), (346, 190, 424, 132),
                            (160, 326, 82, 390), (338, 330, 424, 392)]:
        body.append(_line(x1, y1, x2, y2, stroke=AMBER, stroke_width=8,
                          marker_end=f"url(#{outward})"))
    body.append(_math_text(256, 270, "∇", sub="μ", font_size=50,
                           font_family=FONT, fill=BLACK, text_anchor="middle"))
    body.append(_math_text(306, 270, "T", sup="μν", font_size=44,
                           font_family=FONT, font_style="italic", fill=BLUE))
    body.append(_text(374, 270, "= 0", font_size=40, font_family=FONT,
                      fill=GREEN))
    if variant == "detail":
        body.append(_text(256, 454, "local balance on curved spacetime",
                          font_size=27, font_family=FONT, fill=GREY,
                          text_anchor="middle"))
        body.append(_path("M124,228 C204,202 302,214 386,244", fill="none",
                          stroke=LIGHT_GREY, stroke_width=3, stroke_dasharray="8 8"))
    return _svg(node_id, "Covariant conservation", body, defs)


def create_gr_7_5_equation_of_state(variant: str = "icon") -> str:
    """Equation of state: constitutive relation between pressure and density."""
    node_id = "GR 7.5"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    body: list[str] = []
    ox, oy = 98, 400
    body.extend(_draw_axes(ox, oy, 326, 294, axis_marker,
                           x_label="ε", y_label="p", stroke_width=6))
    body.append(_path("M112,378 C176,342 238,290 294,226 C334,180 370,150 410,126",
                      fill="none", stroke=BLUE, stroke_width=10,
                      stroke_linecap="round"))
    body.append(_circle(282, 240, 16, fill=AMBER, stroke=BLACK, stroke_width=2))
    body.append(_text(326, 206, "p(ε)", font_size=40, font_family=FONT,
                      font_style="italic", fill=BLUE))
    if variant == "detail":
        body.append(_line(112, 378, 410, 126, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="9 8"))
        body.append(_text(220, 316, "p = wε", font_size=32, font_family=FONT,
                          font_style="italic", fill=GREY))
        body.append(_text(256, 464, "closes the matter model", font_size=27,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
    return _svg(node_id, "Equation of state", body, defs)


def create_gr_8_1_einstein_field_equations(variant: str = "icon") -> str:
    """Einstein equations: geometry coupled to stress-energy."""
    node_id = "GR 8.1"
    body: list[str] = []
    body.append(_rect(52, 138, 172, 232, rx=20, fill="#f4f7fc",
                      stroke=BLUE, stroke_width=5))
    for y in [178, 238, 298, 348]:
        body.append(_path(f"M70,{y} C110,{y-24} 168,{y+24} 208,{y}",
                          fill="none", stroke="#91a9d6", stroke_width=4))
    body.append(_math_text(138, 270, "G", sub="μν", font_size=50,
                           font_family=FONT, font_style="italic", fill=BLUE,
                           text_anchor="middle"))
    body.append(_text(256, 268, "=", font_size=54, font_family=FONT,
                      fill=BLACK, text_anchor="middle"))
    body.append(_rect(290, 138, 172, 232, rx=20, fill="#fff8e8",
                      stroke=AMBER, stroke_width=5))
    body.extend(_paren_matrix(342, 194, [["ε", "S"], ["S", "σ"]],
                              col_gap=66, row_gap=80, font_size=33))
    if variant == "detail":
        body.append(_text(138, 416, "geometry", font_size=28,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
        body.append(_text(376, 416, "stress–energy", font_size=28,
                          font_family=FONT, fill=AMBER, text_anchor="middle"))
        body.append(_text(256, 92, "G − Λg = κT", font_size=38,
                          font_family=FONT, font_style="italic", fill=BLACK,
                          text_anchor="middle"))
    return _svg(node_id, "Einstein field equations", body)


def create_gr_8_2_cosmological_constant(variant: str = "icon") -> str:
    """Cosmological constant: uniform vacuum curvature/expansion cue."""
    node_id = "GR 8.2"
    outward = f"{_sid(node_id)}_outward"
    defs = [_arrow_marker(outward, colour=BLUE, size=6)]
    body: list[str] = []
    for r in [58, 112, 168]:
        body.append(_circle(CX, CY, r, fill="none", stroke="#9eb4df",
                            stroke_width=5))
    for angle in range(0, 360, 45):
        a = radians(angle)
        body.append(_line(CX + 76 * cos(a), CY + 76 * sin(a),
                          CX + 210 * cos(a), CY + 210 * sin(a),
                          stroke=BLUE, stroke_width=7,
                          marker_end=f"url(#{outward})"))
    body.append(_text(CX, CY + 18, "Λ", font_size=72, font_family=FONT,
                      font_style="italic", fill=RED, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(256, 472, "curved even with T = 0", font_size=28,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(256, 64, "positive Λ • vacuum term", font_size=27,
                          font_family=FONT, fill=RED, text_anchor="middle"))
    return _svg(node_id, "Cosmological constant", body, defs)


def create_gr_8_3_einstein_hilbert_action(variant: str = "icon") -> str:
    """Einstein-Hilbert action: vary the metric to obtain geometry dynamics."""
    node_id = "GR 8.3"
    arrow = f"{_sid(node_id)}_variation"
    defs = [_arrow_marker(arrow, colour=GREEN, size=6)]
    body: list[str] = []
    body.extend(_label_tile(62, 174, 164, 150, "S_EH", fill="#edf3ff",
                            stroke=BLUE, text_colour=BLUE, font_size=46))
    if variant == "detail":
        body.append(_text(144, 348, "−∫(R+2Λ)√−g", font_size=28,
                          font_family=FONT, font_style="italic", fill=GREY,
                          text_anchor="middle"))
    body.append(_line(232, 250, 320, 250, stroke=GREEN, stroke_width=8,
                      marker_end=f"url(#{arrow})"))
    body.append(_math_text(274, 220, "δg", sup="μν", font_size=31,
                           font_family=FONT, font_style="italic", fill=GREEN,
                           text_anchor="middle"))
    body.extend(_label_tile(334, 174, 120, 150, "Gμν", fill="#eef8f0",
                            stroke=GREEN, text_colour=GREEN, font_size=42))
    if variant == "detail":
        body.append(_text(256, 420, "stationary action → field equation",
                          font_size=27, font_family=FONT, fill=BLACK,
                          text_anchor="middle"))
        body.append(_path("M74,132 C154,98 230,128 300,104", fill="none",
                          stroke="#9eb4df", stroke_width=4))
    return _svg(node_id, "Einstein-Hilbert action", body, defs)


def create_gr_8_4_stress_energy_variation(variant: str = "icon") -> str:
    """Matter action response to metric variation defines stress-energy."""
    node_id = "GR 8.4"
    arrow = f"{_sid(node_id)}_response"
    defs = [_arrow_marker(arrow, colour=AMBER, size=6)]
    body: list[str] = []
    body.extend(_label_tile(62, 170, 160, 154, "S_m", fill="#fff8e8",
                            stroke=AMBER, text_colour=AMBER, font_size=48))
    for y in [194, 246, 298]:
        body.append(_path(f"M82,{y} C120,{y-15} 166,{y+15} 202,{y}",
                          fill="none", stroke="#d5bb79", stroke_width=3))
    body.append(_line(230, 248, 320, 248, stroke=AMBER, stroke_width=8,
                      marker_end=f"url(#{arrow})"))
    body.append(_math_text(274, 216, "δg", sup="μν", font_size=31,
                           font_family=FONT, font_style="italic", fill=BLUE,
                           text_anchor="middle"))
    body.extend(_label_tile(334, 170, 120, 154, "Tμν", fill="#edf3ff",
                            stroke=BLUE, text_colour=BLUE, font_size=43))
    if variant == "detail":
        body.append(_text(256, 402, "matter's response to geometry",
                          font_size=28, font_family=FONT, fill=GREY,
                          text_anchor="middle"))
        body.append(_text(396, 354, "source", font_size=26,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
    return _svg(node_id, "Stress-energy from action variation", body, defs)


def create_gr_8_5_trace_reversed_equations(variant: str = "icon") -> str:
    """Trace reversal: algebraically isolate the Ricci tensor."""
    node_id = "GR 8.5"
    arrow = f"{_sid(node_id)}_trace"
    defs = [_arrow_marker(arrow, colour=GREEN, size=6)]
    body: list[str] = []
    body.extend(_label_tile(48, 178, 160, 132, "Gμν = κTμν",
                            fill="#edf3ff", stroke=BLUE,
                            text_colour=BLUE, font_size=28))
    body.append(_line(216, 244, 302, 244, stroke=GREEN, stroke_width=8,
                      marker_end=f"url(#{arrow})"))
    body.append(_text(258, 210, "trace", font_size=27, font_family=FONT,
                      fill=GREEN, text_anchor="middle"))
    body.extend(_label_tile(316, 178, 150, 132, "Rμν", fill="#eef8f0",
                            stroke=GREEN, text_colour=GREEN, font_size=48))
    if variant == "detail":
        body.append(_text(391, 346, "κ(Tμν − ½gμνT)", font_size=27,
                          font_family=FONT, font_style="italic", fill=GREY,
                          text_anchor="middle"))
        body.append(_text(256, 112, "Λ = 0 • same equation",
                          font_size=28, font_family=FONT, fill=BLACK,
                          text_anchor="middle"))
        body.append(_text(258, 288, "contract + substitute", font_size=24,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
    return _svg(node_id, "Trace-reversed equations", body, defs)


def create_gr_8_6_vacuum_field_equations(variant: str = "icon") -> str:
    """Vacuum equations: Ricci-flat can retain tidal curvature."""
    node_id = "GR 8.6"
    body: list[str] = []
    body.append(_rect(62, 92, 388, 328, rx=22, fill="#f8faff",
                      stroke=LIGHT_GREY, stroke_width=3))
    for offset in [-92, -46, 0, 46, 92]:
        body.append(_path(
            f"M{256 + offset},112 C{218 + offset},194 {294 + offset},318 {256 + offset},400",
            fill="none", stroke="#91a9d6", stroke_width=4,
        ))
    body.append(_text(256, 260, "Tμν = 0", font_size=42, font_family=FONT,
                      font_style="italic", fill=GREY, text_anchor="middle"))
    body.append(_text(256, 316, "Rμν = 0", font_size=46, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))
    if variant == "detail":
        body.append(_line(154, 152, 178, 350, stroke=RED, stroke_width=5,
                          stroke_linecap="round"))
        body.append(_line(358, 152, 334, 350, stroke=RED, stroke_width=5,
                          stroke_linecap="round"))
        body.append(_text(256, 458, "Λ = 0 • vacuum need not be flat", font_size=28,
                          font_family=FONT, fill=RED, text_anchor="middle"))
    return _svg(node_id, "Vacuum field equations", body)


def create_gr_2_1_spacetime_metric(variant: str = "icon") -> str:
    node_id = "GR 2.1"
    body: list[str] = []
    body.extend(_draw_manifold_patch(70, 110, 372, 286))
    body.extend(_draw_tensor_glyph(256, 248, label="g", fill="#ffffff",
                                   stroke=BLUE))
    if variant == "detail":
        body.append(_line(156, 320, 338, 176, stroke=AMBER, stroke_width=7))
        body.append(_text(256, 374, "lengths • times • angles", font_size=28,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
    return _svg(node_id, "Spacetime metric", body)


def create_gr_2_2_inverse_metric(variant: str = "icon") -> str:
    node_id = "GR 2.2"
    body = []
    body.extend(_label_tile(54, 188, 126, 116, "gμν", fill="#edf3ff",
                            stroke=BLUE, text_colour=BLUE, font_size=38))
    body.append(_text(210, 258, "×", font_size=48, font_family=FONT,
                      fill=BLACK, text_anchor="middle"))
    body.extend(_label_tile(240, 188, 126, 116, "g^νρ", fill="#fff8e8",
                            stroke=AMBER, text_colour=AMBER, font_size=38))
    body.append(_text(392, 258, "= δ", font_size=42, font_family=FONT,
                      fill=GREEN, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(256, 374, "lower ↔ raise indices", font_size=29,
                          font_family=FONT, fill=GREY, text_anchor="middle"))
        body.append(_text(256, 132, "inverse contraction", font_size=27,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
    return _svg(node_id, "Inverse metric", body)


def create_gr_2_3_volume_element(variant: str = "icon") -> str:
    node_id = "GR 2.3"
    body: list[str] = []
    body.append(_path("M86,152 L398,118 L438,366 L112,402 Z", fill="#edf3ff",
                      stroke=BLUE, stroke_width=6))
    for t in [0.25, 0.5, 0.75]:
        body.append(_line(86+(398-86)*t, 152+(118-152)*t,
                          112+(438-112)*t, 402+(366-402)*t,
                          stroke="#9eb4df", stroke_width=3))
    body.append(_path("M176,142 L198,390 M270,132 L292,380 M360,122 L382,370",
                      fill="none", stroke="#9eb4df", stroke_width=3))
    body.append(_rect(218, 224, 76, 72, rx=6, fill=AMBER, opacity="0.72",
                      stroke=BLACK, stroke_width=3))
    if variant == "detail":
        body.append(_text(256, 462, "√−g d⁴x", font_size=38, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))
    else:
        body.append(_text(256, 276, "dV", font_size=34, font_family=FONT,
                          font_style="italic", fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Volume element", body)


def create_gr_3_1_line_element(variant: str = "icon") -> str:
    node_id = "GR 3.1"; body: list[str] = []
    body.extend(_draw_manifold_patch(68, 104, 376, 300))
    body += [_circle(166, 310, 15, fill=RED, stroke=BLACK, stroke_width=2),
             _circle(342, 188, 15, fill=RED, stroke=BLACK, stroke_width=2),
             _line(174, 304, 334, 194, stroke=AMBER, stroke_width=8),
             _text(256, 226, "ds²", font_size=44, font_family=FONT,
                   font_style="italic", fill=AMBER, text_anchor="middle")]
    if variant == "detail": body.append(_text(256, 452, "ds² = gμν dxμ dxν", font_size=34, font_family=FONT, fill=BLUE, text_anchor="middle"))
    return _svg(node_id, "Line element", body)


def create_gr_3_2_proper_time(variant: str = "icon") -> str:
    node_id = "GR 3.2"; body: list[str] = []
    body.extend(_draw_manifold_patch(70, 92, 372, 330))
    body.append(_path("M132,370 C176,318 190,248 252,232 C318,214 330,146 386,120", fill="none", stroke=BLACK, stroke_width=8))
    for x,y,a in [(164,326,-25),(214,258,-45),(286,218,-20),(342,164,-45)]: body.append(_tick(x,y,a,34,stroke=BLUE,stroke_width=5))
    body.append(_text(256, 288, "τ", font_size=52, font_family=FONT, fill=BLUE, text_anchor="middle"))
    if variant == "detail": body.append(_text(256, 464, "clock time along a timelike curve", font_size=27, font_family=FONT, fill=GREY, text_anchor="middle"))
    return _svg(node_id, "Proper time in curved spacetime", body)


def create_gr_3_3_null_curve(variant: str = "icon") -> str:
    node_id = "GR 3.3"; body: list[str] = []
    body += [_line(256,420,104,120,stroke=BLUE,stroke_width=7), _line(256,420,408,120,stroke=BLUE,stroke_width=7),
             _path("M256,420 C300,338 330,256 408,120",fill="none",stroke=AMBER,stroke_width=10),
             _text(338,230,"light",font_size=34,font_family=FONT,fill=AMBER)]
    if variant == "detail": body += [_text(256,470,"ds² = 0",font_size=38,font_family=FONT,fill=BLUE,text_anchor="middle"), _line(256,420,256,94,stroke=LIGHT_GREY,stroke_width=3,stroke_dasharray="8 8")]
    return _svg(node_id, "Null curve", body)


def create_gr_3_4_causal_structure(variant: str = "icon") -> str:
    node_id = "GR 3.4"; body: list[str] = []
    body.append(_polygon([(256,250),(112,70),(400,70)],fill="#edf3ff",stroke=BLUE,stroke_width=5))
    body.append(_polygon([(256,262),(112,442),(400,442)],fill="#f7f7f7",stroke=GREY,stroke_width=5))
    body.append(_circle(256,256,18,fill=RED,stroke=BLACK,stroke_width=3))
    body.append(_text(256,128,"future",font_size=32,font_family=FONT,fill=BLUE,text_anchor="middle"))
    if variant == "detail": body += [_text(256,408,"past",font_size=32,font_family=FONT,fill=GREY,text_anchor="middle"), _text(448,264,"spacelike",font_size=25,font_family=FONT,fill=RED,text_anchor="end")]
    return _svg(node_id, "Causal structure", body)


def create_gr_3_5_local_flatness(variant: str = "icon") -> str:
    node_id = "GR 3.5"; body: list[str] = []
    body.extend(_draw_manifold_patch(58, 92, 396, 326))
    body.append(_rect(184,178,144,144,rx=12,fill="#ffffff",stroke=GREEN,stroke_width=5))
    body += [_line(204,286,308,286,stroke=BLACK,stroke_width=5),_line(204,286,204,198,stroke=BLACK,stroke_width=5),_circle(204,286,10,fill=RED)]
    if variant == "detail": body.append(_text(256,464,"g → η at one event",font_size=32,font_family=FONT,fill=GREEN,text_anchor="middle"))
    return _svg(node_id, "Local flatness", body)


def create_gr_3_6_metric_signature(variant: str = "icon") -> str:
    node_id = "GR 3.6"; body: list[str] = []
    body.extend(_label_tile(72,164,168,176,"+ − − −",fill="#edf3ff",stroke=BLUE,text_colour=BLUE,font_size=42))
    body.append(_text(256,260,"or",font_size=32,font_family=FONT,fill=GREY,text_anchor="middle"))
    body.extend(_label_tile(272,164,168,176,"− + + +",fill="#fff8e8",stroke=AMBER,text_colour=AMBER,font_size=42))
    if variant == "detail": body += [_text(156,392,"time-positive",font_size=26,font_family=FONT,fill=BLUE,text_anchor="middle"),_text(356,392,"time-negative",font_size=26,font_family=FONT,fill=AMBER,text_anchor="middle"),_text(256,444,"choose once • use consistently",font_size=26,font_family=FONT,fill=GREY,text_anchor="middle")]
    return _svg(node_id, "Metric signature convention", body)


def create_gr_4_1_connection(variant="icon"):
    n="GR 4.1"; a=f"{_sid(n)}_a"; d=[_arrow_marker(a,colour=GREEN,size=6)]; b=[]
    b.extend(_draw_manifold_patch(62,92,388,330)); b.append(_path("M116,350 C178,286 252,300 316,218 C350,174 376,140 414,122",fill="none",stroke=BLUE,stroke_width=8))
    for x,y,dx,dy in [(158,310,30,-38),(242,278,38,-26),(326,202,22,-44)]: b.append(_line(x,y,x+dx,y+dy,stroke=GREEN,stroke_width=7,marker_end=f"url(#{a})"))
    if variant=="detail": b.append(_text(256,462,"compare directions at nearby points",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Connection",b,d)


def create_gr_4_2_christoffel_symbols(variant="icon"):
    n="GR 4.2"; b=[]; b.extend(_draw_chart_plane(76,104,360,300)); b.extend(_label_tile(188,190,136,112,"Γ",fill="#fff8e8",stroke=AMBER,text_colour=AMBER,font_size=64))
    if variant=="detail": b += [_text(256,452,"coordinate connection coefficients",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"),_math_text(326,222,"Γ",sup="ρ",sub="μν",font_size=30,font_family=FONT,fill=AMBER)]
    return _svg(n,"Christoffel symbols",b)


def create_gr_4_3_covariant_derivative(variant="icon"):
    n="GR 4.3"; a=f"{_sid(n)}_a"; d=[_arrow_marker(a,colour=GREEN,size=6)]; b=[]
    b += [_line(92,350,418,160,stroke=LIGHT_GREY,stroke_width=5),_circle(166,306,13,fill=RED),_circle(350,200,13,fill=RED)]
    for x,y,dx,dy in [(166,306,30,-78),(350,200,50,-66)]: b.append(_line(x,y,x+dx,y+dy,stroke=BLUE,stroke_width=8,marker_end=f"url(#{a})"))
    b.append(_text(256,286,"∇V",font_size=52,font_family=FONT,fill=GREEN,text_anchor="middle"))
    if variant=="detail": b.append(_text(256,428,"ordinary change + connection correction",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Covariant derivative",b,d)


def create_gr_4_4_metric_compatibility(variant="icon"):
    n="GR 4.4"; b=[]; b.extend(_draw_manifold_patch(62,92,388,330)); b += [_line(142,316,226,258,stroke=AMBER,stroke_width=9),_line(288,218,372,160,stroke=AMBER,stroke_width=9)]
    for x,y in [(184,287),(330,189)]: b.append(_tick(x,y,-35,38,stroke=BLACK,stroke_width=5))
    b.append(_text(256,276,"∇g = 0",font_size=44,font_family=FONT,fill=BLUE,text_anchor="middle"))
    if variant=="detail": b.append(_text(256,458,"transport preserves metric inner products",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Metric compatibility",b)


def create_gr_4_5_torsion_free(variant="icon"):
    n="GR 4.5"; a=f"{_sid(n)}_a"; d=[_arrow_marker(a,colour=BLUE,size=6)]; b=[]
    pts=[(126,356),(242,356),(350,218),(234,218),(126,356)]
    for p,q in zip(pts,pts[1:]): b.append(_line(*p,*q,stroke=BLUE,stroke_width=8,marker_end=f"url(#{a})"))
    b.append(_circle(126,356,14,fill=RED,stroke=BLACK,stroke_width=2)); b.append(_text(256,160,"T = 0",font_size=48,font_family=FONT,fill=GREEN,text_anchor="middle"))
    if variant=="detail": b.append(_text(256,430,"infinitesimal parallelogram closes",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Torsion-free connection",b,d)


def create_gr_4_6_parallel_transport(variant="icon"):
    n="GR 4.6"; a=f"{_sid(n)}_a"; d=[_arrow_marker(a,colour=GREEN,size=6)]; b=[]
    b.extend(_draw_manifold_patch(60,88,392,334)); b.append(_path("M138,330 C150,180 342,146 382,300 C334,390 194,404 138,330",fill="none",stroke=BLUE,stroke_width=7))
    for x,y,dx,dy in [(138,330,0,-72),(244,174,56,-34),(382,300,34,52)]: b.append(_line(x,y,x+dx,y+dy,stroke=GREEN,stroke_width=8,marker_end=f"url(#{a})"))
    if variant=="detail": b.append(_text(256,462,"same vector rule • changed orientation after loop",font_size=26,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Parallel transport",b,d)


def create_gr_5_1_geodesic(variant="icon"):
    n="GR 5.1"; b=[]; b.extend(_draw_manifold_patch(60,88,392,336)); b.append(_path("M106,350 C170,286 212,304 270,230 C318,168 362,156 414,116",fill="none",stroke=AMBER,stroke_width=10)); b += [_circle(106,350,15,fill=RED),_circle(414,116,15,fill=RED)]
    if variant=="detail": b.append(_text(256,462,"straightest free path in curved spacetime",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Geodesic",b)


def create_gr_5_2_geodesic_equation(variant="icon"):
    n="GR 5.2"; b=[]; b.extend(_label_tile(58,176,168,144,"d²x/dτ²",fill="#edf3ff",stroke=BLUE,text_colour=BLUE,font_size=34)); b.append(_text(256,260,"+",font_size=52,font_family=FONT,fill=BLACK,text_anchor="middle")); b.extend(_label_tile(286,176,168,144,"Γ uu",fill="#fff8e8",stroke=AMBER,text_colour=AMBER,font_size=38)); b.append(_text(256,374,"= 0",font_size=46,font_family=FONT,fill=GREEN,text_anchor="middle"))
    if variant=="detail": b.append(_text(256,118,"coordinate acceleration + geometry",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Geodesic equation",b)


def create_gr_5_3_geodesic_action(variant="icon"):
    n="GR 5.3"; b=[]; A=(84,360); B=(426,138)
    for d,colour,w in [("M84,360 C176,128 326,382 426,138",LIGHT_GREY,4),("M84,360 C182,300 296,230 426,138",BLUE,9),("M84,360 C194,398 326,164 426,138",LIGHT_GREY,4)]: b.append(_path(d,fill="none",stroke=colour,stroke_width=w,stroke_dasharray="9 8" if colour==LIGHT_GREY else None))
    b += [_circle(*A,16,fill=RED),_circle(*B,16,fill=RED),_text(256,248,"δS = 0",font_size=44,font_family=FONT,fill=BLUE,text_anchor="middle")]
    if variant=="detail": b.append(_text(256,450,"stationary proper-time or length action",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Geodesic action",b)


def create_gr_5_4_four_velocity(variant="icon"):
    n="GR 5.4"; a=f"{_sid(n)}_u"; d=[_arrow_marker(a,colour=GREEN,size=6)]; b=[]; b.extend(_draw_manifold_patch(62,88,388,338)); b.append(_path("M112,360 C194,322 216,240 274,220 C330,198 358,144 408,112",fill="none",stroke=BLACK,stroke_width=7)); b.append(_line(274,220,354,134,stroke=GREEN,stroke_width=9,marker_end=f"url(#{a})")); b.append(_math_text(356,128,"u",sup="μ",font_size=40,font_family=FONT,fill=GREEN))
    if variant=="detail": b.append(_text(256,464,"u = dx/dτ tangent to the worldline",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Four-velocity in curved spacetime",b,d)


def create_gr_5_5_four_acceleration(variant="icon"):
    n="GR 5.5"; a=f"{_sid(n)}_a"; d=[_arrow_marker(a,colour=RED,size=6)]; b=[]; b.append(_path("M92,360 C176,304 246,288 326,198 C358,164 390,140 430,120",fill="none",stroke=BLUE,stroke_width=8)); b.append(_circle(256,270,16,fill=AMBER,stroke=BLACK,stroke_width=2)); b.append(_line(256,270,330,326,stroke=RED,stroke_width=9,marker_end=f"url(#{a})")); b.append(_math_text(340,352,"a",sup="μ",font_size=40,font_family=FONT,fill=RED))
    if variant=="detail": b += [_text(256,82,"supported / thrust",font_size=27,font_family=FONT,fill=RED,text_anchor="middle"),_text(256,450,"geodesic free fall: a = 0",font_size=29,font_family=FONT,fill=GREEN,text_anchor="middle")]
    return _svg(n,"Four-acceleration",b,d)


def create_gr_5_6_geodesic_deviation(variant="icon"):
    n="GR 5.6"; a=f"{_sid(n)}_sep"; d=[_arrow_marker(a,colour=RED,size=6)]; b=[]
    b += [_path("M154,414 C130,302 154,190 206,94",fill="none",stroke=BLUE,stroke_width=8),_path("M358,414 C382,302 358,190 306,94",fill="none",stroke=BLUE,stroke_width=8)]
    b.append(_line(174,250,338,250,stroke=RED,stroke_width=7,marker_end=f"url(#{a})")); b.append(_text(256,226,"ξ",font_size=42,font_family=FONT,fill=RED,text_anchor="middle"))
    if variant=="detail": b.append(_text(256,464,"curvature changes neighbouring separation",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Geodesic deviation",b,d)


def create_gr_6_1_riemann_tensor(variant="icon"):
    n="GR 6.1"; a=f"{_sid(n)}_a"; d=[_arrow_marker(a,colour=GREEN,size=6)]; b=[]; b.extend(_draw_manifold_patch(58,82,396,344)); b.append(_path("M150,334 L154,174 L350,168 L366,334 Z",fill="none",stroke=BLUE,stroke_width=7))
    b.append(_line(150,334,150,252,stroke=GREEN,stroke_width=8,marker_end=f"url(#{a})")); b.append(_line(366,334,416,272,stroke=GREEN,stroke_width=8,marker_end=f"url(#{a})")); b.append(_math_text(256,270,"R",sup="ρ",sub="σμν",font_size=44,font_family=FONT,fill=RED,text_anchor="middle"))
    if variant=="detail": b.append(_text(256,466,"loop transport reveals curvature",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Riemann curvature tensor",b,d)


def create_gr_6_2_ricci_tensor(variant="icon"):
    n="GR 6.2"; b=[]
    for x in [132,194,256,318,380]: b.append(_path(f"M{x},416 C{x-30},310 {256+(x-256)*.45},196 256,92",fill="none",stroke=BLUE,stroke_width=6))
    b.append(_math_text(350,264,"R",sub="μν",font_size=48,font_family=FONT,fill=RED))
    if variant=="detail": b += [_text(256,460,"volume focusing • Riemann contraction",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"),_text(256,70,"neighbouring geodesic bundle",font_size=25,font_family=FONT,fill=BLUE,text_anchor="middle")]
    return _svg(n,"Ricci tensor",b)


def create_gr_6_3_ricci_scalar(variant="icon"):
    n="GR 6.3"; b=[]; b.extend(_draw_manifold_patch(62,88,388,334)); b.append(_circle(256,252,92,fill="#fff0cc",stroke=AMBER,stroke_width=5,opacity="0.8")); b.append(_text(256,276,"R",font_size=78,font_family=FONT,font_style="italic",fill=RED,text_anchor="middle"))
    if variant=="detail": b.append(_text(256,464,"one scalar contraction of Ricci curvature",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Ricci scalar",b)


def create_gr_6_4_einstein_tensor(variant="icon"):
    n="GR 6.4"; b=[]; b.extend(_label_tile(44,188,132,120,"Rμν",fill="#edf3ff",stroke=BLUE,text_colour=BLUE,font_size=39)); b.append(_text(204,258,"−",font_size=50,font_family=FONT,fill=BLACK,text_anchor="middle")); b.extend(_label_tile(232,188,132,120,"½gR",fill="#fff8e8",stroke=AMBER,text_colour=AMBER,font_size=38)); b.append(_text(390,258,"= G",font_size=45,font_family=FONT,fill=GREEN,text_anchor="middle"))
    if variant=="detail": b += [_text(256,128,"divergence-free curvature combination",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"),_text(256,382,"∇μ Gμν = 0",font_size=36,font_family=FONT,fill=GREEN,text_anchor="middle")]
    return _svg(n,"Einstein tensor",b)


def create_gr_6_5_bianchi_identity(variant="icon"):
    n="GR 6.5"; a=f"{_sid(n)}_a"; d=[_arrow_marker(a,colour=BLUE,size=6)]; b=[]; pts=[(256,100),(104,366),(408,366),(256,100)]
    for p,q in zip(pts,pts[1:]): b.append(_line(*p,*q,stroke=BLUE,stroke_width=8,marker_end=f"url(#{a})"))
    for x,y,t in [(256,84,"∇R"),(84,390,"∇R"),(428,390,"∇R")]: b.append(_text(x,y,t,font_size=30,font_family=FONT,fill=BLUE,text_anchor="middle"))
    b.append(_text(256,278,"cyclic = 0",font_size=42,font_family=FONT,fill=GREEN,text_anchor="middle"))
    if variant=="detail": b.append(_text(256,458,"curvature derivatives obey a cyclic identity",font_size=26,font_family=FONT,fill=GREY,text_anchor="middle"))
    return _svg(n,"Bianchi identity",b,d)


def create_gr_6_6_curvature_invariants(variant="icon"):
    n="GR 6.6"; b=[]
    for x,colour,label in [(78,BLUE,"x"),(306,AMBER,"x′")]: b += [_rect(x,154,128,190,rx=10,fill="#fff",stroke=colour,stroke_width=5),_text(x+64,250,label,font_size=44,font_family=FONT,fill=colour,text_anchor="middle")]
    b.append(_text(256,250,"K",font_size=62,font_family=FONT,fill=RED,text_anchor="middle")); b.append(_line(208,250,230,250,stroke=GREEN,stroke_width=5)); b.append(_line(282,250,304,250,stroke=GREEN,stroke_width=5))
    if variant=="detail": b += [_text(256,404,"same scalar in every coordinate chart",font_size=27,font_family=FONT,fill=GREY,text_anchor="middle"),_text(256,104,"K = R·R",font_size=35,font_family=FONT,fill=RED,text_anchor="middle")]
    return _svg(n,"Curvature invariants",b)
