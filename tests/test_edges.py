from srkg.config import EDGE_COLOURS, UNDIRECTED_EDGE_COLOUR
from srkg.edges import (
    build_edge_colour_map,
    enrich_edge_key_with_colours,
    make_edge_tooltip,
    relation_is_directed,
    stable_edge_colour,
)


def test_build_edge_colour_map_assigns_directed_colours_in_sorted_order():
    edge_key = {
        "ZETA": {"directed": True},
        "ALPHA": {"directed": True},
        "RELATED": {"directed": False},
    }

    colours = build_edge_colour_map(edge_key)

    assert colours == {
        "ALPHA": EDGE_COLOURS[0],
        "ZETA": EDGE_COLOURS[1],
        "RELATED": UNDIRECTED_EDGE_COLOUR,
    }


def test_build_edge_colour_map_treats_missing_directed_metadata_as_directed():
    colours = build_edge_colour_map({
        "USES": {},
        "EXPLAINS": {"directed": True},
    })

    assert colours["EXPLAINS"] == EDGE_COLOURS[0]
    assert colours["USES"] == EDGE_COLOURS[1]


def test_stable_edge_colour_is_repeatable_palette_colour():
    first = stable_edge_colour("UNKNOWN_RELATION")
    second = stable_edge_colour("UNKNOWN_RELATION")

    assert first == second
    assert first in EDGE_COLOURS


def test_enrich_edge_key_with_colours_preserves_metadata_and_adds_colour():
    edge_key = {
        "DEPENDS_ON": {
            "relation": "DEPENDS_ON",
            "directed": True,
            "meaning": "source depends on target",
        },
        "RELATED": {
            "relation": "RELATED",
            "directed": False,
        },
    }
    colour_map = {"DEPENDS_ON": "#123456"}

    enriched = enrich_edge_key_with_colours(edge_key, colour_map)

    assert enriched["DEPENDS_ON"] == {
        "relation": "DEPENDS_ON",
        "directed": True,
        "meaning": "source depends on target",
        "colour": "#123456",
    }
    assert enriched["RELATED"]["directed"] is False
    assert enriched["RELATED"]["colour"] == EDGE_COLOURS[0]
    assert "colour" not in edge_key["DEPENDS_ON"]


def test_relation_is_directed_defaults_to_true():
    edge_key = {
        "DIRECTED": {"directed": True},
        "UNDIRECTED": {"directed": False},
    }

    assert relation_is_directed("DIRECTED", edge_key) is True
    assert relation_is_directed("UNDIRECTED", edge_key) is False
    assert relation_is_directed("MISSING", edge_key) is True


def test_make_edge_tooltip_returns_empty_string_for_blank_notes():
    assert make_edge_tooltip("RELATION", "") == ""
    assert make_edge_tooltip("RELATION", "   ") == ""
    assert make_edge_tooltip("RELATION", None) == ""


def test_make_edge_tooltip_wraps_and_escapes_note_text():
    tooltip = make_edge_tooltip(
        "RELATION",
        "alpha beta <tag> gamma delta",
        width=12,
    )

    assert tooltip.splitlines() == [
        "alpha beta",
        "&lt;tag&gt; gamma",
        "delta",
    ]
