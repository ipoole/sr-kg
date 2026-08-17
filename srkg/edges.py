"""Edge relation semantics, colours, and display helpers.

This module interprets relation metadata loaded from ``edges_key.csv``. It
decides whether a relation is directed, assigns repeatable colours, enriches
relation metadata for the viewer UI, and formats edge hover text.

It is intentionally independent of graph layout, PyVis network construction,
and CSV loading. The only project dependency should be ``srkg.config``.
"""

import hashlib
import html
import textwrap

from srkg.config import (
    EDGE_COLOURS,
    EDGE_TOOLTIP_LINE_WIDTH,
    UNDIRECTED_EDGE_COLOUR,
)


def build_edge_colour_map(edge_key: dict[str, dict[str, str | bool]]) -> dict[str, str]:
    """Assign stable colours to relation types, using grey for undirected edges."""
    colour_map = {}
    directed_relations = sorted(
        relation
        for relation, metadata in edge_key.items()
        if bool(metadata.get("directed", True))
    )

    for index, relation in enumerate(directed_relations):
        colour_map[relation] = EDGE_COLOURS[index % len(EDGE_COLOURS)]

    for relation, metadata in edge_key.items():
        if not bool(metadata.get("directed", True)):
            colour_map[relation] = UNDIRECTED_EDGE_COLOUR

    return colour_map


def stable_edge_colour(relation: str) -> str:
    """Return a repeatable fallback colour for relation names not present in the key."""
    digest = hashlib.sha256(relation.encode("utf-8")).digest()
    return EDGE_COLOURS[digest[0] % len(EDGE_COLOURS)]


def enrich_edge_key_with_colours(
    edge_key: dict[str, dict[str, str | bool]],
    edge_colour_map: dict[str, str],
) -> dict[str, dict[str, str | bool]]:
    """Add generated display colours to edge-key metadata shown in the UI."""
    return {
        relation: {
            **metadata,
            "colour": edge_colour_map.get(relation, EDGE_COLOURS[0]),
        }
        for relation, metadata in edge_key.items()
    }


def relation_is_directed(relation: str, edge_key: dict[str, dict[str, str | bool]]) -> bool:
    """Return whether a relation should be treated as directed."""
    return bool(edge_key.get(relation, {}).get("directed", True))


def make_edge_tooltip(
    relation: str,
    note: str,
    width: int = EDGE_TOOLTIP_LINE_WIDTH,
    *,
    source_label: str | None = None,
    target_label: str | None = None,
) -> str:
    """Build readable wrapped tooltip text for an edge note."""
    note = str(note or "").strip()
    if not note:
        return ""

    wrapped_note = textwrap.wrap(
        note,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    tooltip_lines = []
    source_label = str(source_label or "").strip()
    target_label = str(target_label or "").strip()
    if source_label and target_label:
        tooltip_lines.append(
            f"{html.escape(source_label)} {html.escape(str(relation))} {html.escape(target_label)}"
        )
        tooltip_lines.append("")
    tooltip_lines.extend(html.escape(line) for line in wrapped_note)
    return "\n".join(tooltip_lines)
