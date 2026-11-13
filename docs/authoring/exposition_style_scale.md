# Exposition style: succinct–expansive scale

Agreed calibration from the SR-1 review, 13 November 2026. **Current target: 70.**

This is a PhysicsKG editorial convention, not a standard educational measurement.
It describes how fully an exposition expresses connections, reminders and
intermediate reasoning. It does **not** measure the difficulty of its subject,
mathematical sophistication, assumed prerequisites or a required word count.
Advanced material can be explained expansively; elementary material can be terse.
The numbers are reference points for discussion, not quantities to calculate.

Keep titles and statements concise. In bodies, allow the words needed to show
why steps follow, recall a condition or symbol, and acknowledge a non-obvious
calculation. Aim slightly below the 80 example: avoid unnecessary scene-setting
and phrases such as “That unfamiliar word”; prefer “Affine means…”. Do not pad a
complete definition, or replace missing reasoning with reassuring language.

The anchors below preserve the wording discussed in chat. They concern the same
block, **Why the inertial coordinate rule is linear**; the concise statement is
“Homogeneity gives an affine coordinate rule; a shared origin removes its
translation.” The current SR-1 version demonstrates the intermediate target.

## 20 — original, compressed exposition

An inertial coordinate grid is chosen with no distinguished place or time: the
rule converting equal event displacements should be the same wherever those
displacements occur. With continuity, this homogeneity assumption gives an
affine coordinate rule, with constant linear coefficients plus a translation.

Choosing the same origin event removes the translation. A standard boost
therefore has coefficients depending on the relative velocity, not on the
location of the event.

Homogeneity is a background assumption of this construction. Spatial isotropy
and equal rod/clock calibration also matter when fixing the coefficients.
Light-speed invariance constrains the time-space mixing, while the relativity
postulate requires a consistent inverse description.

These ingredients explain why the construction does more than merely propose a
formula that happens to preserve light rays.

## 80 — more expansive teaching draft

Suppose two observers describe the same experiment using different inertial
frames. Each has a grid of positions and a network of synchronised clocks. We
want a rule that converts one observer’s position and time coordinates into
the other’s.

Where should we begin? We assume that space and time are **homogeneous**: there
is no special place or instant at which the coordinate-conversion rule changes.
So, if we repeat the same displacement somewhere else—or at a later time—the
rule should convert it in the same way.

Together with continuity (small coordinate changes should produce small
changes), this leads to an **affine** transformation. That unfamiliar word
means a linear combination of the coordinates, possibly with a constant offset.
An offset is needed, for example, if the observers choose different events as
“position zero, time zero”.

We can simplify matters by having both observers use the same origin event.
The offset then vanishes, leaving a linear transformation. In particular, the
new time coordinate can contain terms proportional to both the old time and
the old position. We have not yet determined their coefficients—or established
that time and position must mix—but we have narrowed down the form the answer
can take.

The physical postulates now do the remaining work. Since both observers must
measure the same vacuum light speed, their coordinate rule must preserve the
forward and backward light rays. And because neither inertial frame is
privileged, exchanging the observers must give a consistent inverse rule.
Together with spatial isotropy and common rod-and-clock calibration, these
conditions fix the standard Lorentz boost.
