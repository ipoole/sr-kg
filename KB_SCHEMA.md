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
  references.csv
  reference_links.csv
  concept_graphic_designs.csv
```

The default project root is `data/`.

## manifest.yaml

The manifest names the source files within the data root.

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | No | Human-readable KB name. |
| `files` | No | Mapping from logical source names to file paths. Defaults to the conventional filenames below. |
| `files.nodes` | Yes | Concept metadata file. |
| `files.edges` | Yes | Concept relationship file. |
| `files.edge_key` | No | Relation metadata file. |
| `files.content_blocks` | Yes | Ordered canonical concept-content file. |
| `files.study_questions` | Yes | Ordered canonical study-question file. |
| `files.references` | Yes | Bibliographic/source reference registry. |
| `files.reference_links` | Yes | Links from KB items to source references. |
| `files.graphic_designs` | No | Concept graphic caption metadata. |

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
`sequence` for narrative order and `pedagogical_level` for graded exposure.

Use only the current study-question types: `short_answer`, `multiple_choice`,
and `calculation`. Multiple-choice options currently live in the `prompt` text.

Add source material through `references.csv` and `reference_links.csv`. Prefer
linking a reference to the most specific useful item, such as a derivation block
or study question, rather than only linking the whole concept.

## nodes.csv

`nodes.csv` contains concept metadata. `content_blocks.csv` is the canonical
source for concept prose in manifest-backed KB roots.

| Column | Required | Meaning |
| --- | --- | --- |
| `id` | Yes | Stable semantic concept identifier, such as `sr.lorentz_transformations`. This is the durable key used by edges, content blocks, links, hashes, and notes. |
| `display_id` | Yes | Human-facing ordered identifier, such as `3.3`. Used for visible numbering, sorting, layout, and navigation. |
| `label` | Yes | Display label shown in the graph and details panel. |
| `layer` | Yes | Pedagogical/layout layer. Used for navigation and initial graph layout. |
| `layer_title` | Yes | Human-readable title for the layer. |

## content_blocks.csv

`content_blocks.csv` contains smaller authored teaching units attached to
concepts. It is the canonical concept-prose source for manifest-backed KB
roots. The loader groups current block kinds back into the visible Definition,
Derivation, and Explanation sections for the existing viewer.

| Column | Required | Meaning |
| --- | --- | --- |
| `block_id` | Yes | Stable identifier for this content block. |
| `concept_id` | Yes | Concept this block belongs to. Must exist in `nodes.csv`. |
| `sequence` | Yes | Numeric ordering key within the concept. |
| `kind` | Yes | Block kind. Currently rendered kinds are `definition`, `derivation`, and `explanation`. |
| `pedagogical_level` | No | Pedagogical level tag. May be blank during migration. |
| `title` | No | Block title or section title. The column must exist, but values may be blank. |
| `body` | Yes | Main text body, including MathJax and supported custom macros. |

Initial migrated block IDs use:

```text
<concept_id>.definition
<concept_id>.derivation
<concept_id>.explanation
```

For example, the Lorentz transformations definition block is identified as
`sr.lorentz_transformations.definition` and points to
`concept_id=sr.lorentz_transformations`.

Future block kinds may include `intuition`, `construction`, `optional_detail`,
`misconception`, `worked_example`, and `historical_note`.

## study_questions.csv

`study_questions.csv` contains ordered question/answer material attached to
concepts. Questions are rendered in the concept details panel after the prose
sections.

| Column | Required | Meaning |
| --- | --- | --- |
| `question_id` | Yes | Stable identifier for this question. |
| `concept_id` | Yes | Concept this question belongs to. Must exist in `nodes.csv`. |
| `sequence` | Yes | Numeric ordering key within the concept. |
| `pedagogical_level` | No | Pedagogical level tag. May be blank during migration. |
| `question_type` | Yes | Question format tag. Allowed values are `short_answer`, `multiple_choice`, and `calculation`. |
| `prompt` | Yes | Question text, including MathJax and supported custom macros. |
| `answer` | No | Answer text. The column must exist, but values may be blank during drafting. |

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
For example, `A PREREQUISITE B` means concept A requires concept B.

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

This file is expected to evolve into a fuller graphics registry where graphics
are independent resources that can link to concepts, questions, derivations,
or volume-specific presentations.

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

The `KnowledgeBase` loader currently enforces:

| Check | Behaviour |
| --- | --- |
| Missing `manifest.yaml` | Load error. |
| Missing required `nodes` or `edges` file | Load error. |
| Missing `content_blocks.csv` in a manifest-backed KB root | Load error. |
| Missing `study_questions.csv` in a manifest-backed KB root | Load error. |
| Missing `references.csv` in a manifest-backed KB root | Load error. |
| Missing `reference_links.csv` in a manifest-backed KB root | Load error. |
| Duplicate concept IDs | Load error. |
| Missing, empty, or duplicate `display_id` values in manifest-backed `nodes.csv` | Load error. |
| Edge endpoints not found in `nodes.csv` | Load error. |
| Missing required `content_blocks.csv` columns | Load error. |
| Duplicate content block IDs | Load error. |
| Empty `block_id`, `concept_id`, `sequence`, `kind`, or `body` values | Load error. |
| Non-numeric content block `sequence` values | Load error. |
| Unknown content block `kind` values | Load error. |
| Content block `concept_id` not found in `nodes.csv` | Load error. |
| Concepts with no content blocks | Load error. |
| Missing required `study_questions.csv` columns | Load error. |
| Duplicate study question IDs | Load error. |
| Empty study question `question_id`, `concept_id`, `sequence`, or `prompt` values | Load error. |
| Non-numeric study question `sequence` values | Load error. |
| Unknown study question `question_type` values | Load error. |
| Study question `concept_id` not found in `nodes.csv` | Load error. |
| Missing required `references.csv` columns | Load error. |
| Duplicate reference IDs | Load error. |
| Empty reference `reference_id`, `reference_type`, `citation`, or `title` values | Load error. |
| Missing required `reference_links.csv` columns | Load error. |
| Empty reference link `source_type`, `source_id`, or `reference_id` values | Load error. |
| Unknown reference link `source_type` values | Load error. |
| Reference link `reference_id` not found in `references.csv` | Load error. |
| Reference link `source_id` not found in the named source file | Load error. |
| Missing optional files | Ignored. |

The loaded Python model exposes concepts, content blocks, grouped viewer
sections, neighbours, relation metadata, source references, and viewer JSON
data. The JavaScript viewer currently consumes the grouped `sections` shape
while also receiving raw `content_blocks`, structured `study_questions`, and
structured `references` for future KB-model work.
