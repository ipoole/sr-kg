# Documentation

- **Design** describes current contracts and consequential decisions:
  [schema](design/kb_schema.md), [architecture](design/architecture.md),
  [viewer behaviour](design/viewer.md), [modules](design/modules.md), and
  [layout](design/layout.md).
- **Authoring** holds the [authoring guide](authoring/AUTHORING_GUIDE.md),
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
