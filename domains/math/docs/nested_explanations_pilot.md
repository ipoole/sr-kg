# Maths nested-explanations pilot: temperature, motion and covectors

Stage 1 teaching draft, 8 November 2026; implemented in the runtime CSV during
stage 4. The draft below records the reviewed teaching argument, rather than
mirroring every later wording change. Runtime CSV remains authoritative; §7
records the actual sources and preservation decisions. See the
[working design](../../../docs/design/nested_explanations_design.md).

A [readable HTML prototype](nested_explanations_mockup.html) presents the teaching
argument with working disclosures, equations and the shared tangent-space graphic.
It remains a standalone review document; the actual viewer now uses the shared
renderer and the authored units listed in §7.

## 1. Audience, destination and scope

The root is **MATHS-1.6 Cotangent space** (`math.cotangent_space`). The learner has
encountered coordinates, differentiation and vectors, but may not see why physics
needs covectors as distinct objects. The practical question is:

> If a probe moves across the scientists' terrain, how does its direction and
> rate of motion determine the temperature change it records?

The intended conclusion is that a temperature differential is a linear rule on
tangent vectors. Its output is independent of coordinate labels, and no metric
is needed for this pairing. It is not simply another arrow or necessarily a
dimensionless number.

Use the existing two-dimensional terrain and rigid-board narrative from
`math.m01_manifolds_and_coordinates.terrain_setup`. The boards label nearby ground
points by smooth, nonsingular projections; they neither flatten the ground nor
give a metric automatically. Axes may have different scales and be oblique.

Assume a smooth **time-independent** surface temperature field and a smooth probe
route. Time is measured in seconds. The result concerns temperature changes due
to motion; a temperature field changing with time would require another term.
The pilot does not introduce curvature, a connection, transport between points,
or the metric conversion of covectors into gradient vectors.

## 2. Proposed short reading, with explanations folded

This is the actual intended reading order. The labels “statement” and “hook” are
editorial annotations here, not compulsory labels in the viewer. `▸` indicates
an explanation available in place.

This is a proposed sequence across the concept's native blocks, not a proposal
to replace the whole page with one large block. The source audit in §5 governs
where the pieces belong. Same-concept reuse is allowed: the core argument can
borrow the native dual-basis or worked-example unit rather than duplicate it.

### A direction asks a question of the temperature field

Temperature gives one number \(T(p)\) at each ground point. But a probe's next
reading depends on how it moves from that point. A direction along an isotherm
can give zero instantaneous temperature change, while another direction gives
a positive or negative rate.

At a point \(p\), the tangent vector \(v\) describes the probe's instantaneous
motion. We can describe what this vector does without choosing a grid:

**Borrowed statement — tangent vectors as directional derivatives:**

> If \(\gamma(0)=p\) and \(v=\dot\gamma(0)\), then for a smooth scalar field
> \(f\),
> \[
> v[f]\coloneqq\left.\frac{d}{dt}f(\gamma(t))\right|_{t=0}.
> \]
> It is the instantaneous change of \(f\) along the motion represented by \(v\).

**▸ How can a tangent vector measure change?** — Tangent space

For our temperature field, the differential \(dT_p\) is defined to give precisely
that readout:

\[
dT_p(v)\coloneqq v[T].
\]

At a fixed point this rule is linear in the tangent vector. A linear rule from
\(T_pM\) to the scalars is a **covector**; the space of all those rules is the
cotangent space \(T_p^*M\).

**▸ Why is the readout linear?** — local clarification

This is one important source of covectors. It does not assert that every
covector field over a region is the differential of one scalar field.

### The same readout on a board's grid

To calculate it, choose local coordinates \(x^1,x^2\). The coordinates label the
same ground points that the probe visits:

**Borrowed statement — local coordinate labels:**

> A coordinate chart assigns smooth local labels \((x^1,x^2)\) to a region of
> the surface. It changes the description of points and curves, not the points
> or the motion themselves. The labelling is one-to-one with a smooth inverse
> on the chosen patch.

**▸ What does the board's coordinate chart supply?** — Coordinate chart

The coordinate basis vectors are \(\partial_1,\partial_2\). Their dual covectors
\(dx^1,dx^2\) read the corresponding vector components:

\[
dx^a(\partial_b)\coloneqq\delta^a{}_b,
\qquad dx^a(v)=v^a.
\]

Write the temperature differential and the motion in these bases. At \(p\),

\[
\begin{aligned}
dT_p&=(\partial_aT)_p\,dx^a,\\
v&=v^a\partial_a,\\
dT_p(v)&=(\partial_aT)_p\,v^a.
\end{aligned}
\]

Here \(a\) is summed over 1 and 2. The last expression is the familiar chain-rule
temperature rate \(dT(\gamma(t))/dt\), evaluated at the point being crossed.
**▸ Algebra: where does the component sum come from?**

### A measurement the scientists can compare

Suppose the local derivatives are \(\partial_1T=2\,\mathrm{K/m}\) and
\(\partial_2T=-1\,\mathrm{K/m}\). The probe has coordinate rates
\(v^1=0.5\,\mathrm{m/s}\), \(v^2=0.2\,\mathrm{m/s}\). Its temperature rate is

\[
\begin{aligned}
dT_p(v)&=(2)(0.5)+(-1)(0.2)\\
&=0.8\,\mathrm{K/s}.
\end{aligned}
\]

The reading is warming, even though one contribution is cooling. These are
coordinate rates, not a claim that the probe's physical speed is the Euclidean
length of that component pair on an arbitrary board.

**▸ Why does a centimetre grid give the same answer?** — worked example

For intuition, think of \(dT_p\) as a linear readout attached to this point: give
it a tangent vector and it returns that vector's instantaneous temperature rate.
It is a rule acting on arrows, not another arrow requiring a dot product.

**▸ Picture the local directions on the curved ground** — shared graphic

No metric was needed to pair the differential with the motion. Asking instead
for the direction of greatest temperature increase at a fixed physical speed
would require a metric to define that speed.

## 3. Content revealed by the supporting branches

### Shared tangent explanation

Owned by Tangent space. Its native block shows its statement and this explanation
together when opened. Borrowing it inserts only the explanation behind the
disclosure; the statement above remains visible once.

> A smooth route through \(p\) supplies an instantaneous tangent vector there.
> Routes with the same first-order motion give the same directional readout
> on every smooth scalar field, even if they bend differently later. The
> temperature measurement therefore needs the tangent at the crossing, not
> the probe's whole future path.
>
> A coordinate chart makes that readout calculable using coordinate rates:
> **[the same shared local-coordinate statement from §2]**
> **▸ What does the board's coordinate chart supply?**
>
> In that chart, the ordinary chain rule gives
> \[
> v[f]=v^1\partial_1f+v^2\partial_2f,
> \qquad v^a=\frac{dx^a}{dt}.
> \]
> The chart supplies a way to calculate the readout. Changing it does not change
> the underlying motion or the scalar rate.
>
> **▸ Picture the local directions on the curved ground** — the same shared
> graphic used from the cotangent explanation.

The square-bracketed instruction means reuse the canonical statement, not maintain
a second authored copy. This gives two occurrences of the chart explanation and
two of the graphic. They are the explicit sharing tests.

### Shared coordinate explanation

Owned by Coordinate chart; the source draft can draw on its definition and terrain
example. Its statement is the one in §2. Its explanation reads:

> Each scientist chooses a patch small enough that nearby ground points can be
> mapped smoothly and uniquely to the grid on the rigid board. Those two numbers
> let the scientist write temperature as a function of coordinates and record
> the probe's track as \(x^a(t)\).
>
> The board is tangent at its reference point, not at every point in the patch.
> At another point, coordinate basis vectors follow the surface coordinate curves
> there. They are not the same fixed arrows drawn on the board. The ground can
> remain curved while its coordinates are well-defined.
>
> **▸ Why do different boards still describe one motion?**

The local nested clarification reads:

> On an overlap the scientists have a smooth conversion \(y^b=y^b(x^1,x^2)\).
> Substituting the track \(x^a(t)\) gives the same route written as \(y^b(t)\).
> Its coordinate rates change by the chain rule; no ground point or physical
> trajectory has moved merely because its labels changed.

This is enough for the pilot. It does not unfold all tensor-transformation
machinery or make a new dependency on GR or SR.

### Shared graphic

Own this with Tangent space, using its existing registered detail SVG, not a copy
of its drawing in each referring block. Proposed borrowable statement:

> Each ground point has a two-dimensional tangent space containing its possible
> instantaneous motions. The attached-plane picture is a visual aid for that
> local vector space, not a claim that the terrain is flat.

Expansion shows the existing illustration and its caption, supplemented if
necessary to distinguish a board at its reference point from tangent spaces
elsewhere. The representation in an ambient three-dimensional picture does not
make an embedding necessary for the mathematical definition.

This graphic illustrates the vectors being measured; it does not demonstrate
covector linearity or derive the pairing. Its type and local hook make that role
clear. Assess the existing asset during rendering before commissioning a new one.

## 4. Locally authored nested explanations

### Why is the readout linear?

> At a fixed point, tangent vectors act as directional-derivative operators.
> Their linear combinations act on a scalar function by
> \[
> (a v+b w)[T]=a\,v[T]+b\,w[T].
> \]
> Consequently \(dT_p(a v+b w)=a\,dT_p(v)+b\,dT_p(w)\), the required covector
> linearity. The scalars \(a,b\) here are numerical weights. This is linearity
> in the tangent vector at \(p\); temperature need not be a linear function
> throughout the patch.
>
> **▸ Why is linearity at one point enough?**
>
> A differential retains the first-order part of a smooth function at that
> point. Higher-order terms can matter over a finite journey without changing
> the linearity of this local first-order readout. Different points generally
> have different differentials.

The final paragraph belongs inside the deeper disclosure, not as visible text
outside it. This tests local nesting without another shared source.

### Algebra: where does the component sum come from?

> Apply the covector to the vector, using linearity and the dual-basis rule:
> \[
> \begin{aligned}
> dT_p(v)&=(\partial_aT)_p\,dx^a(v^b\partial_b)\\
> &=(\partial_aT)_p\,v^b\delta^a{}_b\\
> &=(\partial_aT)_p\,v^a.
> \end{aligned}
> \]
> The Kronecker delta selects matching components. No inner product or metric
> has entered the calculation.

### Why does a centimetre grid give the same answer?

> Relabel both coordinate axes from metres to centimetres. The numerical
> coordinate labels become 100 times larger, and the probe's component rates
> become \(50\) and \(20\,\mathrm{cm/s}\). The corresponding temperature
> derivatives become \(0.02\) and \(-0.01\,\mathrm{K/cm}\). Hence
> \[
> (0.02)(50)+(-0.01)(20)=0.8\,\mathrm{K/s}.
> \]
> The numerical changes compensate because the two descriptions concern the
> same motion through the same temperature field. The result has units K/s;
> coordinate independence does not mean dimensionlessness.

For this example the instantaneous rate is exact under the stated assumptions.
Using it to estimate a finite journey's temperature change would be an
approximation unless the rate stayed constant.

## 5. Ownership and editorial audit

| Proposed piece | Existing source | Stage-4 treatment |
| --- | --- | --- |
| Root readout argument | `math.cotangent_space.gradient_example`, `.terrain_survey` | Integrate the short argument and references, retaining existing identities where possible |
| Linear rule | `math.cotangent_space.definition`, `.readout` | Keep native definition and intuition directly readable; avoid duplicating their explanation as new parallel prose |
| Dual basis and pairing algebra | `math.cotangent_space.basis` | Preserve its ID; add useful local algebra and the chart reference |
| Physical units and grid calculation | `math.cotangent_space.units`, `.units_example` | Reconcile this rate example with the existing displacement example; do not blur K with K/s |
| Tangent directional readout | `math.tangent_space.directional_derivative`, `.curves`, `.components` | Identify one coherent reusable explanation and chart use; keep the coordinate-independent statement intact |
| Local coordinate labels | `math.coordinate_chart.definition`, `.terrain_survey` | Separate a canonical statement and coherent explanation; reconcile the smooth-chart definition with the existing module assumptions |
| Shared illustration | Tangent space graphic registry and caption | Wrap the existing asset in one borrowable Graphic unit; stable addressing decided in stage 2 |
| Physical and metric limits | `math.cotangent_space.metric_warning`, `.level_curve_example` | Keep the warning visible where relevant; preserve the independent source blocks |

The table identifies editorial owners, not a migration instruction to merge or
delete these blocks. Existing IDs have attached notes/read marks; splitting or
restructuring them needs an explicit preservation plan before runtime edits.
Questions and their IDs remain unchanged for the initial authoring pass.

No changes to tensor-calculus content, SR/GR files, concept numbering, module
membership, authored layouts or concept edges are required for stage 1.

## 6. Review walk-through

1. Read only the initial argument. Explain why \(dT_p\) is a covector and why the
   result is a rate in K/s. Identify the borrowed mathematics.
2. Open the tangent explanation, then its chart explanation and deeper board
   clarification. Close tangent and return to the root's component calculation.
3. Open the chart explanation from the root. It has the same source text but its
   own fold state; the deeper clarification is not forced open by the first use.
4. Open the tangent graphic through each branch. Confirm one authored source and
   independent presentation, with no navigation to another concept.
5. Read local linearity and algebra explanations, then the centimetre calculation.
   Close them and check that the short argument remains coherent.
6. Repeat in Details-only view at phone width. No hover, graph or memorised
   return path should be necessary to understand what is being investigated.

The graph may continue to show the selected cotangent concept and its ordinary
context. Opening the chart explanation must not add an edge or change the graph
settings. Coordinate charts are needed by this coordinate calculation, not by
every possible definition of tangent or cotangent space.

## 7. Stage-4 implementation and preservation record

The three main headings are **three existing native blocks**, ordered immediately
after the Cotangent space overview. Their sequence is:

| Reading purpose | Canonical block ID | Change |
| --- | --- | --- |
| A direction asks a temperature question | `math.cotangent_space.gradient_example` | Temperature differential, borrowed tangent result, local linearity and a deeper first-order clarification |
| The readout on a board's grid | `math.cotangent_space.basis` | Borrowed chart result, dual basis, component pairing and local algebra |
| A measurement scientists can compare | `math.cotangent_space.terrain_survey` | Worked velocity/temperature calculation, centimetre relabelling, shared illustration and metric caveat |

Four supporting sources have short statements:

- `math.tangent_space.directional_derivative`: the curve-based scalar rate;
- `math.coordinate_chart.terrain_survey`: smooth local board labels;
- `math.tangent_space.graphic`: the existing registered tangent-space illustration;
- `math.m01_manifolds_and_coordinates.terrain_setup`: the existing module story,
  optionally borrowed from the Cotangent space overview.

The chart's **terrain example**, rather than its general definition, is the
shared chart source. This keeps the board-specific explanation with its existing
owner and leaves the general chart definition separate. The statement describes
the labels briefly; projection, changing tangent planes and overlap conversion
belong in its explanation. The tangent source uses that same source and the same
Graphic unit as the root argument: neither is a copied paragraph/drawing.

The graphic wrapper is the only new block, `math.tangent_space.graphic`. It
replaces that concept's implicit graphic presentation and retains the registered
SVG, icon and caption unchanged. Native and borrowed occurrences use the same
asset. This illustration supplies geometric intuition, not a proof of covector
linearity.

### Identities and personal data

Every previous block ID and owner is retained. No block is deleted, merged or
moved to a different concept/module. Six existing bodies are revised: the chart
terrain example, tangent directional derivative, and the Cotangent overview and
three main argument blocks. Other existing bodies, including the covector
definition, general readout, displacement example and dimensionless algebraic
calculation, remain unchanged. Cotangent sequences are reordered; the numerical
terrain calculation now has kind `worked_example`.

The existing metre/centimetre **displacement** example remains distinct from the
new velocity calculation: the former predicts kelvin to first order; the latter
gives an instantaneous rate in kelvin per second. The new rate is 0.8 K/s on both
grids. Coordinate rates are not presented as physical speed on an arbitrary grid.

Stable native IDs preserve existing read/question records and block note targets.
Paragraph notes in revised prose use the existing contextual recovery rules;
records which cannot be matched remain stored under Notes needing placement.
There is no new personal-data migration or forced retargeting of records.
Unchanged-block notes and legacy graphic notes/read marks are exercised against
the real Maths build in the browser tests. The new Graphic block has its own read
mark, so full completion of Tangent space now includes this new unit.

Concept IDs/numbering, module membership, layouts, edges, questions/options and
registered graphic metadata/creators remain unchanged. Maths-2 content has no
semantic changes; its rows merely receive empty optional columns in the shared
Maths CSV. SR and GR files are untouched.

### Sources and checks

Tong's *General Relativity*, §2.2.1 and §2.3.1, support the tangent/covector
framework already registered for those concepts. The chart now also cites
§2.1.2. The [official HTML chapter](https://www.davidtong.org/teaching/general-relativity/grhtml/S2)
was checked on 8 November 2026. The soil-survey narrative, units examples and
numerical choices are original PhysicsKG teaching material.

Build both `output/PhysicsKG.html` and `output/PhysicsKG_math.html` through the
project environment. The latter loads only Maths; its missing-SR diagnostics
come from unchanged worldline/coordinate-transform content, not this pilot.
Structural tests check source sharing, short statements, local depth and reading
order. Real-Maths browser checks exercise both branches, equations, reused SVGs,
phone width and unchanged personal/graph state. Broader reader review and hosted
preview publication remain stages 5–6.

## MATHS-1 extension

The remaining concepts now participate in shared reading paths: manifold structure,
chart/inverse, coordinate transitions and Jacobians, and curves versus coordinate
plots. Existing IDs, question records, module membership and graph edges remain
unchanged. Tangent-vector construction borrows the probe route and Jacobian;
worldline tangents borrow that construction. These dependencies terminate in
local explanations rather than a prerequisite cycle. Maths-2 is unchanged.

Statements remain short and are blue during this experiment. Borrowed source
headings now expose the native read status and let readers update it in place.
A read mark covers that canonical block, not all its borrowed prerequisites.
Local algebra has no independent progress record. Notes remain native-only.

Sources: Tong's official differential-geometry chapter, §§2.1.2 and 2.2.1,
checked again for this pass. The terrain narrative and calculations are original.
Phone/desktop tests traverse every MATHS-1 route, check maths and overflow, and
exercise borrowed/native progress, persistence and module-source identity.
