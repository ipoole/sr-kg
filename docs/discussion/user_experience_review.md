# User experience and documentation review

Reviewed 6 September 2026. Recommendations, not accepted implementation policy.

## Perspective and evidence

The primary learner is the owner, studying at roughly Susskind's Theoretical
Minimum level, with an ambition to serve a wider range of abilities. I therefore
prioritise finding explanations, repairing gaps and exploring connections over
a prescribed course or assessment system.

I read the README, all four existing design documents, relevant discussion and
issue notes, viewer controls and implementation, and sampled SR and GR content.
The data contains 111 concepts (47 SR, 55 GR, nine mathematics), 273 edges,
762 concept blocks, 488 questions, 13 modules and 20 declared supports. Every
module currently has one overview block. Only three concept blocks are tagged
`worked_example`; this does not count worked solutions in question answers.

I generated the current viewer and inspected it in Chromium at desktop and
phone widths, including search, reading modes and question disclosure. For
interaction checks I substituted local vis-network assets as the browser test
harness does; this was not an offline test of the distributed page. MathJax
rendered in that session. The unit run passed 569 tests, with 150 opt-in browser
tests skipped. Data validation reported zero errors and 185 editorial warnings.
These observations are an expert walkthrough, not user testing,
a full accessibility audit or verification of every physics argument.

## Overall judgement

The project has a stronger content model than product model. Concepts, modules,
semantic teaching blocks and typed relations form a coherent foundation. The
interface presents many independently evolved controls without an equally clear
account of how someone should use them together.

For the primary learner, the strongest experience is: find a concept, understand
its physical meaning, inspect the mathematical argument, briefly visit a missing
prerequisite, return, and try a question. The map should help answer a question
about the physics at each step. Graph editing and relation configuration deserve
less prominence during ordinary reading.

Keep the authored narrative, inline previews, browser navigation, deterministic
concept graphics, module groupings and distinction between personal work and
source content. These already support serious, self-directed exploration.

The validation warnings include differences between prose cross-references and
graph edges. Decide which connections should appear in both views: not every
incidental mention needs an edge, and not every structural edge needs a prose
link. Review missing pedagogically important connections rather than treating
warning count as a measure of learning quality or adding links mechanically.

## Priorities

### 1. Make lookup reliable and immediately available

**Observed:** Search is folded under Tools. Searching the exact title “Lorentz
transformations” returns 15 matches and initially opens “Inertial frames”.
Matching concepts are sorted by display ID, and the first is selected. Searching
by a known name is therefore less reliable than it should be for study alongside
a book. Search snippets can also expose raw mathematical markup.

**Recommend:** Place search in the main header; rank exact ID/title matches
first, then title matches, then body matches. Make broader results available
without unexpectedly opening an incidental mention. Keep modules in the same
search, with their type clear. Start with predictable literal search before
considering anything more elaborate.

**Check:** Typing a known concept title opens that concept; a broad phrase offers
understandable choices and a short readable indication of why each matched.

Evidence: `matchingSearchIds`, `searchFieldsForConcept` and `kgSearch` in
[viewer.js](../../srkg/viewer_assets/viewer.js).

### 2. Give reading modes a defensible learning purpose

**Observed:** Core retains derivations but excludes warnings and conventions.
Maths omits definitions and construction blocks. Context contains warnings and
multiple-choice questions but omits intuition. These are type filters, not
reliable levels of support. In the Lorentz page, Maths omits the standard boost
setup while retaining the boost result. All current module prose disappears in
Maths, Context and Practice because it is tagged overview.

**Recommend:** First describe the existing filters honestly (now documented in
[Viewer behaviour](../design/viewer.md)). Then trial fewer task-oriented choices:
Read, Work through the maths, and Practise. Keep local optional detail available
in each. A mathematical route should retain the setup and assumptions necessary
to read its equations. Avoid equating “less experienced” with “hide mathematics”.
For broader ability support, add specific help such as “remind me what this symbol
means” or “show the missing algebra”, preserving the main narrative.

**Check:** Every filtered page remains intelligible on its own, or explicitly
links to the missing setup. A module never looks like it has lost its introduction
merely because the previous concept was in Practice mode.

### 3. Repair question references, then strengthen self-testing

**Confirmed defect:** In Lorentz transformations, Maths shows two calculation
questions numbered 1 and 2. Question 2 says “For the same event in q3”. In Full or
Practice, the relevant earlier question is indeed Question 3. Filtering breaks
the reference.

**Recommend now:** Make dependent question prompts self-contained, or preserve
stable labels and prerequisite question context across filtering. Add a focused
regression test when fixing the behaviour.

**Next experiment:** Offer “try first → optional hint → reveal solution → revisit”.
A simple personal “revisit this” marker may be more useful than grading or a
mastery model. Calculation questions should include enough intermediate reasoning
to diagnose a mistake. The existing answer disclosure is a good base, but does
not currently capture attempts, feedback or progress.

Evidence: `filteredStudyQuestions` and the `index + 1` question labels in
[viewer.js](../../srkg/viewer_assets/viewer.js), plus
[study_questions.csv](../../data/study_questions.csv).

### 4. Make the graph explain itself in physics language

**Observed:** The lens is active even when its controls are hidden. Auto changes
context as the reader changes sections; Focussed can refit accordingly. Manual
exposes 11 relation/direction choices for the current six relations, each with a
depth choice. “Full graph” still filters the background.

“Where this is used” lists several incoming relation groups, but its automatic
focus follows only derivation links. Also, the “Components” lens follows outgoing
`COMPONENT_OF`: on electric field this points to the field tensor, its containing
object. The label suggests the reverse question to a reader. This is a naming
and semantic-consistency concern, not evidence that the stored edge is wrong.

**Recommend:** Offer understandable context presets: prerequisites, derivation,
applications, related ideas. Explain the active context near the selection even
when advanced controls are hidden. Keep Manual as an advanced option. Distinguish
“parts of this” from “this is part of”. Align the relationship text and highlighted
graph, and preserve relation meanings when implementing the accepted construction
extension. Consider an easy way to hold context still while reading.

**Check:** For each relation, a learner can explain why a highlighted neighbour
is present and predict which direction leads to prerequisites.

### 5. Use modules as optional study routes

**Observed:** The initial details pane is mostly empty; the first-use modal is a
feature inventory. Module prose summarises subject coverage, followed by concepts
and technical sections such as “Incoming boundary links” and “Declared supports”.
The underlying support links are useful, but the presentation asks readers to
interpret the graph's organisation themselves.

**Recommend:** Give each module a concise physical question, assumed background,
an optional short route and one check of understanding. Rename support headings
by purpose where possible. Offer entry choices such as “Find something”, “Explore
a topic” and “Continue reading”. For the owner, continuation and lookup should
be at least as easy as starting at the beginning.

A route is an editorial suggestion, not simply a topological ordering: motivation
and useful revisiting do not always follow dependency order. Keep free exploration.
No hierarchical module schema is needed to try this.

### 6. Recover reading space and distinguish content from controls

**Observed:** At desktop width, the floating Tools panel occupies a substantial
part of the graph. The sticky concept header and open contents list occupy much
of the reading pane on the Lorentz page. “FULL” remains visible in Maths mode
because it is a now-removed concept badge. At a fresh narrow viewport, the graph sits
above the text; opening Tools creates a large overlay. The layout does adapt,
but a small display still makes reading compete with controls and graph space.

**Recommend:** Use a compact contents control with a clear current-section label;
remove the obsolete concept badge. On narrow screens, trial
Read/Map switching with reading first. Provide explicit expand/fold controls as
well as double-click gestures. Keep graph adjustment available without making it
the dominant interaction in a reading session.

**Check:** Inspect long equations, text enlargement, keyboard-only concept lookup,
answer reveal and return navigation. The current text-based navigation provides
a useful alternative to the canvas, but this review does not establish full
keyboard or screen-reader accessibility.

### 7. Make personal study durable

**Observed:** Notes and global layouts persist locally. Notes attach to section
titles and text-block positions rather than stable authored block IDs. A renamed
section or changed paragraph structure can affect where an existing note appears.
Layout revision mismatches show a warning under Tools but apply old positions
immediately. There is no saved reading-session or revisit list.

**Recommend:** Before expanding personal-study features, define how notes survive
content updates and how unmatched notes are surfaced. Prefer stable block IDs
with a fallback for existing notes. Add a lightweight bookmark/revisit list and
resume position if everyday use warrants them. Make export easy to discover.
Keep cloud synchronisation deferred until there is a concrete need.

### 8. Make exploration enjoyable through the physics

The graphics, conceptual traps and links already provide curiosity and surprise.
Build on those rather than introducing points or streaks by default. Pilot one
short exploration, for example: “Change the frame: what changes, and what stays
invariant?” Ask for a prediction, reveal an explanation, and offer a related
concept or calculation. A later interactive diagram could vary boost speed,
but first test whether the authored sequence is satisfying using existing blocks,
links and questions.

Likewise, a path from free fall to geodesics can turn an intimidating dependency
map into a physical question. Judge enjoyment by whether the learner wants to
follow the next connection and can explain what they discovered.

## Documentation audit and edits

| Document | Assessment and action |
| --- | --- |
| README | Accurate GR count, but little learner orientation and understated runtime dependencies. Added audience, current coverage, a short study entry point and explicit CDN/relative-asset dependencies. |
| Architecture | Broadly matches the implementation. Corrected runtime dependencies and added the limitation of note anchors. Linked learner-facing behaviour rather than expanding the architecture into a manual. |
| Modules | The Full graph edge-policy paragraph omitted lens overrides; Focussed wording omitted Manual control and module selection. Corrected these. The ownership and folding contracts remain useful. |
| Layout | The claimed required keep/reset decision was stronger than implementation. Corrected it to an immediately applied override plus non-blocking warning. Other persistence distinctions remain useful. |
| KB schema | Appropriate reference detail, not generally too verbose. Shortened the duplicated authoring-document itinerary and removed migration-history phrasing. Linked question behaviour to its new primary home. No schema changes proposed in this editing pass. |
| Viewer behaviour (new) | Filled the missing current-state account of search, reading modes, practice, navigation and personal work. Makes limitations explicit without presenting recommendations as implemented features. |

The main documentation problem was missing learner-facing intent, rather than
excessive length. Keep the schema detailed, architecture short, and user behaviour
in one primary document. Future ideas should stay in discussion until adopted.
The older adaptive-pedagogy discussion is clearly marked deferred; do not treat
its fine-grained graph as a prerequisite for the improvements above.

## Suggested sequence and open decisions

1. Fix exact-title search and filtered question references; clarify ambiguous
   relation labels.
2. Trial improved reading controls and one module route on SR-1. Check both a
   familiar concept and a topic where the owner needs a refresher.
3. Use that experience to decide on resume/revisit support, richer worked examples
   and one interactive physics exploration. Expand across modules after the pilot.

Two decisions would sharpen the next pass: is the most frequent session looking
up material while reading a book, or exploring within the app itself? And should
phone/tablet reading be a first-class target, or is desktop the priority? Neither
needs to delay the confirmed fixes or the documentation corrections.
