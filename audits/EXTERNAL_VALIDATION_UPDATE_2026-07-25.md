# External validation update — 25 July 2026

## Outcome

Six historical empirical replay contexts have been repaired exactly. The
recovery reran each claim's registered empirical validator against its
immutable derivation seal. A context was written only after its canonical hash
matched the empirical-validation hash already sealed in the claim certificate.
No claim, receipt, census row or engine file was changed by the recovery.

| Claim | Recovered empirical hash | Measurement receipt |
|---|---|---|
| `SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001` | `sha256:3df224f1ca64f8ccc26c3fd5d785d4ee2abdea51c783550accec714a96eb52d5` | `sha256:0c73be05888de167157643d1b1773ade8b7cb32fa0c4eb0fcc0e8aeef4c4b731` |
| `SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001` | `sha256:4580bae1908fdd208c75dc159f8ff406fbbcbbd9be2ec6f6e0e9376bc9a0244f` | `sha256:550f4a01b231c2375c639d5486b8c252ee0431cdf4012d8a7174fd5543d324cb` |
| `SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001` | `sha256:7dc5aa166443cb243a2a2d7e9e81be6188df5f77ee441a95879c35aec27a47fa` | `sha256:5d3f4de0ae278c3995c2316e770d497042e3bbd76514c9f502a946d0f707c62a` |
| `SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001` | `sha256:b2090f6bb9fc1db1e7963539ad9adf580de79e45a0681c0a77cf886046c99c8d` | `sha256:707f4c2183b11bb784794a61169b173740df83da19bd169960a8cc3f5fcbb803` |
| `SFT-PHYS-COSMO-SPATIAL-FLATNESS-001` | `sha256:d552516176eb76d0262093e421930cf43cf3c005763ee90e5c75a88faaf97978` | `sha256:d27eb94493dd7fa36684f9bb7cbd8333bec3046a0251767c2ca2f27cc9a48927` |
| `SFT-PHYS-COSMO-COMPLETE-BUDGET-001` | `sha256:4c109570794bded6ad2fd8b5b916845eb39fa85198d4fe9526291cb683430cd9` | `sha256:4bae1310817433cc59334a735d348e0b4b2295c0f5efaa6aeebb9eabb38da859` |

The recovery is reproducible with
`python3 tools/recover_historical_empirical_contexts.py`. It is idempotent and
fails before writing if any regenerated identity differs.

## Machine-audited corpus state

- Registered claims: 682.
- Empirical claims: 388.
- Missing empirical replay contexts: 0.
- Formal Physics results: 101.
- Formal Physics results reaching a declared post-seal empirical descendant:
  87.
- Formal Physics results without such a descendant: 14.

The remaining 14 are not hidden or treated as complete external validation:

1. `SFT-PHYS-BARYOGENESIS-DEPENDENCY-TERMINAL-021`
2. `SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031`
3. `SFT-PHYS-COUPLING-ACCUMULATED-SEPARATION-TERMINAL-015`
4. `SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016`
5. `SFT-PHYS-ELECTROWEAK-WZ-RATIO-002`
6. `SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023`
7. `SFT-PHYS-FOLD-UNIVERSE-TRANSPORT-TERMINAL-024`
8. `SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022`
9. `SFT-PHYS-MATTER-GENERATION-DEPTH-003`
10. `SFT-PHYS-MATTER-INTER-ENTRY-COUPLING-003`
11. `SFT-PHYS-MATTER-MIRROR-MASS-CLOSURE-003`
12. `SFT-PHYS-MATTER-MIXING-CORRESPONDENCE-003`
13. `SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020`
14. `SFT-PHYS-SCATTERING-PARTITION-PATH-TERMINAL-017`

The coverage gate therefore remains fail-closed. An ancestry link is only a
minimum mechanical coverage test. Each externally measurable consequence must
still be compared with authoritative data, with complete rows, uncertainty,
post-seal target custody and adverse controls. A dependency may not be added to
an older empirical claim merely to clear this list; a new, versioned empirical
successor must execute the actual comparison. If a statement has no empirical
observable at its exact declared scope, that boundary must be demonstrated
rather than assumed.

## Engine integrity

The canonical engine remains unchanged and verifies against seal
`sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`
and Git tree `ad30f4866c18b2adbade95a0b2de40d5caa61308`.
