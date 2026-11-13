# Authoring technical reference

Use alongside the [editorial guide](authoring_guide.md). Storage contracts belong
in the [schema](../design/kb_schema.md); project test/build instructions belong in
[AGENTS.md](../../AGENTS.md). Run Python tools in the `sr-kg` conda environment.

## Domain ownership and identifiers

Tables, bibliography and source-owned edges live in `domains/<id>/data/`;
graphics and their registry in `graphics/`; layouts/tutorials alongside them;
drafts, review notes and source worklists in `docs/`; domain-specific tests in
`tests/`. Shared drawing primitives belong in `srkg/svg_graphics/`. Do not edit
another domain or a shared ID list to add domain content.

Directory, manifest ID and semantic-ID namespace must agree. Current domains
are `sr`, `gr` and `math`; keep existing `math.` identifiers. Edges belong to the
source concept's domain, including cross-domain edges; citations use that domain's
bibliography. Selected-domain builds read only selected packages. Missing external
namespaces generate warnings and their edges/supports are omitted; unavailable
prose labels remain readable. Missing targets within a loaded namespace are
errors. Check a full build too, since it can detect misspellings hidden in an
excluded namespace. See [domain packages](../design/domain_packages.md).

Each concept has one primary same-domain module. Display IDs are module-local:
`SR-X.Y`, `GR-X.Y`, `MATHS-X.Y`, with Y loosely ordered from fundamental to derived.
Renumbering must not change semantic IDs. Put reusable mathematics in `math.*`;
keep SR and GR metrics/stress-energy concepts separate, with appropriate Related
links and distinct scope. Link domains by genuine dependencies; record uncertain
split/merge decisions rather than forcing them during seed authoring.

## Mathematical notation and storage

State metric signature, units, coordinate order, index convention, frame and
gauge where consequential. Use neutral `V` and `W` for generic four-vectors;
reserve `A` for the electromagnetic potential unless explicitly introduced
otherwise. Record recurring decisions in the [notation glossary](notation_glossary.md).
Use natural units, \(c\overset{\text{units}}{=}1\), once context is clear; retain
explicit `c` for introductory, dimensional and familiar interpretive formulae.

Use `\coloneqq` for definitions, `\equiv` for identities, `\simeq` for
approximations and `=` for exact algebra. Short annotated equalities can identify
a law, convention or constraint; explain them in prose and never put a `\cref`
inside `\overset`. See [equality style](equality_annotation_style.md).

CSV fields containing commas, newlines or double quotes need enclosing quotes;
double embedded quotes. CSV is not a Python/JSON string literal. Do not double
TeX backslashes or repair CSV quoting with backslashes. Check column counts and
render maths in blocks, questions, answers and module prose. MathJax 3 does not
automatically wrap long equations; use meaningful `aligned` rows. Horizontal
scrolling is a fallback, even though the viewer marks overflow with ↔.

The `statement` column remains optional in storage for legacy compatibility;
it is editorially required for new/revised blocks. Older `\optional_details{Title}{Body}`
clarifications remain supported. New work uses named `\explanation` slots.
Clarifications have no independent block ID, read tick or tutorial target; notes
use their path through the owning block. Owned-block notes/ticks share canonical
identity across occurrences; personal notes do not affect completion. Legacy
block-borrowing syntax remains loadable, but is superseded for new work by
[generated reading trees](../design/folded_reading_trees_design.md).

## Kind migration

Agreed target: Definition, Derivation, Explanation, Intuition, Example, Graphic,
Convention, Warning, Historical note, Advanced. The loader and viewer support
these ten kinds; the eight other kinds remain valid for unconverted content.
Migrate one module at a time, with stable IDs and an editorial purpose review.
Advanced is available as local content but is not selected by the current recipes.

| Existing kind | Review treatment |
| --- | --- |
| Construction, Decomposition | Derivation when establishing/constructing something; Explanation when interpreting or unpacking it. |
| Derivation step | Integrate into a coherent Derivation, or retain a meaningful bite-sized part as another Derivation. Use a local clarification for optional detail. |
| Worked example | Example. |
| Misconception | Warning. |
| Overview, Summary | Merge/remove repetition; Explanation if independently useful. |
| Result | Definition only when actually defining; otherwise review its explanatory or derivational purpose. Never invent or imply a proof. |

Preserve stable block IDs for retained blocks. Merging/deleting identified blocks
needs an explicit annotation/tutorial migration decision, not just a kind rename.
Module overview rows and their storage also need deliberate treatment during the
migration. Changing the vocabulary does not implicitly broaden reading recipes.

## References

### Internal concept and block links

`\cref{label}{sr.velocity_four_vector}` previews the concept's first Definition.
`\cref{the proper-time construction}{sr.velocity_four_vector.components}`
previews that exact block. The second argument is its registered `block_id`,
not `concept:block`, a display number or a title. Module content blocks can also
be targeted. Local clarifications have no independent block ID and cannot be
targets.

Block previews show title, kind, statement and an optionally unfolded read-only
body. They do not change selection, reading position or camera, and do not offer
notes or reading ticks. “Go to block” is explicit navigation to the owner and
the source block. These are ordinary references, not recursive borrowing calls:
they neither add graph edges nor change generated reading-tree branches.

Retain target IDs when revising prose. An unknown ID in a loaded domain is an
error; an excluded domain leaves the label readable with a generator warning.
Graph consistency diagnostics compare the concepts owning the blocks, so an
ordinary reference to a transitive support may warrant a documented warning
rather than a shortcut prerequisite edge. Check both selective and full builds.

### Bibliography

Use registered sources at the most specific useful concept, block or question
level. Verify locators; never invent page/section precision. A broad locator is
acceptable when marked for tightening. Keep rendered locators compact and record
uncertainty in the domain's `docs/source_review_worklist.md`. Check historical
attributions and treat parallel/disputed contributions neutrally.

## Study questions

Supported types: `short_answer`, `multiple_choice`, `calculation`. Marking is
separate: `automatic` requires structured options with one correct answer;
`self_assessed` requires none. For calculations, ask the learner to identify and
apply a formula, using credible sign, factor, unit, inverse or power errors as
distractors. Vary the correct option's position. The viewer supplies “I don't
know”; do not author that option. Keep feedback sufficient for self-study.
See [study design](../design/study.md).

## Graphics

Keep the domain's creator, semantic-ID registry entry, design/captions CSV and
specific test expectations in sync. Runtime dispatch uses semantic IDs;
display IDs are for selecting/labelling review sheets. Generic tests discover
registered graphics automatically.

Concept assets are deterministic 512×512 `icon` and `detail` SVGs with accessible
titles. Icons need clear small silhouettes; detail variants add useful labels,
comparisons or qualifications. Module assets use landscape motifs: sparse icons
and richer details, with a mnemonic rather than exhaustive teaching purpose.

Review neighbouring designs, choose the teaching cue, author both variants and
captions, test SVG validity/accessibility/registration, then inspect a rendered
contact sheet for clipping, collisions, legibility and distinctness. Prefer
shared drawing/math-text helpers to handwritten XML; escape `<` as `&lt;` and
never leave a raw `&`. When reusing a substantial motif for a third concept,
move it into shared `svg_graphics/motifs.py`.

For guided tutorials, put teaching exposition in Details, one point per card.
Group actions to establish a useful view and leave reading targets available
until Next. Check physics assumptions as well as algebra. See
[tutorial playback](../design/tutorial_playback.md).

## Commands

Use the project environment, e.g. `conda run -n sr-kg python tools/generate_pyvis.py`.
From the repository root:

```bash
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --validate-only
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --dag-report-only
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --module-report-only
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --domains sr math --out output/PhysicsKG.html
conda run -n sr-kg python tools/show_graphics.py 'SR-1.*'
```

Validation errors block generation; review warnings editorially. `--validate`
checks before building; `--validation-strict` treats warnings as failures.
DAG diagnostics cover cycles, redundancy and chains. Module reports cover
boundaries, supports, quotient cycles and member ordering; `--dag-relations` and
`--module-relations` select the edge set. See [modules](../design/modules.md).

Quote graphics wildcard patterns. `show_graphics.py --domain <id>` selects a
domain; `--out` sets its review sheet (default `/tmp/srkg-graphics-review.html`).
Numbering tools can propose across the collection but require `--domain` when
applying changes. Install exported layouts with `tools/install_layout.py
--domain <id> --layout <file> --revision <revision>`.

Partition analysis is advisory and never rewrites membership:

```bash
conda run -n sr-kg python tools/analyse_module_partitions.py --data-root data --domain sr --module-counts 4 5 6 --min-size 5 --max-size 15
```

`--evaluate-members`, `--evaluate-only`, `--show-boundary-edges` assess an authored
partition. See tool help for search weights and reproducibility. Generated viewers
and contact sheets are build artifacts. Keep them outside Git and let the user
open HTML manually. Publishing is a separate, explicitly requested operation;
see [artifact deployment](../design/artefact_deployment.md).
