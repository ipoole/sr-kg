# Simplified Content Block Strategy

Captured on 2026-07-27. Revised on 2026-07-28.

## Decision

For the next practical content phase, step back from the fine-grained
content-graph idea.

The durable knowledge base should stay simple:

```text
Concepts
Concept edges
Layers / display ordering
Content blocks
Study questions
References
Graphics
```

Content blocks should remain attached to concepts. For now, the authored KB
should hold only simple block metadata:

```text
block_id
concept_id
sequence
kind
title
body
```

Every content block should have a short, non-empty `title`. The viewer may or
may not display the title in a particular view, but the title gives the block a
clear editorial handle. It can also support folded-section handles, inline
subheadings, local tables of contents, search results, notes, references, and
review workflows.

The `kind` vocabulary should be semantic, not presentational. It should describe
what the block is, not how the viewer happens to render it. The initial accepted
kinds are:

```text
definition
intuition
explanation
construction
derivation
derivation_step
example
worked_example
misconception
warning
historical_note
summary
```

The meaning of each accepted kind is recorded in `KB_SCHEMA.md`. Expand the
vocabulary only when content curation exposes a recurring need. Multiple blocks
of the same kind within one concept are allowed and expected.

## Viewer Policy

Visibility and disclosure should not be authored KB fields for now.

Fields such as:

```text
default_visibility
disclosure_mode
depth
detail
```

should not be added to the source KB at this stage. These are viewer policy
questions. The app can hard-wire mappings from block `kind` to presentation
behaviour while the model is still evolving.

For example, the viewer might eventually decide:

```text
derivation_step -> folded or inline
misconception -> visually highlighted
historical_note -> tucked away
worked_example -> shown after derivation
```

Those choices belong initially in the viewer implementation, not in the authored
KB. This is analogous to a stylesheet or LaTeX style: the KB supplies semantic
block kinds, and the viewer maps those kinds to presentation.

The viewer should not be forced to render blocks strictly in source sequence in
every view. The `sequence` field is the authored narrative order within a
concept. A viewer may still group references at the end, fold examples, pull
misconceptions into callouts, generate a local contents list, or show a
kind-filtered view.

## Curation Workflow

The next content-building workflow should be:

1. Write a deep, detailed exposition for one concept.
2. Split it manually into ordered content blocks.
3. Assign each block a simple `kind`.
4. Put those blocks directly into the KB.
5. Let the viewer decide presentation from `kind`.

The block `sequence` can come directly from the exposition order. We do not need
topological sorting, graph analysis, or derived ordering for the first step.

Curation should proceed concept by concept, starting from the earliest/foundation
concepts and working upward through the atlas. For each concept, aim to finish
the coherent unit before moving on:

```text
exposition
block split
kind assignment
study questions
references
concept edges
graphics review where relevant
```

Concept edges added during this process should mostly point to earlier concepts,
though this is a guideline rather than a hard rule.

## What We Are Not Doing Yet

For the immediate next phase, do not add:

```text
fine-grained block graph
block-level edge types
content_block_edges.csv
topological ordering
global PL / depth / detail fields
graph-derived visibility
block-edge data in the JS viewer model
parent_block_id / hierarchical content blocks
```

The fine-grained graph experiment remains useful design exploration,
particularly for possible future derivation tracing. But it is not the path for
the immediate content migration.

Hierarchical content blocks are feasible later if flat ordered blocks become
insufficient. A future `parent_block_id` could allow whole sections to fold,
hide, or move together. Do not add it until real curated content demonstrates
the need.

Richer atlas-level concept edge types also remain deferred. The current graph
uses `PREREQUISITE`, `DERIVES_FROM`, and `RELATED`. During curation, note where
`RELATED` feels too vague. Promote only recurring relationships into new edge
types, such as:

```text
SPECIAL_CASE_OF
GENERALIZES
MOTIVATES
CONTRASTS_WITH
EXAMPLE_OF
USES_NOTATION_FROM
```

## Principle

The concept graph is the atlas. Content blocks are the readable pages. Block
kind is authored meaning; visibility and disclosure are viewer policy.
