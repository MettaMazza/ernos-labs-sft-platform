# Guidance for computational and AI agents

This file governs every automated assistant working in this repository.

## Authority order

1. Maria Smith's explicit instruction.
2. `CONSTITUTION.md`.
3. The registered dependency order and claim package.
4. Repository guidance files.
5. Implementation convenience.

Convenience never overrides the scientific constitution.

## Absolute engine immutability

`sft/engine/` is a frozen authority boundary. Its authoritative Git tree is
`ad30f4866c18b2adbade95a0b2de40d5caa61308`, established at commit
`501925b1c8553f49493d8efaeedfac9d8f42ab54`.

An automated agent must never edit, add, delete, move, rename, regenerate,
replace, re-export, monkey-patch or indirectly override anything in
`sft/engine/`. It must never change the engine identity, gates, schemas,
receipt behavior, authority behavior, source binding, isolation rules or test
expectations to obtain an admission. A failing or inconvenient claim must be
corrected outside the engine or remain rejected.

The sole existing post-freeze exception is the read-only live-progress
transparency change in commit `bed68facb01d938b8c5257d0843506f40978e111`.
That exception changes terminal visibility only and grants no authority for
further engine or protocol edits.

Only a new, precise and explicit instruction from Maria Smith that identifies
the proposed engine change may authorize one. General instructions such as
“proceed”, “continue”, “fix it”, “complete the branch”, “make it pass” or
“publish” are never engine-edit authorization. If an agent believes an engine
change is required, it must halt before editing and request Maria's decision.

Before importing or executing any SFT module, an automated agent must require
the canonical runtime-byte seal. The public identities are Git tree
`ad30f4866c18b2adbade95a0b2de40d5caa61308` and SHA-256 seal
`sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`.
Run `python3 tools/verify_engine_seal.py`; the package also enforces this check
before engine import. Any changed, missing, added or symbolically substituted
engine file, or any changed seal manifest, makes the attempted run
`VOID_INVALID_HALTED`. The agent must not edit the seal, verifier or guard to
ratify a mismatch.

No alternate admission engine, compatibility proxy, wrapper, shadow census,
synthetic receipt writer or weaker submission route may be created. Moving the
same behavior outside `sft/engine/` does not make a bypass permissible. Every
scientific submission must satisfy the published protocol through the frozen
engine without target leakage, premarked survivors or outcome-seeking changes.

## Required behavior

- Work only on the requested scope.
- Preserve existing user changes and scientific artifacts.
- Use exact arithmetic in derivational code.
- Generate candidate spaces from stated rules.
- Record rejected alternatives and unfavorable controls.
- Separate WHY, DERIVATION and CHECK.
- Name every provenance class.
- Treat earlier SFT repositories as comparison objects, not proof imports.
- Keep correspondence with conventional theory downstream of derivation.
- Halt or mark `OPEN` when a required closure is absent.
- Report conditional finite results with their exact grammar and depth.
- Use applications only as validation domains.
- Keep target data and scores structurally inaccessible before an empirical
  prediction seal.
- Run every proposed v3 derivation through `SFTAdmissionEngine`; never edit the
  census directly to simulate admission.
- Preserve the engine's accepted or rejected receipt without rewriting it.
- Verify the frozen engine tree before an official admission run and halt on
  any difference.
- Preserve every completed row, including failures and unfavorable outcomes.
- Ask before any push, publication, DOI action or coordinated update to older
  repositories.

## Compression and restart continuity — mandatory

Conversation memory, a compacted summary, an earlier plan and an old numerical
count are never sufficient evidence of the current work position.  After any
context compression, agent restart, hand-off or uncertainty about progress, an
automated agent must remain read-only until it has reconstructed the live
checkpoint from the repository itself.

The reconstruction must inspect, at minimum:

1. the current repository and branch;
2. the newest immutable model-admitted receipts and their timestamps;
3. the newest claim packages and certificates;
4. the active branch continuation checkpoint;
5. the current branch obligation/gap census; and
6. the current publication inventory and gate artifacts.

The agent must compare those sources and state the exact last admitted claim,
the exact remaining operation and any disagreement between them before doing
scientific work.  A generated audit or conversational summary may identify
something to inspect, but it may not override admitted receipts or substitute
for direct inspection of the relevant claim packages.  If the sources
disagree, the agent must halt mutation, resolve the discrepancy read-only and
report it; it must never choose the older or larger workload merely because it
looks comprehensive.

An admitted claim family is completed evidence and must not be regenerated,
resubmitted, revalidated or rebuilt merely because context was compressed.
Never restart a branch from an earlier family, repeat an atomic audit, expand a
remaining-count from memory, or rerun a heavy verification command unless the
live checkpoint proves it is the next required operation or Maria explicitly
orders that exact replay.  New work must begin at the first genuinely absent
receipt after the live checkpoint.

After every new official admission, the agent must immediately update the
durable continuation checkpoint with the claim ID, receipt hash, closure
status and next exact operation.  This update is continuity bookkeeping, not a
scientific admission and never changes an immutable receipt.  Before ending a
turn that leaves work in progress, the agent must ensure the checkpoint names
the precise restart position in small current counts.

### Current Physics restart boundary

As of 2026-07-26, the newest admitted formal Physics claim is
`SFT-PHYS-GRAND-LOCK-TERMINAL-075`, receipt
`sha256:ae18f67371c8e7054430935d6b5e5f3162f24cf9cba073769384bf7ba467d817`.
Its 4,096-form grammar binds the complete pre-lock Physics ownership surface,
534-node acyclic dependency dictionary, root trace to the foundational One,
exact headline vector, cross-domain identity graph and generator-successor
adverse census.  Its empirical successor is
`SFT-PHYS-VALIDATION-GRAND-LOCK-076`, receipt
`sha256:93f4497d6f7ef3c477246079f62c21f96a7ae27fd9516fa876e9d413bbab569e`.
That 256-form claim reconciles all 234 pre-lock empirical claims, 147 distinct
source identities, every available measurement receipt, all six disclosed
legacy receipt shapes and all fourteen detected unfavorable/scope claims.  The
first 076 submission halted on duplicate dependencies and its rejected receipt
is retained; the unchanged scientific claim was admitted only after the
duplicate registration entries were removed.

The categorical audit is now 488/488 same-strength current-evidence closed
with zero open atom and zero remaining family.  The live Physics inventory
contains 349 admitted claims.  Formal and empirical Grand Locks 075 and 076
are the authoritative closure records.  A later handwritten 49-ready/300-
blocked publication ledger was not an engine result, contradicted admitted
receipts and passed empirical certificates, and must never be used to classify
the Physics claims.  Publication readiness is determined from the complete
inventory, immutable admitted receipts, complete claim evidence, passed
empirical certificates, Grand Locks, paper coverage and publication gate.
Remote release remains explicitly unauthorized.  Do not repeat any Physics
family, Grand Lock, inventory rebuild or full `verify-all` run because of
compression.  Do not push or publish without Maria's explicit authorization.

## Prohibited behavior

- Do not import a pretrained consensus equation or mathematical model to fill a
  derivational gap.
- Do not choose a law because it matches a desired constant, benchmark or
  application result.
- Do not hand-pick a candidate neighborhood and call the survivor unique.
- Do not use floating-point equality as an SFT proof.
- Do not allow measured values to enter derivation or prediction.
- Do not silently relabel an observational, constitutional or empirical result
  as directly forced.
- Do not delete failed evidence or select only favorable rows.
- Do not describe an opaque predictor's accuracy as proof of an unstated law.
- Do not modify the future v4 trigger merely to begin self-hosting early.
- Do not attribute scientific authorship or publication authority to an agent.
- Do not call a branch paper complete until its frozen current-knowledge
  obligation inventory passes the branch publication gate.
- Do not alter a protocol, candidate generator, validator, comparator,
  tolerance, source set, test or submission package for the purpose of making
  a desired result pass.
- Do not submit, push, publish, release, upload, create or update a DOI, open a
  pull request, send a contribution, or alter any remote record without
  Maria's explicit action-specific authorization. Prior authorization for a
  different submission or publication does not carry forward.

## File placement

- Scientific implementation: `sft/<science>/`.
- Claim evidence: `claims/<claim-id>/`.
- Natural-science protocols and observations: `experiments/`.
- Conventional comparison: `correspondence/`.
- Generated independent code: `generated/`.
- Current census: `census/`.
- Unclosed work: `frontier/`.
- Application translations: `applications/frontier/` until authorized.

## Completion statement

When reporting work, distinguish:

- files created or changed;
- checks actually executed;
- mathematical status;
- empirical status;
- remaining frontier;
- whether anything was pushed or published.

Never claim comprehensive closure from repository scaffolding, compilation or
unit-test success alone.
