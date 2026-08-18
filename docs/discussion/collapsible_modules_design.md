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

## Possible Schema Shape

A future schema might add:

```text
modules.csv
  module_id,title,parent_module_id,sequence,description,default_collapsed

module_members.csv
  module_id,concept_id,sequence
```

Initial assumptions:

- each concept has one primary module
- modules may be hierarchical
- secondary membership should be deferred unless a real need appears
- module IDs should be stable semantic IDs, not display labels
- module `sequence` is for presentation, not necessarily a DAG guarantee

The data model should allow nested modules, but the first implementation can
probably support only one level visually if that keeps the feature tractable.

## Viewer Behaviour

Likely behaviours:

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

## Boundary Edge Display

When modules are collapsed, boundary edges need summarising.

Possible display rules:

- if any member concept has an edge to a concept outside the module, show a
  module-level edge
- aggregate parallel boundary edges by relation type
- use relation colour when the aggregate is single-relation
- use a mixed or neutral style when several relation types are represented
- edge hover/click should show the underlying concept edges
- a relationship detail panel for a module edge should list the concrete
  concept-level edges it summarises

This would preserve direction and meaning without rendering every hidden edge.

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
- supports nested GR structure
- can have module detail text
- separates pedagogy, layout, and module grouping

Cons:

- schema addition
- authoring discipline required
- needs diagnostics to prevent poor module boundaries

This is the preferred durable route.

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

## Implementation Sketch

A cautious implementation path could be:

1. Add schema for authored modules and primary membership.
2. Load modules into the Python KB model without changing the viewer.
3. Add validation: missing memberships, duplicate memberships, invalid parent
   modules, module cycles in the parent hierarchy.
4. Add authoring diagnostics: module boundary counts and quotient DAG reports.
5. Render module metadata in a simple non-collapsible details section or edge
   key-style diagnostic view.
6. Add viewer support for collapsed module nodes.
7. Add expand/collapse interactions and boundary-edge aggregation.
8. Integrate module selection with graph focus, search, browser history, and
   the focus lens.

This order keeps the data model and diagnostics ahead of the complex UI.

## Open Questions

- Should modules be hierarchical from the start, or should the first version use
  a single flat module layer?
- Should a concept be allowed in more than one module?
- Should modules have authored prose in a new CSV file, or should module
  details use the same content-block schema as concepts?
- How should collapsed module edge labels abbreviate multiple relation types?
- What should happen when a selected concept is inside a manually collapsed
  module?
- Should module collapse state be persisted in browser local storage?
- Should generated concept graphics eventually have equivalent module graphics
  or icons?
