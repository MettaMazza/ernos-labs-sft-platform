# Fundamental knowledge census

`claims.json` is the machine-readable global index of V3 claims admitted through
the engine. Earlier-corpus claims are not automatically admitted into it.

Every row must identify its claim package, status, exact boundary and
dependencies.

`lineage_reconciliation.json` registers the V1/V2 reconstruction requirement.
`prior_obligation_ownership.json` registers categorical ownership and blocks
branch successors until all owner-assigned obligations close at the same
strength.

Do not edit admitted rows manually. `EngineRepository` writes them only from a
closed, externally validated `SFTAdmissionEngine` receipt. Rejected and
conditional receipts remain outside the authoritative claim list.
