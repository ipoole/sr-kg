#!/usr/bin/env python3
"""Capture/compare assembled content during storage-only migrations."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from srkg.kb import load_knowledge_base


def snapshot(root):
    kb = load_knowledge_base(root)
    def rows(frame):
        values = frame.fillna("").astype(str).to_dict("records")
        return sorted(values, key=lambda value: json.dumps(value, sort_keys=True))
    values = {"concepts": kb.concept_data(), "modules": kb.module_data(),
              "tutorials": kb.tutorial_data(), "layout": kb.published_layout.to_viewer_data(),
              "nodes": rows(kb.nodes_df), "edges": rows(kb.edges_df), "edge_key": kb.edge_key}
    return {key: hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            for key, value in values.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", default="data")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    current = snapshot(args.data_root)
    if args.write:
        args.write.write_text(json.dumps(current, indent=2) + "\n")
    else:
        expected = json.loads(args.check.read_text())
        differences = [key for key in expected if current.get(key) != expected[key]]
        if differences:
            raise SystemExit("Changed snapshot components: " + ", ".join(differences))
    print(json.dumps(current, indent=2))


if __name__ == "__main__":
    main()
