# Published branch archive and current reconstruction status

> **Live programme status:** the authoritative 29 July 2026 working-tree ledger
> is [`audits/CURRENT_PROGRAMME_STATUS_2026-07-29.md`](../../audits/CURRENT_PROGRAMME_STATUS_2026-07-29.md).
> This directory records published archival boundaries and must not be used to
> erase newer admitted local continuation work or to imply that an unissued
> successor has already been published.

The `current/` path is retained for compatibility with immutable manifests and
release references. See
[`ARCHIVE_AND_SUCCESSOR_POLICY.md`](../ARCHIVE_AND_SUCCESSOR_POLICY.md); the
directory name does not assert current scientific completeness.

## Current boundary and published roadmap successors

The papers below are real published, citable archival records. Their claim
packages and receipts remain immutable. All fifteen registered branch
foundations are published. The local working tree has since completed the dated
full-field boundaries for Mathematics through Materials and started Biology at
82/424 obligations. Those successor packages remain local until separately
authorized and issued.

The project now uses one rule for every branch: first publish a complete
foundational reconstruction, then extend the same paper through sequential
versions until the dated full-field census is current-evidence complete. Even a
current-knowledge-complete edition remains open to lawful discoveries,
corrections, falsification and stronger evidence.

Same-paper roadmap successors are published for Methods Paper 00, Foundation,
Mathematics, Information Science, Classical Computation, Reversible and Quantum
Computation, Physics, Chemistry and Materials. They preserve all scientific
results and add each branch's exact foundation/full-field plan. The coordinated
set through Chemistry is recorded in
[`branch_roadmap_successor_versions.json`](../../publication/branch_roadmap_successor_versions.json);
the subsequently completed Materials release is recorded in
[`materials_release.json`](../../publication/materials_release.json).

## Published archival papers

| Branch | Paper | DOI | Current status |
|---|---|---|---|
| Methods 00 | [There Is No Nothing](../successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_3.md) | [10.5281/zenodo.21627646](https://doi.org/10.5281/zenodo.21627646) | Version 0.3 publishes the shared two-layer branch roadmap |
| Foundation | [From Nothing to Fold](../successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_3.md) | [10.5281/zenodo.21627656](https://doi.org/10.5281/zenodo.21627656) | 16-law foundation current-evidence complete; v1.3 roadmap published; extension-open |
| Mathematics | [From Fold to Mathematics](../successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_4.md) | [10.5281/zenodo.21627708](https://doi.org/10.5281/zenodo.21627708) | Published v1.4; local 323/323 complete-field v1.5 package prepared |
| Information Science | [From Distinction to Information](../successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_3.md) | [10.5281/zenodo.21627717](https://doi.org/10.5281/zenodo.21627717) | Published v1.3; local 262/262 complete-field v1.4 package prepared |
| Classical Computation | [After Turing: The Fold Machine](../successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_3.md) | [10.5281/zenodo.21627721](https://doi.org/10.5281/zenodo.21627721) | Published v1.3; local 369/369 complete-field v1.4 package prepared |
| Quantum Computation | [The Quantum Fold Machine](../successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_3.md) | [10.5281/zenodo.21627748](https://doi.org/10.5281/zenodo.21627748) | Published v1.3; local 288/288 complete-field v1.4 package prepared |
| Physics | [From Fold to Physics](../successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_2.md) | [10.5281/zenodo.21627765](https://doi.org/10.5281/zenodo.21627765) | Published v1.2; local 368/368 current-scope v1.3 package prepared |
| Chemistry | [From Fold to Chemistry](chemistry/FROM_FOLD_TO_CHEMISTRY.md) | [10.5281/zenodo.21627782](https://doi.org/10.5281/zenodo.21627782) | Published v1.2; local 272/272 discipline obligations and 281 live claims documented in v1.3 package |
| Materials | [From Fold to Materials](materials/FROM_FOLD_TO_MATERIALS.md) | [10.5281/zenodo.21629306](https://doi.org/10.5281/zenodo.21629306) | Published v1.2; local 289/289 complete-field v1.3 package prepared |
| Biology | [From Fold to Life](biology/FROM_FOLD_TO_LIFE.md) | [10.5281/zenodo.21630203](https://doi.org/10.5281/zenodo.21630203) | Published foundation v1.0; local full-field continuation active at 82/424 |
| Medicine | [From Fold to Medicine](medicine/FROM_FOLD_TO_MEDICINE.md) | [10.5281/zenodo.21630785](https://doi.org/10.5281/zenodo.21630785) | Published foundation v1.0; 76 live claims after completed placebo/nocebo return; full-field census not frozen |
| Consciousness and Cognitive Science | [From Fold to Consciousness](consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS.md) | [10.5281/zenodo.21636397](https://doi.org/10.5281/zenodo.21636397) | Published foundation v1.0; 77 live claims after completed nonordinary return; full-field census not frozen |
| Earth and Environmental Sciences | [From One World to Earth](earth_environment/FROM_ONE_WORLD_TO_EARTH.md) | [10.5281/zenodo.21640810](https://doi.org/10.5281/zenodo.21640810) | Published foundation v1.0; 75 live claims after completed tipping return; full-field census not frozen |
| Astronomy and Cosmology | [From One Sky to Cosmos](astronomy_cosmology/FROM_ONE_SKY_TO_COSMOS.md) | [10.5281/zenodo.21640812](https://doi.org/10.5281/zenodo.21640812) | Published foundation v1.0; 77 live claims after completed prior-return family; full-field census not frozen |
| Social and Collective Systems | [From One Relation to Society](social_collective_systems/FROM_ONE_RELATION_TO_SOCIETY.md) | [10.5281/zenodo.21640814](https://doi.org/10.5281/zenodo.21640814) | Published foundation v1.0; 76 live claims after completed exact-return family; full-field census not frozen |
| Engineering Translation | [From One Law to a Working World](engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD.md) | [10.5281/zenodo.21640816](https://doi.org/10.5281/zenodo.21640816) | Published foundation v1.0; 80 live claims after completed translation-return family; full-field census not frozen |

## Machine-readable current gate

Audit all branches without mutation:

```text
python3 tools/verify_publication_compliance.py
```

Require the complete current Physics standard:

```text
python3 tools/verify_publication_compliance.py --branch physics --require-ready
```

The second command intentionally halts while any assigned obligation is
missing, weaker than its registered source result, empirically unclosed or
absent from the successor manuscript.
