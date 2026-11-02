"""Stable, restrained viewer colours for authored modules."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from srkg.model import Module


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
    *,
    palettes: dict | None = None,
) -> dict[str, dict[str, str]]:
    """Return stable module colour metadata keyed by concept ID."""
    by_domain: dict[str, list[Module]] = defaultdict(list)
    for module in modules:
        by_domain[str(module.domain)].append(module)

    result: dict[str, dict[str, str]] = {}
    for domain in sorted(by_domain):
        palette = (palettes or {}).get(domain) or FALLBACK_PALETTE
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
