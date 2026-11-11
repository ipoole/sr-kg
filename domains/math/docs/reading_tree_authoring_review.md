# Maths reading-tree authoring audit

11 November 2026 · stage 4 on `nested-explanations`.
Runtime CSV is authoritative. The paper prototypes remain design experiments.

## MATHS-1 — Manifolds and Coordinates

All 49 concept blocks and five module blocks now have short authored statements.
Existing block IDs and named local clarification slots are retained. The canonical
Definition is the first Definition on each concept; cotangent Definition now
precedes its temperature argument locally as well as in the generated recipes.

Every concept supplies Definition, Derivation and Explanation. Three new
Derivations cover specifying a smooth structure, constructing a local surface
chart and representing a history as a curve. They identify starting structures
and assumptions instead of pretending to prove definitions. Existing curve-tangent,
Jacobian and dual-basis arguments supply the other derivations.

The terrain example is self-contained where used: two-dimensional ground,
invertible local board projection, scalar temperature, motion/growth and linear
readouts. A surface route is distinguished from a spacetime history. Coordinates
do not supply distance, orthogonality or curvature. Cotangent examples distinguish
coordinate independence from units, exact instantaneous rates from finite-change
approximations, and duality from metric-dependent index raising.

Owned-block calls have been removed. Useful support is now offered by generated
concept branches; optional local algebra retains its named slots. Worked examples
are classified as Example so the Teaching recipe can include them. Ordinary
concept links provide excursions/definition previews without adding tree branches.

### Edge review

- Tangent construction explicitly uses the coordinate-transition Jacobian to make
  curve equivalence and vector-space operations chart-independent. Add that
  CONSTRUCTED_FROM support. Remove the older direct tangent-to-manifold edge,
  which is now supplied transitively through transition → chart → manifold.
- Worldline's coordinate-plot explanation needs charts: add REQUIRES. Its
  CONSTRUCTED_FROM manifold edge remains the intrinsic curve construction.
- Clarify existing construction notes so each explains the source's actual use
  of the destination. No reverse manifold-to-chart edge: charts specify the
  manifold's starting structure, rather than a theorem depending on a separately
  derived manifold concept.

The existing illustrations now use ordinary folded Graphic blocks too, rather
than leaving an automatically open legacy figure above the block list. Their
SVGs and captions are unchanged; legacy graphic-note anchors still resolve.
Existing questions, options, graphics, memberships and layouts are untouched.
Old borrowed occurrences no longer exist, but their source block IDs/read ticks
and canonical notes remain; local note slots are retained.

## MATHS-2 — Tensor Calculus

All 24 concept blocks and the module overview now have short statements. The
existing worked calculations are classified as Example so the Teaching recipe
offers them. There are no owned-block calls, including calls between blocks of
the same concept. Meaningful Definition titles replace generic headings.

Two new Derivations construct tensor products from vector/covector pairings and
obtain the contraction sum from a dual-basis expansion. They distinguish a
construction or notation convention from a physical field equation. The existing
higher-order transformation block now explains how multilinearity turns each
basis change into one index factor. It defines its own Jacobians instead of
depending on material “above”.

The Teaching material retains type/order versus matrix rank, abstract versus
component indices, free/dummy labels, bilinearity, pointwise fields, metric
pairings, rescaling and invariant scalar readouts. Formal and teaching expositions
remain different views of the same concepts and graph, rather than duplicate
routes authored inside the prose.

Existing tensor-field → tangent/cotangent supports describe the respective input
and factor roles. Transformation law → tensor field is strengthened from
REQUIRES to CONSTRUCTED_FROM: multilinearity supplies the actual construction of
the component rule. The transition Jacobian is its other direct construction
input; index notation remains a prerequisite. These independent inputs are
retained even where a transitive route also reaches the same concept.

All twelve MATHS-2 questions and options are unchanged. Their previous
[coverage review](tensor_calculus_teaching_review.md) still applies; its
borrowed-block implementation description is historical.

## Sources and verification

Definitions, tangent equivalence, duality and tensor constructions are checked
against David Tong's official
[Introducing Differential Geometry](https://www.davidtong.org/teaching/general-relativity/grhtml/S2),
§§2.1–2.3. Existing registered concept references remain. The board narrative,
numerical calculations and teaching wording are PhysicsKG's own.
The official MIT draft of Guillemin and Haine's
[Differential Forms](https://math.mit.edu/classes/18.952/2018SP/files/18.952_book.pdf)
also supports the chart's inverse-function argument (Theorem 4.2.13, p. 107)
and covariant tensor products/dual-basis expansions (§1.3, pp. 8–10).
These precise block references are registered in the Maths bibliography.

The domain tests now check three-level content, absence of owned-block calls,
retained clarification identities and an acyclic Foundation graph. The real-data
browser tests use the generated routes rather than the superseded borrowed-block
syntax; they check graph-edge parity, equations/pane bounds on phone and desktop,
canonical reading progress and saved-note placement.
