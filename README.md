# SR Knowledge Graph

A small pedagogical knowledge graph viewer for special relativity concepts.

The project reads concept data from CSV files and generates a standalone interactive HTML graph using PyVis and vis.js. The generated viewer supports:

- searchable concept list
- clickable graph nodes
- right-hand concept detail panel
- clickable `\cref{label}{id}` references in concept descriptions
- MathJax rendering for inline and display equations
- layer colouring and legend
- neighbour highlighting and neighbourhood mode
- layout freeze/restart controls

## Repository Layout

```text
data/
  nodes.csv                Concept metadata and descriptions
  edges.csv                Directed concept relationships
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
  --edges data/edges.csv \
  --out output/interactive_graph.html
```

Then open `output/interactive_graph.html` in a browser.

MathJax is loaded from a CDN in the generated HTML, so equation rendering requires network access when viewing the file.

## Data Format

`data/nodes.csv` expects:

```text
id,label,layer,layer_title,body
```

`data/edges.csv` expects:

```text
source,target,type
```

Only `id`, `source`, and `target` are strictly required by the generator. The richer fields drive labels, panel content, layer grouping, search, and rendered concept references.

Concept references in node bodies use:

```latex
\cref{Visible concept title}{concept.id}
```

When the target id exists, the generated viewer renders the reference as a clickable link. Missing targets render as bold text without a link.

