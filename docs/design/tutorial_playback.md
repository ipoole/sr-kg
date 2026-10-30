# Native tutorial playback

Status: guided learner-facing playback implemented. Route loading and
validation, the shared semantic command interface, transient presentation
snapshot/replay, the Tutorials picker, narration card, semantic pointer,
target halo, block spotlight and temporary exploration are in place. Ordinary
viewer controls are unavailable during guided playback; the learner controls
it with Back, Next step, Explore from here and Exit. The viewer
contains an interface orientation and physics routes on rest energy and time
dilation, all available in
Tools or through a `?tutorial=<tutorial-id>` URL.

## Purpose

PhysicsKG should support curated routes through the live viewer. A route may
teach either the interface (for example, how Context works) or physics (for
example, a path from Lorentz symmetry to electromagnetism). During playback an
animated pointer identifies the relevant control, graph object, or details
block; PhysicsKG performs the corresponding action and displays short authored
commentary. Subject exposition remains in the authored Details blocks: tutorial
dialogue directs attention rather than duplicating the physics.

The route must remain a real PhysicsKG session rather than a recording or a
clone. It therefore adapts to desktop, phone and tablet layouts, current graph
positions, and future editorial changes.

## Design principles

1. **Record meaning, not coordinates.** A route says `select concept X` or
   `set context to Foundations`, never `click at (320, 180)`.
2. **Reuse the viewer model.** Tutorials drive the existing Selection, Context,
   Display scope, Module representation, Details and Camera operations. They do
   not create alternative versions of those operations.
3. **Keep tutorial state transient.** Starting a route snapshots the current
   presentation. Exiting restores it. Playback does not alter notes, study
   attempts, reading marks, saved layouts or any other personal data.
4. **Make every action visible.** A pointer and short click pulse show what the
   route is doing. The resulting UI state remains the authoritative
   explanation.
5. **Prefer self-paced playback.** The learner advances after reading each
   step. Timed autoplay and branching are deliberately deferred.
6. **Build for touch, keyboard and slow devices from the start.** The pointer is
   illustrative rather than the only indication of a target.
7. **Point to the source.** Physics commentary tells the learner what to read or
   notice in an authored block; it does not become a second textbook.

## User experience

### Finding a tutorial

Add **Tutorials** to Tools. Its compact list shows a title, one-sentence
description and approximate length. Tutorials may optionally be grouped as:

- **Using PhysicsKG** — interface orientation;
- **Physics routes** — curated journeys through the knowledge graph.

Selecting a tutorial displays its introduction and a **Start** button. Merely
opening the list changes no viewer state.

The Quick Start dialog launches the default interface route. A stable URL such
as `PhysicsKG.html?tutorial=using-physicskg` starts a named route directly,
allowing the public home page or external material to link to guided playback.
Each route introduction exposes its direct launch link for opening, bookmarking
or copying. The link keeps the viewer's current deployment URL and removes the
current concept/module fragment.

### Playback

A compact narration card remains in a fixed position at the lower edge of the
graph pane.

The card uses a lavender tint, purple commentary and a persistent Guided
tutorial label to distinguish its instructions from teaching content. Every
route's first card explains Next step, Explore, Resume and Exit, including
when playback starts through a direct URL. A demonstrated hover tooltip can
move the card to the upper edge to keep the preview readable.
Physics routes begin with a quiet introductory card; their graph demonstrations
start only after the user presses Next step.

It contains:

- tutorial title and `step / total`;
- one short heading and commentary;
- **Back**, **Next step**, **Explore from here** and **Exit**.

The stable card is preferable to commentary which jumps between targets. The
pointer supplies the spatial connection. On a narrow phone the card occupies
a dedicated strip at the bottom of the screen, below both panes. The workspace
reserves its measured height, keeping the existing graph-row sizing and leaving
the remaining area for Details. The strip remains available during
Explore; Exit restores the normal workspace. Desktop narration remains an
overlay, with Fit and Reveal accounting for its occupied space. The interface
tutorial expands and fits its module within one card. When the graph is hidden,
desktop narration is anchored to the workspace rather than the absent pane.

The temporary Fit++ arrangement notice is suppressed during guided playback,
when manual dragging is unavailable. It reappears during Explore.

A card may contain a sequence of visible semantic actions. Each action has its
own pointer target and a pause before the next action (500 ms by default,
up to 5 seconds when the result needs longer inspection).
The card's teaching point and commentary remain fixed throughout. Navigation
and Explore stay unavailable until all its actions finish. Existing single-action
cards retain their behaviour. Back replays the entire sequence without its
authored pauses; Explore/Resume restores its completed checkpoint, including
Full-tree choices and the temporary Fit++ coordinates.

For example:

```yaml
actions:
  - action: {command: expand-context-modules}
    pointer: {target: 'control:expand-context'}
    pause_ms: 500
  - action: {command: fit, value: context}
    pointer: {target: 'control:fit'}
  - action: {command: fit, value: context}
    pointer: {target: 'control:fit'}
```

For each visible action:

1. the narration card updates;
2. the target receives a visible halo and an accessible textual name;
3. the pointer moves to it;
4. a brief pulse represents the click or gesture;
5. the semantic action is invoked directly;
6. playback waits for rendering, camera movement and MathJax as applicable;
7. **Next** becomes available.

The action is not implemented by synthesising a click. Pointer animation and
the action are separate: the pointer explains; the viewer command performs.

### Back, exit and exploration

**Back** reconstructs the previous tutorial checkpoint by restoring the route's
initial snapshot and replaying commands silently up to that step. This is safer
than trying to define an inverse for every command.

**Exit** restores the pre-tutorial snapshot, including:

- selection and selection URL;
- Context rule and depth;
- Display scope;
- every module's folded or expanded representation;
- Details mode, active block and details scroll position;
- workspace split;
- camera centre and scale.

It also cancels tutorial highlights and pointer animation. Authored, personal
and temporary layout coordinates are never modified by a route.

Playback is deliberately guided: ordinary viewer interaction is blocked while
a route is active, leaving Back, Next step, Explore from here and Exit as the
available controls.
This avoids implying that a learner must guess which control to operate.

**Explore from here** snapshots the current tutorial checkpoint, removes the
interaction lock and hides tutorial emphasis while leaving the narration card
available. The learner may navigate, search and change any presentation
control. **Resume tutorial** restores Selection, Context, Display, module
representations, Details and Camera to the saved checkpoint. Notes, question
attempts, reading marks and other personal data created while exploring remain.

Browser Back while a route is active should first exit the tutorial and restore
the snapshot. Tutorial selections do not add browser-history entries.

## Route source format

Routes are authored content and belong under the data root, referenced by
`manifest.yaml`. A nested sequence is clearer in YAML than in several joined
CSV files, so the proposed source is `tutorials.yaml`. It is compiled into the
generated HTML with the other KB data.

Illustrative structure:

```yaml
schema_version: 1
tutorials:
  - tutorial_id: foundations-to-field-theory
    title: From spacetime to field theory
    category: physics
    summary: Follow the foundations used by relativistic field theory.
    sequence: 10
    steps:
      - step_id: begin-with-spacetime
        title: Begin with spacetime
        commentary: >-
          Special relativity starts by replacing separate space and time with
          one geometric structure.
        action:
          command: select
          target: concept:sr.spacetime
        pointer:
          target: graph:concept:sr.spacetime

      - step_id: reveal-foundations
        title: Ask for its foundations
        commentary: >-
          Foundations follows prerequisite, derivation and construction links
          towards the ideas supporting the selection.
        prepare:
          - command: set-display-scope
            value: context
        action:
          command: set-context
          preset: foundations
          depth: one-hop
        pointer:
          target: control:context

      - step_id: inspect-the-definition
        title: Read the definition
        commentary: The details pane develops the selected concept in blocks.
        action:
          command: open-details-block
          target: block:sr.spacetime.definition
        pointer:
          target: details:block:sr.spacetime.definition
```

`prepare` contains unanimated setup needed to make the principal action
meaningful. It should be used sparingly: unexplained state changes make a route
hard to follow. Each step has at most one principal animated action.

Commentary uses the viewer's supported text and MathJax syntax, not arbitrary
HTML.

## Semantic command vocabulary

The first implementation should deliberately expose a small, stable vocabulary:

| Command | Parameters | Existing viewer operation |
| --- | --- | --- |
| `select` | concept or module semantic ID | normal selection transition, without history |
| `set-display-scope` | `all`, `full`, `context` | All equally, Context + background, Context only |
| `set-context` | preset and depth | Context rule controls |
| `set-view` | `both`, `graph`, `details` | Workspace panes; preserves reading state |
| `set-module-representation` | module ID and `folded`/`expanded` | normal module representation transition |
| `set-all-module-representations` | `folded`/`expanded` | fold or expand all non-empty modules |
| `expand-context-modules` | none | expand only folded modules representing the current context |
| `fit` | `reveal`, `selection`, `context`, `displayed` | existing Fit operation |
| `open-details-block` | stable block ID | open and scroll to authored block |
| `open-study-questions` | none | open and scroll to the selected concept's questions without attempting them |
| `open-details-graphic` | none | open and scroll to the selected concept's graphic |
| `open-details-relationship` | `derived-from` or `where-used` | open and frame a relationship section |
| `set-relationship-full-tree` | relationship section and boolean `full_tree` | set the section's Full tree checkbox and refresh its contents |
| `show-relationship-in-graph` | Context preset and full-tree flag | sets context/depth, shows Both if necessary, selects Frame Context and fits after resizing; does not expand or contract |
| `show-graph-concept-hover` | concept ID | show the normal graph-hover preview without selecting |
| `show-graph-edge-hover` | source, relation and target concept IDs | emphasise and preview one visible edge |
| `show-tools-section` | stable section name | open Tools and the named section |
| `search` | query text | open Search and display matching concepts and modules |
| `close-search` | none | close Search without changing Selection |
| `wait` | bounded milliseconds | settling pause only, not exposition timing |

Fit++ may be used by a route because its temporary positions are restored on
Back, Explore/Resume and Exit. Note creation, question answering, personal
layout editing and Google Drive actions are also excluded: a tutorial may point
at them and explain them, but must not perform personal-data or authentication
actions.

## Target vocabulary

Pointer targets must also be semantic:

- `control:context`, `control:depth`, `control:fit`, `control:display-scope`;
- `control:module-fold:<module-id>`;
- `control:expand-context`;
- `graph:concept:<concept-id>` or `graph:module:<module-id>`;
- `graph:edge:<source-id>|<RELATION>|<target-id>`;
- `search:concept:<concept-id>` or `search:module:<module-id>`;
- `details:block:<block-id>`;
- `details:derived-from-show-graph`, `details:where-used-show-graph`;
- `details:derived-from-full-tree`, `details:where-used-full-tree`;
- `details:heading`, `details:contents`, `details:graphic`, `details:study-questions`;
- `tools:section:<section-name>`;
- `narration` for commentary-only steps.

DOM controls resolve to elements by a central target registry, not selectors
embedded in authored data. Graph targets resolve their current representation
and use vis-network's graph-to-DOM conversion. A concept represented by a folded
module therefore has a valid pointer target. Details targets open the required
container, scroll it into view, and then resolve the resulting element.

If a target is unavailable after its preparation commands, playback stops with
a useful message instead of guessing coordinates or silently skipping an
educational step.

## Playback controller

The tutorial controller is an orchestration layer, not another viewer-state
axis. It owns only:

- active tutorial and step;
- the pre-tutorial snapshot;
- whether a transition is running or paused;
- whether the learner is temporarily exploring, plus that step's snapshot;
- pointer, halo and narration presentation;
- a cancellation token for asynchronous settling.

Viewer operations should be callable through one semantic command interface.
Normal event handlers and the tutorial controller call the same operations with
an origin such as `user`, `history` or `tutorial`. Tutorial origin suppresses
history and personal-data writes but does not fork the behaviour itself.

Every command returns, or can be awaited through, a completion signal. In
particular, selection waits for graph projection and details rendering; fit
waits for the network animation (or immediate camera change on slow devices);
and a details-block command waits for MathJax and scrolling.

## Authoring and recording

Hand-author the first route. This will expose whether the command vocabulary and
commentary card are adequate before a recorder makes the format harder to
change.

A later developer-only **Record tutorial** mode can subscribe to the semantic
command interface. It records supported user actions as draft steps, using
stable IDs and enum values. Unsupported actions are reported rather than
captured as coordinates. The author then:

1. removes accidental or redundant steps;
2. adds step IDs, titles and commentary;
3. groups silent preparation actions where necessary;
4. validates and previews the route;
5. saves the YAML into the repository through the normal authoring workflow.

Recording is an authoring convenience, not part of the normal learner UI, and
does not write directly into the generated HTML's source data.

## Validation and compatibility

Generation should reject a route when:

- tutorial or step IDs are duplicated;
- a concept, module or block target is unknown;
- a command or enum value is unsupported;
- a graph object does not belong to the built domain subset;
- a target type is incompatible with its command;
- commentary or required labels are blank.

Sub-domain builds may either omit tutorials whose declared requirements are not
present or fail in strict mode. Each tutorial should declare its required
domains to make that decision explicit.

The route format has its own schema version. Semantic IDs make content routes
resilient to display-ID renumbering and most layout or responsive changes.

## Accessibility and performance

- The narration card is a labelled region; step changes use a polite live
  announcement rather than stealing focus.
- Back, Next and Exit are ordinary keyboard-operable buttons. Left/Right may be
  optional shortcuts when focus is not in a form control; Escape exits.
- The halo, narration and accessible target name carry the meaning; pointer
  motion is decorative.
- `prefers-reduced-motion` uses an immediate pointer relocation and static
  click emphasis.
- Pointer motion uses one compositor transform and no continuous graph redraw.
- A route advances only after the prior command settles. Rapid taps cannot
  queue multiple expensive graph renders.
- On older devices, camera changes inherit the viewer's existing no-animation
  policy.

## Testing strategy

Unit tests should cover schema loading, validation, command dispatch, snapshot
round-tripping and target resolution without launching a browser.

The fast browser lane should use one short synthetic route to verify:

1. opening the tutorial does not change viewer state;
2. Next performs the stated semantic command;
3. pointer and narration identify the resolved target;
4. Back deterministically reconstructs the prior checkpoint;
5. Exit exactly restores the captured state;
6. tutorial actions create no history or personal-data changes;
7. keyboard controls and reduced-motion behaviour work.

One full-data browser test should validate and complete an authored physics
route. The full suite need not replay every route: generation-time validation
provides most coverage without multiplying expensive browser cases.

## Proposed delivery stages

1. **Route schema and validation** — load `tutorials.yaml`, validate stable
   targets and inject routes into the generated viewer; author one short route.
2. **Semantic command interface** — expose the existing transitions to normal
   controls and tutorial playback without changing their behaviour.
3. **Transient presentation state** — capture, restore and deterministically
   replay a route without altering personal data.
4. **Basic playback** — tutorial list, narration card and Back/Next step/Exit;
   no animated pointer yet.
5. **Pointer and targeting** — DOM, graph and details target registries, halo,
   click pulse, responsive placement and reduced-motion handling.
6. **First substantive tutorials** — one interface orientation route and one
   physics route, refined on desktop, phone and old iPad. **Implemented.**
7. **Author recorder** — developer-only capture of supported semantic commands,
   after the format has proved stable.

## Deferred capabilities

- timed autoplay or voice narration;
- branching, quizzes or conditional steps;
- resuming tutorial progress across devices;
- route analytics;
- tutorial actions that write personal data;
- importing third-party recordings;
- an end-user route editor.

These can be added without weakening the core semantic route format if later
experience justifies them.
