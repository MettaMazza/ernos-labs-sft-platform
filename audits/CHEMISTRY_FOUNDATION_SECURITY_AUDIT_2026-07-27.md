# Chemistry foundation security audit

Date: 2026-07-27

Status: `FOUNDATION_CURRENT_EVIDENCE_COMPLETE__FIELD_WIDE_RECONSTRUCTION_ACTIVE__EXTENSION_OPEN`

This audit answers one narrow question: whether the Chemistry foundation meets
the twelve criteria declared in `docs/branch_roadmaps/06-chemistry.md`. It does
not convert the unfinished full-discipline roadmap into a completion claim and
does not permanently lock Chemistry against lawful discoveries, corrections or
stronger evidence.

## Untouched authority

- Canonical admission-engine seal: `sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a`.
- Canonical engine Git tree: `ad30f4866c18b2adbade95a0b2de40d5caa61308`.
- Verified engine runtime files: 16.
- Verification-authority seal: `sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8`.
- Verified protected authority files: 33.
- Both seals passed during this audit. No engine, protected verifier, receipt or
  admitted claim was changed to produce this report or the successor paper.

## Foundation result

The frozen foundational inventory contains 86 of 86 required claims. All 86
have valid `model_admitted` census rows and unchanged-engine receipts. Their
complete evidence surface contains:

- 22,016 generated candidate decisions;
- 86 unique survivors;
- 344 mandatory adverse controls;
- 86 implementation-distinct reconstructions;
- 86 post-seal empirical packages; and
- 86 depth-independent closure certificates.

For reproducible comparison, sort each foundational row as
`claim_id<TAB>receipt_hash`, terminate the joined vector with a newline, and
hash the UTF-8 bytes. The resulting vector identity is
`sha256:5f404a8ef8d64dbebbc2b0950bfeee86885aa46c5401367992f146643ef86f53`.

## Twelve-criterion coverage

| Required foundation criterion | Receipt-backed ownership |
|---|---|
| 1. Entity, species, substance, formula and traceable observation | Eight `measurement_identity` claims, from `SFT-CHEM-MEAS-CHEMICAL-ENTITY-001` through `SFT-CHEM-MEAS-TRACEABILITY-001`. |
| 2. Element, isotope, ion, valence and atomic-weight records | Ten `elements_periodicity` claims, from `SFT-CHEM-ELEM-ELEMENT-001` through `SFT-CHEM-ELEM-PERIODIC-BOUNDARY-001`. |
| 3. Periodic order, recurrence, group, period and observed boundary | The same ten element/periodicity claims plus the three separately identified g-block, Smithium and endpoint prediction claims. |
| 4. Exact retained-identity composition | Seven `composition_stoichiometry` claims, from `SFT-CHEM-STOICH-COMPOSITION-001` through `SFT-CHEM-STOICH-SOLUTION-001`. |
| 5. Stoichiometric conservation, primitive balancing and limiting support | The seven composition/stoichiometry claims include coefficients, conservation, limiting support, yield, mixtures and solutions. |
| 6. Chemical, covalent, ionic and metallic bond support | Twelve `bonding_molecular` claims, from `SFT-CHEM-BOND-CHEMICAL-BOND-001` through `SFT-CHEM-MOL-NETWORK-001`. |
| 7. Bond order, polarity, length and dissociation distinctions | The bonding family retains these distinctions and their exact downstream measurement boundaries. |
| 8. Molecule, geometry, isomerism and intermolecular organization | The molecular half of the twelve bonding/molecular claims plus eight stereochemical, organic, polymer and biomolecular-boundary claims. |
| 9. Reaction identity, mechanism, rate, equilibrium and catalysis | Twelve reaction/kinetics/thermodynamics claims and eight catalysis/network/interface claims. |
| 10. Acid/base, electronegativity, redox and electrochemistry | Ten `acid_base_redox` claims, from `SFT-CHEM-AB-ACID-BASE-001` through `SFT-CHEM-ELECTROCHEM-CELL-001`. |
| 11. Thermochemistry, phase and solution foundations | The reaction/kinetics/thermodynamics and composition/solution families, with exact branch ownership retained. |
| 12. Analytical traceability and exact handoffs | Eight analytical/spectroscopic claims plus the biomolecular and interface boundary claims. |

## Admitted field extension beyond the foundation

Ninety additional Chemistry claims have passed the same untouched engine since
the foundational freeze:

- 16 molecular electronic and quantum-chemical laws;
- 14 quantitative molecular-property laws;
- 19 statistical, thermodynamic, phase and transport laws;
- 13 quantitative kinetics and reaction-dynamics laws;
- 17 inorganic, coordination and organometallic laws; and
- 11 organic structure and mechanism laws through ORG-011.

These extensions add 23,040 candidate decisions, 90 unique survivors, 360
controls and 90 independent reconstructions. Eighty-nine have separate
post-seal empirical packages; the operational classical--quantum correspondence
is registered as independently reconstructed formal correspondence rather than
being awarded an external-comparison package it does not possess. Eighty-five
extension claims are depth-independent and five are finite-complete.

The live Chemistry evidence surface is therefore 176 admitted claims, 45,056
candidate decisions, 176 survivors and 704 controls. This is evidence already
earned, not prose added to make the foundation appear larger.

## Exact boundary and restart

- The foundation is complete to the present published standard and secure for
  use by later dependency-ordered work.
- The full-discipline reconstruction is not complete. The active ledger is 78
  of 175 obligations after the trusted 98-claim checkpoint; 97 remain.
- ORG-001 through ORG-011 are receipt-backed. The next operation is ORG-012,
  the pericyclic-reaction law.
- A frozen earlier 272-row discipline projection is preserved for historical
  verifier reproducibility. It is not silently edited, and its old open count
  is not substituted for the live checkpoint.
- No preparation file, roadmap row, manuscript paragraph or favorable external
  record counts as admission. Only a valid unchanged-engine receipt increases
  the admitted count.
- Current-evidence completion is never a permanent lock. New work remains
  admissible only through a new versioned claim, complete enumeration,
  falsification controls, independent reconstruction, unchanged-engine receipt
  and external comparison wherever observation is possible.

