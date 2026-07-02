#!/usr/bin/env python3
"""
Generate a standalone SVG graphics review sheet.

Examples:
    python tools/show_graphics.py 7.6
    python tools/show_graphics.py '7.*'
    python tools/show_graphics.py '*.*'

Quote wildcard arguments in the shell so they are passed to this script rather
than expanded as filesystem globs.
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import sys
import tempfile
from dataclasses import dataclass
from html import escape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srkg.concept_svg_graphics import createSvgGraphic


@dataclass(frozen=True)
class Concept:
    id: str
    label: str
    layer: str
    icon_caption: str
    detail_caption: str


def concept_sort_key(concept_id: str) -> tuple[int, ...]:
    """Sort dotted numeric concept IDs numerically where possible."""
    parts = []
    for part in concept_id.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def load_concepts(designs_path: Path) -> list[Concept]:
    with designs_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        concepts = [
            Concept(
                id=(row.get("id") or "").strip(),
                label=(row.get("label") or "").strip(),
                layer=(row.get("layer") or "").strip(),
                icon_caption=(row.get("icon_caption") or "").strip(),
                detail_caption=(row.get("detail_caption") or "").strip(),
            )
            for row in reader
        ]
    return sorted((c for c in concepts if c.id), key=lambda c: concept_sort_key(c.id))


def select_concepts(concepts: list[Concept], patterns: list[str]) -> list[Concept]:
    selected: list[Concept] = []
    seen: set[str] = set()
    for pattern in patterns:
        matches = [c for c in concepts if fnmatch.fnmatchcase(c.id, pattern)]
        for concept in matches:
            if concept.id not in seen:
                selected.append(concept)
                seen.add(concept.id)
    return selected


def render_svg_cell(concept_id: str, variant: str) -> str:
    svg = createSvgGraphic(concept_id, variant=variant)
    if svg is None:
        return '<div class="missing">No SVG</div>'
    return svg


def render_html(concepts: list[Concept], patterns: list[str]) -> str:
    rows = []
    for concept in concepts:
        icon_svg = render_svg_cell(concept.id, "icon")
        detail_svg = render_svg_cell(concept.id, "detail")
        rows.append(
            f"""
            <section class="concept-card" id="concept-{escape(concept.id)}">
              <header>
                <div class="concept-id">{escape(concept.id)}</div>
                <div>
                  <h2>{escape(concept.label)}</h2>
                  <p>Layer {escape(concept.layer)}</p>
                </div>
              </header>
              <div class="graphics-row">
                <figure>
                  <figcaption>Icon</figcaption>
                  <div class="svg-box icon">{icon_svg}</div>
                  <p class="graphic-caption">{escape(concept.icon_caption)}</p>
                </figure>
                <figure>
                  <figcaption>Detail</figcaption>
                  <div class="svg-box detail">{detail_svg}</div>
                  <p class="graphic-caption">{escape(concept.detail_caption)}</p>
                </figure>
              </div>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SR-KG Graphics Review</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Arial, sans-serif;
      line-height: 1.35;
    }}
    body {{
      background: #f4f4f4;
      color: #222;
      margin: 0;
      padding: 18px;
    }}
    .page-header {{
      background: white;
      border: 1px solid #d7d7d7;
      border-radius: 8px;
      margin: 0 auto 14px;
      max-width: 1160px;
      padding: 12px 14px;
    }}
    .page-header h1 {{
      font-size: 22px;
      margin: 0 0 4px;
    }}
    .page-header p {{
      color: #555;
      margin: 0;
    }}
    .concept-card {{
      background: white;
      border: 1px solid #d7d7d7;
      border-radius: 8px;
      margin: 14px auto;
      max-width: 1160px;
      padding: 14px;
    }}
    .concept-card header {{
      align-items: center;
      border-bottom: 1px solid #e6e6e6;
      display: flex;
      gap: 12px;
      margin-bottom: 12px;
      padding-bottom: 10px;
    }}
    .concept-id {{
      background: #eef3fd;
      border: 1px solid #cddaf2;
      border-radius: 6px;
      color: #174ea6;
      font-size: 22px;
      font-weight: 700;
      min-width: 62px;
      padding: 8px 10px;
      text-align: center;
    }}
    h2 {{
      font-size: 18px;
      margin: 0;
    }}
    header p {{
      color: #666;
      margin: 2px 0 0;
    }}
    .graphics-row {{
      align-items: stretch;
      display: grid;
      gap: 14px;
      grid-template-columns: minmax(220px, 0.7fr) minmax(360px, 1.3fr);
    }}
    figure {{
      border: 1px solid #e2e2e2;
      border-radius: 8px;
      margin: 0;
      overflow: visible;
      padding: 10px;
    }}
    figcaption {{
      color: #555;
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 8px;
      text-transform: uppercase;
    }}
    .svg-box {{
      align-items: center;
      background:
        linear-gradient(45deg, #fafafa 25%, transparent 25%),
        linear-gradient(-45deg, #fafafa 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #fafafa 75%),
        linear-gradient(-45deg, transparent 75%, #fafafa 75%);
      background-color: #fff;
      background-position: 0 0, 0 8px, 8px -8px, -8px 0;
      background-size: 16px 16px;
      border: 1px solid #eee;
      border-radius: 6px;
      display: flex;
      justify-content: center;
      min-height: 260px;
      overflow: visible;
      padding: 8px;
    }}
    .svg-box.icon svg {{
      height: auto;
      max-height: 230px;
      max-width: 230px;
      width: 100%;
    }}
    .svg-box.detail svg {{
      height: auto;
      max-height: 340px;
      max-width: 440px;
      width: 100%;
    }}
    .graphic-caption {{
      background: #fbfbfb;
      border-left: 3px solid #cddaf2;
      color: #333;
      font-size: 14px;
      margin: 10px 0 0;
      padding: 8px 10px;
    }}
    .missing {{
      align-items: center;
      color: #777;
      display: flex;
      min-height: 220px;
    }}
    @media (max-width: 760px) {{
      .graphics-row {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page-header">
    <h1>SR-KG Graphics Review</h1>
    <p>Patterns: {escape(", ".join(patterns))} · Concepts: {len(concepts)}</p>
  </div>
  {"".join(rows)}
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an HTML review sheet for concept SVG graphics.",
    )
    parser.add_argument(
        "patterns",
        nargs="*",
        default=["*.*"],
        help="Concept ID or wildcard pattern, such as 7.6, '7.*', or '*.*'.",
    )
    parser.add_argument(
        "--designs",
        default="data/concept_graphic_designs.csv",
        help="CSV containing concept IDs and labels.",
    )
    parser.add_argument(
        "--out",
        default=str(Path(tempfile.gettempdir()) / "srkg-graphics-review.html"),
        help="Output HTML path.",
    )
    args = parser.parse_args()

    designs_path = Path(args.designs)
    if not designs_path.is_absolute():
        designs_path = PROJECT_ROOT / designs_path

    concepts = load_concepts(designs_path)
    selected = select_concepts(concepts, args.patterns)
    if not selected:
        available = ", ".join(c.id for c in concepts)
        raise SystemExit(
            f"No concepts matched {args.patterns!r}.\nAvailable IDs: {available}"
        )

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = PROJECT_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_html(selected, args.patterns), encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"Concepts: {len(selected)}")


if __name__ == "__main__":
    main()
