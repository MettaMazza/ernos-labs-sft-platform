# Reproducibility — SFT V3 Protein Fold Computational Proof

**Version:** 0.9.4  
**Date:** 31 July 2026  
**Publication status:** Supporting record for the authorised preliminary-results release  

## 1. Environment and authority checks

Run from the repository root:

```bash
python3 tools/verify_engine_seal.py
python3 tools/verify_verification_authority_seal.py
```

The expected public engine identity is Git tree
`ad30f4866c18b2adbade95a0b2de40d5caa61308` and runtime-byte seal
`sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`.
The verification-authority seal is
`sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`.
Do not repair or reseal a mismatch.

## 2. Complete application test suite

```bash
python3 -m unittest discover \
  -s applications/frontier/v3_computational_proofs/protein_folding/tests \
  -p 'test_*.py'
```

Current expected outcome:

```text
Ran 898 tests
OK
```

Elapsed time depends on the machine. The 31 July 2026 verification completed in
`92.265` seconds on the current Apple workstation. The current receipt is
`audits/full_test_suite_v21.json`. It supersedes the 893-test v20 receipt only
for publication-audit integration; scientific gate v20 remains unchanged.
Application-directory invocations that omit
the repository root from the Python import path are command-context errors, not
scientific test results; the earlier clerical abort remains recorded in its
producing receipt.

The second registered real-carrier shard and its independent archive verifier
can be checked separately from the repository root:

```bash
python3 applications/frontier/v3_computational_proofs/protein_folding/solver/verify_second_real_partitioned_frontier_deep_shard_v1.py
python3 -m unittest applications.frontier.v3_computational_proofs.protein_folding.tests.test_second_real_partitioned_frontier_deep_shard_v1
```

The expected result is independent verification with zero failures, followed by
four passing tests. The authoritative execution itself is preserved in
`audits/second_real_partitioned_frontier_deep_shard_v1.json` and its compressed
machine archive; it need not be rerun merely to verify the receipt.

The disjoint 10,266-candidate sibling and complete 10,620-candidate parent
reconstruction are verified with:

```bash
python3 applications/frontier/v3_computational_proofs/protein_folding/solver/verify_third_real_partitioned_frontier_deep_shard_v1.py
python3 -m unittest applications.frontier.v3_computational_proofs.protein_folding.tests.test_third_real_partitioned_frontier_deep_shard_v1
```

The resumable parallel continuation expands that predecessor to one complete
215,940-candidate parent prefix with 107 retained frontier states. Its primary
and independent records are
`audits/resumable_parallel_parent_execution_v1.json` and
`audits/resumable_parallel_parent_execution_v1_independent_verification.json`.

The next registered fine-grained extension closes one complete
3,347,070-candidate parent prefix across 789 disjoint shards, with 40,899
completed leaves, 3,306,171 certified-pruned candidates and 135 retained
frontier states. Verify its partition, archive and independent reconstruction
from the repository root with:

```bash
python3 applications/frontier/v3_computational_proofs/protein_folding/solver/verify_seeded_parallel_parent_extension_v2.py
python3 -m pytest -q applications/frontier/v3_computational_proofs/protein_folding/tests/test_seeded_parallel_parent_extension_v2.py
```

The expected outcomes are independent verification with zero failures and four
passing tests. The execution and verification records are
`audits/seeded_parallel_parent_extension_v2.json` and
`audits/seeded_parallel_parent_extension_v2_independent_verification.json`.

The disjoint next-parent extension is complete. Its frozen registration in
`spec/seeded_parallel_parent_extension_v3.json` partitions 38,826,012 new
candidates across 11,012 shards and extends the verified predecessor to one
42,173,082-candidate parent. Verify the complete candidate partition, all shard
and state identities, the final archive and exact reduced frontier with:

```bash
python3 applications/frontier/v3_computational_proofs/protein_folding/solver/verify_seeded_parallel_parent_extension_v3.py
python3 -m pytest -q applications/frontier/v3_computational_proofs/protein_folding/tests/test_seeded_parallel_parent_extension_v3_registration.py
```

The expected results are independent verification of 11,012 shards,
42,173,082 target candidates and 205 frontier states with zero failures and
zero symbolic fallbacks, plus four passing registration tests. The execution,
verification and compressed result records are
`audits/seeded_parallel_parent_extension_v3.json`,
`audits/seeded_parallel_parent_extension_v3_independent_verification.json` and
`audits/fourth_real_parent_frontier_v3.json.gz`.

## 3. Source-custody reconstruction

From the protein-folding workspace:

```bash
python3 solver/generate_protein_scale_condition_uncertainty_interface_custody_v1.py
python3 solver/verify_protein_scale_condition_uncertainty_interface_custody_v1.py
```

The current primary and independent audit identities are:

- primary: `99c8be5271e5545ea13f1731d1f05c6cf8ec0eea23622c8a9bc578387080a722`;
- independent: `6edb769f9da138dd0398bf47b5835ae558f0d744212b1c566a8a220d647f90ea`.

The generated surface must retain 17 source records, 60 local assignments,
1,600 ordered interfaces, 218 protonation states, 47,524 protonation interfaces
and zero verification failures.

## 4. Corrected historical development carrier

The 4APD sequence is:

```text
HAEGTFTSDVSSYLEGQAAKEFIAWLVRGRG
```

The preserved V2-material reconstruction bridge is a development control only:

```bash
python3 solver/run_v2_reconstruction_control_v3.py \
  HAEGTFTSDVSSYLEGQAAKEFIAWLVRGRG \
  audits/development/reproduction_4apd_carbonyl_corrected
```

Do not use the resulting structure as a V3 prediction or holdout. A clean run
must bind the preserved V2 command and runtime hashes, emit 239 heavy atoms and
244 bonds, and record zero target accesses.

The authoritative corrected development files remain under:

```text
audits/development/v2_reconstruction_control_fresh_short_4apd_v2_carbonyl_corrected/
```

## 5. Complete interaction ledger

Generation:

```bash
python3 solver/generate_whole_chain_interaction_ledger_control_v1.py \
  --archive audits/development/reproduction_4apd_carbonyl_corrected/interaction_ledger_v1.json.gz \
  --summary audits/development/reproduction_4apd_carbonyl_corrected/interaction_ledger_summary_v1.json
```

Independent verification:

```bash
python3 solver/verify_whole_chain_interaction_ledger_control_v1.py \
  --archive audits/development/reproduction_4apd_carbonyl_corrected/interaction_ledger_v1.json.gz \
  --summary audits/development/reproduction_4apd_carbonyl_corrected/interaction_ledger_summary_v1.json \
  --output audits/development/reproduction_4apd_carbonyl_corrected/interaction_ledger_independent_verification_v1.json
```

Expected invariant counts:

| Quantity | Expected |
|---|---:|
| Heavy atoms | 239 |
| Bonds | 244 |
| Unordered atom pairs | 28,441 |
| Endpoint incidences | 56,882 |
| Shared-atom correlations | 6,740,517 |
| Sub-`1 A` pairs | 0 |
| Independent verification failures | 0 |

The authoritative corrected compressed archive SHA-256 is
`a3b2563d81374c61418360fddb43745c15524fa5a79cdf9c05c54efcbcfbb791`.
The uncompressed canonical JSON contains 25,691,185 bytes and has SHA-256
`292639141abc549efd5cacfd16fae9ca4bede4bf808f604fad415ba6e8874a46`.

## 6. Predictor execution gate

```bash
python3 solver/run_predictor_execution_gate_v1.py \
  --archive audits/development/v2_reconstruction_control_fresh_short_4apd_v2_carbonyl_corrected/interaction_ledger_v1.json.gz \
  --summary audits/development/v2_reconstruction_control_fresh_short_4apd_v2_carbonyl_corrected/interaction_ledger_summary_v1.json \
  --verification audits/development/v2_reconstruction_control_fresh_short_4apd_v2_carbonyl_corrected/interaction_ledger_independent_verification_v1.json \
  --output audits/development/reproduction_capability_halt_v1.json
```

Independent verification:

```bash
python3 solver/verify_predictor_execution_gate_v1.py \
  --result audits/development/reproduction_capability_halt_v1.json \
  --output audits/development/reproduction_capability_halt_independent_verification_v1.json
```

Expected output class: `capability_halt`. The record must expose all six
unavailable coordinate families, emit no prediction or representative, and
record zero target accesses.

## 7. Development evaluation

Evaluation is permitted only after the applicable development carrier has been
sealed. The current local metric kernel is
`evaluators/structural_metrics.py`. It consumes already mapped paired C-alpha
arrays and does not select targets, mappings or representatives.

Expected corrected 4APD values:

```text
tm_repo                     0.08579343893330212
lddt_ca                     0.5241935483870968
ca_rmsd95_angstrom          6.25666027980953
kabsch_ca_rmsd_angstrom     6.515371977465647
ca_drmsd_angstrom           5.18633263505115
```

`tm_repo` is a historical repository diagnostic, not the registered external
full-chain TM-score.

## 8. Physical-coordinate census verification

```bash
python3 -m unittest \
  applications.frontier.v3_computational_proofs.protein_folding.tests.test_condition_bound_physical_coordinate_census_v1 \
  -v
```

Expected result: six focused tests pass. The census must report six structural
laws, zero complete executable protein coordinate families, zero unresolved
transports and a required capability halt.

## 9. Development holdout verification

The three current short-protein records are development evidence. Do not rerun
their target-selection registrars after the targets have been opened. Verify
the preserved registrations, seals, predictions, chronology and evaluations
from the repository root:

```bash
python3 -m unittest discover \
  -s applications/frontier/v3_computational_proofs/protein_folding/tests \
  -p 'test_hydrophobic_majority_alpha_holdouts_v1.py' -v
```

Expected current records:

| Target | Chronology | Official median TM-score | Current classification |
|---|---|---:|---|
| 4B19 | Fresh sealed V2-generalised baseline | `0.17500` across 5 NMR models | Adverse development baseline |
| 8HJC | First unseen hydrophobic-majority transfer | `0.18242` across 20 NMR models | Adverse blind development evidence |
| 1JDM | Unseen cysteine-bounded transfer | `0.45609` across 16 NMR models | Positive blind development evidence for the narrowed class |

The consolidated chronology and identities are in
`audits/development/hydrophobic_majority_alpha_holdout_progress_v2.json`.

## 10. Canonical TM-align evaluator

The source, portability change, executable and parser identities are verified
with:

```bash
python3 -m unittest discover \
  -s applications/frontier/v3_computational_proofs/protein_folding/tests \
  -p 'test_tmalign_evaluator_v1.py' -v
```

The source SHA-256 is
`c68bb4ddc4f6162b2aa53fafb53ed8007eb3f24c21e62ced18a93604742fb013`;
the executable SHA-256 is
`02850a90e548bdd7d2c2280124649323efde2c4aa0d8580348e9f00a701420f6`.
Campaign normalisation uses the full registered sequence length through `-u`.
All deposited NMR models and complete evaluator stdout remain retained.

## 11. Pinned AlphaFold 3 environment

From the protein-folding workspace:

```bash
python3 comparator/verify_local_af3_environment_v1.py
python3 -m unittest discover -s tests -p 'test_alphafold3*' -v
```

The verifier performs no network, model-parameter, full-database, target or
campaign access. It must report the pinned source environment installed, MPS
visible, and all seven official data tests passing. It also reruns and preserves
the upstream inference suite's current `1/17` result: 16 errors arise from its
CUDA-labelled backend requests and the absent restricted parameters. The
verifier returns success only when this favourable and unavailable evidence is
classified exactly, never when inference readiness is falsely promoted.

## 12. Primary campaign and comparator boundary

Do not select or open the primary 100-target panel, run the official matched
campaign or inspect an AlphaFold campaign output while the certified full-V3
predictor gate emits `capability_halt`. The completed short-protein development
holdouts do not alter this primary chronology.

Official AlphaFold 3 execution additionally requires:

- the frozen source commit;
- a verified weights SHA-256;
- the registered historical database surface;
- a compliant full-data execution environment; and
- separately authorised remote compute and storage if the local environment
  remains insufficient.

Access to the model parameters also requires explicit confirmation of
non-commercial eligibility and acceptance of the registered AlphaFold 3 Model
Parameters Terms of Use. Neither acceptance nor paid provisioning may be
inferred from general authority to continue this programme.

## 13. Machine archive verification

From the protein-folding workspace:

```bash
python3 paper/generate_machine_archive_manifest_v1.py --verify
```

The verifier hashes every current regular publication file and fails if a file,
size or identity differs. Local AlphaFold runtime files, restricted parameters,
full databases, Python caches and manifest self-reference are explicitly
excluded. Regenerate the manifest after any authorised file change.

## 14. Interpretation of a successful replay

A successful replay establishes that the current code reproduces the current
representation, custody, correction and halt records. It does not establish a
fold prediction, empirical validation, parity, publication readiness or model
admission.
