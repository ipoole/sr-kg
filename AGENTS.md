# Agent Instructions

## Issues and parallel development

- Track bugs, features and content work in [GitHub Issues](https://github.com/ipoole/sr-kg/issues).
  Check the issue and its linked work before starting. Record who is taking it
  and the branch name. Use the issue for scope changes, blockers and handoffs.
  Record lasting design decisions in the relevant project docs.
- Use a separate checkout and feature branch for each active piece of work.
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

The unit test suite is fast; run it after every significant code change before
handing work back.

Browser integration tests live under `tests/browser` and require Playwright plus
browser binaries in the `sr-kg` environment. For routine viewer development run
the fast synthetic-data lane with:

```bash
conda run -n sr-kg pytest -q tests/browser -m "not browser_full"
```

Before completing viewer work, run the full lane with:

```bash
conda run -n sr-kg pytest -q tests/browser
```

In managed Codex sessions, running browser tests may require command escalation
because Chromium must launch outside the normal command sandbox.

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
