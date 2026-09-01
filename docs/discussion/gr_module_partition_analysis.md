# GR Module Partition Analysis

Captured on 2026-09-01. This is an authoring proposal, not runtime module
data. Its membership is recorded in `gr_module_partition_candidate.csv`.

## Method

The analysis uses the same non-absolute criteria as the SR partition:

1. minimise boundaries for `REQUIRES`, `DERIVES_FROM`, and
   `CONSTRUCTED_FROM`;
2. obtain an acyclic module graph for their union;
3. keep every module pedagogically coherent and readily explainable.

The graph contains 55 GR concepts and 80 selected GR-to-GR edges. Cross-domain
edges are excluded from the partition objective.

### Pruning before partitioning

Transitive pruning was considered before the module search so redundant long
edges would not distort the boundary objective. Only two direct edges have an
alternative path using the same relation:

- `Einstein tensor CONSTRUCTED_FROM Ricci tensor`, also reachable through
  `Ricci scalar`;
- `Curvature invariants CONSTRUCTED_FROM Riemann curvature tensor`, also
  reachable through `Ricci tensor`.

Both are retained. The Ricci tensor is a direct term in the Einstein tensor,
and curvature invariants include direct contractions of the Riemann tensor.
Eleven edges have alternatives only when relation types are mixed; these were
also retained because the paths do not preserve the direct edge meaning.
Consequently the module search uses the unchanged 80-edge graph.

This supports pruning before partition analysis as a workflow, but not blind
transitive reduction as an editorial policy.

## Quantitative Comparison

| Partition | Modules | Sizes | Boundary edges | Boundary share | Modularity | Combined DAG |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| Current layer-derived modules | 10 | 3–6 | 40 | 50.0% | 0.395 | Yes |
| Best observed automated result | 4 | 11–15 | 18 | 22.5% | 0.516 | Yes |
| Best observed five-module result | 5 | 7–14 | 22 | 27.5% | 0.504 | Yes |
| Best observed six-module result | 6 | 6–12 | 23 | 28.7% | 0.537 | Yes |
| Natural six-module coarsening | 6 | 6–14 | 29 | 36.2% | 0.442 | Yes |
| Proposed editorial partition | 6 | 6–14 | 28 | 35.0% | 0.455 | Yes |

The numerical optima mix concepts that belong to different explanations: for
example foundations with the Einstein tensor and cosmological action, or
black-hole singularities with connection machinery. Four or five modules are
therefore too coarse. Seven modules offers little editorial benefit over six.

The proposal is the natural six-module coarsening with the Einstein-Hilbert
action placed beside curvature. This makes the action the bridge from
curvature scalars to gravitational dynamics and removes one boundary edge.

## Proposed Modules

### GR-1 Foundations of Curved Spacetime

Fourteen concepts covering the equivalence principle, local free fall, tidal
gravity, the spacetime metric and its inverse and volume structures, line
elements, proper time, null curves, causal structure, local flatness, and the
signature convention.

This establishes what curved spacetime means operationally and geometrically.

### GR-2 Connections and Geodesics

Twelve concepts covering connections and Christoffel symbols, covariant
differentiation, compatibility and torsion, parallel transport, geodesics and
their action and equation, four-velocity, four-acceleration, and geodesic
deviation.

These concepts form one progression from comparing vectors at neighbouring
events to describing free motion and tidal separation.

### GR-3 Curvature and Gravitational Action

Seven concepts: Riemann, Ricci, scalar and Einstein curvature, the Bianchi
identity, curvature invariants, and the Einstein-Hilbert action.

The module constructs the curvature hierarchy and ends with the geometric
action used to obtain gravitational dynamics.

### GR-4 Matter and Einstein Equations

Ten concepts covering stress-energy and fluid matter, energy conditions and
covariant conservation, the Einstein equations and cosmological term,
stress-energy variation, and trace-reversed and vacuum forms.

This module explains how matter sources geometry and how the resulting field
equations are constrained and specialised.

### GR-5 Weak-Field Gravity

Six concepts covering the weak metric, Newtonian and post-Newtonian limits,
gravitational redshift, light deflection, and perihelion precession.

It connects the full theory to familiar gravity and its classical tests.

### GR-6 Schwarzschild Black Holes

Six concepts covering the Schwarzschild metric and radius, horizons,
coordinate and physical singularities, and effective orbital potentials.

This is a coherent exact-solution case study and a first black-hole module.

## Quotient Structure

Edge direction remains dependent to prerequisite. The non-empty boundaries
are:

```text
Schwarzschild black holes
  -> Curvature and gravitational action
  -> Connections and geodesics
  -> Foundations of curved spacetime

Weak-field gravity
  -> Matter and Einstein equations
  -> Connections and geodesics
  -> Foundations of curved spacetime

Matter and Einstein equations
  -> Curvature and gravitational action
  -> Connections and geodesics
  -> Foundations of curved spacetime

Curvature and gravitational action
  -> Connections and geodesics
  -> Foundations of curved spacetime

Connections and geodesics
  -> Foundations of curved spacetime
```

The quotient is acyclic. The first four modules form the main conceptual
spine; weak-field tests and Schwarzschild geometry are later applications.

## Boundary Cost

The 28 boundary edges comprise:

- 10 `REQUIRES`;
- 10 `DERIVES_FROM`;
- 8 `CONSTRUCTED_FROM`.

The largest boundary contains four edges from connections and motion to
foundational geometry. No boundary has more than four edges. Several
long-range edges remain, especially from the two application modules back to
metric, causal, and geodesic concepts. These are direct mathematical
dependencies, not safe transitive redundancies.

## Recommendation

Use the six-module proposal as the runtime candidate for visual review. Keep
the existing GR display identifiers temporarily, as with SR, and address the
global concept-layout scattering when layers are removed in the later layout
work.

Reproduce the proposal with:

```bash
conda run -n sr-kg python tools/analyse_module_partitions.py \
  --data-root data \
  --domain gr \
  --evaluate-members docs/discussion/gr_module_partition_candidate.csv \
  --evaluate-only \
  --show-boundary-edges
```
