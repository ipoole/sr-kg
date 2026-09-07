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
The focus lens follows the active detail block
in Auto mode. Manual mode allows arbitrary relation-and-direction traversals at
one-hop or tree depth and preserves them as concept selection changes. Modules
containing reached concepts expand temporarily so folding does not hide the
chosen context. In Full mode, the lens is a foreground overlay: its selected
edges override the structural-edge filter applied to the background. Focussed
mode hides that background. This keeps authoring manageable without a second
block-dependency graph or pervasive depth labels.

Graph and details are peer views of the same KB. Selection and the active detail
section determine highlighted context: ordinary neighbourhoods or derivation
ancestry and descendants. Current derivation trees follow `DERIVES_FROM` only;
construction has a separate context. The focus lens explains that context. Search,
cross-references and browser history provide navigation beyond visible nodes.
Module semantics and graph filtering are described in [Modules](modules.md).

Concept graphics are deterministic SVGs, used directly in details and as
rasterised graph icons. HTML labels allow mathematical notation on the graph.
Rendering constants and drawing mechanics remain in code.

## User state

User notes and personal global-layout overrides live in browser-local storage,
separate from authored content. Notes can target concept or module sections and
support backwards-compatible CSV import/export; layout has a
versioned publication workflow described in [Layout](layout.md). Neither writes
back to the KB automatically. Browser origin and profile determine which local
state is available. Notes are anchored by target ID, section title and a local
text-block index, rather than the authored `block_id`; changing section titles
or splitting prose can therefore affect their placement.

## Future plans

Derivation paths will include both `DERIVES_FROM` and `CONSTRUCTED_FROM`,
retaining their distinct relation meanings. This decision is accepted but not
yet implemented; see [open issues](../issues.md).

Fine-grained dependency-driven presentation remains an experiment, not a schema
commitment; see the [pedagogy discussion](../discussion/adaptive_pedagogy_and_fine_grained_kb.md).
