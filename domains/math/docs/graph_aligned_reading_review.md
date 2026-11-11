# Generated reading trees: paper prototype

11 November 2026 · standalone prototype 4.6.11.

Open [the HTML](graph_aligned_reading_mockup.html), or:
https://physicskg.org/preview/graph-aligned-reading.html

This experiment supersedes the previous paper's authored per-profile exposition.
The design document has deliberately not been revised yet. The actual Maths
viewer, schema and domain data are unchanged; no personal data is read or saved.

## Model to review

Every embedded concept owns self-contained blocks with a kind, meaningful title,
short blue statement and body. Bodies can contain locally authored, nested
clarifications, but never include another owned block. Ordinary references still
preview Definitions without adding branches. These are paper texts, not a content
migration. Existing prose has been regrouped into blocks; it is no longer split
around recursive dependencies.

The renderer takes an ordered list of block kinds and an edge filter:

- **Derivation:** Derivation blocks; DERIVES_FROM + CONSTRUCTED_FROM edges.
- **Teaching:** Explanation, Intuition, Example blocks, in that order; the above
  edges plus REQUIRES.

Within a kind, authored block order is retained. Tensor transformation law has
two Example blocks; Tangent space has an Intuition block. Each concept's first
block of the first requested kind starts open. Remaining bodies start folded;
every statement remains visible even when its body is closed. If the preferred
kind is absent, the renderer says so and leaves other kinds folded. If no kinds
match, dependencies still appear. Definition is available separately, not silently
substituted for a missing Derivation or Explanation.

A concept's blocks are followed by all eligible graph edges. Each contributes its
teal justification and a folded concept branch with an informative block title
and a separate kind badge. Opening that branch renders the same block-selection
algorithm for the child. Each statement and its expandable title/body share one light block box. Stronger
rounded concept containers, labelled by code and name, group the blocks and
dependencies belonging to each concept and distinguish siblings. The extra concept
branch is the recursive fold; opening it exposes the preferred block immediately.
This is a prototype folding choice for review, not a change to the final design.

## Map and interactions

The root remains MATHS-2.3. Derivation reaches four concepts/three edges; Teaching
reaches eight concepts/ten edges. These are precisely the same existing Maths
edges as before. Teal text proposes clearer justifications; original notes are
retained in map tooltips. Neither graph data nor domain content has changed.

Depth uses shortest graph distance. Boundaries offer explicit extension. Shared
concepts can occur on several paths with independent open state; ancestor cycles
stop. Alternative proofs await a concrete example. Opening a branch updates amber
reading attention without changing the blue root selection.

Capped indentation and full-width branch focus remain available. Focus/Return
preserves the DOM and open states. Profile/depth changes deliberately reset the
tree. Definition references support hover, keyboard focus and tap. The map starts
folded on phones. No author chooses a reading route or inserts a dependency branch.

## Checks

Focused browser checks at phone and desktop widths cover graph parity, generated
branch coverage, preferred/secondary block folding, multiple blocks of one kind,
missing kinds, cycles, independent repeated occurrences, local clarification boxes,
focus/Return, keyboard use, MathJax rendering and horizontal page overflow.
Publication preserves all other hosted pages, including the current viewer.
