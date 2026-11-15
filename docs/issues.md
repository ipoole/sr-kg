# Open Issues

Issue numbers are retained so existing references remain valid.

## 2. Tutorials

2. **Deferred — generated tutorials.** Explore generating prompts from a concept's derivation tree,
   using short block summaries or learning outcomes that could also serve as hover previews.
   Use this work to audit the KB's dependencies, block structure and explanations.
3. **Deferred — tutorial authoring.** Explore recording viewer actions with commentary and an
   Explore/Continue workflow. Unify recording and editing, including insertion of steps;
   validate that changed actions do not invalidate later presentation states.

## 3. Ambitious ideas

1. Create interactive graphic models with adjustable parameters, e.g. free fall near a black hole.
2. Add a history-of-science view, where nodes are physicists and edges are influences.
3. Extend the implemented static body figures to interactive models within content
   blocks, with an appropriate folded preview and phone/slow-device behaviour.
4. Enable community sharing of tutorials, layouts and notes.
5. Extend to molecular biology (MolBio/MolBioKB); a possible collaborator is in mind.
   Domain separation is already implemented.
7. **Optional tutorial narration.** Compare recorded/generated audio with device-generated speech
   (minimal download, but variable voices and mathematical pronunciation). Prefer separate audio
   files loaded per card; embedding Base64 audio preserves a single-file viewer but adds roughly
   6.4–12.8 MB per 20 minutes at 32–64 kbps. Consider Play/Pause, optional automatic playback,
   stopping on card changes, offline availability and memory use on the old iPad.
   Ian may record the narration himself.
8. Add a symbols glossary giving each symbol, its name (e.g. Lorentz factor) and a
   definition link. Explore unobtrusive inline links, perhaps dark blue or brown.
9. Offer a dark view mode.

## 4. Misc. Issues

1. Support PhysicsKG as an installable web app. Home Screen launch already works on iPhone and the old iPad;
   personal data survives closing and relaunching. Add app identity/installation guidance, reliable offline caching
   of the viewer and all required libraries/assets, and controlled version updates without interrupting study.
   Verify personal-data continuity, Google sign-in/sync and export/import in standalone mode; offline changes must
   remain safe until sync is available. Test on both devices and retain ordinary browser use. Hosted icons and the
   landing-page installation tip are already implemented.
6. Safeguard personal data in subset-domain viewers (e.g. GR-only). Normal question answers,
   reading ticks and sync preserve unloaded-domain records, but “Reset all study progress” currently
   resets every domain, and saving a Personal layout can delete unloaded-domain layout overrides.
   Scope these operations to loaded domains, preserving other domains through sync; add regression tests.

## 5. Notes enhancement and unification

1. Consider first-class nested authored blocks with stable child IDs, tutorial targets
   and possibly independent reading progress. Existing local clarifications already
   support scoped notes; distinguish this from new independently tracked blocks.
2. Consider recursive personal-content editing. Generated reading trees are now implemented;
   define placement, completion and sync semantics for further personal-content nesting.
   See [Notes and authored content](design/notes_content_unification.md) for the implemented rules and scope.

## 6. Build artifacts, publishing and repository size

Publishing, hosted previews and website source consolidation are complete:
[deployment results](design/artefact_deployment_completion.md).
The sampled historical archive is also complete:
[inventory](published_viewers.csv) and [archive notes](published_viewers.md).

4. Back up the repository and remove historical generated viewer files
   (including former filenames) using `git-filter-repo`. Audit all branches and tags, including preview branches,
   so they do not retain the old objects; preserve the current small legacy redirect. Coordinate the history rewrite
   and force-push explicitly, then reclaim local storage and verify a fresh clone. Commit IDs will change,
   other working copies should be recloned, and old GitHack links may cease to work. GitHub storage reclamation
   depends on its garbage collection. Initial audit found 134 viewer versions totalling 193.5 MiB uncompressed
   (about 71% of reachable blob content); actual compressed savings need measurement.

## 7. Issues prior to release v5.0.0
1. **Done.** On a full size browser the PhysicsKG - an atlas ... title overlap with the Graph control.  Right justify it perhaps?
2. **Deferred.** Keep Context + background as the default graph mode, including Home.
   Reconsider the Overview-to-context journey separately; add no extra action or message now.
3. **Done.** In reading trees, default depth to 3 hops.
4. **Done.** In reading trees, remove "Fold supports" - it's confusing and of little use.
5. **Done.** Remove blue and green colours from statement and edge justification text; change to block default.
6. Add to introductory tutorial a short demo of reading trees.
7. Update the user guide
8. Update Quick start
9. Decide user facing statement of changes for the version history.  Highlights are reading trees, more explanatory text 
   and graphics in content.  What else?
10. Make a bit of a splash about v5.0.0 on the home page.
 
