# Selected-domain builds

Revision to the strict subset policy introduced during issue 7.3.

A domain directory, its manifest ID and the first dotted component of its
semantic graph IDs must agree. Child blocks/questions/options also carry their
owning namespace. Bibliography keys remain local; tutorial slugs are unchanged.
Legacy single-root datasets retain their existing compatibility contract.

Explicit selection reads only the requested packages and shared configuration.
An explicitly requested absent package is an error. References into an unloaded
namespace produce generator warnings; they are not checked against other
packages. Unknown IDs within a loaded namespace, malformed source, duplicates
and ownership violations remain errors.

Keep selected concepts/modules. Omit unavailable edges and support links; retain
prose but render unavailable concept labels without links. Omit subject routes
requiring unavailable objects. Common interface-route availability does not add
artificial missing-domain dependencies to otherwise independent subject content.
Warnings belong to the build report rather than the viewer or personal data.

## Implementation and verification

1. Enforce namespace ownership; focused regressions first.
2. Isolate requested-package discovery/loading, with read/import tripwires.
3. Collect external-reference diagnostics and omit dangling relationships.
4. Preserve prose labels and filter unavailable subject tutorials safely.
5. Report warnings and reconcile authoring/schema/architecture guidance.
6. Verify full-build equivalence and partial builds; run unit/browser suites.

Commit after each stage. Generated viewer stays outside source commits.

Stage 1: enforced manifest/directory and owned-record namespaces. The three
focused regressions first failed against the previous behaviour, then passed.
Updated duplicate-ID coverage to use a duplicate within its proper namespace.

Stage 2: selected discovery, raw-table readers and writing-path lookup now address
requested directories directly. A read tripwire first failed on an excluded
manifest; it now passes even when that manifest is broken. All 682 unit tests pass.

Stage 3: immutable build diagnostics now record external namespaces without
loading them. External edges/supports are omitted; concepts/modules and authored
prose remain. Loaded-namespace typos still fail. Support-row structure is checked
before pruning so malformed external links cannot hide errors. Seven focused
regressions first failed; all 688 unit tests now pass.

Stage 4: shared markup now parses nested/escaped cref labels and renders missing
targets as plain escaped text. Subject routes with missing declared requirements
or command/pointer targets are omitted; their loaded-namespace errors and syntax
are still checked. Common routes excluded by availability add no dependencies.
Three tutorial regressions and the browser markup regression first failed, then
passed. All 691 unit tests and the direct markup browser test pass; full-build
semantic snapshot remains identical and the viewer was rebuilt.


Stage 5: the CLI reports missing namespaces once, grouped by domain and reference
kind, with bounded source examples. Tutorial counts deduplicate routes. Library
loading is silent; immutable `KnowledgeBase.build_warnings` and derived
`missing_domains` expose the complete diagnostics. Programmatic generation can
supply `warning_handler` without changing the existing return tuple.

Generation, validation-only, DAG-only and module-only CLI modes now share source
selection. Editorial checks retain errors for loaded targets and do not relabel
intentional external prose as broken content. Five CLI regressions pass with a
broken excluded manifest, including validation plus generation without duplicate
warning reports. The warning formatter has direct count/group coverage. All 697
unit tests pass; the synthetic browser lane passed 269 cases (52 deselected).

Authoring/schema/architecture and tutorial guidance now describe this warning
policy. The older domain-split record is explicitly historical where it records
the initial strict policy. Quick Start needs no control changes: warnings are
build output, and the ordinary full viewer retains its content and navigation.


Stage 6 complete: all seven non-empty combinations of the production
domains now build. Independent fault-isolation regressions cover excluded CSV,
palette and graphics failures, while explicitly selecting each faulty package
still fails. The final unit suite passes 700 cases. Five focused browser checks
pass: GR-only desktop/phone rendering/navigation, independent future-domain
startup, and plain/nested-label rendering. The full browser lane passed all 323 cases
(542.65 s), including the authored desktop/mobile tutorial routes, real MathJax,
notes, study/read progress, personal-data exchange/sync, layouts and graph
interaction. No physical-device or live-account test is claimed.

The full build has zero missing-domain warnings and retains all seven baseline
snapshot hashes (content and exact SVGs, modules, tutorials, coordinates/revision,
node/edge records and relation metadata). GR-only keeps all 56 GR concepts and 6
modules, with 99 retained edges. Its warnings identify `math` and `sr`: 13 and 14
omitted edges respectively, plus two unlinked SR prose references. Loaded-ID
typos remain errors; no missing package is read to validate an external typo.


A fresh-process production GR build succeeded with all SR/MATHS metadata, data,
palette file reads and Python code imports explicitly forbidden. This checks the
actual graphics providers as well as the generic package-isolation regressions.
The ordinary full build reports no missing domains and retains 114 concepts and
282 edges. Its content, exact SVGs, modules, tutorials, graph records and published
layout all match the pre-change semantic snapshot. Generated full HTML was rebuilt
before browser verification and remains outside source commits.

Final documentation audit: 77 local links resolve; whitespace checks pass.
Production source count is 28,124 physical lines using the same combined core +
domain-code scope as the domain-split report (28,044 before this change): 80 more
lines overall, excluding tools, tests, authored data and generated output.
`viewer.js` remains 6,611 lines. No performance improvement is claimed.

All six stages are committed separately on `big-refactor`. No merge, release
version change or push was performed. The source commits exclude generated HTML.
