# Adaptive Pedagogy and a Fine-Grained Knowledge Base

Captured on 2026-07-26.

## Context

The current implementation adds a useful first vertical slice for pedagogical
levels: the viewer can show concept prose and study questions within a selected
level range, and `sr.mass_energy_equivalence` is the pilot concept.

That implementation proves that the plumbing works, but it should not yet be
treated as the final pedagogical model. A single global pedagogical level is
likely too crude for the long-term physics atlas.

## Concern

Assigning a depth/detail value to every concept and every content block risks
becoming a heavy curation burden. The labels would often be subjective, and
maintaining them consistently across SR, GR, QM, mathematics, and other domains
could slow content development.

Presentation sequence is also awkward if it is manually authored everywhere.
Good exposition has dependency structure, but it also uses motivation,
foreshadowing, revisiting, examples, and optional derivations. A pure linear
sequence field is useful locally, but should not become the only organising
principle.

## Separate Dimensions

There are at least three different ideas that should not be collapsed into one
field.

| Dimension | Meaning | Example |
| --- | --- | --- |
| Conceptual depth | How advanced the item is within the subject | Electric field is shallower than Lorentz gauge |
| Presentation detail | How much hand-holding is shown | Extra algebraic steps can appear for a detailed derivation |
| Disclosure mechanism | How the extra material appears | Inline, folded, margin note, tooltip, linked concept, graph expansion |

A derivation might be appropriate for conceptual depth 3-4, while extra
interspersed algebraic support is useful only at a higher-detail setting.

## Graph-First Alternative

A promising alternative is to build the KB as a fine-grained graph with richly
typed edges, then derive depth, detail, visibility, and ordering where possible.

Instead of authoring pervasive labels such as:

```text
depth = 3
detail = 2
sequence = 40
```

we author more factual relationships:

```text
A requires B
A derives_from B
A elaborates B
A motivates B
A gives_example_of B
A supplies_algebra_for B
A warns_about B
A introduces_notation X
A illustrates B
A is_historical_context_for B
```

These relations are less subjective and more reusable. They can support several
views: graph visibility, study paths, derivation expansion, question selection,
reference browsing, and textual presentation.

## Derived Views

Given a richer graph, the system could calculate:

| Derived feature | Possible source |
| --- | --- |
| Conceptual depth | Weighted distance from foundations, prerequisites, and marked anchor concepts |
| Presentation order | Topological sorting through `requires`, `derives_from`, and `motivates`, with local sequence hints |
| Detail expansion | Inclusion of nodes linked by `supplies_algebra_for`, `elaborates`, or `gives_example_of` |
| Graph visibility | Current depth target plus importance, prerequisites, descendants, and collapse rules |
| Study path | Target concept plus unresolved prerequisite and derivation chains |

This should be hybrid rather than fully automatic. Sparse authored anchors and
local overrides will still be needed, especially for important narratives.

## Knowledge Items

The long-term internal model may need a general "knowledge item" layer, rather
than treating only concepts as graph nodes.

Possible item types:

```text
concept
content_block
derivation_step
equation
notation_entry
study_question
graphic
reference
historical_event
scientist
```

Typed edges could then connect any of these items. For example:

```text
sr.mee.derivation_step_2 derives_from sr.energy_momentum_relation
sr.mee.algebra_detail_1 supplies_algebra_for sr.mee.derivation_step_2
sr.mee.binding_energy_note elaborates sr.mass_energy_equivalence
sr.noether_theorem requires sr.action_principle
sr.maxwell_equations.graphic illustrates sr.maxwell_equations
```

This would make the project less like a table of concept descriptions and more
like a reusable physics knowledge base.

## Graph Behaviour

The graph should probably respond to the selected pedagogical view, not just the
details panel.

Possible behaviours:

| Behaviour | Use |
| --- | --- |
| Hide | Remove concepts beyond the current conceptual depth |
| Fade | Show advanced or assumed concepts as background context |
| Collapse | Replace a detailed subgraph with a higher-level parent concept |
| Expand | Reveal derivation steps, examples, or supporting notation |
| Reorder/refit | Prefer visible and currently relevant items in layout |

For example, at a low depth Noether's theorem might be hidden or collapsed into
the broader idea of symmetry and conservation. At a high depth, four-vectors
might remain available but be visually de-emphasised as assumed background.

## Text Decoration and Disclosure

Extra explanation need not always be a large `optional_details` block. More
subtle mechanisms may be useful:

| Mechanism | Use |
| --- | --- |
| Inline foldout | Reveal a short derivation or clarification in place |
| Tooltip | Explain a symbol, equality, or assumption |
| Margin note | Add context without breaking the main flow |
| Derivation expansion | Step through algebra or logic between two displayed equations |
| Linked aside | Jump to a related concept, misconception, historical note, or graphic |

Semantic colour coding could distinguish kinds of help:

| Colour role | Meaning |
| --- | --- |
| Explanatory support | Hand-holding, intuition, algebraic detail |
| Deeper insight | Subtle consequence, advanced interpretation |
| Warning | Misconception, common trap, invalid shortcut |
| Derivation | Hidden or expandable mathematical step |

This overlaps with ideas such as progressive disclosure, marginalia, adaptive
hypertext, semantic annotation, and literate derivation.

## Near-Term Recommendation

Do not invest heavily in extending the current one-dimensional PL model yet.
Keep it as a useful prototype.

The next design experiment should probably use one concept, such as
`sr.mass_energy_equivalence`, and decompose it into finer-grained items:

1. A small set of core concept/content items.
2. A few derivation steps.
3. One or two algebra-support items.
4. One misconception item.
5. One graphic or equation item if useful.
6. Rich typed edges among those items.

Then test which views can be derived from that structure before migrating the
whole KB.

## Open Questions

1. What is the smallest useful set of typed edges for the next experiment?
2. Should content blocks become first-class graph items, or should they remain
   attached to concepts with only selected block-to-block links?
3. How much authored ordering is still needed inside a concept narrative?
4. How should automatic depth be seeded: foundations, entry points, textbook
   sequence, or selected anchor concepts?
5. Which graph behaviours are most useful: hide, fade, collapse, expand, or
   some combination?
6. How should inline annotations be authored without making CSV editing painful?

## Current Working Answers

The next experiment should not start by designing edge types in the abstract.
It should start by writing a deep, detailed account of one concept, then
breaking that account into fine sections: a paragraph, sentence, derivation
line, or algebraic support step. The useful edge types should then emerge from
the actual content.

For now, fine-grained content blocks should remain attached to concepts rather
than becoming graph-level concepts themselves. The experiment can still link
blocks to one another internally.

Use dependency order as the primary ordering target. The draft order can be
preserved as provenance, but should not be treated as the ordering mechanism
being tested. If that means a familiar concept narrative starts somewhere less
famous, such as mass-energy equivalence not beginning with \(E=mc^2\), that is
acceptable for this experiment.

Seeding conceptual depth remains unresolved. Graph-view behaviours can also be
shelved until the content-block graph experiment has produced something real to
analyse. The authoring model for inline annotations remains an open issue.

The first concrete experiment is:

- [Mass-Energy Equivalence: Deep Exposition Draft](mee_deep_exposition.md)
- [MEE Fine-Grained Graph Experiment](mee_fine_grained_graph.md)
- [Electromagnetic Field: Deep Exposition Draft](em_field_deep_exposition.md)
- [Electromagnetic Field Fine-Grained Graph Experiment](em_field_fine_grained_graph.md)
- [Fine-Grained Block Graph Analysis](fine_grained_graph_analysis.md)
- [Simplified Content Block Strategy](simplified_content_block_strategy.md)
