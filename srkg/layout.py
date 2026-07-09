"""Layer-based node layout helpers.

This module computes deterministic initial graph positions from pedagogical
node layers. Layer 1 is placed at the bottom of the graph, higher numbered
layers are placed above it, and each left-aligned row curves upward as nodes
advance left-to-right in numeric concept-ID order.

The layout code accepts already-loaded data frames and plain dictionaries. It
does not load files, create PyVis objects, inject HTML, or inspect edge display
metadata.
"""

import pandas as pd

from srkg.config import (
    LAYOUT_ROW_CURVE_EXPONENT,
    LAYOUT_ROW_CURVE_FLAT_COUNT,
    LAYOUT_ROW_CURVE_MAX_RISE_FRACTION,
    LAYOUT_ROW_CURVE_TARGET_NODE,
    LAYOUT_ROW_CURVE_TARGET_RISE_FRACTION,
    LAYOUT_X_SPACING,
    LAYOUT_Y_SPACING,
)


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
    row_stagger: int | None = None,
    row_curve_flat_count: int = LAYOUT_ROW_CURVE_FLAT_COUNT,
    row_curve_target_node: int = LAYOUT_ROW_CURVE_TARGET_NODE,
    row_curve_target_rise_fraction: float = LAYOUT_ROW_CURVE_TARGET_RISE_FRACTION,
    row_curve_max_rise_fraction: float = LAYOUT_ROW_CURVE_MAX_RISE_FRACTION,
    row_curve_exponent: float = LAYOUT_ROW_CURVE_EXPONENT,
) -> dict[str, tuple[float, float]]:
    """Place nodes on left-aligned rows that curve upward to the right."""
    # Retained as an accepted argument for older callers; curved rows now use
    # the row_curve_* parameters instead.
    _ = row_stagger

    nodes_by_level: dict[int, list[str]] = {}
    for node_id, level in hierarchy_levels.items():
        nodes_by_level.setdefault(level, []).append(node_id)

    ordered_nodes = order_nodes_within_levels(nodes_by_level, hierarchy_levels, edges_df)

    positions = {}
    for level, sorted_nodes in ordered_nodes.items():
        for index, node_id in enumerate(sorted_nodes):
            positions[node_id] = (
                index * x_spacing,
                (level * y_spacing)
                - curved_row_rise(
                    index,
                    y_spacing,
                    flat_count=row_curve_flat_count,
                    target_node=row_curve_target_node,
                    target_rise_fraction=row_curve_target_rise_fraction,
                    max_rise_fraction=row_curve_max_rise_fraction,
                    exponent=row_curve_exponent,
                ),
            )

    return positions


def curved_row_rise(
    index: int,
    y_spacing: int,
    *,
    flat_count: int,
    target_node: int,
    target_rise_fraction: float,
    max_rise_fraction: float,
    exponent: float,
) -> float:
    """Return the upward row rise for a zero-based node index."""
    flat_count = max(1, int(flat_count))
    target_node = max(flat_count + 1, int(target_node))
    exponent = max(0.1, float(exponent))

    curve_step = max(0, index - (flat_count - 1))
    if curve_step == 0:
        return 0.0

    target_step = target_node - flat_count
    target_rise = y_spacing * max(0.0, float(target_rise_fraction))
    max_rise = y_spacing * max(0.0, float(max_rise_fraction))
    uncapped_rise = target_rise * ((curve_step / target_step) ** exponent)
    return min(uncapped_rise, max_rise)


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
