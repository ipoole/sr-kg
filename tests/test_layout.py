import pandas as pd
import pytest

from srkg.layout import (
    build_hierarchy_levels,
    build_hierarchy_positions,
    concept_sort_key,
    curved_row_rise,
    order_nodes_within_levels,
    parse_layer_value,
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


@pytest.mark.parametrize(
    ("node_id", "layer", "expected"),
    [
        ("3.4", " 2 ", 2),
        ("3.4", 2.9, 2),
        ("3.4", "", 3),
        ("3.4", None, 3),
        ("3.4", "0", 3),
        ("3.4", "-1", 3),
        ("bad-id", "", 0),
        ("0.1", "", 0),
    ],
)
def test_parse_layer_value_prefers_positive_layer_then_id_prefix(
    node_id,
    layer,
    expected,
):
    assert parse_layer_value(node_id, layer) == expected


def test_build_hierarchy_levels_maps_layer_one_to_bottom_row():
    nodes_df = pd.DataFrame([
        {"id": "1.1", "layer": "1"},
        {"id": "2.1", "layer": "2"},
        {"id": "4.1", "layer": "4"},
        {"id": "fallback-from-id", "layer": ""},
        {"id": "3.5", "layer": ""},
    ])

    levels = build_hierarchy_levels(nodes_df)

    assert levels == {
        "1.1": 3,
        "2.1": 2,
        "4.1": 0,
        "fallback-from-id": 4,
        "3.5": 1,
    }


def test_build_hierarchy_levels_puts_unlayered_nodes_at_bottom_when_no_layers_exist():
    nodes_df = pd.DataFrame([
        {"id": "appendix", "layer": ""},
        {"id": "0.1", "layer": "0"},
    ])

    assert build_hierarchy_levels(nodes_df) == {
        "appendix": 0,
        "0.1": 0,
    }


def test_curved_row_rise_keeps_initial_nodes_flat_then_curves_and_caps():
    rises = [
        curved_row_rise(
            index,
            100,
            flat_count=2,
            target_node=4,
            target_rise_fraction=1.0,
            max_rise_fraction=1.5,
            exponent=2.0,
        )
        for index in range(5)
    ]

    assert rises == [0.0, 0.0, 25.0, 100.0, 150.0]


def test_curved_row_rise_clamps_invalid_shape_parameters_to_safe_values():
    assert curved_row_rise(
        1,
        100,
        flat_count=0,
        target_node=0,
        target_rise_fraction=1.0,
        max_rise_fraction=2.0,
        exponent=0,
    ) == 100.0
    assert curved_row_rise(
        3,
        100,
        flat_count=2,
        target_node=4,
        target_rise_fraction=-1.0,
        max_rise_fraction=2.0,
        exponent=2.0,
    ) == 0.0
    assert curved_row_rise(
        3,
        100,
        flat_count=2,
        target_node=4,
        target_rise_fraction=1.0,
        max_rise_fraction=-1.0,
        exponent=2.0,
    ) == 0.0


def test_order_nodes_within_levels_sorts_each_level_by_numeric_concept_id():
    nodes_by_level = {
        2: ["2.10", "2.2", "2.1"],
        0: ["10.1", "3.12", "3.2"],
    }
    hierarchy_levels = {
        "2.10": 2,
        "2.2": 2,
        "2.1": 2,
        "10.1": 0,
        "3.12": 0,
        "3.2": 0,
    }
    edges_df = pd.DataFrame([
        {"source": "2.10", "target": "2.1"},
    ])

    assert order_nodes_within_levels(nodes_by_level, hierarchy_levels, edges_df) == {
        2: ["2.1", "2.2", "2.10"],
        0: ["3.2", "3.12", "10.1"],
    }


def test_build_hierarchy_positions_left_aligns_sorted_rows_and_applies_curve():
    hierarchy_levels = {
        "2.10": 0,
        "2.1": 0,
        "2.2": 0,
        "2.3": 0,
        "2.4": 0,
        "1.2": 1,
        "1.1": 1,
    }

    positions = build_hierarchy_positions(
        hierarchy_levels,
        x_spacing=10,
        y_spacing=100,
        row_curve_flat_count=2,
        row_curve_target_node=4,
        row_curve_target_rise_fraction=1.0,
        row_curve_max_rise_fraction=1.5,
        row_curve_exponent=2.0,
    )

    assert positions == {
        "2.1": (0, 0.0),
        "2.2": (10, 0.0),
        "2.3": (20, -25.0),
        "2.4": (30, -100.0),
        "2.10": (40, -150.0),
        "1.1": (0, 100.0),
        "1.2": (10, 100.0),
    }


def test_build_hierarchy_positions_keeps_row_stagger_as_ignored_compatibility_arg():
    hierarchy_levels = {
        "1.2": 0,
        "1.1": 0,
        "1.3": 0,
    }

    without_stagger = build_hierarchy_positions(
        hierarchy_levels,
        x_spacing=10,
        y_spacing=100,
        row_stagger=None,
    )
    with_stagger = build_hierarchy_positions(
        hierarchy_levels,
        x_spacing=10,
        y_spacing=100,
        row_stagger=999,
    )

    assert with_stagger == without_stagger
