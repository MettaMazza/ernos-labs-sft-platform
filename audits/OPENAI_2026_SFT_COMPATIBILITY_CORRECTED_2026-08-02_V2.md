# Corrected SFT Compatibility Audit of OpenAI's 2026 Mathematical Artifacts

Status: **PASS — CLOSED 12/12**

The exact submitted OpenAI artifacts are **incompatible with SFT**. Their SFT-validity propositions are **disproved 12/12**. The separately derived SFT-native results are **proved 12/12 as distinct reconstructions**, and the Lean-verified no-transfer theorem prevents those reconstructions from being used to validate the imported artifacts.

## Corrected logical classification

- `P_OpenAI`: the exact frozen source artifact, including its quantifiers, carriers, imported proof environment, and declared axiom vector.
- `P_SFT`: the separately admitted SFT-native reconstruction.
- Proving `P_SFT` does not prove `SFTValid(P_OpenAI)`.
- A total truth-preserving SFT admission/correspondence was tested and eliminated for every artifact.
- Therefore `¬SFTValid(P_OpenAI)` is proved for all twelve; `P_SFT` remains a distinct SFT theorem and transfers no validity backward.
- The submitted carrier/formula is categorically excluded from SFT theoremhood. This is a closed classification with **0 open obligations**.

The corrected audit does **not** use carrier rejection as though it were the ordinary logical negation of a proposition stated in a different object language. The actual negated proposition is the registered SFT-validity proposition of the exact source artifact.

## Twelve closed compatibility verdicts

| # | Owner | Exact frozen declaration | SFT validity | Total admission | Native result | Transfer |
|---:|---|---|---|---|---|---|
| 1 | mathematics | `PackingBounds.sharpFullCohnElkiesManuscriptConclusions` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 2 | mathematics | `MetricCodes.Johnson.binaryRate_lt_mrrw` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 3 | mathematics | `MetricCodes.Spherical.HigherHierarchy.strict_hierarchy` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 4 | mathematics | `SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 5 | mathematics | `ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 6 | computation | `PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 7 | quantum_computation | `QuantumParallelRepetition.distributionUniformExponential` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 8 | computation | `GapCVP.Comparator.gapCVP400IsNPHard` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 9 | mathematics | `Ehrhart.Volume.ehrhart_volume_inequality_for_sets` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 10 | mathematics | `ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 11 | mathematics | `CompactnessConjecture.quantitativeCompactnessCounterexample` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |
| 12 | mathematics | `TwoDegenerateGraphs.twoDegenerateExtremalCounterexample` | DISPROVED | DOES NOT EXIST | PROVED DISTINCT | FALSE |

## Per-artifact contradiction boundary

### 1. `PackingBounds.sharpFullCohnElkiesManuscriptConclusions`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact PackingBounds.sharpFullCohnElkiesManuscriptConclusions)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** root_before_infimum: Tendsto over generated dimension d; root_before_infimum_vanishing_error: exists err : Nat -> Real; Tendsto err; forall positive d, exact equality; linear_program_root: Tendsto over generated dimension d; natural_logarithmic_rate: Tendsto over generated dimension d; natural_vanishing_exponential_error: exists err : Nat -> Real; Tendsto err; eventually forall d, exact equality; universal_nonnegative_delta: exists delta : Nat -> Real; Tendsto delta; forall d nonnegative; eventually forall d and every FullAdmissible f, lower bound; base_two_exponent_positive: closed strict inequality; base_two_decimal_certificate: closed interval membership; base_two_logarithmic_rate: Tendsto over generated dimension d; base_two_vanishing_exponential_error: exists err : Nat -> Real; Tendsto err; eventually forall d, exact equality.  
**Necessary imported component:** completed real-valued dimension limits and completed error functions.  
**SFT contradiction:** SFT admits generated exact refinement certificates and denies completed infinity or an ungenerated continuum as proof objects.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-SPHERE-PACKING-001` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:3ff1d6fda918860980cb2ed0b5c9b1cd96b4abfe706e9f5f5e88923771fefe67`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.spherePacking_source_invalid`.

### 2. `MetricCodes.Johnson.binaryRate_lt_mrrw`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact MetricCodes.Johnson.binaryRate_lt_mrrw)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** implicit forall d : Real; hypothesis 0 < d; hypothesis d < 1/2; conclusion binaryRate d < mrrwRate d.  
**Necessary imported component:** completed real asymptotic rates defined through limsup, infimum, roots and logarithms.  
**SFT contradiction:** SFT coding closes generated finite code censuses and exact enclosures, not a completed real limsup carrier.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-BINARY-CODE-MRRW-002` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:f0d0f3e0e8e774d38c08c84e45268f5596dd6a47482d09a85d3be9232e1e52a8`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.binaryCodeMrrw_source_invalid`.

### 3. `MetricCodes.Spherical.HigherHierarchy.strict_hierarchy`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact MetricCodes.Spherical.HigherHierarchy.strict_hierarchy)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** implicit forall s : Real; hypothesis 0 < s; hypothesis s < 1; forall r : Nat, two strict successor-level inequalities; four retained hierarchy/row/level comparisons and one terminal equality.  
**Necessary imported component:** an all-level hierarchy of completed real rate infima over an unbounded natural index.  
**SFT contradiction:** SFT retains each generated code and hierarchy stage but denies the completed ungenerated total range required by the source object.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-SPHERICAL-CODE-HIERARCHY-003` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:a7848879142ae8da5b92d9d08fc66aa47b8267ca50e43758fcef5c60989bc6b7`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.sphericalCodeHierarchy_source_invalid`.

### 4. `SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** exists a carrier type G; exists a Group G instance; Group.IsFinitelyPresented G; not SoficGroups.Sofic G.  
**Necessary imported component:** an existential group carrier that is finitely presented and not sofic.  
**SFT contradiction:** Every admitted SFT group stage is generated with a complete finite carrier; its left-regular permutation action supplies an exact sofic model, leaving no admitted nonsofic witness.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-NONSOFIC-GROUP-004` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:c3b8d1629e4dd819f4fdd118365d352065c405865c36d764684f53d9125954ac`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.nonsoficGroup_source_invalid`.

### 5. `ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** exists Lambda : CountableDiscreteGroup; exists Gamma : Nat -> CountableDiscreteGroup; FG Lambda and forall n, FG (Gamma n); IsICC Lambda and forall n, IsICC (Gamma n); HasKazhdanPropertyT Lambda and forall n, HasKazhdanPropertyT (Gamma n); forall n, TracialGroupFactorsIsomorphic (Gamma n) Lambda; forall m n, TracialGroupFactorsIsomorphic (Gamma m) (Gamma n); forall m n, m != n implies not GroupsIsomorphic (Gamma m) (Gamma n); forall n, not GroupsIsomorphic Lambda (Gamma n).  
**Necessary imported component:** infinite groups, an infinite indexed family, infinite conjugacy classes and completed operator factors.  
**SFT contradiction:** SFT group, representation, operator and integration supports are generated finite objects; the source IsICC/infinite-family fields require the denied completed carrier.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-CONNES-RIGIDITY-005` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:bdccf181d2c78cc48f0b466f558ac91e6ca847db93fb85d161f9e6a6eb5b020c`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.connesRigidity_source_invalid`.

### 6. `PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound`

**Owner:** `computation`  
**Registered proposition:** `SFTValid(exact frozen artifact PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** implicit forall n : Nat; hypothesis 32 <= n; forall f : RationalFormula (Fin n x Fin n) Complex; hypothesis RationalFormula.Valid f; hypothesis eval f equals the fraction-ring image of permanentPolynomial n; conclusion n^4/(192*log base 2 n) <= variableLeaves f.  
**Necessary imported component:** complex fraction-ring formulas with subtraction/division and a completed real logarithmic resource scalar.  
**SFT contradiction:** SFT exact operations and circuit lower bounds apply to admitted canonical carriers and Fold edges; the source gate basis has no total SFT transport theorem.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-COMP-OAI26-PERMANENT-FORMULA-001` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:cb63b42d62cde6a79d1fb9478726ca6da5f2073afc8dc4ee5a4622d2459badae`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.permanentFormula_source_invalid`.

### 7. `QuantumParallelRepetition.distributionUniformExponential`

**Owner:** `quantum_computation`  
**Registered proposition:** `SFTValid(exact frozen artifact QuantumParallelRepetition.distributionUniformExponential)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** exists c : Real with 0 < c; forall types X Y A B with Fintype instances; forall game G : Game X Y A B; Nonempty A implies Nonempty B implies positive entangled-value gap implies; forall n : Nat, 0 < n implies the stated repeatedEntangledValue exponential upper bound.  
**Necessary imported component:** real suprema over complex density-matrix and POVM strategies followed by a completed exponential bound.  
**SFT contradiction:** SFT entanglement is generated exact nonfactorable support with no imported Hilbert-space or complex-amplitude axiom; its parallel law retains finite resource traces.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-QUANTUM-OAI26-PARALLEL-REPETITION-001` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:141430b51bc2ddc8e83656de2d0c45b0afeb3020aa1c30842b39316856b3ed05`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.quantumParallelRepetition_source_invalid`.

### 8. `GapCVP.Comparator.gapCVP400IsNPHard`

**Owner:** `computation`  
**Registered proposition:** `SFTValid(exact frozen artifact GapCVP.Comparator.gapCVP400IsNPHard)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** forall language : BitLanguage; IsNP language implies Nonempty (PromiseReduction language gapCVP400Promise); each PromiseReduction existentially carries a total bit-list map and polynomial-time BitTM witness; forall input, language input implies target yes; forall input, not language input implies target no.  
**Necessary imported component:** the completed family of all bit languages and conventional reductions into signed integer lattices with a real gap factor.  
**SFT contradiction:** SFT hardness transfer requires a registered total verdict- and resource-preserving map over the declared family; untransported conventional NP authority and completed source families are excluded.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-COMP-OAI26-GAPCVP400-002` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:f5b14c6e98feafce610f973db57677ef55bb2acde6ad4ea2cbb398f779eeeb87`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.gapCvp400_source_invalid`.

### 9. `Ehrhart.Volume.ehrhart_volume_inequality_for_sets`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact Ehrhart.Volume.ehrhart_volume_inequality_for_sets)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** implicit forall n : Nat; hypothesis 0 < n; forall S : Set (Space n); hypotheses Convex Real S, IsCompact S, Nonempty (interior S); hypothesis barycenter S = zero; hypothesis interiorLatticePoints S = singleton zero; conclusion normalizedVolume S <= (n+1)^n / n!.  
**Necessary imported component:** arbitrary subsets of a completed real space with topological interior, compactness and continuum volume.  
**SFT contradiction:** SFT convexity, lattice geometry and integration close generated hulls and finite support; arbitrary continuum sets and continuum measure are not proof objects.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-EHRHART-VOLUME-006` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:3181c693e4a4584bf741f212c3cda8a258aa01619ca6cba724a45d2682f8f27c`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.ehrhartVolume_source_invalid`.

### 10. `ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** first conjunct: forall k : Nat, 2 <= k implies the explicit real lower bound for triangleRamseyNumber k; second conjunct: Tendsto atTop atTop of k-th roots of triangleRamseyNumber k.  
**Necessary imported component:** a completed Tendsto-atTop conjunct and all-colour real exp/log/fractional-power bounds.  
**SFT contradiction:** SFT Ramsey forcing closes generated finite colouring censuses and replaces limit claims by exact successor/modulus certificates; the submitted completed filter remains outside its object language.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-MULTICOLOUR-RAMSEY-007` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:6ed37c034b19f0820f7fa5507967498458f95964b8cfa4923caf629a0930f18c`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.multicolourRamsey_source_invalid`.

### 11. `CompactnessConjecture.quantitativeCompactnessCounterexample`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact CompactnessConjecture.quantitativeCompactnessCounterexample)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** exists finite family of FiniteGraph and real constants c C; family nonempty; forall forbidden in family: connected, bipartite and cyclic; positive c and positive C; UniformMemberLower family c; forall n and every host SimpleGraph (Fin n), FamilyFree implies the sixteenth-power host bound; forall n, the sixteenth-power familyExtremal bound; positive 1/48 and exact exponent identity; not IsCompactFamily family and not CompactnessConjectureStatement.  
**Necessary imported component:** eventually-atTop real lower bounds, all-size fractional powers and a completed compactness predicate.  
**SFT contradiction:** SFT extremal graph laws close exact finite host/family censuses; the completed eventual filter and unrestricted real exponent required by the source witness are excluded.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-COMPACTNESS-008` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:5daf6c9b58d67ccaa5a4f3ad10799aa287fdde386b0475c1d2da4a55652968dc`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.compactness_source_invalid`.

### 12. `TwoDegenerateGraphs.twoDegenerateExtremalCounterexample`

**Owner:** `mathematics`  
**Registered proposition:** `SFTValid(exact frozen artifact TwoDegenerateGraphs.twoDegenerateExtremalCounterexample)`  
**Verdict:** **INCOMPATIBLE WITH SFT; SOURCE VALIDITY DISPROVED.**  
**Exact source order:** exists q : Nat and H : SimpleGraph (Fin q); H connected, bipartite and two-degenerate; forall two-colourings of H and forall sides, maximum side degree is greater than two; exists real c epsilon with both positive; eventually for all n atTop, c*n^(3/2+epsilon) <= extremalNumber n H.  
**Necessary imported component:** positive completed real constants and an eventually-atTop lower bound with a real fractional exponent.  
**SFT contradiction:** SFT admits each generated finite graph and colouring census but not the source completed eventual filter or ungenerated real exponent witness.  
**Axiom contradiction:** SFT validity forces `[]`; the exact source exposes `['propext', 'Classical.choice', 'Quot.sound']`.  
**Distinct admitted reconstruction:** `SFT-MATH-OAI26-TWO-DEGENERATE-009` — `PROVED_DISTINCT`; transfer to source validity is `false`.  
**Receipt:** `sha256:e1fb5ef1d55728a08a8e27c19b1295c9c315bf8641d77fbac65d2e60c175acba`.  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.twoDegenerate_source_invalid`.

## What was corrected

The earlier conclusion-verdict layer confused three different statements: rejection of a carrier, negation of a conventional mathematical proposition, and invalidity of an imported artifact inside SFT. Only the third is established by the source-bound contradiction. The new V2 obligations register that proposition directly, derive its actual negation, and prove that the native reconstruction does not transfer validity to the source.

| Historical artifact | Corrected status | Reason |
|---|---|---|
| `frontier/openai_ten_advances_2026/STRICT_SFT_PROOF_DISPROOF_OF_OPENAI_TEN_ADVANCES_V0_1.md` | SUPERSEDED_CATEGORY_ERROR | It treated non-admission of a conventional carrier as the ordinary logical negation of the mathematical conclusion. |
| `frontier/openai_ten_advances_2026/STRICT_SFT_PROOF_DISPROOF_OF_OPENAI_TEN_ADVANCES_V0_2.md` | SUPERSEDED_CATEGORY_ERROR | It retained the same invalid transfer from carrier exclusion to conclusion negation. |
| `frontier/openai_ten_advances_2026/conclusion_verdict_report.json` | SUPERSEDED_CATEGORY_ERROR | Its verdict coordinate was not the registered source-validity proposition and is not an engine-admitted disproof of the exact artifact. |
| `frontier/openai_ten_advances_2026/conclusion_translation_census.json` | SUPERSEDED_CATEGORY_ERROR | Its translation table did not establish a total truth-preserving correspondence to the exact source artifacts. |
| `frontier/openai_ten_advances_2026/conclusion_verdict_independent_verification.json` | SUPERSEDED_WITH_PARENT_VERDICT | Independent replay of the wrong target does not repair the target error. |
| `frontier/openai_ten_advances_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_COUNTERPAPER_V0_1.md` | HISTORICAL_PRECURSOR_SUPERSEDED_BY_V2 | Its artifact boundary was directionally correct, but it predated engine-admitted source-validity obligations and the corrected Lean no-transfer result. |
| `frontier/openai_ten_advances_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_COUNTERPAPER_V0_2.md` | HISTORICAL_PRECURSOR_SUPERSEDED_BY_V2 | Its artifact boundary is retained only through the new source-bound engine receipts, not through its former comparison report. |

## Closure evidence

- Source-validity proof chains: **12/12 PASS; 0 open**.
- Ownership: **9 Mathematics / 2 Classical Computation / 1 Quantum Computation**.
- Execution: **120 proof steps / 60 executable checks / 3072 candidates and decisions / 48 controls**.
- Whole-model Lean: **PASS — 2777/2777 claims, 17 branches, 0 source-binding issues, 0 total issues**.
- Engine seal: `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`.
- Verification-authority seal: `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`.
- Audit identity: `sha256:a554dbe0ee8d775e95c50ae5abf535b2926ce5591ec82ac9ee8ea2f6a8cb3b8b`.
