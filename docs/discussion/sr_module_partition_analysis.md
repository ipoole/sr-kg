# SR Module Partition Analysis

Captured on 2026-08-31. This is an authoring proposal, not runtime module data.
The candidate membership is recorded in
`docs/discussion/sr_module_partition_candidate.csv` so the analysis is
reproducible without changing `data/module_members.csv`.

## Criteria

The proposal balances three non-absolute aims:

1. minimise boundary edges for `REQUIRES`, `DERIVES_FROM`, and
   `CONSTRUCTED_FROM`;
2. obtain an acyclic quotient graph for their union;
3. make every module pedagogically coherent and easy to explain.

The initial search treated the 47 SR concepts and 96 selected SR-to-SR edges
in isolation. Cross-domain edges are future module-support relationships, not
pressures on SR concept ownership. All three relations have equal weight, so
weighted and raw boundary counts coincide.

## Tooling

`srkg.module_partitioning` supplies domain filtering, partition metrics,
boundary-pair and cycle diagnostics, deterministic candidate generation,
size constraints, editorial-seed refinement, and Markdown reporting.
`tools/analyse_module_partitions.py` is its command-line interface. It never
rewrites authored KB data.

Candidate generation combines:

- exact-count greedy modularity communities;
- topological strata as an acyclic baseline;
- balanced deterministic random restarts;
- coarsening of existing or supplied authored memberships;
- local concept moves under size, boundary, balance, and cycle penalties.

This is deliberately an advisory search. Module names and pedagogical
coherence remain editorial decisions.

## Quantitative Comparison

| Partition | Modules | Sizes | Boundary edges | Boundary share | Modularity | Combined DAG |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| Current layer-derived SR modules | 11 | 2–7 | 65 | 67.7% | 0.199 | Yes |
| Best observed automated DAG result | 4 | 7–15 | 26 | 27.1% | 0.437 | Yes |
| Best observed five-module DAG refinement | 5 | 5–13 | 28 | 29.2% | 0.477 | Yes |
| Proposed editorial partition, before transitive pruning | 5 | 6–13 | 33 | 34.4% | 0.421 | Yes |
| Proposed editorial partition, after transitive pruning | 5 | 6–13 | 28 | 32.2% | 0.438 | Yes |

The original layer-derived partition internalised only 31 of the initial
selected edges. Before pruning, the proposal internalised 63, slightly more
than double, while reducing the visible SR module count from eleven to five.
The later transitive-edge pass removed nine direct edges without changing the
reachability of any of the three relations. The resulting graph has 87 edges,
of which 59 are internal to a module.

The numerically stronger automated candidates were rejected as final answers.
Typical anomalies included Electric field in a spacetime-foundations module,
Poynting vector in particle mechanics, or Position four-vector and Scalar
field in a general foundations module. The proposed partition accepts five
additional boundary edges relative to the best observed five-module DAG
candidate in exchange for clearer ownership.

## Proposed Modules

### SR-1 Spacetime and Lorentz Symmetry

Eleven concepts: the two postulates and inertial frames; events and locality;
the metric, interval, Lorentz transformations, light cones, Minkowski diagrams,
and Lorentz invariance.

This module establishes the geometry and symmetry structure on which the rest
of the SR graph depends.

### SR-2 Relativistic Particle Mechanics

Six concepts: proper time, four-vectors, position four-vector, velocity
four-vector, momentum four-vector, and mass-energy equivalence.

These form one compact derivational chain from spacetime geometry to particle
energy and momentum.

### SR-3 Action and Field Theory

Nine concepts: Lagrangian, action principle, Euler–Lagrange equations,
canonical momentum, Hamiltonian formalism, scalar field, vector field, field
Lagrangian, and field equations.

The common theme is the variational machinery used to formulate particle and
field dynamics. Noether's theorem moves to the conservation module because its
principal role in this atlas is to explain conserved currents and
energy–momentum.

### SR-4 Covariant Electromagnetism

Thirteen concepts: vector potential, field tensor, electric field, magnetic
field, electromagnetic field, gauge invariance, minimal coupling, Lorentz
force law, Lorenz gauge, Poynting vector, electromagnetic stress-energy,
electromagnetic energy density, and gauge fixing.

This is the largest module, but it has a clear object-centred identity: the
covariant electromagnetic field, its gauge description, its coupling to
matter, and its local energy–momentum content.

### SR-5 Field Dynamics and Radiation

Eight concepts: Noether's theorem, four-current, Maxwell's equations, charge
conservation, energy–momentum tensor, wave equation, electromagnetic waves, and
radiation reaction.

This module follows the path from field equations and symmetries to conserved
quantities, propagation, and radiative back-reaction. It depends on the
electromagnetic structures in module 4 rather than duplicating them.

## Quotient Structure

Edge direction remains dependent to prerequisite. The non-empty module
boundary pairs are:

```text
Field dynamics and radiation
  -> Covariant electromagnetism
  -> Action and field theory
  -> Relativistic particle mechanics
  -> Spacetime and Lorentz symmetry

Covariant electromagnetism
  -> Action and field theory
  -> Relativistic particle mechanics
  -> Spacetime and Lorentz symmetry

Action and field theory
  -> Relativistic particle mechanics
  -> Spacetime and Lorentz symmetry

Relativistic particle mechanics
  -> Spacetime and Lorentz symmetry
```

This quotient is acyclic. A broad learning order is therefore foundations,
kinematics and variational methods, electromagnetic structure, then field
dynamics and radiation. The graph still permits non-linear study within that
outline.

## Boundary Cost

After transitive pruning, the 28 boundary edges comprise:

- 21 `REQUIRES`;
- 6 `DERIVES_FROM`;
- 1 `CONSTRUCTED_FROM`.

The largest boundary is from field dynamics to electromagnetic structure:
five edges. These remain pedagogically intelligible: field dynamics and
radiation use electromagnetic structure, while radiation reaction presupposes
the Lorentz force.

Other boundaries express similarly natural prerequisite transitions. There is
no residual edge whose direction has to be reversed or ignored to obtain the
module DAG.

The direct `Wave equation REQUIRES Metric tensor` edge was removed during
layout review. Its prerequisite reachability remains explicit through the
compact conceptual chain `Wave equation -> Maxwell's equations -> Field tensor
-> Metric tensor`, while removing the sole direct boundary from module SR-5 to
SR-1.

## Remaining Editorial Questions

- Is the thirteen-concept electromagnetic-structure module comfortable when
  expanded in the viewer, or should stress-energy move back beside conservation
  despite the fifteen-edge seam that creates?
- Is “Field Dynamics, Conservation, And Radiation” sufficiently focused, or
  does its title need tightening?
- Should Lorentz invariance remain an explicit capstone inside spacetime
  foundations, as proposed, or become module-level introductory material?

These are suitable review questions because they concern explanation and user
experience, not defects hidden by the graph metrics.

## Reproduction

Evaluate the proposal and show every concrete boundary edge with:

```bash
conda run -n sr-kg python tools/analyse_module_partitions.py \
  --data-root data \
  --domain sr \
  --evaluate-members docs/discussion/sr_module_partition_candidate.csv \
  --evaluate-only \
  --show-boundary-edges
```

Run a fresh comparison with:

```bash
conda run -n sr-kg python tools/analyse_module_partitions.py \
  --data-root data \
  --domain sr \
  --module-counts 4 5 6 \
  --min-size 5 \
  --max-size 15
```
