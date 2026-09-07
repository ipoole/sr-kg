# Open Issues

## 1. Content and implementation

1. Include `CONSTRUCTED_FROM` alongside `DERIVES_FROM` throughout derivation-path
traversal, including ancestry and downstream trees. Preserve relation labels and
check navigation, focus and cycle handling. Current trees use only
`DERIVES_FROM`; this is accepted work, not an open policy question.
2. Add the GR gravitational-waves module and fully author its concepts with
graphics and icons. See the
[General Relativity plan](authoring/general_relativity_concept_plan.md).

## 2. Concrete fixes for the next implementation round

These remaining fixes come from the
[user experience review](discussion/user_experience_review.md). Original issue
IDs are retained below. Add focused regression coverage for reproduced defects
when implementing the fixes; broader redesign experiments remain in the review.

- **2.3 — Keep question references valid after filtering.** In Lorentz transformations,
Maths mode displays Questions 1 and 2, but Question 2 refers to “q3”. Make dependent
prompts self-contained, or preserve stable question labels and access to required
context. Check other cross-question references and verify Full, Maths and Practice
views; changing only this visible number is insufficient if its prerequisite
question can be filtered out.

- **2.4 — Preserve essential context in filtered reading views.** Maths omits the
Lorentz standard boost setup while retaining results that use it; Core excludes
warnings and conventions. Keep necessary definitions, setup and assumptions
available inline or through explicit local disclosure/links. Review representative
SR and GR pages in each mode. Do not require a new difficulty taxonomy or a
complete reading-mode redesign to fix these omissions.

- **2.6 — Reconcile usage text with automatic graph context.** “Where this is used”
lists multiple incoming relation types, while its Auto lens follows only
`DERIVES_FROM`. Make the scope explicit and consistent between the displayed
relationship groups and graph, so readers can tell which links are included.
Coordinate with the accepted `CONSTRUCTED_FROM` traversal extension in section 1;
do not treat every incoming relation as a derivation.

- **2.8 — Explain active graph context when lens controls are hidden.** Hiding the lens
panel does not disable it, and Full graph still filters its background. Provide
a compact visible description of the active context and distinguish hiding the
controls from changing that context. Verify that Auto section changes and Manual
rules remain understandable with the panel closed.

- **2.9 — Disambiguate authoring status.** The `FULL` badge remains visible in Maths
mode and can be mistaken for the selected reading mode. Explicitly identify it
as an authoring status and give it secondary visual prominence. Check that it
cannot be confused with reading mode, difficulty or learner progress.

- **2.10 — Make note anchors resilient to content edits.** Current anchors use section
titles and local text-block positions. Use stable authored block IDs where
available, with backwards-compatible handling of existing stored notes and CSV
imports. Preserve and visibly surface unmatched notes rather than silently
dropping or misplacing them. Verify section renaming, paragraph insertion or
splitting, and import/export of both old and new notes.

## 3. Viewer requests

1. Consider persistent per-focus layouts and their export, separately from the
existing global-layout workflow. Focussed adjustments are currently temporary;
global layout export and publication already work. See [Layout](design/layout.md).
2. Add graphics to modules as icons in the graph and possibly in module details.
This will require space within the module box, perhaps with the icon above smaller
text.
3. Consider recording whether an edge relation belongs in the Full-graph
background in the edge key. The viewer currently hardwires the structural set;
lens-selected foreground edges must continue to override that background filter.
