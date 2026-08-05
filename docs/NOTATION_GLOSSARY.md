# Notation Glossary

This draft glossary collects recurring notation and convention issues from the
current concept-authoring pass. It is an authoring aid for now. The runtime KB
does not yet have first-class glossary entries or glossary links.

Use this document to keep future content consistent. When a convention is local
or pedagogically important, still state it in the concept itself.

## Global Conventions

| Notation | Meaning / Convention | Notes |
| --- | --- | --- |
| \(c=1\) | Natural units. | Default working convention once context is established. Restore \(c\) for dimensional checks and famous formulas such as \(E_0=mc^2\). |
| \(+---\) | Metric signature used in current SR content. | The flat metric is \(\eta_{\mu\nu}=\mathrm{diag}(1,-1,-1,-1)\). |
| \(ct\) | Time coordinate expressed with dimensions of length. | Useful in early SR and diagrams. In natural units \(ct=t\). |
| Greek indices \(\mu,\nu,\rho,\sigma\) | Spacetime indices. | Typically range over \(0,1,2,3\). |
| Latin spatial indices \(i,j,k\) | Spatial indices. | Typically range over \(1,2,3\). |
| Repeated index convention | Repeated upper/lower index pairs are summed. | State explicitly before using dense tensor notation with learners. |

## Spacetime And Four-Vectors

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(x^\mu\) | Position four-vector or coordinate tuple. | `sr.position_four_vector`, `sr.spacetime_event` |
| \(\Delta x^\mu\) | Displacement between two events. | `sr.spacetime_interval`, `sr.position_four_vector` |
| \(\eta_{\mu\nu}\) | Minkowski metric in flat spacetime. | `sr.metric_tensor` |
| \(A_\mu=\eta_{\mu\nu}A^\nu\) | Lowering an index with the metric. | `sr.metric_tensor`, `sr.four_vectors` |
| \(A_\mu B^\mu\) | Minkowski scalar product. | `sr.four_vectors` |
| \(U^\mu=dx^\mu/d\tau\) | Four-velocity. | `sr.velocity_four_vector`, `sr.proper_time` |
| \(p^\mu\) | Four-momentum. | `sr.momentum_four_vector` |
| \(p_\mu p^\mu=m^2c^2\) | Mass-shell invariant for a massive particle. | `sr.momentum_four_vector`, `sr.mass_energy_equivalence` |

## Derivatives And Field Notation

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(\phi(x)\) | Scalar field value at event \(x\). | `sr.scalar_field` |
| \(A^\mu(x)\), \(A_\mu(x)\) | Four-vector field components at event \(x\). | `sr.vector_field`, `sr.vector_potential` |
| \(\partial_\mu\) | Partial derivative with respect to spacetime coordinate \(x^\mu\), with convention-dependent signs/factors. | `sr.field_equations`, `sr.vector_potential` |
| \(\Box=\partial_\mu\partial^\mu\) | D'Alembertian wave operator. | `sr.field_equations`, `sr.wave_equation`, `sr.lorenz_gauge` |
| \(d^4x\) | Four-dimensional spacetime integration measure. | `sr.field_lagrangian` |

## Mechanics And Variational Notation

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(L(q,\dot q,t)\) | Ordinary mechanics Lagrangian. | `sr.lagrangian` |
| \(\mathcal L\) | Field Lagrangian density. | `sr.field_lagrangian` |
| \(S\) | Action. | `sr.action_principle` |
| \(\delta S=0\) | Stationary-action condition. | `sr.action_principle`, `sr.euler_lagrange_equations` |
| \(p_i=\partial L/\partial \dot q^i\) | Canonical momentum. | `sr.canonical_momentum` |
| \(H=p_i\dot q^i-L\) | Hamiltonian via Legendre transform. | `sr.hamiltonian_formalism` |

## Electromagnetism

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(A_\mu\) | Electromagnetic four-potential in the convention used by the concept. | `sr.vector_potential` |
| \(\Lambda\) | Gauge function. | `sr.gauge_invariance`, `sr.gauge_fixing` |
| \(A_\mu\rightarrow A_\mu+\partial_\mu\Lambda\) | Gauge transformation in one common sign convention. | `sr.gauge_invariance` |
| \(F_{\mu\nu}\) | Electromagnetic field tensor. | `sr.field_tensor`, `sr.electromagnetic_field` |
| \(F_{\mu\nu}=\partial_\mu A_\nu-\partial_\nu A_\mu\) | Field tensor constructed from the four-potential. | Signs/factors depend on convention. |
| \(\mathbf E\), \(\mathbf B\) | Electric and magnetic fields from a frame-dependent split of \(F_{\mu\nu}\). | `sr.electric_field`, `sr.magnetic_field` |
| \(j^\mu\) | Four-current. | `sr.four_current` |
| \(\partial_\mu j^\mu=0\) | Charge conservation / continuity equation. | `sr.charge_conservation` |
| \(\partial_\mu A^\mu=0\) | Lorenz gauge condition. | `sr.lorenz_gauge` |
| \(p_\mu-eA_\mu\) | Minimal-coupling combination in one common sign convention. | `sr.minimal_coupling` |

## Energy, Momentum, And Radiation

| Notation | Meaning / Convention | Related Concepts |
| --- | --- | --- |
| \(T^{\mu\nu}\) | Energy-momentum / stress-energy tensor. | `sr.energy_momentum_tensor` |
| \(T^{00}\) | Energy density component in a chosen frame. | `sr.em_energy_density`, `sr.em_stress_energy` |
| \(\mathbf S\) | Poynting vector / electromagnetic energy flux. | `sr.poynting_vector` |
| \(\mathbf g=\mathbf S/c^2\) | Electromagnetic momentum density in SI units. | `sr.poynting_vector` |

## Authoring Notes

- Prefer \(c=1\) for compact relativistic structure, but restore \(c\) when
  teaching dimensions or named physical formulas.
- Always state metric signature before equations where sign would otherwise be
  ambiguous.
- Be explicit when switching between covariant and contravariant components.
- Treat the \(E/B\) split as frame-dependent; avoid wording that makes electric
  and magnetic fields sound like invariantly separate objects.
- Sign conventions for \(A_\mu\), \(F_{\mu\nu}\), charge \(q\), and minimal
  coupling should be kept local until the atlas has a first-class convention
  system.
