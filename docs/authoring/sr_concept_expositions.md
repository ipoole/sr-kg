# Concept Expositions

This file holds readable draft expositions before or alongside their split into
`data/content_blocks.csv`.

The CSV content blocks remain the source consumed by the application. This file
is an authoring and review aid: it preserves the coherent book-section form if
block boundaries, block kinds, or viewer presentation rules change later.

Use one section per concept, labelled with display ID, semantic ID, and title.
Keep concepts in atlas order where practical.

Generic source-locator and notation issues are now collected in
`docs/authoring/SOURCE_REVIEW_WORKLIST.md` and `docs/authoring/NOTATION_GLOSSARY.md`. Keep
concept-specific issues below, but avoid repeating generic notes once they are
covered by those worklists.

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
source or the observer. In SI units \(c\overset{\text{SI definition}}{=}299\,792\,458\,\mathrm{m\,s^{-1}}\)
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
x\overset{\text{light}}{=}\pm ct.
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
- `sr.spacetime_event.ct_coordinate`, `convention`, "Using \(ct\) as a time coordinate".
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

- Section-level source locator is now recorded in `data/reference_links.csv`.
- We may eventually want a sharper atlas edge type for "motivates field
  description" or "enforces finite propagation"; for now the current
  `REQUIRES` and `RELATED` links are adequate.

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
\eta_{\mu\nu}\coloneqq\mathrm{diag}(1,-1,-1,-1).
\]

The first entry belongs to the time component, written as \(ct\) when all four
coordinates are measured in units of length. The three negative entries belong
to the spatial components. These signs are not decoration. They are what make
spacetime geometry different from four-dimensional Euclidean geometry.

For a displacement

\[
\Delta x^\mu\coloneqq(c\Delta t,\Delta x,\Delta y,\Delta z),
\]

the metric gives

\[
\Delta s^2\equiv\eta_{\mu\nu}\Delta x^\mu\Delta x^\nu
          \overset{\text{metric}}{=}
          c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2.
\]

This is the invariant interval between the two events. The repeated indices
mean that we sum over the four components. In the standard inertial coordinates
used for special relativity the metric is diagonal, so there are no cross terms
such as \(dt\,dx\).

The same metric lowers indices. If \(V^\mu\coloneqq(V^0,V^1,V^2,V^3)\), then

\[
V_\mu\coloneqq\eta_{\mu\nu}V^\nu
\overset{+---}{=}
(V^0,-V^1,-V^2,-V^3)
\]

in the \(+---\) convention. This is why the scalar product is written

\[
V_\mu V^\mu
\overset{\text{metric}}{=}
(V^0)^2-(V^1)^2-(V^2)^2-(V^3)^2.
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
\Lambda^T\eta\Lambda\overset{\text{Lorentz}}{=}\eta.
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
for the metric-as-geometry bridge. Section-level locators are now recorded in `data/reference_links.csv`.

### Graphics

Revised the existing graphic. The new version keeps the matrix idea but makes
the metric visibly act as a measuring rule: a displacement on \(x,ct\) axes is
fed through \(\eta\) to produce an \(s^2\) interval expression.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

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
\Delta s^2\coloneqq c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2.
\]

Equivalently, using the \cref{Metric tensor}{sr.metric_tensor},

\[
\Delta s^2\equiv\eta_{\mu\nu}\Delta x^\mu\Delta x^\nu.
\]

The interval is built from a separation, not from one event in isolation. If
two events have coordinates \(x_1^\mu\) and \(x_2^\mu\), form

\[
\Delta x^\mu\coloneqq x_2^\mu-x_1^\mu.
\]

This removes the arbitrary choice of coordinate origin and leaves the
displacement whose invariant square is measured.

Contracting the separation with the metric gives the usual interval formula.
For

\[
\Delta x^\mu\coloneqq(c\Delta t,\Delta x,\Delta y,\Delta z)
\]

and \(\eta_{\mu\nu}\coloneqq\mathrm{diag}(1,-1,-1,-1)\), the contraction
\(\eta_{\mu\nu}\Delta x^\mu\Delta x^\nu\) expands to

\[
\Delta s^2
\overset{\text{metric}}{=}
c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2.
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

For light travelling in one spatial dimension, \(\Delta x\overset{\text{light}}{=}c\Delta t\), so the
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
- `sr.spacetime_interval.classification`, `result`, "Timelike lightlike spacelike".
- `sr.spacetime_interval.invariant_not_components`, `misconception`, "Invariant does not mean unchanged components".
- `sr.spacetime_interval.light_and_proper_time`, `explanation`, "Light and clocks".
- `sr.spacetime_interval.why_it_matters`, `summary`, "Why the interval matters".

### Study Questions

Drafted in `data/study_questions.csv` as five questions: an invariant-quantity
multiple-choice check, a sign-meaning explanation, two classification
calculations, and one invariant-versus-components misconception check.

### References

Linked broadly to `TTM II` for the interval definition and `TRR` for interval
and causal-classification background. Section-level locators are now recorded in `data/reference_links.csv`.

### Graphics

Retain the existing graphic. The diagram already shows representative
timelike, spacelike, and lightlike separations from one event, which is the
right visual emphasis for this concept.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

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
\beta\coloneqq\frac{v}{c}, \qquad
\gamma\coloneqq\frac{1}{\sqrt{1-\beta^2}}.
\]

The origins coincide at \(t\overset{\text{shared origin}}{=}t'\overset{\text{shared origin}}{=}0\), and only the \(ct\) and \(x\) coordinates
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
ds^2\coloneqq c^2dt^2-dx^2-dy^2-dz^2
    \overset{\text{Lorentz invariant}}{=}
    c^2dt'^2-dx'^2-dy'^2-dz'^2.
\]

This interval-preservation condition is what turns the relativity postulates
into a spacetime transformation law.

For a boost along the \(x\)-axis, the Lorentz transformation is

\[
ct'\overset{\text{boost}}{=}\gamma(ct-\beta x), \qquad
x'\overset{\text{boost}}{=}\gamma(x-\beta ct), \qquad
y'\overset{\text{boost}}{=}y, \qquad
z'\overset{\text{boost}}{=}z.
\]

The \(\text{boost}\) label marks that these equalities use the standard \(x\)-directed
Lorentz boost, not an arbitrary algebraic rearrangement.
The inverse transformation is obtained by replacing \(\beta\) with \(-\beta\).
The factor \(\gamma\) becomes large as \(v\) approaches \(c\), encoding the
growing difference between Galilean and relativistic kinematics.

The interval check is worth seeing once. Substitute the boost equations into
\(c^2dt'^2-dx'^2\):

\[
c^2dt'^2-dx'^2
\overset{\text{boost}}{=}
\gamma^2[(cdt-\beta dx)^2-(dx-\beta cdt)^2].
\]

Expanding and cancelling the cross terms gives

\[
\gamma^2(1-\beta^2)(c^2dt^2-dx^2)
\overset{\gamma}{=}
c^2dt^2-dx^2,
\]

because \(\gamma^2(1-\beta^2)\equiv1\). The unchanged \(y\) and \(z\) components
complete the four-dimensional interval check.

In four-vector notation, with \(x^\mu\coloneqq(ct,x,y,z)\), a Lorentz transformation is
written

\[
x'^\mu\overset{\text{Lorentz}}{=}\Lambda^\mu{}_{\nu}x^\nu.
\]

The \(\text{Lorentz}\) label marks the transformation law for four-vector components.
Preservation of the metric is expressed by

\[
\eta_{\alpha\beta}\Lambda^\alpha{}_{\mu}\Lambda^\beta{}_{\nu}
\overset{\text{metric preservation}}{=}\eta_{\mu\nu},
\]

or, in matrix notation,

\[
\Lambda^T\eta\Lambda\overset{\text{metric preservation}}{=}\eta.
\]

The \(\text{metric preservation}\) label names the condition that makes \(\Lambda\) a
Lorentz transformation. This is the compact version of the
interval-preservation rule.

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
- `sr.lorentz_transformations.boost_formula`, `result`, "Boost along \(x\)".
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
Section-level TRR locator is now recorded in `data/reference_links.csv`.

### Graphics

Retain the existing graphic. Tilted primed axes and unprimed axes describing
the same event \(P\) communicate the coordinate-change interpretation directly.
No SVG code change is needed in this pass.

### Drafting Issues

#### Source Issues

- Section-level TRR locator for the matrix/metric preservation viewpoint is recorded in `data/reference_links.csv`.

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
\Delta s^2\coloneqq c^2\Delta t^2-\Delta x^2-\Delta y^2-\Delta z^2
\overset{\text{null}}{=}0.
\]

Equivalently,

\[
|\Delta \mathbf x|\overset{\text{null}}{=}c|\Delta t|.
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

The light cone is defined by \(\Delta s^2\overset{\text{null}}{=}0\), and
\cref{Lorentz transformations}{sr.lorentz_transformations} preserve
\(\Delta s^2\). Different inertial observers may draw different coordinate axes
through the same event, but they agree which separations are timelike,
lightlike, and spacelike.

Being outside the light cone is not the same as being far away in ordinary
space. A nearby event can be outside the cone if too little time has elapsed for
a signal to reach it. A distant event can be inside the future cone if enough
time has elapsed. The comparison is always between spatial separation and
elapsed time multiplied by \(c\).

In a one-space-one-time diagram, light satisfies \(x\overset{\text{light}}{=}\pm ct\), so the cone
boundary is drawn as two 45-degree lines. With two space dimensions plus time,
those lines become a cone. In three space dimensions, each moment after the
event gives an expanding sphere of light; stacking those spheres through time
gives the cone picture.

### Block Plan

- `sr.light_cone.overview`, `overview`, "Causal map from one event".
- `sr.light_cone.definition`, `definition`, "Definition".
- `sr.light_cone.null_condition`, `result`, "Null interval condition".
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
causal-structure background. Section-level locators are now recorded in `data/reference_links.csv`.

### Graphics

Retain the existing graphic. This is the concept where the 45-degree cone
boundary should dominate, and the current graphic keeps that geometry clean.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

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
x\overset{\text{light}}{=}\pm ct
\]

and appear as 45-degree lines. This convention makes the causal structure
visible without writing the interval formula every time.

A curve through many events is a worldline: the history of a particle, clock,
detector, or light pulse. A vertical worldline represents something at rest in
the chosen frame. A tilted timelike worldline represents slower-than-light
motion. A 45-degree worldline represents light.

Axes for a moving inertial frame are drawn using the Lorentz transformations.
The \(ct'\)-axis is the worldline of the moving frame's spatial origin, so it
satisfies \(x'\overset{ct'\text{-axis}}{=}0\), which gives \(x\overset{x'=0}{=}vt\). The \(x'\)-axis is the line of
simultaneity \(t'\overset{x'\text{-axis}}{=}0\), which gives \(ct\overset{t'=0}{=}\beta x\) for a standard boost.

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
- `sr.minkowski_diagram.axes`, `convention`, "Axes and units".
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
spacetime-geometry background. Section-level locators are now recorded in `data/reference_links.csv`.

### Graphics

Retain the existing graphic. The rest worldline, slower-than-light worldline,
and single light ray give this concept a distinct visual identity from the
full light-cone graphic.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

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
ds^2\overset{\text{interval}}{=}c^2dt^2-d\mathbf x^2.
\]
For a timelike segment we define
\[
ds^2\coloneqq c^2d\tau^2,
\]
so \(d\tau\) is the small amount of proper time accumulated along that segment
of the worldline. For a finite path, the clock reading is obtained by summing,
or integrating, those small contributions:
\[
\Delta\tau\coloneqq\int d\tau.
\]

For motion at speed \(v\coloneqq|d\mathbf x|/dt\) in one inertial frame, \(d\mathbf x^2=v^2dt^2\), so
\[
c^2d\tau^2\overset{\text{proper time}}{=}c^2dt^2-v^2dt^2
  =c^2dt^2\left(1-\frac{v^2}{c^2}\right).
\]
Taking the future-directed positive root gives
\[
d\tau=dt\sqrt{1-\frac{v^2}{c^2}}\overset{\gamma}{=}\frac{dt}{\gamma}.
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

Lightlike paths are a useful warning. For light, \(ds^2\overset{\text{null}}{=}0\), so the interval
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
- `result`: Constant-speed relation \(d\tau=dt/\gamma\).
- `explanation`: Path dependence.
- `misconception`: Not merely light-signal delay.
- `warning`: Null paths and the absence of a photon rest clock.
- `summary`: Later role in four-velocity and actions.
- `historical_note`: Minkowski spacetime interpretation.

### Study Questions

1. Identify proper time as the reading of a clock along its worldline.
2. Explain why reunited clocks can disagree.
3. Calculate \(d\tau\) for constant speed.
4. Calculate \(d\tau\) from a simple interval in units where \(c\overset{\text{units}}{=}1\).
5. Distinguish proper-time difference from signal delay.

### References

- TTM SR/CF: proper time from the invariant interval; section-level locator recorded in `data/reference_links.csv`.
- TRR: Minkowski/proper-time geometric background; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing clock ticks on a timelike worldline match the concept and should be
retained unless visual inspection shows a concrete defect.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

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
\Delta x^\mu\coloneqq(c\Delta t,\Delta x,\Delta y,\Delta z).
\]
Under a Lorentz transformation,
\[
\Delta x'^\mu\overset{\text{Lorentz}}{=}\Lambda^\mu{}_\nu\Delta x^\nu.
\]
Any object \(A^\mu\) that transforms by the same rule,
\[
A'^\mu\overset{\text{Lorentz}}{=}\Lambda^\mu{}_\nu A^\nu,
\]
is called a four-vector.

This definition is stricter than it first looks. A column of four unrelated
numbers is not automatically a four-vector. The components must mix in exactly
the Lorentz way under boosts and rotations. In that sense a four-vector is one
geometric object, not four independent measurements glued together.

The metric gives four-vectors their invariant scalar products. With the \(+---\)
metric convention,
\[
V_\mu W^\mu\coloneqq\eta_{\mu\nu}V^\mu W^\nu.
\]
Lorentz transformations preserve \(\eta\), so
\[
V'_\mu W'^\mu\overset{\text{Lorentz}}{=}V_\mu W^\mu.
\]
This is the same structural role played by dot products of ordinary vectors
under rotations, except that the spacetime metric has one time sign and three
space signs.

The distinction between upper and lower components matters. The metric lowers
an index:
\[
V_\mu\coloneqq\eta_{\mu\nu}V^\nu.
\]
In standard coordinates this turns \(V^\mu\coloneqq(V^0,V^1,V^2,V^3)\) into
\[
V_\mu\overset{+---}{=}(V^0,-V^1,-V^2,-V^3).
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
- `result`: Invariant scalar products.
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

- TTM SR/CF: four-vector transformation law; section-level locator recorded in `data/reference_links.csv`.
- TRR: Minkowski scalar products and relativistic vector notation; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic captures the correct idea: one spacetime arrow and a linked
component column. Retain unless visual inspection exposes a layout problem.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Upper/lower indices, repeated-index summation, and the \(+---\) convention
  are now covered in `docs/authoring/NOTATION_GLOSSARY.md`; keep this concept aligned as
  the glossary evolves.

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
x^\mu\coloneqq(ct,x,y,z).
\]
The first component is \(ct\), not just \(t\), so that all four components have
dimensions of length. In one-space-one-time diagrams this convention also makes
light rays satisfy \(x\overset{\text{light}}{=}\pm ct\).

The phrase position four-vector needs care. It is not merely the ordinary
spatial position \(\mathbf x\). It is the spacetime coordinate of an event
relative to a chosen origin event. If the origin changes, the components of
\(x^\mu\) change. That is normal coordinate dependence, not a physical problem.

If two inertial frames share an origin event, their coordinate descriptions of
another event are related by the Lorentz transformation law
\[
x'^\mu\overset{\text{Lorentz}}{=}\Lambda^\mu{}_\nu x^\nu.
\]
For a boost along the \(x\)-axis, \(ct\) and \(x\) mix. This is the concrete
reason time and space coordinates are treated as components of one object.

The most physical use of position four-vectors is usually in differences. For
two events,
\[
\Delta x^\mu\coloneqq x_2^\mu-x_1^\mu.
\]
This displacement does not depend on the arbitrary choice of coordinate origin.
Contracting it with the metric gives the spacetime interval:
\[
\Delta s^2\equiv\eta_{\mu\nu}\Delta x^\mu\Delta x^\nu.
\]
So the position four-vector provides the coordinate packaging, while
displacements between position four-vectors supply invariant spacetime
geometry.

For example, if an event occurs at \(t=2\,\mathrm{ns}\), \(x=0.30\,\mathrm m\),
\(y=z=0\), then with \(c\overset{\text{SI}}{=}3.0\times10^8\,\mathrm{m\,s^{-1}}\),
\[
ct=0.60\,\mathrm m,
\]
so \(x^\mu\coloneqq(0.60\,\mathrm m,0.30\,\mathrm m,0,0)\) relative to the chosen
origin.

The later velocity four-vector is obtained by differentiating \(x^\mu\) with
respect to proper time. Thus position four-vectors are not just labels for
events; they are the starting point for relativistic kinematics.

### Block Plan

- `overview`: Event coordinates as one object.
- `definition`: \(x^\mu\coloneqq(ct,x,y,z)\).
- `convention`: Why use \(ct\).
- `explanation`: Dependence on origin event.
- `result`: Lorentz transformation of position.
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

- TTM SR/CF: position four-vector and event coordinates; section-level locator recorded in `data/reference_links.csv`.
- TRR: spacetime position/displacement vector background; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing origin-to-event arrow with projections matches the concept.
Retain unless visual inspection shows a layout problem.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- \(x^\mu\), \(\Delta x^\mu\), and the convention of using \(ct\) are now
  covered in `docs/authoring/NOTATION_GLOSSARY.md`; keep this concept aligned as the
  glossary evolves.

#### Atlas Issues

- None.


## 4.4 `sr.velocity_four_vector`: Velocity four-vector

### Scope

This concept develops four-velocity as \(dx^\mu/d\tau\), a tangent to a
timelike worldline. It should not become a full treatment of acceleration or
force; those belong later.

### Exposition

Ordinary velocity is \(\mathbf v\coloneqq d\mathbf x/dt\). It is useful, but it is tied
to one inertial frame's coordinate time. A relativistic velocity object should
transform as a four-vector, so its denominator must not depend on a particular
observer's clock grid. The invariant clock along a massive particle's worldline
is proper time.

The velocity four-vector is therefore defined by
\[
U^\mu\coloneqq\frac{dx^\mu}{d\tau},
\]
where \(x^\mu\) is the position four-vector and \(\tau\) is proper time. Since
\(x^\mu\) is a four-vector and \(d\tau\) is invariant, \(U^\mu\) transforms as
a four-vector.

Writing \(x^\mu\coloneqq(ct,\mathbf x)\), we have
\[
U^\mu
\overset{\text{components}}{=}
\left(c\frac{dt}{d\tau},\frac{d\mathbf x}{d\tau}\right).
\]
Because \(dt/d\tau\overset{\text{proper time}}{=}\gamma\), and
\[
\frac{d\mathbf x}{d\tau}
 =\frac{d\mathbf x}{dt}\frac{dt}{d\tau}
 =\gamma\mathbf v,
\]
the components in one inertial frame are
\[
U^\mu\overset{\text{proper time}}{=}\gamma(c,\mathbf v).
\]

The fixed norm is an important check. With the \(+---\) metric,
\[
U_\mu U^\mu
\overset{\text{metric}}{=}
\gamma^2(c^2-v^2)
\overset{\gamma}{=}
c^2.
\]
The \(\text{metric}\) label marks the Minkowski contraction, where the spatial part enters
with a minus sign. The \(\gamma\) label marks use of the definition of the
Lorentz factor.
So all massive particles have four-velocity of invariant magnitude \(c\), even
though their ordinary speeds may be different. This is not saying every
particle moves through space at speed \(c\). It is saying that every massive
worldline has the same normalized timelike tangent when parameterized by
proper time.

Geometrically, four-velocity is the future-directed tangent to the particle's
worldline. If the particle accelerates, this tangent changes from event to
event. For a particle at rest in a chosen frame, \(\mathbf v\overset{\text{rest frame}}{=}0\) and
\(\gamma\overset{\mathbf v=0}{=}1\), so
\[
U^\mu\overset{\text{rest frame}}{=}(c,0,0,0).
\]
The spatial part vanishes, but the particle is still moving along its timelike
worldline.

Four-velocity matters because multiplying it by invariant mass gives
four-momentum. It is the kinematic bridge from the geometry of worldlines to
the dynamics of energy, momentum, and force.

### Block Plan

- `overview`: Tangent per unit proper time.
- `definition`: \(U^\mu\coloneqq dx^\mu/d\tau\).
- `explanation`: Why proper time is the denominator.
- `derivation`: \(U^\mu\overset{\text{proper time}}{=}\gamma(c,\mathbf v)\).
- `result`: Fixed norm \(U_\mu U^\mu\overset{\gamma}{=}c^2\).
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

- TTM SR/CF: four-velocity definition and components; section-level locator recorded in `data/reference_links.csv`.
- TRR: timelike worldline and four-velocity geometry; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing tangent-to-worldline graphic fits the concept well. Retain unless
visual inspection shows label crowding.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- None.

#### Atlas Issues

- Four-acceleration may be needed later if the atlas develops relativistic
  dynamics beyond the Lorentz force law.


## 4.5 `sr.momentum_four_vector`: Momentum four-vector

### Scope

This concept packages energy and momentum as one four-vector and derives the
energy-momentum relation. It should prepare mass-energy equivalence but leave
the interpretation of \(E_0\coloneqq mc^2\) mainly to 4.6.

### Exposition

Four-velocity is kinematic: it describes the tangent to a particle's worldline.
Four-momentum is dynamical: it combines energy and momentum into one
relativistic object. For a massive particle,
\[
p^\mu\coloneqq mU^\mu.
\]
Since \(U^\mu\overset{\text{proper time}}{=}\gamma(c,\mathbf v)\), this gives
\[
p^\mu=(\gamma mc,\gamma m\mathbf v).
\]
Identifying
\[
\mathbf p\coloneqq\gamma m\mathbf v,\qquad E\coloneqq\gamma mc^2,
\]
we write
\[
p^\mu\coloneqq(E/c,\mathbf p).
\]

The invariant norm gives the key relation. With the \(+---\) metric,
\[
p_\mu p^\mu\overset{\text{metric}}{=}\frac{E^2}{c^2}-\mathbf p^2.
\]
The \(\text{metric}\) label marks the expansion of the four-momentum contraction using the
\(+---\) metric.
But \(p^\mu\coloneqq mU^\mu\), and \(U_\mu U^\mu\overset{\text{four-velocity}}{=}c^2\), so
\[
p_\mu p^\mu\overset{p=mU}{=}m^2c^2.
\]
The \(p=mU\) label marks substituting the definition of four-momentum and the
fixed norm of four-velocity.
Equating these two expressions gives
\[
\frac{E^2}{c^2}-\mathbf p^2\overset{\text{mass shell}}{=}m^2c^2,
\]
or
\[
E^2\overset{\text{mass shell}}{=}\mathbf p^2c^2+m^2c^4.
\]
The \(\text{mass shell}\) label names the physical invariant-mass condition for the
particle, rewritten here as an energy relation.

Energy and three-momentum are therefore not separate relativistic bookkeeping
systems. They are components of one four-vector. Different observers may assign
different values of \(E\) and \(\mathbf p\), but they are describing the same
object, and they agree on its invariant norm.

The rest frame makes the structure especially clear. In the rest frame of a
massive particle, \(\mathbf v\overset{\text{rest frame}}{=}0\), \(\gamma\overset{\mathbf v=0}{=}1\), and \(\mathbf p\overset{\text{rest frame}}{=}0\), so
\[
p^\mu\overset{\text{rest frame}}{=}(mc,\mathbf 0).
\]
The time component remains nonzero. This is the immediate doorway to rest
energy and mass-energy equivalence.

There is one important warning. The construction \(p^\mu\coloneqq mU^\mu\) assumes a
massive particle with proper time along its worldline. Massless particles have
no rest frame and no proper time parameter, but they still have four-momentum.
For them \(p_\mu p^\mu\overset{\text{massless}}{=}0\) and \(E\overset{\text{massless}}{=}|\mathbf p|c\).

### Block Plan

- `overview`: Energy and momentum as one object.
- `definition`: \(p^\mu\coloneqq mU^\mu\coloneqq(E/c,\mathbf p)\).
- `derivation`: Components from four-velocity.
- `derivation`: Invariant norm.
- `result`: Energy-momentum relation.
- `explanation`: Frame-dependent components.
- `example`: Rest frame.
- `misconception`: Not Newtonian momentum plus a label.
- `warning`: Massless particles.
- `summary`: Role in relativistic dynamics.

### Study Questions

1. Identify \(p^\mu\coloneqq mU^\mu\coloneqq(E/c,\mathbf p)\).
2. Explain frame-dependent energy/momentum components.
3. Compute \(E\) and \(|\mathbf p|\) for a simple massive particle.
4. Check the invariant mass relation.
5. Describe the rest-frame four-momentum.
6. Explain the massless-particle caveat.

### References

- TTM SR/CF: four-momentum and energy-momentum relation; section-level locator recorded in `data/reference_links.csv`.
- TRR: mass shell/four-momentum geometry; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic correctly pairs a \(p^\mu\) arrow with \(E/c\) and
\(\mathbf p\) components. Retain unless visual inspection shows crowding.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- The atlas may eventually need a concept or block style for massless limits.

#### Atlas Issues

- Consider whether `mass shell` deserves a separate concept when QM or particle
  physics content is added.


## 4.6 `sr.mass_energy_equivalence`: Mass-energy equivalence

### Scope

This concept explains \(E_0\coloneqq mc^2\) as rest energy derived from the
four-momentum norm. It should include interpretation and common mistakes, but
not become a full treatment of nuclear physics, binding energy calculations, or
particle reactions.

### Exposition

Mass-energy equivalence is the statement that invariant mass corresponds to
rest energy:
\[
E_0\coloneqq mc^2.
\]
The subscript is useful. This is rest energy, the energy of a massive system in
the frame where its total three-momentum is zero.

The clean derivation comes from four-momentum. Write
\[
p^\mu\coloneqq(E/c,\mathbf p).
\]
Its invariant norm is computed using the Minkowski metric; the \(\text{metric}\) label
marks that expansion:
\[
p_\mu p^\mu
\overset{\text{metric}}{=}
\frac{E^2}{c^2}-\mathbf p^2.
\]
For a particle or system of invariant mass \(m\), the \(\text{mass shell}\) label marks
the physical condition that this invariant norm is fixed by the rest mass:
\[
p_\mu p^\mu
\overset{\text{mass shell}}{=}
m^2c^2.
\]
Multiplying by \(c^2\) gives the energy-momentum relation
\[
E^2=\mathbf p^2c^2+m^2c^4.
\]

Now choose the rest frame, where the total spatial momentum vanishes:
\[
\mathbf p\overset{\text{rest frame}}{=}0.
\]
Substituting that zero momentum into the energy-momentum relation removes the
momentum term:
\[
E^2\overset{\mathbf p=0}{=}m^2c^4.
\]
Taking the positive physical root gives
\[
E_0\coloneqq E\big|_{\mathbf p=0}\overset{E>0}{=}mc^2.
\]
The \(E>0\) label marks the choice of the positive energy branch.

This is easy to remember and easy to misread. It is not saying that total
energy is always just \(mc^2\). For a moving massive particle, total energy is
\(E=\gamma mc^2\). The rest-energy statement is the zero-momentum case of the
full relation.

It is also not best understood as a magical conversion of one substance called
mass into another substance called energy. In relativity, invariant mass is a
measure of a system's total energy-momentum content. If a closed system loses
rest energy \(\Delta E_0\), the rest-energy formula can be read as a relation
between energy change and mass change:
\[
\Delta m\overset{E_0=mc^2}{=}\frac{\Delta E_0}{c^2}.
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
- `definition`: \(E_0\coloneqq mc^2\) and the full relation.
- `derivation`: From four-momentum norm.
- `result`: Rest-frame limit.
- `explanation`: Applies to systems.
- `misconception`: Not magic substance conversion.
- `example`: \(\Delta m\overset{E_0=mc^2}{=}\Delta E_0/c^2\).
- `warning`: Total energy is not always \(mc^2\).
- `historical_note`: Einstein's 1905 result.
- `summary`: Why it matters.

### Study Questions

1. Identify rest energy.
2. Explain why the full energy-momentum relation matters.
3. Derive \(E_0\coloneqq mc^2\) by setting \(\mathbf p=0\).
4. Calculate \(\Delta m\) from an energy loss.
5. Explain why heating a sealed box changes invariant mass.
6. Explain why "mass turns into energy" can mislead.

### References

- TTM SR/CF: mass-energy relation from four-momentum norm; section-level locator recorded in `data/reference_links.csv`.
- TRR: relativistic energy-momentum and mass-energy discussion; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic rightly keeps \(E=mc^2\) central while showing the
four-momentum norm below. Retain unless visual inspection shows crowding.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

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
S\coloneqq\int L(q,\dot q,t)\,dt.
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
\(c\overset{\text{units}}{=}1\) often makes the symmetry clearer, but \(c\) can be restored when
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
- `definition`: \(L(q,\dot q,t)\) and \(S\coloneqq\int Ldt\).
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

- TTM SR/CF: Lagrangian and action setup; section-level locator recorded in `data/reference_links.csv`.
- TRR: Lagrangian/action and invariant-building background; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing local \(L\) tiles accumulating into \(S\) match the intended
meaning. Retain unless visual inspection shows layout problems.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- \(L\), action \(S\), and field Lagrangian density \(\mathcal L\) are now
  covered in `docs/authoring/NOTATION_GLOSSARY.md`; keep this concept aligned as the
  glossary evolves.

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
S[q]\coloneqq\int_{t_1}^{t_2}L(q,\dot q,t)\,dt.
\]
The physical history is the one for which the first-order change in \(S\)
vanishes under small allowed variations:
\[
\delta S\overset{\text{stationary}}{=}0.
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
q_a(t)\coloneqq q(t)+a\,\eta(t),
\]
then \(\eta(t_1)\overset{\text{fixed endpoints}}{=}\eta(t_2)\overset{\text{fixed endpoints}}{=}0\). The action becomes a function \(S(a)\), and
stationarity of the original path is
\[
\left.\frac{dS}{da}\right|_{a=0}\overset{\text{stationary}}{=}0.
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
- `definition`: \(S[q]\coloneqq\int Ldt\), \(\delta S\overset{\text{stationary}}{=}0\).
- `intuition`: Compare nearby histories.
- `misconception`: Stationary is not always smallest.
- `construction`: Fixed endpoints.
- `derivation_step`: One-parameter variation.
- `explanation`: Relativistic scalar actions.
- `summary`: From global rule to local equations.
- `historical_note`: Least action to stationary action.

### Study Questions

1. Recognize \(\delta S\overset{\text{stationary}}{=}0\).
2. Explain fixed endpoints.
3. Explain why "least" can mislead.
4. Check stationarity for a quadratic \(S(a)\).
5. Check non-stationarity for a linear term.
6. Explain why relativistic actions should be scalar.

### References

- TTM SR/CF: action principle setup; section-level locator recorded in `data/reference_links.csv`.
- TRR: stationary action and variational principles; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing fixed-endpoint path variation graphic matches the intended
meaning. Retain unless visual inspection shows a concrete defect.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- A future derivation trace could show \(L\rightarrow S\rightarrow\delta S\overset{\text{stationary}}{=}0
  \rightarrow\) Euler-Lagrange equations.

#### Atlas Issues

- None.


## 5.3 `sr.euler_lagrange_equations`: Euler-Lagrange equations

### Scope

This concept derives the Euler-Lagrange equations from stationary action for
particle coordinates. It should not yet become field Euler-Lagrange theory,
though it may point forward to field equations.

### Exposition

The action principle says \(\delta S\overset{\text{stationary}}{=}0\). The Euler-Lagrange equations are what
that statement becomes as local differential equations of motion.

For one coordinate, start from
\[
S\coloneqq\int_{t_1}^{t_2}L(q,\dot q,t)\,dt.
\]
Vary the path while holding the endpoints fixed:
\[
q(t)\rightarrow q(t)+\delta q(t),\qquad
\delta q(t_1)\overset{\text{fixed endpoints}}{=}\delta q(t_2)\overset{\text{fixed endpoints}}{=}0.
\]
The velocity varies too, so \(\dot q\rightarrow \dot q+\delta\dot q\).

The first-order variation of the action is
\[
\delta S\overset{\text{variation}}{=}\int_{t_1}^{t_2}\left(
\frac{\partial L}{\partial q}\delta q+
\frac{\partial L}{\partial\dot q}\delta\dot q
\right)dt.
\]
The second term contains \(\delta\dot q\). Since
\(\delta\dot q\coloneqq d(\delta q)/dt\), integrate by parts:
\[
\int_{t_1}^{t_2}\frac{\partial L}{\partial\dot q}\delta\dot q\,dt
\overset{\text{parts}}{=}
\left[\frac{\partial L}{\partial\dot q}\delta q\right]_{t_1}^{t_2}
-\int_{t_1}^{t_2}
\frac{d}{dt}\left(\frac{\partial L}{\partial\dot q}\right)\delta q\,dt.
\]
The boundary term vanishes because the endpoint variations are zero.

So
\[
\delta S\overset{\text{parts}}{=}\int_{t_1}^{t_2}\left[
\frac{\partial L}{\partial q}
-\frac{d}{dt}\left(\frac{\partial L}{\partial\dot q}\right)
\right]\delta q\,dt.
\]
The variation \(\delta q(t)\) can be chosen freely between the endpoints. The
only way for \(\delta S\overset{\text{stationary}}{=}0\) to hold for every such variation is for the bracket
to vanish at every time:
\[
\frac{d}{dt}\left(\frac{\partial L}{\partial\dot q}\right)
-\frac{\partial L}{\partial q}\overset{\text{stationary action}}{=}0.
\]
The \(\text{stationary action}\) label marks that this equation is imposed by requiring
the first variation of the action to vanish for arbitrary allowed variations.

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

- TTM SR/CF: Euler-Lagrange equations from stationary action; section-level locator recorded in `data/reference_links.csv`.
- TRR: variational calculus and Euler-Lagrange derivation; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing variation-to-E-L graphic matches the concept. Retain unless visual
inspection shows crowding.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

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
p_i\coloneqq\frac{\partial L}{\partial \dot q_i}.
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
p\coloneqq\frac{\partial L}{\partial\dot x}=m\dot x.
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
\mathbf p_{\rm can}\coloneqq m\mathbf v+e\mathbf A.
\]
The mechanical momentum is still \(m\mathbf v\), while the canonical momentum
also contains the vector potential. This is not a paradox: canonical momentum
belongs to the variational and Hamiltonian structure.

Canonical momentum is the hinge used to pass to Hamiltonian mechanics. If the
relations
\[
p_i\coloneqq\frac{\partial L}{\partial\dot q_i}
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
- `definition`: \(p_i\coloneqq\partial L/\partial\dot q_i\).
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
  section-level locator recorded in `data/reference_links.csv`.
- TRR: conjugate momentum and Hamiltonian phase-space background; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The current graphic showing \(L(q,\dot q)\) feeding \(p=\partial L/\partial
\dot q\) is conceptually appropriate. Check whether the detail graphic has
enough room for the derivative notation.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Canonical momentum and four-momentum are now covered in
  `docs/authoring/NOTATION_GLOSSARY.md`; mechanical momentum and relativistic
  three-momentum may still deserve explicit entries when the atlas develops
  mechanics notation further.

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
p_i\coloneqq\frac{\partial L}{\partial\dot q_i}.
\]
If these relations can be solved for the velocities \(\dot q_i\) in terms of
\(q_i,p_i,t\), define
\[
H(q,p,t)\coloneqq\sum_i p_i\dot q_i-L(q,\dot q,t),
\]
where the velocities on the right have been re-expressed in terms of
\(q,p,t\). This is a Legendre transform. It changes the independent variables
from velocities to momenta.

Phase space gives a different picture of motion. At one instant the system is a
point with coordinates \((q_i,p_i)\). As time passes, that point traces a curve.
The Hamiltonian determines the flow of this curve.

The equations of motion are Hamilton's equations:
\[
\dot q_i\overset{\text{Hamilton}}{=}\frac{\partial H}{\partial p_i},\qquad
\dot p_i\overset{\text{Hamilton}}{=}-\frac{\partial H}{\partial q_i}.
\]
The \(\text{Hamilton}\) labels mark that these are Hamilton's evolution equations, not
definitions of the partial derivatives.
They are first-order equations in phase space. When the Legendre transform is
valid, they are equivalent to the Euler-Lagrange equations.

For one coordinate, the structure can be seen by differentiating
\[
H\coloneqq p\dot q-L.
\]
Treat \(\dot q\) as the velocity already expressed in terms of \(q,p,t\). Then
\[
dH=\dot q\,dp+p\,d\dot q-\frac{\partial L}{\partial q}dq
-\frac{\partial L}{\partial\dot q}d\dot q.
\]
Because \(p\coloneqq\partial L/\partial\dot q\), the two \(d\dot q\) terms cancel.
Using the Euler-Lagrange equation, \(dp/dt\overset{\text{Euler-Lagrange}}{=}\partial L/\partial q\), gives
\[
dH\overset{\text{Euler-Lagrange}}{=}\dot q\,dp-\dot p\,dq,
\]
which is Hamilton's equation in differential form.

For
\[
L=\frac12m\dot x^2-V(x),
\]
we have \(p\coloneqq m\dot x\), so \(\dot x=p/m\). The Hamiltonian becomes
\[
H\coloneqq p\dot x-L
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
4. Compute \(\dot x\) from \(H\coloneqq p^2/(2m)+V(x)\).
5. Compute \(\dot p\) from the same Hamiltonian.
6. Explain why \(H\) is not simply defined as energy.

### References

- TTM SR/CF: Hamiltonian formalism and Legendre transform; section-level locator recorded in `data/reference_links.csv`.
- TRR: Hamiltonian mechanics as phase-space structure and route toward quantum
  theory; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing phase-space flow graphic is well matched to the concept. Retain
unless visual inspection shows label or arrow crowding.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

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
terms disappear. What remains is a total derivative. The \(\text{conservation}\) label
marks the step where that derivative is zero on physical solutions:
\[
\frac{dQ}{dt}\overset{\text{conservation}}{=}0
\]
in mechanics, or
\[
\partial_\mu J^\mu\overset{\text{conservation}}{=}0
\]
in field theory. The remaining object \(Q\), or current \(J^\mu\), is the
conserved quantity.

The standard examples are worth remembering. Invariance under time translations
gives conservation of energy. Invariance under spatial translations gives
conservation of momentum. Invariance under rotations gives conservation of
angular momentum. The slogan is not "symmetry is pretty"; it is "continuous
symmetry of the action implies conserved quantity."

A simple mechanics example is a cyclic coordinate. If \(q\) does not appear in
the Lagrangian, the \(\text{cyclic}\) label marks that the Lagrangian has no direct
dependence on that coordinate:
\[
\frac{\partial L}{\partial q}\overset{\text{cyclic}}{=}0.
\]
The Euler-Lagrange equation then turns this absence into a conservation
statement:
\[
\frac{d}{dt}\left(\frac{\partial L}{\partial\dot q}\right)
\overset{\text{Euler-Lagrange}}{=}0.
\]
But \(\partial L/\partial\dot q\) is the canonical momentum \(p\). Therefore
the momentum conjugate to that coordinate is conserved. Translation symmetry is
the familiar case where this gives conservation of linear momentum.

In field theory, Noether's theorem usually produces a conserved current. The
conservation condition is local: the four-divergence of the current vanishes,
\[
\partial_\mu J^\mu\overset{\text{conservation}}{=}0.
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

- TTM SR/CF: Noether theorem and action symmetries; section-level locator recorded in `data/reference_links.csv`.
- TRR: Noether theorem, conservation laws, and symmetry in modern field theory;
  section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic uses an implication symbol from an unchanged action to a
conserved \(Q\), which matches the current concept scope. Retain unless visual
inspection shows label crowding.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- This concept would benefit from future disclosure blocks for the exact
  mechanics derivation and the field-current derivation.

#### Atlas Issues

- Future edge types might distinguish "symmetry yields conservation law" from
  ordinary derivation or relatedness.


## 6.1 `sr.scalar_field`: Scalar field

### Scope

This concept introduces scalar fields as the simplest local field objects: one
observer-independent value per spacetime event. It should prepare field
Lagrangians and field equations, while leaving vector fields and electromagnetic
tensors to later concepts.

### Exposition

A scalar field assigns one number to each spacetime event. If \(x\) denotes an
event, the field value is written
\[
\phi(x).
\]
The important relativistic statement is not that \(\phi\) is the same
everywhere. It is that the value assigned to a particular physical event is the
same for every inertial observer. If one observer labels the event by \(x\) and
another by \(x'\), then
\[
\phi'(x')\overset{\text{scalar}}{=}\phi(x).
\]
The \(\text{scalar}\) label marks that the field value is invariant even though
the coordinate label of the event changes.

This is why a temperature field is a useful analogy. At each place and time
there is one temperature value, not an arrow. The temperature can still vary
from point to point. Likewise, a scalar field in spacetime can have rich local
structure while remaining scalar in its transformation law.

The contrast with four-vectors is instructive. A four-vector has components
that mix under Lorentz transformations. A scalar field has no component list to
mix. Its coordinate argument changes when observers relabel spacetime, but the
value at the event does not.

Although \(\phi\) itself is scalar, its derivatives carry directional
information. Quantities such as \(\partial_\mu\phi\) describe how the field
changes from event to event, and these derivatives are natural ingredients in
field Lagrangians. This is how a single value at each event can still support
local dynamics and wave-like behavior.

Scalar fields are useful first examples for field theory because they isolate
the idea of a field without vector or tensor complications. They let us study
locality, variation, field equations, and relativistic covariance in a simple
setting.

### Block Plan

- `overview`: One number at each event.
- `definition`: \(\phi(x)\) and \(\phi'(x')\overset{\text{scalar}}{=}\phi(x)\).
- `intuition`: Local value, not one global number.
- `explanation`: Same event, different coordinates.
- `explanation`: Contrast with four-vectors.
- `example`: Examples and analogies.
- `construction`: Derivatives carry direction.
- `misconception`: Scalar does not mean constant.
- `summary`: Role in field theory.
- `historical_note`: Simple field object.

### Study Questions

1. Recognize a scalar field.
2. Interpret \(\phi'(x')\overset{\text{scalar}}{=}\phi(x)\).
3. Explain why scalar does not mean constant.
4. Evaluate a simple scalar field at an event.
5. Contrast scalar and four-vector transformation behavior.
6. Explain why scalar fields are useful first field examples.

### References

- TTM SR/CF: scalar fields as simple relativistic field variables; section-level locator recorded in `data/reference_links.csv`.
- TRR: scalar versus vector/tensor transformation behavior; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic, showing differently sized scalar values over a spacetime
grid, matches the concept. Retain unless review shows crowding.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- The event \(x\), coordinate tuple \(x^\mu\), and scalar field value
  \(\phi(x)\) are now covered in `docs/authoring/NOTATION_GLOSSARY.md`; keep this concept
  aligned as the glossary evolves.

#### Atlas Issues

- Scalar field derivatives may eventually deserve a small linked notation
  concept if field-theory calculations become more detailed.


## 6.2 `sr.vector_field`: Vector field

### Scope

This concept introduces vector fields as local assignments of four-vector-like
objects to spacetime events. It should contrast them with scalar fields and
prepare the electromagnetic vector potential without teaching gauge theory or
the field tensor in full.

### Exposition

A vector field assigns a vector-like object to each spacetime event. If \(x\)
denotes the event, a typical notation is
\[
A^\mu(x).
\]
The field can vary from event to event, but at each event its components must
transform as a four-vector:
\[
A'^\mu(x')\overset{\text{Lorentz}}{=}\Lambda^\mu{}_{\nu}A^\nu(x).
\]
The \(\text{Lorentz}\) label marks the four-vector transformation law applied
at the same physical event.

This notation contains two ideas at once. The argument \(x\) is the coordinate
label of the event, and that label changes to \(x'\) for another inertial
observer. The component index \(\mu\) describes the four-vector attached to
that event, and those components mix under the Lorentz transformation.

The contrast with a scalar field is useful. A scalar field has one value at an
event, agreed by all inertial observers. A vector field has several components
at the event, and those components change together when the observer changes
frame. Four component functions written in a list are not automatically a
four-vector field; the transformation law is what binds them into one
geometric object.

The main example here is the electromagnetic vector potential \(A_\mu\). It is
a field over spacetime whose derivatives build the electromagnetic field
tensor. That is why vector fields sit naturally between scalar fields and the
tensor description of electromagnetism.

### Block Plan

- `overview`: A vector at every event.
- `definition`: \(A'^\mu(x')\overset{\text{Lorentz}}{=}\Lambda^\mu{}_\nu A^\nu(x)\).
- `intuition`: Local vectors, not one arrow.
- `explanation`: Contrast with scalar fields.
- `warning`: Both argument and components transform.
- `example`: The electromagnetic potential.
- `construction`: Local derivatives.
- `misconception`: Not four unrelated scalar fields.
- `historical_note`: Classical fields and relativistic reorganisation.
- `summary`: Takeaway.

### Study Questions

1. Recognize a vector field.
2. Explain why it is not four scalar fields.
3. Distinguish argument transformation and component transformation.
4. Compute a simple two-component boost.
5. Connect vector fields to the electromagnetic potential.
6. Compare the extra structure beyond scalar fields.

### References

- TTM SR/CF: relativistic vector-field transformation rule; section-level locator recorded in `data/reference_links.csv`.
- TRR: scalar/vector/tensor distinction; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic showing arrows attached to a spacetime grid expresses the
right local-field idea. Retain for this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Contravariant \(A^\mu\), covariant \(A_\mu\), and the electromagnetic
  potential convention are now covered in `docs/authoring/NOTATION_GLOSSARY.md`; keep
  this concept aligned as the glossary evolves.

#### Atlas Issues

- The phrase "vector field" means four-vector field in this relativistic
  layer; later nonrelativistic vector fields may need careful disambiguation.


## 6.3 `sr.field_lagrangian`: Field Lagrangian

### Scope

This concept explains the Lagrangian density and field action. It should link
the action principle to local field theory and prepare field equations, without
doing the full field Euler-Lagrange derivation.

### Exposition

A field Lagrangian is the field-theory version of the Lagrangian idea. For a
particle, the action is an integral over a path:
\[
S\coloneqq\int L\,dt.
\]
For a field, there are degrees of freedom at every spacetime event, so the
action is built from a density:
\[
S[\phi]\coloneqq\int \mathcal L(\phi_a,\partial_\mu\phi_a,x)\,d^4x.
\]

The word density matters. \(\mathcal L\) is not just another symbol for \(L\);
it is the local contribution per spacetime volume. The action adds these local
contributions over a region of spacetime.

Locality constrains what \(\mathcal L\) may depend on. In an ordinary local
field theory, the density at an event is built from field values and derivatives
at that same event. A scalar-field density might use \(\phi\) and
\(\partial_\mu\phi\). An electromagnetic density is naturally written using
the potential \(A_\mu\) and field tensor \(F_{\mu\nu}\).

Relativity adds another strong preference: the action should be a scalar. We
therefore build \(\mathcal L\) from invariant contractions, such as
\(\partial_\mu\phi\partial^\mu\phi\) or \(F_{\mu\nu}F^{\mu\nu}\). Once the
action has been chosen, varying the field throughout a spacetime region gives
the local field equations.

The Lagrangian density should not be confused with energy density. It is the
quantity whose variation produces dynamics. Energy density is extracted from
the energy-momentum tensor, a later concept.

### Block Plan

- `overview`: Action density for fields.
- `definition`: \(S[\phi]\coloneqq\int\mathcal L\,d^4x\).
- `intuition`: Why a density.
- `construction`: Local building blocks.
- `explanation`: Scalar action.
- `example`: Scalar-field pattern.
- `example`: Electromagnetic pattern.
- `construction`: Variation preview.
- `misconception`: Not energy density.
- `historical_note`: Mechanics to field theory.
- `summary`: Takeaway.

### Study Questions

1. Identify the Lagrangian density.
2. Explain why it is a density.
3. State the locality constraint.
4. Compute a constant-density action contribution.
5. Explain why scalar combinations matter.
6. Distinguish Lagrangian density from energy density.

### References

- TTM SR/CF: field action and Lagrangian-density formulation; section-level locator recorded in `data/reference_links.csv`.
- TRR: invariant action and covariant field-theory construction; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic communicates integration of local density over spacetime.
Retain for this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- \(L\), \(\mathcal L\), action \(S\), and \(d^4x\) are now covered in
  `docs/authoring/NOTATION_GLOSSARY.md`; keep this concept aligned as the glossary
  evolves.

#### Atlas Issues

- Energy density is mentioned but belongs to later electromagnetic energy and
  stress-energy concepts.


## 6.4 `sr.field_equations`: Field equations

### Scope

This concept explains field equations as local differential equations for
spacetime fields, especially as equations obtained by varying a field action.
It should prepare Maxwell's equations without presenting all of electromagnetism.

### Exposition

Field equations are the equations of motion for fields. In mechanics the
unknown may be a path \(q(t)\). In field theory the unknown is a function over
spacetime, such as \(\phi_a(x)\). The action is a functional of that whole
field configuration:
\[
S[\phi]\coloneqq\int\mathcal L(\phi_a,\partial_\mu\phi_a,x)\,d^4x.
\]

Varying this action gives the field Euler-Lagrange equations:
\[
\frac{\partial \mathcal L}{\partial \phi_a}
-\partial_\mu\left(
\frac{\partial \mathcal L}{\partial(\partial_\mu\phi_a)}
\right)\overset{\text{stationary action}}{=}0.
\]
The \(\text{stationary action}\) label marks that this field equation is
imposed by requiring the first variation of the field action to vanish.
The derivation follows the same logic as particle mechanics, but with
spacetime derivatives replacing ordinary time derivatives. The variation
contains terms involving \(\partial_\mu\delta\phi_a\); integration by parts
moves the derivative onto its coefficient, and the boundary term is discarded
because the variation is fixed at the boundary.

The result is local. A field equation normally relates field values and
derivatives at an event. It is not a direct instruction from one distant point
to another. This local character is why field equations are usually partial
differential equations.

Relativistic field equations often contain the d'Alembertian
\[
\Box\coloneqq\partial_\mu\partial^\mu
\overset{\text{components}}{=}
\frac{1}{c^2}\frac{\partial^2}{\partial t^2}-\nabla^2.
\]
The \(\text{components}\) label marks the expansion of the covariant operator
in the chosen coordinate convention.
This operator carries the spacetime sign structure and is central in wave-like
relativistic field equations.

Maxwell's equations are the central example in this atlas. In covariant form
they relate the electromagnetic field tensor to the four-current source and
express field propagation locally through spacetime.

### Block Plan

- `overview`: Local rules for fields.
- `definition`: Field equations from varying an action.
- `construction`: From paths to fields.
- `derivation`: Field Euler-Lagrange equation.
- `derivation_step`: Integration by parts.
- `intuition`: Local PDEs.
- `example`: Wave-operator pattern.
- `example`: Maxwell bridge.
- `misconception`: Not just a global constraint.
- `historical_note`: Maxwell before relativity.
- `summary`: Takeaway.

### Study Questions

1. Recognize field equations as local equations of motion.
2. Compare particle and field Euler-Lagrange ideas.
3. Explain the integration-by-parts step.
4. Derive the plane-wave dispersion relation for \(\Box\phi\overset{\text{wave equation}}{=}0\).
5. Explain locality.
6. Connect to Maxwell's equations.

### References

- TTM SR/CF: field Euler-Lagrange equations and field action; section-level locator recorded in `data/reference_links.csv`.
- TRR: covariant wave operator and field equations; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic gives a compact local-equation motif. Retain for this
pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- The d'Alembertian \(\Box\) is now covered in
  `docs/authoring/NOTATION_GLOSSARY.md`; keep this concept aligned as sign conventions
  evolve.

#### Atlas Issues

- A future general "partial differential equation" or "operator" concept may
  be useful if the atlas expands beyond SR/CF.


## 7.1 `sr.vector_potential`: Vector potential \(A_\mu\)

### Scope

This concept introduces the electromagnetic four-potential as a vector field
whose derivatives build the field tensor. It should explain why the potential
is useful and why it is not directly the same as the observable fields, while
leaving detailed gauge fixing to later concepts.

### Exposition

The electromagnetic vector potential \(A_\mu\) is a four-vector field over
spacetime. With one common convention,
\[
A^\mu\coloneqq(\phi/c,\mathbf A),\qquad A_\mu\coloneqq(\phi/c,-\mathbf A),
\]
where \(\phi\) is the scalar potential and \(\mathbf A\) the ordinary
three-vector potential.

The potential is important because its spacetime derivatives build the
electromagnetic field tensor:
\[
F_{\mu\nu}\coloneqq\partial_\mu A_\nu-\partial_\nu A_\mu.
\]
The definition sign marks the local potential convention used here. With that
convention, this antisymmetry is doing real work.
It keeps the curl-like part of the potential's variation and leaves six
independent components, which become the three electric and three magnetic
components after an inertial frame is chosen.

The vector potential is not simply the observed electromagnetic field. The
field strength is \(F_{\mu\nu}\), not \(A_\mu\) itself. Moreover, different
potentials can give the same field tensor:
\[
A_\mu\rightarrow A_\mu+\partial_\mu\Lambda.
\]
The added pure-gradient part cancels out of \(F_{\mu\nu}\) because partial
derivatives commute. This is the beginning of gauge invariance.

In the action formulation, \(A_\mu\) is the electromagnetic field variable that
is varied. A charged particle also couples naturally to it through a scalar
worldline term proportional to \(qA_\mu dx^\mu\). These facts make the vector
potential more than a computational convenience, even though it has gauge
redundancy.

### Block Plan

- `overview`: The potential behind the field.
- `definition`: Four-potential convention.
- `construction`: \(F_{\mu\nu}\) from \(A_\mu\).
- `intuition`: Why antisymmetry.
- `explanation`: Gauge freedom.
- `construction`: Field variable in the action.
- `example`: Coupling to charge.
- `misconception`: Not simply the observed field.
- `historical_note`: Potentials become central.
- `summary`: Takeaway.

### Study Questions

1. Identify what the vector potential constructs.
2. Distinguish potential from observed field.
3. Explain why pure-gradient additions cancel.
4. Package \(\phi\) and \(\mathbf A\) into \(A^\mu\).
5. Explain the action/coupling role.
6. State the significance of gauge freedom.

### References

- TTM SR/CF: four-potential convention and electromagnetic potential
  formulation; section-level locator recorded in `data/reference_links.csv`.
- TRR: potential, field strength, and gauge redundancy; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic shows a potential feeding a derivative/field-strength
construction. Retain for this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Gauge-related notation \(\Lambda\), \(A_\mu\), and \(F_{\mu\nu}\) is now
  covered in `docs/authoring/NOTATION_GLOSSARY.md`; keep this concept aligned as
  convention handling evolves.

#### Atlas Issues

- The edge vocabulary may eventually want a sharper "CONSTRUCTS" relation for
  \(A_\mu\rightarrow F_{\mu\nu}\), rather than using only `DERIVES_FROM` from
  field tensor to vector potential.


## 7.2 `sr.field_tensor`: Field tensor \(F_{\mu\nu}\)

### Scope

This concept introduces \(F_{\mu\nu}\) as the covariant electromagnetic field
strength. It should cover construction from the vector potential,
antisymmetry, the six-component count, and the observer-dependent split into
electric and magnetic fields.

### Exposition

The electromagnetic field tensor is the covariant package for classical
electromagnetism. Starting from the vector potential,
\[
F_{\mu\nu}\coloneqq\partial_\mu A_\nu-\partial_\nu A_\mu.
\]
This is the local potential convention used in this atlas; signs and factors
are fixed only after the potential and coordinate conventions are fixed.
This immediately gives
\[
F_{\mu\nu}\overset{\text{antisymmetry}}{=}-F_{\nu\mu}.
\]
The \(\text{antisymmetry}\) label marks the consequence of swapping the two
derivative terms.

Antisymmetry is not decorative. A general \(4\times4\) tensor has sixteen
entries. Antisymmetry sets the four diagonal entries to zero and pairs each
off-diagonal entry with an opposite-sign partner. That leaves six independent
components.

Those six components are physically suggestive. After choosing an inertial
frame, the time-space components are identified with the electric field, while
the spatial antisymmetric components are identified with the magnetic field.
Signs and factors of \(c\) depend on the convention for \(x^0\), \(A^\mu\),
index placement, and metric signature.

The tensor view explains why electric and magnetic fields mix between
observers. A Lorentz boost mixes time and space directions. Since \(\mathbf E\)
comes from time-space components and \(\mathbf B\) from space-space components,
another observer can split the same \(F_{\mu\nu}\) differently.

The construction from \(A_\mu\) also builds in a structural identity. Cyclic
derivatives of \(F_{\mu\nu}\) cancel because partial derivatives commute. In
three-vector language, this becomes the homogeneous half of Maxwell's
equations.

### Block Plan

- `overview`: One tensor for electromagnetism.
- `definition`: \(F_{\mu\nu}\coloneqq\partial_\mu A_\nu-\partial_\nu A_\mu\).
- `construction`: Antisymmetry.
- `intuition`: Six components.
- `explanation`: Frame split into \(\mathbf E\) and \(\mathbf B\).
- `warning`: Index placement and metric signs.
- `explanation`: Lorentz mixing.
- `construction`: Homogeneous-structure hint.
- `misconception`: Not two unrelated fields.
- `historical_note`: Minkowski formulation.
- `summary`: Takeaway.

### Study Questions

1. Recognize \(F_{\mu\nu}\) as the unified relativistic object.
2. Interpret its definition from \(A_\mu\).
3. Count independent antisymmetric components.
4. Read off electric and magnetic parts.
5. Explain Lorentz mixing.
6. Explain convention sensitivity of index placement.

### References

- TTM SR/CF: electromagnetic field tensor construction from the four-potential;
  section-level locator recorded in `data/reference_links.csv`.
- TRR: unification and Lorentz mixing of electric and magnetic components;
  section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing tensor-matrix graphic is appropriate. Retain for this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Sign conventions for \(F_{\mu\nu}\), \(F^{\mu\nu}\), and the \(E/B\) split
  are now flagged in `docs/authoring/NOTATION_GLOSSARY.md`; continue stating local
  conventions near detailed calculations.

#### Atlas Issues

- The field tensor really wants a richer edge type for "constructed from" the
  vector potential.


## 7.3 `sr.electric_field`: Electric field

### Scope

This concept explains the electric field as the frame-dependent time-space
part of the electromagnetic field tensor, while retaining the elementary force
interpretation. It should not rederive the Lorentz force law in full.

### Exposition

The electric field is the part of the electromagnetic field that acts on a
charge at rest in a chosen inertial frame. Operationally, it is force per unit
charge for such a test charge.

Relativistically, the words "in a chosen frame" matter. The electromagnetic
field tensor \(F_{\mu\nu}\) is the covariant object. Once an observer splits
spacetime into time plus space, the components with one time index and one
space index are identified with the electric field:
\[
F_{0i}\quad\hbox{or}\quad F^{0i},
\]
depending on convention.

In ordinary potential language,
\[
\mathbf E\overset{\text{potentials}}{=}
-\nabla\phi-\frac{\partial\mathbf A}{\partial t}.
\]
The \(\text{potentials}\) label marks the chosen potential convention.
The first term is familiar from electrostatics: the electric field points down
the scalar-potential gradient for a positive test charge. The second term shows
that a time-varying vector potential also contributes to the electric field.

Another observer moving relative to the first may decompose the same
\(F_{\mu\nu}\) differently. Part of what one observer calls electric can appear
as magnetic to another. Thus \(\mathbf E\) is physically meaningful and directly
useful, but it is not the whole invariant electromagnetic object.

### Block Plan

- `overview`: Field seen by charges at rest.
- `definition`: Force per unit charge and tensor location.
- `warning`: Frame choice.
- `construction`: Time-space components.
- `derivation`: \(\mathbf E\overset{\text{potentials}}{=}-\nabla\phi-\partial_t\mathbf A\).
- `example`: Static potential.
- `intuition`: Force meaning.
- `misconception`: Not absolute by itself.
- `historical_note`: Electrostatics to tensor component.
- `summary`: Takeaway.

### Study Questions

1. Locate \(\mathbf E\) in \(F_{\mu\nu}\).
2. Explain frame dependence.
3. State the operational meaning.
4. Compute a one-dimensional electrostatic example.
5. Identify convention-sensitive signs and factors.
6. Name the safer covariant object.

### References

- TTM SR/CF: electric field as part of the relativistic electromagnetic field;
  section-level locator recorded in `data/reference_links.csv`.
- TRR: frame-dependent electric/magnetic split; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic showing electric field arrows is acceptable. Retain for
this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Potential-form definitions of \(\mathbf E\) and \(\mathbf B\) are now flagged
  in `docs/authoring/NOTATION_GLOSSARY.md`; continue stating local conventions near
  detailed calculations.

#### Atlas Issues

- A later Lorentz-force concept owns the full force law; this section only uses
  the force-at-rest interpretation.


## 7.4 `sr.magnetic_field`: Magnetic field

### Scope

This concept explains the magnetic field as the frame-dependent spatial
antisymmetric part of the electromagnetic field tensor. It should connect to
currents, moving charges, and \(\mathbf B\overset{\text{potentials}}{=}\nabla\times\mathbf A\), without
taking over the full Lorentz-force or Maxwell-equation treatments.

### Exposition

The magnetic field is the part of the electromagnetic field associated with
currents and with sideways forces on moving charges. In a chosen inertial
frame, it is read from the purely spatial components of the field tensor.

The spatial block \(F_{ij}\) is antisymmetric. In three spatial dimensions an
antisymmetric \(3\times3\) block has three independent components, and those
components can be encoded as the magnetic field vector \(\mathbf B\).

In ordinary potential language,
\[
\mathbf B\overset{\text{potentials}}{=}\nabla\times\mathbf A.
\]
The \(\text{potentials}\) label marks the chosen potential convention.
This is the spatial curl-like part of the antisymmetric derivative used to
construct \(F_{\mu\nu}\). It also hints at the homogeneous Maxwell equation
\[
\nabla\cdot\mathbf B\overset{\text{curl}}{=}0,
\]
since the divergence of a curl vanishes for smooth potentials.
The \(\text{curl}\) label marks that mathematical identity.

The familiar magnetic-force term is proportional to
\[
\mathbf v\times\mathbf B.
\]
That expression makes the frame dependence vivid: magnetic effects in one
frame may appear with a different mixture of electric and magnetic components
in another. The covariant object is \(F_{\mu\nu}\), not a separate magnetic
substance.

### Block Plan

- `overview`: Motion and current.
- `definition`: Spatial components of \(F_{\mu\nu}\).
- `construction`: Spatial antisymmetry.
- `derivation`: \(\mathbf B\overset{\text{potentials}}{=}\nabla\times\mathbf A\).
- `intuition`: Sideways force.
- `example`: Current-carrying wire.
- `warning`: Frame-dependent split.
- `explanation`: No-monopole hint.
- `misconception`: Not a separate substance.
- `historical_note`: Magnetism to electromagnetism.
- `summary`: Takeaway.

### Study Questions

1. Locate \(\mathbf B\) in \(F_{\mu\nu}\).
2. Explain why electric and magnetic fields are not separate substances.
3. Count antisymmetric spatial components.
4. Compute a curl example.
5. Interpret motion-dependent force.
6. Connect \(\mathbf B\overset{\text{potentials}}{=}\nabla\times\mathbf A\) to \(\nabla\cdot\mathbf B\overset{\text{curl}}{=}0\).

### References

- TTM SR/CF: magnetic field as spatial part of the electromagnetic tensor;
  section-level locator recorded in `data/reference_links.csv`.
- TRR: relativistic electric/magnetic mixing; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic showing a circulating magnetic pattern is appropriate.
Retain for this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- The Levi-Civita mapping between antisymmetric spatial tensor components and
  the \(\mathbf B\) vector may need an optional detail or glossary entry later.

#### Atlas Issues

- Magnetic monopoles are intentionally only hinted at here; there is no
  separate concept for monopole extensions.


## 7.5 `sr.electromagnetic_field`: Electromagnetic field

### Scope

This concept synthesises electric field, magnetic field, and field tensor into
the unified relativistic electromagnetic field. It should emphasise the
observer-dependent split and the local-field viewpoint without deriving
Maxwell's equations.

### Exposition

The electromagnetic field is one physical field. In relativistic notation it is
represented by the antisymmetric field tensor \(F_{\mu\nu}\). After an inertial
frame is chosen, its six independent components are read as
\[
\mathbf E \quad\hbox{and}\quad \mathbf B.
\]
The tensor is the package; the electric and magnetic fields are one observer's
unpacking.

This is more than tidy notation. A Lorentz boost mixes time and space
directions. Since electric components are time-space parts of \(F_{\mu\nu}\)
and magnetic components are space-space parts, a boost can mix what observers
call electric and magnetic. The separate three-vector fields are therefore
frame-dependent descriptions of one covariant object.

The field is also local. Electromagnetic influence is represented by field
values throughout spacetime and by local differential equations, not by direct
instantaneous action between distant charges. Later concepts use this field to
write Maxwell's equations, field energy density, Poynting flux, and the
electromagnetic stress-energy tensor.

Historically, Maxwell unified electricity, magnetism, and light dynamically.
Special relativity and Minkowski spacetime made the unification geometrically
explicit.

### Block Plan

- `overview`: One field, two frame faces.
- `definition`: \(F_{\mu\nu}\), \(\mathbf E\), and \(\mathbf B\).
- `construction`: Six-component package.
- `intuition`: Observer-dependent decomposition.
- `explanation`: Lorentz mixing.
- `explanation`: Local physical field.
- `example`: Energy and momentum preview.
- `misconception`: Not two substances.
- `historical_note`: Maxwell, Einstein, Minkowski.
- `summary`: Takeaway.

### Study Questions

1. Identify the covariant electromagnetic object.
2. Explain observer-dependent decomposition.
3. Explain the six-component count.
4. Count components in a frame example.
5. Explain local field language.
6. State the corrected misconception.

### References

- TTM SR/CF: unified electromagnetic field and field tensor; section-level locator recorded in `data/reference_links.csv`.
- TRR: relativistic unification of electric and magnetic fields; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic presenting \(E\), \(B\), and \(F\) as one structure is
appropriate. Retain for this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Some future view may want to show the same \(F_{\mu\nu}\) decomposed by two
  observers side by side.

#### Atlas Issues

- This is a synthesis concept; edge types may later distinguish packaging,
  decomposition, and prerequisite relations more carefully.


## 7.6 `sr.four_current`: Four-current

### Scope

This concept introduces \(j^\mu\) as the covariant source object for
electromagnetism. It should connect charge density, current density, Maxwell's
equations, and local charge conservation.

### Exposition

Charge density by itself is not a relativistic source. If charges are moving,
different inertial observers can disagree about what part of the description
looks like density and what part looks like current. The covariant object is
the four-current:
\[
j^\mu\coloneqq(c\rho,\mathbf j).
\]

The factor \(c\) gives the time component the same dimensional character as the
spatial current components and fits the four-vector transformation law. The
time component records local charge density. The spatial components record
charge flux through small surfaces.

The four-current is the source in covariant Maxwell equations:
\[
\partial_\mu F^{\mu\nu}\overset{\text{Maxwell}}{=}\mu_0 j^\nu.
\]
This equation says the electromagnetic field is sourced locally by charge and
current at the same spacetime event.

Charge conservation has an especially compact form:
\[
\partial_\mu j^\mu\overset{\text{charge conservation}}{=}0.
\]
The \(\text{charge conservation}\) label marks this as the local conservation
law for charge.
Expanding this gives the ordinary continuity equation
\[
\frac{\partial\rho}{\partial t}+\nabla\cdot\mathbf j
\overset{\text{continuity}}{=}0.
\]
Charge in a small region can change only because charge flows through the
boundary.

### Block Plan

- `overview`: Charge flow as a four-vector.
- `definition`: \(j^\mu\coloneqq(c\rho,\mathbf j)\).
- `explanation`: Why \(c\rho\).
- `misconception`: Charge density alone is not enough.
- `intuition`: Local charge flow.
- `construction`: Four-divergence and conservation.
- `example`: Source for the field.
- `example`: Wire intuition.
- `historical_note`: Sources made covariant.
- `summary`: Takeaway.

### Study Questions

1. Identify the four-current.
2. Explain why charge density alone is insufficient.
3. Interpret \(\partial_\mu j^\mu\overset{\text{charge conservation}}{=}0\).
4. Compute \(j^\mu\) from \(\rho\) and \(\mathbf j\).
5. Locate \(j^\mu\) in Maxwell equations.
6. Give the geometric interpretation.

### References

- TTM SR/CF: four-current definition and source role; section-level locator recorded in `data/reference_links.csv`.
- TRR: relativistic packaging of charge and current density; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing source-flow graphic is appropriate. Retain for this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Source units and SI/natural-unit conventions need consistent notation
  glossary handling.

#### Atlas Issues

- Later charge-conservation content owns the detailed derivation from Maxwell's
  equations; this concept only introduces the continuity form.


## 7.7 `sr.maxwells_equations`: Maxwell's equations

### Scope

This concept presents Maxwell's equations as the local relativistic field
equations of electromagnetism. It should show the covariant source equation,
the homogeneous identity, the relation to the usual four equations, and the
links to charge conservation and waves.

### Exposition

Maxwell's equations are the field equations governing the electromagnetic
field. In relativistic notation, much of their structure is compressed into two
covariant statements.

The sourced equation is
\[
\partial_\mu F^{\mu\nu}\overset{\text{Maxwell}}{=}\mu_0 j^\nu,
\]
in SI-style conventions. It relates local derivatives of the electromagnetic
field tensor to the local four-current source.
The \(\text{Maxwell}\) label marks this as a field law, not an algebraic
identity.

The homogeneous equation is
\[
\partial_\lambda F_{\mu\nu}
+\partial_\mu F_{\nu\lambda}
+\partial_\nu F_{\lambda\mu}\overset{\text{homogeneous}}{=}0.
\]
The \(\text{homogeneous}\) label marks the source-free identity that follows
from the potential construction.
This follows from the construction
\[
F_{\mu\nu}\coloneqq\partial_\mu A_\nu-\partial_\nu A_\mu.
\]
When the cyclic derivative is expanded, second-derivative terms cancel in
pairs because partial derivatives commute.

After choosing an inertial frame, these compact equations become the familiar
four Maxwell equations: Gauss's law for electricity, Gauss's law for magnetism,
Faraday's law, and the Ampere-Maxwell law. The covariant form shows why the
four equations belong together.

The equations are also internally consistent with charge conservation. Taking
the divergence of the sourced equation gives
\[
\partial_\nu\partial_\mu F^{\mu\nu}\overset{\text{Maxwell}}{=}\mu_0\partial_\nu j^\nu.
\]
The \(\text{Maxwell}\) label marks use of the sourced field equation.
The left side vanishes because a symmetric double derivative is contracted
with an antisymmetric tensor, so
\[
\partial_\mu j^\mu\overset{\text{charge conservation}}{=}0.
\]

In source-free regions, \(j^\mu\overset{\text{source-free}}{=}0\), Maxwell's equations still allow nonzero
field configurations. Those solutions include electromagnetic waves travelling
at the invariant light speed.
The \(\text{source-free}\) label marks a physical condition on the source, not
the absence of the electromagnetic field.

### Block Plan

- `overview`: Local laws of electromagnetism.
- `definition`: Maxwell's equations govern the electromagnetic field.
- `definition`: Sourced equation.
- `definition`: Homogeneous equation.
- `derivation`: From the field action.
- `derivation_step`: Homogeneous cancellation.
- `explanation`: Usual four equations.
- `construction`: Charge conservation.
- `example`: Source-free waves.
- `misconception`: Not four unrelated formulas.
- `historical_note`: Maxwell and light.
- `summary`: Takeaway.

### Study Questions

1. Explain the advantage of covariant form.
2. Interpret the sourced equation.
3. Explain the homogeneous cancellation.
4. Reduce the sourced equation in a source-free region.
5. Derive charge-conservation consistency.
6. Explain why the four usual equations belong together.

### References

- TTM SR/CF: covariant Maxwell equations and four-current source; section-level locator recorded in `data/reference_links.csv`.
- TRR: Maxwell theory, light, and relativistic field structure; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing Maxwell graphic is adequate for this pass. Later we may want a
more explicit covariant-pair-to-four-equations graphic.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- This section would benefit from foldable convention notes for SI vs natural
  units and sign conventions.

#### Atlas Issues

- A future richer edge vocabulary should distinguish "component split",
  "source equation", and "identity from construction".


## 8.1 `sr.gauge_invariance`: Gauge invariance

### Scope

This concept introduces electromagnetic gauge invariance as redundancy in the
potential description. It should prove the invariance of \(F_{\mu\nu}\), explain
why this is not a physical change, and prepare gauge fixing and minimal
coupling.

### Exposition

Gauge invariance says that the electromagnetic potential contains redundancy.
The transformation
\[
A_\mu\rightarrow A_\mu+\partial_\mu\Lambda
\]
changes the potential, but not the electromagnetic field tensor.

To see this, substitute the transformed potential into
\[
F_{\mu\nu}\coloneqq\partial_\mu A_\nu-\partial_\nu A_\mu.
\]
The added terms are
\[
\partial_\mu\partial_\nu\Lambda-\partial_\nu\partial_\mu\Lambda
\overset{\text{commuting partials}}{=}0.
\]
The \(\text{commuting partials}\) label marks the mathematical identity
responsible for gauge invariance. Therefore \(F_{\mu\nu}\) is unchanged.

This is conceptually important. We are used to thinking that changing a field
variable changes the physical situation. Gauge invariance says that not every
change in \(A_\mu\) is physical. Gauge-related potentials are different
representatives of the same electromagnetic field.

In classical electromagnetism, the physical field strength is \(F_{\mu\nu}\),
or the electric and magnetic fields read from it after a frame is chosen.
The potential remains structurally important, especially in action principles
and in coupling to charged matter, but its gauge-dependent part is redundant.

This redundancy explains why gauge fixing is possible: one may impose an extra
condition to choose a convenient representative without changing the field.
It also constrains interactions, because charged matter must couple in a way
that respects the gauge redundancy.

### Block Plan

- `overview`: Redundancy without physical change.
- `definition`: \(A_\mu\rightarrow A_\mu+\partial_\mu\Lambda\).
- `derivation`: Cancellation in \(F_{\mu\nu}\).
- `intuition`: Many descriptions, one field.
- `misconception`: Not every change in \(A_\mu\) is physical.
- `explanation`: Observable quantities.
- `construction`: Why gauge fixing exists.
- `example`: Constraint on interactions.
- `historical_note`: From potential freedom to gauge theory.
- `summary`: Takeaway.

### Study Questions

1. Recognize gauge invariance.
2. Explain the derivative cancellation.
3. Interpret redundancy of the potential.
4. Compute a simple mixed-derivative cancellation.
5. Explain why gauge fixing is allowed.
6. Connect gauge invariance to interactions.

### References

- TTM SR/CF: gauge transformation of the electromagnetic potential; section-level locator recorded in `data/reference_links.csv`.
- TRR: gauge freedom as a structural principle in field theory; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing gauge-equivalent-potential graphic is appropriate. Retain for this
pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Gauge function notation \(\Lambda\) should be included in the future notation
  glossary.

#### Atlas Issues

- The missing 8.2 slot remains unresolved; it may eventually hold a bridge
  concept such as "gauge freedom" or "potential equivalence class".


## 8.3 `sr.minimal_coupling`: Minimal coupling

### Scope

This concept explains minimal coupling as the economical, local,
gauge-compatible way to introduce electromagnetic interaction into charged
particle dynamics. It should prepare the Lorentz force law without doing that
full derivation.

### Exposition

Minimal coupling is the standard prescription for making a charged particle
interact with electromagnetism. In momentum language it is often represented by
a potential-dependent combination such as
\[
p_\mu-eA_\mu.
\]
In action language the interaction term can be written proportionally to
\[
eA_\mu dx^\mu.
\]

The word minimal means that the simplest local coupling is used. We do not add
extra higher-order or nonlocal terms unless there is a separate physical reason
to do so. The vector potential enters directly because it is the local field
variable that couples to charge.

The contraction \(A_\mu dx^\mu\) is a Lorentz scalar, so it can be added to the
action without selecting a preferred inertial frame. Gauge invariance also
constrains the coupling: gauge-related potentials must not lead to different
physical predictions.

Minimal coupling also explains why canonical and mechanical momentum can
differ. Once the Lagrangian contains the vector potential, the momentum
conjugate to position can include \(A_\mu\)-dependent pieces. The mechanical
momentum still tracks the particle's motion.

Varying the minimally coupled action produces the Lorentz force law. In that
calculation, derivatives of \(A_\mu\) combine into the field tensor
\(F_{\mu\nu}\).

### Block Plan

- `overview`: Economical electromagnetic interaction.
- `definition`: \(p_\mu-eA_\mu\).
- `explanation`: What minimal means.
- `construction`: Worldline coupling.
- `construction`: Momentum replacement.
- `intuition`: Gauge compatibility.
- `example`: Canonical versus mechanical momentum.
- `derivation`: Toward the force law.
- `misconception`: Not an arbitrary substitution trick.
- `historical_note`: Bridge to modern gauge theory.
- `summary`: Takeaway.

### Study Questions

1. Recognize minimal coupling.
2. Explain "minimal".
3. Explain why \(eA_\mu dx^\mu\) is relativistically natural.
4. Compute a simple \(p-eA\) combination.
5. Explain canonical versus mechanical momentum.
6. Connect to the Lorentz force law.

### References

- TTM SR/CF: minimal coupling of charged particles to electromagnetic
  potentials; section-level locator recorded in `data/reference_links.csv`.
- TRR: gauge-compatible coupling as a field-theory principle; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic showing potential insertion into particle dynamics is
appropriate. Retain for this pass.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Sign conventions for \(p_\mu-eA_\mu\), \(q\), and \(e\) are now flagged in
  `docs/authoring/NOTATION_GLOSSARY.md`; continue stating local conventions near detailed
  calculations.

#### Atlas Issues

- The missing 8.2 slot may affect layer narrative: gauge invariance jumps
  directly to minimal coupling without a separate gauge-freedom bridge.


## 8.4 `sr.lorentz_force_law`: Lorentz force law

### Scope

This concept explains how an electromagnetic field moves a charged particle.
It should connect minimal coupling to the covariant force law, relate that
equation to the familiar three-vector expression, and avoid taking over the
later radiation-reaction concept.

### Exposition

The Lorentz force law is the bridge from field to particle motion. In covariant
form it is
\[
\frac{dp^\mu}{d\tau}\overset{\text{Lorentz force}}{=}qF^\mu{}_{\nu}U^\nu,
\]
where \(p^\mu\) is the particle's momentum four-vector, \(U^\nu\) is its
velocity four-vector, \(F^\mu{}_{\nu}\) is the electromagnetic field tensor,
and \(q\) is the charge.
The \(\text{Lorentz force}\) label marks the dynamical law being imposed.

In a chosen inertial frame the spatial part becomes the familiar three-vector
law
\[
\mathbf F\overset{\text{3-vector}}{=}q(\mathbf E+\mathbf v\times\mathbf B).
\]
The \(\text{3-vector}\) label marks the frame-dependent decomposition of the
covariant force law.
The electric field contributes a force along the field direction. The magnetic
field contributes a sideways, velocity-dependent force.

The covariant law follows from the action principle applied to a charged
particle with minimal coupling. In the worldline variation, derivative terms
from the potential combine as
\[
\partial_\mu A_\nu-\partial_\nu A_\mu,
\]
which is precisely \(F_{\mu\nu}\). Thus the force law depends on the
gauge-invariant field tensor, not on a gauge-dependent part of the potential.

The electric and magnetic pieces have different roles in an inertial frame. A
charge at rest feels no magnetic force, because the magnetic term contains the
velocity. In a magnetic-only situation the force is perpendicular to the
velocity. Taking the dot product with \(\mathbf v\),
\[
\mathbf F\cdot\mathbf v
\overset{\text{Lorentz force}}{=}
q\mathbf E\cdot\mathbf v+q(\mathbf v\times\mathbf B)\cdot\mathbf v,
\]
and the magnetic term is zero. The \(\text{Lorentz force}\) label marks
substitution of the three-vector force law. In that frame, the electric field is the part
that changes the particle's energy directly.

Signs and factors of \(c\) depend on metric signature, index placement, charge
convention, and the convention used to place \(\mathbf E\) and \(\mathbf B\)
inside \(F_{\mu\nu}\). The physical content is unchanged when the convention
is used consistently.

The basic Lorentz force law does not solve every problem involving a charged
particle. In particular, it does not by itself include the reaction of an
accelerating charge to its own emitted radiation. That is the separate
radiation-reaction problem.

### Block Plan

- `overview`: How fields move charges.
- `definition`: Covariant Lorentz force law.
- `explanation`: Three-vector form.
- `construction`: From the action.
- `derivation_step`: Why the field tensor appears.
- `intuition`: Electric and magnetic roles.
- `derivation`: Power delivered to the particle.
- `warning`: Conventions matter.
- `misconception`: Not the whole story for an emitting charge.
- `historical_note`: Lorentz's synthesis.
- `summary`: Takeaway.

### Study Questions

1. Recognize the three-vector law.
2. Interpret the covariant equation.
3. Compute a simple \(\mathbf E+\mathbf v\times\mathbf B\) force.
4. Explain why magnetic force does no work in a magnetic-only case.
5. Explain why \(F_{\mu\nu}\) appears.
6. Identify what radiation reaction adds beyond the basic law.

### References

- TTM SR/CF: covariant and ordinary Lorentz force law; section-level locator recorded in `data/reference_links.csv`.
- TRR: relativistic electrodynamics and field tensor context; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic is adequate for this pass. A future revision could show a
charged trajectory curving in a magnetic field beside the covariant tensor
equation.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Sign conventions for the field tensor and the charge \(q\) are now flagged in
  `docs/authoring/NOTATION_GLOSSARY.md`; continue stating local conventions near detailed
  calculations.

#### Atlas Issues

- Radiation reaction is intentionally kept out of this concept except as a
  boundary note.


## 8.5 `sr.charge_conservation`: Charge conservation

### Scope

This concept treats charge conservation as a local continuity equation. It
should explain the physical bookkeeping meaning, show how the equation follows
from Maxwell's sourced field equation, and avoid turning into a full account of
electric charge or four-current.

### Exposition

Charge conservation says more than that the total charge of a complete isolated
system stays fixed. It says charge can leave a region only by flowing through
the boundary of that region. Locally, the relativistic statement is
\[
\partial_\mu j^\mu\overset{\text{charge conservation}}{=}0,
\]
where \(j^\mu\) is the four-current.

In ordinary vector notation the four-divergence expands as
\[
\partial_\mu j^\mu
\equiv
\frac{\partial \rho}{\partial t}+\nabla\cdot\mathbf j,
\]
so the same conservation law becomes
\[
\frac{\partial \rho}{\partial t}+\nabla\cdot\mathbf j
\overset{\text{continuity}}{=}0.
\]
The \(\text{continuity}\) label marks the ordinary vector form of the same
local conservation law.
If \(\nabla\cdot\mathbf j\) is positive, more current is flowing out than in,
so the charge density decreases. If it is negative, current is converging and
the charge density increases.

Define the charge inside a fixed volume by
\[
Q_V\coloneqq\int_V\rho\,d^3x.
\]
Integrating the local equation over \(V\) gives
\[
\frac{d}{dt}\int_V\rho\,d^3x
\overset{\text{continuity}}{=}
-\int_V\nabla\cdot\mathbf j\,d^3x.
\]
Using the divergence theorem,
\[
\frac{dQ_V}{dt}
\overset{\text{Gauss theorem}}{=}
-\oint_{\partial V}\mathbf j\cdot d\mathbf a.
\]
The charge inside the volume changes by the negative of the outward current
flux.

In Maxwell theory charge conservation is also a consistency condition. Taking
the divergence of the sourced equation
\[
\partial_\mu F^{\mu\nu}\overset{\text{Maxwell}}{=}\mu_0j^\nu
\]
gives
\[
\partial_\nu\partial_\mu F^{\mu\nu}
\overset{\text{Maxwell}}{=}
\mu_0\partial_\nu j^\nu.
\]
The left-hand side vanishes because \(F^{\mu\nu}\) is antisymmetric, while the
commuting double derivative is symmetric in the two indices. Therefore
\[
\partial_\nu j^\nu\overset{\text{charge conservation}}{=}0.
\]
The \(\text{charge conservation}\) label marks the local continuity condition
forced by Maxwell consistency.
Equivalently, let
\[
C\coloneqq\partial_\nu\partial_\mu F^{\mu\nu}.
\]
Swapping the two dummy indices gives
\[
C\overset{\mu\leftrightarrow\nu}{=}-C,
\]
so \(C\overset{C=-C}{=}0\). The \(C=-C\) label marks the final consequence of
the antisymmetry argument.

A global conservation law alone would allow too much. It might say the total
charge is unchanged, but not how charge gets from one place to another. The
local continuity equation forbids charge from disappearing here and reappearing
elsewhere without a current connecting the events.

### Block Plan

- `overview`: Local bookkeeping.
- `definition`: Covariant and ordinary continuity equation.
- `intuition`: What the equation says.
- `derivation_step`: From local to integral form.
- `derivation`: Consistency of Maxwell's equations.
- `explanation`: Why antisymmetry matters.
- `misconception`: Not just a global rule.
- `warning`: Sources must be compatible.
- `historical_note`: From circuits to fields.
- `summary`: Takeaway.

### Study Questions

1. Recognize \(\partial_\mu j^\mu\overset{\text{charge conservation}}{=}0\).
2. Interpret the ordinary continuity equation.
3. Compute a simple one-dimensional density change.
4. Explain the Maxwell-equation derivation.
5. Distinguish local and global conservation.
6. Explain why inconsistent sources are forbidden.

### References

- TTM SR/CF: four-current and continuity equation; section-level locator recorded in `data/reference_links.csv`.
- TRR: charge conservation as a consistency condition of Maxwell theory;
  section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic showing current flux out of a region remains appropriate.
A future refinement could make the local-to-integral relationship more explicit.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Divergence theorem notation may eventually deserve a mathematical sidebar or
  linked mathematics concept.

#### Atlas Issues

- Four-current remains the main prerequisite; no new concept split needed here.


## 8.6 `sr.lorenz_gauge`: Lorenz gauge

### Scope

This concept explains the Lorenz gauge as a covariant condition on the
electromagnetic potential. It should connect gauge fixing, gauge invariance,
and the wave-equation form of Maxwell's equations, while avoiding the later
full wave-equation and electromagnetic-wave concepts.

### Exposition

The Lorenz gauge is the condition
\[
\partial_\mu A^\mu\overset{\text{Lorenz gauge}}{=}0
\]
imposed on the vector potential. It is a particular gauge choice: it chooses a
convenient representative from a gauge-equivalent family of potentials.
The \(\text{Lorenz gauge}\) label marks a gauge choice, not a new physical law.

This is allowed because the electromagnetic potential has gauge redundancy.
Gauge-related potentials represent the same physical electromagnetic field.
The gauge condition changes the description, not \(F_{\mu\nu}\).

The Lorenz gauge is especially useful in relativity because
\(\partial_\mu A^\mu\) is a scalar contraction. If it is zero in one inertial
frame, it remains zero in every Lorentz-related inertial frame. Thus the gauge
choice keeps covariance manifest.

In potential form, the sourced Maxwell equation contains a term schematically
like
\[
\Box A^\nu-\partial^\nu(\partial_\mu A^\mu)
\overset{\text{Maxwell}}{=}\mu_0j^\nu.
\]
The \(\text{Maxwell}\) label marks that this is the sourced field equation
rewritten in terms of the potential.
Imposing \(\partial_\mu A^\mu\overset{\text{Lorenz gauge}}{=}0\) removes the
second term, leaving a wave equation for each component of the potential, up
to sign and unit conventions. The \(\text{Lorenz gauge}\) label marks the
condition being used to simplify the potential equation.

The Lorenz gauge may not remove all gauge freedom. A further transformation
\[
A_\mu\rightarrow A_\mu+\partial_\mu\Lambda
\]
preserves the condition if \(\Box\Lambda\overset{\text{residual gauge}}{=}0\).
The \(\text{residual gauge}\) label marks the extra condition on the gauge function. The remaining freedom is usually
manageable, but it is worth remembering that gauge fixing is not always a
complete elimination of redundancy.

Finally, the spelling matters. This is the Lorenz gauge, named after Ludvig
Lorenz, not Hendrik Lorentz. The confusion is natural because the condition is
Lorentz-covariant.

### Block Plan

- `overview`: A covariant gauge choice.
- `definition`: \(\partial_\mu A^\mu\overset{\text{Lorenz gauge}}{=}0\).
- `explanation`: Why a gauge condition is allowed.
- `intuition`: Why this gauge is relativistic.
- `derivation`: Maxwell equations become wave equations.
- `warning`: It may not fix everything.
- `misconception`: Not a new physical law.
- `historical_note`: Lorenz, not Lorentz.
- `summary`: Takeaway.

### Study Questions

1. Recognize the Lorenz gauge condition.
2. Explain why gauge fixing is legitimate.
3. Explain why the condition is covariant.
4. Check a toy divergence condition.
5. Explain the Maxwell-equation simplification.
6. Avoid the Lorenz/Lorentz naming confusion.

### References

- TTM SR/CF: Lorenz gauge and potential form of Maxwell equations; section-level locator recorded in `data/reference_links.csv`.
- TRR: gauge conditions and covariant electrodynamics context; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic is adequate. A future version could show a family of
gauge-equivalent potentials with the Lorenz-gauge slice highlighted.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Residual gauge freedom may need a future optional derivation or linked
  mathematical side note.

#### Atlas Issues

- The connection to the wave equation is deliberately preparatory; the full
  wave-equation concept remains in layer 10.


## 9.1 `sr.energy_momentum_tensor`: Energy--momentum tensor

### Scope

This concept introduces \(T^{\mu\nu}\) as the general local bookkeeping object
for energy and momentum in fields and continuous systems. It should derive the
idea from spacetime translation symmetry and prepare the electromagnetic
specializations in 9.2 to 9.4.

### Exposition

The energy-momentum tensor records how energy and momentum are stored and
transported. It is a rank-two tensor \(T^{\mu\nu}\). For an isolated system its
local conservation law is
\[
\partial_\mu T^{\mu\nu}\overset{\text{energy-momentum conservation}}{=}0.
\]
The \(\text{energy-momentum conservation}\) label marks the local balance law
for energy and momentum.

Roughly, one index describes the spacetime direction through which something
flows, and the other describes which component of energy-momentum is being
transported. \(T^{00}\) is energy density. Mixed time-space components encode
energy flux or momentum density. Spatial-spatial components encode stresses:
the flow of momentum through surfaces.

The tensor arises naturally from Noether's theorem. Time translation symmetry
gives energy conservation; spatial translation symmetry gives momentum
conservation. In field theory these four conserved currents are assembled into
one two-index object.

For fields \(\phi_a\) with Lagrangian density
\(\mathcal L(\phi_a,\partial_\mu\phi_a)\), a canonical expression is
\[
T^\mu{}_{\nu}
\overset{\text{Noether}}{=}
\frac{\partial\mathcal L}{\partial(\partial_\mu\phi_a)}
\partial_\nu\phi_a-\delta^\mu{}_{\nu}\mathcal L.
\]
The \(\text{Noether}\) label marks that this canonical tensor comes from
spacetime translation symmetry.

The canonical tensor is not always the final physical form. It may not be
symmetric, gauge-invariant, or the most useful representative. One can often
add an improvement term whose divergence vanishes identically, so the conserved
total energy and momentum do not change.

For electromagnetism the useful symmetric tensor is built from the field
tensor. In natural units and one common sign convention,
\[
T^{\mu\nu}
\overset{\text{EM tensor}}{=}
-F^{\mu\lambda}F^\nu{}_{\lambda}
+\frac14\eta^{\mu\nu}F^{\alpha\beta}F_{\alpha\beta}.
\]
The \(\text{EM tensor}\) label marks the electromagnetic stress-energy
construction in that convention.
Its components contain electromagnetic energy density, momentum density, flux,
and stress.

The most important idea is local flow. Energy or momentum does not disappear at
a point. If a small region loses it, the loss is balanced by a flux through the
boundary.

### Block Plan

- `overview`: Local energy-momentum bookkeeping.
- `definition`: \(T^{\mu\nu}\) and \(\partial_\mu T^{\mu\nu}\overset{\text{energy-momentum conservation}}{=}0\).
- `explanation`: What the indices mean.
- `derivation`: Origin in translation symmetry.
- `derivation_step`: Canonical form.
- `intuition`: Conservation as flow.
- `warning`: Canonical is not always final.
- `example`: Electromagnetic example.
- `misconception`: Not just energy density.
- `historical_note`: From conservation laws to tensors.
- `summary`: Takeaway.

### Study Questions

1. Recognize what the tensor packages.
2. Interpret \(\partial_\mu T^{\mu\nu}\overset{\text{energy-momentum conservation}}{=}0\).
3. Connect the tensor to Noether's theorem.
4. Compute a simple one-dimensional conservation balance.
5. Explain why improvement terms may be used.
6. Avoid reducing the tensor to \(T^{00}\) only.

### References

- TTM SR/CF: energy-momentum tensor and translation symmetry; section-level locator recorded in `data/reference_links.csv`.
- TRR: stress-energy tensor in field theory and electromagnetism; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic is acceptable. A future refinement could show a small
spacetime box with energy density, energy flux, momentum density, and stress
labels on different tensor components.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Tensor component interpretation would benefit from future richer graphics or
  a table-like viewer block.

#### Atlas Issues

- The distinction between canonical, symmetric, and Hilbert stress-energy
  tensors is compressed here. It may deserve a later advanced concept.


## 9.2 `sr.poynting_vector`: Momentum density (Poynting vector)

### Scope

This concept explains the Poynting vector as electromagnetic energy flux and
connects it to momentum density. It should prepare the stress-energy and energy
density concepts without replacing them.

### Exposition

The Poynting vector tells us where electromagnetic energy is flowing. In SI
units it is
\[
\mathbf S\overset{\text{SI}}{=}\frac{1}{\mu_0}\mathbf E\times\mathbf B.
\]
The \(\text{SI}\) label marks the unit convention responsible for the factor
\(1/\mu_0\).
It measures energy crossing unit area per unit time.

The cross product is physically useful. It points perpendicular to both the
electric and magnetic fields. In a plane wave with \(\mathbf E\) along \(y\)
and \(\mathbf B\) along \(z\), \(\mathbf S\) points along \(x\), the direction
of propagation.

The Poynting vector is not the stored field energy. Energy density tells us how
much electromagnetic energy is present in a small volume. \(\mathbf S\) tells
us how quickly that energy flows through a surface and in which direction.

In the electromagnetic energy-momentum tensor, the Poynting vector appears in
the mixed time-space components. When those components are decomposed into
\(\mathbf E\) and \(\mathbf B\), the combination \(\mathbf E\times\mathbf B\)
appears.

Relativity links energy flow and momentum density. In SI units the field
momentum density is
\[
\mathbf g\overset{\text{SI}}{=}\frac{\mathbf S}{c^2}.
\]
The \(\text{SI}\) label marks the conventional SI relation between field
momentum density and energy flux.
In natural units, \(c\overset{\text{units}}{=}1\), the relationship is less cluttered, though index and
unit conventions still matter.

A beam of light can exert radiation pressure because the electromagnetic field
carries momentum. Absorbing or reflecting the beam transfers that momentum to
matter.

### Block Plan

- `overview`: Energy in motion.
- `definition`: SI formula.
- `intuition`: Direction from a cross product.
- `explanation`: Flux, not stored energy.
- `derivation`: Origin in the energy-momentum tensor.
- `definition`: Momentum density.
- `example`: Radiation pressure.
- `warning`: Unit conventions.
- `misconception`: Not a stream of little arrows.
- `historical_note`: Poynting's theorem.
- `summary`: Takeaway.

### Study Questions

1. Recognize the SI formula.
2. State the physical meaning.
3. Compute a simple cross product.
4. Relate \(\mathbf S\) to momentum density.
5. Explain radiation pressure.
6. Avoid the literal-arrow misconception.

### References

- TTM SR/CF: Poynting vector and electromagnetic momentum density; section-level locator recorded in `data/reference_links.csv`.
- TRR: electromagnetic energy flow and field momentum context; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic is appropriate. A future refinement could explicitly show
energy flux through a small surface element.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Cross-product orientation could benefit from an interactive or animated
  graphic later.

#### Atlas Issues

- The node title includes "Momentum density" although the concept also covers
  energy flux. The current title is acceptable but slightly asymmetrical.


## 9.3 `sr.em_stress_energy`: Stress-energy of EM field

### Scope

This concept treats the electromagnetic stress-energy tensor as the
electromagnetic instance of the general energy-momentum tensor. It should
explain the formula, the component interpretation, and the observer-dependent
split without taking over the separate Poynting-vector or field-energy-density
concepts.

### Exposition

The electromagnetic stress-energy tensor is the complete local accounting
object for electromagnetic energy and momentum. It is the electromagnetic-field
instance of the general energy-momentum tensor.

It is built from the field tensor and the metric tensor. With the \(+---\)
metric convention and suppressing unit-dependent constants, one common form is
\[
T^{\mu\nu}
\overset{\text{EM tensor}}{=}
-F^{\mu\lambda}F^\nu{}_{\lambda}
+\frac14\eta^{\mu\nu}F^{\alpha\beta}F_{\alpha\beta}.
\]
The \(\text{EM tensor}\) label marks the electromagnetic stress-energy
construction in the stated convention.

The expression is quadratic in \(F_{\mu\nu}\). That is physically natural:
reversing the electromagnetic field should not reverse the sign of the field
energy. Quadratic contractions are the simplest Lorentz-covariant way to build
that behaviour while retaining two free indices for density, flow, and stress.

In a chosen inertial frame, \(T^{00}\) is field energy density. Mixed
time-space components describe energy flux and momentum density.
Spatial-spatial components describe stresses: momentum flowing across surfaces.
Radiation pressure is a concrete example. Light striking a surface carries
momentum, so it can push.

The split into energy density, momentum density, flux, and stress is
frame-dependent. Different observers decompose the same tensor differently.
The covariant object is \(T^{\mu\nu}\) itself.

The stress-energy tensor is not an additional electromagnetic field. It is
built from \(F_{\mu\nu}\) to describe what energy and momentum that field
carries and transfers.

### Block Plan

- `overview`: The field's accounting tensor.
- `definition`: Electromagnetic instance of \(T^{\mu\nu}\).
- `derivation`: Tensor formula.
- `intuition`: Why it is quadratic.
- `explanation`: Component meaning.
- `example`: Stress and pressure.
- `warning`: Observer-dependent split.
- `misconception`: Not a new electromagnetic field.
- `historical_note`: Electromagnetic momentum made local.
- `summary`: Takeaway.

### Study Questions

1. Recognize why the tensor is richer than energy density.
2. Identify construction from \(F_{\mu\nu}\) and the metric.
3. Explain the quadratic dependence.
4. Compute a simple radiation-pressure value.
5. Explain observer-dependent component splits.
6. Avoid treating the tensor as a new field.

### References

- TTM SR/CF: electromagnetic stress-energy tensor formula; section-level locator recorded in `data/reference_links.csv`.
- TRR: stress-energy tensor and frame-dependent component decomposition;
  section-level locator recorded in `data/reference_links.csv`.

### Graphics

The current component-grid graphic is adequate. A future version could use
colour-coded tensor blocks for density, flux, momentum density, and stress.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- This concept would benefit from a table-style mathematical block in the
  viewer for component interpretation.

#### Atlas Issues

- A future advanced concept may distinguish Maxwell stress tensor, Hilbert
  stress-energy tensor, and canonical tensor more carefully.


## 9.4 `sr.em_energy_density`: Energy density of EM field

### Scope

This concept explains the local energy density of the electromagnetic field. It
should give the familiar SI formula, connect it to \(T^{00}\), and emphasize
that field energy is locally stored and transported.

### Exposition

Electromagnetic fields can store energy locally, even in a region where no
charged particles are present. In SI units the energy density is
\[
u\overset{\text{SI}}{=}
\frac12\left(\epsilon_0E^2+\frac{1}{\mu_0}B^2\right).
\]
Here \(\mathbf E\) and \(\mathbf B\) are the electric and magnetic fields.
The \(\text{SI}\) label marks the unit convention built into the constants
\(\epsilon_0\) and \(\mu_0\).

In a chosen inertial frame, this energy density is the time-time component of
the electromagnetic energy-momentum tensor:
\[
T^{00}\overset{\text{frame}}{=}u.
\]
The \(\text{frame}\) label marks that this component identification depends on
the observer's time-space split.
Substituting the electric and magnetic components of the field tensor gives the
squared-field formula.

The squared dependence is natural. Reversing the sign of \(\mathbf E\) or
\(\mathbf B\) should not make stored energy negative. The leading local
quantities with the right behaviour are \(E^2\) and \(B^2\).

This is a conceptual step beyond treating fields only as devices for exerting
forces on charges. Energy can be stored in the field between charges and can
flow through space. Electromagnetic waves make that point vivid: field energy
travels.

In a plane wave, the electric and magnetic contributions to the energy density
are equal in SI units. The energy is shared between the two field components
while the wave propagates.

Energy density is still a frame-dependent component. Another inertial observer
decomposes the same stress-energy tensor differently. The covariant account is
the full tensor, not \(u\) alone.

### Block Plan

- `overview`: Energy stored in fields.
- `definition`: SI formula.
- `derivation`: The \(T^{00}\) component.
- `intuition`: Why squared fields appear.
- `explanation`: Energy beyond particles.
- `example`: Plane-wave balance.
- `warning`: Energy density is frame-dependent.
- `misconception`: Not just potential energy between charges.
- `historical_note`: Maxwell's field energy.
- `summary`: Takeaway.

### Study Questions

1. State what energy density measures.
2. Explain squared field strengths.
3. Compute a simplified energy density.
4. Relate \(u\) to \(T^{00}\).
5. Explain energy in fields rather than only particles.
6. Explain why \(u\) is not the full covariant account.

### References

- TTM SR/CF: electromagnetic energy density formula; section-level locator recorded in `data/reference_links.csv`.
- TRR: field energy and electromagnetic radiation context; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The current graphic is adequate. A future version could pair local field energy
density with nearby Poynting-vector flow arrows.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- The viewer may later benefit from equation-callout styling for formulas that
  are intended as key results.

#### Atlas Issues

- This concept naturally points to electromagnetic waves, but detailed wave
  structure is left to layer 10.


## 10.1 `sr.wave_equation`: Wave equation

### Scope

This concept introduces the relativistic wave equation as a mathematical
structure for finite-speed propagation. It should show how Maxwell's equations
lead to a potential wave equation in Lorenz gauge and prepare the specific
electromagnetic-wave concept.

### Exposition

The wave equation is the mathematical pattern for disturbances that propagate
through spacetime at a finite speed. In relativity it uses the d'Alembertian
operator
\[
\Box\coloneqq\partial_\mu\partial^\mu
\overset{\text{components}}{=}
\frac{1}{c^2}\frac{\partial^2}{\partial t^2}-\nabla^2
\]
for the \(+---\) metric convention. A source-free scalar component satisfies
\[
\Box\psi\overset{\text{wave equation}}{=}0.
\]
The \(\text{components}\) label marks the coordinate expansion of the
covariant operator. The \(\text{wave equation}\) label marks imposition of the
source-free wave equation.

The d'Alembertian is built from the metric. Its time and spatial parts enter
with opposite signs, encoding the light-cone structure of relativistic
propagation.

In electromagnetism, write the field in terms of the vector potential and
impose the Lorenz gauge. The potential form of Maxwell's equations then becomes
schematically
\[
\Box A^\mu\overset{\text{Maxwell + Lorenz gauge}}{=}\mu_0j^\mu.
\]
The \(\text{Maxwell + Lorenz gauge}\) label marks that this form uses
Maxwell's equations together with the gauge condition.
If the four-current vanishes in a region, this reduces to
\[
\Box A^\mu\overset{\text{source-free}}{=}0.
\]
The \(\text{source-free}\) label marks the condition \(j^\mu=0\).

Plane waves show the propagation speed directly. Trying
\[
\psi\coloneqq e^{i(kx-\omega t)}
\]
in \(\Box\psi\overset{\text{wave equation}}{=}0\) gives
\[
-\frac{\omega^2}{c^2}+k^2\overset{\text{wave equation}}{=}0,
\]
so \(\omega\overset{\text{dispersion}}{=}ck\).
The \(\text{wave equation}\) label marks imposition of the source-free equation,
and the \(\text{dispersion}\) label marks the resulting relation between
frequency and wave number.

The source-free wave equation describes free propagation. With sources present,
the equation describes how charges and currents generate or drive fields.

### Block Plan

- `overview`: Finite-speed propagation.
- `definition`: D'Alembertian and source-free equation.
- `explanation`: Metric structure.
- `derivation`: From Maxwell equations.
- `derivation_step`: Source-free region.
- `example`: Plane-wave test.
- `warning`: Sources change the equation.
- `misconception`: Not every oscillation is a wave equation.
- `historical_note`: Maxwell's prediction of light.
- `summary`: Takeaway.

### Study Questions

1. Recognize the d'Alembertian.
2. Explain the Lorenz-gauge simplification.
3. Compute \(\omega\overset{\text{dispersion}}{=}ck\).
4. Explain source terms.
5. Explain why the metric matters.
6. Distinguish a wave equation from mere oscillation.

### References

- TTM SR/CF: wave equation from Maxwell equations in Lorenz gauge; section-level locator recorded in `data/reference_links.csv`.
- TRR: Maxwell wave equation and light context; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The current graphic is adequate. A future version could show light-cone
propagation beside a sinusoidal plane-wave slice.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- D'Alembertian sign conventions are now covered in
  `docs/authoring/NOTATION_GLOSSARY.md`; keep this concept aligned as sign conventions
  evolve.

#### Atlas Issues

- This concept is deliberately mathematical; electromagnetic polarization and
  energy transport are left to 10.2.


## 10.2 `sr.electromagnetic_waves`: Electromagnetic waves

### Scope

This concept explains electromagnetic waves as source-free propagating
disturbances of the electromagnetic field. It should connect Maxwell's
equations, the wave equation, transverse field structure, and energy-momentum
transport.

### Exposition

Electromagnetic waves are self-propagating disturbances of the electromagnetic
field. In a chosen frame they appear as coupled oscillations of the electric
and magnetic fields, travelling at speed \(c\) in vacuum.

In a region where the four-current vanishes, source-free Maxwell equations
imply a wave equation for the field or for the potential in a suitable gauge.
For the potential this can be written schematically as
\[
\Box A^\mu\overset{\text{source-free}}{=}0.
\]
The \(\text{source-free}\) label marks that the current source has been set to
zero.

For a plane wave moving in direction \(\mathbf k\), the source-free divergence
equations imply
\[
\mathbf k\cdot\mathbf E\overset{\text{transverse}}{=}0,
\qquad
\mathbf k\cdot\mathbf B\overset{\text{transverse}}{=}0.
\]
The \(\text{transverse}\) label marks that both field components are
perpendicular to the propagation direction.

In a simple plane wave, \(\mathbf E\), \(\mathbf B\), and the propagation
direction form a mutually perpendicular triad. The direction of energy flow is
given by the right-hand-rule direction of \(\mathbf E\times\mathbf B\).

The wave equation gives the dispersion relation \(\omega\overset{\text{wave equation}}{=}ck\). The speed is
not the speed of a disturbance through an ether-like mechanical medium. It is
fixed by Maxwell's equations and by the spacetime structure of special
relativity.

An electromagnetic wave carries energy and momentum. That is why light can heat
a surface, exert radiation pressure, and transport energy across empty space.

The wave is not an electric wave plus an independent magnetic wave. It is one
electromagnetic field disturbance whose components are constrained by Maxwell's
equations.

### Block Plan

- `overview`: Light as a field disturbance.
- `definition`: Propagating source-free disturbance.
- `derivation`: Source-free Maxwell equations.
- `explanation`: Transverse fields.
- `intuition`: The wave triad.
- `derivation_step`: Speed \(c\).
- `explanation`: Energy and momentum.
- `misconception`: Not two separate waves.
- `historical_note`: Maxwell and light.
- `summary`: Takeaway.

### Study Questions

1. Recognize the transverse triad.
2. Explain source-free.
3. Use the right-hand rule for propagation direction.
4. Explain why the fields are transverse.
5. Connect waves to radiation pressure.
6. Avoid treating \(E\) and \(B\) as independent waves.

### References

- TTM SR/CF: electromagnetic waves from source-free Maxwell equations; section-level locator recorded in `data/reference_links.csv`.
- TRR: Maxwell's identification of light as electromagnetic radiation; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The current improved graphic should be retained. It shows mutually
perpendicular electric and magnetic oscillations with propagation/energy-flow
direction.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- This concept is an excellent future candidate for interactive graphics:
  polarization, phase, and propagation direction would all benefit.

#### Atlas Issues

- Polarization may deserve its own concept when the atlas expands.


## 10.3 `sr.radiation_reaction`: Radiation reaction

### Scope

This concept introduces radiation reaction as the back-effect of emitted
radiation on an accelerating charged particle. It should explain the
energy-momentum-balance motivation and the conceptual difficulty without
turning into a full advanced treatment of Abraham-Lorentz-Dirac theory.

### Exposition

Radiation reaction is the correction to a charged particle's motion caused by
the energy and momentum it radiates away. An accelerating charge emits
electromagnetic waves. Those waves carry energy and momentum.

The ordinary Lorentz force describes how an external electromagnetic field acts
on a charge. Radiation reaction asks a harder question: how does the charge
respond to the field generated by its own accelerated motion?

Energy-momentum balance gives the motivation. Radiation carries energy and
momentum away from the particle-field system. If total energy-momentum is
conserved, the particle's motion cannot be exactly the same as it would have
been under only the applied external Lorentz force.

A driven charged oscillator gives the right intuition. Some work done by the
driver leaves as radiation rather than remaining as mechanical energy of the
particle. The motion therefore behaves as if there is a radiation-related
damping effect.

This is not ordinary friction against a material medium. It comes from the
charge's coupling to its own electromagnetic field.

The technical problem is subtle. Naive point-particle self-force equations can
produce unphysical runaway solutions or apparent pre-acceleration. These
pathologies signal that the idealization of a point charge and its self-field
must be handled with care.

In many practical regimes, radiation reaction is treated as a small correction
within an approximation. The aim is to preserve energy-momentum balance without
trusting the point-particle idealization outside its domain.

### Block Plan

- `overview`: When the charge feels its own radiation.
- `definition`: Back-reaction from emitted electromagnetic waves.
- `derivation`: Energy-momentum balance.
- `explanation`: External force versus self-effect.
- `intuition`: Radiative damping.
- `misconception`: Not ordinary friction.
- `warning`: Runaways and pre-acceleration.
- `explanation`: Effective-theory viewpoint.
- `historical_note`: A long-standing classical problem.
- `summary`: Takeaway.

### Study Questions

1. Recognize radiation reaction.
2. Explain the energy-momentum motivation.
3. Compute radiated energy from power and time.
4. Distinguish radiation reaction from ordinary friction.
5. Explain why runaway solutions are worrying.
6. Explain why approximate treatments are common.

### References

- TTM SR/CF: radiation reaction and energy-momentum balance; section-level locator recorded in `data/reference_links.csv`.
- TRR: classical self-force and radiation-reaction context; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic is adequate. A future refinement could show a charged
particle trajectory, outgoing wavefronts, and a small recoil/damping cue.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- This concept could use an advanced/details disclosure mode when the viewer
  supports more nuanced optional mathematical material.

#### Atlas Issues

- Abraham-Lorentz-Dirac and Landau-Lifshitz equations should probably become
  advanced descendant concepts if the atlas later expands into radiation theory.


## 11.1 `sr.lorentz_invariance`: Lorentz invariance

### Scope

This concept presents Lorentz invariance as the mathematical expression of the
relativity principle in special relativity. It should connect the principle of
relativity, Lorentz transformations, metric preservation, invariant scalars,
and covariant tensor equations without becoming a full group-theory treatment.

### Exposition

Lorentz invariance is the precise mathematical form of the claim that no
inertial frame is privileged in the laws of physics. A physical law should keep
the same content when rewritten between inertial frames related by Lorentz
transformations.

The principle of relativity says inertial frames are physically equivalent.
Lorentz invariance implements that idea in spacetime: the allowed frame changes
are those preserving the Minkowski interval. In matrix form, a Lorentz
transformation \(\Lambda\) preserves the metric:
\[
\Lambda^T\eta\Lambda\overset{\text{Lorentz}}{=}\eta.
\]
The \(\text{Lorentz}\) label marks the metric-preservation condition that
defines Lorentz transformations.

This is why scalar products such as \(A^\mu B_\mu\) have the same value in
every Lorentz-related inertial frame. A scalar invariant is unchanged as a
number; a vector or tensor usually has different components in different
frames, but transforms according to a consistent rule.

Tensor notation makes Lorentz invariance visible. If both sides of an equation
are tensors of the same type, changing frame transforms both sides in the same
way. The component values may change, but the equation remains true.

Electromagnetism is the central example in this atlas. Electric and magnetic
fields mix under Lorentz transformations, but the electromagnetic field tensor
transforms as one object. Maxwell theory can therefore be Lorentz-invariant
even though \(\mathbf E\) and \(\mathbf B\) separately look frame-dependent.

Lorentz invariance is not merely a tidy notation choice. In special relativity
it is a basic constraint on candidate laws: a law that singles out one inertial
frame needs a physical reason or it is suspect.

### Block Plan

- `overview`: Same laws in every inertial frame.
- `definition`: Laws keep form under Lorentz transformations.
- `explanation`: Relativity principle made mathematical.
- `derivation`: Metric preservation \(\Lambda^T\eta\Lambda\overset{\text{Lorentz}}{=}\eta\).
- `construction`: Writing covariant tensor equations.
- `example`: Four-vectors, field tensor, and energy-momentum tensor.
- `warning`: Invariant is not the same as unchanged components.
- `intuition`: Why electromagnetism fits.
- `misconception`: Not an optional decoration.
- `historical_note`: From covariance to spacetime structure.
- `summary`: Takeaway.

### Study Questions

1. Recognize Lorentz invariance as a constraint on laws.
2. Relate Lorentz invariance to the principle of relativity.
3. Use an invariant contraction to infer invariant mass.
4. Explain why tensor notation helps.
5. Distinguish invariant scalars from covariant vector/tensor equations.
6. Explain why Maxwell theory remains Lorentz-invariant when \(\mathbf E\) and \(\mathbf B\) mix.

### References

- TTM SR/CF: Lorentz covariance of relativistic equations; section-level locator recorded in `data/reference_links.csv`.
- TRR: Lorentz invariance and spacetime structure; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic is adequate. A future version could show the same tensor
equation in two frames beside the preserved light cone or metric.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- A future notation view could distinguish invariant scalar, covariant vector
  equation, and tensor equation examples.

#### Atlas Issues

- This concept overlaps with the principle of relativity and Lorentz
  transformations; keep it focused on laws and equations rather than coordinate
  transformation mechanics.


## 11.2 `sr.gauge_fixing`: Gauge fixing

### Scope

This concept explains gauge fixing as the general act of choosing one
representative from a gauge-equivalent family. It should distinguish gauge
choice from physical change, use Lorenz gauge as an example, and keep the
observable/gauge-invariant boundary clear.

### Exposition

Gauge fixing is the imposition of an extra condition on the vector potential to
remove redundant descriptive freedom. It is needed because gauge invariance
says that many potentials can represent the same physical electromagnetic
field.

The transformation
\[
A_\mu\rightarrow A_\mu+\partial_\mu\Lambda
\]
can leave the field tensor \(F_{\mu\nu}\) unchanged. A gauge condition chooses
one convenient representative from that equivalence class. It should simplify
calculation without changing the physical field.

This is why gauge fixing is not an extra law of nature. It does not add a force,
remove the electromagnetic field, or change the charge distribution. It removes
redundancy from the description.

The Lorenz gauge is a useful example:
\[
\partial_\mu A^\mu\overset{\text{Lorenz gauge}}{=}0.
\]
The \(\text{Lorenz gauge}\) label marks this as a gauge choice. It respects
Lorentz invariance and simplifies Maxwell's equations for the potential into a
wave-equation form.

Gauge fixing does not always remove every redundant degree of freedom. In
Lorenz gauge, a further transformation
\[
A_\mu\rightarrow A_\mu+\partial_\mu\Lambda
\]
preserves the condition when
\[
\Box\Lambda\overset{\text{residual gauge}}{=}0.
\]
The \(\text{residual gauge}\) label marks the extra condition on the gauge
function. This is residual gauge freedom.

After fixing a gauge, physical predictions should still be expressible in
gauge-invariant terms. If a result changes under a remaining gauge
transformation, it may be a description-dependent quantity rather than an
observable.

Gauge fixing is similar in spirit to choosing coordinates: a convenient
description can make a calculation simpler. The analogy is not perfect, because
gauge redundancy acts on field variables rather than directly on spacetime
labels.

### Block Plan

- `overview`: Choosing one description from many.
- `definition`: Gauge fixing.
- `explanation`: Why it is needed.
- `intuition`: Representative, not new physics.
- `example`: Lorenz gauge example \(\partial_\mu A^\mu\overset{\text{Lorenz gauge}}{=}0\).
- `warning`: Residual freedom can remain, \(\Box\Lambda\overset{\text{residual gauge}}{=}0\).
- `construction`: Keep observables gauge-invariant.
- `intuition`: Coordinate analogy and its limit.
- `misconception`: Not an extra law of nature.
- `historical_note`: From electromagnetic convenience to gauge theory.
- `summary`: Takeaway.

### Study Questions

1. Recognize gauge fixing.
2. Explain why gauge invariance makes it possible.
3. Check a residual-gauge condition \(\Box\Lambda\overset{\text{residual gauge}}{=}0\).
4. Explain why it is not an extra physical assumption.
5. Explain why Lorenz gauge is useful.
6. Apply gauge-invariant reasoning to two equivalent potentials.

### References

- TTM SR/CF: gauge fixing and gauge-equivalent potentials; section-level locator recorded in `data/reference_links.csv`.
- TRR: gauge choice and gauge-independent physical predictions; section-level locator recorded in `data/reference_links.csv`.

### Graphics

The existing graphic is adequate. A future refinement could show an
equivalence class of potentials with one gauge slice selecting a representative.

### Drafting Issues

#### Source Issues

- Section-level TTM and TRR locators are recorded in `data/reference_links.csv`.

#### Schema/View Issues

- Residual gauge freedom could eventually be shown as a folded derivation or
  advanced side note, but the current block kinds are sufficient.

#### Atlas Issues

- Future gauge-theory material will need a broader gauge-choice concept that is
  not limited to electromagnetism.

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
