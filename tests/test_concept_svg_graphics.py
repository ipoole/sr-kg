from xml.etree import ElementTree

import pytest

from srkg.concept_svg_graphics import createSvgGraphic, saveSvgGraphics
from srkg.svg_graphics.registry import IMPLEMENTED_NODE_IDS, create_svg_graphic


GRAPHIC_NODE_IDS = [
    "sr.inertial_frames", "sr.constancy_of_speed_of_light", "sr.principle_of_relativity",
    "sr.spacetime_event", "sr.principle_of_locality",
    "sr.metric_tensor", "sr.spacetime_interval", "sr.lorentz_transformations", "sr.light_cone", "sr.minkowski_diagram",
    "sr.proper_time", "sr.four_vectors", "sr.position_four_vector", "sr.velocity_four_vector", "sr.momentum_four_vector", "sr.mass_energy_equivalence",
    "sr.lagrangian", "sr.action_principle", "sr.euler_lagrange_equations", "sr.canonical_momentum", "sr.hamiltonian_formalism", "sr.noether_theorem",
    "sr.scalar_field", "sr.vector_field", "sr.field_lagrangian", "sr.field_equations",
    "sr.vector_potential", "sr.field_tensor", "sr.electric_field", "sr.magnetic_field", "sr.electromagnetic_field", "sr.four_current", "sr.maxwells_equations",
    "sr.gauge_invariance", "sr.minimal_coupling", "sr.lorentz_force_law", "sr.charge_conservation", "sr.lorenz_gauge",
    "sr.energy_momentum_tensor", "sr.poynting_vector", "sr.em_stress_energy", "sr.em_energy_density",
    "sr.wave_equation", "sr.electromagnetic_waves", "sr.radiation_reaction",
    "sr.lorentz_invariance", "sr.gauge_fixing",
    "math.manifold", "math.coordinate_chart", "math.coordinate_transformation", "math.worldline", "math.tangent_space", "math.cotangent_space", "math.tensor_field",
    "math.index_notation", "math.tensor_transformation_law",
    "gr.gravity_as_geometry", "gr.equivalence_principle", "gr.local_inertial_frame", "gr.freely_falling_observer", "gr.tidal_gravity",
    "gr.metric_tensor", "gr.inverse_metric", "gr.volume_element",
    "gr.line_element", "gr.proper_time", "gr.null_curve", "gr.causal_structure", "gr.local_flatness", "gr.metric_signature",
    "gr.connection", "gr.christoffel_symbols", "gr.covariant_derivative", "gr.metric_compatibility", "gr.torsion_free_connection", "gr.parallel_transport",
    "gr.geodesic", "gr.geodesic_equation", "gr.geodesic_action", "gr.four_velocity", "gr.four_acceleration", "gr.geodesic_deviation",
    "gr.riemann_tensor", "gr.ricci_tensor", "gr.ricci_scalar", "gr.einstein_tensor", "gr.bianchi_identity", "gr.curvature_invariants",
    "gr.stress_energy_tensor", "gr.perfect_fluid", "gr.energy_conditions", "gr.covariant_conservation", "gr.equation_of_state",
    "gr.einstein_field_equations", "gr.cosmological_constant", "gr.einstein_hilbert_action", "gr.stress_energy_variation", "gr.trace_reversed_equations", "gr.vacuum_field_equations",
    "gr.weak_field_metric", "gr.newtonian_limit", "gr.gravitational_redshift", "gr.light_deflection", "gr.perihelion_precession", "gr.post_newtonian_approximation",
    "gr.schwarzschild_metric", "gr.schwarzschild_radius", "gr.event_horizon", "gr.coordinate_singularity", "gr.black_hole_singularity", "gr.effective_potential_orbits",
]
SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse_svg(svg_text: str):
    root = ElementTree.fromstring(svg_text)
    title = root.find(f"{SVG_NS}title")
    return root, title


@pytest.mark.parametrize("node_id", GRAPHIC_NODE_IDS)
@pytest.mark.parametrize("variant", ["icon", "detail"])
def test_create_svg_graphic_returns_valid_accessible_square_svg(node_id, variant):
    svg_text = createSvgGraphic(node_id, variant=variant)

    assert svg_text is not None
    assert svg_text.strip().startswith("<svg")
    root, title = _parse_svg(svg_text)
    assert root.tag == f"{SVG_NS}svg"
    assert root.attrib["width"] == "512"
    assert root.attrib["height"] == "512"
    assert root.attrib["viewBox"] == "0 0 512 512"
    assert root.attrib["role"] == "img"
    assert title is not None
    assert root.attrib["aria-labelledby"] == title.attrib["id"]
    assert title.text


def test_create_svg_graphic_returns_none_for_unknown_node_id():
    assert createSvgGraphic("99.99") is None


def test_create_svg_graphic_trims_node_id_whitespace():
    assert createSvgGraphic(" sr.inertial_frames ") == createSvgGraphic("sr.inertial_frames")


def test_public_svg_api_delegates_to_registry():
    assert createSvgGraphic("sr.inertial_frames") == create_svg_graphic("sr.inertial_frames")
    assert list(IMPLEMENTED_NODE_IDS) == GRAPHIC_NODE_IDS


@pytest.mark.parametrize(
    ("node_id", "expected_title"),
    [
        ("sr.inertial_frames", "Inertial frames"),
        ("sr.maxwells_equations", "Maxwell's equations"),
        ("sr.lorenz_gauge", "Lorenz gauge"),
        ("sr.gauge_fixing", "Gauge fixing"),
        ("math.manifold", "Manifold"),
        ("math.coordinate_chart", "Coordinate chart"),
        ("math.coordinate_transformation", "Coordinate transformation"),
        ("math.worldline", "Worldline"),
        ("math.tangent_space", "Tangent space"),
        ("math.cotangent_space", "Cotangent space"),
        ("math.tensor_field", "Tensor field"),
        ("math.index_notation", "Abstract and component indices"),
        ("math.tensor_transformation_law", "Tensor transformation law"),
        ("gr.gravity_as_geometry", "Gravity as geometry"),
        ("gr.equivalence_principle", "Equivalence principle"),
        ("gr.local_inertial_frame", "Local inertial frame"),
        ("gr.freely_falling_observer", "Freely falling observer"),
        ("gr.tidal_gravity", "Tidal gravity"),
        ("gr.metric_tensor", "Spacetime metric"),
        ("gr.inverse_metric", "Inverse metric"),
        ("gr.volume_element", "Volume element"),
        ("gr.line_element", "Line element"),
        ("gr.proper_time", "Proper time in curved spacetime"),
        ("gr.null_curve", "Null curve"),
        ("gr.causal_structure", "Causal structure"),
        ("gr.local_flatness", "Local flatness"),
        ("gr.metric_signature", "Metric signature convention"),
        ("gr.connection", "Connection"),
        ("gr.christoffel_symbols", "Christoffel symbols"),
        ("gr.covariant_derivative", "Covariant derivative"),
        ("gr.metric_compatibility", "Metric compatibility"),
        ("gr.torsion_free_connection", "Torsion-free connection"),
        ("gr.parallel_transport", "Parallel transport"),
        ("gr.geodesic", "Geodesic"),
        ("gr.geodesic_equation", "Geodesic equation"),
        ("gr.geodesic_action", "Geodesic action"),
        ("gr.four_velocity", "Four-velocity in curved spacetime"),
        ("gr.four_acceleration", "Four-acceleration"),
        ("gr.geodesic_deviation", "Geodesic deviation"),
        ("gr.riemann_tensor", "Riemann curvature tensor"),
        ("gr.ricci_tensor", "Ricci tensor"),
        ("gr.ricci_scalar", "Ricci scalar"),
        ("gr.einstein_tensor", "Einstein tensor"),
        ("gr.bianchi_identity", "Bianchi identity"),
        ("gr.curvature_invariants", "Curvature invariants"),
        ("gr.stress_energy_tensor", "Stress-energy tensor in GR"),
        ("gr.perfect_fluid", "Perfect fluid"),
        ("gr.energy_conditions", "Energy conditions"),
        ("gr.covariant_conservation", "Covariant conservation"),
        ("gr.equation_of_state", "Equation of state"),
        ("gr.einstein_field_equations", "Einstein field equations"),
        ("gr.cosmological_constant", "Cosmological constant"),
        ("gr.einstein_hilbert_action", "Einstein-Hilbert action"),
        ("gr.stress_energy_variation", "Stress-energy from action variation"),
        ("gr.trace_reversed_equations", "Trace-reversed equations"),
        ("gr.vacuum_field_equations", "Vacuum field equations"),
        ("gr.weak_field_metric", "Weak-field metric"),
        ("gr.newtonian_limit", "Newtonian limit"),
        ("gr.gravitational_redshift", "Gravitational redshift"),
        ("gr.light_deflection", "Light deflection"),
        ("gr.perihelion_precession", "Perihelion precession"),
        ("gr.post_newtonian_approximation", "Post-Newtonian approximation"),
        ("gr.schwarzschild_metric", "Schwarzschild metric"),
        ("gr.schwarzschild_radius", "Schwarzschild radius"),
        ("gr.event_horizon", "Event horizon"),
        ("gr.coordinate_singularity", "Coordinate singularity"),
        ("gr.black_hole_singularity", "Black hole singularity"),
        ("gr.effective_potential_orbits", "Effective potential for orbits"),
    ],
)
def test_create_svg_graphic_uses_expected_accessible_titles(node_id, expected_title):
    _, title = _parse_svg(createSvgGraphic(node_id))

    assert title.text == expected_title


@pytest.mark.parametrize("node_id", [
    node_id
    for node_id in GRAPHIC_NODE_IDS
    if node_id != "sr.principle_of_locality"
])
def test_detail_variant_adds_or_changes_graphic_content_for_most_nodes(node_id):
    assert createSvgGraphic(node_id, variant="detail") != createSvgGraphic(
        node_id,
        variant="icon",
    )


def test_principle_of_locality_currently_uses_same_icon_and_detail_graphic():
    assert createSvgGraphic("sr.principle_of_locality", variant="detail") == createSvgGraphic(
        "sr.principle_of_locality",
        variant="icon",
    )


def test_save_svg_graphics_writes_current_icon_set(tmp_path):
    saveSvgGraphics(tmp_path)

    saved_files = {path.name for path in tmp_path.glob("image_*.svg")}
    assert saved_files == {
        f"image_{node_id.replace(' ', '_').replace('.', '_')}.svg"
        for node_id in GRAPHIC_NODE_IDS
    }
    assert (tmp_path / "image_sr_inertial_frames.svg").read_text(encoding="utf-8") == createSvgGraphic(
        "sr.inertial_frames",
        variant="icon",
    )
