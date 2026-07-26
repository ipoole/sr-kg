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

from srkg.kb import KnowledgeBase, load_knowledge_base
from srkg.edges import build_edge_colour_map, enrich_edge_key_with_colours
from srkg.html_injection import inject_controls
from srkg.layout import (
    build_concept_sort_keys,
    build_hierarchy_levels,
    build_hierarchy_positions,
)
from srkg.render_pyvis import write_pyvis_html


def generate_viewer_from_root(
    *,
    data_root: str,
    out_path: str,
    height: str,
    width: str,
    title: str,
) -> tuple[Path, int, int, Path | None, int]:
    """Generate the standalone HTML viewer from a knowledge-base data root."""
    kb = load_knowledge_base(data_root)
    return generate_viewer_from_kb(
        kb=kb,
        out_path=out_path,
        height=height,
        width=width,
        title=title,
    )


def generate_viewer_from_kb(
    *,
    kb: KnowledgeBase,
    out_path: str,
    height: str,
    width: str,
    title: str,
) -> tuple[Path, int, int, Path | None, int]:
    """Generate the standalone HTML viewer from a loaded knowledge base."""
    edge_colour_map = build_edge_colour_map(kb.edge_key)

    hierarchy_levels = build_hierarchy_levels(kb.nodes_df)
    hierarchy_positions = build_hierarchy_positions(
        hierarchy_levels,
        kb.edges_df,
        sort_key_by_id=build_concept_sort_keys(kb.nodes_df),
    )

    output_file = Path(out_path)
    write_pyvis_html(
        nodes_df=kb.nodes_df,
        edges_df=kb.edges_df,
        edge_key=kb.edge_key,
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
        kb.concept_data(),
        enrich_edge_key_with_colours(kb.edge_key, edge_colour_map),
        title,
    )
    output_file.write_text(html_text, encoding="utf-8")

    return (
        output_file,
        len(kb.nodes_df),
        len(kb.edges_df),
        kb.paths.edge_key,
        len(kb.edge_key),
    )
