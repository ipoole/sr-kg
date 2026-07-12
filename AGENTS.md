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
