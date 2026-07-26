# Post-seal Planck/CODATA vacuum-density scale test

Claim: `SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036`

## Why this comparison matters

The formal predecessor fixes four typed vacuum quantities and their transport before this empirical executable receives any target. This claim then tests the global share and normalized cosmological magnitude against a primary Planck parameter table, transports the dimensional relation through the measured Hubble interval and exact CODATA speed, and uses the measurement itself as an adverse control against conflating the local floor with the global density.

V1/V2 cosmological targets and an older local Planck transcription were known before the reconstruction, so this is not presented as historical blindness. The enforceable scientific boundary is operational: formal claim 035 had immutable engine receipt `sha256:c7b477...` before the primary PDF was downloaded; the capability-closed prediction program cannot read files, targets, clocks, environment, network or subprocesses; and the target custodian releases the committed record only after the prediction seal matches.

## Primary source and transcription correction

The source snapshot is the ESA Planck Legacy Archive's 341-page 68-percent parameter table PDF, hash

`sha256:03038805021f2f894e09f4b21b0f20418570e352822f095abcc085942919da70`.

Page 225, table 12.16, reports the complete registered rows:

- `H0 = 67.68 +/- 0.42 km s^-1 Mpc^-1`;
- `Omega_Lambda = 0.6889 +/- 0.0056`;
- `Omega_m = 0.3111 +/- 0.0056`.

The page directly shows `67.68`, not the older local transcription `67.66`. This claim records the correction explicitly and does not edit or invalidate any earlier receipt. The dimensional speed reference is the NIST/CODATA exact row `c=299792458 m s^-1`, or `299792.458 km s^-1`, snapshot hash `sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67`.

## Exact comparison

The complete Planck vacuum interval is

`[0.6889-0.0056, 0.6889+0.0056] = [6833/10000,1389/2000]`.

The sealed Fold share satisfies

`6833/10000 <= 11/16 <= 1389/2000`.

Multiplying both measurement endpoints by the separately forced three-space rate count gives

`[20499/10000,4167/2000]`.

The sealed normalized magnitude satisfies

`20499/10000 <= 33/16 <= 4167/2000`.

The Planck central rows also close exactly:

`0.6889 + 0.3111 = One`.

The complete Hubble interval is `[67.26,68.10]`. With exact CODATA `c`, the dimensional transport remains the exact positive interval

`[(33/16)(67.26/299792.458)^2, (33/16)(68.10/299792.458)^2] Mpc^-2`.

No square root, floating fit or signed proof magnitude is needed.

The adverse type check is decisive: `One/2^20` lies below the complete global vacuum-fraction interval, as does the finite-ledger mean `1/2`. That mismatch does not invalidate either local quantity; it invalidates their unscaled identification with the global fraction. The dimensional relation requires its held `H` and `c` references.

## Controls and falsification

The engine enumerates all `256` empirical grammar candidates and retains one. The target package preserves all Planck central values, uncertainties, the exact CODATA speed, the Hubble transcription correction and the local/global type control. A deliberately changed vacuum central value of `0.6000` removes `11/16` from the measurement interval and is rejected.

The claim is falsified if any source identity or row changes, either exact Fold magnitude leaves its complete interval, the central matter-vacuum budget ceases to close, dimensional transport becomes nonpositive or scale-inconsistent, `One/2^20` is relabeled as the global fraction, the old Hubble transcription is silently substituted, or any target changes the formal survivor.

## Machine evidence

- Candidate count: `256`.
- Measurement rows: `8`, including correction and adverse control.
- Closure: `depth_independent`.
- Source manifest: `sha256:f13f4bb53dc4e55f6ffa2503fba63bdc74c8024e6692b57e3f30269ee5c18485`.
- Derivation seal: `sha256:aac1f5afbedc98835000ee0959231e7e6213eae90e23f1502c48346abd816225`.
- Independent validation: `sha256:d8ddaf48a77d46203c68ba9687c9b06a2bc92bee78d687688e73cd0fa83b6cab`.
- Empirical validation: `sha256:7695b43af80dd5ba9987cee7e0375f9f91c9dcd81fde97020402fd544559998a`.
- Measurement receipt: `sha256:0bb3659038316226f202044b500f6bf1a6867720089a91f659b908e9fe356cf4`.
- Engine receipt: `sha256:6379f0d35a606d217e2351a35c42ae258aea71c52d8d20d2c4abeef2fdd8c202`.

This closes the declared V1/V2 vacuum-density magnitude family at current V3 strength while preserving future falsification and lawful extension.
