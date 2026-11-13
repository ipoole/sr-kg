# SR block audit inventory

12 November 2026 · frozen stage-1 inventory; [audit](reading_tree_authoring_audit.md).
Every row needs title/statement review. Flags are screening aids, not proof of poor content.
Def/Der/Exp below means Definition/Derivation/Explanation where shown in the main audit.
Body words are whitespace counts, including TeX source; length is not a quality judgement.

## SR-1 Spacetime and Lorentz Symmetry

### SR-1.1 Inertial frames

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| definition | definition | Definition | 44 | 0 | generic-title |
| reference_frame | explanation | What a frame supplies | 62 | 0 | — |
| free_motion | explanation | Free motion as the test | 59 | 0 | — |
| idealization | explanation | Approximation and acceleration | 100 | 0 | — |
| relativistic_role | explanation | Why inertial frames matter | 73 | 0 | — |
| frame_dependent | explanation | Frame-dependent is not arbitrary | 79 | 0 | — |
| historical_context | historical_note | From Galileo's ship to inertial systems | 61 | 0 | — |

### SR-1.2 Constancy of the speed of light

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| definition | definition | Definition | 50 | 0 | generic-title |
| not_merely_fast | misconception | Not merely very fast | 37 | 0 | — |
| galilean_conflict | explanation | Conflict with Galilean velocity addition | 50 | 0 | — |
| wavefront_picture | intuition | Lightfront picture | 70 | 0 | — |
| vacuum_warning | warning | Vacuum, not material media | 52 | 0 | — |
| historical_context | historical_note | Light without an ether frame | 72 | 0 | — |
| relativistic_role | explanation | Role in special relativity | 54 | 0 | — |

### SR-1.3 Principle of relativity

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| definition | definition | Definition | 30 | 0 | generic-title |
| no_preferred_frame | explanation | No preferred inertial frame | 39 | 0 | — |
| same_laws_not_same_numbers | misconception | Same laws, not same numbers | 45 | 0 | — |
| sealed_lab | intuition | Sealed laboratory intuition | 53 | 0 | — |
| historical_context | historical_note | From Galileo to Einstein | 65 | 0 | — |
| galilean_to_lorentz | explanation | From Galilean to Lorentz transformations | 47 | 0 | — |
| lorentz_invariance | explanation | Modern invariant form | 43 | 0 | — |

### SR-1.4 Spacetime event

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| definition | definition | Definition | 31 | 0 | generic-title |
| coordinate_label | explanation | Coordinates label the event | 46 | 0 | — |
| not_a_process | warning | Event, not process | 44 | 0 | — |
| ct_coordinate | convention | Using \(ct\) as a time coordinate | 55 | 0 | — |
| frame_dependence | misconception | Frame-dependent is not unreal | 49 | 0 | — |
| role_in_spacetime | explanation | Atoms of spacetime reasoning | 39 | 0 | — |

### SR-1.5 Principle of locality

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| definition | definition | Definition | 27 | 0 | generic-title |
| local_neighbourhood | explanation | Same event or immediate neighbourhood | 55 | 0 | — |
| fields_fit_locality | explanation | Why fields fit locality | 48 | 0 | — |
| not_no_distant_effects | misconception | Not no distant effects | 53 | 0 | — |
| finite_propagation | explanation | Finite propagation in relativity | 54 | 0 | — |
| historical_context | historical_note | From action at a distance to fields | 61 | 0 | — |
| role_in_field_theory | explanation | Role in field theory | 46 | 0 | — |

### SR-1.6 Metric tensor

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | What the metric does | 37 | 0 | — |
| definition | definition | Definition | 36 | 0 | generic-title |
| signs_matter | explanation | The signs do the work | 47 | 0 | — |
| interval_contraction | derivation | Reading the metric from the interval | 69 | 0 | — |
| lowering_indices | construction | Lowering an index | 32 | 0 | outside-both-recipe-kinds |
| not_euclidean | misconception | Not an ordinary ruler | 50 | 0 | — |
| lorentz_preservation | explanation | Preserved by Lorentz transformations | 44 | 0 | — |
| gr_bridge | historical_note | Minkowski's geometry and Einstein's extension | 51 | 0 | — |

### SR-1.7 Spacetime interval

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | What remains fixed | 40 | 0 | — |
| definition | definition | Definition | 31 | 0 | generic-title |
| constructing_delta | construction | Start with two events | 42 | 0 | outside-both-recipe-kinds |
| metric_derivation | derivation | Metric contraction | 59 | 0 | — |
| classification | result | Timelike lightlike spacelike | 46 | 0 | outside-both-recipe-kinds |
| invariant_not_components | misconception | Invariant does not mean unchanged components | 43 | 0 | — |
| light_and_proper_time | explanation | Light and clocks | 51 | 0 | — |
| why_it_matters | summary | Why the interval matters | 47 | 0 | — |
| historical_context | historical_note | Minkowski's invariant geometry | 46 | 0 | — |

### SR-1.8 Lorentz transformations

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Coordinate translation in spacetime | 39 | 1 | — |
| definition | definition | Definition | 34 | 0 | generic-title |
| setup | construction | Standard boost setup | 51 | 0 | outside-both-recipe-kinds |
| why_linear | explanation | Why the transformation is linear | 53 | 0 | — |
| interval_condition | derivation | Preserve the interval | 45 | 0 | — |
| boost_formula | result | Boost along \(x\) | 65 | 1 | outside-both-recipe-kinds |
| interval_check | derivation_step | Checking the boost | 35 | 0 | outside-both-recipe-kinds |
| matrix_form | construction | Matrix form | 55 | 0 | outside-both-recipe-kinds |
| not_moving_events | misconception | Not moving the event | 50 | 0 | — |
| physical_effects | explanation | What changes between frames | 51 | 0 | — |
| historical_development | historical_note | How the transformation emerged | 69 | 0 | — |
| historical_reinterpretation | historical_note | From ether device to spacetime symmetry | 55 | 0 | — |

### SR-1.9 Time dilation

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Whose clock and which two events? | 70 | 1 | — |
| definition | definition | Definition | 57 | 1 | generic-title |
| measurement | construction | One travelling clock and a lab clock network | 98 | 1 | outside-both-recipe-kinds |
| light_clock_setup | construction | A clock made from a returning light pulse | 109 | 1 | outside-both-recipe-kinds |
| light_clock_triangle | intuition | A diagonal path at the same speed | 96 | 1 | — |
| light_clock_derivation | derivation | Derive the factor with a right triangle | 69 | 1 | — |
| ideal_clocks | explanation | Why the argument is not just about mirrors | 79 | 1 | — |
| worked_comparison | worked_example | Ten lab seconds and eight clock seconds | 77 | 1 | worked-example-outside-teaching |
| lorentz_derivation | derivation | Derivation from a boost | 63 | 1 | — |
| interval_derivation | derivation | The same result from proper time | 69 | 1 | — |
| reciprocal | explanation | How can each call the other's clock slow? | 97 | 1 | — |
| not_signal_delay | misconception | Not a signal-travel delay | 82 | 1 | — |
| historical_context | historical_note | From local time to moving clocks | 55 | 0 | — |

### SR-1.10 Length contraction

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Moving lengths measured shorter | 44 | 0 | — |
| definition | definition | Definition | 59 | 0 | generic-title |
| measurement | explanation | Lengths require simultaneous endpoint events | 66 | 0 | — |
| lorentz_derivation | derivation | Derivation from a boost | 51 | 0 | — |
| not_material_squashing | misconception | Not material squashing | 41 | 0 | — |
| historical_context | historical_note | The FitzGerald-Lorentz contraction | 48 | 0 | — |

### SR-1.11 Light cone

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Causal map from one event | 40 | 0 | — |
| definition | definition | Definition | 45 | 0 | generic-title |
| null_condition | result | Null interval condition | 46 | 0 | outside-both-recipe-kinds |
| future_past | explanation | Future and past cones | 49 | 0 | — |
| causal_regions | explanation | Inside on outside | 50 | 0 | — |
| invariant_cone | explanation | Same cone for all inertial observers | 36 | 0 | — |
| not_distance_only | misconception | Not just distance | 63 | 0 | — |
| diagram_picture | intuition | Why it looks like a cone | 53 | 0 | — |
| historical_context | historical_note | Minkowski's light cone | 42 | 0 | — |

### SR-1.12 Minkowski diagram

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Spacetime as a working plot | 35 | 0 | — |
| definition | definition | Definition | 33 | 0 | generic-title |
| axes | convention | Axes and units | 46 | 0 | — |
| events_worldlines | explanation | Events and worldlines | 49 | 0 | — |
| primed_axes | derivation | Moving-frame axes | 81 | 0 | — |
| not_ordinary_graph | misconception | Not ordinary graph paper | 46 | 0 | — |
| what_it_reveals | explanation | What the diagram reveals | 44 | 0 | — |
| reading_carefully | warning | Read with care | 50 | 0 | — |
| historical_context | historical_note | A geometry designed for relativity | 48 | 0 | — |

### SR-1.13 Lorentz invariance

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Same laws in every inertial frame | 21 | 0 | — |
| definition | definition | Definition | 30 | 0 | generic-title |
| relativity_principle | explanation | Relativity principle made mathematical | 31 | 0 | — |
| metric_preservation | result | Metric preservation | 38 | 0 | outside-both-recipe-kinds |
| tensor_equations | construction | Writing covariant equations | 37 | 0 | outside-both-recipe-kinds |
| examples | example | Examples across the atlas | 25 | 0 | — |
| invariant_vs_covariant | warning | Invariant is not the same as unchanged components | 34 | 0 | — |
| maxwell | intuition | Why electromagnetism fits | 35 | 0 | — |
| not_extra_symmetry | misconception | Not an optional decoration | 38 | 0 | — |
| historical_context | historical_note | From covariance to spacetime symmetry | 59 | 0 | — |
| summary | summary | Takeaway | 28 | 0 | generic-title |

## SR-2 Relativistic Particle Mechanics

### SR-2.1 Proper time

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Time carried by a clock | 36 | 0 | — |
| definition | definition | Definition | 40 | 0 | generic-title |
| coordinate_time | explanation | Coordinate time versus clock time | 69 | 1 | — |
| rate | result | Rate along an inertial segment | 40 | 1 | outside-both-recipe-kinds |
| path_dependence | explanation | Path dependence | 61 | 0 | — |
| not_observation_delay | misconception | Not an observation delay | 50 | 0 | — |
| light_limit | warning | No clock rides with light | 62 | 0 | — |
| later_role | summary | Why proper time matters | 45 | 0 | — |
| historical_context | historical_note | Clock time becomes geometry | 57 | 0 | — |

### SR-2.2 Four-vectors

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | One object, four linked components | 41 | 0 | — |
| definition | definition | Definition | 32 | 0 | generic-title |
| prototype | construction | Prototype from displacement | 36 | 0 | outside-both-recipe-kinds |
| transformation_law | explanation | The transformation law is the test | 56 | 0 | — |
| scalar_products | result | Invariant scalar products | 41 | 0 | outside-both-recipe-kinds |
| lowering_indices | construction | Upper and lower components | 40 | 0 | outside-both-recipe-kinds |
| not_ordinary_list | misconception | Not any four numbers | 46 | 0 | — |
| examples | example | Recurring examples | 42 | 0 | — |
| summary | summary | Why four-vectors matter | 46 | 0 | — |
| historical_context | historical_note | Minkowski's four-dimensional calculus | 50 | 0 | — |

### SR-2.3 Position four-vector

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Event coordinates as one object | 27 | 0 | — |
| definition | definition | Definition | 34 | 0 | generic-title |
| ct_component | convention | Why the time component is \(ct\) | 44 | 0 | — |
| origin_dependence | explanation | Relative to an origin event | 45 | 0 | — |
| transforming | result | Lorentz transformation of position | 44 | 0 | outside-both-recipe-kinds |
| displacements | explanation | Differences are usually physical | 38 | 0 | — |
| not_position_in_space | misconception | Not just position in space | 53 | 0 | — |
| example | example | A simple coordinate example | 28 | 0 | — |
| summary | summary | Why it matters | 38 | 0 | generic-title |

### SR-2.4 Velocity four-vector

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Tangent per unit proper time | 30 | 1 | — |
| definition | definition | Definition | 32 | 0 | generic-title |
| why_tau | explanation | Why use proper time | 45 | 0 | — |
| components | derivation | Components in one frame | 22 | 0 | short-body-screen |
| fixed_norm | result | Fixed invariant norm | 64 | 1 | outside-both-recipe-kinds |
| tangent_picture | intuition | Worldline tangent | 43 | 0 | — |
| not_three_velocity | misconception | Not ordinary velocity with an extra slot | 41 | 0 | — |
| rest_case | example | Particle at rest | 45 | 0 | — |
| later_role | summary | Why it matters | 33 | 0 | generic-title |

### SR-2.5 Momentum four-vector

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Energy and momentum as one object | 19 | 1 | — |
| definition | definition | Definition | 29 | 0 | generic-title |
| components | derivation | Components from four-velocity | 70 | 1 | page-dependent-wording |
| work_energy | derivation | Why this quantity measures energy transfer | 203 | 1 | — |
| kinetic_limit | result | Kinetic energy and the slow-speed check | 55 | 1 | outside-both-recipe-kinds |
| energy_physical_input | explanation | What work alone leaves undetermined | 107 | 1 | — |
| invariant_norm | derivation | Invariant norm | 71 | 2 | — |
| energy_momentum_relation | result | Energy-momentum relation | 48 | 0 | outside-both-recipe-kinds |
| frame_dependence | explanation | Components are frame-dependent | 36 | 0 | — |
| rest_frame | example | Rest frame | 37 | 0 | — |
| not_newtonian_only | misconception | Not Newtonian momentum with a label | 42 | 0 | — |
| massless_warning | warning | Massless particles | 47 | 0 | — |
| summary | summary | Why it matters | 28 | 0 | generic-title |

### SR-2.6 Mass-energy equivalence

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Why should a resting body have energy? | 67 | 1 | — |
| three_energies | decomposition | Rest energy is not kinetic energy | 69 | 1 | outside-both-recipe-kinds |
| definition | definition | Definition | 47 | 1 | generic-title |
| from_momentum | derivation | From four-momentum | 66 | 0 | — |
| light_emission | intuition | Light leaves without a kick | 171 | 1 | — |
| light_inertia | derivation | Infer inertia from the energy balance | 205 | 1 | — |
| rest_frame | result | Rest-frame limit | 60 | 1 | outside-both-recipe-kinds |
| systems | explanation | The mass belongs to the whole system | 86 | 1 | — |
| heated_box | example | A heated sealed box | 154 | 2 | — |
| heating_calculation | worked_example | How much mass does stored energy add? | 70 | 1 | worked-example-outside-teaching |
| not_substance_conversion | misconception | Not a magic substance conversion | 48 | 1 | — |
| mass_change | example | Changing internal energy changes mass | 56 | 0 | — |
| total_energy_warning | warning | Total energy is not always \(mc^2\) | 34 | 0 | — |
| historical_context | historical_note | Einstein's 1905 mass-energy argument | 61 | 0 | — |
| summary | summary | Why it matters | 35 | 0 | generic-title |

## SR-3 Action and Field Theory

### SR-3.1 Lagrangian

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | The local rule inside an action | 37 | 0 | — |
| definition | definition | Definition | 39 | 0 | generic-title |
| local_to_global | explanation | Local to global | 47 | 0 | — |
| not_unique | warning | Not unique | 38 | 0 | — |
| simple_example | example | Simple mechanical example | 51 | 0 | — |
| relativistic_building_blocks | construction | Relativistic building blocks | 38 | 0 | outside-both-recipe-kinds |
| chosen_not_found | misconception | Chosen, not mechanically discovered | 38 | 0 | — |
| field_bridge | summary | Why it matters | 38 | 0 | generic-title |
| historical_context | historical_note | Lagrange's analytical mechanics | 50 | 0 | — |

### SR-3.2 Action principle

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Choosing a whole history | 28 | 0 | — |
| definition | definition | Definition | 34 | 0 | generic-title |
| histories | intuition | Compare nearby histories | 47 | 0 | — |
| stationary_not_minimum | misconception | Stationary is not always smallest | 33 | 0 | — |
| fixed_endpoints | construction | Fixed endpoints | 41 | 0 | outside-both-recipe-kinds |
| variation_parameter | derivation_step | One-parameter variation | 35 | 0 | outside-both-recipe-kinds |
| relativistic_actions | explanation | Relativistic actions | 38 | 0 | — |
| local_equations | summary | From global rule to local equations | 28 | 0 | — |
| historical_context | historical_note | From least to stationary action | 57 | 0 | — |

### SR-3.3 Euler–Lagrange equations

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Stationary action as an equation | 24 | 0 | — |
| definition | definition | Definition | 33 | 0 | generic-title |
| setup | construction | Vary the path | 24 | 0 | outside-both-recipe-kinds, short-body-screen |
| first_variation | derivation | First variation | 42 | 0 | — |
| integration_by_parts | derivation_step | Integration by parts | 29 | 0 | outside-both-recipe-kinds, short-body-screen |
| arbitrary_variation | derivation_step | Arbitrary variations | 40 | 0 | outside-both-recipe-kinds |
| result | result | Equation of motion | 55 | 0 | outside-both-recipe-kinds |
| simple_example | worked_example | Recovering Newton's equation | 26 | 0 | worked-example-outside-teaching |
| not_extra_law | misconception | Not an extra force law | 32 | 0 | — |
| historical_context | historical_note | Euler, Lagrange and the calculus of variations | 51 | 0 | — |

### SR-3.4 Canonical momentum

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | A coordinate's dynamical partner | 32 | 0 | — |
| definition | definition | Definition | 37 | 0 | generic-title |
| boundary_origin | construction | Where it appears in the variation | 49 | 0 | outside-both-recipe-kinds |
| simple_example | example | Simple mechanical example | 31 | 0 | — |
| velocity_dependent | example | Velocity-dependent interactions | 42 | 0 | — |
| hamiltonian_role | explanation | Role in Hamiltonian mechanics | 36 | 0 | — |
| not_four_momentum | misconception | Not automatically four-momentum | 46 | 0 | — |
| notation_warning | warning | Notation overload | 31 | 0 | — |
| summary | summary | Why it matters | 24 | 0 | generic-title |

### SR-3.5 Hamiltonian formalism

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Dynamics in phase space | 25 | 0 | — |
| definition | definition | Definition | 41 | 0 | generic-title |
| legendre_transform | construction | The Legendre transform | 33 | 0 | outside-both-recipe-kinds |
| phase_space | intuition | Phase space | 42 | 0 | — |
| hamilton_equations | result | Hamilton's equations | 46 | 0 | outside-both-recipe-kinds |
| differential_derivation | derivation_step | Why the equations have that form | 54 | 0 | outside-both-recipe-kinds |
| energy_caveat | warning | Hamiltonian is not merely a synonym for energy | 41 | 0 | — |
| free_particle | worked_example | Free particle with a potential | 28 | 0 | worked-example-outside-teaching |
| why_it_matters | summary | Why it matters | 30 | 0 | generic-title |
| historical_context | historical_note | Hamilton between optics and mechanics | 49 | 0 | — |

### SR-3.6 Scalar field

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | One number at each event | 37 | 0 | — |
| definition | definition | Definition | 50 | 0 | generic-title |
| local_not_global | intuition | Local value, not one global number | 42 | 0 | — |
| coordinates | explanation | Same event, different coordinates | 37 | 0 | — |
| vector_contrast | explanation | Contrast with four-vectors | 39 | 0 | — |
| examples | example | Examples and analogies | 36 | 0 | — |
| derivatives | construction | Derivatives carry direction | 31 | 0 | outside-both-recipe-kinds |
| not_constant | misconception | Scalar does not mean constant | 28 | 0 | — |
| field_theory_role | summary | Why it matters | 27 | 0 | generic-title |

### SR-3.7 Vector field

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | A vector at every event | 33 | 0 | — |
| definition | definition | Definition | 44 | 0 | generic-title |
| local_objects | intuition | Local vectors, not one arrow | 42 | 0 | — |
| scalar_contrast | explanation | Contrast with scalar fields | 37 | 0 | — |
| argument_and_components | warning | Both argument and components transform | 39 | 0 | — |
| example | example | The electromagnetic potential | 25 | 0 | — |
| derivative_role | construction | Field equations act locally | 36 | 0 | outside-both-recipe-kinds |
| not_four_scalars | misconception | Not four unrelated scalar fields | 37 | 0 | — |
| summary | summary | Takeaway | 30 | 0 | generic-title |

### SR-3.8 Field Lagrangian

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Action density for fields | 32 | 0 | — |
| definition | definition | Definition | 40 | 0 | generic-title |
| why_density | intuition | Why a density | 36 | 0 | — |
| locality | construction | Local building blocks | 24 | 0 | outside-both-recipe-kinds, short-body-screen |
| scalar_action | explanation | The action should be scalar | 37 | 0 | — |
| example_scalar | example | A scalar-field pattern | 43 | 0 | — |
| example_em | example | Electromagnetic pattern | 33 | 0 | — |
| variation_preview | construction | Variation gives equations | 36 | 0 | outside-both-recipe-kinds |
| not_energy_density | misconception | Not simply energy density | 32 | 0 | — |
| historical_context | historical_note | From mechanics to field theory | 30 | 0 | — |
| summary | summary | Takeaway | 25 | 0 | generic-title |

### SR-3.9 Field equations

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Local rules for fields | 25 | 0 | — |
| definition | definition | Definition | 37 | 0 | generic-title |
| particle_to_field | construction | From paths to fields | 39 | 0 | outside-both-recipe-kinds |
| euler_lagrange | result | Field Euler-Lagrange equation | 51 | 0 | outside-both-recipe-kinds |
| integration_by_parts | derivation_step | Why a derivative moves | 29 | 0 | outside-both-recipe-kinds, short-body-screen |
| local_pde | intuition | Local partial differential equations | 28 | 0 | — |
| wave_operator | example | The wave-operator pattern | 38 | 0 | — |
| maxwell_bridge | example | Maxwell as the central example | 25 | 0 | — |
| not_global_constraint | misconception | Not just a global constraint | 33 | 0 | — |
| historical_context | historical_note | Field equations before relativity | 29 | 0 | — |
| summary | summary | Takeaway | 23 | 0 | generic-title |

## SR-4 Covariant Electromagnetism

### SR-4.1 Vector potential \(A_\mu\)

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | The potential behind the field | 28 | 0 | — |
| definition | definition | Definition | 36 | 0 | generic-title |
| field_strength | construction | From potential to field strength | 39 | 0 | outside-both-recipe-kinds |
| why_antisymmetric | intuition | Why the antisymmetric derivative | 31 | 0 | — |
| gauge_freedom | explanation | Gauge freedom | 22 | 0 | short-body-screen |
| lagrangian_role | construction | Field variable in the action | 27 | 0 | outside-both-recipe-kinds, short-body-screen |
| coupling_role | example | Coupling to charge | 33 | 0 | — |
| not_direct_observable | misconception | Not simply the observed field | 35 | 0 | — |
| historical_context | historical_note | Potentials become central | 26 | 0 | — |
| summary | summary | Takeaway | 28 | 0 | generic-title |

### SR-4.2 Field tensor \(F_{\mu\nu}\)

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | One tensor for electromagnetism | 21 | 0 | — |
| definition | definition | Definition | 64 | 0 | generic-title |
| antisymmetry | construction | Antisymmetry | 23 | 0 | outside-both-recipe-kinds, short-body-screen |
| six_components | intuition | Why six is suggestive | 32 | 0 | — |
| frame_split | decomposition | The frame split | 34 | 0 | outside-both-recipe-kinds |
| metric_role | convention | Index placement matters | 29 | 0 | — |
| lorentz_mixing | explanation | Why electric and magnetic mix | 32 | 0 | — |
| homogeneous_hint | construction | Built-in homogeneous structure | 27 | 0 | outside-both-recipe-kinds, short-body-screen |
| not_two_fields | misconception | Not two unrelated fields | 24 | 0 | — |
| historical_context | historical_note | Minkowski's electromagnetic form | 28 | 0 | — |
| summary | summary | Takeaway | 27 | 0 | generic-title |

### SR-4.3 Electric field

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | The field seen by charges at rest | 33 | 0 | — |
| definition | definition | Definition | 44 | 0 | generic-title |
| frame_choice | warning | A chosen frame is part of the statement | 31 | 0 | — |
| tensor_split | decomposition | Time-space components | 39 | 0 | outside-both-recipe-kinds |
| potential_formula | derivation | From potentials | 50 | 0 | — |
| static_example | example | Static potential example | 47 | 0 | — |
| force_meaning | intuition | Force meaning | 33 | 0 | — |
| not_absolute | misconception | Not absolute by itself | 34 | 0 | — |
| historical_context | historical_note | From electrostatics to field components | 24 | 0 | — |
| summary | summary | Takeaway | 24 | 0 | generic-title |

### SR-4.4 Magnetic field

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | The field tied to motion and current | 30 | 0 | — |
| definition | definition | Definition | 36 | 0 | generic-title |
| spatial_components | decomposition | Spatial antisymmetry | 31 | 0 | outside-both-recipe-kinds |
| curl_potential | derivation | From the vector potential | 39 | 0 | — |
| force_role | intuition | Sideways force | 29 | 0 | — |
| current_example | example | Current-carrying wire | 38 | 0 | — |
| frame_dependence | warning | Frame-dependent split | 26 | 0 | — |
| no_monopole_hint | explanation | A hint of no magnetic monopoles | 34 | 0 | — |
| not_independent_substance | misconception | Not a separate substance | 24 | 0 | — |
| historical_context | historical_note | From magnetism to electromagnetism | 22 | 0 | — |
| summary | summary | Takeaway | 34 | 0 | generic-title |

### SR-4.5 Electromagnetic field

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | One field, two frame faces | 24 | 0 | — |
| definition | definition | Definition | 32 | 0 | generic-title |
| six_component_package | decomposition | The six-component package | 32 | 0 | outside-both-recipe-kinds |
| observer_split | intuition | Observer-dependent decomposition | 43 | 0 | — |
| lorentz_mixing | explanation | Lorentz mixing | 24 | 0 | short-body-screen |
| locality | explanation | A local physical field | 24 | 0 | short-body-screen |
| energy_momentum_preview | example | Energy and momentum | 29 | 0 | — |
| not_two_substances | misconception | Not electricity plus magnetism glued together | 22 | 0 | — |
| historical_context | historical_note | Maxwell, Einstein, Minkowski | 24 | 0 | — |
| summary | summary | Takeaway | 24 | 0 | generic-title |

### SR-4.6 Gauge invariance

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Redundancy without physical change | 21 | 0 | — |
| definition | definition | Definition | 27 | 0 | generic-title |
| cancellation | derivation | Why \(F_{\mu\nu}\) is unchanged | 31 | 0 | — |
| redundancy | intuition | Many descriptions, one field | 28 | 0 | — |
| not_observable | misconception | Not every change in \(A_\mu\) is physical | 34 | 0 | — |
| observable_focus | explanation | Observable quantities | 33 | 0 | — |
| gauge_fixing | construction | Why gauge fixing exists | 31 | 0 | outside-both-recipe-kinds |
| minimal_coupling | example | Constraint on interactions | 26 | 0 | — |
| historical_context | historical_note | From potential freedom to gauge theory | 28 | 0 | — |
| weyl_history | historical_note | How gauge became a principle | 56 | 0 | — |
| summary | summary | Takeaway | 24 | 0 | generic-title |

### SR-4.7 Minimal coupling

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | The economical electromagnetic interaction | 25 | 0 | — |
| definition | definition | Definition | 28 | 0 | generic-title |
| why_minimal | explanation | What minimal means | 33 | 0 | — |
| worldline_term | construction | Worldline coupling | 32 | 0 | outside-both-recipe-kinds |
| momentum_replacement | construction | Momentum replacement | 31 | 0 | outside-both-recipe-kinds |
| gauge_compatibility | intuition | Gauge compatibility | 30 | 0 | — |
| canonical_momentum | example | Canonical versus mechanical momentum | 27 | 0 | — |
| force_law_preview | derivation | Toward the force law | 27 | 0 | short-body-screen |
| not_arbitrary_substitution | misconception | Not an arbitrary substitution trick | 25 | 0 | — |
| historical_context | historical_note | A bridge to modern gauge theory | 29 | 0 | — |
| summary | summary | Takeaway | 22 | 0 | generic-title |

### SR-4.8 Lorentz force law

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | How fields move charges | 19 | 0 | — |
| definition | definition | Definition | 44 | 0 | generic-title |
| three_vector_form | decomposition | Three-vector form | 48 | 0 | outside-both-recipe-kinds |
| construction | construction | From the action | 31 | 0 | outside-both-recipe-kinds |
| derivative_combination | derivation_step | Why the field tensor appears | 41 | 0 | outside-both-recipe-kinds |
| electric_magnetic_roles | intuition | Electric and magnetic roles | 49 | 0 | — |
| power | derivation | Power delivered to the particle | 64 | 0 | — |
| convention_warning | convention | Conventions matter | 37 | 0 | — |
| not_self_force | misconception | Not the whole story for an emitting charge | 39 | 0 | — |
| historical_context | historical_note | Lorentz's electron theory | 62 | 0 | — |
| summary | summary | Takeaway | 29 | 0 | generic-title |

### SR-4.9 Lorenz gauge

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | A covariant gauge choice | 22 | 0 | — |
| definition | definition | Definition | 37 | 0 | generic-title |
| gauge_invariance_context | explanation | Why a gauge condition is allowed | 27 | 0 | short-body-screen |
| covariance | intuition | Why this gauge is relativistic | 38 | 0 | — |
| maxwell_simplification | derivation | Maxwell equations become wave equations | 74 | 0 | — |
| residual_freedom | warning | It may not fix everything | 39 | 0 | — |
| not_physical_restriction | misconception | Not a new physical law | 27 | 0 | — |
| spelling | historical_note | Lorenz, not Lorentz | 43 | 0 | — |
| summary | summary | Takeaway | 24 | 0 | generic-title |

### SR-4.10 Momentum density (Poynting vector)

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Energy in motion | 20 | 0 | — |
| definition | result | Definition | 38 | 0 | generic-title, outside-both-recipe-kinds |
| direction | intuition | Direction from a cross product | 33 | 0 | — |
| energy_flux | explanation | Flux, not stored energy | 29 | 0 | short-body-screen |
| tensor_origin | derivation | Origin in the energy-momentum tensor | 32 | 0 | — |
| momentum_density | result | Momentum density | 47 | 0 | outside-both-recipe-kinds |
| radiation_pressure | example | Radiation pressure | 29 | 0 | — |
| units_warning | convention | Unit conventions | 24 | 0 | — |
| not_particle_stream | misconception | Not a stream of little arrows | 29 | 0 | — |
| historical_context | historical_note | Poynting makes energy flow local | 55 | 0 | — |
| summary | summary | Takeaway | 23 | 0 | generic-title |

### SR-4.11 Stress–energy of EM field

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | The field's accounting tensor | 17 | 0 | — |
| definition | definition | Definition | 26 | 0 | generic-title |
| formula | result | Tensor formula | 40 | 0 | outside-both-recipe-kinds |
| quadratic | intuition | Why it is quadratic | 39 | 0 | — |
| components | decomposition | Component meaning | 26 | 0 | outside-both-recipe-kinds |
| stress | example | Stress and pressure | 37 | 0 | — |
| observer_split | warning | Observer-dependent split | 27 | 0 | — |
| not_extra_field | misconception | Not a new electromagnetic field | 27 | 0 | — |
| historical_context | historical_note | Electromagnetic momentum made local | 22 | 0 | — |
| summary | summary | Takeaway | 23 | 0 | generic-title |

### SR-4.12 Energy density of EM field

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Energy stored in fields | 16 | 0 | — |
| definition | result | Definition | 45 | 0 | generic-title, outside-both-recipe-kinds |
| tensor_component | decomposition | The \(T^{00}\) component | 48 | 0 | outside-both-recipe-kinds |
| why_squared | intuition | Why squared fields appear | 38 | 0 | — |
| field_not_particle | explanation | Energy beyond particles | 34 | 0 | — |
| plane_wave | example | Plane-wave balance | 32 | 0 | — |
| frame_warning | warning | Energy density is frame-dependent | 38 | 0 | — |
| not_potential_energy_only | misconception | Not just potential energy between charges | 29 | 0 | — |
| historical_context | historical_note | Maxwell's field energy | 30 | 0 | — |
| summary | summary | Takeaway | 18 | 0 | generic-title |

### SR-4.13 Gauge fixing

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Choosing one description from many | 16 | 0 | — |
| definition | definition | Definition | 29 | 0 | generic-title |
| why_needed | explanation | Why it is needed | 30 | 0 | — |
| representative | intuition | Representative, not new physics | 33 | 0 | — |
| lorenz_example | example | Lorenz gauge example | 35 | 0 | — |
| residual_freedom | warning | Residual freedom can remain | 37 | 0 | — |
| physical_observables | construction | Keep observables gauge-invariant | 32 | 0 | outside-both-recipe-kinds |
| coordinate_analogy | intuition | Coordinate analogy and its limit | 35 | 0 | — |
| not_extra_law | misconception | Not an extra law of nature | 29 | 0 | — |
| summary | summary | Takeaway | 24 | 0 | generic-title |

## SR-5 Field Dynamics and Radiation

### SR-5.1 Noether's theorem

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Symmetry becomes conservation | 28 | 0 | — |
| definition | result | Definition | 33 | 0 | generic-title, outside-both-recipe-kinds |
| symmetry_of_action | explanation | The symmetry is a symmetry of the action | 46 | 0 | — |
| continuous_warning | warning | Continuous matters | 47 | 0 | — |
| derivation_sketch | derivation | Derivation sketch | 71 | 0 | — |
| mechanics_examples | example | Mechanical examples | 47 | 0 | — |
| cyclic_coordinate | worked_example | A cyclic coordinate | 62 | 0 | worked-example-outside-teaching |
| field_theory | explanation | Field theory form | 37 | 0 | — |
| not_magic | misconception | Not a magic conservation generator | 42 | 0 | — |
| historical_context | historical_note | Noether resolves a relativity puzzle | 59 | 0 | — |
| summary | summary | Why it matters | 29 | 0 | generic-title |

### SR-5.2 Four-current

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Charge flow as a four-vector | 23 | 0 | — |
| definition | definition | Definition | 30 | 0 | generic-title |
| why_c | convention | Why \(c\rho\) | 28 | 0 | — |
| not_density_alone | misconception | Charge density alone is not enough | 28 | 0 | — |
| local_flow | intuition | Local charge flow | 28 | 0 | — |
| continuity | construction | Four-divergence and conservation | 35 | 0 | outside-both-recipe-kinds |
| source_role | example | Source for the field | 34 | 0 | — |
| wire_example | example | Wire intuition | 35 | 0 | — |
| summary | summary | Takeaway | 25 | 0 | generic-title |

### SR-5.3 Maxwell's equations

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Local laws of electromagnetism | 22 | 0 | — |
| definition | definition | Definition | 27 | 0 | generic-title |
| sourced_equation | result | Sourced equation | 37 | 0 | outside-both-recipe-kinds |
| homogeneous_equation | result | Homogeneous equation | 30 | 0 | outside-both-recipe-kinds |
| lagrangian_derivation | derivation | From the field action | 40 | 0 | — |
| homogeneous_derivation | derivation_step | Why the homogeneous part cancels | 29 | 0 | outside-both-recipe-kinds, short-body-screen |
| three_vector_split | decomposition | The usual four equations | 34 | 0 | outside-both-recipe-kinds |
| charge_conservation | construction | Consistency with charge conservation | 33 | 0 | outside-both-recipe-kinds |
| waves | example | Source-free waves | 45 | 0 | — |
| not_four_unrelated | misconception | Not four unrelated formulas | 26 | 0 | — |
| historical_context | historical_note | Maxwell's synthesis | 63 | 0 | — |
| heaviside_history | historical_note | From Maxwell's system to four equations | 58 | 0 | — |
| summary | summary | Takeaway | 26 | 0 | generic-title |

### SR-5.4 Charge conservation

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Local bookkeeping | 24 | 0 | — |
| definition | definition | Definition | 64 | 0 | generic-title |
| local_meaning | intuition | What the equation says | 33 | 0 | — |
| integral_form | derivation_step | From local to integral form | 51 | 0 | outside-both-recipe-kinds |
| maxwell_derivation | derivation | Consistency of Maxwell's equations | 62 | 0 | — |
| antisymmetry | explanation | Why antisymmetry matters | 59 | 0 | — |
| not_global_only | misconception | Not just a global rule | 34 | 0 | — |
| source_constraint | warning | Sources must be compatible | 23 | 0 | — |
| historical_context | historical_note | From circuits to fields | 28 | 0 | — |
| summary | summary | Takeaway | 26 | 0 | generic-title |

### SR-5.5 Energy--momentum tensor

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Local energy-momentum bookkeeping | 21 | 0 | — |
| definition | definition | Definition | 46 | 0 | generic-title |
| component_meaning | decomposition | What the indices mean | 40 | 0 | outside-both-recipe-kinds |
| noether_origin | derivation | Origin in translation symmetry | 33 | 0 | — |
| canonical_form | result | Canonical form | 30 | 0 | outside-both-recipe-kinds |
| local_conservation | intuition | Conservation as flow | 39 | 0 | — |
| improvement | warning | Canonical is not always final | 34 | 0 | — |
| em_bridge | example | Electromagnetic example | 49 | 0 | — |
| not_just_energy | misconception | Not just energy density | 30 | 0 | — |
| historical_context | historical_note | From conservation laws to tensors | 31 | 0 | — |
| summary | summary | Takeaway | 20 | 0 | generic-title |

### SR-5.6 Wave equation

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Finite-speed propagation | 17 | 0 | — |
| definition | result | Definition | 34 | 0 | generic-title, outside-both-recipe-kinds |
| metric_structure | explanation | Metric structure | 26 | 0 | short-body-screen |
| maxwell_origin | derivation | From Maxwell equations | 50 | 0 | — |
| source_free | result | Source-free region | 38 | 0 | outside-both-recipe-kinds |
| plane_wave | example | Plane-wave test | 45 | 0 | — |
| sources | warning | Sources change the equation | 26 | 0 | — |
| not_any_oscillation | misconception | Not every oscillation is a wave equation | 27 | 0 | — |
| summary | summary | Takeaway | 27 | 0 | generic-title |

### SR-5.7 Electromagnetic waves

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | Light as a field disturbance | 16 | 0 | — |
| definition | definition | Definition | 32 | 0 | generic-title |
| maxwell_origin | derivation | Source-free Maxwell equations | 49 | 0 | — |
| transverse | result | Transverse fields | 35 | 0 | outside-both-recipe-kinds |
| triad | intuition | The wave triad | 33 | 0 | — |
| speed | result | Speed \(c\) | 49 | 0 | outside-both-recipe-kinds |
| energy_momentum | explanation | Energy and momentum | 24 | 0 | short-body-screen |
| one_field | misconception | Not two separate waves | 26 | 0 | — |
| historical_context | historical_note | Maxwell identifies light | 62 | 0 | — |
| hertz_history | historical_note | Hertz makes the waves visible | 44 | 0 | — |
| summary | summary | Takeaway | 28 | 0 | generic-title |

### SR-5.8 Radiation reaction

| Block suffix | Kind | Current title | Body words | Tutorial steps | Other screening flags |
| --- | --- | --- | ---: | ---: | --- |
| overview | overview | When the charge feels its own radiation | 19 | 0 | — |
| definition | definition | Definition | 27 | 0 | generic-title |
| energy_balance | derivation | Energy-momentum balance | 36 | 0 | — |
| external_vs_self | explanation | External force versus self-effect | 34 | 0 | — |
| damping_intuition | intuition | Radiative damping | 36 | 0 | — |
| not_simple_friction | misconception | Not ordinary friction | 27 | 0 | — |
| pathologies | warning | Runaways and pre-acceleration | 30 | 0 | — |
| effective_view | explanation | Effective-theory viewpoint | 31 | 0 | — |
| historical_context | historical_note | The classical electron confronts its own field | 62 | 0 | — |
| dirac_history | historical_note | Dirac and Landau-Lifshitz | 57 | 0 | — |
| summary | summary | Takeaway | 27 | 0 | generic-title |

## Module overview blocks

| Block ID | Title | Statement |
| --- | --- | --- |
| sr.spacetime_foundations.overview | Module overview | missing |
| sr.relativistic_mechanics.overview | Module overview | missing |
| sr.variational_and_field_theory.overview | Module overview | missing |
| sr.electromagnetic_structure_gauge_and_stress_energy.overview | Module overview | missing |
| sr.field_dynamics_conservation_and_radiation.overview | Module overview | missing |

All 483 concept blocks and five module blocks lack statements at this baseline.
The 49 implicit concept figures are separate from these counts; see the main audit.
