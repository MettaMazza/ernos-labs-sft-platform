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
