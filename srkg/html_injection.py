"""HTML asset injection for the generated viewer.

This module owns the Python side of the browser application shell layered on
top of PyVis: it loads static viewer assets, serializes graph/concept data, and
inserts everything into the generated PyVis document. Browser behaviour lives
in ``srkg/viewer_assets`` so CSS and JavaScript can be reviewed independently.
"""

import json
from pathlib import Path
from html import escape as html_escape

from srkg.config import (
    EDGE_HOVER_WIDTH,
    INFO_PANEL_FONT_SIZE_PX,
    INFO_PANEL_MOBILE_FONT_SIZE_PX,
    INFO_PANEL_TABLET_FONT_SIZE_PX,
    INFO_PANEL_TABLET_WIDTH_MAX_PX,
    INFO_PANEL_TABLET_WIDTH_VIEWPORT_PERCENT,
    INFO_PANEL_TEXT_ZOOM_MAX_PX,
    INFO_PANEL_TEXT_ZOOM_MIN_PX,
    INFO_PANEL_WIDTH_MAX_PX,
    INFO_PANEL_WIDTH_MIN_PX,
    INFO_PANEL_WIDTH_VIEWPORT_PERCENT,
    LAYOUT_ROW_STAGGER,
    LAYOUT_X_SPACING,
    LAYOUT_Y_SPACING,
    NODE_LABEL_FONT_SIZE,
    NODE_LABEL_FONT_WEIGHT,
    NODE_LABEL_HIDE_BELOW_PX,
    NODE_LABEL_WIDTH,
    NOTE_EDITING_STORAGE_KEY,
    SPLASH_DISMISSED_STORAGE_KEY,
    USER_NOTES_STORAGE_KEY,
)

ASSET_DIR = Path(__file__).with_name("viewer_assets")
VIEWPORT_META = '<meta name="viewport" content="width=device-width, initial-scale=1">'
MATHJAX_ASSET = """
<script>
  window.MathJax = {
    tex: {
      inlineMath: [['\\\\(', '\\\\)']],
      displayMath: [['\\\\[', '\\\\]']],
      processEscapes: true
    },
    svg: {
      fontCache: 'global'
    }
  };
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
"""


def require_html_marker(html_text: str, marker: str) -> None:
    """Fail clearly if PyVis output no longer contains an injection marker."""
    if marker not in html_text:
        raise ValueError(f"Generated PyVis HTML is missing expected marker: {marker}")


def inject_controls(
    html_text: str,
    concept_data: dict[str, dict[str, object]],
    edge_key: dict[str, dict[str, str | bool]],
    view_title: str,
) -> str:
    """Inject the viewer shell, assets, and serialized data into PyVis HTML."""
    for marker in ("</head>", "<body>", "</body>"):
        require_html_marker(html_text, marker)

    css = _style_tag(_render_template("viewer.css", _css_replacements()))
    controls = _render_template(
        "controls.html",
        {
            "__TITLE_HTML__": f'<div id="kg_view_title">{html_escape(view_title)}</div>',
            "__VIEW_TITLE__": html_escape(view_title),
        },
    )
    js = _script_tag(
        _render_template(
            "viewer.js",
            {
                "__CONCEPT_DATA__": _json_for_script(concept_data),
                "__EDGE_KEY__": _json_for_script(edge_key),
                "__VIEWER_CONFIG__": _json_for_script(_viewer_runtime_config()),
            },
        )
    )

    head_assets = MATHJAX_ASSET + "\n" + css
    if 'name="viewport"' not in html_text and "name='viewport'" not in html_text:
        head_assets = VIEWPORT_META + "\n" + head_assets

    html_text = html_text.replace("</head>", head_assets + "\n</head>")
    html_text = html_text.replace("<body>", "<body>\n" + controls)
    html_text = html_text.replace("</body>", js + "\n</body>")
    return html_text


def _asset_text(name: str) -> str:
    """Read a viewer asset from the package-local asset directory."""
    return (ASSET_DIR / name).read_text(encoding="utf-8")


def _render_template(name: str, replacements: dict[str, object]) -> str:
    text = _asset_text(name)
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, str(value))
    return text


def _json_for_script(data: object) -> str:
    """Serialize data for inline script use without literal closing tags."""
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def _style_tag(css_text: str) -> str:
    return "<style>\n" + css_text.rstrip() + "\n</style>"


def _script_tag(js_text: str) -> str:
    return '<script type="text/javascript">\n' + js_text.rstrip() + "\n</script>"


def _css_replacements() -> dict[str, object]:
    return {
        "__NODE_LABEL_WIDTH__": NODE_LABEL_WIDTH,
        "__NODE_LABEL_FONT_SIZE__": NODE_LABEL_FONT_SIZE,
        "__NODE_LABEL_FONT_WEIGHT__": NODE_LABEL_FONT_WEIGHT,
        "__INFO_PANEL_WIDTH_MIN_PX__": INFO_PANEL_WIDTH_MIN_PX,
        "__INFO_PANEL_WIDTH_VIEWPORT_PERCENT__": INFO_PANEL_WIDTH_VIEWPORT_PERCENT,
        "__INFO_PANEL_WIDTH_MAX_PX__": INFO_PANEL_WIDTH_MAX_PX,
        "__INFO_PANEL_TABLET_WIDTH_MAX_PX__": INFO_PANEL_TABLET_WIDTH_MAX_PX,
        "__INFO_PANEL_TABLET_WIDTH_VIEWPORT_PERCENT__": (
            INFO_PANEL_TABLET_WIDTH_VIEWPORT_PERCENT
        ),
        "__INFO_PANEL_FONT_SIZE_PX__": INFO_PANEL_FONT_SIZE_PX,
        "__INFO_PANEL_TABLET_FONT_SIZE_PX__": INFO_PANEL_TABLET_FONT_SIZE_PX,
        "__INFO_PANEL_MOBILE_FONT_SIZE_PX__": INFO_PANEL_MOBILE_FONT_SIZE_PX,
    }


def _viewer_runtime_config() -> dict[str, object]:
    """Return browser-side constants that are injected with generated data."""
    return {
        "edgeHoverWidth": EDGE_HOVER_WIDTH,
        "layout": {
            "xSpacing": LAYOUT_X_SPACING,
            "ySpacing": LAYOUT_Y_SPACING,
            "rowStagger": LAYOUT_ROW_STAGGER,
        },
        "nodeLabels": {
            "width": NODE_LABEL_WIDTH,
            "fontSize": NODE_LABEL_FONT_SIZE,
            "hideBelowPx": NODE_LABEL_HIDE_BELOW_PX,
        },
        "infoPanel": {
            "fontSizePx": INFO_PANEL_FONT_SIZE_PX,
            "textZoomMinPx": INFO_PANEL_TEXT_ZOOM_MIN_PX,
            "textZoomMaxPx": INFO_PANEL_TEXT_ZOOM_MAX_PX,
        },
        "storageKeys": {
            "userNotes": USER_NOTES_STORAGE_KEY,
            "noteEditing": NOTE_EDITING_STORAGE_KEY,
            "splashDismissed": SPLASH_DISMISSED_STORAGE_KEY,
        },
    }
