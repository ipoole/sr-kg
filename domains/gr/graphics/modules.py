"""Domain-owned module motifs and their accessible titles."""
from functools import partial
from pathlib import Path
from srkg.svg_graphics.module_frames import landscape_svg

ASSETS = {'gr.foundations_and_spacetime_geometry': 'gr1_curved_spacetime_{variant}.svg', 'gr.connections_transport_and_motion': 'gr2_geometric_compass_{variant}.svg', 'gr.curvature_and_gravitational_action': 'gr3_curvature_action_{variant}.svg', 'gr.matter_and_einstein_equations': 'gr4_matter_einstein_{variant}.svg', 'gr.weak_field_and_classical_tests': 'gr5_weak_field_{variant}.svg', 'gr.schwarzschild_geometry_and_black_holes': 'gr6_black_hole_{variant}.svg'}
TITLES = {'gr.foundations_and_spacetime_geometry': 'GR-1 Foundations of Curved Spacetime', 'gr.connections_transport_and_motion': 'GR-2 Connections and Geodesics', 'gr.curvature_and_gravitational_action': 'GR-3 Curvature and Gravitational Action', 'gr.matter_and_einstein_equations': 'GR-4 Matter and Einstein Equations', 'gr.weak_field_and_classical_tests': 'GR-5 Weak-Field Gravity', 'gr.schwarzschild_geometry_and_black_holes': 'GR-6 Schwarzschild Black Holes'}


def create_module(module_id, variant="icon"):
    variant = "detail" if variant == "detail" else "icon"
    source = (Path(__file__).with_name("module_assets") / ASSETS[module_id].format(variant=variant)).read_text(encoding="utf-8")
    return landscape_svg(module_id, TITLES[module_id], source, variant)


MODULE_CREATORS = {module_id: partial(create_module, module_id) for module_id in ASSETS}
