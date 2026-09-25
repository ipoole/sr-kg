# General Relativity Concept Plan

This is an authoring scope plan. The existing 55 GR concepts have completed full
authoring and review; gravitational waves, advanced tools and cosmology are future scope.
Topic groups below describe subject progression, not runtime modules. Use
`data/module_members.csv` for current authoring batches and `data/nodes.csv` for
display IDs and status. Semantic IDs keep this plan independent of renumbering.

Reusable mathematics belongs in `math.*`; GR-specific concepts belong in `gr.*`.
Full authoring follows the [authoring guide](authoring_guide.md).

## Design Assumptions

- GR should build explicitly on the current SR concepts: spacetime event,
  metric tensor, spacetime interval, four-vectors, proper time, action
  principle, field equations, stress-energy, and conservation laws.
- Differential geometry should be introduced as needed, not as a detached
  mathematics course.
- The early GR graph should remain pedagogical: start with why flat spacetime is
  insufficient, then introduce local inertial frames, manifolds, tensors,
  curvature, dynamics, and standard solutions.
- Module membership is established. Revisit boundaries only when full authoring
  reveals a teaching or dependency problem.

## Motivation And Equivalence

Purpose: bridge from SR to GR and explain what problem GR is solving.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.gravity_as_geometry` | Gravity as geometry | The central conceptual move: gravity is not a force field on fixed Minkowski spacetime, but geometry of spacetime itself. |
| `gr.equivalence_principle` | Equivalence principle | Local indistinguishability of uniform gravity and acceleration; inertial and gravitational mass. |
| `gr.local_inertial_frame` | Local inertial frame | The frame where SR is locally valid at an event; connects directly to `sr.inertial_frames`. |
| `gr.freely_falling_observer` | Freely falling observer | Physical observer following inertial motion in curved spacetime. |
| `gr.tidal_gravity` | Tidal gravity | What cannot be transformed away; first operational hint of curvature. |

## Manifolds And Coordinates

Purpose: replace global inertial coordinates with local coordinate charts on a
smooth spacetime.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `math.manifold` | Manifold | Smooth space that looks locally like `\(\mathbb R^n\)`. Keep topology minimal. |
| `math.coordinate_chart` | Coordinate chart | Local coordinate labels; coordinates are not physical structure. |
| `math.coordinate_transformation` | Coordinate transformation | General smooth changes of coordinates, extending Lorentz transformations. |
| `math.worldline` | Worldline | Curve representing a particle/observer through spacetime. |
| `math.tangent_space` | Tangent space | Vector space attached to an event; local home of vectors and velocities. |
| `math.cotangent_space` | Cotangent space | Dual vectors/covectors; needed for gradients and one-forms. |

## Tensor Calculus On Spacetime

Purpose: provide the core language for coordinate-independent equations.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `math.tensor_field` | Tensor field | Tensor assigned smoothly at each event. |
| `math.index_notation` | Abstract and component indices | Distinguish geometric tensors from component arrays. |
| `math.tensor_transformation_law` | Tensor transformation law | What makes tensor equations coordinate-independent. |
| `gr.metric_tensor` | Spacetime metric | Curved-spacetime metric `\(g_{\mu\nu}\)`; relates to `sr.metric_tensor`. |
| `gr.inverse_metric` | Inverse metric | Raising indices and metric inverse in curved spacetime. |
| `gr.volume_element` | Volume element | `\(\sqrt{-g}\,d^4x\)` and invariant integration. |

## Metric Geometry

Purpose: show how the metric determines lengths, times, causal structure, and
motion of clocks and light.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.line_element` | Line element | `\(ds^2=g_{\mu\nu}dx^\mu dx^\nu\)` as the local spacetime interval. |
| `gr.proper_time` | Proper time in curved spacetime | Time measured along a timelike worldline. |
| `gr.null_curve` | Null curve | Lightlike paths and causal propagation. |
| `gr.causal_structure` | Causal structure | Light cones vary from event to event. |
| `gr.local_flatness` | Local flatness | The metric can be made Minkowskian at a point, but not generally over a region. |
| `gr.metric_signature` | Metric signature convention | Sign convention and notation choices for GR. |

## Connections And Covariant Derivatives

Purpose: explain differentiation of fields on curved spacetime.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.connection` | Connection | Rule for comparing vectors at nearby events. |
| `gr.christoffel_symbols` | Christoffel symbols | Coordinate representation of the Levi-Civita connection. |
| `gr.covariant_derivative` | Covariant derivative | Derivative compatible with tensor transformation laws. |
| `gr.metric_compatibility` | Metric compatibility | `\(\nabla_\alpha g_{\mu\nu}=0\)` for the Levi-Civita connection. |
| `gr.torsion_free_connection` | Torsion-free connection | Symmetric lower Christoffel indices in standard GR. |
| `gr.parallel_transport` | Parallel transport | Moving vectors along curves; path dependence as curvature signal. |

## Geodesics And Free Fall

Purpose: connect the mathematical connection to physical motion.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.geodesic` | Geodesic | Straightest/free-fall path in curved spacetime. |
| `gr.geodesic_equation` | Geodesic equation | Equation using Christoffel symbols. |
| `gr.geodesic_action` | Geodesic action | Variational derivation from proper time or path length. |
| `gr.four_velocity` | Four-velocity in curved spacetime | Tangent to timelike worldline; generalises `sr.velocity_four_vector`. |
| `gr.four_acceleration` | Four-acceleration | Distinguish proper acceleration from gravitational free fall. |
| `gr.geodesic_deviation` | Geodesic deviation | Relative acceleration of nearby geodesics; operational curvature. |

## Curvature

Purpose: define curvature tensors and their contractions.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.riemann_tensor` | Riemann curvature tensor | Full curvature tensor from the connection. |
| `gr.ricci_tensor` | Ricci tensor | Trace of the Riemann tensor relevant to volume focusing. |
| `gr.ricci_scalar` | Ricci scalar | Scalar curvature `\(R\)`. |
| `gr.einstein_tensor` | Einstein tensor | Divergence-free curvature combination. |
| `gr.bianchi_identity` | Bianchi identity | Geometric identity behind conservation consistency. |
| `gr.curvature_invariants` | Curvature invariants | Scalars used to distinguish coordinate effects from real singularities. |

## Matter, Stress-Energy, And Conservation

Purpose: connect spacetime geometry to physical sources.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.stress_energy_tensor` | Stress-energy tensor in GR | General source tensor; connects to `sr.energy_momentum_tensor`. |
| `gr.perfect_fluid` | Perfect fluid | Standard matter model for stars and cosmology. |
| `gr.energy_conditions` | Energy conditions | Optional but useful constraints on physically reasonable matter. |
| `gr.covariant_conservation` | Covariant conservation | `\(\nabla_\mu T^{\mu\nu}=0\)` and its interpretation. |
| `gr.equation_of_state` | Equation of state | Relation between pressure and density for matter models. |

## Einstein Field Equations

Purpose: present the dynamical equation of GR and its immediate interpretation.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.einstein_field_equations` | Einstein field equations | `\(G_{\mu\nu}=8\pi G T_{\mu\nu}/c^4\)` plus conventions. |
| `gr.cosmological_constant` | Cosmological constant | `\(\Lambda g_{\mu\nu}\)` term and vacuum energy interpretation. |
| `gr.einstein_hilbert_action` | Einstein-Hilbert action | Variational route to the field equations. |
| `gr.stress_energy_variation` | Stress-energy from action variation | How matter action supplies `\(T_{\mu\nu}\)`. |
| `gr.trace_reversed_equations` | Trace-reversed equations | Common algebraic form of the field equations. |
| `gr.vacuum_field_equations` | Vacuum field equations | `\(R_{\mu\nu}=0\)` away from matter when `\(\Lambda=0\)`. |

## Weak Field And Newtonian Limit

Purpose: recover Newtonian gravity and introduce approximations used throughout
applications.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.weak_field_metric` | Weak-field metric | Metric close to Minkowski plus small perturbation. |
| `gr.newtonian_limit` | Newtonian limit | Recovery of Newton's law and gravitational potential. |
| `gr.gravitational_redshift` | Gravitational redshift | Clock-rate effect in a static gravitational field. |
| `gr.light_deflection` | Light deflection | Null geodesics in weak gravity. |
| `gr.perihelion_precession` | Perihelion precession | Classic weak-field orbital correction. |
| `gr.post_newtonian_approximation` | Post-Newtonian approximation | Optional bridge to precision tests. |
| `gr.gravitational_waves` | Gravitational waves | Weak-field vacuum radiation and tidal strain. |

## Schwarzschild Geometry And Black Holes

Purpose: introduce the central exact solution around a spherical mass.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.schwarzschild_metric` | Schwarzschild metric | Static spherically symmetric vacuum solution. |
| `gr.schwarzschild_radius` | Schwarzschild radius | Horizon scale `\(r_s=2GM/c^2\)`. |
| `gr.event_horizon` | Event horizon | Causal boundary, not a local material surface. |
| `gr.coordinate_singularity` | Coordinate singularity | Distinguish coordinate pathology from curvature singularity. |
| `gr.black_hole_singularity` | Black hole singularity | Curvature blow-up and limits of classical GR. |
| `gr.effective_potential_orbits` | Effective potential for orbits | Timelike and null geodesics in Schwarzschild spacetime. |

## Deferred: Cosmology

Purpose: cover the standard homogeneous and isotropic application of GR.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.cosmological_principle` | Cosmological principle | Homogeneity and isotropy at large scales. |
| `gr.flrw_metric` | FLRW metric | Metric for expanding homogeneous universe. |
| `gr.scale_factor` | Scale factor | Time-dependent expansion variable. |
| `gr.friedmann_equations` | Friedmann equations | Dynamics of the scale factor from Einstein equations. |
| `gr.cosmological_redshift` | Cosmological redshift | Stretching of wavelengths by expansion. |
| `gr.critical_density` | Critical density | Density scale for spatial curvature and expansion fate. |

## Planned: Gravitational Waves

Purpose: introduce linearised dynamics and wave solutions.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.linearized_gravity` | Linearized gravity | Perturbation `\(g_{\mu\nu}=\eta_{\mu\nu}+h_{\mu\nu}\)`. |
| `gr.gauge_freedom_linearized_gravity` | Gauge freedom in linearized gravity | Coordinate/gauge freedom for metric perturbations. |
| `gr.transverse_traceless_gauge` | Transverse-traceless gauge | Physical gravitational-wave degrees of freedom. |
| `gr.gravitational_wave_equation` | Gravitational wave equation | Wave equation for perturbations in vacuum. |
| `gr.gravitational_wave_polarizations` | Gravitational wave polarizations | Plus and cross polarizations. |
| `gr.quadrupole_radiation` | Quadrupole radiation | Leading source mechanism for gravitational waves. |

## Future: Symmetry, Coordinates, And Advanced Tools

Purpose: collect important tools and interpretive concepts that should probably
arrive after the main conceptual spine.

| Concept ID | Label | Scope notes |
| --- | --- | --- |
| `gr.killing_vector` | Killing vector | Continuous spacetime symmetry and conserved quantities. |
| `gr.stationary_spacetime` | Stationary spacetime | Time-translation symmetry. |
| `gr.axisymmetric_spacetime` | Axisymmetric spacetime | Rotational symmetry; preparation for Kerr. |
| `gr.adm_split` | ADM split | Optional 3+1 decomposition for evolution viewpoint. |
| `gr.penrose_diagram` | Penrose diagram | Conformal causal diagram. |
| `gr.kerr_metric` | Kerr metric | Rotating black hole solution; likely advanced/optional. |

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

## Dependency Review Prompts

Use these conceptual relationships to review explanations during full authoring.
They are not a duplicate edge list or instructions to add every link; current
relations live in `data/edges.csv`:

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
  require `math.tangent_space` and `math.tensor_field`.
- `gr.riemann_tensor` derives from `gr.connection` and
  `gr.covariant_derivative`.
- `gr.einstein_tensor` is constructed from `gr.ricci_tensor`,
  `gr.ricci_scalar`, and `gr.metric_tensor`.
- `gr.einstein_field_equations` relates `gr.einstein_tensor` to
  `gr.stress_energy_tensor`.
- `gr.schwarzschild_metric`, `gr.flrw_metric`, and
  `gr.linearized_gravity` should derive from or instantiate the Einstein field
  equations, depending on final edge semantics.

## Scope Decisions

- Keep distinct SR/GR metric and stress-energy concepts, linked by `RELATED`
  edges. This scope decision is settled; develop complementary explanations.
- Add the gravitational-wave progression after reviewing the seeded spine.
- Keep cosmology deferred. Select advanced tools according to the needs of the
  explanations rather than treating the entire list as a committed backlog.
