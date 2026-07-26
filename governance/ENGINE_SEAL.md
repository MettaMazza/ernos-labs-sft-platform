# Canonical SFT admission-engine seal

## Public identity

The canonical Smithian Fold Theory v3 admission engine is identified by both:

- Git tree: `ad30f4866c18b2adbade95a0b2de40d5caa61308`
- byte-manifest seal: `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`

The Git tree identifies the frozen committed directory. The SHA-256 seal binds
the exact runtime support of 16 files, every file's byte count and every file's
content hash. Both identities must agree. A Git identity alone is insufficient
because an uncommitted local edit can otherwise be imported while `HEAD` still
names the canonical tree.

## One command

From the repository root, every researcher, reviewer and automated system runs:

```text
python3 tools/verify_engine_seal.py
```

The command uses only the Python standard library and behaves identically on
macOS, Windows and Linux. Machine-readable output is available with `--json`.

A valid result begins:

```text
SFT ENGINE SEAL: VALID CANONICAL ENGINE
```

Any changed, missing, added or symbolically substituted engine file instead
returns a non-success status beginning:

```text
SFT ENGINE SEAL VIOLATION — VOID / INVALID / HALTED
```

The repository package also verifies the seal before any `sft.engine` module
can import. A mismatching runtime therefore halts ordinary admission launchers
even when their own script checks only the committed Git tree.

## What the seal makes invariant

The sealed bytes enforce the same registration, enumeration, forcing, form
closure, adverse-control, derivation-seal, independent-validation, empirical-
validation and model-admission behavior for every user. They preserve:

1. the sole root theorem and exact dependency trace;
2. the prohibition on axioms and free, fitted, learned or measurement-selected
   parameters;
3. complete declared candidate enumeration and one decision per candidate;
4. exactly one survivor, minimality and named-shape uniqueness;
5. the four mandatory adverse-control kinds;
6. implementation-distinct recomputation;
7. target custody, prediction sealing and post-seal measurement requirements;
8. complete favorable and unfavorable empirical row retention; and
9. fail-closed rejection before model admission.

Editing the seal manifest cannot ratify an edited engine. The verifier contains
the canonical seal identity independently and recomputes the manifest identity
before trusting its file list.

## What remains separately required

The seal proves that a result was evaluated by the identical engine only when
the seal was checked against the runtime that produced it. It does not turn an
inadmissible submission into science. A claim remains void if it hides a fitted
choice, imports an answer-producing prior, exposes a target before sealing,
misstates its candidate boundary, fabricates a control or omits evidence. The
claim's source manifest, derivation dependencies, complete census, rejected
alternatives, controls, external implementation, target custody and immutable
engine receipt remain independently inspectable requirements.

The seal also does not prevent someone who controls a private copy from editing
local files. Cryptography makes that edit detectable. Public immutability is
established when the canonical seal identity is anchored in Maria Smith's
authorized Git history, signed release material and Zenodo record. Until that
specific publication is authorized, the separate anchor registry truthfully
reports that no commit, signature, push or publication anchor has been made.

## Versioning and authority

There is no silent resealing. A different engine produces a different file
support, Git tree and SHA-256 seal and is not SFT v3 engine version 1. Only Maria
Smith may explicitly authorize a separately named engine version and seal.
Changing the manifest, verifier, guard, tests or documentation to disguise an
engine change is itself a protocol violation and cannot preserve the original
seal identity.

Researchers may independently publish reproductions of the two canonical
identities. No credential, contributor role or automated system may waive a
mismatch.
