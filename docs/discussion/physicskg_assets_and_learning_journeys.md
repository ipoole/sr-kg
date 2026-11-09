# PhysicsKG assets and learning journeys

Captured on 9 November 2026 from the conversation preceding the
[nested-explanations work](../design/nested_explanations_design.md).

**Provenance:** this is a reconstruction of the inventory and ensuing discussion,
not a verbatim transcript. The user's original three-part inventory and subsequent
exchange remain available, but the complete assistant response beginning “I'd
distinguish five main asset groups, with the supporting infrastructure listed
separately” is not available in the retained conversation. The five-group
organisation below is therefore reconstructed too.

## 1. Knowledge structure

The model records what the subject contains and how its parts relate:

- Domains, modules and concepts, with stable semantic identities and readable
  display numbering.
- Module membership and the distinction between subject organisation and
  dependency structure.
- Typed concept edges, including prerequisites, derivations, constructions,
  components, instances and other relationships.
- Explanations attached to those dependencies: why one concept needs another,
  rather than merely the fact that an edge exists.
- Typed content blocks, their identities and presentation order within an owner.
- References, source attribution and cross-references.

This is more than a graph for display. It can support dependency audits,
alternative explanatory routes, module organisation and learning sequences.
An edge alone does not supply the argument connecting its endpoints.

## 2. Explanatory and visual content

The authored collection supplies material with which to teach:

- Definitions, results, derivations, assumptions and conventions.
- Intuitions, analogies, examples, calculations, warnings and misconceptions.
- Historical notes and the scientific problems behind an idea.
- Concept and module graphics, recognisable graph icons, captions and notation.
- Optional clarifications and algebra embedded in an argument.
- Bibliographic support and explanations of the limits of a claim.

These are complementary forms of explanation. Intuition deserves explicit
support alongside mathematical reasoning. A graphic or example can help several
kinds of argument; explanatory paths need not be homogeneous in block type.

## 3. Learning activities and routes

The collection also contains ways to organise purposeful study:

- Study questions, calculation exercises, multiple-choice alternatives, model
  answers and feedback.
- Guided tutorials: curated sequences of reading targets and viewer actions.
- Sequential reading through modules and concepts.
- Explore/Resume, allowing a reader to investigate without losing the curated
  route.

Questions can reveal a missing prerequisite as well as test recall. Tutorials
can direct attention to existing content rather than duplicate the exposition
in their commentary. Eventually, some routes might be generated from dependency
structure; that is an ambition, not an existing general capability.

## 4. Exploration and presentation

The viewer supplies a visual and textual workspace:

- Graph and Details views, separately or together.
- Selection, Context rules and depth, foreground/background treatment and edge
  filtering.
- Overview, Context + background and Context-only graph presentations.
- Folded and expanded modules: seeing the overall organisation or its constituent
  concepts without discarding their relationship.
- Search, cross-references, concept/edge hover information and dependency lists.
- Camera framing, Fit, temporary Fit++ arrangements and personal layouts.
- Foldable content, mathematical rendering, scrolling, zooming and reading
  navigation.

The graph reveals relationships and the wider setting; Details carries the
argument. Their integration should preserve the predictable separation of
Selection, Context, representation and Camera.

## 5. Personal learning material and state

A reader brings another set of assets:

- Personal notes, mathematical annotations and personal content blocks.
- Reading ticks and question-completion records.
- Personal graph layouts and preferences.
- Portable personal-data export/import and optional Google Drive synchronisation.

This material belongs to the reader. Reusing an authored explanation should not
create duplicate progress records or expose personal notes as shared content.
Reading status is a useful reminder of previous study, not proof of mastery.

## Supporting infrastructure

Supporting these assets are the schema and validators; domain-owned data and
SVG-generation code; authoring and notation guidance; graph diagnostics; the
viewer generator; unit/browser tests and profiling tools; and exact-build release
and preview packaging. Stable IDs and transparent personal-data formats make
reuse and persistence possible across content and viewer changes.

These are enabling infrastructure rather than additional teaching content.

## Direction developed in the discussion

The two organising questions were **how we explain it** and **how we organise
the user's journey**.

Understanding a concept often requires traversing dependencies, while reading
is sequential. A learner may accept supporting results provisionally and return
to their foundations later, or study the foundations before continuing. The
underlying structure may be a DAG, with shared prerequisites, rather than a tree.

Recursively folded explanations give readers control over this traversal while
keeping the enclosing argument visible. They need explicit grammatical hooks
and finer links to particular blocks, rather than only whole concepts.
Reusable sources should be authored once; local clarifications such as “Algebra”
or “Why exactly?” can remain part of the enclosing explanation.

A short **statement** expresses the contribution a source makes to an argument;
its short **title** identifies it, and its **explanation** supplies the reasoning,
intuition, example or illustration. The statement should not be forced into the
title. Reusing a block and asserting a concept-level dependency are related but
distinct editorial choices.

A possible later graph integration would retain the top-level concept as the
Selection and highlight the concept currently being investigated through an
expanded explanation. This is a proposed reading-attention cue, not permission
for reading actions to silently change Context, Camera or the selected concept.
The first prototype deliberately concentrated on the text.

The subsequent accepted design and implementation are recorded in the
[nested-explanations design](../design/nested_explanations_design.md),
[minimum schema](../design/nested_explanations_schema.md) and
[shared reader](../design/nested_explanations_renderer.md). This discussion note
preserves the broader inventory and motivation; those documents define the
current contracts.
