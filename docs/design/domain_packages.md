# Domain authoring packages — issue 7.3

Status: domain split complete. The subsequent [selected-domain warning policy](missing_domain_builds.md)
replaces the initial strict subset policy recorded in the historical stages below.

Every domain, including future subjects, owns one directory under `domains/`.
`domain.yaml` declares its stable ID, title, sequence, table paths and graphics
provider. Optional `display_name` and owned `initial_selection` supply browser
labels and startup preferences. Sequence controls reading order. An optional
`module_palette` points to domain-owned JSON colour pairs; absent palettes use
the shared neutral fallback. The collection manifest declares the domains directory, common relation
vocabulary and general interface tutorials. Discovery reads only directories with
an explicit domain manifest, sorted by `(sequence, id)`; no central domain list.
Directory name, manifest ID and semantic-ID namespace must agree. Explicit
selection locates those directories directly and reads no other package metadata,
tables, palettes or graphics.

A package owns `data/*.csv`, `layout.json`, subject `tutorials.yaml`, `graphics/`
(creators, registries, module assets and specialised helpers) and `tests/`.
Common Python/browser machinery, drawing primitives and integration tests remain
shared. A new concept or graphic must not require editing shared registration
code or another domain. Domain IDs do not depend on a hardcoded list of subjects.

Concept/module/block/question IDs remain globally unique and stable. Records
belong to their concept/module's domain, options to their question, and edges to
the recorded source concept's domain (also for undirected edges). Cross-domain
edges and content/support references may name unloaded namespaces. They produce
structured generator warnings: omit dangling edges/supports and render external
prose labels as plain text. Unknown IDs within loaded namespaces remain errors.
The generator never checks unloaded packages to distinguish valid external IDs
from typos and never imports their concepts implicitly.
References resolve against a domain-local bibliography, so different packages
may use the same citation key independently. Cross-domain references use stable
semantic IDs and require no copy of the referenced concept.

Layout coordinates remain global, split by owning concept/module. Preserve
revision `7` during the initial migration. Later per-domain revision changes
produce a deterministic combined revision. Browser storage formats and identity
keys do not change. Subject tutorial routes belong to one package; interface
routes remain common and are included only when their declared domains are
available. All retained tutorial targets must resolve.

The normal build assembles one KnowledgeBase and the same viewer payload. No
combined source CSVs are generated or tracked. Single-root test/library fixtures
retain a small compatibility path. All writing tools must select their domain;
read-only tools use the common composition layer.

## Initial domain-split stages and verification (historical)

1. Contract and baseline. Added `tools/check_content_snapshot.py` to compare
   concept/module SVGs and teaching content, questions, references, tutorials,
   layout (including revision), node/edge records and relation metadata.
   Baseline saved outside Git at `/tmp/kg-domain-baseline.json`. The existing
   658-unit/318-browser responsibility-refactor verification is the starting
   point; full browser verification is repeated at completion.
2. Generic discovery, composition and strict reference/ownership contracts.
3. Mechanical data/layout/tutorial migration, checking baseline equivalence.
4. Domain-owned SVG generation/registries/assets, checking identical output.
5. Authoring tools, domain-owned expectations and guidance.
6. Full integration, subset-build checks and architecture reconciliation.

Commit after each stage; leave generated viewer outside source commits.

Stage 2 complete: generic collection loading, deterministic discovery, ownership
and missing-target checks, domain-local bibliography resolution and combined
layout/tutorial assembly. Six invented-domain tests cover registration-free
loading, local citation keys, independent subsets, missing edge/prose targets,
foreign edge ownership, duplicate identities and unknown selections. All 664
unit tests pass; the original full-build snapshot still matches every component.
Legacy single-root fixtures remain supported. Collection builds reject automatic
linked-concept inclusion; selected packages must form a closed reference set.

Stage 3 complete: SR, MATHS (stable ID `math`) and GR now own separate data,
layout and subject-tutorial files. Every assembled snapshot component matches.
A row-level audit accounted for all 13 moved tables; shared relation metadata
and the interface tutorial remain in `data/`. Tests read composed tables/model
rather than deleted aggregate paths. All 664 unit tests pass; viewer rebuilt.

Stage 4 complete: all 114 concept creators and 11 module motifs/assets moved to
domain-owned graphics directories. Shared primitives/motifs/framing remain in
`srkg/svg_graphics`; public dispatch APIs discover providers with no subject
list. Providers load in isolated per-directory namespaces and support relative
imports. Unknown/foreign registrations fail; text-only loads do not import them.
Three further tests cover future-domain graphics, import isolation and ownership.
All 667 unit tests pass; every baseline snapshot component still matches; viewer
rebuilt. No diagram functions were renamed or redrawn.

Stage 5 complete: graphics review, DAG/partition diagnostics and numbering tools
read the composed model/table API. Applying numbering requires an explicit owner;
new layout installation writes only one domain. Tests verify the other package's
files remain byte-identical. Domain-specific graphic/study expectations, content
regressions, partition fixtures/tests, drafts and source worklists now live inside
their domain. Shared tests discover domain expectations and registered IDs.
Authoring guide, README and schema describe the new paths and strict subset policy.
All 672 unit tests pass. DAG report, curated partition evaluation, graphics review
and numbering proposal CLI smoke checks pass; all baseline hashes still match.


## Manifest and provider example

```yaml
id: molbio
title: Molecular biology
display_name: BIO
sequence: 40
initial_selection: module:molbio.foundations
graphics: graphics.registry
module_palette: module_palette.json
files:
  nodes: data/nodes.csv
  edges: data/edges.csv
  content_blocks: data/content_blocks.csv
  study_questions: data/study_questions.csv
  study_question_options: data/study_question_options.csv
  references: data/references.csv
  reference_links: data/reference_links.csv
  modules: data/modules.csv
  module_members: data/module_members.csv
  module_content_blocks: data/module_content_blocks.csv
  layout: layout.json
  tutorials: tutorials.yaml
```

Paths belong to the package. Optional caption/support roles follow the same
`files` mapping. When modules are absent, omit the module files and select a
concept instead. A package with no subject tutorials can omit that file.

```python
# domains/molbio/graphics/registry.py
from .concepts import draw_example
CONCEPT_CREATORS = {"molbio.example": draw_example}
MODULE_CREATORS = {}
```

Creators accept `variant="icon"` or `"detail"` and return SVG text. There is no
shared registry edit. Put specialised expectations in local `tests/` files;
use distinct test filenames (e.g. `test_molbio_content.py`) to avoid pytest's
legacy module-name collisions. Generic integration tests discover packages.

The initial move preserved every assembled snapshot component. For later
storage-only migrations, capture a fresh comparison before editing:

```bash
conda run -n sr-kg python tools/check_content_snapshot.py --write /tmp/before.json
conda run -n sr-kg python tools/check_content_snapshot.py --check /tmp/before.json
```

This compares semantic payloads and exact SVG strings; it is not a permanently
frozen content test. Authors can legitimately change content/graphics afterwards.


Stage 6 integration checks: runtime labels, reading order and preferred startup
selection now come from package metadata, preserving the current full viewer's
SR-5/transitive-foundations start and SR → MATHS → GR reading order. No subject
names remain in shared Python/JavaScript dispatch or ordering code. Domain module
palettes also moved out of shared Python into owned JSON files; that final move
produces an identical colour map and byte-identical generated viewer.

A new molecular-biology-only synthetic collection boots, expands its module and
navigates concepts in desktop and phone emulation. Unit contracts additionally
cover resolved collection paths, duplicate domain IDs, reversed undirected edge
duplicates, individually filtered common tutorials with retained-target checks,
owned startup selection, deterministic layout revisions and future-domain colour
palettes. The text macro parser is shared independently of loading/editorial
diagnostics to avoid introducing a dependency cycle.

All seven non-empty production-domain selections were checked. SR + MATHS builds
with 58 concepts; all three domains build with 114. SR-only, MATHS-only, GR-only,
SR + GR and MATHS + GR fail on an explicit missing target under the agreed strict
policy. An independent future domain does not need any physics package.

Latest unit verification: 679 passed (320 browser cases skipped by the plain unit
command). The content snapshot still matches all baseline components: exact SVG
strings, blocks/questions/references, modules, tutorials, graph rows and published
coordinates/revision. Full browser-suite results are recorded below on completion.

Final stage 6 verification: **679 unit tests and all 320 browser tests passed**.
Full browser lane: 535.12 s, including all authored tutorial walkthroughs, real
MathJax, mobile emulation, storage/archive/sync, notes, study/reading progress,
layouts/Fit++ and the two future-domain cases. Six focused startup/order/future-
domain browser checks passed first. No physical-device or live-account test is
claimed. Rebuilt `output/PhysicsKG.html` remains outside source commits.

The final palette extraction occurred during the browser run; an independent
rebuild confirmed its colour map and complete generated HTML were byte-identical
to the tested pre-extraction build. Its new provider/configuration path is also
covered by the final unit suite. All seven original semantic snapshot hashes
still match. Documentation audit: 72 local links resolve; whitespace checks pass.

Production source now totals 28,044 physical lines, counting `.py/.js/.css/.html`
under `srkg/` **plus the moved domain graphics Python** and excluding tests,
tools, SVG/JSON/CSV data and generated HTML. Compared with the pre-domain split
27,738 this is 306 additional lines (about 1.1%) for discovery/composition and
provider contracts, not a hidden reduction by moving files. Domain palettes now
count as JSON data rather than inline Python. `viewer.js`: 6,611 lines. This is an
ownership/authoring change; no runtime performance improvement is claimed.

All six stages committed separately on `big-refactor`; no merge or publication
was performed as part of this task. Artifact publishing/history cleanup remain
issue 6. The initially strict missing-domain policy was subsequently relaxed as described
in [selected-domain builds](missing_domain_builds.md).
