# Nested explanations: minimum schema

**Earlier implementation:** this records the block-borrowing pilot, retained
while content is migrated. New authoring follows the agreed
[blocks and generated reading-tree design](nested_explanations_design.md):
self-contained blocks and graph-generated branches. Its implementation is next;
this document does not claim those rules are already enforced.

Stage 2, 8 November 2026. The Python loader/model contract is implemented, and
stage 3 adds the [shared reader](nested_explanations_renderer.md) on synthetic
content. Stage 4 applies it to the selected Maths pilot blocks. The
[design](nested_explanations_design.md) and [Maths draft](../../domains/math/docs/nested_explanations_pilot.md)
provide the intended reading experience. This document specifies storage and
identity, not a second content format or renderer.

## Sources stay in their existing tables

`content_blocks.csv` and `module_content_blocks.csv` keep their required columns,
row identities, owners, ordering and kinds. Add optional columns only where
needed:

| Column | Default | Contract |
| --- | --- | --- |
| `statement` | Empty | An explicitly authored, reusable result or contribution. Required only when another unit borrows this source. |
| `graphic` | Empty | `detail` for a `graphic` block wrapping its own concept/module's registered detail illustration and caption. Empty for every other kind. |

A statement is **as short as reasonably possible** while retaining what the
reader needs to use the result correctly. Put supporting reasoning, examples
and nonessential qualifications in the explanation. No fixed word limit and no
automatic extraction from a paragraph. Statements can use ordinary inline
markup, concept links and MathJax, but cannot contain explanation/reference
macros. A short title is still a separate field.

`body` remains required, holding explanatory prose and the macros below. For a
Graphic unit it holds any additional guidance about reading the picture; it does
not store SVG bytes or a duplicate registry caption. Graphic units need no new
asset registry or graphics table. Their canonical graphic locator is
`(owner_type, owner_id, detail)`. Text-only loaders need not generate SVGs.
The renderer will obtain the image and caption from that loaded owner's existing
payload. When converting native graphic presentation, replace the corresponding
implicit presentation rather than show the illustration twice.

All rows remain native top-level blocks in their owning concept/module. There
is no hidden-source table, row move or required CSV migration. A useful nested
local explanation can later become a borrowable block by explicit editorial
promotion; arbitrary paragraphs and anonymous legacy disclosures are not targets.

## Shared reference in a body

```text
\explain{chart}{math.coordinate_chart.definition}{Coordinate chart}{What does the board's chart supply?}
```

The four arguments are:

1. **Slot:** a short stable name for this use within its immediate parent.
2. **Target:** the canonical `block_id`, never a display number or a copied body.
3. **Target label:** a short source-side label for attribution/fallback when that
   domain is excluded. The loaded source supplies its authoritative title/owner.
4. **Hook:** the locally authored question/title inviting expansion. Surrounding
   prose supplies any grammatical bridge.

Labels and hooks are nonempty inline text, optionally with maths; neither may
contain further explanation/reference macros. A slot matches
`[a-z][a-z0-9_-]*`. Siblings, whether references or local explanations, must not
reuse a slot. The same slot can be used inside different parents.

A valid loaded target must have a nonempty `statement`. There is one canonical
statement/body, not an override per reference. The local hook describes purpose;
no reference-role enum is needed by this pilot. Source `kind` remains independent:
a Derivation can use an Intuition, Graphic or Worked example.

The reference is a structural content insertion, not an inline concept link:
place it between prose passages, outside maths and other macro arguments. Use
`\cref` for ordinary inline navigation. References do not create or modify
concept edges.

## Local recursive explanation

```text
\explanation{algebra}{Where does the component sum come from?}{
  Apply linearity and the dual-basis rule.
  \explanation{delta}{What does the delta do?}{It selects matching components.}
}
```

Each local explanation has a slot, short title and nonempty body. Its body may
contain text, shared references and more local explanations. It inherits the
source block's owner; it is not an independent global source or a separately
persisted reading mark. Named local note anchors use the enclosing block ID plus
a slot path in the existing `sectionKey` field, not a new global block ID. New local nesting is limited to 100 levels
so a pathological authored input produces a useful loading error.

Existing `\optional_details{Title}{Body}` is normalised to the **same local
explanation node**. Its generated `~legacy-N` slot is positional, not an authored
identity. It supports transient page state, not durable links. Existing malformed
legacy syntax remains available to the established editorial diagnostics as raw
text; malformed new syntax fails loading. This retains useful multi-error reports
without adding a legacy rendering path.

## One normalised source model

`KnowledgeBase.content_units` maps every concept/module block ID to one immutable
`ContentUnit` containing:

- `source_id`, `owner_type`, `owner_id`, `kind`, `title`, `statement`;
- ordered `parts`: text, reference, or recursive local explanation;
- optional registered graphic locator.

Plain text, mathematics and existing inline markup are retained, rather than
pre-rendered HTML. Macro parsing is brace-aware. Existing blocks with no new
columns map to exactly this model with an empty statement. Missing optional
columns in mixed-domain collections map to empty strings, never `NaN`.

`content_unit_data()` returns this source registry as JSON-compatible records.
Reference parts contain only their slot, target ID, fallback label and hook;
they do not contain recursively copied source bodies. Native placement/order
still comes from the existing concept/module block lists. Existing native viewer
payloads retain their previous shape unless new optional fields are supplied.
The shared reader indexes these native records and uses the same recursive model.
Its wire representation retains each verbatim body once, preserving existing
note anchors. The extended browser text parser normalises it on rendering;
cross-language tests check agreement with the Python model. The parsed registry
is available to Python callers without shipping a second copy of every body.

## Source identity versus occurrence identity

A source is identified by its durable `block_id`. Existing notes and read marks
continue to use that native identity, and existing question IDs are untouched.

A reading occurrence has a transient `OccurrencePath`:

```text
root source ID
  → (reference slot, target source ID)
  → (local explanation slot, no new source)
  → (reference slot, target source ID)
```

Its key is a JSON array encoding, avoiding ambiguous delimiter concatenation.
Two routes to the same source have different keys; repeating a route yields the
same key. Including target IDs prevents retargeting a slot from inheriting the
old target's open state. Source data is never copied into personal storage.

Fold state is local to these occurrence paths for the active page visit. Closing
a parent hides rather than destroys its descendants. Ordinary rerender/sync must
preserve the current page's open state. Nothing here introduces synchronised
study journeys, nested completion, new notes controls or graph attention tracking.
Those are renderer/future feature contracts, not effects of source resolution.

## Resolution, cycles and domain boundaries

Validate every reference, including ones inside folded local explanations:

- Duplicate source IDs across concept/module tables are errors.
- An unknown target inside a loaded namespace is an authoring error, even if its
  concept exists. A loaded target without a statement is also an error.
- A target in an excluded namespace produces a `content-reference` build warning.
  Keep the reference's hook and target label for a readable unavailable state;
  there is no target statement to display and no expansion or hidden lookup.
- Do not inspect an excluded package to discover whether its target exists.
  Include that domain in a full validation build to catch external typos.

Loading validates a flat source registry without recursively expanding references.
At reading time `resolve(reference, ancestors=...)` returns:

| State | Meaning / intended presentation |
| --- | --- |
| `available` | Show the target statement and a normally folded explanation. |
| `cycle` | Target is on this occurrence's ancestor chain. Show its statement and an “Already explained above” return link; do not expand again. |
| `unavailable` | Domain excluded. Show source-side hook/label and an unavailable explanation notice. |

A source used on two sibling routes is not a cycle. No global “already visited”
set suppresses a useful second occurrence. Validation does not require the source
reference graph to be a DAG; runtime ancestor checking terminates cycles.

## Stage-2 checks and limits

Tests cover brace-aware nesting and equations, legacy normalisation, malformed
new syntax, duplicate slots/sources, statement requirements, heterogeneous and
module-owned sources, Graphic locators, cycles versus sibling reuse, occurrence
keys, mixed-column domain loading and strict selected-domain isolation. Existing
KB content and concept edges remain unchanged. Stage-3 tests cover browser
interaction, native versus borrowed presentation, personal-state preservation
through rerenders and rendered graphic lookup; see the reader document above.
