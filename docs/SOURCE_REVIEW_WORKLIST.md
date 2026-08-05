# Source Review Worklist

This worklist records the source-locator pass for the current SR/CF knowledge
base. It should be used when checking TTM and TRR directly. Do not invent page
or section locators from memory; update `data/reference_links.csv` only after
checking the source text.

The machine-readable source links live in `data/reference_links.csv`. This file
is an editorial worklist, not a second runtime source of truth.

## Current State

- Registered sources are `ttm.sr_cf` (`TTM II`) and `penrose.rtr` (`TRR`).
- Most source links already attach to content blocks rather than whole
  concepts, which is the right granularity.
- One TTM link has a specific locator:
  `sr.lorentz_transformations.boost_formula` -> `TTM II, 1.3 General Lorentz Transformation`.
- The early layer-1 links use broad `TTM II, Ch. 1` locators.
- Most remaining links have blank locators with notes such as `add precise
  locator during source review`.

## Review Rules

When tightening a source locator:

1. Prefer section names over page numbers when the section title is stable.
2. Use page numbers only when they add useful precision.
3. Keep the short rendered form compact, for example
   `TTM II, 1.3 General Lorentz Transformation`.
4. Keep any uncertainty in the `note` column rather than pretending the link is
   exact.
5. Link the source to the most specific useful item: content block first,
   concept only when the whole treatment is supported, study question when the
   question is source-derived.

## TTM II Priorities

Start with TTM II because it is the spine for the current atlas. These entries
are broad or blank and should be checked against the book:

- Layer 1: inertial frames, constancy of light speed, and principle of
  relativity currently use `Ch. 1`.
- Layer 2: spacetime event and principle of locality need precise locators.
- Layer 3: metric tensor, spacetime interval, light cone, and Minkowski diagram
  need precise locators; Lorentz transformations already has one specific
  locator for the boost formula.
- Layer 4: proper time, four-vectors, position four-vector, velocity
  four-vector, momentum four-vector, and mass-energy equivalence need precise
  locators.
- Layer 5: Lagrangian, action principle, Euler-Lagrange equations, canonical
  momentum, Hamiltonian formalism, and Noether's theorem need precise locators.
- Layer 6: scalar field, vector field, field Lagrangian, and field equations
  need precise locators.
- Layer 7: vector potential, field tensor, electric field, magnetic field,
  electromagnetic field, four-current, and Maxwell's equations need precise
  locators.
- Layer 8: gauge invariance, minimal coupling, Lorentz force law, charge
  conservation, and Lorenz gauge need precise locators.
- Layers 9-11: energy-momentum tensor, Poynting vector, EM stress-energy, EM
  energy density, wave equation, electromagnetic waves, radiation reaction,
  Lorentz invariance, and gauge fixing need precise locators.

## TRR Priorities

TRR links should usually support geometric, structural, or historical context
rather than duplicate the TTM learning path. Check these groups:

- Minkowski geometry: metric tensor, spacetime interval, Lorentz
  transformations, light cone, Minkowski diagram, proper time, four-vectors,
  position/velocity/momentum four-vectors, and mass-energy equivalence.
- Variational mechanics and field theory: Lagrangian, action principle,
  Euler-Lagrange equations, canonical momentum, Hamiltonian formalism,
  Noether's theorem, scalar/vector fields, field Lagrangian, and field
  equations.
- Electromagnetic structure: vector potential, field tensor, electric/magnetic
  split, electromagnetic field, four-current, Maxwell's equations, gauge
  invariance, minimal coupling, Lorentz force law, charge conservation, Lorenz
  gauge, gauge fixing.
- Energy and radiation: energy-momentum tensor, Poynting vector, EM
  stress-energy, EM energy density, wave equation, electromagnetic waves, and
  radiation reaction.

## Completion Criteria

The source pass is complete when:

- `data/reference_links.csv` has no blank locator for TTM/TRR links unless the
  note explicitly explains why no precise locator is suitable.
- Broad `Ch. 1` locators have been replaced by section/page locators or marked
  as deliberately broad.
- `docs/concept_expositions.md` no longer carries generic "Add precise TTM and
  TRR locators" drafting issues except where a source genuinely still needs
  research.
- New source links added during later authoring follow the same standard.
