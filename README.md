# SR Knowledge Graph

A small pedagogical knowledge graph viewer for special relativity and classical fields concepts.

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

- layer-based manual node placement
- layer colouring and a layer legend
- relation-aware edge colouring and an edge key
- directed and undirected edge rendering
- section-aware graph focus with a focus-lens status display
- derived-from and where-used sections that drive graph context
- relationship details and edge hover notes with MathJax-aware custom tooltips
- stable, repeatable colour choices across runs

### Math And Graphics

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
docs/
  authoring/
    AUTHORING_GUIDE.md     House style for drafting concept content
    concept_expositions.md Readable draft expositions before CSV block splits
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
  layout.py                Layer-based initial layout logic
  render_pyvis.py          Base PyVis network rendering
  html_injection.py        Browser-side CSS/JS/MathJax injection
  pipeline.py              End-to-end generation workflow
  kb.py                    Manifest-backed knowledge-base loader and query API
tools/
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

It also emits warning-level diagnostics for likely data-quality issues, such as `\cref` references without a corresponding graph edge, graph edges without a reciprocal `\cref`, layer-order issues in directed edges, and transitively redundant directed edges. These warnings are useful review prompts; they are not automatically wrong.

## Review Directed DAGs

Relations marked `directed=true` in `edges_key.csv` are checked as directed graph edges. Their CSV direction is `source -> target`; for example, `A REQUIRES B` means A requires B.

Print DAG diagnostics without regenerating the viewer:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data \
  --dag-report-only
```

By default, the report checks every relation marked `directed=true` in `edges_key.csv` and their combined subgraph. It lists directed cycles if any are present, edges that point from an earlier pedagogical layer to a later target layer, same-layer directed edges, same-layer order violations where a lower-display-numbered source points to a higher-display-numbered target, transitively redundant direct edges, suggested target-first display-ID renumberings within affected layers, any forward references that would remain after those renumberings, foundation nodes, capstone nodes, and the longest source-to-target chain.

Use `--dag-report` to print the same diagnostics before normal HTML generation. Use `--dag-relations RELATION ...` to inspect an explicit relation set instead of the directed defaults.

## Review Concept Graphics

Generate a standalone HTML sheet showing icon and detail SVGs side by side:

```bash
conda run -n sr-kg python tools/show_graphics.py 7.7
conda run -n sr-kg python tools/show_graphics.py '7.*'
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

There is always one selected concept after navigation has started. Additional
highlighted concepts come from the selected detail section: ordinary content
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

Some concepts also have deterministic SVG graphics generated by `srkg.concept_svg_graphics`. When a graphic exists, the detail panel embeds the SVG directly so it remains crisp at panel size. The graph node also shows a small rasterized version clipped inside the circular node, with a pale layer-colour background and a full layer-colour outline. Nodes without a graphic keep the existing solid layer-colour circle.

Graph labels are rendered in an HTML overlay rather than as raw vis.js labels. This allows equation fragments such as `\(A_\mu\)` to render correctly in node labels while preserving normal graph interaction.

Node layout is seeded from the pedagogical layer encoded in each node. The generator reads the `layer` column, falling back to the leading `display_id` prefix such as `3` in `3.2`; layer 1 is placed at the bottom of the graph and higher numbered layers appear above it. Within each layer, nodes are placed left-to-right by `display_id` on a left-aligned upward curve.

The generated viewer uses these manual coordinates directly. Graph focus and highlighting reuse the same source layout, so the graph does not drift or resettle during interaction. In all-graph mode, selecting a node fits the selected concept and current highlighted context into the unobscured graph pane, taking visible panels into account. Focussed mode applies a compact layer-based layout to only the selected local context, collapsing missing layers into a compact view. Clicking a visible node walks one step by making that node the new selected concept; search and concept-list navigation remain global.

The visible graph nodes are custom-drawn circles on the canvas. The underlying vis.js nodes are transparent fixed-size boxes that include room for the external label, giving the graph a larger interaction footprint. Labels remain in the HTML overlay for MathJax support and scale with graph zoom so they do not dominate the view when zoomed out.

Edge rendering is relation-aware:

- relation colours are stable and repeatable across runs
- directed relations use contrasting colours and arrowheads
- undirected relations are rendered without arrowheads and in light grey
- edge lines are drawn heavier than the PyVis default
- edge hover uses the same custom MathJax-aware tooltip path as concept hover
- edge hover headings use readable relationship grammar, while relationship
  detail panels also show the raw relation name
- dimmed background edges in all-graph mode remain visible but are not hoverable

## Architecture
The project is a static HTML generator. Concept and relationship content is read from a text-file knowledge-base data root, then Python prepares the data model, computes an initial graph layout, and uses PyVis to emit a base vis-network HTML document. The generator then injects additional CSS and JavaScript for the application UI, MathJax rendering, custom node labels, graph/detail focus behaviour, and interaction handlers. The final output is a standalone interactive_graph.html file that runs directly in a browser.

The generator is organized as a small staged pipeline. The command-line script parses arguments and delegates to `srkg.pipeline`, which coordinates data loading, validation, relation metadata, layout, PyVis rendering, and final HTML injection. `srkg.kb` loads the directory-backed `KnowledgeBase` from `manifest.yaml` and exposes Python query helpers for concepts, content blocks, viewer sections, and graph neighbours.

The lower-level modules are intentionally separated so the data, edge semantics, and layout code can be tested without PyVis or browser-side HTML. PyVis rendering is isolated from the injected viewer application: `srkg.render_pyvis` writes the base graph document, then `srkg.html_injection` layers on MathJax setup, custom node drawing, labels, controls, focus lens display, details panes, and interaction handlers.

`srkg.config` is dependency-free and can be imported by any module. `srkg.pipeline` is the only module that depends on all major stages.

## Module dependency graph

```text
tools/generate_pyvis.py
  -> srkg.pipeline

tools/show_graphics.py
  -> srkg.concept_svg_graphics

srkg.pipeline
  -> srkg.kb
  -> srkg.data
  -> srkg.edges
  -> srkg.layout
  -> srkg.render_pyvis
  -> srkg.html_injection

srkg.validation
  -> srkg.config
  -> srkg.data
  -> srkg.dag
  -> srkg.edges
  -> srkg.kb
  -> srkg.layout

srkg.render_pyvis
  -> srkg.config
  -> srkg.edges

srkg.html_injection
  -> srkg.config

srkg.data
  -> srkg.config
  -> srkg.concept_svg_graphics
  -> srkg.model

srkg.kb
  -> srkg.config
  -> srkg.data
  -> srkg.model

srkg.edges
  -> srkg.config

srkg.layout
  -> srkg.config

srkg.concept_svg_graphics
  -> no project modules

srkg.model
  -> no project modules

srkg.config
  -> no project modules
```

## Layout Tuning

The main layout, node display, and edge display constants live in `srkg/config.py`:

```python
EDGE_WIDTH = 5.0
EDGE_HOVER_WIDTH = 9.0
EDGE_ARROW_ENDPOINT_OFFSET = 36
LAYOUT_X_SPACING = 350
LAYOUT_Y_SPACING = 400
LAYOUT_ROW_STAGGER = 35
LAYOUT_ROW_CURVE_FLAT_COUNT = 2
LAYOUT_ROW_CURVE_TARGET_NODE = 6
LAYOUT_ROW_CURVE_TARGET_RISE_FRACTION = 0.9
LAYOUT_ROW_CURVE_MAX_RISE_FRACTION = 1.5
LAYOUT_ROW_CURVE_EXPONENT = 2.0
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
Nodes are placed left-to-right by `display_id` within each layer, with every global row sharing the same left x anchor. The `LAYOUT_ROW_CURVE_*` constants control the upward curve used by the global Python layout. `LAYOUT_ROW_STAGGER` is still used by the browser-side compact focussed layout.
Active visible edges temporarily use `EDGE_HOVER_WIDTH` while hovered, making the edge path easier to trace in dense parts of the graph. Dimmed background edges remain inert on hover.

The generated graph disables vis-network physics and uses the deterministic coordinates from `srkg.layout`.

## Data Format

The current KB file schema is documented in [KB_SCHEMA.md](KB_SCHEMA.md).

`data/nodes.csv` expects concept metadata:

```text
id,display_id,label,layer,layer_title
```

`id` is the stable semantic concept key, for example `sr.lorentz_transformations`.
`display_id` is the human-facing ordered number, for example `3.3`, used for
visible numbering, sorting, and layout.

`data/content_blocks.csv` is the canonical source for concept prose in the manifest-backed KB.
For drafting style and concept-by-concept workflow, see `docs/authoring/AUTHORING_GUIDE.md`.
Readable draft expositions are kept in `docs/authoring/concept_expositions.md` before or
alongside their split into CSV blocks.

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

The documented schema in [KB_SCHEMA.md](KB_SCHEMA.md) is the supported generator input. The richer fields drive labels, panel content, layer grouping, search, rendered concept references, source references, graph focus behaviour, and optional generated concept graphics.

Concept references in content block bodies use:

```latex
\cref{Visible concept title}{concept.id}
```

When the target id exists, the generated viewer renders the reference as a clickable link. Missing targets render as bold text without a link.
