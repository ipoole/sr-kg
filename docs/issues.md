# Open Issues

Issue numbers are retained so existing references remain valid.

## 1. Content

3. Module MATHS-2 — Tensor Calculus needs more work. There is insufficient explanation to answer some questions.
   Tensor rank needs more explanation, and more examples are needed generally. There is too much emphasis on
   subtleties such as abstract versus component indices and not enough on the basics. Perhaps the module is trying
   to be too general rather than concentrating on the tensor calculus needed in GR. Needs discussion.

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
3. Graphics (static or dynamic) should not be restricted to one per concept, but be inserted in (or between) content blocks
   wherever they can usefully illustrate a point.
4. Enable community sharing of tutorials, layouts and notes.
5. Extend to molecular biology (MolBio/MolBioKB); a possible collaborator is in mind.
   Domain separation is already implemented.
6. Build a concept's derivation as a recursively foldable tree of explanations drawn
   from its supporting concepts.
7. **Optional tutorial narration.** Compare recorded/generated audio with device-generated speech
   (minimal download, but variable voices and mathematical pronunciation). Prefer separate audio
   files loaded per card; embedding Base64 audio preserves a single-file viewer but adds roughly
   6.4–12.8 MB per 20 minutes at 32–64 kbps. Consider Play/Pause, optional automatic playback,
   stopping on card changes, offline availability and memory use on the old iPad.

## 4. Misc. Issues

1. Support PhysicsKG as an installable web app. Home Screen launch already works on iPhone and the old iPad;
   personal data survives closing and relaunching. Add app identity/installation guidance, reliable offline caching
   of the viewer and all required libraries/assets, and controlled version updates without interrupting study.
   Verify personal-data continuity, Google sign-in/sync and export/import in standalone mode; offline changes must
   remain safe until sync is available. Test on both devices and retain ordinary browser use. Hosted icons and the
   landing-page installation tip are already implemented.
6. Safeguard personal data in subset-domain viewers (e.g. GR-only). Normal question attempts,
   reading ticks and sync preserve unloaded-domain records, but “Reset all study progress” currently
   resets every domain, and saving a Personal layout can delete unloaded-domain layout overrides.
   Scope these operations to loaded domains, preserving other domains through sync; add regression tests.
7. Stop tracking question attempts; simplify study records and their presentation accordingly.
8. Consider a Home button that restores the initial selection and view settings.
   Define which presentation settings it resets; preserve personal data.

## 5. Notes enhancement and unification

1. Extend the shared foldable-content foundation to identifiable nested authored blocks when needed:
   stable child IDs for annotations, tutorial targets and possibly independent reading progress.
   Current optional disclosures and personal notes already share rendering; top-level personal notes,
   mathematical reading/editing and SR-2.5's folded algebra clarifications are implemented.
2. Consider recursive personal-content editing and generated derivation/explanation trees (see 3.6).
   Define placement, depth/cycle limits, completion and sync semantics before exposing these features.
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
