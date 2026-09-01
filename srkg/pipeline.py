"""End-to-end graph generation pipeline.

This module coordinates the complete generation workflow for callers that do
not want to manage individual stages. It resolves input paths, reads CSV files,
validates and normalizes data, builds relation colour metadata, computes layout
levels and positions, writes the base PyVis HTML, injects viewer assets, and
returns summary information for the CLI.

The pipeline is the only ``srkg`` module intended to depend on all major stages.
Lower-level modules should not import it.
"""

from dataclasses import replace
from pathlib import Path

import pandas as pd

from srkg.kb import KnowledgeBase, load_knowledge_base
from srkg.edges import build_edge_colour_map, enrich_edge_key_with_colours
from srkg.html_injection import inject_controls
from srkg.layout import (
    build_concept_sort_keys,
    build_hierarchy_levels,
    build_hierarchy_positions,
)
from srkg.layout_persistence import resolve_published_layout
from srkg.render_pyvis import write_pyvis_html


def generate_viewer_from_root(
    *,
    data_root: str,
    out_path: str,
    height: str,
    width: str,
    title: str,
    domains: list[str] | tuple[str, ...] | None = None,
    also_load_linked_concepts: bool = False,
    relations: list[str] | tuple[str, ...] | None = None,
) -> tuple[Path, int, int, Path | None, int]:
    """Generate the standalone HTML viewer from a knowledge-base data root."""
    kb = load_knowledge_base(data_root)
    kb = filter_knowledge_base_by_domains(
        kb,
        domains=domains,
        also_load_linked_concepts=also_load_linked_concepts,
    )
    kb = filter_knowledge_base_by_relations(kb, relations=relations)
    return generate_viewer_from_kb(
        kb=kb,
        out_path=out_path,
        height=height,
        width=width,
        title=title,
    )


def filter_knowledge_base_by_relations(
    kb: KnowledgeBase,
    *,
    relations: list[str] | tuple[str, ...] | None,
) -> KnowledgeBase:
    """Return a KB view containing only explicitly selected edge relations."""
    selected = {
        str(relation).strip()
        for relation in relations or []
        if str(relation).strip()
    }
    if not selected:
        return kb

    known = set(kb.edges_df["relation"].astype(str)) | set(kb.edge_key)
    unknown = sorted(selected - known)
    if unknown:
        raise ValueError("Unknown edge relation(s): " + ", ".join(unknown))

    return replace(
        kb,
        edges_df=kb.edges_df[
            kb.edges_df["relation"].astype(str).isin(selected)
        ].copy(),
        edge_key={
            relation: metadata
            for relation, metadata in kb.edge_key.items()
            if relation in selected
        },
    )


def concept_domain(row: pd.Series) -> str:
    """Return a concept domain from an explicit column or semantic id prefix."""
    if "domain" in row.index:
        domain = str(row.get("domain", "") or "").strip()
        if domain:
            return domain

    concept_id = str(row.get("id", "") or "").strip()
    if "." in concept_id:
        return concept_id.split(".", 1)[0]
    return ""


def filter_knowledge_base_by_domains(
    kb: KnowledgeBase,
    *,
    domains: list[str] | tuple[str, ...] | None,
    also_load_linked_concepts: bool = False,
) -> KnowledgeBase:
    """Return a view of the KB containing only selected domains and links."""
    requested_domains = {str(domain).strip() for domain in domains or [] if str(domain).strip()}
    if not requested_domains:
        return kb

    domain_by_id = {
        str(row["id"]).strip(): concept_domain(row)
        for _, row in kb.nodes_df.iterrows()
    }
    selected_ids = {
        concept_id
        for concept_id, domain in domain_by_id.items()
        if domain in requested_domains
    }
    if not selected_ids:
        raise ValueError(
            "No concepts matched domain(s): " + ", ".join(sorted(requested_domains))
        )

    if also_load_linked_concepts:
        for row in kb.edges_df.itertuples(index=False):
            source = str(row.source)
            target = str(row.target)
            if source in selected_ids or target in selected_ids:
                selected_ids.add(source)
                selected_ids.add(target)

    filtered_nodes = kb.nodes_df[kb.nodes_df["id"].astype(str).isin(selected_ids)].copy()
    filtered_edges = kb.edges_df[
        kb.edges_df["source"].astype(str).isin(selected_ids)
        & kb.edges_df["target"].astype(str).isin(selected_ids)
    ].copy()
    filtered_concepts = tuple(
        concept for concept in kb.concepts if concept.id in selected_ids
    )
    filtered_modules = tuple(
        replace(
            module,
            members=[
                concept_id
                for concept_id in module.members
                if concept_id in selected_ids
            ],
            supports=[
                support
                for support in module.supports
                if support.target_type != "concept" or support.target_id in selected_ids
            ],
        )
        for module in kb.modules
        if module.domain in requested_domains
        and any(concept_id in selected_ids for concept_id in module.members)
    )

    return KnowledgeBase(
        paths=kb.paths,
        nodes_df=filtered_nodes,
        edges_df=filtered_edges,
        edge_key=kb.edge_key,
        concepts=filtered_concepts,
        modules=filtered_modules,
        published_layout=kb.published_layout,
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
    published_layout = resolve_published_layout(
        kb.published_layout,
        generated_concept_positions=hierarchy_positions,
        modules=kb.modules,
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
        module_data=kb.module_data(),
        published_layout=published_layout.to_viewer_data(),
    )
    output_file.write_text(html_text, encoding="utf-8")

    return (
        output_file,
        len(kb.nodes_df),
        len(kb.edges_df),
        kb.paths.edge_key,
        len(kb.edge_key),
    )
