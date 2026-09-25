# Open Issues

## 1. Concrete fixes for the next implementation round

These remaining fixes come from the
[user experience review](discussion/user_experience_review.md). Original issue
IDs are retained below. Add focused regression coverage for reproduced defects
when implementing the fixes; broader redesign experiments remain in the review.

- **2.8 — Explain active graph context when lens controls are hidden.** Hiding the lens
panel does not disable it, and Full graph still filters its background. Provide
a compact visible description of the active context and distinguish hiding the
controls from changing that context. Verify that Auto section changes and Manual
rules remain understandable with the panel closed.

- **2.10 — Make note anchors resilient to content edits.** Current anchors use section
titles and local text-block positions. Use stable authored block IDs where
available, with backwards-compatible handling of existing stored notes and CSV
imports. Preserve and visibly surface unmatched notes rather than silently
dropping or misplacing them. Verify section renaming, paragraph insertion or
splitting, and import/export of both old and new notes.

## 2. Viewer requests

1. Consider persistent per-focus layouts and their export, separately from the
existing global-layout workflow. Focussed adjustments are currently temporary;
global layout export and publication already work. See [Layout](design/layout.md).
2. Add graphics to modules as icons in the graph and possibly in module details.
This will require space within the module box, perhaps with the icon above smaller
text.
3. Consider recording whether an edge relation belongs in the Full-graph
background in the edge key. The viewer currently hardwires the structural set;
lens-selected foreground edges must continue to override that background filter.
4. When a module is expanded, keep a *faint* grey outline of the module box.
