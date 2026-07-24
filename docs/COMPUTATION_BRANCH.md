# Classical Computation branch status and review guide

Status: `published_v1_inventory_closed_v2_reconciliation_open`; standalone paper: `published`; publication:
`10.5281/zenodo.21518311`.

Paper: [After Turing: The Fold Machine](../publications/current/computation/AFTER_TURING_THE_FOLD_MACHINE.md)

## Closed scope

The branch contains 113 dependency-ordered claims across:

1. Formal Computation - 12;
2. Computability - 10;
3. Computational Complexity - 13;
4. Algorithms and mathematical data structures - 14;
5. Semantics and mathematical programming theory - 12;
6. Concurrent and Distributed Computation - 12;
7. Cryptography and Computational Security - 13;
8. Learning and Intelligence Theory - 14; and
9. Scientific Computation - 13.

The complete grammars contain 28,928 candidates and exactly 113 survivors.
Every claim has a structural-One base/successor certificate, four passing
controls, an independent validator and a model-admitted receipt. The frozen
inventory contains no unclassified or frontier row.

## Exact boundary

Closure applies to the exact generated-finite kernels in
`publications/inventories/computation.json`. The later authoritative V2 corpus
Steps 404-406 additionally derive native unrestricted Fold Busy-Beaver
behavior, `P_F = NP_F`, and arbitrary admitted Fold-circuit lower bounds. Those
results are scientific V2 closures whose V3 clean-room replication is pending;
they must not be described as absent from SFT and must not be imported into the
V3 census without new receipts. They make no claim about arbitrary external
Turing tables, languages, polynomial conventions or Boolean gate bases.

Physical implementations, application results and quantum operations remain
outside this classical inventory. Named historical models enter only as
post-seal correspondence.

## Review route

Run `python3 -m sft verify-all` on macOS/Linux or `py -m sft verify-all` on
Windows. For each claim, inspect `WHY_DERIVATION_CHECK.md`, registration,
candidate census, elimination receipt, controls, certificate, execution,
independent validator and model-admitted receipt. The paper evidence map binds
all 113 sections to exact artifact hashes.

## Publication record

The 396-page paper, complete Markdown source, repository evidence/source ZIP
and checksum ledger are published at DOI
[`10.5281/zenodo.21518311`](https://doi.org/10.5281/zenodo.21518311) and in the
GitHub release
[`classical-computation-v1.0.0`](https://github.com/MettaMazza/ernos-labs-sft-platform/releases/tag/classical-computation-v1.0.0).
