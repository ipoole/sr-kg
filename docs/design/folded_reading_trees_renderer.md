# Folded reading trees: shared viewer implementation

11 November 2026 · stage 3, initially reviewed in a Maths-only build.

The [design](folded_reading_trees_design.md) defines the contract; the
[schema record](folded_reading_trees_schema.md) describes the optional statement
field and existing local/legacy syntax. Canonical authored CSV remains the source.
The standalone paper is retained as a design experiment, not a second viewer.

## Shared block rendering

`viewer.js:renderOwnerContentBlock` adapts an owned block or a tree occurrence
into `content_markup.js:renderContentUnit`. Title, kind, statement and actions
stay visible in the folded summary; the body starts folded. Missing statements
produce no empty placeholder and are never inferred from body text. Kind tints
apply to the whole box. Local clarifications retain smaller, quiet headings.

Both placements use `shared_explanations.js` for the same source body, graphics,
read toggle and note actions. Repeated SVGs have namespaced IDs. Canonical block
IDs remain in read/notes records; occurrence IDs control DOM identity and folding.
The first authored Definition supplies the concept preview.

`content_markup.js` carries reading context through named local clarifications.
Named slots retain canonical local-note scope. A legacy owned-block call within
a generated tree becomes a contribution/source preview, not another recursive
branch. Native legacy sharing remains supported until its authoring migration.
No edges or statements are inferred from those calls.

## Reading-tree controller

`reading_trees.js` owns recipe metadata, independent cards, lazy concept branches,
depth and full-width focus. It receives the actual `computeViewerContext` result;
its available edge IDs exactly match the shared Context algorithm for the loaded
edition. Missing block kinds are skipped and ancestor cycles stop explicitly.

The controller captures open occurrences before a same-page refresh, rebuilds
only previously opened paths, then lets the shared renderer restore block/local
state. Programmatic restoration does not move Reading position or detach sync.
Full-width focus moves the same DOM; note editing can rebuild and restore the
focus path. Changing a tree's depth rebuilds only that tree. A first-level concept
has no full-width action; deeper concepts/local clarifications can offer it.

Each card has Depth, Synchronise graph and Fold supports. Synchronisation starts
off. Enabling it keeps Selection at the root and sets the recipe's Context/depth,
without changing Camera, Graph mode, View, module folds or layout. Only one card
can synchronise. Manual selection/context changes, closing that card or reading
in another unsynchronised tree detach the marker; the graph settings remain.

Reading position follows the last opened/focused concept within the active tree.
It is transient and does not mark content read. A steady amber outer ring is drawn
after graph nodes, separately from selection styling. A folded module represents
an enclosed reading position; its tooltip names the actual concept. No pulsing,
automatic expansion or camera movement is used.

## Compatibility and review

Maths-only generation reads no excluded domain packages and retains the existing
missing-domain warnings. There is no new personal-data storage format. Stable
block IDs and named local slots preserve reading ticks, notes and sync identity.

The small demonstration adds three statements in Tensor transformation law and
classifies its existing higher-order argument and vector/covector discussion as
Derivation and Explanation. Their IDs and body prose are preserved. The rest of
the Maths authoring audit, including removing old block calls, is stage 4.

Focused checks live in `tests/browser/test_reading_trees.py`: graph parity,
folded defaults, missing statements, independent cards, canonical notes/read
ticks through full-width focus, explicit nonspatial synchronisation and detachment.
Legacy sharing and real-Maths MathJax tests remain in their existing files.
