"""Reusable SVG diagram motifs shared by concept graphics."""

from __future__ import annotations

from srkg.svg_graphics.primitives import (
    BLACK,
    BLUE,
    FONT,
    GREEN,
    GREY,
    LIGHT_GREY,
    RED,
    VERY_LIGHT_GREY,
    _arrow_marker,
    _line,
    _math_text,
    _path,
    _polygon,
    _rect,
    _sid,
    _text,
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


def _implies_symbol(
    x: float,
    y: float,
    *,
    width: float = 104,
    height: float = 34,
    colour: str = BLUE,
    stroke_width: float = 5,
) -> list[str]:
    """Draw a clear line-based implication symbol, shaped like ==>."""
    mid_y = y + height / 2
    line_end = x + width - height * 0.42
    head_tip = x + width
    head_half = height / 2
    upper_y = mid_y - height * 0.22
    lower_y = mid_y + height * 0.22
    return [
        _line(x, upper_y, line_end, upper_y, stroke=colour,
              stroke_width=stroke_width, stroke_linecap="round"),
        _line(x, lower_y, line_end, lower_y, stroke=colour,
              stroke_width=stroke_width, stroke_linecap="round"),
        _polygon(
            [
                (line_end, mid_y - head_half),
                (head_tip, mid_y),
                (line_end, mid_y + head_half),
            ],
            fill=colour,
            stroke="none",
        ),
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


def _draw_manifold_patch(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str = "#f3f8ff",
    stroke: str = BLUE,
    grid_colour: str = "#aabbe8",
    stroke_width: float = 4,
    grid_opacity: str = "0.55",
) -> list[str]:
    """Draw a curved manifold patch with gentle intrinsic grid curves."""
    left = x
    right = x + width
    top = y
    bottom = y + height
    d = (
        f"M{left + 0.12 * width},{top + 0.32 * height} "
        f"C{left + 0.06 * width},{top + 0.02 * height} "
        f"{left + 0.43 * width},{top - 0.04 * height} "
        f"{left + 0.66 * width},{top + 0.10 * height} "
        f"C{right + 0.03 * width},{top + 0.30 * height} "
        f"{right - 0.08 * width},{bottom - 0.05 * height} "
        f"{right - 0.33 * width},{bottom - 0.02 * height} "
        f"C{left + 0.43 * width},{bottom + 0.08 * height} "
        f"{left + 0.02 * width},{bottom - 0.05 * height} "
        f"{left + 0.12 * width},{top + 0.32 * height} Z"
    )
    body = [_path(d, fill=fill, stroke=stroke, stroke_width=stroke_width)]

    for frac in (0.25, 0.45, 0.65):
        yy = top + height * frac
        body.append(_path(
            f"M{left + 0.13 * width},{yy} "
            f"C{left + 0.34 * width},{yy - 0.12 * height} "
            f"{left + 0.64 * width},{yy + 0.12 * height} "
            f"{right - 0.14 * width},{yy - 0.02 * height}",
            fill="none",
            stroke=grid_colour,
            stroke_width=2.5,
            opacity=grid_opacity,
            stroke_linecap="round",
        ))
    for frac in (0.30, 0.50, 0.70):
        xx = left + width * frac
        body.append(_path(
            f"M{xx},{top + 0.10 * height} "
            f"C{xx - 0.11 * width},{top + 0.34 * height} "
            f"{xx + 0.10 * width},{top + 0.62 * height} "
            f"{xx - 0.04 * width},{bottom - 0.05 * height}",
            fill="none",
            stroke=grid_colour,
            stroke_width=2.5,
            opacity=grid_opacity,
            stroke_linecap="round",
        ))
    return body


def _draw_chart_plane(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str = "#f8f8f8",
    stroke: str = BLACK,
    grid_colour: str = LIGHT_GREY,
) -> list[str]:
    """Draw a flat local coordinate chart with axes and light grid."""
    body = [
        _rect(x, y, width, height, rx=8, fill=fill, stroke=stroke, stroke_width=4),
    ]
    for frac in (0.25, 0.50, 0.75):
        body.append(_line(x + width * frac, y + 16, x + width * frac, y + height - 16,
                          stroke=grid_colour, stroke_width=2, opacity="0.65"))
        body.append(_line(x + 16, y + height * frac, x + width - 16, y + height * frac,
                          stroke=grid_colour, stroke_width=2, opacity="0.65"))
    body.append(_line(x + 34, y + height - 34, x + width - 34, y + height - 34,
                      stroke=BLACK, stroke_width=4, stroke_linecap="round"))
    body.append(_line(x + 34, y + height - 34, x + 34, y + 32,
                      stroke=BLACK, stroke_width=4, stroke_linecap="round"))
    return body


def _draw_tangent_plane(
    cx: float,
    cy: float,
    width: float,
    height: float,
    *,
    fill: str = "#f8f8f8",
    stroke: str = BLACK,
    opacity: str = "0.90",
) -> list[str]:
    """Draw a tilted tangent plane as a parallelogram."""
    hw = width / 2
    hh = height / 2
    skew = width * 0.16
    points = [
        (cx - hw + skew, cy - hh),
        (cx + hw + skew, cy - hh),
        (cx + hw - skew, cy + hh),
        (cx - hw - skew, cy + hh),
    ]
    return [
        _polygon(points, fill=fill, stroke=stroke, stroke_width=4, opacity=opacity),
        _line(cx - hw + 22, cy, cx + hw - 20, cy, stroke=GREY,
              stroke_width=3, opacity="0.55"),
        _line(cx + skew - 14, cy - hh + 20, cx - skew + 14, cy + hh - 20,
              stroke=GREY,
              stroke_width=3, opacity="0.55"),
    ]


def _draw_tangent_basis(
    x: float,
    y: float,
    *,
    x_label: str = "e₁",
    y_label: str = "e₂",
    colour: str = GREEN,
) -> tuple[list[str], list[str]]:
    """Draw two small tangent basis arrows and return body plus marker defs."""
    marker_id = f"basis_{int(x)}_{int(y)}"
    defs = [_arrow_marker(marker_id, colour=colour, size=5)]
    body = [
        _line(x, y, x + 86, y - 8, stroke=colour, stroke_width=5,
              stroke_linecap="round", marker_end=f"url(#{marker_id})"),
        _line(x, y, x + 28, y - 76, stroke=colour, stroke_width=5,
              stroke_linecap="round", marker_end=f"url(#{marker_id})"),
        _text(x + 96, y - 10, x_label, font_size=26, font_family=FONT,
              font_style="italic", fill=colour),
        _text(x + 34, y - 88, y_label, font_size=26, font_family=FONT,
              font_style="italic", fill=colour),
    ]
    return body, defs


def _draw_tensor_glyph(
    x: float,
    y: float,
    *,
    label: str = "T",
    fill: str = "#f7f7f7",
    stroke: str = BLUE,
) -> list[str]:
    """Draw a compact tensor object glyph for a tensor field."""
    return [
        _rect(x - 22, y - 22, 44, 44, rx=8, fill=fill, stroke=stroke,
              stroke_width=3),
        _math_text(x, y + 10, label, font_size=25, font_family=FONT,
                   font_style="italic", fill=stroke, text_anchor="middle"),
        _line(x - 36, y, x - 58, y - 18, stroke=RED, stroke_width=3,
              stroke_linecap="round", opacity="0.75"),
        _line(x + 36, y, x + 58, y + 18, stroke=GREEN, stroke_width=3,
              stroke_linecap="round", opacity="0.75"),
    ]


__all__ = [
    '_axis_arrow_defs',
    '_draw_chart_plane',
    '_draw_axes',
    '_draw_grid',
    '_draw_manifold_patch',
    '_draw_tangent_basis',
    '_draw_tangent_plane',
    '_draw_tensor_glyph',
    '_implies_symbol',
    '_label_tile',
    '_paren_column',
    '_paren_matrix',
]
