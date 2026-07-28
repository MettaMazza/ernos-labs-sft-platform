# Complete verification command

Run from the repository root on macOS or Linux:

```text
python3 -m sft verify-all
```

On Windows use `py -m sft verify-all`.

## Expected runtime

This command is intentionally exhaustive. The last complete timed run of the
current 1,319-claim corpus took **1 hour, 19 minutes and 13.7 seconds** on an
Apple M3 Ultra Mac with 512 GiB memory, macOS 15.6 and Python 3.9.6. It started
at 2026-07-28 07:31:18 UTC and printed the terminal pass at 2026-07-28
08:50:31 UTC.

Reviewers using a comparable machine should reserve at least **two hours**.
Contributors using ordinary laptops or slower storage should allow several
hours. Processor speed, filesystem performance, available memory and the final
network request can move a run outside those expectations. Individual large
candidate censuses or empirical validators may remain quiet for several
minutes while still progressing. This is one measured reference run, not yet a
cross-platform median or guarantee. Complete timed macOS, Windows and Linux
runs should continue to be recorded so a measured distribution can replace
this planning guidance.

### Last complete timed verification

- Command: `python3 -m sft verify-all`
- Result: `SFT COMPLETE VERIFICATION: PASS`
- Recorded interval: **4,753.740 seconds** (**01:19:13.740**)
- Corpus: **1,319/1,319 registered derivations replayed**
- Tests: **969/969 unit and end-to-end tests passed**
- Core engine: **1,264/1,264 executable lines covered (100%)**
- Measurement coverage: **1,011 empirical claims**; **114/114** formal Physics
  claims reach measurement
- Live comparison: **5/5** current NIST/CODATA checks passed
- Host: Mac15,14; Apple M3 Ultra; arm64; 512 GiB memory; macOS 15.6 build
  24G84; Python 3.9.6
- Dated operational record:
  `audits/FULL_VERIFICATION_RUNTIME_2026-07-28_FOUNDATIONS_1319.json`

The earlier 1,029-claim timed run remains preserved at
`audits/FULL_VERIFICATION_RUNTIME_2026-07-28.json` as historical operational
evidence; it is not the current-corpus verification record.

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
