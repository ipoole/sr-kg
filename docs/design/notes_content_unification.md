# Notes and authored content

## Model

A **content unit** is a titled, foldable piece of content. A **block** is a
unit at the top level; an **explanation** is a nested unit. **Built-in** and
**personal** describe origin; **reading** and **editing** describe presentation
state. Folding is independent of both. “Note” remains the user-facing name for
personal content.

Both origins use one recursive `renderContentUnit` renderer. A unit supplies title,
body, optional children, origin, placement level, open state and capabilities.
`children` recursively use the same renderer; the existing `optional_details`
syntax also produces these units. There is no source-specific nesting limit in
the renderer. Text is escaped and mathematical notation preserved; renderer-owned
HTML slots provide paragraph anchors, editor controls and actions.

One CSS frame defines the accent width (5px), thin surrounding border (1px),
rounding and padding. Folded explanations show only their title, with compact
margins, no padding or border, and coloured titles (brown for personal content).
Open explanations inherit the enclosing text colour, including the title, and
have a thin subdued grey border without a thick accent bar. Explanations have no
background tint in either state.
This state-based exception applies equally to built-in and personal explanations.
Block/explanation level controls margins.
Kind and origin set colours only. Summary/body structure is shared, including
personal reading and editing. Kind marks/labels are optional heading metadata.

Capabilities explicitly allow `edit`, `annotate` and `trackRead`; action slots
name their required capability and the common renderer filters them. Capabilities
are not inferred from origin or inherited from parent units. An optional
explanation written inside personal text retains personal origin but has no
independent editing/annotation/tracking controls.

Current adapters apply these limits: built-in blocks allow annotation and read
tracking, personal records allow editing, and nested macro explanations have no
independent actions. The notes controller retains editor/draft state and supplies
the editor body. Built-in and personal records retain their separate storage
adapters. Future editing of built-in content will need a personal-override
persistence policy, rather than a second presentation system. Personal content
currently never contributes to completion.

Personal notes have `placement: anchor` (the default for existing records) or
`placement: owner`. Anchor notes retain stable block IDs and paragraph context;
owner notes attach directly to a concept/module and appear after its authored
exposition, before relationships/study. Their IDs and timestamps remain stable.
Placement is an optional additive column in notes CSV and personal-data archives;
old archives remain readable. Existing anchors are not reinterpreted as owner notes.

## Reading and editing

Existing notes open in reading mode with a small Edit action. New notes open in
editing mode. Done returns to reading; folding is independent. Delete is available
only in editing. Input is saved locally as typed. Navigation, sync and rerendering
must preserve drafts; sync must preserve the current editor, fold state and scroll.
Presentation state is not part of synchronised personal content.

Read mode supports paragraphs and MathJax inline/display delimiters. Insert maths
inserts an editable example at the current cursor/selection, preserving
surrounding text and leaving the caret after the unselected example. Users enter
literal backslashes, not CSV/JSON string escaping.

Authored optional explanations use the existing recursive `optional_details`
macro. SR-2.5's derivation demonstrates folded chain-rule and algebra details.
Descriptive titles remain; derivation blocks retain a visible role label.

## Scope and later work

Personal content is visually distinct. No notes-on-notes editor is exposed.
Stable identities for nested authored disclosures, separate nested reading ticks,
and generated derivation trees (with depth/cycle limits) are deferred. Sharing a
renderer does not make personal notes part of the published KB or its graph.

## Implementation stages

1. Placement/persistence contract and this design.
2. Shared content-unit presentation and reading/editing separation.
3. Mathematics and editor insertion, including persistence verification.
4. Owner-level notes and navigation.
5. Authored clarification and shared disclosure presentation.
6. Browser/unit verification, documentation and issue cleanup.

## Verification and follow-ups

Release 4.4.0 verification: 700 unit tests and all 341 browser cases passed,
including the final folded/open explanation styling and Quick Start update.
The browser cases ran across three isolated Chromium processes (221.04 seconds),
with no skips.

Regression coverage includes recursive mixed-origin trees, capability filtering,
HTML escaping, MathJax, placement, editor/draft lifecycle, timestamps, archive/CSV
round trips, merge/deletion tombstones and unchanged completion accounting.
Computed styles compare built-in and personal blocks/explanations, including
multiple built-in kinds and folded/expanded states. Bodies/editors add no extra
left rule or indentation.

The full viewer retains 114 concepts and 282 edges. Desktop and 430-pixel phone
layouts are inspected in isolated Chromium profiles; Google sync uses mocked
provider paths, not a live account. Physical iPhone/iPad testing remains user
review.

Portrait guidance uses device orientation where available so opening the phone
keyboard does not falsely block a portrait editor. Derived from and Where this is
used start folded; Full tree updates keep the section open.
