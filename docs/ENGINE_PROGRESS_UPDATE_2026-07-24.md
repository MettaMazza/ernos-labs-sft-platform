# Verification progress-only update

Date: 2026-07-24

## Scope

This update changes only the visibility of `python3 -m sft verify-all` (or
`py -m sft verify-all` on Windows). The command now flushes live progress at
the repository-integrity, unit/E2E and coverage, and registered-derivation
replay stages. While the coverage subprocess remains active it emits a timed
heartbeat every thirty seconds. During replay it reports the first claim,
every twenty-five claims and the final claim.

## Exact implementation changes

- `sft.verification.verify_all` accepts an optional progress callback and
  emits stage boundaries around the unchanged validation functions.
- `sft.verification.rerun_registered_claims` accepts the same optional callback
  and emits counted replay milestones after a receipt has already been
  recomputed, compared and admitted to the temporary replay ledger.
- `sft.verification.run_core_coverage` retains its original silent
  `subprocess.run` route when no callback is supplied. With a callback it uses
  the same command and captured streams through `Popen.communicate`, adding
  only a thirty-second timeout loop that emits elapsed-time heartbeats.
- `sft.cli` supplies a writer that prefixes each line with
  `[SFT verify-all]` and uses `flush=True`, preventing long buffered silence.
- `tests/test_verification_progress.py` proves that progress delivery leaves
  the returned `VerificationReport` unchanged and that the CLI exposes the
  messages before its final summary.

## Explicit non-changes

The patch does not change the admission engine, engine policy, candidate
generation, elimination, survivor decision, closure tests, controls,
independent validators, empirical validators, source manifests, receipt
construction, canonical hashing, census order or fail-closed behavior. The
callback defaults to absent, so programmatic callers retain the prior silent
interface and receive the same report. Progress text has no scientific value,
does not enter a derivation, and is not hashed into any receipt.
