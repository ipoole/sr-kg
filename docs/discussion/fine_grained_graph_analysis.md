# Fine-Grained Block Graph Analysis

Generated from the experimental Markdown worksheets. This report is not
runtime KB data.

## Dependency Relation Orientation

| Relation | Dependency-order interpretation |
| --- | --- |
| `requires` | `target` must appear before `source` |
| `derives_from` | `target` must appear before `source` |
| `special_case_of` | `target` must appear before `source` |
| `supplies_algebra_for` | `source` must appear before `target` |

Other relations are treated as non-ordering side links for this pass.

## MEE Fine-Grained Graph Experiment

Source: [mee_fine_grained_graph.md](mee_fine_grained_graph.md)

| Metric | Value |
| --- | ---: |
| Fine blocks | 36 |
| Edge rows | 51 |
| Ordering constraints | 31 |
| Non-ordering side links | 20 |
| External dependency nodes | 4 |
| DAG? | yes |
| Cycles | 0 |
| Draft-order conflicts | 5 |

**Relation Counts**

- `connects_to`: 1
- `derives_from`: 17
- `elaborates`: 13
- `gives_example_of`: 2
- `requires`: 8
- `special_case_of`: 3
- `supplies_algebra_for`: 3
- `warns_about`: 4

**Non-Ordering Relations**

- `connects_to`: 1
- `elaborates`: 13
- `gives_example_of`: 2
- `warns_about`: 4

**External Dependency Nodes**

- `sr.four_vectors` _(external)_
- `sr.inertial_frames` _(external)_
- `sr.metric_tensor` _(external)_
- `sr.momentum_four_vector` _(external)_

**Main Ordered Blocks**

- `mee.020.rest_energy_formula` _core_formula_
- `mee.060.system_mass_statement` _core_claim_
- `mee.070.energy_exchange_changes_mass` _consequence_
- `mee.080.energy_momentum_relation` _core_formula_
- `mee.090.rest_frame_zero_momentum` _definition_
- `mee.100.rest_case_substitution` _derivation_step_
- `mee.110.positive_energy_root` _algebra_support_
- `mee.130.four_momentum_unifies_energy_momentum` _definition_
- `mee.140.four_momentum_norm` _derivation_step_
- `mee.150.mass_shell_invariant` _definition_
- `mee.160.equate_norms` _derivation_step_
- `mee.170.multiply_by_c_squared` _algebra_support_
- `mee.180.energy_momentum_result` _derivation_step_
- `mee.190.four_momentum_geometry_summary` _summary_
- `mee.220.relativistic_energy` _core_formula_
- `mee.230.lorentz_factor` _definition_
- `mee.240.gamma_expansion` _algebra_support_
- `mee.250.newtonian_limit` _consequence_
- `mee.290.mass_defect_energy_release` _calculation_rule_
- `mee.310.massless_energy_relation` _derivation_step_
- `mee.320.photon_no_rest_energy` _warning_
- `mee.340.massive_things_have_rest_energy` _summary_
- `mee.350.compact_geometry_summary` _summary_

**Isolated Blocks Under Ordering Relations**

- `mee.010.mass_as_invariant_energy` _core_claim_
- `mee.030.invariant_mass_and_conversion_factor` _definition_
- `mee.040.mass_energy_same_content` _intuition_
- `mee.050.conversion_slogan_warning` _warning_
- `mee.120.rest_formula_scope` _warning_
- `mee.200.relativistic_mass_warning` _warning_
- `mee.210.invariant_mass_convention` _definition_
- `mee.260.composite_system_mass` _core_claim_
- `mee.270.internal_energy_examples` _example_
- `mee.280.nuclear_mass_defect` _example_
- `mee.300.c_squared_scale` _intuition_
- `mee.330.quantum_photon_energy` _connection_
- `mee.360.misconception_summary` _summary_

**Optional-Role Blocks**

- `mee.040.mass_energy_same_content` _intuition_
- `mee.050.conversion_slogan_warning` _warning_
- `mee.110.positive_energy_root` _algebra_support_
- `mee.120.rest_formula_scope` _warning_
- `mee.170.multiply_by_c_squared` _algebra_support_
- `mee.190.four_momentum_geometry_summary` _summary_
- `mee.200.relativistic_mass_warning` _warning_
- `mee.240.gamma_expansion` _algebra_support_
- `mee.270.internal_energy_examples` _example_
- `mee.280.nuclear_mass_defect` _example_
- `mee.300.c_squared_scale` _intuition_
- `mee.320.photon_no_rest_energy` _warning_
- `mee.330.quantum_photon_energy` _connection_
- `mee.340.massive_things_have_rest_energy` _summary_
- `mee.350.compact_geometry_summary` _summary_
- `mee.360.misconception_summary` _summary_

**Topological Dependency Order**

1. `sr.four_vectors` _(external)_
2. `sr.inertial_frames` _(external)_
3. `sr.metric_tensor` _(external)_
4. `sr.momentum_four_vector` _(external)_
5. `mee.010.mass_as_invariant_energy` _core_claim_
6. `mee.030.invariant_mass_and_conversion_factor` _definition_
7. `mee.040.mass_energy_same_content` _intuition_
8. `mee.050.conversion_slogan_warning` _warning_
9. `mee.060.system_mass_statement` _core_claim_
10. `mee.070.energy_exchange_changes_mass` _consequence_
11. `mee.090.rest_frame_zero_momentum` _definition_
12. `mee.110.positive_energy_root` _algebra_support_
13. `mee.120.rest_formula_scope` _warning_
14. `mee.130.four_momentum_unifies_energy_momentum` _definition_
15. `mee.140.four_momentum_norm` _derivation_step_
16. `mee.150.mass_shell_invariant` _definition_
17. `mee.160.equate_norms` _derivation_step_
18. `mee.170.multiply_by_c_squared` _algebra_support_
19. `mee.180.energy_momentum_result` _derivation_step_
20. `mee.080.energy_momentum_relation` _core_formula_
21. `mee.020.rest_energy_formula` _core_formula_
22. `mee.100.rest_case_substitution` _derivation_step_
23. `mee.190.four_momentum_geometry_summary` _summary_
24. `mee.200.relativistic_mass_warning` _warning_
25. `mee.210.invariant_mass_convention` _definition_
26. `mee.230.lorentz_factor` _definition_
27. `mee.220.relativistic_energy` _core_formula_
28. `mee.240.gamma_expansion` _algebra_support_
29. `mee.250.newtonian_limit` _consequence_
30. `mee.260.composite_system_mass` _core_claim_
31. `mee.270.internal_energy_examples` _example_
32. `mee.280.nuclear_mass_defect` _example_
33. `mee.290.mass_defect_energy_release` _calculation_rule_
34. `mee.300.c_squared_scale` _intuition_
35. `mee.310.massless_energy_relation` _derivation_step_
36. `mee.320.photon_no_rest_energy` _warning_
37. `mee.330.quantum_photon_energy` _connection_
38. `mee.340.massive_things_have_rest_energy` _summary_
39. `mee.350.compact_geometry_summary` _summary_
40. `mee.360.misconception_summary` _summary_

**Longest Dependency Chain**

`sr.momentum_four_vector` _(external)_ -> `mee.130.four_momentum_unifies_energy_momentum` _definition_ -> `mee.140.four_momentum_norm` _derivation_step_ -> `mee.160.equate_norms` _derivation_step_ -> `mee.170.multiply_by_c_squared` _algebra_support_ -> `mee.180.energy_momentum_result` _derivation_step_ -> `mee.080.energy_momentum_relation` _core_formula_ -> `mee.220.relativistic_energy` _core_formula_ -> `mee.250.newtonian_limit` _consequence_

**Ordering Conflicts With Draft Handles**

| Required-before | Required-after | Relation | Worksheet edge |
| --- | --- | --- | --- |
| `mee.080.energy_momentum_relation` _core_formula_ | `mee.020.rest_energy_formula` _core_formula_ | `special_case_of` | `mee.020.rest_energy_formula` -> `mee.080.energy_momentum_relation` |
| `mee.110.positive_energy_root` _algebra_support_ | `mee.020.rest_energy_formula` _core_formula_ | `derives_from` | `mee.020.rest_energy_formula` -> `mee.110.positive_energy_root` |
| `mee.110.positive_energy_root` _algebra_support_ | `mee.100.rest_case_substitution` _derivation_step_ | `supplies_algebra_for` | `mee.110.positive_energy_root` -> `mee.100.rest_case_substitution` |
| `mee.180.energy_momentum_result` _derivation_step_ | `mee.080.energy_momentum_relation` _core_formula_ | `derives_from` | `mee.080.energy_momentum_relation` -> `mee.180.energy_momentum_result` |
| `mee.230.lorentz_factor` _definition_ | `mee.220.relativistic_energy` _core_formula_ | `requires` | `mee.220.relativistic_energy` -> `mee.230.lorentz_factor` |

## Electromagnetic Field Fine-Grained Graph Experiment

Source: [em_field_fine_grained_graph.md](em_field_fine_grained_graph.md)

| Metric | Value |
| --- | ---: |
| Fine blocks | 38 |
| Edge rows | 78 |
| Ordering constraints | 58 |
| Non-ordering side links | 20 |
| External dependency nodes | 12 |
| DAG? | yes |
| Cycles | 0 |
| Draft-order conflicts | 3 |

**Relation Counts**

- `connects_to`: 6
- `derives_from`: 25
- `elaborates`: 7
- `gives_example_of`: 1
- `motivates`: 1
- `requires`: 31
- `special_case_of`: 1
- `supplies_algebra_for`: 1
- `warns_about`: 5

**Non-Ordering Relations**

- `connects_to`: 6
- `elaborates`: 7
- `gives_example_of`: 1
- `motivates`: 1
- `warns_about`: 5

**External Dependency Nodes**

- `sr.field_tensor` _(external)_
- `sr.four_current` _(external)_
- `sr.gauge_invariance` _(external)_
- `sr.inertial_frames` _(external)_
- `sr.lorentz_transformations` _(external)_
- `sr.lorenz_gauge` _(external)_
- `sr.metric_tensor` _(external)_
- `sr.momentum_four_vector` _(external)_
- `sr.principle_of_locality` _(external)_
- `sr.spacetime_event` _(external)_
- `sr.vector_field` _(external)_
- `sr.velocity_four_vector` _(external)_

**Main Ordered Blocks**

- `emf.010.local_field_view` _core_claim_
- `emf.040.vector_potential` _definition_
- `emf.050.potential_components` _core_formula_
- `emf.060.potential_unifies_scalar_and_vector` _core_claim_
- `emf.070.field_tensor_definition` _core_formula_
- `emf.090.field_tensor_antisymmetry` _derivation_step_
- `emf.100.six_independent_components` _consequence_
- `emf.110.electric_from_time_space_components` _definition_
- `emf.120.magnetic_from_spatial_components` _definition_
- `emf.130.electric_from_potential` _core_formula_
- `emf.140.magnetic_from_potential` _core_formula_
- `emf.150.frame_dependent_split` _core_claim_
- `emf.160.boosts_mix_electric_and_magnetic` _consequence_
- `emf.170.unified_tensor_field` _summary_
- `emf.180.gauge_transformation` _core_formula_
- `emf.190.gauge_cancellation` _algebra_support_
- `emf.200.gauge_invariance` _consequence_
- `emf.210.potential_not_unique_warning` _warning_
- `emf.220.sourced_maxwell_equation` _core_formula_
- `emf.230.four_current_source` _definition_
- `emf.240.homogeneous_maxwell_identity` _core_formula_
- `emf.250.f_equals_dA_implies_homogeneous_identity` _derivation_step_
- `emf.260.frame_split_maxwell_equations` _consequence_
- `emf.270.charge_conservation_from_antisymmetry` _derivation_step_
- `emf.280.covariant_lorentz_force` _core_formula_
- `emf.290.three_vector_lorentz_force` _consequence_
- `emf.310.field_energy_density` _core_formula_
- `emf.320.poynting_vector` _core_formula_
- `emf.330.stress_energy_connection` _connection_
- `emf.340.source_free_wave_equation` _core_formula_
- `emf.350.dalembertian` _definition_
- `emf.360.electromagnetic_waves` _consequence_
- `emf.370.plane_wave_geometry` _example_

**Isolated Blocks Under Ordering Relations**

- `emf.020.field_values_over_spacetime` _definition_
- `emf.030.locality_motivation` _intuition_
- `emf.080.antisymmetric_derivative_intuition` _intuition_
- `emf.300.operational_meaning_of_components` _intuition_
- `emf.380.misconception_summary` _summary_

**Optional-Role Blocks**

- `emf.030.locality_motivation` _intuition_
- `emf.080.antisymmetric_derivative_intuition` _intuition_
- `emf.170.unified_tensor_field` _summary_
- `emf.190.gauge_cancellation` _algebra_support_
- `emf.210.potential_not_unique_warning` _warning_
- `emf.300.operational_meaning_of_components` _intuition_
- `emf.330.stress_energy_connection` _connection_
- `emf.370.plane_wave_geometry` _example_
- `emf.380.misconception_summary` _summary_

**Topological Dependency Order**

1. `sr.field_tensor` _(external)_
2. `sr.four_current` _(external)_
3. `sr.gauge_invariance` _(external)_
4. `sr.inertial_frames` _(external)_
5. `sr.lorentz_transformations` _(external)_
6. `sr.lorenz_gauge` _(external)_
7. `sr.metric_tensor` _(external)_
8. `sr.momentum_four_vector` _(external)_
9. `sr.principle_of_locality` _(external)_
10. `sr.spacetime_event` _(external)_
11. `sr.vector_field` _(external)_
12. `sr.velocity_four_vector` _(external)_
13. `emf.010.local_field_view` _core_claim_
14. `emf.020.field_values_over_spacetime` _definition_
15. `emf.030.locality_motivation` _intuition_
16. `emf.040.vector_potential` _definition_
17. `emf.050.potential_components` _core_formula_
18. `emf.060.potential_unifies_scalar_and_vector` _core_claim_
19. `emf.070.field_tensor_definition` _core_formula_
20. `emf.080.antisymmetric_derivative_intuition` _intuition_
21. `emf.090.field_tensor_antisymmetry` _derivation_step_
22. `emf.100.six_independent_components` _consequence_
23. `emf.110.electric_from_time_space_components` _definition_
24. `emf.120.magnetic_from_spatial_components` _definition_
25. `emf.130.electric_from_potential` _core_formula_
26. `emf.140.magnetic_from_potential` _core_formula_
27. `emf.150.frame_dependent_split` _core_claim_
28. `emf.160.boosts_mix_electric_and_magnetic` _consequence_
29. `emf.170.unified_tensor_field` _summary_
30. `emf.180.gauge_transformation` _core_formula_
31. `emf.190.gauge_cancellation` _algebra_support_
32. `emf.200.gauge_invariance` _consequence_
33. `emf.210.potential_not_unique_warning` _warning_
34. `emf.230.four_current_source` _definition_
35. `emf.220.sourced_maxwell_equation` _core_formula_
36. `emf.250.f_equals_dA_implies_homogeneous_identity` _derivation_step_
37. `emf.240.homogeneous_maxwell_identity` _core_formula_
38. `emf.260.frame_split_maxwell_equations` _consequence_
39. `emf.270.charge_conservation_from_antisymmetry` _derivation_step_
40. `emf.280.covariant_lorentz_force` _core_formula_
41. `emf.290.three_vector_lorentz_force` _consequence_
42. `emf.300.operational_meaning_of_components` _intuition_
43. `emf.310.field_energy_density` _core_formula_
44. `emf.320.poynting_vector` _core_formula_
45. `emf.330.stress_energy_connection` _connection_
46. `emf.350.dalembertian` _definition_
47. `emf.340.source_free_wave_equation` _core_formula_
48. `emf.360.electromagnetic_waves` _consequence_
49. `emf.370.plane_wave_geometry` _example_
50. `emf.380.misconception_summary` _summary_

**Longest Dependency Chain**

`sr.spacetime_event` _(external)_ -> `emf.010.local_field_view` _core_claim_ -> `emf.040.vector_potential` _definition_ -> `emf.070.field_tensor_definition` _core_formula_ -> `emf.090.field_tensor_antisymmetry` _derivation_step_ -> `emf.100.six_independent_components` _consequence_ -> `emf.110.electric_from_time_space_components` _definition_ -> `emf.150.frame_dependent_split` _core_claim_ -> `emf.160.boosts_mix_electric_and_magnetic` _consequence_ -> `emf.170.unified_tensor_field` _summary_

**Ordering Conflicts With Draft Handles**

| Required-before | Required-after | Relation | Worksheet edge |
| --- | --- | --- | --- |
| `emf.230.four_current_source` _definition_ | `emf.220.sourced_maxwell_equation` _core_formula_ | `requires` | `emf.220.sourced_maxwell_equation` -> `emf.230.four_current_source` |
| `emf.250.f_equals_dA_implies_homogeneous_identity` _derivation_step_ | `emf.240.homogeneous_maxwell_identity` _core_formula_ | `derives_from` | `emf.240.homogeneous_maxwell_identity` -> `emf.250.f_equals_dA_implies_homogeneous_identity` |
| `emf.350.dalembertian` _definition_ | `emf.340.source_free_wave_equation` _core_formula_ | `requires` | `emf.340.source_free_wave_equation` -> `emf.350.dalembertian` |

## Cross-Experiment Observations

All analyzed worksheet graphs are acyclic under the current relation orientation.
That makes dependency-order presentation mechanically feasible for the
acyclic examples.

The ordering conflicts are useful rather than alarming: they identify
places where the original prose introduced a memorable or familiar item
before its graph prerequisites. MEE should be expected to have more of
these than the EM-field worksheet because the famous rest-energy formula
comes late in the derivation graph.

For this pass, only `requires`, `derives_from`, `special_case_of`, and
`supplies_algebra_for` constrain the main order. Side-link relations such
as `elaborates`, `warns_about`, `gives_example_of`, and `connects_to` are
better treated as optional expansions, annotations, or navigation links.

The largest unresolved modelling issue is the orientation and purpose of
`supplies_algebra_for`. Some algebra support is genuinely on the main
derivation spine; other algebra support is explanatory detail that should
probably unfold after its target. This relation may need to split into
two relations before becoming production schema.

| Worksheet | Blocks | Constraints | Draft Conflicts | Side Links |
| --- | ---: | ---: | ---: | ---: |
| MEE Fine-Grained Graph Experiment | 36 | 31 | 5 | 20 |
| Electromagnetic Field Fine-Grained Graph Experiment | 38 | 58 | 3 | 20 |
