# Open Issues

## 1. Content
1. It is surprising that the Schwarzschild metric has no derivation edges. Other GR concepts may need review.
2. In explanation of tangent and cotangent spaces, I feel a units/dimensional angle is helpful;
   their product needs to form a dimensionless (or at least coordinate-less) quantity.
3. Module MATHS-2 — Tensor Calculus needs more work. There is insufficient explanation to answer some questions.
   Tensor rank needs more explanation, and more examples are needed generally. There is too much emphasis on
   subtleties such as abstract versus component indices and not enough on the basics. Perhaps the module is trying
   to be too general rather than concentrating on the tensor calculus needed in GR. Needs discussion.
4. We should add User Guide, in addition to the current Quick start.   It should be aimed primarily at the human reader,
   but with some concession to an AI agent (with no prior context) which is required to drive PhysicsKG to achieve some
   task.


## 2 Tutorial related
1. DONE — New users (e.g. my wife!) may not appreciate that the tutorial dialogue is not part of the normal content.  Try to
   distinguish it perhaps with a different coloured font.
2. DEFERRED to a later branch — Looking forward to the possibility of automatically generated tutorials - e.g. to explain the derivation tree of a
   given concept, we will need move away from authoring the tutorial prompts explicitly.  We could associate with
   every details block a short sentence summary, or learning outcome.  That could be used in a tutorial prompt and also
   available as mouse-over in normal use.  Needs thought.  Such considerations of automated exposition should drive
   improvements to the KB structure, edge types, block types and their content.  Discuss.
3. DEFERRED to a later branch — Tutorial authoring could be added.  Roughly, "Record tutorial", user make an interaction then enters a prompt, then
   hits next.  At any time they can hit "Explore" to freely experiment with the next step, before hitting "Resume".
   There would also need to be a means of editing a tutorial, which needs careful thought; just editing the prompts is
   easy, but changing an interaction might move to an incompatible state. Ideally, record and edit should be the same
   thing, providing editing allows adding new steps, then record is just edit starting from and empty list.  Discuss.
4. DONE — The Using PhysicsKG tutorial is likely to be launched into directly via a link, so the first card need to explain
   something like "Press Next to step through the tutorial or "Explore from here" temporarily take control". Or
   effectively the same text which usually appears when the tutorial is started via Tools->Tutorial
5. DONE — I have a smart friend, Andrew, who broadly understands SR but has always found the mass=energy thing slippery.
   So I'd like us to make our tutorial a clear and engaging as possible, working on the tutorial *and* content simultaneously,
   editing, adding or splitting content blocks and adjusting edges as necessary.   Then I'll send it to Andrew for his
   review :-).
6. DONE — In a similar manner to 2.5 above, I'd like to add a tutorial and audit content with the goal of explaining time dilation.
7. DONE — The introductory tutorial suffers on the phone because the expanded block (SR 1.1) falls under the tutorial dialogue.
8. DONE — Need a way to directly launch a named tutorial. Each introduction now offers a direct launch link.

## 3 Ambitious ideas
1. Create dynamic graphic models, user might adjust parameters.  E.g. free fall near a black hole given initial velocity.
2. Add a history of science view, were nodes are physicists and edges are influences.
3. Graphics (static or dynamic) should not be restricted to one per concept, but be inserted in (or between) content blocks
   wherever they can usefully got a point across.

## 4. Misc. Issues
1. DONE — The viewer is pretty much un-usable on the phone in landscape orientation; lets just not allow it.
