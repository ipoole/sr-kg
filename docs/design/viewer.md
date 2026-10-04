# Viewer behaviour

This describes the implemented viewer. Source contracts live in
[KB schema](kb_schema.md); module representation and saved positions live in
[Modules](modules.md) and [Layout](layout.md). The concise user-facing
introduction is [Viewer quick start](viewer_quick_start.md).

## Core state

Four independent axes determine the graph:

1. **Selection**: no selection, one concept, or one module.
2. **Context rule**: named or custom relationship traversals and a shared depth.
3. **Display scope**: Full graph, Context only, or Hidden.
4. **Module representation**: each module folded or expanded.

Selecting or clearing an object does not alter the other axes. Changing context
does not fold modules or move the camera. Folding does not change semantic
context. Browser Back and Forward retrace selections, not complete viewer state.

## Starting and navigating

The first visit opens the Quick start; dismissal is remembered locally and
**Tools → Quick start** reopens it. Startup has no selection, Foundations at one
hop, Full graph, authored module defaults, layout editing off, and one initial
fit of the displayed graph.

Click graph objects, module lists, search results, or details links to select.
Search covers concept IDs, titles and prose plus module metadata and member
titles. Exact ID/title matches rank first. Concept previews and edge inspection
do not replace the current selection details.

A selected concept inside a folded module is represented by its normal circular
concept face and title inside the module box; the module title and concept count
remain below it. Explicit module selection instead uses a strong outer module
outline. The viewer offers actions to expand the selected concept's module or
all context modules. Double-clicking and module-detail controls fold or expand
modules without changing selection.

## Context and display

Named contexts are Connections, Prerequisites, Derivation, Foundations, Uses
and Related. Foundations combines derivation, construction and prerequisite
inputs. Custom context exposes clearly worded
relation/direction checkboxes and can be reopened for editing.
Depth is one hop, two hops or Transitive and applies uniformly to the rule.

In Full graph, the Context relation set filters edges across the whole graph.
With no selection, every matching edge has its relation colour. With a
selection, matching edges reached in the chosen direction and depth retain
their colours; all other matching edges are light grey. Direction and depth do
not restrict the global edge set. Context only contains just the context
subgraph. Hidden suppresses the graph while retaining selection, context and
module state.

The details selector controls presentation only: Full details, Folded, Core,
Maths, Context, Practice, or Hide details. Scrolling and opening sections update
only details navigation. Reading filters are content filters, not difficulty or
mastery levels. Pinching or using Ctrl/Cmd-wheel over the details pane scales
both its text and its concept or module graphics without changing the graph
camera.

## Camera and layout

Pan and zoom affect only the camera. Selecting an off-screen object pans only
far enough to reveal its current representation and preserves zoom. The Fit
control explicitly offers Reveal selection, Fit selection, Fit context and Fit
displayed graph. Context, display, folding, details and viewport changes do not
fit or rezoom automatically.

After **Fit context** frames a selected Context-only view, the button becomes
**Fit++**. This explicit action moves each visible context node radially towards
the selected concept or folded module until it reaches another node's clearance
zone, then fits the result. The contraction is presentation state only: saved
and manually edited layouts are unchanged, and selection, context, scope or
module-representation navigation restores the underlying positions.

Node dragging is disabled during ordinary browsing; a drag attempt explains how
to unlock it. Enable **Tools → Layouts → Edit layout** to move nodes. Changes are
Temporary by default, remain across viewer-state changes, and are discarded when
editing is turned off or the page reloads. Personal changes are saved locally.
The choice is independent of display scope; Hidden cannot be dragged. Layouts
can be exported, reset to the published layout, or retained
when a newer published revision is detected. Camera state is never persisted.

## Reading and personal work

Concept details contain teaching blocks, graphics, relationships, questions and
references. **Show in graph** in Derived from and Where this is used explicitly
selects Derivation or Uses context respectively; the section's Full-tree choice
sets one-hop or Transitive depth. A hidden graph changes to Context only so the
requested result is visible. Modules contain their overview, graphic, member
list, boundary links and declared supports. Mathematical text is rendered with
MathJax.

Each authored teaching block has an unlabelled visual checkbox in its header.
Its blue tick records that the block has been read and remains available when
the block is folded. Read marks can be toggled and persist locally; they do not
currently feed a score or summary. A larger, non-interactive blue tick appears
beside a concept or module title when all content blocks directly owned by it
are marked read.

Enable **Tools → Notes → Note editing** to add browser-local notes. CSV import
and export preserve stable content anchors; unresolved notes remain visible as
needing placement rather than being moved speculatively. Notes, note-editing
preference, personal layout and Quick start dismissal are local to the browser
profile and origin; they are not cross-device sync. Content read marks and
study-question progress are local in the same way.
