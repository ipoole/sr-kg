"""Shared configuration constants for the SR knowledge graph generator.

This module is intentionally dependency-free. It defines the stable values
used across data validation, layout, PyVis rendering, and injected viewer
assets: colours, required CSV columns, layout spacing, node collision geometry,
label sizing, and edge display defaults.

Keep this module limited to simple constants so every other ``srkg`` module can
import it without creating dependency cycles.
"""

EDGE_COLUMNS = ("source", "target", "relation", "note")
EDGE_KEY_COLUMNS = ("relation", "directed", "category", "meaning", "example")
EDGE_TOOLTIP_LINE_WIDTH = 50
EDGE_WIDTH = 5.0
EDGE_HOVER_WIDTH = 9.0
EDGE_ARROW_ENDPOINT_OFFSET = 36
LAYOUT_X_SPACING = 350
LAYOUT_Y_SPACING = 400
NODE_COLLISION_WIDTH = 230
NODE_COLLISION_HEIGHT = 150
NODE_CIRCLE_BASE_SIZE = 90
NODE_CIRCLE_IMPORTANCE_SCALE = 4.0
NODE_LABEL_WIDTH = 250
NODE_LABEL_FONT_SIZE = 30
NODE_LABEL_FONT_WEIGHT = 600
NODE_LABEL_HIDE_BELOW_PX = 6
INFO_PANEL_WIDTH_MIN_PX = 420
INFO_PANEL_WIDTH_VIEWPORT_PERCENT = 34
INFO_PANEL_WIDTH_MAX_PX = 620
INFO_PANEL_TABLET_WIDTH_MAX_PX = 440
INFO_PANEL_TABLET_WIDTH_VIEWPORT_PERCENT = 42
INFO_PANEL_FONT_SIZE_PX = 18
INFO_PANEL_TABLET_FONT_SIZE_PX = 15
INFO_PANEL_MOBILE_FONT_SIZE_PX = 11
INFO_PANEL_TEXT_ZOOM_MIN_PX = 6
INFO_PANEL_TEXT_ZOOM_MAX_PX = 28
USER_NOTES_STORAGE_KEY = "srkg.userNotes.v1"
NOTE_EDITING_STORAGE_KEY = "srkg.noteEditing.v1"
SPLASH_DISMISSED_STORAGE_KEY = "srkg.splash.dismissed.v1"
GLOBAL_LAYOUT_STORAGE_KEY = "srkg.layout.global.v1"
STUDY_PROGRESS_STORAGE_KEY = "srkg.studyProgress.v1"
CONTENT_READ_PROGRESS_STORAGE_KEY = "srkg.contentReadProgress.v1"
PERSONAL_DATA_STORAGE_KEY = "srkg.personalData.v1"
PERSONAL_DATA_DEVICE_STORAGE_KEY = "srkg.personalData.device.v1"
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
