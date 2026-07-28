# Physics mismatch-admission correction ledger

Status date: 2026-07-25

This ledger prevents a historical engine receipt from being mistaken for current Physics branch closure when its submitted acceptance predicate treated a mismatch, tension, or nonmatching row as a successful empirical result. Historical receipts remain immutable. Branch closure uses only the measured-value successor recorded here.

The untouched admission engine remains authoritative. The defect corrected here is claim-level: an acceptance predicate that expected a mismatch could be verified faithfully by the engine while remaining scientifically inadmissible under the project standard.

## Resolved successors

### Proton/electron precision

- Superseded validation: `SFT-PHYS-VALIDATION-PROTON-ELECTRON-003`.
- Measured-value successor: `SFT-PHYS-MATTER-PROTON-ELECTRON-TERMINAL-004`.
- Successor receipt: `sha256:c52208ec2212ffa3fd16e34b90abfdd3adc083411d7a19914d3591b4f8ea9d23`.
- Exact successor enclosure: approximately `1836.1526734253127` to `1836.1526734253130`.
- External CODATA interval: approximately `1836.152673394` to `1836.152673458`.
- Closure use: successor only; the earlier non-overlap cannot establish closure.

### CKM complete vector

- Superseded validation: `SFT-PHYS-VALIDATION-QUARK-CKM-003`.
- Measured-value successor: `SFT-PHYS-MATTER-CKM-TERMINAL-004`.
- Successor receipt: `sha256:745bc9840a7f5396866ff2e581fe700d9f254bff2538ef3c31eb74fc8683513e`.
- External result: all four registered `s12`, `s23`, `s13`, and Jarlskog rows overlap their complete PDG uncertainty intervals; no mismatch is an acceptance condition.
- Closure use: successor only; the earlier `s23`-tension predicate cannot establish closure.

### Terminal electroweak value

- Superseded validation: `SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003`.
- Measured-value successor: `SFT-PHYS-VALIDATION-ELECTROWEAK-MEASURED-VALUE-053`.
- Successor receipt: `sha256:e93f04515944a1951b78463db3083350fbc77e6d8506edbcdc13178cedfbc852`.
- Exact forced value: `1930922298157999/8642477221479757`, approximately `0.22342231847125288`.
- Direct PDG measurement: `0.22342 +/- 0.00009`; the forced value is approximately `0.0258` stated uncertainties from the centre.
- Independent like-typed check: the exact complement lies in the complete compatible-input W/Z squared interval.
- Method correction: the all-input W aggregate contains a source-identified incompatible input and is retained unchanged as a measurement-method record, not admitted as an SFT mismatch.
- Closure use: successor only.

### Common scale and low-transfer electroweak values

- Superseded empirical closure predicate: `SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030`; its formal common-axis derivation and immutable receipt remain dependencies.
- Measured-value successor: `SFT-PHYS-VALIDATION-COMMON-SCALE-MEASURED-VALUE-054`.
- Successor receipt: `sha256:0514d2a2fe7ad505dfd99c494f0c6ac6214169791c09596d4657e32ee1c458d8`.
- Exact terminal result: `1930922298157999/8642477221479757` lies inside the direct on-shell interval `[22333,22351]/100000`.
- Exact support-eight result: `25/106` lies inside the complete cesium APV interval `[2331,2367]/10000`.
- Method correction: the NuTeV DIS extraction is preserved unchanged with the source's stated interpretation concerns, but its displacement is neither an SFT result nor an acceptance condition.
- Closure use: successor 054 supplies empirical closure; Claim 030 continues to supply its independently generated formal common-axis result.

### Cosmic component transport and acceleration

- Superseded empirical closure predicate: `SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032`; its formal transport derivation and immutable receipt remain dependencies.
- Measured-value successor: `SFT-PHYS-VALIDATION-COSMIC-TRANSPORT-MEASURED-VALUE-055`.
- Successor receipt: `sha256:e3e00a1c023f76cd0817c7eaec86c0243ab10d338e552f6bae1f90a94a959380`.
- Complete direct-data result: all 32 cosmic-chronometer rows enter one exact standard-uncertainty-normalized mean-squared residual ledger. Its exact upper enclosure is below the One on the fourth enclosure round, without a selected sigma multiplier.
- Exact measured-value results: `11/5`, `22/5`, `17/32`, and tension-One lie inside the complete registered Planck-budget, acceleration-transition, present-acceleration, and constant-state intervals.
- Method correction: the alternate 2019 acceleration reconstruction and DESI `w0-wa` model-comparison preference remain unchanged as method/model records; neither displacement is an SFT result or acceptance condition.
- Closure use: successor 055 supplies empirical closure; Claim 032 continues to supply its independently generated formal transport law.

### Criticality, universality and turbulence

- Superseded validation: `SFT-PHYS-VALIDATION-CRITICALITY-UNIVERSALITY-TURBULENCE-048`.
- Measured-value successor: `SFT-PHYS-VALIDATION-CRITICALITY-MEASURED-VALUE-056`.
- Successor receipt: `sha256:7e437d81bee9d4c88b304a013c5c980fa9d0390f95acaf30c2dfb45b30a1602a`.
- Class-key correction: each of the five manganites retains its complete observed transition order, long-range interaction classification, Widom relation and beta/gamma/delta vector. All five source-derived keys identify the mean-field class.
- Complete measured-vector result: all fifteen exponent values enter once; the exact mean squared normalized residual is `5286961/10584000`, below the One.
- Independent checks: the complete erbium vector contains the exact critical carriers; the turbulence interval contains `2/3`; and both physical spectral routes exhibit the falling `5/3` plateau.
- Method correction: La02 remains fully visible, but its individual displacement is not rewarded as a result or acceptance condition.
- Closure use: successor 056 only; the earlier La02-nonmatch predicate cannot establish closure.

### Thermal history and physical helium abundance

- Superseded validation: `SFT-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038`; its formal thermal-history dependencies and immutable receipt remain available as provenance, but its mismatch predicate cannot establish empirical closure.
- Formal physical-value successor: `SFT-PHYS-THERMAL-HELIUM-ISOTOPE-TERMINAL-057`.
- Formal successor receipt: `sha256:a3b3a44a0d3add7032680427c3b2b504147c0eb824d05fa5d044cef454c5ebc4`.
- Measured-value successor: `SFT-PHYS-VALIDATION-THERMAL-HISTORY-MEASURED-VALUE-058`.
- Measured-value successor receipt: `sha256:7339aa07e1a9f52e8ef1fede03cbe17d38834362f1c9d63bb00b05deb6d49021`.
- Exact physical helium result: `59/240`, which lies inside the complete registered external interval `[489/2000,2471/10000]` without fitting or uncertainty widening.
- Typed analytic distinction: the earlier `1/4` remains the exact analytic family value; it is not substituted for the separately derived physical isotope share.
- Complete thermal custody: the temperature exponent, freeze-out labels, positive deuterium result, finite recombination record, all eighteen extrema and all seven TT rows remain present in the measured-value execution.
- Method correction: acoustic angular-projection rows remain visible as method records, but their displacement is neither a result nor an acceptance condition.
- Closure use: formal Claim 057 and empirical successor 058 only.

### Light-hadron Regge spectrum

- Superseded empirical predicate: `SFT-PHYS-HADRON-REGGE-TERMINAL-005`; its exact multiplet enumeration and normalized fixed-carrier theorem remain immutable formal dependencies, but its pole-error mismatch predicate cannot establish empirical closure.
- Formal dimensional successor: `SFT-PHYS-HADRON-REGGE-DIMENSIONAL-TERMINAL-059`.
- Formal successor receipt: `sha256:f82510d61a2e1472c8d090f2fd1f63b53491bab9f875ce4ae27b0e0b6b5fc54e`.
- Measured-value successor: `SFT-PHYS-VALIDATION-HADRON-REGGE-MEASURED-VALUE-060`.
- Measured-value successor receipt: `sha256:15c9daaa90d88c5193e5e3af4a5ca64a75c0418ee85797a2b90607c37a21cb06`.
- Exact forced law: the admitted three-motion share supplies base `3/5`; the two Fold tube hands force successor `6/5`; hence `Q(J)=(6J-3)/5` at every positive rank, with no fitted slope or intercept.
- Complete measured-vector result: exact carriers `3/5`, `9/5`, `3`, `21/5` and `27/5` all lie inside the corresponding most-restrictive measured resonance-support intervals. Each interval uses the reported width reduced by its lower uncertainty and inward mass-uncertainty endpoints; no uncertainty or width is widened.
- Method correction: pole-mass standard uncertainty is not the physical support of an unstable resonance. All five masses, mass uncertainties, widths, width uncertainties and listing statuses remain visible, including the `rho5(2350)` summary omission and single-measurement basis.
- Closure use: Claim 005 supplies the multiplet and normalized theorem; formal Claim 059 and empirical successor 060 supply the corrected dimensional measured-value closure.

## Remaining mismatch-admission repairs

None. All eight historically identified mismatch-as-success predicates now have separately enumerated, independently replicated and officially admitted measured-value successors. Historical receipts remain immutable and cannot substitute for the successors listed above.

No historical mismatch is treated as a model result or as evidence of closure.
