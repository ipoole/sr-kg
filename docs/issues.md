# Open Issues

Issue numbers are retained so existing references remain valid.

## 2. Tutorials

2. **Deferred — generated tutorials.** Explore generating prompts from a concept's derivation tree,
   using short block summaries or learning outcomes that could also serve as hover previews.
   Use this work to audit the KB's dependencies, block structure and explanations.
3. **In progress — user tutorial authoring**, branch `user-creation-of-tutorials`.
   Personal drafts, built-in copies, card/action editing, rehearsal and recording
   with Undo/Redo and phone support, text export/import, backups and companion-file
   Google sync are implemented; optional human narration is next.
   Learners' Explore actions are not recorded. See
   [the staged design and review gates](design/tutorial_authoring.md).

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
13. **Deferred — details masthead redesign, for a later minor feature release.** Keep its scale fixed like the graph toolbar, independently of content zoom. Reduce vertical space and the prominence of the module link on desktop; reconsider the Fold/Unfold controls and the messy “+” note marker. Resolve these together before implementing a compact layout.
14. **Website analytics.** Consider lightweight, privacy-conscious page-level analytics for
   physicskg.org, reporting home-page visits, viewer opens and user-guide visits separately.
   Exclude preview/test traffic. Initially avoid tracking reading activity, answers or
   personal content; review the provider and any privacy-policy changes before enabling.

## 5. Notes enhancement and unification

1. Consider first-class nested authored blocks with stable child IDs, tutorial targets
   and possibly independent reading progress. Existing local clarifications already
   support scoped notes; distinguish this from new independently tracked blocks.
2. Consider recursive personal-content editing. Generated reading trees are now implemented;
   define placement, completion and sync semantics for further personal-content nesting.
   See [Notes and authored content](design/notes_content_unification.md) for the implemented rules and scope.

