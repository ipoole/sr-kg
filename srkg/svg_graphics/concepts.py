"""Individual deterministic SVG concept drawings."""

from __future__ import annotations

from math import cos, radians, sin

from srkg.svg_graphics.motifs import (
    _axis_arrow_defs,
    _draw_axes,
    _draw_chart_plane,
    _draw_grid,
    _draw_manifold_patch,
    _draw_tangent_basis,
    _draw_tangent_plane,
    _draw_tensor_glyph,
    _implies_symbol,
    _label_tile,
    _paren_column,
    _paren_matrix,
)
from srkg.svg_graphics.primitives import (
    AMBER,
    BLACK,
    BLUE,
    CX,
    CY,
    FONT,
    GREEN,
    GREY,
    LIGHT_GREY,
    RED,
    VERY_LIGHT_GREY,
    _arrow_marker,
    _circle,
    _line,
    _math_text,
    _path,
    _polygon,
    _rect,
    _sid,
    _svg,
    _text,
    _tick,
)

# ---------------------------------------------------------------------------
# Layer 1: Foundational Postulates
# ---------------------------------------------------------------------------


def create_1_3_principle_of_relativity(variant: str = "icon") -> str:
    """
    Node: 1.3
    Title: Principle of relativity

    Design prompt
    -------------
    Create a clean educational vector diagram as an SVG.

    This image is one member of a consistent series of illustrations for a
    knowledge graph on Special Relativity and Classical Field Theory.

    Subject: the principle of relativity.

    Show two simple inertial reference frames, labelled S and S', moving
    uniformly relative to one another.  The frames should look structurally
    identical, indicating that the same laws of physics hold in both.  Use a
    single relative-velocity arrow labelled v between them.  Do not include
    acceleration, forces, curved paths, engines, rockets, planets, or clocks.

    The dominant icon-scale silhouette should be:
        two similar coordinate frames + one relative motion arrow.

    Include only the labels S, S', v, x, y.  No title, no equation.
    """
    node_id = "1.3"
    marker_id, defs = _axis_arrow_defs(node_id, BLACK)
    v_marker = f"{_sid(node_id)}_v_arrow"
    defs.append(_arrow_marker(v_marker, colour=BLUE, size=6))

    body: list[str] = []

    # Two equal "laboratory frames" with identical axes and identical internal
    # straight experiment traces. Their offset and the single arrow carry the
    # relative-motion idea; identical structure carries the symmetry idea.
    for ox, oy, frame_label in [(94, 368, "S"), (308, 244, "S′")]:
        body.append(_rect(ox - 34, oy - 118, 170, 148, rx=18,
                          fill=VERY_LIGHT_GREY, opacity="0.62", stroke=LIGHT_GREY,
                          stroke_width=2))
        body.extend(_draw_axes(ox, oy, 112, 104, marker_id,
                               x_label="x", y_label="y", stroke_width=5))
        body.append(_line(ox + 26, oy - 35, ox + 88, oy - 78,
                          stroke=AMBER, stroke_width=7, stroke_linecap="round"))
        body.append(_circle(ox + 55, oy - 55, 10, fill=AMBER, stroke=BLACK,
                            stroke_width=2))
        if variant == "detail":
            for tick_x in [ox + 34, ox + 58, ox + 82]:
                body.append(_line(tick_x, oy - 15, tick_x + 12, oy - 15,
                                  stroke=GREY, stroke_width=3,
                                  stroke_linecap="round", opacity="0.55"))
            for tick_y in [oy - 78, oy - 54, oy - 30]:
                body.append(_line(ox + 122, tick_y, ox + 122, tick_y + 12,
                                  stroke=GREY, stroke_width=3,
                                  stroke_linecap="round", opacity="0.55"))
        body.append(_text(ox - 24, oy + 42, frame_label, font_size=50,
                          font_family=FONT, font_style="italic", fill=BLACK))

    body.append(_line(206, 176, 268, 176, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{v_marker})"))
    body.append(_text(238, 148, "v", font_size=46, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Principle of relativity", body, defs)


def create_1_2_constancy_of_speed_of_light(variant: str = "icon") -> str:
    """
    Node: 1.2
    Title: Constancy of the speed of light

    Design prompt
    -------------
    Create a clean educational vector diagram as an SVG.

    Subject: constancy of the speed of light.

    Show a central light flash as a small source emitting circular wavefronts.
    Use three concentric circles expanding from the same centre.  Add two
    outward radial light rays in different directions, each labelled c, to
    suggest that the same light speed is measured in different directions or
    by different inertial observers.  Do not include material media, mirrors,
    prisms, lenses, stars, rockets, or detailed observers.

    The dominant icon-scale silhouette should be:
        concentric light wavefronts around a central flash.

    Include only the labels c and source dot.  No title, no equation.
    """
    node_id = "1.2"
    ray_marker = f"{_sid(node_id)}_ray_arrow"
    defs = [_arrow_marker(ray_marker, colour=BLUE, size=6)]

    body: list[str] = []

    # Concentric equal-centre wavefronts are the whole silhouette.
    body.append(_circle(CX, CY, 186, fill="#f4f8ff", stroke="none"))
    for r, sw in [(66, 7), (124, 6), (182, 5)]:
        body.append(_circle(CX, CY, r, fill="none", stroke=BLUE, stroke_width=sw))

    if variant == "detail":
        for angle in [18, 142, 265]:
            a = radians(angle)
            x = CX + 196 * cos(a)
            y = CY - 196 * sin(a)
            tx = 12 * sin(a)
            ty = 12 * cos(a)
            body.append(_line(x - tx, y - ty, x + tx, y + ty,
                              stroke=GREY, stroke_width=4,
                              stroke_linecap="round", opacity="0.45"))

    # Central source dot and flash.
    body.append(_path(
        "M256,209 L269,239 L302,240 L276,260 L286,292 L256,274 L226,292 L236,260 L210,240 L243,239 Z",
        fill=AMBER, opacity="0.34", stroke="none",
    ))
    body.append(_circle(CX, CY, 21, fill=AMBER, stroke=BLACK, stroke_width=3))

    # Two rays in deliberately different directions, both labelled c.
    ray_specs = [
        (24, 404, 160),
        (122, 116, 178),
    ]
    for angle, lx, ly in ray_specs:
        a = radians(angle)
        x1 = CX + 38 * cos(a)
        y1 = CY - 38 * sin(a)
        x2 = CX + 214 * cos(a)
        y2 = CY - 214 * sin(a)
        body.append(_line(x1, y1, x2, y2, stroke=BLUE, stroke_width=7,
                          stroke_linecap="round", marker_end=f"url(#{ray_marker})"))
        body.append(_text(lx, ly, "c", font_size=46, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Constancy of the speed of light", body, defs)


# ---------------------------------------------------------------------------
# Layer 2: Observers and Events
# ---------------------------------------------------------------------------


def create_1_1_inertial_frames(variant: str = "icon") -> str:
    """
    Node: 1.1
    Title: Inertial frames

    Design prompt
    -------------
    Create a clean educational vector diagram as an SVG.

    Subject: inertial frames.

    Show a single Cartesian reference frame with x and y axes.  In the frame,
    draw a small free particle following a straight-line trajectory with a
    constant-velocity arrow.  The line should be straight and uncurved to
    suggest no acceleration and no force.  Do not include gravitational fields,
    curved paths, circular motion, springs, engines, rockets, or clocks.

    The dominant icon-scale silhouette should be:
        coordinate axes + one straight particle track.

    Include only the labels x, y, and v.  No title, no equation.
    """
    node_id = "1.1"
    marker_id, defs = _axis_arrow_defs(node_id, BLACK)
    v_marker = f"{_sid(node_id)}_v_arrow"
    defs.append(_arrow_marker(v_marker, colour=GREEN, size=6))

    body: list[str] = []
    body.extend(_draw_axes(92, 392, 330, 276, marker_id, x_label="x", y_label="y", stroke_width=7))

    # One straight horizontal free-particle track: no curvature, no force cue.
    y_track = 250
    body.append(_line(132, y_track, 390, y_track, stroke=VERY_LIGHT_GREY,
                      stroke_width=20, stroke_linecap="round", opacity="0.7"))
    body.append(_line(132, y_track, 390, y_track, stroke=GREEN, stroke_width=9,
                      stroke_linecap="round", marker_end=f"url(#{v_marker})"))
    for x in [170, 224, 278]:
        body.append(_circle(x, y_track, 11, fill=GREEN, stroke=BLACK, stroke_width=2))
    if variant == "detail":
        for x in [170, 224, 278, 332]:
            body.append(_line(x, y_track - 34, x, y_track + 34,
                              stroke=LIGHT_GREY, stroke_width=3,
                              stroke_dasharray="5 8", stroke_linecap="round"))
    body.append(_text(334, y_track - 28, "v", font_size=46, font_family=FONT,
                      font_style="italic", fill=GREEN))

    return _svg(node_id, "Inertial frames", body, defs)


def create_2_2_spacetime_event(variant: str = "icon") -> str:
    """
    Node: 2.2
    Title: Spacetime event

    Design prompt
    -------------
    Create a clean educational vector diagram as an SVG.

    Subject: spacetime event.

    Show a two-dimensional spacetime coordinate diagram with horizontal x axis
    and vertical ct axis.  Place a single highlighted point P at one location
    in spacetime.  Add faint dotted projection lines from P to the axes to
    suggest that the event has coordinates.  Do not include worldlines, light
    cones, multiple events, clocks, observers, or equations.

    The dominant icon-scale silhouette should be:
        spacetime axes + one red event point.

    Include only the labels x, ct, and P.  No title, no equation.
    """
    node_id = "2.2"
    marker_id, defs = _axis_arrow_defs(node_id, BLACK)

    body: list[str] = []
    ox, oy = 90, 402
    px, py = 342, 206

    body.extend(_draw_axes(ox, oy, 328, 300, marker_id, x_label="x", y_label="ct", stroke_width=7))

    # A coordinate "corner" from the axes to the event point.
    body.append(_line(px, py, px, oy, stroke=LIGHT_GREY, stroke_width=5,
                      stroke_dasharray="9 9", stroke_linecap="round"))
    body.append(_line(ox, py, px, py, stroke=LIGHT_GREY, stroke_width=5,
                      stroke_dasharray="9 9", stroke_linecap="round"))
    if variant == "detail":
        body.append(_rect(px - 9, oy - 9, 18, 18, rx=3, fill=VERY_LIGHT_GREY,
                          stroke="none"))
        body.append(_rect(ox - 9, py - 9, 18, 18, rx=3, fill=VERY_LIGHT_GREY,
                          stroke="none"))

    # The single event dominates the diagram.
    body.append(_circle(px, py, 25, fill=RED, stroke=BLACK, stroke_width=3.5))
    body.append(_circle(px, py, 7, fill="white", stroke="none", opacity="0.8"))
    body.append(_text(px + 34, py - 24, "P", font_size=50, font_family=FONT,
                      font_style="italic", fill=RED))

    return _svg(node_id, "Spacetime event", body, defs)


def create_2_3_principle_of_locality(variant: str = "icon") -> str:
    """
    Node: 2.3
    Title: Principle of locality

    Design prompt
    -------------
    Create a clean educational vector diagram as an SVG.

    Subject: principle of locality.

    Show a spacetime event at the centre of a small local neighbourhood.  Draw
    short nearby field arrows converging on or meeting at that same event, to
    indicate that interactions depend on quantities defined at the same point
    in spacetime.  Use a faint circular neighbourhood around the event.  Do not
    show instantaneous long-distance action, distant forces, planets, magnets,
    or particles acting across empty space.

    The dominant icon-scale silhouette should be:
        central event + small local neighbourhood + short local arrows.

    Include only the labels x and ct on faint axes.  No title, no equation.
    """
    node_id = "2.3"
    axis_marker = f"{_sid(node_id)}_axis_arrow"
    local_marker_green = f"{_sid(node_id)}_green_arrow"
    local_marker_blue = f"{_sid(node_id)}_blue_arrow"
    defs = [
        _arrow_marker(axis_marker, colour=GREY, size=8),
        _arrow_marker(local_marker_green, colour=GREEN, size=6),
        _arrow_marker(local_marker_blue, colour=BLUE, size=6),
    ]

    body: list[str] = []

    # Faint spacetime axes as context, not the main subject.
    ox, oy = 96, 400
    body.append(_line(ox, oy, 415, oy, stroke=LIGHT_GREY, stroke_width=4,
                      stroke_linecap="round", marker_end=f"url(#{axis_marker})"))
    body.append(_line(ox, oy, ox, 112, stroke=LIGHT_GREY, stroke_width=4,
                      stroke_linecap="round", marker_end=f"url(#{axis_marker})"))
    body.append(_text(424, 402, "x", font_size=32, font_family=FONT,
                      font_style="italic", fill=GREY))
    body.append(_text(73, 101, "ct", font_size=32, font_family=FONT,
                      font_style="italic", fill=GREY))

    # Local neighbourhood: a small bounded region around one event.
    body.append(_circle(CX, CY, 116, fill="#edf3ff", stroke=BLUE,
                        stroke_width=4, stroke_dasharray="12 9"))
    # Short local arrows from nearby directions. All terminate at the same event.
    for x1, y1, x2, y2, colour, marker in [
        (CX - 96, CY, CX - 31, CY, GREEN, local_marker_green),
        (CX + 96, CY, CX + 31, CY, BLUE, local_marker_blue),
        (CX, CY - 96, CX, CY - 31, AMBER, local_marker_green),
        (CX, CY + 96, CX, CY + 31, GREY, local_marker_blue),
    ]:
        body.append(_line(x1, y1, x2, y2, stroke=colour, stroke_width=7,
                          stroke_linecap="round", marker_end=f"url(#{marker})"))

    # The event where local quantities meet.
    body.append(_circle(CX, CY, 24, fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_circle(CX, CY, 7, fill="white", stroke="none"))

    return _svg(node_id, "Principle of locality", body, defs)


# ---------------------------------------------------------------------------
# Layer 3: Minkowski Geometry
# ---------------------------------------------------------------------------


def create_3_3_lorentz_transformations(variant: str = "icon") -> str:
    """
    Node: 3.3
    Title: Lorentz transformations

    Icon design: Show black x/ct axes, blue tilted x'/ct' axes, and one red
    event P. Keep the tilted primed axes as the icon silhouette.

    Detail design: Show the same event receiving different coordinate
    descriptions, using dashed projections to both coordinate systems. Place P
    at a generic non-45-degree location. Light-cone guides may be faint only.
    """
    node_id = "3.3"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    primed_marker = f"{_sid(node_id)}_primed_arrow"
    defs.append(_arrow_marker(primed_marker, colour=BLUE, size=6))

    body: list[str] = []
    ox, oy = 118, 392
    px, py = 340, 196

    body.extend(_draw_axes(ox, oy, 300, 282, axis_marker, x_label="x", y_label="ct", stroke_width=5.5))

    if variant == "detail":
        body.append(_line(ox - 88, oy + 88, ox + 268, oy - 268, stroke=LIGHT_GREY,
                          stroke_width=2.5, stroke_dasharray="8 10", opacity="0.45"))
        body.append(_line(ox - 88, oy - 88, ox + 268, oy + 268, stroke=LIGHT_GREY,
                          stroke_width=2.5, stroke_dasharray="8 10", opacity="0.28"))
        body.append(_line(px, py, px, oy, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="7 8", stroke_linecap="round"))
        body.append(_line(ox, py, px, py, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="7 8", stroke_linecap="round"))
        body.append(_line(px, py, 172, 252, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="7 8", stroke_linecap="round"))
        body.append(_line(px, py, 286, 336, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="7 8", stroke_linecap="round"))

    # Primed frame: same origin, tilted axes.
    body.append(_line(ox, oy, ox + 250, oy - 84, stroke=BLUE, stroke_width=6.5,
                      stroke_linecap="round", marker_end=f"url(#{primed_marker})"))
    body.append(_line(ox, oy, ox + 104, oy - 268, stroke=BLUE, stroke_width=6.5,
                      stroke_linecap="round", marker_end=f"url(#{primed_marker})"))
    body.append(_text(ox + 262, oy - 86, "x′", font_size=38, font_family=FONT,
                      font_style="italic", fill=BLUE))
    body.append(_text(ox + 96, oy - 292, "ct′", font_size=38, font_family=FONT,
                      font_style="italic", fill=BLUE))

    body.append(_circle(px, py, 22, fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_text(px + 28, py - 20, "P", font_size=46, font_family=FONT,
                      font_style="italic", fill=RED))

    return _svg(node_id, "Lorentz transformations", body, defs)


def create_3_2_spacetime_interval(variant: str = "icon") -> str:
    """
    Node: 3.2
    Title: Spacetime interval

    Icon design: Simplify the detailed diagram to two red events A and B
    connected by one bold blue interval segment labelled s^2. Use a
    non-45-degree separation for the icon.

    Detail design: Show a central event O and three example separations:
    timelike inside the light cone labelled s^2 > 0, spacelike outside the
    light cone labelled s^2 < 0, and lightlike on the cone labelled s^2 = 0.
    Timelike/spacelike examples should be deliberately away from accidental
    45-degree placement.
    """
    node_id = "3.2"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)

    body: list[str] = []
    ox, oy = 96, 398

    if variant != "detail":
        ax, ay = 164, 330
        bx, by = 352, 224  # deliberately not a 45-degree displacement
        body.extend(_draw_axes(ox, oy, 322, 292, axis_marker, x_label="x", y_label="ct", stroke_width=5.5))
        body.append(_line(ax, ay, bx, by, stroke=BLUE, stroke_width=10, stroke_linecap="round"))
        body.append(_circle(ax, ay, 18, fill=RED, stroke=BLACK, stroke_width=3))
        body.append(_circle(bx, by, 18, fill=RED, stroke=BLACK, stroke_width=3))
        body.append(_text(ax - 44, ay + 8, "A", font_size=42, font_family=FONT,
                          font_style="italic", fill=RED))
        body.append(_text(bx + 24, by - 14, "B", font_size=42, font_family=FONT,
                          font_style="italic", fill=RED))
        body.append(_text(260, 248, "s²", font_size=44, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))
        return _svg(node_id, "Spacetime interval", body, defs)

    # Detail panel: the interval's sign classification is the lesson.
    ex, ey = 252, 278
    body.extend(_draw_axes(86, 414, 344, 322, axis_marker, x_label="x", y_label="ct", stroke_width=5.2))
    body.append(_line(ex - 138, ey + 138, ex + 138, ey - 138, stroke=BLUE,
                      stroke_width=3.8, stroke_dasharray="9 8", opacity="0.48"))
    body.append(_line(ex - 126, ey - 126, ex + 126, ey + 126, stroke=BLUE,
                      stroke_width=3.8, stroke_dasharray="9 8", opacity="0.48"))

    # Three separations from the same central event.
    timelike = (214, 126)
    spacelike = (406, 244)
    lightlike = (360, 170)
    body.append(_line(ex, ey, timelike[0], timelike[1], stroke=GREEN,
                      stroke_width=8, stroke_linecap="round"))
    body.append(_line(ex, ey, spacelike[0], spacelike[1], stroke=AMBER,
                      stroke_width=8, stroke_linecap="round"))
    body.append(_line(ex, ey, lightlike[0], lightlike[1], stroke=BLUE,
                      stroke_width=7, stroke_linecap="round"))

    for x, y, fill in [(ex, ey, RED), (timelike[0], timelike[1], GREEN),
                       (spacelike[0], spacelike[1], AMBER), (lightlike[0], lightlike[1], BLUE)]:
        body.append(_circle(x, y, 13, fill=fill, stroke=BLACK, stroke_width=2.3))

    body.append(_text(ex - 32, ey + 35, "O", font_size=34, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(128, 114, "s² &gt; 0", font_size=32, font_family=FONT,
                      font_style="italic", fill=GREEN))
    body.append(_text(352, 232, "s² &lt; 0", font_size=32, font_family=FONT,
                      font_style="italic", fill=AMBER))
    body.append(_text(366, 158, "s² = 0", font_size=31, font_family=FONT,
                      font_style="italic", fill=BLUE))

    return _svg(node_id, "Spacetime interval", body, defs)


def create_3_1_metric_tensor(variant: str = "icon") -> str:
    """
    Node: 3.1
    Title: Metric tensor

    Icon design: Show eta as the spacetime measuring rule applied to a single
    displacement on x/ct axes.

    Detail design: Show the metric as a compact diagonal matrix between a
    displacement vector and the invariant interval it computes. Pair this with
    a small spacetime inset so the signs read as a measuring rule, not as a
    free-standing table.
    """
    node_id = "3.1"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)

    body: list[str] = []
    if variant != "detail":
        ox, oy = 112, 390
        px, py = 300, 176
        body.extend(_draw_axes(ox, oy, 290, 286, axis_marker, x_label="x", y_label="ct", stroke_width=5.5))
        body.append(_line(ox, py, px, py, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="7 8", stroke_linecap="round"))
        body.append(_line(px, py, px, oy, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="7 8", stroke_linecap="round"))
        body.append(_line(ox, oy, px, py, stroke=BLUE, stroke_width=9,
                          stroke_linecap="round", marker_end=f"url(#{axis_marker})"))
        body.append(_rect(326, 238, 92, 82, rx=10, fill="#f7f7f7",
                          stroke=BLACK, stroke_width=4))
        body.append(_text(372, 295, "η", font_size=62, font_family=FONT,
                          font_style="italic", fill=BLACK, text_anchor="middle"))
        body.append(_text(382, 214, "s²", font_size=38, font_family=FONT,
                          font_style="italic", fill=GREEN, text_anchor="middle"))
        return _svg(node_id, "Metric tensor", body, defs)

    # Detail panel: the matrix is shown as the rule that measures a displacement.
    body.append(_math_text(254, 62, "η", sub="μν", font_size=34,
                           font_family=FONT, font_style="italic",
                           fill=BLACK, text_anchor="middle"))
    x0, y0 = 206, 98
    entries = [
        ["+1", "0", "0", "0"],
        ["0", "−1", "0", "0"],
        ["0", "0", "−1", "0"],
        ["0", "0", "0", "−1"],
    ]
    body.extend(_paren_matrix(x0, y0, entries, col_gap=48, row_gap=42, font_size=26))
    body.append(_text(254, 302, "measures", font_size=26, font_family=FONT,
                      fill=GREY, text_anchor="middle"))
    body.append(_line(166, 318, 342, 318, stroke=GREEN, stroke_width=5,
                      stroke_linecap="round", marker_end=f"url(#{axis_marker})"))
    body.append(_text(256, 356, "s² = (ct)² − x² − y² − z²", font_size=31,
                      font_family=FONT, font_style="italic", fill=GREEN,
                      text_anchor="middle"))

    # Small spacetime-axis inset: one displacement whose components are measured.
    inset_marker = axis_marker
    ox, oy = 88, 458
    px, py = 236, 382
    body.extend(_draw_axes(ox, oy, 166, 108, inset_marker, x_label="x", y_label="ct",
                           colour=BLACK, stroke_width=3.8))
    body.append(_line(ox, py, px, py, stroke=LIGHT_GREY, stroke_width=3,
                      stroke_dasharray="5 7", stroke_linecap="round"))
    body.append(_line(px, py, px, oy, stroke=LIGHT_GREY, stroke_width=3,
                      stroke_dasharray="5 7", stroke_linecap="round"))
    body.append(_line(ox, oy, px, py, stroke=BLUE, stroke_width=6,
                      stroke_linecap="round", marker_end=f"url(#{axis_marker})"))
    body.append(_text(118, 418, "+ time", font_size=24, font_family=FONT,
                      fill=BLUE, font_weight=700))
    body.append(_text(386, 474, "− space", font_size=22, font_family=FONT,
                      fill=GREY, font_weight=700, text_anchor="middle"))

    return _svg(node_id, "Metric tensor", body, defs)


def create_3_4_light_cone(variant: str = "icon") -> str:
    """
    Node: 3.4
    Title: Light cone

    Icon design: Simplify the detailed diagram to one central red event and
    four 45-degree blue light rays forming future and past cones on x/ct axes.

    Detail design: Keep this geometrically pure: one central event, future and
    past light-cone boundaries, lightly shaded causal regions, and separated
    spacelike side regions. Here 45-degree lines are intentional.
    """
    node_id = "3.4"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)

    body: list[str] = []
    ox, oy = 94, 402
    ex, ey = 256, 266

    body.extend(_draw_axes(ox, oy, 328, 302, axis_marker, x_label="x", y_label="ct", stroke_width=5.5))

    if variant == "detail":
        body.append(_polygon([(ex, ey), (ex - 126, ey - 126), (ex + 126, ey - 126)],
                             fill=BLUE, opacity="0.07", stroke="none"))
        body.append(_polygon([(ex, ey), (ex - 110, ey + 110), (ex + 110, ey + 110)],
                             fill=BLUE, opacity="0.045", stroke="none"))
        body.append(_polygon([(ex, ey), (ex - 118, ey - 118), (ex - 110, ey + 110)],
                             fill=AMBER, opacity="0.035", stroke="none"))
        body.append(_polygon([(ex, ey), (ex + 118, ey - 118), (ex + 110, ey + 110)],
                             fill=AMBER, opacity="0.035", stroke="none"))

    body.append(_line(ex, ey, ex - 128, ey - 128, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round"))
    body.append(_line(ex, ey, ex + 128, ey - 128, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round"))
    body.append(_line(ex, ey, ex - 106, ey + 106, stroke=BLUE, stroke_width=4.5,
                      stroke_linecap="round", opacity="0.52"))
    body.append(_line(ex, ey, ex + 106, ey + 106, stroke=BLUE, stroke_width=4.5,
                      stroke_linecap="round", opacity="0.52"))
    body.append(_circle(ex, ey, 22, fill=RED, stroke=BLACK, stroke_width=3))
    if variant == "detail":
        body.append(_text(ex + 162, ey - 150, "c", font_size=38, font_family=FONT,
                          font_style="italic", fill=BLUE))

    return _svg(node_id, "Light cone", body, defs)


def create_3_5_minkowski_diagram(variant: str = "icon") -> str:
    """
    Node: 3.5
    Title: Minkowski diagram

    Icon design: Simplify the detailed diagram to x/ct axes with three
    worldlines: black vertical rest line, green slanted massive-particle line,
    and one blue 45-degree light ray labelled c.

    Detail design: A working spacetime plot with grid, a rest worldline, a
    sub-light massive-particle worldline deliberately not at 45 degrees, one
    45-degree light ray, upward time arrowheads, and event dots.
    """
    node_id = "3.5"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    rest_marker = f"{_sid(node_id)}_rest_arrow"
    world_marker = f"{_sid(node_id)}_world_arrow"
    light_marker = f"{_sid(node_id)}_light_arrow"
    defs.extend([
        _arrow_marker(rest_marker, colour=BLACK, size=6),
        _arrow_marker(world_marker, colour=GREEN, size=6),
        _arrow_marker(light_marker, colour=BLUE, size=6),
    ])

    body: list[str] = []
    ox, oy = 96, 400

    if variant == "detail":
        for x in [146, 196, 246, 296, 346]:
            body.append(_line(x, 118, x, oy, stroke=VERY_LIGHT_GREY, stroke_width=2))
        for y in [150, 200, 250, 300, 350]:
            body.append(_line(ox, y, 416, y, stroke=VERY_LIGHT_GREY, stroke_width=2))

    body.extend(_draw_axes(ox, oy, 326, 300, axis_marker, x_label="x", y_label="ct", stroke_width=5.5))
    marker_rest = f"url(#{rest_marker})" if variant == "detail" else None
    marker_green = f"url(#{world_marker})" if variant == "detail" else None
    marker_blue = f"url(#{light_marker})" if variant == "detail" else None
    body.append(_line(178, 374, 178, 132, stroke=BLACK, stroke_width=7,
                      stroke_linecap="round", marker_end=marker_rest))
    body.append(_line(236, 374, 328, 132, stroke=GREEN, stroke_width=7,
                      stroke_linecap="round", marker_end=marker_green))
    body.append(_line(126, 374, 350, 150, stroke=BLUE, stroke_width=6,
                      stroke_linecap="round", marker_end=marker_blue))
    body.append(_text(326, 172, "c", font_size=38, font_family=FONT,
                      font_style="italic", fill=BLUE))

    if variant == "detail":
        body.append(_text(190, 146, "rest", font_size=28, font_family=FONT,
                          fill=BLACK))
        body.append(_text(292, 268, "massive", font_size=26, font_family=FONT,
                          fill=GREEN))
        body.append(_circle(178, 252, 9, fill=RED, stroke=BLACK, stroke_width=2))
        body.append(_circle(284, 248, 9, fill=RED, stroke=BLACK, stroke_width=2))

    return _svg(node_id, "Minkowski diagram", body, defs)


# ---------------------------------------------------------------------------
# Layer 4: Four-Vectors and Proper Time
# ---------------------------------------------------------------------------


def create_4_1_proper_time(variant: str = "icon") -> str:
    """Proper time: clock ticks accumulated along a timelike worldline."""
    node_id = "4.1"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    body: list[str] = []
    ox, oy = 90, 404
    ax, ay = 142, 352
    bx, by = 276, 130
    worldline = "M142,352 C158,286 226,274 276,130"

    if variant == "detail":
        body.extend(_draw_grid(ox, 112, 318, 292, 53))
    body.extend(_draw_axes(ox, oy, 330, 302, axis_marker, x_label="x", y_label="ct",
                           stroke_width=5.5))
    if variant == "detail":
        body.append(_line(bx, by, bx, oy, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="8 9", stroke_linecap="round"))
        body.append(_text(bx + 18, oy - 10, "t", font_size=34, font_family=FONT,
                          font_style="italic", fill=GREY))
        body.append(_path("M142,352 C190,220 258,316 276,130", fill="none",
                          stroke=LIGHT_GREY, stroke_width=4, stroke_dasharray="9 9",
                          stroke_linecap="round"))

    body.append(_path(worldline, fill="none", stroke=BLACK, stroke_width=8,
                      stroke_linecap="round"))
    for x, y, angle in [(162, 300, 18), (198, 268, 32), (236, 220, 48), (262, 166, 64)]:
        body.append(_tick(x, y, angle, 34, stroke=BLUE, stroke_width=5,
                          stroke_linecap="round"))
    body.append(_circle(ax, ay, 17, fill=RED, stroke=BLACK, stroke_width=2.5))
    body.append(_circle(bx, by, 17, fill=RED, stroke=BLACK, stroke_width=2.5))
    body.append(_text(ax - 42, ay + 8, "A", font_size=38, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(bx + 22, by - 8, "B", font_size=38, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(214, 246, "τ", font_size=48, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))
    return _svg(node_id, "Proper time", body, defs)


def create_4_2_four_vectors(variant: str = "icon") -> str:
    """Four-vectors: one spacetime object with linked components."""
    node_id = "4.2"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    vec_marker = f"{_sid(node_id)}_vec"
    defs.append(_arrow_marker(vec_marker, colour=BLUE, size=6))
    body: list[str] = []
    ox, oy = 98, 390
    px, py = 306, 230

    body.extend(_draw_axes(ox, oy, 260, 274, axis_marker, x_label="x", y_label="ct",
                           stroke_width=5.2))
    if variant == "detail":
        body.append(_line(px, py, px, oy, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="8 9", stroke_linecap="round"))
        body.append(_line(ox, py, px, py, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="8 9", stroke_linecap="round"))
    body.append(_line(ox, oy, px, py, stroke=BLUE, stroke_width=9,
                      stroke_linecap="round", marker_end=f"url(#{vec_marker})"))
    body.append(_math_text(210, 262, "A", sup="μ", font_size=38,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))

    rows = ["A⁰", "A¹", "A²", "A³"] if variant == "detail" else ["•", "•", "•", "•"]
    body.extend(_paren_column(362, 154, rows, row_gap=34, font_size=24, colour=GREY))
    if variant == "detail":
        body.extend(_label_tile(358, 294, 68, 58, "η", fill="#f7f7f7",
                                stroke=BLACK, font_size=36))
    return _svg(node_id, "Four-vectors", body, defs)


def create_4_3_position_four_vector(variant: str = "icon") -> str:
    """Position four-vector: event position as a vector from the origin."""
    node_id = "4.3"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    vec_marker = f"{_sid(node_id)}_vec"
    defs.append(_arrow_marker(vec_marker, colour=BLUE, size=6))
    body: list[str] = []
    ox, oy = 92, 398
    px, py = 332, 206

    body.extend(_draw_axes(ox, oy, 330, 296, axis_marker, x_label="x", y_label="ct",
                           stroke_width=5.5))
    if variant == "detail":
        body.append(_line(px, py, px, oy, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="8 9", stroke_linecap="round"))
        body.append(_line(ox, py, px, py, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="8 9", stroke_linecap="round"))
        body.extend(_paren_column(366, 292, ["ct", "x"], row_gap=34, font_size=25,
                                  colour=GREY))
    body.append(_line(ox, oy, px, py, stroke=BLUE, stroke_width=9,
                      stroke_linecap="round", marker_end=f"url(#{vec_marker})"))
    body.append(_circle(ox, oy, 9, fill=BLACK, stroke="none"))
    body.append(_circle(px, py, 22, fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_text(ox - 34, oy + 34, "O", font_size=34, font_family=FONT,
                      font_style="italic", fill=BLACK))
    body.append(_text(px + 28, py - 18, "P", font_size=44, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_math_text(220, 286, "x", sup="μ", font_size=38,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))
    return _svg(node_id, "Position four-vector", body, defs)


def create_4_4_velocity_four_vector(variant: str = "icon") -> str:
    """Velocity four-vector: tangent to a timelike worldline per proper time."""
    node_id = "4.4"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    u_marker = f"{_sid(node_id)}_u"
    defs.append(_arrow_marker(u_marker, colour=GREEN, size=6))
    body: list[str] = []
    ox, oy = 92, 402
    ex, ey = 244, 246

    if variant == "detail":
        body.extend(_draw_grid(ox, 112, 318, 290, 53))
    body.extend(_draw_axes(ox, oy, 328, 300, axis_marker, x_label="x", y_label="ct",
                           stroke_width=5.3))
    body.append(_path("M132,366 C168,324 210,300 244,246 C270,198 318,144 386,118",
                      fill="none", stroke=BLACK, stroke_width=7,
                      stroke_linecap="round"))
    if variant == "detail":
        body.append(_tick(208, 286, -34, 32, stroke=BLUE, stroke_width=4.5,
                          stroke_linecap="round"))
        body.append(_tick(288, 194, -34, 32, stroke=BLUE, stroke_width=4.5,
                          stroke_linecap="round"))
        body.append(_text(176, 306, "τ", font_size=29, font_family=FONT,
                          font_style="italic", fill=BLUE))
        body.append(_text(304, 188, "τ+dτ", font_size=27, font_family=FONT,
                          font_style="italic", fill=BLUE))
        body.append(_line(208, 286, 288, 194, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="7 7", stroke_linecap="round"))
        body.append(_text(310, 226, "dx^μ", font_size=27, font_family=FONT,
                          font_style="italic", fill=GREY))
    body.append(_circle(ex, ey, 18, fill=RED, stroke=BLACK, stroke_width=2.5))
    body.append(_line(ex, ey, ex + 72, ey - 126, stroke=GREEN, stroke_width=9,
                      stroke_linecap="round", marker_end=f"url(#{u_marker})"))
    body.append(_math_text(ex + 82, ey - 132, "u", sup="μ", font_size=38,
                           font_family=FONT, font_style="italic", fill=GREEN))
    return _svg(node_id, "Velocity four-vector", body, defs)


def create_4_5_momentum_four_vector(variant: str = "icon") -> str:
    """Momentum four-vector: energy and momentum as one timelike vector."""
    node_id = "4.5"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    p_marker = f"{_sid(node_id)}_p"
    defs.append(_arrow_marker(p_marker, colour=BLUE, size=6))
    body: list[str] = []
    ox, oy = 100, 390
    px, py = 286, 168

    body.extend(_draw_axes(ox, oy, 260, 276, axis_marker, x_label="p", y_label="E/c",
                           stroke_width=5.2))
    if variant == "detail":
        body.append(_line(ox, oy, px - 26, py + 28, stroke=GREEN, stroke_width=7,
                          stroke_linecap="round", opacity="0.35"))
        body.append(_math_text(204, 256, "u", sup="μ", font_size=30,
                               font_family=FONT, font_style="italic",
                               fill=GREEN, opacity="0.65"))
        body.append(_text(318, 146, "m", font_size=31, font_family=FONT,
                          font_style="italic", fill=GREY))
    body.append(_line(ox, oy, px, py, stroke=BLUE, stroke_width=10,
                      stroke_linecap="round", marker_end=f"url(#{p_marker})"))
    body.append(_math_text(232, 202, "p", sup="μ", font_size=40,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))

    body.extend(_paren_column(360, 194, ["E/c", ""], row_gap=48,
                              font_size=31, colour=BLUE))
    body.append(_text(385, 276, "p", font_size=34, font_family=FONT,
                      font_style="italic", fill=GREY, text_anchor="middle"))
    return _svg(node_id, "Momentum four-vector", body, defs)


def create_4_6_mass_energy_equivalence(variant: str = "icon") -> str:
    """Mass-energy equivalence: rest energy from the four-momentum norm."""
    node_id = "4.6"
    body: list[str] = []

    tile_y = 104 if variant == "detail" else 162
    body.append(_rect(74, tile_y, 364, 142, rx=18, fill="#f7f7f7",
                      stroke=BLACK, stroke_width=4))
    body.append(_text(256, tile_y + 92, "E=mc", font_size=72, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))
    body.append(_text(364, tile_y + 60, "2", font_size=36, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))

    if variant == "detail":
        body.append(_line(256, 264, 256, 310, stroke=LIGHT_GREY, stroke_width=5,
                          stroke_linecap="round"))
        body.append(_rect(88, 326, 336, 70, rx=10, fill="#ffffff",
                          stroke=BLACK, stroke_width=3))
        body.append(_math_text(158, 372, "p", sub="μ", font_size=31,
                               font_family=FONT, font_style="italic",
                               fill=GREY, text_anchor="middle"))
        body.append(_math_text(209, 372, "p", sup="μ", font_size=31,
                               font_family=FONT, font_style="italic",
                               fill=GREY, text_anchor="middle"))
        body.append(_text(256, 372, "=", font_size=31, font_family=FONT,
                          fill=GREY, text_anchor="middle"))
        body.append(_text(309, 372, "m", font_size=31, font_family=FONT,
                          font_style="italic", fill=GREY, text_anchor="middle"))
        body.append(_text(326, 357, "2", font_size=19, font_family=FONT,
                          font_style="italic", fill=GREY, text_anchor="middle"))
        body.append(_text(350, 372, "c", font_size=31, font_family=FONT,
                          font_style="italic", fill=GREY, text_anchor="middle"))
        body.append(_text(366, 357, "2", font_size=19, font_family=FONT,
                          font_style="italic", fill=GREY, text_anchor="middle"))
        body.append(_text(256, 446, "rest frame: p = 0", font_size=28,
                          font_family=FONT, font_style="italic", fill=GREY,
                          text_anchor="middle"))
    return _svg(node_id, "Mass-energy equivalence", body)


# ---------------------------------------------------------------------------
# Layer 5: Variational and Hamiltonian Structure
# ---------------------------------------------------------------------------


def create_5_2_action_principle(variant: str = "icon") -> str:
    """Action principle: fixed endpoints, nearby variations, stationary path."""
    node_id = "5.2"
    body: list[str] = []
    ax, ay = 96, 370
    bx, by = 416, 150
    main = "M96,370 C170,250 290,280 416,150"
    varied_a = "M96,370 C158,188 304,356 416,150"
    varied_b = "M96,370 C198,324 274,164 416,150"

    if variant == "detail":
        body.append(_path("M96,370 C145,208 326,334 416,150", fill="none",
                          stroke=LIGHT_GREY, stroke_width=4, stroke_dasharray="10 9"))
        body.append(_path(varied_b, fill="none", stroke=LIGHT_GREY,
                          stroke_width=4, stroke_dasharray="10 9"))
        body.append(_path("M144,260 C176,242 196,242 228,260", fill="none",
                          stroke=AMBER, stroke_width=4, stroke_linecap="round",
                          opacity="0.55"))
        body.append(_path("M250,270 C286,254 318,254 354,270", fill="none",
                          stroke=AMBER, stroke_width=4, stroke_linecap="round",
                          opacity="0.55"))
        body.append(_text(246, 214, "δx", font_size=34, font_family=FONT,
                          font_style="italic", fill=GREY, text_anchor="middle"))
    else:
        body.append(_path(varied_a, fill="none", stroke=LIGHT_GREY,
                          stroke_width=4, stroke_dasharray="10 9"))
        body.append(_path(varied_b, fill="none", stroke=LIGHT_GREY,
                          stroke_width=4, stroke_dasharray="10 9"))

    body.append(_path(main, fill="none", stroke=BLUE, stroke_width=10,
                      stroke_linecap="round"))
    body.append(_circle(ax, ay, 20, fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_circle(bx, by, 20, fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_text(ax - 44, ay + 10, "A", font_size=42, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(bx + 24, by - 10, "B", font_size=42, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(250, 210, "S", font_size=48, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))
    return _svg(node_id, "Action principle", body)


def create_5_1_lagrangian(variant: str = "icon") -> str:
    """Lagrangian: local L tiles accumulate into the action S."""
    node_id = "5.1"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []

    body.append(_path("M80,340 C158,246 230,294 300,206", fill="none",
                      stroke=GREY, stroke_width=7, stroke_linecap="round"))
    if variant == "detail":
        for x, y in [(126, 286), (190, 270), (254, 230)]:
            body.extend(_label_tile(x - 28, y - 28, 56, 56, "L",
                                    fill="#edf3ff", stroke=BLUE,
                                    text_colour=BLUE, font_size=34))
        body.append(_text(260, 388, "∫ L dt", font_size=38, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))
    else:
        body.extend(_label_tile(172, 244, 70, 62, "L", fill="#edf3ff",
                                stroke=BLUE, text_colour=BLUE, font_size=42))

    body.append(_line(308, 256, 382, 256, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.extend(_label_tile(390, 214, 76, 84, "S", fill="#fff6df",
                            stroke=AMBER, text_colour=AMBER, font_size=50))
    return _svg(node_id, "Lagrangian", body, defs)


def create_5_3_euler_lagrange(variant: str = "icon") -> str:
    """Euler-Lagrange equations: variation produces an equation of motion."""
    node_id = "5.3"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []

    body.append(_path("M62,342 C118,232 204,308 254,190", fill="none",
                      stroke=LIGHT_GREY, stroke_width=4, stroke_dasharray="10 8"))
    body.append(_path("M62,342 C128,270 194,262 254,190", fill="none",
                      stroke=BLUE, stroke_width=8, stroke_linecap="round"))
    body.append(_circle(62, 342, 14, fill=RED, stroke=BLACK, stroke_width=2))
    body.append(_circle(254, 190, 14, fill=RED, stroke=BLACK, stroke_width=2))
    body.append(_text(50, 382, "A", font_size=34, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(262, 176, "B", font_size=34, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(154, 228, "δ", font_size=40, font_family=FONT,
                      font_style="italic", fill=GREY))

    if variant == "detail":
        body.extend(_label_tile(288, 98, 112, 58, "δS = 0",
                                fill="#f7f7f7", stroke=GREY, font_size=30))
        body.append(_line(344, 164, 344, 238, stroke=BLUE, stroke_width=5,
                          marker_end=f"url(#{arrow})"))
        body.extend(_label_tile(280, 248, 100, 72, "E-L", fill="#edf3ff",
                                stroke=BLUE, text_colour=BLUE, font_size=34))
        body.append(_path("M390,284 C430,272 454,244 474,202", fill="none",
                          stroke=GREEN, stroke_width=6, stroke_linecap="round",
                          marker_end=f"url(#{arrow})"))
    else:
        body.append(_line(270, 256, 340, 256, stroke=BLUE, stroke_width=7,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.extend(_label_tile(356, 214, 96, 84, "E-L", fill="#edf3ff",
                                stroke=BLUE, text_colour=BLUE, font_size=38))

    return _svg(node_id, "Euler-Lagrange equations", body, defs)


def create_5_5_hamiltonian_formalism(variant: str = "icon") -> str:
    """Hamiltonian formalism: phase-space flow generated by H."""
    node_id = "5.5"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    flow_marker = f"{_sid(node_id)}_flow"
    defs.append(_arrow_marker(flow_marker, colour=GREEN, size=6))
    body: list[str] = []

    ox, oy = 100, 388
    body.extend(_draw_axes(ox, oy, 322, 286, axis_marker, x_label="q", y_label="p",
                           stroke_width=6))
    if variant == "detail":
        body.append(_path("M146,318 C214,236 308,230 374,306", fill="none",
                          stroke=LIGHT_GREY, stroke_width=4, stroke_dasharray="9 9"))
        body.append(_path("M166,344 C236,276 316,276 396,338", fill="none",
                          stroke=LIGHT_GREY, stroke_width=4, stroke_dasharray="9 9"))
    body.append(_path("M154,318 C210,214 318,230 376,152", fill="none",
                      stroke=GREEN, stroke_width=8, stroke_linecap="round",
                      marker_end=f"url(#{flow_marker})"))
    body.extend(_label_tile(322, 284, 72, 66, "H", fill="#eef8f0",
                            stroke=GREEN, text_colour=GREEN, font_size=44))
    return _svg(node_id, "Hamiltonian formalism", body, defs)


def create_5_4_canonical_momentum(variant: str = "icon") -> str:
    """Canonical momentum: p paired with q through L's qdot dependence."""
    node_id = "5.4"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=GREEN, size=6)]
    body: list[str] = []

    body.append(_line(76, 344, 290, 344, stroke=BLACK, stroke_width=6,
                      stroke_linecap="round"))
    body.append(_text(298, 374, "q", font_size=42, font_family=FONT,
                      font_style="italic", fill=BLACK))
    body.append(_circle(172, 344, 13, fill=RED, stroke=BLACK, stroke_width=2))
    body.append(_line(172, 344, 172, 242, stroke=GREEN, stroke_width=8,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(188, 250, "p", font_size=44, font_family=FONT,
                      font_style="italic", fill=GREEN))

    if variant == "detail":
        body.append(_line(122, 300, 206, 300, stroke=AMBER, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.append(_text(154, 288, "q̇", font_size=34, font_family=FONT,
                          font_style="italic", fill=AMBER, text_anchor="middle"))
        body.extend(_label_tile(312, 164, 64, 60, "L", fill="#edf3ff",
                                stroke=BLUE, text_colour=BLUE, font_size=38))
        body.append(_line(340, 232, 340, 282, stroke=BLUE, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.append(_rect(304, 270, 126, 54, rx=12, fill="#f7f7f7",
                          stroke=GREY, stroke_width=3))
        body.append(_text(367, 305, "∂L / ∂q̇", font_size=25,
                          font_family=FONT, font_style="italic",
                          fill=BLACK, text_anchor="middle"))
        body.append(_line(304, 318, 214, 306, stroke=GREEN, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
    else:
        body.extend(_label_tile(320, 252, 72, 62, "L", fill="#edf3ff",
                                stroke=BLUE, text_colour=BLUE, font_size=38))
        body.append(_line(314, 282, 220, 282, stroke=GREEN, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))

    return _svg(node_id, "Canonical momentum", body, defs)


def create_5_6_noethers_theorem(variant: str = "icon") -> str:
    """Noether's theorem: continuous symmetry implies conserved Q."""
    node_id = "5.6"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []

    body.extend(_label_tile(92, 204, 98, 88, "S", fill="#edf3ff",
                            stroke=BLUE, text_colour=BLUE, font_size=54))
    body.append(_path("M108,194 C86,152 112,110 156,104 C210,96 238,154 206,194",
                      fill="none", stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    if variant == "detail":
        body.append(_text(140, 324, "unchanged", font_size=30, font_family=FONT,
                          fill=BLUE, text_anchor="middle"))
    body.extend(_implies_symbol(204, 229, width=104, height=38,
                                colour=BLUE, stroke_width=5))
    body.extend(_label_tile(324, 198, 108, 100, "Q", fill="#fff6df",
                            stroke=AMBER, text_colour=AMBER, font_size=58))
    body.append(_circle(406, 212, 11, fill="none", stroke=AMBER, stroke_width=4))
    body.append(_line(400, 218, 412, 206, stroke=AMBER, stroke_width=4,
                      stroke_linecap="round"))
    if variant == "detail":
        body.append(_text(378, 332, "conserved", font_size=30, font_family=FONT,
                          fill=AMBER, text_anchor="middle"))
    return _svg(node_id, "Noether's theorem", body, defs)


# ---------------------------------------------------------------------------
# Layer 6: Classical Fields
# ---------------------------------------------------------------------------


def create_6_1_scalar_field(variant: str = "icon") -> str:
    """Scalar field: one non-directional value assigned to every event."""
    node_id = "6.1"
    axis_marker, defs = _axis_arrow_defs(node_id, GREY)
    body: list[str] = []
    x0, y0, width, height = 98, 118, 300, 280
    body.extend(_draw_grid(x0, y0, width, height, 60))
    body.extend(_draw_axes(82, 414, 336, 310, axis_marker, x_label="x", y_label="ct",
                           colour=GREY, stroke_width=4))

    samples = [
        (138, 336, 13, "#d7e5ff"), (198, 292, 22, "#8fb0ff"),
        (258, 248, 31, BLUE), (318, 204, 21, "#8fb0ff"),
        (378, 322, 16, "#bdd0ff"),
    ]
    if variant == "detail":
        samples += [(138, 192, 18, "#bdd0ff"), (198, 160, 26, "#6d93ed"),
                    (318, 352, 12, "#d7e5ff"), (378, 152, 15, "#bdd0ff")]
    for x, y, r, fill in samples:
        body.append(_circle(x, y, r, fill=fill, stroke=BLACK, stroke_width=2,
                            opacity="0.92"))
    label = "φ(x)" if variant == "detail" else "φ"
    body.append(_text(300, 246, label, font_size=42, font_family=FONT,
                      font_style="italic", fill=BLACK))
    return _svg(node_id, "Scalar field", body, defs)


def create_6_2_vector_field(variant: str = "icon") -> str:
    """Vector field: a vector anchored at every spacetime event."""
    node_id = "6.2"
    axis_marker, defs = _axis_arrow_defs(node_id, GREY)
    arrow = f"{_sid(node_id)}_vec"
    defs.append(_arrow_marker(arrow, colour=BLUE, size=5))
    body: list[str] = []
    x0, y0, width, height = 96, 118, 306, 282
    body.extend(_draw_grid(x0, y0, width, height, 60))
    body.extend(_draw_axes(80, 416, 340, 312, axis_marker, x_label="x", y_label="ct",
                           colour=GREY, stroke_width=4))

    vectors = [
        (140, 336, 36, -18), (202, 300, 42, -8), (264, 258, 38, -30),
        (326, 216, 32, -38), (202, 186, 34, 18), (328, 342, 44, -10),
    ]
    if variant == "detail":
        vectors += [(140, 216, 28, 24), (264, 152, 36, -16), (382, 284, 26, -34)]
    for x, y, dx, dy in vectors:
        body.append(_circle(x, y, 5, fill=BLACK, opacity="0.45"))
        body.append(_line(x, y, x + dx, y + dy, stroke=BLUE, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_math_text(278, 86, "A", sub="μ", font_size=40,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(308, 86, "(x)", font_size=31, font_family=FONT,
                          font_style="italic", fill=BLUE))
    return _svg(node_id, "Vector field", body, defs)


def create_6_3_field_lagrangian(variant: str = "icon") -> str:
    """Field Lagrangian: local density over spacetime integrates to field action."""
    node_id = "6.3"
    axis_marker, defs = _axis_arrow_defs(node_id, GREY)
    arrow = f"{_sid(node_id)}_arrow"
    defs.append(_arrow_marker(arrow, colour=BLUE, size=6))
    body: list[str] = []
    body.extend(_draw_grid(76, 112, 260, 280, 52))
    body.extend(_draw_axes(64, 410, 286, 310, axis_marker, x_label="x", y_label="ct",
                           colour=GREY, stroke_width=4))

    region = [
        (112, 324), (94, 250), (132, 184), (214, 154),
        (292, 190), (314, 276), (254, 342), (174, 356),
    ]
    body.append(_polygon(region, fill="#edf3ff", stroke=BLUE,
                         stroke_width=4, opacity="0.82"))
    body.append(_text(198, 262, "∫ℒ d⁴x", font_size=35, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))
    if variant == "detail":
        for x, y in [(126, 276), (156, 212), (224, 198), (266, 274)]:
            body.append(_circle(x, y, 5, fill=BLUE, stroke="none", opacity="0.75"))
            body.append(_text(x + 12, y - 8, "ℒ", font_size=25, font_family=FONT,
                              font_style="italic", fill=BLUE))
        body.append(_text(220, 386, "region in d⁴x", font_size=26,
                          font_family=FONT, font_style="italic", fill=GREY,
                          text_anchor="middle"))
    body.append(_line(322, 252, 380, 252, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.extend(_label_tile(392, 210, 78, 84, "S", fill="#fff6df",
                            stroke=AMBER, text_colour=AMBER, font_size=50))
    return _svg(node_id, "Field Lagrangian", body, defs)


def create_6_4_field_equations(variant: str = "icon") -> str:
    """Field equations: local differential stencil propagates field values."""
    node_id = "6.4"
    axis_marker, defs = _axis_arrow_defs(node_id, GREY)
    arrow = f"{_sid(node_id)}_arrow"
    defs.append(_arrow_marker(arrow, colour=GREEN, size=5))
    body: list[str] = []
    body.extend(_draw_grid(76, 110, 250, 282, 50))
    body.extend(_draw_axes(64, 410, 282, 308, axis_marker, x_label="x", y_label="ct",
                           colour=GREY, stroke_width=4))

    cx, cy = 202, 250
    neighbours = [(152, 250), (252, 250), (202, 200), (202, 300)]
    for x, y in neighbours:
        body.append(_circle(x, y, 13, fill="#d7e5ff", stroke=BLUE, stroke_width=2))
        body.append(_line(x, y, cx + (x - cx) * 0.25, cy + (y - cy) * 0.25,
                          stroke=GREEN, stroke_width=4, stroke_linecap="round",
                          marker_end=f"url(#{arrow})"))
    body.append(_circle(cx, cy, 21, fill=BLUE, stroke=BLACK, stroke_width=2.5))
    body.append(_text(cx, cy + 9, "φ", font_size=32, font_family=FONT,
                      font_style="italic", fill="white", text_anchor="middle"))
    body.append(_line(288, 250, 350, 250, stroke=BLUE, stroke_width=6,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.extend(_label_tile(362, 214, 104, 72, "field eq", fill="#f7f7f7",
                            stroke=BLACK, font_size=25))
    if variant == "detail":
        body.append(_path("M374,334 C410,304 448,326 470,286", fill="none",
                          stroke=BLUE, stroke_width=5, stroke_linecap="round",
                          marker_end=f"url(#{arrow})"))
    return _svg(node_id, "Field equations", body, defs)


# ---------------------------------------------------------------------------
# Layer 7: Electromagnetic Field Structure
# ---------------------------------------------------------------------------


def create_7_1_vector_potential(variant: str = "icon") -> str:
    """Vector potential A_mu: potential field whose derivatives build F."""
    node_id = "7.1"
    axis_marker, defs = _axis_arrow_defs(node_id, GREY)
    avec = f"{_sid(node_id)}_avec"
    flow = f"{_sid(node_id)}_flow"
    defs.extend([
        _arrow_marker(avec, colour=BLUE, size=5),
        _arrow_marker(flow, colour=GREEN, size=6),
    ])
    body: list[str] = []
    body.extend(_draw_grid(76, 110, 258, 288, 52))
    body.extend(_draw_axes(64, 416, 286, 314, axis_marker, x_label="x", y_label="ct",
                           colour=GREY, stroke_width=4))
    for x, y, dx, dy in [(118, 334, 34, -14), (170, 282, 38, -30),
                         (222, 230, 32, -24), (274, 178, 30, -36),
                         (222, 334, 42, -8)]:
        body.append(_circle(x, y, 4, fill=BLACK, opacity="0.45"))
        body.append(_line(x, y, x + dx, y + dy, stroke=BLUE, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{avec})"))
    if variant == "detail":
        body.append(_rect(148, 204, 128, 104, rx=10, fill="none", stroke=GREEN,
                          stroke_width=3, stroke_dasharray="8 7"))
        body.append(_text(210, 196, "∂A", font_size=31, font_family=FONT,
                          font_style="italic", fill=GREEN, text_anchor="middle"))
    body.append(_line(324, 256, 374, 256, stroke=GREEN, stroke_width=6,
                      stroke_linecap="round", marker_end=f"url(#{flow})"))
    body.extend(_label_tile(386, 218, 82, 76, "F", fill="#eef8f0",
                            stroke=GREEN, text_colour=GREEN, font_size=48))
    body.append(_math_text(154, 82, "A", sub="μ", font_size=38,
                           font_family=FONT, font_style="italic", fill=BLUE))
    return _svg(node_id, "Vector potential", body, defs)


def create_7_2_field_tensor(variant: str = "icon") -> str:
    """Electromagnetic field tensor: antisymmetric F_mu_nu containing E and B."""
    node_id = "7.2"
    body: list[str] = []

    if variant != "detail":
        body.extend(_label_tile(156, 124, 200, 200, "F", fill="#f7f7f7",
                                stroke=BLACK, font_size=76))
        body.append(_line(186, 178, 326, 178, stroke=BLUE, stroke_width=16,
                          stroke_linecap="round", opacity="0.65"))
        body.append(_line(326, 270, 186, 270, stroke=RED, stroke_width=16,
                          stroke_linecap="round", opacity="0.65"))
        body.append(_math_text(256, 388, "F", sub="μν", font_size=36,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))
        return _svg(node_id, "Field tensor", body)

    x0, y0, cell = 118, 108, 68
    body.append(_math_text(254, 72, "F", sub="μν", font_size=36,
                           font_family=FONT, font_style="italic",
                           fill=BLACK, text_anchor="middle"))
    for r in range(4):
        for c in range(4):
            x, y = x0 + c * cell, y0 + r * cell
            diag = r == c
            if diag:
                fill = "#f7f7f7"
            elif r == 0 or c == 0:
                fill = "#edf3ff"
            else:
                fill = "#eef8f0"
            body.append(_rect(x, y, cell, cell, rx=4, fill=fill,
                              stroke=VERY_LIGHT_GREY, stroke_width=2))
            if diag:
                label, colour = "0", LIGHT_GREY
            elif r == 0:
                label, colour = "E", BLUE
            elif c == 0:
                label, colour = "−E", BLUE
            else:
                label, colour = "B", GREEN
            body.append(_text(x + cell / 2, y + 43, label, font_size=28,
                              font_family=FONT, font_style="italic",
                              fill=colour, text_anchor="middle"))
    body.append(_text(124, 424, "antisymmetric", font_size=30, font_family=FONT,
                      fill=GREY))
    body.append(_text(356, 424, "E + B", font_size=34, font_family=FONT,
                      fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Field tensor", body)


def create_7_3_electric_field(variant: str = "icon") -> str:
    """Electric field: radial field and force on a rest test charge."""
    node_id = "7.3"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []
    cx, cy = 226, 254
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        a = radians(angle)
        x1, y1 = cx + 42 * cos(a), cy + 42 * sin(a)
        x2, y2 = cx + 154 * cos(a), cy + 154 * sin(a)
        body.append(_line(x1, y1, x2, y2, stroke=BLUE, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_circle(cx, cy, 30, fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_line(cx - 12, cy, cx + 12, cy, stroke="white", stroke_width=5,
                      stroke_linecap="round"))
    body.append(_line(cx, cy - 12, cx, cy + 12, stroke="white", stroke_width=5,
                      stroke_linecap="round"))
    body.append(_text(384, 140, "E", font_size=48, font_family=FONT,
                      font_style="italic", fill=BLUE))
    if variant == "detail":
        tqx, tqy = 388, 254
        body.append(_circle(tqx, tqy, 16, fill="#ffdada", stroke=RED, stroke_width=2))
        body.append(_text(tqx, tqy + 9, "+", font_size=25, font_family=FONT,
                          fill=RED, text_anchor="middle"))
        body.append(_line(tqx + 24, tqy, tqx + 86, tqy, stroke=RED, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.append(_text(tqx + 66, tqy - 16, "F", font_size=32, font_family=FONT,
                          font_style="italic", fill=RED))
    return _svg(node_id, "Electric field", body, defs)


def create_7_4_magnetic_field(variant: str = "icon") -> str:
    """Magnetic field: circular field around current or moving charge."""
    node_id = "7.4"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=GREEN, size=5)]
    body: list[str] = []

    body.append(_line(256, 392, 256, 120, stroke=RED, stroke_width=10,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(286, 194, "v", font_size=34, font_family=FONT,
                      font_style="italic", fill=RED))
    for rx, ry, sw in [(86, 34, 6), (132, 56, 5), (178, 78, 4)]:
        body.append(_path(f"M{256-rx},{256} C{256-rx},{256-ry} {256+rx},{256-ry} {256+rx},{256} "
                          f"C{256+rx},{256+ry} {256-rx},{256+ry} {256-rx},{256}",
                          fill="none", stroke=GREEN, stroke_width=sw,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(404, 214, "B", font_size=48, font_family=FONT,
                      font_style="italic", fill=GREEN))
    if variant == "detail":
        body.append(_circle(382, 320, 13, fill=RED, stroke=BLACK, stroke_width=2))
        body.append(_line(382, 320, 432, 342, stroke=AMBER, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.append(_text(450, 360, "F", font_size=30, font_family=FONT,
                          font_style="italic", fill=AMBER))
    return _svg(node_id, "Magnetic field", body, defs)


def create_7_5_electromagnetic_field(variant: str = "icon") -> str:
    """Electromagnetic field: unified F with E and B as components."""
    node_id = "7.5"
    axis_marker, defs = _axis_arrow_defs(node_id, GREY)
    e_arrow = f"{_sid(node_id)}_e"
    defs.append(_arrow_marker(e_arrow, colour=BLUE, size=6))
    body: list[str] = []
    if variant == "detail":
        body.extend(_draw_grid(82, 108, 348, 296, 58))
        body.extend(_draw_axes(70, 420, 382, 326, axis_marker, x_label="x", y_label="ct",
                               colour=GREY, stroke_width=3.5))
        body.append(_text(382, 120, "frame", font_size=28, font_family=FONT,
                          fill=GREY))

    body.extend(_label_tile(190, 172, 132, 116, "F", fill="#f7f7f7",
                            stroke=BLACK, font_size=68))
    body.append(_line(114, 224, 184, 224, stroke=BLUE, stroke_width=8,
                      stroke_linecap="round", marker_end=f"url(#{e_arrow})"))
    body.append(_text(106, 214, "E", font_size=42, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="end"))
    body.append(_path("M330,224 C372,182 418,218 376,258 C350,284 322,270 338,238",
                      fill="none", stroke=GREEN, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{e_arrow})"))
    body.append(_text(394, 288, "B", font_size=42, font_family=FONT,
                      font_style="italic", fill=GREEN))
    if variant == "detail":
        body.append(_math_text(256, 336, "F", sub="μν", font_size=36,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Electromagnetic field", body, defs)


def create_7_7_maxwells_equations(variant: str = "icon") -> str:
    """Maxwell equations: local source-field law and propagation."""
    node_id = "7.7"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []
    body.extend(_label_tile(58, 210, 84, 84, "J", fill="#ffeaea",
                            stroke=RED, text_colour=RED, font_size=52))
    body.append(_line(150, 252, 214, 252, stroke=RED, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.extend(_label_tile(226, 196, 112, 112, "F", fill="#edf3ff",
                            stroke=BLUE, text_colour=BLUE, font_size=62))
    if variant == "detail":
        body.append(_text(282, 178, "∂", font_size=38, font_family=FONT,
                          fill=GREY, text_anchor="middle"))
        body.append(_math_text(100, 322, "J", sub="μ", font_size=30,
                               font_family=FONT, font_style="italic",
                               fill=RED, text_anchor="middle"))
        body.append(_math_text(282, 340, "F", sub="μν", font_size=31,
                               font_family=FONT, font_style="italic",
                               fill=BLUE, text_anchor="middle"))
    body.append(_line(346, 252, 394, 252, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    for r in [18, 34, 50]:
        body.append(_path(f"M410,{252-r} C456,{232-r} 456,{272+r} 410,{252+r}",
                          fill="none", stroke=BLUE, stroke_width=4,
                          stroke_linecap="round", opacity="0.82"))
    if variant == "detail":
        body.append(_text(438, 332, "wave", font_size=27, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))
    return _svg(node_id, "Maxwell's equations", body, defs)


def create_8_6_lorenz_gauge(variant: str = "icon") -> str:
    """Lorenz gauge: covariant condition selecting a clean potential."""
    node_id = "8.6"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []

    # Equivalent potential representatives entering the gauge condition.
    for y, opacity in [(180, "0.35"), (234, "0.55"), (288, "0.35")]:
        body.append(_path(f"M72,{y} C124,{y-34} 174,{y+28} 220,{y-10}",
                          fill="none", stroke=BLUE, stroke_width=6,
                          stroke_linecap="round", opacity=opacity))
    body.append(_line(230, 234, 286, 234, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_path("M290,142 L368,184 L368,284 L290,326 Z", fill="#f7f7f7",
                      stroke=GREY, stroke_width=4))
    body.append(_text(329, 240, "Lorenz", font_size=23, font_family=FONT,
                      fill=GREY, text_anchor="middle"))
    body.append(_line(364, 234, 418, 234, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_path("M424,234 C448,202 476,218 470,252", fill="none",
                      stroke=BLUE, stroke_width=8, stroke_linecap="round"))
    body.append(_math_text(446, 288, "A", sub="μ", font_size=30,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(
            256, 334,
            '∂<tspan baseline-shift="sub" font-size="68%">μ</tspan> '
            'A<tspan baseline-shift="super" font-size="68%">μ</tspan> = 0',
            font_size=34, font_family=FONT, font_style="italic",
            fill=BLACK, text_anchor="middle",
        ))
        body.extend(_label_tile(82, 378, 58, 50, "F", fill="#eef8f0",
                                stroke=GREEN, text_colour=GREEN, font_size=32))
        body.extend(_label_tile(410, 378, 58, 50, "F", fill="#eef8f0",
                                stroke=GREEN, text_colour=GREEN, font_size=32))
        body.append(_line(144, 404, 406, 404, stroke=GREEN, stroke_width=3,
                          stroke_dasharray="9 8", opacity="0.55"))
    else:
        body.append(_text(
            256, 382,
            '∂<tspan baseline-shift="sub" font-size="68%">μ</tspan>A'
            '<tspan baseline-shift="super" font-size="68%">μ</tspan> = 0',
            font_size=32, font_family=FONT, font_style="italic",
            fill=BLACK, text_anchor="middle",
        ))
    return _svg(node_id, "Lorenz gauge", body, defs)


# ---------------------------------------------------------------------------
# Layer 8: Gauge Coupling and Conservation
# ---------------------------------------------------------------------------


def create_8_1_gauge_invariance(variant: str = "icon") -> str:
    """Gauge invariance: equivalent potentials produce the same F."""
    node_id = "8.1"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []

    body.append(_path("M82,178 C128,146 164,192 214,162", fill="none",
                      stroke=BLUE, stroke_width=7, stroke_linecap="round"))
    body.append(_path("M82,304 C134,264 172,326 214,290", fill="none",
                      stroke=BLUE, stroke_width=7, stroke_linecap="round", opacity="0.62"))
    body.append(_path("M124,222 C152,244 152,252 124,276", fill="none",
                      stroke=AMBER, stroke_width=5, stroke_linecap="round",
                      marker_end=f"url(#{arrow})"))
    body.append(_text(152, 252, "Λ", font_size=38, font_family=FONT,
                      font_style="italic", fill=AMBER, text_anchor="middle"))
    if variant == "detail":
        body.append(_math_text(150, 140, "A", sub="μ", font_size=30,
                               font_family=FONT, font_style="italic",
                               fill=BLUE, text_anchor="middle"))
        body.append(_text(
            154, 356,
            'A<tspan baseline-shift="sub" font-size="68%">μ</tspan> + '
            '∂<tspan baseline-shift="sub" font-size="68%">μ</tspan>Λ',
            font_size=28, font_family=FONT, font_style="italic",
            fill=BLUE, text_anchor="middle",
        ))
    body.append(_line(224, 176, 332, 232, stroke=BLUE, stroke_width=5,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_line(224, 294, 332, 256, stroke=BLUE, stroke_width=5,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.extend(_label_tile(350, 206, 92, 84, "F", fill="#eef8f0",
                            stroke=GREEN, text_colour=GREEN, font_size=54))
    if variant == "detail":
        body.append(_circle(428, 220, 10, fill="none", stroke=GREEN, stroke_width=4))
        body.append(_line(422, 226, 434, 214, stroke=GREEN, stroke_width=4,
                          stroke_linecap="round"))
        body.append(_text(
            394, 326,
            'same F<tspan baseline-shift="sub" font-size="68%">μν</tspan>',
            font_size=28, font_family=FONT, fill=GREEN,
            text_anchor="middle",
        ))
    return _svg(node_id, "Gauge invariance", body, defs)


def create_7_6_four_current(variant: str = "icon") -> str:
    """Four-current: charge density and current density as one source vector."""
    node_id = "7.6"
    axis_marker, defs = _axis_arrow_defs(node_id, GREY)
    arrow = f"{_sid(node_id)}_arrow"
    defs.append(_arrow_marker(arrow, colour=RED, size=6))
    body: list[str] = []

    if variant == "detail":
        body.extend(_draw_grid(70, 122, 250, 260, 50))
        body.extend(_draw_axes(58, 398, 282, 290, axis_marker, x_label="x", y_label="ct",
                               colour=GREY, stroke_width=3.8))
        for x, y in [(112, 318), (148, 286), (172, 334), (214, 272), (240, 318)]:
            body.append(_circle(x, y, 8, fill=RED, stroke=BLACK, stroke_width=1.5))
        body.append(_line(132, 250, 248, 222, stroke=RED, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))

    body.append(_rect(324, 162, 112, 160, rx=12, fill="#ffeaea",
                      stroke=RED, stroke_width=3))
    body.append(_math_text(380, 224, "J", sup="μ", font_size=38,
                           font_family=FONT, font_style="italic",
                           fill=RED, text_anchor="middle"))
    body.append(_line(342, 214, 418, 214, stroke=RED, stroke_width=4,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_circle(356, 268, 14, fill=RED, stroke=BLACK, stroke_width=2))
    body.append(_text(380, 274, "ρ", font_size=32, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(382, 204, "J", font_size=34, font_family=FONT,
                      font_style="italic", fill=RED, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(380, 348, "ρc + J", font_size=29, font_family=FONT,
                          font_style="italic", fill=RED, text_anchor="middle"))
    return _svg(node_id, "Four-current", body, defs)


def create_8_3_minimal_coupling(variant: str = "icon") -> str:
    """Minimal coupling: p is replaced by a gauge-covariant p - eA."""
    node_id = "8.3"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []

    if variant == "detail":
        for x, y, dx, dy in [(190, 164, 26, -18), (228, 218, 34, -8), (190, 286, 30, -24)]:
            body.append(_line(x, y, x + dx, y + dy, stroke=BLUE, stroke_width=4,
                              stroke_linecap="round", marker_end=f"url(#{arrow})", opacity="0.65"))
        body.append(_path("M70,346 C142,260 214,306 286,218", fill="none",
                          stroke=GREY, stroke_width=5, stroke_linecap="round"))
        body.append(_circle(164, 292, 13, fill=RED, stroke=BLACK, stroke_width=2))

    body.append(_line(62, 252, 166, 252, stroke=BLACK, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(98, 232, "p", font_size=42, font_family=FONT,
                      font_style="italic", fill=BLACK, text_anchor="middle"))
    body.extend(_label_tile(184, 210, 84, 84, "eA", fill="#edf3ff",
                            stroke=BLUE, text_colour=BLUE, font_size=38))
    body.append(_line(278, 252, 356, 252, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.extend(_label_tile(368, 210, 112, 84, "p-eA", fill="#f7f7f7",
                            stroke=BLACK, font_size=34))
    if variant == "detail":
        body.append(_text(
            242, 338,
            'p<tspan baseline-shift="sub" font-size="68%">μ</tspan> - eA'
            '<tspan baseline-shift="sub" font-size="68%">μ</tspan>',
            font_size=32, font_family=FONT, font_style="italic",
            fill=BLACK, text_anchor="middle",
        ))
    return _svg(node_id, "Minimal coupling", body, defs)


def create_8_4_lorentz_force_law(variant: str = "icon") -> str:
    """Lorentz force law: F and u change particle momentum."""
    node_id = "8.4"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=RED, size=6)]
    body: list[str] = []

    body.append(_path("M88,360 C148,254 236,310 296,182", fill="none",
                      stroke=BLACK, stroke_width=6, stroke_linecap="round"))
    body.append(_circle(196, 276, 17, fill=RED, stroke=BLACK, stroke_width=2.5))
    body.append(_line(196, 276, 240, 220, stroke=GREEN, stroke_width=6,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(224, 226, "u", font_size=38, font_family=FONT,
                      font_style="italic", fill=GREEN))
    body.extend(_label_tile(316, 168, 86, 78, "F", fill="#edf3ff",
                            stroke=BLUE, text_colour=BLUE, font_size=50))
    body.append(_line(292, 258, 380, 306, stroke=RED, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(358, 294, "dp", font_size=38, font_family=FONT,
                      font_style="italic", fill=RED))
    if variant == "detail":
        body.append(_text(
            258, 388,
            'q F<tspan baseline-shift="sub" font-size="68%">μν</tspan> '
            'u<tspan baseline-shift="super" font-size="68%">μ</tspan> → '
            'dp<tspan baseline-shift="super" font-size="68%">μ</tspan>/dτ',
            font_size=27, font_family=FONT, font_style="italic",
            fill=BLACK, text_anchor="middle",
        ))
    return _svg(node_id, "Lorentz force law", body, defs)


def create_8_5_charge_conservation(variant: str = "icon") -> str:
    """Charge conservation: local continuity of density and current."""
    node_id = "8.5"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=RED, size=6)]
    body: list[str] = []

    body.append(_rect(150, 142, 180, 180, rx=12, fill="#fff6f6",
                      stroke=BLACK, stroke_width=4))
    for x, y in [(196, 198), (238, 230), (276, 184), (230, 278)]:
        body.append(_circle(x, y, 10, fill=RED, stroke=BLACK, stroke_width=1.5))
    for x1, y1, x2, y2 in [(330, 204, 408, 184), (330, 264, 408, 294),
                           (182, 142, 154, 78), (150, 254, 78, 278)]:
        body.append(_line(x1, y1, x2, y2, stroke=RED, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(386, 232, "J", font_size=42, font_family=FONT,
                      font_style="italic", fill=RED))
    if variant == "detail":
        body.append(_text(
            240, 372,
            '∂<tspan baseline-shift="sub" font-size="68%">μ</tspan>'
            'J<tspan baseline-shift="super" font-size="68%">μ</tspan> = 0',
            font_size=34, font_family=FONT, font_style="italic",
            fill=BLACK, text_anchor="middle",
        ))
        body.append(_text(238, 130, "rho", font_size=30, font_family=FONT,
                          font_style="italic", fill=RED, text_anchor="middle"))
    return _svg(node_id, "Charge conservation", body, defs)


# ---------------------------------------------------------------------------
# Layer 9: Energy, Momentum, and Stress
# ---------------------------------------------------------------------------


def create_9_4_em_energy_density(variant: str = "icon") -> str:
    """Energy density of EM field: local stored energy in E and B."""
    node_id = "9.4"
    body: list[str] = []
    cells = [(188, 196, 90), (284, 196, 90), (188, 292, 90), (284, 292, 90)] if variant == "detail" else [(210, 190, 130)]
    for x, y, size in cells:
        body.append(_rect(x, y, size, size, rx=12, fill="#fff6df",
                          stroke=AMBER, stroke_width=3, opacity="0.92"))
        body.append(_line(x + 18, y + size * 0.42, x + size - 18, y + size * 0.42,
                          stroke=BLUE, stroke_width=6, stroke_linecap="round"))
        body.append(_path(f"M{x+24},{y+size*0.66} C{x+40},{y+size*0.48} {x+58},{y+size*0.84} {x+size-24},{y+size*0.64}",
                          fill="none", stroke=GREEN, stroke_width=5,
                          stroke_linecap="round"))
    if variant == "detail":
        body.append(_math_text(256, 416, "u", sub="EM", font_size=44,
                               font_family=FONT, font_style="italic",
                               fill=AMBER, text_anchor="middle"))
    else:
        body.append(_text(256, 372, "u", font_size=44, font_family=FONT,
                          font_style="italic", fill=AMBER,
                          text_anchor="middle"))
    body.append(_text(170, 164, "E", font_size=34, font_family=FONT,
                      font_style="italic", fill=BLUE))
    body.append(_text(332, 164, "B", font_size=34, font_family=FONT,
                      font_style="italic", fill=GREEN))
    return _svg(node_id, "Energy density of EM field", body)


def create_9_2_poynting_vector(variant: str = "icon") -> str:
    """Poynting vector: crossed E and B produce energy-momentum flow S."""
    node_id = "9.2"
    arrow_b = f"{_sid(node_id)}_blue"
    arrow_g = f"{_sid(node_id)}_green"
    arrow_a = f"{_sid(node_id)}_amber"
    defs = [
        _arrow_marker(arrow_b, colour=BLUE, size=6),
        _arrow_marker(arrow_g, colour=GREEN, size=6),
        _arrow_marker(arrow_a, colour=AMBER, size=7),
    ]
    body: list[str] = []
    positions = [(180, 260)] if variant != "detail" else [(132, 220), (230, 260), (328, 300)]
    for x, y in positions:
        body.append(_line(x, y + 54, x, y - 54, stroke=BLUE, stroke_width=7,
                          stroke_linecap="round", marker_end=f"url(#{arrow_b})"))
        body.append(_line(x - 54, y, x + 54, y, stroke=GREEN, stroke_width=7,
                          stroke_linecap="round", marker_end=f"url(#{arrow_g})"))
        body.append(_line(x + 12, y - 12, x + 112, y - 72, stroke=AMBER, stroke_width=9,
                          stroke_linecap="round", marker_end=f"url(#{arrow_a})"))
    body.append(_text(112, 162, "E", font_size=40, font_family=FONT,
                      font_style="italic", fill=BLUE))
    body.append(_text(210, 322, "B", font_size=40, font_family=FONT,
                      font_style="italic", fill=GREEN))
    body.append(_text(386, 176, "S", font_size=48, font_family=FONT,
                      font_style="italic", fill=AMBER))
    if variant == "detail":
        body.append(_text(258, 402, "E × B → S", font_size=34, font_family=FONT,
                          font_style="italic", fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Momentum density", body, defs)


def create_9_3_em_stress_energy(variant: str = "icon") -> str:
    """EM stress-energy: density, flux, and stress in one tensor block."""
    node_id = "9.3"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=AMBER, size=6)]
    body: list[str] = []
    body.append(_rect(166, 148, 180, 170, rx=12, fill="#f7f7f7",
                      stroke=BLACK, stroke_width=3))
    body.append(_math_text(256, 240, "T", sub="EM", font_size=42,
                           font_family=FONT, font_style="italic",
                           fill=BLACK, text_anchor="middle"))
    body.append(_line(190, 204, 322, 204, stroke=BLUE, stroke_width=5,
                      stroke_linecap="round"))
    body.append(_path("M202,250 C230,222 258,278 310,246", fill="none",
                      stroke=GREEN, stroke_width=5, stroke_linecap="round"))
    body.append(_line(346, 232, 424, 232, stroke=AMBER, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    if variant == "detail":
        for x1, y1, x2, y2 in [(166, 178, 112, 178), (346, 284, 408, 284),
                               (222, 148, 222, 94), (286, 318, 286, 380)]:
            body.append(_line(x1, y1, x2, y2, stroke=GREY, stroke_width=5,
                              stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.append(_text(390, 216, "S", font_size=32, font_family=FONT,
                          font_style="italic", fill=AMBER))
        body.append(_text(256, 360, "u + flux + stress", font_size=29,
                          font_family=FONT, fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Stress-energy of EM field", body, defs)


def create_9_1_energy_momentum_tensor(variant: str = "icon") -> str:
    """Energy-momentum tensor: local density and flux of energy-momentum."""
    node_id = "9.1"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=GREY, size=6)]
    body: list[str] = []
    if variant == "detail":
        body.append(_rect(80, 164, 144, 144, rx=12, fill="#f7f7f7",
                          stroke=BLACK, stroke_width=3))
        for x1, y1, x2, y2 in [(224, 204, 286, 184), (224, 264, 286, 292),
                               (136, 164, 116, 104), (80, 236, 34, 254)]:
            body.append(_line(x1, y1, x2, y2, stroke=GREY, stroke_width=5,
                              stroke_linecap="round", marker_end=f"url(#{arrow})"))
    x0, y0, cell = 286, 154, 58
    body.append(_rect(x0, y0, 2 * cell, 2 * cell, rx=8, fill="#f7f7f7",
                      stroke=BLACK, stroke_width=4))
    body.append(_rect(x0 + 8, y0 + 8, cell - 12, cell - 12, rx=5,
                      fill="#fff6df", stroke="none"))
    body.append(_rect(x0 + cell + 6, y0 + 8, cell - 12, cell - 12, rx=5,
                      fill="#edf3ff", stroke="none"))
    body.append(_rect(x0 + 8, y0 + cell + 6, cell - 12, cell - 12, rx=5,
                      fill="#edf3ff", stroke="none"))
    body.append(_line(x0 + cell, y0, x0 + cell, y0 + 2 * cell, stroke=LIGHT_GREY, stroke_width=3))
    body.append(_line(x0, y0 + cell, x0 + 2 * cell, y0 + cell, stroke=LIGHT_GREY, stroke_width=3))
    body.append(_math_text(x0 + cell, y0 + 2 * cell + 44, "T", sup="μν",
                           font_size=35, font_family=FONT, font_style="italic",
                           fill=BLACK, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(
            256, 390,
            '∂<tspan baseline-shift="sub" font-size="68%">μ</tspan>'
            'T<tspan baseline-shift="super" font-size="68%">μν</tspan> = 0',
            font_size=33, font_family=FONT, font_style="italic",
            fill=BLACK, text_anchor="middle",
        ))
    return _svg(node_id, "Energy-momentum tensor", body, defs)


# ---------------------------------------------------------------------------
# Layer 10: Waves and Radiation
# ---------------------------------------------------------------------------


def create_10_2_electromagnetic_waves(variant: str = "icon") -> str:
    """Electromagnetic waves: coupled E and B oscillations propagating at c."""
    node_id = "10.2"
    arrow = f"{_sid(node_id)}_arrow"
    e_arrow = f"{_sid(node_id)}_e_arrow"
    b_arrow = f"{_sid(node_id)}_b_arrow"
    defs = [
        _arrow_marker(arrow, colour=AMBER, size=7),
        _arrow_marker(e_arrow, colour=BLUE, size=5),
        _arrow_marker(b_arrow, colour=GREEN, size=5),
    ]
    body: list[str] = []

    axis_y = 256
    x0, x1 = 78, 432
    span = x1 - x0

    def phase(x: float) -> float:
        return radians((x - x0) / span * 720 - 18)

    def amp_at(x: float, amplitude: float) -> float:
        return amplitude * sin(phase(x))

    def x_for_phase(degrees: float) -> float:
        return x0 + ((degrees + 18) / 720) * span

    def wave_path(points: list[tuple[float, float]]) -> str:
        first_x, first_y = points[0]
        rest = " ".join(f"L{x:.1f},{y:.1f}" for x, y in points[1:])
        return f"M{first_x:.1f},{first_y:.1f} {rest}"

    samples = [x0 + i * span / 56 for i in range(57)]
    e_points = [(x, axis_y - amp_at(x, 72)) for x in samples]
    b_points = [
        (x + 0.78 * amp_at(x, 66), axis_y + 0.48 * amp_at(x, 66))
        for x in samples
    ]

    if variant == "detail":
        for x in [x0 + span * frac for frac in [0.18, 0.43, 0.68, 0.93]]:
            body.append(_line(x, axis_y - 92, x, axis_y + 78,
                              stroke=LIGHT_GREY, stroke_width=2.5,
                              stroke_dasharray="6 8", opacity="0.55"))

    body.append(_line(x0 - 12, axis_y, x1 + 6, axis_y, stroke=AMBER,
                      stroke_width=7, stroke_linecap="round",
                      marker_end=f"url(#{arrow})"))
    body.append(_text(x1 + 28, axis_y + 12, "c", font_size=40,
                      font_family=FONT, font_style="italic", fill=AMBER))

    body.append(_path(wave_path(b_points), fill="none", stroke=GREEN,
                      stroke_width=6, stroke_linecap="round",
                      stroke_linejoin="round", opacity="0.9"))
    body.append(_path(wave_path(e_points), fill="none", stroke=BLUE,
                      stroke_width=6.5, stroke_linecap="round",
                      stroke_linejoin="round"))

    vector_xs = (
        [x_for_phase(degrees) for degrees in [90, 270, 450, 630]]
        if variant == "detail" else
        [x_for_phase(degrees) for degrees in [90, 270, 450]]
    )
    for x in vector_xs:
        e_amp = amp_at(x, 72)
        b_amp = amp_at(x, 66)
        body.append(_line(x, axis_y, x, axis_y - e_amp,
                          stroke=BLUE, stroke_width=4.5,
                          stroke_linecap="round", marker_end=f"url(#{e_arrow})"))
        body.append(_line(x, axis_y, x + 0.78 * b_amp, axis_y + 0.48 * b_amp,
                          stroke=GREEN, stroke_width=4.5,
                          stroke_linecap="round", marker_end=f"url(#{b_arrow})"))

    body.append(_text(116, 162, "E", font_size=42, font_family=FONT,
                      font_style="italic", fill=BLUE))
    body.append(_text(96, 320, "B", font_size=42, font_family=FONT,
                      font_style="italic", fill=GREEN))
    if variant == "detail":
        body.append(_line(164, 390, 348, 390, stroke=AMBER, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.append(_text(256, 376, "S", font_size=34, font_family=FONT,
                          font_style="italic", fill=AMBER, text_anchor="middle"))
    return _svg(node_id, "Electromagnetic waves", body, defs)


def create_10_1_wave_equation(variant: str = "icon") -> str:
    """Wave equation: operator acting on A_mu produces propagating waves."""
    node_id = "10.1"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []
    body.append(_rect(78, 204, 112, 86, rx=12, fill="#f7f7f7",
                      stroke=BLACK, stroke_width=3))
    body.append(_math_text(134, 258, "□A", sub="μ", font_size=42,
                           font_family=FONT, font_style="italic",
                           fill=BLACK, text_anchor="middle"))
    if variant == "detail":
        body.append(_rect(92, 96, 84, 62, rx=12, fill="#ffeaea",
                          stroke=RED, stroke_width=3))
        body.append(_math_text(134, 136, "j", sub="μ", font_size=27,
                               font_family=FONT, font_style="italic",
                               fill=RED, text_anchor="middle"))
        body.append(_line(134, 164, 134, 198, stroke=RED, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_line(202, 246, 282, 246, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_path("M296,246 C330,200 364,292 398,246 C420,216 442,248 458,230",
                      fill="none", stroke=BLUE, stroke_width=7, stroke_linecap="round"))
    if variant == "detail":
        body.append(_text(142, 334, "operator", font_size=28, font_family=FONT,
                          fill=GREY, text_anchor="middle"))
        body.append(_text(372, 334, "wave", font_size=30, font_family=FONT,
                          fill=BLUE, text_anchor="middle"))
    return _svg(node_id, "Wave equation", body, defs)


def create_10_3_radiation_reaction(variant: str = "icon") -> str:
    """Radiation reaction: accelerating charge emits waves and recoils."""
    node_id = "10.3"
    wave_arrow = f"{_sid(node_id)}_wave"
    recoil_arrow = f"{_sid(node_id)}_recoil"
    defs = [
        _arrow_marker(wave_arrow, colour=AMBER, size=6),
        _arrow_marker(recoil_arrow, colour=RED, size=6),
    ]
    body: list[str] = []
    body.append(_path("M96,354 C150,250 216,314 256,208", fill="none",
                      stroke=BLACK, stroke_width=5, stroke_linecap="round"))
    body.append(_circle(194, 278, 24, fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_text(194, 288, "q", font_size=31, font_family=FONT,
                      font_style="italic", fill="white", text_anchor="middle"))
    body.append(_path("M178,240 C194,210 216,210 230,238", fill="none",
                      stroke=GREEN, stroke_width=5, stroke_linecap="round",
                      marker_end=f"url(#{wave_arrow})"))
    for r in [34, 58, 82]:
        body.append(_path(f"M250,{278-r} C318,{248-r} 356,{306+r} 294,{278+r}",
                          fill="none", stroke=BLUE, stroke_width=4,
                          stroke_linecap="round", opacity="0.82"))
    body.append(_line(182, 292, 118, 336, stroke=RED, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{recoil_arrow})"))
    body.append(_text(88, 350, "recoil", font_size=28, font_family=FONT,
                      fill=RED, text_anchor="middle"))
    if variant == "detail":
        body.append(_line(292, 254, 398, 212, stroke=AMBER, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{wave_arrow})"))
        body.append(_text(366, 202, "radiation", font_size=29, font_family=FONT,
                          fill=AMBER, text_anchor="middle"))
    return _svg(node_id, "Radiation reaction", body, defs)


# ---------------------------------------------------------------------------
# Layer 11: Symmetry Choices
# ---------------------------------------------------------------------------


def create_11_1_lorentz_invariance(variant: str = "icon") -> str:
    """Lorentz invariance: the same law in unprimed and primed frames."""
    node_id = "11.1"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    blue_marker = f"{_sid(node_id)}_blue"
    arrow = f"{_sid(node_id)}_arrow"
    defs.extend([
        _arrow_marker(blue_marker, colour=BLUE, size=5),
        _arrow_marker(arrow, colour=GREY, size=5),
    ])
    body: list[str] = []
    ox, oy = 82, 368
    body.extend(_draw_axes(ox, oy, 126, 132, axis_marker, x_label="x", y_label="ct",
                           stroke_width=4))
    body.append(_line(ox, oy, ox + 118, oy - 38, stroke=BLUE, stroke_width=4.5,
                      stroke_linecap="round", marker_end=f"url(#{blue_marker})"))
    body.append(_line(ox, oy, ox + 42, oy - 124, stroke=BLUE, stroke_width=4.5,
                      stroke_linecap="round", marker_end=f"url(#{blue_marker})"))
    body.append(_text(184, 326, "x′", font_size=27, font_family=FONT,
                      font_style="italic", fill=BLUE))
    body.append(_text(114, 226, "ct′", font_size=27, font_family=FONT,
                      font_style="italic", fill=BLUE))
    body.append(_line(220, 270, 306, 244, stroke=GREY, stroke_width=5,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.extend(_label_tile(320, 202, 120, 92, "law", fill="#f7f7f7",
                            stroke=BLACK, font_size=42))
    body.append(_circle(424, 214, 13, fill="none", stroke=GREEN, stroke_width=4))
    body.append(_line(416, 218, 424, 226, stroke=GREEN, stroke_width=4,
                      stroke_linecap="round"))
    body.append(_line(424, 226, 438, 206, stroke=GREEN, stroke_width=4,
                      stroke_linecap="round"))
    if variant == "detail":
        body.append(_text(380, 332, "invariant form", font_size=30,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
    return _svg(node_id, "Lorentz invariance", body, defs)


def create_11_2_gauge_fixing(variant: str = "icon") -> str:
    """Gauge fixing: choose one representative without changing F."""
    node_id = "11.2"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []
    for y, opacity in [(156, "0.35"), (214, "0.52"), (272, "0.35")]:
        body.append(_path(f"M70,{y} C130,{y-40} 172,{y+38} 228,{y-8}",
                          fill="none", stroke=BLUE, stroke_width=6,
                          stroke_linecap="round", opacity=opacity))
    if variant == "detail":
        body.extend(_label_tile(90, 348, 66, 54, "F", fill="#eef8f0",
                                stroke=GREEN, text_colour=GREEN, font_size=34))
        body.append(_text(
            150, 330,
            'same F<tspan baseline-shift="sub" font-size="68%">μν</tspan>',
            font_size=25, font_family=FONT, fill=GREEN,
            text_anchor="middle",
        ))
    body.append(_line(238, 218, 286, 218, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_path("M294,124 L362,166 L362,286 L294,328 Z", fill="#f7f7f7",
                      stroke=GREY, stroke_width=4))
    body.append(_text(330, 230, "gauge", font_size=27, font_family=FONT,
                      fill=GREY, text_anchor="middle"))
    body.append(_line(368, 218, 418, 218, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_path("M424,218 C454,184 486,212 468,252", fill="none",
                      stroke=BLUE, stroke_width=9, stroke_linecap="round"))
    body.append(_math_text(448, 292, "A", sub="μ", font_size=32,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))
    if variant == "detail":
        body.append(_text(332, 360, "chosen representative", font_size=27,
                          font_family=FONT, fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Gauge fixing", body, defs)


# ---------------------------------------------------------------------------
# Reusable mathematics for GR
# ---------------------------------------------------------------------------


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
    basis_body, basis_defs = _draw_tangent_basis(214, 192)
    body.extend(basis_body)
    defs.extend(basis_defs)
    body.append(_line(250, 300, 260, 236, stroke=GREY, stroke_width=3,
                      stroke_dasharray="6 7", opacity="0.68"))

    if variant == "detail":
        body.append(_math_text(346, 148, "T", sub="p", font_size=35,
                               font_family=FONT, font_style="italic",
                               fill=BLACK, text_anchor="middle"))
        body.append(_text(376, 148, "M", font_size=34, font_family=FONT,
                          font_style="italic", fill=BLACK))
    else:
        body.append(_math_text(340, 150, "T", sub="p", font_size=36,
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


# ---------------------------------------------------------------------------
# General Relativity seed concepts
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# GR Layer 9: Weak Field and Newtonian Limit
# ---------------------------------------------------------------------------


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
    body.append(_path("M54,154 C180,154 248,160 292,184 C340,210 386,224 454,224",
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
    body.append(_path("M76,256 C104,118 404,118 436,256 C404,394 104,394 76,256 Z",
                      fill="none", stroke=BLUE, stroke_width=7))
    body.append(_path("M102,154 C230,72 430,244 382,360 C254,442 54,270 102,154 Z",
                      fill="none", stroke=GREEN, stroke_width=6,
                      opacity="0.72"))
    body.append(_circle(76, 256, 14, fill=BLUE, stroke=BLACK, stroke_width=2))
    body.append(_circle(102, 154, 14, fill=GREEN, stroke=BLACK, stroke_width=2))
    body.append(_path("M92,242 A184,184 0 0 1 124,170", fill="none",
                      stroke=RED, stroke_width=7, marker_end=f"url(#{arrow})"))
    if variant == "detail":
        body.append(_line(256, 256, 76, 256, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="7 8"))
        body.append(_line(256, 256, 102, 154, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="7 8"))
        body.append(_text(142, 244, "Δϖ", font_size=34, font_family=FONT,
                          font_style="italic", fill=RED))
        body.append(_text(274, 274, "M", font_size=30, font_family=FONT,
                          font_style="italic", fill=BLACK))
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


# ---------------------------------------------------------------------------
# GR Layer 10: Schwarzschild Geometry and Black Holes
# ---------------------------------------------------------------------------


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
    body.append(_path("M82,112 L430,112 L330,414 L182,414 Z", fill="#e8ecf4",
                      stroke=BLACK, stroke_width=5, stroke_linejoin="round"))
    body.append(_line(82, 112, 430, 112, stroke=BLUE, stroke_width=10))
    for x in [126, 196, 266, 336, 406]:
        body.append(_path(f"M{x},128 C{x},220 {256 + (x-256)*0.28},302 256,386",
                          fill="none", stroke=RED, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{inward})"))
    body.append(_path("M256,362 L270,390 L302,394 L278,416 L284,448 L256,432 L228,448 L234,416 L210,394 L242,390 Z",
                      fill=RED, stroke=BLACK, stroke_width=3))
    body.append(_text(286, 444, "r = 0", font_size=32, font_family=FONT,
                      font_style="italic", fill=RED))
    if variant == "detail":
        body.append(_text(256, 78, "horizon", font_size=28, font_family=FONT,
                          fill=BLUE, text_anchor="middle"))
        body.append(_text(380, 330, "K → ∞", font_size=34, font_family=FONT,
                          font_style="italic", fill=RED, text_anchor="middle"))
    return _svg(node_id, "Black hole singularity", body, defs)


def create_gr_10_6_effective_potential_orbits(variant: str = "icon") -> str:
    """Effective potential: orbital turning points and circular extrema."""
    node_id = "GR 10.6"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)
    body: list[str] = []
    ox, oy = 78, 414
    body.extend(_draw_axes(ox, oy, 360, 322, axis_marker,
                           x_label="r", y_label="V", stroke_width=5.5))
    body.append(_path("M92,122 C128,146 160,332 224,306 C282,282 326,158 424,224",
                      fill="none", stroke=BLUE, stroke_width=9,
                      stroke_linecap="round"))
    body.append(_line(90, 250, 426, 250, stroke=AMBER, stroke_width=4,
                      stroke_dasharray="10 9"))
    body.append(_circle(176, 250, 14, fill=AMBER, stroke=BLACK, stroke_width=2))
    body.append(_circle(392, 250, 14, fill=AMBER, stroke=BLACK, stroke_width=2))
    body.append(_circle(226, 306, 17, fill=GREEN, stroke=BLACK, stroke_width=3))
    if variant == "detail":
        body.append(_circle(324, 177, 17, fill=RED, stroke=BLACK, stroke_width=3))
        body.append(_text(226, 344, "stable", font_size=25, font_family=FONT,
                          fill=GREEN, text_anchor="middle"))
        body.append(_text(350, 156, "unstable", font_size=25, font_family=FONT,
                          fill=RED, text_anchor="middle"))
        body.append(_text(294, 238, "E", font_size=29, font_family=FONT,
                          font_style="italic", fill=AMBER))
    return _svg(node_id, "Effective potential for orbits", body, defs)


# ---------------------------------------------------------------------------
# GR Layer 7: Matter, Stress-Energy, and Conservation
# ---------------------------------------------------------------------------


def create_gr_7_1_stress_energy_tensor(variant: str = "icon") -> str:
    """Stress-energy in GR: density, flux, and stress in one tensor."""
    node_id = "GR 7.1"
    arrow = f"{_sid(node_id)}_flux"
    defs = [_arrow_marker(arrow, colour=AMBER, size=6)]
    body: list[str] = []
    body.append(_rect(122, 126, 268, 258, rx=22, fill="#f4f7fc",
                      stroke=BLACK, stroke_width=5))
    body.extend(_paren_matrix(194, 180, [["ρ", "S"], ["S", "σ"]],
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
    """Perfect fluid: density carried by U with isotropic pressure."""
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
    body.append(_math_text(344, 112, "U", sup="μ", font_size=40,
                           font_family=FONT, font_style="italic", fill=GREEN))
    if variant == "detail":
        body.append(_text(256, 468, "same pressure in every direction",
                          font_size=26, font_family=FONT, fill=BLUE,
                          text_anchor="middle"))
        body.append(_text(210, 246, "ρ", font_size=36, font_family=FONT,
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
                           x_label="ρ", y_label="p", stroke_width=6))
    body.append(_path("M112,378 C176,342 238,290 294,226 C334,180 370,150 410,126",
                      fill="none", stroke=BLUE, stroke_width=10,
                      stroke_linecap="round"))
    body.append(_circle(282, 240, 16, fill=AMBER, stroke=BLACK, stroke_width=2))
    body.append(_text(326, 206, "p(ρ)", font_size=40, font_family=FONT,
                      font_style="italic", fill=BLUE))
    if variant == "detail":
        body.append(_line(112, 378, 410, 126, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="9 8"))
        body.append(_text(220, 316, "p = wρ", font_size=32, font_family=FONT,
                          font_style="italic", fill=GREY))
        body.append(_text(256, 464, "closes the matter model", font_size=27,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
    return _svg(node_id, "Equation of state", body, defs)


# ---------------------------------------------------------------------------
# GR Layer 8: Einstein Field Equations
# ---------------------------------------------------------------------------


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
    body.extend(_paren_matrix(342, 194, [["ρ", "S"], ["S", "σ"]],
                              col_gap=66, row_gap=80, font_size=33))
    if variant == "detail":
        body.append(_text(138, 416, "geometry", font_size=28,
                          font_family=FONT, fill=BLUE, text_anchor="middle"))
        body.append(_text(376, 416, "stress–energy", font_size=28,
                          font_family=FONT, fill=AMBER, text_anchor="middle"))
        body.append(_text(256, 92, "G + Λg = κT", font_size=38,
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
        body.append(_text(256, 64, "uniform vacuum term", font_size=27,
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
        body.append(_text(144, 348, "∫(R−2Λ)√−g", font_size=28,
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
        body.append(_text(256, 112, "same equation • Ricci form",
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
        body.append(_text(256, 458, "vacuum need not be flat", font_size=28,
                          font_family=FONT, fill=RED, text_anchor="middle"))
    return _svg(node_id, "Vacuum field equations", body)


# ---------------------------------------------------------------------------
# Maths and GR Layer 2: Tensor Calculus on Spacetime
# ---------------------------------------------------------------------------


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


# GR Layer 3: Metric Geometry

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

# GR Layer 4: Connections and Covariant Derivatives
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

# GR Layer 5: Geodesics and Free Fall
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

# GR Layer 6: Curvature
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


__all__ = [
    'create_1_3_principle_of_relativity',
    'create_1_2_constancy_of_speed_of_light',
    'create_1_1_inertial_frames',
    'create_2_2_spacetime_event',
    'create_2_3_principle_of_locality',
    'create_3_3_lorentz_transformations',
    'create_3_2_spacetime_interval',
    'create_3_1_metric_tensor',
    'create_3_4_light_cone',
    'create_3_5_minkowski_diagram',
    'create_4_1_proper_time',
    'create_4_2_four_vectors',
    'create_4_3_position_four_vector',
    'create_4_4_velocity_four_vector',
    'create_4_5_momentum_four_vector',
    'create_4_6_mass_energy_equivalence',
    'create_5_2_action_principle',
    'create_5_1_lagrangian',
    'create_5_3_euler_lagrange',
    'create_5_5_hamiltonian_formalism',
    'create_5_4_canonical_momentum',
    'create_5_6_noethers_theorem',
    'create_6_1_scalar_field',
    'create_6_2_vector_field',
    'create_6_3_field_lagrangian',
    'create_6_4_field_equations',
    'create_7_1_vector_potential',
    'create_7_2_field_tensor',
    'create_7_3_electric_field',
    'create_7_4_magnetic_field',
    'create_7_5_electromagnetic_field',
    'create_7_7_maxwells_equations',
    'create_8_6_lorenz_gauge',
    'create_8_1_gauge_invariance',
    'create_7_6_four_current',
    'create_8_3_minimal_coupling',
    'create_8_4_lorentz_force_law',
    'create_8_5_charge_conservation',
    'create_9_4_em_energy_density',
    'create_9_2_poynting_vector',
    'create_9_3_em_stress_energy',
    'create_9_1_energy_momentum_tensor',
    'create_10_2_electromagnetic_waves',
    'create_10_1_wave_equation',
    'create_10_3_radiation_reaction',
    'create_11_1_lorentz_invariance',
    'create_11_2_gauge_fixing',
    'create_m_1_1_manifold',
    'create_m_1_2_coordinate_chart',
    'create_m_1_3_coordinate_transformation',
    'create_m_1_4_worldline',
    'create_m_1_5_tangent_space',
    'create_m_1_6_cotangent_space',
    'create_m_2_1_tensor_field',
    'create_gr_1_1_gravity_as_geometry',
    'create_gr_1_2_equivalence_principle',
    'create_gr_1_3_local_inertial_frame',
    'create_gr_1_4_freely_falling_observer',
    'create_gr_1_5_tidal_gravity',
]
