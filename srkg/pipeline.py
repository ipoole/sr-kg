"""End-to-end graph generation pipeline.

This module coordinates the complete generation workflow for callers that do
not want to manage individual stages. It resolves input paths, reads CSV files,
validates and normalizes data, builds relation colour metadata, computes module
layout positions, writes the base PyVis HTML, injects viewer assets, and
returns summary information for the CLI.

The pipeline is the only ``srkg`` module intended to depend on all major stages.
Lower-level modules should not import it.
"""

from dataclasses import replace
from pathlib import Path

import pandas as pd

from srkg.kb import KnowledgeBase, load_knowledge_base, resolve_knowledge_base_paths
from srkg.data import concept_domain
from srkg.content_units import build_content_registry
from srkg.edges import build_edge_colour_map, enrich_edge_key_with_colours
from srkg.html_injection import inject_controls
from srkg.layout import build_flat_positions
from srkg.layout_persistence import resolve_published_layout
from srkg.module_layout import (
    build_generated_module_anchors,
    build_module_local_layout,
)
from srkg.module_colours import build_module_visuals_by_concept
from srkg.render_pyvis import write_pyvis_html
from srkg.tutorials import tutorials_for_domains


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
    google_drive_client_id: str = "",
    warning_handler=None,
) -> tuple[Path, int, int, Path | None, int]:
    """Generate the standalone HTML viewer from a knowledge-base data root."""
    kb = load_viewer_knowledge_base(data_root, domains=domains,
        also_load_linked_concepts=also_load_linked_concepts, relations=relations)
    return generate_viewer_from_kb(
        kb=kb,
        out_path=out_path,
        height=height,
        width=width,
        title=title,
        google_drive_client_id=google_drive_client_id,
        warning_handler=warning_handler,
    )


def load_viewer_knowledge_base(data_root, *, domains=None, also_load_linked_concepts=False,
                             relations=None, include_graphics=True):
    """Apply the same source selection to generation and diagnostic CLI modes."""
    collection = resolve_knowledge_base_paths(data_root).domains_root is not None
    kb = load_knowledge_base(data_root, domains=domains if collection else None, include_graphics=include_graphics)
    kb = filter_knowledge_base_by_domains(
        kb,
        domains=domains,
        also_load_linked_concepts=also_load_linked_concepts,
    )
    kb = filter_knowledge_base_by_relations(kb, relations=relations)
    return kb


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


def filter_knowledge_base_by_domains(
    kb: KnowledgeBase,
    *,
    domains: list[str] | tuple[str, ...] | None,
    also_load_linked_concepts: bool = False,
) -> KnowledgeBase:
    """Return a view of the KB containing only selected domains and links."""
    if kb.paths.domains_root is not None and domains:
        if also_load_linked_concepts:
            raise ValueError("Domain collections retain only explicit domains; automatic linked-concept inclusion is not supported")
        if set(domains) != {package.id for package in kb.domain_packages}:
            return load_knowledge_base(kb.paths.root, domains=list(domains))
        return kb
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
    available_domains = {
        concept_domain(row)
        for _, row in filtered_nodes.iterrows()
        if concept_domain(row)
    }
    content_units = build_content_registry(filtered_concepts, filtered_modules, domains=available_domains)

    return KnowledgeBase(
        paths=kb.paths,
        nodes_df=filtered_nodes,
        edges_df=filtered_edges,
        edge_key=kb.edge_key,
        concepts=filtered_concepts,
        modules=filtered_modules,
        published_layout=kb.published_layout,
        tutorials=tutorials_for_domains(kb.tutorials, available_domains),
        content_units=content_units,
        build_warnings=content_units.warnings,
    )


def generate_viewer_from_kb(
    *,
    kb: KnowledgeBase,
    out_path: str,
    height: str,
    width: str,
    title: str,
    google_drive_client_id: str = "",
    warning_handler=None,
) -> tuple[Path, int, int, Path | None, int]:
    """Generate the standalone HTML viewer from a loaded knowledge base."""
    if warning_handler is not None and kb.build_warnings:
        warning_handler(kb.build_warnings)
    edge_colour_map = build_edge_colour_map(kb.edge_key)

    if kb.modules:
        generated_modules = build_generated_module_anchors(
            kb.nodes_df,
            kb.edges_df,
            kb.modules,
        )
        effective_anchors = dict(generated_modules.anchors)
        effective_anchors.update({
            module_id: (position.x, position.y)
            for module_id, position in kb.published_layout.modules.items()
        })
        generated_concepts = build_module_local_layout(
            kb.nodes_df,
            kb.edges_df,
            kb.modules,
            module_anchors=effective_anchors,
        )
        hierarchy_levels = generated_concepts.ranks
        hierarchy_positions = generated_concepts.positions
        generated_module_positions = generated_modules.anchors
    else:
        # Generic compatibility for module-free library fixtures. Supported
        # authored roots use modules as their pedagogical grouping.
        hierarchy_levels = {
            str(concept_id): 0 for concept_id in kb.nodes_df["id"]
        }
        hierarchy_positions = build_flat_positions(kb.nodes_df)
        generated_module_positions = {}
    published_layout = resolve_published_layout(
        kb.published_layout,
        generated_concept_positions=hierarchy_positions,
        generated_module_positions=generated_module_positions,
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
        module_visuals_by_concept=build_module_visuals_by_concept(kb.modules, palettes={package.id: package.palette for package in kb.domain_packages}),
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
        tutorial_data=kb.tutorial_data(),
        domain_data=kb.domain_data(),
        google_drive_client_id=google_drive_client_id,
    )
    output_file.write_text(html_text, encoding="utf-8")

    return (
        output_file,
        len(kb.nodes_df),
        len(kb.edges_df),
        kb.paths.edge_key,
        len(kb.edge_key),
    )
