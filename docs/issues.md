# Open Issues

## Content and implementation

- Review unmarked content, especially SR concepts, and explicitly set
  `authoring_status=full` where complete. Blank remains optional and means
  not recorded. Align status documentation and presentation when implementing.
- Migrate SVG dispatch from display IDs to semantic concept IDs so renumbering
  does not require registry edits. Preserve graphic coverage and review tooling.
- Include `CONSTRUCTED_FROM` alongside `DERIVES_FROM` throughout derivation-path
  traversal, including ancestry and downstream trees. Preserve relation labels
  and check navigation, focus and cycle handling. Current trees use only
  `DERIVES_FROM`; this is accepted work, not an open policy question.

## Viewer requests (deferred design)

- Add a reading mode that starts all detail sections folded closed.
- Allow graph and details to be unlinked, with a visible linking control.
- When unlinked, let the focus lens control graph context directly.
- Consider persistent per-focus layouts and their export, separately from the
  existing global-layout workflow. Focussed adjustments are currently temporary;
  global layout export and publication already work. See [Layout](design/layout.md).
