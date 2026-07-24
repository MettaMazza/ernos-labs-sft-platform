# Published branch archive and current reconstruction status

The `current/` path is retained for compatibility with immutable manifests and
release references. See
[`ARCHIVE_AND_SUCCESSOR_POLICY.md`](../ARCHIVE_AND_SUCCESSOR_POLICY.md); the
directory name does not assert current scientific completeness.

## Completion correction

The eight papers below are real published, citable and immutable archival
artifacts. Their claim packages and receipts remain preserved. They are not
currently designated complete V3 branch papers because the later full
V1/V2-to-V3 audit found that the publication gate checked each paper only
against its self-declared frozen inventory, not against every registered prior
result belonging to that branch.

The binding finding and repair are documented in
[`PUBLISHED_BRANCH_COMPLETENESS_AUDIT_2026-07-24.md`](../../audits/PUBLISHED_BRANCH_COMPLETENESS_AUDIT_2026-07-24.md).
Successor publication is blocked until categorical ownership and same-strength
reconstruction are complete. Foundation has now passed that stronger route;
the other seven listed branches remain blocked.

The current Foundation account is
[`Foundation Branch Paper 002`](../successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_002.md),
with its [rendered PDF](../../output/pdf/from-nothing-to-fold-foundation-branch-paper-002.pdf)
and complete successor evidence bundle. Paper 001 below remains immutable
archival evidence.

This correction does not alter any paper, DOI, hash, engine receipt or failed
experimental record. It corrects the claim of current completeness.

## Published archival papers

| Branch | Paper | DOI | Current status |
|---|---|---|---|
| Foundation | [From Nothing to Fold](foundation/FROM_NOTHING_TO_FOLD.md) | [10.5281/zenodo.21515629](https://doi.org/10.5281/zenodo.21515629) | Published v1 archive; Paper 002 successor closed and release-ready |
| Mathematics | [From Fold to Mathematics](mathematics/FROM_FOLD_TO_MATHEMATICS.md) | [10.5281/zenodo.21516146](https://doi.org/10.5281/zenodo.21516146) | Published v1; successor blocked |
| Information Science | [From Distinction to Information](information_science/FROM_DISTINCTION_TO_INFORMATION.md) | [10.5281/zenodo.21516916](https://doi.org/10.5281/zenodo.21516916) | Published v1; successor blocked |
| Classical Computation | [After Turing: The Fold Machine](computation/AFTER_TURING_THE_FOLD_MACHINE.md) | [10.5281/zenodo.21518311](https://doi.org/10.5281/zenodo.21518311) | Published v1; successor blocked |
| Quantum Computation | [The Quantum Fold Machine](quantum_computation/THE_QUANTUM_FOLD_MACHINE.md) | [10.5281/zenodo.21518313](https://doi.org/10.5281/zenodo.21518313) | Published v1; successor blocked |
| Physics | [From Fold to Physics](physics/FROM_FOLD_TO_PHYSICS.md) | [10.5281/zenodo.21520881](https://doi.org/10.5281/zenodo.21520881) | Published v1; superseded for current completeness; paper covers 140 of 160 live Physics claims and the full value audit is open |
| Chemistry | [From Fold to Chemistry](chemistry/FROM_FOLD_TO_CHEMISTRY.md) | [10.5281/zenodo.21531455](https://doi.org/10.5281/zenodo.21531455) | Published v1; successor must correct Physics dependency placement |
| Materials | [From Fold to Materials](materials/FROM_FOLD_TO_MATERIALS.md) | [10.5281/zenodo.21532482](https://doi.org/10.5281/zenodo.21532482) | Published v1; successor blocked by owner/same-strength audit |

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
