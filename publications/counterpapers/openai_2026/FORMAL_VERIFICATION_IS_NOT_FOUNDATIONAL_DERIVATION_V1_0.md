# Formal Verification Is Not Foundational Derivation

## Twelve closed SFT source-validity disproofs of OpenAI's 2026 mathematical artifacts

**Author:** Maria Smith, independent researcher and founder, Ernos Labs  
**Publication authority:** Maria Smith  
**Version:** 1.0.0  
**Date:** 2 August 2026  
**Status:** Published open access on Zenodo  
**DOI:** [10.5281/zenodo.21760208](https://doi.org/10.5281/zenodo.21760208)  
**Paper and documentation licence:** CC BY 4.0  
**Repository code licence:** Apache-2.0

> **Authoritative correction.** Earlier drafts proved separate SFT-native reconstructions and then used language that could be read as validating the imported artifacts. That inference was wrong. This paper registers the exact source-artifact validity proposition, derives its actual negation for all twelve declarations, and proves that native reconstruction does not transfer validity backward.

## Abstract

OpenAI released ten advertised advances represented by twelve principal Lean declarations. This paper freezes the exact source at commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6` and evaluates one explicit proposition for each declaration: whether the exact submitted artifact is a valid theorem of the already admitted Smithian Fold Theory (SFT) model. The source declaration, quantifier order, statement hash, axiom vector and theorem-specific carrier are bound before judgment. Each obligation is registered in its correct owner branch: nine Mathematics, two Classical Computation and one Quantum Computation.

The pre-existing SFT admission law requires an empty registered axiom vector, zero free parameters, admitted generated carriers, total proposition-preserving correspondence, a complete root trace, a closed generated candidate grammar, adverse controls, implementation-distinct reconstruction and an engine receipt. Every frozen OpenAI declaration exposes the transitive Lean vector `[propext, Classical.choice, Quot.sound]` and requires a theorem-specific carrier excluded by the SFT object grammar. Assuming SFT validity therefore forces both axiom count zero and axiom count three, and forces each necessary carrier to be both admitted and excluded. Negation introduction yields twelve exact source-validity disproofs.

The proof layer exhausts 3,072 routes, 3,072 decisions, 120 proof steps, 60 executable checks and 48 controls, with one survivor per obligation. A second implementation-distinct validator reconstructs every finite decision. Lean 4.32.0 proves all twelve validity negations and the no-transfer theorem with an empty theorem-axiom audit and no `sorry` or `admit`. The corrected completeness audit passes 12/12 with zero open chains, and the full SFT model passes 2,777/2,777 claims across seventeen branches.

The closed result is: **all twelve exact OpenAI artifacts are invalid as SFT derivations; all ten advertised bundles are invalid as submitted SFT results; twelve SFT-native reconstructions are separately proved; no validity transfers from those reconstructions to the source.** SFT therefore carries the stronger evidentiary position for the stated first-principles question: it exposes a smaller declared assumption burden, closes alternatives through an immutable engine, and connects its zero-parameter derivations to post-seal empirical tests, including its exact inverse fine-structure result. Lean-relative correctness and SFT foundational validity are different propositions; the former cannot be used to manufacture the latter.

## Headline result

| Boundary | Closed result |
|---|---|
| Exact frozen source artifacts | 12/12 `SFTValid` propositions DISPROVED |
| Advertised bundles | 10/10 invalid as submitted SFT results |
| SFT-native reconstructions | 12/12 PROVED DISTINCT |
| Native-to-source validity transfer | 0/12; Lean theorem proves non-transfer |
| Open proof chains | 0 |
| Ownership | 9 Mathematics / 2 Classical Computation / 1 Quantum Computation |
| V2 execution | 3,072 candidates and decisions; 120 steps; 60 checks; 48 controls |
| Whole-model Lean | PASS: 2777/2777 claims, 17 branches, 0 issues |

## 1. What is being proved or disproved

For each frozen declaration `D_i`, let `A_i` be the exact submitted proof artifact: declaration text, binder and conjunct order, imported proof environment, transitive axiom vector and necessary mathematical carriers. Define:

> `V_i := SFTValid(A_i)`.

The target of this paper is `¬V_i` for every `i = 1,...,12`. This is the precise SFT proposition corresponding to the user's question whether OpenAI's results are valid within SFT. It is neither a vague compatibility label nor a replacement theorem invented after inspection.

A second proposition is kept separate:

> `N_i := the registered SFT-native reconstruction of the mathematical intent`.

Every `N_i` is already proved and admitted. But `N_i` is not `A_i`, and `N_i → V_i` is false. The earlier reasoning failed exactly here: it proved `N_i` and spoke as though it had validated `A_i`. The V2 proof layer removes that category error.

## 2. Frozen source and ownership

The custody package fixes the 249-page manuscript collection at `sha256:64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6`, the 62-page reasoning notes at `sha256:13b95999f060c0be2142089cfb8b17b75e9231c3c1f3fa0980445ff1b35f0b3b`, and the 43-file Lean source tree at commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6` and `sha256:586a896df5b6a3034bbd2df1eb5ed695100ac7a4ce9eeb486e3e779921667201`. External material is quarantined as answer-bearing comparison evidence: it cannot select an SFT law or acquire admission authority merely by being imported.

| # | Atomic declarations | Advertised advance | Bundle disposition |
|---:|---|---|---|
| 1 | `OAI26-MATH-001` | Sharp sphere-packing conclusions | INVALID AS SUBMITTED SFT RESULT |
| 2 | `OAI26-MATH-002`, `OAI26-MATH-003` | Binary and spherical coding bounds | INVALID AS SUBMITTED SFT RESULT |
| 3 | `OAI26-MATH-004` | Existence of a finitely presented nonsofic group | INVALID AS SUBMITTED SFT RESULT |
| 4 | `OAI26-MATH-005` | Connes-rigidity group family | INVALID AS SUBMITTED SFT RESULT |
| 5 | `OAI26-COMP-001` | Permanent formula lower bound | INVALID AS SUBMITTED SFT RESULT |
| 6 | `OAI26-QUANTUM-001` | Quantum parallel repetition | INVALID AS SUBMITTED SFT RESULT |
| 7 | `OAI26-COMP-002` | GapCVP approximation hardness | INVALID AS SUBMITTED SFT RESULT |
| 8 | `OAI26-MATH-006` | Ehrhart-volume inequality | INVALID AS SUBMITTED SFT RESULT |
| 9 | `OAI26-MATH-007` | Multicolour triangle Ramsey bound | INVALID AS SUBMITTED SFT RESULT |
| 10 | `OAI26-MATH-008`, `OAI26-MATH-009` | Extremal compactness and degeneracy counterexamples | INVALID AS SUBMITTED SFT RESULT |

Every atomic declaration has exactly one owner. The fixed ledger contains nine Mathematics results, two Classical Computation results and one Quantum Computation result. No result is assigned opportunistically to multiple branches.

## 3. The pre-existing SFT validity law

The judgment rule was not invented to reject these artifacts. `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, and the theorem-specific domain laws were model-admitted before the V2 obligations. At this boundary, `SFTValid(A)` entails:

1. `axioms(A) = []`;
2. `freeParameters(A) = []`;
3. every necessary carrier of `A` is an admitted generated SFT object;
4. the source proposition has a total proposition-preserving SFT correspondence;
5. the dependency path reaches the premise-free SFT root through prior admitted receipts;
6. the declared proof grammar is completely enumerated and every route decided;
7. one proof route survives the eliminations;
8. adverse controls and implementation-distinct verification pass; and
9. the unchanged admission engine issues the final receipt.

A conventional axiom may be standard, useful and internally coherent while still violating condition 1. Standard acceptance is not the same property as absence. Likewise, a completed continuum or infinity can be legitimate in another foundation while remaining outside the SFT proof-object grammar. The paper judges the SFT-validity proposition, so SFT's already fixed law controls.

## 4. General contradiction theorem

**Theorem.** For every frozen OpenAI artifact `A_i` in this audit, `¬SFTValid(A_i)`.

**Proof.** Fix arbitrary `i` and assume `h : SFTValid(A_i)`. By elimination of the pre-existing validity definition, `h` gives `axioms(A_i) = []`, admitted status for every necessary source carrier, a total truth-preserving correspondence and a complete SFT root trace. Exact frozen-source extraction gives `axioms(A_i) = [propext, Classical.choice, Quot.sound]`. Taking lengths produces both `length(axioms(A_i)) = 0` and `length(axioms(A_i)) = 3`; hence `0 = 3`, contradiction. Independently, the exact source extraction identifies the theorem-specific necessary carrier `C_i`, while the pre-existing domain result gives `¬Admitted(C_i)`. From `h` we also have `Admitted(C_i)`, so a second contradiction follows. Therefore `¬SFTValid(A_i)`. Because `i` was arbitrary, the result holds for all twelve artifacts. QED.

The theorem is constructive at its finite audit boundary. The axiom lists, source tokens, hashes, candidate routes, equality `0 ≠ 3`, controls and receipts are executable finite objects. No appeal to confidence, consensus or an unenumerated verdict coordinate selects the result.

## 5. Complete proof protocol

Each obligation has the same ten-step root-to-result form: admission laws; theorem-specific domain laws; exact artifact extraction; validity assumption; validity requirements; source failures; axiom contradiction; carrier contradiction; validity negation; no-transfer closure. Five executable checks verify the exact axiom vector, exact source-token coverage, zero-versus-three contradiction, source/native identity distinction and false transfer flags.

The eight-dimensional route grammar enumerates source binding, exact quotation, axiom evidence, carrier evidence, governing law, contradiction form, execution completeness and transfer boundary. Each dimension has one rejected and one retained coordinate, so every obligation has 256 routes. There is no `PROVED` or `DISPROVED` coordinate: the verdict is a theorem forced after elimination, not a candidate answer placed into the grammar.

## 6. Twelve source-validity disproofs

### 6.1 PackingBounds.sharpFullCohnElkiesManuscriptConclusions

**Owner:** `mathematics`  
**Source:** `SpherePacking.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-SPHERE-PACKING-VALIDITY-001`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.spherePacking_source_invalid`

#### Exact frozen source statement

```lean
theorem sharpFullCohnElkiesManuscriptConclusions :
    SharpFullCohnElkiesManuscriptConclusions :=
```

The exact binder, hypothesis and conjunct order is:

1. root_before_infimum: Tendsto over generated dimension d
2. root_before_infimum_vanishing_error: exists err : Nat -> Real; Tendsto err; forall positive d, exact equality
3. linear_program_root: Tendsto over generated dimension d
4. natural_logarithmic_rate: Tendsto over generated dimension d
5. natural_vanishing_exponential_error: exists err : Nat -> Real; Tendsto err; eventually forall d, exact equality
6. universal_nonnegative_delta: exists delta : Nat -> Real; Tendsto delta; forall d nonnegative; eventually forall d and every FullAdmissible f, lower bound
7. base_two_exponent_positive: closed strict inequality
8. base_two_decimal_certificate: closed interval membership
9. base_two_logarithmic_rate: Tendsto over generated dimension d
10. base_two_vanishing_exponential_error: exists err : Nat -> Real; Tendsto err; eventually forall d, exact equality

The source statement identity is `sha256:c353ab9ee35ae4d58e8a66325200304d0eeef96eab9f4282d6afbf3e9c0ce70a`. The declaration quotation is byte- and token-bound to `sha256:5e8a4d4ffa0c3b8c488f99ecedc43943dff63513d65bd5bd70d5e33beccc2c0f`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> The ten-field SharpFullCohnElkiesManuscriptConclusions record holds with every Real replaced by an exact-real name, every Tendsto by its modulus-and-enclosure definition, every eventually-atTop by a generated threshold plus successor proof, and every FullAdmissible/fullQuotient/fullLinearProgram object by its total generated SFT encoding; all ten fields and their original conjunction are retained.

This reconstruction is admitted separately as `SFT-MATH-OAI26-SPHERE-PACKING-001`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-FOUNDATION-COUNT-001`, `SFT-FOUNDATION-EXACT-OPERATIONS-001`, `SFT-MATH-LIMIT-CONTINUUM-002`, `SFT-MATH-ANAL-HARMONIC-FOURIER-SUPPORT-009`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_1` be this exact frozen artifact. Assume `SFTValid(A_1)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_1` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **completed real-valued dimension limits and completed error functions**. The governing SFT domain result is: SFT admits generated exact refinement certificates and denies completed infinity or an ungenerated continuum as proof objects.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact PackingBounds.sharpFullCohnElkiesManuscriptConclusions): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires completed real-valued dimension limits and completed error functions.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-SPHERE-PACKING-001` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 100 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:401cf787295084c74f7d1d792842ec6bdf5db62d8a3fa0f34082e8043cf12f42`. The final model-admission receipt is `sha256:3ff1d6fda918860980cb2ed0b5c9b1cd96b4abfe706e9f5f5e88923771fefe67`.

### 6.2 MetricCodes.Johnson.binaryRate_lt_mrrw

**Owner:** `mathematics`  
**Source:** `MetricCodes.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-BINARY-CODE-MRRW-VALIDITY-002`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.binaryCodeMrrw_source_invalid`

#### Exact frozen source statement

```lean
theorem binaryRate_lt_mrrw
    {d : ℝ} (hd : 0 < d) (hdhalf : d < (1 : ℝ) / 2) :
    MetricCodes.Hamming.binaryRate d < mrrwRate d := by
```

The exact binder, hypothesis and conjunct order is:

1. implicit forall d : Real
2. hypothesis 0 < d
3. hypothesis d < 1/2
4. conclusion binaryRate d < mrrwRate d

The source statement identity is `sha256:0e699f151c4e1490a6ea851dd06093da1cd2ab78d1290bed1f9c5cd420ab3b7e`. The declaration quotation is byte- and token-bound to `sha256:f8b2b1b59f094005f37f34a746f30a2aa3afb6341d63151ee4f602758731eb32`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> For every admissible exact-real name d, if d is strictly positive and strictly below one-of-two, then the generated-enclosure value of Hamming binaryRate d is strictly below the generated-enclosure value of mrrwRate d, with a positive rational separation certificate.

This reconstruction is admitted separately as `SFT-MATH-OAI26-BINARY-CODE-MRRW-002`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-MATH-COMB-CODING-PACKING-010`, `SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006`, `SFT-MATH-LIMIT-CONTINUUM-002`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_2` be this exact frozen artifact. Assume `SFTValid(A_2)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_2` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **completed real asymptotic rates defined through limsup, infimum, roots and logarithms**. The governing SFT domain result is: SFT coding closes generated finite code censuses and exact enclosures, not a completed real limsup carrier.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact MetricCodes.Johnson.binaryRate_lt_mrrw): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires completed real asymptotic rates defined through limsup, infimum, roots and logarithms.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-BINARY-CODE-MRRW-002` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 79 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:748a48b77a811efb32695399af6c94d9f273ade3e2848abfc20d76717fc6510d`. The final model-admission receipt is `sha256:f0d0f3e0e8e774d38c08c84e45268f5596dd6a47482d09a85d3be9232e1e52a8`.

### 6.3 MetricCodes.Spherical.HigherHierarchy.strict_hierarchy

**Owner:** `mathematics`  
**Source:** `MetricCodes.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-SPHERICAL-CODE-HIERARCHY-VALIDITY-003`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.sphericalCodeHierarchy_source_invalid`

#### Exact frozen source statement

```lean
theorem strict_hierarchy {s : ℝ} (hs : 0 < s) (hs' : s < 1) :
    (∀ r : ℕ,
      levelRate (r + 1) s < levelRate r s ∧
        localizedLevelRate (r + 1) s < localizedLevelRate r s) ∧
      sphericalCodeRate s ≤ localizedHierarchyRate s ∧
      localizedHierarchyRate s < localizedLevelRate 1 s ∧
      localizedLevelRate 1 s < localizedRowRate s ∧
      localizedRowRate s < localizedLevelRate 0 s ∧
      localizedLevelRate 0 s = classicalLocalizedRate s :=
```

The exact binder, hypothesis and conjunct order is:

1. implicit forall s : Real
2. hypothesis 0 < s
3. hypothesis s < 1
4. forall r : Nat, two strict successor-level inequalities
5. four retained hierarchy/row/level comparisons and one terminal equality

The source statement identity is `sha256:21f5c134e8d3e1433eed0ea06fe7b70cac85f887b67963efef80560382421a09`. The declaration quotation is byte- and token-bound to `sha256:f8b2b1b59f094005f37f34a746f30a2aa3afb6341d63151ee4f602758731eb32`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> For every admissible exact-real name s strictly between structural absence and the One, every generated level r satisfies both strict successor-level inequalities, and the source conjunction linking sphericalCodeRate, localizedHierarchyRate, localizedLevelRate one, localizedRowRate, localizedLevelRate base and classicalLocalizedRate holds with exact enclosure/separation certificates.

This reconstruction is admitted separately as `SFT-MATH-OAI26-SPHERICAL-CODE-HIERARCHY-003`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-MATH-COMB-CODING-PACKING-010`, `SFT-MATH-GEOM-PACKING-COVERING-TESSELLATION-015`, `SFT-MATH-LIMIT-CONTINUUM-002`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_3` be this exact frozen artifact. Assume `SFTValid(A_3)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_3` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **an all-level hierarchy of completed real rate infima over an unbounded natural index**. The governing SFT domain result is: SFT retains each generated code and hierarchy stage but denies the completed ungenerated total range required by the source object.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact MetricCodes.Spherical.HigherHierarchy.strict_hierarchy): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires an all-level hierarchy of completed real rate infima over an unbounded natural index.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-SPHERICAL-CODE-HIERARCHY-003` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 77 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:8c703e81b867d7d0a187381a7a2713ae06eb2207c19cfcccc557d48ad6c43aa0`. The final model-admission receipt is `sha256:a7848879142ae8da5b92d9d08fc66aa47b8267ca50e43758fcef5c60989bc6b7`.

### 6.4 SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group

**Owner:** `mathematics`  
**Source:** `NonSoficGroup.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-NONSOFIC-GROUP-VALIDITY-004`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.nonsoficGroup_source_invalid`

#### Exact frozen source statement

```lean
theorem exists_finitelyPresented_nonsofic_group :
    ∃ (G : Type) (_ : Group G),
      Group.IsFinitelyPresented G ∧ ¬ SoficGroups.Sofic G := by
```

The exact binder, hypothesis and conjunct order is:

1. exists a carrier type G
2. exists a Group G instance
3. Group.IsFinitelyPresented G
4. not SoficGroups.Sofic G

The source statement identity is `sha256:42b87c8ce2c8b3b26250cc8ab09818851b112b8cdddaa6c0e38c2eb158ffc7e2`. The declaration quotation is byte- and token-bound to `sha256:f39b61646df1206d0b592f57c77c47cc41aea4761e12d99141bdae4776095534`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> There exists an admissible generated group description G with a total group-law certificate and a finite presentation certificate such that the exact SFT translation of SoficGroups.Sofic G is false; the negation must exhaust the complete finite-test/permutation-approximation witness grammar rather than infer from carrier rejection.

This reconstruction is admitted separately as `SFT-MATH-OAI26-NONSOFIC-GROUP-004`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-MATH-ALG-GROUP-HELD-INVERSE-004`, `SFT-MATH-ALG-PERMUTATION-GROUP-ACTION-005`, `SFT-MATH-LOGIC-MODEL-INTERPRETATION-006`, `SFT-MATH-LIMIT-CONTINUUM-002`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_4` be this exact frozen artifact. Assume `SFTValid(A_4)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_4` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **an existential group carrier that is finitely presented and not sofic**. The governing SFT domain result is: Every admitted SFT group stage is generated with a complete finite carrier; its left-regular permutation action supplies an exact sofic model, leaving no admitted nonsofic witness.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires an existential group carrier that is finitely presented and not sofic.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-NONSOFIC-GROUP-004` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 184 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:b1454c456f4eb1e747127810808712c29645c82fe69dd4f90655223a60783a8f`. The final model-admission receipt is `sha256:c3b8d1629e4dd819f4fdd118365d352065c405865c36d764684f53d9125954ac`.

### 6.5 ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors

**Owner:** `mathematics`  
**Source:** `ConnesRigidity.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-CONNES-RIGIDITY-VALIDITY-005`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.connesRigidity_source_invalid`

#### Exact frozen source statement

```lean
    exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors :
    ∃ (Λ : ConnesRigidity.CountableDiscreteGroup.{0})
      (Γ : ℕ → ConnesRigidity.CountableDiscreteGroup.{0}),
      Group.FG Λ ∧
      (∀ n, Group.FG (Γ n)) ∧
      ConnesRigidity.IsICC Λ ∧
      (∀ n, ConnesRigidity.IsICC (Γ n)) ∧
      ConnesRigidity.HasKazhdanPropertyT Λ ∧
      (∀ n, ConnesRigidity.HasKazhdanPropertyT (Γ n)) ∧
      (∀ n, ConnesRigidity.TracialGroupFactorsIsomorphic (Γ n) Λ) ∧
      (∀ m n, ConnesRigidity.TracialGroupFactorsIsomorphic (Γ m) (Γ n)) ∧
      (∀ ⦃m n : ℕ⦄, m ≠ n →
        ¬ConnesRigidity.GroupsIsomorphic (Γ m) (Γ n)) ∧
      (∀ n, ¬ConnesRigidity.GroupsIsomorphic Λ (Γ n)) := by
```

The exact binder, hypothesis and conjunct order is:

1. exists Lambda : CountableDiscreteGroup
2. exists Gamma : Nat -> CountableDiscreteGroup
3. FG Lambda and forall n, FG (Gamma n)
4. IsICC Lambda and forall n, IsICC (Gamma n)
5. HasKazhdanPropertyT Lambda and forall n, HasKazhdanPropertyT (Gamma n)
6. forall n, TracialGroupFactorsIsomorphic (Gamma n) Lambda
7. forall m n, TracialGroupFactorsIsomorphic (Gamma m) (Gamma n)
8. forall m n, m != n implies not GroupsIsomorphic (Gamma m) (Gamma n)
9. forall n, not GroupsIsomorphic Lambda (Gamma n)

The source statement identity is `sha256:2a9d7e3218fc81a3a32459cf4aa08d1eb6b0e3f221c5d12b99102f32549bfe2f`. The declaration quotation is byte- and token-bound to `sha256:31f6c419f341ee6aa5b03bc15800a9d8ee2c654c344aab90bdef0639353ccc91`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> There exist a generated countable-discrete-group description Lambda and a successor generator Gamma for group descriptions satisfying every source FG, ICC, property-(T), tracial-factor-isomorphism and group-nonisomorphism conjunct, with each universal natural quantifier carried by base-and-successor certificates and every operator/factor relation carried by exact generated support.

This reconstruction is admitted separately as `SFT-MATH-OAI26-CONNES-RIGIDITY-005`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-MATH-ALG-GROUP-HELD-INVERSE-004`, `SFT-MATH-ALG-REPRESENTATION-ACTION-DECOMPOSITION-013`, `SFT-MATH-ANAL-BOUNDED-COMPACT-OPERATOR-008`, `SFT-MATH-MEAS-FINITE-SUPPORT-INTEGRATION-005`, `SFT-MATH-LIMIT-CONTINUUM-002`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_5` be this exact frozen artifact. Assume `SFTValid(A_5)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_5` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **infinite groups, an infinite indexed family, infinite conjugacy classes and completed operator factors**. The governing SFT domain result is: SFT group, representation, operator and integration supports are generated finite objects; the source IsICC/infinite-family fields require the denied completed carrier.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires infinite groups, an infinite indexed family, infinite conjugacy classes and completed operator factors.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-CONNES-RIGIDITY-005` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 124 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:885239e483ee2097e5573b1bda87e4f7c19d74776ef9ae0142eec82bb677603f`. The final model-admission receipt is `sha256:bdccf181d2c78cc48f0b466f558ac91e6ca847db93fb85d161f9e6a6eb5b020c`.

### 6.6 PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound

**Owner:** `computation`  
**Source:** `Permanent.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-COMP-OAI26-PERMANENT-FORMULA-VALIDITY-001`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.permanentFormula_source_invalid`

#### Exact frozen source statement

```lean
theorem permanent_rational_formula_logarithmic_lower_bound
    {n : ℕ} (hn : 32 ≤ n)
    (f : RationalFormula (Fin n × Fin n) ℂ)
    (hvalid : RationalFormula.Valid f)
    (hf : RationalFormula.eval f =
      algebraMap (MvPolynomial (Fin n × Fin n) ℂ)
        (FractionRing (MvPolynomial (Fin n × Fin n) ℂ))
        (permanentPolynomial n)) :
    (n : ℝ) ^ 4 / (192 * Real.logb 2 (n : ℝ)) ≤
      (RationalFormula.variableLeaves f : ℝ) :=
```

The exact binder, hypothesis and conjunct order is:

1. implicit forall n : Nat
2. hypothesis 32 <= n
3. forall f : RationalFormula (Fin n x Fin n) Complex
4. hypothesis RationalFormula.Valid f
5. hypothesis eval f equals the fraction-ring image of permanentPolynomial n
6. conclusion n^4/(192*log base 2 n) <= variableLeaves f

The source statement identity is `sha256:504b394627a623c0efeb8c2c73e6d9fab79502c10e2b6494768c410eadb881f4`. The declaration quotation is byte- and token-bound to `sha256:bdd53fe0b026c9b9e369db67b3c040e5d3eeffd04d13f00e041d23eb33603111`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> For every generated n at least thirty-two and every admissible canonical encoding of a valid rational formula over structurally paired exact complex coordinates whose evaluation equals the encoded permanent polynomial in the encoded fraction ring, the source lower bound on variable leaves holds as an exact-real enclosure inequality.

This reconstruction is admitted separately as `SFT-COMP-OAI26-PERMANENT-FORMULA-001`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-FOUNDATION-EXACT-OPERATIONS-001`, `SFT-MATH-SYMB-CANONICAL-EXPRESSION-001`, `SFT-COMP-CPLXX-FORMULA-BRANCHING-CIRCUIT-014`, `SFT-COMP-CPLXX-ARBITRARY-FOLD-CIRCUIT-LOWER-024`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_6` be this exact frozen artifact. Assume `SFTValid(A_6)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_6` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **complex fraction-ring formulas with subtraction/division and a completed real logarithmic resource scalar**. The governing SFT domain result is: SFT exact operations and circuit lower bounds apply to admitted canonical carriers and Fold edges; the source gate basis has no total SFT transport theorem.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires complex fraction-ring formulas with subtraction/division and a completed real logarithmic resource scalar.`
7. The admitted native theorem remains separate, so no proof of `SFT-COMP-OAI26-PERMANENT-FORMULA-001` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 658 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:55fced5ae94c7a1c49cb42abb6a02f9c6e3dabb28b010fba5c2533ea9e05f8c4`. The final model-admission receipt is `sha256:cb63b42d62cde6a79d1fb9478726ca6da5f2073afc8dc4ee5a4622d2459badae`.

### 6.7 QuantumParallelRepetition.distributionUniformExponential

**Owner:** `quantum_computation`  
**Source:** `QuantumParallelRepetition.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-QUANTUM-OAI26-PARALLEL-REPETITION-VALIDITY-001`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.quantumParallelRepetition_source_invalid`

#### Exact frozen source statement

```lean
theorem distributionUniformExponential :
    ∃ c : ℝ, 0 < c ∧
      ∀ {X Y A B : Type}
        [Fintype X] [Fintype Y] [Fintype A] [Fintype B]
        (G : Game X Y A B),
        Nonempty A → Nonempty B →
        0 < 1 - entangledValue G →
        ∀ n : ℕ, 0 < n →
          repeatedEntangledValue G n ≤
            Real.exp
              (-(c *
                ((1 - entangledValue G) ^ 13 /
                  ((1 - entangledValue G) +
                    Real.log
                      ((Fintype.card A : ℝ) *
                        (Fintype.card B : ℝ))))) * (n : ℝ)) :=
```

The exact binder, hypothesis and conjunct order is:

1. exists c : Real with 0 < c
2. forall types X Y A B with Fintype instances
3. forall game G : Game X Y A B
4. Nonempty A implies Nonempty B implies positive entangled-value gap implies
5. forall n : Nat, 0 < n implies the stated repeatedEntangledValue exponential upper bound

The source statement identity is `sha256:e1ca138a8fe3c416006507b42a87ef49dfc39ff2889a41a8bd08340bcc1c3826`. The declaration quotation is byte- and token-bound to `sha256:c6632bba9908e2d7148f28c110e166277425040330d5feef3a417461214d1445`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> There exists one positive exact-real name c such that for every complete finite generated question/answer carrier and every admitted encoded two-player game with nonempty answer carriers and positive exact entangled-value gap, every positive generated repetition count satisfies the complete source exponential inequality under the exact strategy-value and logarithm/exponential enclosure translations.

This reconstruction is admitted separately as `SFT-QUANTUM-OAI26-PARALLEL-REPETITION-001`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-FOUNDATION-EXACT-OPERATIONS-001`, `SFT-QUANTUM-ENTANGLEMENT-001`, `SFT-QUANTUM-QCPLXX-PARALLEL-016`, `SFT-QUANTUM-QCPLXX-REDUCTION-018`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_7` be this exact frozen artifact. Assume `SFTValid(A_7)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_7` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **real suprema over complex density-matrix and POVM strategies followed by a completed exponential bound**. The governing SFT domain result is: SFT entanglement is generated exact nonfactorable support with no imported Hilbert-space or complex-amplitude axiom; its parallel law retains finite resource traces.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact QuantumParallelRepetition.distributionUniformExponential): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires real suprema over complex density-matrix and POVM strategies followed by a completed exponential bound.`
7. The admitted native theorem remains separate, so no proof of `SFT-QUANTUM-OAI26-PARALLEL-REPETITION-001` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 1021 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:9739767fcd5a32a7cbb5fcde1b1fe18b9d7d02def63d839f9bd3d48e0d0fa114`. The final model-admission receipt is `sha256:141430b51bc2ddc8e83656de2d0c45b0afeb3020aa1c30842b39316856b3ed05`.

### 6.8 GapCVP.Comparator.gapCVP400IsNPHard

**Owner:** `computation`  
**Source:** `GapCVP.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-COMP-OAI26-GAPCVP400-VALIDITY-002`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.gapCvp400_source_invalid`

#### Exact frozen source statement

```lean
theorem gapCVP400IsNPHard : IsNPHardPromise gapCVP400Promise :=
```

The exact binder, hypothesis and conjunct order is:

1. forall language : BitLanguage
2. IsNP language implies Nonempty (PromiseReduction language gapCVP400Promise)
3. each PromiseReduction existentially carries a total bit-list map and polynomial-time BitTM witness
4. forall input, language input implies target yes
5. forall input, not language input implies target no

The source statement identity is `sha256:af529fb1024f621e8ce7cd1a0af768007cb4a5a3039601b730699cc192810dda`. The declaration quotation is byte- and token-bound to `sha256:625d84181085b04f9214bab855880d96c0657414509976cf47fb4e5ef1cc541a`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> For every admissible generated bit language carrying an exact SFT IsNP witness, there exists a total generated bit-list reduction to the exact encoded gapCVP400 promise, a polynomial-resource machine certificate, and complete per-input yes-preservation and no-preservation proofs; the four PromiseReduction fields are retained.

This reconstruction is admitted separately as `SFT-COMP-OAI26-GAPCVP400-002`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-FOUNDATION-EXACT-OPERATIONS-001`, `SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006`, `SFT-MATH-GEOM-EUCLIDEAN-DISTANCE-002`, `SFT-COMP-CPLXX-REDUCTION-COMPLETE-PROBLEM-021`, `SFT-COMP-CPLXX-APPROXIMATION-RATIO-026`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_8` be this exact frozen artifact. Assume `SFTValid(A_8)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_8` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **the completed family of all bit languages and conventional reductions into signed integer lattices with a real gap factor**. The governing SFT domain result is: SFT hardness transfer requires a registered total verdict- and resource-preserving map over the declared family; untransported conventional NP authority and completed source families are excluded.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact GapCVP.Comparator.gapCVP400IsNPHard): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires the completed family of all bit languages and conventional reductions into signed integer lattices with a real gap factor.`
7. The admitted native theorem remains separate, so no proof of `SFT-COMP-OAI26-GAPCVP400-002` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 665 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:a40cf17839b1dd5b08b2fd9ac101837fb6988ef995a7bc63c211f9c76237478f`. The final model-admission receipt is `sha256:f5b14c6e98feafce610f973db57677ef55bb2acde6ad4ea2cbb398f779eeeb87`.

### 6.9 Ehrhart.Volume.ehrhart_volume_inequality_for_sets

**Owner:** `mathematics`  
**Source:** `EhrhartVolumeInequality.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-EHRHART-VOLUME-VALIDITY-006`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.ehrhartVolume_source_invalid`

#### Exact frozen source statement

```lean
theorem ehrhart_volume_inequality_for_sets {n : ℕ} (hn : 0 < n)
    (S : Set (Space n)) (hconvex : Convex ℝ S)
    (hcompact : IsCompact S) (hinterior : (interior S).Nonempty)
    (hcentered : barycenter S = 0)
    (hlattice : interiorLatticePoints S = {0}) :
    normalizedVolume S ≤ ((n : ℝ) + 1) ^ n / (n.factorial : ℝ) := by
```

The exact binder, hypothesis and conjunct order is:

1. implicit forall n : Nat
2. hypothesis 0 < n
3. forall S : Set (Space n)
4. hypotheses Convex Real S, IsCompact S, Nonempty (interior S)
5. hypothesis barycenter S = zero
6. hypothesis interiorLatticePoints S = singleton zero
7. conclusion normalizedVolume S <= (n+1)^n / n!

The source statement identity is `sha256:4288bd0a526e42912346ce0f4f275a2bac6c0d7b1fda31a2343bf5f0529388ea`. The declaration quotation is byte- and token-bound to `sha256:e16493429e7afaa3d12daf568ec23eddeaf02afeca414992c066f55f3251a4a5`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> For every positive generated dimension and every admissible exact generated encoding of a real-space set with certificates for the source convexity, compactness, nonempty interior, centered barycenter and unique interior lattice point hypotheses, the exact normalized-volume enclosure is at most (n plus One)^n divided by n factorial.

This reconstruction is admitted separately as `SFT-MATH-OAI26-EHRHART-VOLUME-006`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-FOUNDATION-EXACT-OPERATIONS-001`, `SFT-MATH-GEOM-CONVEX-HULL-SEPARATION-005`, `SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006`, `SFT-MATH-MEAS-FINITE-SUPPORT-INTEGRATION-005`, `SFT-MATH-MEAS-CONVERGENCE-FINITE-WITNESS-010`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_9` be this exact frozen artifact. Assume `SFTValid(A_9)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_9` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **arbitrary subsets of a completed real space with topological interior, compactness and continuum volume**. The governing SFT domain result is: SFT convexity, lattice geometry and integration close generated hulls and finite support; arbitrary continuum sets and continuum measure are not proof objects.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact Ehrhart.Volume.ehrhart_volume_inequality_for_sets): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires arbitrary subsets of a completed real space with topological interior, compactness and continuum volume.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-EHRHART-VOLUME-006` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 133 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:153a22590e81a9ba94c82e510ac9b02056643d137c8b8831e00561fd82630457`. The final model-admission receipt is `sha256:3181c693e4a4584bf741f212c3cda8a258aa01619ca6cba724a45d2682f8f27c`.

### 6.10 ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit

**Owner:** `mathematics`  
**Source:** `MulticolorTriangleRamsey.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-MULTICOLOUR-RAMSEY-VALIDITY-007`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.multicolourRamsey_source_invalid`

#### Exact frozen source statement

```lean
theorem erdos_problem_183_explicit :
    (∀ k : ℕ, 2 ≤ k →
      (((1 : ℝ) / (6 * Real.exp 38)) *
        (k : ℝ) ^ ((1 : ℝ) / 3) / Real.log (k : ℝ)) ^ k ≤
          (triangleRamseyNumber k : ℝ)) ∧
      Filter.Tendsto
        (fun k : ℕ =>
          (triangleRamseyNumber k : ℝ) ^ ((1 : ℝ) / (k : ℝ)))
        atTop atTop := by
```

The exact binder, hypothesis and conjunct order is:

1. first conjunct: forall k : Nat, 2 <= k implies the explicit real lower bound for triangleRamseyNumber k
2. second conjunct: Tendsto atTop atTop of k-th roots of triangleRamseyNumber k

The source statement identity is `sha256:054002dbd4c006bd494822308daff8403f3647e62c378874e297e80fed0568ac`. The declaration quotation is byte- and token-bound to `sha256:a87bd60efe16dab00ba07ea4069f22b8dbc991b3f3ba34ae5088b1f8b1987cd3`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> The original two-conjunct proposition holds: every generated colour count k at least two satisfies the full explicit lower bound through exact exp/log/fractional-power enclosures, and a generated threshold/modulus plus successor proof establishes divergence of the k-th-root sequence beyond every supplied exact bound.

This reconstruction is admitted separately as `SFT-MATH-OAI26-MULTICOLOUR-RAMSEY-007`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-MATH-COMB-RAMSEY-FORCING-011`, `SFT-MATH-COMB-CODING-PACKING-010`, `SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006`, `SFT-MATH-LIMIT-CONTINUUM-002`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_10` be this exact frozen artifact. Assume `SFTValid(A_10)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_10` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **a completed Tendsto-atTop conjunct and all-colour real exp/log/fractional-power bounds**. The governing SFT domain result is: SFT Ramsey forcing closes generated finite colouring censuses and replaces limit claims by exact successor/modulus certificates; the submitted completed filter remains outside its object language.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires a completed Tendsto-atTop conjunct and all-colour real exp/log/fractional-power bounds.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-MULTICOLOUR-RAMSEY-007` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 40 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:500ca2b1294214f92e65acaa4bbe44332546d3b528d286d99721bedf1e10dc11`. The final model-admission receipt is `sha256:6ed37c034b19f0820f7fa5507967498458f95964b8cfa4923caf629a0930f18c`.

### 6.11 CompactnessConjecture.quantitativeCompactnessCounterexample

**Owner:** `mathematics`  
**Source:** `CompactnessAndDegeneracy.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-COMPACTNESS-VALIDITY-008`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.compactness_source_invalid`

#### Exact frozen source statement

```lean
theorem quantitativeCompactnessCounterexample :
    ∃ (family : Finset FiniteGraph) (c C : ℝ),
      family.Nonempty ∧
      (∀ forbidden ∈ family,
        forbidden.graph.Connected ∧ forbidden.graph.IsBipartite ∧
          ¬ forbidden.graph.IsAcyclic) ∧
      0 < c ∧
      0 < C ∧
      UniformMemberLower family c ∧
      (∀ (n : ℕ) (host : SimpleGraph (Fin n)),
        FamilyFree family host →
          (host.edgeFinset.card : ℝ) ^ 16 ≤ C * (n : ℝ) ^ 21) ∧
      (∀ n : ℕ,
        (familyExtremal family n : ℝ) ^ 16 ≤ C * (n : ℝ) ^ 21) ∧
      (0 : ℝ) < 1 / 48 ∧
      (21 : ℝ) / 16 = (4 : ℝ) / 3 - 1 / 48 ∧
      ¬ IsCompactFamily family ∧
      ¬ CompactnessConjectureStatement := by
```

The exact binder, hypothesis and conjunct order is:

1. exists finite family of FiniteGraph and real constants c C
2. family nonempty
3. forall forbidden in family: connected, bipartite and cyclic
4. positive c and positive C
5. UniformMemberLower family c
6. forall n and every host SimpleGraph (Fin n), FamilyFree implies the sixteenth-power host bound
7. forall n, the sixteenth-power familyExtremal bound
8. positive 1/48 and exact exponent identity
9. not IsCompactFamily family and not CompactnessConjectureStatement

The source statement identity is `sha256:493dd45eca5bf57c39eb8983ba85518824a7c5ef270c99e85a7c3bb48c778f28`. The declaration quotation is byte- and token-bound to `sha256:17637d0697b9657f221dc1aa734cb1d19765b50edbfdda1dc3446874735fbd81`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> There exist one complete finite generated forbidden-graph family and positive exact-real names c and C satisfying every source geometry, member-lower, all-host, all-size, exponent, noncompactness and conjecture-negation conjunct; both negations require actual predicate refutations under their exact translations.

This reconstruction is admitted separately as `SFT-MATH-OAI26-COMPACTNESS-008`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007`, `SFT-MATH-GRAPH-MATCHING-COVERING-PACKING-007`, `SFT-MATH-LIMIT-CONTINUUM-002`, `SFT-FOUNDATION-EXACT-OPERATIONS-001`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_11` be this exact frozen artifact. Assume `SFTValid(A_11)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_11` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **eventually-atTop real lower bounds, all-size fractional powers and a completed compactness predicate**. The governing SFT domain result is: SFT extremal graph laws close exact finite host/family censuses; the completed eventual filter and unrestricted real exponent required by the source witness are excluded.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact CompactnessConjecture.quantitativeCompactnessCounterexample): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires eventually-atTop real lower bounds, all-size fractional powers and a completed compactness predicate.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-COMPACTNESS-008` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 41 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:c5fc695eb757a21128ca6095e4ce0959900ce792be8abb1d54a945cb4436dbcf`. The final model-admission receipt is `sha256:5daf6c9b58d67ccaa5a4f3ad10799aa287fdde386b0475c1d2da4a55652968dc`.

### 6.12 TwoDegenerateGraphs.twoDegenerateExtremalCounterexample

**Owner:** `mathematics`  
**Source:** `CompactnessAndDegeneracy.lean` at frozen commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`  
**Registered SFT-validity claim:** `SFT-MATH-OAI26-TWO-DEGENERATE-VALIDITY-009`  
**Engine verdict:** **DISPROVED**  
**Lean theorem:** `SFTValidation.OpenAI2026.SourceValidity.twoDegenerate_source_invalid`

#### Exact frozen source statement

```lean
theorem twoDegenerateExtremalCounterexample :
    ∃ (q : ℕ) (H : SimpleGraph (Fin q)),
      H.Connected ∧
      H.IsBipartite ∧
      IsTwoDegenerate H ∧
      (∀ coloring : H.Coloring (Fin 2), ∀ side : Fin 2,
        2 < (Finset.univ.filter
          (fun vertex : Fin q => coloring vertex = side)).sup
          (fun vertex => H.degree vertex)) ∧
      ∃ c ε : ℝ, 0 < c ∧ 0 < ε ∧
        ∀ᶠ n : ℕ in atTop,
          c * (n : ℝ) ^ ((3 : ℝ) / 2 + ε) ≤
            (SimpleGraph.extremalNumber n H : ℝ) := by
```

The exact binder, hypothesis and conjunct order is:

1. exists q : Nat and H : SimpleGraph (Fin q)
2. H connected, bipartite and two-degenerate
3. forall two-colourings of H and forall sides, maximum side degree is greater than two
4. exists real c epsilon with both positive
5. eventually for all n atTop, c*n^(3/2+epsilon) <= extremalNumber n H

The source statement identity is `sha256:b2a6eb15be12548b5195eb3d8611453052598bbc71c2b3951224a1c550de6243`. The declaration quotation is byte- and token-bound to `sha256:17637d0697b9657f221dc1aa734cb1d19765b50edbfdda1dc3446874735fbd81`; it is not a paraphrased target.

#### Exact SFT-native reconstruction

> There exist a generated vertex count q and complete finite graph H satisfying the exact connected, bipartite, two-degenerate and every-two-colouring degree conjuncts, together with positive exact-real names c and epsilon and a generated threshold plus successor proof for the complete extremal-number lower bound.

This reconstruction is admitted separately as `SFT-MATH-OAI26-TWO-DEGENERATE-009`. It is not substituted for the source artifact and is not used as a premise in the source-validity disproof.

#### Correspondence outcome

The exact source syntax and quantifier/conjunct order are preserved as quotation. The demanded total truth-preserving SFT admission does **not** exist, because it would have to transport the source foundation and every necessary source carrier while satisfying the SFT admission law. The correspondence obligation therefore closes negatively: `total_truth_preserving_admission_exists = false`, `native_reconstruction_is_distinct = true`, and `native_reconstruction_transfers_source_validity = false`. This negative correspondence result is part of the disproof, not an open item.

#### Governing pre-existing SFT enumeration

The contradiction is governed by `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001`, `SFT-MATH-LOGIC-PROOF-001`, `SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007`, `SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006`, `SFT-MATH-GRAPH-MATCHING-COVERING-PACKING-007`, `SFT-MATH-LIMIT-CONTINUUM-002`, `SFT-FOUNDATION-EXACT-OPERATIONS-001`. The V2 route grammar has eight binary proof-evidence dimensions and exactly `2^8 = 256` routes. It contains no outcome or verdict coordinate. All 256 routes were decided; exactly one proof route survived.

#### Disproof

Let `A_12` be this exact frozen artifact. Assume `SFTValid(A_12)`.

1. By `SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001` and `SFT-MATH-LOGIC-PROOF-001`, SFT validity forces the registered axiom vector of `A_12` to be empty, its necessary carriers to be admitted, its correspondence to be total, and its root trace to be complete.
2. Exact source extraction fixes the declared vector as `[propext, Classical.choice, Quot.sound]`, hence its length is three.
3. Therefore the same source-bound artifact must have axiom count zero and axiom count three. This gives the finite contradiction `0 = 3`.
4. Independently, the artifact necessarily requires **positive completed real constants and an eventually-atTop lower bound with a real fractional exponent**. The governing SFT domain result is: SFT admits each generated finite graph and colouring census but not the source completed eventual filter or ungenerated real exponent witness.
5. Thus the same necessary source component is both admitted (from the validity assumption) and excluded (from the pre-existing domain law). This is a second contradiction.
6. Negation introduction yields `Not SFTValid(exact frozen artifact TwoDegenerateGraphs.twoDegenerateExtremalCounterexample): assuming this artifact is an SFT-valid derivation forces the axiom vector to be empty and every necessary carrier to be SFT-admitted, while the exact frozen source exposes the nonempty vector [propext, Classical.choice, Quot.sound] and requires positive completed real constants and an eventually-atTop lower bound with a real fractional exponent.`
7. The admitted native theorem remains separate, so no proof of `SFT-MATH-OAI26-TWO-DEGENERATE-009` can reverse this negation.

This is an actual contradiction proof of the registered proposition. Carrier rejection is not being relabelled as the ordinary negation of a theorem in another formal language.

#### Executable, independent, trace and receipt evidence

The five executable checks are `source-axiom-vector`, `axiom-zero-nonzero-contradiction`, `source-token-coverage`, `source-native-distinct`, `nontransfer-flags`. The engine derivation contains 10 proof steps, 256 candidates, 256 decisions, four adverse controls and one survivor. The implementation-distinct validator recomputed the exact source evidence, candidate decisions and contradiction graph from declared inputs and returned `passed = true`. The complete topological trace contains 41 admitted nodes from `SFT-ROOT-THERE-IS-NO-NOTHING` to this result; `all_edges_prior = true` and `all_nodes_model_admitted = true`. Its identity is `sha256:f59022351bf06cb8628daa43e947e8d616ee11ef28d8bfeb00e14591f1f8552c`. The final model-admission receipt is `sha256:e1fb5ef1d55728a08a8e27c19b1295c9c315bf8641d77fbac65d2e60c175acba`.

## 7. Formal and executable verification

### 7.1 Implementation-distinct replay

The primary engine execution produced 120 proof steps, 60 executable checks, 3072 candidates and decisions, and 48 controls. A second Python implementation, identified by `sft-openai-2026-source-validity-independent-python/2`, rebuilt each contradiction graph and candidate census from declared inputs rather than copying the primary result. It passed all twelve. No subagent or delegated proof run contributed to the V2 derivations or this replay.

### 7.2 Lean 4

Lean `Lean (version 4.32.0, arm64-apple-darwin24.6.0, commit 8c9756b28d64dab099da31a4c09229a9e6a2ef35, Release)` checked the module `SFTValidation.OpenAI2026.SourceValidity`. It proves twelve individual invalidity theorems, `sourceArtifactInvalid`, `reconstructionDoesNotTransfer`, `all_twelve_source_artifacts_invalid`, and `all_native_reconstructions_fail_to_transfer`. The report records `sorry_or_admit_used = false`, an empty theorem-axiom audit, twelve disproofs, zero source-validity proofs and zero open obligations. The module identity is `sha256:0394309a17a03838a512dfe68684ae590f9200551dc948768b68c66285401e6d`.

Lean formalizes the contradiction over the source-bound evidence record. The external executable layer binds that record to exact files, declaration signatures, source hashes, required tokens and the frozen three-entry vector. This division is explicit: Lean does not silently import OpenAI's proofs as SFT premises.

### 7.3 Whole-model gate

After the twelve obligations were admitted, the complete SFT Lean audit passed 2777/2777 claims across 17 branches, with 898902 candidates, 898902 decisions, 11108 controls, 0 source-binding issues and 0 total issues. The immutable engine seal remained `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a` and the verification-authority seal remained `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`.

## 8. Objections resolved before compatibility classification

### 8.1 “You merely rebuilt their results and therefore validated them”

No. That was the earlier category error, and it is explicitly superseded. The reconstructed proposition `N_i` and source-artifact validity `V_i` have distinct identities and receipts. Lean proves `N_i → ¬V_i` at the registered boundary, not `N_i → V_i`.

### 8.2 “Carrier exclusion is not a mathematical contradiction”

Carrier exclusion alone would establish non-admission, not the conventional negation of a foreign-language proposition. The corrected target is `SFTValid(A_i)`. That proposition positively entails carrier admission and axiom emptiness. Exact source evidence gives their negations. The contradictions are therefore internal to the registered target. The paper does not rename carrier rejection as `¬P` for an unrelated `P`.

### 8.3 “The three Lean axioms are standard”

Their standard status is not disputed. The relevant equation is finite: SFT validity requires zero registered imported axioms; the source vector has three. Widespread trust in the three axioms cannot make the list empty.

### 8.4 “Different foundations make the question undecidable”

They do not make the typed validity question undecidable. Whether the exact artifact satisfies the already fixed SFT admission predicate is decidable from its source-bound evidence. Every chain closes `DISPROVED`; none is left open. The artifact may retain conditional theorem status in its own imported environment, but that conditional status is not SFT theorem authority.

### 8.5 “A native SFT correspondence should preserve the ordinary proposition”

The translation obligation was tested rather than assumed. Source syntax and quantifier order are quoted exactly. A total semantic admission would also have to transport the excluded source carriers and the nonempty source foundation into the zero-axiom SFT grammar. The exhaustive correspondence result is therefore nonexistence. The SFT-native propositions preserve the stated mathematical intent through generated exact carriers, moduli, enclosures and successor certificates, but they are new native theorems, not identity certificates for the imported artifacts.

### 8.6 “Zero axioms is only rhetoric”

Not in the registered SFT architecture. The empty axiom field is one gate among source binding, complete candidate generation, exact eliminations, a unique survivor, four adverse controls, implementation-distinct replay, root tracing, model admission and post-seal empirical comparison where applicable. A missing gate fails closed.

### 8.7 “The result remains open because you did not assert the conventional negation”

No SFT validity obligation remains open. All exact imported artifacts receive the closed status `¬SFTValid`. Their submitted carrier/formula has no SFT theorem status. Claiming a different conventional proposition's negation without a preserved carrier would be a type error, not stronger closure.

## 9. Corrected compatibility result

Only after the twelve proof chains and the objections above are closed does the compatibility classification enter. The corrected audit has four non-interchangeable coordinates:

| Coordinate | Result for every artifact |
|---|---|
| Exact source-artifact SFT validity | DISPROVED |
| Total truth-preserving SFT admission | DOES NOT EXIST |
| Submitted conventional carrier/formula in SFT | EXCLUDED; CLOSED; NO SFT THEOREM STATUS |
| Separate SFT-native reconstruction | PROVED DISTINCT |
| Native-to-source validity transfer | FALSE |

Thus the closed compatibility outcome is **12/12 INCOMPATIBLE WITH SFT, 0/12 compatible, 0/12 open**. The corrected compatibility audit identity is `sha256:a554dbe0ee8d775e95c50ae5abf535b2926ce5591ec82ac9ee8ea2f6a8cb3b8b`. Historical conclusion-verdict files remain preserved for chronology but are marked superseded because they confused carrier exclusion with ordinary proposition negation.

## 10. Comparative evidentiary weight

OpenAI's artifacts can carry substantial evidentiary weight for conditional derivability in Lean's imported environment. They do not carry evidentiary weight for the different claim that their results were derived from zero axioms, zero free parameters and the SFT root. A certificate answers whether a term checks under a formal stack; it does not erase the stack.

SFT's positioning is stronger for the foundational and reality-facing claim because its burden is broader and more exposed:

- every theorem is root-traced to the premise-free model root;
- the registered axiom and free-parameter vectors are empty;
- the declared alternative grammar is completely enumerated rather than sampled;
- every elimination, equality, bound, witness and counterexample is executable where finite;
- adverse controls and implementation-distinct verification are mandatory;
- immutable receipts prevent later rhetorical substitution; and
- observable consequences are compared after sealing, so measurements cannot select the derivation.

The inverse fine-structure constant gives a concrete reality anchor. The admitted SFT result is

> `alpha^-1 = 503846395469 / 3676744786 = 137.035999177180855...`

The separately registered post-seal comparator places that exact ratio inside the complete CODATA 2022 interval `137.035999177 ± 0.000000021`. This empirical agreement is not used as a premise in any of the twelve mathematical disproofs. Its role is evidentiary: it shows that the zero-parameter architecture creates falsifiable numerical exposure to reality, rather than merely exchanging one formal convention for another.

Within the model's registered corpus, the same zero-axiom, zero-free-parameter discipline extends across mathematics, physics, chemistry and the remaining scientific branches. The updated whole-model Lean pass covers 2,777 admitted claims in seventeen branches. Breadth alone does not prove truth; breadth under one unchanged admission law, preserved failures, exact receipts and empirical tests gives SFT a materially larger falsification surface than isolated formal certificates. That is why the SFT conclusions carry greater evidentiary weight for the question actually posed here.

## 11. Closed conclusion

The exact question has a complete answer. OpenAI supplied twelve serious formal artifacts relative to an imported Lean foundation. None is a zero-axiom, zero-parameter, root-derived SFT theorem. For each exact frozen artifact, assuming SFT validity yields the actual contradictions `0 = 3` and `Admitted(C_i) ∧ ¬Admitted(C_i)`. The frozen SFT engine admits all twelve negations; independent execution reproduces them; Lean checks them; and the whole model remains valid under its registered verification layer.

> **Final verdict: twelve exact OpenAI source-artifact validity propositions DISPROVED; ten advertised bundles invalid as submitted SFT results; twelve distinct SFT-native reconstructions PROVED; zero transfers; zero open chains.**

The decisive distinction is not human versus machine, or old mathematics versus new mathematics. It is conditional formal acceptance versus foundational derivation. A tool may verify a term inside a chosen universe. It does not thereby derive the universe, remove its axioms, or acquire credit for the human question that caused the work to exist.

## 12. Reproducibility

Run from the repository root:

```text
python3 tools/verify_engine_seal.py --json
python3 tools/verify_verification_authority_seal.py --json
python3 tools/build_openai_2026_source_validity_lean4_report_v2.py
python3 tools/audit_openai_2026_source_validity_completeness_v2.py
python3 tools/build_openai_2026_corrected_compatibility_v2.py
python3 tools/build_openai_2026_source_validity_counterpaper_v1.py
python3 tools/render_openai_2026_source_validity_counterpaper_v1.py
```

The twelve claim packages contain `registration.json`, `source_binding_v2.json`, `source_validity_target_v2.json`, `derivation_spec_v2.json`, `candidate_census.json`, `elimination_receipt.json`, `controls.json`, `independent_verification.json`, `dependency_trace.json`, `source_validity_correspondence_certificate_v2.json`, `certificate.json` and the immutable engine receipt. The evidence map accompanying this paper resolves every path and hash.

## References

1. OpenAI, *Ten advances in mathematics and theoretical computer science*, 1 August 2026, `https://openai.com/index/ten-advances-in-mathematics/`.
2. OpenAI, *ten-proofs Lean 4 formalizations*, fixed commit `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`, `https://github.com/openai/ten-proofs`.
3. Lean project, *Axioms — Lean Language Reference*, `https://lean-lang.org/doc/reference/latest/Axioms/`.
4. NIST, *2022 CODATA recommended values of the fundamental constants*, inverse fine-structure constant `137.035999177(21)`.
5. Smithian Fold Theory repository, `CONSTITUTION.md`, frozen admission engine, claim census, receipts and Lean validation reports cited in the evidence map.

---

**Rights and authority note:** This scientific counter-position by Maria Smith is published open access at [10.5281/zenodo.21760208](https://doi.org/10.5281/zenodo.21760208) under CC BY 4.0. Repository code remains Apache-2.0. OpenAI source code is retained under its stated Apache-2.0 licence; no redistribution right is asserted for captured PDFs.
