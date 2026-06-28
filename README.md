# SR Knowledge Graph

A small pedagogical knowledge graph viewer for special relativity concepts.

The project reads concept data from CSV files and generates a standalone interactive HTML graph using PyVis and vis.js. The generated viewer supports:

- searchable concept list
- clickable graph nodes, concept-list entries, and concept references
- browser back/forward navigation between selected concepts
- recent-concept navigation in the control panel
- right-hand concept detail panel with rendered equations
- clickable `\cref{label}{id}` references in concept descriptions
- MathJax rendering for inline and display equations
- MathJax-rendered graph labels for node IDs and concept names
- topological-sort-based initial node placement with physics refinement
- layer colouring and a layer legend
- relation-aware edge colouring and an edge key
- edge-type filters with persistent checkboxes
- relation-specific edge hover notes with wrapped tooltip text
- directed and undirected edge rendering
- neighbour highlighting, neighbourhood mode, and show-all mode
- layout restart control
- stable, repeatable colour choices across runs

## Repository Layout

```text
data/
  nodes.csv                Concept metadata and descriptions
  knowledge_edges.csv      Concept relationships with relation types and notes
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
  edges.py                 Edge relation semantics and tooltip helpers
  layout.py                Layer-based initial layout logic
  render_pyvis.py          Base PyVis network rendering
  html_injection.py        Browser-side CSS/JS/MathJax injection
  pipeline.py              End-to-end generation workflow
tools/
  generate_pyvis.py        Command-line entry point
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
  --edges data/knowledge_edges.csv \
  --edge-key data/edges_key.csv \
  --out output/interactive_graph.html \
  --title "Special Relativity and Classical Fields"
```

Then open `output/interactive_graph.html` in a browser.

MathJax is loaded from a CDN in the generated HTML, so equation rendering requires network access when viewing the file.

There is also a PyCharm run configuration named `Generate Knowledge Graph` that runs the same command against `data/nodes.csv`, `data/knowledge_edges.csv`, and `data/edges_key.csv`.

If `--edge-key` is omitted, the generator automatically looks for `edges_key.csv` beside the selected edge file.

## Viewer Features

The left control panel provides:

- search by concept ID, title, layer text, or body text
- a scrollable concept list
- graph reset and show-all controls
- neighbourhood mode for the selected node
- layout restart control
- an Edge key button
- edge-type filter checkboxes
- a controls-panel show/hide toggle
- a details-panel show/hide toggle

The right panel shows the selected concept body with MathJax-rendered equations. References written as `\cref{Visible concept title}{concept.id}` become clickable links when the target concept exists.

Graph labels are rendered in an HTML overlay rather than as raw vis.js labels. This allows equation fragments such as `\(A_\mu\)` to render correctly in node labels while preserving normal graph interaction.

Node layout is seeded from the pedagogical layer encoded in each node. The generator reads the `layer` column, falling back to the leading ID prefix such as `3` in `3.2`; layer 1 is placed at the bottom of the graph and higher numbered layers appear above it. Within each layer, nodes are ordered by a deterministic barycentric pass that uses connected neighbours in other layers to reduce crossings while preserving the layer assignment.

The generated viewer then runs a short initial vis.js physics adjustment with vertical movement locked, so nodes can shift sideways but stay in their pedagogical layers. Once the layout stabilizes, after a short timeout, or as soon as the user interacts with the graph, the current node positions are captured, physics is disabled, and node dragging is unlocked in both axes. Filtering and selection therefore do not cause the graph to drift or snap back, while users can still manually move nodes up or down after the initial layout.

The visible graph nodes are custom-drawn circles on the canvas. The underlying vis.js nodes are transparent fixed-size collision boxes that include room for the external label, so the physics model has a better approximation of the rendered footprint. Labels remain in the HTML overlay for MathJax support and scale with graph zoom so they do not dominate the view when zoomed out.

Edge rendering is relation-aware:

- relation colours are stable and repeatable across runs
- directed relations use contrasting colours and arrowheads
- undirected relations are rendered without arrowheads and in light grey
- edge lines are drawn heavier than the PyVis default
- edge hover text shows the relation name and the edge note, wrapped across multiple lines
- edge tooltips use an opaque background and are drawn above graph labels

The `Edge types` checkboxes in the left panel toggle relation types on and off. The filter is respected in show-all, selected-node highlighting, and neighbourhood mode.

## Architecture
The project is a static HTML generator. Concept and relationship content is read from CSV files, then Python prepares the data model, computes an initial graph layout, and uses PyVis to emit a base vis-network HTML document. The generator then injects additional CSS and JavaScript for the application UI, MathJax rendering, custom node labels, filtering, and interaction behaviour. The final output is a standalone interactive_graph.html file that runs directly in a browser.

The generator is organized as a small staged pipeline. The command-line script parses arguments and delegates to `srkg.pipeline`, which coordinates data loading, validation, relation metadata, layout, PyVis rendering, and final HTML injection.

The lower-level modules are intentionally separated so the data, edge semantics, and layout code can be tested without PyVis or browser-side HTML. PyVis rendering is isolated from the injected viewer application: `srkg.render_pyvis` writes the base graph document, then `srkg.html_injection` layers on MathJax setup, custom node drawing, labels, controls, filters, and interaction handlers.

`srkg.config` is dependency-free and can be imported by any module. `srkg.pipeline` is the only module that depends on all major stages.

## Modules

- `tools/generate_pyvis.py`: generate_pyvis.py
- `srkg/__init__.py`: SR knowledge graph generation package.
- `srkg/config.py`: Shared configuration constants for the SR knowledge graph generator.
- `srkg/data.py`: CSV-adjacent data helpers for the SR knowledge graph.
- `srkg/edges.py`: Edge relation semantics, colours, and display helpers.
- `srkg/layout.py`: Layer-based node layout helpers.
- `srkg/render_pyvis.py`: PyVis network rendering for the SR knowledge graph.
- `srkg/html_injection.py`: HTML, CSS, and JavaScript injection for the generated viewer.
- `srkg/pipeline.py`: End-to-end graph generation pipeline.

Module dependency graph:

```text
tools/generate_pyvis.py
  -> srkg.pipeline

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

srkg.edges
  -> srkg.config

srkg.layout
  -> srkg.config

srkg.config
  -> no project modules
```

## Layout Tuning

The main layout and node display constants live in `srkg/config.py`:

```python
LAYOUT_X_SPACING = 600
LAYOUT_Y_SPACING = 320
LAYOUT_ROW_STAGGER = 70
NODE_COLLISION_WIDTH = 280
NODE_COLLISION_HEIGHT = 170
NODE_LABEL_WIDTH = 180
NODE_LABEL_FONT_SIZE = 28
```

Circle size is controlled where nodes are added in `srkg/render_pyvis.py`:

```python
size = 50 + 4.0 * math.sqrt(importance + 1)
```

The physics settings are in the `net.set_options(...)` block in `srkg/render_pyvis.py`. They control the initial relaxation only; the generated viewer freezes the settled layout before normal interaction.

## Data Format

`data/nodes.csv` expects:

```text
id,label,layer,layer_title,body
```

`data/knowledge_edges.csv` expects:

```text
source,target,relation,note
```

The `relation` value controls edge colour, direction, filtering, and edge-key lookup. The `note` value is shown in the edge hover tooltip.

`data/edges_key.csv` expects:

```text
relation,directed,category,meaning,example
```

The generator uses `directed` to decide whether each relation type should render with an arrow. The generated viewer includes an `Edge key` button that shows the relation colour, direction, category, meaning, and example.

Only `id`, `source`, and `target` are strictly required by the generator. The richer node fields drive labels, panel content, layer grouping, search, and rendered concept references.

Concept references in node bodies use:

```latex
\cref{Visible concept title}{concept.id}
```

When the target id exists, the generated viewer renders the reference as a clickable link. Missing targets render as bold text without a link.
