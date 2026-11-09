# Graph-aligned reading: paper prototype

9 November 2026 · standalone prototype 4.6.9.

Open [the HTML](graph_aligned_reading_mockup.html), or the hosted review page:
https://physicskg.org/preview/graph-aligned-reading.html

This is a teaching/interaction experiment for the
[revised design](../../../docs/design/nested_explanations_design.md), not a viewer
or schema implementation. It does not read or write personal data.

## What to review

The root is MATHS-2.3 Tensor transformation law. Derivation follows outgoing
DERIVES_FROM/CONSTRUCTED_FROM edges; Explanation follows the Foundations family,
including REQUIRES. The example currently has construction and prerequisite
edges, with no DERIVES_FROM edges. It does not propose new graph edges.

The transitive Derivation map has four concepts and three edges: the root,
Coordinate transformation, Coordinate chart and Manifold. Explanation has eight
concepts and ten edges, adding Index notation, Tensor field, Cotangent space and
Tangent space. Worldline is an ordinary reference, not a Foundations branch.

Embedded edge records are taken from the current Maths CSV. Teal connecting
sentences propose revised edge justifications, stored separately by edge triple.
The original notes remain available in map-edge tooltips. Definition/contribution
statements are blue. These prototype texts are separately authored proposals;
they have not replaced the live blocks or notes.

The two expositions are separately authored. The succinct Derivation assumes
vector/covector familiarity and reaches the Jacobian construction. Explanation
also develops notation and tensor objects through their actual prerequisite
paths. All supports shown in this example are joint supports; alternative proof
styling remains for another exercise.

## Interactions and deliberate limits

- Profile and depth determine one available map/tree edge set. A branch's content
  is created on first opening. Repeated sources have independent open state.
- Opening a branch highlights its concept in amber. Root selection stays blue.
  Same-concept Definition/Example/Algebra inclusions do not add graph hops.
- At the map-depth boundary, an explicit action extends to the full tree. Profile
  and depth changes currently rebuild/reset the tree. This reset is a prototype
  simplification, not a proposed final preservation policy.
- Capped indentation stops adding padding beyond three levels. Borders/path text
  retain ancestry. Logical reading depth is not truncated.
- The full-width option exposes a focus button inside open branches. Nested focus
  and Return move the same DOM content, retaining the enclosing argument's open
  branches. The source controls and map remain available.
- An ordinary concept reference previews its Definition on hover, focus or tap;
  Escape/Close dismisses it without changing the map or reading attention.
- On phones the map starts folded to leave reading space. It can be opened.

Try the Explanation path through Index notation → Tensor field → Cotangent space
→ Tangent space, then the tangent block's local clarifications. This exceeds six
visual levels without changing the graph's shortest-distance hop calculation.
Compare the indentation cap with full-width focus and return.

## Checks

The focused browser exercise runs at 390 and 1280 pixels with real MathJax. It
checks exact map/tree edge coverage after expansion, both profiles, the depth
boundary, repeated sources, nested focus/return, reference previews without map
changes, keyboard disclosure, equation rendering and page width. Original graph
triples/notes are checked against the Maths CSV. The current viewer and earlier
paper prototypes are preserved by publication.
