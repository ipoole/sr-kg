# SR Knowledge Graph

A pedagogical knowledge graph viewer for special relativity, classical fields,
general relativity and supporting mathematics. GR content is at seed level and
still needs full authoring and review.

The project reads concept data from CSV files and generates a standalone
interactive HTML graph using PyVis and vis.js. The generated viewer supports:

### Navigation And View Layout

- searchable concept list
- clickable graph nodes, concept-list entries, and concept references
- browser back/forward navigation between selected concepts
- peer graph and details panes with independent show/hide controls
- hide/all/focussed graph modes

### Details And Study Content

- sticky concept masthead, reading-mode selector, and local contents navigation
- semantic content-block rendering with textbook-style callouts, symbols, and folded notes
- clickable `\cref{label}{id}` references in concept descriptions
- linked-concept previews in details sections
- browser-local user notes in concept details, with CSV export/import

### Graph Semantics

- authored modules with folding, module colours and module-local concept numbering
- persistent manual layouts with module-local fallback placement
- relation-aware edge colouring and an edge key
- directed and undirected edge rendering
- section-aware graph focus with a focus-lens status display
- derived-from and where-used sections that drive graph context
- relationship details and edge hover notes with MathJax-aware custom tooltips
- stable, repeatable colour choices across runs

### Maths And Graphics

- MathJax rendering for inline and display equations
- MathJax-rendered graph labels for node IDs and concept names
- generated concept SVG graphics in the detail panel and graph nodes where available

## Repository Layout

```text
data/
  manifest.yaml            Data-root file manifest
  nodes.csv                Concept metadata
  edges.csv                Concept relationships with relation types and notes
  edges_key.csv            Edge relation meanings and direction metadata
  content_blocks.csv       Ordered concept content blocks with semantic kinds
  modules.csv              Authored flat module registry
  module_members.csv       Primary concept membership for modules
  module_supports.csv      Cross-module/domain support declarations
  module_content_blocks.csv Ordered module-level content blocks
  layout.json              Versioned published concept positions and module anchors
docs/
  authoring/
    AUTHORING_GUIDE.md     House style for drafting concept content
    sr_concept_expositions.md SR draft expositions before CSV block splits
    gr_concept_expositions.md GR draft expositions before CSV block splits
    NOTATION_GLOSSARY.md   Shared notation conventions
  discussion/              Design discussion notes and experiments
lib/
  vis-9.1.2/               Vendored vis-network assets used by PyVis output
  tom-select/              Vendored PyVis UI assets
  bindings/                PyVis binding asset
output/
  interactive_graph.html   Generated standalone viewer
srkg/
  config.py                Shared constants
  data.py                  CSV validation and concept-data helpers
  concept_svg_graphics.py  Deterministic SVG concept graphic generation
  edges.py                 Edge relation semantics, colours, and display helpers
  layout.py                Natural ID sorting and module-free fixture layout
  module_layout.py         Dependency-based module and concept placement
  layout_persistence.py    Published layout validation and fallback resolution
  module_colours.py        Stable module visual identities
  render_pyvis.py          Base PyVis network rendering
  html_injection.py        Browser-side CSS/JS/MathJax injection
  pipeline.py              End-to-end generation workflow
  kb.py                    Manifest-backed knowledge-base loader and query API
  module_diagnostics.py    Module boundary and quotient-graph diagnostics
  module_partitioning.py   Candidate module search and comparison
tools/
  analyse_module_partitions.py  Module-partition authoring aid
  generate_pyvis.py        Command-line entry point
  show_graphics.py         SVG graphics review sheet generator
```

## Setup

Use Python 3.12 or newer. The development workflow assumes the project conda
environment named `sr-kg`.

```bash
conda run -n sr-kg python -m pip install -r requirements.txt
```

## Testing

Run the unit test suite:

```bash
conda run -n sr-kg pytest -q
```

Browser integration tests use Playwright. Install the Chromium browser binary
once inside the project environment:

```bash
conda run -n sr-kg python -m playwright install chromium
```

Then run the browser tests explicitly:

```bash
conda run -n sr-kg pytest -q tests/browser
```

Browser tests reuse generated fixture viewers and a shared Chromium process, but
still exercise real generated HTML through Playwright. They are intentionally
opt-in for whole-suite runs; selecting `tests/browser` explicitly enables them.

## Generate The Viewer

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --out output/interactive_graph.html \
  --title "Special Relativity and Classical Fields"
```

Then open `output/interactive_graph.html` in a browser.

MathJax is loaded from a CDN in the generated HTML, so equation rendering requires network access when viewing the file.

There is also a PyCharm run configuration named `Generate Knowledge Graph` that runs the same command against the files in `data/`. Generation is manifest-backed; use `--data-root` rather than passing individual CSV files.

During domain authoring, generate a smaller viewer with `--domains`. The
generator uses `nodes.csv` column `domain` when present, otherwise it uses the
semantic ID prefix before the first dot, such as `sr`, `gr`, or `math`:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --out output/interactive_graph.html \
  --domains gr
```

Add `--also-load-linked-concepts` to include one-hop concepts linked to the
selected domain concepts, which is useful when checking cross-domain SR/GR
references:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --out output/interactive_graph.html \
  --domains gr \
  --also-load-linked-concepts
```

## Validate Source Data

After manually editing the source files in `data/`, run the generator in validation-only mode:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --validate-only
```

Validation prints a diagnostic report and exits with a non-zero status when it finds errors. Use `--validate` to run the same checks before normal HTML generation:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --out output/interactive_graph.html \
  --title "Special Relativity and Classical Fields" \
  --validate
```

By default, errors fail validation and warnings are informational. Add `--validation-strict` when warnings should also fail the command, for example in a stricter pre-commit or CI check.

The validator checks structural and textual consistency, including:

- required CSV columns and required concept metadata fields
- duplicate concept ids and duplicate labels
- edge endpoints and relation names
- `\cref{label}{id}` syntax and target ids
- `\optional_details{title}{body}` syntax
- balanced braces and balanced MathJax delimiters `\(...\)` and `\[...\]`
- accidental control characters in text fields
- study-question/study-answer mismatches
- directed relation cycles using the relation direction metadata in `edges_key.csv`

It also reports review warnings such as cross-reference/edge mismatches,
module or member ordering contradictions, and transitively redundant directed
edges. Warnings are review prompts, not necessarily errors.

## Review Directed DAGs

Relations marked `directed=true` in `edges_key.csv` are checked as directed graph edges. Their CSV direction is `source -> target`; for example, `A REQUIRES B` means A requires B.

Print DAG diagnostics without regenerating the viewer:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --dag-report-only
```

By default, the report checks every relation marked `directed=true` in
`edges_key.csv` and their combined subgraph. It lists directed cycles,
transitively redundant edges, foundation and capstone nodes, and longest
source-to-target chains. Module and member order are checked separately by
the module report.

Use `--dag-report` to print the same diagnostics before normal HTML generation. Use `--dag-relations RELATION ...` to inspect an explicit relation set instead of the directed defaults.

## Review Modules

Authored modules can be checked against the concrete concept graph. The module
report contracts concept edges through `module_members.csv`, counts internal
and boundary edges by relation, lists module-to-module boundary pairs, compares
those boundaries with declared `module_supports.csv` entries, and runs DAG
diagnostics on the quotient module graph. It also checks dependencies against
same-domain module sequence and within-module member order.

Print module diagnostics without regenerating the viewer:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --module-report-only
```

Use `--module-report` to print the same diagnostics before normal HTML
generation. Use `--module-relations RELATION ...` to inspect an explicit
relation set, for example:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --module-report-only \
  --module-relations DERIVES_FROM CONSTRUCTED_FROM REQUIRES
```

### Explore Candidate Module Partitions

Candidate generation is a separate authoring operation; it never rewrites the
authored module CSV files. Search one domain over the three principal
dependency relations with:

```bash
conda run -n sr-kg python tools/analyse_module_partitions.py \
  --data-root data \
  --domain sr \
  --module-counts 4 5 6 \
  --min-size 5 \
  --max-size 15
```

The report compares boundary edges, relation counts, modularity, module sizes,
quotient-DAG status, concrete cycle causes, boundary pairs, and concept
membership. Searches are deterministic for a given `--random-seed`; use
`--restarts` to trade runtime for broader exploration. Relation weights can be
changed with repeated `--relation-weight RELATION=WEIGHT` options.

Evaluate an editorial proposal exactly, without searching or changing runtime
data:

```bash
conda run -n sr-kg python tools/analyse_module_partitions.py \
  --data-root data \
  --domain sr \
  --evaluate-members docs/discussion/sr_module_partition_candidate.csv \
  --evaluate-only \
  --show-boundary-edges
```

Without `--evaluate-only`, that proposal is also used as a starting point for
local refinement. `--out report.md` writes the same Markdown report printed to
the terminal.

## Review Concept Graphics

Generate a standalone HTML sheet showing icon and detail SVGs side by side:

```bash
conda run -n sr-kg python tools/show_graphics.py SR-1.8
conda run -n sr-kg python tools/show_graphics.py 'SR-1.*'
conda run -n sr-kg python tools/show_graphics.py '*.*'
```

The default output is `/tmp/srkg-graphics-review.html`. Quote wildcard patterns so the shell does not expand them as filenames. Use `--out path/to/review.html` to choose a different output path.

The review sheet also shows the `icon_caption` and `detail_caption` fields from `data/concept_graphic_designs.csv`, which describe the intended mnemonic and teaching point for each graphic.

## Viewer Features

The viewer presents the graph and the text details as two peer views of the same
knowledge base. The graph pane is on the left, the details pane is on the right,
and the header controls are aligned over the pane they affect:

- `Graph`: `Hide graph`, `All`, or `Focussed`
- `Details`: `Full`, reading-focused modes, or `Hide`
- `Show lens` / `Hide lens` for the graph focus-lens status display

Selection can be a concept, module or relationship, or cleared altogether.
For a selected concept, additional highlighted concepts come from the detail section: ordinary content
uses the immediate neighbourhood, `Derived from` follows the configured
derivation relation outward, and `Where this is used` follows it inward. In
`All` graph mode, background concepts remain visible but dimmed. In `Focussed`
mode, background concepts are hidden and the graph refits to the selected plus
highlighted set. The focus lens summarises that current rule using relation
abbreviations, relation colours, direction, and immediate/tree state.

The control panel contains the global tools that are not local to a single
details section:

- search by display ID, concept ID, title, block text, question text, or
  reference text, with highlighted result snippets and details-panel matches
- a scrollable concept list
- an edge key showing relation colour, direction, category, meaning, and example
- browser-local notes export/import and note editing controls
- published and personal global-layout status, export and reset

The published graph layout is versioned in `data/layout.json`. In Full graph mode,
manual concept and folded-module moves become browser-local overrides and
survive reload. Focussed mode preserves the same global coordinates while
changing only visibility and camera framing. Visible concepts and folded
modules can be moved to improve the current focussed view, but the muted
`Temporary layout` notice indicates that these changes are discarded on
navigation and never alter the saved global layout. The
`Layouts` control-panel section can export a repository-compatible complete
layout, reset personal overrides to the published revision, or resolve a stale
published-revision warning. Folded boxes always follow their member bounds;
no recenter command is necessary.

On phone-sized viewports, the control panel starts hidden and the details panel uses a full-width bottom sheet in portrait orientation. In phone landscape, the details panel returns to a compact right-side sheet so the graph remains usable in the wider canvas.

The details pane shows the selected concept content with MathJax-rendered
equations. It has a sticky masthead, reading-mode selector, and a local contents
section. Contents links open folded target blocks and synchronise the active
detail-section cursor that drives the graph focus. References written as
`\cref{Visible concept title}{concept.id}` become clickable links when the
target concept exists, and hovering a concept link shows a rendered concept
preview without navigating.

Concept prose is rendered from ordered `content_blocks.csv` rows. The viewer
maps semantic block `kind` values to presentation policy:

- definitions, explanations, constructions, results, decompositions, examples,
  and summaries render as normal teaching blocks
- warnings, misconceptions, historical notes, conventions, and derivation steps
  render as compact folded callouts where appropriate
- block icons, colour accents, and labels are viewer policy; the data authors
  semantic kind rather than CSS instructions

The KB also has explicit module source files. Modules are flat authored topic
groups with one primary same-domain module per concept, and
`module_members.csv` is the durable source of truth. The viewer can browse
module pages and fold or expand their graph representation. The module set,
membership, numbering and persistent-layout workflow have been reviewed.
Modules are complete for this phase; GR content remains seed-level WIP.

The details pane also includes relationship sections where available:

- `Derived from` lists immediate derivation inputs, with a local `Full tree`
  toggle for derivation ancestry
- `Where this is used` lists downstream uses grouped by relation, with a local
  `Full tree` toggle for derivation descendants
- `References` lists linked source material attached to the concept, content
  blocks, or study questions
- `Study Questions` is closed by default except in practice-oriented reading
  mode, and each answer is folded

The details panel also supports browser-local user notes. Notes are stored in the browser's `localStorage` under the generated viewer's origin, so they are private to that browser profile and are not written back to the source CSV files. Existing notes are shown as amber fold-down sections. The `Notes` control-panel section has a `Note editing` toggle; when it is off, existing notes are read-only and add-note hooks are hidden. When it is on, small `+ note` controls appear at line boundaries in open content blocks, and notes can be added, edited, or deleted. Use `Export notes` and `Import notes` to move notes through a CSV review workflow.

Concept SVGs are generated by `srkg.concept_svg_graphics`. The details panel
embeds SVG directly; graph nodes show a rasterized icon inside a circle, with
the owning module's background and border colours. Nodes without a graphic
use a plain module-coloured circle.

Graph labels are rendered in an HTML overlay rather than as raw vis.js labels. This allows equation fragments such as `\(A_\mu\)` to render correctly in node labels while preserving normal graph interaction.

Node layout comes from the versioned published layout in `data/layout.json`.
Missing concepts use deterministic module-local placement: structural
prerequisites below more derived concepts, with authored member order breaking
ties and wide ranks wrapping. Missing module anchors use the structural module
DAG. Published coordinates and browser-local overrides take precedence; the
viewer never automatically repacks modules or their concepts.

Folded boxes match their contents' bounding rectangles, including labels and
the configured padding. Corner radius is 18% of the shorter side. Titles fit
within the box up to 160 graph-space font units; counts use a fixed size of 48.
Move modules manually to leave room for boundary edges between them.

The generated viewer uses these coordinates directly. Graph focus and
highlighting reuse the same global layout, so entering Focussed mode changes
visibility and camera framing without projecting the visible nodes into a
different compact layout. In Full graph mode, selecting a node fits the
selected concept and current highlighted context into the unobscured graph
pane, taking visible panels into account. Clicking a visible node walks one
step by making that node the new selected concept; search and concept-list
navigation remain global.

The visible graph nodes are custom-drawn circles on the canvas. The underlying vis.js nodes are transparent fixed-size boxes that include room for the external label, giving the graph a larger interaction footprint. Labels remain in the HTML overlay for MathJax support and scale with graph zoom so they do not dominate the view when zoomed out.

Edge rendering is relation-aware:

- Full graph mode shows only `REQUIRES`, `DERIVES_FROM`, and `CONSTRUCTED_FROM`,
  including internal and folded-module edges; Focussed mode keeps its existing
  context-dependent relations
- relation colours are stable and repeatable across runs
- directed relations use contrasting colours and arrowheads
- undirected relations are rendered without arrowheads and in light grey
- edge lines retain a minimum on-screen thickness when zoomed out, including
  module boundary edges; their stored styles are unchanged
- edge hover uses the same custom MathJax-aware tooltip path as concept hover
- edge hover headings use readable relationship grammar, while relationship
  detail panels also show the raw relation name
- dimmed background edges in all-graph mode remain visible but are not hoverable

## Architecture
The project is a static HTML generator. Concept and relationship content is read from a text-file knowledge-base data root, then Python prepares the data model, computes an initial graph layout, and uses PyVis to emit a base vis-network HTML document. The generator then injects additional CSS and JavaScript for the application UI, MathJax rendering, custom node labels, graph/detail focus behaviour, and interaction handlers. The final output is a standalone interactive_graph.html file that runs directly in a browser.

The generator is organized as a small staged pipeline. The command-line script parses arguments and delegates to `srkg.pipeline`, which coordinates data loading, validation, relation metadata, layout, PyVis rendering, and final HTML injection. `srkg.kb` loads the directory-backed `KnowledgeBase` from `manifest.yaml` and exposes Python query helpers for concepts, content blocks, viewer sections, and graph neighbours.

The lower-level modules are intentionally separated so the data, edge semantics, and layout code can be tested without PyVis or browser-side HTML. PyVis rendering is isolated from the injected viewer application: `srkg.render_pyvis` writes the base graph document, then `srkg.html_injection` layers on MathJax setup, custom node drawing, labels, controls, focus lens display, details panes, and interaction handlers.

`srkg.config` is dependency-free and can be imported by any module. `srkg.pipeline` is the only module that depends on all major stages.

Module placement, colour and persistence are separated into `srkg.module_layout`,
`srkg.module_colours` and `srkg.layout_persistence`. Graph diagnostics live in
`srkg.dag` and `srkg.module_diagnostics`; SVG generation is dispatched through
`srkg.svg_graphics.registry`. Browser rendering and interaction code lives in
`srkg/viewer_assets`.

## Layout Tuning

The main layout, node display, and edge display constants live in `srkg/config.py`:

```python
EDGE_WIDTH = 5.0
EDGE_HOVER_WIDTH = 9.0
EDGE_ARROW_ENDPOINT_OFFSET = 36
NODE_COLLISION_WIDTH = 230
NODE_COLLISION_HEIGHT = 150
NODE_CIRCLE_BASE_SIZE = 90
NODE_CIRCLE_IMPORTANCE_SCALE = 4.0
NODE_LABEL_WIDTH = 250
NODE_LABEL_FONT_SIZE = 30
NODE_LABEL_FONT_WEIGHT = 600
NODE_LABEL_HIDE_BELOW_PX = 6
```

Circle radius is computed from `NODE_CIRCLE_BASE_SIZE` plus `NODE_CIRCLE_IMPORTANCE_SCALE * sqrt(incoming_edge_count + 1)`.
Generated module layout defaults live in `srkg/module_layout.py`: concept
spacing is 350 horizontally and 300 vertically, with at most four columns;
module-anchor spacing is 3300 horizontally and 2700 vertically. These are
fallbacks, not overrides of saved coordinates. `LAYOUT_X_SPACING` and
`LAYOUT_Y_SPACING` in `config.py` serve module-free fixtures only.

Module padding is the default argument in
`srkg/viewer_assets/module_geometry.js` (currently 1 graph unit). Module title
and count sizing live in `fittedModuleLabel` in `srkg/viewer_assets/viewer.js`.
Regenerate the HTML after changing these values.

Active visible edges temporarily use `EDGE_HOVER_WIDTH` while hovered, making the edge path easier to trace in dense parts of the graph. Dimmed background edges remain inert on hover.

The generated graph disables vis-network physics and uses the resolved global
layout. Focussed-mode adjustments are temporary; there is no compact projection.

## Data Format

The current KB file schema is documented in [KB_SCHEMA.md](KB_SCHEMA.md).

`data/nodes.csv` expects concept metadata:

```text
id,display_id,label,domain,domain_title,authoring_status
```

`id` is the stable semantic concept key, for example `sr.lorentz_transformations`.
`display_id` is the module-local number, such as `SR-1.8`, `GR-3.2`, or
`MATHS-2.1`. The first number identifies the module; the second follows a loose
fundamental-to-derived order. Module membership lives in `module_members.csv`,
not in a separate layer field.

`data/content_blocks.csv` is the canonical source for concept prose in the manifest-backed KB.
For drafting style and concept-by-concept workflow, see `docs/authoring/AUTHORING_GUIDE.md`.
Readable draft expositions are kept in `docs/authoring/sr_concept_expositions.md`
and `docs/authoring/gr_concept_expositions.md` before or alongside their split
into CSV blocks.

`data/content_blocks.csv` expects:

```text
block_id,concept_id,sequence,kind,title,body
```

Block `kind` is semantic, not presentational; see `KB_SCHEMA.md` for the accepted
vocabulary and meanings. The viewer renders blocks directly and maps each kind
to presentation policy such as callout colour, symbol, folded/default-open
state, reading-mode membership, local contents entry, and graph-focus role.

`data/study_questions.csv` is the canonical source for concept study questions:

```text
question_id,concept_id,sequence,question_type,prompt,answer
```

If a concept has one or more questions, its details panel includes a default-closed `Study Questions` section. Each answer is rendered inside its own fold-down. Question text can include multiple-choice options, ordinary prose, and MathJax notation.
Current `question_type` values are `short_answer`, `multiple_choice`, and `calculation`.

`data/references.csv` registers books, papers, lectures, websites, and other
sources:

```text
reference_id,reference_type,citation,authors,title,year,url,note
```

Use `citation` for the abbreviated source label shown in the viewer, for
example `TTM II` or `TRR`; keep fuller bibliographic detail in the other fields
or in `note`.

`data/reference_links.csv` attaches those sources to concepts, content blocks,
or study questions:

```text
source_type,source_id,reference_id,locator,note
```

Current `source_type` values are `concept`, `content_block`, and
`study_question`. Prefer linking to the most specific useful item, such as a
derivation content block, with page or section information in `locator`.

`data/edges.csv` expects:

```text
source,target,relation,note
```

The `relation` value controls edge colour, direction, edge-key lookup, detail
section graph focus, and focus-lens display. The `note` value is shown as
edge-specific text in edge hover and relationship details.

`data/edges_key.csv` expects:

```text
relation,directed,category,meaning,example
```

The generator uses `directed` to decide whether each relation type should render
with an arrow and how DAG diagnostics should interpret the edge. The generated
viewer includes an `Edge key` button that shows relation colour, direction,
category, meaning, and example.

The documented schema in [KB_SCHEMA.md](KB_SCHEMA.md) is the supported generator input. Its fields drive labels, panel content, module grouping, search, rendered concept references, source references, graph focus behaviour, and generated concept graphics.

Concept references in content block bodies use:

```latex
\cref{Visible concept title}{concept.id}
```

When the target id exists, the generated viewer renders the reference as a clickable link. Missing targets render as bold text without a link.
