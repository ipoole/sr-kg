"""Generic deterministic layout helpers for module-free graph fixtures."""

import math
import re

import pandas as pd

from srkg.config import LAYOUT_X_SPACING, LAYOUT_Y_SPACING


def concept_sort_key(cid: str):
    """Sort numeric and module-prefixed display IDs naturally."""
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part.casefold())
        for part in re.split(r"(\d+)", str(cid))
        if part
    )


def concept_display_id(row) -> str:
    """Return the human-facing concept number for a node row."""
    display_id = str(row.get("display_id", "")).strip()
    if display_id:
        return display_id
    return str(row.get("id", "")).strip()


def build_concept_sort_keys(nodes_df: pd.DataFrame) -> dict[str, tuple]:
    """Return natural sort keys keyed by stable concept ID."""
    return {
        str(row["id"]): concept_sort_key(concept_display_id(row))
        for _, row in nodes_df.iterrows()
    }


def build_flat_positions(
    nodes_df: pd.DataFrame,
    *,
    x_spacing: int = LAYOUT_X_SPACING,
    y_spacing: int = LAYOUT_Y_SPACING,
    max_columns: int = 4,
) -> dict[str, tuple[float, float]]:
    """Place module-free concepts on a small deterministic centred grid."""
    if nodes_df.empty:
        return {}

    sort_keys = build_concept_sort_keys(nodes_df)
    node_ids = sorted(
        (str(node_id) for node_id in nodes_df["id"]),
        key=lambda node_id: sort_keys[node_id],
    )
    column_count = min(max(1, int(max_columns)), len(node_ids))
    row_count = math.ceil(len(node_ids) / column_count)
    positions: dict[str, tuple[float, float]] = {}
    for index, node_id in enumerate(node_ids):
        row, column = divmod(index, column_count)
        columns_in_row = min(column_count, len(node_ids) - row * column_count)
        row_width = (columns_in_row - 1) * x_spacing
        positions[node_id] = (
            column * x_spacing - row_width / 2,
            (row - (row_count - 1) / 2) * y_spacing,
        )
    return positions
