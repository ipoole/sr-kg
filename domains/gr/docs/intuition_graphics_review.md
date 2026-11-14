# GR intuition and body-figure pass

14 November 2026. This follows the GR teaching revision and the body-figure
demonstration in GR-2.3. It adds qualitative ways into difficult ideas, rather
than another proof or a second copy of each concept's Explanation.

## Editorial inventory

At the start there were 56 concepts, four Intuition blocks (including the GR-2.3
demo), and many useful Examples. The following 23 targets are a selective working list,
not a requirement to add 23 blocks. Existing intuitions are marked **review**;
the others are candidates for new blocks or improvements to existing material.
Keep examples that teach a calculation as Examples. Concepts absent from this
list retain their existing treatment unless the module review finds a gap.

| Concept | Learner's difficulty and intended insight | Existing coverage / action |
| --- | --- | --- |
| GR-1.1 Equivalence principle | Weight is a support-force measurement, rather than a test for curvature. | Falling-capsule explanation already works; add a complementary comparison of supported and falling laboratories. |
| GR-1.4 Tidal gravity | How weightlessness can coexist with stretching and squeezing. | Keep the point-mass calculation; add a released particle constellation and body figure. |
| GR-1.5 Gravity as geometry | What the rubber sheet leaves out. | **Review** the existing Intuition: replace a list of objections with a positive mental model of clocks and free paths. |
| GR-1.13 Local flatness | How an exact pointwise result becomes an approximate laboratory. | Keep the normal-coordinate proof and scale example; add a shrinking-laboratory mental experiment. |
| GR-2.3 Covariant derivative | Changing components need not mean a changing arrow. | **Review/retain** the constant-arrow demo and its optional polar cancellation; do not duplicate it under Connection. |
| GR-2.6 Parallel transport | How locally unchanged arrows can disagree after a loop. | **Review** the existing spherical-triangle Intuition; add a labelled, quantitatively correct figure and optional check. |
| GR-2.7 Geodesic | An apparently curved orbit can be unforced motion. | Add a coasting/supported comparison; keep the affine definition and stationary-proper-time qualification. |
| GR-2.12 Geodesic deviation | Why comparing two unforced paths detects something one accelerometer misses. | Add a two-capsule experiment with controlled initial relative velocity; refer to the tidal picture without repeating it. |
| GR-3.1 Riemann tensor | What the curvature components compare. | Explain an infinitesimal loop experiment, distinguishing tensor information from the finite spherical example. |
| GR-3.2 Ricci tensor | What contraction retains and discards. | Use geodesic-bundle focusing versus shear; priority figure. Avoid implying that vacuum has no tides. |
| GR-3.3 Ricci scalar | Why one number cannot describe all curvature. | An overall contraction loses directional information; keep the existing worked contraction as an Example. |
| GR-3.5 Bianchi identity | Why curvature components cannot vary independently. | Give a qualitative consistency interpretation without presenting a closure picture as a proof. |
| GR-4.1 Stress-energy | Why energy density is not the whole source. | Measurements across faces of a local box introduce energy flow, momentum flow and stress. |
| GR-4.2 Perfect fluid | How pressure is momentum flux even in the fluid rest frame. | Priority figure of opposite-face momentum exchange; distinguish zero net momentum from nonzero flux. |
| GR-4.4 Covariant conservation | Local balance without a universal global energy total. | A small freely falling laboratory and neighbouring comparisons; state when symmetry supplies a global charge. |
| GR-4.6 Field equations | How source and geometry constrain each other. | An equation for the measuring structure, not a pointwise recipe determining all curvature from local density. |
| GR-5.3 Redshift | What two clocks actually compare. | Priority pulse-exchange figure with a specified stationary setup and observer rates. |
| GR-5.4 Light deflection | Why a locally straight ray has a bent overall route. | Accumulation along the path; do not identify a coordinate ray slope with a locally measured angle. |
| GR-5.5 Perihelion precession | What advances between successive closest approaches. | Compare radial and angular repetition rather than suggesting an orbit continually loses energy. |
| GR-5.7 Gravitational waves | A wave is a changing tidal pattern, not bulk motion of a drawing. | **Review** the existing two-polarisation Intuition and its canonical graphic before adding artwork. |
| GR-6.3 Event horizon | A causal boundary rather than a material surface. | Priority light-cone figure in explicitly identified regular coordinates; distinguish local detection from global definition. |
| GR-6.4 Coordinate singularity | A chart can fail where an observer does not. | Distinguish coordinate breakdown from invariant pathology; avoid treating every divergent expression as harmless. |
| GR-6.6 Effective potentials | How a radial plot encodes permitted motion and stability. | Read turning points and minima with fixed constants of motion; label the plot's assumptions. |

The six priority *new* figures are tides, spherical transport, bundle focusing,
fluid momentum flux, clock signals and the horizon. The constant-vector figure
is already implemented. Prefer one image per useful mental model; folded
thumbnails identify the topic, while the full image and body explain it.

## Pilot decisions: GR-1 and GR-2

- Add three GR-1 Intuitions and revise its existing rubber-sheet block.
  Add two GR-2 Intuitions, revise spherical transport, and retain the vector demo.
- Place the new units after the opening Explanation, before formal definitions.
  Preserve existing IDs, sequence values, clarification slots and question records.
- Keep all existing canonical Graphic blocks, icons and captions. New body
  figures are domain-owned assets registered in `data/figures.csv`.
- Tidal arrows denote **relative acceleration in a freely falling frame**, not
  the common inward fall. Initial relative velocities are zero. The drawing is
  a weak-field, short-time point-mass illustration with exaggerated deformation.
- The transport triangle has two quarter-meridians and one quarter-equator.
  Its three right angles enclose one eighth of a sphere. Keep incoming/outgoing
  tangent vectors distinct at the corners: changing route is not resetting the arrow.
- Local surface analogies illustrate comparison rules; they do not replace
  Lorentzian spacetime or imply an extra embedding dimension is required.
- No new graph edges or recipe changes are required. Definitions, examples and
  existing dependencies already support these mental models. Any later gap must
  be justified independently, not introduced merely to put a picture in a tree.

## Sources and checking

Primary teaching reference: [Tong, GR](https://www.damtp.cam.ac.uk/user/tong/gr/grhtml/),
§1.2.4 (equivalence), §3.3.1–3.3.4 (geodesics, normal coordinates, transport and
deviation). Retain the atlas's +--- convention. The Newtonian tidal comparison
uses the existing potential Hessian and point-mass Example, rather than borrowing
an unconverted Riemann sign from a source. The sphere uses a positive-definite
surface metric, explicitly distinguished from spacetime.

For each module: review native sequential reading and Teaching-tree copies,
render equations and figures at phone/desktop widths, verify statements and
figure slots, run unit tests, validate and rebuild the ignored viewer. Complete
the browser suite before publishing the pilot preview. Questions, dependency
edges and all established annotation identities should remain unchanged.

## Progress

Inventory complete. GR-1 adds the floor/ball, particle-constellation and
shrinking-laboratory Intuitions; its existing rubber-sheet block now offers a
positive clock-and-path mental model. The tidal SVG and folded preview have
been inspected at phone and desktop widths. All 784 unit tests and the two
GR-1 full-content browser cases pass; validation retains zero errors.

GR-2 adds the coasting-orbit and two-capsule Intuitions. Its existing spherical
transport block now follows a specific arrow through all three legs, with an
optional quarter-turn check. The new figure projects the actual great-circle
route and transported tangents; an unskewed tangent-plane inset shows the 90°
return angle. The constant-arrow demo is retained, with a small terminology fix.
The two GR-2 phone/desktop cases and all 784 unit tests pass; validation still
reports zero errors and the existing 216 warnings.

The pilot adds five blocks, revises two existing Intuitions, and adds two body
figures. GR now has nine Intuition blocks, eight in GR-1/GR-2 and the existing
wave Intuition in GR-5. No edges, questions, canonical graphics or module
overviews changed. The module overviews remain consistent with these additions.
Source IDs and named clarification paths are retained. Rebuild the new SVGs with
`conda run -n sr-kg python -m domains.gr.graphics.body_figures`.

Final pilot checks: all 784 unit tests, 351 fast browser cases and 94 full-content
browser cases pass. After making the inset's two arrows equal in drawn length,
the final unit suite and GR-2 phone/desktop checks pass again. The ignored viewer
was rebuilt for pilot preview v4.6.21. The subsequent module pass is recorded below.

## Extension: GR-3

Two new Intuitions explain local loop experiments and shape versus volume.
The Ricci-scalar and Bianchi candidates are consolidated into their existing
Explanations: both already had effective qualitative arguments, so another
folded unit would repeat them. Their bodies now emphasise the concrete zero-R
counterexample and the difference between an identity and a physical field law.
The trace/tidal-map figure sits in the Ricci **Explanation**, not its Intuition.
It shows all three spatial coefficients and labels these as instantaneous maps,
avoiding a false claim that zero Ricci preserves volume for all time.

Validation: zero errors, 216 existing warnings; 784 unit tests and both GR-3
phone/desktop content cases pass. Full and folded artwork inspected at both widths.

## Extension: GR-4

Four new Intuitions compare equal densities with different flows, microscopic
motion with fluid rest, local balance with global energy, and joint matter/metric
solutions. The new opposing-stream figure belongs to the stress-energy
**Explanation**. Both streams contribute positive diagonal momentum flux even
though their momentum densities cancel; the drawing is explicitly one-axis,
not a claim that two beams alone constitute an isotropic perfect fluid.

Validation remains at zero errors/216 warnings. All 784 unit tests and the GR-4
phone/desktop cases pass; the figure has been inspected at both sizes.

## Extension: GR-5

Three new Intuitions explain pulse counting, local/geodesic light propagation
versus distant bending, and the mismatch of radial/angular orbital cycles.
The existing wave Intuition now distinguishes freely falling masses from a rigid
hoop and coordinate motion from measured strain; its canonical graphic remains
suitable. The clock-signal figure belongs to a worked **Example**, retaining the
old block ID while adding a 100 m, approximately −1.1×10⁻¹⁴ frequency-shift
calculation. The figure explicitly exaggerates clock rates, preserves equal
static-coordinate pulse intervals and is not a local light-speed diagram.

Validation: zero errors/216 warnings; 784 unit tests and the GR-5 phone/desktop
cases pass. Source locators checked against Tong's current chapter headings.

## Extension: GR-6

Three new Intuitions explain the future horizon's causal restriction, chart
failure versus a continuing infaller, and radial motion at fixed angular momentum.
The horizon figure uses regular time T=v−r, with radial null slopes −1 and
(r−2m)/(r+2m), so its cone directions are calculated rather than guessed.
The body explicitly limits the picture to the Schwarzschild future horizon:
it is not a universal local event-horizon detector. Its optional calculation
extends the concept's existing ingoing-coordinate derivation, retaining that
source's clarification and the established graph structure.

All 784 unit tests and the GR-6 phone/desktop cases pass. Artwork inspected at
both widths; final label adjustments keep the bottom caption inside the SVG.

## Cross-module review

| Module | Intuition blocks after review | Registered body figures |
| --- | ---: | ---: |
| GR-1 | 4 | 1 |
| GR-2 | 4 | 2 |
| GR-3 | 2 | 1 |
| GR-4 | 4 | 1 |
| GR-5 | 4 | 1 |
| GR-6 | 3 | 1 |

GR now has 400 blocks, including 21 Intuitions, and seven body figures (the vector
demo plus six additions). Across the pass, 17 Intuition blocks were added; the
rubber-sheet, spherical-transport and wave Intuitions were improved in place.
The two unneeded extra Intuitions in GR-3 were consolidated into existing
Explanations. No new block kinds or reading-tree recipes were introduced.

The figures sit in four Intuitions, two Explanations and one Example. The latter
placements let diagrams support interpretation or calculation directly, without
reclassifying content merely to provide artwork. Canonical graphics/icons remain
unchanged. The six module overviews still describe the scope correctly.

Review checks: each new block states its physical setup and the limits of its
analogy; bodies add a mental experiment rather than merely restating statements.
Expansivity remains near 70. Clarifications carry optional algebra rather than
necessary hidden premises. Native order leads from opening explanation to the
new intuition and then formal treatment; Teaching-tree copies remain standalone
when recipes group kinds differently. Cross-references identify the particular
calculation or qualification; none manufacture a new graph dependency.

Edges, questions/options and module overviews are byte-for-byte unchanged from
the pilot baseline. Existing block IDs and named clarification slots remain
available; the domain baseline regression checks their retention. New body
figures reuse their SVG for the folded recognition preview, with stable slots,
descriptive alternatives and independent SVG identifiers at each occurrence.

The reading-layout cleanup gives personal and built-in clarification titles
matching full-size bold text, while bodies share the same normal typography and
line spacing. Authored blank lines supply paragraph spacing; the structural line
ending after a figure is retained invisibly for positional note compatibility.
Footer read controls follow Fold and align with heading controls even at maximum
details text zoom. Focused browser checks exercise both read controls, paragraph
spacing, shared note typography and retained figure/paragraph note anchors.

## Completion checks

Preview v4.6.22: 784 unit tests, 351 fast browser cases and 94 full-content browser
cases pass, including all GR concepts at both widths, generated reading routes,
personal notes, touch interaction and the three guided tutorials. Validation
reports zero errors and the existing 216 editorial warnings. Every new figure
has been visually inspected as full artwork and in folded/open phone and desktop
blocks. The horizon slopes also satisfy the regular radial metric by direct
substitution; the 100 m example gives −1.09×10⁻¹⁴ before rounding.

Generated output remains ignored. Publication uses the exact local build and
retains the public release while updating only the hosted preview.
