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
   First draft: [User guide](user_guide.md), approximately 2,000 words with three
   screenshot captions. Still to do: images, standalone webpage and links from
   the viewer/homepage, plus consolidation of superseded documentation.

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
4. Community!  Tutorials, layouts, notes could be shared.
5. Apply to an entirely new domain - molecular biology!  
   I have a collaborator in mind. Author new domain MolBio,MolBioKB.  
   Motivates clean separation of data by domain (done). 
6. When recursively foldable content is in place it will be possible to show the derivation of a concept by building a tree of explanation content traversing the deriving concepts.
 
## 4. Misc. Issues
1. Support PhysicsKG as an installable web app. Home Screen launch already works on iPhone and the old iPad;
   personal data survives closing and relaunching. Add app identity/installation guidance, reliable offline caching
   of the viewer and all required libraries/assets, and controlled version updates without interrupting study.
   Verify personal-data continuity, Google sign-in/sync and export/import in standalone mode; offline changes must
   remain safe until sync is available. Test on both devices and retain ordinary browser use. Hosted icons and the
   landing-page installation tip are already implemented.
5. Avoid questions with free text answers if possible; they are tedious and not particularly instructive. 
   Separate authoring pass: convert suitable questions to automatic multiple choice,
   with plausible distractors and an unknown option. Preserve question IDs and
   existing answered status; retain free text where explaining reasoning is the goal.
6. Safeguard personal data in subset-domain viewers (e.g. GR-only). Normal question attempts,
   reading ticks and sync preserve unloaded-domain records, but “Reset all study progress” currently
   resets every domain, and saving a Personal layout can delete unloaded-domain layout overrides.
   Scope these operations to loaded domains, preserving other domains through sync; add regression tests.
 
## 5. Notes enhancement and unification

1. Extend the shared foldable-content foundation to identifiable nested authored blocks when needed:
   stable child IDs for annotations, tutorial targets and possibly independent reading progress.
   Current optional disclosures and personal notes already share rendering; top-level personal notes,
   mathematical reading/editing and SR-2.5's folded algebra clarifications are implemented.
2. Consider recursive personal-content editing and generated derivation/explanation trees (see 3.6).
   Define placement, depth/cycle limits, completion and sync semantics before exposing these features.
   See [Notes and authored content](design/notes_content_unification.md) for the implemented rules and scope.

## 6. Build artifacts, publishing and repository size
Publishing preparation (stages 1–4) is complete on `untracked-artefact-deployment`;
see [rehearsal results](design/artefact_deployment_rehearsal.md). Live Pages is unchanged;
explicit switchover and untracking (stages 5–6) remain. Implement and verify publishing before rewriting history.

1. Publish the exact locally built and tested website as an untracked GitHub Pages deployment artifact,
   rather than rebuilding on GitHub or committing `output/PhysicsKG.html`. Keep local generation unchanged,
   ignore the generated viewer in Git, and retain the public URL and the small legacy redirect page.
   Provide a publish command using the GitHub CLI and an Actions deployment workflow; record the source
   commit and artifact checksum for traceability.
2. Provide a separately updatable hosted preview artifact, e.g. `https://physicskg.org/preview/PhysicsKG.html`,
   replacing the GitHack/phone-preview branch workflow. Publish the exact local test build without changing
   the public release; deployments must preserve both release and preview. Same-origin previews share browser
   personal data and Google authorization, so document that testing can affect that data.
3. Before the following repository editing, extract all published viewers (.html) and save locally to an untracked directory with a filename which includes the version number, or date before v4.0.0.  Would be interesting to see how the project has developed over time.  
4. After artifact deployment is proven, back up the repository and remove historical generated viewer files
   (including former filenames) using `git-filter-repo`. Audit all branches and tags, including preview branches,
   so they do not retain the old objects; preserve the current small legacy redirect. Coordinate the history rewrite
   and force-push explicitly, then reclaim local storage and verify a fresh clone. Commit IDs will change,
   other working copies should be recloned, and old GitHack links may cease to work. GitHub storage reclamation
   depends on its garbage collection. Initial audit found 134 viewer versions totalling 193.5 MiB uncompressed
   (about 71% of reachable blob content); actual compressed savings need measurement.
5. Consolidate homepage/site sources and branding assets under `website/` as part of artifact publishing,
   reducing repository-root clutter. Assemble these at the deployed website root, preserving the homepage,
   privacy/terms, viewer, favicon/icon, robots/sitemap and custom-domain URLs. Update generator asset paths,
   tests and documentation; retain browser favicon fallback and Google branding/OAuth links.
