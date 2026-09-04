# Layout

## One global layout

Concepts have absolute graph-space coordinates and modules have persistent
anchors. Full graph mode is the global editing view. Camera position, zoom,
selection and visibility are separate from layout.

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

## Focussed views

Focussed mode keeps global coordinates, hides unrelated objects and fits the
camera to the visible context. Concept and folded-module drags are temporary
adjustments, visibly distinguished from global editing. They are discarded when
the view is rebuilt or left and never change saved coordinates or module anchors.

## Personal persistence and publication

Browser-local overrides save global edits relative to the published layout and
survive reload. They exclude camera, selection, visibility and focussed changes.
A published-revision mismatch requires an explicit keep-or-reset decision so an
old personal layout does not silently mask new defaults.

The layout controls export a complete repository-compatible layout keyed by
stable semantic IDs, or reset personal overrides to the published defaults.
Publishing is a separate repository action: validate the export and update the
published revision when adopting it. Browser editing never writes source files.

## Future plans

Separate persistent focussed layouts and their export remain deferred. Automatic
repacking would need an explicit interaction that preserves deliberate edits.
