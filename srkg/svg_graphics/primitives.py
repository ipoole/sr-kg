"""Low-level SVG drawing primitives for concept graphics."""

from __future__ import annotations

from math import cos, radians, sin

SIZE = 512
CX = SIZE / 2
CY = SIZE / 2

# House palette. Keep this small so the whole icon set looks coherent.
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


def _tick(x: float, y: float, angle_degrees: float, length: float, **kwargs: object) -> str:
    """Draw a small tick centred at a point and rotated by angle."""
    a = radians(angle_degrees)
    dx = 0.5 * length * cos(a)
    dy = 0.5 * length * sin(a)
    return _line(x - dx, y - dy, x + dx, y + dy, **kwargs)


__all__ = [
    'SIZE',
    'CX',
    'CY',
    'BLACK',
    'GREY',
    'LIGHT_GREY',
    'VERY_LIGHT_GREY',
    'BLUE',
    'RED',
    'GREEN',
    'AMBER',
    'FONT',
    '_sid',
    '_attrs',
    '_line',
    '_circle',
    '_rect',
    '_path',
    '_polyline',
    '_polygon',
    '_text',
    '_math_text',
    '_arrow_marker',
    '_dot_marker',
    '_svg',
    '_tick',
]
