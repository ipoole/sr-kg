# Agent Instructions

## Issues and parallel development

- Track bugs, features and content work in [GitHub Issues](https://github.com/ipoole/sr-kg/issues).
  Check the issue and its linked work before starting. Record who is taking it
  and the branch name. Use the issue for scope changes, blockers and handoffs.
  Record lasting design decisions in the relevant project docs.
- Use one assigned checkout per agent and a feature branch for each active
  piece of work. Reuse the assigned checkout for successive tasks by switching
  branches there. Use separate checkouts when agents work in parallel.
  Fetch `origin`, check the current branch and working tree, and base new work
  on `origin/main`. Include the issue number in the branch name when there is
  one, for example `issue-11-domain-personal-data`. Coordinate scope and merge
  order when work overlaps in a shared component or data contract.
- Open a pull request against `main` and record the change and checks run.
  Use `Closes #N` if the PR fully resolves the issue, or `Refs #N` for partial
  work. Bring in current `origin/main` before merging and repeat affected checks
  after resolving conflicts or integrating overlapping changes.
- Coordinate hosted previews and releases across checkouts. Agree who will
  publish, which commit to build, and which version to use before changing
  shared release metadata. Record the deployed preview version and link on
  the PR. Follow the publishing instructions below.

## Python Environment

Use the project conda environment for all Python commands:

```bash
conda run -n sr-kg python ...
conda run -n sr-kg pytest -q
```

Do not install packages into the base conda environment. If a dependency is
missing, stop and confirm the intended environment and install command first.

## Testing

Run tests from the repository root with:

```bash
conda run -n sr-kg pytest -q
```

When fixing a reported defect, prefer a test-first workflow: add or update a
focused regression test that fails against the current behaviour, confirm the
failure when practical, then patch the code and rerun the test to make it pass.

Run the Python unit suite after every significant code change. Chromium tests
take longer. For viewer changes, start with focused Playwright cases that cover
the changed behaviour. The synthetic-data lane is useful for broader checks
during development:

```bash
conda run -n sr-kg pytest -q tests/browser -m "not browser_full"
```

**Share the build early.** Once the unit and focused checks pass, send the user
a link to the tested local build or, if requested, the hosted preview. Say
which checks passed and which are still pending. Continue the remaining checks
in the same task and report their results. A review build is not a sign-off.

Before marking viewer work ready to merge or release, run the full Chromium suite:

```bash
conda run -n sr-kg pytest -q tests/browser
```

Browser tests require Playwright and browser binaries in the `sr-kg`
environment. In managed Codex sessions, Chromium may require command escalation.

## Design Principles

- Keep the user model and interface simple. Remove duplicate controls and
  rarely useful actions that take space or distract.
- Give content priority, especially on phones. Use width before adding rows
  and keep headers compact while preserving readable labels and usable tap targets.
- Put controls where their effect is visible. Reuse familiar controls, keep
  common actions one step away, and show contextual actions only when they apply.
- Keep interface controls stable while reading. Reading zoom scales text and
  graphics without growing toolbars. Keep navigation and keyboard focus clear
  at narrow widths.

## Build Artifacts

`output/PhysicsKG.html` is a generated build product. After any material
data, content, layout, or viewer change, rebuild it with:

```bash
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --out output/PhysicsKG.html
```

Generated viewers under `output/` are ignored and must remain outside Git.
`output/interactive_graph.html` is the small hand-authored legacy URL page and
remains tracked. Website source pages and branding files live in `website/`;
packaging places them at the public site root.

## Publishing and previews

Publish the exact locally built and tested HTML through the artifact workflow;
GitHub does not run the generator. Pushing source to main does not deploy.
After committing/pushing source, retrieve the live package, package the release
or preview, upload it and explicitly request deployment. See
`docs/design/artefact_deployment.md` for commands and rollback.

Before each new preview publication, increment the product patch version in
`srkg/branding.py`, add a dated Version history entry labelled Preview, and build/test
that version. A retry of the same package keeps its version. See
`docs/design/releases.md` for the versioning convention.

The hosted preview is `https://physicskg.org/preview/PhysicsKG.html`; use this
instead of committing builds to `phone-preview` or GitHack. Preview publication
must retain the release, and release publication must retain the preview. Previews
share browser personal data and Google authorization with the public viewer.
Do not rewrite repository history as part of routine publishing.
