# Nested explanations: shared reader

Stage 3, 8 November 2026. Implemented and exercised on a synthetic teaching
fixture; stage 4 applies it to the real Maths pilot. This implements the
[reviewed design](nested_explanations_design.md) and
[minimum schema](nested_explanations_schema.md), without changing concept IDs,
edges or personal-data storage.

## Data and rendering

Each source body travels in the generated HTML once, verbatim in its existing
concept/module block record. This preserves paragraph-note contexts and avoids
shipping a second parsed copy of the prose. Statements and Graphic locators are
optional fields on those records.

The Python loader normalises and validates sources/references before generation.
The browser's `content_markup.js` adapter reads the same recursive text,
explanation and reference model from the verbatim body. A browser test compares
its parts directly with the Python parser, including nested braces and maths.
This extends the existing browser text parser, needed for personal notes and
question text as well, rather than introducing a separate legacy renderer.
Ordinary text takes a fast path without constructing a content tree.

`shared_explanations.js` indexes native records by source block ID. It supplies
reference resolution, occurrence state and graphic lookup to the common
`content_markup.js` content-unit shell. It has no dependency on graph operations,
personal-data mutation or source-domain names.

## Native and borrowed occurrences

An open native block shows its optional statement, illustration and explanatory
body directly. Existing kind policy controls its initial native fold state.
Native block IDs, note actions and read checkboxes remain unchanged. The statement
is separate from the annotated body, so adding it does not insert a new numbered
paragraph anchor into that body's existing sequence.

A borrowed occurrence shows the source's short statement in the enclosing
argument and a quiet, initially folded question below it. Attribution identifies
the owning concept/module and source block. Opening inserts the explanation
without repeating the statement. The body uses the common disclosure, maths and
graphic machinery. Its heading shares the source block's read control; there
notes use the same source paragraph anchors as on its native page.

Borrowed bodies are **lazy**: closed references do not construct their target's
DOM or recurse through its dependencies. On first opening, that occurrence's body
is rendered and MathJax typesets the new subtree. Subsequent folding hides rather
than destroys it. A parent can therefore be closed and reopened without losing
its children's state. Two branches using one source remain independent.

Locally authored named explanations and legacy optional disclosures use the same
content-unit shell. Named slots give stable page-local reading paths; legacy
slots also include their paragraph position when native note rendering has split
the body into paragraphs.

## Page lifetime and refresh

Occurrence keys follow the schema's JSON path encoding: root source, then local
slots and shared target IDs. DOM IDs are separate, unique within the active page.
The controller resets its reading paths when the owning concept/module changes.
It keeps those paths when the same page is rebuilt, for example after adding a
note. Native disclosure states are also retained on that same-page rebuild.

Restoring a page rebuilds only the branches the user previously opened. A closed
parent still retains descendant state for a later reopening. Stale toggle events
from detached DOM elements are ignored.

These states are transient. They are not exported or synchronised, and opening
an explanation does not mark anything read. Existing notes, native read marks,
question records and sync behaviour use their existing controllers/storage.

## Cycles, unavailable sources and graphics

The active occurrence's source-ancestor chain detects cycles. A back-reference
shows the canonical statement and an **Already explained above** button which
scrolls/focuses the relevant ancestor heading in Details. It changes neither URL
nor graph state. Reusing a source on sibling branches is not a cycle.

An excluded-domain reference retains its authored target label and local question,
with a short unavailable notice. It has no working disclosure and cannot import
an excluded package. Unknown loaded targets remain loader errors.

Graphic units reuse the loaded owner's registered detail SVG/caption. Their
explicit native block replaces the corresponding implicit graphic section,
preventing a duplicate hero image. Legacy graphic-note placement remains available
inside that native presentation, and its note bubble includes those existing
graphic notes. Borrowed graphic occurrences have the same canonical read tick
as their native block, and share the same canonical notes.

Every rendered instance namespaces its SVG IDs and local references, including
accessible title/description links. Shared gradients, glyphs, markers and labels
therefore do not collide when the same picture appears several times. Existing
Details zoom, caption spacing and equation-overflow handling apply to these units.

## Regression coverage and limits

The synthetic diamond fixture covers native direct reading, lazy first expansion,
independent shared branches, local nesting, ancestor cycles, unavailable sources,
module-owned sources, repeated SVG definitions, existing note/read persistence,
same-page rebuilds, navigation reset, keyboard focus, phone width, parser parity
and real MathJax typesetting after opening.

There is no graph reading highlight, automatic navigation, nested completion,
notes within personal notes, notation substitution or persistent learning journey.
The standalone paper prototypes remain review documents; the stage-4 Maths
conversion and preservation record are in the
[domain-owned pilot](../../domains/math/docs/nested_explanations_pilot.md#7-stage-4-implementation-and-preservation-record).

## MATHS-1 extension and shared reading status

All six MATHS-1 concepts now have short canonical statements and optional shared
routes, using the same reader. Manifold, chart, transition/Jacobian and curve
foundations extend the original temperature argument. Statements are blue
(`#1458b0`) in both native and borrowed occurrences, including their mathematics.

A borrowed heading uses the existing source-block read control. Its durable
`data-read-block-id` identifies the source even inside another owner's block.
Changing it updates every rendered copy, native completion and graph markers
through the existing study controller, persistence and sync. Incoming data updates
checkboxes in place without folding disclosures. No per-occurrence personal data
is created. Opening a source does not mark it read. Local authored explanations
still have no separate read record. Source notes are now available within borrowed content.

## Common source rendering

Native and borrowed units use the same source-body and heading-action factories.
Both pass explicit `annotate` and `trackRead` capabilities. The body factory
combines the registered graphic, legacy graphic-note location and the same
paragraph renderer/anchor sequence. Placement affects the outer shell, title,
statement location and lazy loading; it does not select a second text renderer.
Personal-note insertion is controlled by capability rather than a native-only
body implementation. Local disclosures still use the common recursive content
shell and mathematics renderer.

## Personal notes in reading trees

Native and borrowed source occurrences both enable annotation. Notes retain the
canonical concept/module owner, source block ID and paragraph anchor; no reading
occurrence is written into personal data. Existing source notes appear wherever
that source is unfolded, including legacy graphic notes. Creating or deleting a
note restores the current reading tree. Editing updates other visible copies
without replacing the active editor or closing explanations. Only the occurrence
where Edit was invoked contains an editor; occurrence identity is transient DOM
state. Notes stay private and use the existing archive and sync paths.

Named local explanations support the same paragraph renderer and note controls.
Their anchor uses the enclosing source block ID plus the existing `sectionKey`
field, encoded as `explanation:` followed by a JSON array of local slot names.
The path restarts at each borrowed canonical source. Candidate discovery walks
only that source's authored local explanations, never the shared dependency graph.
Removed/renamed slots leave notes needing placement rather than retargeting them.
Anonymous legacy disclosures and notes inside personal notes gain no new scope.
No new personal-data fields or schema version are required.
