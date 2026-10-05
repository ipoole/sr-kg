# Architecture

## Generation and runtime

The project generates a static interactive HTML viewer from a manifest-backed
knowledge base. Python loads and validates authored data, resolves relationships
and layout, renders a base PyVis network, and injects the browser application.
The generated page needs no application server, but is not self-contained:
vis-network and MathJax load from CDNs, and the PyVis template also references
`lib/bindings/utils.js` relative to the HTML file.

`srkg.pipeline` coordinates the stages. `srkg.kb` exposes the loaded knowledge
model; data, graph diagnostics, layout and SVG graphics can be tested separately
from rendering. `srkg.render_pyvis` produces the base document and
`srkg.html_injection` adds the application in `srkg/viewer_assets`.

The [schema](kb_schema.md) defines durable input contracts. The generated viewer
is an artifact, not an alternative authoring source.

## Content and presentation

The concept graph provides navigation; flat ordered blocks provide the teaching
narrative. Block kinds express meaning. Folding, reading modes, visual treatment
and visibility are viewer policy; see [Viewer behaviour](viewer.md).
The viewer keeps four concerns independent: selection, context rule, display
scope and camera. A single renderer derives the selected context from a relation
preset and depth, then projects it through the current folded or expanded module
representation. Full display adds the structural graph as subdued background;
Context-only display omits it. Neither mode silently changes folding or camera.

Graph and details are peer views of the same KB. Selecting a detail section can
offer a relevant context, but applying it remains an explicit user action.
Search, cross-references and browser history provide navigation beyond visible
nodes.
Module semantics and graph filtering are described in [Modules](modules.md).

Concept graphics are deterministic SVGs, used directly in details and as
rasterised graph icons. HTML labels allow mathematical notation on the graph.
Rendering constants and drawing mechanics remain in code.

## User state

Notes, personal layout, study attempts and reading marks form one local-first
[personal-data model](personal_data.md), separate from authored content and
transient viewer state. A versioned portable archive supports backup and
transfer; browser origin and profile still determine which local copy is
available. Layout has the separate publication workflow described in
[Layout](layout.md). Browser data never writes back to the KB automatically.

Notes can target concept or module sections. New notes use the authored
`block_id` where available and retain textual context around their insertion
point. Existing title/index anchors are migrated when they resolve
unambiguously. Notes whose content no longer has a safe match remain stored and
are visibly flagged for placement.

## Future plans

Fine-grained dependency-driven presentation remains an experiment, not a schema
commitment; see the [pedagogy discussion](../discussion/adaptive_pedagogy_and_fine_grained_kb.md).
