# Viewer behaviour

This describes the current interface, not a proposed learning system. Source
contracts live in [KB schema](kb_schema.md); graph representation and saved
positions live in [Modules](modules.md) and [Layout](layout.md).

## Starting and navigating

The first visit opens a Features dialog. Dismissing it is remembered locally;
**Tools → Features** reopens it. The initial details pane invites selection of a
concept or module. The current dataset initially folds all modules.

Select a module to read its overview, concept list, boundary links and declared
supports. Expand it to show its concepts on the graph. Concept pages include
teaching blocks, graphics where available, relationship sections, questions and
references. The `FULL` badge is an authoring status, not a reading-mode or
mastery indicator.

**Tools → Search** matches concept IDs, titles and prose, and module metadata,
overviews and member titles. Concept results use display order, not relevance
ranking. Find opens the first matching concept, or a module if no concept
matches. Search is not a question, reference or personal-note search.

Concept links navigate between pages; previews allow a brief look at linked
material. Browser Back and Forward retrace concept and module selections.
Concept and module URLs have stable-ID hashes. History is not a saved study
session: it does not record question attempts or restore a complete reading state.

## Reading and practice

The Details selector controls visibility and filters content by block kind.
These are content filters, not difficulty levels or prerequisites assessments.
Graphics and relationship sections may remain alongside the filtered prose.

| Mode | Prose shown | Questions shown |
| --- | --- | --- |
| Full details | All kinds, with note-like kinds initially folded | All types |
| Folded | All kinds, with top-level detail sections folded | All types, within the folded section |
| Core | Overview, definition, intuition, explanation, construction, result, decomposition, derivation, example, summary | Short answer |
| Maths | Derivation, derivation step, result, decomposition, worked example | Calculation |
| Context | Misconception, warning, historical note, convention | Multiple choice |
| Practice | Example, worked example, derivation step, result, summary | All types |

Practice opens the questions section. Answers are individually revealed; there
is no answer entry, automatic marking, attempt history or mastery tracking.
Questions are numbered after filtering, so authored references such as “q3”
can become misleading. Modules use the same prose filters but have no module
question collection; the current module overviews disappear in Maths, Context
and Practice modes while their navigation sections remain.

The contents list jumps within the current page. On wide screens it starts open;
on narrow screens it starts closed. Dragging the divider changes pane sizes.
Hide graph or Hide details gives the other view more space.

## Graph context

Graph offers Full graph, Focussed and Hide graph. Full graph retains a structural
background; Focussed hides unrelated objects. Show lens reveals the context
controls; hiding the lens panel does not disable its effect.

Auto follows the active detail section, including changes while scrolling.
Manual selects relation directions and one-hop or tree traversals, retaining
those choices across concept selection. Its controls use stored edge direction:
for example, outgoing `REQUIRES` links lead to prerequisites.

Current derivation and usage trees traverse `DERIVES_FROM` only. The text under
“Where this is used” also groups other incoming relations, so that section's
text and automatic graph context do not have identical scope. See
[open issues](../issues.md) for the accepted construction-traversal extension.

## Personal work

Enable **Tools → Notes → Note editing** to add notes at supported locations in
concept or module content. Notes save in this browser and can be exported and
imported as CSV. They do not alter the knowledge base. Note placement depends
on section titles and local text-block positions; it is not guaranteed to
survive editorial restructuring unchanged.

Global graph edits are saved locally, whereas Focussed drags are temporary.
See [Layout](layout.md) for reset, export and published-revision handling.
Notes, note-editing preference and splash dismissal are also stored locally.
Browser profile and origin affect availability; this is not cross-device sync.
