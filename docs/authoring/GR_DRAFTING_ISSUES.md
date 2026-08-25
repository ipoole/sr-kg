# GR Drafting Issues

This file collects cross-cutting issues found while adding General Relativity
and reusable mathematics concepts. Keep concept-specific notes in
`docs/authoring/gr_concept_expositions.md`; use this file when an issue affects
several concepts or the atlas design.

## Source Issues

- Add precise TTM GR source locators once the relevant volume/sections are
  identified.
- Add precise TRR locators for manifolds, coordinates, tangent spaces, tensors,
  equivalence principle, and curvature.
- Decide whether broad source links should be attached to seed concepts now or
  only after full exposition drafts are written.

## Schema And Validation Issues

- Validation currently treats `layer` as globally ordered. With domain-local
  numbering, layer-title and DAG layer-order warnings should become
  domain-aware.
- Decide whether `domain_title` should remain repeated in every `nodes.csv` row
  or eventually move to a separate domains table.
- Decide whether minimal seed concepts without study questions or graphics
  should be marked explicitly as incomplete.

## Atlas Issues

- Decide whether `sr.metric_tensor` should broaden into a shared metric concept
  or whether GR should keep a distinct `gr.metric_tensor`/spacetime metric
  concept.
- Decide whether `sr.energy_momentum_tensor` should broaden into a shared
  stress-energy concept or whether GR should keep a distinct
  `gr.stress_energy_tensor`.
- Recheck the edge directions around `gr.gravity_as_geometry`,
  `gr.equivalence_principle`, and `gr.tidal_gravity` after full exposition
  authoring.
- Keep cosmology deferred for now; black holes and gravitational waves remain
  in scope for the initial GR spine.

## Graphics Issues

- Create a shared visual language for manifolds, tangent spaces, local inertial
  frames, and curvature rather than one-off diagrams.
- Decide whether seed concepts should receive simple placeholder graphics
  before full authoring, or whether graphics should wait for concept-by-concept
  exposition passes.

## Viewer Issues

- Domain-filtered builds work for authoring, but the combined graph may need
  domain-aware colour, layout bands, or filtering once GR grows.
- Concept headers/details may need to show domain title for non-SR concepts
  when display IDs such as `GR 1.2` and `M 1.1` appear alongside SR IDs.
