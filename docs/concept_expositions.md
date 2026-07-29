# Concept Expositions

This file holds readable draft expositions before or alongside their split into
`data/content_blocks.csv`.

The CSV content blocks remain the source consumed by the application. This file
is an authoring and review aid: it preserves the coherent book-section form if
block boundaries, block kinds, or viewer presentation rules change later.

Use one section per concept, labelled with display ID, semantic ID, and title.
Keep concepts in atlas order where practical.

## 1.1 `sr.inertial_frames`: Inertial frames

### Scope

This concept introduces inertial frames as the clean reference frames used by
special relativity. It should explain what a frame supplies, how inertial frames
are recognized by free-particle motion, and why acceleration is different from
uniform relative motion. It should not derive Lorentz transformations, develop
spacetime geometry, or treat non-inertial observers in detail.

### Exposition

An inertial frame is a reference frame in which a free particle moves in a
straight line at constant velocity. In one spatial dimension this means that,
when no net force acts,

\[
x(t)=x_0+vt,
\]

with constant \(v\). In three spatial dimensions the same idea is
\(\mathbf x(t)=\mathbf x_0+\mathbf v t\). The important word is "free": if a
particle is pushed, pulled, or constrained, its acceleration tells us about the
interaction. The inertial-frame test concerns what happens when those
interactions are absent.

A reference frame is more than a viewpoint. It is a rule for assigning space
and time coordinates to events: a spatial coordinate grid, a clock convention,
and an agreed way to label where and when something happens. A laboratory fixed
to Earth, a smoothly moving train, and a coasting spacecraft can each be treated
as frames over some range of accuracy. Calling such a frame inertial means that
the frame itself is not accelerating or rotating in a way that would introduce
fictitious forces into the description of free motion.

This is an idealization, but it is a useful and controlled one. No real
laboratory is perfectly isolated from gravity, vibration, or rotation. A train
is only approximately inertial while it moves smoothly along a straight track; a
train braking or rounding a bend is not. A spacecraft far from large masses,
coasting without thrust, is a better approximation. Physics often begins with
ideal cases like this because they expose the basic structure before corrections
are added.

Inertial frames are central to special relativity because the theory first
compares descriptions made by these clean observers. The
\cref{Principle of relativity}{sr.principle_of_relativity} says that the laws
of physics have the same form in every inertial frame. The
\cref{Constancy of the speed of light}{sr.constancy_of_speed_of_light} adds
that every inertial observer measures the same vacuum light speed \(c\). Those
two statements become powerful only after we have identified the class of
frames to which they apply.

Uniform relative motion does not make one inertial frame more real than
another. If two laboratories coast past one another at constant relative
velocity, each may regard itself as at rest and the other as moving. That
disagreement is a coordinate choice, not a physical defect. Acceleration is
different: an accelerometer, a pendulum, or the apparent curvature of free
particle tracks can reveal acceleration locally. This is why special relativity
does not begin by saying that every observer is equivalent in the same simple
way. It begins with inertial frames.

The distinction also prevents a common mistake. "Frame-dependent" does not mean
"arbitrary" or "unphysical". Velocities, electric and magnetic field components,
and coordinate times can depend on the inertial frame used to describe them.
The physical laws relating those quantities must still fit together
consistently across inertial frames. Later concepts such as
\cref{Lorentz transformations}{sr.lorentz_transformations},
\cref{Spacetime events}{sr.spacetime_event}, and the
\cref{Electric field}{sr.electric_field} all rely on this idea: quantities are
reported in a frame, while the theory tells us how different inertial-frame
reports are related.

### Block Plan

- `sr.inertial_frames.definition`, `definition`, "Definition".
- `sr.inertial_frames.reference_frame`, `explanation`, "What a frame supplies".
- `sr.inertial_frames.free_motion`, `explanation`, "Free motion as the test".
- `sr.inertial_frames.idealization`, `explanation`, "Approximation and acceleration".
- `sr.inertial_frames.relativistic_role`, `explanation`, "Why inertial frames matter".
- `sr.inertial_frames.frame_dependent`, `explanation`, "Frame-dependent is not arbitrary".

The current split keeps all live blocks as `definition` or `explanation` for a
conservative first pass. Later revisions can promote suitable paragraphs to
more specific kinds such as `intuition`, `example`, or `warning`.

### Study Questions

Drafted in `data/study_questions.csv` as five questions: two
multiple-choice/short conceptual checks, one observer/frame distinction, and
two short calculation/manipulation checks.

### Graphics

Retain the existing graphic idea. A coordinate frame with a straight,
equally-spaced free-particle track is exactly the right visual test for this
concept. No SVG code change is needed in this pass.

### Drafting Issues

- Consider whether the idealization/acceleration paragraph should become a
  `warning` or `intuition` block once we have reviewed the block-kind policy on
  a few more concepts.
- The reference link uses a broad `TTM II, Ch. 1` locator for now. Tighten this
  to a specific section/page when the source text is checked directly.

## 1.2 `sr.constancy_of_speed_of_light`: Constancy of the speed of light

### Scope

This concept introduces the invariant vacuum speed of light as a postulate of
special relativity. It should explain what is being claimed, why the claim
conflicts with Galilean velocity addition, and why the word "vacuum" matters.
It should not derive Lorentz transformations, introduce the spacetime interval
in detail, or treat electromagnetic waves beyond the minimal light-pulse
picture.

### Exposition

The constancy of the speed of light is the postulate that light in vacuum is
measured to travel at the same speed \(c\) by every
\cref{Inertial frame}{sr.inertial_frames}, independent of the motion of the
source or the observer. In SI units \(c=299\,792\,458\,\mathrm{m\,s^{-1}}\)
exactly, because the metre is defined using this speed.

The claim is not merely that light is very fast. The radical statement is that
different inertial observers, moving uniformly relative to one another, still
measure the same vacuum light speed. If one observer chases an ordinary
projectile, Galilean intuition says the projectile's speed relative to that
observer should be reduced. If the projectile is replaced by a vacuum light
pulse, special relativity says the measured speed is still \(c\).

A useful picture is a flash emitted from one event. In an inertial frame, after
time \(t\), the lightfront has radius \(ct\). In one-space-one-time language,
light rays satisfy

\[
x=\pm ct.
\]

The postulate says that any other inertial observer, using their own coordinates
for the same lightfront, also describes the rays as moving at speed \(c\). This
is already a hint that time and space coordinates cannot transform in the old
Galilean way.

The vacuum qualification matters. Light can travel more slowly in glass, water,
or other material media, and the measured speed in a medium can depend on the
state of that medium. The invariant speed \(c\) is the speed of light in vacuum
and, more deeply, the limiting speed built into the spacetime structure of
special relativity.

Historically, this postulate sits against the background of ether theories and
the Michelson-Morley experiment of 1887. Michelson and Morley failed to detect
the expected motion of Earth through a luminiferous ether. That null result did
not by itself prove special relativity, but it sharpened the problem: Maxwell's
electrodynamics seemed to contain a fixed light speed, while Galilean kinematics
made speeds depend on the observer. Einstein's 1905 move was to treat the vacuum
speed of light as a postulate for all inertial observers, rather than as a speed
measured only in the ether rest frame.

Together with the \cref{Principle of relativity}{sr.principle_of_relativity},
the constancy of \(c\) strongly constrains how inertial-frame coordinates can be
related. The result is not a small correction to Galilean transformations but
their replacement by \cref{Lorentz transformations}{sr.lorentz_transformations}.
The later mathematics is built to preserve the statement that lightlike motion
has the same speed in every inertial frame.

### Block Plan

- `sr.constancy_of_speed_of_light.definition`, `definition`, "Definition".
- `sr.constancy_of_speed_of_light.not_merely_fast`, `misconception`, "Not merely very fast".
- `sr.constancy_of_speed_of_light.galilean_conflict`, `explanation`, "Conflict with Galilean velocity addition".
- `sr.constancy_of_speed_of_light.wavefront_picture`, `intuition`, "Lightfront picture".
- `sr.constancy_of_speed_of_light.vacuum_warning`, `warning`, "Vacuum, not material media".
- `sr.constancy_of_speed_of_light.historical_context`, `historical_note`, "Einstein and the ether experiments".
- `sr.constancy_of_speed_of_light.relativistic_role`, `explanation`, "Role in special relativity".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: conceptual invariant
speed checks, one vacuum/media distinction, one light-travel calculation, and
one Galilean-contrast manipulation.

### Graphics

Retain the existing graphic. The central flash with concentric wavefronts and
repeated \(c\) labels is the right icon-scale visual for invariant light speed.
No SVG code change is needed in this pass.

### Drafting Issues

- The reference link uses a broad `TTM II, Ch. 1` locator for now. Tighten this
  to a specific section/page when the source text is checked directly.

## 1.3 `sr.principle_of_relativity`: Principle of relativity

### Scope

This concept introduces the principle that the laws of physics have the same
form in all inertial frames. It should emphasize no preferred inertial rest
frame, the distinction between laws and coordinate values, and the connection
to Lorentz invariance. It should not repeat the full definition of inertial
frames, derive Lorentz transformations, or discuss general covariance.

### Exposition

The principle of relativity says that the laws of physics have the same form in
all \cref{Inertial frames}{sr.inertial_frames}. No inertial frame is physically
privileged as the true state of rest. If two laboratories coast past one another
at constant relative velocity, either laboratory can describe itself as at rest
and the other as moving.

The principle is about laws, not about all measured numbers being identical.
Two inertial observers may assign different positions, times, velocities,
energies, electric fields, or magnetic fields to the same physical situation.
What must survive is the form of the rule connecting the measured quantities.
A valid law cannot require one inertial frame to be the secretly correct frame.

The standard intuition is the sealed, smoothly moving laboratory. If a train
moves uniformly along a straight track, experiments performed entirely inside
the sealed carriage do not reveal a special state of uniform motion. Balls,
springs, clocks, and light pulses obey the same laws as they would in another
smoothly moving inertial laboratory. The train may be moving relative to the
station, but uniform relative motion is not an intrinsic physical defect.

The relativity principle has older roots than special relativity. Galileo's
ship argument already captured the idea that uniform motion cannot be detected
by experiments confined to the moving system. Einstein's 1905 step was to apply
this principle without exception to mechanics and electrodynamics together,
pairing it with the invariant vacuum speed of light. That pairing forced a new
transformation law between inertial frames.

Historically, this idea extends the relativity already present in Newtonian
mechanics. What changes in special relativity is the transformation rule
between inertial frames. The \cref{Constancy of the speed of light}{sr.constancy_of_speed_of_light}
cannot be reconciled with Galilean transformations, so the same relativity
principle leads to a different spacetime geometry.

In modern language, the principle points toward
\cref{Lorentz invariance}{sr.lorentz_invariance}. Equations should be written so
that changing inertial frames changes components and coordinates but not the
physical content of the law. \cref{Lorentz transformations}{sr.lorentz_transformations}
are the coordinate transformations that make this possible in special
relativity.

### Block Plan

- `sr.principle_of_relativity.definition`, `definition`, "Definition".
- `sr.principle_of_relativity.no_preferred_frame`, `explanation`, "No preferred inertial frame".
- `sr.principle_of_relativity.same_laws_not_same_numbers`, `misconception`, "Same laws, not same numbers".
- `sr.principle_of_relativity.sealed_lab`, `intuition`, "Sealed laboratory intuition".
- `sr.principle_of_relativity.historical_context`, `historical_note`, "From Galileo to Einstein".
- `sr.principle_of_relativity.galilean_to_lorentz`, `explanation`, "From Galilean to Lorentz transformations".
- `sr.principle_of_relativity.lorentz_invariance`, `explanation`, "Modern invariant form".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: no-preferred-frame
checks, sealed-lab intuition, same-law versus same-number distinctions, and one
short Galilean-invariance manipulation.

### Graphics

Retain the existing graphic. Two equal inertial frames with matching internal
experiments and a relative-velocity arrow communicate the principle directly:
neither frame is drawn as privileged. No SVG code change is needed in this pass.

### Drafting Issues

- The reference link uses a broad `TTM II, Ch. 1` locator for now. Tighten this
  to a specific section/page when the source text is checked directly.
- The relationship between this concept and `sr.lorentz_invariance` may deserve
  a sharper edge type than `RELATED` later.

## 2.2 `sr.spacetime_event`: Spacetime event

### Scope

This concept introduces a spacetime event as one localized occurrence with
coordinates assigned by an inertial frame. It should explain the distinction
between the event and its coordinate labels, why \(ct\) is often used, and why
events become the basic units for later spacetime geometry. It should not
derive Lorentz transformations, define the spacetime interval in detail, or
develop worldlines and Minkowski diagrams beyond brief forward links.

### Exposition

A spacetime event is a single occurrence at a definite place and time. In an
\cref{Inertial frame}{sr.inertial_frames}, it is labelled by spacetime
coordinates such as \((ct,x,y,z)\) or \((t,x,y,z)\), depending on convention.
A detector click, a spark, or the emission of a light pulse can be an event.
The important idea is that the occurrence is localized: it is one where-and-when.

The event is the occurrence itself; the coordinates are labels assigned by a
chosen frame. Two inertial observers may assign different coordinate times and
positions to the same physical event. That does not mean they are talking about
different events. It means that their coordinate grids and clock conventions
slice and label spacetime differently.

An event is deliberately pointlike in spacetime. A bulb flashing at one place
and one time is an event; the whole journey of the bulb is not. A journey,
orbit, wave pulse, or experiment is built from many events arranged into an
extended history. This distinction is useful because it prevents us from mixing
up a single occurrence with a process that occupies a region of spacetime.

It is often useful to multiply time by \(c\) and write the time coordinate as
\(ct\). Then time and space coordinates have the same unit of length, so a
one-dimensional spacetime event can be plotted as \((ct,x)\). This is a
bookkeeping choice, not a claim that time is the same kind of thing as space.
It prepares the notation for spacetime diagrams and invariant intervals.

The frame dependence of coordinates is not a defect. It is like using different
grid systems for the same point, except that in relativity the time label also
changes between inertial frames. A coordinate value is frame-dependent; the
event being labelled is not. Later, \cref{Lorentz transformations}{sr.lorentz_transformations}
will describe how the labels change from one inertial frame to another.

Spacetime events are the basic objects related by later constructions. The
\cref{Spacetime interval}{sr.spacetime_interval} measures separation between
pairs of events, a \cref{Minkowski diagram}{sr.minkowski_diagram} plots events
on spacetime axes, and the \cref{Position four-vector}{sr.position_four_vector}
packages an event's coordinates into a relativistic vector.

### Block Plan

- `sr.spacetime_event.definition`, `definition`, "Definition".
- `sr.spacetime_event.coordinate_label`, `explanation`, "Coordinates label the event".
- `sr.spacetime_event.not_a_process`, `warning`, "Event, not process".
- `sr.spacetime_event.ct_coordinate`, `explanation`, "Using \(ct\) as a time coordinate".
- `sr.spacetime_event.frame_dependence`, `misconception`, "Frame-dependent is not unreal".
- `sr.spacetime_event.role_in_spacetime`, `explanation`, "Atoms of spacetime reasoning".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: one event-versus-process
multiple choice check, two short conceptual checks, one \(ct\) coordinate
calculation, and one link forward to the spacetime interval.

### Graphics

Retain the existing graphic. A single highlighted event \(P\) on \(x,ct\) axes
with coordinate projections is the right visual for the concept. No SVG code
change is needed in this pass.

### Drafting Issues

- The reference link uses a broad `TTM II, Ch. 1` locator for now. Tighten this
  to a specific section/page when the source text is checked directly.
- There is no current 2.1 concept in the atlas. We should decide later whether
  the numbering gap should be filled or the layer renumbered.

## 2.3 `sr.principle_of_locality`: Principle of locality

### Scope

This concept introduces locality as the rule that physical laws relate
quantities at the same spacetime event, or infinitesimally nearby events,
rather than allowing instantaneous action at a distance. It should explain why
field language fits locality, how finite propagation enters special relativity,
and what locality does not mean. It should not derive Maxwell's equations,
construct field Lagrangians, or treat quantum nonlocality.

### Exposition

The principle of locality states that physical laws relate quantities at the
same \cref{Spacetime event}{sr.spacetime_event}, or infinitesimally nearby
events, rather than allowing instantaneous action at a distance. A local law
does not ask what a distant charge or field is doing right now far away. It uses
the information available at the event under consideration and in its immediate
neighbourhood.

This is a point-by-point idea. At one event, a law may involve field values,
sources, and derivatives evaluated there. A derivative is still local because it
describes how the field changes in an infinitesimal neighbourhood of the event.
The law is not a rule that reaches across the universe in one step.

Fields fit locality naturally because a field assigns values to spacetime
events. A field equation can say how the value and nearby changes of a field at
one event relate to sources at that same event. Disturbances then propagate from
event to neighbouring event. This is the field-theory alternative to imagining
one object directly tugging on another object far away.

Locality does not say that distant objects can never influence one another. It
says the influence is mediated through intermediate events and cannot be an
instantaneous command from here to there. If a charge is shaken and another
charge later responds, locality asks for the field disturbance that carried the
influence between them.

In special relativity, the
\cref{Constancy of the speed of light}{sr.constancy_of_speed_of_light} gives a
limiting causal speed. A local relativistic theory should allow disturbances to
spread through spacetime at finite speed, with electromagnetic waves as the
central example. The effect at a distant event can occur only after a signal has
had time to get there.

Historically, classical mechanics often tolerated action-at-a-distance language,
especially in Newtonian gravity. Nineteenth-century field theory, developed
through Faraday and Maxwell, changed the picture: electromagnetic influence was
carried by fields spread through space and time. Special relativity made this
local field viewpoint feel necessary rather than optional, because
instantaneous influence would select a preferred notion of simultaneity.

Locality is the organizing idea behind later field concepts.
\cref{Field equations}{sr.field_equations} are local differential rules, a
\cref{Field Lagrangian}{sr.field_lagrangian} is built from fields and
derivatives at the same event, and \cref{Charge conservation}{sr.charge_conservation}
becomes local bookkeeping rather than just a statement about the total charge
of the universe.

### Block Plan

- `sr.principle_of_locality.definition`, `definition`, "Definition".
- `sr.principle_of_locality.local_neighbourhood`, `explanation`, "Same event or immediate neighbourhood".
- `sr.principle_of_locality.fields_fit_locality`, `explanation`, "Why fields fit locality".
- `sr.principle_of_locality.not_no_distant_effects`, `misconception`, "Not no distant effects".
- `sr.principle_of_locality.finite_propagation`, `explanation`, "Finite propagation in relativity".
- `sr.principle_of_locality.historical_context`, `historical_note`, "From action at a distance to fields".
- `sr.principle_of_locality.role_in_field_theory`, `explanation`, "Role in field theory".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: one multiple-choice
recognition check, locality-at-an-event and field-language short answers, one
finite-propagation calculation, and one misconception correction.

### Graphics

Retain the existing graphic. The central event inside a small dashed
neighbourhood, with only short arrows ending locally, directly expresses the
concept. No SVG code change is needed in this pass.

### Drafting Issues

- The reference link intentionally has no precise locator yet. Add a specific
  TTM or other source locator during source review.
- We may eventually want a sharper atlas edge type for "motivates field
  description" or "enforces finite propagation"; for now the current
  `PREREQUISITE` and `RELATED` links are adequate.

## 3.1 `sr.metric_tensor`: Metric tensor

### Scope

This concept introduces the Minkowski metric as the spacetime measuring rule in
flat spacetime. It should explain the \(+---\) convention, how contractions
produce invariant intervals and scalar products, and why the signs matter. It
should not teach general tensor calculus, develop curved spacetime, or derive
Lorentz transformations in full.

### Exposition

The metric tensor is the measuring rule for spacetime. It tells us how to
combine time and space components so that the result has invariant meaning,
especially when computing the \cref{Spacetime interval}{sr.spacetime_interval}
and scalar products of \cref{Four-vectors}{sr.four_vectors}. In ordinary
Euclidean geometry the measuring rule adds squared components with the same
sign. Minkowski spacetime uses a different rule.

With the \(+---\) convention used here, the flat spacetime metric is

\[
\eta_{\mu\nu}=\mathrm{diag}(1,-1,-1,-1).
\]

The first entry belongs to the time component, written as \(ct\) when all four
coordinates are measured in units of length. The three negative entries belong
to the spatial components. These signs are not decoration. They are what make
spacetime geometry different from four-dimensional Euclidean geometry.

For a displacement

\[
\Delta x^\mu=(c\Delta t,\Delta x,\Delta y,\Delta z),
\]

the metric gives

\[
\Delta s^2=\eta_{\mu\nu}\Delta x^\mu\Delta x^\nu
          =c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2.
\]

This is the invariant interval between the two events. The repeated indices
mean that we sum over the four components. In the standard inertial coordinates
used for special relativity the metric is diagonal, so there are no cross terms
such as \(dt\,dx\).

The same metric lowers indices. If \(A^\mu=(A^0,A^1,A^2,A^3)\), then

\[
A_\mu=\eta_{\mu\nu}A^\nu=(A^0,-A^1,-A^2,-A^3)
\]

in the \(+---\) convention. This is why the scalar product is written

\[
A_\mu A^\mu=(A^0)^2-(A^1)^2-(A^2)^2-(A^3)^2.
\]

Lowering an index is not just typographical tidying; it applies the metric
measuring rule.

A common mistake is to treat the metric as if it were the Euclidean dot product
with time added as a fourth coordinate. The Minkowski metric deliberately is not
positive in every direction. A nonzero displacement can have positive, zero, or
negative interval square. Those cases become the timelike, lightlike, and
spacelike classifications developed in the
\cref{Spacetime interval}{sr.spacetime_interval} and
\cref{Light cone}{sr.light_cone} concepts.

The \cref{Lorentz transformations}{sr.lorentz_transformations} are exactly the
inertial-frame transformations that preserve this metric structure. In matrix
notation the condition is

\[
\Lambda^T\eta\Lambda=\eta.
\]

This equation means that although the components of a vector change between
inertial frames, contractions made with \(\eta\) have the same value.

In special relativity the metric can be written as the fixed matrix
\(\eta_{\mu\nu}\) in standard inertial coordinates. In general relativity the
metric becomes \(g_{\mu\nu}(x)\), a spacetime-dependent measuring rule. That
later development does not change the basic lesson introduced here: the metric
is the object that tells geometry how to measure intervals and scalar products.

### Block Plan

- `sr.metric_tensor.overview`, `overview`, "What the metric does".
- `sr.metric_tensor.definition`, `definition`, "Definition".
- `sr.metric_tensor.signs_matter`, `explanation`, "The signs do the work".
- `sr.metric_tensor.interval_contraction`, `derivation`, "Reading the metric from the interval".
- `sr.metric_tensor.lowering_indices`, `construction`, "Lowering an index".
- `sr.metric_tensor.not_euclidean`, `misconception`, "Not an ordinary ruler".
- `sr.metric_tensor.lorentz_preservation`, `explanation`, "Preserved by Lorentz transformations".
- `sr.metric_tensor.gr_bridge`, `historical_note`, "From Minkowski to curved spacetime".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: one convention check,
one role-of-metric explanation, two short calculations, and one Euclidean
misconception correction.

### References

Linked broadly to `TTM II` for the flat Minkowski metric convention and to `TRR`
for the metric-as-geometry bridge. Precise locators should be added during
source review.

### Graphics

Revised the existing graphic. The new version keeps the matrix idea but makes
the metric visibly act as a measuring rule: a displacement on \(x,ct\) axes is
fed through \(\eta\) to produce an \(s^2\) interval expression.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- No new schema issue beyond using the newly allowed `overview` kind.

#### Atlas Issues

- Later GR work should decide whether the `gr.metric_tensor` concept is a
  separate concept linked from this one, rather than letting this SR concept
  carry curved-spacetime detail.

## 3.2 `sr.spacetime_interval`: Spacetime interval

### Scope

This concept introduces the spacetime interval as the invariant separation
between two events. It should explain how the interval is built from coordinate
differences and the metric, why its sign classifies separations, and why
invariance does not mean unchanged coordinate components. It should not derive
Lorentz transformations in full or develop proper time and light cones beyond
forward links.

### Exposition

The spacetime interval is the quantity all inertial observers agree on when
comparing two \cref{Spacetime events}{sr.spacetime_event}. Observers may
disagree about the coordinate time and coordinate distance between the events,
but they agree on the metric combination that defines the interval.

With the \(+---\) convention, the interval between two events is

\[
\Delta s^2=c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2.
\]

Equivalently, using the \cref{Metric tensor}{sr.metric_tensor},

\[
\Delta s^2=\eta_{\mu\nu}\Delta x^\mu\Delta x^\nu.
\]

The interval is built from a separation, not from one event in isolation. If
two events have coordinates \(x_1^\mu\) and \(x_2^\mu\), form

\[
\Delta x^\mu=x_2^\mu-x_1^\mu.
\]

This removes the arbitrary choice of coordinate origin and leaves the
displacement whose invariant square is measured.

Contracting the separation with the metric gives the usual interval formula.
For

\[
\Delta x^\mu=(c\Delta t,\Delta x,\Delta y,\Delta z)
\]

and \(\eta_{\mu\nu}=\mathrm{diag}(1,-1,-1,-1)\), the contraction
\(\eta_{\mu\nu}\Delta x^\mu\Delta x^\nu\) expands to

\[
\Delta s^2=c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2.
\]

The sign of \(\Delta s^2\) classifies the separation. With the convention used
here, \(\Delta s^2>0\) is timelike, \(\Delta s^2=0\) is lightlike or null, and
\(\Delta s^2<0\) is spacelike. These are not merely algebraic labels; they
describe what kinds of causal connection are possible between the events.

A common misunderstanding is to think that invariant means every component is
unchanged. A \cref{Lorentz transformation}{sr.lorentz_transformations} changes
the individual components \(\Delta t,\Delta x,\Delta y,\Delta z\). What stays
fixed is the combination

\[
c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2.
\]

This is like rotating an ordinary vector: the separate \(x\) and \(y\)
components change, but the length \(x^2+y^2\) does not.

For light travelling in one spatial dimension, \(\Delta x=c\Delta t\), so the
interval is zero. That null condition leads to the
\cref{Light cone}{sr.light_cone}. For a massive clock following a timelike path,
the interval along the path defines \cref{Proper time}{sr.proper_time}. Thus
the same interval formula governs both causal structure and clock time.

The interval is the replacement for ordinary distance as the invariant geometric
quantity in special relativity. Once it is fixed, many later ideas become
systematic: Lorentz transformations are the transformations that preserve it,
four-vector norms are computed from it, and spacetime diagrams use it to
classify separations.

### Block Plan

- `sr.spacetime_interval.overview`, `overview`, "What remains fixed".
- `sr.spacetime_interval.definition`, `definition`, "Definition".
- `sr.spacetime_interval.constructing_delta`, `construction`, "Start with two events".
- `sr.spacetime_interval.metric_derivation`, `derivation`, "Metric contraction".
- `sr.spacetime_interval.classification`, `explanation`, "Timelike lightlike spacelike".
- `sr.spacetime_interval.invariant_not_components`, `misconception`, "Invariant does not mean unchanged components".
- `sr.spacetime_interval.light_and_proper_time`, `explanation`, "Light and clocks".
- `sr.spacetime_interval.why_it_matters`, `summary`, "Why the interval matters".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: an invariant-quantity
multiple-choice check, a sign-meaning explanation, two classification
calculations, and one invariant-versus-components misconception check.

### References

Linked broadly to `TTM II` for the interval definition and `TRR` for interval
and causal-classification background. Precise locators should be added during
source review.

### Graphics

Retain the existing graphic. The diagram already shows representative
timelike, spacelike, and lightlike separations from one event, which is the
right visual emphasis for this concept.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- None.

#### Atlas Issues

- The interval and metric are tightly coupled. The current order, metric first
  then interval, works, but future authoring should keep the two concepts from
  duplicating each other excessively.

## 3.3 `sr.lorentz_transformations`: Lorentz transformations

### Scope

This concept introduces Lorentz transformations as the coordinate translation
rules between inertial frames in special relativity. It should state the
standard boost, explain why the interval-preservation condition matters, and
connect the component formulas with the metric matrix condition. It should not
develop every consequence such as time dilation and length contraction in full,
and it should not replace the later four-vector treatment.

### Exposition

Lorentz transformations are the rules for translating spacetime coordinates
between inertial frames in special relativity. They replace Galilean
transformations because the
\cref{Constancy of the speed of light}{sr.constancy_of_speed_of_light} and the
\cref{Principle of relativity}{sr.principle_of_relativity} cannot both be
satisfied by absolute time.

More precisely, Lorentz transformations are the linear coordinate
transformations relating two \cref{Inertial frames}{sr.inertial_frames}. They
preserve the \cref{Spacetime interval}{sr.spacetime_interval}, or equivalently
the \cref{Metric tensor}{sr.metric_tensor}, so that all inertial observers
agree on invariant spacetime separations.

For the standard boost, take two inertial frames \(S\) and \(S'\), with \(S'\)
moving at speed \(v\) in the \(+x\) direction relative to \(S\). Write

\[
\beta=\frac{v}{c}, \qquad
\gamma=\frac{1}{\sqrt{1-\beta^2}}.
\]

The origins coincide at \(t=t'=0\), and only the \(ct\) and \(x\) coordinates
mix; \(y\) and \(z\) remain unchanged.

Homogeneity of space and time motivates linear transformations. There is no
special place or time at which the coordinate rule should change. Equal
displacements between events must transform in the same way wherever they
occur, so the transformation between inertial coordinate differences should not
have coefficients depending on \(x\) or \(t\).

The invariant light speed requires lightlike separations to remain lightlike in
every inertial frame. The stronger geometric statement is that the full interval
is preserved:

\[
ds^2=c^2dt^2-dx^2-dy^2-dz^2
    =c^2dt'^2-dx'^2-dy'^2-dz'^2.
\]

This interval-preservation condition is what turns the relativity postulates
into a spacetime transformation law.

For a boost along the \(x\)-axis, the Lorentz transformation is

\[
ct'=\gamma(ct-\beta x), \qquad
x'=\gamma(x-\beta ct), \qquad
y'=y, \qquad
z'=z.
\]

The inverse transformation is obtained by replacing \(\beta\) with \(-\beta\).
The factor \(\gamma\) becomes large as \(v\) approaches \(c\), encoding the
growing difference between Galilean and relativistic kinematics.

The interval check is worth seeing once. Substitute the boost equations into
\(c^2dt'^2-dx'^2\):

\[
c^2dt'^2-dx'^2
=\gamma^2[(cdt-\beta dx)^2-(dx-\beta cdt)^2].
\]

Expanding and cancelling the cross terms gives

\[
\gamma^2(1-\beta^2)(c^2dt^2-dx^2)=c^2dt^2-dx^2,
\]

because \(\gamma^2(1-\beta^2)=1\). The unchanged \(y\) and \(z\) components
complete the four-dimensional interval check.

In four-vector notation, with \(x^\mu=(ct,x,y,z)\), a Lorentz transformation is
written

\[
x'^\mu=\Lambda^\mu{}_{\nu}x^\nu.
\]

Preservation of the metric is expressed by

\[
\eta_{\alpha\beta}\Lambda^\alpha{}_{\mu}\Lambda^\beta{}_{\nu}
=\eta_{\mu\nu},
\]

or, in matrix notation,

\[
\Lambda^T\eta\Lambda=\eta.
\]

This is the compact version of the interval-preservation rule.

A Lorentz transformation does not move the physical event. It changes the
coordinate description assigned by one inertial frame into the coordinate
description assigned by another. In a
\cref{Minkowski diagram}{sr.minkowski_diagram}, this looks like tilted axes
describing the same event, not the event being dragged to a different place in
reality.

Because time and space mix, observers can disagree about simultaneity,
coordinate time intervals, lengths, and velocity components. Those effects are
not separate rules added after the fact; they are consequences of using Lorentz
transformations as the coordinate translation rule while preserving the
spacetime interval.

### Block Plan

- `sr.lorentz_transformations.overview`, `overview`, "Coordinate translation in spacetime".
- `sr.lorentz_transformations.definition`, `definition`, "Definition".
- `sr.lorentz_transformations.setup`, `construction`, "Standard boost setup".
- `sr.lorentz_transformations.why_linear`, `explanation`, "Why the transformation is linear".
- `sr.lorentz_transformations.interval_condition`, `derivation`, "Preserve the interval".
- `sr.lorentz_transformations.boost_formula`, `derivation`, "Boost along \(x\)".
- `sr.lorentz_transformations.interval_check`, `derivation_step`, "Checking the boost".
- `sr.lorentz_transformations.matrix_form`, `construction`, "Matrix form".
- `sr.lorentz_transformations.not_moving_events`, `misconception`, "Not moving the event".
- `sr.lorentz_transformations.physical_effects`, `explanation`, "What changes between frames".

### Study Questions

Drafted in `data/study_questions.csv` as six questions: one interval-preserving
definition check, one conceptual space-time mixing explanation, two boost
calculations, one metric-matrix interpretation, and one same-event misconception
correction.

### References

Linked to `TTM II, 1.3 General Lorentz Transformation` for the standard boost
formula and broadly to `TRR` for the metric-preservation/matrix viewpoint.
Precise TRR locator should be added during source review.

### Graphics

Retain the existing graphic. Tilted primed axes and unprimed axes describing
the same event \(P\) communicate the coordinate-change interpretation directly.
No SVG code change is needed in this pass.

### Drafting Issues

#### Source Issues

- Add precise TRR locator for the matrix/metric preservation viewpoint.

#### Schema/View Issues

- This concept is now long enough that the details panel may benefit from a
  local table-of-contents view over block titles.

#### Atlas Issues

- Consequences such as time dilation, length contraction, and relativity of
  simultaneity may deserve explicit concepts later if the atlas expands the
  introductory SR material.

## 3.4 `sr.light_cone`: Light cone

### Scope

This concept introduces the light cone as the causal map from one spacetime
event. It should explain the null interval condition, future and past cones,
inside/on/outside causal regions, and frame-invariant classification. It should
not become a general treatment of Minkowski diagrams or a full discussion of
causality in general relativity.

### Exposition

A light cone is the causal map drawn from a chosen spacetime event. It marks
which events could be reached by light, which could be reached by
slower-than-light matter or signals, and which are spacelike separated from the
starting event.

The light cone of an event is the set of spacetime directions for which the
\cref{Spacetime interval}{sr.spacetime_interval} is zero. It separates timelike
directions, which can be followed by massive particles, from spacelike
directions, which cannot be connected by causal signals moving at or below
\(c\).

The cone is derived by setting the interval from a chosen event to zero:

\[
\Delta s^2=c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2=0.
\]

Equivalently,

\[
|\Delta \mathbf x|=c|\Delta t|.
\]

This is the condition for a signal moving exactly at speed \(c\), either away
from or toward the chosen event.

The future light cone has \(\Delta t>0\): events on it can be reached by light
emitted from the starting event. The past light cone has \(\Delta t<0\): events
on it could have sent light to the starting event. Inside the cones are timelike
regions; outside them are spacelike regions.

Inside the future cone are events that could be influenced by a slower-than-light
signal from the starting event. On the cone are events reached by light. Outside
are spacelike-separated events, where any influence would need to outrun light.
This inside/on/outside classification is the practical causal meaning of the
interval sign.

The light cone is defined by \(\Delta s^2=0\), and
\cref{Lorentz transformations}{sr.lorentz_transformations} preserve
\(\Delta s^2\). Different inertial observers may draw different coordinate axes
through the same event, but they agree which separations are timelike,
lightlike, and spacelike.

Being outside the light cone is not the same as being far away in ordinary
space. A nearby event can be outside the cone if too little time has elapsed for
a signal to reach it. A distant event can be inside the future cone if enough
time has elapsed. The comparison is always between spatial separation and
elapsed time multiplied by \(c\).

In a one-space-one-time diagram, light satisfies \(x=\pm ct\), so the cone
boundary is drawn as two 45-degree lines. With two space dimensions plus time,
those lines become a cone. In three space dimensions, each moment after the
event gives an expanding sphere of light; stacking those spheres through time
gives the cone picture.

### Block Plan

- `sr.light_cone.overview`, `overview`, "Causal map from one event".
- `sr.light_cone.definition`, `definition`, "Definition".
- `sr.light_cone.null_condition`, `derivation`, "Null interval condition".
- `sr.light_cone.future_past`, `explanation`, "Future and past cones".
- `sr.light_cone.causal_regions`, `explanation`, "Inside on outside".
- `sr.light_cone.invariant_cone`, `explanation`, "Same cone for all inertial observers".
- `sr.light_cone.not_distance_only`, `misconception`, "Not just distance".
- `sr.light_cone.diagram_picture`, `intuition`, "Why it looks like a cone".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: one region
classification multiple-choice check, one invariance explanation, two
interval/light-travel calculations, and one distance-versus-causal-separation
misconception check.

### References

Linked broadly to `TTM II` for null separations/light cones and to `TRR` for
causal-structure background. Precise locators should be added during source
review.

### Graphics

Retain the existing graphic. This is the concept where the 45-degree cone
boundary should dominate, and the current graphic keeps that geometry clean.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- None.

#### Atlas Issues

- Later GR content will need to revisit light cones when curvature and local
  tangent frames are introduced.

## 3.5 `sr.minkowski_diagram`: Minkowski diagram

### Scope

This concept introduces Minkowski diagrams as visual tools for reasoning about
events, worldlines, light propagation, and inertial-frame axes. It should
explain the \(x,ct\) axes, 45-degree light rays, tilted moving-frame axes, and
how to read the diagram safely. It should not re-derive Lorentz transformations
in full or become a general course on spacetime geometry.

### Exposition

A Minkowski diagram is a visual tool for reasoning about events, worldlines,
light propagation, and changing inertial frames. It turns the algebra of
\cref{Lorentz transformations}{sr.lorentz_transformations} and the geometry of
the \cref{Light cone}{sr.light_cone} into a picture.

A Minkowski diagram represents \cref{Spacetime events}{sr.spacetime_event},
worldlines, light cones, and Lorentz-transformed axes in a reduced number of
dimensions, usually one space axis \(x\) and one time axis \(ct\). A point on
the diagram is an event: one where-and-when.

The vertical axis is usually \(ct\), not \(t\), so both axes have units of
length. With equal scales on \(x\) and \(ct\), light rays satisfy

\[
x=\pm ct
\]

and appear as 45-degree lines. This convention makes the causal structure
visible without writing the interval formula every time.

A curve through many events is a worldline: the history of a particle, clock,
detector, or light pulse. A vertical worldline represents something at rest in
the chosen frame. A tilted timelike worldline represents slower-than-light
motion. A 45-degree worldline represents light.

Axes for a moving inertial frame are drawn using the Lorentz transformations.
The \(ct'\)-axis is the worldline of the moving frame's spatial origin, so it
satisfies \(x'=0\), which gives \(x=vt\). The \(x'\)-axis is the line of
simultaneity \(t'=0\), which gives \(ct=\beta x\) for a standard boost.

A Minkowski diagram is not ordinary graph paper with a time label attached.
Vertical and horizontal page distances are not themselves invariant lengths.
The invariant quantity is the spacetime interval, and the diagram is designed
to preserve causal relationships and coordinate geometry, not Euclidean visual
distance.

The diagram makes frame dependence visible. A moving observer's axes tilt, so
that different observers slice the same spacetime into space and time
differently. This helps explain relativity of simultaneity, time dilation,
length contraction, and why the same event can receive different coordinate
labels.

Minkowski diagrams are most reliable when read qualitatively unless the scale
conventions are stated carefully. Angles and apparent Euclidean lengths on the
page can mislead. The safe questions are: where are the events, which worldlines
connect them, where are the lightlike directions, and which axes belong to which
inertial frame?

### Block Plan

- `sr.minkowski_diagram.overview`, `overview`, "Spacetime as a working plot".
- `sr.minkowski_diagram.definition`, `definition`, "Definition".
- `sr.minkowski_diagram.axes`, `construction`, "Axes and units".
- `sr.minkowski_diagram.events_worldlines`, `explanation`, "Events and worldlines".
- `sr.minkowski_diagram.primed_axes`, `derivation`, "Moving-frame axes".
- `sr.minkowski_diagram.not_ordinary_graph`, `misconception`, "Not ordinary graph paper".
- `sr.minkowski_diagram.what_it_reveals`, `explanation`, "What the diagram reveals".
- `sr.minkowski_diagram.reading_carefully`, `warning`, "Read with care".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: a \(ct'\)-axis
multiple-choice check, a 45-degree light-ray explanation, one moving-origin
calculation, an event/worldline distinction, and a warning about Euclidean
visual readings.

### References

Linked broadly to `TTM II` for spacetime diagrams and to `TRR` for broader
spacetime-geometry background. Precise locators should be added during source
review.

### Graphics

Retain the existing graphic. The rest worldline, slower-than-light worldline,
and single light ray give this concept a distinct visual identity from the
full light-cone graphic.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- None.

#### Atlas Issues

- If introductory SR is expanded, relativity of simultaneity, time dilation,
  and length contraction may become separate concepts linked from this one and
  `sr.lorentz_transformations`.


## 4.1 `sr.proper_time`: Proper time

### Scope

This concept explains proper time as clock time accumulated along a timelike
worldline. It should rely on the spacetime interval and prepare for
four-velocity, but it should not fully develop four-vector calculus or the twin
paradox as a separate extended topic.

### Exposition

Proper time is the time carried by a clock. If a clock moves from one event to
another along a timelike worldline, its proper time is the elapsed time shown by
that clock. An inertial frame may assign a coordinate time between the same two
events, but that coordinate time belongs to the frame's grid of synchronized
clocks. Proper time belongs to the travelling clock itself.

The definition comes directly from the spacetime interval. With the sign
convention used in this atlas,
\[
ds^2=c^2dt^2-d\mathbf x^2.
\]
For a timelike segment we define
\[
ds^2=c^2d\tau^2,
\]
so \(d\tau\) is the small amount of proper time accumulated along that segment
of the worldline. For a finite path, the clock reading is obtained by summing,
or integrating, those small contributions:
\[
\Delta\tau=\int d\tau.
\]

For motion at speed \(v\) in one inertial frame, \(d\mathbf x^2=v^2dt^2\), so
\[
c^2d\tau^2=c^2dt^2-v^2dt^2
  =c^2dt^2\left(1-\frac{v^2}{c^2}\right).
\]
Taking the future-directed positive root gives
\[
d\tau=dt\sqrt{1-\frac{v^2}{c^2}}=\frac{dt}{\gamma}.
\]
This is the familiar moving-clock result, but here it is not an isolated rule.
It is a direct consequence of measuring timelike length with the spacetime
interval.

Proper time is invariant for a specified worldline segment: every inertial
observer who correctly calculates the interval along that same segment obtains
the same \(d\tau\). That does not mean that all clocks between the same two
meetings accumulate the same time. If two clocks leave one event, follow
different timelike paths, and reunite at another event, each clock has measured
the proper time along its own worldline. Different paths through spacetime can
have different timelike lengths.

A common mistake is to treat time dilation as a mere delay in seeing a distant
clock. Signal delay certainly affects observation, but it is not what proper
time means. When clocks reunite at the same event and compare readings, no
light-travel correction remains to be made. Any difference in readings is a
worldline property.

Lightlike paths are a useful warning. For light, \(ds^2=0\), so the interval
would give \(d\tau=0\). This is not a license to imagine a photon's rest-frame
clock. There is no inertial rest frame for light. Proper time is defined for
timelike worldlines of massive clocks and particles; null worldlines sit at the
boundary where the interval vanishes.

Proper time matters because it supplies the natural parameter for relativistic
particle motion. Differentiating position with respect to \(\tau\) gives the
velocity four-vector, and integrating invariant quantities over \(d\tau\) later
becomes a standard way to build relativistic actions. In Minkowski's geometric
language, a clock measures the timelike length of its own path through
spacetime.

### Block Plan

- `overview`: Time carried by a clock.
- `definition`: Interval definition and finite path integral.
- `explanation`: Coordinate time versus clock time.
- `derivation`: Constant-speed relation \(d\tau=dt/\gamma\).
- `explanation`: Path dependence.
- `misconception`: Not merely light-signal delay.
- `warning`: Null paths and the absence of a photon rest clock.
- `summary`: Later role in four-velocity and actions.
- `historical_note`: Minkowski spacetime interpretation.

### Study Questions

1. Identify proper time as the reading of a clock along its worldline.
2. Explain why reunited clocks can disagree.
3. Calculate \(d\tau\) for constant speed.
4. Calculate \(d\tau\) from a simple interval in units where \(c=1\).
5. Distinguish proper-time difference from signal delay.

### References

- TTM SR/CF: proper time from the invariant interval; precise locator needed.
- TRR: Minkowski/proper-time geometric background; precise locator needed.

### Graphics

The existing clock ticks on a timelike worldline match the concept and should be
retained unless visual inspection shows a concrete defect.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- Proper time would benefit from a future derivation-trace view showing the path
  from interval to clock time to four-velocity.

#### Atlas Issues

- The twin-clock comparison might eventually deserve its own application or
  example block, but it should not become a separate concept yet.


## 4.2 `sr.four_vectors`: Four-vectors

### Scope

This concept introduces the general four-vector pattern: transformation law,
metric contraction, and geometric meaning. It should prepare the reader for
position, velocity, and momentum four-vectors without doing all of those
special cases here.

### Exposition

A four-vector is the relativistic version of a vector-like quantity. It has one
time component and three spatial components, but the number of components is
not the essence. The essence is how those components change when one inertial
observer is replaced by another.

The prototype is the displacement between two spacetime events,
\[
\Delta x^\mu=(c\Delta t,\Delta x,\Delta y,\Delta z).
\]
Under a Lorentz transformation,
\[
\Delta x'^\mu=\Lambda^\mu{}_\nu\Delta x^\nu.
\]
Any object \(A^\mu\) that transforms by the same rule,
\[
A'^\mu=\Lambda^\mu{}_\nu A^\nu,
\]
is called a four-vector.

This definition is stricter than it first looks. A column of four unrelated
numbers is not automatically a four-vector. The components must mix in exactly
the Lorentz way under boosts and rotations. In that sense a four-vector is one
geometric object, not four independent measurements glued together.

The metric gives four-vectors their invariant scalar products. With the \(+---\)
metric convention,
\[
A_\mu B^\mu=\eta_{\mu\nu}A^\mu B^\nu.
\]
Lorentz transformations preserve \(\eta\), so
\[
A'_\mu B'^\mu=A_\mu B^\mu.
\]
This is the same structural role played by dot products of ordinary vectors
under rotations, except that the spacetime metric has one time sign and three
space signs.

The distinction between upper and lower components matters. The metric lowers
an index:
\[
A_\mu=\eta_{\mu\nu}A^\nu.
\]
In standard coordinates this turns \(A^\mu=(A^0,A^1,A^2,A^3)\) into
\[
A_\mu=(A^0,-A^1,-A^2,-A^3).
\]
The minus signs are what prevent the scalar product from becoming an ordinary
Euclidean length.

Four-vectors matter because they make relativistic laws portable between
frames. Position, velocity, momentum, current, and potential all use this
pattern. In each case the components depend on the observer, but the
transformation law and invariant contractions express the underlying physical
quantity.

### Block Plan

- `overview`: One object, four linked components.
- `definition`: Lorentz transformation law.
- `construction`: Prototype from spacetime displacement.
- `explanation`: Transformation law as the test.
- `derivation`: Invariant scalar products.
- `construction`: Upper and lower components.
- `misconception`: Not any four numbers.
- `example`: Recurring examples.
- `summary`: Why four-vectors matter.

### Study Questions

1. Identify the transformation-law criterion.
2. Explain why a four-vector is not just a list.
3. Calculate a simple invariant square.
4. Calculate a simple scalar product.
5. Explain why invariant contractions are useful.

### References

- TTM SR/CF: four-vector transformation law; precise locator needed.
- TRR: Minkowski scalar products and relativistic vector notation; precise
  locator needed.

### Graphics

The existing graphic captures the correct idea: one spacetime arrow and a linked
component column. Retain unless visual inspection exposes a layout problem.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- A future notation glossary should include upper/lower indices, repeated-index
  summation, and the \(+---\) convention.

#### Atlas Issues

- `RELATED` between metric and four-vectors is adequate for now, but a future
  edge type such as `MEASURES` or `CONTRACTS` may be more precise.


## 4.3 `sr.position_four_vector`: Position four-vector

### Scope

This concept treats event coordinates packaged as a four-vector and emphasizes
the difference between origin-dependent position and origin-independent
displacement. It should not become a full repeat of four-vectors or spacetime
intervals.

### Exposition

The position four-vector is the first concrete four-vector most learners meet.
In an inertial frame, an event \(P\) is assigned coordinates
\[
x^\mu=(ct,x,y,z).
\]
The first component is \(ct\), not just \(t\), so that all four components have
dimensions of length. In one-space-one-time diagrams this convention also makes
light rays satisfy \(x=\pm ct\).

The phrase position four-vector needs care. It is not merely the ordinary
spatial position \(\mathbf x\). It is the spacetime coordinate of an event
relative to a chosen origin event. If the origin changes, the components of
\(x^\mu\) change. That is normal coordinate dependence, not a physical problem.

If two inertial frames share an origin event, their coordinate descriptions of
another event are related by the Lorentz transformation law
\[
x'^\mu=\Lambda^\mu{}_\nu x^\nu.
\]
For a boost along the \(x\)-axis, \(ct\) and \(x\) mix. This is the concrete
reason time and space coordinates are treated as components of one object.

The most physical use of position four-vectors is usually in differences. For
two events,
\[
\Delta x^\mu=x_2^\mu-x_1^\mu.
\]
This displacement does not depend on the arbitrary choice of coordinate origin.
Contracting it with the metric gives the spacetime interval:
\[
\Delta s^2=\eta_{\mu\nu}\Delta x^\mu\Delta x^\nu.
\]
So the position four-vector provides the coordinate packaging, while
displacements between position four-vectors supply invariant spacetime
geometry.

For example, if an event occurs at \(t=2\,\mathrm{ns}\), \(x=0.30\,\mathrm m\),
\(y=z=0\), then with \(c=3.0\times10^8\,\mathrm{m\,s^{-1}}\),
\[
ct=0.60\,\mathrm m,
\]
so \(x^\mu=(0.60\,\mathrm m,0.30\,\mathrm m,0,0)\) relative to the chosen
origin.

The later velocity four-vector is obtained by differentiating \(x^\mu\) with
respect to proper time. Thus position four-vectors are not just labels for
events; they are the starting point for relativistic kinematics.

### Block Plan

- `overview`: Event coordinates as one object.
- `definition`: \(x^\mu=(ct,x,y,z)\).
- `construction`: Why use \(ct\).
- `explanation`: Dependence on origin event.
- `derivation`: Lorentz transformation of position.
- `explanation`: Differences and intervals.
- `misconception`: Not just ordinary spatial position.
- `example`: Simple coordinate conversion.
- `summary`: Role in kinematics.

### Study Questions

1. Identify why \(ct\) is used.
2. Explain origin dependence.
3. Explain why differences matter.
4. Convert an event coordinate into \(x^\mu\).
5. Compute an interval from two position four-vectors.

### References

- TTM SR/CF: position four-vector and event coordinates; precise locator needed.
- TRR: spacetime position/displacement vector background; precise locator
  needed.

### Graphics

The existing origin-to-event arrow with projections matches the concept.
Retain unless visual inspection shows a layout problem.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- A notation glossary should explain \(x^\mu\), \(\Delta x^\mu\), and the
  convention of using \(ct\).

#### Atlas Issues

- None.


## 4.4 `sr.velocity_four_vector`: Velocity four-vector

### Scope

This concept develops four-velocity as \(dx^\mu/d\tau\), a tangent to a
timelike worldline. It should not become a full treatment of acceleration or
force; those belong later.

### Exposition

Ordinary velocity is \(\mathbf v=d\mathbf x/dt\). It is useful, but it is tied
to one inertial frame's coordinate time. A relativistic velocity object should
transform as a four-vector, so its denominator must not depend on a particular
observer's clock grid. The invariant clock along a massive particle's worldline
is proper time.

The velocity four-vector is therefore defined by
\[
U^\mu=\frac{dx^\mu}{d\tau},
\]
where \(x^\mu\) is the position four-vector and \(\tau\) is proper time. Since
\(x^\mu\) is a four-vector and \(d\tau\) is invariant, \(U^\mu\) transforms as
a four-vector.

Writing \(x^\mu=(ct,\mathbf x)\), we have
\[
U^\mu=\left(c\frac{dt}{d\tau},\frac{d\mathbf x}{d\tau}\right).
\]
Because \(dt/d\tau=\gamma\), and
\[
\frac{d\mathbf x}{d\tau}
 =\frac{d\mathbf x}{dt}\frac{dt}{d\tau}
 =\gamma\mathbf v,
\]
the components in one inertial frame are
\[
U^\mu=\gamma(c,\mathbf v).
\]

The fixed norm is an important check. With the \(+---\) metric,
\[
U_\mu U^\mu=\gamma^2(c^2-v^2)=c^2.
\]
So all massive particles have four-velocity of invariant magnitude \(c\), even
though their ordinary speeds may be different. This is not saying every
particle moves through space at speed \(c\). It is saying that every massive
worldline has the same normalized timelike tangent when parameterized by
proper time.

Geometrically, four-velocity is the future-directed tangent to the particle's
worldline. If the particle accelerates, this tangent changes from event to
event. For a particle at rest in a chosen frame, \(\mathbf v=0\) and
\(\gamma=1\), so
\[
U^\mu=(c,0,0,0).
\]
The spatial part vanishes, but the particle is still moving along its timelike
worldline.

Four-velocity matters because multiplying it by invariant mass gives
four-momentum. It is the kinematic bridge from the geometry of worldlines to
the dynamics of energy, momentum, and force.

### Block Plan

- `overview`: Tangent per unit proper time.
- `definition`: \(U^\mu=dx^\mu/d\tau\).
- `explanation`: Why proper time is the denominator.
- `derivation`: \(U^\mu=\gamma(c,\mathbf v)\).
- `derivation`: Fixed norm \(U_\mu U^\mu=c^2\).
- `intuition`: Worldline tangent picture.
- `misconception`: Not \((c,\mathbf v)\).
- `example`: Particle at rest.
- `summary`: Bridge to four-momentum.

### Study Questions

1. Identify proper time as the parameter.
2. Explain why three-velocity is not a four-vector.
3. Compute components for \(v=0.6c\).
4. Check the invariant norm.
5. Explain the tangent-to-worldline meaning.

### References

- TTM SR/CF: four-velocity definition and components; precise locator needed.
- TRR: timelike worldline and four-velocity geometry; precise locator needed.

### Graphics

The existing tangent-to-worldline graphic fits the concept well. Retain unless
visual inspection shows label crowding.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- None.

#### Atlas Issues

- Four-acceleration may be needed later if the atlas develops relativistic
  dynamics beyond the Lorentz force law.


## 4.5 `sr.momentum_four_vector`: Momentum four-vector

### Scope

This concept packages energy and momentum as one four-vector and derives the
energy-momentum relation. It should prepare mass-energy equivalence but leave
the interpretation of \(E_0=mc^2\) mainly to 4.6.

### Exposition

Four-velocity is kinematic: it describes the tangent to a particle's worldline.
Four-momentum is dynamical: it combines energy and momentum into one
relativistic object. For a massive particle,
\[
p^\mu=mU^\mu.
\]
Since \(U^\mu=\gamma(c,\mathbf v)\), this gives
\[
p^\mu=(\gamma mc,\gamma m\mathbf v).
\]
Identifying
\[
\mathbf p=\gamma m\mathbf v,\qquad E=\gamma mc^2,
\]
we write
\[
p^\mu=(E/c,\mathbf p).
\]

The invariant norm gives the key relation. With the \(+---\) metric,
\[
p_\mu p^\mu=\frac{E^2}{c^2}-\mathbf p^2.
\]
But \(p^\mu=mU^\mu\), and \(U_\mu U^\mu=c^2\), so
\[
p_\mu p^\mu=m^2c^2.
\]
Equating these two expressions gives
\[
\frac{E^2}{c^2}-\mathbf p^2=m^2c^2,
\]
or
\[
E^2=\mathbf p^2c^2+m^2c^4.
\]

Energy and three-momentum are therefore not separate relativistic bookkeeping
systems. They are components of one four-vector. Different observers may assign
different values of \(E\) and \(\mathbf p\), but they are describing the same
object, and they agree on its invariant norm.

The rest frame makes the structure especially clear. In the rest frame of a
massive particle, \(\mathbf v=0\), \(\gamma=1\), and \(\mathbf p=0\), so
\[
p^\mu=(mc,\mathbf 0).
\]
The time component remains nonzero. This is the immediate doorway to rest
energy and mass-energy equivalence.

There is one important warning. The construction \(p^\mu=mU^\mu\) assumes a
massive particle with proper time along its worldline. Massless particles have
no rest frame and no proper time parameter, but they still have four-momentum.
For them \(p_\mu p^\mu=0\) and \(E=|\mathbf p|c\).

### Block Plan

- `overview`: Energy and momentum as one object.
- `definition`: \(p^\mu=mU^\mu=(E/c,\mathbf p)\).
- `derivation`: Components from four-velocity.
- `derivation`: Invariant norm.
- `derivation_step`: Energy-momentum relation.
- `explanation`: Frame-dependent components.
- `example`: Rest frame.
- `misconception`: Not Newtonian momentum plus a label.
- `warning`: Massless particles.
- `summary`: Role in relativistic dynamics.

### Study Questions

1. Identify \(p^\mu=mU^\mu=(E/c,\mathbf p)\).
2. Explain frame-dependent energy/momentum components.
3. Compute \(E\) and \(|\mathbf p|\) for a simple massive particle.
4. Check the invariant mass relation.
5. Describe the rest-frame four-momentum.
6. Explain the massless-particle caveat.

### References

- TTM SR/CF: four-momentum and energy-momentum relation; precise locator
  needed.
- TRR: mass shell/four-momentum geometry; precise locator needed.

### Graphics

The existing graphic correctly pairs a \(p^\mu\) arrow with \(E/c\) and
\(\mathbf p\) components. Retain unless visual inspection shows crowding.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- The atlas may eventually need a concept or block style for massless limits.

#### Atlas Issues

- Consider whether `mass shell` deserves a separate concept when QM or particle
  physics content is added.


## 4.6 `sr.mass_energy_equivalence`: Mass-energy equivalence

### Scope

This concept explains \(E_0=mc^2\) as rest energy derived from the
four-momentum norm. It should include interpretation and common mistakes, but
not become a full treatment of nuclear physics, binding energy calculations, or
particle reactions.

### Exposition

Mass-energy equivalence is the statement that invariant mass corresponds to
rest energy:
\[
E_0=mc^2.
\]
The subscript is useful. This is rest energy, the energy of a massive system in
the frame where its total three-momentum is zero.

The clean derivation comes from four-momentum. Write
\[
p^\mu=(E/c,\mathbf p).
\]
Its invariant norm is
\[
p_\mu p^\mu=\frac{E^2}{c^2}-\mathbf p^2.
\]
For a particle or system of invariant mass \(m\), this norm is \(m^2c^2\), so
\[
\frac{E^2}{c^2}-\mathbf p^2=m^2c^2.
\]
Multiplying by \(c^2\) gives the energy-momentum relation
\[
E^2=\mathbf p^2c^2+m^2c^4.
\]

Now choose the rest frame, where the total spatial momentum vanishes:
\[
\mathbf p=0.
\]
Then
\[
E^2=m^2c^4.
\]
Taking the positive physical root gives
\[
E_0=mc^2.
\]

This is easy to remember and easy to misread. It is not saying that total
energy is always just \(mc^2\). For a moving massive particle, total energy is
\(E=\gamma mc^2\). The rest-energy statement is the zero-momentum case of the
full relation.

It is also not best understood as a magical conversion of one substance called
mass into another substance called energy. In relativity, invariant mass is a
measure of a system's total energy-momentum content. If a closed system loses
rest energy \(\Delta E_0\), its invariant mass decreases by
\[
\Delta m=\frac{\Delta E_0}{c^2}.
\]
Conversely, adding internal energy to a closed system, for example by heating
it, increases its invariant mass by a tiny amount.

For everyday energy changes the mass difference is extremely small because
\(c^2\) is enormous. In nuclear and particle processes the changes are large
enough to dominate the phenomena. Binding energy, radiation, heat, and internal
motion can all contribute to the total rest-frame energy of a system and
therefore to its invariant mass.

Historically, Einstein's 1905 argument linked emitted energy with a decrease in
inertia. The later four-momentum formulation makes the result look inevitable:
rest energy is simply the time component of four-momentum in the frame where
the spatial momentum vanishes.

### Block Plan

- `overview`: Rest energy is mass energy.
- `definition`: \(E_0=mc^2\) and the full relation.
- `derivation`: From four-momentum norm.
- `derivation_step`: Rest-frame limit.
- `explanation`: Applies to systems.
- `misconception`: Not magic substance conversion.
- `example`: \(\Delta m=\Delta E_0/c^2\).
- `warning`: Total energy is not always \(mc^2\).
- `historical_note`: Einstein's 1905 result.
- `summary`: Why it matters.

### Study Questions

1. Identify rest energy.
2. Explain why the full energy-momentum relation matters.
3. Derive \(E_0=mc^2\) by setting \(\mathbf p=0\).
4. Calculate \(\Delta m\) from an energy loss.
5. Explain why heating a sealed box changes invariant mass.
6. Explain why "mass turns into energy" can mislead.

### References

- TTM SR/CF: mass-energy relation from four-momentum norm; precise locator
  needed.
- TRR: relativistic energy-momentum and mass-energy discussion; precise locator
  needed.

### Graphics

The existing graphic rightly keeps \(E=mc^2\) central while showing the
four-momentum norm below. Retain unless visual inspection shows crowding.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- This concept would benefit from richer inline disclosure for examples:
  mass defect, heating a box, and radiation emission are useful optional
  expansions.

#### Atlas Issues

- Binding energy may eventually need a separate concept if the atlas expands
  toward nuclear or particle physics.


## 5.1 `sr.lagrangian`: Lagrangian

### Scope

This concept introduces the Lagrangian as the local dynamical rule whose
integral forms the action. It should prepare the action principle and
Euler-Lagrange equations, but not derive the full variational equations here.

### Exposition

A Lagrangian is the local ingredient in a variational description of motion. In
particle mechanics it is a function of generalized coordinates, velocities, and
possibly time:
\[
L(q,\dot q,t).
\]
Its accumulated value is the action,
\[
S=\int L(q,\dot q,t)\,dt.
\]
The action principle then asks which histories make \(S\) stationary.

The contrast between \(L\) and \(S\) is important. The Lagrangian is evaluated
locally along a proposed history: at each time it looks at the current
coordinates and velocities. The action is global over the whole interval: it
adds those local contributions. This is how a compact local rule can select an
entire path.

For many simple nonrelativistic systems,
\[
L=T-V.
\]
For a particle in one dimension this might be
\[
L=\frac12m\dot x^2-V(x).
\]
That example is useful, but \(T-V\) is not the definition of a Lagrangian. The
definition is functional: \(L\) is the quantity whose integral is varied to get
the equations of motion.

A Lagrangian is also not unique. If we replace
\[
L\rightarrow L+\frac{dF(q,t)}{dt},
\]
the action changes only by endpoint terms. For variations with fixed endpoints,
those boundary terms do not affect the Euler-Lagrange equations. Different
Lagrangians can therefore encode the same dynamics.

In relativistic theories the Lagrangian, or sometimes the action directly,
should be built from invariant ingredients. Proper time, spacetime intervals,
and scalar contractions of four-vectors are natural building blocks. Setting
\(c=1\) often makes the symmetry clearer, but \(c\) can be restored when
dimensional interpretation matters.

There is no universal machine that derives the correct Lagrangian from nothing.
A proposed \(L\) encodes modelling choices: which variables describe the
system, what symmetries it has, what interactions are allowed, and which
approximations are being made. The variational principle then turns that
proposal into equations that can be tested.

The Lagrangian viewpoint becomes especially powerful in field theory. A field
Lagrangian density plays the same local role at each spacetime event, and
symmetries of the action become conservation laws through Noether's theorem.

### Block Plan

- `overview`: The local rule inside an action.
- `definition`: \(L(q,\dot q,t)\) and \(S=\int Ldt\).
- `explanation`: Local-to-global role.
- `warning`: Non-uniqueness under total derivatives.
- `example`: Simple \(T-V\) model.
- `construction`: Relativistic invariant building blocks.
- `misconception`: Chosen, not mechanically discovered.
- `summary`: Bridge to field theory and Noether.
- `historical_note`: Lagrange's reformulation.

### Study Questions

1. Identify the role of \(L\).
2. Explain why \(T-V\) is not the definition.
3. Explain total-derivative equivalence.
4. Calculate a simple \(T-V\) Lagrangian value.
5. Explain why relativistic Lagrangians use invariant ingredients.

### References

- TTM SR/CF: Lagrangian and action setup; precise locator needed.
- TRR: Lagrangian/action and invariant-building background; precise locator
  needed.

### Graphics

The existing local \(L\) tiles accumulating into \(S\) match the intended
meaning. Retain unless visual inspection shows layout problems.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- A future notation glossary should distinguish \(L\), action \(S\), and field
  Lagrangian density \(\mathcal L\).

#### Atlas Issues

- Total derivatives might eventually need a small optional exposition block or
  linked concept if gauge-field Lagrangians become more detailed.


## 5.2 `sr.action_principle`: Action principle

### Scope

This concept explains the stationary-action idea and the comparison of nearby
histories. It should prepare the Euler-Lagrange equations but leave the full
integration-by-parts derivation to 5.3.

### Exposition

The action principle describes motion by comparing whole possible histories.
For particle mechanics, a history \(q(t)\) is assigned an action
\[
S[q]=\int_{t_1}^{t_2}L(q,\dot q,t)\,dt.
\]
The physical history is the one for which the first-order change in \(S\)
vanishes under small allowed variations:
\[
\delta S=0.
\]

The standard picture is a family of nearby paths between the same endpoints.
Each trial path gives a number \(S\). The physical path is not chosen by
inspecting a force arrow at one instant; it is selected by how the whole action
responds when the path is varied.

Stationary does not necessarily mean smallest. A minimum is one kind of
stationary point, but a maximum or saddle can also have zero first-order
change. This is why modern accounts usually say stationary action rather than
least action.

In the standard derivation the endpoint values are fixed. If the varied path is
\[
q_a(t)=q(t)+a\,\eta(t),
\]
then \(\eta(t_1)=\eta(t_2)=0\). The action becomes a function \(S(a)\), and
stationarity of the original path is
\[
\left.\frac{dS}{da}\right|_{a=0}=0.
\]
Those fixed endpoints are what make boundary terms vanish when the
Euler-Lagrange equations are derived.

For relativistic systems, the action should be a scalar. Different inertial
observers may use different coordinates, but they should agree on which history
is physical. This motivates building the action from invariant ingredients:
proper time, spacetime intervals, scalar contractions of four-vectors, and
later local field quantities.

The action principle can feel global because it compares entire histories.
The remarkable result is that this global-sounding rule produces local
differential equations of motion. That bridge is the role of the
Euler-Lagrange equations.

### Block Plan

- `overview`: Choosing a whole history.
- `definition`: \(S[q]=\int Ldt\), \(\delta S=0\).
- `intuition`: Compare nearby histories.
- `misconception`: Stationary is not always smallest.
- `construction`: Fixed endpoints.
- `derivation_step`: One-parameter variation.
- `explanation`: Relativistic scalar actions.
- `summary`: From global rule to local equations.
- `historical_note`: Least action to stationary action.

### Study Questions

1. Recognize \(\delta S=0\).
2. Explain fixed endpoints.
3. Explain why "least" can mislead.
4. Check stationarity for a quadratic \(S(a)\).
5. Check non-stationarity for a linear term.
6. Explain why relativistic actions should be scalar.

### References

- TTM SR/CF: action principle setup; precise locator needed.
- TRR: stationary action and variational principles; precise locator needed.

### Graphics

The existing fixed-endpoint path variation graphic matches the intended
meaning. Retain unless visual inspection shows a concrete defect.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- A future derivation trace could show \(L\rightarrow S\rightarrow\delta S=0
  \rightarrow\) Euler-Lagrange equations.

#### Atlas Issues

- None.


## 5.3 `sr.euler_lagrange_equations`: Euler-Lagrange equations

### Scope

This concept derives the Euler-Lagrange equations from stationary action for
particle coordinates. It should not yet become field Euler-Lagrange theory,
though it may point forward to field equations.

### Exposition

The action principle says \(\delta S=0\). The Euler-Lagrange equations are what
that statement becomes as local differential equations of motion.

For one coordinate, start from
\[
S=\int_{t_1}^{t_2}L(q,\dot q,t)\,dt.
\]
Vary the path while holding the endpoints fixed:
\[
q(t)\rightarrow q(t)+\delta q(t),\qquad
\delta q(t_1)=\delta q(t_2)=0.
\]
The velocity varies too, so \(\dot q\rightarrow \dot q+\delta\dot q\).

The first-order variation of the action is
\[
\delta S=\int_{t_1}^{t_2}\left(
\frac{\partial L}{\partial q}\delta q+
\frac{\partial L}{\partial\dot q}\delta\dot q
\right)dt.
\]
The second term contains \(\delta\dot q\). Since
\(\delta\dot q=d(\delta q)/dt\), integrate by parts:
\[
\int_{t_1}^{t_2}\frac{\partial L}{\partial\dot q}\delta\dot q\,dt
=\left[\frac{\partial L}{\partial\dot q}\delta q\right]_{t_1}^{t_2}
-\int_{t_1}^{t_2}
\frac{d}{dt}\left(\frac{\partial L}{\partial\dot q}\right)\delta q\,dt.
\]
The boundary term vanishes because the endpoint variations are zero.

So
\[
\delta S=\int_{t_1}^{t_2}\left[
\frac{\partial L}{\partial q}
-\frac{d}{dt}\left(\frac{\partial L}{\partial\dot q}\right)
\right]\delta q\,dt.
\]
The variation \(\delta q(t)\) can be chosen freely between the endpoints. The
only way for \(\delta S\) to vanish for every such variation is for the bracket
to vanish at every time:
\[
\frac{d}{dt}\left(\frac{\partial L}{\partial\dot q}\right)
-\frac{\partial L}{\partial q}=0.
\]

For a familiar check, take
\[
L=\frac12m\dot x^2-V(x).
\]
Then \(\partial L/\partial\dot x=m\dot x\) and
\(\partial L/\partial x=-dV/dx\). The Euler-Lagrange equation gives
\[
m\ddot x+\frac{dV}{dx}=0,
\]
or \(m\ddot x=-dV/dx\), Newton's equation for a conservative force.

The important lesson is not that Newton's equation has been rediscovered in a
complicated way. The lesson is that once a Lagrangian is chosen, the same
variational machinery produces the motion. That pattern generalizes to
generalized coordinates and, later, to fields.

### Block Plan

- `overview`: Stationary action as an equation.
- `definition`: Euler-Lagrange equation.
- `construction`: Vary the path.
- `derivation`: First variation.
- `derivation_step`: Integration by parts.
- `derivation_step`: Arbitrary variations force the bracket to vanish.
- `summary`: Equation of motion.
- `worked_example`: Recover Newton's equation.
- `misconception`: Not an extra force law.
- `historical_note`: Euler and Lagrange.

### Study Questions

1. Recognize the Euler-Lagrange equation.
2. Explain integration by parts.
3. Explain fixed-endpoint boundary terms.
4. Compute partial derivatives for \(L=\tfrac12m\dot x^2-V(x)\).
5. Derive \(m\ddot x=-dV/dx\).
6. Explain usefulness in generalized coordinates.

### References

- TTM SR/CF: Euler-Lagrange equations from stationary action; precise locator
  needed.
- TRR: variational calculus and Euler-Lagrange derivation; precise locator
  needed.

### Graphics

The existing variation-to-E-L graphic matches the concept. Retain unless visual
inspection shows crowding.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- Long derivations like this would benefit from optional line-by-line
  disclosure for integration by parts and arbitrary-variation logic.

#### Atlas Issues

- Field Euler-Lagrange equations may eventually need their own concept or a
  strongly expanded field-equations concept.


## 5.4 `sr.canonical_momentum`: Canonical momentum

### Scope

This concept defines canonical momentum as the momentum conjugate to a
coordinate in the Lagrangian formulation. It should prepare Hamiltonian
formalism while warning that canonical, mechanical, and four-momentum are not
automatically the same thing.

### Exposition

Canonical momentum is the momentum-like quantity paired with a coordinate in
the Lagrangian and Hamiltonian descriptions. For a coordinate \(q_i\) with
velocity \(\dot q_i\), the canonical momentum conjugate to \(q_i\) is
\[
p_i=\frac{\partial L}{\partial \dot q_i}.
\]
For several generalized coordinates, each \(q_i\) has its own conjugate
momentum \(p_i\).

This definition is not arbitrary notation. It appears directly when the action
is varied. In the Euler-Lagrange derivation, integration by parts produces a
boundary contribution of the form
\[
\left[\frac{\partial L}{\partial\dot q_i}\delta q_i\right]_{t_1}^{t_2}.
\]
The coefficient of the endpoint displacement is precisely \(p_i\). Even when
the endpoints are fixed and this term vanishes, the calculation has revealed
which quantity is naturally paired with \(q_i\).

For the familiar Lagrangian
\[
L=\frac12m\dot x^2-V(x),
\]
the canonical momentum is
\[
p=\frac{\partial L}{\partial\dot x}=m\dot x.
\]
In this simple case canonical momentum agrees with ordinary mechanical
momentum. That agreement is useful, but it is not the definition.

Velocity-dependent interactions show the distinction. For a charged particle
in a nonrelativistic electromagnetic Lagrangian,
\[
L=\frac12m\mathbf v^2+e\mathbf A\cdot\mathbf v-e\phi,
\]
the canonical momentum is
\[
\mathbf p_{\rm can}=m\mathbf v+e\mathbf A.
\]
The mechanical momentum is still \(m\mathbf v\), while the canonical momentum
also contains the vector potential. This is not a paradox: canonical momentum
belongs to the variational and Hamiltonian structure.

Canonical momentum is the hinge used to pass to Hamiltonian mechanics. If the
relations
\[
p_i=\frac{\partial L}{\partial\dot q_i}
\]
can be inverted to express the velocities in terms of \(q_i,p_i,t\), then a
Legendre transform replaces velocity dependence by momentum dependence. The
resulting Hamiltonian formalism treats \((q_i,p_i)\) as phase-space variables.

The terminology can be hazardous. The symbol \(p\) may denote Newtonian
momentum, relativistic three-momentum, components of four-momentum, or
canonical momentum. The right question is always: which variables are being
used, and which Lagrangian derivative defines this \(p\)?

### Block Plan

- `overview`: A coordinate's dynamical partner.
- `definition`: \(p_i=\partial L/\partial\dot q_i\).
- `construction`: Boundary origin in the variation.
- `example`: Simple mechanical agreement with \(m\dot x\).
- `example`: Velocity-dependent electromagnetic interaction.
- `explanation`: Role in the Legendre transform and Hamiltonian mechanics.
- `misconception`: Not automatically four-momentum.
- `warning`: Notation overload.
- `summary`: Why it matters.
- `historical_note`: Generalized coordinates and phase space.

### Study Questions

1. Recognize the definition of canonical momentum.
2. Explain why it is conjugate to a coordinate.
3. Compute \(p\) for \(L=\tfrac12m\dot x^2-V(x)\).
4. Compute canonical momentum with a velocity-dependent potential term.
5. Explain why canonical and mechanical momentum can differ.
6. State its role in the transition to Hamiltonian mechanics.

### References

- TTM SR/CF: canonical momentum in the transition to Hamiltonian mechanics;
  precise locator needed.
- TRR: conjugate momentum and Hamiltonian phase-space background; precise
  locator needed.

### Graphics

The current graphic showing \(L(q,\dot q)\) feeding \(p=\partial L/\partial
\dot q\) is conceptually appropriate. Check whether the detail graphic has
enough room for the derivative notation.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- A future notation glossary should distinguish canonical momentum, mechanical
  momentum, relativistic three-momentum, and four-momentum.

#### Atlas Issues

- The electromagnetic example creates a useful bridge to vector potential and
  minimal coupling, but the detailed gauge interpretation belongs later.


## 5.5 `sr.hamiltonian_formalism`: Hamiltonian formalism

### Scope

This concept introduces Hamiltonian formalism as a phase-space reformulation of
Lagrangian mechanics. It should explain the Legendre transform, Hamilton's
equations, and the energy caveat without developing Poisson brackets or
quantum mechanics in detail.

### Exposition

Hamiltonian formalism rewrites dynamics in phase space. The Lagrangian
description uses coordinates and velocities,
\[
L(q,\dot q,t).
\]
The Hamiltonian description uses coordinates and their canonical momenta,
\[
(q_i,p_i).
\]
This pair is the state of the system in phase space.

The construction starts from canonical momentum:
\[
p_i=\frac{\partial L}{\partial\dot q_i}.
\]
If these relations can be solved for the velocities \(\dot q_i\) in terms of
\(q_i,p_i,t\), define
\[
H(q,p,t)=\sum_i p_i\dot q_i-L(q,\dot q,t),
\]
where the velocities on the right have been re-expressed in terms of
\(q,p,t\). This is a Legendre transform. It changes the independent variables
from velocities to momenta.

Phase space gives a different picture of motion. At one instant the system is a
point with coordinates \((q_i,p_i)\). As time passes, that point traces a curve.
The Hamiltonian determines the flow of this curve.

The equations of motion are Hamilton's equations:
\[
\dot q_i=\frac{\partial H}{\partial p_i},\qquad
\dot p_i=-\frac{\partial H}{\partial q_i}.
\]
They are first-order equations in phase space. When the Legendre transform is
valid, they are equivalent to the Euler-Lagrange equations.

For one coordinate, the structure can be seen by differentiating
\[
H=p\dot q-L.
\]
Treat \(\dot q\) as the velocity already expressed in terms of \(q,p,t\). Then
\[
dH=\dot q\,dp+p\,d\dot q-\frac{\partial L}{\partial q}dq
-\frac{\partial L}{\partial\dot q}d\dot q.
\]
Because \(p=\partial L/\partial\dot q\), the two \(d\dot q\) terms cancel.
Using the Euler-Lagrange equation, \(dp/dt=\partial L/\partial q\), gives
\[
dH=\dot q\,dp-\dot p\,dq,
\]
which is Hamilton's equation in differential form.

For
\[
L=\frac12m\dot x^2-V(x),
\]
we have \(p=m\dot x\), so \(\dot x=p/m\). The Hamiltonian becomes
\[
H=p\dot x-L
=\frac{p^2}{m}-\left(\frac{p^2}{2m}-V(x)\right)
=\frac{p^2}{2m}+V(x).
\]
Here \(H\) is the familiar total energy.

That familiar result should not become the definition. The Hamiltonian is the
generator of time evolution in phase space. In many simple time-independent
systems it equals the energy, but constrained systems, gauge theories, and
explicitly time-dependent systems require more care.

The Hamiltonian viewpoint matters because many deeper structures become more
visible in phase space: conserved quantities, symmetry generators, Poisson
brackets, statistical mechanics, and the later transition toward quantum
mechanics.

### Block Plan

- `overview`: Dynamics in phase space.
- `definition`: Hamiltonian as a Legendre transform.
- `construction`: Velocity variables replaced by momentum variables.
- `intuition`: Phase-space flow.
- `definition`: Hamilton's equations.
- `derivation_step`: Differential derivation.
- `warning`: Hamiltonian is not merely energy.
- `worked_example`: \(p^2/(2m)+V\).
- `summary`: Why it matters.
- `historical_note`: Hamilton's reformulation.

### Study Questions

1. Identify the primary variables.
2. Explain the Legendre transform.
3. Explain phase space.
4. Compute \(\dot x\) from \(H=p^2/(2m)+V(x)\).
5. Compute \(\dot p\) from the same Hamiltonian.
6. Explain why \(H\) is not simply defined as energy.

### References

- TTM SR/CF: Hamiltonian formalism and Legendre transform; precise locator
  needed.
- TRR: Hamiltonian mechanics as phase-space structure and route toward quantum
  theory; precise locator needed.

### Graphics

The existing phase-space flow graphic is well matched to the concept. Retain
unless visual inspection shows label or arrow crowding.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- Poisson brackets may eventually deserve their own concept if the atlas grows
  toward quantum mechanics.

#### Atlas Issues

- The current edge vocabulary does not distinguish "reformulates" from
  "derives from"; Hamiltonian formalism is presently represented with
  `DERIVES_FROM` edges from Lagrangian and canonical momentum.


## 5.6 `sr.noether_theorem`: Noether's theorem

### Scope

This concept explains Noether's theorem as the link from continuous symmetries
of the action to conserved quantities. It should give the mechanics intuition,
a light derivation sketch, and the field-theory bridge without turning into a
full treatment of gauge symmetries or stress-energy tensors.

### Exposition

Noether's theorem is the precise link between symmetry and conservation. It
states that every continuous symmetry of the action corresponds to a conserved
quantity. This is why conservation laws in physics are not merely separate
rules: they reveal structure in the action.

The symmetry must be a symmetry of the action, not just an attractive pattern
in an equation. A transformation might shift the time origin, shift every
position by the same amount, rotate the whole experiment, or change field
phases. If the action is unchanged, or changes only by an allowed boundary
term, then Noether's theorem applies.

Continuous matters. The standard theorem uses transformations depending
smoothly on a small parameter. Time translations, spatial translations, and
rotations are continuous. A discrete symmetry such as reflection can be
physically important, but it does not by itself produce a conserved quantity
through this version of the theorem.

The derivation has a common shape. Take a one-parameter transformation of the
dynamical variables and compute the corresponding variation of the action. If
the transformation is a symmetry, this variation vanishes, apart from possible
boundary terms. On histories that satisfy the equations of motion, the bulk
terms disappear. What remains is a total derivative:
\[
\frac{dQ}{dt}=0
\]
in mechanics, or
\[
\partial_\mu J^\mu=0
\]
in field theory. The remaining object \(Q\), or current \(J^\mu\), is the
conserved quantity.

The standard examples are worth remembering. Invariance under time translations
gives conservation of energy. Invariance under spatial translations gives
conservation of momentum. Invariance under rotations gives conservation of
angular momentum. The slogan is not "symmetry is pretty"; it is "continuous
symmetry of the action implies conserved quantity."

A simple mechanics example is a cyclic coordinate. If \(q\) does not appear in
the Lagrangian, then
\[
\frac{\partial L}{\partial q}=0.
\]
The Euler-Lagrange equation gives
\[
\frac{d}{dt}\left(\frac{\partial L}{\partial\dot q}\right)=0.
\]
But \(\partial L/\partial\dot q\) is the canonical momentum \(p\). Therefore
the momentum conjugate to that coordinate is conserved. Translation symmetry is
the familiar case where this gives conservation of linear momentum.

In field theory, Noether's theorem usually produces a conserved current:
\[
\partial_\mu J^\mu=0.
\]
This is a local conservation law. It says that the quantity is not disappearing
at a point; it is balanced by flow. Spacetime translation symmetry gives the
energy-momentum tensor, whose conservation packages local conservation of
energy and momentum.

Noether's theorem should not be treated as a magic conservation generator. The
symmetry must be continuous, it must be a symmetry of the action, and the
resulting conservation law is normally stated for fields or paths satisfying
the equations of motion. Boundary terms, constraints, and gauge redundancy can
all matter in advanced applications.

Historically, Emmy Noether published the theorem in 1918 while clarifying
conservation laws in modern field theories, especially in the setting created
by relativity. It became one of the organizing principles of twentieth-century
theoretical physics.

### Block Plan

- `overview`: Symmetry becomes conservation.
- `definition`: Continuous symmetry of the action gives conserved quantity.
- `explanation`: The symmetry is a symmetry of the action.
- `warning`: Continuous matters.
- `derivation`: Bulk terms vanish, total derivative remains.
- `example`: Time, space, and rotation examples.
- `worked_example`: Cyclic coordinate.
- `explanation`: Field-theory current form.
- `misconception`: Not a magic conservation generator.
- `historical_note`: Emmy Noether's 1918 result.
- `summary`: Why it matters.

### Study Questions

1. Recognize the symmetry-conservation link.
2. Explain why continuous symmetry matters.
3. Match time, space, and rotation symmetries to conserved quantities.
4. Show that a cyclic coordinate gives conserved canonical momentum.
5. Compute conserved momentum for \(L=\tfrac12m\dot x^2\).
6. Explain why a field-theory current is a local conservation statement.

### References

- TTM SR/CF: Noether theorem and action symmetries; precise locator needed.
- TRR: Noether theorem, conservation laws, and symmetry in modern field theory;
  precise locator needed.

### Graphics

The existing graphic uses an implication symbol from an unchanged action to a
conserved \(Q\), which matches the current concept scope. Retain unless visual
inspection shows label crowding.

### Drafting Issues

#### Source Issues

- Add precise TTM and TRR locators.

#### Schema/View Issues

- This concept would benefit from future disclosure blocks for the exact
  mechanics derivation and the field-current derivation.

#### Atlas Issues

- Future edge types might distinguish "symmetry yields conservation law" from
  ordinary derivation or relatedness.

## Template

```markdown
## <display_id> `<concept_id>`: <Concept title>

### Scope

Short note on what this concept should and should not cover.

### Exposition

Draft the concept as a coherent book-like section here.

### Block Plan

Optional notes on likely content blocks, titles, and kinds before editing the
CSV. Use an `overview` block when the concept needs a short orientation before
the definition or detailed development.

### Study Questions

Optional draft questions before editing `data/study_questions.csv`. Order them
from easier recognition or interpretation toward calculation, connection, or
synthesis.

### References

Optional source notes before editing `data/reference_links.csv`. Include TTM
and TRR where relevant. Broad locators are acceptable during drafting if marked
for later tightening.

### Graphics

Optional notes on whether the concept graphic should be retained, refined, or
replaced.

### Drafting Issues

Record non-blocking issues found while drafting, such as missing concepts,
awkward concept boundaries, possible splits/merges, insufficient block kinds,
weak edge types, notation glossary needs, reference gaps, or viewer limitations.
Fix critical blockers immediately; leave everything else here for later review.

Before moving on to the next concept, check block count and kinds, block
titles, question count and types, question ordering, reference links, `\cref`
targets, likely concept edges, and any graphic change.

#### Source Issues

- Missing or imprecise source locators.

#### Schema/View Issues

- Block-kind, rendering, folding, disclosure, or viewer-policy questions.

#### Atlas Issues

- Missing concepts, concept splits/merges, numbering gaps, or weak edge types.
```
