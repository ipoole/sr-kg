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

The unit test suite is fast; run it after every significant code change before
handing work back.

Browser integration tests live under `tests/browser` and require Playwright plus
browser binaries in the `sr-kg` environment. Run them with:

```bash
conda run -n sr-kg pytest -q tests/browser
```

In managed Codex sessions, running browser tests may require command escalation
because Chromium must launch outside the normal command sandbox.
