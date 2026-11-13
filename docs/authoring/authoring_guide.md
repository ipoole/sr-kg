# Knowledge Base Authoring Guide

Use this guide for consistent teaching content. Read it before an authoring pass
and revisit it between modules. The [technical reference](technical_reference.md)
covers storage, graphics procedures and commands; the [schema](../design/kb_schema.md)
records the current implementation.

## Working method

Work within `domains/<id>/`, using current module membership for authoring batches.
Read each concept's blocks, edges, questions, references and graphic, plus its
neighbours, before changing it. Define its scope and genuine dependencies first.
Complete and check one module at a time; prefer one local commit per module.

Runtime CSV is authoritative. Separate exposition drafts are optional working
notes, not another publication to maintain. Preserve useful scope decisions and
unresolved questions in the domain's review/source worklists. Keep concept, block,
question and clarification identities stable: notes, ticks and tutorials use them.

## Teaching style

Aim for **70 on our succinct–expansive scale**. The [20 and 80 examples](exposition_style_scale.md)
calibrate expansiveness, not subject difficulty, prerequisites or word count.
Keep titles and statements concise; let bodies explain the reasoning.

Use “because”, “so”, “given” and similar connections when they help the reader
follow an argument. Recall symbols and measurement conditions, with brief
parenthetical reminders where useful. Explain technical terms directly (“Affine
means…”). Acknowledge substantial algebra or non-obvious results, but do not hide
the step being taught behind “after some algebra”. Avoid padding, unexplained
symbol changes, patronising language and “obviously”. Formal derivations also
need connective prose.

Keep qualifications that help understand the science: assumptions, limitations,
alternative routes and why a step follows. Put commentary about our authoring
process, graph maintenance or migration decisions in review notes. Avoid repeatedly
telling learners how the KB was constructed.

## Blocks and sequential reading

Order a concept's blocks as a sensible exposition for someone reading them all
in sequence. Usually introduce meaning and motivation before detailed arguments
and applications; place conventions before the calculations that need them.
The first Definition supplies concept-reference previews, so make it the canonical
definition of the concept. Repeated kinds are allowed.

Every block has a stable ID, owner, sequence and kind, plus three authored levels:

| Level | Purpose |
| --- | --- |
| Title | Identify what this particular block contains; its kind badge is not its title. |
| Statement | Give its useful result or interpretation succinctly, visible while folded. |
| Body | Supply reasoning, detail or illustration that makes opening worthwhile. |

Write statements explicitly, as results rather than teasers or outlines. Include
essential conditions; a formula is useful if its symbols are understandable.
Do not automatically extract the first sentence. A body should add substance
rather than merely paraphrase its statement. Definitions can be short.

Aim for bite-sized blocks a learner can digest and mark read in a few minutes,
without imposing a word limit. Split long arguments at meaningful results. Each
part should state its starting result, introduce the notation it needs and reach
an identifiable conclusion. It may assume a stated input; it need not reproduce
the proof of that input. Prefer “Given [result], …” to “As shown above, …”.

For example, a variational argument might have separate Derivation blocks for
forming the first variation, integrating by parts, and using arbitrary variations.
The second restates the first's needed expression, rather than repeating its
proof. A recipe selecting Derivation includes **all** those instances, not just
the first. Reuse the same title, statement and body in every occurrence.

## Block kinds

The agreed consolidated vocabulary is:

| Kind | Purpose |
| --- | --- |
| Definition | Precise meaning. |
| Derivation | An argument that establishes a result or constructs an object. |
| Explanation | Meaning, motivation, interpretation and intermediate reasoning. |
| Intuition | A qualitative mental model, analogy or visual way of thinking. |
| Example | A concrete illustration, including a worked calculation. |
| Graphic | A visual contribution, with an informative caption. |
| Convention | A choice of notation, signs, units, coordinates or gauge. |
| Warning | A limitation, trap or misconception. |
| Historical note | A historical problem, contribution or change of understanding. |
| Advanced | Further treatment for readers ready for greater depth or sophistication. |

Usually provide a Definition, Derivation and Explanation, adding other kinds
when useful. Do not invent proofs for definitions, postulates or primitive
structure. Derivation blocks in particular must explicitly knit together the
results supplied by linked dependent concepts: state the inputs being used and
show the argument that combines them into this block's result. Naming or linking
the dependencies is not enough. Explanation blocks should make those connections
accessible to a less experienced reader; their exposition can differ substantially
even when they use the same dependencies.
Advanced is supplementary to the chosen core treatment: do not hide a necessary
premise there merely because it is difficult. It can contain more technical
reasoning or perhaps an advanced application or consequence of the concept;
its title should identify the subject, not merely say “Advanced”.
Historical notes should explain the scientific contribution, not give detached
biographies; source attribution and treat disputed priority neutrally.

Runtime supports these ten authoring kinds, including `advanced`. Eight legacy
kinds remain loadable while existing modules are converted individually; new
authoring uses the consolidated vocabulary. See the [migration mapping](technical_reference.md#kind-migration).
Do not relabel blocks just to make them appear in a recipe.

## Local clarifications and reading trees

Blocks do not call other owned blocks, even within their own concept. Use local
clarifications for optional algebra, reminders or “Why exactly?” details:
`\explanation{stable-slot}{Title}{Body}`. They may nest, but have title/body only,
not formal statements or independent read ticks. Keep the main argument readable
without opening them. Preserve named slots and existing anonymous clarification
paths; annotations depend on them. Do not add `\explain` borrowing calls.

Reading trees are generated from graph edges and recipe-selected kinds. They
include every block of each selected kind, preserving authored sequence within
that kind; recipes currently group kinds in their specified order. Thus local
sequential order and recipe presentation need not be identical. Check both.
Never rely on an omitted block to supply an unstated premise.

Use `\cref{label}{concept.id}` for terminology or excursions; it previews the
canonical Definition. To point to a particular argument, use its stable block ID,
e.g. `\cref{the boost}{sr.lorentz_transformations.boost_formula}`. A block preview
shows its title, kind, statement and optional full body; “Go to block” opens its
owning concept and reveals the block. Previewing leaves the current reading tree
and selection in place. Neither reference creates a branch or dependency edge:
actual prerequisite supports still belong in the graph.

Here “concept:block” describes the destination, not literal colon syntax: use
the exact `block_id` from the content table. Link the needed result by name
(“Given the invariant norm, …”), rather than “click here”. Prefer a block target
when the reader needs a particular proof or qualification; use a concept target
for a definition. Keep the surrounding argument understandable without opening
the preview, and avoid self-links or links on every occurrence of a term.

## Edges and arguments

| Relation | Meaning |
| --- | --- |
| `DERIVES_FROM` | Genuine derivation dependency. |
| `CONSTRUCTED_FROM` | Structural, algebraic or differential construction. |
| `REQUIRES` | Prerequisite understanding. |
| `COMPONENT_OF` | Component or extracted part. |
| `INSTANCE_OF` | Example or special case. |
| `RELATED` | A useful connection without a sharper relation. |

Derivation trees follow the first two; Teaching also follows `REQUIRES`.
Derivation/construction imply prerequisite understanding, so do not duplicate
these with `REQUIRES`. Taxonomic and Related edges imply no prerequisite, though
an independently justified Requires edge can coexist with taxonomy.

Write each justification as a self-contained sentence saying how the source
uses the destination. The viewer supplies the relationship introduction; avoid
repeating “because” or assuming one particular reading path. Review prose and
graph together, keep routes traceable to foundations, and distinguish alternative
arguments from jointly necessary premises. Do not add shortcut dependencies for
convenient reading-tree access.

## Equations, questions and graphics

State consequential notation and assumptions near their use. Follow the
[notation glossary](notation_glossary.md) and [equality style](equality_annotation_style.md).
Use explicit `c` in early introductions and dimensional checks; announce changes
to natural units. Split long display calculations into meaningful `aligned` rows
for phone widths.

In CSV, use **one** backslash: `\(\nabla_\mu V^\nu\)`,
`\[G_{\mu\nu}=\kappa T_{\mu\nu}\]`, `\cref{label}{gr.metric_tensor}`.
Doubled delimiters/commands do not render correctly. Inside `aligned`, row breaks
are `\\` followed by whitespace or a newline. CSV quoting is separate from TeX.

Write 3–6 progressive questions, normally with at most three calculations:
interpretation, misconception checks, useful numerical/algebraic work and
synthesis. Prefer automatic multiple choice when plausible distractors genuinely
test understanding; use self-assessment when recognition would make the task
shallow. Answers should teach, not just repeat the correct option. Keep question
and option IDs stable. See [technical details](technical_reference.md#study-questions).

Graphics should contribute geometry, comparison or a memorable visual model.
Concepts need icons and useful detail variants; module graphics are optional
chapter-like mnemonics. Keep drawings, captions, registry and tests synchronised;
inspect rendering and legibility. See the [graphics workflow](technical_reference.md#graphics).

## Before handing back

Check scope, sequential flow, three-level content, assumptions, graph supports,
references, questions and graphics. Retain source IDs, clarification paths and
tutorial targets. Verify actual MathJax rendering at phone and desktop widths;
review validation warnings, and run appropriate unit/browser checks. Regenerate
ignored `output/PhysicsKG.html` for manual review; do not commit it. Record any
remaining issues. Commands and ownership details are in the [technical reference](technical_reference.md).
