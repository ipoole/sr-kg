"""Reusable SVG diagram motifs shared by concept graphics."""

from __future__ import annotations

from srkg.svg_graphics.primitives import (
    BLACK,
    BLUE,
    FONT,
    GREY,
    LIGHT_GREY,
    VERY_LIGHT_GREY,
    _arrow_marker,
    _line,
    _path,
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


__all__ = [
    '_axis_arrow_defs',
    '_draw_axes',
    '_draw_grid',
    '_label_tile',
    '_paren_column',
    '_paren_matrix',
]
