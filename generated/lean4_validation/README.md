# Lean 4 whole-model verification

This directory is an independent, read-only Lean 4 verification layer for the
current Smithian Fold Theory model. It does not replace the frozen admission
engine or the repository's existing verification authority. It reads the live
model artifacts from the repository root and writes only its generated report
under this directory.

The toolchain is pinned by `lean-toolchain` to Lean 4.32.0. The local `.elan/`
toolchain and `.lake/` build output are ignored, so building and running this
project does not edit the model, claim packages, census, receipts, engine, or
existing validation records.

## Current verified result — 2 August 2026

The pinned Lean 4.32.0 build and compiled verifier return `PASS` for the complete
current ordered census:

| Surface | Verified result |
|---|---:|
| Claims and proof-bearing accepted gates | 2,777/2,777 |
| Source-bound claims | 2,777/2,777 |
| Candidates | 898,902 |
| Decisions | 898,902 |
| Controls | 11,108 |
| Branch identifiers | 17 |
| Issues | 0 |

The machine report is `reports/whole_model_validation.json`, SHA-256
`sha256:6b6a5a9a9a0b74687a6f97fb3b4fcc7455968e35c82395290837cda60d7501cf`.
The standalone publication candidate and its evidence map are under
`publications/lean4_verification/`.

The root theorem and generic gate implications are native Lean propositions.
The other 2,776 scientific statements are checked as complete registered
artifacts by the Lean executable, not misrepresented as bespoke native Lean
theorems. The PASS supports formal coherence, current-census exhaustiveness,
unique-survivor enforcement and provenance integrity. It does not replace
empirical tests or establish superiority to every rival theory.

The initial whole-model run halted on six byte-level source-binding mismatches after
working-tree line-ending normalisation. The expected identities were not
weakened. Exact registered bytes were restored, all 385 registered external
bindings were re-audited with no remaining mismatch, and the unchanged
verifier then passed. The halt remains preserved as fail-closed custody
evidence.

## Formalized propositions

`SFTValidation/Root.lean` defines the registered two-class operational root as
an inductive type with exactly two constructors:

- `unpresentedAbsence`, which is rejected; and
- `presentedOccurrence`, which survives because a presentation supplies an
  occurrence.

It proves constructively that `presentedOccurrence` is the unique survivor.
The module prints Lean's axiom audit for the root theorem during compilation.

`SFTValidation/Gates.lean` defines the twelve whole-claim acceptance gates and
constructs a proof-bearing certificate only when every gate is true. Its
exported gate results are also included in the compile-time axiom audit.

## Complete live-model artifact verification

`SFTValidation/Verifier.lean` reads the current ordered claim census and
execution manifest directly. For every registered claim it checks:

- claim, branch, grammar, dependency, and execution-manifest identity;
- byte-exact source manifests against executable registrations and certificates;
- complete candidate cardinality and unique candidate identifiers;
- one-to-one decision coverage and exactly one survivor;
- closure scope, closure boundary, minimality, and named-shape uniqueness;
- the four mandatory controls and every registered empirical extension;
- empirical protocol, custody, isolation, retained-row, and hash bindings;
- certificate identity, closure, hashes, and preserved receipt lineage; and
- the current authoritative admitted receipt and every required admission gate.

The verifier fails closed: a malformed or missing artifact, a false gate, an
exception, a missing branch, or any issue produces a nonzero exit status.
The source-manifest gate uses `source_binding_probe.py` only to load the
model's registered Python execution factories; Lean consumes its result and
includes the source gate in each proof-bearing claim certificate. The probe is
read-only and is not an admission or receipt-writing route.

## Run

From this directory, after installing the pinned toolchain into `.elan/`:

```sh
ELAN_HOME="$PWD/.elan" PATH="$PWD/.elan/bin:$PATH" lake build
ELAN_HOME="$PWD/.elan" PATH="$PWD/.elan/bin:$PATH" \
  .lake/build/bin/sft-verify ../.. reports/whole_model_validation.json
```

Or use the checked-in wrapper:

```sh
./run_validation.sh
```

The machine-readable result is
`reports/whole_model_validation.json`. The two claim-package directories
reported as `uncensused_nonmodel_package_count` are not part of the current
ordered census and therefore are not counted as model branches or accepted
claims.
