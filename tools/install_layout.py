#!/usr/bin/env python3
"""Install exported coordinates into one explicitly selected authored domain."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from srkg.domain_sources import owning_source_paths
from srkg.kb import load_knowledge_base
from srkg.layout_persistence import PublishedLayout, load_published_layout


def install_layout(data_root, domain, source, revision):
    paths = owning_source_paths(data_root, domain)
    if not str(revision).strip():
        raise ValueError("A non-empty layout revision is required")
    kb = load_knowledge_base(data_root, include_graphics=False)
    own_concepts = {concept.id for concept in kb.concepts if concept.domain == domain}
    own_modules = {module.module_id for module in kb.modules if module.domain == domain}
    if not own_concepts:
        raise ValueError(f"Unknown/empty domain: {domain}")
    incoming = load_published_layout(Path(source), concept_ids=kb.concept_index, module_ids=kb.module_index)
    previous = load_published_layout(paths.layout, concept_ids=own_concepts, module_ids=own_modules)
    result = PublishedLayout(revision=str(revision).strip(),
        concepts=dict(previous.concepts) | {key: value for key, value in incoming.concepts.items() if key in own_concepts},
        modules=dict(previous.modules) | {key: value for key, value in incoming.modules.items() if key in own_modules})
    paths.layout.write_text(json.dumps(result.to_viewer_data(), indent=2) + "\n", encoding="utf-8")
    return paths.layout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    print(install_layout(args.data_root, args.domain, args.layout, args.revision))


if __name__ == "__main__":
    main()
