# Refactoring progress — issue 7.2

Scope: preserve current behaviour while reducing coupling. Domain data/graphics
separation (7.3), publishing changes (6), new UI features and changes to personal
data formats are deferred. Current responsibilities are documented in
[architecture.md](architecture.md); the pre-refactor snapshot is retained in Git
at stage-1 commit `3885607`.

## Stage 1 — baseline

Before application changes: 27,282 physical source lines under `srkg/`, counting
`.py`, `.js`, `.css` and `.html`; excludes binary/SVG assets, tools, tests and
generated HTML. `viewer.js`: 11,208; `viewer.css`: 3,698; `kb.py`: 1,224.
Keep this same scope for later comparisons: extracting files must not conceal
increases in total code.

Unit baseline: 656 passed (4.97 s); browser baseline: 309 passed (533.49 s).

`tools/profile_viewer.py` builds an isolated temporary viewer with repository
vis-network assets, stub MathJax, reduced motion and no external requests.
It measures command completion plus two animation frames, with one warm-up and
seven measured samples per operation. It does not measure real MathJax, remote
loading, or predict physical iPad speed. Startup/build are single observations;
operation values are medians. Timings vary with host load and are observations,
not test thresholds. CPU throttling is Chromium's 4x emulation.

```bash
conda run -n sr-kg python tools/profile_viewer.py
```

Initial observation (Chromium 149.0.7827.55; another browser suite was running):

| Measurement | Baseline ms |
| --- | ---: |
| Build | 870.8 |
| Load until initial graph, including splash dismissal | 5649.3 |
| Select rest energy then Lorentz transformations | 939.6 |
| Expand all then fold all | 1717.9 |
| Reset context, Fit then Fit++ | 440.3 |

The regression baseline covers selection/context/scope independence, folded
module proxies and boundaries, layout/camera/Fit++, mobile controls, lazy Details
and MathJax, notes/study/profile round trips, sync and tutorial restoration.
Existing browser tests remain authoritative for those behaviours.

## Stage 2 — small consolidation

Implemented shared owner-aware teaching-block rendering, domain resolution and
CSV mechanics; derive implemented graphic IDs from dispatch registries without
changing their order. Removed unused render options and duplicate control
refreshes. Legacy personal-data migration remains intact; notes imports retain
their lenient final-quote handling while archive imports remain strict. Notes
exports retain LF and archive tables retain CRLF line endings.

The complete loaded concepts/modules/tutorials/published-layout payload has the
same SHA-256 as before consolidation. Production source: 27,093 lines (189 fewer);
`viewer.js`: 11,130. Unit tests: 656 passed. Browser checks: 264 passed,
46 deselected (430.11 s), including all six walkthroughs before the explicit
marker correction.

Marked the six dynamically selected repository tutorial walkthroughs explicitly
`browser_full`: automatic fixture classification could not detect their
`request.getfixturevalue()` dependencies. All six remain in the full suite; the
fast lane now correctly selects 258 of 310 cases, including the new CSV contract
test, instead of also running those six full walkthroughs.

## Stage 3 — graph computation and library boundary

Extracted context traversal, folded-boundary grouping and Fit++ hop planning to
`graph_model.js`, independent of DOM, storage and vis-network. The application
supplies visible endpoint mappings and rendered edge flags; grouping retains
direction, relation counts, original edge IDs and context/background distinctions.
Only eligible visible boundary endpoints are resolved, once per projection.

`vis_network_adapter.js` now owns all direct `network.body` and `network.canvas`
access. It exposes borrowed geometry for synchronous reading, precise positions
(avoiding rounded public coordinates), canvas access, curve points and draw-only
edge widths. Width changes still bypass DataSet mutation/redraw loops. Public
network operations remain with their controllers; this is a boundary around
library internals, not a replacement network API.

Seven direct browser cases cover cyclic/depth-limited traversal, custom reverse
and undirected traversal, folded boundaries, shortest-hop parent candidates and
adapter coordinate/drawing contracts. They run without generating the viewer or
loading MathJax. The initial focused integration run passed 54 cases (39.62 s).
Latest unit run: 656 passed (6.77 s). Full browser run: 317 passed (534.67 s),
including all six repository tutorial walkthroughs, mobile emulation and real
MathJax. The baseline full run took 533.49 s for 309 cases. The regenerated
`output/PhysicsKG.html` is excluded from the stage commits.

| Stage | Production lines under `srkg/` | `viewer.js` lines |
| --- | ---: | ---: |
| 1: baseline | 27,282 | 11,208 |
| 2: consolidation | 27,093 | 11,130 |
| 3: extraction | 27,151 | 10,922 |

Stage 3 adds 58 lines overall to provide explicit interfaces and independent
modules; the combined result is 131 fewer production lines. Tools and tests are
excluded consistently from this count; the new profiling tool is additional code.

A sequential comparison with the stage-1 source snapshot (same Chromium, 4x CPU,
seven measured samples, no concurrent browser suite) gave:

| Operation median, ms | Baseline | Stage 3 |
| --- | ---: | ---: |
| Selection pair | 887.2 | 928.8 |
| Expand/fold pair | 1463.7 | 1541.0 |
| Context reset, Fit, Fit++ | 429.0 | 414.3 |

These small mixed differences are not evidence of a speed improvement or a
confirmed regression. The initial concurrent observations varied more, so avoid
inferring performance from a single run. The comparison above used the first
extraction. Final confirmation after boundary-endpoint filtering reversed the
order (final viewer first, then the same baseline snapshot), again with no
concurrent browser suite:

| Operation median, ms | Baseline | Final stage 3 |
| --- | ---: | ---: |
| Selection pair | 936.9 | 921.8 |
| Expand/fold pair | 1489.0 | 1510.4 |
| Context reset, Fit, Fit++ | 425.0 | 440.3 |

Final differences range from about 2% faster to 4% slower. Together these runs
show broadly comparable operation times, not a consistent performance change.
No claim of faster operation or physical-device verification is made.

## Scope still deferred

All eight stages below are complete. Domain data and domain-specific graphics
separation remain issue 7.3; publishing changes remain issue 6. Neither is needed
to use the ownership boundaries established here.

## Stage 4 — layout, camera and canvas ownership

`global_layout.js` owns published/personal positions, revision state and debounced
persistence. Sync reloads that store explicitly. Temporary Fit++ canvas moves do
not enter the store. Reset cancels a pending save; snapshots are copied.
`graph_camera.js` owns viewport/panel-aware framing and the generation counter
which cancels obsolete deferred camera restores. `graph_presentation.js` owns
canvas painting, SVG images and fitted-label caches. `layout_geometry.js` holds
stateless coordinate/collision helpers. Existing public viewer test/command APIs
remain compatible; Fit++ orchestration and graph/module projection remain in the
application for now.

Verification: 656 unit tests; 152 focused browser cases; the independent layout
store case; and 266 fast-lane browser cases (191.93 s), all passed. The viewer was
rebuilt before browser verification and is excluded from commits. Production
source: 27,322 lines, up 171 from stage 3 for explicit ports/controllers;
`viewer.js`: 9,888, down 1,034. The total includes all new source files.

## Stage 5 — Details, notes, study and personal-data coordination

`content_markup.js` shares escaping, optional details, math-aware paragraph
splitting and caption/study markup. `details_view.js` owns MathJax replacement,
contents selection and scroll state/timers. `notes_controller.js` owns the notes
list, anchor recovery, editor identity, rendering and CSV exchange.
`study_controller.js` owns reading/question state and indexes, completion caches,
marking and scorecard rendering. `personal_data_controller.js` owns OAuth state,
sync timers, visibility resumption and import/export UI. A read-only content facade
and explicit callbacks connect the features; sync reloads their state without
rebuilding the active Details pane. Existing storage formats and legacy note
recovery remain supported. Private helper exports/unused aliases were removed.

Removed the unreferenced `lazyFoldedSectionBodies` reset, which otherwise created
an implicit global. Adjusted an injection-order check to distinguish injected KB
data from a controller's local variable. Focused testing caught an accidentally
copied OAuth client ID; the controller now reads current configuration explicitly.
Added coverage for syncing stale data when a visible page resumes.

Verification: 656 unit tests and 266 fast-lane cases passed (186.37 s). Focused
startup/notes/study checks passed before the configuration failure; all 15 targeted
sync/archive/presentation cases then passed after correction. Production source:
27,569 lines; `viewer.js`: 7,858. Source growth reflects explicit feature interfaces,
not hidden exclusions from the count. Viewer rebuilt, excluded from commits.

## Stage 6 — tutorials, temporary layout checkpoints and canonical content

`tutorial_targets.js` resolves semantic controls, blocks, graph objects and hover
previews using live geometry. Fold-control lookup uses a reader because rebuilding
controls replaces their map. `guided_tutorial.js` owns route/pointer/narration
state, input locking, replay progression and Explore/Resume. It uses the existing
semantic command dispatcher and an explicit presentation capture/restore bridge;
it does not capture or restore personal data.

`context_layout.js` owns Fit++ priming, temporary positions, drag membership and
capture/restore. The application and tutorial bridge no longer mutate those
private variables. Personal layout remains a distinct store. Camera restore
cancellation, collision geometry, graph-hop ordering and temporary movement
semantics are retained.

Removed the alternate coarse-section renderer, its unused CSS and obsolete
coarse-rendering test. Both concept and module teaching content now use the same
canonical block path. Search/preview section summaries derive from those blocks;
Python's grouped-section query facade remains for library compatibility, but
`Concept.to_viewer_data()` no longer exports a duplicate `sections` field.
Updated fixture edits/selectors to use authored block IDs/bodies. Saved legacy
section anchors migrate to unambiguous stable blocks; ambiguous/orphaned notes
remain stored for placement. The migration test first failed against the old
renderer, then passed with canonicalisation, alongside existing paragraph-edit
and CSV/archive tests.

All normalized loaded content/modules/tutorials/layout data matches the original
baseline SHA-256 after excluding the intentionally removed field. Concept payload:
1,650,260 to 1,551,475 UTF-8 JSON bytes (98,785 fewer). Built viewer: 2,624,929 bytes
at published v4.3.1 to 2,529,779 bytes at this stage (95,150 fewer).

Focused checks passed: 21 fast tutorial command/pointer/presentation cases;
126 content/notes/search/startup cases; and 17 Fit++/checkpoint/layout-store cases.
Latest unit run: 656 passed (6.71 s). Full browser run: 318 passed (535.48 s),
including all six complete tutorial routes on desktop/mobile emulation, real
MathJax, storage/archive/sync and graph interaction.
Production source: 27,629 lines; `viewer.js`: 6,605. Compared with stage 1 this is
347 extra production lines (about 1.3%), including every new controller, and
4,603 fewer lines in the application hub. Interfaces add code; moving code into
files alone is not counted as a reduction. Generated viewer remains outside commits.

Final sequential timing comparison against the stage-3 snapshot, with no concurrent
browser tests (same Chromium, 4x CPU, seven measured samples, local vis assets and
stub MathJax):

| Operation median, ms | Stage 3 | Stage 6 |
| --- | ---: | ---: |
| Selection pair | 923.3 | 951.0 |
| Expand/fold pair | 1482.2 | 1479.2 |
| Context reset, Fit, Fit++ | 412.2 | 415.6 |

These local observations are broadly comparable (roughly 0–3% variation), not a
claim of improved speed or verification on physical Apple devices. Single
startup observations were 5105.7 and 5099.4 ms respectively. Full browser-suite
time also remained close to stage 3 (534.67 s for 317 cases).

## Stage 7 — Python loading, contracts and graphic enrichment

`kb.py` now coordinates paths/files, structural checks and assembly rather than
containing the table schema and every validator. `schema.py` owns column/kind
contracts and the shared loading exception; `table_validation.py` owns fail-fast
frame/referential checks. Existing public schema imports through `kb.py` remain
compatible. Validation logic and exception messages are unchanged.

`graphic_enrichment.py` is the bridge from typed records to the existing concept
and module SVG registries. Construction retains captions, then optionally adds
SVGs to replacement records. Loading/build helpers default to graphics as before;
`include_graphics=False` skips importing/running the generators. Editorial
validation uses that path. Two tests cover synthetic and full authored KBs,
asserting identical records apart from SVG fields, with rendering guarded against
accidental calls. The test was introduced before the extraction and first failed.
Browser fixtures now patch the enrichment boundary rather than a data-module
import side effect. Domain file/graphic implementation splitting remains deferred.

Reviewed CSS and test organisation: preserved cascade order and the existing
behaviour-based test groups; added navigation comments rather than moving rules
or duplicating tests around the new controller files. Existing contract tests
continue to exercise the loader's public boundary.

Unit tests: 658 passed. The complete normalized concept/module/tutorial/layout
payload still matches the original SHA-256; concept payload remains 1,551,475
UTF-8 JSON bytes. Production source: 27,738 lines; `viewer.js`: 6,605; `kb.py`: 406
(previously 1,224). Moving contracts does not reduce the combined line count:
this stage adds 109 lines overall for the separated interfaces and optional
text-only loading path. Generated viewer rebuilt and excluded from source commits.

Fast browser lane: 266 passed, 52 deselected (194.63 s).

## Stage 8 — final audit and documentation

Updated `architecture.md` to describe the implemented Python stages, controller
owners, query/callback interfaces, borrowed adapter geometry versus copied
snapshots, caches/timers and remaining application coordination. Updated README,
personal-data and tutorial implementation references. Marked 7.2 complete; 7.3
remains open and will need its own architecture refresh. Quick Start remains
accurate: this branch changes responsibilities, not learner-facing controls.

Final audit confirmed that all 15 extracted validators/helpers are AST-identical
after the deliberate private/public function rename. Checked changed-document
local links and whitespace; direct vis-network internals remain confined to the
adapter. A fresh process loaded all 114 concepts and 13 modules without importing
SVG generators when graphics were disabled. The canonical payload checksum is
unchanged from the baseline comparison recorded above. No further code changes
were required during this final pass.

Verification: 658 unit tests passed; full browser suite: 318 passed in 535.93s (0:08:55).
This includes desktop/mobile-emulated authored tutorial walkthroughs, real
MathJax, notes migration, layout/camera behaviour, storage/archive/sync and study
state. No physical iPad/iPhone verification or live Google account test is claimed.
Stage-7 preview source: `b813b3f`; exact built HTML published separately as
`e56e3c9` on `phone-preview` for user review. Main was not changed.

Final production source count (same scope as stage 1): 27,738 versus 27,282,
**456 more lines, about 1.7%**. `viewer.js`: 6,605 versus 11,208; `kb.py`: 406
versus 1,224. Smaller coordinator files are not counted as an overall reduction.
Built HTML: 2,529,894 bytes versus 2,624,929 at published v4.3.1: 95,035 fewer.
Generated HTML remains outside the source-branch commits.

Final timing check ran after the browser suite with no concurrent browser tests:
current viewer first, then the stage-3 reference, same Chromium/4x CPU, seven
measured samples, local vis assets and stub MathJax:

| Operation median, ms | Stage 3 reference | Final stage 8 |
| --- | ---: | ---: |
| Selection pair | 922.5 | 964 |
| Expand/fold pair | 1475.9 | 1589.7 |
| Context reset, Fit, Fit++ | 433 | 407.4 |

These are local comparative observations, not a speed-improvement claim or
physical-device prediction. Single startup observations were 5229.1 ms
(reference) and 5041.7 ms (final). The application still owns module projection/
geometry coordination, search/navigation and command/event wiring; further
extractions should be justified by cohesion or a concrete feature rather than
a target file size.

The first final comparison showed roughly 4.5% slower selection, 7.7% slower
expand/fold and 5.9% faster Fit/Fit++. Because that differed from the earlier
stage-6 observations, repeated in the opposite order (reference first, then final),
again with no concurrent browser suite and identical settings:

| Operation median, ms | Stage 3 reference | Final stage 8 repeat |
| --- | ---: | ---: |
| Selection pair | 939.7 | 924.2 |
| Expand/fold pair | 1517 | 1525.1 |
| Context reset, Fit, Fit++ | 422.9 | 421.9 |

The repeat ranges from about 1.6% faster to 0.5% slower. Together with the earlier
runs, this does not establish a consistent performance change; the first larger
expand/fold difference did not reproduce. Both results are retained rather than
selecting a favourable run. Startup was 5142.4 ms (reference) and 5094.2 ms (final)
in the repeat.
