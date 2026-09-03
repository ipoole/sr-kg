# Module-Local Layout And Renumbering

This document records the staged design for replacing pedagogical layers with
authored modules. Stage 1 added the deterministic machinery and a reviewable
numbering proposal. Stage 2 connected module geometry to generated fallback
layout without yet changing the complete authored runtime layout.

## Ordering Convention

The structural edge types are `REQUIRES`, `DERIVES_FROM`, and
`CONSTRUCTED_FROM`. Runtime edges point from a more derived concept to a
prerequisite. For ordering, the algorithm reverses these edges so that
fundamental concepts precede concepts built from them.

Within each module, strongly connected concepts are treated as one group and
reported for editorial review. A stable topological walk then prefers the
existing authored member order whenever more than one concept is available.
This produces a pedagogically conservative ordering while still respecting
every acyclic internal structural dependency.

The proposed visible identifier is the module code plus the one-based position
in this order: `SR-X.Y`, `GR-X.Y`, or `MATHS-X.Y`. The corresponding authored
member sequences are `10, 20, 30, ...`. Semantic concept IDs do not change.

The complete proposal is in
`docs/discussion/module_concept_renumbering_proposal.csv`. It is reproducible
with:

```bash
conda run -n sr-kg python tools/propose_module_numbering.py \
  --data-root data \
  --out docs/discussion/module_concept_renumbering_proposal.csv
```

The proposal contains 111 IDs and no within-module structural cycles. Stage 4
applied it to `nodes.csv`, `module_members.csv`, and the graphics catalogue.
The CSV remains as an audit trail from the old display IDs to the new ones.

## Local Layout Convention

Each module is laid out independently as a compact concept island:

- longest-path dependency rank controls vertical placement;
- prerequisites appear below concepts that depend on them;
- authored member order controls left-to-right placement within a rank;
- wide ranks wrap to a configurable maximum number of columns;
- the resulting concept centroid is translated onto the module anchor; and
- non-structural and cross-module edges do not distort the island.

Dependency rank and numbering order are deliberately related but distinct.
Rank gives a clear downward visual flow. The stable topological numbering can
interleave independent concepts where the authored teaching narrative calls
for it.

The generator now resolves layout in this order:

1. generate module anchors from the structural module DAG;
2. override those anchors with any published module anchors;
3. generate missing concept positions as module-local islands around the
   effective anchors; and
4. override those positions with any published concept coordinates.

Module-free library fixtures use a neutral compact-grid fallback. Authored roots
use modules; layer metadata is no longer part of the runtime concept schema or
viewer payload.

Published layout revision 5 rebuilds all 111 concept positions using this local
layout, replacing the older scattered coordinates. Each island is translated
to preserve its previous displayed module-box centre, including circle and
label extents. All 13 module anchors are unchanged. This is a one-off authored
layout update, not runtime reflow; subsequent manual adjustments remain valid.

Revision 6 installs the user's subsequent exported layout without altering its
concept coordinates or module anchors.

## Diagnostics Convention

DAG analysis is now independent of any pedagogical grouping. It reports
cycles, transitively redundant edges, foundations, capstones, and longest
chains for arbitrary directed relation sets.

Module diagnostics contract the three structural relations through authored
membership and check three complementary constraints:

- the module quotient graph remains acyclic;
- a concept does not depend on a later module in the same domain; and
- a concept does not precede one of its prerequisites in its module's member
  order.

Module sequence values are domain-local, so cross-domain edges participate in
the quotient DAG but not in sequence-order warnings. On the current complete
dataset, the combined structural module graph is acyclic and has no module- or
member-order contradictions.

## Phase Completion

The layer-to-module migration, module footprints and reviewed revision 6 layout
are complete. Module counts use a fixed font size; Full graph is restricted to
the three structural relations while Focussed mode keeps its context relations.
Modules are no longer WIP. GR content remains at seed status pending full
authoring and review. Manual edge-filter controls, automatic repacking and
separate persistent Focussed layouts are follow-up work, not release blockers.

The final validation has no errors and retains 205 content-review warnings
(cross-reference/edge mismatches and transitive-redundancy suggestions). These
belong to later authoring review; the reviewed graph is not automatically pruned
to silence them. Structural module diagnostics have no cycles or module/member
ordering contradictions.
