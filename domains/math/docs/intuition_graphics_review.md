# MATHS intuition and body-figure review

14 November 2026 · baseline `acc9bc7` · branch `graphics-within-blocks`.

## Inventory and decisions

The domain starts with nine concepts, 73 blocks, three Intuitions and nine
canonical concept graphics. The tangent/cotangent treatment and the shared
terrain narrative are already substantial. This pass adds missing mental models
and selective body figures, keeping existing arguments and annotation identities.

| Concept | Existing support and learner difficulty | Decision |
| --- | --- | --- |
| MATHS-1.1 Manifold | Terrain Example, smooth-atlas construction and an intrinsic/embedding distinction. Local dimension can be mistaken for a claim about one global flat map. | Add Intuition about local labels versus a global grid. Curvature alone does not forbid a single chart for a terrain site. |
| MATHS-1.2 Coordinate chart | Clear labels/inverse Explanation, board Example and inverse-function argument. | Retain the teaching structure; illustrate the Example with one shared ground peg in overlapping chart domains and two flat coordinate images. |
| MATHS-1.3 Coordinate transformation | Good chain-rule argument and explicit nonlinear-board transition qualification. | Retain; use the overlap figure via the existing chart support rather than duplicating the same mental model. |
| MATHS-1.4 Worldline | Surface-route versus spacetime-history clarification and existing spacetime graphic. | Add Intuition about a stationary probe's continuing history, distinguishing route, clock parametrisation and spacetime dimension. |
| MATHS-1.5 Tangent space | Directional-derivative Intuition, curve equivalence, units Example and tangent-plane graphic. | Retain the Intuition and strengthen its first-order interpretation with an optional concrete pair of curves. Do not equate a tangent space with a finite flat patch. |
| MATHS-1.6 Cotangent space | Two useful Intuitions plus temperature, contour, units and dual-basis calculations. | Enrich the linear-readout Intuition with a contour diagram. Keep the units Intuition and worked examples. Distinguish a differential from a metric-dependent gradient vector. |
| MATHS-2.1 Tensor field | Slots, multilinear construction and metric Example already supply the formal and computational argument. | Add Intuition about a local multi-input measuring rule; separate tensor type from dependence on position. |
| MATHS-2.2 Index notation | Practical contraction sums and free/dummy rules; abstract notation is optional. | Add Intuition about a family of component equations versus a completed scalar readout. Match it to existing sums rather than another matrix-icon drawing. |
| MATHS-2.3 Tensor transformation law | One-index proof, multi-index derivation and numerical rescaling Example. | Add Intuition about compensating descriptions; illustrate the existing rescaling Example with the same arrow and unchanged scalar pairing on two grids. |

## Artwork and scope

Three priority body figures: overlapping chart records; a temperature differential
reading two tangent velocities; reciprocal changes preserving a vector/covector
pairing. The first and third belong to **Examples**; the contour figure belongs
to the existing cotangent **Intuition**. Each gets a recognition thumbnail from
the same SVG. Existing canonical graphics/icons are retained.

The survey uses an actual two-dimensional curved surface. A board is rigid with
a straight grid and tangent at its reference point only; ground-to-board projection
must be locally invertible. Coordinate images drawn flat are spaces of labels,
not flattened pieces of terrain. Coordinates supply neither metric lengths nor
curvature. Curvature alone does not force multiple charts on every possible site.

Contour lines depict the first-order scalar readout in a coordinate picture.
Their drawn angles do not define intrinsic orthogonality, and no metric is needed
to evaluate dT(v). The component-rescaling picture keeps the physical arrow and
curve parameter fixed; the changed numbers compensate for the changed basis.

## Process and source checks

Read the authoring guide before each module, use expansivity 70, keep statements
short and give each body a genuine teaching contribution. Preserve block IDs,
clarification paths, questions/options, module membership, edges and overviews.
Review native sequence and generated Teaching trees. Figures and helpers remain
inside `domains/math/`, without depending on SR/GR artwork or viewer changes.

Primary mathematical source: [Tong, Introducing Differential Geometry](https://www.damtp.cam.ac.uk/user/tong/gr/grhtml/S2.html),
§2.1.2 (charts/atlases), §2.2.1 (curve tangents), §2.3.1 (duality) and §2.3.3
(multilinear tensors and components). Existing references to Guillemin–Haine
remain. Terrain examples, coordinate choices and diagrams are original teaching
illustrations, not source quotations.

Commit each module independently. Inspect artwork and equations at phone/desktop
widths, validate and rebuild the ignored viewer, run the relevant tests and publish
a versioned MATHS preview for review before starting SR authoring.

## Progress

Inventory complete. MATHS-1 adds two Intuitions (local/global labels and stationary
histories), extends the existing directional-derivative Intuition with a concrete
curve comparison, and enriches the covector readout with a nonzero differential
and critical-point qualification. The two body figures sit in the chart Example
and cotangent Intuition. Domain registration is independent of GR/SR assets.

All 784 unit tests pass. Both real-data maths phone/desktop equation/reading-tree
cases pass. The annotation regression's former “one image anywhere” assertion is
updated to check one **canonical** graphic, allowing the intended body figure.
Legacy graphic notes, scalar-calculation notes and shared read ticks are retained.
Full/folded SVGs inspected at both widths. Validation remains zero errors and the
existing 216 full-viewer warnings.

MATHS-2 adds three Intuitions: tensors as local multi-input rules, free versus
contracted index questions, and compensating descriptions. The rescaling Example
now illustrates an unchanged tangent arrow, a halved basis unit and reciprocal
covector components preserving the scalar pairing. Its title says “Double the
labels” rather than implying that a physical grid or vector was stretched.
Two small pre-existing grammatical errors in the slots/index exposition are fixed.

The domain now has 78 blocks, eight Intuitions and three body figures (two in
Examples, one in Intuition). All 73 prior IDs/kinds and all named clarification
paths are retained. Edges, questions/options, module overviews and membership are
byte-for-byte unchanged from the baseline. A Maths-only load contains exactly the
three Maths figure assets and retains only the existing missing-SR diagnostics.

All 784 unit tests and four real-Maths phone/desktop reading/annotation cases pass.
Full and folded artwork inspected at both widths. Full-viewer validation still
reports zero errors and 216 existing warnings. Complete-suite preview verification
follows; SR remains an inventory only, pending review of this MATHS batch.
