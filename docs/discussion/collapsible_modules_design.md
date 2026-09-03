# Collapsible Module Graph Design

Captured on 2026-08-18.

## Context

Adding General Relativity will probably make the full graph too large to keep
usable as one always-expanded canvas. The likely solution is collapsible and
expandable subgraphs, referred to here as modules.

This note captures design discussion before any schema or viewer changes. It is
not runtime KB data.

## Core Direction

Modules should be explicit authored knowledge-base entities, not graph clusters
computed live by the viewer.

Graph analysis can suggest candidate module boundaries and diagnose awkward
assignments, but the runtime source of truth should be authored module data.
That keeps the user experience stable, explainable, and pedagogically curated.

The important distinction is:

- graph analysis is an authoring/review aid
- module membership is authored source data
- collapse/expand state is viewer state

## Domain, Module, Concept, Block

The atlas now has several organising axes that should not be collapsed into one
field:

```text
domain
  module
    concept
      content block
```

Modules now subsume the former layers as pedagogical and layout groupings.
Module sequence and within-module dependency order provide teaching order;
there is no separate runtime layer field. Historical alternatives later in
this document record the earlier layer-based design discussion.

The current branch already uses domain metadata in `nodes.csv`, for example
`sr`, `gr`, and `math`. Modules should therefore have an owning domain, and a
concept's primary module should normally be in the same domain as the concept.
This keeps the hierarchy simple and makes folding easier to reason about.

Cross-domain support should be represented explicitly rather than by making
module membership arbitrary. For example, a GR module may use
`math.tangent_space` or `math.tensor_field` as prerequisite support, but those
math concepts should remain owned by a math module. The GR module can list them
as supports.

Initial rule:

- a concept has one primary owning module
- a module belongs to one domain
- cross-domain dependencies are supports, not ownership
- arbitrary overlapping fold sets are deferred
- modules are flat in the first schema; hierarchical modules are deferred until
  the viewer can make hierarchy visible

This preserves a clean hierarchy while allowing GR modules to expose the maths
they depend on.

## Semantic Folding

The desired behaviour is semantic folding, not only visual clustering.

A collapsed module should stand for a meaningful topic area, such as:

- Special Relativity
- Four-vectors and tensors
- Differential geometry
- Curvature
- Einstein field equations
- Schwarzschild geometry
- Cosmology

When collapsed, the module appears as a graph object. When expanded, it reveals
its member concepts and internal edges.

Collapsed modules should still participate in the graph. Edges crossing the
module boundary should be summarised rather than lost.

## Fit With Current Viewer Model

The current graph/details integration is a good foundation:

- after startup there is exactly one selected concept
- additional highlighted concepts are determined by the active detail section
- background concepts can be visible or hidden
- the graph refits to selected plus highlighted visible graph objects
- the focus lens explains how the focus set was chosen

With modules, this can extend to:

- selected graph object is either a concept or a module
- highlighted graph objects may be concepts, modules, or both
- background graph objects may be hidden, visible, dimmed, or collapsed
- graph refit targets selected plus highlighted visible objects
- the focus lens reports whether the current view is a concept neighbourhood,
  derivation tree, module overview, expanded module, or collapsed outside
  context

The existing focus lens becomes more important because it can explain why some
areas are expanded while others are represented compactly.

## Module Nodes Should Be Real Knowledge Objects

A collapsed module should not be only a visual aggregate. It should be a
selectable knowledge object with its own details panel content.

A module detail view should probably include:

- short module overview
- what the module is for
- major concepts inside it
- important prerequisites
- important exits to later modules
- internal concept list
- maybe a recommended first path through the module

This makes collapse pedagogically useful rather than just a space-saving
mechanism.

Module-level teaching material should use the same general content model as
concept teaching material. A module may need definitions, orientation,
warnings, study route notes, and references just as a concept does. The first
schema can keep module content in a separate file, but the presentation model
should deliberately mirror concept content blocks.

## Possible Schema Shape

A future schema might add:

```text
modules.csv
  module_id,domain,title,sequence,default_collapsed

module_members.csv
  module_id,concept_id,sequence

module_supports.csv
  module_id,target_type,target_id,role,note

module_content_blocks.csv
  block_id,module_id,sequence,kind,title,body
```

Initial assumptions:

- each concept has one primary module
- each module has one owning domain
- modules are flat in the first version
- cross-domain support is represented through `module_supports.csv`
- secondary membership and arbitrary overlapping fold sets should be deferred
  unless a real need appears
- module IDs should be stable semantic IDs, not display labels
- module `sequence` is for presentation, not necessarily a DAG guarantee

Do not add hidden hierarchy fields before the UI can represent them. A
`parent_module_id` field can be added later if hierarchical modules become a
real viewer feature with breadcrumbs, parent/child module pages, and clear
selection behaviour.

`module_content_blocks.csv` is deliberately separate from
`content_blocks.csv` for a first pass. A later schema could generalise content
blocks to an `owner_type,owner_id` model if that proves worth the migration.

## Viewer Behaviour

The eventual graph behaviour is true semantic folding:

- selecting a collapsed module shows the module detail view
- expanding a module reveals member concepts in place
- collapsing a module replaces visible member concepts with the module node
- selecting a concept inside a collapsed module expands enough context to show
  the selected concept
- search can jump directly to a concept and expand the module path as needed
- concept backlinks and `\cref` navigation should select the target concept,
  expanding containing modules if necessary
- manual expand/collapse controls should live on module nodes or local module
  detail sections, not as a large global checklist

The current `Hide graph`, `All`, and `Focussed` modes should still make sense:

- `Hide graph`: graph hidden, details remain usable
- `All`: show the whole graph, but distant modules may be collapsed
- `Focussed`: expand only enough module/concept context around the selected
  object and active detail section

Before implementing graph folding, the first visible behaviour should be
module-aware selection and highlighting.

In this phase modules are selected outside the graph, for example from a module
list, a domain overview page, a concept masthead module chip, module-aware
search results, or links in another module page. The graph responds to module
selection but does not yet contain selectable module nodes.

Initial graph behaviour:

- the graph still renders concept nodes only
- there are no collapsed module nodes yet
- there are no aggregated module edges yet
- selecting a module from non-graph UI shows the module detail page
- concepts in the selected module are highlighted
- concepts outside the module are dimmed or hidden according to graph mode
- boundary concepts directly connected to module members may be highlighted more
  lightly
- the graph refits to module member concepts plus boundary concepts
- the focus lens reports something like
  `Module overview: member concepts + boundary links`

Graph modes during this initial module-aware phase:

- `Hide graph`: unchanged.
- `All`: show the whole graph; selected module members highlighted and
  non-members dimmed.
- `Focussed`: show selected module members plus immediate boundary concepts;
  hide the rest.

This validates module schema, module details, module selection, search, browser
history, and graph focus semantics before the harder work of graph topology
folding.

## First Graph Folding UI

The first prototype adds manual folding from the currently selected module page.
This is the first step where modules become graph objects, but it should avoid
automatic distant-module folding, persistent fold state, and nested modules
until the basic semantics feel right. Multiple modules may be folded at once,
but each fold/unfold operation is still made locally from that module's detail
page.

The Modules section of the control panel also provides graph-wide actions:

- `Collapse all`: fold every module with members, preserving existing folded
  module positions where already folded
- `Expand all`: unfold every currently folded module, restoring member concepts
  around any moved module-node positions

These actions are convenience operations over the same manual fold state. They
do not change authored module membership and do not imply automatic folding
policy. They are disabled when the graph is hidden, because hidden graph mode is
treated as a display state rather than a folding workspace.

The graph header also provides a `Clear` action that returns the viewer to the
unselected full-graph state: all modules are expanded, all concept nodes and
concrete concept edges are visible, active concept/module selection is cleared,
and the details panel returns to its initial prompt.

The control should be local to the selected module. A module detail page should
offer a small graph-state control in or just below the module masthead, for
example:

```text
Graph: Expanded | Folded
```

This local control keeps folding attached to the object it affects. It should
not become another global checklist in the tools panel.

When the selected module is folded:

- member concept nodes are hidden
- a single module node appears in their place
- the module node is placed at the centre of gravity of its member concepts'
  current graph positions
- internal member-member edges are hidden
- boundary links are represented by aggregate module edges
- selecting the module node selects the module and opens its module detail page
- hovering the module node shows a module preview, analogous to concept hover:
  module title, domain/member count, and overview text where present
- double-clicking the module node expands it in place
- the graph refits to the folded module node plus relevant boundary objects
- the focus lens reports `Folded module`, `member concepts hidden`, and
  `boundary links summarised`

When the selected module is expanded:

- the module node is hidden or removed from the visible graph
- member concept nodes are visible again
- if the module node has been moved, member concepts are placed around the
  module's current position using their stored offsets from the fold-time centre
  of gravity
- internal concept edges are visible according to the current graph mode
- the existing module-aware highlighting behaviour applies

Double-clicking a visible concept node folds that concept's owning module, when
there is one. This is the graph-side counterpart to double-clicking a folded
module node to expand it.

If the user navigates to a concept inside a folded module, for example through
search, a `\cref` link, a backlink, or the module member list, the viewer should
automatically unfold enough context to show that concept and then select the
concept normally. A selected concept should not remain hidden inside a folded
module.

Folding is viewer state, not authored KB state. The KB defines module
membership; the viewer decides whether that module is currently displayed as
member concepts or as one folded graph object.

Folded module visibility follows the graph mode:

- `All`: show all folded module nodes.
- `Focussed`: show only folded module nodes that intersect the selected and
  highlighted focus set, plus the selected module if the selected object is a
  module.
- `Hide graph`: hide all graph objects.

A folded module still owns its folded state when hidden by `Focussed`; switching
back to `All` should reveal it again. Selecting a concept inside a folded module
unfolds only that concept's owning module.

### Module Node Visual Treatment

A folded module node must be visually distinct from a concept node. It should
be larger than a concept node and read as a container or topic area, not as
another concept.

The folded rectangle matches the padded bounding box of its member concepts
and labels in the persistent global layout. Corners have a radius of 18% of
the shorter side. The title fits the available space, capped at 160 graph-space
font units; the member count below it uses a fixed size of 48 graph-space units.
The title already includes the module code,
so no separate domain badge is needed.

Changing a module's footprint never automatically moves it or its neighbours.
Users can zoom out and use the boxes to judge the separation needed, then move
modules manually. Generated fallback anchors use generous spacing; published
layout revision 4 also spreads the previous module centres threefold, with
rigid translations that preserve each module's internal concept arrangement.

Edges retain a minimum screen-space width when zoomed out (1.8 pixels for
module boundary edges, 1.5 for ordinary concept edges). Hover emphasis remains
proportional; zoom changes rendering only, not stored edge styles or layout.

Full graph mode (including a highlighted selection) displays only `REQUIRES`,
`DERIVES_FROM`, and `CONSTRUCTED_FROM`. Filtering happens before module-edge
aggregation, so counts and internal edges follow the same rule. Focussed mode
retains its existing context-dependent relation visibility. The underlying
knowledge graph and relationship details are not filtered.

## Boundary Edge Display

When modules are collapsed, boundary edges need summarising.

Possible display rules:

- if any member concept has an edge to a concept outside the module, show a
  module-level edge
- aggregate parallel boundary edges by relation type
- use relation colour when the aggregate is single-relation
- use a mixed or neutral style when several relation types are represented
- edge hover/click should show the underlying concept edges
- a module-boundary detail panel for a module edge should list the concrete
  concept-level edges it summarises

This would preserve direction and meaning without rendering every hidden edge.

A single black edge should be avoided except as a temporary placeholder because
it hides too much of the relation semantics. A better collapsed-module edge
would carry a compact summary:

```text
Electromagnetic Field -> Foundations

7 concept links
REQUIRES 4
DERIVES_FROM 2
CONSTRUCTED_FROM 1
```

If the aggregate contains one relation type, use that relation colour. If it
contains multiple relation types, use a neutral or mixed style and make the
hover/click detail explain the underlying relation counts.

The module edge data model should include:

- source visible object
- target visible object
- relation counts
- representative display style
- underlying concrete concept-edge IDs or endpoints

The current prototype implements these module edges as a runtime viewer
projection over the concept graph. It does not add module edges to the authored
schema. Module-edge hover shows the compact relation-count summary. Clicking the
module edge opens a module-boundary detail view grouped by relation, listing the
underlying concrete concept edges. If the aggregate represents three or fewer
concrete concept edges, the hover text also lists those concept-level
relationships directly.

## Collapse Policy Options

Several policies are possible:

### Layer-Based Collapse

Use current pedagogical layers as collapsible groups.

Pros:

- minimal schema change
- easy to explain
- quick prototype

Cons:

- layers encode teaching order rather than conceptual modules
- graph analysis suggests current layers are poor natural clusters
- GR will likely need nested thematic structure within and across layers

### Explicit Module Membership

Add authored module data and module membership.

Pros:

- stable and explainable
- can later support nested GR structure if the UI grows to match it
- can have module detail text
- separates pedagogy, layout, and module grouping

Cons:

- schema addition
- authoring discipline required
- needs diagnostics to prevent poor module boundaries

This is the preferred durable route.

For the first data pass, membership may be seeded mechanically from existing
layers. The important point is that the result is written as explicit module
membership and can then be reviewed, edited, and analysed. Runtime folding
should read module membership, not infer modules directly from layers.

### Automatic Community Clustering

Use graph algorithms to detect communities.

Pros:

- little manual authoring
- useful diagnostics

Cons:

- unstable as graph data changes
- pedagogically unreliable
- hard to explain to learners
- may conflict with authored narrative order

This should not be the runtime source of truth, but it is useful for authoring
analysis.

## Relationship To DAG Analysis

Modules need not preserve DAG structure for every edge type.

The concept graph can remain a DAG for selected directed relations while the
contracted module graph becomes cyclic. This happens because thematic clusters
often interleave prerequisite relationships.

Current analysis suggests:

- `{DERIVES_FROM, CONSTRUCTED_FROM}` is a good candidate for strict module-DAG
  diagnostics
- `REQUIRES` is useful for warning about awkward boundaries
- requiring `REQUIRES` to be acyclic at module level can force modules to become
  prerequisite strata rather than clean topics

Therefore module tooling should report:

- quotient DAG status by relation set
- concrete concept edges causing each module cycle
- possible concept moves that remove cycles
- modularity/cohesion scores

But authored module design should retain human judgement.

## UX Principles

Avoid turning module collapse into another large global control panel.

Preferred principles:

- local controls near the object they affect
- module nodes can expand/collapse directly
- module detail pages can offer local internal navigation
- search/navigation automatically expands the necessary path
- the graph should explain its state through the focus lens
- the details pane should make clear whether the selected object is a concept or
  a module

The UI should reinforce that graph and details are two views of the same KB:
modules are graph objects and textual study objects.

Selecting a module changes the current invariant from exactly one selected
concept to exactly one selected graph object:

```text
concept:<concept_id>
module:<module_id>
```

A selected module needs a distinct details masthead, browser-history state,
search result behaviour, focus-lens wording, and graph focus policy. It should
not be squeezed into the selected-concept code path without making the
distinction explicit.

## Implementation Sketch

A cautious implementation path could be:

1. Ensure domain-aware validation and diagnostics are sound.
2. Add schema for authored modules, primary membership, supports, and module
   content blocks.
3. Load modules into the Python KB model without changing the graph topology.
4. Add validation: missing memberships, duplicate memberships, invalid module
   IDs, cross-domain ownership mistakes, invalid supports, and duplicate module
   content blocks.
5. Add authoring diagnostics: module boundary counts and quotient DAG reports.
6. Render module pages in the details panel.
7. Add module selection, search results, browser history, and focus-lens
   wording.
8. Add module-aware graph highlighting while still rendering concept nodes only.
9. Add viewer support for collapsed module nodes.
10. Add expand/collapse interactions and boundary-edge aggregation.
    Prototype status: manual folding, stable fold geometry, and runtime
    aggregate boundary edges are implemented; automatic distant-module folding
    remains deferred.

This order keeps the data model and diagnostics ahead of the complex UI.

## Decisions And Open Questions

Current decisions:

- Use a single flat module layer initially. Add hierarchy only when the viewer
  can represent it visibly.
- Supports are enough for the first version; secondary concept membership is
  deferred.
- Use a separate module content file initially. A later migration can share a
  generic content-block owner model if that proves worthwhile.
- Defer selected-concept-inside-collapsed-module behaviour until true graph
  folding exists. In the initial module-aware highlighting phase there are no
  manually collapsed graph modules.
- Accept whatever persistence behaviour naturally falls out initially; decide
  later whether module collapse state belongs in browser local storage.
- Module graphics or icons are desirable eventually.

Open questions for true graph folding:

- How should collapsed module edge labels abbreviate multiple relation types?
  Multi-colour or "rainbow" edges may be worth exploring, but hover text should
  at least list the underlying `A RELATION B` edges, with fuller explanations in
  the edge details panel.
- What is the right visual language for module nodes, especially when module
  graphics are not yet available?
