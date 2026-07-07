"""Layer-based node layout helpers.

This module computes deterministic initial graph positions from pedagogical
node layers. Layer 1 is placed at the bottom of the graph, higher numbered
layers are placed above it, and nodes within each layer are placed left to
right in numeric concept-ID order.

The layout code accepts already-loaded data frames and plain dictionaries. It
does not load files, create PyVis objects, inject HTML, or inspect edge display
metadata.
"""

import pandas as pd

from srkg.config import LAYOUT_ROW_STAGGER, LAYOUT_X_SPACING, LAYOUT_Y_SPACING


def concept_sort_key(cid: str):
    """Sort concept IDs like 3.12 numerically."""
    try:
        return tuple(int(x) for x in str(cid).split("."))
    except Exception:
        return (9999, str(cid))


def parse_layer_value(node_id: str, layer: str | int | float | None) -> int:
    """Read a pedagogical layer from the layer column, falling back to the id prefix."""
    try:
        value = int(float(str(layer).strip()))
        if value > 0:
            return value
    except Exception:
        pass

    try:
        value = int(str(node_id).split(".", 1)[0])
        if value > 0:
            return value
    except Exception:
        pass

    return 0


def build_hierarchy_levels(nodes_df: pd.DataFrame) -> dict[str, int]:
    """Assign top-to-bottom layout levels from pedagogical node layers.

    Larger hierarchy levels are drawn lower by build_hierarchy_positions(), so
    layer 1 is mapped to the bottom row and the largest layer is mapped to the
    top row.
    """
    node_layers = {
        str(row["id"]): parse_layer_value(row["id"], row.get("layer", ""))
        for _, row in nodes_df.iterrows()
    }
    positive_layers = [layer for layer in node_layers.values() if layer > 0]
    max_layer = max(positive_layers, default=0)

    return {
        node_id: (max_layer - layer if layer > 0 else max_layer)
        for node_id, layer in node_layers.items()
    }


def build_hierarchy_positions(
    hierarchy_levels: dict[str, int],
    edges_df: pd.DataFrame | None = None,
    x_spacing: int = LAYOUT_X_SPACING,
    y_spacing: int = LAYOUT_Y_SPACING,
    row_stagger: int = LAYOUT_ROW_STAGGER,
) -> dict[str, tuple[float, float]]:
    """Place nodes in numeric order on rows that slope upward to the right."""
    nodes_by_level: dict[int, list[str]] = {}
    for node_id, level in hierarchy_levels.items():
        nodes_by_level.setdefault(level, []).append(node_id)

    ordered_nodes = order_nodes_within_levels(nodes_by_level, hierarchy_levels, edges_df)

    positions = {}
    for level, sorted_nodes in ordered_nodes.items():
        row_width = (len(sorted_nodes) - 1) * x_spacing
        row_slope_height = (len(sorted_nodes) - 1) * row_stagger
        for index, node_id in enumerate(sorted_nodes):
            positions[node_id] = (
                (index * x_spacing) - (row_width / 2),
                (level * y_spacing) + (row_slope_height / 2) - (index * row_stagger),
            )

    return positions


def order_nodes_within_levels(
    nodes_by_level: dict[int, list[str]],
    hierarchy_levels: dict[str, int],
    edges_df: pd.DataFrame | None,
    sweeps: int = 6,
) -> dict[int, list[str]]:
    """Order nodes within each fixed layer by numeric concept ID."""
    return {
        level: sorted(nodes, key=concept_sort_key)
        for level, nodes in nodes_by_level.items()
    }
