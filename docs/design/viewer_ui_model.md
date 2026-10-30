# Viewer UI model

Status: implemented, including the [UI simplifications](ui_simplifications_plan.md).
Terms are defined in [Viewer state terminology](viewer_terminology.md).
The [Quick start](viewer_quick_start.md) introduces the controls;
[Viewer behaviour](viewer.md) describes the running interface.

## Independent axes

1. **Selection**: always one concept or module.
2. **Context rule**: relations, directions and a shared depth.
3. **Graph**: All equally, Context + background, or Context only.
4. **Module representation**: each module folded or expanded.
5. **View**: Both, Graph or Details.

Selection never chooses a Graph mode or opens a module. Changing View preserves
selection, context, camera, layout, splitter and reading state. Context and
module-representation changes do not automatically fit. Explicit combined
actions, such as Show in graph, are labelled as actions.

## Controls

The header groups Tools and Search, View, and Graph. Graph-specific controls are
hidden in Details-only. The graph toolbar groups Context/Depth and Frame/Fit.
Its compact summary counts semantic context concepts; Expand context reveals
folded modules representing those concepts.

| Context | Traversals |
| --- | --- |
| Connections | Every relation, both directions where directed |
| Prerequisites | Outgoing `REQUIRES` |
| Derivation | Outgoing `DERIVES_FROM` and `CONSTRUCTED_FROM` |
| Foundations | Outgoing `REQUIRES`, `DERIVES_FROM`, `CONSTRUCTED_FROM` |
| Uses | Incoming `REQUIRES`, `DERIVES_FROM`, `CONSTRUCTED_FROM` |
| Related | Undirected `RELATED` |
| Custom | Explicit relation/direction choices |

Depth is one hop, two hops or Transitive. Traversal is cycle-safe. A concept
selection supplies one seed; a module selection supplies every member concept.
The selection and a selected module's members are always in the context.

In both whole-graph modes, the Context relation set filters eligible edges
across the whole graph. Direction and depth determine the context, rather than
restricting that global edge set. All equally puts all eligible objects in
foreground, with coloured edges. Context + background emphasises the context
and subdues the rest. Context only excludes the background. Context counts,
expansion and Fit context remain meaningful in every mode.

## Selection and representation

Graph objects, search, details links and history share one selection transition.
It updates details, context, URL/history and active section, clears inspection,
and restores any temporary Fit++ arrangement. It preserves View, Graph, Context
rule, folding, saved layout and camera zoom. If necessary, it minimally pans to
reveal the selected object's representation. Empty-space clicks retain selection;
there is no Clear action.

Module corner buttons, module-detail controls and Tools fold or expand modules.
Semantic context is computed before folded-module substitution. A selected
concept inside a folded module keeps its circular concept face and title within
the module; module selection instead thickens the module boundary. Expanded
modules retain a faint selectable outline. Folding changes representation,
without changing selection or semantic context.

## Camera, details and layout

Frame offers Reveal selection, Selection, Context and All. Fit changes the
camera, never the authored or Personal layout. Fit context arms Fit++ in any
Graph mode. The second press contracts represented context nodes breadth-first,
keeping the selection anchor fixed and leaving collision clearance. Where
several shortest routes reach a node, the closest newly placed parent is used.
Only those context nodes become temporarily draggable. Background nodes and
saved layouts remain fixed; navigation discards the temporary arrangement.

Details use authored individual section folds. Opening or scrolling sections
does not change the graph. A separate Folded reading mode is retired; global
Collapse/Expand sections remains deferred.

Show in graph in Derived from or Where this is used explicitly sets Derivation
or Uses and the section's one-hop/Full-tree depth. It changes Details-only to
Both, sets Frame Context and fits after the panes resize. It preserves Graph
mode, selection and module folding, and never invokes Fit++ automatically.
Concept previews and edge inspection are temporary inspection, with explicit
endpoint selection actions; they do not replace the main selection details.

Ordinary browsing locks dragging. Tools → Layouts enables Personal editing,
which saves browser-local positions. Fit++ suspends Personal editing while its
context nodes are temporarily draggable, then restores the previous setting.
View changes never initiate layout changes or automatic fitting.

## Startup and history

Startup selects SR-1, otherwise the first available module or concept. A valid
deep link overrides that default; missing/invalid selections use the fallback.
The initial controls are Both, All equally, Foundations/one hop and Frame All,
with authored module defaults and layout editing off. Initial load fits once.
Browser Back/Forward and the viewer history buttons retrace selections, leaving
View, Graph, Context rule and module representation unchanged.

Tutorials explicitly specify View and Graph. Explore/Resume and Exit restore
presentation snapshots, including pane choice, reading state and camera.
Personal data is independent of playback and graph presentation.

## Deliberate simplifications

There is no hidden graph scope, null selection, Clear action, separate reading
mode, automatic lens or details-scroll context change, per-relation depth,
automatic temporary expansion, or implicit refit on folding, pane or context
changes. The graph edge filter always follows the Context relation set.
These choices keep controls predictable while allowing explicit shortcuts.
