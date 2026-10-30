# Viewer behaviour

This describes the implemented viewer. Source contracts live in
[KB schema](kb_schema.md); module representation and saved positions live in
[Modules](modules.md) and [Layout](layout.md). The concise user-facing
introduction is [Viewer quick start](viewer_quick_start.md).

## Core state

Independent controls determine the workspace and graph:

1. **Selection**: always one concept or module.
2. **Context rule**: named or custom relationship traversals and a shared depth.
3. **Graph**: All equally, Context + background, or Context only.
4. **Module representation**: each module folded or expanded.
5. **View**: Both, Graph, or Details; controls pane visibility only.

Selecting an object does not alter the other axes. Changing context
does not fold modules or move the camera. Folding does not change semantic
context. Browser Back and Forward retrace selections, not complete viewer state.
Floating **‹ ›** controls expose the same history without consuming a toolbar row,
including when the graph is hidden. They are bounded to selections made since this
page load, so Back cannot leave the viewer; unavailable directions are disabled.
Native browser history remains unchanged. Guided playback hides these controls;
Explore makes them available again. Tutorial snapshot restoration preserves the
current browser-entry marker independently of the restored selection.

## Starting and navigating

On phone-sized touch screens in landscape, a full-screen notice asks the user
to rotate to portrait. Returning to portrait restores the current view.

The first visit opens the Quick start; dismissal is remembered locally and
**Tools → Quick start** reopens it. Startup selects SR-1 (or the first available
module/concept), with Foundations/one hop, All equally, Both, Frame All, authored
module defaults, layout editing off, and one initial fit. Valid URL selections
override that default; missing/invalid URLs and history entries use the fallback.
Empty-space clicks retain selection, and no Clear action is exposed.

Click graph objects, module lists, search results, or details links to select.
Search covers concept IDs, titles and prose plus module metadata and member
titles. Exact ID/title matches rank first. Concept previews and edge inspection
do not replace the current selection details.

A selected concept inside a folded module is represented by its normal circular
concept face and title inside the module box; the module title and concept count
remain below it. Explicit module selection instead uses a strong outer module
outline. The viewer offers actions to expand the selected concept's module or
all context modules. The `+` at a folded module's top-right corner expands it;
the `−` at the corner of an expanded module boundary folds it. These native
controls, and the module-detail controls, preserve selection.

## Context and display

Named contexts are Connections, Prerequisites, Derivation, Foundations, Uses
and Related. Foundations combines derivation, construction and prerequisite
inputs. Custom context exposes clearly worded
relation/direction checkboxes and can be reopened for editing.
Depth is one hop, two hops or Transitive and applies uniformly to the rule.

In All equally and Context + background, the Context relation set filters edges
across the whole graph. All equally shows every eligible edge in its relation
colour and all nodes in foreground, while retaining a conspicuous selection.
Context + background emphasises the selected context and subdues other nodes and
edges. Direction and depth govern context traversal, not the global edge filter.
Context only includes the context subgraph. Selection never changes Graph mode.
Context counts, module expansion and Fit/Fit++ remain available in All equally.

View chooses Both, Graph or Details. Switching panes preserves camera, splitter,
selection, section opening states and graph mode; it does not fit automatically.
Graph-specific controls disappear in Details-only. Details use authored individual
folding defaults, with no separate reading mode. Global Collapse/Expand sections
is deferred. Pinching or Ctrl/Cmd-wheel over details scales text and graphics
without changing the graph camera.

## Camera and layout

Pan and zoom affect only the camera. Selecting an off-screen object pans only
far enough to reveal its current representation and preserves zoom. The Fit
control explicitly offers Reveal selection, Fit selection, Fit context and Fit
displayed graph. Context, display, folding, details and viewport changes do not
fit or rezoom automatically.

Frame offers Reveal selection, Selection, Context and All. The default is All.
Selection and its context remain available in each graph mode; module folding
changes their representation without changing the selected object.

After **Fit context** frames a selected context in any graph mode, the button becomes **Fit++**. This explicit action contracts the
represented context breadth-first through its graph structure. One-hop nodes
move towards the selection first; each later layer then moves towards a newly
placed parent in the preceding layer. If several shortest routes reach a node,
the closest candidate parent in its new position is used. Movement stops at
another node's clearance zone before the result is fitted. In either whole-graph mode,
background nodes remain fixed. The represented context nodes may then be
dragged to refine the temporary arrangement. The contraction remains
presentation state only: saved and manually edited layouts are unchanged, and
selection, context, scope or module-representation navigation restores the
underlying positions.

Node dragging is disabled during ordinary browsing; a drag attempt explains how
to unlock it. Enable **Tools → Layouts → Edit personal layout** to move nodes and
save their positions locally. This is independent of Graph mode; the hidden graph cannot be dragged. During Fit++, Personal editing is suspended while represented
context nodes are temporarily draggable. Layouts can be exported, reset to the
published layout, or retained
when a newer published revision is detected. Camera state is never persisted.

## Reading and personal work

Concept details contain teaching blocks, graphics, relationships, questions and
references. **Show in graph** in Derived from and Where this is used explicitly
selects Derivation or Uses context respectively; the section's Full-tree choice
sets one-hop or Transitive depth. Details-only changes to Both. Frame becomes Context and the camera fits after
the pane resize; module folding is preserved and Fit++ is not invoked automatically. Modules contain their overview, graphic, member
list, boundary links and declared supports. Mathematical text is rendered with
MathJax.

Each authored teaching block has an unlabelled visual checkbox in its header.
Its blue tick records that the block has been read and remains available when
the block is folded. Read marks can be toggled and persist locally; they do not
currently feed a score or summary. A larger, non-interactive blue tick appears
beside a concept title when all its blocks are marked read, or beside a module
when its own and all member-concept blocks are read. A green title tick appears
when all study questions on a concept—or across a module—are currently correct.

At the foot of every concept, **Next** follows the authored module and member
sequence through SR, MATHS and GR. The final GR concept offers an explicit
**Start again** link to SR-1.1. This changes selection and URL in the normal
way without changing Context, graph extent or module folding.

The graph also shows discreet completion markers by default: blue when all
content blocks on a concept have been read, or when a module's own blocks and
all blocks on its member concepts have been read; green when all questions on a
concept—or across a module's member concepts—are currently correct. **Tools →
Study → Show completion ticks in graph** controls both marker types without
changing the recorded progress.

Use the speech-bubble `+` in a content-block heading, then choose a paragraph,
to add a browser-local note. A filled bubble means the block already has notes
and still adds another. The chosen paragraph highlights and the note is placed
below it; paragraph spaces are not separate targets. Graphics and Study
Questions use their one block-level note position immediately. CSV import and
export preserve stable content anchors;
unresolved notes remain visible as needing placement rather than being moved
speculatively. Notes, Personal layout, study-question attempts and content read
marks belong to the unified personal profile. They remain local by default, can
be downloaded or imported together, and can optionally be synchronised on
connection and automatically after changes through the visible
`PhysicsKG personal data.zip` file in Google Drive.
If Google authorization expires, local work continues safely and a persistent
**Sync paused — reconnect** action opens the Personal data controls and starts
reconnection.
Quick start dismissal remains a browser-local preference and is not synchronised.
