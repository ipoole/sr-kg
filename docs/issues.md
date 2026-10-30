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

## 3 Ambitious ideas
1. Create dynamic graphic models, user might adjust parameters.  E.g. free fall near a black hole given initial velocity.
2. Add a history of science view, were nodes are physicists and edges are influences.
3. Graphics (static or dynamic) should not be restricted to one per concept, but be inserted in (or between) content blocks
   wherever they can usefully got a point across.

## 4. Misc. Issues
3. Support PhysicsKG as an installable web app. Home Screen launch already works on iPhone and the old iPad;
   personal data survives closing and relaunching. Add app identity/installation guidance, reliable offline caching
   of the viewer and all required libraries/assets, and controlled version updates without interrupting study.
   Verify personal-data continuity, Google sign-in/sync and export/import in standalone mode; offline changes must
   remain safe until sync is available. Test on both devices and retain ordinary browser use. Hosted icons and the
   landing-page installation tip are already implemented.

## 5. UI Simplifications.
1. DONE — Perhaps the "Show in graph" actions in Derived from, Where used, should also automatically do a fit.  These are already
   shortcuts for several actions.
2. DONE — UI simplification.  On the phone in particular I often need to switch between graph and details views which involves
   two interactions - hide one, show the other.  I also observe that details folded mode is not particularly useful
   (but see item below).  Thus, we could remove the Details pulldown altogether, removed the Hidden option from the Graph
   pulldown and replace with a View: {Graph, Details, Both}.  That's simpler to operate, avoids the possibilty of
   neither view being shown, and is space neutral on the phone.
3. DEFERRED — The lost feature of folded details from above, could be replaced by a "Fold/Unfold all blocks" in the details view,
   though this would require care in placement and wording to avoid confusion with graph folding/expanding.
4. DONE — We currently support the 'no selection' state, and need a "Clear selection" to support it, using valuable space ("Clear")
   on the phone.  In fact I only wanted this state to trigger a special/particular view, where *all* edges (subject to)
   to the Context filter) and all modules/concepts are shown in foreground.  So lets consider disallowing the 'no selection'
   state (a simplification), and adding an explicit option to Graph which means that special state (not sure how to name
   it succinctly).  A further requirement is that there is some initial selection; not sure - module SR-1 perhaps?
5. DONE — Given the above simplifications, we need to consider carefully exactly how the remaining pulldowns
   (Tools, Graph, Context, Depth, Frame, Fit/Fit++) are arranged, named and framed - particularly
   on desktop where we are less constrained, and exactly how they are named.
