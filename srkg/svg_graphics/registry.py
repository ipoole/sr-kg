"""Registry and public dispatch helpers for concept SVG graphics."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from srkg.svg_graphics.concepts import (
    create_10_1_wave_equation,
    create_10_2_electromagnetic_waves,
    create_10_3_radiation_reaction,
    create_11_1_lorentz_invariance,
    create_11_2_gauge_fixing,
    create_1_1_inertial_frames,
    create_1_2_constancy_of_speed_of_light,
    create_1_3_principle_of_relativity,
    create_2_2_spacetime_event,
    create_2_3_principle_of_locality,
    create_3_1_metric_tensor,
    create_3_2_spacetime_interval,
    create_3_3_lorentz_transformations,
    create_3_4_light_cone,
    create_3_5_minkowski_diagram,
    create_4_1_proper_time,
    create_4_2_four_vectors,
    create_4_3_position_four_vector,
    create_4_4_velocity_four_vector,
    create_4_5_momentum_four_vector,
    create_4_6_mass_energy_equivalence,
    create_5_1_lagrangian,
    create_5_2_action_principle,
    create_5_3_euler_lagrange,
    create_5_4_canonical_momentum,
    create_5_5_hamiltonian_formalism,
    create_5_6_noethers_theorem,
    create_6_1_scalar_field,
    create_6_2_vector_field,
    create_6_3_field_lagrangian,
    create_6_4_field_equations,
    create_7_1_vector_potential,
    create_7_2_field_tensor,
    create_7_3_electric_field,
    create_7_4_magnetic_field,
    create_7_5_electromagnetic_field,
    create_7_6_four_current,
    create_7_7_maxwells_equations,
    create_8_1_gauge_invariance,
    create_8_3_minimal_coupling,
    create_8_4_lorentz_force_law,
    create_8_5_charge_conservation,
    create_8_6_lorenz_gauge,
    create_9_1_energy_momentum_tensor,
    create_9_2_poynting_vector,
    create_9_3_em_stress_energy,
    create_9_4_em_energy_density,
)

IMPLEMENTED_NODE_IDS = (
    '1.1',
    '1.2',
    '1.3',
    '2.2',
    '2.3',
    '3.1',
    '3.2',
    '3.3',
    '3.4',
    '3.5',
    '4.1',
    '4.2',
    '4.3',
    '4.4',
    '4.5',
    '4.6',
    '5.1',
    '5.2',
    '5.3',
    '5.4',
    '5.5',
    '5.6',
    '6.1',
    '6.2',
    '6.3',
    '6.4',
    '7.1',
    '7.2',
    '7.3',
    '7.4',
    '7.5',
    '7.6',
    '7.7',
    '8.1',
    '8.3',
    '8.4',
    '8.5',
    '8.6',
    '9.1',
    '9.2',
    '9.3',
    '9.4',
    '10.1',
    '10.2',
    '10.3',
    '11.1',
    '11.2',
)

CREATORS: dict[str, Callable[[str], str]] = {
    '1.1': create_1_1_inertial_frames,
    '1.2': create_1_2_constancy_of_speed_of_light,
    '1.3': create_1_3_principle_of_relativity,
    '2.2': create_2_2_spacetime_event,
    '2.3': create_2_3_principle_of_locality,
    '3.1': create_3_1_metric_tensor,
    '3.2': create_3_2_spacetime_interval,
    '3.3': create_3_3_lorentz_transformations,
    '3.4': create_3_4_light_cone,
    '3.5': create_3_5_minkowski_diagram,
    '4.1': create_4_1_proper_time,
    '4.2': create_4_2_four_vectors,
    '4.3': create_4_3_position_four_vector,
    '4.4': create_4_4_velocity_four_vector,
    '4.5': create_4_5_momentum_four_vector,
    '4.6': create_4_6_mass_energy_equivalence,
    '5.1': create_5_1_lagrangian,
    '5.2': create_5_2_action_principle,
    '5.3': create_5_3_euler_lagrange,
    '5.4': create_5_4_canonical_momentum,
    '5.5': create_5_5_hamiltonian_formalism,
    '5.6': create_5_6_noethers_theorem,
    '6.1': create_6_1_scalar_field,
    '6.2': create_6_2_vector_field,
    '6.3': create_6_3_field_lagrangian,
    '6.4': create_6_4_field_equations,
    '7.1': create_7_1_vector_potential,
    '7.2': create_7_2_field_tensor,
    '7.3': create_7_3_electric_field,
    '7.4': create_7_4_magnetic_field,
    '7.5': create_7_5_electromagnetic_field,
    '7.6': create_7_6_four_current,
    '7.7': create_7_7_maxwells_equations,
    '8.1': create_8_1_gauge_invariance,
    '8.3': create_8_3_minimal_coupling,
    '8.4': create_8_4_lorentz_force_law,
    '8.5': create_8_5_charge_conservation,
    '8.6': create_8_6_lorenz_gauge,
    '9.1': create_9_1_energy_momentum_tensor,
    '9.2': create_9_2_poynting_vector,
    '9.3': create_9_3_em_stress_energy,
    '9.4': create_9_4_em_energy_density,
    '10.1': create_10_1_wave_equation,
    '10.2': create_10_2_electromagnetic_waves,
    '10.3': create_10_3_radiation_reaction,
    '11.1': create_11_1_lorentz_invariance,
    '11.2': create_11_2_gauge_fixing,
}


def create_svg_graphic(node_id: str, variant: str = "icon") -> str | None:
    """Return an SVG XML string for a KG node id and variant, if known."""
    creator = CREATORS.get(str(node_id).strip())
    if creator is None:
        return None
    return creator(variant)


def save_svg_graphics(output_dir: str | Path = ".") -> None:
    """Write all currently implemented icon SVGs to files."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for node_id in IMPLEMENTED_NODE_IDS:
        svg = create_svg_graphic(node_id, variant="icon")
        if svg is not None:
            (output / f"image_{node_id.replace('.', '_')}.svg").write_text(svg, encoding="utf-8")


__all__ = ["CREATORS", "IMPLEMENTED_NODE_IDS", "create_svg_graphic", "save_svg_graphics"]
