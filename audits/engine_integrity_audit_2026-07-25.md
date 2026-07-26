# SFT v3 admission-engine history and empirical-strength audit

Date: 2026-07-25

Repository HEAD inspected: `1944fe037ed869d13c298246b37587ac0eb08dd0`

Remote main inspected: `1944fe037ed869d13c298246b37587ac0eb08dd0`

Audit boundary: every Git ref touching `sft/engine/`, the publication-compliance
gate, runtime admission launchers and the present working tree.

## Executive finding

The present runtime engine is clean. Its Git tree is exactly
`ad30f4866c18b2adbade95a0b2de40d5caa61308`, its 16 canonical files match the
frozen commit byte for byte, and there is no working-tree change beneath
`sft/engine/`.

The core `SFTAdmissionEngine` decision code has remained byte-identical since
the freeze. History nevertheless contains a real protected-boundary breach:
post-freeze claim-evidence and publication utilities were added beneath
`sft/engine/`. They did not remove or relax an admission gate, but they changed
the engine tree and therefore defeated the stronger claim that every run used
one identical protected directory. The files were later relocated outside the
engine and the exact frozen tree was restored.

The audit also found a runtime-attestation weakness: all 77 inspected admission
launchers imported `sft.engine` before performing any local identity check; 21
later compared only `HEAD:sft/engine`, and 56 contained no canonical tree
literal. That check cannot detect an uncommitted file edit. The new seal closes
this path by hashing actual runtime bytes before the package permits an engine
import.

## Complete engine history

| Commit | Engine tree | Change | Strength classification |
|---|---|---|---|
| `8f0e473c95f3682b2954f3be0140927a9aac4e91` | `e5e870f5efc1e408a9ce57b3544c32eb75468c3d` | Created the fail-closed engine | Initial authority |
| `9d5184bc45f0404425ddb3961c0640fa3f95e5ec` | `267cd6d792021c0f9b13eb7928d5515e8a4386a4` | Added root-theorem handling and bound external and empirical validation hashes into receipts | Pre-freeze strengthening; one neutral census-order change |
| `501925b1c8553f49493d8efaeedfac9d8f42ab54` | `ad30f4866c18b2adbade95a0b2de40d5caa61308` | Re-expressed a custody comparison as a named positive boolean for cross-platform byte stability | Semantically equivalent freeze |
| `780de3a7888d69c6d1c10678a174654f3dcc0a02` | `cc3147268896dccfe81a96c42f56af7a940c020f` | Added `fold_language.py`, `custody.py`, `hostile.py` and public exports under the engine namespace | Post-freeze boundary violation; auxiliary empirical strengthening, no core-gate change |
| `8963cd974ee2aeb640879f655884d97dd5af800b` | `311b7e6e8b9b85f3bb53dcd5fa6cc5a11e7e8f36` | Added `publication_compliance.py` beneath the engine namespace | Post-freeze boundary violation; publication gate, no claim-admission change |
| `3c815132bccd9a56a3a7c05105a620607e979536` | `ad30f4866c18b2adbade95a0b2de40d5caa61308` | Relocated the four auxiliary modules without rewriting their content and restored `__init__.py` | Complete tree restoration |

No later commit on any inspected Git ref changes `sft/engine/`. The authorized
live-progress commit `bed68facb01d938b8c5257d0843506f40978e111` does not touch
the engine and changes terminal visibility only.

The frozen and current `sft/engine/engine.py` SHA-256 identity is
`cc150b5556b62f3d67e91ad9d008811abb429b2a3d547159a565b53cfab7e525`.
An exact Git comparison between the frozen and last pre-restoration versions
returns no difference for that file.

## Empirical-strength findings

### Admission gates

The frozen engine applies registration, enumeration, forcing, form closure,
four-kind adverse controls, derivation sealing, implementation-distinct
validation, blind empirical validation when registered, and model admission in
that order. A violation constructs a rejection receipt and raises `EngineHalt`.
The post-freeze namespace additions did not edit this sequence or its predicate
methods.

### Historical namespace interval

Between the first expanded-tree commit and the restoration parent, 458 claim
identities entered the census; all 458 remain present at the inspected HEAD.
Of those, 341 source packages explicitly bound one or more of the auxiliary
paths while those paths lived under `sft/engine/`:

- 171 Physics claims;
- 86 Chemistry claims; and
- 84 Materials claims.

Their immutable receipts are preserved, and their core admission judge was the
byte-identical `SFTAdmissionEngine`. They cannot, however, be described as
having the present full-directory seal because that seal did not exist and the
protected tree was larger. The historical source bytes remain reconstructible
from Git. Current files that still name the relocated old paths cannot be
silently rewritten without changing their registered source identity. Any
future canonical-seal replay must therefore be a disclosed, versioned replay;
it must preserve the original receipt rather than pretending the history never
occurred.

This is a seal-attestation distinction, not a retroactive rewrite of the
receipts or a claim that the unchanged core gates accepted a different
survivor.

### Temporary publication-gate weakening

Commit `86327a0004ea3d51eb3e230e4217eab2385a6b21` temporarily allowed the label
`current_categorical_inventory_closed` to bypass incomplete all-source
ownership assignment. That weakened publication completeness, not claim
admission. Commit `27fab0ceecb09748855d7bbab1a2c06aa358bae9` restored the
exhaustive blocker twelve minutes later. The current gate again requires full
assignment and `closed_same_strength`.

An additional uncommitted test relaxation was detected during the current
Physics work and restored before this audit. It never entered Git history. The
current test again asserts strict publication behavior, and its working-tree
diff is empty. Git cannot independently reconstruct discarded uncommitted
bytes, so this row is reported from the retained work record rather than
misrepresented as a commit finding.

### Runtime identity gap

A committed-tree lookup does not hash the files Python imports. An uncommitted
edit can leave `git rev-parse HEAD:sft/engine` unchanged. Before this seal, none
of the 77 inspected admission launchers established an actual-byte check before
engine import. This was an attestation failure surface even though the present
tree is clean.

The correction is external to the engine:

- `governance/engine_seal_v1.json` binds all canonical runtime files;
- `sft/engine_seal.py` recomputes actual byte identities and exact support;
- `sft/__init__.py` requires the seal before any engine submodule import; and
- `tools/verify_engine_seal.py` gives researchers a standalone one-command
  verifier that does not import the engine.

### Scientific boundary of the seal

The seal fixes the judge. It does not excuse a fraudulent submission. The
engine validates registered evidence structures, identities and required
relations; source review and capability custody remain necessary to establish
that a claimant did not hide a target, fitted selector or fabricated premise
inside claim-specific code. A canonical engine result is valid only when both
the engine seal and the complete claim admission route pass. Neither condition
substitutes for the other.

## Current canonical identities

- engine Git tree: `ad30f4866c18b2adbade95a0b2de40d5caa61308`
- actual-byte seal: `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`
- canonical file count: 16
- current engine working-tree changes: none
- current seal result: `VALID_CANONICAL_ENGINE`
- external anchoring: prepared locally; not yet pushed, signed or published

## Required interpretation

Any result produced after an engine-byte mismatch, missing file, extra file,
symbolic substitution or altered manifest is `VOID_INVALID_HALTED`. A claimant
cannot restore validity by editing the verifier or issuing a new local hash.
Reviewers compare the presented seal with the canonical public identity.

The final immutable public trust anchor requires Maria Smith's separate
authorization to commit, push and publish the seal identity. No such remote
action occurred during this audit.
