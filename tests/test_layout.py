import pandas as pd

from srkg.layout import (
    build_concept_sort_keys,
    build_flat_positions,
    concept_display_id,
    concept_sort_key,
)


def test_concept_sort_key_orders_dotted_ids_numerically():
    concept_ids = ["3.10", "3.2", "2.12", "2.2.1", "2.2", "10.1"]

    assert sorted(concept_ids, key=concept_sort_key) == [
        "2.2",
        "2.2.1",
        "2.12",
        "3.2",
        "3.10",
        "10.1",
    ]


def test_concept_sort_key_places_non_numeric_ids_after_numeric_ids():
    concept_ids = ["appendix", "1.2", "bad.id", "1.10"]

    assert sorted(concept_ids, key=concept_sort_key) == [
        "1.2",
        "1.10",
        "appendix",
        "bad.id",
    ]


def test_concept_sort_key_orders_module_prefixed_ids_numerically():
    concept_ids = ["SR-2.1", "SR-1.10", "SR-1.2", "GR-1.1"]

    assert sorted(concept_ids, key=concept_sort_key) == [
        "GR-1.1",
        "SR-1.2",
        "SR-1.10",
        "SR-2.1",
    ]


def test_concept_display_id_falls_back_to_semantic_id():
    assert concept_display_id({"id": "sr.alpha", "display_id": " SR-1.2 "}) == "SR-1.2"
    assert concept_display_id({"id": "sr.alpha", "display_id": ""}) == "sr.alpha"


def test_build_concept_sort_keys_uses_display_ids():
    nodes_df = pd.DataFrame([
        {"id": "test.gamma", "display_id": "2.10"},
        {"id": "test.alpha", "display_id": "2.1"},
        {"id": "test.beta", "display_id": "2.2"},
    ])

    keys = build_concept_sort_keys(nodes_df)

    assert sorted(keys, key=keys.get) == ["test.alpha", "test.beta", "test.gamma"]


def test_build_flat_positions_is_sorted_centred_and_wrapped():
    nodes_df = pd.DataFrame([
        {"id": "test.five", "display_id": "TEST-1.5"},
        {"id": "test.two", "display_id": "TEST-1.2"},
        {"id": "test.four", "display_id": "TEST-1.4"},
        {"id": "test.one", "display_id": "TEST-1.1"},
        {"id": "test.three", "display_id": "TEST-1.3"},
    ])

    assert build_flat_positions(
        nodes_df,
        x_spacing=100,
        y_spacing=80,
        max_columns=3,
    ) == {
        "test.one": (-100.0, -40.0),
        "test.two": (0.0, -40.0),
        "test.three": (100.0, -40.0),
        "test.four": (-50.0, 40.0),
        "test.five": (50.0, 40.0),
    }


def test_build_flat_positions_handles_an_empty_frame():
    assert build_flat_positions(pd.DataFrame(columns=["id", "display_id"])) == {}
