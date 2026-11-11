# Knowledge Base Authoring Guide

Use this guide to produce consistent, efficient concept content. Read it before
starting a new authoring pass and revisit the relevant sections between modules.

New/revised blocks follow the [reading-tree design](../design/folded_reading_trees_design.md):
self-contained title, statement and body, connected by graph edges. The shared
viewer supports this model; domain content migration is staged. Legacy missing
statements and block-borrowing calls remain loadable meanwhile; they are not
patterns for new authoring.

## Editorial Aim

Write compact, reusable knowledge elements. Each concept should:

- define the idea and explain why it is needed;
- introduce equations in prose and state assumptions and conventions;
- explain physical or geometric meaning and common misconceptions;
- respect the scope of neighbouring concepts; and
- connect to prerequisites, descendants, and sources.

Aim for direct sentences and smooth transitions between mathematics and
interpretation. Avoid marketing language, unexplained symbol changes,
unnecessary digressions, and words such as "obviously" when a learner may need
the missing step.

## Domain ownership

Work inside `domains/<domain-id>/`: tables in `data/`, graphics and local registry
in `graphics/`, layouts/tutorials alongside them, drafts/source work in `docs/`,
and domain-specific expectations in `tests/`. Do not edit another domain or a
shared ID list to add a concept or graphic. Shared conventions and drawing
primitives remain common. See [domain packages](../design/domain_packages.md).

Edges belong to the source concept's domain, including cross-domain edges.
Citations resolve against that domain's bibliography. The directory, manifest ID
and semantic-ID prefix must agree. A selected-domain build reads only its chosen
packages. External namespaces produce generator warnings: their edges/supports
are omitted and prose labels remain readable without links. A missing target
inside a loaded namespace is an error; external typos are only detected when
that namespace is included. Review the warning summary or use the full build
when checking cross-domain dependencies.
Semantic IDs and existing `math.` prefixes remain stable.

## Before Drafting

1. Read the concept's node, edges, blocks, questions, references, and graphic
   notes, plus nearby prerequisite and descendant concepts.
2. Check the [schema](../design/kb_schema.md), `notation_glossary.md`, and the relevant domain
   plan or exposition file.
3. Define the scope boundary and required supports. Record those supports as
   graph edges; use `\cref{label}{id}` for useful terminology or excursions,
   not to hide a premise from the dependency graph.
4. Check `equality_annotation_style.md` for derivations with meaningful
   equality steps.
5. Identify useful registered sources. Record uncertain locators in
   the owning domain’s `docs/source_review_worklist.md` rather than inventing precision.

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

Inside `aligned`, use `\\` followed by whitespace or a newline to separate rows.

CSV quoting is separate. Quote a complete field containing a comma, newline, or
double quote, and double embedded CSV quotes. Do not add backslashes to repair
CSV structure.

Author display maths for phone widths: split lists of equations and long
calculation chains into meaningful lines with `aligned`. MathJax 3 does not
automatically wrap them. The viewer marks remaining horizontal overflow with
↔, but scrolling should be a fallback rather than a required derivation step.

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

### Title, statement, body

Every new or revised block needs a stable ID, owner, numeric sequence, semantic
kind and **three authored content levels**. The CSV `statement` column remains
optional for legacy compatibility; it is an editorial requirement for new work.

| Level | Job |
| --- | --- |
| Title | Briefly identify what this block contains. Use a meaningful heading, not just “Explanation” or its kind. |
| Statement | Express the useful result, definition or interpretation in as few words as reasonably possible. It stays visible when the body is folded. |
| Body | Supply the reasoning, detail, interpretation, evidence or illustration that makes opening worthwhile. |

Write a short declarative statement, not a teaser, question or outline. Include
essential assumptions. A compact formula can serve if its symbols and conditions
are clear; keep calculation chains in the body. Author the statement explicitly:
do not extract the first sentence or substitute a whole-concept summary.

For an `example` block:

- **Title:** A grid rescaled by two.
- **Statement:** Components change while the scalar pairing remains unchanged.
- **Body:** Introduce numerical coordinate labels \(x'=2x\). Show
  \(V^x=3\to V^{x'}=6\) and \(\omega_x=8\to\omega_{x'}=4\), then explain why
  \(\omega_xV^x=8(3)=4(6)=24\).

Bodies must work independently within their scope: introduce notation and
conditions; avoid “the block above”. Do not re-teach the whole prerequisite field.
A short Definition may suffice; a Derivation or Explanation that only paraphrases
its statement needs revision, not padding. Keep the canonical title/statement/body
unchanged across local and reading-tree occurrences.

### Choose blocks by purpose

Every concept has a Definition and usually a Derivation and an Explanation:

- `definition`: precise meaning. Put the canonical definition of the whole concept
  first if several Definition blocks exist; it supplies concept-reference previews.
- `derivation`: a succinct argument/construction and its assumptions, for a reader
  familiar with the field. Identify definitions, postulates or starting structure
  honestly; do not invent proofs for primitive concepts.
- `explanation`: meaning, motivation and intermediate reasoning for a less
  experienced learner. It can differ substantially from the Derivation even when
  both depend on the same concepts.

Add `intuition`, `example`, `graphic`, or other supported kinds when they contribute
something useful. Repeated kinds are allowed. Use kinds semantically, not to request
visual styling. Existing kinds remain valid; vocabulary pruning is a separate task.
Order blocks as useful local teaching units, not one oversized explanation.

Use `historical_note` selectively. Explain the problem, contribution and change of
understanding rather than writing a detached biography. Treat disputed priority
and parallel contributions neutrally; source specific attributions.

### Local clarifications and generated trees

**Blocks never call other owned blocks**, even locally. Reading trees are
generated from concept edges and selected block kinds, not authored routes.
Do not add `\explain` calls. Audit legacy calls with the graph during migration,
preserving IDs and useful reasoning.

Local clarifications may nest. Prefer `\explanation{slot}{title}{body}` with stable
named slots; legacy `\optional_details{Title}{Body}` remains valid. Keep the main
exposition readable without opening optional algebra or “Why exactly?” details.
Clarifications have title/body only: explanatory lead-ins are ordinary prose.
They do not call owned blocks or add concept hops.

Clarifications have no independent block ID, read tick or tutorial target. Named
slots anchor notes through the enclosing block; renaming/moving one may leave
notes needing placement. Owned-block ticks and notes share canonical identity
across occurrences. Personal notes do not affect completion. The
[current storage contract](../design/folded_reading_trees_schema.md) documents
syntax; its borrowing workflow is superseded by this guide.

## Cross-References And Edges

Add a `\cref` only when following it helps the learner. All targets must
resolve in the full KB; selected-domain builds retain readable unavailable labels.

Choose the sharpest defensible edge:

- `DERIVES_FROM`: a genuine derivation dependency;
- `CONSTRUCTED_FROM`: algebraic, differential, or structural construction;
- `COMPONENT_OF`: a component or extracted part;
- `INSTANCE_OF`: an example or special case;
- `REQUIRES`: prerequisite understanding; and
- `RELATED`: a real connection with no sharper current type.

`DERIVES_FROM` and `CONSTRUCTED_FROM` imply prerequisite understanding: do not
also store a redundant `REQUIRES` edge for the same dependency. Taxonomic and
`RELATED` edges do not imply prerequisites.

Write each edge justification as a concise, self-contained sentence explaining
why the source uses the destination. For example: “The component rule uses the
Jacobian of the coordinate transition.” The viewer supplies the source/relation
introduction; avoid fragments or a repeated “because”. This note appears at every
incoming reading-tree occurrence, so do not assume a particular enclosing route.

Derivation trees traverse `DERIVES_FROM` + `CONSTRUCTED_FROM`; Teaching also uses
`REQUIRES`. Review content and these edges together. Do not add shortcut edges
just because a deeper block would be convenient, or manufacture dependencies for
ordinary cross-references. Alternative arguments need explicit justification;
do not imply that all alternatives are jointly necessary.

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
  --out output/PhysicsKG.html \
  --domains gr
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

1. creator in the domain's `graphics/concepts.py`;
2. semantic-ID entry in its `graphics/registry.py`;
3. design/captions in its `data/concept_graphic_designs.csv`; and
4. any specific expectations in its `tests/graphics_expectations.json` or tests.

Generic tests discover registered IDs automatically. Module motifs/assets and
accessible titles also belong to the owning `graphics/` directory. Shared
`srkg/svg_graphics/` contains reusable primitives, motifs and framing only.

Review with `tools/show_graphics.py --domain <id>`. Numbering proposals may be
computed over the collection; applying them requires `--domain <id>`. Install an
exported layout with `tools/install_layout.py --domain <id> --layout <file> --revision <new-revision>`; it updates only that domain's coordinates. Run these
Python tools through the project conda environment.

Runtime SVG dispatch and captions use semantic IDs such as
`gr.riemann_tensor`. Use display IDs only to select and label review sheets;
renumbering must not change a concept's graphic identity.

For physics tutorials, keep one teaching point per card and put the exposition
in Details. Group visible actions to establish a useful graph view, then leave
each reading target available until Next. Audit the argument's physical
assumptions as well as its algebra; see [tutorial playback](../design/tutorial_playback.md).

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
`output/PhysicsKG.html` when needed, let the reviewer open it
manually, and do not commit generated HTML unless explicitly requested.

Module graphics are optional and should primarily give a module a memorable
visual identity, not diagram every member concept. Use a strong landscape motif
with rounded framing; keep the icon sparse and enrich the same motif for the
detail page. Small modules need not have graphics.

## Completion Checklist

Before finishing a concept or module, confirm:

- scope, prose, notation, assumptions, and conventions are clear;
- titles identify content, statements stand usefully when folded, and bodies add
  substance; kinds and sequence match their purposes;
- bodies have no owned-block calls; local clarifications and note slots are stable;
- equations use single backslashes and render through MathJax;
- CSV fields have the expected column count;
- cross-references, edge endpoints and references resolve; dependency justifications
  explain the actual teaching/derivation support;
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
