# Equality Annotation Style

## Objective

Use mathematical notation and surrounding prose so that the exposition
communicates **why an equality holds**, not merely that its two sides are equal.

The motivation is pedagogical. In physics, the ordinary equals sign is routinely used for several quite different claims: definitions, mathematical identities, physical postulates, constraints, substitutions from previous results, approximations, choices of units, and simple algebra. For an experienced reader the provenance is often reconstructed unconsciously; for a learner it can be precisely the missing step.

SR-KG should make that provenance unusually explicit, while keeping the durable
content readable as authored text.

This fits the existing authoring philosophy: concepts are intended as compact learning sections rather than dictionary entries, derivations should state their assumptions, and significant dependencies should link back to earlier concepts. The current KB should remain structurally simple, with semantic content blocks rather than introducing a fine-grained derivation graph at this stage.

## Core Principle

Treat `=` as the **unmarked case**, not the universal relation.

The notation should answer, where useful:

> **What licenses this step?**

However, do not annotate every trivial manipulation. The objective is increased
semantic clarity, not a forest of decorated equals signs.

A useful rule is:

**Annotate an equality when knowing the reason for the equality contributes to understanding the physics or the logical structure of the derivation.**

Thus

\[
a+b=b+a
\]

needs no annotation in ordinary exposition, whereas

\[
E^2
\overset{\text{four-momentum invariant}}{=}
\mathbf p^2c^2+m^2c^4
\]

probably does.

## Prose Carries The Explanation

The preferred house style is:

1. Use a short equality annotation to mark **where** a result, convention, frame
   choice, constraint, or physical law is being used.
2. Put the explanation of that annotation in the associated prose immediately
   before or after the equation.

The annotation should be a compact signpost, not the full teaching content.

Good:

\[
p_\mu p^\mu
\overset{\text{metric}}{=}
\frac{E^2}{c^2}-\mathbf p^2
\overset{\text{mass shell}}{=}
m^2c^2.
\]

with nearby prose such as:

> The label "metric" marks the expansion of the four-momentum contraction using
> the Minkowski metric. The label "mass shell" marks the physical condition that
> this invariant norm is fixed by the rest mass.

Less good:

- relying on a long annotation above the equals sign;
- relying on tooltip or popover text to explain the mathematical step;
- putting essential derivation logic only in viewer-specific behaviour.

Interactive affordances may be useful later, but they should be optional
presentation aids. The authored KB should remain understandable in plain text,
CSV, Markdown, printed output, and any future viewer.

---

## SR-KG Equality Vocabulary

### 1. Definition

Use

\[
A \coloneqq B
\]

when \(A\) is being **defined** by \(B\).

Examples:

\[
\gamma \coloneqq \frac{1}{\sqrt{1-v^2}}
\]

\[
U^\mu \coloneqq \frac{dx^\mu}{d\tau}.
\]

This should replace the present common practice of using `=` for definitions.

**House rule:** reserve `\coloneqq` for definition. Do not use `\equiv` for definition.

That leaves `\equiv` with a cleaner mathematical meaning.

---

### 2. Mathematical identity

Use

\[
A\equiv B
\]

when equality holds identically for all values in the stated domain, rather than as the result of a physical condition.

Examples:

\[
\cosh^2\phi-\sinh^2\phi\equiv1
\]

or an algebraically identical rewriting.

Use this relatively sparingly. Ordinary algebra inside a derivation can still use `=`.

---

### 3. Ordinary mathematical equality

Retain plain

\[
A=B
\]

for equality whose provenance is immediate from the surrounding mathematics and carries no particular conceptual significance.

Examples include routine arithmetic, substitution of numbers, rearrangement and short algebraic transformations.

This becomes the **low-information equality**.

---

### 4. Equality by a previously established result

This is the most important decorated-equality convention for SR-KG.

Use an annotated equals sign:

\[
A
\overset{\text{Lorentz transformation}}{=}
B.
\]

Where possible, ordinary surrounding prose should link to the concept that
supplies the result.

Avoid putting `\cref` inside `\overset`; it is visually noisy and likely to be
fragile in MathJax. If a future viewer makes compact clickable markers easy,
that can be revisited. For now, use a compact marker above the equality and put
the link in prose, for example

\[
A\overset{\mathrm{LT}}{=}B
\]

where the neighbouring sentence links to `\cref{Lorentz transformations}{sr.lorentz_transformations}`.

This should cover applications of:

- previous equations;
- established mathematical theorems;
- previously derived SR results;
- conservation laws;
- transformation laws;
- other named results.

The annotation should normally name the **reason**, not merely repeat an equation number.

Good:

\[
p_\mu p^\mu
\overset{\text{Lorentz invariant}}{=}
m^2.
\]

Less useful:

\[
p_\mu p^\mu\overset{(17)}{=}m^2.
\]

---

### 5. Equality by physical law or postulate

Physical assertions deserve particularly clear provenance.

For example,

\[
c'
\overset{\text{light-speed postulate}}{=}
c
\]

or

\[
\partial_\mu j^\mu
\overset{\text{charge conservation}}{=}
0.
\]

A subtle distinction should be preserved between **stating the law itself** and **using the law in a derivation**.

When introducing Maxwell's equation,

\[
\nabla\cdot\mathbf B=0
\]

may be left visually simple because the surrounding prose explicitly says “Maxwell's equation states...”.

Later, when it is invoked to eliminate a term,

\[
\cdots
\overset{\nabla\cdot\mathbf B=0}{=}
\cdots
\]

is much more informative.

Thus the notation need not make every displayed physical law typographically exotic.

---

### 6. Equality under a condition or constraint

Use an annotation naming the condition:

\[
E
\overset{\mathbf p=0}{=}
mc^2,
\]

\[
\Delta x
\overset{\Delta t=0}{=}
\gamma\,\Delta x'.
\]

This is particularly valuable in relativity, where many familiar-looking equations hold only:

- in the rest frame;
- for simultaneous events in one particular frame;
- along a worldline;
- for lightlike separation;
- under a gauge choice;
- on shell;
- subject to boundary conditions.

The annotation exposes the hidden qualifier.

---

### 7. Choice of units or convention

Avoid allowing

\[
c=1
\]

to masquerade as an ordinary physical equality.

Prefer prose plus notation such as

\[
c\overset{\text{units}}{=}1
\]

when emphasizing the change, followed thereafter by formulas written in natural units.

Likewise metric-signature, coordinate-ordering and similar convention choices should be stated explicitly rather than encoded as if they were physical results.

---

### 8. Approximation

Do not use `=`.

Use

\[
A\simeq B
\]

for an approximation, with the regime stated where useful:

\[
E
\simeq_{\,v\ll1}
m+\frac12mv^2
\]

although ordinary prose such as “for \(v\ll1\)” may render better than putting the condition directly on the symbol.

Use `\sim` only where its meaning is genuinely asymptotic or otherwise explicitly defined. Do not use `\sim` casually as another “approximately”.

---

### 9. Equivalence rather than equality

Use

\[
A\sim B
\]

only when an actual equivalence relation is intended.

Examples include gauge-equivalent configurations or objects equivalent modulo some transformation.

This distinction matters later in the KB because

\[
A_\mu
\quad\text{and}\quad
A_\mu+\partial_\mu\Lambda
\]

are not literally identical fields, although they may represent the same electromagnetic physics.

Do not overload `=` to mean “physically equivalent”.

---

## Derivation style

The largest gain will come from **chains of equality**.

Instead of

\[
E^2=p_\mu p^\mu=p^2+m^2=m^2,
\]

prefer something structurally like

\[
E^2
\overset{\text{four-momentum}}{=}
\mathbf p^2+m^2
\overset{\mathbf p=0}{=}
m^2.
\]

The reader can now see that the two equals signs perform completely different jobs.

Another example:

\[
ds'^2
\overset{\text{Lorentz transformation}}{=}
dt^2-dx^2
\equiv ds^2.
\]

Here the first step invokes physics/mathematical structure already established; the final relation expresses the identity of the invariant interval represented in the two coordinate systems.

This is exactly the sort of distinction that SR-KG can make better than an ordinary textbook.

---

## Annotation granularity

Annotations should be **short**.

Prefer:

\[
\overset{\text{Lorentz transform}}{=}
\]

rather than:

\[
\overset{\text{using the Lorentz transformation derived in the previous section}}{=}.
\]

The surrounding prose supplies the detail.

A sensible visual vocabulary would be approximately one to four words:

`definition`, `rest frame`, `lightlike`, `Lorentz transform`, `mass shell`, `energy conservation`, `Gauss theorem`, `c=1`, etc.

Where the justification is purely local, use the actual condition:

\[
\overset{x=0}{=}.
\]

Where it comes from another SR-KG concept, use the concept's short name in the
annotation and link to the concept in prose.

---

## What should *not* be annotated

Do not write

\[
a(b+c)
\overset{\text{distributivity}}{=}
ab+ac
\overset{\text{collect terms}}{=}
\cdots
\]

unless distributivity itself is the teaching point.

Likewise, routine cancellation, substitution and arithmetic generally remain plain `=`.

A good editing test is:

> If I removed this annotation, would a competent but learning reader have to infer a significant assumption, physical principle, previous result or special condition?

If yes, annotate it.

If no, leave `=` alone.

---

## Relationship to the knowledge graph

For the first revision, **do not create equation-level nodes or equality-level graph edges**.

The current design deliberately keeps the durable KB at concept level plus ordered content blocks and explicitly postpones a fine-grained block graph.

Instead:

1. Put provenance directly into authored mathematical notation.
2. Explain provenance in the surrounding prose.
3. Hyperlink ordinary prose to existing concepts where appropriate.
4. Continue using concept-level `PREREQUISITE`, `DERIVES_FROM`, and `RELATED` edges for atlas structure.
5. Note cases where equality annotations expose missing concepts or weak concept edges.

This provides much of the benefit of a derivation graph without committing the schema to one.

There is nevertheless an interesting longer-term possibility: annotated equalities could later be **machine-readable derivation evidence**. A derivation such as

\[
A
\overset{X}{=}
B
\overset{Y}{=}
C
\]

already contains the beginnings of the provenance graph

\[
X\rightarrow(A=B),\qquad
Y\rightarrow(B=C).
\]

That should be regarded as a future opportunity, not a requirement for this revision.

---

## Revision procedure

The revision should be carried out concept-by-concept, in the same order as the current authoring pass.

For **every displayed and inline mathematical use of `=`**, classify it mentally as one of:

1. definition;
2. identity;
3. routine mathematical equality;
4. application of previous result/theorem;
5. physical law/postulate;
6. condition/constraint;
7. convention/units;
8. approximation;
9. equivalence rather than literal equality.

Then revise only where the classification warrants a different notation or provenance annotation.

Particular attention should be paid to `derivation` and `derivation_step` blocks, but definitions and explanations should also be checked.

---

## Proposed house-style summary

The core notation should be:

\[
\boxed{
\begin{aligned}
A\coloneqq B &\quad &&\text{definition}\\
A\equiv B &&&\text{identity}\\
A=B &&&\text{routine exact equality}\\
A\overset{X}{=}B &&&\text{equality because of }X\\
A\simeq B &&&\text{approximation}\\
A\sim B &&&\text{specified equivalence/asymptotic relation}
\end{aligned}}
\]

with \(X\) used particularly for:

- a previously established SR-KG concept/result;
- a physical law;
- a theorem;
- a constraint or special case;
- a frame, gauge or state condition.

Where \(X\) corresponds to an existing concept, link to that concept in the
surrounding prose rather than trying to make the equality annotation itself
clickable.

## Recommended first experiment

Before revising the whole corpus, apply this policy thoroughly to **one equation-rich concept**, ideally a concept containing an actual multi-stage derivation rather than an introductory concept such as inertial frames.

That pilot should answer practical questions:

- how dense the annotations should be before they become distracting;
- how much explanatory prose is needed around annotated equalities;
- whether the label vocabulary is stable across concepts;
- whether a future viewer affordance would genuinely add value beyond the prose.

The convention is recorded in `docs/authoring/NOTATION_GLOSSARY.md` and the
mathematics section of `AUTHORING_GUIDE.md`; use it systematically during
exposition review.

The underlying editorial idea can be stated very simply:

> **An equation should show not only what is equal, but—when it matters—why it is equal.**
