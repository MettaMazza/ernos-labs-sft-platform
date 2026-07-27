# Frozen verification authority

## Purpose

The canonical engine seal protects the admission engine itself. This separate
authority seal protects the shared evidence gates around it: repository
verification, branch and publication verifiers, discipline-census verifiers,
schemas, shared policy, and the active Chemistry closure map implicated in the
2026-07-26 correction.

The protected files are enumerated by exact path, byte count and SHA-256 digest
in `verification_authority_seal_v1.json`. The verifier recomputes the manifest
identity and every protected file from disk. A missing, added-by-substitution,
symbolic or changed protected file returns `VOID_INVALID_HALTED`.

## Non-ratification rule

A halted verifier is evidence. No contributor or automated system may change
its expected count, predicate, comparator, tolerance, source set, mapping or
supporting helper to turn that result into a pass. The following do not cure the
violation:

- calling the edit bookkeeping;
- replacing a fixed expectation with a value derived from a newly edited map;
- moving the same weakened rule into another file;
- changing the authority manifest or its verifier to accept the changed bytes;
- deleting the adverse run; or
- crediting an admitted narrow claim with broader obligations that it did not
  separately close.

The lawful response is to preserve the halted state, improve the scientific
submission outside the protected gate, and run the unchanged gate again.

## Versioning

Existing protected gates are never edited in place. If new knowledge genuinely
requires a new gate, Maria Smith must explicitly authorize its exact scope
before implementation. The successor is created under a new versioned path,
the predecessor and its results remain preserved, and a new authority seal is
issued rather than silently rewriting version 1.

Claim-specific independent validators are different from shared gates. They
are created as part of a submission before admission. Their implementation hash
is bound into the engine receipt; after that receipt exists, the exact validator
is immutable. A successor claim must use a new claim identity and its own new
validator.

## Local protection and external trust boundary

`python3 tools/lock_verification_authority.py` removes ordinary write permission
from every protected path on macOS, Linux and Windows. On macOS it additionally
sets the user-immutable filesystem flag where supported. This prevents
accidental or ordinary in-place edits.

Cryptographic verification makes changes detectable; it cannot make files
literally unchangeable to a process that controls the same operating-system
account and can also remove file flags or replace a local checker. The public
authority seal therefore becomes independently anchored only when Maria Smith
explicitly authorizes its commit and publication to external, append-only
records such as GitHub and Zenodo. No local tool may claim that remote anchor
before it exists.

## Required commands

Before any official scientific or publication operation:

```text
python3 tools/verify_engine_seal.py
python3 tools/verify_verification_authority_seal.py
```

Both must pass. A failure in either halts the affected operation.
