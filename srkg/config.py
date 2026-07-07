"""Shared configuration constants for the SR knowledge graph generator.

This module is intentionally dependency-free. It defines the stable values
used across data validation, layout, PyVis rendering, and injected viewer
assets: colours, required CSV columns, layout spacing, node collision geometry,
label sizing, and edge display defaults.

Keep this module limited to simple constants so every other ``srkg`` module can
import it without creating dependency cycles.
"""

LAYER_COLOURS = [
    "#e6194b", "#f58231", "#ffe119", "#3cb44b", "#46f0f0",
    "#4363d8", "#911eb4", "#f032e6", "#fabed4", "#9a6324",
    "#808080", "#469990", "#dcbeff", "#aaffc3"
]

EDGE_COLUMNS = ("source", "target", "relation", "note")
EDGE_KEY_COLUMNS = ("relation", "directed", "category", "meaning", "example")
EDGE_TOOLTIP_LINE_WIDTH = 50
EDGE_WIDTH = 5.0
LAYOUT_X_SPACING = 350
LAYOUT_Y_SPACING = 400
LAYOUT_ROW_STAGGER = 35
NODE_COLLISION_WIDTH = 280
NODE_COLLISION_HEIGHT = 170
NODE_CIRCLE_BASE_SIZE = 60
NODE_CIRCLE_IMPORTANCE_SCALE = 4.0
NODE_LABEL_WIDTH = 250
NODE_LABEL_FONT_SIZE = 32
NODE_LABEL_FONT_WEIGHT = 700
UNDIRECTED_EDGE_COLOUR = "#c8c8c8"
EDGE_COLOURS = [
    "#1f77b4",
    "#d62728",
    "#2ca02c",
    "#9467bd",
    "#ff7f0e",
    "#17becf",
    "#8c564b",
    "#e377c2",
]
