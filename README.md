# SR Knowledge Graph

A small pedagogical knowledge graph viewer for special relativity concepts.

The project reads concept data from CSV files and generates a standalone interactive HTML graph using PyVis and vis.js. The generated viewer supports:

- searchable concept list
- clickable graph nodes, concept-list entries, and concept references
- right-hand concept detail panel with rendered equations
- clickable `\cref{label}{id}` references in concept descriptions
- MathJax rendering for inline and display equations
- MathJax-rendered graph labels for node IDs and concept names
- layer colouring and a layer legend
- relation-aware edge colouring and an edge key
- edge-type filters with persistent checkboxes
- relation-specific edge hover notes with wrapped tooltip text
- directed and undirected edge rendering
- neighbour highlighting, neighbourhood mode, and show-all mode
- layout freeze/restart controls
- stable, repeatable colour choices across runs

## Repository Layout

```text
data/
  nodes.csv                Concept metadata and descriptions
  edges.csv                Legacy concept relationships
  knowledge_edges.csv      Refined relationships with relation types and notes
  edges_key.csv            Edge relation meanings and direction metadata
lib/
  vis-9.1.2/               Vendored vis-network assets used by PyVis output
  tom-select/              Vendored PyVis UI assets
  bindings/                PyVis binding asset
output/
  interactive_graph.html   Generated standalone viewer
tools/
  generate_pyvis.py        CSV-to-HTML generator
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
  --out output/interactive_graph.html
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
- layout freeze and restart controls
- an Edge key button
- edge-type filter checkboxes

The right panel shows the selected concept body with MathJax-rendered equations. References written as `\cref{Visible concept title}{concept.id}` become clickable links when the target concept exists.

Graph labels are rendered in an HTML overlay rather than as raw vis.js labels. This allows equation fragments such as `\(A_\mu\)` to render correctly in node labels while preserving normal graph interaction.

Edge rendering is relation-aware:

- relation colours are stable and repeatable across runs
- directed relations use contrasting colours and arrowheads
- undirected relations are rendered without arrowheads and in light grey
- edge lines are drawn heavier than the PyVis default
- edge hover text shows the relation name and the edge note, wrapped across multiple lines
- edge tooltips use an opaque background and are drawn above graph labels

The `Edge types` checkboxes in the left panel toggle relation types on and off. The filter is respected in show-all, selected-node highlighting, and neighbourhood mode.

## Data Format

`data/nodes.csv` expects:

```text
id,label,layer,layer_title,body
```

`data/edges.csv` expects:

```text
source,target,type
```

`data/knowledge_edges.csv` uses the same required endpoints but normally includes relation notes:

```text
source,target,relation,note
```

The edge relation column may be named either `type` or `relation`. Optional `note` or `notes` columns are accepted. When present, the note is shown in the edge hover tooltip.

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
