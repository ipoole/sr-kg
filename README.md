# SR Knowledge Graph

A small pedagogical knowledge graph viewer for special relativity and classical fields concepts.

The project reads concept data from CSV files and generates a standalone interactive HTML graph using PyVis and vis.js. The generated viewer supports:

- searchable concept list
- clickable graph nodes, concept-list entries, and concept references
- browser back/forward navigation between selected concepts
- recent-concept navigation in the control panel
- right-hand concept detail panel with rendered equations and optional SVG graphics
- clickable `\cref{label}{id}` references in concept descriptions
- MathJax rendering for inline and display equations
- MathJax-rendered graph labels for node IDs and concept names
- generated concept SVG graphics in the detail panel and graph nodes where available
- layer-based manual node placement
- layer colouring and a layer legend
- relation-aware edge colouring and an edge key
- edge-type filters with persistent checkboxes
- relation-specific edge hover notes with wrapped tooltip text
- directed and undirected edge rendering
- neighbour highlighting, descendants mode, neighbourhood mode, and all-graph mode
- stable, repeatable colour choices across runs

## Repository Layout

```text
data/
  nodes.csv                Concept metadata and descriptions
  edges.csv                Concept relationships with relation types and notes
  edges_key.csv            Edge relation meanings and direction metadata
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
  edges.py                 Edge relation semantics and tooltip helpers
  layout.py                Layer-based initial layout logic
  render_pyvis.py          Base PyVis network rendering
  html_injection.py        Browser-side CSS/JS/MathJax injection
  pipeline.py              End-to-end generation workflow
tools/
  generate_pyvis.py        Command-line entry point
  show_graphics.py         SVG graphics review sheet generator
```

## Setup

Use Python 3.12 or newer.

```bash
python -m pip install -r requirements.txt
```

## Generate The Viewer

```bash
python tools/generate_pyvis.py \
  --nodes data/nodes.csv \
  --edges data/edges.csv \
  --edge-key data/edges_key.csv \
  --out output/interactive_graph.html \
  --title "Special Relativity and Classical Fields"
```

Then open `output/interactive_graph.html` in a browser.

MathJax is loaded from a CDN in the generated HTML, so equation rendering requires network access when viewing the file.

There is also a PyCharm run configuration named `Generate Knowledge Graph` that runs the same command against `data/nodes.csv`, `data/edges.csv`, and `data/edges_key.csv`.

If `--edge-key` is omitted, the generator automatically looks for `edges_key.csv` beside the selected edge file.

## Review Directed DAGs

Relations marked `directed=true` in `edges_key.csv` are checked as directed graph edges. Their CSV direction is `source -> target`; for example, `A PREREQUISITE B` means A requires B.

Print DAG diagnostics without regenerating the viewer:

```bash
python tools/generate_pyvis.py \
  --nodes data/nodes.csv \
  --edges data/edges.csv \
  --dag-report-only
```

By default, the report checks every relation marked `directed=true` in `edges_key.csv` and their combined subgraph. It lists directed cycles if any are present, edges that point from an earlier pedagogical layer to a later target layer, same-layer directed edges, same-layer order violations where a lower-numbered source points to a higher-numbered target, transitively redundant direct edges, suggested target-first renumberings within affected layers, any forward references that would remain after those renumberings, foundation nodes, capstone nodes, and the longest source-to-target chain.

Use `--dag-report` to print the same diagnostics before normal HTML generation. Use `--dag-relations RELATION ...` to inspect an explicit relation set instead of the directed defaults.

## Review Concept Graphics

Generate a standalone HTML sheet showing icon and detail SVGs side by side:

```bash
python tools/show_graphics.py 7.7
python tools/show_graphics.py '7.*'
python tools/show_graphics.py '*.*'
```

The default output is `/tmp/srkg-graphics-review.html`. Quote wildcard patterns so the shell does not expand them as filenames. Use `--out path/to/review.html` to choose a different output path.

The review sheet also shows the `icon_caption` and `detail_caption` fields from `data/concept_graphic_designs.csv`, which describe the intended mnemonic and teaching point for each graphic.

## Viewer Features

The left control panel provides:

- search by concept ID, title, definition, derivation, or explanation text, with highlighted result snippets and details-panel matches
- a scrollable concept list
- an all-graph control
- neighbourhood mode for the selected node
- descendants mode for nodes reachable from the selected node via enabled directed edges
- an Edge key button
- edge-type filter checkboxes

Canvas-level controls provide persistent show/hide toggles for the control panel and the details panel. Hiding the details panel remains in effect while browsing; selecting another node updates the details content in the background without reopening the panel.

On phone-sized viewports, the control panel starts hidden and the details panel uses a full-width bottom sheet in portrait orientation. In phone landscape, the details panel returns to a compact right-side sheet so the graph remains usable in the wider canvas.

The right panel shows the selected concept content with MathJax-rendered equations. It renders optional `Definition`, `Derivation`, and `Explanation` sections when those fields are present. References written as `\cref{Visible concept title}{concept.id}` become clickable links when the target concept exists.

Some concepts also have deterministic SVG graphics generated by `srkg.concept_svg_graphics`. When a graphic exists, the detail panel embeds the SVG directly so it remains crisp at panel size. The graph node also shows a small rasterized version clipped inside the circular node, with a pale layer-colour background and a full layer-colour outline. Nodes without a graphic keep the existing solid layer-colour circle.

Graph labels are rendered in an HTML overlay rather than as raw vis.js labels. This allows equation fragments such as `\(A_\mu\)` to render correctly in node labels while preserving normal graph interaction.

Node layout is seeded from the pedagogical layer encoded in each node. The generator reads the `layer` column, falling back to the leading ID prefix such as `3` in `3.2`; layer 1 is placed at the bottom of the graph and higher numbered layers appear above it. Within each layer, nodes are placed left-to-right by numeric concept ID on a left-aligned upward curve.

The generated viewer uses these manual coordinates directly. Filtering and highlighting reuse the same source layout, so the graph does not drift or resettle during interaction. In all-graph mode, selecting a node fits the selected node and its enabled neighbours into the unobscured canvas area, taking the visible control and details panels into account. Neighbourhood mode applies a compact layer-based layout to only the selected local nodes, collapsing missing layers into a compact view. Descendants mode applies the same compact layout to the selected node and every node reachable by following enabled directed edges outward. In either local browsing mode, clicking a visible node walks one step by making that node the new focus; search and concept-list navigation remain global.

The visible graph nodes are custom-drawn circles on the canvas. The underlying vis.js nodes are transparent fixed-size boxes that include room for the external label, giving the graph a larger interaction footprint. Labels remain in the HTML overlay for MathJax support and scale with graph zoom so they do not dominate the view when zoomed out.

Edge rendering is relation-aware:

- relation colours are stable and repeatable across runs
- directed relations use contrasting colours and arrowheads
- undirected relations are rendered without arrowheads and in light grey
- edge lines are drawn heavier than the PyVis default
- edge hover text shows the relation name and the edge note, wrapped across multiple lines
- edge tooltips use an opaque background and are drawn above graph labels

The `Edge types` checkboxes in the left panel toggle relation types on and off. The filter is respected in all-graph, selected-node highlighting, neighbourhood, and descendants modes.

## Architecture
The project is a static HTML generator. Concept and relationship content is read from CSV files, then Python prepares the data model, computes an initial graph layout, and uses PyVis to emit a base vis-network HTML document. The generator then injects additional CSS and JavaScript for the application UI, MathJax rendering, custom node labels, filtering, and interaction behaviour. The final output is a standalone interactive_graph.html file that runs directly in a browser.

The generator is organized as a small staged pipeline. The command-line script parses arguments and delegates to `srkg.pipeline`, which coordinates data loading, validation, relation metadata, layout, PyVis rendering, and final HTML injection.

The lower-level modules are intentionally separated so the data, edge semantics, and layout code can be tested without PyVis or browser-side HTML. PyVis rendering is isolated from the injected viewer application: `srkg.render_pyvis` writes the base graph document, then `srkg.html_injection` layers on MathJax setup, custom node drawing, labels, controls, filters, and interaction handlers.

`srkg.config` is dependency-free and can be imported by any module. `srkg.pipeline` is the only module that depends on all major stages.

## Module dependency graph

```text
tools/generate_pyvis.py
  -> srkg.pipeline

tools/show_graphics.py
  -> srkg.concept_svg_graphics

srkg.pipeline
  -> srkg.data
  -> srkg.edges
  -> srkg.layout
  -> srkg.render_pyvis
  -> srkg.html_injection

srkg.render_pyvis
  -> srkg.config
  -> srkg.edges

srkg.html_injection
  -> srkg.config

srkg.data
  -> srkg.config
  -> srkg.concept_svg_graphics

srkg.edges
  -> srkg.config

srkg.layout
  -> srkg.config

srkg.concept_svg_graphics
  -> no project modules

srkg.config
  -> no project modules
```

## Layout Tuning

The main layout, node display, and edge display constants live in `srkg/config.py`:

```python
EDGE_WIDTH = 5.0
EDGE_HOVER_WIDTH = 12.0
LAYOUT_X_SPACING = 350
LAYOUT_Y_SPACING = 400
LAYOUT_ROW_STAGGER = 35
LAYOUT_ROW_CURVE_FLAT_COUNT = 2
LAYOUT_ROW_CURVE_TARGET_NODE = 6
LAYOUT_ROW_CURVE_TARGET_RISE_FRACTION = 0.9
LAYOUT_ROW_CURVE_MAX_RISE_FRACTION = 1.5
LAYOUT_ROW_CURVE_EXPONENT = 2.0
NODE_COLLISION_WIDTH = 280
NODE_COLLISION_HEIGHT = 170
NODE_CIRCLE_BASE_SIZE = 60
NODE_CIRCLE_IMPORTANCE_SCALE = 4.0
NODE_LABEL_WIDTH = 250
NODE_LABEL_FONT_SIZE = 30
NODE_LABEL_FONT_WEIGHT = 700
```

Circle radius is computed from `NODE_CIRCLE_BASE_SIZE` plus `NODE_CIRCLE_IMPORTANCE_SCALE * sqrt(incoming_edge_count + 1)`.
Nodes are placed left-to-right by numeric concept ID within each layer, with every global row sharing the same left x anchor. The `LAYOUT_ROW_CURVE_*` constants control the upward curve used by the global Python layout. `LAYOUT_ROW_STAGGER` is still used by the browser-side compact neighbourhood layout.
Visible edges temporarily use `EDGE_HOVER_WIDTH` while hovered, making the edge path easier to trace in dense parts of the graph.

The generated graph disables vis-network physics and uses the deterministic coordinates from `srkg.layout`.

## Data Format

`data/nodes.csv` expects:

```text
id,label,layer,layer_title,definition_new,derivation_new,explanation_new
```

The generated details panel renders `definition_new`, `derivation_new`, and `explanation_new`, including optional derivations. The learner-focused `explanation_new` field should include any useful examples. Empty values are skipped in the details panel.

Nodes may also include optional numbered study-question pairs:

```text
study_question_1,study_answer_1,study_question_2,study_answer_2,...
```

The viewer detects all `study_question_N` columns present in `nodes.csv`. If a concept has one or more questions, its details panel includes a default-closed `Study Questions` section. Each answer is rendered inside its own fold-down. Question text can include multiple-choice options, ordinary prose, and MathJax notation.

`data/edges.csv` expects:

```text
source,target,relation,note
```

The `relation` value controls edge colour, direction, filtering, and edge-key lookup. The `note` value is shown in the edge hover tooltip.

`data/edges_key.csv` expects:

```text
relation,directed,category,meaning,example
```

The generator uses `directed` to decide whether each relation type should render with an arrow. The generated viewer includes an `Edge key` button that shows the relation colour, direction, category, meaning, and example.

Only `id`, `source`, and `target` are strictly required by the generator. The richer node fields drive labels, panel content, layer grouping, search, rendered concept references, and optional generated concept graphics.

Concept references in node bodies use:

```latex
\cref{Visible concept title}{concept.id}
```

When the target id exists, the generated viewer renders the reference as a clickable link. Missing targets render as bold text without a link.
