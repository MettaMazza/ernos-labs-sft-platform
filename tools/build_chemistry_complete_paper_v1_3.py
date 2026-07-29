#!/usr/bin/env python3
"""Build the complete 281-claim Chemistry v1.3 successor manuscript."""
from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from tools.build_chemistry_paper import claim_block  # noqa: E402
from tools.publication_series_voice import OPEN_SCIENCE_REFERENCES, open_science_position  # noqa: E402

PAPER = ROOT / "publications/current/chemistry/FROM_FOLD_TO_CHEMISTRY.md"
CENSUS = ROOT / "census/claims.json"
OBLIGATIONS = ROOT / "census/chemistry_discipline_obligations.json"

FIELD_ORDER = (
    "existing_core__measurement_identity", "existing_core__elements_periodicity", "existing_core__composition_stoichiometry",
    "existing_core__bonding_molecular", "existing_core__acid_base_redox", "existing_core__reaction_kinetics_thermodynamics",
    "existing_core__catalysis_networks_interfaces", "existing_core__stereochemistry_organic_polymer", "existing_core__analytical_spectroscopic",
    "existing_core__gblock_smithium", "molecular_electronic_quantum", "quantitative_molecular_properties",
    "statistical_molecular_thermodynamics_transport", "quantitative_kinetics_reaction_dynamics", "inorganic_coordination_organometallic",
    "organic_structure_mechanisms", "quantitative_electrochemistry", "nuclear_radiochemistry",
    "analytical_spectroscopy_separation", "computational_chemistry_cheminformatics", "quantitative_polymer_chemistry",
    "blind_external_validation", "cross_branch_handoffs",
)
FIELD_TITLES = {
    "existing_core__measurement_identity": "Measurement, identity, nomenclature and traceability",
    "existing_core__elements_periodicity": "Elements, isotopes, ions and periodic structure",
    "existing_core__composition_stoichiometry": "Composition, mixtures, solutions and stoichiometry",
    "existing_core__bonding_molecular": "Bonding and molecular organization",
    "existing_core__acid_base_redox": "Acid-base, electronegativity, redox and electrochemistry foundations",
    "existing_core__reaction_kinetics_thermodynamics": "Reaction, kinetics, equilibrium and thermochemistry foundations",
    "existing_core__catalysis_networks_interfaces": "Catalysis, networks, surfaces and interfaces",
    "existing_core__stereochemistry_organic_polymer": "Stereochemistry, organic and polymer foundations",
    "existing_core__analytical_spectroscopic": "Analytical and spectroscopic foundations",
    "existing_core__gblock_smithium": "g-block, Smithium and the periodic endpoint",
    "molecular_electronic_quantum": "Molecular electronic and quantum-chemical correspondence",
    "quantitative_molecular_properties": "Quantitative molecular structure and properties",
    "statistical_molecular_thermodynamics_transport": "Statistical, thermodynamic, phase and transport chemistry",
    "quantitative_kinetics_reaction_dynamics": "Quantitative kinetics and reaction dynamics",
    "inorganic_coordination_organometallic": "Inorganic, coordination, solid-state and organometallic chemistry",
    "organic_structure_mechanisms": "Organic structure, stereochemistry and reaction mechanisms",
    "quantitative_electrochemistry": "Quantitative electrochemistry",
    "nuclear_radiochemistry": "Nuclear chemistry and radiochemistry",
    "analytical_spectroscopy_separation": "Analytical chemistry, spectroscopy and separation science",
    "computational_chemistry_cheminformatics": "Computational chemistry and cheminformatics",
    "quantitative_polymer_chemistry": "Quantitative polymer chemistry",
    "blind_external_validation": "Complete external-validation vectors and Chemistry Grand Lock",
    "cross_branch_handoffs": "Cross-branch ownership and handoff laws",
}
FIELD_MEANINGS = {
    "existing_core__measurement_identity": "Chemical science begins with retained identity, declared observation class, exact amount carrier, reversible naming, uncertainty and source traceability.",
    "existing_core__elements_periodicity": "Elements, isotopes, ions and periodic recurrence retain exact proton, neutron, electronic and observation boundaries.",
    "existing_core__composition_stoichiometry": "Every constituent remains in a positive exact ledger across mixtures, solutions and complete reaction maps.",
    "existing_core__bonding_molecular": "Bonds and molecules are generated joint-support and recurrence structures with held adjacency and orientation.",
    "existing_core__acid_base_redox": "Transfer sense and charge orientation are held labels; no negative proof magnitude enters the derivation.",
    "existing_core__reaction_kinetics_thermodynamics": "Reaction paths retain source, intermediate, condition, energy, time and terminal identity without importing a fitted law.",
    "existing_core__catalysis_networks_interfaces": "Catalysts, networks and interfaces preserve alternative paths, returned carriers and explicit boundaries.",
    "existing_core__stereochemistry_organic_polymer": "Constitutional, orientation and chain distinctions arise from complete finite equivalence and connected support.",
    "existing_core__analytical_spectroscopic": "Measurement identity, selectivity and spectra remain downstream tests with complete uncertainty and adverse rows.",
    "existing_core__gblock_smithium": "Known periodic support, exact structural extrapolation and standing unobserved prediction are separate evidence classes.",
    "molecular_electronic_quantum": "One exact state carrier supports occupancy, symmetry, transitions, measurement and classical-quantum correspondence.",
    "quantitative_molecular_properties": "Thirteen property families share a single carrier; no property-specific fitted parameter is admitted.",
    "statistical_molecular_thermodynamics_transport": "Finite support, exact ratios and held transfer directions reconstruct thermodynamic and transport relations.",
    "quantitative_kinetics_reaction_dynamics": "Rates, barriers, branches, isotope effects and product states retain complete condition-specific custody.",
    "inorganic_coordination_organometallic": "Coordination, spin, colour, magnetism, metal-carbon support, clusters and defects remain exact typed organizations.",
    "organic_structure_mechanisms": "Conjugation, aromatic recurrence, conformers and every registered reaction family are completely enumerated.",
    "quantitative_electrochemistry": "Half-reactions, cell composition, transport, polarization, interfaces and storage handoff retain one-owner ledgers.",
    "nuclear_radiochemistry": "Nuclear carrier changes and chemical consequences retain activity, branching, separation, isotope and radiation custody.",
    "analytical_spectroscopy_separation": "Accuracy, precision, sensitivity, NMR, emission, diffraction, chromatography and multimodal identity retain all rows.",
    "computational_chemistry_cheminformatics": "Chemical data structures are exact organizations of information with reversible provenance and complete finite enumerations.",
    "quantitative_polymer_chemistry": "Polymer size, dispersity, networks, sequence, architecture, gelation, conformation, phase and degradation are separately forced.",
    "blind_external_validation": "The complete dated evidence surface preserves every receipt, closure class, source, result class and formal boundary without aggregate scoring.",
    "cross_branch_handoffs": "Chemistry exports exact laws through directed dependencies while downstream branches retain their own distinct ownership.",
}


def read(path): return json.loads(path.read_text())


def current_certificate(cid, receipt_hash):
    matches = [p for p in (ROOT / "claims" / cid).glob("certificate*.json") if read(p).get("engine_receipt_hash") == receipt_hash]
    if len(matches) != 1: raise SystemExit(f"current certificate count for {cid}: {len(matches)}")
    return read(matches[0])


def field_partition(rows):
    obligations = read(OBLIGATIONS)["obligations"]
    by_obligation = {row["obligation_id"]: row["field"] for row in obligations}
    by_claim = {cid: row["field"] for row in obligations for cid in row.get("current_claim_ids", ())}
    groups = defaultdict(list)
    for row in rows:
        cid = row["claim_id"]
        field = by_claim.get(cid)
        if not field:
            field = by_obligation.get(current_certificate(cid, row["receipt_hash"]).get("chemistry_obligation"))
        if not field and cid == "SFT-CHEM-ROVIBRONIC-COMPOSITION-001": field = "molecular_electronic_quantum"
        if not field and ("SMITHIUM" in cid): field = "existing_core__gblock_smithium"
        if field not in FIELD_ORDER: raise SystemExit(f"unowned paper claim: {cid} -> {field}")
        groups[field].append(row)
    return groups


def main():
    rows = [row for row in read(CENSUS)["claims"] if row.get("branch") == "chemistry"]
    if len(rows) != 281: raise SystemExit(f"expected 281 Chemistry claims, found {len(rows)}")
    candidate_total = control_total = empirical_total = depth = finite = 0
    for row in rows:
        package = ROOT / "claims" / row["claim_id"]
        candidate_total += len(read(package / "candidate_census.json")["candidates"])
        control_total += len(read(package / "controls.json")["controls"])
        empirical_total += (package / "empirical_validation.json").is_file()
        receipt = read(ROOT / row["receipt_path"])
        depth += receipt["closure_status"] == "depth_independent"
        finite += receipt["closure_status"] == "finite_complete"
    if (candidate_total, control_total, empirical_total, depth, finite) != (71936, 1124, 273, 276, 5):
        raise SystemExit("Chemistry paper totals differ from admitted evidence")
    groups = field_partition(rows)
    if sum(map(len, groups.values())) != 281: raise SystemExit("paper partition incomplete")
    mission = open_science_position("For Chemistry, a periodic-table entry, handbook definition, fitted Hamiltonian or opaque predictor may test or translate a sealed consequence but cannot choose the law. Measured agreement, disagreement, non-observation and standing prediction remain separate evidence classes. No institution, credential or funding body can substitute for the public derivation and evidence chain.")
    sections = [f"""# From Fold to Chemistry

**Chemistry Branch Paper 001, version 1.3.0 — complete-current-standard successor manuscript**

**LOCAL PREPUBLICATION SUCCESSOR. REMOTE PUBLICATION IS NOT AUTHORIZED.** The published version 1.2.0 remains at [DOI 10.5281/zenodo.21627782](https://doi.org/10.5281/zenodo.21627782). This manuscript is the next same-paper version and will not be pushed or deposited without Maria Smith's explicit authorization.

## Abstract

This paper reports the complete current Chemistry reconstruction in the third clean-room build of Smithian Fold Theory. All **272 of 272 registered discipline obligations** are separately receipt-backed and the branch remains open to lawful extension. The complete live Chemistry surface contains **281 admitted claims**, including nine supplemental lineage and Smithium consequence claims; **71,936** completely enumerated candidates; **281** unique survivors; **1,124** mandatory controls; **281** implementation-distinct reconstructions; **273** post-seal empirical packages; and **eight** explicitly formal-only boundaries. Closure is depth-independent for 276 claims and finite-complete for five. Every claim traces through named dependencies to the premise-free root theorem and was accepted by the same sealed fail-closed engine with zero imported axioms and zero free parameters.

The field reconstruction spans chemical identity and measurement; elements and periodicity; composition and stoichiometry; bonding and molecular structure; acid-base, redox and electrochemistry; thermodynamics, kinetics and transport; inorganic, organic, polymer, nuclear, analytical and computational chemistry; complete empirical vectors; and cross-branch ownership. Its headline exact results include orbit capacities `2, 6, 10, 14, 18`; nuclear closures `2, 8, 20, 28, 50, 82, 126, 184`; g-block opening at `Z=121`; Smithium at `Z=126`, `N=184`, `A=310`, `[Og] 8s2 5g6`; and the structural endpoint `Z=137`. These extrapolations are standing predictions, not falsely labelled observations. External records test consequences after sealing; they never choose the grammar or survivor.

## Results first: a complete current Chemistry reconstruction

| Headline | Exact result | Evidence and meaning |
|---|---|---|
| Complete branch | `272/272` registered obligations; `281` admitted claims | Complete to Maria Smith's registered current standard, explicitly open to lawful extension rather than permanently locked. |
| Full machine surface | `71,936` candidates; `281` survivors; `1,124` controls; `281` independent reconstructions | Every registered grammar was exhaustively enumerated and admitted separately through the untouched sealed engine. |
| Empirical surface | `273` post-seal empirical packages; `8` explicit formal-only boundaries | Missing measurements are not invented; favorable, adverse, absent, unavailable and unresolved rows remain distinct. |
| Atomic orbit capacities | `2, 6, 10, 14, 18` | Forced from three-space, boundary rank two, two held Fold labels and exclusion; known periodic organization tests the sealed result. |
| Nuclear closure sequence | `2, 8, 20, 28, 50, 82, 126, 184` | Exact registered correspondence; `126/184` supplies the island-of-stability carrier used by Chemistry. |
| g-block and Smithium | opening `Z=121`; Smithium `Z=126`, `N=184`, `A=310`, `[Og] 8s2 5g6` | Standing unobserved predictions. The known table through 118 is retained separately and cannot masquerade as their observation. |
| Structural endpoint | `Z=137` | Standing prediction from the greatest-whole order below the exact Physics-owned inverse-alpha carrier. |
| Physics-owned prerequisite | `alpha^-1 = 503846395469/3676744786 = 137.035999177180855...` | Derived and measured in Physics; Chemistry consumes the admitted dependency without refitting or relocating it. |
| Molecular property unification | 13 families; 9,025 source rows; 1,104 carriers; 676 overlap carriers; 6,676 overlap rows | One source-bound carrier serves every property family; separate fitted coefficients are a registered falsifier. |
| Entropy correspondence | 13 water rows; phase jump `13637763/125000 J mol^-1 K^-1`; independent ratio `4066845420/37275593` | Exact distinction accounting is primary; the measured vector opens after sealing. |
| Colligative response | 276 records: 144 boiling, 37 freezing, 95 osmotic | Complete solvent/solute custody with orientation held as a label and no fitted derivational constant. |
| Kinetic isotope effects | 90 explicit rate ratios and 3 direct decay effects across 47 pages and 23 worksheets | Normal, inverse, near-equal and adverse rows remain in the same evidence surface. |
| Aromatic recurrence | supports `6, 10, 14`; stability excess `150.39 kJ mol^-1`; uncertainty `6.60`; lower envelope `143.79` | Three outcome-unopened CCCBDB sources, 59 tables and 353 rows test the sealed recurrence law. |
| Quantitative electrochemistry | 13/13 laws | Half-reactions, potentials, work, electrolysis, conductivity, kinetics, polarization, interfaces, corrosion and storage handoff are separately forced. |
| Nuclear and radiochemistry | 12/12 laws | Carrier, transformation, activity, branching, equilibria, isotope effects, tracer custody, separation, yields and radiation networks remain distinct. |
| Analytical science | 22/22 laws | Complete NMR, Raman, fluorescence, phosphorescence, diffraction, separation and multimodal records retain accuracy, uncertainty and adverse evidence. |
| Computational chemistry | 14/14 laws | Exact molecular graphs, isomers, conformers, reactions, atom maps, mechanism proof traces, provenance, symbolic evaluation and classical-quantum correspondence. |
| Polymer chemistry | 13/13 laws | Size, dispersity, growth, composition, architecture, gelation, conformation, phase, degradation and Materials handoff are independently closed. |
| Chemistry empirical Grand Lock | 263 pre-VALID claims: 255 empirical and 8 formal-only; 26,486 evidence lines; 1,177 source occurrences | Every receipt and evidence class remains claim-specific; no aggregate success score hides a failed row. |
| One-owner cross-branch graph | 1,484 frozen claims; 25,013 dependency edges; 18,553 cross-branch uses; all root-traced | Materials, Biology, Medicine, Earth Science and Astronomy consume Chemistry through directed dependencies and do not re-own its laws. |

{mission}

## 1. Authorship, rights and publication boundary

Maria Smith is the author and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Submissions and reproducibility reports: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

Copyright 2026 Maria Smith. The paper and documentation are prepared under CC BY 4.0; code is Apache-2.0. “Ernos Labs” is a separate, revocable standards-conformance designation: reuse is open under the licences, but the designation applies only while the public empirical constitution, adverse evidence, untouched engine, critical review and community standards remain intact.

## 2. Exact scope and meaning of completion

The registered discipline census contains 272 obligations in 23 dependency-ordered fields, all now receipt-backed. Nine additional claims retain the separately returned rovibronic and Smithium consequences, giving 281 live Chemistry claims. “Complete” means complete to this dated, registered current-knowledge and evidence standard. It does not mean immutable, permanently locked, or immune from a valid discovery. A lawful extension adds a versioned claim and successor census through the same engine; it never rewrites an old receipt.

Chemistry owns substances, species, composition, bonds, molecular structures and chemical transformations. Materials owns bulk response; Biology owns living organization and function; Medicine owns intervention and health outcome; Earth and Environmental Science owns system history, transport and planetary context; Astronomy owns source populations and cosmic context. Applications cannot select the laws.

## 3. Constitutional mathematics

Structural absence is represented by `0` but does not denote conventional numerical zero. Scientific proof magnitudes are generated positive whole counts and exact positive rational parts or ratios. Direction, opposition, gain/loss and charge sense are held labels rather than negative magnitudes. Irrational, imaginary, floating, continuum, fitted or learned values are not admitted as Fold-native proof objects. Host counters may enumerate files and rows but cannot carry scientific authority.

Every law has zero imported axioms and zero free parameters. External values may test an already sealed result; they may not choose its form. A failed attempt retires nothing. It earns no completion credit, remains preserved, and is followed by a genuinely distinct lawful route unless a complete structural impossibility proof closes the registered grammar.

## 4. One sealed admission engine

Every claim is registered against the root theorem and already admitted dependencies. The engine requires complete candidate identity and cardinality, one decision per candidate, exactly one survivor, closure, minimality, named-shape uniqueness, four mandatory controls and an implementation-distinct reconstruction. Empirical claims additionally require capability isolation, target absence before the matching prediction seal, custody-checked release, all-row retention and an explicit falsifier. Any violated condition halts. Neither this paper builder nor any branch-specific tool can alter the protected engine or verification authority.

## 5. External evidence and observation

Observation is indispensable empirical science. IUPAC, NIST, IAEA, primary supporting information, complete databases and authoritative branch-specific sources test sealed consequences. Each measurement retains source, unit, condition, uncertainty and result class where supplied. The work does not use “empirical” to mean institutional approval; it means founded on observation or experiment. Blindness applies to target custody before prediction, not to pretending prior observations do not exist.

## 6. Preserved failures and lawful repair

Failed capture routes, incomplete tables, unavailable packages, source defects, adverse measurements and implementation-interface halts remain in the audit record. None was promoted into a model failure or used to manufacture performative balance. The HAND family itself preserved a zero-credit graph halt: the census carries owners but not dependencies, so the corrected route reconstructed all 25,013 edges from authoritative registrations before admission. The successful route did not alter a law, target, engine or verifier.

## 7. How to read the exhaustive ledger

The following 281 claim sections reproduce each statement, root-bound dependencies, generated grammar, complete candidate census, unique survivor, axis eliminations, controls, independent reconstruction, post-seal evidence, exclusions and immutable receipt. The claim packages and receipts remain authoritative; this manuscript is a human-readable projection of them.
"""]
    section = 8
    order = 1
    for field in FIELD_ORDER:
        family = groups[field]
        sections.append(f"\n## {section}. {FIELD_TITLES[field]} — {len(family)} admitted claims\n\n{FIELD_MEANINGS[field]} This entire registered subcategory is included; no proper subset is presented as field completion.\n")
        context = field.removeprefix("existing_core__")
        for row in family:
            sections.append(claim_block(order, row["claim_id"], context))
            order += 1
        section += 1
    sections.append(f"""
## {section}. Integrated empirical synthesis

The complete branch contains 273 empirically compared claims and eight explicitly formal-only boundaries. The frozen VALID vector reopens no law and awards no aggregate score: it verifies that all 263 pre-VALID Chemistry claims retain their own current receipts, controls, closure types and evidence classes. Across that surface it preserves 26,486 evidence lines and 1,177 source-identity occurrences. The final six handoff laws then test seventeen paired empirical records and the complete owner/dependency graph. Every unfavorable, absent, unavailable and unresolved row remains available for criticism without substituting for the separately admitted law.

## {section + 1}. Standing predictions and direct falsifiers

- Direct observation inconsistent with g-block opening at `Z=121` falsifies that registered extrapolation.
- A confirmed element-126 carrier inconsistent with `N=184`, `A=310` or `[Og] 8s2 5g6` falsifies the corresponding Smithium claims.
- A positive measured Smithium lifetime, spectrum, decay or chemistry outside the registered generated consequence classes falsifies the relevant successor claim; present non-observation is retained as non-observation.
- A verified atomic carrier beyond the registered `Z=137` structural endpoint falsifies that exact boundary.
- Any omitted source row, changed source identity, replay mismatch, accepted tampered control, duplicate owner or target access before seal invalidates the affected claim.
- A later lawful discovery is not prohibited by “completion”; it must be added through a new claim, complete grammar and successor evidence vector.

## {section + 2}. Reproducibility and current verification state

The complete HAND family reproduced six of six receipt hashes exactly. The combined VALID/HAND focused suite passed eight tests; lightweight repository validation passed at 1,490 total V3 claims; the engine and verification-authority seals remained valid. The full heavy all-branch command is intentionally reserved for the final global Grand Lock and is not misrepresented as rerun for this paper draft. The release evidence map binds every Chemistry package and current receipt by hash.

## {section + 3}. Conclusion

Chemistry is complete to the registered current standard: 272 of 272 obligations, 281 live admitted claims, 71,936 exhaustively enumerated candidates, 281 unique survivors, 1,124 mandatory controls, 281 independent reconstructions, 273 post-seal empirical packages and eight formal-only boundaries. This is not a consensus summary or an opaque prediction system. It is an open, claim-by-claim chain from the root theorem through exact structure, explicit falsification and observation. Its authority is reproducibility. Its completion remains open to every lawful correction and discovery.

## References and authoritative records

- International Union of Pure and Applied Chemistry, *Compendium of Chemical Terminology (Gold Book)*, https://goldbook.iupac.org/.
- International Union of Pure and Applied Chemistry, *Periodic Table of Elements*, release dated 4 May 2022, https://iupac.org/what-we-do/periodic-table-of-elements/.
- National Institute of Standards and Technology / CODATA, *2022 Recommended Values of the Fundamental Physical Constants*, https://physics.nist.gov/constants.
- International Atomic Energy Agency Nuclear Data Section, INDC(NDS)-0452 Part 1, nuclear shell-structure record.
- Smith, Maria, *There Is No Nothing*, Ernos Labs methods and foundation paper.
- Smith, Maria, *From One to Fold*, Foundation branch paper.
- Smith, Maria, *From Fold to Mathematics*, Mathematics branch paper.
- Smith, Maria, *From Distinction to Information*, Information Science branch paper.
- Smith, Maria, *After Turing: The Fold Machine*, Classical Computation branch paper.
- Smith, Maria, *The Quantum Fold Machine*, Reversible and Quantum Computation branch paper.
- Smith, Maria, *From Fold to Physics*, Physics branch paper.
{OPEN_SCIENCE_REFERENCES}
""")
    if order - 1 != 281: raise SystemExit(f"paper omitted claims: {order - 1}")
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(sections).rstrip() + "\n"
    for dash in ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2212"):
        text = text.replace(dash, "-")
    PAPER.write_text(text)
    print(f"CHEMISTRY_V1_3_PAPER claims=281 candidates={candidate_total} controls={control_total} empirical={empirical_total} path={PAPER.relative_to(ROOT)}")


if __name__ == "__main__": main()
