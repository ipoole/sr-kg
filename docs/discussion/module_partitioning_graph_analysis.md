# Module Partitioning Graph Analysis

Captured on 2026-08-18.

## Context

Adding General Relativity will make the concept graph much larger than the
current Special Relativity and Classical Fields graph. The viewer will probably
need collapsible and expandable subgraphs.

The preferred long-term model is explicit authored modules, not runtime
auto-clustering. Graph analysis can still be useful as an authoring aid:

- suggest candidate module boundaries
- identify concepts that sit awkwardly across boundaries
- show which inter-module links make a proposed module graph cyclic
- guide content or edge revisions before module assignments are made durable

The current SR and Classical Fields graph was analysed as a pilot.

## Source Graph

Current data files:

- `data/nodes.csv`
- `data/edges.csv`
- `data/edges_key.csv`

Counts at the time of analysis:

| Metric | Value |
| --- | ---: |
| Concepts | 47 |
| Edges | 141 |
| Connected components, undirected | 1 |

Relation counts:

| Relation | Count |
| --- | ---: |
| `REQUIRES` | 52 |
| `DERIVES_FROM` | 37 |
| `RELATED` | 33 |
| `CONSTRUCTED_FROM` | 8 |
| `INSTANCE_OF` | 7 |
| `COMPONENT_OF` | 4 |

For community detection, the graph was treated as undirected because the
question was concept cohesion rather than prerequisite order. A weighted pass
downweighted `RELATED` edges to `0.35`, treating them as weaker associative
links.

## Current Layers Are Not Natural Modules

Using the existing pedagogical layers as a partition gives low modularity:

| Partition | Approximate modularity |
| --- | ---: |
| Existing levels/layers | 0.24 |
| Graph-derived communities | 0.42-0.45 |

This supports the intuition that levels encode pedagogical sequence, not
collapsible thematic subgraphs. Modules should therefore not be formed
mechanically from levels.

## Initial Graph-Derived Modules

A weighted Louvain/community pass suggested the following six-module sketch.
This is an advisory grouping, not a proposed source-of-truth schema.

### M1 SR Foundations And Spacetime

- `1.1` Inertial frames
- `1.2` Constancy of the speed of light
- `1.3` Principle of relativity
- `2.2` Spacetime event
- `2.3` Principle of locality
- `3.2` Spacetime interval
- `3.3` Lorentz transformations
- `3.4` Light cone
- `3.5` Minkowski diagram
- `4.1` Proper time
- `6.1` Scalar field
- `6.2` Vector field

### M2 Four-Vectors And Relativistic Mechanics

- `3.1` Metric tensor
- `4.2` Four-vectors
- `4.3` Position four-vector
- `4.4` Velocity four-vector
- `4.5` Momentum four-vector
- `4.6` Mass-energy equivalence
- `8.4` Lorentz force law
- `9.3` Stress-energy of EM field
- `11.1` Lorentz invariance

### M3 Variational Principles And Field Equations

- `5.1` Lagrangian
- `5.2` Action principle
- `5.3` Euler-Lagrange equations
- `5.4` Canonical momentum
- `5.5` Hamiltonian formalism
- `5.6` Noether's theorem
- `6.3` Field Lagrangian
- `6.4` Field equations

### M4 Potentials, Gauge, And Coupling

- `7.1` Vector potential `\(A_\mu\)`
- `7.2` Field tensor `\(F_{\mu\nu}\)`
- `8.1` Gauge invariance
- `8.3` Minimal coupling
- `8.6` Lorenz gauge
- `11.2` Gauge fixing

### M5 Electromagnetic Field, Stress-Energy, And Radiation

- `7.3` Electric field
- `7.4` Magnetic field
- `7.5` Electromagnetic field
- `9.1` Energy-momentum tensor
- `9.2` Momentum density (Poynting vector)
- `9.4` Energy density of EM field
- `10.2` Electromagnetic waves
- `10.3` Radiation reaction

### M6 Maxwell Dynamics And Charge Conservation

- `7.6` Four-current
- `7.7` Maxwell's equations
- `8.5` Charge conservation
- `10.1` Wave equation

## DAG Checks On The Initial Modules

The analysis contracted each proposed module to a single node and tested the
resulting module graph for cycles. Edge direction is the existing concept-graph
direction: dependent concept points to prerequisite/source concept. Therefore a
learning order is roughly the reverse topological order.

For the initial six modules:

| Relation set | Module quotient DAG? | Notes |
| --- | --- | --- |
| `REQUIRES` | no | Several cycles |
| `DERIVES_FROM` | no | One M1/M2 cycle |
| `CONSTRUCTED_FROM` | yes | No cycles |
| `COMPONENT_OF` | yes | No cycles |
| `INSTANCE_OF` | yes | No cycles |
| all directed relations | no | Many cycles |

For the combined set `{DERIVES_FROM, CONSTRUCTED_FROM}`, there was one
module-level cycle:

```text
M1 SR Foundations And Spacetime
  -> M2 Four-Vectors And Relativistic Mechanics
  -> M1 SR Foundations And Spacetime
```

The edges causing `M1 -> M2` were:

```text
3.3 Lorentz transformations DERIVES_FROM 3.1 Metric tensor
3.2 Spacetime interval DERIVES_FROM 3.1 Metric tensor
```

The edges causing `M2 -> M1` were:

```text
4.4 Velocity four-vector DERIVES_FROM 4.1 Proper time
11.1 Lorentz invariance DERIVES_FROM 3.3 Lorentz transformations
```

No `CONSTRUCTED_FROM` edge participated in that cycle.

## Small Repair For Derivation/Construction DAG

Moving `3.1 Metric tensor` from M2 to M1 removes the
`{DERIVES_FROM, CONSTRUCTED_FROM}` module cycle.

This is also pedagogically plausible: the metric tensor belongs naturally with
spacetime geometry rather than with four-vector mechanics.

The revised first two modules are:

### M1 SR Foundations And Spacetime Geometry

- `1.1` Inertial frames
- `1.2` Constancy of the speed of light
- `1.3` Principle of relativity
- `2.2` Spacetime event
- `2.3` Principle of locality
- `3.1` Metric tensor
- `3.2` Spacetime interval
- `3.3` Lorentz transformations
- `3.4` Light cone
- `3.5` Minkowski diagram
- `4.1` Proper time
- `6.1` Scalar field
- `6.2` Vector field

### M2 Four-Vectors And Relativistic Mechanics

- `4.2` Four-vectors
- `4.3` Position four-vector
- `4.4` Velocity four-vector
- `4.5` Momentum four-vector
- `4.6` Mass-energy equivalence
- `8.4` Lorentz force law
- `9.3` Stress-energy of EM field
- `11.1` Lorentz invariance

After this move, the cross edges between M2 and M1 point only from M2 to M1
under `{DERIVES_FROM, CONSTRUCTED_FROM}`:

```text
4.4 Velocity four-vector DERIVES_FROM 4.1 Proper time
4.6 Mass-energy equivalence DERIVES_FROM 3.1 Metric tensor
9.3 Stress-energy of EM field CONSTRUCTED_FROM 3.1 Metric tensor
11.1 Lorentz invariance DERIVES_FROM 3.3 Lorentz transformations
11.1 Lorentz invariance DERIVES_FROM 3.1 Metric tensor
```

## REQUIRES Remains Cyclic

Using the revised assignment above, the `REQUIRES` quotient still has cycles:

| Metric | Value |
| --- | ---: |
| `REQUIRES` edges | 52 |
| Internal to modules | 29 |
| Cross-module | 23 |
| Module-level edges | 13 |
| Module-level cycles | 5 |

Important cycle causes include:

```text
M1 -> M2
6.2 Vector field REQUIRES 4.2 Four-vectors
```

versus:

```text
M2 -> M1
4.2 Four-vectors REQUIRES 3.3 Lorentz transformations
4.3 Position four-vector REQUIRES 2.2 Spacetime event
4.3 Position four-vector REQUIRES 3.3 Lorentz transformations
4.5 Momentum four-vector REQUIRES 3.1 Metric tensor
```

and:

```text
M4 -> M5
8.6 Lorenz gauge REQUIRES 7.5 Electromagnetic field
8.1 Gauge invariance REQUIRES 7.5 Electromagnetic field
11.2 Gauge fixing REQUIRES 7.5 Electromagnetic field
```

versus:

```text
M5 -> M4
7.5 Electromagnetic field REQUIRES 7.2 Field tensor
```

This suggests that `REQUIRES` is useful for identifying awkward module
boundaries, but too broad to require strict acyclicity for authored thematic
modules.

## Acyclic Assignment For REQUIRES, DERIVES_FROM, CONSTRUCTED_FROM

The concept-level graph for the combined set
`{REQUIRES, DERIVES_FROM, CONSTRUCTED_FROM}` is a DAG:

| Metric | Value |
| --- | ---: |
| Concepts | 47 |
| Constraint edges | 97 |
| Concept-level DAG? | yes |

It is therefore possible to assign concepts to modules whose contracted module
graph is acyclic. The problem is how to avoid the trivial one-module solution.

A useful formulation is:

Given:

- a directed concept graph for selected edge types
- a target number of modules
- minimum and maximum module sizes

Find:

- a concept-to-module assignment

Such that:

- the contracted module graph is a DAG
- modules are nontrivial
- cohesion is maximised, for example by internal weighted edge count or
  modularity
- boundary edges remain interpretable

A heuristic search with six modules and size bounds found an acyclic assignment
with modularity about `0.402`, close to the unconstrained community result.
However, the resulting modules are partly prerequisite strata rather than clean
topics.

### Acyclic Six-Module Assignment

The contracted module graph was acyclic. One topological module order was:

```text
M1, M3, M2, M4, M5, M6
```

Remember that edge direction points from dependent to prerequisite, so a
learning order would be closer to the reverse of this.

#### M1 Maxwell Dynamics, Waves, Radiation

- `7.6` Four-current
- `7.7` Maxwell's equations
- `8.5` Charge conservation
- `10.1` Wave equation
- `10.2` Electromagnetic waves
- `10.3` Radiation reaction

#### M2 Relativistic Particle Dynamics And Coupling

- `4.1` Proper time
- `4.4` Velocity four-vector
- `4.5` Momentum four-vector
- `4.6` Mass-energy equivalence
- `8.3` Minimal coupling
- `8.4` Lorentz force law

#### M3 Locality, Diagrams, And Field Laws

- `2.3` Principle of locality
- `3.4` Light cone
- `3.5` Minkowski diagram
- `6.3` Field Lagrangian
- `6.4` Field equations

#### M4 Electromagnetic Field, Gauge, Stress-Energy

- `7.1` Vector potential `\(A_\mu\)`
- `7.2` Field tensor `\(F_{\mu\nu}\)`
- `7.3` Electric field
- `7.4` Magnetic field
- `7.5` Electromagnetic field
- `8.1` Gauge invariance
- `8.6` Lorenz gauge
- `9.1` Energy-momentum tensor
- `9.2` Momentum density (Poynting vector)
- `9.3` Stress-energy of EM field
- `9.4` Energy density of EM field
- `11.2` Gauge fixing

#### M5 Variational Mechanics

- `5.1` Lagrangian
- `5.2` Action principle
- `5.3` Euler-Lagrange equations
- `5.4` Canonical momentum
- `5.5` Hamiltonian formalism
- `5.6` Noether's theorem

#### M6 Foundations, Spacetime Geometry, Four-Vectors

- `1.1` Inertial frames
- `1.2` Constancy of the speed of light
- `1.3` Principle of relativity
- `2.2` Spacetime event
- `3.1` Metric tensor
- `3.2` Spacetime interval
- `3.3` Lorentz transformations
- `4.2` Four-vectors
- `4.3` Position four-vector
- `6.1` Scalar field
- `6.2` Vector field
- `11.1` Lorentz invariance

This assignment proves that an acyclic six-module quotient is feasible for the
combined relation set, but it is not necessarily a good authored module design.
It mixes thematic concerns with prerequisite strata.

## Design Conclusions

1. Modules should be explicit authored KB entities, not derived live from graph
   clustering.
2. Graph analysis should be part of the authoring workflow after adding a large
   body of concepts and edges.
3. Existing levels are useful for pedagogy and layout, but should not be reused
   directly as modules.
4. `{DERIVES_FROM, CONSTRUCTED_FROM}` is a good candidate relation set for
   strict module-DAG diagnostics.
5. `REQUIRES` should probably be reported as a softer module-boundary warning,
   because strict acyclicity can force less natural modules.
6. When graph analysis suggests persistent awkward boundaries, the right fix may
   be to revise concept definitions, split concepts, move concepts, or adjust
   edge semantics rather than force the module assignment.

## Possible Future Tooling

A future authoring tool could take a proposed module assignment and report:

- modularity and internal/cross-edge counts
- quotient DAG status for selected relation sets
- cycles in the quotient graph
- concrete concept edges causing each module cycle
- concepts with many cross-module links
- candidate concept moves that improve acyclicity or modularity
- comparison with existing levels or authored module hierarchy

This would make module assignment a guided authoring decision rather than a
manual guess or an opaque automatic clustering result.
