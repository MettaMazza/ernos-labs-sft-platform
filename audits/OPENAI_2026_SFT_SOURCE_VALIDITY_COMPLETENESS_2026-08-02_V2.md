# OpenAI 2026 SFT Source-Validity Completeness Audit V2

Status: **PASS**

This audit corrects the earlier category error. The target is the SFT validity of each exact frozen OpenAI artifact. The separately proved SFT-native reconstruction is not transferred back to that artifact.

- Exact source-artifact validity disproofs: **12/12**
- Native reconstructions retained as distinct SFT results: **12/12**
- Open chains: **0**
- Ownership: **9 Mathematics / 2 Classical Computation / 1 Quantum Computation**
- Proof execution: **120 steps / 60 checks / 3072 candidates / 48 controls**
- Whole-model Lean: **PASS (2777/2777)**

| # | Owner | Frozen declaration | Source validity | Native reconstruction |
|---:|---|---|---|---|
| 1 | mathematics | `PackingBounds.sharpFullCohnElkiesManuscriptConclusions` | DISPROVED | PROVED_DISTINCT |
| 2 | mathematics | `MetricCodes.Johnson.binaryRate_lt_mrrw` | DISPROVED | PROVED_DISTINCT |
| 3 | mathematics | `MetricCodes.Spherical.HigherHierarchy.strict_hierarchy` | DISPROVED | PROVED_DISTINCT |
| 4 | mathematics | `SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group` | DISPROVED | PROVED_DISTINCT |
| 5 | mathematics | `ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors` | DISPROVED | PROVED_DISTINCT |
| 6 | computation | `PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound` | DISPROVED | PROVED_DISTINCT |
| 7 | quantum_computation | `QuantumParallelRepetition.distributionUniformExponential` | DISPROVED | PROVED_DISTINCT |
| 8 | computation | `GapCVP.Comparator.gapCVP400IsNPHard` | DISPROVED | PROVED_DISTINCT |
| 9 | mathematics | `Ehrhart.Volume.ehrhart_volume_inequality_for_sets` | DISPROVED | PROVED_DISTINCT |
| 10 | mathematics | `ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit` | DISPROVED | PROVED_DISTINCT |
| 11 | mathematics | `CompactnessConjecture.quantitativeCompactnessCounterexample` | DISPROVED | PROVED_DISTINCT |
| 12 | mathematics | `TwoDegenerateGraphs.twoDegenerateExtremalCounterexample` | DISPROVED | PROVED_DISTINCT |

## Meaning of the result

For each artifact, assuming SFT validity forces an empty axiom vector and admitted source carriers. The exact frozen source instead exposes `propext`, `Classical.choice`, and `Quot.sound`, plus the theorem-specific carrier conflict. Lean proves the contradiction and the resulting validity negation without user axioms. This does not assert that carrier rejection is the logical negation of the conventional mathematical conclusion; it proves the explicitly registered proposition that the submitted artifact is not an SFT-valid derivation.

Audit identity: `sha256:5571c92ce37746e08258e7e3dba8b3960e14ffddffdda49629171b25e781b1e1`
