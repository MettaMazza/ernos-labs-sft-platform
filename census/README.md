# Fundamental knowledge census

As of the 29 July 2026 working-tree checkpoint, `claims.json` contains 2,751
registered, model-admitted V3 claims. The branch-level interpretation of that
live census is indexed in
[`../audits/CURRENT_PROGRAMME_STATUS_2026-07-29.md`](../audits/CURRENT_PROGRAMME_STATUS_2026-07-29.md).

`claims.json` is the machine-readable global index of V3 claims admitted through
the engine. Earlier-corpus claims are not automatically admitted into it.

Every row must identify its claim package, status, exact boundary and
dependencies.

`lineage_reconciliation.json` registers the V1/V2 reconstruction requirement.
`prior_obligation_ownership.json` registers categorical ownership and blocks
branch successors until all owner-assigned obligations close at the same
strength.

The dated 14/14 novel-return programme completion and the older global lineage
row/step merge are distinct ledgers. Completion of the former does not silently
rewrite the latter; the final one-owner global merge remains a final-ToE gate.

Do not edit admitted rows manually. `EngineRepository` writes them only from a
closed, externally validated `SFTAdmissionEngine` receipt. Rejected and
conditional receipts remain outside the authoritative claim list.
