# Maths and SR authoring completion

13 November 2026 · `nested-explanations`. Local commits only; generated viewers
remain ignored. Follow the [authoring guide](../authoring/authoring_guide.md).

Complete statements, Definition/Explanation and dependency arguments, teaching
prose at level 70, selective block references, consolidated kinds and sequential
ordering. Preserve source identities, clarification paths, questions, artwork,
layout and tutorial targets. Do not broaden reading recipes implicitly.

| Stage | Scope | Status |
| --- | --- | --- |
| 1 | Shared ten-kind support, retaining legacy content | Complete: Advanced loads/renders; old kinds remain valid. 763 unit tests, 397 browser cases and the fast lane pass. |
| 2 | MATHS-1 prose, kinds, order and block references | Complete: 49 concept/five module blocks reviewed; canonical IDs/slots retained; unit and actual phone/desktop checks pass. |
| 3 | MATHS-2, building on MATHS-1 | Complete: 24 bodies and overview reviewed; consolidated kinds and precise input references; unit and nine focused browser checks pass. |
| 4 | SR-1 kind consolidation and systematic block-reference review | Complete: all 125 blocks reviewed; approved level-70 prose retained, with precise source pointers and a vector/covector clarification. |

SR-2 through SR-5 and eventual GR authoring are later stages, not authorised by
this four-stage batch. Check actual equations and reading routes on phone and
desktop, and canonical note/read identity. Run unit and focused module browser
checks per module, then the complete browser suite at the end of this batch.
Regenerate the SR+Maths viewer for review before broad checks.

The batch covers 198 concept blocks and seven module blocks. Concept blocks retain
their IDs, titles, statements and local clarification paths; module overviews
gain informative titles while retaining their IDs. Maths bodies were revised
at level 70; SR-1's existing revision was preserved. Reading recipes are unchanged;
Advanced remains optional. Questions, edges, artwork, layouts, tutorial targets,
SR-2–5 content and GR are unchanged.

Final verification: 765 unit tests pass. All 397 browser cases pass after two
note-label checks were made independent of the old module overview title
(395 passed in the full run; the two corrected checks passed on rerun).
The 12 focused Maths/SR-1/block-reference checks also pass. SR+Maths validation
reports zero errors and 62 visible warnings; see the domain reviews for intent.
The ignored SR+Maths viewer was regenerated for local review, without publication.

Detailed module decisions and source checks belong in the corresponding domain
review, not this progress table. No automatic merges, deletions or ID changes.

## Continuation — SR-2

13 November 2026, on `major-content-revision-maths-sr` after separating the
completed reading-tree work onto main. SR-2 is now revised: 65 original blocks
retain canonical identity and clarification scopes, gain concise statements,
consolidated kinds and level-70 bodies. Six Graphic blocks, a momentum frame-change
Derivation and a second mass–energy Intuition bring its total to 73 blocks.
The SR-2 module overview is revised too. See the [SR review](../../domains/sr/docs/reading_tree_authoring_review.md#sr-2--relativistic-particle-mechanics)
for the two rest-energy arguments, the one justified prerequisite addition and
source/preservation decisions. SR-3–5 and GR remain later work.

Verification: 768 unit tests pass; all 399 browser cases pass after a phone-width
equation correction and isolation of an order-dependent presentation test.
Focused phone/desktop checks cover both reading recipes, canonical read ticks
and the actual SR-2 equations. The ignored SR+Maths viewer is rebuilt locally.

## Completion — SR-3 to SR-5

The guide was reread before each module and the teaching target remains 70.

| Module | Original blocks reviewed | Current blocks | Main work |
| --- | ---: | ---: | --- |
| SR-3 | 87 | 96 | Complete particle/field variation and Hamiltonian reasoning. |
| SR-4 | 135 | 149 | Consistent SI conventions; potential, force and stress–energy derivations; gauge scope. |
| SR-5 | 85 | 94 | Noether and translation currents, Maxwell variation, waves and controlled radiation-reaction explanation. |

All 49 SR concepts now have Definition and Explanation blocks, explicit
statements throughout, consolidated kinds and canonical graphics. All 307
original SR-3–5 IDs and clarification paths remain; the earlier SR/Maths content,
questions/options, artwork, layout and tutorial targets are preserved.
The SR domain now contains 537 concept blocks. Reading recipes are unchanged.
GR revision is future work.

Final verification: 774 unit tests and all 405 browser cases pass (327 fast,
78 full). The full lane includes every guided tutorial on desktop and phone.
The three routes were also reviewed against their target content: three
Rest-energy narration prompts were brought into line with the revised
four-momentum and kinetic-energy blocks; tutorial actions and targets are
unchanged. Focused checks cover all SR-3–5 concepts, rendered equations and
both reading recipes. The ignored SR+Maths viewer is rebuilt for local review.
