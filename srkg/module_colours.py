"""Stable, restrained viewer colours for authored modules."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from srkg.model import Module


DOMAIN_PALETTES = {
    "sr": (
        ("#dcecf5", "#285a76"),
        ("#cde3f0", "#285a76"),
        ("#bed9ea", "#285a76"),
        ("#afd0e4", "#285a76"),
        ("#a0c6de", "#285a76"),
    ),
    "gr": (
        ("#f3e2db", "#7b4938"),
        ("#efd8ce", "#7b4938"),
        ("#eacdc1", "#7b4938"),
        ("#e5c2b4", "#7b4938"),
        ("#dfb7a7", "#7b4938"),
        ("#d9ac99", "#7b4938"),
    ),
    "math": (
        ("#dfedda", "#45683d"),
        ("#cfe4c8", "#45683d"),
    ),
}
FALLBACK_PALETTE = (
    ("#e4e9ef", "#536273"),
    ("#d7e0e8", "#536273"),
    ("#cad6e0", "#536273"),
)
UNKNOWN_MODULE_VISUAL = {
    "module_id": "",
    "background": "#e4e7eb",
    "border": "#59636e",
}


def build_module_visuals_by_concept(
    modules: Iterable[Module],
) -> dict[str, dict[str, str]]:
    """Return stable module colour metadata keyed by concept ID."""
    by_domain: dict[str, list[Module]] = defaultdict(list)
    for module in modules:
        by_domain[str(module.domain)].append(module)

    result: dict[str, dict[str, str]] = {}
    for domain in sorted(by_domain):
        palette = DOMAIN_PALETTES.get(domain, FALLBACK_PALETTE)
        ordered = sorted(
            by_domain[domain],
            key=lambda module: (module.sequence, module.module_id),
        )
        for index, module in enumerate(ordered):
            background, border = palette[index % len(palette)]
            for concept_id in module.members:
                result[str(concept_id)] = {
                    "module_id": str(module.module_id),
                    "background": background,
                    "border": border,
                }
    return result
