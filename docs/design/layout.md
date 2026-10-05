# Layout

## One global layout

Concepts have absolute graph-space coordinates and modules have persistent
anchors. Camera position, zoom, selection and visibility are separate from
layout.

Moving a concept changes its position without recalculating its module anchor.
Moving a folded module translates its members together. Folding and expansion
preserve coordinates; visible module boxes follow member and label bounds.
There is no automatic repacking or recentering after manual edits.

## Published defaults and generated fallbacks

The published layout is versioned in `data/layout.json`; its file contract is in
the [schema](kb_schema.md#layoutjson). Missing positions are resolved in order:

1. Generate module anchors from the structural module DAG.
2. Apply published anchors.
3. Place missing concepts in compact module-local islands around those anchors.
4. Apply published concept coordinates.

Local placement puts prerequisites below dependent concepts. Dependency rank
sets vertical position; authored member order breaks horizontal ties and wide
ranks wrap. Cross-module and non-structural edges do not distort an island.
Module-free library fixtures use a compact grid. These are deterministic
fallbacks, not a runtime reflow policy.

## Explicit editing

Dragging is disabled during ordinary browsing. **Tools → Layouts → Edit layout**
enables it and visibly states whether changes are Temporary or Personal.
Temporary is the default; its in-memory overlay survives graph-state changes and
is discarded when editing is disabled or the page reloads. Personal moves are
saved as browser-local overrides. This choice is independent of Full graph or
Context-only display; Hidden display cannot be edited. Changing display never
automatically fits the camera.

**Fit++** contraction is separate from both layout modes. It temporarily moves
only the current visible context, writes neither overlay nor saved positions,
and is discarded on navigation.

## Personal persistence and publication

Browser-local overrides save Personal edits relative to the published layout and
survive reload. They form part of the unified [personal-data](personal_data.md)
profile and archive. They exclude camera, selection, display and Temporary changes.
A published-revision mismatch displays a keep-or-reset warning under
**Tools → Layouts**. Existing personal positions are applied immediately;
the warning does not block their use pending a decision.

The layout controls export a complete repository-compatible layout keyed by
stable semantic IDs, or reset personal overrides to the published defaults.
Publishing is a separate repository action: validate the export and update the
published revision when adopting it. Browser editing never writes source files.

## Future plans

Separate layouts for different contexts remain deferred. Automatic repacking
would need an explicit interaction that preserves deliberate edits.
