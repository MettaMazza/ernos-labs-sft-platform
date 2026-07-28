# Published branch archive and current reconstruction status

The `current/` path is retained for compatibility with immutable manifests and
release references. See
[`ARCHIVE_AND_SUCCESSOR_POLICY.md`](../ARCHIVE_AND_SUCCESSOR_POLICY.md); the
directory name does not assert current scientific completeness.

## Current boundary and published roadmap successors

The papers below are real published, citable archival records.
Their claim packages and receipts remain immutable. All fifteen registered
branch foundations are now published. Later ownership audits and same-strength
reconstructions repaired the earlier completion boundary through Physics; the
Chemistry foundation is secure and 90 further Chemistry laws have also been
admitted through ORG-011. Every complete-field programme remains open until its
dated field census has been fully admitted at the same standard.

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
| Mathematics | [From Fold to Mathematics](../successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_4.md) | [10.5281/zenodo.21627708](https://doi.org/10.5281/zenodo.21627708) | 22-law kernel plus calculator lineage admitted; v1.4 full-field roadmap published |
| Information Science | [From Distinction to Information](../successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_3.md) | [10.5281/zenodo.21627717](https://doi.org/10.5281/zenodo.21627717) | 12-law kernel and 77 prior obligations complete; v1.3 roadmap published |
| Classical Computation | [After Turing: The Fold Machine](../successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_3.md) | [10.5281/zenodo.21627721](https://doi.org/10.5281/zenodo.21627721) | 116 laws and 134 prior obligations admitted; v1.3 roadmap published |
| Quantum Computation | [The Quantum Fold Machine](../successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_3.md) | [10.5281/zenodo.21627748](https://doi.org/10.5281/zenodo.21627748) | 22 laws and 29 prior obligations admitted; v1.3 roadmap published |
| Physics | [From Fold to Physics](../successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_2.md) | [10.5281/zenodo.21627765](https://doi.org/10.5281/zenodo.21627765) | 349 laws and 488 prior atoms current-evidence complete; v1.2 roadmap published; extension-open |
| Chemistry | [From Fold to Chemistry](chemistry/FROM_FOLD_TO_CHEMISTRY.md) | [10.5281/zenodo.21627782](https://doi.org/10.5281/zenodo.21627782) | Foundation 86/86 secure; 90 further laws admitted; v1.2 published; 97 continuation operations remain |
| Materials | [From Fold to Materials](materials/FROM_FOLD_TO_MATERIALS.md) | [10.5281/zenodo.21629306](https://doi.org/10.5281/zenodo.21629306) | Version 1.2; 92 laws and 56/56 prior Materials atoms current-evidence closed; extension-open |
| Biology | [From Fold to Life](biology/FROM_FOLD_TO_LIFE.md) | [10.5281/zenodo.21630203](https://doi.org/10.5281/zenodo.21630203) | Version 1.0; 75 foundational laws and 30/30 prior Biology atoms current-evidence closed; extension-open |
| Medicine | [From Fold to Medicine](medicine/FROM_FOLD_TO_MEDICINE.md) | [10.5281/zenodo.21630785](https://doi.org/10.5281/zenodo.21630785) | Version 1.0; 72 foundational laws and 5/5 prior Medicine atoms current-evidence closed; extension-open |
| Consciousness and Cognitive Science | [From Fold to Consciousness](consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS.md) | [10.5281/zenodo.21636397](https://doi.org/10.5281/zenodo.21636397) | Version 1.0; 72 foundational laws and 46/46 prior atoms current-evidence closed; extension-open |
| Earth and Environmental Sciences | [From One World to Earth](earth_environment/FROM_ONE_WORLD_TO_EARTH.md) | [10.5281/zenodo.21640810](https://doi.org/10.5281/zenodo.21640810) | Version 1.0; 74 foundational laws and 3/3 prior atoms current-evidence closed; extension-open |
| Astronomy and Cosmology | [From One Sky to Cosmos](astronomy_cosmology/FROM_ONE_SKY_TO_COSMOS.md) | [10.5281/zenodo.21640812](https://doi.org/10.5281/zenodo.21640812) | Version 1.0; 72 foundational laws and 53/53 prior atoms current-evidence closed; extension-open |
| Social and Collective Systems | [From One Relation to Society](social_collective_systems/FROM_ONE_RELATION_TO_SOCIETY.md) | [10.5281/zenodo.21640814](https://doi.org/10.5281/zenodo.21640814) | Version 1.0; 72 foundational laws and 5/5 prior atoms current-evidence closed; extension-open |
| Engineering Translation | [From One Law to a Working World](engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD.md) | [10.5281/zenodo.21640816](https://doi.org/10.5281/zenodo.21640816) | Version 1.0; 72 foundational laws and 7/7 prior atoms current-evidence closed; extension-open |

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
