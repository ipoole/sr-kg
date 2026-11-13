# Documentation

- **Using PhysicsKG:** the illustrated [user guide](../website/user-guide.html)
  is maintained as a website page. The viewer's Quick Start covers the basics;
  Tools → Version history records release news.
- **Design** describes current contracts and consequential decisions:
  [schema](design/kb_schema.md), [architecture](design/architecture.md),
  [viewer behaviour](design/viewer.md), [modules](design/modules.md), and
  [layout](design/layout.md). The [viewer state terminology](design/viewer_terminology.md)
  defines the vocabulary used by the accepted [revised viewer UI model](design/viewer_ui_model.md),
  with [Quick Start scope and maintenance rules](design/viewer_quick_start.md). The
  [guided tutorial design](design/tutorial_playback.md) describes semantic
  routes, grouped actions, direct launch links and presentation restoration.
  Current physics routes cover rest energy and time dilation. The
  [blocks and generated reading-tree design](design/folded_reading_trees_design.md)
  records the agreed title/statement/body model, graph alignment and Reading
  position, with Python pseudocode and prototype screenshots. The
  [standalone paper prototype](../domains/math/docs/graph_aligned_reading_mockup.html)
  exercises its presentation. The [minimum schema](design/folded_reading_trees_schema.md)
  records storage and legacy syntax; the
  [shared reader](design/folded_reading_trees_renderer.md) implements the new model.
  Domain content is being migrated from the earlier block-borrowing pilot; the
  [Maths authoring audit](../domains/math/docs/reading_tree_authoring_review.md)
  records the completed first domain. The
  [SR stage-1 inventory](../domains/sr/docs/reading_tree_authoring_audit.md)
  records block coverage, argument/dependency review questions and preservation
  inputs before the SR authoring pass; the
  [SR module reviews](../domains/sr/docs/reading_tree_authoring_review.md)
  record the completed SR-1 content and dependency changes. The earlier
  [Maths draft](../domains/math/docs/nested_explanations_pilot.md) and
  [MATHS-2 teaching review](../domains/math/docs/tensor_calculus_teaching_review.md)
  retain content and preservation decisions. The earlier
  [Field equations paper](design/folded_reading_trees_paper_prototype.md) is a
  historical experiment, not the new authoring contract. The
  [study-question design](design/study.md) defines marking, latest results, progress,
  and the authored question schema. [Personal data](design/personal_data.md)
  defines local notes, layouts, study and reading records, plus portable
  export/import and optional Google Drive synchronisation. The
  [Google OAuth publication checklist](design/google_oauth_publication.md)
  records the public branding URLs and Console settings. [Release versioning](design/releases.md)
  defines the product version independently of data schema versions.
- **Authoring** holds the concise [authoring guide](authoring/authoring_guide.md),
  [exposition scale](authoring/exposition_style_scale.md),
  [technical procedures](authoring/technical_reference.md) and notation conventions.
  Subject drafts, source worklists, fixtures and graphics
  belong in `domains/<id>/`; see [domain packages](design/domain_packages.md).
- **Discussion** holds speculative ideas, not instructions for current behaviour.
  The [user experience review](discussion/user_experience_review.md) records
  observed usability issues and proposed improvements. The
  [assets and learning journeys discussion](discussion/physicskg_assets_and_learning_journeys.md)
  reconstructs the inventory behind the nested-explanations work.
- [Issues](issues.md) tracks open content and implementation work.

Update the relevant design document when behaviour or a contract changes.
Keep tuning values and implementation details in code. Use a short final
“Future plans” section for likely extensions; longer speculation belongs in
`discussion`. Completed work and migration history belong in Git, not growing
worklists. Link to a rule's primary home instead of repeating it.

CSV content is authoritative. Exposition files support drafting and review;
they are not a second publication to keep synchronised with every CSV edit.
