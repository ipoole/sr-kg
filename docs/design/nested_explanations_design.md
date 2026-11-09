# Nested explanations: design for the Maths pilot

Stage 1, 8 November 2026. Reviewed design for the Maths pilot.

Stage 2 now defines the [minimum schema](nested_explanations_schema.md) and its
Python loading/model contracts. Stage 3 implements the [shared reader](nested_explanations_renderer.md)
on synthetic content; stage 4 now applies it to the selected Maths pilot blocks.
The reviewed choices below are accepted. Keep statements as short as
reasonably possible, retaining only essential qualifications.

No runtime or authored-data changes are made by this document. It incorporates
the discussion following the [Field equations paper prototype](nested_explanations_paper_prototype.md)
and [text mock-up](nested_explanations_mockup.html). Where they differ, this
document takes precedence for subsequent work.

The proposed teaching text and source audit are in the domain-owned
[Maths pilot](../../domains/math/docs/nested_explanations_pilot.md).
Read that first to judge the educational experience; use this document to assess
the reusable structure and behaviour. Storage syntax and schema versioning are
stage 2 work, not decided here.

## 1. Purpose and first demonstration

Enable a reader to accept a stated result and continue, or unfold its meaning,
reasoning, example or graphic without leaving the enclosing argument. Different
readers can investigate foundations first or revisit them after seeing their
application. No traversal mode needs to be selected.

The pilot is a real Maths-only build, centred on MATHS-1.6 Cotangent space:
**How does a temperature field measure a direction of motion?** Tangent spaces
and coordinate charts provide reusable supporting content. The terrain story
supplies a continuous motivating setting, not separate unrelated examples.

The first demonstration includes mixed content types, genuinely repeated shared
content, a local clarification nested inside an explanation, a calculation and
a shared graphic. It is not a conversion of all Maths content.

## 2. Agreed content model

A **content unit** has stable identity, an owning concept or module, a short
title, a semantic type and content. A top-level unit is a **block**; a nested unit
is an **explanation**. These are placement terms, not separate implementations.
An explanation may be locally authored or refer to another independently owned
unit. Local children can themselves contain local children or shared references.

A unit intended for borrowing supplies an explicitly authored **statement**:
what the reader can use without opening its explanation. It can contain equations
or essential qualifications. It is not an extracted first sentence or a long
replacement title. Some kinds, such as graphics and history, may use a statement
that describes their contribution rather than asserting a theorem. We will test
the terminology, not require every kind to imitate mathematical prose.

The unit's **explanation** develops the statement. A content unit does not need
to be borrowable merely because it exists. Unconverted blocks need no invented
statement or new disclosure wrapper.

For a Graphic, the explanation includes the graphic, its caption and any needed
qualification. The pilot should wrap an existing registered SVG as addressable
content, not copy its drawing into several blocks. Exact addressing belongs to
the schema stage.

### Native and borrowed presentation

| Situation | Statement | Explanation |
| --- | --- | --- |
| Native block folded | Short title only; no statement-length heading | Hidden |
| Native block open | Included once at the start, where supplied | Visible directly; locally nested clarifications can remain folded |
| Borrowed occurrence folded | Visible in the enclosing prose | Folded below a short, locally appropriate question/title |
| Borrowed occurrence open | Remains visible, without repetition | Visible beneath it, with source attribution |

Opening a native block must not impose another click simply because it is
shareable. Source content is shared; initial presentation depends on placement.
Both presentations use the same content-unit machinery.

Statement previews on hover/focus may be useful later. They are not part of the
first demonstration and cannot become the only means of accessing a statement
on touch devices.

### Grammatical connections

A reference occurrence supplies the **local hook**: why this material is needed
here, and the question inviting expansion. The target supplies its canonical
statement and explanation. A local bridge can follow the inserted material.

Do not generate fluent prose by inserting titles into a universal sentence.
Do not silently tailor a canonical statement by substitution. The Maths draft
uses compatible notation and scopes its statements to the same surface setting;
notation remapping and selectable statement variants are deferred.

### Types and roles

Explanatory paths are heterogeneous. A Derivation may borrow a Definition, use a
Worked example and embed an Intuition or Graphic. The target type describes what
that unit is; the reference's purpose describes its role in this argument.

Retain existing meaningful types where possible, including Historical note;
reserve Context for the viewer's existing context rule. Do not introduce separate
“formal” and “intuition” reading modes. Any initial reference-role vocabulary must
be justified by the pilot rather than made an exhaustive taxonomy in advance.

## 3. Sharing, identity and transient state

Separate **source identity** from **occurrence identity**. A shared unit is
authored once, but each use is a distinct location in an unfolding page. The same
source may appear twice through different branches, or natively and as an
embedded explanation on the same concept page.

Each occurrence has independent disclosure state, including the state of its
children. Closing an ancestor hides the branch but preserves those states for
reopening during the page visit. Reopening a parent must not synchronise its
descendants with a sibling occurrence. Rendering and ordinary sync must not
reset the current reading arrangement or scroll position.

The tree of occurrences is generated from the reusable content network. A source
already on the active ancestor chain is a recursive reference, not an invitation
to expand indefinitely. Show its statement and a return reference instead. A
source already open in a different branch is not a cycle and remains expandable.
The concrete return control, identity format and validation rules need specification
in stage 2. Resource/depth limits are implementation details to resolve before
production use, without imposing a different model at each depth.

No automatic reading marks, new completion rules, bookmarks or
cross-device reading-tree persistence are introduced in the pilot. Existing native
top-level notes, read records and question IDs must remain valid. Borrowed units
show a read checkbox for their canonical source block, shared with its native
page and all other occurrences. They gain no independent completion record or
reading records. Notes now use the canonical source paragraph anchors in both
native and borrowed presentations. Named local explanations use their source
block ID and stable slot path; notes inside personal notes remain deferred.
Do not copy personal records per occurrence or silently migrate their targets.
Existing personal content remains personal; sharing authored units does not
turn personal notes into publicly shared content.

## 4. Interaction contract for the first demonstration

| Action | Result |
| --- | --- |
| Open a native block | Read its statement and explanation together |
| Open a borrowed explanation | Reveal the target's explanation in place; retain its statement and surrounding prose |
| Open a local Algebra / Why exactly? | Reveal the locally authored child using the same disclosure behaviour |
| Open the same source through another branch | Create/use that occurrence's independent open state |
| Close a parent | Hide the branch, retaining descendant state for this page visit |
| Scroll or zoom Details | Ordinary reading; no interpretation of attention or understanding |
| Activate a disclosure by keyboard | Same effects as pointer activation; retain focus on its heading |
| Follow an ordinary concept link or select another graph node | Existing explicit navigation behaviour; a disclosure is not such a link |

Native and borrowed content must support mathematics and accessible disclosures.
Keep folded explanations compact. Avoid excessive cumulative indentation on
phones, and retain the existing quiet folded / thin-bordered open styling.
Expansion must not force an unrelated scroll or camera change. Content can extend
below the viewport; preserve the user's place at the activation point where feasible.

The pilot will use normal view controls, including Details-only on phones. It
must not require simultaneous Graph and Details to make sense.

## 5. Relationship to the concept graph

The existing graph remains usable but **reading highlights are deferred**.
Opening explanations in the pilot does not change Selection, Context rule, Graph
mode, module representation, layout, camera or URL/history. No scroll tracking,
automatic module expansion or new Graph mode is introduced.

Block references identify contributions to particular explanations. Concept edges
are the coarser authored relationships between ideas. A shared graphic or optional
intuition is not automatically a prerequisite. A coordinate-based explanation of
a tangent vector does not establish that tangent space intrinsically requires a
coordinate chart. No concept edges are generated automatically from references.

Keep enough source/occurrence information for later graph integration: the owner
of an explicitly opened explanation could receive a distinct reading highlight
while Selection remains on the root concept. Local explanations retain their
owner; closing the active branch would fall back to its visible ancestor. Folded,
off-screen and excluded graph targets must not cause implicit axis changes.
Those behaviours need a separate implementation and review stage.

## 6. Compatibility and domain boundaries

There is one modified viewer and one common internal content model. Old blocks
should map to it as title/type/body; new statements and references are optional
capabilities. This is not a promise to support two parallel formats indefinitely.
If simple compatibility is impractical, present a concrete mechanical migration
before implementing it, preserving identities and personal data.

Only Maths authored content is revised for the pilot. Shared loader/renderer work
must still generate the unconverted SR and GR collection. Maths-only loading must
not read or import those domains to resolve references.

Within Maths, unknown targets are authoring errors. References to excluded domains
follow the existing missing-domain warning policy and cannot display a statement
that was never loaded. Stage 2 must specify a readable source-side fallback using
the local hook and target label, with no working expansion or hidden cross-domain
lookup. The initial teaching argument contains no external-domain references.
Other existing Maths content does reference SR. A Maths-only build can therefore
still report the expected missing-SR warnings; those do not justify loading SR
or changing unrelated content to silence the diagnostics.

## 7. Stage boundaries and review gate

Stage 1 settled this experience and the teaching draft. Stage 2 defines the
storage representation, identity/reference contracts, normalisation, validation,
cycle handling and compatibility. Stage 3 implements the renderer on synthetic
data. Stage 4 applies the draft to selected Maths content. Stages 5–6 verify and
publish a Maths-only review viewer. The Python source/loading contracts are now
implemented, along with the stage-3 reader and stage-4 Maths content. The pilot
document records actual source IDs and preservation decisions. Broader review
and hosted Maths-only preview publication remain stages 5–6.

The demonstration succeeds if a reader can explain the role of a covector, work
the temperature-rate example, investigate both supporting branches and return
without losing the argument. Shared content must really have one authored source,
not several copies maintained in step. Deepest mathematical exposition is not a
requirement; differentiability, linearity and the chain rule may be explicit
borrowed foundations.

The following review choices were accepted before stage 2:

1. Is the short folded argument useful and honest about its assumptions?
2. Are native blocks directly readable without an extra disclosure layer?
3. Do repeated shared statements remain helpful rather than tiresome?
4. Do the graphic and intuition clarify the same argument without pretending to
   be its proof?
5. Is source attribution sufficient to explain reuse without exposing editorial
   machinery to the learner?

The stage-2 schema wraps an owner's registered detail illustration as a Graphic
unit and uses the local hook to express purpose without a reference-role enum.
Neither requires separate renderers or type-homogeneous traversal paths.
