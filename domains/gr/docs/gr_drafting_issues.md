# GR Drafting Issues

The existing 56 GR concepts have completed full authoring. Runtime CSV carries
the text; the [notation glossary](../../../docs/authoring/notation_glossary.md#general-relativity)
records the conventions that future changes must preserve.

- Gravitational waves are now seeded in GR-5. Cosmology and advanced tools
  remain deferred; see the [concept plan](general_relativity_concept_plan.md).
- Supporting mathematics exposition and source work is retained in
  [the drafts](gr_concept_expositions.md).
- Cross-reference/edge warnings remain editorial prompts. Contextual comparisons
  and forward links do not automatically warrant new dependency edges. The full
  pass corrected misleading action-variation dependencies and the coordinate-
  singularity taxonomy; revisit other edges when their teaching role changes.
- Consider a separate domains table only if repeated `domain_title` metadata
  becomes a practical maintenance problem.

The SR and GR metric and stress-energy concepts remain separate, linked by
`RELATED`. This is settled policy, not a pending merge decision.

The [November derivation-edge review](derivation_edge_review.md) records repaired
Schwarzschild/action dependencies and remaining module-ordering or alternative-
derivation decisions. Those follow-ups are explicit limitations of the teaching DAG.
