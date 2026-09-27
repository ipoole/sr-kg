"""Optional deterministic SVG graphics for authored modules."""

from __future__ import annotations

from pathlib import Path
import re


IMPLEMENTED_MODULE_IDS = (
    "sr.spacetime_foundations",
    "sr.relativistic_mechanics",
    "sr.variational_and_field_theory",
    "sr.electromagnetic_structure_gauge_and_stress_energy",
    "sr.field_dynamics_conservation_and_radiation",
    "gr.foundations_and_spacetime_geometry",
    "gr.connections_transport_and_motion",
    "gr.curvature_and_gravitational_action",
    "gr.matter_and_einstein_equations",
    "gr.weak_field_and_classical_tests",
    "gr.schwarzschild_geometry_and_black_holes",
)

_ASSET_ROOT = Path(__file__).with_name("svg_graphics") / "module_assets"
_ASSETS = {
    "sr.spacetime_foundations": "sr1_spacetime_lorentz_{variant}.svg",
    "sr.relativistic_mechanics": "sr2_relativistic_particle_{variant}.svg",
    "sr.variational_and_field_theory": "sr3_action_field_{variant}.svg",
    "sr.electromagnetic_structure_gauge_and_stress_energy": "sr4_covariant_em_{variant}.svg",
    "sr.field_dynamics_conservation_and_radiation": "sr5_field_radiation_{variant}.svg",
    "gr.foundations_and_spacetime_geometry": "gr1_curved_spacetime_{variant}.svg",
    "gr.connections_transport_and_motion": "gr2_geometric_compass_{variant}.svg",
    "gr.curvature_and_gravitational_action": "gr3_curvature_action_{variant}.svg",
    "gr.matter_and_einstein_equations": "gr4_matter_einstein_{variant}.svg",
    "gr.weak_field_and_classical_tests": "gr5_weak_field_{variant}.svg",
    "gr.schwarzschild_geometry_and_black_holes": "gr6_black_hole_{variant}.svg",
}
_TITLES = {
    "sr.spacetime_foundations": "SR-1 Spacetime and Lorentz Symmetry",
    "sr.relativistic_mechanics": "SR-2 Relativistic Particle Mechanics",
    "sr.variational_and_field_theory": "SR-3 Action and Field Theory",
    "sr.electromagnetic_structure_gauge_and_stress_energy": "SR-4 Covariant Electromagnetism",
    "sr.field_dynamics_conservation_and_radiation": "SR-5 Field Dynamics and Radiation",
    "gr.foundations_and_spacetime_geometry": "GR-1 Foundations of Curved Spacetime",
    "gr.connections_transport_and_motion": "GR-2 Connections and Geodesics",
    "gr.curvature_and_gravitational_action": "GR-3 Curvature and Gravitational Action",
    "gr.matter_and_einstein_equations": "GR-4 Matter and Einstein Equations",
    "gr.weak_field_and_classical_tests": "GR-5 Weak-Field Gravity",
    "gr.schwarzschild_geometry_and_black_holes": "GR-6 Schwarzschild Black Holes",
}


def _landscape_svg(module_id: str, source: str, variant: str) -> str:
    """Present the square source motif in a module-specific landscape card."""
    start = source.index(">") + 1
    end = source.rfind("</svg>")
    inner = source[start:end]
    if variant == "detail":
        # Keep one landscape frame rather than the source motif's old square
        # review-card frame nested inside it.
        inner = re.sub(
            r'\s*<rect x="(?:20|26)" y="(?:20|26)"[^>]*stroke="#dbe3f3"[^>]*/>',
            "",
            inner,
            count=1,
        )
    safe_id = module_id.replace(".", "-")
    title = f"{_TITLES[module_id]} {variant} graphic"
    frame = (
        '<rect x="2" y="2" width="764" height="476" rx="54" '
        'fill="#fbfcff" stroke="#dbe3f3" stroke-width="4"/>'
        if variant == "detail"
        else '<rect width="768" height="480" fill="#fbfcff"/>'
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="768" height="480" '
        'viewBox="0 0 768 480" role="img" '
        f'aria-labelledby="title-{safe_id}-{variant}">\n'
        f'<title id="title-{safe_id}-{variant}">{title}</title>\n'
        f'{frame}\n'
        '<svg x="144" y="-16" width="480" height="480" viewBox="0 0 512 512" '
        'preserveAspectRatio="xMidYMid meet">\n'
        f'{inner}\n</svg>\n</svg>'
    )


def createModuleSvgGraphic(module_id: str, variant: str = "icon") -> str | None:
    """Return an optional landscape module SVG keyed by stable semantic id."""
    module_id = str(module_id).strip()
    pattern = _ASSETS.get(module_id)
    if pattern is None:
        return None
    variant = "detail" if variant == "detail" else "icon"
    source = (_ASSET_ROOT / pattern.format(variant=variant)).read_text(encoding="utf-8")
    return _landscape_svg(module_id, source, variant)


__all__ = ["IMPLEMENTED_MODULE_IDS", "createModuleSvgGraphic"]
