# Modules

## Authored structure

Modules are stable teaching topics, each owned by one domain. Every concept has
one primary module in that domain. Explicit supports connect modules to useful
concepts or modules without changing ownership. Modules have their own ordered
content and detail pages. File contracts live in the [schema](kb_schema.md).

Membership is authored, not computed by the viewer. Partition analysis helps
review boundaries, but numerical cohesion does not guarantee a good teaching
topic. The adopted SR grouping keeps spacetime, particle mechanics, action,
electromagnetic structure, and field dynamics coherent; GR separates foundational
geometry, connections, curvature, matter equations, and applications.

## Ordering and diagnostics

Structural relations are `REQUIRES`, `DERIVES_FROM`, and `CONSTRUCTED_FROM`.
Edges point from dependent to prerequisite. Fundamental-first numbering reverses
that direction, using a stable topological order with authored member order as
the tie-breaker. Strongly connected concepts are grouped and flagged for review.
Display IDs identify the domain, module and member position; semantic IDs remain
stable when ordering changes.

Diagnostics check the contracted module graph for cycles, same-domain module
sequence against dependencies, and member order against internal prerequisites.
Cross-domain dependencies participate in cycle checks but do not compare domain-
local sequence values. These checks guide editorial review. A direct dependency
can carry meaning even when another path connects the same concepts; transitive
reduction must not silently remove that meaning.

## Folding and navigation

A folded module represents its members as one selectable graph object. Its
page remains accessible; expanding reveals concepts in place. Internal edges
are hidden while folded, and boundary edges retain the underlying concept links.
Double-clicking a folded module expands it. Double-clicking a concept or empty
space within one unambiguous expanded-module footprint folds that module. Global
expand/collapse controls provide the same operations in bulk.

The viewer separates preferred folding from effective representation. Navigation
to a concept temporarily expands its module if necessary; when that requirement
ends, the preferred state can return. Authored defaults initialise preferences.
Selection may be a concept, module, relationship, or nothing.

Folded boxes follow the bounds of their concepts and labels. Folding changes
representation rather than stored coordinates. Movement and persistence follow
the [layout contract](layout.md).

## Boundary edges

The viewer projects concept edges onto visible objects and aggregates links
across folded boundaries. A single relation retains its colour; mixed relations
use a neutral summary. Hover and relationship details expose the concrete links
so folding does not erase their meaning. No separate authored module-edge graph
is required.

Full graph mode shows the three structural relations, filtering before boundary
aggregation. Focussed mode uses section-dependent context relations. This display
policy does not remove relationships from the KB or its detail pages.

## Future plans

Nested modules, overlapping ownership and automatic distant-module folding remain
deferred until a clear teaching need and usable navigation model justify them.
