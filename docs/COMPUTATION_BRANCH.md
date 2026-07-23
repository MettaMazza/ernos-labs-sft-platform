# Classical Computation branch status and review guide

Status: `frozen_complete`; standalone paper: `published`; publication:
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
`publications/inventories/computation.json`. It does not claim an unrestricted
Busy Beaver table, P versus NP separation, arbitrary circuit lower bounds,
physical implementations, application results or quantum operations. Named
historical models enter only as post-seal correspondence.

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
