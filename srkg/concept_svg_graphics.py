"""
KG SVG graphics for Special Relativity / Classical Field Theory.

This module generates simple, deterministic SVG diagrams for selected
knowledge-graph nodes.  It currently covers layers 1 through 11.

Public entry point:
    createSvgGraphic(node_id, variant="icon") -> str | None

The return value is an SVG XML string.  Unknown node ids return None.

Design principles:
- Square 512 x 512 SVG viewBox.
- Transparent background by default; the viewer can provide the node fill,
  layer-colour outline, or detail-panel background.
- Clean, flat, textbook-style vector graphics.
- Strong silhouette at icon size, with modest extra detail at panel size.
- No dependencies beyond the Python standard library.
"""

from __future__ import annotations

from math import cos, sin, radians
from pathlib import Path
from typing import Callable

SIZE = 512
CX = SIZE / 2
CY = SIZE / 2

# House palette.  Keep this small so the whole icon set looks coherent.
BLACK = "#222222"
GREY = "#555555"
LIGHT_GREY = "#c8c8c8"
VERY_LIGHT_GREY = "#eeeeee"
BLUE = "#1f4fbf"
RED = "#d22f2f"
GREEN = "#248a3d"
AMBER = "#c78a00"

FONT = "STIX Two Math, Cambria Math, Times New Roman, serif"


def _sid(node_id: str) -> str:
    """Return a safe SVG id prefix for this node."""
    return "n" + node_id.replace(".", "_").replace("-", "_")


def _attrs(**kwargs: object) -> str:
    """Convert Python keyword attributes to SVG/XML attributes."""
    out = []
    for key, value in kwargs.items():
        if value is None:
            continue
        key = key.replace("_", "-")
        out.append(f'{key}="{value}"')
    return " ".join(out)


def _line(x1: float, y1: float, x2: float, y2: float, **kwargs: object) -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {_attrs(**kwargs)}/>'


def _circle(cx: float, cy: float, r: float, **kwargs: object) -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" {_attrs(**kwargs)}/>'


def _rect(x: float, y: float, width: float, height: float, rx: float = 0, **kwargs: object) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="{rx:.1f}" {_attrs(**kwargs)}/>'


def _path(d: str, **kwargs: object) -> str:
    return f'<path d="{d}" {_attrs(**kwargs)}/>'


def _polyline(points: list[tuple[float, float]], **kwargs: object) -> str:
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{coords}" {_attrs(**kwargs)}/>'


def _polygon(points: list[tuple[float, float]], **kwargs: object) -> str:
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{coords}" {_attrs(**kwargs)}/>'


def _text(x: float, y: float, text: str, **kwargs: object) -> str:
    # Text content is intentionally restricted to short controlled labels.
    return f'<text x="{x:.1f}" y="{y:.1f}" {_attrs(**kwargs)}>{text}</text>'


def _math_text(
    x: float,
    y: float,
    base: str,
    *,
    sub: str | None = None,
    sup: str | None = None,
    **kwargs: object,
) -> str:
    """Draw a short math label with real SVG sub/superscript placement."""
    parts = [base]
    if sub:
        parts.append(f'<tspan baseline-shift="sub" font-size="68%">{sub}</tspan>')
    if sup:
        parts.append(f'<tspan baseline-shift="super" font-size="68%">{sup}</tspan>')
    return f'<text x="{x:.1f}" y="{y:.1f}" {_attrs(**kwargs)}>{"".join(parts)}</text>'


def _arrow_marker(marker_id: str, colour: str = BLACK, size: int = 8) -> str:
    """Filled triangular arrow marker."""
    return f'''
<marker id="{marker_id}" markerWidth="{size}" markerHeight="{size}"
        refX="{size - 2}" refY="{size / 2:.1f}" orient="auto"
        markerUnits="strokeWidth">
  <path d="M0,0 L{size - 2},{size / 2:.1f} L0,{size} Z" fill="{colour}"/>
</marker>'''


def _dot_marker(marker_id: str, colour: str = RED, radius: int = 4) -> str:
    return f'''
<marker id="{marker_id}" markerWidth="{2 * radius}" markerHeight="{2 * radius}"
        refX="{radius}" refY="{radius}" orient="auto">
  <circle cx="{radius}" cy="{radius}" r="{radius}" fill="{colour}"/>
</marker>'''


def _svg(node_id: str, title: str, body: list[str], defs: list[str] | None = None) -> str:
    """Wrap SVG body elements in a complete SVG document."""
    defs = defs or []
    defs_block = f"<defs>\n{''.join(defs)}\n</defs>" if defs else ""
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}" role="img" aria-labelledby="title-{_sid(node_id)}">',
            f'<title id="title-{_sid(node_id)}">{title}</title>',
            defs_block,
            *body,
            "</svg>",
        ]
    )


def _axis_arrow_defs(node_id: str, colour: str = BLACK) -> tuple[str, list[str]]:
    marker_id = f"{_sid(node_id)}_axis_arrow"
    return marker_id, [_arrow_marker(marker_id, colour=colour, size=6)]


def _draw_axes(
    ox: float,
    oy: float,
    x_len: float,
    y_len: float,
    marker_id: str,
    x_label: str = "x",
    y_label: str = "y",
    colour: str = BLACK,
    stroke_width: float = 4,
) -> list[str]:
    """Draw 2D coordinate axes with arrowheads."""
    return [
        _line(ox, oy, ox + x_len, oy, stroke=colour, stroke_width=stroke_width,
              stroke_linecap="round", marker_end=f"url(#{marker_id})"),
        _line(ox, oy, ox, oy - y_len, stroke=colour, stroke_width=stroke_width,
              stroke_linecap="round", marker_end=f"url(#{marker_id})"),
        _text(ox + x_len + 18, oy + 10, x_label, font_size=36,
              font_family=FONT, font_style="italic", fill=colour),
        _text(ox - 16, oy - y_len - 18, y_label, font_size=36,
              font_family=FONT, font_style="italic", fill=colour),
    ]


def _draw_grid(x0: float, y0: float, width: float, height: float, step: float, colour: str = VERY_LIGHT_GREY) -> list[str]:
    """Draw a light rectangular grid."""
    body: list[str] = []
    x = x0 + step
    while x < x0 + width:
        body.append(_line(x, y0, x, y0 + height, stroke=colour, stroke_width=2))
        x += step
    y = y0 + step
    while y < y0 + height:
        body.append(_line(x0, y, x0 + width, y, stroke=colour, stroke_width=2))
        y += step
    return body


def _tick(x: float, y: float, angle_degrees: float, length: float, **kwargs: object) -> str:
    """Draw a small tick centred at a point and rotated by angle."""
    a = radians(angle_degrees)
    dx = 0.5 * length * cos(a)
    dy = 0.5 * length * sin(a)
    return _line(x - dx, y - dy, x + dx, y + dy, **kwargs)


def _label_tile(
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    *,
    fill: str = "#f7f7f7",
    stroke: str = BLACK,
    text_colour: str = BLACK,
    font_size: float = 36,
    rx: float = 12,
) -> list[str]:
    """Draw a labelled rounded tile."""
    return [
        _rect(x, y, width, height, rx=rx, fill=fill, stroke=stroke, stroke_width=3),
        _text(x + width / 2, y + height / 2 + font_size * 0.34, label,
              font_size=font_size, font_family=FONT, font_style="italic",
              fill=text_colour, text_anchor="middle"),
    ]


def _paren_column(
    x: float,
    y: float,
    rows: list[str],
    *,
    row_gap: float = 34,
    font_size: float = 25,
    colour: str = BLACK,
) -> list[str]:
    """Draw a compact column vector with round parentheses."""
    height = row_gap * (len(rows) - 1) + font_size
    mid_y = y + height / 2 - font_size * 0.35
    body = [
        _path(f"M{x - 22},{y - 18} C{x - 42},{mid_y - 34} {x - 42},{mid_y + 34} {x - 22},{y + height - 6}",
              fill="none", stroke=BLACK, stroke_width=3.2, stroke_linecap="round"),
        _path(f"M{x + 72},{y - 18} C{x + 92},{mid_y - 34} {x + 92},{mid_y + 34} {x + 72},{y + height - 6}",
              fill="none", stroke=BLACK, stroke_width=3.2, stroke_linecap="round"),
    ]
    for idx, row in enumerate(rows):
        body.append(_text(x + 25, y + idx * row_gap + font_size * 0.35, row,
                          font_size=font_size, font_family=FONT,
                          font_style="italic", fill=colour,
                          text_anchor="middle"))
    return body


def _paren_matrix(
    x: float,
    y: float,
    rows: list[list[str]],
    *,
    col_gap: float = 50,
    row_gap: float = 42,
    font_size: float = 25,
) -> list[str]:
    """Draw a compact matrix with round parentheses and no table grid."""
    cols = max(len(row) for row in rows)
    width = col_gap * (cols - 1)
    height = row_gap * (len(rows) - 1) + font_size
    mid_y = y + height / 2 - font_size * 0.35
    body = [
        _path(f"M{x - 30},{y - 20} C{x - 54},{mid_y - 54} {x - 54},{mid_y + 54} {x - 30},{y + height - 6}",
              fill="none", stroke=BLACK, stroke_width=3.2, stroke_linecap="round"),
        _path(f"M{x + width + 30},{y - 20} C{x + width + 54},{mid_y - 54} {x + width + 54},{mid_y + 54} {x + width + 30},{y + height - 6}",
              fill="none", stroke=BLACK, stroke_width=3.2, stroke_linecap="round"),
    ]
    for r_idx, row in enumerate(rows):
        for c_idx, text in enumerate(row):
            colour = BLUE if r_idx == c_idx == 0 else GREY if r_idx == c_idx else LIGHT_GREY
            body.append(_text(x + c_idx * col_gap, y + r_idx * row_gap + font_size * 0.35,
                              text, font_size=font_size, font_family=FONT,
                              fill=colour, text_anchor="middle",
                              font_weight=700 if r_idx == c_idx else 400))
    return body


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

    body.append(_line(168, 176, 344, 176, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{v_marker})"))
    body.append(_text(256, 148, "v", font_size=46, font_family=FONT,
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
        body.append(_line(px, py, px - 86, py + 50, stroke=LIGHT_GREY, stroke_width=3,
                          stroke_dasharray="7 8", stroke_linecap="round"))
        body.append(_line(px, py, px - 54, py - 88, stroke=LIGHT_GREY, stroke_width=3,
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

    Icon design: Simplify the detailed diagram to an eta tile applied to x/ct
    axes, with one blue time-like mark and one grey space-like mark.

    Detail design: Show an actual compact 4x4 diagonal Minkowski metric matrix
    labelled eta_mu_nu, with +1 in the time slot and -1 entries in the three
    spatial slots. Pair it with a small spacetime-axis inset showing time-like
    and space-like components measured by the matrix.
    """
    node_id = "3.1"
    axis_marker, defs = _axis_arrow_defs(node_id, BLACK)

    body: list[str] = []
    if variant != "detail":
        ox, oy = 128, 382
        body.extend(_draw_axes(ox, oy, 284, 276, axis_marker, x_label="x", y_label="ct", stroke_width=5.5))
        body.append(_line(ox, oy - 26, ox, oy - 146, stroke=BLUE, stroke_width=11,
                          stroke_linecap="round"))
        body.append(_line(ox + 34, oy, ox + 166, oy, stroke=GREY, stroke_width=11,
                          stroke_linecap="round"))
        body.append(_rect(300, 176, 100, 100, rx=12, fill="#f7f7f7",
                          stroke=BLACK, stroke_width=4))
        body.append(_text(350, 242, "η", font_size=70, font_family=FONT,
                          font_style="italic", fill=BLACK, text_anchor="middle"))
        return _svg(node_id, "Metric tensor", body, defs)

    # Detail panel: matrix first, with a small geometric inset.
    body.append(_math_text(254, 70, "η", sub="μν", font_size=34,
                           font_family=FONT, font_style="italic",
                           fill=BLACK, text_anchor="middle"))
    x0, y0 = 206, 118
    entries = [
        ["+1", "0", "0", "0"],
        ["0", "−1", "0", "0"],
        ["0", "0", "−1", "0"],
        ["0", "0", "0", "−1"],
    ]
    body.extend(_paren_matrix(x0, y0, entries, col_gap=48, row_gap=42, font_size=26))

    # Small spacetime-axis inset: the matrix is a measuring rule, not just a table.
    inset_marker = axis_marker
    ox, oy = 104, 444
    body.extend(_draw_axes(ox, oy, 132, 84, inset_marker, x_label="x", y_label="ct",
                           colour=BLACK, stroke_width=3.8))
    body.append(_line(ox, oy - 10, ox, oy - 62, stroke=BLUE, stroke_width=8,
                      stroke_linecap="round"))
    body.append(_line(ox + 18, oy, ox + 96, oy, stroke=GREY, stroke_width=8,
                      stroke_linecap="round"))
    body.append(_text(104, 390, "+1", font_size=30, font_family=FONT,
                      fill=BLUE, font_weight=700))
    body.append(_text(218, 466, "−1", font_size=30, font_family=FONT,
                      fill=GREY, font_weight=700))

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
    bx, by = 340, 130
    worldline = "M142,352 C174,286 258,286 340,130"

    if variant == "detail":
        body.extend(_draw_grid(ox, 112, 318, 292, 53))
    body.extend(_draw_axes(ox, oy, 330, 302, axis_marker, x_label="x", y_label="ct",
                           stroke_width=5.5))
    if variant == "detail":
        body.append(_line(bx, by, bx, oy, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="8 9", stroke_linecap="round"))
        body.append(_text(bx + 18, oy - 10, "t", font_size=34, font_family=FONT,
                          font_style="italic", fill=GREY))
        body.append(_path("M142,352 C210,214 284,336 340,130", fill="none",
                          stroke=LIGHT_GREY, stroke_width=4, stroke_dasharray="9 9",
                          stroke_linecap="round"))

    body.append(_path(worldline, fill="none", stroke=BLACK, stroke_width=8,
                      stroke_linecap="round"))
    for x, y, angle in [(178, 298, 28), (224, 272, 38), (270, 232, 48), (308, 174, 54)]:
        body.append(_tick(x, y, angle, 34, stroke=BLUE, stroke_width=5,
                          stroke_linecap="round"))
    body.append(_circle(ax, ay, 17, fill=RED, stroke=BLACK, stroke_width=2.5))
    body.append(_circle(bx, by, 17, fill=RED, stroke=BLACK, stroke_width=2.5))
    body.append(_text(ax - 42, ay + 8, "A", font_size=38, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(bx + 22, by - 8, "B", font_size=38, font_family=FONT,
                      font_style="italic", fill=RED))
    body.append(_text(242, 246, "τ", font_size=48, font_family=FONT,
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
    body.append(_math_text(224, 292, "A", sup="μ", font_size=38,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))

    rows = ["A⁰", "A¹", "A²", "A³"] if variant == "detail" else ["•", "•", "•", "•"]
    body.extend(_paren_column(362, 154, rows, row_gap=34, font_size=24, colour=GREY))
    if variant == "detail":
        body.extend(_label_tile(358, 326, 68, 58, "η", fill="#f7f7f7",
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
    body.append(_path("M132,366 C184,324 176,244 244,246 C314,248 306,156 386,118",
                      fill="none", stroke=BLACK, stroke_width=7,
                      stroke_linecap="round"))
    if variant == "detail":
        body.append(_tick(210, 270, -34, 32, stroke=BLUE, stroke_width=4.5,
                          stroke_linecap="round"))
        body.append(_tick(286, 214, -34, 32, stroke=BLUE, stroke_width=4.5,
                          stroke_linecap="round"))
        body.append(_text(178, 286, "τ", font_size=29, font_family=FONT,
                          font_style="italic", fill=BLUE))
        body.append(_text(306, 204, "τ+dτ", font_size=27, font_family=FONT,
                          font_style="italic", fill=BLUE))
        body.append(_line(210, 270, 286, 214, stroke=LIGHT_GREY, stroke_width=4,
                          stroke_dasharray="7 7", stroke_linecap="round"))
        body.append(_text(322, 182, "dx^μ", font_size=27, font_family=FONT,
                          font_style="italic", fill=GREY))
    body.append(_circle(ex, ey, 18, fill=RED, stroke=BLACK, stroke_width=2.5))
    body.append(_line(ex, ey, ex + 104, ey - 88, stroke=GREEN, stroke_width=9,
                      stroke_linecap="round", marker_end=f"url(#{u_marker})"))
    body.append(_math_text(ex + 130, ey - 92, "u", sup="μ", font_size=38,
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
    body.append(_math_text(208, 264, "p", sup="μ", font_size=40,
                           font_family=FONT, font_style="italic",
                           fill=BLUE, text_anchor="middle"))

    body.append(_rect(348, 174, 92, 116, rx=12, fill="#f7f7f7",
                      stroke=BLACK, stroke_width=3))
    body.append(_line(348, 232, 440, 232, stroke=LIGHT_GREY, stroke_width=2))
    body.append(_text(394, 216, "E/c", font_size=30, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))
    body.append(_text(394, 270, "p", font_size=34, font_family=FONT,
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
    if variant == "detail":
        body.append(_tick(226, 252, -32, 30, stroke=GREEN, stroke_width=5,
                          stroke_linecap="round"))
        body.append(_tick(310, 204, -32, 30, stroke=GREEN, stroke_width=5,
                          stroke_linecap="round"))
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
        body.append(_text(154, 288, "qdot", font_size=28, font_family=FONT,
                          font_style="italic", fill=AMBER, text_anchor="middle"))
        body.extend(_label_tile(312, 164, 64, 60, "L", fill="#edf3ff",
                                stroke=BLUE, text_colour=BLUE, font_size=38))
        body.append(_line(340, 232, 340, 282, stroke=BLUE, stroke_width=5,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.extend(_label_tile(304, 270, 126, 54, "∂L/∂q̇", fill="#f7f7f7",
                                stroke=GREY, font_size=25))
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
    body.append(_path("M104,196 C78,144 158,104 196,156 C214,184 210,198 196,198",
                      fill="none", stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    if variant == "detail":
        body.append(_text(140, 324, "unchanged", font_size=30, font_family=FONT,
                          fill=BLUE, text_anchor="middle"))
    body.append(_line(204, 248, 306, 248, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
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

    cells = [(112, 286), (164, 234), (216, 286)] if variant != "detail" else [
        (112, 286), (164, 234), (216, 286), (216, 182), (268, 234)
    ]
    for x, y in cells:
        body.extend(_label_tile(x - 24, y - 24, 48, 48, "L",
                                fill="#edf3ff", stroke=BLUE,
                                text_colour=BLUE, font_size=28, rx=8))
    if variant == "detail":
        body.append(_text(206, 390, "d⁴x", font_size=31, font_family=FONT,
                          font_style="italic", fill=GREY, text_anchor="middle"))
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
        body.append(_text(256, 334, "∂μ Aμ = 0", font_size=34,
                          font_family=FONT, font_style="italic",
                          fill=BLACK, text_anchor="middle"))
        body.extend(_label_tile(82, 378, 58, 50, "F", fill="#eef8f0",
                                stroke=GREEN, text_colour=GREEN, font_size=32))
        body.extend(_label_tile(410, 378, 58, 50, "F", fill="#eef8f0",
                                stroke=GREEN, text_colour=GREEN, font_size=32))
        body.append(_line(144, 404, 406, 404, stroke=GREEN, stroke_width=3,
                          stroke_dasharray="9 8", opacity="0.55"))
    else:
        body.append(_text(256, 382, "∂·A = 0", font_size=36,
                          font_family=FONT, font_style="italic",
                          fill=BLACK, text_anchor="middle"))
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
        body.append(_text(154, 356, "Aμ + ∂μΛ", font_size=28, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))
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
        body.append(_text(394, 326, "same Fμν", font_size=28, font_family=FONT,
                          fill=GREEN, text_anchor="middle"))
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

    body.extend(_label_tile(324, 162, 112, 160, "Jμ", fill="#ffeaea",
                            stroke=RED, text_colour=RED, font_size=38))
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
        body.append(_text(242, 338, "pμ - eAμ", font_size=32,
                          font_family=FONT, font_style="italic", fill=BLACK,
                          text_anchor="middle"))
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
        body.append(_text(258, 388, "q Fμν u^μ → dp^μ/dτ", font_size=27,
                          font_family=FONT, font_style="italic", fill=BLACK,
                          text_anchor="middle"))
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
        body.append(_text(240, 372, "∂μJ^μ = 0", font_size=34,
                          font_family=FONT, font_style="italic", fill=BLACK,
                          text_anchor="middle"))
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
    body.append(_text(256, 372 if variant != "detail" else 416, "u_EM" if variant == "detail" else "u",
                      font_size=44, font_family=FONT, font_style="italic",
                      fill=AMBER, text_anchor="middle"))
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
        body.append(_text(258, 402, "E x B → S", font_size=34, font_family=FONT,
                          font_style="italic", fill=BLACK, text_anchor="middle"))
    return _svg(node_id, "Momentum density", body, defs)


def create_9_3_em_stress_energy(variant: str = "icon") -> str:
    """EM stress-energy: density, flux, and stress in one tensor block."""
    node_id = "9.3"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=AMBER, size=6)]
    body: list[str] = []
    body.extend(_label_tile(166, 148, 180, 170, "T_EM", fill="#f7f7f7",
                            stroke=BLACK, font_size=42))
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
        body.append(_text(256, 390, "∂μT^μν = 0", font_size=33,
                          font_family=FONT, font_style="italic", fill=BLACK,
                          text_anchor="middle"))
    return _svg(node_id, "Energy-momentum tensor", body, defs)


# ---------------------------------------------------------------------------
# Layer 10: Waves and Radiation
# ---------------------------------------------------------------------------


def create_10_2_electromagnetic_waves(variant: str = "icon") -> str:
    """Electromagnetic waves: coupled E and B oscillations propagating at c."""
    node_id = "10.2"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=AMBER, size=7)]
    body: list[str] = []
    body.append(_path("M70,230 C110,170 150,290 190,230 C230,170 270,290 310,230 C350,170 390,290 430,230",
                      fill="none", stroke=BLUE, stroke_width=7, stroke_linecap="round"))
    body.append(_path("M70,292 C110,352 150,232 190,292 C230,352 270,232 310,292 C350,352 390,232 430,292",
                      fill="none", stroke=GREEN, stroke_width=7, stroke_linecap="round"))
    body.append(_line(104, 128, 408, 128, stroke=AMBER, stroke_width=8,
                      stroke_linecap="round", marker_end=f"url(#{arrow})"))
    body.append(_text(256, 106, "c", font_size=42, font_family=FONT,
                      font_style="italic", fill=AMBER, text_anchor="middle"))
    body.append(_text(86, 204, "E", font_size=40, font_family=FONT,
                      font_style="italic", fill=BLUE))
    body.append(_text(86, 346, "B", font_size=40, font_family=FONT,
                      font_style="italic", fill=GREEN))
    if variant == "detail":
        for x in [150, 250, 350]:
            body.append(_line(x, 172, x, 350, stroke=LIGHT_GREY, stroke_width=3,
                              stroke_dasharray="7 8"))
        body.append(_line(154, 386, 354, 386, stroke=AMBER, stroke_width=6,
                          stroke_linecap="round", marker_end=f"url(#{arrow})"))
        body.append(_text(256, 374, "S", font_size=34, font_family=FONT,
                          font_style="italic", fill=AMBER, text_anchor="middle"))
    return _svg(node_id, "Electromagnetic waves", body, defs)


def create_10_1_wave_equation(variant: str = "icon") -> str:
    """Wave equation: operator acting on A_mu produces propagating waves."""
    node_id = "10.1"
    arrow = f"{_sid(node_id)}_arrow"
    defs = [_arrow_marker(arrow, colour=BLUE, size=6)]
    body: list[str] = []
    body.extend(_label_tile(78, 204, 112, 86, "□A", fill="#f7f7f7",
                            stroke=BLACK, font_size=42))
    if variant == "detail":
        body.extend(_label_tile(92, 96, 84, 62, "Jμ", fill="#ffeaea",
                                stroke=RED, text_colour=RED, font_size=27))
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
        body.append(_text(150, 330, "same Fμν", font_size=25,
                          font_family=FONT, fill=GREEN, text_anchor="middle"))
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
# Public API
# ---------------------------------------------------------------------------


def createSvgGraphic(node_id: str, variant: str = "icon") -> str | None:
    """
    Return an SVG XML string for a KG node id and variant, or None if this
    module does not yet provide a graphic for that node.

    ``variant`` can be "icon" or "detail". Icons keep a strong small-scale
    silhouette for graph nodes; details include more instructional structure
    for the side panel.

    Currently implemented:
        1.1  Inertial frames
        1.2  Constancy of the speed of light
        1.3  Principle of relativity
        2.2  Spacetime event
        2.3  Principle of locality
        3.1  Metric tensor
        3.2  Spacetime interval
        3.3  Lorentz transformations
        3.4  Light cone
        3.5  Minkowski diagram
        4.1  Proper time
        4.2  Four-vectors
        4.3  Position four-vector
        4.4  Velocity four-vector
        4.5  Momentum four-vector
        4.6  Mass-energy equivalence
        5.1  Lagrangian
        5.2  Action principle
        5.3  Euler-Lagrange equations
        5.4  Canonical momentum
        5.5  Hamiltonian formalism
        5.6  Noether's theorem
        6.1  Scalar field
        6.2  Vector field
        6.3  Field Lagrangian
        6.4  Field equations
        7.1  Vector potential
        7.2  Field tensor
        7.3  Electric field
        7.4  Magnetic field
        7.5  Electromagnetic field
        7.6  Four-current
        7.7  Maxwell's equations
        8.1  Gauge invariance
        8.3  Minimal coupling
        8.4  Lorentz force law
        8.5  Charge conservation
        8.6  Lorenz gauge
        9.1  Energy-momentum tensor
        9.2  Momentum density
        9.3  Stress-energy of EM field
        9.4  Energy density of EM field
        10.1 Wave equation
        10.2 Electromagnetic waves
        10.3 Radiation reaction
        11.1 Lorentz invariance
        11.2 Gauge fixing
    """
    key = str(node_id).strip()
    creators: dict[str, Callable[[str], str]] = {
        "1.1": create_1_1_inertial_frames,
        "1.2": create_1_2_constancy_of_speed_of_light,
        "1.3": create_1_3_principle_of_relativity,
        "2.2": create_2_2_spacetime_event,
        "2.3": create_2_3_principle_of_locality,
        "3.1": create_3_1_metric_tensor,
        "3.2": create_3_2_spacetime_interval,
        "3.3": create_3_3_lorentz_transformations,
        "3.4": create_3_4_light_cone,
        "3.5": create_3_5_minkowski_diagram,
        "4.1": create_4_1_proper_time,
        "4.2": create_4_2_four_vectors,
        "4.3": create_4_3_position_four_vector,
        "4.4": create_4_4_velocity_four_vector,
        "4.5": create_4_5_momentum_four_vector,
        "4.6": create_4_6_mass_energy_equivalence,
        "5.1": create_5_1_lagrangian,
        "5.2": create_5_2_action_principle,
        "5.3": create_5_3_euler_lagrange,
        "5.4": create_5_4_canonical_momentum,
        "5.5": create_5_5_hamiltonian_formalism,
        "5.6": create_5_6_noethers_theorem,
        "6.1": create_6_1_scalar_field,
        "6.2": create_6_2_vector_field,
        "6.3": create_6_3_field_lagrangian,
        "6.4": create_6_4_field_equations,
        "7.1": create_7_1_vector_potential,
        "7.2": create_7_2_field_tensor,
        "7.3": create_7_3_electric_field,
        "7.4": create_7_4_magnetic_field,
        "7.5": create_7_5_electromagnetic_field,
        "7.6": create_7_6_four_current,
        "7.7": create_7_7_maxwells_equations,
        "8.1": create_8_1_gauge_invariance,
        "8.3": create_8_3_minimal_coupling,
        "8.4": create_8_4_lorentz_force_law,
        "8.5": create_8_5_charge_conservation,
        "8.6": create_8_6_lorenz_gauge,
        "9.1": create_9_1_energy_momentum_tensor,
        "9.2": create_9_2_poynting_vector,
        "9.3": create_9_3_em_stress_energy,
        "9.4": create_9_4_em_energy_density,
        "10.1": create_10_1_wave_equation,
        "10.2": create_10_2_electromagnetic_waves,
        "10.3": create_10_3_radiation_reaction,
        "11.1": create_11_1_lorentz_invariance,
        "11.2": create_11_2_gauge_fixing,
    }
    creator = creators.get(key)
    if creator is None:
        return None
    return creator(variant)


def saveSvgGraphics(output_dir: str | Path = ".") -> None:
    """Convenience helper: write all currently implemented SVGs to files."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for node_id in [
        "1.1", "1.2", "1.3", "2.2", "2.3",
        "3.1", "3.2", "3.3", "3.4", "3.5",
        "4.1", "4.2", "4.3", "4.4", "4.5", "4.6",
        "5.1", "5.2", "5.3", "5.4", "5.5", "5.6",
        "6.1", "6.2", "6.3", "6.4",
        "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7",
        "8.1", "8.3", "8.4", "8.5", "8.6",
        "9.1", "9.2", "9.3", "9.4",
        "10.1", "10.2", "10.3",
        "11.1", "11.2",
    ]:
        svg = createSvgGraphic(node_id, variant="icon")
        if svg is not None:
            (output / f"image_{node_id.replace('.', '_')}.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    saveSvgGraphics()
