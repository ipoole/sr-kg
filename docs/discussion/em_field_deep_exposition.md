# Electromagnetic Field: Deep Exposition Draft

Captured on 2026-07-26.

This is a dependency-ordered prose draft for later decomposition into
fine-grained content blocks and typed edges. It is not current runtime KB
content.

## Exposition

A relativistic field is a physical quantity assigned locally to spacetime
events. Instead of one particle having a position \(q(t)\), a field has values
throughout spacetime, such as \(\phi(x)\), \(A^\mu(x)\), or
\(F_{\mu\nu}(x)\). This local viewpoint is especially natural in relativity:
influence is carried from event to nearby event, not transmitted instantly
across space.

The electromagnetic field is most cleanly introduced through the four-potential
\(A_\mu(x)\). In a chosen convention one may write

\[
A^\mu = \left(\frac{\phi}{c}, \mathbf A\right),
\]

where \(\phi\) is the scalar potential and \(\mathbf A\) is the ordinary vector
potential. Relativistically, these are not separate objects. They are components
of one spacetime field.

The directly useful covariant electromagnetic object is the field tensor

\[
F_{\mu\nu}=\partial_\mu A_\nu-\partial_\nu A_\mu .
\]

This antisymmetric derivative extracts the curl-like part of the potential's
spacetime variation. Because \(F_{\mu\nu}=-F_{\nu\mu}\), the diagonal components
vanish and the off-diagonal components come in opposite pairs. In four
dimensions this leaves six independent components.

Those six components are the relativistic home of the familiar electric and
magnetic fields. Once an inertial frame is chosen, the time-space components of
\(F_{\mu\nu}\) are read as the electric field, up to convention-dependent signs
and factors of \(c\). The purely spatial antisymmetric components are read as
the magnetic field. In ordinary three-vector notation this corresponds to

\[
\mathbf E=-\nabla\phi-\frac{\partial\mathbf A}{\partial t},
\]

and

\[
\mathbf B=\nabla\times\mathbf A .
\]

The important point is that this split into \(\mathbf E\) and \(\mathbf B\) is
frame-dependent. A Lorentz boost mixes time and space. Since the electric field
comes from time-space components of \(F_{\mu\nu}\), and the magnetic field from
space-space components, a boost can mix what one observer calls electric with
what another observer calls magnetic.

Thus the electromagnetic field is not really two independent fields, electric
and magnetic. It is one antisymmetric tensor field, with electric and magnetic
parts appearing after an observer chooses a time-space split. The tensor
\(F_{\mu\nu}\) is the covariant object; \(\mathbf E\) and \(\mathbf B\) are
frame-dependent readings of it.

The potential \(A_\mu\) contains redundancy. If

\[
A_\mu \rightarrow A_\mu+\partial_\mu\Lambda,
\]

then the field tensor is unchanged:

\[
F_{\mu\nu}\rightarrow F_{\mu\nu}.
\]

The extra terms cancel because partial derivatives commute:

\[
\partial_\mu\partial_\nu\Lambda-\partial_\nu\partial_\mu\Lambda=0.
\]

This is gauge invariance. Different potentials can represent the same physical
electromagnetic field. In classical electromagnetism the physical field is
captured by \(F_{\mu\nu}\), not by a unique choice of \(A_\mu\).

Maxwell's equations govern the electromagnetic field. In covariant notation,
the sourced equations can be written schematically as

\[
\partial_\mu F^{\mu\nu}=\mu_0 j^\nu,
\]

where \(j^\nu\) is the four-current. The four-current packages charge density
and current density into one relativistic source:

\[
j^\mu=(c\rho,\mathbf j).
\]

The homogeneous Maxwell equations are encoded by the cyclic identity

\[
\partial_\lambda F_{\mu\nu}
+\partial_\mu F_{\nu\lambda}
+\partial_\nu F_{\lambda\mu}=0.
\]

This identity follows from the definition \(F=dA\): each term contains second
derivatives of the potential, and the pairs cancel when partial derivatives
commute.

Together, these equations say that local sources determine the local divergence
of the field tensor, while the antisymmetric construction of the tensor imposes
the source-free constraints. When decomposed into a chosen inertial frame, the
covariant equations become the four familiar Maxwell equations for
\(\mathbf E\) and \(\mathbf B\).

Charge conservation is built into the same structure. Taking the divergence of
the sourced equation gives

\[
\partial_\nu\partial_\mu F^{\mu\nu}=\mu_0\partial_\nu j^\nu .
\]

The left-hand side vanishes because the double derivative is symmetric in its
indices while \(F^{\mu\nu}\) is antisymmetric. Therefore

\[
\partial_\mu j^\mu=0,
\]

the covariant continuity equation.

The field is not only a bookkeeping device for forces. It acts locally on
charged matter. In covariant form the Lorentz force law can be written as

\[
\frac{dp^\mu}{d\tau}=qF^\mu{}_\nu U^\nu,
\]

where \(U^\nu\) is the four-velocity of the charged particle. In a chosen
inertial frame this contains the familiar three-vector force

\[
\mathbf F=q(\mathbf E+\mathbf v\times\mathbf B).
\]

This is where the frame-dependent electric and magnetic components become
operational: they describe how the unified field pushes charged particles in
that frame.

The electromagnetic field also carries energy and momentum. Its local energy
density in SI units is

\[
u=\frac{1}{2}\left(\epsilon_0 E^2+\frac{1}{\mu_0}B^2\right).
\]

Its energy flux is described by the Poynting vector

\[
\mathbf S=\frac{1}{\mu_0}\mathbf E\times\mathbf B.
\]

Relativistically, energy density, momentum density, energy flux, and stress are
all components of an electromagnetic stress-energy tensor constructed from
\(F_{\mu\nu}\) and the metric.

In source-free regions Maxwell's equations admit wave solutions. In a suitable
gauge, the potential satisfies a wave equation such as

\[
\Box A^\mu=0,
\]

where

\[
\Box=\partial_\mu\partial^\mu
=\frac{1}{c^2}\frac{\partial^2}{\partial t^2}-\nabla^2 .
\]

The resulting electromagnetic waves are propagating disturbances of the same
field tensor. In a plane wave, the electric component, magnetic component, and
direction of propagation are mutually perpendicular, and the Poynting vector
points in the propagation direction.

Several misconceptions are worth guarding against. First, \(\mathbf E\) and
\(\mathbf B\) are not two independent substances; they are frame-dependent
components of one field tensor. Second, the vector potential is not normally a
unique physical field in classical electromagnetism; gauge-related potentials
can describe the same \(F_{\mu\nu}\). Third, fields are not merely
computational shortcuts for action at a distance; in relativity they carry
energy, momentum, and causal influence locally. Fourth, Maxwell's equations are
not just four unrelated vector formulas; they are a compact covariant structure
linking sources, potentials, fields, conservation, and waves.

