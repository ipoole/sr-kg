# Knowledge Base Schema

This document describes the current text-file schema loaded by `srkg.kb`.
The schema is intentionally file-based and Git-friendly. The Python loader may
construct richer internal objects, but the authored source of truth remains the
domain-owned files discovered from the KB collection root.

## Data Root

The default collection root is `data/`, containing shared metadata and a
manifest which discovers independently owned domain packages:

```text
data/
  manifest.yaml           # domains_root: ../domains
  edges_key.csv
  tutorials.yaml          # general interface routes

domains/<domain-id>/
  domain.yaml
  data/*.csv              # all table roles listed below, except shared edge key
  graphics/               # creators, registry and optional module assets
  layout.json
  tutorials.yaml          # subject routes
  docs/
  tests/
```

The collection manifest declares `domains_root`, shared `files.edge_key`,
optional shared `files.tutorials` and a migration `layout_revision`. Each
`domain.yaml` declares stable `id`, `title`, integer `sequence`, optional
`display_name` (default: uppercase ID), optional owned `initial_selection`
(`concept:<id>` or `module:<id>`), optional `module_palette` (an owned JSON
file of non-empty `[background, border]` hex-colour pairs), and optional `graphics` (a relative dotted Python module such as `graphics.registry`) and
`files` paths. Domain files must stay inside their package directory. Discovery
is ordered by `(sequence, id)` and has no fixed list of domain names. No shared
registration file changes when adding a package. See [domain packages](domain_packages.md).

Single-root `manifest.yaml` datasets remain supported for tests/library callers.
The table contracts below apply to both forms; collection tables are composed
in memory, never written back to a combined source CSV. The domain directory
name, manifest ID and first dotted component of owned semantic IDs must agree.
Explicit selection reads only those packages; see [selected-domain builds](missing_domain_builds.md).

For drafting, notation and source-review workflows, see the
[authoring guide](../authoring/authoring_guide.md).

## manifest.yaml

A domain manifest (or legacy single-root manifest) names its source files. File entries may be
omitted to use default filenames. For `files.*` rows below, “Required” means
the source file is required, not that its manifest entry must be written.

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | No | Human-readable KB name. |
| `files` | No | Mapping from logical source names to file paths. Defaults to the conventional filenames below. |
| `files.nodes` | Yes | Concept metadata file. |
| `files.edges` | Yes | Concept relationship file. |
| `files.edge_key` | No | Relation metadata file. |
| `files.content_blocks` | Yes | Ordered canonical concept-content file. |
| `files.study_questions` | Yes | Ordered canonical study-question file. |
| `files.study_question_options` | Yes | Ordered alternatives for automatically marked study questions. May be header-only. |
| `files.references` | Yes | Bibliographic/source reference registry. |
| `files.reference_links` | Yes | Links from KB items to source references. |
| `files.graphic_designs` | No | Concept graphic caption metadata. |
| `files.modules` | No | Authored flat module registry for module pages and graph folding. |
| `files.module_members` | No | Explicit primary concept membership for modules. Required when `modules.csv` is present. |
| `files.module_supports` | No | Optional cross-module or cross-domain support links declared by modules. |
| `files.module_content_blocks` | No | Ordered module-level content blocks. Required when `modules.csv` is present. |
| `files.layout` | No | Versioned published concept positions and module anchors. Missing objects use deterministic generated positions. |
| `files.tutorials` | No | Versioned semantic tutorial routes. Missing files mean that the viewer contains no tutorials. |

Domain paths are resolved relative to the owning package and cannot escape it.
Legacy single-root paths retain their existing relative/absolute resolution.
Optional files are ignored when absent. For manifest-backed KB roots,
`content_blocks.csv`, `study_questions.csv`, `references.csv`, and
`reference_links.csv` are required even though the manifest may omit the
filenames and use the defaults. The reference files may be header-only while
source references are being curated.

## Authoring Rules

Use stable semantic IDs for durable references. Concept IDs should look like
`sr.lorentz_transformations`, not `3.3`; the numeric ordering belongs in
`display_id`. Edges, content blocks, study questions, reference links, notes,
and `\cref` targets should all point at semantic IDs.

Keep `display_id` as the human navigation/order key. Renumbering a concept for
layout or teaching sequence should only change `display_id`, not `id`.

Put concept prose in `content_blocks.csv`; do not add new prose columns to
`nodes.csv`. Split new material into the smallest useful teaching blocks, using
`sequence` for the authored narrative order and `kind` for the semantic role of
each block.

Use only the current study-question types: `short_answer`, `multiple_choice`,
and `calculation`. Marking is independently `automatic` or `self_assessed`;
structured automatic-question alternatives live in
`study_question_options.csv`.

Add source material through `references.csv` and `reference_links.csv`. Prefer
linking a reference to the most specific useful item, such as a derivation block
or study question, rather than only linking the whole concept.

Modules are the authored pedagogical and layout groupings.
`module_members.csv` is the source of truth. A concept has exactly one
primary module, and that module must currently be in the same domain as the
concept. Cross-domain reuse, such as a GR module depending on maths concepts,
belongs in `module_supports.csv` rather than by giving concepts multiple module
owners.

## nodes.csv

`nodes.csv` contains concept metadata. `content_blocks.csv` is the canonical
source for concept prose in manifest-backed KB roots.

| Column | Required | Meaning |
| --- | --- | --- |
| `id` | Yes | Stable semantic concept identifier, such as `sr.lorentz_transformations`. This is the durable key used by edges, content blocks, links, hashes, and notes. |
| `display_id` | Yes | Module-local human-facing identifier, such as `SR-1.8`, `GR-3.2`, or `MATHS-2.1`. Used for visible numbering, sorting, and navigation. |
| `label` | Yes | Display label shown in the graph and details panel. |
| `domain` | Yes | Short domain key used for authoring subsets and broad atlas grouping, such as `sr`, `gr`, or `math`. |
| `domain_title` | Yes | Human-readable domain title, such as `Special Relativity and Classical Fields` or `General Relativity`. |

The prefix and first number identify the owning module. The final number follows
a loose fundamental-to-derived topological order within that module. Stable
semantic IDs, rather than display IDs, remain the targets of all references.

## content_blocks.csv

`content_blocks.csv` contains smaller authored teaching units attached to
concepts. It is the canonical concept-prose source for manifest-backed KB
roots. The viewer renders blocks directly and maps `kind` values to section
labels, folded notes, local contents entries, and graph-focus
lenses. Those presentation choices remain viewer policy; the KB authors the
semantic `kind`, not display instructions.

| Column | Required | Meaning |
| --- | --- | --- |
| `block_id` | Yes | Stable identifier for this content block. |
| `concept_id` | Yes | Concept this block belongs to. Must exist in `nodes.csv`. |
| `sequence` | Yes | Numeric ordering key within the concept. |
| `kind` | Yes | Semantic block kind. See the allowed values below. |
| `title` | Yes | Short editorial title for this block. The viewer may use it as a heading, folded-section handle, search label, or local contents entry. |
| `body` | Yes | Main text body, including MathJax and supported custom macros. |
| `statement` | No | Brief explicitly authored reusable result/contribution. Required when borrowed through `\explain`; empty for unconverted blocks. |
| `graphic` | No | `detail` for a `graphic` block wrapping its owner's registered detail SVG and caption; empty otherwise. |

The [authoring guide](../authoring/authoring_guide.md) requires explicit title,
statement and body for new/revised blocks. An optional storage column preserves
legacy compatibility; it does not make statements optional editorially. The
[generated reading-tree design](folded_reading_trees_design.md) supersedes authored
block borrowing for new work, while the current loader still accepts the earlier
pilot syntax described below.

Allowed `kind` values:

| Kind | Meaning |
| --- | --- |
| `overview` | A short orientation block stating what the concept will do. |
| `definition` | A precise statement of what the concept is. |
| `intuition` | A qualitative mental model or physical interpretation. |
| `explanation` | General explanatory prose that develops the concept. |
| `construction` | A setup or construction that builds an object or argument. |
| `result` | A central result, formula, theorem statement, or named conclusion. |
| `decomposition` | A breakdown of an object into components, frame splits, or parts. |
| `convention` | A notation, sign, unit, coordinate, or gauge convention used locally. |
| `derivation` | A coherent mathematical derivation or proof. |
| `derivation_step` | A smaller algebraic or logical step inside a derivation. |
| `example` | A short illustrative example. |
| `worked_example` | A worked problem or calculation with solution details. |
| `misconception` | A common mistake, ambiguity, or misleading intuition. |
| `warning` | A caveat, domain restriction, or notation trap. |
| `historical_note` | Historical context about discovery, attribution, or influence. |
| `summary` | A concise recap of the main result or takeaway. |
| `graphic` | An addressable explanation wrapping its owner's registered detail graphic. |

Example stable block IDs:

```text
<concept_id>.definition
<concept_id>.derivation
<concept_id>.explanation
```

For example, the Lorentz transformations definition block is identified as
`sr.lorentz_transformations.definition` and points to
`concept_id=sr.lorentz_transformations`.

The existing `\optional_details{Title}{Body}` text macro remains available
inside block bodies. It is a local text-disclosure device, not a `kind` value.
These disclosures and personal notes share rendering, while authored rows retain
stable block IDs and reading-completion semantics. Personal notes live only in the
[personal-data profile](personal_data.md), with optional paragraph (`anchor`) or
concept/module (`owner`) placement; they are not rows in these authored tables.
Nested optional disclosures do not yet have independent IDs or read ticks.

The [minimum nested-explanations schema](folded_reading_trees_schema.md) adds
`\explanation{slot}{title}{body}` for named local explanations and
`\explain{slot}{block_id}{target label}{hook}` for borrowing a canonical statement
and explanation. Both normalise with existing blocks into one recursive source
model. Slots distinguish occurrences, not new personal-data records. The loader
validates these additions; the [shared reader](folded_reading_trees_renderer.md)
implements them on a synthetic fixture before production-content conversion.
Existing tables/content need no conversion to load or render.

## modules.csv

`modules.csv` registers authored flat modules. Modules are the semantic unit of graph folding and have their own detail pages.

| Column | Required | Meaning |
| --- | --- | --- |
| `module_id` | Yes | Stable semantic module identifier, such as `gr.foundations_and_spacetime_geometry`. |
| `domain` | Yes | Owning domain key. Must match a domain used in `nodes.csv`. |
| `title` | Yes | Human-readable module title. |
| `sequence` | Yes | Numeric ordering key within the domain. |
| `default_collapsed` | No | Boolean-like initial viewer folding preference. The column must exist, but values may be blank. |

Modules are flat in the current schema. Do not add hierarchical parent fields
until the viewer can make hierarchy visible and selectable.

## module_graphic_designs.csv

This optional file records recognition-oriented module artwork keyed by stable
`module_id`. It uses the same design, avoidance and caption fields as
`concept_graphic_designs.csv`, with `module_id` replacing concept `id`. Only
modules with authored artwork need rows; small modules may remain text-only.
Registered modules receive landscape `icon` and `detail` SVG variants from the
module graphic registry. Captions are required for registered artwork.

## module_members.csv

`module_members.csv` assigns concepts to primary owning modules.

| Column | Required | Meaning |
| --- | --- | --- |
| `module_id` | Yes | Module that owns the concept. Must exist in `modules.csv`. |
| `concept_id` | Yes | Concept owned by the module. Must exist in `nodes.csv`. |
| `sequence` | Yes | Numeric ordering key within the module. |

When module files are present, every concept in `nodes.csv` must appear exactly
once in `module_members.csv`, and the concept's domain must match the module's
domain.

## module_supports.csv

`module_supports.csv` declares important support material for a module without
changing ownership. It is optional and may be header-only.

| Column | Required | Meaning |
| --- | --- | --- |
| `module_id` | Yes | Module declaring the support. Must exist in `modules.csv`. |
| `target_type` | Yes | Supported target type. Allowed values are `concept` and `module`. |
| `target_id` | Yes | Namespaced concept/module ID. Must exist within a loaded namespace; an unloaded target produces a warning and the support is omitted. |
| `role` | Yes | Short role label, such as `prerequisite`, `motivation`, or `application`. |
| `note` | No | Author-facing or viewer-facing explanatory note. The column must exist, but values may be blank. |

## module_content_blocks.csv

`module_content_blocks.csv` contains ordered teaching material attached to
modules. It deliberately mirrors `content_blocks.csv` but uses `module_id`
instead of `concept_id`.

| Column | Required | Meaning |
| --- | --- | --- |
| `block_id` | Yes | Stable identifier for this module content block. |
| `module_id` | Yes | Module this block belongs to. Must exist in `modules.csv`. |
| `sequence` | Yes | Numeric ordering key within the module. |
| `kind` | Yes | Semantic block kind. Uses the same allowed values as `content_blocks.csv`. |
| `title` | Yes | Short editorial title for this block. |
| `body` | Yes | Main text body, including MathJax and supported custom macros. |

Every module must currently have at least one module content block.
The same optional `statement` and `graphic` columns and nested-content rules
apply to module blocks as to concept blocks.

## tutorials.yaml

`tutorials.yaml` contains curated semantic routes through the live viewer. Its
top-level `schema_version` is currently `1`; `tutorials` is an ordered source
list whose visible order is determined by each route's numeric `sequence`.

Each tutorial has a stable `tutorial_id`, `title`, `category` (`interface` or
`physics`), short `summary`, numeric `sequence`, non-empty list of required
`domains`, and a non-empty list of `steps`. Domain-filtered builds omit routes
whose declared domains are unavailable.

Each step has a stable route-local `step_id`, `title`, `commentary`, optional
unanimated `prepare` commands, and either one `action` with an optional
`pointer`, or an `actions` list. Each list entry has an `action`, optional
`pointer` and `pause_ms` (default 500, range 0–2000). Sequences contain 1–20
entries. Mixing step-level `action`/`pointer` with `actions` is rejected.
One card stays visible while its actions run; Next is enabled on completion.
Commands refer to concepts, modules and
content blocks by stable semantic IDs. Generation rejects unknown IDs,
unsupported commands, invalid enum values and duplicate tutorial or step IDs.
Raw screen coordinates and CSS selectors are not part of the authored format.

The initial command vocabulary is:

- `select` and `clear-selection`;
- `set-display-scope`, `set-context` and `set-details-mode`;
- `set-module-representation`, `set-all-module-representations`, `expand-context-modules` and `fit`;
- `open-details-relationship`, `set-relationship-full-tree` and `show-relationship-in-graph`;
- `open-details-block`, `open-details-graphic`, `open-study-questions` and `show-tools-section`;
- `search` and `close-search`;
- a bounded settling `wait`.

A generated viewer may launch a route directly with
`?tutorial=<tutorial-id>`. Unknown IDs leave the viewer at its normal start.

The detailed playback and restoration model is specified in
[Native tutorial playback](tutorial_playback.md).

## study_questions.csv

`study_questions.csv` contains ordered question/answer material attached to
concepts. Questions are rendered in the concept details panel after the prose
sections. Question marking and answer disclosure are described in
[Viewer behaviour](viewer.md#reading-and-practice).

| Column | Required | Meaning |
| --- | --- | --- |
| `question_id` | Yes | Stable identifier for this question. Browser-local progress is keyed by it, so do not change it during routine editing. |
| `concept_id` | Yes | Concept this question belongs to. Must exist in `nodes.csv`. |
| `sequence` | Yes | Numeric ordering key within the concept. |
| `question_type` | Yes | Question format tag. Allowed values are `short_answer`, `multiple_choice`, and `calculation`. |
| `marking_mode` | Yes | Response assessment: `automatic` or `self_assessed`. Independent of `question_type`; a calculation may use either. |
| `prompt` | Yes | Question text, including MathJax and supported custom macros. |
| `answer` | No | Answer text. The column must exist, but values may be blank during drafting. |

An authored question remains `self_assessed` until its alternatives are
structured and its correct option is unambiguous. Do not mark a question
`automatic` merely because prompt text contains lettered choices. For an
automatic question, `answer` should explain the result after marking; for a
self-assessed question, it is the model answer used for comparison.

## study_question_options.csv

`study_question_options.csv` contains the ordered alternatives used to mark
automatic questions. The viewer adds its own `?` response, so it must not be
authored here.

| Column | Required | Meaning |
| --- | --- | --- |
| `question_id` | Yes | Existing question in `study_questions.csv`. |
| `option_id` | Yes | Stable, globally unique option identifier, conventionally derived from the question ID. |
| `sequence` | Yes | Numeric ordering key within the question. |
| `text` | Yes | Option text, including MathJax and supported custom macros. |
| `is_correct` | Yes | `true` for the one correct option; otherwise `false`. |

An automatic question must have at least two options and exactly one correct
option. A self-assessed question must have none. Keep `option_id` stable, use
credible distractors, and vary the correct option's sequence. The viewer adds
the non-answer `?` choice and records it as an `unknown` outcome.

## references.csv

`references.csv` is the source registry. Each row describes one book, paper,
website, lecture, or other source that may be linked from concepts, content
blocks, or study questions.

| Column | Required | Meaning |
| --- | --- | --- |
| `reference_id` | Yes | Stable domain-local reference identifier, such as `ttm.sr_cf`. The same key may be used independently by another domain. |
| `reference_type` | Yes | Broad source type, such as `book`, `paper`, `website`, or `lecture`. |
| `citation` | Yes | Short human-readable source label rendered in the viewer, such as `TTM II` or `TRR`. Put full bibliographic detail in the structured fields and/or `note`. |
| `authors` | No | Author/editor names. The column must exist, but values may be blank. |
| `title` | Yes | Source title. |
| `year` | No | Publication or relevant date. The column must exist, but values may be blank. |
| `url` | No | Optional URL. The column must exist, but values may be blank. |
| `note` | No | Private/editorial note about the source. The column must exist, but values may be blank. |

## reference_links.csv

`reference_links.csv` attaches registered sources to authored KB items.

| Column | Required | Meaning |
| --- | --- | --- |
| `source_type` | Yes | Linked item type. Allowed values are `concept`, `content_block`, and `study_question`. |
| `source_id` | Yes | ID of the linked item. Must exist in the corresponding source file. |
| `reference_id` | Yes | Source reference. Must exist in the owning domain’s `references.csv`. |
| `locator` | No | Page, section, theorem, lecture timestamp, or other local locator, such as `1.3 General Lorentz Transformation`. Rendered after the short citation. |
| `note` | No | Link-specific note rendered with the reference. |

## edges.csv

`edges.csv` contains concept-to-concept relations and belongs to the recorded
source concept's domain, including for undirected relations. Cross-domain targets
in unloaded namespaces generate warnings. Their edges/support links are omitted;
prose references retain their labels without hyperlinks. Unknown targets within
loaded namespaces remain errors. Targets are never imported implicitly. Semantic concept/module/block/question/
option IDs remain global.
Duplicate undirected edges are checked irrespective of endpoint orientation.

| Column | Required | Meaning |
| --- | --- | --- |
| `source` | Yes | Source concept ID. Must exist in `nodes.csv`. |
| `target` | Yes | Namespaced concept ID. Must exist when its namespace is loaded; otherwise the edge is omitted with a warning. |
| `relation` | Yes | Relation type. Blank values are normalised to `REFERENCE`. |
| `note` | No | Edge note shown in the hover tooltip. |

For directed relation types, the stored direction is `source -> target`.
For example, `A REQUIRES B` means concept A requires concept B.

Current relation types are:

| Relation | Direction | Meaning |
| --- | --- | --- |
| `REQUIRES` | Directed | A requires knowledge of B. |
| `DERIVES_FROM` | Directed | A can be mathematically derived from B. |
| `CONSTRUCTED_FROM` | Directed | A is algebraically, differentially, or structurally built from B, without necessarily being derived as a theorem. |
| `COMPONENT_OF` | Directed | A is a component, frame split, or extracted part of B. |
| `INSTANCE_OF` | Directed | A is a concrete example, special case, or named instance of B. |
| `RELATED` | Undirected | A and B are closely associated, without a sharper relation. |

## edges_key.csv

`edges_key.csv` describes relation types.

| Column | Required | Meaning |
| --- | --- | --- |
| `relation` | Yes | Relation name used in `edges.csv`. |
| `directed` | Yes | Boolean-like value controlling arrows and DAG diagnostics. |
| `category` | No | Broad relation category. |
| `meaning` | No | Human-readable explanation shown in the edge key. |
| `example` | No | Example edge shown in the edge key. |

Boolean values such as `true`, `false`, `yes`, `no`, `1`, and `0` are accepted.

## concept_graphic_designs.csv

This file currently stores caption metadata for generated concept graphics.
The graphics themselves are still generated by Python code.

| Column | Required | Meaning |
| --- | --- | --- |
| `id` | Yes | Semantic concept ID the captions currently attach to. |
| `display_id` | No | Human-facing concept number retained for review and migration readability. |
| `icon_caption` | No | Caption for the compact graph-node/icon version. |
| `detail_caption` | No | Caption for the details-panel graphic. |

## layout.json

Each domain's `layout.json` contains its owned portion of the published global
graph layout. Coordinates remain global. The loader combines them into one
viewer snapshot. The initial split retains revision `7`; subsequent changes to a
domain revision produce a deterministic combined revision, without a shared
layout file to edit. It stores
stable graph-space coordinates, not screen pixels, camera position, zoom,
visibility, selection, browser-local overrides, or temporary layout adjustments.

```json
{
  "schema_version": 1,
  "revision": "1",
  "concepts": {
    "sr.inertial_frames": {"x": 0, "y": 1200}
  },
  "modules": {
    "sr.spacetime_foundations": {"anchor": {"x": 350, "y": 1000}}
  }
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `schema_version` | Yes | Integer layout schema version. The current version is `1`. |
| `revision` | Yes | Non-empty published-layout revision string used to distinguish repository defaults. |
| `concepts` | Yes | Mapping from stable concept IDs to finite numeric `x` and `y` graph coordinates. May be empty or partial. |
| `modules` | Yes | Mapping from stable module IDs to an `anchor` with finite numeric `x` and `y` graph coordinates. May be empty or partial. |

Unknown concept or module IDs, duplicate JSON keys, malformed coordinates, and
unsupported schema versions are load errors. Concepts omitted from the file
fall back to deterministic module-local layout. An omitted module anchor is
generated from the structural module DAG. The generator
passes the resolved layout to the viewer as its initial global layout. See
[Layout](layout.md) for editing and persistence behaviour.

## Text Markup

Text fields may contain:

| Markup | Meaning |
| --- | --- |
| `\( ... \)` | Inline MathJax. |
| `\[ ... \]` | Display MathJax. |
| `\cref{label}{concept_id}` | Concept link when loaded; plain authored label otherwise. |
| `\optional_details{title}{body}` | Fold-down optional detail inside a section. |
| `\explanation{slot}{title}{body}` | Named, recursive local explanation in a block body. |
| `\explain{slot}{block_id}{target label}{hook}` | Borrow a source's short statement and foldable explanation; a missing external domain retains the label/hook. |

Validation checks balanced braces, MathJax delimiters, supported custom macro
syntax, and whether `\cref` targets exist within their loaded namespaces.
Unloaded-namespace references are generator diagnostics rather than text errors.

## Loader Guarantees

The loader rejects missing required files or columns, duplicate identifiers,
invalid required values and ordering keys, unknown kinds or question types,
and unresolved references within loaded namespaces. External namespaces produce
build warnings and safe omissions. Concepts need content; modules need content and
exactly one same-domain membership for each concept. Optional files may be
absent, but supplied files must satisfy their contracts above.

Text validation additionally checks markup and graph consistency. Review
warnings, such as redundant edges or ordering contradictions, require editorial
judgement rather than automatic deletion. See the [authoring guide](../authoring/authoring_guide.md).

## Future plans

Hierarchical modules remain a possible extension, not a current source contract. Add either only when authoring and presentation
needs justify the migration.
