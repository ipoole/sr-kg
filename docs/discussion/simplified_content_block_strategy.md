# Simplified Content Block Strategy

Captured on 2026-07-27.

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

The `kind` vocabulary still needs design, but it should be semantic. Candidate
kinds include:

```text
definition
intuition
derivation
derivation_step
example
worked_example
misconception
warning
historical_note
summary
```

## Viewer Policy

Visibility and disclosure should not be authored KB fields for now.

Fields such as:

```text
default_visibility
disclosure_mode
depth
detail
pedagogical_level
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
KB.

## Curation Workflow

The next content-building workflow should be:

1. Write a deep, detailed exposition for one concept.
2. Split it manually into ordered content blocks.
3. Assign each block a simple `kind`.
4. Put those blocks directly into the KB.
5. Let the viewer decide presentation from `kind`.

The block `sequence` can come directly from the exposition order. We do not need
topological sorting, graph analysis, or derived ordering for the first step.

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
```

The fine-grained graph experiment remains useful design exploration,
particularly for possible future derivation tracing. But it is not the path for
the immediate content migration.

## Principle

The concept graph is the atlas. Content blocks are the readable pages. Block
kind is authored meaning; visibility and disclosure are viewer policy.

