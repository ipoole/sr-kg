# Knowledge Base Schema

This document describes the current text-file schema loaded by `srkg.kb`.
The schema is intentionally file-based and Git-friendly. The Python loader may
construct richer internal objects, but the authored source of truth remains the
files under the KB data root.

## Data Root

A KB data root is a directory containing `manifest.yaml`.

```text
data/
  manifest.yaml
  nodes.csv
  edges.csv
  edges_key.csv
  content_blocks.csv
  study_questions.csv
  study_question_options.csv
  references.csv
  reference_links.csv
  concept_graphic_designs.csv
  module_graphic_designs.csv
  modules.csv
  module_members.csv
  module_supports.csv
  module_content_blocks.csv
  layout.json
```

The default project root is `data/`.

For drafting, notation and source-review workflows, see the
[authoring guide](../authoring/authoring_guide.md).

## manifest.yaml

The manifest names the source files within the data root. File entries may be
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

Paths are resolved relative to the data root unless absolute paths are used.
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
labels, folded notes, reading modes, local contents entries, and graph-focus
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
| `target_id` | Yes | Target concept or module ID. Must exist in the corresponding source file. |
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

## study_questions.csv

`study_questions.csv` contains ordered question/answer material attached to
concepts. Questions are rendered in the concept details panel after the prose
sections. Reading-mode filtering and answer disclosure are described in
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
| `reference_id` | Yes | Stable reference identifier, such as `ttm.sr_cf`. |
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
| `reference_id` | Yes | Source reference. Must exist in `references.csv`. |
| `locator` | No | Page, section, theorem, lecture timestamp, or other local locator, such as `1.3 General Lorentz Transformation`. Rendered after the short citation. |
| `note` | No | Link-specific note rendered with the reference. |

## edges.csv

`edges.csv` contains concept-to-concept relations.

| Column | Required | Meaning |
| --- | --- | --- |
| `source` | Yes | Source concept ID. Must exist in `nodes.csv`. |
| `target` | Yes | Target concept ID. Must exist in `nodes.csv`. |
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

`layout.json` contains the repository-published global graph layout. It stores
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
| `\cref{label}{concept_id}` | Clickable concept reference. |
| `\optional_details{title}{body}` | Fold-down optional detail inside a section. |

Validation checks balanced braces, MathJax delimiters, supported custom macro
syntax, and whether `\cref` targets exist.

## Loader Guarantees

The loader rejects missing required files or columns, duplicate identifiers,
invalid required values and ordering keys, unknown kinds or question types,
and unresolved references. Concepts need content; modules need content and
exactly one same-domain membership for each concept. Optional files may be
absent, but supplied files must satisfy their contracts above.

Text validation additionally checks markup and graph consistency. Review
warnings, such as redundant edges or ordering contradictions, require editorial
judgement rather than automatic deletion. See the [authoring guide](../authoring/authoring_guide.md).

## Future plans

A shared graphics registry and hierarchical modules remain possible extensions,
not current source contracts. Add either only when authoring and presentation
needs justify the migration.
