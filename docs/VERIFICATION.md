# Complete verification command

Run from the repository root on macOS or Linux:

```text
python3 -m sft verify-all
```

On Windows use `py -m sft verify-all`.

## Expected runtime

This command is intentionally exhaustive. For the current 679-claim corpus,
allow approximately **20–45 minutes on a typical modern laptop**. Processor
speed, filesystem performance and the final network request can move a run
outside that range, and individual large candidate censuses or empirical
validators may remain quiet for several minutes while still progressing. This
is a provisional planning range based on present development runs, not yet a
statistically measured cross-platform average. Published release reports must
record complete timed runs on macOS, Windows and Linux so this note can be
replaced by a measured median, range and host specification.

The verifier prints progress during long phases. A run is complete only when it
prints `SFT COMPLETE VERIFICATION: PASS`; elapsed time alone is never evidence
of success.

This is the sole public validation route. It performs, in order:

1. repository and policy validation;
2. a generated external-measurement coverage audit that fails if an empirical
   claim lacks executable evidence or a Physics result terminates without a
   post-seal empirical descendant;
3. every unit, adverse-control and end-to-end engine test;
4. a standard-library trace over every executable line in every `sft.engine`
   module, failing unless measured coverage is exactly 100%;
5. loading the complete ordered execution manifest;
6. rerunning every admitted derivation from its current source with a fresh
   in-memory authority ledger;
7. rerunning its independent validator and controls;
8. comparing the recomputed receipt with the immutable census receipt; and
9. only after complete replay, fetching the current machine-accessible NIST
   CODATA table and testing the already-forced alpha, charged-lepton, Koide and
   terminal proton/electron results against complete reported uncertainty
   intervals using exact rational arithmetic.

An omitted claim, changed source, changed receipt, dependency-order error,
failed test, uncovered core-engine line, unavailable authoritative live source,
missing source row or failed exact live comparison makes the command fail.

The live comparison is a post-seal freshness check, not an input to derivation
and not an admission route. The registered capability-closed empirical
validators still rerun every preserved authoritative snapshot, favorable and
unfavorable row, custody check and tampered control. The network stage cannot
change a law, receipt or census entry.

## External-measurement completeness rule

Every externally measurable result must be compared automatically with
authoritative external data wherever such data exist. Partial external coverage
is an open blocker, not an acceptable completion category. Every empirical
claim must carry an executable comparator, complete source identities, every
registered row, uncertainties where reported, post-seal custody and unfavorable
controls. A formally forced Physics result must reach at least one such
post-seal empirical claim through its declared dependency chain. That automatic
ancestry check is a minimum coverage condition, not permission to omit another
measurable consequence of the same law.

Only a proposition with no empirical observable at its declared boundary may
remain formal-only. That exception must be justified by the claim's exact scope;
labelling a result “formal” does not itself establish non-measurability. When an
authoritative body exposes a stable machine endpoint, the final post-seal
freshness stage must query it directly. Static primary reports remain
hash-locked, versioned external records and must be re-registered when their
authoritative version changes.

The dated machine-audited external-validation state, including the exact
recovery identities for six historical empirical replay contexts, is recorded
in `audits/EXTERNAL_VALIDATION_UPDATE_2026-07-25.md` and its JSON companion.

## Immutable replay identity

Replay means byte-exact execution of the source context sealed at admission,
not acceptance of a previously stored receipt without execution. Source hashes
therefore include every byte, including terminal line endings and blank lines.
Do not run a formatter or normalizer across admitted source artifacts unless it
is proven to preserve their bytes.

Empirical replay also restores the host-platform and Python-implementation
labels sealed into the original isolation certificate. These are receipt-bound
metadata, not scientific inputs: the prediction, target custody, comparison,
all registered rows and adverse controls are still executed afresh on the
reviewer's actual operating system.

An existing receipt, certificate, census row and source identity are immutable.
If a later engine or source revision needs a compatibility run, preserve the
original replay context and record the new result as separate, versioned
compatibility evidence. Never replace the original evidence and never bypass
replay.

## Exact meaning of 100%

The percentage is executable-line coverage of the complete core engine package,
measured by Python's standard-library tracer. The release gate additionally
tests every named admission and rejection class. This is a precise software
test statement, not a claim that testing can prove the absence of every possible
future defect. Scientific closure remains claim-specific and is established by
generated enumeration, forcing, controls and independent certificates.
