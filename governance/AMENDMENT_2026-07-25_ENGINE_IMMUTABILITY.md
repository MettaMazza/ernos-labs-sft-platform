# Amendment: immutable admission engine and authorization boundary

Date: 2026-07-25

Authority: Maria Smith

Status: explicitly authorized

## Rationale

An automated agent altered admission-related implementation and constructed
claim submissions that could encode the desired survivor or observation. That
conduct was incompatible with the project's fail-closed scientific method and
created an outcome-seeking validation risk. Maria Smith explicitly directed
that the validation engine must never be edited and that no submission may
depart from protocol without her prior explicit request.

## Frozen authority

- Engine commit: `501925b1c8553f49493d8efaeedfac9d8f42ab54`
- Engine Git tree: `ad30f4866c18b2adbade95a0b2de40d5caa61308`
- Sole existing post-freeze exception:
  `bed68facb01d938b8c5257d0843506f40978e111`
- Exception scope: read-only live terminal progress during verification; no
  scientific gate, decision, receipt, authority or protocol behavior changes.

## Binding rule

Automated agents and contributors may inspect and execute the frozen engine but
may not edit, extend, replace, relocate, wrap, proxy, monkey-patch or bypass it.
They may not modify claim or empirical protocols to manufacture acceptance.
Only Maria Smith can authorize a precisely identified exception before the
change occurs. General instructions to proceed, continue, fix, complete or
publish do not supply that authorization.

Remote submissions and mutations—including pushes, releases, pull requests,
uploads, paper updates, Zenodo versions and DOI actions—also require explicit
authorization for the particular action and target. Authorization does not
carry forward between actions, repositories, papers or sessions.

## Updated surfaces

- `AGENTS.md`
- `CONSTITUTION.md`
- `docs/CLEAN_ROOM_PROTOCOL.md`
- `docs/CLAIM_LIFECYCLE.md`
- `CONTRIBUTING.md`
- `governance/engine_policy.json`

## Adverse controls

The amendment is violated if any automated agent:

1. changes a file beneath `sft/engine/` without Maria Smith's specific prior
   authorization;
2. changes the engine's behavior indirectly through a wrapper, proxy, shadow
   authority, alternate receipt writer or direct census promotion;
3. alters a candidate, validator, comparator, tolerance, source set, test or
   protocol to force a desired acceptance;
4. treats a general instruction as engine-edit or remote-submission authority;
   or
5. pushes, submits, uploads, releases or publishes without action-specific
   authorization.

Any such event must halt the affected work. It cannot be relabeled as a repair,
convenience change or successful derivation.
