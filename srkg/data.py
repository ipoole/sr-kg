"""CSV-adjacent data helpers for the SR knowledge graph.

This module owns validation and lightweight normalization of tabular inputs,
plus conversion of node rows into the concept-data mapping used by the injected
viewer. It deliberately does not know about PyVis, HTML generation, physics, or
layout. Callers are responsible for reading the primary CSV files and passing
``pandas`` data frames in.

Dependencies should stay limited to ``srkg.config`` and general-purpose parsing
libraries.
"""

from pathlib import Path

import pandas as pd

from srkg.config import EDGE_COLUMNS, EDGE_KEY_COLUMNS
from srkg.concept_svg_graphics import createSvgGraphic


def build_concept_data(nodes_df: pd.DataFrame) -> dict[str, dict[str, str]]:
    """Build panel data directly from nodes.csv, independent of PyVis metadata."""
    concept_data = {}

    def text(row: pd.Series, *columns: str) -> str:
        for column in columns:
            value = str(row.get(column, "")).strip()
            if value:
                return value
        return ""

    for _, row in nodes_df.iterrows():
        cid = str(row.get("id", "")).strip()
        if not cid:
            continue
        svg_icon = createSvgGraphic(cid, variant="icon")
        svg_detail = createSvgGraphic(cid, variant="detail")
        concept_data[cid] = {
            "label": str(row.get("label", "")).strip(),
            "layer": str(row.get("layer", "")).strip(),
            "layer_title": str(row.get("layer_title", "")).strip(),
            "definition_new": text(row, "definition_new"),
            "derivation_new": text(row, "derivation_new"),
            "explanation_new": text(row, "explanation_new"),
            "svg_icon": svg_icon or "",
            "svg_detail": svg_detail or svg_icon or "",
            "svg_graphic": svg_detail or svg_icon or "",
        }
    return concept_data


def normalise_edges(edges_df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean the knowledge edge data."""
    missing = set(EDGE_COLUMNS) - set(edges_df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"edges.csv must contain columns: {missing_cols}")

    edges_df = edges_df.copy()
    edges_df["relation"] = edges_df["relation"].replace("", "REFERENCE")

    return edges_df


def parse_bool(value, default: bool = True) -> bool:
    """Parse common CSV boolean spellings."""
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"true", "t", "yes", "y", "1"}:
        return True
    if text in {"false", "f", "no", "n", "0"}:
        return False
    return default


def load_edge_key(path: Path | None) -> dict[str, dict[str, str | bool]]:
    """Load relation metadata that controls edge direction and help text."""
    if path is None or not path.exists():
        return {}

    edge_key_df = pd.read_csv(path).fillna("")
    missing = set(EDGE_KEY_COLUMNS) - set(edge_key_df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"{path} must contain columns: {missing_cols}")

    edge_key = {}
    for _, row in edge_key_df.iterrows():
        relation = str(row.get("relation", "")).strip()
        if not relation:
            continue
        edge_key[relation] = {
            "relation": relation,
            "directed": parse_bool(row.get("directed", ""), default=True),
            "category": str(row.get("category", "")).strip(),
            "meaning": str(row.get("meaning", "")).strip(),
            "example": str(row.get("example", "")).strip(),
        }
    return edge_key


def find_edge_key_path(edges_path: Path, configured_path: str | None) -> Path | None:
    """Use an explicit edge key, or edges_key.csv beside the edge file when present."""
    if configured_path:
        path = Path(configured_path)
        if not path.exists():
            raise FileNotFoundError(f"Configured edge key file does not exist: {path}")
        return path

    sibling = edges_path.parent / "edges_key.csv"
    if sibling.exists():
        return sibling

    return None
