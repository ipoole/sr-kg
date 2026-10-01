# Knowledge Base Authoring Guide

Use this guide to produce consistent, efficient concept content. Read it before
starting a new authoring pass and revisit the relevant sections between modules.

## Editorial Aim

Write a compact learning aid, not a dictionary entry. Each concept should:

- define the idea and explain why it is needed;
- introduce equations in prose and state assumptions and conventions;
- explain physical or geometric meaning and common misconceptions;
- respect the scope of neighbouring concepts; and
- connect to prerequisites, descendants, and sources.

Aim for direct sentences and smooth transitions between mathematics and
interpretation. Avoid marketing language, unexplained symbol changes,
unnecessary digressions, and words such as "obviously" when a learner may need
the missing step.

## Before Drafting

1. Read the concept's node, edges, blocks, questions, references, and graphic
   notes, plus nearby prerequisite and descendant concepts.
2. Check the [schema](../design/kb_schema.md), `notation_glossary.md`, and the relevant domain
   plan or exposition file.
3. Define the scope boundary. Use `\cref{label}{id}` rather than re-teaching
   material owned by another concept.
4. Check `equality_annotation_style.md` for derivations with meaningful
   equality steps.
5. Identify useful registered sources. Record uncertain locators in
   `source_review_worklist.md` rather than inventing precision.

After each concept, check its block structure, questions, references,
cross-references, edges, notation, and graphic before continuing.

## Mathematics And Notation

Follow nearby notation and state consequential choices at first use: metric
signature, units, coordinate order, index placement, frame, and gauge.

Use natural units, \(c\overset{\text{units}}{=}1\), once the context is clear.
Keep \(c\) explicit for early introductions, dimensional checks, source terms,
and familiar interpretive results. Announce any switch of convention.

Use mathematical relations deliberately:

- \(\coloneqq\) for definitions;
- \(\equiv\) for identities;
- \(\simeq\) for approximations;
- plain \(=\) for exact algebra; and
- compact annotated equality labels when a result depends on a law,
  convention, frame, gauge, or constraint.

Explain annotated equalities in prose. Link supporting concepts with `\cref`;
do not place a cross-reference inside `\overset`. Preserve intermediate
derivation steps only when they carry conceptual weight.

Use neutral \(V^\mu\) and \(W^\mu\) for generic four-vectors. Reserve
\(A^\mu\) for the electromagnetic four-potential unless another use is made
explicit. Add recurring notation decisions to `notation_glossary.md`.

### CSV And MathJax Escaping

CSV is not a Python, JSON, or shell string literal. Use exactly one backslash:

- inline maths: `\(\nabla_\mu V^\nu\)`;
- display maths: `\[G_{\mu\nu}=\kappa T_{\mu\nu}.\]`; and
- cross-references: `\cref{Covariant derivative}{gr.covariant_derivative}`.

Never write doubled forms such as `\\(\\nabla_\\mu V^\\nu\\)`.
MathJax will treat them as escaped text and may display raw notation.

CSV quoting is separate. Quote a complete field containing a comma, newline, or
double quote, and double embedded CSV quotes. Do not add backslashes to repair
CSV structure.

After editing equations:

1. run the real-data tests to catch column and escaping errors;
2. check blocks, questions, answers, and module prose; and
3. confirm a representative generated page contains MathJax output rather than
   raw delimiters or commands.

## Expositions And Blocks

Draft coherent prose before or alongside the CSV split. Use the relevant
exposition file, with one section per concept labelled by semantic ID and title.
Expositions are working drafts and review notes; runtime CSV remains authoritative.
They need not mirror later CSV edits. Before retiring a completed draft, preserve
any unique scope decisions and unresolved issues. Prefer semantic IDs in draft
headings so renumbering does not create maintenance work.

Record non-blocking concerns under `Drafting Issues`. Route recurring source,
notation, and edge concerns to their worklists. Fix an issue immediately only
when it blocks coherent authoring or makes the KB misleading.

Split the exposition into the smallest useful teaching units. Every block needs
a stable ID, owner, numeric sequence, semantic kind, short title, and
substantive body. The sequence should preserve the exposition's narrative.

Use block kinds semantically, not as presentation instructions. In particular:

- `overview`: short orientation;
- `result`: a central theorem, equation, or conclusion worth finding again;
- `derivation_step`: a meaningful algebraic step;
- `decomposition`: an explicit split into components or parts;
- `convention`: notation, sign, units, coordinates, frame, or gauge; and
- `warning`: a genuine trap, caveat, or limitation.

Repeated kinds are allowed. Avoid one large explanation block containing
several separable teaching moves.

## Cross-References And Edges

Add a `\cref` only when following it helps the learner. All targets must
resolve.

Choose the sharpest defensible edge:

- `DERIVES_FROM`: a genuine derivation dependency;
- `CONSTRUCTED_FROM`: algebraic, differential, or structural construction;
- `COMPONENT_OF`: a component or extracted part;
- `INSTANCE_OF`: an example or special case;
- `REQUIRES`: prerequisite understanding; and
- `RELATED`: a real connection with no sharper current type.

Use `RELATED` sparingly. Record concrete unresolved edge questions with the
relevant concept draft. Prefer dependencies on earlier concepts and
keep important derivation paths traceable toward foundations.

Taxonomy and teaching prerequisites can coexist: retain `INSTANCE_OF` alongside
`REQUIRES` when the authored explanation needs the general concept first. Do not
infer prerequisites automatically from taxonomy or repeat dependencies already
carried by a derivation chain.

## Domains, Modules, And Status

Current domain keys are:

- `sr`: Special Relativity and Classical Fields;
- `gr`: General Relativity; and
- `math`: reusable mathematics.

Use semantic namespace-qualified concept IDs. Put a concept in `math.*` only
when it genuinely belongs outside one physics domain. Display IDs remain
module-local: use `SR-X.Y`, `GR-X.Y`, or `MATHS-X.Y`, where X is the module
number and Y follows a loose fundamental-to-derived order within it. Every
concept has one primary same-domain module in `module_members.csv`; modules
replace the former layer grouping. Keep semantic IDs stable when renumbering.

Keep SR and GR metric and stress-energy concepts separate, with `RELATED`
links between the corresponding concepts. Give each its own domain-specific
scope rather than duplicating the exposition.

Link domains through genuine prerequisites. Prefer conservative edge types and
record uncertain split/merge decisions rather than forcing them during a seed
pass.

For a multi-module pass, complete one module at a time. Audit planned concepts,
block and question counts, module membership, links, and edges; then
run a domain-filtered build. Re-read the guide when a long pass risks stylistic
drift and prefer one commit per coherent module. Use current module membership
for authoring batches; domain plans describe
subject scope and may group topics differently.

Example filtered build:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --out output/interactive_graph.html \
  --domains gr \
  --also-load-linked-concepts
```

## References

Use registered sources to support authoring and review without cluttering the
prose. Link at the most specific useful level: concept, content block, or study
question. A broad locator is acceptable during drafting if it is marked for
tightening. Never invent a page or section reference from memory. Prefer stable
section
names; add page numbers when they improve precision. Keep rendered locators
compact and record uncertainty in the link note.

## Study Questions

Write 3 to 6 progressively ordered questions per concept, with no more than
three calculations or symbol manipulations. Prefer a mix of:

- basic recognition or interpretation;
- a misconception or convention check;
- a short calculation where useful; and
- a connection or synthesis question.

Use only schema-supported types: `short_answer`, `multiple_choice`, and
`calculation`. Choose marking separately: `automatic` requires structured
options with one correct answer; `self_assessed` requires none. Prefer
automatic marking when plausible alternatives test the intended knowledge,
but keep explanation and synthesis questions self-assessed when recognition
would make them shallow.

Numerical and simple algebraic calculations are especially valuable. Ask the
learner to identify and apply the right formula, with distractors based on
realistic sign, factor, unit, inverse, or power errors. Vary the position of the
correct option, keep every alternative credible, and do not author an “I don't
know” option: the viewer supplies it.

Keep question and option IDs stable because browser-local progress uses them.
Write the `answer` as useful feedback, not merely a repetition of the correct
option. Model answers should be concise but sufficient for self-study. See the
[study-question design](../design/study.md) for the interaction contract.

## Graphics

Every concept needs a graphic, at least for its graph icon. Use graphics to show
geometry, direction, propagation, component structure, or conceptual contrast
that prose alone hides.

Keep these four pieces synchronized:

1. creator in `srkg/svg_graphics/concepts.py`;
2. display-ID registry entry in `srkg/svg_graphics/registry.py`;
3. semantic-ID design and captions in
   `data/concept_graphic_designs.csv`; and
4. expected ID and accessible title in
   `tests/test_concept_svg_graphics.py`.

Runtime SVG dispatch uses display IDs such as `GR-6.1`; captions attach to
semantic IDs such as `gr.riemann_tensor`. Consequently renumbering currently
requires registry changes; migration to semantic-ID dispatch is tracked in
[open issues](../issues.md).

Provide deterministic 512-by-512 `icon` and `detail` SVGs with non-empty
accessible titles. The icon needs a clear small-scale silhouette. The detail
variant must add a useful label, comparison, qualification, or teaching cue.

Reuse shared motifs. When substantially the same structure appears for a third
concept, move it to `svg_graphics/motifs.py`. Prefer drawing and math-text
helpers over hand-written XML. Escape XML-sensitive text: use `&lt;` for
`<` and never leave a raw `&`.

Graphics workflow:

1. review the existing design and neighbouring graphics;
2. decide the teaching mnemonic and what to avoid;
3. implement both variants and both captions;
4. run focused SVG validity, accessibility, registry, and variant tests;
5. generate a sheet with `tools/show_graphics.py`; and
6. inspect clipping, collisions, icon legibility, and conceptual distinctness.

Generated review sheets and HTML are build artifacts. Regenerate
`output/interactive_graph.html` when needed, let the reviewer open it
manually, and do not commit generated HTML unless explicitly requested.

Module graphics are optional and should primarily give a module a memorable
visual identity, not diagram every member concept. Use a strong landscape motif
with rounded framing; keep the icon sparse and enrich the same motif for the
detail page. Small modules need not have graphics.

## Completion Checklist

Before finishing a concept or module, confirm:

- scope, prose, notation, assumptions, and conventions are clear;
- blocks are well-sized, semantically typed, and correctly ordered;
- equations use single backslashes and render through MathJax;
- CSV fields have the expected column count;
- cross-references, edge endpoints, and references resolve;
- questions are progressive and varied;
- module membership is correct;
- icon/detail SVGs, accessible titles, designs, and captions are synchronized;
- the graphics review sheet has been visually checked;
- remaining issues are recorded in the appropriate worklist; and
- real-data tests, the full suite, and the relevant viewer build pass.

## Review Commands

Run commands from the repository root in the `sr-kg` environment. Validation
errors block a build; warnings need editorial judgement. `--validate` validates
before generation, and `--validation-strict` also fails on warnings.

```bash
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --validate-only
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --dag-report-only
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --module-report-only
```

DAG reports inspect directed relations, cycles, redundancy and dependency chains.
Module reports inspect boundaries, declared supports, quotient cycles and
module/member ordering. Use `--dag-relations` or `--module-relations` to select
relations. See [Modules](../design/modules.md) for the interpretation of these checks.

Partition search is an advisory operation and never rewrites authored membership:

```bash
conda run -n sr-kg python tools/analyse_module_partitions.py \
  --data-root data --domain sr --module-counts 4 5 6 --min-size 5 --max-size 15
```

Evaluate an authored membership file using `--evaluate-members PATH`,
`--evaluate-only`, and `--show-boundary-edges`. See the tool's `--help` for
search weights, reproducibility and report output options.

Generate a graphics review sheet with:

```bash
conda run -n sr-kg python tools/show_graphics.py 'SR-1.*'
```

Quote wildcard patterns. The default sheet is `/tmp/srkg-graphics-review.html`;
`--out` selects another location. It includes both graphic variants and captions.
