"""Edge relation semantics, colours, and display helpers."""

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


def make_edge_tooltip(relation: str, note: str, width: int = EDGE_TOOLTIP_LINE_WIDTH) -> str:
    """Build a readable wrapped tooltip for an edge relation and optional note."""
    relation_text = html.escape(relation)
    note = str(note or "").strip()
    if not note:
        return relation_text

    wrapped_note = textwrap.wrap(
        note,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    wrapped_note_text = "\n".join(html.escape(line) for line in wrapped_note)
    return f"{relation_text}:\n{wrapped_note_text}"
