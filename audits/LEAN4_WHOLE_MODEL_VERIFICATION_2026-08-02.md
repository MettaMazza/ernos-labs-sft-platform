# Lean 4 whole-model verification audit — 2 August 2026

**Author and publication authority:** Maria Smith  
**Audit status:** PASS  
**Publication status:** Local evidence record; no remote action authorised

## Result

The independent Lean 4 layer passed the complete current ordered SFT census: 2,777/2,777 claims accepted, 898,902 candidates and decisions checked, 11,108 controls checked, 17 branches traversed and 0 issue reported.

- Machine report: `generated/lean4_validation/reports/whole_model_validation.json`
- Machine report SHA-256: `sha256:6b6a5a9a9a0b74687a6f97fb3b4fcc7455968e35c82395290837cda60d7501cf`
- Census identity: `sha256:f3f540f77a9b677bf7ddb9f5c6ea1ea41f08e57bb07163e25f385fd4d1dcde71`
- Execution-manifest identity: `sha256:517fd288f4484f43fdc0343b17fcabd06ea9e12c977a4512d4a891dd038fce41`
- Toolchain: `leanprover/lean4:v4.32.0`
- Standalone paper: `publications/lean4_verification/SMITHIAN_FOLD_THEORY_LEAN4_WHOLE_MODEL_VERIFICATION_PAPER_V1_0.md`
- Evidence map: `publications/lean4_verification/SMITHIAN_FOLD_THEORY_LEAN4_WHOLE_MODEL_VERIFICATION_EVIDENCE_MAP_V1_0.json`

## Exact interpretation

Lean natively formalises the registered two-class operational root and proves `presentedOccurrence` is the unique survivor. It also proves the implications of the twelve acceptance gates and constructs a proof-bearing certificate only for an all-true gate record. The other 2,776 current claims are parsed and checked as complete registered repository artifacts by the Lean executable; they are not each restated as bespoke Lean propositions in this version.

The result supports formal coherence, exhaustive current-census coverage, exactly-one-survivor enforcement, source custody, dependency integrity, certificate and receipt binding and cross-branch consistency. It does not replace empirical validation or prove comparative superiority to every alternative theory.

## Preserved mismatch halt

The initial run halted on six source-capture byte mismatches caused by working-tree line-ending normalisation. The expected hashes were not weakened. The exact registered bytes were restored, the six paths were marked for byte preservation, all 385 registered external bindings were audited with no remaining mismatch, and the unchanged verifier reran to PASS. The halt is preserved as evidence of fail-closed sensitivity.

## Protected boundaries

The protected engine seal and verification-authority seal passed before publication-layer work. The Lean project is read-only with respect to model claims and writes only its generated report. No engine receipt, historical receipt, published paper or DOI record was rewritten.
