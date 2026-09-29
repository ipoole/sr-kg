# Revised viewer UI model

Status: implemented.

This document specifies the simplified graph-viewer interaction model. Terms
have their precise meanings from [Viewer state terminology](viewer_terminology.md).
The [quick start](viewer_quick_start.md) is the user-facing introduction;
[Viewer behaviour](viewer.md) describes the running interface in more detail.

## Design principles

The viewer must make a large graph navigable without drawing every concept and
edge indiscriminately. Modules provide the high-level view: the wood rather than
the trees. Context rules select a purposeful relation set across Full graph and
expose the reachable subset around a selection.

The primary state axes are independent:

1. **Selection**: no selection, one concept, or one module.
2. **Context rule**: relation set, direction, and depth.
3. **Display scope**: Full graph, Context only, or Graph hidden.
4. **Module representation**: each module folded or expanded.

A control changes only the state named by that control. Any combined transition
must be explicitly labelled. Layout, camera, viewport, details mode, active
section, and inspection are supporting state, not aliases for the four axes.

## Exposed controls

The global header contains **Tools**, **Search**, the selection title, the
**Details** selector, and **Clear selection**.

The graph pane has a persistent toolbar:

```text
Display: [Full graph | Context only | Hidden]
Context: [Foundations v]   Depth: [1 hop v]   [Fit v]
```

Below it, a compact summary states the selection, complete context rule,
semantic context counts, background state, and any folded modules representing
context concepts. There is no control which merely hides an active context.

### Context presets

| Preset | Traversals |
| --- | --- |
| Connections | Every relation, both directions where directed |
| Prerequisites | Outgoing `REQUIRES` |
| Derivation | Outgoing `DERIVES_FROM` and `CONSTRUCTED_FROM` |
| Foundations | Outgoing `REQUIRES`, `DERIVES_FROM`, and `CONSTRUCTED_FROM` |
| Uses | Incoming `REQUIRES`, `DERIVES_FROM`, and `CONSTRUCTED_FROM` |
| Related | Undirected `RELATED` |
| Custom | User-selected relation and direction combinations |

Depth is **1 hop**, **2 hops**, or **Transitive**. One depth applies to all
traversals in the active rule. Traversal is cycle-safe. A concept is the sole
seed for concept selection; every member concept is a seed for module selection.
The selection and, for a module, all its members are always in the context.

Custom context exposes labelled relation/direction checkboxes plus the shared
depth. It deliberately does not retain the old ability to assign a different
depth to every relation and direction.

### Display scope and background

Full graph contains all concepts, subject to module representation, and every
edge whose relation occurs in the active Context rule. With a selection, edges
reached in the chosen direction and depth retain their relation colours while
the other matching edges are light grey. With no selection, every matching
edge is coloured; direction and depth have no global meaning. Context only
contains the context subgraph. Graph hidden contains no graph objects but
preserves the other state.

With no selection the context is empty. Full graph still shows its background;
Context only explains that a selection is required rather than silently
changing scope.

### Selection

Graph objects, search results, details links, module lists, and browser history
all use one selection transition. It changes selection, main details, context
result, active section, URL/history, and clears inspection. It preserves the
context rule, display scope, module representation, layout, camera zoom, and
details mode. If necessary it pans just enough to reveal the selected object's
current representation.

**Clear selection** changes only selection, main details, and inspection.

### Module representation

Double-click and explicit module-detail controls fold or expand one module;
Tools retains Fold all and Expand all. These actions do not change semantic
context, selection, display scope, layout, or camera.

Context is computed before folded modules are substituted. Projected context
and background edges remain distinguishable. A selected concept inside a folded
module does not expand it automatically: its circular concept face and title
replace the module artwork while the module footer remains. Explicit module
selection retains the strong outer outline. Actions can expand the selected
concept's module or all context modules. Expanded modules retain a faint
selectable outline.

### Camera and fit

Panning and zooming change only the camera. The Fit menu offers **Reveal
selection**, **Fit selection**, **Fit context**, and **Fit displayed graph**.
Initial load fits the displayed graph. Selection may minimally reveal an
off-screen object. No other selection, context, scope, folding, details,
viewport, or custom-rule change automatically pans, fits, or rezooms.

### Details and inspection

The existing Details reading filters initially remain. They affect details
presentation, not graph state. Scrolling or opening a section changes only the
active section. Graph-aware sections may offer an explicit complete suggested
context, such as Derivation at one hop.

**Show in graph** in Derived from and Where this is used explicitly selects
Derivation or Uses context; the section's Full-tree choice selects one-hop or
Transitive depth. If the graph is hidden, this action sets Context only so its
result is visible. Concept previews and relationship inspection are temporary
inspection. Edge inspection does not replace selection details; it offers
explicit endpoint selection actions.

### Layout editing

Node dragging is disabled during ordinary browsing. Tools -> Layouts enables
editing with an explicit persistence choice independent of display scope.
Temporary is the default and lasts until editing is disabled or the page reloads;
Personal writes browser-local overrides. A locked drag attempt and every
completed move explain the active consequence in the context bar.

## State transitions

| Action | Changes | Preserves |
| --- | --- | --- |
| Select concept/module | Selection, details, context result, active section; minimal reveal if needed | Context rule, scope, representation, zoom, layout |
| Clear selection | Selection, details, inspection | Context rule, scope, representation, camera, layout |
| Choose context or depth | Context rule and result; Full-graph edge filter | Selection, scope, representation, camera, layout |
| Choose display scope | Displayed-graph membership | Selection, context rule, representation, camera, layout |
| Fold/expand module | Module representation and projected objects | Selection, semantic context, scope, camera, layout |
| Fit or pan/zoom | Camera | All semantic state and layout |
| Scroll details | Active section | Selection and graph state |
| Change Details mode | Details presentation and viewport | Selection and graph state |
| Preview or inspect edge | Inspection | Selection and graph state |
| Layout-edit drag | Temporary overlay or Personal layout, as explicitly chosen | Selection, context rule, scope |
| Browser Back/Forward | Selection | Context rule, scope, representation, camera |

## Startup

The initial state is no selection, Foundations at one hop, Full graph, authored
module defaults (currently all folded), the coloured foundations overview, Full
details, no inspection, and layout editing off. Initial load fits the displayed
graph.

## Accepted simplifications

The following current functionality is deliberately removed in favour of a
smaller and more predictable model:

- automatic context changes while details are scrolled;
- hidden but active Auto or Manual lens state;
- mixed per-relation traversal depths;
- automatic temporary module expansion;
- automatic refitting after context, folding, details, or viewport changes;
- implicit display-dependent temporary node adjustments;
- separate Neighbourhood, Descendants, and Derivation-trace graph modes;
- edge details replacing the selected object's main details;
- Clear selection acting as a wider reset;
- any complete-graph view which draws every authored edge.

These decisions may be revisited after experience with the simpler model.

## Implementation record

1. Recorded this model and established state-observation test helpers.
2. Introduced one viewer state and a pure context engine.
3. Replaced specialised graph rendering with the context, scope/background,
   module-representation and emphasis pipeline.
4. Replaced graph/lens controls with Display, Context, Depth, Fit and a visible
   state summary.
5. Centralised selection and separated details, inspection and representation.
6. Restricted automatic camera action to startup fit and selection reveal.
7. Made personal layout editing explicit and independent of display scope.
8. Removed legacy machinery, updated current documentation and replaced the
   Features splash with the Quick start.

Each stage was committed separately. Regression tests distinguish intentionally
retired behaviour from accidental loss. The generated viewer is rebuilt for
review but excluded from commits.
