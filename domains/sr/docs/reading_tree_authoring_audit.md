# SR reading-tree authoring audit — stage 1

12 November 2026 · branch `nested-explanations` · baseline `ddc458467d33`.

This is an inventory and editorial triage, not an authoring pass. Runtime content,
graph edges, questions, graphics and tutorials are unchanged. Kind counts and
dependency lists are exact at the recorded baseline. Review notes identify work
to inspect or develop; they are not automatic rewrite rules or a completed
source-by-source physics verification.

## Scope and preservation baseline

- **49 concepts; 483 concept blocks; five module overview blocks.** All 488 need statements.
- **277 questions and 1,108 options** retain their identities and content.
- **141 SR-owned edges:** 43 Derivation-context edges and 92 Foundation-context edges.
  The SR-owned Foundation subgraph has no directed cycle; that does not rule out circular prose arguments.
- **34 distinct block tutorial targets, in 36 step occurrences**, across Using PhysicsKG, rest energy and time dilation.
- **Eight local clarifications**, all anonymous legacy optional disclosures; preserve their paths or test a deliberate migration.
- **No owned-block borrowing calls** are present in SR.
- **49 existing concept graphics** are implicit figures, not counted among the 483 blocks.
  Following the Maths presentation would introduce explicit Graphic blocks around the existing SVGs/captions.
  Preserve legacy graphic notes; no new SVG artwork is proposed in this pass.

The [frozen machine-readable baseline](reading_tree_authoring_baseline.json)
records input hashes, every block ID/kind/title/body hash and clarification path,
question/option IDs, all edges and tutorial targets. The
[block inventory](reading_tree_block_inventory.md) lists every existing block,
with kind, title, body-word screening count and tutorial use.

## Module inventory

Missing counts refer to the exact kinds used by the current recipes, not necessarily absent ideas.
There is no proposal to create a fake proof for a definition or postulate.

| Module | Concepts | Blocks | Missing Definition | Missing Derivation | Missing Explanation |
| --- | ---: | ---: | ---: | ---: | ---: |
| SR-1 Spacetime and Lorentz Symmetry | 13 | 111 | 0 | 7 | 0 |
| SR-2 Relativistic Particle Mechanics | 6 | 65 | 0 | 3 | 0 |
| SR-3 Action and Field Theory | 9 | 87 | 0 | 8 | 3 |
| SR-4 Covariant Electromagnetism | 13 | 135 | 2 | 6 | 3 |
| SR-5 Field Dynamics and Radiation | 8 | 85 | 2 | 1 | 3 |
| **Total** | **49** | **483** | **4** | **25** | **9** |

The five module overview blocks are additional. The concept blocks currently use
16 kinds: Definition 45; Explanation 64; Derivation 29; Intuition 32; Example 32;
Overview 44; Construction 30; Result 26; Derivation step 9; Decomposition 10;
Worked example 5; Summary 37; Historical note 44; Warning 22; Misconception 47;
Convention 7.

## Findings that should shape the module passes

1. **Recipe visibility is not the same as content existence.** Derivation currently
   selects only Definition and Derivation; Teaching selects Definition, Explanation,
   Intuition and Example. Construction/Result/Derivation-step/Decomposition blocks
   can contain essential reasoning but are excluded. The five Worked examples are
   also excluded from Teaching. Reclassify or assemble self-contained arguments by
   purpose, rather than blindly converting whole kinds or widening recipes to hide gaps.
   Broadening Teaching for independently useful material is considered separately below.
2. **Four Definitions are misclassified as Result:** Poynting vector (SR-4.10), EM
   energy density (SR-4.12), Noether (SR-5.1) and Wave equation (SR-5.6). EM energy
   density currently has no root block selected by the Derivation recipe at all.
3. **Some supposed roots are accidental.** Magnetic field (SR-4.4) has only
   COMPONENT_OF/RELATED links, and Four-current (SR-5.2) only INSTANCE_OF.
   Neither has a Foundation support branch. Vector potential → Vector field is
   likewise taxonomic only; Electric field → Field tensor is component-only.
   These relations do not imply REQUIRES automatically. Review the actual exposition
   before adding a separate prerequisite or choosing a construction relation.
4. **Existing derivations sometimes stop before the combination argument.**
   Euler–Lagrange includes First variation but excludes its integration-by-parts
   and arbitrary-variation steps. Lorentz force has a Derivation of power, while
   the derivation of the force law itself is a Construction/Derivation-step sketch.
   Field equations has neither Derivation nor Explanation under those kinds.
5. **Alternative routes need explicit scope.** The metric/interval/Lorentz sequence
   can be circular in prose even though its graph is acyclic. Time dilation and
   rest energy have useful alternative arguments not all represented by the same
   current edge set. Lorenz gauge should not acquire a Maxwell dependency without
   considering the wave-equation chain. Resolve these cases while writing the bodies.
6. **Separate geometry, physical input and conventions.** In particular, four-momentum
   needs dynamical identification/conservation; minimal coupling is not uniquely
   forced by gauge invariance alone; field-action normalisations and E/B component
   signs need a single stated convention; radiation balance alone is not a full
   instantaneous self-force calculation.
7. **Titles and statements need genuine editing.** The screening found 87 generic
   headings, including five module overviews, and 17 very short reasoning bodies.
   A generic heading is a review candidate, not automatically bad; source word
   counts include TeX and do not measure mathematical substance. Do not duplicate
   a title in its statement or pad a concise but complete calculation.
8. **Protect readers and tutorials.** Retain IDs and local clarification placement;
   check 34 tutorial block targets after title/body changes. Ordinary concept links
   can remain excursions, but cannot substitute for a premise in a generated tree.

## Teaching recipe — proposed extension, not implemented

Broaden this recipe by pedagogical purpose, while still requiring a coherent
Explanation that combines the supporting concepts. Do not change a block's
semantic kind merely to make it appear in a reading tree.

| Kind to add | SR blocks | Why include it? |
| --- | ---: | --- |
| Worked example | 5 | A calculation is as useful in Teaching as an ordinary Example. |
| Construction | 30 | How an object is assembled is important teaching content. |
| Decomposition | 10 | Unpacking components or terms helps interpret the object. |
| Misconception | 47 | Correcting a likely wrong model is central to understanding. |
| Warning | 22 | Scope limits and failure cases are useful when judging understanding. |

Keep Definition, Explanation, Intuition and Example. A possible ordered list is
Definition → Explanation → Intuition → Construction → Decomposition → Example →
Worked example → Misconception → Warning, retaining authored order within each kind.

This changes the number of eligible *unique SR concept blocks* from **173 to 287**
(+66%). Adding Worked example alone gives 178. Adding Result and Convention as
well would give 320. These are coverage counts, not numbers of initially rendered
blocks: concept branches hydrate lazily, and a full tree may repeat a source on
several paths. More eligible kinds still mean longer statement lists per opened
concept, especially on a phone.

Result (26) and Convention (7) deserve a second look: include them where they
provide independent information, but first remove needless restatement and make
essential assumptions explicit in the blocks that use them. Keep formal
Derivation content in the distinct derivation recipe initially. Derivation step
is not a substitute for a self-contained argument. Historical note can remain an
optional excursion; Overview and Summary usually repeat context already supplied
by other blocks rather than advancing the reading tree.

This extension would make existing material available without relabelling it for
presentation. It would **not** repair the four missing Definition kinds, gaps in
the combination arguments, or taxonomy-only graph supports. The recipe should
remain unchanged until this proposal is agreed.

## Concept-by-concept working inventory

**Def/Der/Exp** counts mean Definition / Derivation / Explanation.
**Inputs** are direct outgoing graph supports, labelled with their stored relation
 types. Taxonomic links are discussed separately where relevant.
Evidence lists are existing block suffixes, not proposed new IDs.

### SR-1 Spacetime and Lorentz Symmetry

| Concept | Blocks | Def/Der/Exp | Tutorial blocks | Review focus |
| --- | ---: | --- | ---: | --- |
| SR-1.1 Inertial frames | 7 | 1/0/5 | 0 | Retain the operational free-motion definition and explain its idealisation; label the starting structure honestly rather than inventing a proof. |
| SR-1.2 Constancy of the speed of light | 7 | 1/0/2 | 0 | State the vacuum postulate succinctly; distinguish the measured invariant speed from its exact SI numerical definition. |
| SR-1.3 Principle of relativity | 7 | 1/0/3 | 0 | Separate equality of law form from equality of measured components; keep the postulate distinct from its later Lorentz-covariant formulation. |
| SR-1.4 Spacetime event | 6 | 1/0/2 | 0 | Distinguish an occurrence from its coordinate labels; introduce coordinate and origin conventions before packaging an event as a vector. |
| SR-1.5 Principle of locality | 7 | 1/0/4 | 0 | Separate pointwise dependence of laws from finite causal propagation; make the extra relativistic/causal assumptions explicit. |
| SR-1.6 Metric tensor | 8 | 1/1/2 | 0 | Resolve which starting structure is being assumed: the metric block currently reads coefficients from an interval, while the interval derives from the metric. |
| SR-1.7 Spacetime interval | 9 | 1/1/1 | 0 | Combine two-event displacement with the chosen metric; distinguish construction of the quadratic form from its physical invariance. |
| SR-1.8 Lorentz transformations | 12 | 1/1/2 | 2 | Complete a chosen boost derivation with its homogeneity/linearity and normalisation assumptions; distinguish deriving the boost from checking an announced formula. |
| SR-1.9 Time dilation | 13 | 1/3/2 | 12 | Preserve the strong light-clock, boost and interval arguments, each with a self-contained setup; state ideal-clock assumptions and avoid assuming the desired clock-rate result. |
| SR-1.10 Length contraction | 6 | 1/1/1 | 0 | Knit the rest-frame endpoint separation and measuring-frame simultaneity condition into the boost calculation; keep optical appearance separate. |
| SR-1.11 Light cone | 9 | 1/0/3 | 0 | Turn the null-condition calculation into a useful included construction/derivation; distinguish cone boundary from the timelike interior. |
| SR-1.12 Minkowski diagram | 9 | 1/1/2 | 0 | Make axis conventions and the moving-axis calculation independently readable; explain equal axis scales for 45-degree light rays. |
| SR-1.13 Lorentz invariance | 11 | 1/0/1 | 0 | Distinguish invariant scalars, covariant component equations and unchanged law form; provide the actual contraction argument rather than only the matrix condition. |

**SR-1.1 — Inertial frames**
- Inputs: —.
- Inspect: `reference_frame`, `free_motion`, `idealization`.
- Graph/scope question: No outgoing foundation edge is expected for this starting concept; forward-looking links must remain excursions.

**SR-1.2 — Constancy of the speed of light**
- Inputs: SR-1.1 [REQUIRES].
- Inspect: `galilean_conflict`, `relativistic_role`.
- Graph/scope question: Do not claim that Maxwell theory or the metre definition proves this postulate.

**SR-1.3 — Principle of relativity**
- Inputs: SR-1.1 [REQUIRES].
- Inspect: `no_preferred_frame`, `galilean_to_lorentz`.
- Graph/scope question: Avoid a circular dependency on Lorentz transformations or Lorentz invariance.

**SR-1.4 — Spacetime event**
- Inputs: SR-1.1 [REQUIRES].
- Inspect: `coordinate_label`, `ct_coordinate`.
- Graph/scope question: Review whether the frame edge is a prerequisite for the representation rather than existence of an event.

**SR-1.5 — Principle of locality**
- Inputs: SR-1.4 [REQUIRES]; SR-1.2 [REQUIRES].
- Inspect: `local_neighbourhood`, `finite_propagation`.
- Graph/scope question: Do not present locality alone as a proof of finite-speed propagation.

**SR-1.6 — Metric tensor**
- Inputs: —.
- Inspect: `interval_contraction`, `lowering_indices`.
- Graph/scope question: Choose an honest construction direction or explicitly distinguish alternative routes; avoid a prose-level circle.

**SR-1.7 — Spacetime interval**
- Inputs: SR-1.6 [DERIVES_FROM]; SR-1.4 [REQUIRES].
- Inspect: `constructing_delta`, `metric_derivation`, `classification`.
- Graph/scope question: Keep the metric input and event input explicit; do not infer Lorentz invariance merely from writing a contraction.

**SR-1.8 — Lorentz transformations**
- Inputs: SR-1.3 [DERIVES_FROM]; SR-1.2 [DERIVES_FROM]; SR-1.7 [DERIVES_FROM]; SR-1.1 [REQUIRES].
- Inspect: `why_linear`, `interval_condition`, `boost_formula`, `interval_check`.
- Graph/scope question: Three derivation supports currently list the postulates and interval together; clarify their roles rather than silently treating alternative starting routes as joint premises.

**SR-1.9 — Time dilation**
- Inputs: SR-1.8 [DERIVES_FROM].
- Inspect: `measurement`, `light_clock_setup`, `light_clock_derivation`, `lorentz_derivation`, `interval_derivation`.
- Graph/scope question: The graph follows the boost route; assess how the light-clock and proper-time alternatives should be represented without introducing a cycle.

**SR-1.10 — Length contraction**
- Inputs: SR-1.8 [DERIVES_FROM].
- Inspect: `measurement`, `lorentz_derivation`.
- Graph/scope question: The Lorentz-transformation support matches the principal route; retain the diagram as an optional aid.

**SR-1.11 — Light cone**
- Inputs: SR-1.7 [DERIVES_FROM].
- Inspect: `null_condition`, `future_past`, `causal_regions`.
- Graph/scope question: The existing interval derivation edge is appropriate; its argument is currently stored as Result.

**SR-1.12 — Minkowski diagram**
- Inputs: SR-1.4 [REQUIRES].
- Inspect: `axes`, `events_worldlines`, `primed_axes`.
- Graph/scope question: The derivation uses Lorentz transformations, currently RELATED only; assess explicit support rather than allowing a tree with no supporting branch.

**SR-1.13 — Lorentz invariance**
- Inputs: SR-1.8 [DERIVES_FROM].
- Inspect: `metric_preservation`, `tensor_equations`, `invariant_vs_covariant`.
- Graph/scope question: The Lorentz-transformation edge supplies the basic support; audit any metric input used by the proof.

### SR-2 Relativistic Particle Mechanics

| Concept | Blocks | Def/Der/Exp | Tutorial blocks | Review focus |
| --- | ---: | --- | ---: | --- |
| SR-2.1 Proper time | 9 | 1/0/2 | 2 | Promote/develop the rate calculation into a self-contained derivation; distinguish infinitesimal integration, straight inertial segments and path dependence. |
| SR-2.2 Four-vectors | 10 | 1/0/1 | 0 | Use the transformation test as the definition; separate the chosen representation from invariant contractions and index movement. |
| SR-2.3 Position four-vector | 9 | 1/0/2 | 0 | Explain the shared-origin restriction and why displacements transform homogeneously; distinguish affine event coordinates from an origin-relative vector. |
| SR-2.4 Velocity four-vector | 9 | 1/1/1 | 2 | Combine a timelike worldline, position derivative and invariant proper time; show transformation and fixed norm with a consistent parameter convention. |
| SR-2.5 Momentum four-vector | 13 | 1/3/2 | 6 | Retain the bridge from mU to physical momentum/energy, fixed-mass work transfer, Newtonian calibration and isolated-system conservation. |
| SR-2.6 Mass-energy equivalence | 15 | 1/2/1 | 10 | Keep the four-momentum rest-frame argument and the light-emission inertia-change argument distinct; expose assumptions and system boundaries in each. |

**SR-2.1 — Proper time**
- Inputs: SR-1.7 [DERIVES_FROM]; MATHS-1.4 [REQUIRES].
- Inspect: `rate`, `coordinate_time`, `path_dependence`.
- Graph/scope question: Retain interval plus worldline support; do not require the time-dilation result to define proper time.

**SR-2.2 — Four-vectors**
- Inputs: SR-1.8 [REQUIRES].
- Inspect: `prototype`, `transformation_law`, `scalar_products`, `lowering_indices`.
- Graph/scope question: If scalar products become the derivation, assess the metric premise explicitly; a four-component list alone is insufficient.

**SR-2.3 — Position four-vector**
- Inputs: SR-1.4 [REQUIRES]; SR-2.2 [REQUIRES]; SR-1.8 [REQUIRES].
- Inspect: `origin_dependence`, `transforming`, `displacements`.
- Graph/scope question: Preserve the explicit Four-vectors prerequisite alongside INSTANCE_OF; review possible redundant frame-change supports without hiding assumptions.

**SR-2.4 — Velocity four-vector**
- Inputs: SR-2.1 [DERIVES_FROM]; SR-2.3 [DERIVES_FROM]; MATHS-1.4 [CONSTRUCTED_FROM].
- Inspect: `why_tau`, `components`, `fixed_norm`.
- Graph/scope question: The three direct derivation/construction inputs already form a useful combination argument; keep the massless limitation visible.

**SR-2.5 — Momentum four-vector**
- Inputs: SR-2.4 [DERIVES_FROM]; SR-1.6 [REQUIRES].
- Inspect: `components`, `work_energy`, `energy_physical_input`, `invariant_norm`.
- Graph/scope question: Do not let the four-velocity edge imply that geometry alone establishes the momentum law or energy conservation; state remaining physical inputs.

**SR-2.6 — Mass-energy equivalence**
- Inputs: SR-2.5 [DERIVES_FROM].
- Inspect: `from_momentum`, `light_emission`, `light_inertia`, `rest_frame`, `systems`.
- Graph/scope question: The graph carries the four-momentum route; review the light-energy transformation/conservation assumptions of the alternative without adding cyclic or misleading dependencies.

### SR-3 Action and Field Theory

| Concept | Blocks | Def/Der/Exp | Tutorial blocks | Review focus |
| --- | ---: | --- | ---: | --- |
| SR-3.1 Lagrangian | 9 | 1/0/1 | 0 | Separate the general definition and choice of L from a relativistic example; state that stationarity and dynamics are additional structure. |
| SR-3.2 Action principle | 9 | 1/0/1 | 0 | Present stationarity as a dynamical principle; make allowed variations, fixed endpoints and the first-variation test explicit. |
| SR-3.3 Euler–Lagrange equations | 10 | 1/1/0 | 0 | Assemble first variation, integration by parts, boundary cancellation and arbitrary interior variation into a complete included derivation; add an accessible explanation. |
| SR-3.4 Canonical momentum | 9 | 1/0/1 | 0 | Explain the velocity derivative and its boundary-term role; preserve canonical versus mechanical momentum and constrained/invertibility caveats. |
| SR-3.5 Hamiltonian formalism | 10 | 1/0/0 | 0 | Complete the Legendre-transform differential argument and Hamilton equations; state regularity, explicit time dependence and the energy caveat. |
| SR-3.6 Scalar field | 9 | 1/0/2 | 0 | Distinguish field value from its coordinate formula; explain derivatives without confusing a scalar field with a constant. |
| SR-3.7 Vector field | 9 | 1/0/1 | 0 | Define the event assignment and transformation of both argument and components; use generic vector notation consistently with the reserved EM potential symbol. |
| SR-3.8 Field Lagrangian | 11 | 1/0/1 | 0 | Combine local field ingredients, scalar action and spacetime integration; distinguish the density from the action and from energy density. |
| SR-3.9 Field equations | 11 | 1/0/0 | 0 | Show the field first variation, spacetime integration by parts and boundary condition through to the local Euler-Lagrange equation; provide a teaching explanation. |

**SR-3.1 — Lagrangian**
- Inputs: SR-1.7 [REQUIRES]; SR-2.2 [REQUIRES].
- Inspect: `local_to_global`, `relativistic_building_blocks`, `simple_example`.
- Graph/scope question: Current interval/four-vector prerequisites describe relativistic examples, not every Lagrangian; resolve generic versus SR scope.

**SR-3.2 — Action principle**
- Inputs: SR-3.1 [REQUIRES].
- Inspect: `fixed_endpoints`, `variation_parameter`, `relativistic_actions`.
- Graph/scope question: Do not derive the principle from the Euler-Lagrange equations; the Lagrangian is the stated starting input.

**SR-3.3 — Euler–Lagrange equations**
- Inputs: SR-3.2 [DERIVES_FROM]; SR-3.1 [REQUIRES].
- Inspect: `first_variation`, `integration_by_parts`, `arbitrary_variation`, `result`.
- Graph/scope question: The graph inputs are present, but the Derivation recipe currently excludes two essential Derivation-step blocks and the Result.

**SR-3.4 — Canonical momentum**
- Inputs: SR-3.1 [DERIVES_FROM].
- Inspect: `boundary_origin`, `hamiltonian_role`, `velocity_dependent`.
- Graph/scope question: The Lagrangian dependency is real; classify definition/construction honestly rather than claiming a separate physical law.

**SR-3.5 — Hamiltonian formalism**
- Inputs: SR-3.4 [DERIVES_FROM].
- Inspect: `legendre_transform`, `differential_derivation`, `hamilton_equations`.
- Graph/scope question: The derivation also uses Euler-Lagrange dynamics, currently RELATED only; review the support needed beyond canonical momentum.

**SR-3.6 — Scalar field**
- Inputs: SR-1.4 [REQUIRES]; SR-1.8 [REQUIRES].
- Inspect: `coordinates`, `vector_contrast`, `derivatives`.
- Graph/scope question: A scalar transformation rule is defining structure, not dynamics; preserve event/frame prerequisites and avoid forward field-equation assumptions.

**SR-3.7 — Vector field**
- Inputs: SR-2.2 [REQUIRES].
- Inspect: `scalar_contrast`, `argument_and_components`, `derivative_role`.
- Graph/scope question: Four-vectors is an explicit prerequisite; do not manufacture a derivation from later electromagnetic examples.

**SR-3.8 — Field Lagrangian**
- Inputs: SR-3.2 [DERIVES_FROM]; SR-1.5 [REQUIRES].
- Inspect: `locality`, `scalar_action`, `variation_preview`, `example_scalar`, `example_em`.
- Graph/scope question: Current action/locality supports need to match the field-type and Lorentz assumptions actually used; state units and measure conventions.

**SR-3.9 — Field equations**
- Inputs: SR-3.8 [DERIVES_FROM]; SR-3.3 [DERIVES_FROM]; SR-1.8 [REQUIRES].
- Inspect: `particle_to_field`, `euler_lagrange`, `integration_by_parts`.
- Graph/scope question: Both principal supports exist, but no block is currently included as Derivation or Explanation under those kinds.

### SR-4 Covariant Electromagnetism

| Concept | Blocks | Def/Der/Exp | Tutorial blocks | Review focus |
| --- | ---: | --- | ---: | --- |
| SR-4.1 Vector potential \(A_\mu\) | 10 | 1/0/1 | 0 | Clarify the four-potential convention, local field assignment and gauge redundancy; do not describe the potential as derived from its later field equations. |
| SR-4.2 Field tensor \(F_{\mu\nu}\) | 11 | 1/0/1 | 0 | Develop the antisymmetric derivative, component count and homogeneous identity as self-contained arguments, using one fixed index/sign convention. |
| SR-4.3 Electric field | 10 | 1/1/0 | 0 | Connect the operational force definition, observer split and potential formula; show the intermediate component calculation. |
| SR-4.4 Magnetic field | 11 | 1/1/1 | 0 | Connect the spatial antisymmetric components to curl A; distinguish a local potential construction from global/topological claims. |
| SR-4.5 Electromagnetic field | 10 | 1/0/2 | 0 | Explain how one tensor yields observer-dependent E/B and how boosts mix them; avoid making component recombination sound like a new independent physical law. |
| SR-4.6 Gauge invariance | 11 | 1/1/1 | 0 | Retain and expand the commuting-partials cancellation; state smoothness, redundancy and which physical quantities are unchanged. |
| SR-4.7 Minimal coupling | 11 | 1/1/1 | 0 | Specify an action/coupling convention and what makes it minimal; replace the force-law preview with an actual argument or correctly classified preview. |
| SR-4.8 Lorentz force law | 11 | 1/1/0 | 0 | Perform the charged-path variation through to the antisymmetric field tensor, then connect covariant force, three-force and power. |
| SR-4.9 Lorenz gauge | 9 | 1/1/1 | 0 | Separate choosing/reaching the gauge, residual freedom and its use in Maxwell's potential equation; make the cancellation explicit. |
| SR-4.10 Momentum density (Poynting vector) | 11 | 0/1/1 | 0 | Correct the kind of the existing Definition; distinguish energy flux S from momentum density g=S/c² and carry units through the tensor extraction. |
| SR-4.11 Stress–energy of EM field | 10 | 1/0/0 | 0 | Explain the quadratic construction and its energy/flux/stress components with explicit normalisation; provide both derivation and teaching content. |
| SR-4.12 Energy density of EM field | 10 | 0/0/1 | 0 | Correct the kind of the existing Definition; actually extract T00 or explain the electric/magnetic energy contributions with consistent SI factors. |
| SR-4.13 Gauge fixing | 10 | 1/0/1 | 0 | Explain representative choice, gauge-invariant observables and remaining freedom; distinguish imposing a condition from fully removing redundancy. |

**SR-4.1 — Vector potential \(A_\mu\)**
- Inputs: SR-1.4 [REQUIRES].
- Inspect: `field_strength`, `gauge_freedom`, `lagrangian_role`.
- Graph/scope question: Vector-field link is INSTANCE_OF only and excluded from both trees; review a genuine prerequisite alongside the taxonomic relation.

**SR-4.2 — Field tensor \(F_{\mu\nu}\)**
- Inputs: SR-4.1 [CONSTRUCTED_FROM]; SR-1.6 [REQUIRES].
- Inspect: `antisymmetry`, `frame_split`, `homogeneous_hint`.
- Graph/scope question: Potential construction and metric prerequisite exist; decide which constructions belong in the two recipe kinds.

**SR-4.3 — Electric field**
- Inputs: SR-1.1 [REQUIRES].
- Inspect: `tensor_split`, `potential_formula`, `force_meaning`.
- Graph/scope question: Field-tensor link is COMPONENT_OF only; the Derivation tree currently has no supports although the body uses tensor/potential structure.

**SR-4.4 — Magnetic field**
- Inputs: —.
- Inspect: `spatial_components`, `curl_potential`, `no_monopole_hint`.
- Graph/scope question: Only COMPONENT_OF and RELATED links are present, so both trees are roots despite the derivation body.

**SR-4.5 — Electromagnetic field**
- Inputs: SR-4.2 [REQUIRES]; SR-4.3 [REQUIRES]; SR-4.4 [REQUIRES]; SR-1.8 [REQUIRES].
- Inspect: `six_component_package`, `lorentz_mixing`, `locality`.
- Graph/scope question: Current prerequisites are explicit; select an honest construction argument and retain the tensor versus component distinction.

**SR-4.6 — Gauge invariance**
- Inputs: SR-4.2 [DERIVES_FROM]; SR-4.5 [REQUIRES].
- Inspect: `cancellation`, `observable_focus`, `gauge_fixing`.
- Graph/scope question: The field-tensor derivation support is useful; separate the classical local statement from broader quantum/topological claims.

**SR-4.7 — Minimal coupling**
- Inputs: SR-4.1 [CONSTRUCTED_FROM]; SR-4.6 [DERIVES_FROM].
- Inspect: `worldline_term`, `momentum_replacement`, `force_law_preview`.
- Graph/scope question: Gauge invariance constrains couplings but does not generally select minimal coupling uniquely; do not borrow the force law back into its own derivation.

**SR-4.8 — Lorentz force law**
- Inputs: SR-3.2 [DERIVES_FROM]; SR-4.7 [DERIVES_FROM]; SR-2.4 [REQUIRES]; SR-2.5 [REQUIRES]; SR-4.2 [REQUIRES].
- Inspect: `construction`, `derivative_combination`, `three_vector_form`, `power`.
- Graph/scope question: Action plus minimal coupling supply the main derivation; the only current Derivation block derives power, not the force law.

**SR-4.9 — Lorenz gauge**
- Inputs: SR-4.1 [REQUIRES]; SR-4.5 [REQUIRES]; SR-4.6 [REQUIRES].
- Inspect: `gauge_invariance_context`, `maxwell_simplification`, `residual_freedom`.
- Graph/scope question: The Maxwell simplification body uses a RELATED input while the wave equation derives from Lorenz gauge; avoid turning this into a dependency cycle.

**SR-4.10 — Momentum density (Poynting vector)**
- Inputs: SR-4.3 [CONSTRUCTED_FROM]; SR-4.4 [CONSTRUCTED_FROM]; SR-4.5 [REQUIRES].
- Inspect: `definition`, `tensor_origin`, `momentum_density`.
- Graph/scope question: The title currently foregrounds momentum density while its Definition defines energy flux; review that mismatch. COMPONENT_OF is not a derivation support.

**SR-4.11 — Stress–energy of EM field**
- Inputs: SR-1.6 [CONSTRUCTED_FROM]; SR-4.2 [CONSTRUCTED_FROM].
- Inspect: `formula`, `components`, `quadratic`.
- Graph/scope question: Metric and field tensor are existing construction inputs; INSTANCE_OF general energy-momentum is not traversed by the recipes.

**SR-4.12 — Energy density of EM field**
- Inputs: SR-4.3 [CONSTRUCTED_FROM]; SR-4.4 [CONSTRUCTED_FROM]; SR-4.5 [REQUIRES].
- Inspect: `definition`, `tensor_component`, `why_squared`.
- Graph/scope question: Electric and magnetic construction inputs exist; the stress-energy COMPONENT_OF link currently supplies no reading-tree branch.

**SR-4.13 — Gauge fixing**
- Inputs: SR-4.6 [DERIVES_FROM]; SR-4.1 [REQUIRES]; SR-4.2 [REQUIRES]; SR-4.5 [REQUIRES].
- Inspect: `why_needed`, `physical_observables`, `residual_freedom`.
- Graph/scope question: Gauge-invariance derivation support exists; provide a construction rather than a purported new field law.

### SR-5 Field Dynamics and Radiation

| Concept | Blocks | Def/Der/Exp | Tutorial blocks | Review focus |
| --- | ---: | --- | ---: | --- |
| SR-5.1 Noether's theorem | 11 | 0/1/2 | 0 | Correct the Definition kind and develop a real symmetry-to-current argument, including on-shell conditions and allowed boundary terms. |
| SR-5.2 Four-current | 9 | 1/0/0 | 0 | Explain how charge density and current combine and transform; distinguish defining j from imposing its conservation. |
| SR-5.3 Maxwell's equations | 13 | 1/1/0 | 0 | Show the potential variation of the specified EM action with source term; separately derive the homogeneous identity, and add the physical teaching explanation. |
| SR-5.4 Charge conservation | 10 | 1/1/1 | 0 | Retain the antisymmetric/symmetric derivative cancellation and include the local-to-integral flow argument where appropriate. |
| SR-5.5 Energy--momentum tensor | 11 | 1/1/0 | 0 | Develop the translation-symmetry calculation yielding the canonical tensor; distinguish matter/field/total tensors, improvement and exchange terms. |
| SR-5.6 Wave equation | 9 | 0/1/1 | 0 | Correct the Definition kind and decide whether this is a generic wave operator or the EM potential equation; show the Maxwell-to-wave cancellation. |
| SR-5.7 Electromagnetic waves | 11 | 1/1/1 | 0 | Derive the plane-wave dispersion, transverse constraints and E/B relation, rather than only restating the potential wave equation. |
| SR-5.8 Radiation reaction | 11 | 1/1/2 | 0 | Keep this a controlled qualitative/effective-theory account; distinguish radiated energy balance from a complete instantaneous self-force law. |

**SR-5.1 — Noether's theorem**
- Inputs: SR-3.2 [DERIVES_FROM].
- Inspect: `definition`, `symmetry_of_action`, `derivation_sketch`, `field_theory`.
- Graph/scope question: Assess the field-action and equation-of-motion inputs behind the current very short sketch; do not treat every local gauge freedom as an independent physical conserved charge.

**SR-5.2 — Four-current**
- Inputs: —.
- Inspect: `definition`, `why_c`, `continuity`, `wire_example`.
- Graph/scope question: Only INSTANCE_OF four-vectors is stored; neither recipe has a support branch and there is no Derivation or Explanation block.

**SR-5.3 — Maxwell's equations**
- Inputs: SR-3.3 [DERIVES_FROM]; SR-3.8 [DERIVES_FROM]; SR-4.5 [REQUIRES]; SR-5.2 [REQUIRES].
- Inspect: `lagrangian_derivation`, `homogeneous_derivation`, `sourced_equation`, `three_vector_split`.
- Graph/scope question: Knit field Lagrangian and variational machinery together; check the most appropriate field-versus-particle Euler-Lagrange support and normalisation.

**SR-5.4 — Charge conservation**
- Inputs: SR-5.3 [DERIVES_FROM]; SR-5.2 [REQUIRES].
- Inspect: `maxwell_derivation`, `antisymmetry`, `integral_form`.
- Graph/scope question: The Maxwell route and current prerequisite are explicit; distinguish that consequence from independently assuming source conservation.

**SR-5.5 — Energy--momentum tensor**
- Inputs: SR-5.1 [DERIVES_FROM].
- Inspect: `noether_origin`, `canonical_form`, `component_meaning`, `improvement`.
- Graph/scope question: Noether supplies the current route; assess field-action assumptions and avoid claiming that an interacting subsystem is divergence-free on its own.

**SR-5.6 — Wave equation**
- Inputs: SR-4.9 [DERIVES_FROM]; SR-5.3 [DERIVES_FROM]; SR-4.1 [REQUIRES]; SR-5.2 [REQUIRES].
- Inspect: `definition`, `metric_structure`, `maxwell_origin`, `source_free`.
- Graph/scope question: Maxwell and Lorenz gauge are current derivation supports; keep the previously pruned metric edge under deliberate review rather than reinstating it automatically.

**SR-5.7 — Electromagnetic waves**
- Inputs: SR-5.6 [DERIVES_FROM]; SR-4.5 [REQUIRES].
- Inspect: `maxwell_origin`, `transverse`, `speed`, `triad`.
- Graph/scope question: The graph follows wave equation; review how Maxwell constraints needed beyond the scalar wave equation reach the tree without adding shortcuts for convenience.

**SR-5.8 — Radiation reaction**
- Inputs: SR-5.5 [DERIVES_FROM]; SR-5.7 [DERIVES_FROM]; SR-4.8 [REQUIRES].
- Inspect: `energy_balance`, `external_vs_self`, `effective_view`, `pathologies`.
- Graph/scope question: Specify near-field/bound-field and approximation limitations where relevant; precise source support is already an open worklist item before expanding this treatment.

## Tutorial and source review

| Tutorial | Distinct SR block targets |
| --- | ---: |
| using-physicskg | 1 |
| rest-energy-to-sr-foundations | 18 |
| time-dilation | 15 |

The baseline contains the exact tutorial/step mapping. Preserve target IDs even
when titles change, then inspect dialogue references and the highlighted extent.
Question IDs/options are preservation inputs, not an invitation to re-author study questions.

Use the existing SR bibliography and block/concept reference links. The
[rest-energy review](rest_energy_tutorial_review.md) already records important
physical-input boundaries; preserve that work. The
[source worklist](source_review_worklist.md) specifically requests more precise
radiation-reaction sourcing before expanding that subject. New or materially
changed physical arguments need primary/source checking in the module passes;
this inventory has not invented new locators.

## Execution checkpoints

1. SR-1 establishes the title/statement/body style and resolves the metric/interval/
   Lorentz route before downstream reuse.
2. SR-2 protects the physical energy argument and both major tutorial routes.
3. SR-3 assembles the variational steps into reusable combination arguments.
4. SR-4 fixes taxonomy-only reading supports and the EM convention chain.
5. SR-5 joins symmetry, conservation and propagation inputs, keeping radiation
   reaction within a defensible scope.

For each module: re-read the authoring guide, finish title/statement/body review,
audit its edge notes, verify preserved IDs/slots/questions/tutorial targets, run
validation and relevant tests, rebuild locally, then commit locally. Review joint
SR+Maths trees before final verification. No feature-branch push or preview
publication is implied by this audit.
