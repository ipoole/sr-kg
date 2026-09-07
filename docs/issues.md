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

These come from the [user experience review](discussion/user_experience_review.md).
Start with search and question references. Each item describes the required
outcome; broader redesign experiments remain in the review. Add focused
regression coverage for reproduced defects when implementing the fixes.

1. **Rank search results by relevance.** An exact-title search for “Lorentz
transformations” currently opens “Inertial frames”. Rank exact ID/title matches
above partial title matches, then prose matches; use display order for ties.
Apply consistent ranking to concept and module results. Verify that an exact
concept title opens that concept and broad searches retain understandable choices.
2. **Make search visible and its snippets readable.** Move the search entry point
out of the folded Tools section into the main header or an equally discoverable
location. Render or normalise mathematical markup in snippets so results do not
expose raw TeX commands. Preserve the indication of where a match occurred and
check both desktop and narrow layouts.
3. **Keep question references valid after filtering.** In Lorentz transformations,
Maths mode displays Questions 1 and 2, but Question 2 refers to “q3”. Make dependent
prompts self-contained, or preserve stable question labels and access to required
context. Check other cross-question references and verify Full, Maths and Practice
views; changing only this visible number is insufficient if its prerequisite
question can be filtered out.
4. **Preserve essential context in filtered reading views.** Maths omits the
Lorentz standard boost setup while retaining results that use it; Core excludes
warnings and conventions. Keep necessary definitions, setup and assumptions
available inline or through explicit local disclosure/links. Review representative
SR and GR pages in each mode. Do not require a new difficulty taxonomy or a
complete reading-mode redesign to fix these omissions.
5. **Keep module introductions visible across reading modes.** All current module
prose is overview content and disappears in Maths, Context and Practice. Opening
a module from a filtered concept should still show its introduction and navigation.
Verify this without silently losing the learner's preferred concept reading mode.
6. **Reconcile usage text with automatic graph context.** “Where this is used”
lists multiple incoming relation types, while its Auto lens follows only
`DERIVES_FROM`. Make the scope explicit and consistent between the displayed
relationship groups and graph, so readers can tell which links are included.
Coordinate with the accepted `CONSTRUCTED_FROM` traversal extension in section 1;
do not treat every incoming relation as a derivation.
7. **Correct the component-direction label.** The “Components” lens follows
outgoing `COMPONENT_OF`; for electric field it reaches the containing field tensor.
Label this as “Part of” (or equivalent), and reserve “Parts of this” for incoming
component links. Preserve the stored edge meaning and verify both directions
using the electric/magnetic fields and field tensor.
8. **Explain active graph context when lens controls are hidden.** Hiding the lens
panel does not disable it, and Full graph still filters its background. Provide
a compact visible description of the active context and distinguish hiding the
controls from changing that context. Verify that Auto section changes and Manual
rules remain understandable with the panel closed.
9. **Disambiguate authoring status.** The `FULL` badge remains visible in Maths
mode and can be mistaken for the selected reading mode. Explicitly identify it
as an authoring status and give it secondary visual prominence. Check that it
cannot be confused with reading mode, difficulty or learner progress.
10. **Make note anchors resilient to content edits.** Current anchors use section
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

## 4. Documents

1. Rename all documents under `/docs` and their references to use lowercase
filenames consistently.
