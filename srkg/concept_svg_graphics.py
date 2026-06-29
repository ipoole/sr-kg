"""
KG SVG graphics for Special Relativity / Classical Field Theory.

This module generates simple, deterministic SVG diagrams for selected
knowledge-graph nodes.  For now it covers layers 1 and 2 only.

Public entry point:
    createSvgGraphic(node_id) -> str | None

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


def _text(x: float, y: float, text: str, **kwargs: object) -> str:
    # Text content is intentionally restricted to short controlled labels.
    return f'<text x="{x:.1f}" y="{y:.1f}" {_attrs(**kwargs)}>{text}</text>'


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


# ---------------------------------------------------------------------------
# Layer 1: Foundational Postulates
# ---------------------------------------------------------------------------


def create_1_1_principle_of_relativity() -> str:
    """
    Node: 1.1
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
    node_id = "1.1"
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
        body.append(_text(ox - 24, oy + 42, frame_label, font_size=50,
                          font_family=FONT, font_style="italic", fill=BLACK))

    body.append(_line(168, 176, 344, 176, stroke=BLUE, stroke_width=7,
                      stroke_linecap="round", marker_end=f"url(#{v_marker})"))
    body.append(_text(256, 148, "v", font_size=46, font_family=FONT,
                      font_style="italic", fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Principle of relativity", body, defs)


def create_1_2_constancy_of_speed_of_light() -> str:
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

    # Central source dot and flash.
    body.append(_path(
        "M256,209 L269,239 L302,240 L276,260 L286,292 L256,274 L226,292 L236,260 L210,240 L243,239 Z",
        fill=AMBER, opacity="0.34", stroke="none",
    ))
    body.append(_circle(CX, CY, 21, fill=AMBER, stroke=BLACK, stroke_width=3))

    # Two rays in deliberately different directions, both labelled c.
    for angle, label_offset in [(24, (22, -12)), (122, (-10, -24))]:
        a = radians(angle)
        x1 = CX + 38 * cos(a)
        y1 = CY - 38 * sin(a)
        x2 = CX + 214 * cos(a)
        y2 = CY - 214 * sin(a)
        body.append(_line(x1, y1, x2, y2, stroke=BLUE, stroke_width=7,
                          stroke_linecap="round", marker_end=f"url(#{ray_marker})"))
        lx = CX + 120 * cos(a) + label_offset[0]
        ly = CY - 120 * sin(a) + label_offset[1]
        body.append(_text(lx, ly, "c", font_size=46, font_family=FONT,
                          font_style="italic", fill=BLUE, text_anchor="middle"))

    return _svg(node_id, "Constancy of the speed of light", body, defs)


# ---------------------------------------------------------------------------
# Layer 2: Observers and Events
# ---------------------------------------------------------------------------


def create_2_1_inertial_frames() -> str:
    """
    Node: 2.1
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
    node_id = "2.1"
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
    body.append(_text(334, y_track - 28, "v", font_size=46, font_family=FONT,
                      font_style="italic", fill=GREEN))

    return _svg(node_id, "Inertial frames", body, defs)


def create_2_2_spacetime_event() -> str:
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
    px, py = 326, 174

    body.extend(_draw_axes(ox, oy, 328, 300, marker_id, x_label="x", y_label="ct", stroke_width=7))

    # A coordinate "corner" from the axes to the event point.
    body.append(_line(px, py, px, oy, stroke=LIGHT_GREY, stroke_width=5,
                      stroke_dasharray="9 9", stroke_linecap="round"))
    body.append(_line(ox, py, px, py, stroke=LIGHT_GREY, stroke_width=5,
                      stroke_dasharray="9 9", stroke_linecap="round"))
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


def create_2_3_principle_of_locality() -> str:
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
# Public API
# ---------------------------------------------------------------------------


def createSvgGraphic(node_id: str) -> str | None:
    """
    Return an SVG XML string for a KG node id, or None if this module does not
    yet provide a graphic for that node.

    Currently implemented:
        1.1  Principle of relativity
        1.2  Constancy of the speed of light
        2.1  Inertial frames
        2.2  Spacetime event
        2.3  Principle of locality
    """
    key = str(node_id).strip()
    creators: dict[str, Callable[[], str]] = {
        "1.1": create_1_1_principle_of_relativity,
        "1.2": create_1_2_constancy_of_speed_of_light,
        "2.1": create_2_1_inertial_frames,
        "2.2": create_2_2_spacetime_event,
        "2.3": create_2_3_principle_of_locality,
    }
    creator = creators.get(key)
    if creator is None:
        return None
    return creator()


def saveSvgGraphics(output_dir: str | Path = ".") -> None:
    """Convenience helper: write all currently implemented SVGs to files."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for node_id in ["1.1", "1.2", "2.1", "2.2", "2.3"]:
        svg = createSvgGraphic(node_id)
        if svg is not None:
            (output / f"image_{node_id.replace('.', '_')}.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    saveSvgGraphics()
