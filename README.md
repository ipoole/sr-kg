# SR Knowledge Graph

A pedagogical knowledge graph for special relativity, classical fields, general
relativity and supporting mathematics. The 55 GR concepts across six modules
have completed full authoring and review; supporting mathematics has its own
prerequisite status.

The project turns CSV source data into an interactive HTML viewer with searchable
concepts, mathematical teaching content, study questions, foldable topic modules,
relationship exploration, personal notes and persistent graph layouts.

## Setup

Use Python 3.12 or newer and the project conda environment `sr-kg`:

```bash
conda run -n sr-kg python -m pip install -r requirements.txt
```

## Generate and view

From the repository root:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data --out output/interactive_graph.html
```

Open `output/interactive_graph.html` in a browser. Equation rendering requires
network access because MathJax loads from a CDN. Generated HTML is a build
artifact; do not commit it unless explicitly requested.

## Validate and test

```bash
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --validate-only
conda run -n sr-kg pytest -q
```

Validation errors fail the command; warnings are editorial review prompts.
Browser integration tests are opt-in and require Chromium:

```bash
conda run -n sr-kg python -m playwright install chromium
conda run -n sr-kg pytest -q tests/browser
```

## Documentation

- [Documentation index](docs/README.md): where guidance, drafts and discussion live.
- [Architecture](docs/design/architecture.md): generation, presentation and user state.
- [KB schema](docs/design/kb_schema.md): source-file contracts.
- [Modules](docs/design/modules.md) and [layout](docs/design/layout.md): graph behaviour and persistence.
- [Authoring guide](docs/authoring/AUTHORING_GUIDE.md): content workflow, domain builds, diagnostics and graphics review.
- [Open viewer requests](docs/issues.md).

Source content lives in `data/`, implementation in `srkg/`, command-line tools
in `tools/`, and tests in `tests/`. Run a tool with `--help` for its full options.
