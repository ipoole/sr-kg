# Maths reading-tree authoring audit

11 November 2026 · stage 4 on `nested-explanations`.
Runtime CSV is authoritative. The paper prototypes remain design experiments.

## MATHS-1 — Manifolds and Coordinates

All 44 concept blocks and five module blocks now have short authored statements.
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

Existing questions, options, graphics, memberships and layouts are untouched.
Old borrowed occurrences no longer exist, but their source block IDs/read ticks
and canonical notes remain; local note slots are retained.

## MATHS-2 — Tensor Calculus

Pending in this pass.

## Sources and verification

Definitions, tangent equivalence, duality and tensor constructions are checked
against David Tong's official
[Introducing Differential Geometry](https://www.davidtong.org/teaching/general-relativity/grhtml/S2),
§§2.1–2.3. Existing registered concept references remain. The board narrative,
numerical calculations and teaching wording are PhysicsKG's own.

The domain tests now check three-level content, absence of owned-block calls,
retained clarification identities and an acyclic Foundation graph. The real-data
browser tests use the generated routes rather than the superseded borrowed-block
syntax; they check graph-edge parity, equations/pane bounds on phone and desktop,
canonical reading progress and saved-note placement.
