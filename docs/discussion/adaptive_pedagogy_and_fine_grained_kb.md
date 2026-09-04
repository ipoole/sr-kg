# Adaptive Pedagogy and a Fine-Grained Knowledge Base

Captured on 2026-07-26.

## Status: deferred exploration

This note explores possible future pedagogy. The current system uses flat,
ordered semantic blocks and viewer-defined presentation, as described in
[Architecture](../design/architecture.md). The earlier pedagogical-level pilot
and block-graph worksheets are no longer the implementation direction.

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

## Possible experiment

If dependency-driven presentation becomes a priority, start with one concept
and test which views genuinely help learning before extending the KB schema.
The earlier mass-energy and electromagnetic-field experiments produced acyclic
ordering graphs, but dependency order differed from natural exposition order.
Algebra support also proved ambiguous: some steps belong on the main derivation
path, while others are optional explanation. A future experiment should resolve
that distinction and retain editorial control over narrative order.

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

## Future plans

Keep this deferred until a concrete learning need justifies the extra authoring
burden. Any renewed experiment should use actual exposition, retain concept-owned
blocks, and evaluate the result before proposing a production schema change.
