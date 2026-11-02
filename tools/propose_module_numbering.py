#!/usr/bin/env python3
"""Write a reviewable proposal for module-based concept display IDs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srkg.kb import load_knowledge_base
from srkg.domain_sources import owning_source_paths
from srkg.module_layout import propose_module_concept_numbering


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Propose module-prefixed display IDs without changing runtime data.",
    )
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--domain", help="Limit proposals; required with --apply for a domain collection")
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the proposal to nodes, module members, and graphic designs.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    paths = owning_source_paths(args.data_root, args.domain) if args.apply else None
    kb = load_knowledge_base(args.data_root, include_graphics=False)
    proposals = propose_module_concept_numbering(
        kb.nodes_df,
        kb.edges_df,
        kb.modules,
    )
    if args.domain:
        own_ids = {concept.id for concept in kb.concepts if concept.domain == args.domain}
        if not own_ids:
            raise ValueError(f"Unknown/empty domain: {args.domain}")
        proposals = [proposal for proposal in proposals if proposal.concept_id in own_ids]
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "module_id",
                "module_title",
                "concept_id",
                "old_display_id",
                "proposed_display_id",
                "proposed_member_sequence",
                "dependency_rank",
                "ordering_rationale",
            ]
        )
        for proposal in proposals:
            writer.writerow(
                [
                    proposal.module_id,
                    proposal.module_title,
                    proposal.concept_id,
                    proposal.old_display_id,
                    proposal.new_display_id,
                    proposal.member_sequence,
                    proposal.dependency_rank,
                    proposal.rationale,
                ]
            )
    print(f"Wrote {len(proposals)} proposed concept IDs to {output}")
    if args.apply:
        _apply_proposals(kb, proposals, paths=paths)
        print("Applied proposed display IDs and member sequences to runtime data")


def _apply_proposals(kb, proposals, *, paths=None) -> None:
    paths = paths or owning_source_paths(kb.paths.root)
    proposal_by_id = {proposal.concept_id: proposal for proposal in proposals}

    nodes = pd.read_csv(paths.nodes, dtype=str, keep_default_na=False)
    nodes["display_id"] = nodes["id"].astype(str).map(
        {key: proposal.new_display_id for key, proposal in proposal_by_id.items()}
    ).fillna(nodes["display_id"])
    nodes = nodes.drop(columns=["layer", "layer_title"], errors="ignore")
    nodes.to_csv(paths.nodes, index=False)

    members = pd.read_csv(paths.module_members, dtype=str, keep_default_na=False)
    members["sequence"] = members["concept_id"].astype(str).map(
        {key: str(proposal.member_sequence) for key, proposal in proposal_by_id.items()}
    ).fillna(members["sequence"])
    module_order = {
        module.module_id: index for index, module in enumerate(kb.modules)
    }
    members["_module_order"] = members["module_id"].map(module_order)
    members["_sequence_order"] = members["sequence"].astype(int)
    members = members.sort_values(
        ["_module_order", "_sequence_order", "concept_id"], kind="stable"
    ).drop(columns=["_module_order", "_sequence_order"])
    members.to_csv(paths.module_members, index=False)

    if paths.graphic_designs is not None:
        designs = pd.read_csv(paths.graphic_designs, dtype=str, keep_default_na=False)
        designs["display_id"] = designs["id"].astype(str).map(
            {key: proposal.new_display_id for key, proposal in proposal_by_id.items()}
        ).fillna(designs["display_id"])
        designs = designs.drop(columns=["layer"], errors="ignore")
        designs.to_csv(paths.graphic_designs, index=False)


if __name__ == "__main__":
    main()
