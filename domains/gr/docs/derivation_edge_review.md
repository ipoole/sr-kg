# GR derivation-edge review — 5 November 2026

Reviewed the outgoing dependencies of all 56 GR concepts against their runtime
explanations. This pass repairs missing derivation routes without treating every
definition or construction as a theorem. Stable concept IDs and module membership
are unchanged.

## Changes

| Result | Added `DERIVES_FROM` input | Reason |
| --- | --- | --- |
| Schwarzschild metric | Vacuum field equations | Solving the spherical vacuum problem gives the exterior metric; the edge note states the zero cosmological constant, asymptotic normalisation and mass assumptions. |
| Einstein field equations | Einstein–Hilbert action | The existing action blocks derive the metric equation by stationary variation of the combined gravitational and matter actions, with consistent source signs and boundary treatment. |
| Christoffel symbols | Metric compatibility; torsion-free connection | The existing formula derivation uses both conditions to select the Levi-Civita coefficients. |
| Light deflection | Weak-field metric | The authored leading-order calculation uses both temporal and spatial perturbations, in addition to the geodesic equation already linked. |

Schwarzschild retains its `INSTANCE_OF` edge to the vacuum equations: being a
solution and being derived by solving those equations express different facts.
A new derivation block gives the static exterior calculation, with the radial
integration folded. It distinguishes that calculation from Birkhoff's stronger
statement about spherical vacuum solutions. Its source is Tong GR, §§6.1–6.1.1,
translated into the atlas signature and units.

The resulting route is Schwarzschild → vacuum equations → Einstein equations →
Einstein–Hilbert action. The Schwarzschild module's declared supports now include
GR-4, reflecting the new direct derivation. GR-5 and GR-6 remain unconnected by
primary dependency edges. No added derivation edge has a redundant alternative
path within `DERIVES_FROM`. Both the combined primary-dependency graph and the
GR module graph remain DAGs.

## Definitions and constructions retained

The metric, inverse metric, volume element, connection, covariant derivative,
parallel transport, geodesic, Ricci contractions, Einstein tensor, curvature
invariants, fluid models and energy conditions generally introduce objects,
operations or assumptions. `CONSTRUCTED_FROM`, `REQUIRES` and `INSTANCE_OF` remain
appropriate; a missing `DERIVES_FROM` is not evidence of missing knowledge.
Existing links already cover the Newtonian limit, trace reversal, vacuum
reduction, post-Newtonian expansion, waves, redshift and effective orbit dynamics.
Their approximations and conventions remain part of the teaching, rather than
being inferred from an unqualified edge.

## Follow-up cases requiring a separate decision

- **Geodesic deviation and Riemann curvature.** Its mathematical derivation uses
  curvature, but its current primary link to tidal gravity expresses physical
  motivation. A Riemann dependency would create a GR-2 → GR-3 module link opposite
  the existing GR-3 → GR-2 dependence. This is a module-ordering question, not a
  reason to claim the dependency is absent mathematically. Consider moving
  geodesic deviation into the curvature module, or explicitly accepting a module
  cycle, before changing its primary edges.
- **Alternative derivations.** The geodesic equation can be obtained from the
  geodesic action, but the action currently requires that equation as teaching
  context. Adding the reverse primary edge would create a concept cycle. Likewise,
  deriving matter conservation from the field equations would reverse their
  existing consistency prerequisite. The present prose may explain both routes;
  the graph still chooses an acyclic teaching route. A general representation of
  alternative derivations is a separate design task.
- **Perihelion precession.** The current worked calculation uses the Schwarzschild
  orbit equation, but its edges describe geodesic motion and a weak spherical
  regime. An explicit Schwarzschild derivation input is defensible and would add
  a GR-5 → GR-6 dependency, changing their intentional parallel module arrangement.
  Review that tradeoff separately; the broader geodesic input is retained here.

This is a conservative repair and audit, not a claim that every possible
mathematical derivation is represented by the current teaching DAG.
