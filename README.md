# SR Knowledge Graph

A knowledge-graph study companion for special relativity, classical fields,
general relativity and supporting mathematics. It is primarily aimed at personal
study around Theoretical Minimum level, with an ambition to support a wider
range of backgrounds.

The current data contains 47 SR/classical-field concepts and 55 GR concepts
marked `full`, plus nine mathematics concepts marked `prerequisite_support`.
These are authoring statuses, not learner progress or difficulty ratings.

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

Open `output/interactive_graph.html` in a browser. The generated page references
CDN-hosted vis-network assets and MathJax, as well as a relative
`lib/bindings/utils.js` asset; it is not a self-contained offline file.
Generated HTML is a build artifact; do not commit it unless explicitly requested.

## Study with the viewer

Select a module for an overview and concept list, or use **Tools → Search** to
find a concept. Follow links to explore related material and use browser Back
to return. **Details** filters the reading material; **Practice** shows questions
with answers you can reveal for self-checking. **Graph → Focussed** isolates the
selected context, while **Hide graph** gives the reading pane more space.

See [Viewer behaviour](docs/design/viewer.md) for reading modes, navigation and
personal notes. The viewer does not currently record mastery or question attempts.

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
- [Viewer behaviour](docs/design/viewer.md): current learner-facing controls and limitations.
- [KB schema](docs/design/kb_schema.md): source-file contracts.
- [Modules](docs/design/modules.md) and [layout](docs/design/layout.md): graph behaviour and persistence.
- [Authoring guide](docs/authoring/AUTHORING_GUIDE.md): content workflow, domain builds, diagnostics and graphics review.
- [Open viewer requests](docs/issues.md).

Source content lives in `data/`, implementation in `srkg/`, command-line tools
in `tools/`, and tests in `tests/`. Run a tool with `--help` for its full options.
