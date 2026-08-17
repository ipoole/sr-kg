# Knowledge Base Authoring Guide

This guide records the house style for drafting concept content. Read it before
starting a new concept, especially after a gap in the work.

## Purpose

Write each concept as a learning aid, not as a dictionary entry. The result
should feel like a compact book section: coherent, explanatory, mathematically
careful, and aware of where the concept sits in the atlas.

The style may be similar in spirit to Susskind's TTM volumes, but the text
should be original, tailored to this knowledge base, and usually a little more
compact. Use references to TTM, TRR, and other sources to locate and support
the content, not as text to paraphrase mechanically.

## Before Drafting

Before authoring a concept:

1. Read the concept's existing `nodes.csv`, `edges.csv`, content blocks, study
   questions, references, and graphic notes.
2. Look at nearby concepts: prerequisites, concepts in the same layer, and
   likely descendants.
3. Decide the scope boundary. The concept should explain itself, but avoid
   taking over material that belongs naturally to a neighbouring concept.
4. Check the project-root `KB_SCHEMA.md` for the current source schema and
   accepted block `kind` values. The implementation source of the same
   vocabulary is `CONTENT_BLOCK_KIND_DESCRIPTIONS` in `srkg/kb.py`.
5. Check `docs/authoring/concept_expositions.md` for any existing draft exposition for
   the concept, and update that draft before splitting it into CSV blocks.
6. Check whether TTM, TRR, or another registered source should be linked. Use
   `docs/authoring/SOURCE_REVIEW_WORKLIST.md` when tightening source locators. Add broad
   reference hooks while drafting if precise locations are not yet known, and
   mark those links for later locator tightening.
7. Check `docs/authoring/NOTATION_GLOSSARY.md` for recurring notation and convention
   choices before introducing or revising symbols.
8. For derivations with significant equality steps, check
   `docs/authoring/equality_annotation_style.md` and decide where annotated
   equals signs would help the learner see which result, convention, condition,
   or frame choice is being used.

After authoring each concept, pause for a small local consistency check before
moving on to the next one: block count and kinds, block titles, question count
and types, question ordering, reference links, `\cref` targets, likely concept
edges, and any graphic change.

## Concept Scope

Focus on the concept at hand. It is fine to remind the reader of prerequisites,
but do not re-teach a neighbouring concept in full. Use `\cref{label}{id}` when
the reader should be taken to the fuller treatment elsewhere.

A good concept account usually answers:

- What is the concept?
- Why is it needed?
- What problem, ambiguity, or physical situation motivates it?
- What are the main mathematical objects and equations?
- How is it derived, constructed, or justified from earlier concepts?
- What does it mean physically or geometrically?
- What does it not mean?
- How does it connect to nearby and later concepts?
- What notation and sign conventions are being used?
- Which source references support the treatment?

Not every concept needs all of these in equal weight. Foundational concepts may
need more interpretation. Technical concepts may need more construction and
derivation. High-level synthesis concepts may need more connections.

## Exposition Style

Prefer clear explanatory prose over terse formula lists. Brevity is valuable,
but a few extra words are often worth it when they prevent a learner from
silently losing the thread.

Aim for:

- Direct sentences.
- Smooth transitions between physical meaning and mathematics.
- Equations introduced in prose before they are used.
- Definitions that are precise but not cryptic.
- Derivations that state the assumptions being used.
- Warnings where common shortcuts hide a conceptual trap.
- Consistent notation within the concept and across linked concepts.

Avoid:

- Marketing-style summaries.
- Unexplained symbol changes.
- Long digressions into material owned by another concept.
- Phrases such as "obviously", "clearly", or "it is easy to see" where a step
  may not be obvious to a learner.
- Leaving a formula as a black box when one or two sentences would reveal the
  structure.

## Mathematics And Notation

Use MathJax notation consistently with nearby concepts. If a convention matters,
state it near first use. Examples include metric signature, index placement,
units, coordinate ordering, and whether \(c\) is explicit.

Use natural units, \(c\overset{\text{units}}{=}1\), as the default working
convention once the learner has enough context for it. This reduces algebraic
clutter and makes spacetime symmetry clearer. Keep \(c\) explicit when it is
pedagogically important:
early introductions to \(ct\), dimensional checks, source terms such as
\(j^\mu=(c\rho,\mathbf j)\), and physically famous or interpretive results
such as \(E_0\coloneqq mc^2\),
\(E^2\overset{\text{mass shell}}{=}\mathbf p^2c^2+m^2c^4\), or
\(\Delta m\overset{E_0=mc^2}{=}\Delta E/c^2\). If a block switches
convention, say so near the first equation: for example, "Setting
\(c\overset{\text{units}}{=}1\)" or "Restoring \(c\)".

Treat `=` as the unmarked exact equality, not as the universal mathematical
relation. When revising equations, ask what licenses each equality. Use
\(\coloneqq\) for definitions, \(\equiv\) for identities, and annotated
equals signs such as \(\overset{\text{metric}}{=}\),
\(\overset{\text{Lorentz}}{=}\), \(\overset{\text{rest frame}}{=}\), or
\(\overset{\text{stationary}}{=}\) when the equality depends on a convention,
previous result, physical law, frame choice, gauge choice, or constraint. Leave
routine algebra and arithmetic plain unless the provenance is the teaching
point. Use \(\simeq\) for approximations, and reserve \(\sim\) for a stated
equivalence or asymptotic relation.

Annotated equality labels should be compact signposts, not the explanation
itself. Explain the label in ordinary prose near the equation, especially when
the equality uses a result or condition that a learner may not reconstruct
automatically. For example, if a derivation uses
\(\overset{\text{metric}}{=}\) and \(\overset{\text{mass shell}}{=}\), the
surrounding text should say that the first label expands a contraction using
the Minkowski metric and the second imposes the invariant-mass condition. Avoid
putting essential explanation only in UI hover text or trying to hide a long
sentence above the equals sign.

When an equality annotation corresponds to another concept, link that concept
in prose with `\cref{label}{id}` rather than putting a `\cref` inside
`\overset`. The authored text should remain understandable in Markdown, CSV,
printed output, and any future viewer. See
`docs/authoring/equality_annotation_style.md` for the full house style.

When deriving:

- Identify the starting assumptions.
- Keep important intermediate lines when they carry conceptual weight.
- Use `derivation_step` blocks for small algebraic steps only when the step is
  worth preserving as its own teaching unit.
- Do not expand every algebraic manipulation by default. Include hand-holding
  where it prevents a known or likely misunderstanding.
- End by naming the result and saying what it tells the reader.

If notation is shared across many concepts or likely to become a recurring
source of confusion, add or update an entry in `docs/authoring/NOTATION_GLOSSARY.md`.
For generic four-vector examples, prefer neutral symbols such as \(V^\mu\) and
\(W^\mu\). Reserve \(A^\mu\) and \(A_\mu\) for the electromagnetic
four-potential, or for a non-electromagnetic vector field only when the context
is explicit.

## Draft Expositions

Keep a readable exposition draft before or alongside the CSV block split. The
current home for these drafts is `docs/authoring/concept_expositions.md`.

Use one top-level section per concept, labelled with display ID, semantic ID,
and title. Within that section, use ordinary Markdown subsections where helpful.
The draft should read like a compact book section before it is divided into
blocks.

This intermediate draft has two purposes:

- It gives a human-readable text for review before CSV escaping and block
  splitting obscure the flow.
- It preserves the coherent exposition if we later revise block boundaries,
  block kinds, or viewer presentation policy.

The CSV content blocks remain the source consumed by the application. The
exposition file is an authoring and review aid, not a second runtime source of
truth.

Use the `Drafting Issues` subsection to record non-blocking issues discovered
while writing: missing concepts, possible concept splits or merges, weak edge
types, insufficient block kinds, notation glossary needs, reference gaps,
graphic concerns, or viewer limitations. Fix issues immediately only when they
block coherent authoring or would make the committed KB misleading. Otherwise
leave a clear note and keep the concept pass moving.

For longer concepts, group drafting issues under short subheadings where useful:

- `Source Issues`: missing or imprecise TTM, TRR, page, section, or source links.
- `Schema/View Issues`: block kinds, viewer policy, disclosure, or rendering
  questions.
- `Atlas Issues`: missing concepts, concept splits/merges, numbering gaps, or
  weak concept-edge vocabulary.
Use `docs/authoring/SOURCE_REVIEW_WORKLIST.md` and `docs/authoring/NOTATION_GLOSSARY.md` to collect
issues that recur across many concepts, rather than repeating the same generic
note in every concept.

## Block Splitting

Draft the concept first as a coherent exposition. Then split it into blocks.
The block order should usually follow the exposition order.

Each block should be the smallest useful teaching unit: large enough to make
sense when read, small enough to be moved, folded, searched, referenced, or
reviewed independently.

Keep block splitting stricter as concepts become longer. Long concepts may
legitimately produce many blocks, but one large `explanation` block should be
avoided when it contains several separable teaching moves. Use an `overview`
block when a concept needs a short orientation before the definition or detailed
development.

Every block must have:

- A stable `block_id`.
- The owning `concept_id`.
- A numeric `sequence`.
- A semantic `kind`.
- A short, non-empty `title`.
- A substantive `body`.

Use `kind` to describe what the block is, not how the viewer should display it.
Visibility, folding, callouts, grouping, and ordering variations are viewer
policy. Do not add presentation instructions to the KB content unless the
schema explicitly supports them.

Multiple blocks with the same `kind` are allowed. For example, a concept may
have several `derivation_step` or `example` blocks.

Use the richer structural kinds sparingly:

- Use `result` for a central equation, theorem statement, named conclusion, or
  formula that the learner should be able to find again quickly. Do not use it
  for every intermediate equation.
- Use `decomposition` when an object is explicitly split into components,
  frame-dependent parts, or extracted pieces.
- Use `convention` for local notation, sign, unit, coordinate, or gauge
  conventions. A convention is not necessarily a warning; reserve `warning` for
  traps, caveats, and limitations.

## Cross-References And Edges

Use concept links deliberately. A `\cref` should help the learner move to a
specific supporting idea, not merely decorate every familiar term.

When adding or revising concept edges:

- Prefer edges to earlier or prerequisite concepts where possible.
- Use `DERIVES_FROM` only when there is a defensible derivation dependency.
- Use `CONSTRUCTED_FROM` when a concept is built algebraically,
  differentially, or structurally from another concept, but the relationship is
  weaker than a theorem-style derivation.
- Use `COMPONENT_OF` when a concept is a component, frame split, or extracted
  part of another concept.
- Use `INSTANCE_OF` when a concept is a concrete example, named instance, or
  special case of a more general concept.
- Use `REQUIRES` for concepts a learner should know first.
- Use `RELATED` sparingly when the connection is real but not yet a sharper
  relation.
- Note recurring cases where `RELATED` feels too vague; those are candidates
  for future edge-type design. Collect edge-type review notes in
  `docs/authoring/EDGE_TYPE_REVIEW_WORKLIST.md`.

Keep the derivation tree in mind. One long-term goal is to trace important
concepts back toward postulates, axioms, and foundational definitions.

## References

Add references as first-class KB material. Prefer a short rendered citation
such as `TTM II, 1.3 General Lorentz Transformation`, backed by fuller
bibliographic detail in `references.csv`.

Use both TTM and Penrose's `TRR` where relevant. It is acceptable to add a broad
reference link during drafting, with a note that the locator needs tightening.
Prefer not to invent precise page or section references from memory.

Link references to the most specific useful item:

- A concept when the source supports the whole treatment.
- A content block when it supports a particular definition, derivation, or
  explanation.
- A study question when the question is adapted from or motivated by a source.

References should support authoring and later review. They do not need to
clutter the prose.

## Study Questions

Study questions should test understanding of the concept just authored. Use the
current question types in `KB_SCHEMA.md`: `short_answer`, `multiple_choice`,
and `calculation`.

Aim for 3 to 6 questions per concept. Use no more than three calculation or
symbol-manipulation questions for one concept; the rest should check conceptual
understanding, interpretation, common mistakes, or links to nearby concepts.
Questions should start easy and get progressively more challenging.

A healthy question set usually includes:

- One conceptual check.
- One common-misconception check, where relevant.
- One short calculation or symbolic manipulation, where relevant.
- One convention or dimensional check, such as setting \(c\overset{\text{units}}{=}1\) or restoring
  factors of \(c\), where relevant.
- One connection question linking to nearby concepts, where useful.

Order the questions deliberately. Start with recognition or basic
interpretation, then move through conceptual explanation, calculation or
symbolic manipulation, and finally a connection or synthesis question if the
concept supports one.

Answers should be concise but complete enough for self-study.

Study questions are currently authored separately from content blocks. This may
change later, so keep question IDs stable and avoid depending on presentation
details of the current viewer.

## Graphics

All concepts need a graphic (if only to use as icon in the graph). A good
graphic should reveal structure that prose or equations alone make hard to see.

Useful graphics may show:

- Geometry, such as axes, cones, fields, or transformations.
- Directional relationships, such as propagation or flux.
- Component relationships, such as tensor packaging or vector decompositions.
- Historical or conceptual structure where that aids learning.

Graphics should use shared motifs where possible so global style improvements
remain easy.

Treat graphics as part of the concept-authoring pass, but revise them with
care. The existing graphics are protected by Git history, so they can be
recovered, but do not rewrite many concept graphics in one undifferentiated
change. Prefer a concept-by-concept workflow:

1. Review the existing icon/detail graphic.
2. Decide whether the current idea should be retained, refined, or replaced.
3. Reuse shared motifs where possible.
4. Regenerate a review sheet or viewer output.
5. Visually inspect the result before handing it back.

If an old graphic contains an idea worth preserving but the new graphic takes a
different approach, record that in the commit or discussion note rather than
silently losing it.

## Review Checklist

Before finishing a concept, check:

- The concept has a clear scope and does not trespass heavily into neighbouring
  concepts.
- Definitions, equations, assumptions, and conventions are explicit.
- Recurring notation agrees with `docs/authoring/NOTATION_GLOSSARY.md`.
- The prose is readable as a coherent book-like section.
- Blocks have good titles and appropriate semantic kinds.
- `sequence` reflects the intended narrative order.
- Important dependencies have `\cref` links and concept edges where appropriate.
- Derivation claims are backed by enough mathematical detail.
- Common misconceptions or caveats are included where useful.
- Study questions cover concept, calculation, and connection as appropriate.
- The concept has 3 to 6 study questions, with no more than three calculation
  or symbol-manipulation questions.
- Study questions start easy and become progressively more challenging.
- References are linked at the most specific useful level; broad source
  locators are recorded in `docs/authoring/SOURCE_REVIEW_WORKLIST.md`.
- Any graphic need or graphic defect is recorded.
- Validation and tests pass after CSV edits.
