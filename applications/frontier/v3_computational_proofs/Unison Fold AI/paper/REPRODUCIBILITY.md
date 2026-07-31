# Reproducibility — From Attention to an Exact Conversational Architecture

**Candidate version:** 0.1.0-rc1
**Date:** 31 July 2026
**Author and publication authority:** Maria Smith
**DOI:** [10.5281/zenodo.21726397](https://doi.org/10.5281/zenodo.21726397)
**Publication status:** Published open-access preliminary version

## 1. Reproduction boundary

This record covers the preliminary Unison Fold AI evidence state reported in
the accompanying paper. It includes the registered 40-row operation-role map,
the 27-entry dependency inventory, the 256-candidate translation census, the
identified predecessor artefact, retained adverse conversation results,
teacher-signal and corpus custody, and the existing application test suite.

The active teacher-distilled build has no result in this paper because its
final bundle, exact acceptance record, independent verification, frozen
conversation decision, comparator record and manual Discord observation do
not yet exist. Later results require a successor paper version under
`PUBLICATION_UPDATE_PROTOCOL.md`.

Reproduction of the recorded mechanism does not establish conversational
quality, GPT-2 parity, a completed model or a newly admitted SFT law.

## 2. Prerequisites and credential boundary

Use Python 3.9 or later. From the repository root:

```bash
cd "applications/frontier/v3_computational_proofs/Unison Fold AI/development"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[discord,dev,build]'
```

No Discord credential is required for offline reproduction. Do not copy,
print, hash, archive or load the original Unison AI token during these steps.
Large model artefacts, raw teacher signals, restricted corpus rows, caches and
the mutable terminal log remain outside the paper payload.

## 3. Protected-authority checks

Run from the repository root:

```bash
python3 tools/verify_engine_seal.py
python3 tools/verify_verification_authority_seal.py
```

The paper records the following preparation-boundary identities:

| Authority | Recorded identity |
|---|---|
| Frozen engine Git tree | `ad30f4866c18b2adbade95a0b2de40d5caa61308` |
| Runtime-byte seal | `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a` |
| Verification-authority seal | `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8` |

A mismatch invalidates the attempted replay. Do not repair or reseal a
protected authority as part of paper reproduction.

## 4. Registered inventories

Validate the registered JSON without rewriting it:

```bash
python3 -m json.tool \
  "applications/frontier/v3_computational_proofs/Unison Fold AI/spec/dependency_inventory.json" \
  >/dev/null
python3 -m json.tool \
  "applications/frontier/v3_computational_proofs/Unison Fold AI/proof/translation_candidate_census.json" \
  >/dev/null
python3 -m json.tool \
  "applications/frontier/v3_computational_proofs/Unison Fold AI/audits/readiness_audit_v1.json" \
  >/dev/null
```

The recorded boundary is:

| Inventory | Expected record |
|---|---:|
| Operation-role rows | 40 |
| Dependency entries | 27 |
| Translation axes | 8 |
| Translation candidates | 256 |
| Eliminated candidates | 255 |
| Surviving candidates | 1 |

The sole survivor is `UNISON-TRANS-001`; its internal canonical census
identity is
`sha256:019797d71296fcc4e8dffa878e3c9d84ab8f70eebaa19dd187b28abd89b80346`.
These counts report the existing registered boundary; this paper does not
alter the operation map, dependency inventory or verification specification.

## 5. Application test suite

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="applications/frontier/v3_computational_proofs/Unison Fold AI/development/src:applications/frontier/v3_computational_proofs/Unison Fold AI" \
python3 -m unittest discover \
  -s "applications/frontier/v3_computational_proofs/Unison Fold AI/development/tests" \
  -p 'test_*.py' -v
```

Expected recorded result:

```text
Ran 56 tests
OK
```

The suite establishes implementation and protocol behaviour only at its
declared boundaries. It does not establish acceptable unseen conversation.

## 6. Independent predecessor reconstruction

The widest completed predecessor before the active build has these recorded
identities:

| Object | Identity |
|---|---|
| Bundle | `sha256:6b460b208438a1b4c71695fa9e700eb5cb2f41b02758946df48bc6ee6a4c81e4` |
| Model | `sha256:fe8f6f64f8786334d63a0aabdcef260b3fcbcfe0e05f727d07fd39bd4ffbde4d` |
| Tokenizer | `sha256:09891845445384c92df8fb2cdf300d5e201dce4403781b80f2a8167ef4d3dc90` |

Reconstruct its saved forward trace without importing the runtime:

```bash
cd "applications/frontier/v3_computational_proofs/Unison Fold AI"
python3 independent_verifier/verify_forward.py \
  evidence/development/native_build_v1/model_artifact.json \
  evidence/development/native_build_v1/forward_trace.json \
  /tmp/unison-fold-ai-predecessor-independent-report.json
```

The existing report records `status: pass` and
`runtime_module_imported: false`. This result belongs to the identified
predecessor; active-candidate verification remains pending.

## 7. Corpus, teacher and adverse-result custody

The paper records the following immutable identities:

| Object | Identity |
|---|---|
| DailyDialog outer archive | `sha256:2de93416a95060057d8b95ef9e2ab9b17a317906f1e352414001a1887f081193` |
| DailyDialog train archive | `sha256:6191257f8250da0e045bfd1d017645e15b2358df975ec4c5c431a5a1f99662a4` |
| Development rows | `sha256:9f8b7e22bbfb9cdfcbaab785a9ba78aef5b3af44fcc2719b742cbfcbd1f9f050` |
| Frozen development probe | `sha256:12d7c5fb8e7cf66a3538a30ecb8335ae6ad325d6c0dd3a4614f925238245bf26` |
| GPT-2 124M teacher weights | `sha256:248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707` |
| Teacher signal corpus | `sha256:b4fb07550506758266ef4f433285d594307cdfcddfa21c336058aefefa19e6bf` |

DailyDialog remains restricted to the recorded local, non-commercial custody
boundary. GPT-2 serves only as the frozen offline teacher and later comparator;
no teacher parameter is copied into the native student and no teacher is
permitted at runtime. All 11 recorded conversation candidates remain rejected
for hand-off.

## 8. Paper rendering

Render the paper from the repository root:

```bash
python3 tools/render_unison_fold_ai_preliminary_paper.py
```

The expected output path is:

```text
output/pdf/sft-v3-unison-fold-ai-computational-proof-preliminary-v0.1.0-rc1.pdf
```

For the authorised release, the PDF text and metadata were checked and all 18
pages were rendered and visually inspected for clipping, overlap,
illegibility, malformed tables and missing content.

## 9. Reproducibility conclusion

This procedure reproduces the preliminary architecture, registered evidence
and identified predecessor boundary. It deliberately leaves the active build,
unseen conversation, comparator, final seals and manual Discord observation
open. The direct GitHub `main` push and Zenodo publication of version
0.1.0-rc1 were separately authorised; future remote actions are not authorised
by this record.
