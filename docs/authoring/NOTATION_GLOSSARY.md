# Notation Glossary

This draft glossary collects recurring notation and convention issues from the
current concept-authoring pass. It is an authoring aid for now. The runtime KB
does not yet have first-class glossary entries or glossary links.

Use this document to keep future content consistent. When a convention is local
or pedagogically important, still state it in the concept itself.

## Global Conventions

| Notation | Meaning / Convention | Notes |
| --- | --- | --- |
| \(c\overset{\text{units}}{=}1\) | Natural units. | Default working convention once context is established. Restore \(c\) for dimensional checks and famous formulas such as \(E_0\coloneqq mc^2\). |
| \(+---\) | Metric signature used in current SR content. | The flat metric is \(\eta_{\mu\nu}\coloneqq\mathrm{diag}(1,-1,-1,-1)\). |
| \(ct\) | Time coordinate expressed with dimensions of length. | Useful in early SR and diagrams. In natural units \(ct=t\). |
| \(x^\mu\coloneqq(ct,x,y,z)\) or \(x^\mu\coloneqq(t,x,y,z)\) | Coordinate ordering used for spacetime components. | State which is being used when factors of \(c\) matter. |
| Greek indices \(\mu,\nu,\rho,\sigma\) | Spacetime indices. | Typically range over \(0,1,2,3\). |
| Latin spatial indices \(i,j,k\) | Spatial indices. | Typically range over \(1,2,3\). |
| Repeated index convention | Repeated upper/lower index pairs are summed. | State explicitly before using dense tensor notation with learners. |

## Equality And Equivalence

| Notation | Meaning / Convention | Notes |
| --- | --- | --- |
| \(A\coloneqq B\) | Definition. | Use when the left-hand symbol is being introduced or fixed by the right-hand expression. |
| \(A\equiv B\) | Mathematical identity. | Use for identities or exactly equivalent rewritings, not for definitions. |
| \(A=B\) | Ordinary exact equality. | Use for routine algebra, arithmetic, and exact equalities whose provenance is immediate from context. |
| \(A\overset{X}{=}B\) | Equality licensed by \(X\). | Use short labels such as `metric`, `Lorentz`, `rest frame`, `mass shell`, `stationary`, `units`, `conservation`, `Maxwell`, `potentials`, `Lorenz gauge`, `source-free`, `3-vector`, `Noether`, `EM tensor`, `frame`, `transverse`, or `dispersion` when the reason matters pedagogically. Explain the label in nearby prose rather than relying on UI hover text or long annotation text. |
| \(A\simeq B\) | Approximation. | State the approximation regime in prose or, sparingly, on the symbol. |
| \(A\sim B\) | Stated equivalence or asymptotic relation. | Do not use casually as another approximation sign. |

See `docs/authoring/equality_annotation_style.md` for the full equality
annotation house style.

## Spacetime And Four-Vectors

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(x^\mu\) | Position four-vector or coordinate tuple. | `sr.position_four_vector`, `sr.spacetime_event` |
| \(\Delta x^\mu\) | Displacement between two events. | `sr.spacetime_interval`, `sr.position_four_vector` |
| \(\Delta s^2\) | Spacetime interval / invariant squared separation. | `sr.spacetime_interval` |
| \(d\tau\), \(\Delta\tau\) | Proper-time element or elapsed proper time along a timelike path. | `sr.proper_time` |
| \(\eta_{\mu\nu}\) | Minkowski metric in flat spacetime. | `sr.metric_tensor` |
| \(V_\mu\coloneqq\eta_{\mu\nu}V^\nu\) | Lowering an index with the metric. | `sr.metric_tensor`, `sr.four_vectors` |
| \(V_\mu W^\mu\) | Minkowski scalar product. | `sr.four_vectors` |
| \(U^\mu\coloneqq dx^\mu/d\tau\) | Four-velocity. | `sr.velocity_four_vector`, `sr.proper_time` |
| \(p^\mu\) | Four-momentum. | `sr.momentum_four_vector` |
| \(p_\mu p^\mu\overset{\text{mass shell}}{=}m^2c^2\) | Mass-shell invariant for a massive particle. | `sr.momentum_four_vector`, `sr.mass_energy_equivalence` |

## Derivatives And Field Notation

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(\phi(x)\) | Scalar field value at event \(x\). | `sr.scalar_field` |
| \(A^\mu(x)\), \(A_\mu(x)\) | Four-vector field components at event \(x\). | `sr.vector_field`, `sr.vector_potential` |
| \(\partial_\mu\) | Partial derivative with respect to spacetime coordinate \(x^\mu\), with convention-dependent signs/factors. | `sr.field_equations`, `sr.vector_potential` |
| \(\partial^\mu\coloneqq\eta^{\mu\nu}\partial_\nu\) | Raised-index derivative. | With \(+---\) and \(c\overset{\text{units}}{=}1\), raising the derivative index flips the spatial signs. |
| \(\Box=\partial_\mu\partial^\mu\) | D'Alembertian wave operator. | `sr.field_equations`, `sr.wave_equation`, `sr.lorenz_gauge` |
| \(d^4x\) | Four-dimensional spacetime integration measure. | `sr.field_lagrangian` |

## Mechanics And Variational Notation

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(L(q,\dot q,t)\) | Ordinary mechanics Lagrangian. | `sr.lagrangian` |
| \(\mathcal L\) | Field Lagrangian density. | `sr.field_lagrangian` |
| \(S\) | Action. | `sr.action_principle` |
| \(\delta S\overset{\text{stationary}}{=}0\) | Stationary-action condition. | `sr.action_principle`, `sr.euler_lagrange_equations` |
| \(p_i\coloneqq\partial L/\partial \dot q^i\) | Canonical momentum. | `sr.canonical_momentum` |
| \(H\coloneqq p_i\dot q^i-L\) | Hamiltonian via Legendre transform. | `sr.hamiltonian_formalism` |

## Electromagnetism

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(A_\mu\) | Electromagnetic four-potential in the convention used by the concept. | `sr.vector_potential` |
| \(\Lambda\) | Gauge function. | `sr.gauge_invariance`, `sr.gauge_fixing` |
| \(A_\mu\rightarrow A_\mu+\partial_\mu\Lambda\) | Gauge transformation in one common sign convention. | `sr.gauge_invariance` |
| \(F_{\mu\nu}\) | Electromagnetic field tensor. | `sr.field_tensor`, `sr.electromagnetic_field` |
| \(F_{\mu\nu}=\partial_\mu A_\nu-\partial_\nu A_\mu\) | Field tensor constructed from the four-potential. | Signs/factors depend on convention. |
| \(F^\mu{}_\nu\) | Mixed-index field tensor, often used in the covariant Lorentz force law. | `sr.lorentz_force_law` |
| \(\mathbf E\), \(\mathbf B\) | Electric and magnetic fields from a frame-dependent split of \(F_{\mu\nu}\). | `sr.electric_field`, `sr.magnetic_field` |
| \(\epsilon_{ijk}\) | Three-dimensional Levi-Civita symbol. | Useful when mapping the spatial antisymmetric part of \(F_{\mu\nu}\) to \(\mathbf B\). |
| \(j^\mu\) | Four-current. | `sr.four_current` |
| \(j^\mu\coloneqq(c\rho,\mathbf j)\) | Common SI-style four-current component convention. | In \(c\overset{\text{units}}{=}1\) units this is often written \((\rho,\mathbf j)\). |
| \(\partial_\mu j^\mu=0\) | Charge conservation / continuity equation. | `sr.charge_conservation` |
| \(\partial_\mu A^\mu=0\) | Lorenz gauge condition. | `sr.lorenz_gauge` |
| \(\epsilon_0\), \(\mu_0\) | SI electromagnetic constants. | Keep explicit in SI formulas; suppress only after stating a natural-unit convention. |
| \(q\), \(e\) | Charge of a particle. | Prefer \(q\) for a general particle charge; use \(e\) only when the sign convention is clear. |
| \(p_\mu-eA_\mu\) | Minimal-coupling combination in one common sign convention. | `sr.minimal_coupling` |

## Energy, Momentum, And Radiation

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(T^{\mu\nu}\) | Energy-momentum / stress-energy tensor. | `sr.energy_momentum_tensor` |
| \(T^{00}\) | Energy density component in a chosen frame. | `sr.em_energy_density`, `sr.em_stress_energy` |
| \(u_\mathrm{EM}\) | Electromagnetic energy density in ordinary three-vector notation. | `sr.em_energy_density` |
| \(\mathbf S\) | Poynting vector / electromagnetic energy flux. | `sr.poynting_vector` |
| \(\mathbf g=\mathbf S/c^2\) | Electromagnetic momentum density in SI units. | `sr.poynting_vector` |

## Authoring Notes

- Prefer \(c\overset{\text{units}}{=}1\) for compact relativistic structure, but restore \(c\) when
  teaching dimensions or named physical formulas.
- Always state metric signature before equations where sign would otherwise be
  ambiguous.
- Be explicit when switching between covariant and contravariant components.
- Treat the \(E/B\) split as frame-dependent; avoid wording that makes electric
  and magnetic fields sound like invariantly separate objects.
- Sign conventions for \(A_\mu\), \(F_{\mu\nu}\), charge \(q\), and minimal
  coupling should be kept local until the atlas has a first-class convention
  system.
- Use \(V^\mu,W^\mu\), or another neutral letter, for generic four-vector
  examples. Reserve \(A^\mu,A_\mu\) for the electromagnetic four-potential or
  for a vector field when the context is explicitly not electromagnetic.
