# PhysicsKG

**An Atlas of Physics Knowledge.** A knowledge-graph study companion for special relativity, classical fields,
general relativity and supporting mathematics. It is primarily aimed at personal
study around Theoretical Minimum level, with an ambition to support a wider
range of backgrounds.

The published [PhysicsKG home page](https://physicskg.org/) introduces the atlas
and links to its [privacy policy](https://physicskg.org/privacy.html).

The current data contains 49 SR/classical-field concepts, 56 GR concepts, and
nine supporting mathematics concepts.

The project turns CSV source data into an interactive HTML viewer with searchable
concepts, mathematical teaching content, study questions, foldable topic modules,
relationship exploration and a unified personal-data profile for notes, layouts,
study progress and reading marks. Self-paced guided tutorials operate the live
viewer with an animated semantic pointer; routes can also be launched directly
with `?tutorial=<tutorial-id>`.

## Setup

Use Python 3.12 or newer and the project conda environment `sr-kg`:

```bash
conda run -n sr-kg python -m pip install -r requirements.txt
```

## Generate and view

From the repository root:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data --out output/PhysicsKG.html
```

Open `output/PhysicsKG.html` in a browser. The generated page references
CDN-hosted vis-network assets and MathJax, as well as a relative
`lib/bindings/utils.js` asset; it is not a self-contained offline file.
Generated viewer HTML is an ignored build artifact and is not committed.
Hosted pages use icon sources in `website/` (`favicon.svg`, `favicon-32.png`,
`favicon.ico`, `apple-touch-icon.png`); keep them in sync with the source icons
in `srkg/viewer_assets`. Increment the icon URL version when replacing the artwork.
Locally opened viewer HTML retains embedded icons.
Packaging places website sources at the deployed root, preserving their public URLs.
Public pages declare their preferred `https://physicskg.org/` addresses with
canonical links. `sitemap.xml` lists the four public pages and is advertised in
`robots.txt`; submit `https://physicskg.org/sitemap.xml` in Google Search Console
after publishing it. Keep the sitemap aligned with changes to public page URLs.
The published interface tour can be launched directly at
`https://physicskg.org/output/PhysicsKG.html?tutorial=using-physicskg`.

## Study with the viewer

**View** chooses Graph, Details or Both. **Graph** chooses All equally, Context +
background or Context only. Selection is always retained; startup selects SR-5 with transitive Foundations and Context + background.
The Context rule remains available for fitting and expansion in every graph mode.
Show in graph fits its context automatically without unfolding modules.

Select a module for an overview and concept list; use its visible corner control
to expand or fold it, or use the header **Search** button to find a concept.
Follow links to explore related material and use browser Back or the floating
**‹ ›** selection-history controls to return.
**Details** shows the complete material, folds its blocks, or hides the pane.
Open **Study Questions** to answer or self-mark questions before seeing their model answers. Automatic
questions include an “I don't know” choice; free-text questions ask you to
compare with a model answer. Clear ticks and crosses show the latest result,
and optional graph ticks summarise reading and question completion.
Use **Context** and **Depth** to choose related material, and **Display** to show
the full graph, only that context, or the details pane on its own.
The responsive viewer is tuned for phones and reduces costly rendering,
animation and eager content work on older or slower devices.

Use **Quick start → Start guided tutorial** for an automatic orientation, or
choose interface and physics routes under **Tools → Tutorials**.
Physics routes include **Why mass has rest energy** and **Why moving clocks
record less time**. Each introduction offers a direct launch link to bookmark
or share; the time-dilation route uses `?tutorial=time-dilation`.
During playback PhysicsKG performs the actions; use **Back**, **Next step** and **Exit** to
control playback. **Explore from here** temporarily releases the viewer for
free investigation; **Resume tutorial** restores the saved tutorial view
without undoing notes or study progress.

See [Viewer behaviour](docs/design/viewer.md) for details presentation, navigation and
personal notes. The **Study** tools keep attempt counts and latest results, with
links back to each attempted question and controls to reset progress. Teaching
blocks also have a persistent blue read tick. Notes, personal layout, study
attempts and reading marks remain local by default; **Tools → Personal data**
downloads or imports them together as a portable ZIP of readable CSV files. See the
[Viewer quick start](docs/design/viewer_quick_start.md) for a short introduction.
Use the speech-bubble `+` in a block heading, then choose a paragraph, to add a
note without leaving permanent insertion controls throughout the text. A filled
bubble means that block already has notes. The bubble beside a concept/module
heading adds personal content after its authored exposition. Notes unfold into a
reading view; use **Edit**, then **Done** to return to reading. Mathematics uses
MathJax notation, with **Insert maths** supplying an editable example. Personal
notes do not affect completion ticks. See [Notes and authored content](docs/design/notes_content_unification.md).

An optional Google Drive connection synchronises the same visible
`PhysicsKG personal data.zip` file between browsers. It syncs immediately on
connection and automatically after changes while connected, while retaining a
manual **Sync now** action. Local storage remains the working copy and the viewer
remains usable without connecting. The project's
public Google OAuth web-client ID is used by default and authorises the
`https://physicskg.org` origin. A different deployment can override it at
build time:

```bash
conda run -n sr-kg python tools/generate_pyvis.py \
  --data-root data --out output/PhysicsKG.html \
  --google-drive-client-id CLIENT_ID.apps.googleusercontent.com
```

The `PHYSICSKG_GOOGLE_DRIVE_CLIENT_ID` environment variable is the equivalent
override. An empty override disables Google Drive controls for a build. See
[Personal data](docs/design/personal_data.md) for the data and synchronisation
model. The public privacy policy is linked from the Personal data controls in
the viewer.

## Validate and test

```bash
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --validate-only
conda run -n sr-kg pytest -q
```

Validation errors fail the command; warnings are editorial review prompts.
Browser integration tests are opt-in and require Chromium. Run the fast
synthetic-data lane during routine viewer work:

```bash
conda run -n sr-kg python -m playwright install chromium
conda run -n sr-kg pytest -q tests/browser -m "not browser_full"
```

Before merging viewer changes, run the full lane; it adds repository-data,
mobile-emulation and real-MathJax coverage:

```bash
conda run -n sr-kg pytest -q tests/browser
```

## Documentation

- [Documentation index](docs/readme.md): where guidance, drafts and discussion live.
- [Architecture](docs/design/architecture.md): generation stages, browser controller ownership and personal-data boundaries.
- [Viewer behaviour](docs/design/viewer.md): current learner-facing controls and limitations.
- [Personal data](docs/design/personal_data.md): local-first storage, portable archives and Google Drive synchronisation.
- [Google OAuth publication](docs/design/google_oauth_publication.md): public branding, Console settings and release checklist.
- [Release versioning](docs/design/releases.md): product release numbering and its single source of truth.
- [KB schema](docs/design/kb_schema.md): source-file contracts.
- [Domain packages](docs/design/domain_packages.md): ownership, discovery and authoring.
- [Selected-domain builds](docs/design/missing_domain_builds.md): isolated loading, missing-domain warnings and omitted relationships.
- [Modules](docs/design/modules.md) and [layout](docs/design/layout.md): graph behaviour and persistence.
- [Authoring guide](docs/authoring/authoring_guide.md): content workflow, domain builds, diagnostics and graphics review.
- [Open viewer requests](docs/issues.md).

Source content and graphics live in `domains/<domain-id>/`; `data/` holds shared
collection metadata. Shared implementation lives in `srkg/`, command-line tools
in `tools/`, and tests in `tests/`. Run a tool with `--help` for its full options.

## Exact-build publishing

GitHub Pages now deploys the exact locally built and tested website package;
GitHub does not regenerate the viewer. See [Artefact deployment](docs/design/artefact_deployment.md)
for packaging, upload, explicit publication and rollback commands. Pushing source
to main alone no longer publishes the website.

Website sources live only in `website/`; the tracked legacy URL page is
`output/interactive_graph.html`. Generated viewers remain locally in ignored
`output/*.html`, and local packages belong in ignored `.deployment/`.

For remote review use `https://physicskg.org/preview/PhysicsKG.html` instead of
GitHack. Release updates preserve the preview; preview updates preserve the
release. Both URLs share browser personal data and Google authorization.
Historical generated files remain in Git history pending a separate cleanup.
