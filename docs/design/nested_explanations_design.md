# Nested explanations: graph-aligned reading trees

Revised 9 November 2026 after review of the Maths prototype.

**Status:** this document records the agreed direction and explicitly identifies
open choices. It supersedes the earlier assumption that block borrowing and
concept dependencies could remain loosely related. It does not change the
runtime, schema or authored data by itself.

The current v4.6.8 preview implements shared blocks, statements, recursive
clarifications, canonical reading ticks and personal notes across all Maths
concepts. Its arbitrary cross-concept borrowing and locally retitled disclosures
do **not** yet enforce the graph/tree contract below. The three standard block
roles, Definition previews and new restrictions on borrowing are also design
directions, not claims about the current viewer. The
[current schema](nested_explanations_schema.md) and
[renderer record](nested_explanations_renderer.md) describe that implementation.
The [Maths pilot](../../domains/math/docs/nested_explanations_pilot.md) and
[Tensor Calculus review](../../domains/math/docs/tensor_calculus_teaching_review.md)
record the existing content. Earlier paper prototypes remain historical experiments.

## 1. Purpose and vocabulary

The graph is the learner's map of an argument's foundations. The reading tree
lets the learner inspect those foundations without losing the enclosing argument.
A reader can accept a supporting statement provisionally and continue, or unfold
its support before continuing. Intuition and worked examples matter as well as
formal reasoning.

| Term | Meaning |
| --- | --- |
| Block | An independently owned content unit with a stable ID and semantic type |
| Exposition | The authored argument or teaching text within a Derivation or Explanation block |
| Statement | A short canonical contribution the reader may accept without unfolding its support |
| Dependency branch | A cross-concept reading step justified by an actual concept edge |
| Block inclusion | Reuse of another owned block; same-concept inclusion adds no graph hop |
| Local clarification | Content authored inside its enclosing block, such as Algebra or Why exactly?; it may itself contain clarifications |
| Edge justification | Why the source concept uses the target concept in this argument |
| Occurrence | One appearance of a canonical source within a particular reading path |

A block's title identifies it; its statement expresses its contribution; its body
explains that contribution. Statements stay as short as reasonably possible,
retaining essential assumptions. They are explicitly authored, not extracted from
the first sentence or silently adapted by notation substitution.

## 2. Standard concept blocks and reading profiles

**Agreed direction:** each concept provides Definition, Derivation and Explanation
blocks, alongside optional supporting material such as intuition, examples,
graphics and historical notes.

| Standard block | Purpose |
| --- | --- |
| Definition | What the concept means; canonical content for ordinary concept-reference previews |
| Derivation | Succinct derivation/construction route for a reader reasonably familiar with the subject, including its starting assumptions |
| Explanation | A more supportive exposition for a less experienced reader, with motivation, interpretation, examples and clarification |

A primitive concept, definition or postulate can be a terminal foundation. Its
Derivation must honestly identify that status rather than invent a proof. The
precise presentation of such endpoints and migration of seed content remain to
be designed. Three standard roles do not require three long blocks.

| Reading profile | Outgoing dependency edges | Normal continuation at a supporting concept |
| --- | --- | --- |
| Derivation | `DERIVES_FROM`, `CONSTRUCTED_FROM` | Its Derivation exposition |
| Explanation | Those two plus `REQUIRES` — the Foundations set | Its Explanation exposition |

The supporting Definition can establish what is being accepted at the transition.
Other blocks supply material inside the relevant concept's exposition.

Explanation is **not** generated merely by adding prerequisite branches to
Derivation. Even when both profiles traverse exactly the same edges, their
expositions may differ substantially: equations and assumptions in one;
interpretation, examples and intermediate reasoning in the other. Sharing content
is available where useful, not mandatory sentence-by-sentence reuse.

Only Derivation and Explanation blocks make inclusions of other owned blocks,
local or cross-concept. Other block types do not call owned blocks. However,
**any block may contain locally authored folded clarifications, recursively**.
The restriction on owned-block calls also applies inside those clarifications.
This distinction permits a Definition to explain a subtle phrase locally without
turning it into a second dependency-tree entry point.

## 3. One dependency structure, two presentations

**Agreed contract:** the concept graph defines the reading tree. Exposition and
edges are authored together; their agreement must be checked by construction.

1. Every cross-concept dependency branch realises an actual graph edge permitted
   by the chosen reading profile.
2. Every eligible graph dependency has an explanatory realisation available
   through that profile's entry point. Arbitrary individual blocks need not each
   repeat the entire concept's support structure.
3. Same-concept block inclusions and local clarifications add no concept hop.
4. Multiple occurrences of one source remain one concept on the map.
5. Ordinary cross-references are not counted as dependency-tree branches.

For a given root, profile and graph depth, the tree's **available cross-concept
branches**, projected onto concept nodes and edges, must match the corresponding
Context subgraph. The learner need not open every available branch. The subset
actually investigated can be highlighted later without redefining Context.

Use the existing graph traversal's node **and edge** sets. Do not independently
reimplement hops as disclosure nesting or branch length: shared descendants can
have several routes and different path lengths from the root.

The graph determines available supports. Authors select the supporting blocks,
place the transitions in the argument and order them readably. A missing edge or
missing explanatory realisation is an authoring diagnostic, not an invitation to
silently add edges or manufacture prose. A development-only list of otherwise
unplaced supports could expose gaps; whether to retain such a fallback is open.

### Dependency hierarchy

`REQUIRES` is the broad learning-dependency relation. `DERIVES_FROM` and
`CONSTRUCTED_FROM` are more specific forms and imply it. Store the strongest
applicable dependency description rather than redundant copies within this
family. The implication concerns the argument or construction presented, not
every conceivable approach to the concept.

Foundations already traverses the inclusive family. The current Prerequisites
preset follows only explicit `REQUIRES`; bringing it into line with inclusive
prerequisite semantics is future implementation work.

`COMPONENT_OF`, `INSTANCE_OF` and `RELATED` do not automatically imply a learning
prerequisite. Their role in explanatory traversal is unresolved; initially they
remain outside these two profiles. A prerequisite and a taxonomic relationship
are independent assertions, so the strongest-edge rule does not settle whether
parallel edges from different families should be retained.

### Intermediate concepts and alternatives

Do not bypass a graph path simply because a deeper block is convenient to borrow.
Preserve meaningful intermediate concepts, or review the graph and exposition
together. Transitive pruning must not be undone by automatically adding a direct
edge for every borrowed source.

Keep both dependency edges when there are alternative arguments. The exposition
must distinguish **joint supports** from **alternative routes**; it must not imply
that the learner needs every alternative proof. Grouping, wording and eventually
visual styling should make that distinction apparent. Storage and route-selection
semantics are not yet decided. The available map/tree can offer alternatives
without claiming that every displayed edge belongs to one chosen proof.

## 4. How a supporting branch reads

The purpose is: **if you understand and accept this statement, carry on;
otherwise, the folded content explains it.** A heading should not be an enticing
question whose answer the target block does not actually provide.

The conceptual sequence is:

1. Edge justification: why A uses B here.
2. Canonical supporting statement supplied by B's relevant content.
3. A folded, accurately titled explanation of that statement, with attribution.
4. A local bridge back into A's argument where needed.

These are semantic roles, not a requirement to display four separate boxes or
labels. The exact placement of Definition versus a profile-specific statement
at a concept transition still needs a worked prototype.

Preserve the canonical title where possible. A local title variation must still
identify what the explanation explains; contextual purpose belongs primarily in
the connecting prose. Do not retitle a covector Definition as “What must remain
unchanged when we relabel?”: the Definition does not establish coordinate
invariance. “Covectors as linear readouts” accurately describes that support.

The edge-specific note should supply the justification, rather than remain only
hover information. Author it as grammatical, self-contained connecting prose
with compatible notation and assumptions. Do not concatenate arbitrary titles
and sentence fragments. An edge's general justification and a block-specific
application may need distinction; their association with the same edge must
remain explicit. The exact storage contract is open.

### Same-concept inclusions

**Agreed:** calls to other blocks of the same concept should also be folded and
indented. They use the same source, statement, attribution and reading/note
machinery. They remain within the current graph node and consume no hop. The
same principle applies when an exposition includes its own Intuition, Example
or Graphic block. This is distinct from a locally authored clarification, though
both share disclosure rendering.

Cross-concept supporting graphics/examples belong within the corresponding
concept branch, not in an unexplained shortcut across the map.

### Prototype colours

**Required during prototype development:** distinguish both statements and edge
justifications from ordinary exposition, and from each other. Keep statement
text, including mathematics, blue (currently `#1458b0`). Use a distinct text colour
for edge justification; a dark teal such as `#08776e` is a provisional candidate,
not an approved final palette. Apply the distinction consistently to repeated
occurrences. Do not use italics as the primary signal for mathematical text.

Colour is an editorial aid here, not the only means of identifying the roles:
placement, attribution and accessible descriptions must remain meaningful.
Final cosmetic styling, including how to convey “optional support”, remains open.
This document does not implement the new justification colour.

## 5. Graph and reading-tree alignment

**Required outcome:** whenever the graph is presented as the current reading
map, its root Selection and Context edge set must match the reading tree's root
and profile. A later reading-attention highlight identifies the current concept
without moving the root Selection.

**Open interaction choice:** starting a reading tree may explicitly establish
Selection and Context, as Show in graph does. Candidate actions are “Read
derivation” and “Read explanation”, or a Show in graph action attached to those
blocks. Merely opening a block need not be the start command. Exact controls
and when alignment begins are not decided.

Once a tree is active, unfolding within it should retain the root and profile.
Same-concept inclusions retain the highlighted concept; a dependency branch
advances attention to its target. No implicit camera movement, layout change or
module expansion follows merely from opening prose.

If the user changes Selection or Context, the app must not silently leave an
old tree paired with a different map. Options include explicitly reconfiguring
or ending the active reading tree, or asking the user to resume its map. Which
policy is simplest remains open. Uses, Related and arbitrary Custom contexts
cannot silently be treated as foundational derivations.

Graph mode, module representation and camera framing remain distinct controls.
A supporting concept can be represented by its folded module; the map still needs
a clear indication of where reading attention lies. Details-only reading on a
phone remains valid: alignment must not require both panes to be visible.

### Graph depth versus available reading

It is not settled whether graph depth limits the available reading tree or only
the portion currently mapped. Two candidates are:

- Limit cross-concept expansion to the Context subgraph, show a clear boundary
  marker, and offer an explicit action to extend depth in both views.
- Let opening a deeper branch extend the mapped Context depth, with a clear
  indication of that effect, instead of requiring a separate depth-change action.

Both must prevent silent divergence. A boundary concept may retain its statement
and local clarifications without exposing further unmapped dependency branches.
Do not silently omit essential premises without indicating the depth boundary.
Starting depth, automatic versus requested extension, and behaviour when the
user reduces depth while branches are open all remain to be tested.

## 6. Excessive visual depth

**Open:** around six cumulative indentation levels will exhaust useful width,
earlier on phones. This is a presentation problem separate from dependency hops
and from parser/resource limits. Do not truncate a valid argument merely because
its indentation is deep.

Candidate solutions to prototype:

| Approach | Benefit | Cost / question |
| --- | --- | --- |
| Cap cumulative indentation; use path markers or rails beyond the cap | Keeps the enclosing argument on one page | Deep parentage needs another clear cue |
| Focus a deep branch at full available width, with a breadcrumb and Return | Gives equations and prose enough space | Must preserve and restore the enclosing reading state and position |
| Reduce indentation increments with depth/viewport width | Small initial change | Does not solve arbitrary depth on its own |

A plausible first experiment combines a modest indentation cap with an explicit
full-width branch-focus action. This is a proposal, not an implementation decision.
Logical ancestry, attribution, notes, independent fold state and eventual graph
attention must remain correct whichever layout is chosen. Local clarifications
consume visual depth but no concept hops. Never use indentation width to compute
Context depth. Horizontal scrolling of the entire reading tree is not an adequate
phone solution.

## 7. Ordinary cross-references

Definitions provide the canonical content for `\cref` mouseover/preview, with an
equivalent touch/keyboard means of inspection. Inspecting a reference should not
require leaving the enclosing exposition or change root Selection/Context.
Concise Definition authoring and treatment of lengthy Definition clarifications
in previews need review; avoid replacing a definition with an unrelated summary.

**Provisional:** allow ordinary `\cref` references even when no direct graph edge
connects the concepts. They can supply terminology, comparisons or excursions.
They do not automatically assert a `RELATED` edge and are not dependency branches
for tree/map matching. Following a link remains explicit navigation.

The boundary needs authoring discipline: a required premise must not be hidden
in an ordinary cross-reference to evade the dependency model. How strict
validation should be, and whether readers need a visible distinction between
support and excursion links, remain open.

## 8. Pruning block types

**Agreed goal:** reduce the current 17 types. The final vocabulary is **not yet
agreed**, and this document does not remove types or migrate content.

One candidate for discussion is the three core types plus Overview, Intuition,
Example, Graphic and Historical note (eight in total). Under that proposal:

- Worked example could become Example, with an informative title.
- Result, Summary, Construction, Decomposition and Derivation step could become
  appropriately placed Derivation/Explanation content or local clarifications.
- Convention, Warning and Misconception might become explanatory content with
  explicit titles or an appropriate presentation cue.

These are possibilities, not prescribed conversions. Important warnings and
assumptions must remain conspicuous. A reduced type list must still support
useful authoring, previews and navigation, rather than simply move an equally
large taxonomy into another field. Type migration must preserve meaningful
block identities, notes, reading records and tutorial targets; do not mechanically
merge existing blocks merely to reduce the number of type names.

## 9. Sharing, persistence and domain boundaries

Keep one shared renderer, separating semantic role, placement and capabilities.
Native blocks show statement and body directly when opened; being reusable must
not impose an extra native disclosure layer. Folded children stay compact and
opened children retain the established quiet frame styling, subject to later
cosmetic review.

A source is authored once. Each occurrence has independent disclosure state.
Closing a parent retains descendant state for the page visit. Rerenders, note
editing and sync preserve the current tree and reading position. Repeated sources
in sibling branches remain expandable; an active ancestor cycle needs an explicit
return reference instead of unbounded expansion. Do not confuse visiting another
block of the same concept with repeating the same source in a cycle.

Read ticks and notes retain canonical source identity, not occurrence identity.
Named local notes use the enclosing source block and stable slot path. Opening
content never automatically marks it read. Personal content remains private;
notes inside personal notes and persistent/synchronised reading paths are deferred.

Keep old content valid while the new rules are prototyped, without maintaining
parallel renderers. Identify nonconforming legacy content honestly rather than
claiming it satisfies graph/tree matching. Migration, validation severity and new
schema fields require a separate plan preserving existing identities.

A domain-filtered build reads only selected packages. Missing external domains
produce the established warnings and readable unavailable-support boundaries;
never load excluded packages to resolve a reading branch. Map/tree guarantees
must be stated for the loaded edition, with omitted external supports apparent.

## 10. Next design exercise and review questions

The [standalone HTML prototype](../../domains/math/docs/graph_aligned_reading_mockup.html)
and its [review notes](../../domains/math/docs/graph_aligned_reading_review.md)
now make this exercise concrete. They test proposals; they do not implement
the revised schema in the viewer.

Work through Tensor transformation law with its graph beside the exposition.
Under the **current** edges, its transitive Derivation Context reaches Coordinate
transformation, Coordinate chart and Manifold. Foundations additionally reaches
Index notation, Tensor field, Cotangent space and Tangent space. Worldline is not
in those supporting contexts merely because some prose mentions it.

The current direct borrowing of a Cotangent definition is therefore not an
appropriate one-hop Derivation branch. Decide what an experienced reader accepts,
what becomes an ordinary reference, and how the fuller Explanation follows its
actual dependency path. Map every transition to its edge justification and target
blocks. Do not add shortcut edges merely to retain the current prose layout.

Use that exercise to settle:

1. The compact transition layout: edge justification, Definition/profile statement,
   accurate folded title and optional same-concept supporting blocks.
2. Starting a reading tree and keeping Selection/Context aligned after user changes.
3. Depth boundaries and the presentation of deep branches on phones.
4. Joint supports versus alternative routes.
5. The boundary between ordinary references and explanatory dependencies.
6. A genuinely smaller block-type vocabulary and a safe content migration.

Only then revise storage/validation and implementation. The existing preview
remains a useful content/rendering experiment, not evidence that the stronger
semantic contract is already implemented.
