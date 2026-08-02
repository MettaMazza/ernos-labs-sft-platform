# Claim packages

Every scientific result receives a stable directory under `claims/` before it
is implemented. Copy the structure of `TEMPLATE/`, replace every placeholder
and keep the status no stronger than the preserved evidence.

Directory existence, a passing test or an earlier-corpus result does not admit
a v3 claim.

The current ordered census contains 2,765 admitted claim packages. The
read-only Lean 4 layer verifies their identities, sources, dependencies,
candidate and decision coverage, unique survivors, controls, certificates and
admitted receipts; it cannot create or change a claim status. See
`generated/lean4_validation/README.md` and
`audits/CURRENT_PROGRAMME_STATUS_2026-08-02.md`.
