"""Domain-owned module motifs and their accessible titles."""
from functools import partial
from pathlib import Path
from srkg.svg_graphics.module_frames import landscape_svg

ASSETS = {'sr.spacetime_foundations': 'sr1_spacetime_lorentz_{variant}.svg', 'sr.relativistic_mechanics': 'sr2_relativistic_particle_{variant}.svg', 'sr.variational_and_field_theory': 'sr3_action_field_{variant}.svg', 'sr.electromagnetic_structure_gauge_and_stress_energy': 'sr4_covariant_em_{variant}.svg', 'sr.field_dynamics_conservation_and_radiation': 'sr5_field_radiation_{variant}.svg'}
TITLES = {'sr.spacetime_foundations': 'SR-1 Spacetime and Lorentz Symmetry', 'sr.relativistic_mechanics': 'SR-2 Relativistic Particle Mechanics', 'sr.variational_and_field_theory': 'SR-3 Action and Field Theory', 'sr.electromagnetic_structure_gauge_and_stress_energy': 'SR-4 Covariant Electromagnetism', 'sr.field_dynamics_conservation_and_radiation': 'SR-5 Field Dynamics and Radiation'}


def create_module(module_id, variant="icon"):
    variant = "detail" if variant == "detail" else "icon"
    source = (Path(__file__).with_name("module_assets") / ASSETS[module_id].format(variant=variant)).read_text(encoding="utf-8")
    return landscape_svg(module_id, TITLES[module_id], source, variant)


MODULE_CREATORS = {module_id: partial(create_module, module_id) for module_id in ASSETS}
