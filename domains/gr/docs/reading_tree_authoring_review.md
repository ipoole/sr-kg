# GR teaching-content revision

Revision begun 13 November 2026, using the current six-module membership.
The starting inventory is 56 concepts and 318 blocks without statements. Stable
concept/block/question identities, local clarification paths and graphics are
retained. Each module is reviewed against the shared authoring guide at teaching
expansivity 70. New canonical Graphic blocks expose the existing illustrations;
no artwork regeneration is required.

| Module | Status | Main teaching work |
| --- | --- | --- |
| GR-1 | Revised | Operational free fall, metric measurement, local/global distinctions; statements, consolidated kinds and local clarifications. |
| GR-2 | Revised | Connections and basis changes; explicit Levi-Civita, particle-action and deviation arguments with optional algebra. |
| GR-3 | Revised | Curvature commutator, contraction information loss, differential identity and full interior action variation. |
| GR-4 | Revised | Rest-frame fluid construction, pressure work, matter response, coupled variation and explicit trace reversal. |
| GR-5 | Revised | Distinct approximation regimes; crest counting, bending integral, precession resonance and constrained linear waves. |
| GR-6 | Revised | Horizon-crossing cancellation, causal escape, singular incompleteness, orbital stability and advanced photon capture. |

## Editorial decisions

- Keep the atlas's complete convention bundle: +---, the registered Riemann
  definition, positive matter metric variation and negative gravitational action.
  A source's signature alone is insufficient to translate its equations.
- Definitions and empirical principles do not acquire artificial proof blocks.
  The free-fall/tidal argument motivates metric gravity; it does not uniquely
  derive Einstein's field equations.
- Existing alternative-derivation/module-order decisions remain recorded in
  [the edge review](derivation_edge_review.md). No module reshuffle is implicit
  in this content pass.
- Primary reference: Tong's GR lectures, particularly §§1–3 for the initial
  module; use the atlas convention rather than copying source signs.

The baseline file records existing identities and clarification paths for
regression checks. It is not a second copy of the exposition.

GR-3 adds the genuine Einstein-tensor → Bianchi-identity derivation input.
This is internal to the curvature module and preserves its acyclic ordering.

GR-4 adds understanding prerequisites from the fluid to stress-energy and from
the cosmological constant to the field equation. Taxonomic Component/Instance
relations alone do not carry those teaching dependencies.

## Final consistency review

All 56 concepts now have a canonical Definition and Explanation, and every one
of the 382 blocks has an explicit statement. The pass adds 56 canonical Graphic
blocks and eight additional teaching/definition/advanced units. There are 50
local clarifications, including the retained Schwarzschild radial-equation
clarification. Bodies of 144 original blocks were revised or expanded; concise
existing definitions, examples and historical notes were retained where suitable.
All 224 study questions and their options are unchanged.

The final prose pass expands 37 remaining compressed explanations. Motivation
edges from metric gravity to equivalence/tides, and from deviation to tidal
intuition, now use Requires rather than suggesting a mathematical derivation.
The fluid's conservation projection also has its genuine understanding prerequisite.
The concept dependency graph and six-module quotient remain acyclic.

The previously documented Riemann/deviation module-order question, alternative
variational routes and the Schwarzschild input to perihelion calculations remain
explicit limitations of the teaching DAG. The deviation proof links directly to
the curvature convention; a local clarification supplies the spherical orbit
reduction. These prose links do not silently change module membership or pretend
that every mathematical input is currently a primary tree edge.

Validation has no errors. Remaining warnings concern contextual/transitive
references, redundant teaching supports and existing display ordering; they are
editorial diagnostics, not suppressed failures. Real MathJax checks cover all
56 concepts at phone and desktop widths, plus generated Derivation and Teaching
routes from the field equations, waves and exact orbital dynamics. Existing
annotation IDs and local clarification paths are checked against the baseline.

Final verification: 776 unit tests, 347 fast browser cases and 94 full-data
browser cases pass. The existing atomic-note regression now targets the canonical
GR Graphic block and verifies placement after navigation, rather than expecting
the retired standalone figure container. Validation reports 0 errors and 216
editorial warnings. The full viewer is rebuilt in ignored `output/PhysicsKG.html`.
