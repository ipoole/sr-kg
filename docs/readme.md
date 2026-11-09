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
  [nested-explanations Maths pilot design](design/nested_explanations_design.md)
  and its domain-owned teaching draft explore recursively shared content. The
  [minimum schema](design/nested_explanations_schema.md) implements the Python
  source/loading contracts; the [shared reader](design/nested_explanations_renderer.md)
  is implemented and used by the Maths pilot, whose draft records the actual
  sources and preservation decisions. The
  earlier [paper prototype](design/nested_explanations_paper_prototype.md) records
  the Field equations experiment and deferred graph reading highlights. These are
  teaching/design drafts, rather than converted production content. The
  [study-question design](design/study.md) defines marking, attempts, progress,
  and the authored question schema. [Personal data](design/personal_data.md)
  defines local notes, layouts, study and reading records, plus portable
  export/import and optional Google Drive synchronisation. The
  [Google OAuth publication checklist](design/google_oauth_publication.md)
  records the public branding URLs and Console settings. [Release versioning](design/releases.md)
  defines the product version independently of data schema versions.
- **Authoring** holds the shared [authoring guide](authoring/authoring_guide.md)
  and notation conventions. Subject drafts, source worklists, fixtures and graphics
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
