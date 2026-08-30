# GR and Mathematics Concept Expositions

This file holds readable draft expositions for General Relativity and reusable
mathematics concepts before or alongside their split into `data/content_blocks.csv`.

The CSV content blocks remain the source consumed by the application. This file
is an authoring and review aid: it preserves the coherent book-section form if
block boundaries, block kinds, or viewer presentation rules change later.

Use one section per concept, labelled with display ID, semantic ID, and title.
Keep concepts in domain-local atlas order where practical. Use
`docs/authoring/general_relativity_concept_plan.md` for the broader GR atlas
plan and `docs/authoring/GR_DRAFTING_ISSUES.md` for cross-cutting unresolved
questions.

## Template

Use this structure when starting a new GR or maths concept:

```markdown
## Display ID `concept.id`: Concept title

### Status

Current `nodes.csv` `authoring_status`, if any, and what would move the concept
to the next authoring state.

### Scope

What this concept owns, what it should only remind the reader of, and what
belongs elsewhere.

### Exposition

A coherent book-section draft before splitting into CSV blocks.

### Block Plan

- `concept.id.block`, `kind`, "Block title".

### Study Questions

Planned or drafted question set, starting easy and becoming more challenging.

### Graphics

Graphic intention, current status, and visual checks needed.

### References

Precise or broad source hooks.

### Drafting Issues

Concept-specific open points.
```

## M 1.1 `math.manifold`: Manifold

### Status

`prerequisite_support`: seed blocks and a graphic exist so GR content can link
to this concept. It is not yet a direct maths learning target.

### Scope

Introduce a manifold as the minimal smooth setting needed before GR can talk
about spacetime without global inertial coordinates. Keep topology light. Do
not teach curvature, metric geometry, tangent vectors, or tensor calculus in
full.

### Exposition

Seed text exists in `data/content_blocks.csv`. Full exposition still to be
drafted.

### Block Plan

- `math.manifold.overview`, `overview`, "Local Euclidean spaces".
- `math.manifold.definition`, `definition`, "Definition".

### Study Questions

Not drafted yet. Add questions if this maths concept becomes a direct learning
target rather than only a prerequisite.

### Graphics

Needs a simple chart/patch visual: a curved surface or abstract blob with a
local coordinate patch mapped to a plane.

### References

- TRR likely useful for broad geometric background; precise locator needed.

### Drafting Issues

- Decide how far topology should enter before it distracts from GR.

## M 1.2 `math.coordinate_chart`: Coordinate chart

### Status

`prerequisite_support`: seed blocks and a graphic exist so GR content can link
to this concept. It is not yet a direct maths learning target.

### Scope

Explain coordinates as local labels on a manifold and prepare the reader for
coordinate dependence in GR. Do not develop full tensor transformation laws
here.

### Exposition

Seed text exists in `data/content_blocks.csv`. Full exposition still to be
drafted.

### Block Plan

- `math.coordinate_chart.overview`, `overview`, "Coordinates as labels".
- `math.coordinate_chart.definition`, `definition`, "Definition".

### Study Questions

Not drafted yet. Add questions if this maths concept becomes a direct learning
target.

### Graphics

Needs a chart map visual showing a patch on a manifold mapped to numbered
coordinate axes.

### References

- TRR likely useful for broad geometric background; precise locator needed.

### Drafting Issues

- Coordinate transformations are planned as a distinct later concept. Avoid
  overloading this entry.

## M 1.3 `math.coordinate_transformation`: Coordinate transformation

### Status

`prerequisite_support`: seed blocks now exist so GR content can link to this
concept. It is not yet a direct maths learning target.

### Scope

Explain how coordinate descriptions change between overlapping charts. Keep
the focus on smooth relabelling of the same manifold points, not full tensor
transformation laws.

### Exposition

A coordinate transformation changes the numerical labels assigned to manifold
points while leaving the points themselves unchanged. In special relativity the
central examples are \cref{Lorentz transformations}{sr.lorentz_transformations}
between inertial frames. In general relativity the allowed coordinate changes
are broader: curved spacetime usually requires local charts, and the transition
from one chart to another may be smooth, nonlinear, and only locally defined.

Given two overlapping charts \(x^\mu\) and \(x'^\mu\), the transition rule is
written \(x'^\mu\coloneqq x'^\mu(x)\) on the overlap, with an inverse
\(x^\mu=x^\mu(x')\). The same manifold point is being described in either
chart. The derivatives \(\partial x'^\mu/\partial x^\nu\) form the Jacobian of
the change. Later, tensor components will use this Jacobian to change their
component values while preserving the geometric tensor itself.

The trap is to mistake coordinate change for physical change. A poorly chosen
coordinate system can make a simple situation look complicated, and a good one
can simplify a calculation, but the coordinate-independent statement is not
altered by the relabelling.

### Block Plan

- `math.coordinate_transformation.overview`, `overview`, "Changing labels, not points".
- `math.coordinate_transformation.definition`, `definition`, "Definition".
- `math.coordinate_transformation.jacobian`, `construction`, "Jacobian of the change".
- `math.coordinate_transformation.lorentz_as_special_case`, `example`, "Lorentz transformations as a special case".
- `math.coordinate_transformation.not_physics_change`, `misconception`, "Not a change of physics".

### Study Questions

Not drafted. Add questions only if this maths concept becomes a direct
learning target.

### Graphics

Needs an overlapping-chart visual or two coordinate grids connected by a
coordinate-change arrow.

### References

- TRR likely useful for coordinate and manifold background; precise locator
  needed.

### Drafting Issues

- Keep tensor transformation laws for later `math.tensor_transformation_law`.

## M 1.4 `math.worldline`: Worldline

### Status

`prerequisite_support`: seed blocks now exist so GR content can link to this
concept. It is not yet a direct maths learning target.

### Scope

Introduce a worldline as the curve traced by a particle, observer, detector, or
light signal through spacetime. Connect to existing SR use without duplicating
the full Minkowski-diagram treatment.

### Exposition

A worldline is the curve traced by a particle, observer, clock, detector, or
light signal through spacetime. It turns a sequence of
\cref{Spacetime events}{sr.spacetime_event} into one geometric object. In a
spacetime diagram the worldline is the visible path; in the manifold language
of GR it is a curve in spacetime itself.

Mathematically, a worldline is a parametrized curve \(x^\mu(\lambda)\). The
parameter \(\lambda\) labels points along the curve. For a massive clock or
particle, \cref{Proper time}{sr.proper_time} \(\tau\) is often the most useful
parameter because it is read by the clock following the path.

The curve itself should not be confused with one drawing of it. A
\cref{Minkowski diagram}{sr.minkowski_diagram} or a curved-spacetime chart may
make the same worldline look different. At each sufficiently smooth point the
curve has a tangent direction. In SR, parametrizing a timelike worldline by
proper time gives the \cref{Velocity four-vector}{sr.velocity_four_vector}; in
GR the same idea lives in the local tangent space at the event.

Massive particles and ordinary clocks follow timelike worldlines. Light follows
null worldlines. Spacelike curves can be drawn, but they do not represent the
history of a material object or signal.

### Block Plan

- `math.worldline.overview`, `overview`, "A history through spacetime".
- `math.worldline.definition`, `definition`, "Definition".
- `math.worldline.curves_and_coordinates`, `explanation`, "Curve versus coordinate plot".
- `math.worldline.tangent`, `construction`, "Tangent direction".
- `math.worldline.timelike_null`, `convention`, "Timelike and null cases".

### Study Questions

Not drafted. Add questions only if this maths concept becomes a direct
learning target.

### Graphics

Needs a spacetime/manifold curve with event points along it.

### References

- TRR likely useful for spacetime paths; precise locator needed.

### Drafting Issues

- Decide how much to distinguish timelike, null, and spacelike curves here
  versus later GR causal-structure concepts.

## M 1.5 `math.tangent_space`: Tangent space

### Status

`prerequisite_support`: seed blocks and a graphic exist so GR content can link
to this concept. It is not yet a direct maths learning target.

### Scope

Introduce the local vector space attached to a point of a manifold. Make clear
why SR's global vector-space intuition no longer suffices in curved spacetime.
Do not yet teach connections or parallel transport.

### Exposition

Seed text exists in `data/content_blocks.csv`. Full exposition still to be
drafted.

### Block Plan

- `math.tangent_space.overview`, `overview`, "Vector space at a point".
- `math.tangent_space.definition`, `definition`, "Definition".

### Study Questions

Not drafted yet. Add questions if this maths concept becomes a direct learning
target.

### Graphics

Needs a tangent-plane visual attached at a point, with local basis arrows.

### References

- TRR likely useful for broad geometric background; precise locator needed.

### Drafting Issues

- Later `math.cotangent_space` and `math.tensor_field` concepts may require a
  shared visual motif.

## M 1.6 `math.cotangent_space`: Cotangent space

### Status

`prerequisite_support`: seed blocks now exist so GR content can link to this
concept. It is not yet a direct maths learning target.

### Scope

Introduce cotangent vectors as dual objects that eat tangent vectors and return
numbers. Prepare gradients, one-forms, index lowering, and tensor fields
without trying to teach the full tensor algebra.

### Exposition

The cotangent space is the dual partner of the
\cref{Tangent space}{math.tangent_space}. Tangent vectors are the natural
objects for velocities and infinitesimal displacements. Cotangent vectors,
also called covectors or one-forms, are linear objects that act on tangent
vectors and return numbers.

At a point \(p\), the cotangent space \(T_p^*M\) is the vector space of linear
maps from \(T_pM\) to real numbers. If \(v\in T_pM\) and
\(\omega\in T_p^*M\), their natural pairing is written \(\omega(v)\). A
standard example is the differential \(df\) of a scalar function \(f\): given a
tangent vector \(v\), \(df(v)\) is the directional rate of change of \(f\) along
that tangent direction.

In coordinates, if \(\partial/\partial x^\mu\) is the tangent basis, the dual
covector basis is written \(dx^\mu\). It is defined by
\(dx^\mu(\partial/\partial x^\nu)\coloneqq\delta^\mu{}_\nu\). This is the
minimal distinction needed before tensor fields: tensors are built from
tangent and cotangent ingredients at each point.

The common warning is not to identify vectors and covectors too early. A metric
can relate them by raising and lowering indices, but the cotangent space itself
exists before a metric is chosen.

### Block Plan

- `math.cotangent_space.overview`, `overview`, "Dual vectors at a point".
- `math.cotangent_space.definition`, `definition`, "Definition".
- `math.cotangent_space.gradient_example`, `example`, "Gradient as a covector".
- `math.cotangent_space.basis`, `construction`, "Dual basis".
- `math.cotangent_space.metric_warning`, `warning`, "Do not assume the metric too soon".

### Study Questions

Not drafted. Add questions only if this maths concept becomes a direct
learning target.

### Graphics

Needs a visual paired with tangent space: a covector/gradient or contour motif
acting on tangent arrows.

### References

- TRR likely useful for tangent/cotangent and differential forms; precise
  locator needed.

### Drafting Issues

- The seed text emphasizes the dual-space definition first, then gradients as
  the concrete example. Revisit if this proves too abstract in the GR pass.

## M 2.1 `math.tensor_field`: Tensor field

### Status

`prerequisite_support`: seed blocks and a graphic exist so GR content can link
to this concept. It is not yet a direct maths learning target.

### Scope

Introduce a tensor assigned smoothly at each point. Connect to coordinate
independence, but leave detailed index notation and transformation laws to
later concepts.

### Exposition

A tensor field assigns a tensor to each point of a manifold. The word "field"
means point-by-point assignment: the tensor may vary from event to event, just
as an ordinary scalar or vector field can vary across spacetime. GR needs this
language because its central objects are not single global quantities but
spacetime-dependent geometric structures.

At each point \(p\), tensors are built from the local
\cref{Tangent space}{math.tangent_space} and
\cref{Cotangent space}{math.cotangent_space}. A scalar field assigns a number
to each point. A vector field assigns a tangent vector. More general tensor
fields have several vector or covector slots and can represent objects such as
the metric, stress-energy, and curvature.

The important conceptual point is coordinate independence. A tensor field has
components in a chosen chart, but it is not merely the array of components.
When coordinates change, the component array changes in a controlled way so the
underlying geometric object is preserved.

### Block Plan

- `math.tensor_field.overview`, `overview`, "Tensors varying over spacetime".
- `math.tensor_field.definition`, `definition`, "Definition".
- `math.tensor_field.pointwise`, `explanation`, "Point-by-point objects".
- `math.tensor_field.examples`, `example`, "Scalars, vectors, and higher tensors".
- `math.tensor_field.not_component_array`, `misconception`, "Not just an array of components".

### Study Questions

Not drafted yet. Add questions if this maths concept becomes a direct learning
target.

### Graphics

Needs a field visual showing small tensor/vector glyphs attached at several
points on a manifold.

### References

- TRR likely useful for broad geometric background; precise locator needed.

### Drafting Issues

- Decide whether scalar and vector fields should be treated as examples here
  or only linked back to existing SR field concepts.

## M 2.2 `math.index_notation`: Abstract and component indices

### Status

`prerequisite_support`: seed blocks exist so GR content can link to this
concept. It is not yet a direct maths learning target.

### Scope

Distinguish abstract index notation from component notation. Keep this as a
notation support concept; leave tensor transformation details to
`math.tensor_transformation_law`.

### Exposition

Index notation is compact, but it carries more than one meaning. Sometimes an
index names the type of tensor slot: vector-like, covector-like, or a
combination of both. Sometimes an index names an actual coordinate component in
a chosen basis. GR uses both habits, and confusion between them makes tensor
equations look more mysterious than they are.

In abstract index notation, \(T^a{}_b\) denotes a tensor with one vector slot
and one covector slot; the letters are bookkeeping for the tensor's type and
contractions, not a request to choose coordinates. In component notation,
\(T^\mu{}_\nu\) denotes the numerical components of that tensor in a selected
coordinate system or frame. The same geometric tensor can have different
component arrays in different charts.

This atlas often uses Greek indices such as \(\mu,\nu,\alpha,\beta\) for
spacetime components. Repeated upper/lower index pairs are summed. A free index
must appear consistently on both sides of an equation, while a repeated index
is a dummy label that can be renamed.

The warning is simple: an equation can be coordinate-independent even when it
is written using indices. The test is not whether indices appear, but whether
the objects and their contractions transform correctly.

### Block Plan

- `math.index_notation.overview`, `overview`, "Indices as bookkeeping".
- `math.index_notation.definition`, `definition`, "Definition".
- `math.index_notation.component_indices`, `convention`, "Component indices".
- `math.index_notation.summation`, `convention`, "Repeated and free indices".
- `math.index_notation.not_coordinates_only`, `misconception`, "Indexed need not mean coordinate-bound".

### Study Questions

Not drafted. Add questions only if this maths concept becomes a direct
learning target.

### Graphics

Deferred for this seed pass.

### References

- TRR likely useful for tensor/index notation; precise locator needed.

### Drafting Issues

- Later authoring should decide whether to use Latin abstract indices in GR
  prose or mostly Greek component indices with explanatory cautions.

## M 2.3 `math.tensor_transformation_law`: Tensor transformation law

### Status

`prerequisite_support`: seed blocks exist so GR content can link to this
concept. It is not yet a direct maths learning target.

### Scope

Explain what makes tensor component equations coordinate-independent. Keep the
focus on the transformation law and Jacobian factors; leave detailed examples
to later GR concepts.

### Exposition

The tensor transformation law is the rule that tells how component arrays
change when coordinates change. It is the mathematical protection against
confusing a coordinate description with the object itself. Coordinates may be
changed using a \cref{Coordinate transformation}{math.coordinate_transformation},
but a tensor equation keeps its geometric meaning only if every component
changes by the proper Jacobian factors.

For a vector, the components transform with one Jacobian:
\[
V'^\mu \coloneqq \frac{\partial x'^\mu}{\partial x^\nu}V^\nu.
\]
For a covector, the inverse Jacobian appears:
\[
\omega'_\mu \coloneqq \frac{\partial x^\nu}{\partial x'^\mu}\omega_\nu.
\]
Higher-rank tensors get one such factor for each index. This is the practical
meaning of saying that the indices know how the object transforms.

The law does not say that tensor components stay numerically unchanged. Usually
they do not. It says that the change of components is controlled so that
contractions and tensor equations describe the same geometric statement in any
allowed coordinate system.

### Block Plan

- `math.tensor_transformation_law.overview`, `overview`, "Components that transform correctly".
- `math.tensor_transformation_law.definition`, `definition`, "Definition".
- `math.tensor_transformation_law.vector_covector`, `construction`, "Vector and covector cases".
- `math.tensor_transformation_law.higher_rank`, `construction`, "One factor per index".
- `math.tensor_transformation_law.not_invariant_components`, `misconception`, "Not unchanged components".

### Study Questions

Not drafted. Add questions only if this maths concept becomes a direct
learning target.

### Graphics

Deferred for this seed pass.

### References

- TRR likely useful for tensors and coordinate transformations; precise
  locator needed.

### Drafting Issues

- The seed text uses component notation rather than abstract indices. Revisit
  when GR metric and connection notation settles.

## GR 1.1 `gr.gravity_as_geometry`: Gravity as geometry

### Status

`seed`: seed blocks, seed study questions, graph links, and a graphic exist.
Full book-section exposition and source tightening remain to be done.

### Scope

State the central conceptual move of GR: gravitational phenomena are described
by spacetime geometry rather than a force field on fixed Minkowski spacetime.
Use this as an orientation concept. Do not try to derive the Einstein field
equations here.

### Exposition

Seed text exists in `data/content_blocks.csv`. Full exposition still to be
drafted after the equivalence-principle treatment is settled.

### Block Plan

- `gr.gravity_as_geometry.overview`, `overview`, "The central move".
- `gr.gravity_as_geometry.definition`, `definition`, "Definition".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one basic
multiple-choice check and two short conceptual interpretation questions.

### Graphics

Needs a conceptual bridge graphic: flat grid versus curved grid, with a free
particle following a natural path.

### References

- TTM GR source locator needed.
- TRR broad locator needed.

### Drafting Issues

- This concept currently derives from both the equivalence principle and tidal
  gravity in the seed graph. Recheck edge direction after fuller exposition.
- Decide whether this should be a short orientation concept or a richer
  synthesis concept revisited later.

## GR 1.2 `gr.equivalence_principle`: Equivalence principle

### Status

`seed`: seed blocks, seed study questions, graph links, and a graphic exist.
Full book-section exposition and source tightening remain to be done.

### Scope

Explain local indistinguishability of uniform gravity and acceleration, and
connect that physical fact to free-fall laboratories. This should be the first
full GR authoring target.

### Exposition

Seed text exists in `data/content_blocks.csv`. Full exposition to be drafted
next.

### Block Plan

- `gr.equivalence_principle.overview`, `overview`, "Local gravity and acceleration".
- `gr.equivalence_principle.definition`, `definition`, "Definition".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one basic
multiple-choice check, one question about local scope, and one SR-connection
question.

### Graphics

Needs an elevator/free-fall visual, ideally showing both an accelerated rocket
and a local freely falling laboratory.

### References

- TTM GR source locator needed.
- TRR broad locator needed.

### Drafting Issues

- Be precise about "sufficiently small": tidal effects are not transformed away
  over finite regions.
- Decide whether inertial and gravitational mass should be in this concept or a
  separate historical/experimental note.

## GR 1.3 `gr.local_inertial_frame`: Local inertial frame

### Status

`seed`: seed blocks, seed study questions, graph links, and a graphic exist.
Full book-section exposition and source tightening remain to be done.

### Scope

Show how SR is recovered locally in GR. Connect directly to
`\cref{Inertial frames}{sr.inertial_frames}` and tangent-space intuition.
Do not yet teach normal coordinates or Christoffel symbols in detail.

### Exposition

Seed text exists in `data/content_blocks.csv`. Full exposition still to be
drafted.

### Block Plan

- `gr.local_inertial_frame.overview`, `overview`, "SR recovered locally".
- `gr.local_inertial_frame.definition`, `definition`, "Definition".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one basic
multiple-choice check, one SR comparison, and one finite-region limitation
question.

### Graphics

Needs a local patch visual where the metric/grid is approximately Minkowskian
near one event but not over a large region.

### References

- TTM GR source locator needed.
- TRR broad locator needed.

### Drafting Issues

- Clarify relationship to `math.tangent_space` without forcing too much
  differential geometry into the first GR layer.

## GR 1.4 `gr.freely_falling_observer`: Freely falling observer

### Status

`seed`: seed blocks, seed study questions, graph links, and a graphic exist.
Full book-section exposition and source tightening remain to be done.

### Scope

Explain free fall as inertial motion in GR: no support force, no rocket thrust,
and no non-gravitational acceleration. Do not yet develop the geodesic equation.

### Exposition

Seed text exists in `data/content_blocks.csv`. Full exposition still to be
drafted.

### Block Plan

- `gr.freely_falling_observer.overview`, `overview`, "Inertial motion in gravity".
- `gr.freely_falling_observer.definition`, `definition`, "Definition".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one basic
multiple-choice check, one supported-versus-free-fall distinction, and one
coordinate interpretation question.

### Graphics

Needs a falling-laboratory or orbiting-observer visual contrasting free fall
with supported rest.

### References

- TTM GR source locator needed.
- TRR broad locator needed.

### Drafting Issues

- The later `gr.geodesic` concept should own the mathematical derivation.

## GR 1.5 `gr.tidal_gravity`: Tidal gravity

### Status

`seed`: seed blocks, seed study questions, graph links, and a graphic exist.
Full book-section exposition and source tightening remain to be done.

### Scope

Introduce tidal effects as relative acceleration between neighbouring freely
falling bodies and as the operational sign of curvature. Do not yet define the
Riemann tensor.

### Exposition

Seed text exists in `data/content_blocks.csv`. Full exposition still to be
drafted.

### Block Plan

- `gr.tidal_gravity.overview`, `overview`, "What cannot be transformed away".
- `gr.tidal_gravity.definition`, `definition`, "Definition".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one basic
multiple-choice check, one local-frame limitation question, and one curvature
connection question.

### Graphics

Needs a converging/diverging family of neighbouring free-fall worldlines, or a
falling cloud stretched radially and squeezed transversely.

### References

- TTM GR source locator needed.
- TRR broad locator needed.

### Drafting Issues

- This concept will later link tightly to geodesic deviation and curvature.
  Keep the first-layer treatment operational rather than tensorial.

## GR 2.1 `gr.metric_tensor`: Spacetime metric

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

Introduce the metric as the central measuring tensor field of GR. Connect it
back to the SR metric and local inertial frames, but do not yet develop the
Einstein equation, Christoffel symbols, or curvature.

### Exposition

The spacetime metric is the central field of general relativity. In special
relativity the metric can be represented by a fixed Minkowski matrix in
standard inertial coordinates. In GR the metric becomes a field
\(g_{\mu\nu}(x)\), assigning a local measuring rule at each event.

The metric is a symmetric rank-\((0,2)\) tensor field. It takes tangent
vectors as inputs and returns their inner product. From this one obtains local
intervals, clock times, spatial distances within a chosen slicing, null cones,
and the distinction between timelike, null, and spacelike directions.

For a small coordinate displacement the metric gives the line element
\[
ds^2 \coloneqq g_{\mu\nu}(x)\,dx^\mu dx^\nu .
\]
This is the curved-spacetime successor of the SR interval. Near a freely
falling observer it can locally resemble the Minkowski metric, but over a
larger region it may vary from point to point.

The metric is not merely a picture of curved coordinate grid lines. Coordinates
label events; the metric supplies the physical measuring rule attached to
those labels.

### Block Plan

- `gr.metric_tensor.overview`, `overview`, "The measuring field".
- `gr.metric_tensor.definition`, `definition`, "Definition".
- `gr.metric_tensor.from_sr_metric`, `construction`, "From \(\eta_{\mu\nu}\) to \(g_{\mu\nu}\)".
- `gr.metric_tensor.line_element_preview`, `result`, "Local interval rule".
- `gr.metric_tensor.not_grid`, `misconception`, "Not just coordinate grid spacing".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one basic
multiple-choice check, one SR-to-GR comparison, and one short interval
calculation.

### Graphics

Deferred for this seed pass. A useful graphic would contrast fixed Minkowski
light cones with light cones attached point-by-point to a curved spacetime
surface.

### References

- TTM GR source locator needed.
- TRR metric/geometry locator needed.

### Drafting Issues

- A later line-element concept may deserve its own node. For now the line
  element is only previewed here because it is the most compact operational
  use of the metric.

## GR 2.2 `gr.inverse_metric`: Inverse metric

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

Define the inverse metric and its role in raising indices. Keep the discussion
to the algebraic relation with the metric; do not yet use it in curvature or
field equations.

### Exposition

The inverse metric is the tensor that undoes the metric's index-lowering
operation. If \(g_{\mu\nu}\) lowers vector indices, then \(g^{\mu\nu}\) raises
covector indices. It is the object needed whenever GR forms contractions or
writes the same geometric quantity with different index positions.

The defining relation is
\[
g^{\mu\alpha}g_{\alpha\nu}\coloneqq\delta^\mu{}_\nu .
\]
This relation requires the metric to be non-degenerate, so the component
matrix has a nonzero determinant. In practical component calculations,
\(g^{\mu\nu}\) is the inverse matrix of \(g_{\mu\nu}\), but geometrically it
is still a tensor, not just a matrix trick.

The inverse metric is not a second independent geometry. Once the metric is
given, its inverse is fixed.

### Block Plan

- `gr.inverse_metric.overview`, `overview`, "Undoing the metric map".
- `gr.inverse_metric.definition`, `definition`, "Definition".
- `gr.inverse_metric.raising_indices`, `construction`, "Raising indices".
- `gr.inverse_metric.coordinate_dependence`, `convention`, "Same geometry, transformed components".
- `gr.inverse_metric.not_new_geometry`, `misconception`, "Not a second metric".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one definition
check, one conceptual distinction, and one simple inverse-matrix calculation.

### Graphics

Deferred for this seed pass. A useful graphic would show the metric lowering a
tangent vector to a covector and the inverse metric reversing that map.

### References

- TTM GR source locator needed.
- TRR metric/tensor locator needed.

### Drafting Issues

- Later authoring should decide how much abstract-index language to introduce
  when discussing raising and lowering.

## GR 2.3 `gr.volume_element`: Volume element

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

Introduce the invariant spacetime volume measure \(\sqrt{-g}\,d^4x\). Keep the
focus on integration measure and coordinate independence; do not yet discuss
actions in detail.

### Exposition

The GR volume element supplies the coordinate-independent measure used for
integration over spacetime. Coordinate volume \(d^4x\) by itself depends on the
labels used for events. The metric determinant supplies the compensating
factor.

For a Lorentzian metric with determinant \(g\coloneqq\det(g_{\mu\nu})\), the
standard spacetime volume element is
\[
\sqrt{-g}\,d^4x .
\]
The minus sign reflects the common Lorentzian signature convention in which
the determinant is negative in standard local coordinates.

The factor \(\sqrt{-g}\) changes oppositely to the coordinate volume under a
coordinate transformation, so the product behaves as an invariant integration
measure. It is part of the geometry, not a matter density.

### Block Plan

- `gr.volume_element.overview`, `overview`, "Invariant volume measure".
- `gr.volume_element.definition`, `definition`, "Definition".
- `gr.volume_element.why_needed`, `explanation`, "Why the factor is needed".
- `gr.volume_element.determinant_role`, `construction`, "Metric determinant".
- `gr.volume_element.not_extra_matter`, `misconception`, "Not a field density of matter".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one basic
multiple-choice check, one coordinate-invariance question, and one determinant
calculation.

### Graphics

Deferred for this seed pass. A useful graphic would compare a coordinate grid
cell with its metric-weighted spacetime volume.

### References

- TTM GR source locator needed.
- TRR integration/metric determinant locator needed.

### Drafting Issues

- This concept will become more useful once action principles are added. For
  now it mainly prepares notation for later GR equations.

## GR 3.1 `gr.line_element`: Line element

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

Introduce the line element as the local interval formula determined by the
metric. Connect it to the SR spacetime interval and to later proper-time/null
curve concepts, but do not yet develop geodesics.

### Exposition

The line element is the compact local formula by which the spacetime metric
turns an infinitesimal coordinate displacement into an interval. With the
mostly-minus signature convention and natural units, it is written
\[
ds^2 \coloneqq g_{\mu\nu}(x)\,dx^\mu dx^\nu .
\]
This is the curved-spacetime successor of the special-relativistic interval.

The metric supplies the coefficients \(g_{\mu\nu}(x)\), while \(dx^\mu\)
describes a small displacement in the chosen chart. The coordinate components
can change from chart to chart, but the contracted interval is the local
geometric quantity.

The line element is local. To obtain a finite clock time or path length, one
must integrate along a particular curve.

### Block Plan

- `gr.line_element.overview`, `overview`, "The interval written locally".
- `gr.line_element.definition`, `definition`, "Definition".
- `gr.line_element.metric_use`, `construction`, "Using the metric".
- `gr.line_element.sr_limit`, `result`, "SR as a special case".
- `gr.line_element.not_global_distance`, `misconception`, "Not a global ruler by itself".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one definition
check, one locality question, and one short interval calculation.

### Graphics

Deferred for this seed pass. A useful graphic would show a tiny displacement
on a curved coordinate grid, with the metric converting it to \(ds^2\).

### References

- TTM GR source locator needed.
- TRR metric/interval locator needed.

### Drafting Issues

- Decide later whether a separate "spacetime interval in GR" alias or view is
  needed, or whether `gr.line_element` is enough.

## GR 3.2 `gr.proper_time`: Proper time in curved spacetime

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

Introduce proper time as clock time accumulated along a timelike worldline in
curved spacetime. Keep the geodesic/free-fall dynamics for later concepts.

### Exposition

Proper time in GR is what an ideal clock records along a timelike worldline.
The metric determines how much clock time each small segment contributes. With
the mostly-minus convention and natural units,
\[
d\tau \coloneqq \sqrt{ds^2}
\]
for timelike segments, and a finite elapsed proper time is obtained by
integrating along the worldline.

This generalises the SR idea of proper time. In flat spacetime the metric is
Minkowskian in inertial coordinates; in GR the metric may vary along the path.
The central physical point is unchanged: proper time belongs to the clock's
own path, not to a coordinate label.

### Block Plan

- `gr.proper_time.overview`, `overview`, "Clock time along a worldline".
- `gr.proper_time.definition`, `definition`, "Definition".
- `gr.proper_time.worldline_dependence`, `construction`, "Depends on the path".
- `gr.proper_time.sr_generalisation`, `result`, "Generalising SR proper time".
- `gr.proper_time.not_coordinate_time`, `misconception`, "Not coordinate time".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one basic
definition check, one path-dependence question, and one simple \(d\tau\)
calculation.

### Graphics

Deferred for this seed pass. A useful graphic would show two timelike
worldlines between meetings with different accumulated clock readings.

### References

- TTM GR source locator needed.
- TRR proper-time/clock locator needed.

### Drafting Issues

- Later authoring should coordinate this concept carefully with
  `gr.geodesic_action` and `gr.four_velocity`.

## GR 3.3 `gr.null_curve`: Null curve

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

Define null curves as zero-interval curves and connect them to lightlike
propagation and causal boundaries. Leave null geodesics and lensing for later.

### Exposition

A null curve has tangent directions with zero spacetime interval:
\[
ds^2 \coloneqq g_{\mu\nu}dx^\mu dx^\nu = 0 .
\]
This does not mean that the curve has zero coordinate displacement. It means
that the metric classifies its tangent direction as lightlike.

Null directions form the boundary of the local light cone. Timelike directions
lie inside the cone, spacelike directions outside it. Later geodesic concepts
will add the dynamical statement that freely propagating light follows null
geodesics.

### Block Plan

- `gr.null_curve.overview`, `overview`, "Zero interval paths".
- `gr.null_curve.definition`, `definition`, "Definition".
- `gr.null_curve.lightlike`, `explanation`, "Lightlike propagation".
- `gr.null_curve.cone_boundary`, `result`, "Boundary of the light cone".
- `gr.null_curve.not_zero_motion`, `misconception`, "Zero interval is not no motion".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one metric
property check, one misconception question, and one light-cone connection.

### Graphics

Deferred for this seed pass. A useful graphic would show a local cone with a
null tangent lying on its surface.

### References

- TTM GR source locator needed.
- TRR causal/null curve locator needed.

### Drafting Issues

- Keep this distinct from `gr.geodesic`; null describes metric type, while
  geodesic describes free propagation/straightest motion.

## GR 3.4 `gr.causal_structure`: Causal structure

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

Introduce causal structure as the metric-determined pattern of timelike, null,
and spacelike relations. Prepare for horizons later without defining them yet.

### Exposition

Causal structure records what can influence what. At each event the metric
determines timelike, null, and spacelike directions. Null directions form the
local light cone; timelike directions lie inside it; spacelike directions lie
outside it.

This is local metric geometry, not merely a drawing convention. A diagram of a
light cone depends on coordinates and visual choices, but the classification
of directions is determined by the metric. As light cones are followed across
spacetime, they control larger questions about which events can send signals
to which observers.

### Block Plan

- `gr.causal_structure.overview`, `overview`, "What can influence what".
- `gr.causal_structure.definition`, `definition`, "Definition".
- `gr.causal_structure.light_cones`, `construction`, "Light cones from the metric".
- `gr.causal_structure.local_to_global`, `explanation`, "Local cones and global questions".
- `gr.causal_structure.not_picture_only`, `misconception`, "Not just a diagram convention".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one definition
check, one local light-cone question, and one global-consequence question.

### Graphics

Deferred for this seed pass. A useful graphic would show light cones changing
orientation/width from event to event while preserving local causal meaning.

### References

- TTM GR source locator needed.
- TRR causal-structure locator needed.

### Drafting Issues

- This concept should later link strongly to event horizons and Penrose
  diagrams when those concepts are added.

## GR 3.5 `gr.local_flatness`: Local flatness

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

State local flatness as the metric form of the equivalence principle. Emphasise
that it is a point/local statement and does not remove curvature over a finite
region.

### Exposition

Local flatness says that at any event one can choose local inertial coordinates
in which the metric takes its Minkowski form at that event:
\[
g_{\mu\nu}\overset{\text{at the event}}{=}\eta_{\mu\nu}.
\]
With a suitable choice, the first derivatives of the metric also vanish at the
event. This is the metric-language version of recovering SR in a sufficiently
small freely falling laboratory.

The warning is essential: local flatness is not global flatness. Tidal effects
and curvature depend on behaviour over a region and cannot generally be
removed by making the metric Minkowskian at one point.

### Block Plan

- `gr.local_flatness.overview`, `overview`, "SR at one event".
- `gr.local_flatness.definition`, `definition`, "Definition".
- `gr.local_flatness.equivalence_principle`, `construction`, "Metric form of the equivalence principle".
- `gr.local_flatness.curvature_remains`, `warning`, "Curvature is not removed".
- `gr.local_flatness.not_global_flatness`, `misconception`, "Not global flatness".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one coordinate
choice check, one global-flatness distinction, and one equivalence-principle
connection.

### Graphics

Deferred for this seed pass. A useful graphic would show a curved surface with
a tangent plane at one point, paired with a warning that curvature remains over
larger regions.

### References

- TTM GR source locator needed.
- TRR local inertial frame/local flatness locator needed.

### Drafting Issues

- Later source review should check how strongly to state the vanishing of first
  metric derivatives, since this depends on the smooth coordinate construction
  being introduced at the right level.

## GR 3.6 `gr.metric_signature`: Metric signature convention

### Status

`seed`: seed blocks, seed study questions, and graph links exist. Graphics,
full book-section exposition, and source tightening remain to be done.

### Scope

Record the sign and unit conventions used by the GR seed text. Keep this as a
supporting convention concept, not a physics derivation.

### Exposition

Metric signature records the sign convention for time and space in the
interval. This atlas uses the mostly-minus convention \(+---\) for GR seed
content unless stated otherwise. In natural units, timelike intervals have
\(ds^2>0\), null intervals have \(ds^2=0\), and spacelike intervals have
\(ds^2<0\).

Many sources use the opposite convention, \(-+++\). The physics is not changed
by the sign convention, but formulas must be translated consistently. This
matters especially when comparing curvature, stress-energy, and field-equation
signs across books.

### Block Plan

- `gr.metric_signature.overview`, `overview`, "Choosing the sign convention".
- `gr.metric_signature.definition`, `definition`, "Definition".
- `gr.metric_signature.alternative`, `convention`, "The opposite convention".
- `gr.metric_signature.units`, `convention`, "Natural units and dimensions".
- `gr.metric_signature.warning`, `warning`, "Watch signs when comparing sources".

### Study Questions

Drafted in `data/study_questions.csv` as three seed questions: one convention
check, one source-comparison question, and one simple interval-classification
calculation.

### Graphics

Deferred for this seed pass. A small sign-convention table may be enough rather
than a full conceptual graphic.

### References

- TTM GR source locator needed.
- TRR sign-convention locator needed if available.

### Drafting Issues

- This concept may later be better treated as a notation/convention appendix
  rather than a normal graph node. For now a visible node helps explain signs
  in the GR seed content.

## GR 4.1 `gr.connection`: Connection

### Status

`seed`: two seed blocks, three study questions, and conservative graph links
exist. Full exposition, graphics, and source tightening remain deferred.

### Scope And Exposition

A connection solves the comparison problem created by curved spacetime:
vectors at different events live in different tangent spaces and cannot be
subtracted without an additional rule. It supplies differentiation and
transport between neighbouring tangent spaces. Standard GR uses the unique
metric-compatible, torsion-free Levi-Civita connection.

### Block Plan

- `gr.connection.overview`, `overview`, "Comparing neighbouring vectors".
- `gr.connection.definition`, `definition`, "Definition".

### Drafting Issues

- Add a tangent-space comparison graphic and precise TTM/TRR connection locators.

## GR 4.2 `gr.christoffel_symbols`: Christoffel symbols

### Status

`seed`: two seed blocks, three study questions, and graph links exist.

### Scope And Exposition

Christoffel symbols are coordinate coefficients of the Levi-Civita connection,
not tensor components. Their metric formula shows how first derivatives of the
metric correct component differentiation. Suitable coordinates can make them
vanish at one event without eliminating curvature.

### Block Plan

- `gr.christoffel_symbols.overview`, `overview`, "Connection coefficients".
- `gr.christoffel_symbols.definition`, `definition`, "Definition".

### Drafting Issues

- A full pass should derive the metric formula and compare transformation laws.

## GR 4.3 `gr.covariant_derivative`: Covariant derivative

### Status

`seed`: two seed blocks, three study questions, and graph links exist.

### Scope And Exposition

The covariant derivative adds connection terms to an ordinary component
derivative so the result transforms tensorially. Each upper index contributes
a positive connection term and each lower index a negative term; scalars retain
their ordinary partial derivative.

### Block Plan

- `gr.covariant_derivative.overview`, `overview`, "Differentiation that respects geometry".
- `gr.covariant_derivative.definition`, `definition`, "Definition".

### Drafting Issues

- The full exposition needs multi-index examples and a derivation of signs.

## GR 4.4 `gr.metric_compatibility`: Metric compatibility

### Status

`seed`: two seed blocks, three study questions, and graph links exist.

### Scope And Exposition

Metric compatibility,
\(\nabla_\alpha g_{\mu\nu}=0\), says that the connection preserves metric
inner products under parallel transport. It also lets index raising and
lowering commute with covariant differentiation. Combined with zero torsion it
selects the Levi-Civita connection.

### Block Plan

- `gr.metric_compatibility.overview`, `overview`, "Preserving the metric".
- `gr.metric_compatibility.definition`, `definition`, "Definition".

### Drafting Issues

- Later explain uniqueness without taking over the connection derivation.

## GR 4.5 `gr.torsion_free_connection`: Torsion-free connection

### Status

`seed`: two seed blocks, three study questions, and graph links exist.

### Scope And Exposition

Torsion is the antisymmetric part of the connection in a coordinate basis.
Standard GR sets it to zero, making the lower Christoffel indices symmetric.
This condition does not imply zero curvature and should not be confused with
flatness.

### Block Plan

- `gr.torsion_free_connection.overview`, `overview`, "No infinitesimal twist".
- `gr.torsion_free_connection.definition`, `definition`, "Definition".

### Drafting Issues

- The full pass should motivate torsion geometrically without introducing tetrads.

## GR 4.6 `gr.parallel_transport`: Parallel transport

### Status

`seed`: two seed blocks, three study questions, and graph links exist.

### Scope And Exposition

Parallel transport carries a vector along a curve according to the connection.
The condition \(u^\nu\nabla_\nu V^\mu=0\) expresses unchanged direction in
the connection's sense. Path dependence and closed-loop rotation preview
curvature without yet defining the Riemann tensor.

### Block Plan

- `gr.parallel_transport.overview`, `overview`, "Carrying a direction along a curve".
- `gr.parallel_transport.definition`, `definition`, "Definition".

### Drafting Issues

- Add a sphere/loop transport graphic and later link holonomy to curvature.

## GR 5.1 `gr.geodesic`: Geodesic

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

A geodesic is a curve whose tangent is parallel transported along itself. This
"straightest path" definition avoids the misleading claim that every geodesic
is a shortest path. Timelike geodesics model unforced massive test bodies and
null geodesics model freely propagating light.

### Block Plan And Drafting Issues

- `gr.geodesic.overview`, `overview`; `gr.geodesic.definition`, `definition`.
- Add causal-type examples, conjugate-point caveats, graphics, and sources later.

## GR 5.2 `gr.geodesic_equation`: Geodesic equation

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The coordinate geodesic equation expands the autoparallel condition into a
coordinate acceleration plus a Christoffel term. It teaches that nonzero
coordinate acceleration need not represent force; covariant acceleration is
the invariant test.

### Block Plan And Drafting Issues

- `gr.geodesic_equation.overview`, `overview`; `gr.geodesic_equation.definition`, `definition`.
- Derive the coordinate form and explain affine parameters in the full pass.

## GR 5.3 `gr.geodesic_action`: Geodesic action

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The massive-particle action integrates proper time or path length between fixed
events. Its stationary paths obey the geodesic equation. The seed keeps the
parameter-choice subtlety visible without taking over the full variational
derivation.

### Block Plan And Drafting Issues

- `gr.geodesic_action.overview`, `overview`; `gr.geodesic_action.definition`, `definition`.
- Later compare square-root and quadratic actions and treat null paths carefully.

## GR 5.4 `gr.four_velocity`: Four-velocity in curved spacetime

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Four-velocity is the proper-time tangent to a timelike worldline. The familiar
SR normalization survives point by point, but the vector now belongs to a
different tangent space at each event.

### Block Plan And Drafting Issues

- `gr.four_velocity.overview`, `overview`; `gr.four_velocity.definition`, `definition`.
- Add explicit normalization derivation and a tangent-bundle graphic later.

## GR 5.5 `gr.four_acceleration`: Four-acceleration

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Four-acceleration is the covariant change of four-velocity along a worldline.
It vanishes in gravitational free fall but not for a supported or propelled
observer. This distinguishes proper acceleration from chart-dependent
coordinate acceleration.

### Block Plan And Drafting Issues

- `gr.four_acceleration.overview`, `overview`; `gr.four_acceleration.definition`, `definition`.
- Later derive orthogonality to four-velocity and add accelerometer interpretation.

## GR 5.6 `gr.geodesic_deviation`: Geodesic deviation

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Geodesic deviation relates relative acceleration of neighbouring free-fall
paths to the Riemann tensor. It is the mathematical bridge from tidal gravity
to curvature. The seed flags the convention-dependent overall sign.

### Block Plan And Drafting Issues

- `gr.geodesic_deviation.overview`, `overview`; `gr.geodesic_deviation.definition`, `definition`.
- Derive the equation only after the Riemann convention is fixed in Layer 6.

## GR 6.1 `gr.riemann_tensor`: Riemann curvature tensor

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The Riemann tensor is the full local curvature of the connection. It measures
the commutator of covariant derivatives, closed-loop transport failure, and
relative geodesic acceleration. Its overall sign is convention-dependent and
must be fixed before detailed derivations.

### Block Plan And Drafting Issues

- `gr.riemann_tensor.overview`, `overview`; `gr.riemann_tensor.definition`, `definition`.
- Add component construction, symmetries, loop graphic, and source locators later.

## GR 6.2 `gr.ricci_tensor`: Ricci tensor

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The Ricci tensor contracts the Riemann tensor and captures curvature associated
with local volume focusing. It does not contain all curvature in four
dimensions, so Ricci-flat is not synonymous with flat.

### Block Plan And Drafting Issues

- `gr.ricci_tensor.overview`, `overview`; `gr.ricci_tensor.definition`, `definition`.
- Later connect focusing carefully without pre-empting the Raychaudhuri equation.

## GR 6.3 `gr.ricci_scalar`: Ricci scalar

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The Ricci scalar is the metric trace of the Ricci tensor. It is central to the
gravitational action but is only one scalar summary; a zero Ricci scalar does
not eliminate trace-free curvature.

### Block Plan And Drafting Issues

- `gr.ricci_scalar.overview`, `overview`; `gr.ricci_scalar.definition`, `definition`.
- Add low-dimensional examples and source locators in the full pass.

## GR 6.4 `gr.einstein_tensor`: Einstein tensor

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The Einstein tensor combines Ricci curvature and its scalar trace so that its
covariant divergence vanishes. That geometric property makes it the natural
left-hand side of the field equations.

### Block Plan And Drafting Issues

- `gr.einstein_tensor.overview`, `overview`; `gr.einstein_tensor.definition`, `definition`.
- Later derive its trace and divergence with explicit dimension assumptions.

## GR 6.5 `gr.bianchi_identity`: Bianchi identity

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The differential Bianchi identity is a geometric identity of Riemann curvature.
Its contracted form gives the divergence-free Einstein tensor; it is not an
extra dynamical equation imposed on solutions.

### Block Plan And Drafting Issues

- `gr.bianchi_identity.overview`, `overview`; `gr.bianchi_identity.definition`, `definition`.
- Add the contraction steps only after index symmetries are fully taught.

## GR 6.6 `gr.curvature_invariants`: Curvature invariants

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Scalar curvature contractions provide coordinate-independent diagnostics of
geometry. Divergence can reveal genuine curvature singularities, while finite
values of a limited invariant set do not establish complete regularity.

### Block Plan And Drafting Issues

- `gr.curvature_invariants.overview`, `overview`; `gr.curvature_invariants.definition`, `definition`.
- Revisit with Schwarzschild examples after Layer 10 exists.

## GR 7.1 `gr.stress_energy_tensor`: Stress-energy tensor in GR

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Stress-energy packages local energy density, momentum density, flux, and stress
as one geometric tensor field. GR uses it as the matter source for curvature.
Its conceptual overlap with `sr.energy_momentum_tensor` remains an explicit
atlas-design question rather than being resolved during seeding.

### Block Plan And Drafting Issues

- `gr.stress_energy_tensor.overview`, `overview`; `gr.stress_energy_tensor.definition`, `definition`.
- Decide merge versus distinct scope during full authoring; add observer projections.

## GR 7.2 `gr.perfect_fluid`: Perfect fluid

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

A perfect fluid is an isotropic nondissipative matter idealization described by
rest-frame energy density, pressure, and four-velocity. The tensor formula uses
the atlas's mostly-minus signature and natural units explicitly.

### Block Plan And Drafting Issues

- `gr.perfect_fluid.overview`, `overview`; `gr.perfect_fluid.definition`, `definition`.
- Add rest-frame component decomposition and imperfect-fluid contrast later.

## GR 7.3 `gr.energy_conditions`: Energy conditions

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Energy conditions are optional inequalities on stress-energy used to formalize
particular classical reasonableness assumptions. The seed introduces null and
weak conditions and warns that they are not universal laws, especially in
quantum settings.

### Block Plan And Drafting Issues

- `gr.energy_conditions.overview`, `overview`; `gr.energy_conditions.definition`, `definition`.
- Add dominant/strong conditions and theorem-specific uses in a full pass.

## GR 7.4 `gr.covariant_conservation`: Covariant conservation

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The equation \(\nabla_\mu T^{\mu\nu}=0\) expresses local energy-momentum
balance in curved spacetime. Connection terms make the statement covariant;
the equation does not by itself define a generally conserved global
gravitational energy.

### Block Plan And Drafting Issues

- `gr.covariant_conservation.overview`, `overview`; `gr.covariant_conservation.definition`, `definition`.
- Later derive fluid equations and distinguish local from global conservation.

## GR 7.5 `gr.equation_of_state`: Equation of state

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

An equation of state supplies constitutive matter information, commonly a
relation between pressure and energy density. It closes a fluid system but is
not itself a gravitational field equation.

### Block Plan And Drafting Issues

- `gr.equation_of_state.overview`, `overview`; `gr.equation_of_state.definition`, `definition`.
- Add dust, radiation, and stellar-matter examples during application authoring.

## GR 8.1 `gr.einstein_field_equations`: Einstein field equations

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Einstein's equations equate a divergence-free curvature tensor, with an
optional cosmological term, to stress-energy with coupling
\(8\pi G/c^4\). Keeping \(c\) explicit here makes the physical dimensions of
the central equation visible.

### Block Plan And Drafting Issues

- `gr.einstein_field_equations.overview`, `overview`; `gr.einstein_field_equations.definition`, `definition`.
- Full authoring needs Newtonian-limit normalization and convention comparison.

## GR 8.2 `gr.cosmological_constant`: Cosmological constant

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The cosmological constant is a metric-proportional geometric term that permits
curved matter-free solutions. Moving it to the source side supports an
effective vacuum-energy interpretation but does not settle its microscopic
origin.

### Block Plan And Drafting Issues

- `gr.cosmological_constant.overview`, `overview`; `gr.cosmological_constant.definition`, `definition`.
- Add de Sitter examples and unit/sign translations during full authoring.

## GR 8.3 `gr.einstein_hilbert_action`: Einstein-Hilbert action

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The Einstein-Hilbert action integrates scalar curvature and the cosmological
term using the invariant volume element. Stationary metric variation produces
the gravitational field equations, subject to appropriate boundary treatment.

### Block Plan And Drafting Issues

- `gr.einstein_hilbert_action.overview`, `overview`; `gr.einstein_hilbert_action.definition`, `definition`.
- A full derivation needs the metric-variation identities and boundary term.

## GR 8.4 `gr.stress_energy_variation`: Stress-energy from action variation

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Metric variation of the matter action defines the stress-energy source in a
form reusable across matter theories. Sign and index conventions are stated as
source-dependent rather than silently universal.

### Block Plan And Drafting Issues

- `gr.stress_energy_variation.overview`, `overview`; `gr.stress_energy_variation.definition`, `definition`.
- Later work examples for scalar and electromagnetic matter actions.

## GR 8.5 `gr.trace_reversed_equations`: Trace-reversed equations

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Tracing and substituting Einstein's equation produces an equivalent Ricci-form
equation in four dimensions. The seed includes the cosmological term and makes
the stress-energy trace explicit.

### Block Plan And Drafting Issues

- `gr.trace_reversed_equations.overview`, `overview`; `gr.trace_reversed_equations.definition`, `definition`.
- Show each contraction step and dimension dependence in the full exposition.

## GR 8.6 `gr.vacuum_field_equations`: Vacuum field equations

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

For zero ordinary stress-energy and zero cosmological constant, Einstein's
equation reduces to Ricci flatness. Vacuum need not be Riemann-flat: tidal
fields, black-hole exteriors, and gravitational waves can remain.

### Block Plan And Drafting Issues

- `gr.vacuum_field_equations.overview`, `overview`; `gr.vacuum_field_equations.definition`, `definition`.
- Revisit with Schwarzschild and wave examples after Layers 10 and 11.

## GR 9.1 `gr.weak_field_metric`: Weak-field metric

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The weak-field split \(g_{\mu\nu}=\eta_{\mu\nu}+h_{\mu\nu}\) organizes small
departures from a chosen flat background. Its usefulness depends on an explicit
order count and gauge choice; the perturbation components are not individually
coordinate-invariant.

### Block Plan And Drafting Issues

- `gr.weak_field_metric.overview`, `overview`; `gr.weak_field_metric.definition`, `definition`.
- Add gauge transformations and linearized curvature during Layer 11 authoring.

## GR 9.2 `gr.newtonian_limit`: Newtonian limit

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Weak, stationary geometry and slow test motion recover Newtonian gravity. The
time-time metric component contains \(\Phi\), the geodesic equation yields
\(-\nabla\Phi\), and Einstein's equation yields Poisson's equation.

### Block Plan And Drafting Issues

- `gr.newtonian_limit.overview`, `overview`; `gr.newtonian_limit.definition`, `definition`.
- Full authoring should derive the coupling normalization with explicit units.

## GR 9.3 `gr.gravitational_redshift`: Gravitational redshift

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Stationary clocks at different potentials accumulate proper time at different
rates. Exchanged light therefore has different measured frequencies. Emitter,
receiver, time normalization, and static-spacetime assumptions must be stated.

### Block Plan And Drafting Issues

- `gr.gravitational_redshift.overview`, `overview`; `gr.gravitational_redshift.definition`, `definition`.
- Add the weak-potential expansion and operational clock experiment later.

## GR 9.4 `gr.light_deflection`: Light deflection

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Light bends because it follows null geodesics of curved spacetime, not because
it acquires rest mass. The leading isolated-mass result includes both temporal
and spatial metric curvature.

### Block Plan And Drafting Issues

- `gr.light_deflection.overview`, `overview`; `gr.light_deflection.definition`, `definition`.
- Add a controlled impact-parameter derivation and lensing distinction later.

## GR 9.5 `gr.perihelion_precession`: Perihelion precession

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Relativistic bound orbits are not exactly closed Kepler ellipses. The radial
and angular periods mismatch slightly, advancing the perihelion by a calculable
weak-field amount each revolution.

### Block Plan And Drafting Issues

- `gr.perihelion_precession.overview`, `overview`; `gr.perihelion_precession.definition`, `definition`.
- Derive from the Schwarzschild effective potential after Layer 10 matures.

## GR 9.6 `gr.post_newtonian_approximation`: Post-Newtonian approximation

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Post-Newtonian methods solve relativistic gravity order by order in weak
potential and small \(v/c\). The approximation requires declared order and
gauge bookkeeping; intermediate coordinate formulas need not look unique.

### Block Plan And Drafting Issues

- `gr.post_newtonian_approximation.overview`, `overview`; `gr.post_newtonian_approximation.definition`, `definition`.
- Add named PN orders and binary-system examples only in a full pass.

## GR 10.1 `gr.schwarzschild_metric`: Schwarzschild metric

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The Schwarzschild metric is the exact static, spherically symmetric,
asymptotically flat vacuum geometry outside a nonrotating uncharged source. The
seed states the mostly-minus line element and its exterior coordinate limits.

### Block Plan And Drafting Issues

- `gr.schwarzschild_metric.overview`, `overview`; `gr.schwarzschild_metric.definition`, `definition`.
- Full authoring needs Birkhoff's theorem, interior matching, and source locators.

## GR 10.2 `gr.schwarzschild_radius`: Schwarzschild radius

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

The scale \(r_s=2GM/c^2\) marks the Schwarzschild horizon for a black hole. It
is not automatically a material surface; ordinary bodies can be much larger
than their Schwarzschild radius.

### Block Plan And Drafting Issues

- `gr.schwarzschild_radius.overview`, `overview`; `gr.schwarzschild_radius.definition`, `definition`.
- Add numerical scales for the Sun and Earth in a full pass.

## GR 10.3 `gr.event_horizon`: Event horizon

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

An event horizon is a global causal boundary, not a material membrane or local
curvature singularity. For the extended Schwarzschild black hole it lies at
\(r_s\), where regular coordinates permit smooth infall.

### Block Plan And Drafting Issues

- `gr.event_horizon.overview`, `overview`; `gr.event_horizon.definition`, `definition`.
- Add global definition with future null infinity and a Penrose diagram later.

## GR 10.4 `gr.coordinate_singularity`: Coordinate singularity

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

A coordinate singularity is a failure of a chart rather than invariant
geometry. Schwarzschild components fail at the horizon, while regular charts
and finite curvature invariants show that the spacetime does not.

### Block Plan And Drafting Issues

- `gr.coordinate_singularity.overview`, `overview`; `gr.coordinate_singularity.definition`, `definition`.
- Demonstrate Eddington-Finkelstein coordinates in the full exposition.

## GR 10.5 `gr.black_hole_singularity`: Black hole singularity

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

At \(r=0\), Schwarzschild curvature invariants diverge. This cannot be removed
by a coordinate change and signals geodesic incompleteness and the limits of
classical GR, unlike the regular horizon.

### Block Plan And Drafting Issues

- `gr.black_hole_singularity.overview`, `overview`; `gr.black_hole_singularity.definition`, `definition`.
- Refine the distinction between scalar divergence and the modern incompleteness definition.

## GR 10.6 `gr.effective_potential_orbits`: Effective potential for orbits

### Status

`seed`: two blocks, three questions, and graph links exist.

### Scope And Exposition

Schwarzschild symmetries provide conserved energy and angular momentum, reducing
radial geodesic motion to an effective one-dimensional problem. Separate
timelike and null potentials expose turning points, circular orbits, and
stability.

### Block Plan And Drafting Issues

- `gr.effective_potential_orbits.overview`, `overview`; `gr.effective_potential_orbits.definition`, `definition`.
- Add ISCO and photon-sphere calculations with explicit normalization later.
