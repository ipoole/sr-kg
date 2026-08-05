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
- Section-level locators have been checked against local PDFs in `docs/books`
  and added to every current TTM/TRR link in `data/reference_links.csv`.
- The early layer-1 `TTM II, Ch. 1` locators have been replaced by the book
  introduction or by named Lecture 1 sections.
- The only intentionally broad current links are the radiation-reaction
  background links. The checked TTM II and TRR text does not appear to contain a
  dedicated classical radiation-reaction section.

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

## Completed Section-Level Pass

TTM II now supplies the main learning-path references, with locators such as:

- `Introduction` for Einstein's two postulates.
- `1.2 Inertial Reference Frames`, `1.5 Minkowski's World`, and the named
  Lecture 1 Minkowski sections for early SR geometry.
- `3.4.1 Principle of Least Action`, `4.2 Fields and Action`, and related
  Lecture 4 sections for variational field theory.
- `6.3.1 The Action Integral and the Vector Potential`, `6.4 Interlude on the
  Field Tensor`, and Lecture 8 sections for electromagnetic structure.
- `10.1 Electromagnetic Waves` and Lecture 11 sections for waves, field energy,
  momentum density, and the energy-momentum tensor.

TRR now supplies structural and historical background, with locators such as:

- `§17.7 Light cones`, `§18.1 Euclidean and Minkowskian 4-space`, and `§18.2
  The symmetry groups of Minkowski space` for SR geometry.
- `§18.7 Relativistic energy and (angular) momentum` for four-momentum and
  mass-energy context.
- `§20.1 The magical Lagrangian formalism`, `§20.5 Lagrangian treatment of
  fields`, and `§20.6 How Lagrangians drive modern theory` for variational
  mechanics, field Lagrangians, and Noether's theorem.
- `§19.2 Maxwell's electromagnetic theory`, `§19.4 The Maxwell field as gauge
  curvature`, and `§19.5 The energy-momentum tensor` for electromagnetism,
  gauge structure, and field energy-momentum.

## Remaining Review Items

- Radiation reaction remains only broadly supported by the current TTM II/TRR
  links. Add a more specific source later if this concept is expanded.
- Page-level locators are not currently recorded. Add page numbers only where
  a section is too broad for a particular block.
- Future content imports should add source locators during authoring rather
  than relying on a later bulk pass.

## Completion Criteria

The source pass is complete when:

- `data/reference_links.csv` has no blank locator for TTM/TRR links unless the
  note explicitly explains why no precise locator is suitable.
- Broad `Ch. 1` locators have been replaced by section/page locators or marked
  as deliberately broad.
- `docs/authoring/concept_expositions.md` no longer carries generic "Add
  precise TTM and TRR locators" drafting issues except where a source genuinely
  still needs research.
- New source links added during later authoring follow the same standard.
