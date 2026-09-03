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
from srkg.module_layout import propose_module_concept_numbering


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Propose module-prefixed display IDs without changing runtime data.",
    )
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the proposal to nodes, module members, and graphic designs.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    kb = load_knowledge_base(args.data_root)
    proposals = propose_module_concept_numbering(
        kb.nodes_df,
        kb.edges_df,
        kb.modules,
    )
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
        _apply_proposals(kb, proposals)
        print("Applied proposed display IDs and member sequences to runtime data")


def _apply_proposals(kb, proposals) -> None:
    proposal_by_id = {proposal.concept_id: proposal for proposal in proposals}

    nodes = pd.read_csv(kb.paths.nodes, dtype=str, keep_default_na=False)
    nodes["display_id"] = nodes["id"].astype(str).map(
        lambda concept_id: proposal_by_id[concept_id].new_display_id
    )
    nodes = nodes.drop(columns=["layer", "layer_title"], errors="ignore")
    nodes.to_csv(kb.paths.nodes, index=False)

    members = pd.read_csv(kb.paths.module_members, dtype=str, keep_default_na=False)
    members["sequence"] = members["concept_id"].astype(str).map(
        lambda concept_id: proposal_by_id[concept_id].member_sequence
    )
    module_order = {
        module.module_id: index for index, module in enumerate(kb.modules)
    }
    members["_module_order"] = members["module_id"].map(module_order)
    members["_sequence_order"] = members["sequence"].astype(int)
    members = members.sort_values(
        ["_module_order", "_sequence_order", "concept_id"], kind="stable"
    ).drop(columns=["_module_order", "_sequence_order"])
    members.to_csv(kb.paths.module_members, index=False)

    if kb.paths.graphic_designs is not None:
        designs = pd.read_csv(kb.paths.graphic_designs, dtype=str, keep_default_na=False)
        designs["display_id"] = designs["id"].astype(str).map(
            lambda concept_id: proposal_by_id[concept_id].new_display_id
        )
        designs = designs.drop(columns=["layer"], errors="ignore")
        designs.to_csv(kb.paths.graphic_designs, index=False)


if __name__ == "__main__":
    main()
