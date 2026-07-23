# SFT single admission engine

This package is the sole v3 model-admission kernel.

`SFTAdmissionEngine` executes registered programs through registration,
enumeration, forcing, controls, independent validation and optional blind
empirical validation. Any violation raises `EngineHalt` containing a
deterministic rejection receipt.

The package validates evidence structure; it does not predeclare any scientific
answer. Claim-specific generators, decisions, completeness proofs and external
validators live in their registered claim packages.

`EngineRepository` preserves every accepted or rejected receipt and is the sole
supported writer of model-admitted rows in `census/claims.json`. Conditional
evidence receives a receipt but cannot become a dependency.

Blind empirical work uses the same standard-library-only capability and target-
custody contract on macOS, Windows and Linux. It does not require Docker. The
portable verifier rejects missing denied capabilities, forbidden operations,
target presence, comparison-code presence or a changed certificate. Arbitrary
Python execution is not treated as isolated; the official capability-closed
Fold interpreter remains an explicit pre-empirical milestone.
