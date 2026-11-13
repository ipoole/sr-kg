# Source review worklist

Verified locators belong in `../data/reference_links.csv`. Follow the shared
[authoring guide](../../../docs/authoring/authoring_guide.md#references).

- Radiation reaction now has precise introductory support below. A complete self-force derivation still needs a specified charge model and controlled approximation; it is outside the current treatment.
- Add page-level precision where an existing section locator is too broad.

## SR-1 checks — 12 November 2026

- Einstein, *On the Electrodynamics of Moving Bodies* (1905), §§1–4:
  [translation](https://fourmilab.ch/etexts/einstein/specrel/www/).
  Checked the clock/synchronisation setup, spacetime homogeneity, reciprocal
  frame changes and scale normalisation. Six new block-level source links are
  registered across the sources listed here; the rewritten coefficient proof
  uses modern notation.
- OpenStax, *University Physics III*, [§5.5](https://openstax.org/books/university-physics-volume-3/pages/5-5-the-lorentz-transformation):
  checked boost equations and interval preservation. Its own derivation order
  uses earlier length contraction; the SR-1 postulate-first proof does not.
- Panagiota Daskalopoulos, *Introduction to Diffusion Equations*, IAS June 2009,
  [Lecture 1, PDF p. 9](https://www.math.ias.edu/files/Lecture-No1.pdf): checked
  positivity of the heat kernel and instantaneous spreading. This is a
  counterexample about differential locality, not a relativistic signal model.

## SR-2 checks — 13 November 2026

- Einstein, *Does the Inertia of a Body Depend upon its Energy-Content?* (1905),
  [Perrett–Jeffery translation](https://www.fourmilab.ch/etexts/einstein/E_mc2/www/index.html):
  checked equal opposite pulses, two-frame energy balances, a common energy-zero
  convention and the low-speed inertia coefficient. Distinguish the argument
  for a change in mass from the complete physical four-momentum formulation.
- Einstein, *On the Electrodynamics of Moving Bodies* (1905),
  [§8](https://www.fourmilab.ch/etexts/einstein/specrel/www/): radiation energy
  transformation, used for the sum of oppositely directed pulses. The new
  four-vector component derivation is modern notation, not a quotation.
- OpenStax, *University Physics III*,
  [§5.8](https://openstax.org/books/university-physics-volume-3/pages/5-8-relativistic-momentum):
  proper-time momentum construction, Newtonian calibration and the physical
  conservation law.
- Same book, [§5.9](https://openstax.org/books/university-physics-volume-3/pages/5-9-relativistic-energy):
  fixed-mass work–energy calculation; Rest Energy; Stored Energy and Potential
  Energy; Relativistic Energy and Momentum. Our vector-rate calculation,
  system-boundary discussion and opposite-pulse illustration are authored
  explanations. Source links do not claim that the textbook uses this exact
  derivation order or all of these formulations.

## SR-3 checks — 13 November 2026

- Sussman and Wisdom, *Structure and Interpretation of Classical Mechanics*,
  second edition, [chapter 1](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/9579/sicm_edition_2.zip/chapter001.html):
  stationary action, path variations, boundary conditions and Lagrange equations.
- Tong, *Quantum Field Theory*, [primary lecture text hosted by Durham](https://www.ippp.dur.ac.uk/~mspannow/files/Tong_QFT.pdf),
  §§1.1, 1.1.1 and 1.4: first-derivative field variation, scalar example and
  Hamiltonian structure. The Cambridge copies timed out; this is the same
  author text, not a secondary exposition. Our blocks state measure/units and
  write out their own particle and field algebra.

## SR-4 checks — 13 November 2026

- Tong, primary QFT lecture text, §§6.1–6.1.1: potential antisymmetry,
  homogeneous identity and gauge freedom. Our SI convention restores constants
  explicitly rather than importing natural-unit signs in isolation.
- Blaschke, Gieres, Reboud and Schweda, *The Energy-Momentum Tensor(s) in
  Classical Gauge Theories* (2016), [§3.3](https://arxiv.org/html/1605.01121):
  metric-response construction in Minkowski space and its relationship with
  improved tensors. The auxiliary-metric method is not a derivation of gravity.
- Independently checked the charged-worldline variation with a fixed parameter,
  obtaining dp_rho/dtau=q F_rho nu U^nu for the stated negative worldline
  coupling. This is an application of the already sourced variational method;
  it is not a quotation from the field-theory source.

## SR-5 checks — 13 November 2026

- Tong, primary QFT text, §§1.3.1–1.3.2 and §6.1: Noether current identity,
  translation tensor and Maxwell variation. The SI intermediate algebra is
  explicitly authored, not copied from natural-unit notation.
- Blaschke et al. (2016), §§2.1.2–2.2: superpotential/improvement terms,
  symmetry and gauge properties, and the need for boundary qualifications.
- Steane, *Tracking the radiation reaction energy when charged bodies accelerate*,
  AJP 83, 703 (2015), [author copy](https://users.physics.ox.ac.uk/~Steane/teaching/em/energy_AJP1.4914421.pdf),
  §II, “An Energy Paradox”: near-field and radiation-energy accounting. Our
  introductory balance does not assert a particular exact self-force model.
- Ekman, Heinzl and Ilderton, *Reduction of order, resummation and radiation
  reaction* (2021), [primary paper](https://arxiv.org/abs/2105.01640): leading
  Landau–Lifshitz approximation and limitations. The nonrelativistic force
  derivative example is a local illustration of the method, not a claim that
  the paper derives every displayed introductory formula in these terms.
