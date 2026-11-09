# MATHS-2: working tensor tools for GR

9 November 2026. Content pass addressing the open Tensor Calculus issue
(currently Content item 1.3 in `docs/issues.md`; referred to as 3.1 in discussion).
Runtime CSV is authoritative.

## Scope and sequence

The module teaches tensor type/order, pointwise fields, components, contractions
and coordinate changes. It assumes the vectors, covectors and charts of MATHS-1,
which can now be unfolded where needed. Metric and stress-energy tensors and the
index pattern of Riemann curvature motivate GR use, without assuming curvature
calculations or covariant differentiation. Abstract-index notation remains
available as an optional explanation after ordinary component notation.

The new worked material distinguishes tensor order from matrix rank and manifold
dimension; counts entries and independent symmetric metric components; computes a
metric pairing; expands sums; and checks coordinate rescaling and contraction.
It also explains bilinearity separately in each input. These foundations precede
the general multi-index transformation rule.

## Existing question coverage

All twelve questions and their options retain their IDs, text and marking.
This pass supplies the missing teaching rather than lowering the questions.

| Concept / question | Supporting blocks or local explanations |
| --- | --- |
| Tensor field q1: field versus tensor | definition; pointwise |
| Tensor field q2: scalar/vector/covector types | rank; definition; slots/vector-slot |
| Tensor field q3: contraction | pointwise/contraction |
| Tensor field q4: same field in different charts | not_component_array; transformation-law definition |
| Index notation q1: dummy label | summation |
| Index notation q2: two-dimensional sum | summation worked calculation |
| Index notation q3: free-index mismatch | summation/free and summation/check |
| Index notation q4: abstract versus component | definition/abstract, deliberately optional |
| Transformation law q1: opposite factors | definition; vector_covector/why-inverse |
| Transformation law q2: one-dimensional rescaling | rescaling |
| Transformation law q3: three index factors | higher_rank; borrowed tensor_field.rank |
| Transformation law q4: invariant contraction | not_invariant_components/cancel |

## Sharing and identity

Tensor fields borrow the MATHS-1 tangent/cotangent definitions. Index notation
borrows tensor type/rank and the dual-basis pairing. Transformation rules borrow
the chart Jacobian, covector definition, tensor rank and their own one-index rules.
Local algebra, counts and cautions use named slots. This dependency graph is
acyclic. Canonical source statements remain short and blue in the reader.

All existing block IDs, ordering, kinds and titles are retained. Four new blocks
supply rank, multilinear slots, a metric calculation and coordinate rescaling.
Two MATHS-1 sources gain short statements so they can be borrowed; their bodies
are unchanged. Concept/module membership, edges, graphics and questions remain
unchanged. Existing notes and read records keep their identities; contextual
recovery handles body changes without forcing notes to a different paragraph.
The module overview states its GR-oriented scope explicitly.

## Source and checks

Checked Tong's official [Introducing Differential Geometry](https://www.davidtong.org/teaching/general-relativity/grhtml/S2),
§2.3.3, with §2.3.1 for the covector pairing. Rank conventions are stated locally:
`(r,s)` is type, `r+s` is total order/rank. Numerical calculations and teaching
examples are authored here, not attributed to Tong.

Content tests check reusable foundations and stable questions. Browser checks
traverse all nine Maths concepts at phone and desktop widths, verify MathJax and
pane bounds, and exercise source/local notes and archive round trips. The module
remains a compact introduction to the tensor tools needed for GR, not a complete
tensor-calculus course.
