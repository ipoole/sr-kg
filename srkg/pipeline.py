"""End-to-end graph generation pipeline.

This module coordinates the complete generation workflow for callers that do
not want to manage individual stages. It resolves input paths, reads CSV files,
validates and normalizes data, builds relation colour metadata, computes layout
levels and positions, writes the base PyVis HTML, injects viewer assets, and
returns summary information for the CLI.

The pipeline is the only ``srkg`` module intended to depend on all major stages.
Lower-level modules should not import it.
"""

from pathlib import Path

import pandas as pd

from srkg.data import (
    build_concept_data,
    find_edge_key_path,
    load_edge_key,
    normalise_edges,
)
from srkg.edges import build_edge_colour_map, enrich_edge_key_with_colours
from srkg.html_injection import inject_controls
from srkg.layout import build_hierarchy_levels, build_hierarchy_positions
from srkg.render_pyvis import write_pyvis_html


def generate_viewer(
    *,
    nodes_path: str,
    edges_path: str,
    edge_key_path: str | None,
    out_path: str,
    height: str,
    width: str,
) -> tuple[Path, int, int, Path | None, int]:
    """Generate the standalone HTML viewer and return summary metadata."""
    edges_file = Path(edges_path)
    resolved_edge_key_path = find_edge_key_path(edges_file, edge_key_path)

    nodes_df = pd.read_csv(nodes_path).fillna("")
    edges_df = pd.read_csv(edges_file).fillna("")
    edge_key = load_edge_key(resolved_edge_key_path)
    edge_colour_map = build_edge_colour_map(edge_key)

    if "id" not in nodes_df.columns:
        raise ValueError("nodes.csv must contain an 'id' column")

    edges_df = normalise_edges(edges_df)

    nodes_df["id"] = nodes_df["id"].astype(str)
    edges_df["source"] = edges_df["source"].astype(str)
    edges_df["target"] = edges_df["target"].astype(str)

    node_ids = set(nodes_df["id"])
    edges_df = edges_df[edges_df["source"].isin(node_ids) & edges_df["target"].isin(node_ids)].copy()
    hierarchy_levels = build_hierarchy_levels(nodes_df)
    hierarchy_positions = build_hierarchy_positions(hierarchy_levels, edges_df)

    concept_data = build_concept_data(nodes_df)

    output_file = Path(out_path)
    write_pyvis_html(
        nodes_df=nodes_df,
        edges_df=edges_df,
        edge_key=edge_key,
        edge_colour_map=edge_colour_map,
        hierarchy_levels=hierarchy_levels,
        hierarchy_positions=hierarchy_positions,
        out_path=output_file,
        height=height,
        width=width,
    )

    html_text = output_file.read_text(encoding="utf-8")
    html_text = inject_controls(
        html_text,
        concept_data,
        enrich_edge_key_with_colours(edge_key, edge_colour_map),
    )
    output_file.write_text(html_text, encoding="utf-8")

    return output_file, len(nodes_df), len(edges_df), resolved_edge_key_path, len(edge_key)
