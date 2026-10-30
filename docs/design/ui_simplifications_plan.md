# UI simplifications

## Agreed contract

- View: Both, Graph, Details. This controls panes, independently of Graph.
- Graph: All equally, Context + background, Context only. Selection never changes it.
- Selection always identifies an existing concept or module. Prefer SR-1 as the
  startup/fallback module; a valid URL overrides it. Empty-space clicks retain it.
- Startup: Both, All equally, Foundations/one hop, Frame All, authored module defaults.
- Context remains meaningful for counts, expansion and Fit/Fit++ in every Graph mode.
- View changes preserve camera, splitter and reading state; they never automatically fit.
- Show in graph sets Derivation/Uses and the section's depth, makes Both available
  from Details-only, chooses Frame Context and fits after resizing. It preserves
  module folding and never automatically contracts the context.
- Remove Clear, Hidden graph scope, and the separate Folded reading mode. Keep Full
  presentation with authored individual folds. Collapse/Expand sections is deferred.
- History retraces selections only; missing/invalid selections use the fallback.
- Guided playback explicitly specifies View and Graph and restores both on exit.
  Quiet physics introductions remain quiet. Explore/Resume restores the checkpoint.

## Stages and verification

1. Record this contract and baseline.
2. Separate View from Graph; remove reading modes and migrate tutorial pane commands.
3. Add explicit graph emphasis and permanent selection; migrate tutorial selection setup.
4. Implement Show in graph fitting and responsive, accessible control groups.
5. Revise all tutorials, pointers and snapshots; walk all routes on desktop/phone.
6. Update glossary, behaviour, Quick Start, README and issues; remove obsolete tests/code,
   report line counts and run the complete unit/browser suites.

Each stage is committed separately. Rebuild before browser testing; generated HTML
is excluded from commits. No merge or publication until user review.

Regression coverage must include all nine View/Graph combinations, startup and
deep links, invalid URLs, history, module folding, Fit++ restoration, switching
panes without changing context/camera/reading state, Show in graph from Details-only,
and tutorial Back/Explore/Resume/Exit. Study answers and personal data must remain safe.

## Baseline

At branch start: viewer.js 11,406; viewer.css 3,719; controls.html 364;
html_injection.py 266; tutorials.py 559 lines; total 16,314. Tests/data are excluded.

## Completion record

All six stages are implemented. The separate Folded reading mode, null-selection
and empty-graph recovery paths are removed. Global section folding remains deferred.
The tutorials explicitly demonstrate View and Graph, and restore both on Exit or
Resume. The regression suite covers all nine combinations, permanent selection,
invalid URLs/history, context framing, folding, and pane changes without loss of
camera, section folds or layout. A camera-generation guard prevents delayed pane
restoration from undoing an explicit Fit, including Show in graph.

Comparable production line counts for v4.3.0, including review refinements:

| File | Before | After |
| --- | ---: | ---: |
| viewer.js | 11,406 | 11,207 |
| viewer.css | 3,719 | 3,698 |
| controls.html | 364 | 369 |
| html_injection.py | 266 | 266 |
| tutorials.py | 559 | 557 |
| **Total** | **16,314** | **16,097** |

Reduction: 217 lines (1.3%). These counts exclude tests, authored data and docs.

Release validation: 656 unit tests and all 307 browser tests passed. Coverage
includes all three authored tutorials on desktop and phone, the 29-case workspace
suite, personal-data preservation, compact note previews and Quick Start behaviour.
The complete browser suite ran serially in 539 seconds to avoid memory pressure.
Guide tests check behaviour and structure rather than exact section counts or
badge placement. Source changes are squash-merged for v4.3.0; the generated HTML
is rebuilt and committed separately for publication.
