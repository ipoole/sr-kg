# Concept details and generated reading trees: paper prototype

11 November 2026 · standalone prototype 4.6.14.

Open [the HTML](graph_aligned_reading_mockup.html), or:
https://physicskg.org/preview/graph-aligned-reading.html

The page mocks up MATHS-2.3 Tensor transformation law: local knowledge blocks,
then a divider and two generated reading-tree cards. The design document has
not been revised. Production viewer code, schema and Maths data are unchanged;
no personal data is read or saved.

## Presentation

Every block has a kind, meaningful title, short blue statement and body. The
statement and expandable title/body share one light box, tinted by kind using
the real viewer's palette (including its pale label/mark colours for Definition
and Explanation). Every body starts folded, including Definitions. Local
clarifications can be nested, but a block body never calls another owned block.
Clarifications have a smaller, subdued title and body, without a statement field
or badge. Their former statement text is ordinary prose inside the body.
Ordinary references still preview Definitions.

The two reading-tree cards use the same statement/title/body arrangement, with
separate tints, a stronger outline and restrained raised shadow. Their authored
recipe metadata supplies a generic title and statement, with `{concept}` replaced
by the root concept's name:

- **Full derivation tree:** “Trace the derivation of {concept} through its
  supporting concepts, recursively.” Selects Definition, Derivation; follows
  DERIVES_FROM and CONSTRUCTED_FROM.
- **Detailed teaching tree:** “Explore {concept} through definitions,
  explanations, intuition and examples, following its foundational dependencies.”
  Selects Definition, Explanation, Intuition, Example; also follows REQUIRES.

Within a kind, authored block order is retained. There is no preferred-kind or
first-block-open exception. A concept's selected blocks precede all eligible graph
branches. Root blocks deliberately appear again inside each tree. A missing kind
is simply absent; when no selected kinds exist, a notice appears and dependencies
remain available. Tensor transformation law has two Examples; Tangent space has
an Intuition block.

Stronger labelled concept containers distinguish sibling concepts and group their
blocks and dependencies. A bold heading gives the full destination code/name
first, including on phones. Its button is the disclosure control; the incoming
justification remains visible directly below whether the body is open or closed.
For example “MATHS-2.3 is constructed from this concept because:” precedes the teal
justification. Desktop adds the source concept name; phones retain its code.
The former “Why this concept?” border legend is removed. There is no separate
Definition statement preview: it appears only in the owned Definition block,
visible once the concept is opened. The child heading is not repeated inside.

Native details retains occurrence folding state, controlled by the separate
heading button with synchronised aria-expanded/aria-controls. The justification
belongs to the incoming edge occurrence; another route to the same concept can
supply a different justification. Cycle endpoints have a named heading without a
disclosure button. All concept bodies start folded.

## Map and interactions

Both reading-tree cards can stay open independently. Each has its own depth and
open branches. Opening/using one changes the mock map to that tree's context but
does not rebuild the other tree. Opening ordinary local content does not change
the map context. The automatic map relationship is labelled as prototype behaviour;
optional synchronisation with the production graph is not implemented here.

Derivation reaches four concepts/three edges; Teaching reaches eight concepts/ten
edges. The edges are unchanged. Teal justifications propose clearer wording;
original notes remain in map tooltips. No author chooses a reading route.

Depth uses shortest graph distance. Boundaries offer extension. Changing depth
rebuilds only that tree. Repeated concepts have independent occurrences; ancestor
cycles stop. Alternative proofs await a concrete example. Amber reading attention
moves while the blue root selection remains fixed.

Each tree's Fold supports button closes all its block, clarification and concept
disclosures, without closing the outer card or affecting local content/the other
tree. Capped indentation and full-width focus/Return preserve existing DOM and
folds. Full-width buttons start at nesting level two: the first supporting concept and
first local clarification at the root have no button; deeper concepts and local
clarifications can offer it. This is presentation depth, not shortest graph hops.
Definition references support hover, keyboard focus and tap. The map starts
folded on phones.

## Checks

Focused phone/desktop browser checks cover tinted boxed statements and titles,
all-folded defaults, independent cards, Definition-first selection, multiple
Examples, exact graph parity at all depths, generated branch coverage, dependency
wording, full-width focus/Return, keyboard use, equation rendering and page width.
The unit suite also passes. Publication preserves every other hosted file,
including both existing viewers and the earlier paper prototypes.
