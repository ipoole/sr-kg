"""Layer-based node layout helpers."""

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
    """Place nodes in compact staggered rows derived from hierarchy levels."""
    nodes_by_level: dict[int, list[str]] = {}
    for node_id, level in hierarchy_levels.items():
        nodes_by_level.setdefault(level, []).append(node_id)

    ordered_nodes = order_nodes_within_levels(nodes_by_level, hierarchy_levels, edges_df)

    positions = {}
    for level, sorted_nodes in ordered_nodes.items():
        row_width = (len(sorted_nodes) - 1) * x_spacing
        for index, node_id in enumerate(sorted_nodes):
            stagger = 0
            if len(sorted_nodes) > 1:
                stagger = ((index % 3) - 1) * row_stagger
            positions[node_id] = (
                (index * x_spacing) - (row_width / 2),
                (level * y_spacing) + stagger,
            )

    return positions


def order_nodes_within_levels(
    nodes_by_level: dict[int, list[str]],
    hierarchy_levels: dict[str, int],
    edges_df: pd.DataFrame | None,
    sweeps: int = 6,
) -> dict[int, list[str]]:
    """Reduce crossings by reordering nodes within each fixed layer.

    This is a small barycentric ordering pass: each node is sorted by the
    average normalized horizontal position of its neighbours in other layers.
    """
    ordered = {
        level: sorted(nodes, key=concept_sort_key)
        for level, nodes in nodes_by_level.items()
    }
    if edges_df is None or edges_df.empty:
        return ordered

    neighbours: dict[str, set[str]] = {node_id: set() for node_id in hierarchy_levels}
    for _, row in edges_df.iterrows():
        source = str(row["source"])
        target = str(row["target"])
        if source not in neighbours or target not in neighbours:
            continue
        if hierarchy_levels[source] == hierarchy_levels[target]:
            continue
        neighbours[source].add(target)
        neighbours[target].add(source)

    levels = sorted(ordered)

    def normalized_orders() -> dict[str, float]:
        values = {}
        for level, nodes in ordered.items():
            denominator = max(len(nodes) - 1, 1)
            for index, node_id in enumerate(nodes):
                values[node_id] = index / denominator
        return values

    def reorder_level(level: int, order_values: dict[str, float], direction: int) -> None:
        previous_index = {node_id: index for index, node_id in enumerate(ordered[level])}

        def sort_key(node_id: str):
            candidates = [
                order_values[neighbour]
                for neighbour in neighbours.get(node_id, set())
                if neighbour in order_values
                and (hierarchy_levels[neighbour] - level) * direction < 0
            ]
            if candidates:
                barycenter = sum(candidates) / len(candidates)
            else:
                barycenter = previous_index[node_id]
            return (barycenter, previous_index[node_id], concept_sort_key(node_id))

        ordered[level] = sorted(ordered[level], key=sort_key)

    for _ in range(sweeps):
        order_values = normalized_orders()
        for level in levels[1:]:
            reorder_level(level, order_values, direction=1)

        order_values = normalized_orders()
        for level in reversed(levels[:-1]):
            reorder_level(level, order_values, direction=-1)

    return ordered
