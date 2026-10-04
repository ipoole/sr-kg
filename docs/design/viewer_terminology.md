# Viewer state terminology

This document defines the vocabulary for analysing and redesigning the viewer.
It is a conceptual model, not a description of every current interaction. The
[viewer behaviour](viewer.md) document remains the account of the implemented
interface.

The main design principle is that each state axis has one purpose. Changing one
axis should not silently or surprisingly change another. Where an interaction
must change several axes, the combined transition should be explicit.

## Primary axes

### Selection

The durable object being studied: one concept, one module, or nothing. Selection
normally determines the main details content, the centre from which context is
calculated, and the URL/history entry. Use **selected concept**, **selected
module**, and **no selection**; do not use *focus* as a synonym.

### Context rule

The semantic question asked about the selection. A complete rule includes:

- one or more relations;
- a direction for each directed relation;
- a depth, such as one hop or transitive;
- any further traversal constraint needed by the rule.

Learner-facing presets such as **Connections**, **Prerequisites**,
**Derivation**, **Foundations**, and **Uses** name complete rules. **Custom
context** may expose relation, direction, and depth directly.

Applying the context rule to the selection produces the **context subgraph**,
comprising **context nodes** and **context edges**. The selection is always part
of its context. A module's normal context may contain its members and boundary
relationships.

### Display scope

Which graph objects are included in the displayed graph, whether or not the
camera currently places them on screen:

- **Full graph** includes the context and a useful background.
- **Context only** excludes the background.
- **Graph hidden** includes no graph objects.

Display scope replaces the spatially ambiguous term *map extent*. It does not
set the camera or determine traversal depth.

### Module representation

Whether a module is **folded**, represented by one module object, or **expanded**,
represented by its concepts. Different modules may have different states.

Folding changes representation, not semantic context. A concept may be in the
context while represented by its folded module. Projected module edges preserve
the underlying context and background relationships. If that concept is
selected, its circular concept face and title appear within the folded module;
this is still concept selection, not module selection.

## Background and visual state

### Full-graph edge filter

In Full graph, the relation set in the Context rule selects eligible edges
across the whole graph. Direction and depth determine the context reached from
a selection, but do not further restrict this global edge set. Full graph need
not mean that every authored edge is drawn.

### Background

Eligible objects which are not in the context. With a selection, background
edges are light grey and background nodes are subdued; with no selection, all
eligible edges retain their relation colours. Background objects do not
contribute to semantic context counts.
If `C` is the context and `B` the background, the displayed graph is:

```text
Full graph   = C ∪ B
Context only = C
Graph hidden = ∅
```

### Emphasis

Visual treatment derived from state, rather than a state called *highlight*.
The principal treatments are:

1. **Selected** — the primary object.
2. **In context** — other context objects.
3. **Background** — surrounding objects retained by Full graph.
4. **Inspected** — a temporary preview or hover target.

## Spatial terms

### Layout

Graph-object positions in graph coordinates. Distinguish **authored layout**,
**personal layout**, and **temporary layout adjustment**. Dragging changes
layout; panning and zooming do not.

### Camera

The centre and zoom scale through which the displayed graph is viewed. The
camera determines which spatial region of the displayed graph falls within the
viewport. It does not determine which objects belong to the displayed graph.

### Viewport

The rectangular screen area available for rendering the graph after accounting
for the window, details pane, controls, and splitter position.

### Fit

An explicit camera operation that chooses a centre and zoom to frame a named set
of displayed objects, such as **Fit selection**, **Fit context**, or **Fit full
graph**. Fit changes only the camera.

After **Fit context** in an eligible Context-only view, **Fit++** is a distinct
explicit presentation action: it temporarily contracts the visible context
around its selected representation and then fits the camera. It changes no
layout and is discarded when the user navigates away.

The distinctions are:

- Display scope: **what is available to see?**
- Camera: **which spatial region are we looking at?**
- Viewport: **how much screen space are we looking through?**

## Reading and transient state

### Details

The durable content belonging to the selection. Selecting a concept normally
shows concept details; selecting a module shows module details.

### Active section

The part of the selected object's details currently being read or explicitly
opened. This is reading state, not graph state. A section may offer a **suggested
context**, but crossing it while scrolling should not silently redefine context.

### Inspection

A temporary look at something other than the selection, such as a concept-link
preview or relationship details. Inspection does not replace the selection or
context. A **preview path** is temporary emphasis connecting the selection to an
inspected concept; it is not part of the context.

## Rendering model

The concepts above form a pipeline:

```text
Knowledge graph
      |
      +-- selection + context rule --> context subgraph
      |
      +-- display scope + context relation set --> displayed graph
      |
      +-- module representation --> display objects
      |
      +-- layout --> positioned scene
      |
      +-- camera + viewport --> on-screen image
```

An object may therefore be:

- in the context but represented by a folded module;
- included in the displayed graph but off-screen;
- excluded by display scope despite having a stored layout position.

Use **included/excluded** for displayed-graph membership, **on-screen/off-screen**
for camera results, and **represented by a folded module** where applicable.
Avoid using *visible* to mean all three.

## Terms to restrict or retire

- Replace **Focussed** with **Context only**.
- Replace **Focus lens** with **Context**, and **Manual lens** with **Custom
  context**.
- Use **selected**, **in context**, **background**, or **inspected** instead of
  the ambiguous **highlighted**.
- Replace **current view** with the specific state meant: display scope, camera,
  details, or displayed graph.
- Use **transitive** rather than **tree** unless the result is genuinely a tree.
- Reserve **Clear selection** for changing selection only. Reserve **Reset** for
  an explicitly defined wider restoration.
