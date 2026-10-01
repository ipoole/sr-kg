# Documentation

- **Design** describes current contracts and consequential decisions:
  [schema](design/kb_schema.md), [architecture](design/architecture.md),
  [viewer behaviour](design/viewer.md), [modules](design/modules.md), and
  [layout](design/layout.md). The [viewer state terminology](design/viewer_terminology.md)
  defines the vocabulary used by the accepted [revised viewer UI model](design/viewer_ui_model.md),
  with a user-facing [viewer quick start](design/viewer_quick_start.md). The
  [study-question design](design/study.md) defines marking, attempts, progress,
  and the authored question schema.
- **Authoring** holds the [authoring guide](authoring/authoring_guide.md),
  notation conventions, working drafts, and outstanding editorial work.
- **Discussion** holds speculative ideas, not instructions for current behaviour.
  The [user experience review](discussion/user_experience_review.md) records
  observed usability issues and proposed improvements.
- [Issues](issues.md) tracks open content and implementation work.

Update the relevant design document when behaviour or a contract changes.
Keep tuning values and implementation details in code. Use a short final
“Future plans” section for likely extensions; longer speculation belongs in
`discussion`. Completed work and migration history belong in Git, not growing
worklists. Link to a rule's primary home instead of repeating it.

CSV content is authoritative. Exposition files support drafting and review;
they are not a second publication to keep synchronised with every CSV edit.
