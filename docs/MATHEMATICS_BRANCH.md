# Mathematics branch status and review guide

## Lean-verified current published successor — 2 August 2026

Version 1.6.1 is the published status-corrected successor for
this branch. It binds all 341 current registered claims and is included in the
17-branch Lean 4 PASS. The manuscript is
[`FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_6_1.md`](../publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_6_1.md), published at
[10.5281/zenodo.21761651](https://doi.org/10.5281/zenodo.21761651). This patch
corrects only the false prepublication wording. Earlier
open-work wording below is retained as historical chronology and does not
override the [2 August current programme ledger](../audits/CURRENT_PROGRAMME_STATUS_2026-08-02.md).

## Most recent published complete-field release — 29 July 2026

Status: `published_v1_5_complete_field_current_evidence_closed_extension_open`.

The authoritative complete-field paper is
[`FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md`](../publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md),
published as version 1.5.0 at
[10.5281/zenodo.21688766](https://doi.org/10.5281/zenodo.21688766) in the
retained concept DOI lineage `10.5281/zenodo.21516145`. It covers 323 claims,
97,280 candidates, 323 unique survivors and 1,292 controls. The historical
scope below is retained for chronology but is superseded wherever it describes
the branch as reconciliation-open.

Status: `published_v1_current_reconciliation_open`

Paper: [From Fold to Mathematics](../publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md)

DOI: [10.5281/zenodo.21516146](https://doi.org/10.5281/zenodo.21516146)

## Archived claim-set scope

The V3 Mathematics branch contains twelve dependency-ordered claims:

1. exact arithmetic and generated number structure;
2. discrete mathematics;
3. combinatorics;
4. graph and network theory;
5. algebraic structures;
6. order and conditional lattice structure;
7. finite computational geometry and topology;
8. exact probability and statistics from deterministic support and observation;
9. optimization and retained optima;
10. finite dynamical systems;
11. logic and proof boundaries; and
12. category, type and compositional structure.

The archived frozen inventory is
[`publications/inventories/mathematics.json`](../publications/inventories/mathematics.json).
It has no unclassified or frontier obligation. The twelve grammars contain 7,424
generated candidates and exactly twelve survivors. Every claim is
depth-independently closed, model-admitted and independently replicated at its
registered boundary. At that archived checkpoint, branch completion remained
blocked until every Mathematics-owned V1/V2 result had a same-strength V3
disposition. The later complete-field release and version 1.6.0 local successor
record that closure.

## Exact domain

Formal proof values are structural One, exact positive finite traces and parts,
canonical labels, fibres, words, pair cells, relations, forms and proof traces.
Semantic numerical zero, negative quantities, irrational or imaginary proof
values, floating proof arithmetic, completed infinity and ungenerated continua
are outside the branch boundary. Empty and identity cases use structural empty
One. Held orientation replaces signed magnitude.

Probability does not add random dynamics. It records exact held support relative
to complete deterministic support under an observation relation. Any later
natural-data claim must use the sealed blind empirical route and preserve every
row.

## Review route

Run the complete repository verifier:

```text
python3 -m sft verify-all   # macOS and most Linux systems
py -m sft verify-all        # standard Windows Python launcher
```

The command validates the repository, runs the complete test suite with 100%
core-engine executable-line coverage and reruns all admitted claims and their
independent validators in census order.

For a single claim, begin with its `WHY_DERIVATION_CHECK.md`, then inspect its
registration, candidate census, elimination receipt, controls, certificate,
execution binding, independent validator and model-admitted engine receipt. The
paper evidence map supplies exact file hashes for every one of those artifacts.

## Next branch

The next dependency branch is Information Science: symbols and
distinguishability; encoding and decoding; information quantity; entropy and
uncertainty; compression; channels and capacity; noise and error; coding;
mutual and conditional information; and classical, probabilistic and quantum
information correspondence.
