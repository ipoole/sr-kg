# Concept Edge-Type Review Worklist

This worklist records a conservative review of concept-level edge types. It is
an editorial/design document for now. The machine-readable graph remains
`data/edges.csv` plus `data/edges_key.csv` until a migration is deliberately
made.

## Purpose

The atlas currently uses a deliberately small relation vocabulary:

| Relation | Count | Current Role |
| --- | ---: | --- |
| `DERIVES_FROM` | 37 | A can be mathematically derived from B. |
| `REQUIRES` | 52 | A requires knowledge of B. |
| `CONSTRUCTED_FROM` | 8 | A is built structurally from B without necessarily being derived as a theorem. |
| `COMPONENT_OF` | 4 | A is a component, frame split, or extracted part of B. |
| `INSTANCE_OF` | 7 | A is a concrete example, special case, or named instance of B. |
| `RELATED` | 33 | A and B are closely associated, without a sharper relation. |

This has kept the graph manageable, but `RELATED` and some broad
`DERIVES_FROM` edges are now carrying several distinct meanings. Sharper edge
types should support better graph views, derivation traces, concept previews,
and future curation without making ordinary authoring fussy.

## Design Rules

- Keep the default direction as `source -> target`, meaning the source concept
  depends on, is built from, or is interpreted through the target concept.
- Keep `DERIVES_FROM` strict. Use it when there is a defensible mathematical or
  logical derivation dependency, not merely when a formula mentions another
  object.
- Keep `REQUIRES` for essential prior knowledge. Avoid using it for
  loose connections, examples, or every object appearing in an equation.
- Keep `RELATED` as a last resort, not a dumping ground.
- Add only a few relation types at a time. A relation type should earn its
  place by improving multiple edges and by supporting a plausible viewer
  feature.

## Adopted First-Pass Vocabulary

These relations have been added to `data/edges_key.csv`. The first migrations
have deliberately been limited to high-confidence and structurally obvious
edges, with later-layer candidates left for separate review.

| Relation | Directed | Meaning | Example |
| --- | --- | --- | --- |
| `CONSTRUCTED_FROM` | Yes | A is algebraically, differentially, or structurally built from B. This is weaker than a full derivation theorem. | `sr.field_tensor -> sr.vector_potential` |
| `COMPONENT_OF` | Yes | A is a component, frame split, or extracted part of B. | `sr.electric_field -> sr.field_tensor` |
| `INSTANCE_OF` | Yes | A is a concrete example, special case, or named instance of B. | `sr.lorenz_gauge -> sr.gauge_fixing` |

These three cover many current ambiguities while staying close to the existing
mental model.

## Watchlist Vocabulary

These may be useful later, but should not be added until repeated curation work
shows they are worth the extra concept count.

| Relation | Possible Meaning | Reason to Defer |
| --- | --- | --- |
| `REFORMULATES` | A is an equivalent or near-equivalent reformulation of B. | Useful for Hamiltonian/Lagrangian mechanics, but may overlap with `DERIVES_FROM`. |
| `PRESERVED_BY` | A structure is preserved by a transformation or symmetry. | Useful for intervals, light cones, and Lorentz transformations, but direction and UI treatment need thought. |
| `CONTRASTS_WITH` | A and B are deliberately contrasted. | Useful pedagogically, but may be too presentation-like for the core graph. |
| `USES_AS_EXAMPLE` | A concept uses B as an illustrative example. | This may belong in content links or study questions rather than concept edges. |
| `SIMPLIFIES` | A condition or choice simplifies equations in B. | Useful for Lorenz gauge and Maxwell equations, but narrow. |
| `FORMULATED_WITH` | A law or equation is written using B as one of its mathematical objects. | Useful for Lorentz force law, but may be too weak for graph navigation. |
| `COMPATIBLE_WITH` | A must respect B but is not derived from B. | Broad and potentially vague; risks becoming a new `RELATED`. |

## Candidate CSV Edits

These are proposed edits, some of which have now been applied. The `note` text
can usually remain unchanged for a first migration.

### Applied In Layer 1-4 First Pass

| Source | Target | Previous | Current | Reason |
| --- | --- | --- | --- | --- |
| `sr.position_four_vector` | `sr.four_vectors` | `REQUIRES` | `INSTANCE_OF` | Position four-vector is a specific four-vector. |
| `sr.velocity_four_vector` | `sr.four_vectors` | `RELATED` | `INSTANCE_OF` | Velocity four-vector is a specific four-vector. |
| `sr.momentum_four_vector` | `sr.four_vectors` | `RELATED` | `INSTANCE_OF` | Momentum four-vector is a specific four-vector. |

### Applied In Layer 5-8 First Pass

| Source | Target | Previous | Current | Reason |
| --- | --- | --- | --- | --- |
| `sr.vector_potential` | `sr.vector_field` | `REQUIRES` | `INSTANCE_OF` | Vector potential is a specific relativistic vector field. |
| `sr.field_tensor` | `sr.vector_potential` | `DERIVES_FROM` | `CONSTRUCTED_FROM` | \(F_{\mu\nu}\) is constructed from derivatives of \(A_\mu\). |
| `sr.electric_field` | `sr.field_tensor` | `DERIVES_FROM` | `COMPONENT_OF` | \(\mathbf E\) is a frame-dependent time-space split of \(F_{\mu\nu}\). |
| `sr.magnetic_field` | `sr.field_tensor` | `DERIVES_FROM` | `COMPONENT_OF` | \(\mathbf B\) is a frame-dependent spatial split of \(F_{\mu\nu}\). |
| `sr.four_current` | `sr.four_vectors` | `DERIVES_FROM` | `INSTANCE_OF` | Four-current is a particular four-vector, not derived from the general concept. |
| `sr.minimal_coupling` | `sr.vector_potential` | `DERIVES_FROM` | `CONSTRUCTED_FROM` | Minimal coupling is built by introducing \(A_\mu\). |
| `sr.lorenz_gauge` | `sr.gauge_fixing` | `RELATED` | `INSTANCE_OF` | Lorenz gauge is a specific gauge fixing. |

### Applied In Layer 9-11 First Pass

| Source | Target | Previous | Current | Reason |
| --- | --- | --- | --- | --- |
| `sr.em_energy_density` | `sr.electric_field` | `DERIVES_FROM` | `CONSTRUCTED_FROM` | EM energy density is algebraically built from field squares. |
| `sr.em_energy_density` | `sr.magnetic_field` | `DERIVES_FROM` | `CONSTRUCTED_FROM` | EM energy density is algebraically built from field squares. |
| `sr.em_energy_density` | `sr.energy_momentum_tensor` | `DERIVES_FROM` | `COMPONENT_OF` | EM energy density is the time-time component of the tensor. |
| `sr.poynting_vector` | `sr.energy_momentum_tensor` | `DERIVES_FROM` | `COMPONENT_OF` | Poynting vector and momentum flow appear in mixed time-space tensor components. |
| `sr.em_stress_energy` | `sr.metric_tensor` | `DERIVES_FROM` | `CONSTRUCTED_FROM` | The EM tensor formula uses the metric to contract and raise/lower indices. |
| `sr.em_stress_energy` | `sr.field_tensor` | `DERIVES_FROM` | `CONSTRUCTED_FROM` | The EM tensor is algebraically built from \(F_{\mu\nu}\). |
| `sr.em_stress_energy` | `sr.energy_momentum_tensor` | `RELATED` | `INSTANCE_OF` | EM stress-energy is the electromagnetic-field instance of the general tensor. |
| `sr.poynting_vector` | `sr.electric_field` | `DERIVES_FROM` | `CONSTRUCTED_FROM` | \(\mathbf S\) is built from \(\mathbf E\times\mathbf B\). |
| `sr.poynting_vector` | `sr.magnetic_field` | `DERIVES_FROM` | `CONSTRUCTED_FROM` | \(\mathbf S\) is built from \(\mathbf E\times\mathbf B\). |

### Applied During Edge-Note Review

| Source | Target | Previous | Current | Reason |
| --- | --- | --- | --- | --- |
| `sr.lorenz_gauge` | `sr.vector_potential` | `DERIVES_FROM` | `REQUIRES` | The condition is imposed on the potential, but is not derived from it alone. |
| `sr.lorentz_force_law` | `sr.velocity_four_vector` | `DERIVES_FROM` | `REQUIRES` | Four-velocity appears in the covariant equation; this is closer to a formulation dependency. |
| `sr.lorentz_force_law` | `sr.momentum_four_vector` | `DERIVES_FROM` | `REQUIRES` | Four-momentum is the quantity whose rate of change is described by the law. |
| `sr.lorentz_force_law` | `sr.field_tensor` | `DERIVES_FROM` | `REQUIRES` | The field tensor appears in the law, but the derivation comes through the action/minimal-coupling route. |
| `sr.poynting_vector` | `sr.electromagnetic_field` | `DERIVES_FROM` | `REQUIRES` | The vector is an energy-flow quantity for electromagnetic field configurations, not derived from the abstract field concept alone. |
| `sr.energy_momentum_tensor` | `sr.field_tensor` | `DERIVES_FROM` | `RELATED` | The general tensor concept is broader; the field-tensor construction belongs to the electromagnetic instance. |

### High Confidence

No remaining high-confidence rows are currently pending after the first
layer-based passes.

### Medium Confidence

These are plausible, but should be checked against the desired graph view
before migration.

| Source | Target | Current | Proposed | Reason / Question |
| --- | --- | --- | --- | --- |
| `sr.electromagnetic_field` | `sr.field_tensor` | `REQUIRES` | `COMPONENT_OF` or keep `REQUIRES` | The EM field is represented by the tensor; `COMPONENT_OF` direction is not quite right. |
| `sr.electromagnetic_field` | `sr.electric_field` | `REQUIRES` | `CONSTRUCTED_FROM` or keep `REQUIRES` | The unified EM field packages electric and magnetic fields, but the direction is pedagogical. |
| `sr.electromagnetic_field` | `sr.magnetic_field` | `REQUIRES` | `CONSTRUCTED_FROM` or keep `REQUIRES` | Same issue as electric field. |
| `sr.position_four_vector` | `sr.metric_tensor` | `RELATED` | `CONSTRUCTED_FROM` or keep `RELATED` | Metric contractions give intervals between position vectors; the concept itself is not constructed from the metric. |
| `sr.lagrangian` | `sr.proper_time` | `RELATED` | `CONSTRUCTED_FROM` or keep `RELATED` | Relativistic particle Lagrangians may use proper time, but the general concept does not. |
| `sr.action_principle` | `sr.proper_time` | `RELATED` | `CONSTRUCTED_FROM` or keep `RELATED` | Relativistic actions often use proper time, but the action principle is broader. |
| `sr.action_principle` | `sr.four_vectors` | `RELATED` | `CONSTRUCTED_FROM` or keep `RELATED` | Relativistic actions use Lorentz scalars from four-vectors, but this may be too broad. |
| `sr.hamiltonian_formalism` | `sr.lagrangian` | `DERIVES_FROM` | `REFORMULATES` | Strong candidate if `REFORMULATES` is adopted later. |
| `sr.hamiltonian_formalism` | `sr.euler_lagrange_equations` | `RELATED` | `REFORMULATES` | Hamilton's equations are equivalent when the Legendre transform is valid. |

### Probably Keep As `RELATED`

These seem genuinely associative or pedagogical rather than structural.

| Source | Target | Reason |
| --- | --- | --- |
| `sr.principle_of_relativity` | `sr.constancy_of_speed_of_light` | Foundational postulates jointly constrain SR but neither derives from the other. |
| `sr.metric_tensor` | `sr.four_vectors` | They mutually support scalar products; a future `MEASURES` relation may be better, but not yet. |
| `sr.scalar_field` | `sr.four_vectors` | Pedagogical contrast between transformation behaviours. |
| `sr.vector_field` | `sr.scalar_field` | Pedagogical contrast. |
| `sr.magnetic_field` | `sr.electric_field` | Mutual frame-dependent components; `RELATED` is acceptable unless a paired-component relation is added. |
| `sr.canonical_momentum` | `sr.momentum_four_vector` | Contrast between canonical and kinetic/relativistic momentum. |
| `sr.canonical_momentum` | `sr.vector_potential` | Useful example of canonical/mechanical distinction. |
| `sr.noether_theorem` | `sr.canonical_momentum` | Example of cyclic-coordinate conservation. |
| `sr.electromagnetic_waves` | `sr.four_current` | Source-free condition is important but not a structural dependency. |
| `sr.gauge_fixing` | `sr.lorentz_invariance` | Lorenz gauge respects Lorentz invariance, but this is a choice property. |

## Suggested Migration Sequence

1. Continue applying the remaining high-confidence edits in small layer-based
   passes.
2. Regenerate and inspect the viewer after each pass, especially derivation
   sections and graph highlighting.
3. Decide whether the viewer should treat `CONSTRUCTED_FROM` as derivation-like
   in some modes, or whether strict derivation traces should continue to use
   only `DERIVES_FROM`.
4. Revisit medium-confidence edges after using the new vocabulary on real
   content for a while.

## Open Questions

- Should `CONSTRUCTED_FROM` participate in derivation traces, or remain a
  separate construction trace?
- Is `COMPONENT_OF` the right name for frame-dependent splits such as electric
  and magnetic fields, or should this eventually be `FRAME_SPLIT_OF`?
- Does `INSTANCE_OF` belong in the concept graph, or should type hierarchy be a
  separate mechanism later?
- Should high-level compatibility relations such as Lorentz covariance live in
  concept edges, content blocks, or a future notation/convention system?
