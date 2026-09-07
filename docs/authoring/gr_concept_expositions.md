# GR and Mathematics Concept Expositions

This file holds readable draft expositions for General Relativity and reusable
mathematics concepts before or alongside their split into `data/content_blocks.csv`.

The CSV content blocks remain the source consumed by the application. This file
is an authoring and review aid: it preserves the coherent book-section form if
block boundaries, block kinds, or viewer presentation rules change later.

Use one section per concept, labelled with semantic ID and title.
These are working drafts, not a second publication to synchronise with CSV.
Look up current display IDs and module membership in the runtime data.
Keep concepts in domain-local atlas order where practical. Use
`docs/authoring/general_relativity_concept_plan.md` for the broader GR atlas
plan and `docs/authoring/gr_drafting_issues.md` for cross-cutting unresolved
questions.

## Template

Use this structure when starting a new GR or maths concept:

```markdown
## `concept.id`: Concept title

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

## `math.manifold`: Manifold

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

## `math.coordinate_chart`: Coordinate chart

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

- Keep coordinate transformations in `math.coordinate_transformation`; avoid
  overloading this entry.

## `math.coordinate_transformation`: Coordinate transformation

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

## `math.worldline`: Worldline

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

## `math.tangent_space`: Tangent space

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

- Review shared visual motifs with `math.cotangent_space` and
  `math.tensor_field`.

## `math.cotangent_space`: Cotangent space

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

## `math.tensor_field`: Tensor field

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

## `math.index_notation`: Abstract and component indices

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

## `math.tensor_transformation_law`: Tensor transformation law

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

## Completed GR Authoring

The 55 existing GR concepts across GR-1 through GR-6 have completed full
content, question, source and graphic review. Their runtime CSV is authoritative;
completed drafts have been retired rather than maintained as duplicate text.
Current membership and status are recorded in `module_members.csv` and `nodes.csv`.

The [notation glossary](notation_glossary.md#general-relativity) records the
shared signature, curvature, action, matter and orbital conventions. The SR and
GR metric and stress-energy concepts remain separate and linked by `RELATED`.

The mathematics drafts above retain their prerequisite-support scope. Further
GR scope is recorded in the [concept plan](general_relativity_concept_plan.md),
with remaining work in [GR drafting issues](gr_drafting_issues.md).
