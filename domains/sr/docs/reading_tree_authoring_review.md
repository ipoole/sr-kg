# SR reading-tree authoring review

## SR-1 — Spacetime and Lorentz Symmetry

12 November 2026. Completed against the [frozen stage-1 inventory](reading_tree_authoring_audit.md).
All five SR modules are now completed in the follow-ups below.
Reading-tree recipe changes (finding 1) are deferred.

### Content

Reviewed all 111 existing blocks across 13 concepts: meaningful titles, concise
statements and independently readable bodies. Reworked all 30 Explanation and
eight Derivation bodies, including intermediate combination arguments, local
notation and assumptions. Definitions and postulates remain honest starting
points rather than acquiring artificial proofs. Original semantic kinds remain.

Added 13 explicit Graphic blocks around the existing artwork and captions, plus
one Derivation explaining covariance through matching transformation laws. There
are now 125 SR-1 concept blocks. The module overview also has a statement and a
revised account of the route through its concepts.

Distinguished physical postulates from coordinate/calibration conventions;
observer invariance from conservation; local differential dependence from
finite causal propagation; simultaneous endpoint measurements from photographs;
and mathematical covariance from experimental validity of a physical law.
The locality caption now makes the same distinction as the text.

### Dependency route

The chosen formal route is:

**Inertial postulates → Lorentz boosts → Minkowski metric → interval.**

The boost argument uses linearity from homogeneity, invariant forward/backward
light speeds, reciprocal commonly calibrated frames, spatial isotropy and the
continuous identity branch. A named local clarification supplies the transverse
scale argument. The metric argument then derives the invariant quadratic form
from spatial isotropy and boost invariance, fixing its overall normalisation by
convention. Neither argument assumes the interval as a hidden premise.

SR-owned edge changes:

- Lorentz transformations → Interval becomes Related: an equivalent geometric
  characterisation and a check, rather than a premise of this derivation.
- Metric → Lorentz transformations gains Derives from.
- Minkowski diagram → Lorentz transformations becomes Derives from: the primed
  axes are actually constructed using the boost equations.
- Time dilation → Interval gains Derives from for its explicitly labelled
  alternative proof. The direct boost route is retained as an independent
  argument, not an additional joint prerequisite.

Revised edge justifications state how each input is used. Foundation routes and
the module quotient remain acyclic. SR's internal Foundation edge count becomes
64; its 28 boundary edges and module memberships are unchanged.

The metric's display number precedes Lorentz transformations. Validation now
flags this within-module order contradiction; renumbering and layout changes
are deliberately outside this authoring pass. The intentional alternative
clock-rate proofs also produce a transitive-redundancy warning. Generated trees
still present both as supports; alternative-route UI remains future work.

### Sources and preservation

Checked Einstein's 1905 paper §§1–4 and OpenStax University Physics III §5.5;
registered precise links for synchronisation, boost assumptions and interval
preservation. The modern coefficient arguments are authored explanations, not
quotations or claims that those sources use precisely this proof order.
Daskalopoulos's IAS diffusion lecture, PDF p. 9, supports the heat-equation
counterexample to equating local differential form with finite propagation.
See [source review notes](source_review_worklist.md).

Retained every original block ID, kind and local clarification path. Questions,
options, tutorial targets, concept IDs, membership, layout and SVG drawing code
are unchanged. Canonical IDs preserve block-level annotations and read ticks;
rewritten prose does not promise unchanged paragraph text anchors. The legacy
standalone graphic-note anchor is checked against its new explicit Graphic block.
Other modules' original block fields are unchanged.

### Follow-up — 13 November 2026

All 125 SR-1 block bodies, their local clarifications and the module overview
have received the agreed teaching-style pass at exposition level 70. Titles,
statements, kinds, identities, graph structure, questions and layout are retained.
Four ordinary cross-references now demonstrate block-specific previews: the
time-dilation and length-contraction boost arguments, Lorentz-transformation
consequences, and the interval-preservation check. These links leave reading-tree
branches unchanged. Selective demonstration links do not constitute a complete
block-reference audit.

At this point the authoring guide recorded the ten-kind consolidation, with
runtime/content migration still pending. Checks: 762 unit tests and all 396
browser cases passed, with focused reruns covering lazy preview-body rendering
and the long-preview viewport correction. Real SR-1 previews and equations were
also checked at phone and desktop widths. The SR+Maths viewer was regenerated
locally; nothing was published.

### SR-1 completion — 13 November 2026

All 125 blocks and the module overview now use the ten agreed authoring kinds.
Interpretative Overview/Summary and formula blocks become Explanation;
Misconception becomes Warning, and Worked example becomes Example. The explicit
interval-preservation proof and light-cone construction remain available as
Derivation blocks. The compact Lorentz matrix formalism is Advanced: optional
notation, not a concealed premise of the boost derivation. Recipes are unchanged.

Sequential reading now introduces the `ct` convention before using it, places
history after the main argument and leaves the matrix formalism after physical
consequences. Concept numbering and layout remain unchanged.

The block-reference review adds precise pointers to the boost formula, its
assumptions, interval construction, measurement conventions and Maths support.
These ordinary previews do not add reading-tree branches or shortcut graph edges.
The approved level-70 prose is retained apart from these pointers and one
scientific clarification: lowering an index associates a covector through the
metric; this is not a change of observer.

Every ID, title, statement and local clarification path is retained. All other
SR modules, questions, graph edges, graphics, layouts and tutorial targets are
unchanged. Shared support accepts Advanced alongside legacy kinds; SR-2–5 and
GR kind/content consolidation remain later work.

The final SR+Maths validation has zero errors and 62 warnings. Warnings remain
visible, including ordinary transitive source pointers, the intentional
alternative time-dilation proof and the known metric/boost display-order issue.

Final checks: 765 unit tests and 12 focused actual-content/browser checks pass.
The full browser run passed 395 cases; its two failures were assertions tied to
the old Maths module overview title. Both pass after checking the note button's
accessible label against the current block title instead. Thus all 397 cases
have passed, without changing note behaviour to satisfy obsolete wording.

### Verification

- Unit suite: 760 passed (browser cases skipped in this lane).
- Focused actual SR-1 browser checks: phone/desktop native blocks and equations,
  both generated tree routes, canonical read ticks and legacy graphic notes.
- SR+Maths source validation: zero errors. Warnings include excursions without
  direct edges, existing transitive relationships, the deliberate alternative
  proof and the ordering issue described above; no blanket warning suppression.
- Full browser suite: 390 of 392 cases passed initially. Both time-dilation
  walkthroughs exposed the legacy-only graphic selector; after updating the
  graphic action and pointer to support authored Graphic blocks, both passed
  on rerun. All 392 cases have therefore passed, with that targeted correction.
- Complete-KB validation also reports zero errors (187 warnings); the SR+Maths
  validation reports 61 warnings. These diagnostics are not treated as a clean
  warning-free audit of the other modules or domains.

The locally regenerated `output/PhysicsKG.html` includes SR and Maths. It remains
an ignored, unpublished build; the product version and live preview are unchanged.

## SR-2 — Relativistic Particle Mechanics

13 November 2026 · `major-content-revision-maths-sr`.

Reviewed all 65 original blocks, their titles and bodies, and added explicit
statements. Use the agreed ten kinds and teaching prose at level 70. Retain all
original block IDs and exact local clarification paths, including the anonymous
algebra disclosures used by existing notes. The six existing graphics now have
canonical Graphic blocks without changing drawings or captions. Add one momentum
Derivation and one rest-energy Intuition: 73 concept blocks in total. The module
overview has an informative title, statement and a revised account of the route.

### The combination arguments

- **Proper time:** combine the infinitesimal interval with a specified timelike
  path. Derive the local rate, integrate changing speeds and distinguish an
  ideal clock's elapsed reading from distant optical observations. Constant-speed
  integration is a special case, not a restriction to inertial worldlines.
- **Four-vectors:** define by transformation, use displacement to explain origin
  cancellation, and derive invariant products from metric preservation. Lowering
  associates a covector, not another observer's vector components.
- **Position:** make the shared-origin condition explicit. Event coordinates
  transform affinely when origins differ, while differences transform linearly.
  An invariant contraction is distinguished from a frame-dependent displacement.
- **Four-velocity:** combine position differentiation, the timelike worldline
  and the proper-time rate. The norm calculation explains why ordinary speed
  can change while the Minkowski norm remains fixed.
- **Four-momentum:** retain the fixed-mass work calculation and Newtonian check.
  Explain that work determines differences, while conserved physical
  four-momentum is additional dynamical input. Derive the boost of energy and
  radiation-pulse sums in a new `energy_transformation` block, so the input used
  by the rest-energy argument is available on the actual prerequisite branch.

### Mass–energy equivalence

Keep the compact physical-four-momentum derivation distinct from the two-frame
light-emission argument. The first combines conserved energy–momentum, the
invariant norm and zero total spatial momentum to obtain positive rest energy.
The second states the light-energy transformation, applies energy conservation
in both frames, subtracts to isolate kinetic energy and identifies the
low-speed inertia coefficient. It establishes a mass/energy **change**, not
an absolute energy zero by itself. Its Derivation is self-contained even when
the Intuition blocks are omitted by a reading recipe.

`light_emission` remains an Intuition, now with clearer reasoning about the
unchanged speed and reduced kinetic energy. The new `trapped_light` Intuition
explains how cancelling momenta and adding energies give a system nonzero mass
even when individual photons are massless. It is explicitly an interpretation,
not another proof. The heated box poses the question before referring to the
inertia argument; its later calculation is an application, not circular evidence.
Keep system boundaries, positive/negative changes, binding energy, rest versus
bulk kinetic energy and invariance versus conservation explicit throughout.

### Graph, sources and preservation

Add **Four-vectors REQUIRES Metric tensor**, because the concept's core scalar
products and index-lowering treatment actually use it. The defining Lorentz rule
remains a direct prerequisite. This adds one SR module-boundary edge (29 rather
than 28), preserves the module DAG and all original edges, and deliberately
exposes additional transitive-redundancy diagnostics. Revise twelve existing
prerequisite notes to state the particular input used. No shortcut dependencies
are added for preview convenience; ordinary block references to transitive
supports and the optional Maths dual-space excursion remain distinct from edges.

Verify source locators against Einstein's two 1905 papers and the OpenStax
momentum/energy sections; see the [source worklist](source_review_worklist.md).
Existing questions, options, artwork, membership, numbering, layouts and
tutorial actions/targets are unchanged. No other concept or module block is
modified. Existing standalone figure notes remain supported by canonical graphic
identity. Paragraph-text anchors can become unmatched after prose revision;
canonical block/clarification scope is preserved, not every old paragraph string.

SR+Maths validation reports zero errors and 65 warnings; full-KB validation
reports zero errors and 191 warnings. Review warnings rather than suppressing
them. The known metric/boost display order remains outside this authoring scope.

### Verification

- 768 unit tests pass, including identity/scope, consolidated-kind and acyclic
  support checks for SR-2.
- Both phone and desktop checks open all six concepts' blocks and equations,
  traverse both rest-energy recipes against the actual context edges, and
  verify a borrowed block's read tick at its canonical owner.
- The 399-case full browser suite initially passed 397 cases. Its equation
  check caught a too-wide labelled energy display: labels were moved to prose,
  and that check plus the strengthened SR-2 equation checks pass on rerun.
  The other failure exposed an existing module-font test's inherited concept
  selection; it now uses the existing clean-view fixture and passes on rerun.
  All cases have therefore passed after these focused corrections.
- The SR+Maths viewer is regenerated locally. Product version and hosted release
  are unchanged.

## SR-3 — Action and Field Theory

13 November 2026 · authoring guide reread before this module. All 87 existing
blocks reviewed at exposition level 70: informative titles, explicit statements,
consolidated kinds, and bodies explaining how the inputs combine. Nine canonical
Graphic blocks reuse existing drawings and captions. Original block IDs remain;
there were no existing local clarification slots to migrate. Questions, options,
layouts, membership and tutorial targets are unchanged.

The particle derivation now includes first variation, integration by parts and
the arbitrary-interior-variation argument as separate self-contained Derivation
blocks. Fixed endpoint assumptions and independent variations are explicit.
Canonical momentum is explained through its endpoint coefficient, distinguishing
it from mechanical and four-momentum. The Legendre differential includes the
explicit time term; Hamilton's equations need both the momentum construction
and Euler–Lagrange dynamics. The latter Related edge is promoted to Derives from.

Scalar and vector field bodies distinguish changes of argument from component
transformation, use V for generic vectors, and qualify temperature-map analogies.
The scalar gradient rule is actually derived. The field-action measure and units
are stated, with explicit natural-unit example conventions. The field-equation
variation includes the product rule, boundary contribution and pointwise
arbitrary-variation conclusion. A scalar prototype supplies a genuine additional
Requires edge from Field Lagrangian to Scalar field. No field is derived from its
own future equations. The module quotient remains a DAG; SR now has 66 internal
Foundation edges and 29 module-boundary edges.

Checked the MIT Press author textbook SICM, chapter 1, and Tong's classical
field-theory chapter in the Durham-hosted primary lecture text. Cambridge's
copies could not be fetched, so the bibliography points to the checked copy.
Reference locators distinguish our modern staged exposition from quotations.

Verification: 770 unit tests and both real-content phone/desktop checks pass.
SR+Maths generation has zero validation errors (71 visible warnings before the
final precise-link correction). Ordinary excursions and the known SR-1 numbering
warning remain diagnostics, not a reason to add shortcut graph edges. The
ignored SR+Maths viewer is rebuilt locally; nothing is published.

## SR-4 — Covariant Electromagnetism

13 November 2026 · guide reread before the module. All 135 original blocks now
have explicit statements, reviewed titles, consolidated kinds and level-70
bodies. Thirteen canonical Graphic blocks reuse existing artwork. Add a core
Derivation for reaching Lorenz gauge: 149 blocks total. Keep all original IDs,
questions/options, layouts, membership and tutorial targets.

Fix one explicit SI convention throughout: +---, x0=ct, A^mu=(phi/c,A),
F0i=Ei/c and Fij=-epsilon_ijk Bk. Electric and magnetic potential formulas,
boost examples, gauge signs, charged-action coupling and energy components now
agree with that convention. The external-force derivation uses a fixed path
parameter, varies both the sampled potential and path displacement, and only
then converts to proper time. Its force and power arguments state the external,
structureless, fixed-mass scope. Canonical and mechanical momentum are separated.

Gauge invariance constrains minimal coupling without uniquely deriving it;
that edge becomes Requires. The Lorenz condition is reached through a gauge
function equation, without a Maxwell prerequisite. Its existing Maxwell
application becomes Advanced, preventing a circular derivation dependency while
preserving the application and its canonical identity. Residual and boundary
freedom are explicit rather than claiming a unique representative.

The physical electromagnetic tensor has an actual metric-response construction
from the Maxwell density, and its components are extracted with SI constants.
This introduces an auxiliary measuring metric for the calculation, not a new
GR field equation. State the distinction between this physical tensor and a
canonical tensor. Poynting flux S and momentum density g=S/c2 are distinct;
energy density and flux are for the vacuum electromagnetic contribution, not
unqualified material-medium totals.

Graph changes: retain taxonomy, add independent construction supports for the
electric/magnetic split and the extraction of energy/flux components from the
physical stress tensor. Add Vector potential Requires Vector field and EM stress
energy Derives from Field Lagrangian. SR has 70 internal Foundation edges and
31 module-boundary edges; the module quotient remains a DAG. Additional
transitive diagnostics are accepted rather than adding shortcuts for previews.
SR+Maths validation: zero errors, 95 visible warnings.

Sources: Tong's primary field-theory text §§6.1–6.1.1 and Blaschke et al. (2016),
§3.3 for the metric construction; the SI translation and staged algebra are
explicitly authored. All native blocks and equations pass phone/desktop checks.
The larger teaching route has 13 levels, exceeding the Maths test helper's old
12-level guard. The helper now accepts a finite bound for this larger graph;
production reading-tree code is unchanged. Unit suite: 772 passed.

## SR-5 — Field Dynamics and Radiation

13 November 2026 · guide reread before authoring. Review all 85 original blocks
at level 70, with explicit statements, informative titles and the consolidated
kinds. Add eight canonical Graphic blocks and one density/current boost
Derivation, giving 94 blocks. All source IDs and original clarification scopes
are preserved. Questions/options, artwork, layouts, memberships and tutorials
are unchanged; the other SR modules and Maths content are unchanged in this pass.

Noether's first theorem now has an actual variational-current argument:
the general variation identity, symmetry boundary term and on-shell field
Euler–Lagrange condition combine to give J=Pi Delta-K. Global symmetries,
discrete symmetries and local gauge identities are distinguished. Translation
variations then construct the canonical energy–momentum tensor, rather than
merely naming that connection. Component SI factors, improvement boundaries and
field/matter exchange terms are explicit.

Four-current separates covariance from continuity; its boost components and
conservation-condition expansion are derived. Maxwell's sourced equation is
obtained by varying the stated density, antisymmetrising the potential variation,
integrating by parts and using arbitrary interior variations. The homogeneous
identity has its separate commuting-derivative proof. Current compatibility and
the local-to-integral charge-flow argument are developed without treating a
prescribed nonconserved source as automatically repaired by Maxwell's equation.

The wave equation combines the Maxwell potential form with Lorenz gauge.
Plane-wave dispersion is not enough: divergence/curl constraints also establish
transversality and the electric/magnetic amplitude relation. Keep source-free
regions distinct from field-free regions and state the ideal plane-wave scope.
The previously pruned Wave equation–Metric prerequisite is not restored.

Radiation reaction remains a controlled introduction. The conservation argument
includes retained particle and bound near-field energy as well as outgoing
radiation, and explicitly does not claim to determine a unique instantaneous
self-force. Point-charge pathologies are illustrated with a labelled limited
nonrelativistic model; reduction of order is explained as a controlled
approximation. Add precise primary support for near-field/Schott accounting and
reduced-order limitations, resolving the former broad-source-only worklist item.

Graph: add Noether Derives from Field equations and Four-current Requires
Four-vectors. Maxwell now derives via Field equations, with its old particle
Euler–Lagrange connection retained as Related, and explicitly derives its
homogeneous half from Field tensor. Revised justification notes identify what
each input actually supplies. SR has 70 internal Foundation edges and 34 boundary
edges; both concept prerequisites and the module quotient remain acyclic.
Validation: zero errors, 104 warnings for SR+Maths; zero errors, 230 warnings for
the complete KB. Transitive supports, illustrative excursions and the known
SR-1 numbering warning remain visible diagnostics.

All six phone/desktop checks for SR-3–5 pass, including native equations, pane
and equation widths, and equality of reading-tree edge coverage with context.
For the larger DAGs, the test expands each support concept once; every eligible
edge is still checked, without constructing exponentially many duplicate paths.
The actual lazy viewer behaviour is unchanged. Unit suite: 774 passed.

The full browser suite also passes: 327 fast and 78 full cases. All three
existing tutorials complete on desktop and phone. A semantic narration review
identified three Rest-energy prompts referring to the earlier SR-2 exposition;
these now distinguish energy identification, the kinetic-energy difference and
the rest-frame calculation accurately. No tutorial action or target changed.
