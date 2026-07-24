# Complete verification command

Run from the repository root on macOS, Windows or Linux:

```text
python -m sft verify-all
```

This is the sole public validation route. It performs, in order:

1. repository and policy validation;
2. every unit, adverse-control and end-to-end engine test;
3. a standard-library trace over every executable line in every `sft.engine`
   module, failing unless measured coverage is exactly 100%;
4. loading the complete ordered execution manifest;
5. rerunning every admitted derivation from its current source with a fresh
   in-memory authority ledger;
6. rerunning its independent validator and controls; and
7. comparing the recomputed receipt with the immutable census receipt.

An omitted claim, changed source, changed receipt, dependency-order error,
failed test or uncovered core-engine line makes the command fail.

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
