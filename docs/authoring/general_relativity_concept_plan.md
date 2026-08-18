# General Relativity Concept Plan

Draft started on 2026-08-18.

This is an authoring plan, not runtime KB data. It sketches an initial set of
General Relativity concepts in pedagogical layers so that concepts, edges,
modules, and exposition scope can be reviewed before adding rows to the CSV
source files.

The numbering continues the existing SR and Classical Fields layers:

- layers `1-11`: current Special Relativity and Classical Fields material
- layers `12+`: proposed General Relativity material

The concept IDs use the `gr.` namespace. Some mathematical concepts may later
deserve a separate `math.` namespace if they are reused outside GR.

## Design Assumptions

- GR should build explicitly on the current SR concepts: spacetime event,
  metric tensor, spacetime interval, four-vectors, proper time, action
  principle, field equations, stress-energy, and conservation laws.
- Differential geometry should be introduced as needed, not as a detached
  mathematics course.
- The early GR graph should remain pedagogical: start with why flat spacetime is
  insufficient, then introduce local inertial frames, manifolds, tensors,
  curvature, dynamics, and standard solutions.
- Module assignment should remain provisional until the GR concepts and edges
  exist. Graph analysis should then be used to guide module boundaries.

## Layer 12: Motivation And Equivalence

Purpose: bridge from SR to GR and explain what problem GR is solving.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `12.1` | `gr.gravity_as_geometry` | Gravity as geometry | The central conceptual move: gravity is not a force field on fixed Minkowski spacetime, but geometry of spacetime itself. |
| `12.2` | `gr.equivalence_principle` | Equivalence principle | Local indistinguishability of uniform gravity and acceleration; inertial and gravitational mass. |
| `12.3` | `gr.local_inertial_frame` | Local inertial frame | The frame where SR is locally valid at an event; connects directly to `sr.inertial_frames`. |
| `12.4` | `gr.freely_falling_observer` | Freely falling observer | Physical observer following inertial motion in curved spacetime. |
| `12.5` | `gr.tidal_gravity` | Tidal gravity | What cannot be transformed away; first operational hint of curvature. |

## Layer 13: Manifolds And Coordinates

Purpose: replace global inertial coordinates with local coordinate charts on a
smooth spacetime.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `13.1` | `gr.manifold` | Manifold | Smooth space that looks locally like `\(\mathbb R^n\)`. Keep topology minimal. |
| `13.2` | `gr.coordinate_chart` | Coordinate chart | Local coordinate labels; coordinates are not physical structure. |
| `13.3` | `gr.coordinate_transformation` | Coordinate transformation | General smooth changes of coordinates, extending Lorentz transformations. |
| `13.4` | `gr.worldline` | Worldline | Curve representing a particle/observer through spacetime. |
| `13.5` | `gr.tangent_space` | Tangent space | Vector space attached to an event; local home of vectors and velocities. |
| `13.6` | `gr.cotangent_space` | Cotangent space | Dual vectors/covectors; needed for gradients and one-forms. |

## Layer 14: Tensor Calculus On Spacetime

Purpose: provide the core language for coordinate-independent equations.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `14.1` | `gr.tensor_field` | Tensor field | Tensor assigned smoothly at each event. |
| `14.2` | `gr.index_notation` | Abstract and component indices | Distinguish geometric tensors from component arrays. |
| `14.3` | `gr.tensor_transformation_law` | Tensor transformation law | What makes tensor equations coordinate-independent. |
| `14.4` | `gr.metric_tensor` | Spacetime metric | Curved-spacetime metric `\(g_{\mu\nu}\)`; relates to `sr.metric_tensor`. |
| `14.5` | `gr.inverse_metric` | Inverse metric | Raising indices and metric inverse. |
| `14.6` | `gr.volume_element` | Volume element | `\(\sqrt{-g}\,d^4x\)` and invariant integration. |

## Layer 15: Metric Geometry

Purpose: show how the metric determines lengths, times, causal structure, and
motion of clocks and light.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `15.1` | `gr.line_element` | Line element | `\(ds^2=g_{\mu\nu}dx^\mu dx^\nu\)` as the local spacetime interval. |
| `15.2` | `gr.proper_time` | Proper time in curved spacetime | Time measured along a timelike worldline. |
| `15.3` | `gr.null_curve` | Null curve | Lightlike paths and causal propagation. |
| `15.4` | `gr.causal_structure` | Causal structure | Light cones vary from event to event. |
| `15.5` | `gr.local_flatness` | Local flatness | The metric can be made Minkowskian at a point, but not generally over a region. |
| `15.6` | `gr.metric_signature` | Metric signature convention | Sign convention and notation choices for GR. |

## Layer 16: Connections And Covariant Derivatives

Purpose: explain differentiation of fields on curved spacetime.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `16.1` | `gr.connection` | Connection | Rule for comparing vectors at nearby events. |
| `16.2` | `gr.christoffel_symbols` | Christoffel symbols | Coordinate representation of the Levi-Civita connection. |
| `16.3` | `gr.covariant_derivative` | Covariant derivative | Derivative compatible with tensor transformation laws. |
| `16.4` | `gr.metric_compatibility` | Metric compatibility | `\(\nabla_\alpha g_{\mu\nu}=0\)` for the Levi-Civita connection. |
| `16.5` | `gr.torsion_free_connection` | Torsion-free connection | Symmetric lower Christoffel indices in standard GR. |
| `16.6` | `gr.parallel_transport` | Parallel transport | Moving vectors along curves; path dependence as curvature signal. |

## Layer 17: Geodesics And Free Fall

Purpose: connect the mathematical connection to physical motion.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `17.1` | `gr.geodesic` | Geodesic | Straightest/free-fall path in curved spacetime. |
| `17.2` | `gr.geodesic_equation` | Geodesic equation | Equation using Christoffel symbols. |
| `17.3` | `gr.geodesic_action` | Geodesic action | Variational derivation from proper time or path length. |
| `17.4` | `gr.four_velocity` | Four-velocity in curved spacetime | Tangent to timelike worldline; generalises `sr.velocity_four_vector`. |
| `17.5` | `gr.four_acceleration` | Four-acceleration | Distinguish proper acceleration from gravitational free fall. |
| `17.6` | `gr.geodesic_deviation` | Geodesic deviation | Relative acceleration of nearby geodesics; operational curvature. |

## Layer 18: Curvature

Purpose: define curvature tensors and their contractions.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `18.1` | `gr.riemann_tensor` | Riemann curvature tensor | Full curvature tensor from the connection. |
| `18.2` | `gr.ricci_tensor` | Ricci tensor | Trace of the Riemann tensor relevant to volume focusing. |
| `18.3` | `gr.ricci_scalar` | Ricci scalar | Scalar curvature `\(R\)`. |
| `18.4` | `gr.einstein_tensor` | Einstein tensor | Divergence-free curvature combination. |
| `18.5` | `gr.bianchi_identity` | Bianchi identity | Geometric identity behind conservation consistency. |
| `18.6` | `gr.curvature_invariants` | Curvature invariants | Scalars used to distinguish coordinate effects from real singularities. |

## Layer 19: Matter, Stress-Energy, And Conservation

Purpose: connect spacetime geometry to physical sources.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `19.1` | `gr.stress_energy_tensor` | Stress-energy tensor in GR | General source tensor; connects to `sr.energy_momentum_tensor`. |
| `19.2` | `gr.perfect_fluid` | Perfect fluid | Standard matter model for stars and cosmology. |
| `19.3` | `gr.energy_conditions` | Energy conditions | Optional but useful constraints on physically reasonable matter. |
| `19.4` | `gr.covariant_conservation` | Covariant conservation | `\(\nabla_\mu T^{\mu\nu}=0\)` and its interpretation. |
| `19.5` | `gr.equation_of_state` | Equation of state | Relation between pressure and density for matter models. |

## Layer 20: Einstein Field Equations

Purpose: present the dynamical equation of GR and its immediate interpretation.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `20.1` | `gr.einstein_field_equations` | Einstein field equations | `\(G_{\mu\nu}=8\pi G T_{\mu\nu}/c^4\)` plus conventions. |
| `20.2` | `gr.cosmological_constant` | Cosmological constant | `\(\Lambda g_{\mu\nu}\)` term and vacuum energy interpretation. |
| `20.3` | `gr.einstein_hilbert_action` | Einstein-Hilbert action | Variational route to the field equations. |
| `20.4` | `gr.stress_energy_variation` | Stress-energy from action variation | How matter action supplies `\(T_{\mu\nu}\)`. |
| `20.5` | `gr.trace_reversed_equations` | Trace-reversed equations | Common algebraic form of the field equations. |
| `20.6` | `gr.vacuum_field_equations` | Vacuum field equations | `\(R_{\mu\nu}=0\)` away from matter when `\(\Lambda=0\)`. |

## Layer 21: Weak Field And Newtonian Limit

Purpose: recover Newtonian gravity and introduce approximations used throughout
applications.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `21.1` | `gr.weak_field_metric` | Weak-field metric | Metric close to Minkowski plus small perturbation. |
| `21.2` | `gr.newtonian_limit` | Newtonian limit | Recovery of Newton's law and gravitational potential. |
| `21.3` | `gr.gravitational_redshift` | Gravitational redshift | Clock-rate effect in a static gravitational field. |
| `21.4` | `gr.light_deflection` | Light deflection | Null geodesics in weak gravity. |
| `21.5` | `gr.perihelion_precession` | Perihelion precession | Classic weak-field orbital correction. |
| `21.6` | `gr.post_newtonian_approximation` | Post-Newtonian approximation | Optional bridge to precision tests. |

## Layer 22: Schwarzschild Geometry And Black Holes

Purpose: introduce the central exact solution around a spherical mass.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `22.1` | `gr.schwarzschild_metric` | Schwarzschild metric | Static spherically symmetric vacuum solution. |
| `22.2` | `gr.schwarzschild_radius` | Schwarzschild radius | Horizon scale `\(r_s=2GM/c^2\)`. |
| `22.3` | `gr.event_horizon` | Event horizon | Causal boundary, not a local material surface. |
| `22.4` | `gr.coordinate_singularity` | Coordinate singularity | Distinguish coordinate pathology from curvature singularity. |
| `22.5` | `gr.black_hole_singularity` | Black hole singularity | Curvature blow-up and limits of classical GR. |
| `22.6` | `gr.effective_potential_orbits` | Effective potential for orbits | Timelike and null geodesics in Schwarzschild spacetime. |

## Layer 23: Cosmology

Purpose: cover the standard homogeneous and isotropic application of GR.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `23.1` | `gr.cosmological_principle` | Cosmological principle | Homogeneity and isotropy at large scales. |
| `23.2` | `gr.flrw_metric` | FLRW metric | Metric for expanding homogeneous universe. |
| `23.3` | `gr.scale_factor` | Scale factor | Time-dependent expansion variable. |
| `23.4` | `gr.friedmann_equations` | Friedmann equations | Dynamics of the scale factor from Einstein equations. |
| `23.5` | `gr.cosmological_redshift` | Cosmological redshift | Stretching of wavelengths by expansion. |
| `23.6` | `gr.critical_density` | Critical density | Density scale for spatial curvature and expansion fate. |

## Layer 24: Gravitational Waves

Purpose: introduce linearised dynamics and wave solutions.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `24.1` | `gr.linearized_gravity` | Linearized gravity | Perturbation `\(g_{\mu\nu}=\eta_{\mu\nu}+h_{\mu\nu}\)`. |
| `24.2` | `gr.gauge_freedom_linearized_gravity` | Gauge freedom in linearized gravity | Coordinate/gauge freedom for metric perturbations. |
| `24.3` | `gr.transverse_traceless_gauge` | Transverse-traceless gauge | Physical gravitational-wave degrees of freedom. |
| `24.4` | `gr.gravitational_wave_equation` | Gravitational wave equation | Wave equation for perturbations in vacuum. |
| `24.5` | `gr.gravitational_wave_polarizations` | Gravitational wave polarizations | Plus and cross polarizations. |
| `24.6` | `gr.quadrupole_radiation` | Quadrupole radiation | Leading source mechanism for gravitational waves. |

## Layer 25: Symmetry, Coordinates, And Advanced Tools

Purpose: collect important tools and interpretive concepts that should probably
arrive after the main conceptual spine.

| Display ID | Concept ID | Label | Scope notes |
| --- | --- | --- | --- |
| `25.1` | `gr.killing_vector` | Killing vector | Continuous spacetime symmetry and conserved quantities. |
| `25.2` | `gr.stationary_spacetime` | Stationary spacetime | Time-translation symmetry. |
| `25.3` | `gr.axisymmetric_spacetime` | Axisymmetric spacetime | Rotational symmetry; preparation for Kerr. |
| `25.4` | `gr.adm_split` | ADM split | Optional 3+1 decomposition for evolution viewpoint. |
| `25.5` | `gr.penrose_diagram` | Penrose diagram | Conformal causal diagram. |
| `25.6` | `gr.kerr_metric` | Kerr metric | Rotating black hole solution; likely advanced/optional. |

## Concepts To Consider Later

These are likely useful but should wait until the first GR spine is reviewed.

- tetrads/vierbeins
- spin connection
- Raychaudhuri equation
- trapped surfaces
- singularity theorems
- junction conditions
- Reissner-Nordstrom metric
- de Sitter and anti-de Sitter spacetime
- gravitational lensing as a richer topic
- numerical relativity
- Hamiltonian constraints
- Arnowitt-Deser-Misner energy
- cosmic microwave background as an application concept
- inflation as an application concept

## Early Edge Expectations

The following high-level dependencies are expected and should guide the first
edge pass:

- `gr.equivalence_principle` requires `sr.inertial_frames` and
  `sr.principle_of_relativity`.
- `gr.local_inertial_frame` derives from `gr.equivalence_principle` and
  requires `sr.inertial_frames`.
- `gr.metric_tensor` generalises `sr.metric_tensor`.
- `gr.line_element` derives from `gr.metric_tensor` and generalises
  `sr.spacetime_interval`.
- `gr.proper_time` derives from `gr.line_element` and generalises
  `sr.proper_time`.
- `gr.connection`, `gr.covariant_derivative`, and `gr.parallel_transport`
  require `gr.tangent_space` and `gr.tensor_field`.
- `gr.riemann_tensor` derives from `gr.connection` and
  `gr.covariant_derivative`.
- `gr.einstein_tensor` is constructed from `gr.ricci_tensor`,
  `gr.ricci_scalar`, and `gr.metric_tensor`.
- `gr.einstein_field_equations` relates `gr.einstein_tensor` to
  `gr.stress_energy_tensor`.
- `gr.schwarzschild_metric`, `gr.flrw_metric`, and
  `gr.linearized_gravity` should derive from or instantiate the Einstein field
  equations, depending on final edge semantics.

## Open Questions

- Should differential-geometry concepts use `gr.` IDs or a reusable `math.`
  namespace?
- Should the GR layer numbering continue from `12`, or should the atlas adopt a
  higher-level domain/module field before adding GR rows?
- Should `gr.metric_tensor` be distinct from `sr.metric_tensor`, or should the
  existing concept be broadened into a cross-domain concept?
- Does `gr.stress_energy_tensor` need to be distinct from
  `sr.energy_momentum_tensor`, or should one concept cover both with GR content
  blocks?
- How far should the first pass go into black holes, cosmology, and
  gravitational waves before module tooling exists?
- Which relation set should be used for module-DAG diagnostics after GR is
  added: `{DERIVES_FROM, CONSTRUCTED_FROM}` only, or also selected `REQUIRES`
  edges?
