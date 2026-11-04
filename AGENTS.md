# Agent Instructions

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

The hosted preview is `https://physicskg.org/preview/PhysicsKG.html`; use this
instead of committing builds to `phone-preview` or GitHack. Preview publication
must retain the release, and release publication must retain the preview. Previews
share browser personal data and Google authorization with the public viewer.
Do not rewrite repository history as part of routine publishing.
