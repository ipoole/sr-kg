# Layout Persistence Design

## Core model

- **All mode** is the authoritative layout-editing view.
- **Focussed mode** changes only node visibility and camera framing; it does not automatically move nodes.
- Module collapse/expansion changes representation, not stored coordinates.
- Camera position and zoom are independent of layout.

## Persistent global layout

Concepts and modules have stable positions in one global layout. Manual moves made in All mode update this layout and persist across navigation.

A module has a persistent anchor, initially derived from its members' centroid. Member positions are relative to that anchor. Consequently:

- collapsing and reopening a module restores its contents unchanged;
- moving a collapsed module translates its hidden contents as a group;
- moving an expanded module by a module-level control does likewise;
- moving an individual concept changes its position within the module.

The module anchor is not automatically recalculated after manual editing; recentering should be an explicit command.

## Focussed mode

On entering Focussed mode, the viewer:

1. hides objects outside the focus set;
2. retains the global coordinates of visible objects;
3. fits the camera to the visible subset.

This preserves the user's spatial context. Manual concept moves are allowed in
Focussed mode as temporary adjustments to the current rendered view. A discreet
warning distinguishes them from global layout editing. Temporary moves of both
concepts and folded modules are discarded when the view is rebuilt or left and
never alter the global layout or module anchors. Persisting or publishing
separate focused-view layouts is outside the initial implementation.

## Module folding and navigation

Maintain separate **preferred** and **effective** module states. A user's manual collapsed/expanded choice is preferred state; navigation may temporarily expand a module to reveal a selected concept. When that requirement ends, the module returns to its preferred state.

## Personal and published persistence

- Browser-local overrides preserve a user's global layout work.
- **Export global layout** writes stable concept/module IDs and layout coordinates—not screen pixels, zoom, camera state, or focused-view adjustments.
- The exported layout can be validated and added to the repository as the generated viewer's new default layout.
- A layout revision should distinguish published defaults and prevent stale browser overrides silently masking a newer default.
- Provide **Reset to published layout** for discarding personal overrides.

Objects absent from the published layout file may fall back to the deterministic generated layout.

## Published file format

The repository default is stored in `data/layout.json`. Schema version 1 uses a
non-empty string `revision`, concept positions keyed by stable semantic concept
ID, and module anchors keyed by stable module ID. Coordinates are graph-space
values rather than screen pixels. The file may be partial: missing concepts use
the deterministic generated layout, and missing module anchors use the resolved
centroid of their members.

Stage 1 loads and validates this file and supplies the resolved complete layout
to the generated viewer without yet changing runtime positioning behaviour.

Stage 2 introduces an authoritative browser-side global layout initialized from
that resolved payload. Normal graph re-rendering restores concept coordinates
from this state rather than from node styling snapshots, and completed drags in
All mode update it. The current compact Focussed-mode coordinates remain a
temporary rendering projection and do not alter the global layout.

Stage 3 removes that compact projection. Focussed and section-driven graph
views now change only visibility, edge filtering, and camera framing while
retaining global coordinates. Node dragging is disabled outside All mode.

Stage 4 makes module anchors persistent and separates preferred folding from
effective representation. Navigation can temporarily expand a preferred-folded
module to reveal a member concept, then restore the preference when that module
is no longer required. Folded-module moves translate members rigidly, individual
concept moves leave the anchor unchanged, and recentering is explicit.

Stage 5 stores browser-local concept and module-anchor overrides in a versioned
record. Only coordinates that differ from the published layout are saved;
camera, zoom, visibility, selection, and focused state are excluded. Overrides
are restored before first render, and a published-revision mismatch is retained
and exposed for an explicit keep-or-reset decision.

Stage 6 adds the `Layouts` control-panel section. It reports published and
personal state, handles stale-revision Keep/Reset choices, exports a stable
repository-compatible complete layout, resets personal overrides, and exposes
explicit recentering when a module is selected in All mode.

Stage 7 is the integration and documentation pass. It verifies the complete
unit and browser suites, reconciles viewer documentation with the authoritative
global-layout model, and records the final Focussed-mode policy: concept and
folded-module moves are temporary and visibly labelled, while published layout,
personal global overrides, and module anchors remain unchanged. Module folding remains marked
work in progress pending a separate review of the authored module set and
concept membership.
