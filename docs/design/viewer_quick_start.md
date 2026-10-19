# Viewer quick start

**Modules** show the overall structure; **concepts** reveal detailed physics.
See [Viewer behaviour](viewer.md) for the full model.

**New:** The user model has been simplified, the UI space optimised for phones,
and rendering and interaction made faster on older or slower devices. Selection,
context, display, module folding and camera behave independently and predictably.

## Start with the map

The viewer opens with modules folded.

- Click a module to read its introduction.
- Use the `+` in a folded module's top-right corner to reveal its concepts; use
  the `−` on an expanded module's boundary to fold it again.
- Use **Search** to find a concept or module.
- **Clear selection** resumes browsing without rearranging the map.

## Choose relationships and surroundings

**Context** filters Full graph relationships and, with a selection, chooses
which relationships are followed:

- **Connections** — every immediate relationship.
- **Prerequisites** — ideas needed beforehand.
- **Derivation** — what the selection is derived or constructed from.
- **Foundations** — derivation, construction and prerequisites together.
- **Uses** — ideas that depend on or use the selection.

Choose one hop, two hops or the complete transitive chain.

**Full graph** retains the background; **Context only** removes it; **Hidden**
gives details more room. With a selection, reached edges are coloured and other
matching edges are grey. Without one, all matching edges are coloured.

A selected concept inside a folded module appears within the module. Use the
offered actions to expand its module or any folded part of its context.

## Move, read and edit

Pan and zoom freely; selection pans only enough to reveal an off-screen item.
Use **Fit** to frame the selection, context or displayed graph. In Full or
Context-only display, fitting a selected context changes the button to
**Fit++**; press it to draw the visible context nodes closer along their graph
connections without changing a saved layout. Navigating away restores their
positions. Pinch or Ctrl/Cmd-wheel over details to magnify its text and graphics
without changing the graph camera.

Details contain explanations, graphics, relationships and questions. A block's
checkbox records a blue read tick; completing every block marks its concept or
module. Use a block's speech-bubble `+`, then choose a paragraph, to add a note;
a filled bubble means notes are already present. **Show in graph** changes
Context. Back and Forward retrace selections.

Dragging is locked while browsing. Enable **Tools → Layouts → Edit personal
layout** to save moved nodes in this browser. After Fit++, represented context
nodes can instead be adjusted temporarily; navigating away restores them.

## Personal data

Personal layouts, notes, study-question attempts and results, and blue reading
ticks are stored together in this browser. **Tools → Personal data** downloads
them as one portable ZIP of readable CSV files. Import that archive in another
browser and choose **Merge** to combine work or **Replace** to restore the
exported snapshot. Optionally sign in with a Google account to synchronise this
data through Google Drive across browsers and devices. None of these actions
changes authored graph content.

## Study — NEW

Open a concept's **Study Questions** block to answer questions. Answers appear
after an attempt or **I don't know**. Automatic questions mark your choice; for free text, compare the
model answer and mark yourself. Green ticks and red crosses record the latest
result. **Tools → Study** lists attempts and links to each question. Progress is
stored locally and is included in the Personal data archive. By default the
graph shows discreet blue reading-complete and green questions-complete ticks
on concepts and folded modules; one **Tools → Study** option hides both.

## Content status

Covers Special Relativity and General Relativity.

**Manifolds and Coordinates exposition enhanced with motivating example — NEW.**

**Enhanced historical context — NEW:** selected concepts now explain how key
ideas developed, who contributed, and how their physical meaning changed.
