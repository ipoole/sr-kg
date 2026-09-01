#!/usr/bin/env python3
"""Explore candidate authored-module partitions for one knowledge domain."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srkg.kb import resolve_knowledge_base_paths
from srkg.module_partitioning import (
    DEFAULT_RELATIONS,
    PartitionSearchConfig,
    analyse_partition,
    build_domain_graph,
    format_partition_report,
    search_module_partitions,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate and compare candidate module partitions without changing KB data.",
    )
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--relations", nargs="+", default=list(DEFAULT_RELATIONS))
    parser.add_argument("--module-counts", nargs="+", type=int, default=[4, 5, 6])
    parser.add_argument("--min-size", type=int, default=4)
    parser.add_argument("--max-size", type=int, default=16)
    parser.add_argument("--restarts", type=int, default=8)
    parser.add_argument("--random-seed", type=int, default=0)
    parser.add_argument("--candidates-per-count", type=int, default=5)
    parser.add_argument(
        "--relation-weight",
        action="append",
        default=[],
        metavar="RELATION=WEIGHT",
        help="Override a relation's cohesion weight; may be repeated.",
    )
    parser.add_argument(
        "--ignore-authored-seed",
        action="store_true",
        help="Do not use the current authored modules as one search starting point.",
    )
    parser.add_argument(
        "--evaluate-members",
        metavar="CSV",
        help="Evaluate and use a module_id,concept_id candidate CSV as a search seed.",
    )
    parser.add_argument(
        "--evaluate-only",
        action="store_true",
        help="Report --evaluate-members exactly and skip candidate search.",
    )
    parser.add_argument(
        "--show-boundary-edges",
        action="store_true",
        help="List the concrete concept edges under every boundary module pair.",
    )
    parser.add_argument("--out", help="Optional Markdown report path; stdout is always written.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    paths = resolve_knowledge_base_paths(args.data_root)
    nodes_df = pd.read_csv(paths.nodes).fillna("")
    edges_df = pd.read_csv(paths.edges).fillna("")
    weights = _parse_relation_weights(args.relation_weight)
    graph = build_domain_graph(
        nodes_df,
        edges_df,
        args.domain,
        args.relations,
        relation_weights=weights,
    )
    seeds = []
    evaluated = None
    if args.evaluate_members:
        candidate_df = pd.read_csv(args.evaluate_members).fillna("")
        required = {"module_id", "concept_id"}
        if not required.issubset(candidate_df.columns):
            raise ValueError(
                f"{args.evaluate_members} must contain module_id and concept_id columns"
            )
        domain_ids = set(graph.concept_ids)
        selected_candidate = candidate_df[
            candidate_df["concept_id"].astype(str).isin(domain_ids)
        ]
        proposed = dict(zip(
            selected_candidate["concept_id"].astype(str),
            selected_candidate["module_id"].astype(str),
        ))
        evaluated = analyse_partition(graph, proposed, origin="supplied editorial candidate")
        seeds.append(proposed)
    elif args.evaluate_only:
        raise ValueError("--evaluate-only requires --evaluate-members")
    if not args.ignore_authored_seed and paths.module_members:
        members_df = pd.read_csv(paths.module_members).fillna("")
        domain_ids = set(graph.concept_ids)
        selected = members_df[members_df["concept_id"].astype(str).isin(domain_ids)]
        authored = dict(zip(
            selected["concept_id"].astype(str),
            selected["module_id"].astype(str),
        ))
        if set(authored) == domain_ids:
            seeds.append(authored)

    config = PartitionSearchConfig(
        module_counts=tuple(args.module_counts),
        min_module_size=args.min_size,
        max_module_size=args.max_size,
        restarts=args.restarts,
        random_seed=args.random_seed,
        candidates_per_count=args.candidates_per_count,
    )
    if args.evaluate_only:
        candidates = (evaluated,)
    else:
        searched = search_module_partitions(graph, config, seed_partitions=seeds)
        candidates = ((evaluated,) if evaluated is not None else ()) + searched
    report = format_partition_report(
        graph,
        candidates,
        include_boundary_edges=args.show_boundary_edges,
    )
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")


def _parse_relation_weights(values: list[str]) -> dict[str, float]:
    weights = {}
    for value in values:
        relation, separator, raw_weight = value.partition("=")
        if not separator or not relation or not raw_weight:
            raise ValueError(f"Expected RELATION=WEIGHT, got {value!r}")
        weight = float(raw_weight)
        if not weight > 0:
            raise ValueError(f"Relation weights must be positive: {value!r}")
        weights[relation] = weight
    return weights


if __name__ == "__main__":
    main()
