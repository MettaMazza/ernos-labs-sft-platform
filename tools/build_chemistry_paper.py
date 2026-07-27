#!/usr/bin/env python3
"""Build the exhaustive Chemistry manuscript from immutable admitted evidence."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.publication_series_voice import OPEN_SCIENCE_REFERENCES, open_science_position  # noqa: E402
INVENTORY = ROOT / "publications/inventories/chemistry.json"
PAPER = ROOT / "publications/current/chemistry/FROM_FOLD_TO_CHEMISTRY.md"
CENSUS = ROOT / "census/claims.json"
METADATA = ROOT / "publication/chemistry_zenodo_metadata.json"

UPSTREAM = (
    "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
    "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",
    "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001",
    "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
    "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",
    "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
    "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001",
)

SUBBRANCH_INTRO = {
    "measurement_identity": "Chemistry begins with exact identity and measurement boundaries: entity, species, substance, amount, formula, nomenclature, uncertainty and traceability.",
    "elements_periodicity": "Element identity is a held proton-count class; isotopes, atomic-weight records, periodic order, recurrence, group, period, valence and ions retain exact provenance and observation boundaries.",
    "composition_stoichiometry": "Composition and stoichiometry preserve every elemental carrier across complete reactant/product maps, primitive positive coefficients, limiting support, yield, mixture and solution organization.",
    "bonding_molecular": "Bonding and molecular structure are exact joint recurrences over held atomic, electron, adjacency and orientation support rather than imported molecular pictures.",
    "acid_base_redox": "Acid/base and redox laws retain transfer orientation as held labels, not negative proof magnitudes, and preserve every donor, acceptor, charge and boundary carrier.",
    "reaction_kinetics_thermodynamics": "Reactions are complete transition maps; mechanisms, intermediates, activation, rate, equilibrium, direction, phase and photochemical response retain source, condition and observation boundaries.",
    "catalysis_networks_interfaces": "Catalysis and interfaces preserve catalyst return, alternative pathways, reaction networks, autocatalysis, adsorption, colloids and cross-boundary transfer without fitted rates.",
    "stereochemistry_organic_polymer": "Stereochemical and polymer distinctions arise from complete finite structure equivalence, held orientation, recurrence and connected composition.",
    "analytical_spectroscopic": "Analytical chemistry keeps sample, calibration, selectivity, spectra, uncertainty, adverse controls and falsification records separate from derivational law.",
    "gblock_smithium": "The final subbranch applies separately admitted exact physical prerequisites to a complete positive-rank fill walk and distinguishes known-domain validation from unobserved prediction.",
    "molecular_electronic_quantum": "The field-wide extension derives molecular electronic identity, state composition, occupancy, ordering, symmetry, correlation, transitions, measurement and operational classical-quantum correspondence from the same exact carrier laws.",
    "quantitative_molecular_properties": "The quantitative property family derives bond length, dissociation, angle, torsion, dipole, polarizability, ionization, affinity, vibration, rotation, binding, magnetic response, formation energy and their common-carrier vector without per-property fitting.",
    "statistical_molecular_thermodynamics_transport": "The thermodynamic extension derives finite microstate support, temperature, energy, heat/work, entropy, enthalpy, free direction, chemical potential, activity, fugacity, phases, colligative response, solvation and coupled transport while keeping external scalar inscriptions downstream.",
    "quantitative_kinetics_reaction_dynamics": "The kinetics extension derives exact rate, concentration and temperature dependence, activation, transition boundaries, competing and composed mechanisms, reversible equilibrium, turnover, diffusion limits, isotope effects and product-state dynamics.",
    "inorganic_coordination_organometallic": "The inorganic extension derives coordination identity and number, denticity, geometry, isomerism, splitting, spin, colour, magnetism, organometallic support, inverse redox transforms, cluster bonding, local solid organization, defects and coupled inorganic reaction networks.",
    "organic_structure_mechanisms": "The organic extension derives conjugation, resonance, aromatic recurrence and its measured stability excess, antiaromatic/nonaromatic distinction, conformer classes and populations, substitution, addition, elimination and composition-retaining rearrangement with complete adverse evidence.",
}

EXTENSION_FAMILIES = (
    ("molecular_electronic_quantum", 16),
    ("quantitative_molecular_properties", 14),
    ("statistical_molecular_thermodynamics_transport", 19),
    ("quantitative_kinetics_reaction_dynamics", 13),
    ("inorganic_coordination_organometallic", 17),
    ("organic_structure_mechanisms", 11),
)

CLAIM_EVIDENCE_HIGHLIGHTS = {
    "SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011": (
        "The eight independently enumerated source/product inventories are "
        "`C8H12O3`, `C9H14O3`, `C12H20O3`, `C15H18O3`, `C9H14O3`, `C11H18O3`, "
        "`C16H20O3` and `C16H26O3`. The printed paired mass inscriptions "
        "`179.06787`, `193.08352`, `235.13047`, `269.1`, `193.08352`, `221.1`, "
        "`283.1` and `289.17742 [M+Na]+` independently cross-check those enumerations "
        "without selecting the rearrangement law."
    ),
}


@lru_cache(maxsize=None)
def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: object) -> str:
    return (
        str(value)
        .replace("\n", " ")
        .replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .strip()
    )


def bullets(values) -> str:
    rows = tuple(values)
    return "\n".join(f"- {clean(value)}" for value in rows) if rows else "- None."


def axis_rows(candidate: dict, elimination: dict) -> str:
    decisions = {row["candidate_id"]: row for row in elimination["decisions"]}
    survivor = next(row for row in elimination["decisions"] if row["survives"])["candidate_id"]
    coordinates = survivor.split("__")
    survivor_candidate = next(row for row in candidate["candidates"] if row["candidate_id"] == survivor)
    names = [part.split("=", 1)[0] for part in survivor_candidate["exact_form"].split("; ")]
    domains = [
        tuple(dict.fromkeys(row["candidate_id"].split("__")[index] for row in candidate["candidates"]))
        for index in range(len(coordinates))
    ]
    output = ["| Axis | Forced form | Eliminated alternatives | Exact rejection basis |", "|---|---|---|---|"]
    for index, (name, chosen) in enumerate(zip(names, coordinates)):
        rejected = [value for value in domains[index] if value != chosen]
        reasons = []
        for value in rejected:
            changed = list(coordinates)
            changed[index] = value
            reasons.append(clean(decisions["__".join(changed)]["reason"]))
        output.append(
            f"| `{name}` | `{chosen}` | {', '.join(f'`{value}`' for value in rejected)} | {'; '.join(dict.fromkeys(reasons))} |"
        )
    return "\n".join(output)


@lru_cache(maxsize=1)
def experiment_index() -> dict[str, tuple[tuple[str, ...], tuple[str, ...]]]:
    rows: dict[str, list[dict]] = {}
    for branch in ("chemistry", "physics"):
        for path in (ROOT / "experiments" / branch).glob("*/registration.json"):
            payload = read(path)
            claim_id = payload.get("claim_id")
            if claim_id:
                rows.setdefault(claim_id, []).append(payload)
    result = {}
    for claim_id, registrations in rows.items():
        sources, targets = [], []
        for row in registrations:
            for source in row.get("external_measurement_sources", []):
                sources.append(f"{source.get('measurement_body', source.get('source_id'))}: {source.get('source_uri', '')} ({source.get('snapshot_hash', '')})")
            for target in row.get("withheld_targets", []):
                targets.append(f"{target.get('target_id')} from {target.get('source_id')}")
        result[claim_id] = (tuple(dict.fromkeys(sources)), tuple(dict.fromkeys(targets)))
    return result


def experiment_details(claim_id: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return experiment_index().get(claim_id, ((), ()))


def claim_block(order: int, claim_id: str, context: str, level: int = 3) -> str:
    root = ROOT / "claims" / claim_id
    registration = read(root / "registration.json")
    candidate = read(root / "candidate_census.json")
    decision_paths = tuple(
        path for path in root.glob("*receipt.json")
        if path.name not in {"empirical_validation.json"}
        and "decisions" in read(path)
    )
    if len(decision_paths) != 1:
        raise SystemExit(f"{claim_id} requires exactly one decision receipt; found {[path.name for path in decision_paths]}")
    elimination = read(decision_paths[0])
    controls = read(root / "controls.json")["controls"]
    certificate = read(root / "certificate.json")
    empirical = read(root / "empirical_validation.json") if (root / "empirical_validation.json").exists() else None
    census_row = next(row for row in read(CENSUS)["claims"] if row["claim_id"] == claim_id)
    survivor = next(row for row in elimination["decisions"] if row["survives"])
    sources, targets = experiment_details(claim_id)
    empirical_text = (
        "This is a sealed formal law with an implementation-distinct reconstruction and no separate external-observation "
        "package at this boundary. It receives no empirical-comparison credit that is not present in its claim package."
    )
    if empirical:
        empirical_text = f"""Target content was opened only after the matching prediction seal: `{empirical['target_opened_after_seal']}`. All registered rows were preserved: `{empirical['all_rows_preserved']}`. The capability-isolation and custody certificates passed. External source identities:

{bullets(empirical['data_source_ids'])}

Comparison records:

{bullets(empirical['measurements'])}

Falsification boundary: {clean(empirical['falsification_condition'])}

Measurement receipt: `{empirical['measurement_receipt_hash']}`. Isolation certificate: `{empirical['isolation_certificate']['certificate_hash']}`. Custody certificate: `{empirical['target_custody_certificate']['certificate_hash']}`."""
    control_text = "\n".join(
        f"- `{row['kind']}`: passed; expected {clean(row['expected_behavior'])}; observed {clean(row['observed_behavior'])}; receipt `{row['receipt_hash']}`."
        for row in controls
    )
    heading = "#" * level
    status_boundary = ""
    if claim_id.startswith("SFT-CHEM-PRED-"):
        status_boundary = " The official record checks only the known prefix; every coordinate beyond element 118 remains a standing unobserved prediction."
    return f"""{heading} {order}. {registration['title']}

Claim identity: `{claim_id}`

**Question and theorem.** {clean(registration['statement'])}

> {clean(certificate['exact_result'])}

**Rooted dependency chain.** The registration names the single premise-free root theorem and accepts only these already admitted dependencies:

{bullets(f'`{value}`' for value in registration.get('dependencies', []))}

**Generated grammar.** {clean(candidate['generation_rule'])}

Boundary: {clean(candidate['grammar_boundary'])}

The engine regenerated `{candidate['expected_cardinality']}` candidates and `{len(elimination['decisions'])}` one-for-one decisions. Exactly one survived: `{survivor['candidate_id']}`. Closure is `{certificate['closure_scope']}`; minimality and named-shape uniqueness are recorded in the closure certificate.

**Coordinate-by-coordinate uniqueness.** Each row compares the survivor with every otherwise-surviving alternative on that coordinate.

{axis_rows(candidate, elimination)}

**Adverse controls.** All mandatory controls passed:

{control_text}

**Independent reconstruction.** Implementation hash `{certificate['independent_implementation_hash']}`; independent certificate `{certificate['independent_certificate_hash']}`; external-validation hash `{certificate['external_validation_hash']}`. The independent program regenerates the declared product and sole survivor without importing the derivation implementation.

**Post-seal external check.** {empirical_text}

{f"**Exact evidence highlight.** {CLAIM_EVIDENCE_HIGHLIGHTS[claim_id]}" if claim_id in CLAIM_EVIDENCE_HIGHLIGHTS else ""}

Registered source descriptions:

{bullets(sources)}

Registered target identities:

{bullets(targets)}

**Meaning.** {SUBBRANCH_INTRO.get(context, 'This upstream claim supplies an exact prerequisite used by the final Chemistry predictions.')} This particular result is closed only at its exact registered grammar and evidence boundary.{status_boundary}

**Explicit exclusions.**

{bullets(registration.get('excluded_inputs', []))}

**Immutable identities.** Source manifest `{certificate['source_manifest_hash']}`; derivation seal `{certificate['derivation_seal_hash']}`; engine receipt `{census_row['receipt_hash']}` at `{census_row['receipt_path']}`; empirical hash `{certificate.get('empirical_validation_hash')}`; measurement receipt `{certificate.get('measurement_receipt_hash')}`.
"""


def main() -> None:
    inventory = read(INVENTORY)
    metadata = read(METADATA)
    if inventory["admitted_claim_count_at_freeze"] != inventory["required_claim_count"]:
        raise SystemExit("Chemistry inventory is not completely admitted")
    if any(row["status"] != "model_admitted" for row in inventory["obligations"]):
        raise SystemExit("Chemistry inventory contains an unadmitted obligation")
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized and not doi:
        raise SystemExit("Authorized Chemistry publication requires a DOI")
    obligations = inventory["obligations"]
    foundation_ids = {row["claim_id"] for row in obligations}
    census_rows = read(CENSUS)["claims"]
    all_chemistry_rows = [
        row for row in census_rows
        if row.get("branch") == "chemistry" and row.get("model_admitted") is True
    ]
    extension_rows = [row for row in all_chemistry_rows if row["claim_id"] not in foundation_ids]
    if len(obligations) != 86 or len(extension_rows) != sum(count for _, count in EXTENSION_FAMILIES):
        raise SystemExit(
            f"unexpected Chemistry coverage: foundation={len(obligations)}, extension={len(extension_rows)}"
        )
    if len(all_chemistry_rows) != 176:
        raise SystemExit(f"expected 176 live admitted Chemistry claims, found {len(all_chemistry_rows)}")
    boundary = (
        f"**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: [{doi}](https://doi.org/{doi})."
        if authorized
        else (
            "**LOCAL SUCCESSOR MANUSCRIPT; REMOTE PUBLICATION IS NOT AUTHORIZED.** "
            f"The preceding Chemistry paper is preserved at DOI [{doi}](https://doi.org/{doi}). "
            "This version 1.2.0 does not authorize a push, upload, DOI-version action or publication."
        )
    )
    foundation_candidates = sum(
        read(ROOT / "claims" / row["claim_id"] / "candidate_census.json")["expected_cardinality"]
        for row in obligations
    )
    extension_candidates = sum(
        read(ROOT / "claims" / row["claim_id"] / "candidate_census.json")["expected_cardinality"]
        for row in extension_rows
    )
    live_candidates = foundation_candidates + extension_candidates
    foundation_controls = sum(
        len(read(ROOT / "claims" / row["claim_id"] / "controls.json")["controls"])
        for row in obligations
    )
    extension_controls = sum(
        len(read(ROOT / "claims" / row["claim_id"] / "controls.json")["controls"])
        for row in extension_rows
    )
    extension_empirical = sum(
        (ROOT / "claims" / row["claim_id"] / "empirical_validation.json").exists()
        for row in extension_rows
    )
    if extension_empirical != 89:
        raise SystemExit(f"expected 89 empirical extension packages, found {extension_empirical}")
    upstream_candidates = sum(
        read(ROOT / "claims" / claim_id / "candidate_census.json")["expected_cardinality"]
        for claim_id in UPSTREAM
    )
    mission = open_science_position(
        "For Chemistry, a periodic-table entry, handbook definition, fitted Hamiltonian or opaque predictor may test or "
        "translate a sealed result but cannot select chemical identity, shell capacity, nuclear closure or an endpoint. "
        "Known-domain agreement, standing prediction and specimen-dependent measurement are kept as different evidence "
        "classes so that persuasive presentation never erases scientific custody."
    )
    sections = [f"""# From Fold to Chemistry

**Chemistry Branch Paper 001, version 1.2.0 — Smithian Fold Theory V3 Clean-Room Reconstruction**

## Abstract

This paper reports the secure Chemistry foundation and the admitted field-wide extension of the third clean-room reconstruction of Smithian Fold Theory. The foundational inventory contains 86 admitted laws, {foundation_candidates:,} completely enumerated candidates, 86 unique survivors and {foundation_controls} adverse controls. Ninety further Chemistry laws have since passed the same untouched fail-closed engine, adding {extension_candidates:,} candidates, 90 survivors and {extension_controls} controls. The live evidence surface therefore contains 176 admitted Chemistry laws, {live_candidates:,} enumerated candidates, 176 survivors and {foundation_controls + extension_controls} controls. One hundred seventy-five claims include post-seal empirical packages; the remaining operational classical-quantum correspondence is an independently reconstructed formal law. Closure is exact at each registered grammar and evidence boundary: 171 laws are depth-independent and five are finite-complete. The foundation is complete to the present standard and remains open to lawful extension; the full-discipline reconstruction is not represented as finished.

The results include exact orbit capacities 2, 6, 10, 14 and 18; nuclear closures 2, 8, 20, 28, 50, 82, 126 and 184; Smithium at Z=126, N=184, A=310 with active 8s2 5g6 organization; g-block opening at 121; and a structural endpoint at 137. The field extension establishes a single shared carrier across thirteen molecular-property families and 9,025 source rows without per-property fitting; an exact thirteen-row water entropy vector and phase jump of 13637763/125000 J mol^-1 K^-1; 276 retained colligative-response records; a 90-ratio and three-decay isotope-effect record; recurrence supports 6, 10 and 14 with a blind aromatic stability excess of 150.39 kJ mol^-1; and eight of eight independently enumerated rearrangement endpoint inventories. External records test sealed consequences; they do not choose the grammar or survivor.

## Results first: exact chemical structure and standing predictions

| Headline result | Exact result | Empirical status and meaning |
|---|---|---|
| Atomic orbit capacities | `2, 6, 10, 14, 18` | Forced from three-space, its rank-two boundary, two held Fold labels and exclusion; the known periodic organization is checked only after sealing. |
| Nuclear closure sequence | `2, 8, 20, 28, 50, 82, 126, 184` | Exact match to the complete registered IAEA closure sequence. The `126/184` coordinate supplies the island-of-stability carrier used below. |
| g-block opening | `Z = 121` | Standing unobserved prediction: the complete fill walk first opens the `5g` organization at element 121. |
| Smithium | `Z = 126`, `N = 184`, `A = 310`; active organization `8s2 5g6` | Standing unobserved prediction. Known IUPAC support through element 118 is retained separately and does not count as observation of Smithium. |
| Atomic structural endpoint | `Z = 137` | Standing unobserved prediction forced by the greatest-whole order beneath the exact inverse-alpha carrier. |
| Physical prerequisite used at the chemical boundary | `alpha^-1 = 503846395469/3676744786 = 137.035999177180855...` | Derived and empirically validated in the owning Physics branch against CODATA; Chemistry cites that admitted dependency and does not relocate or re-fit the constant. |
| Secure Chemistry foundation | 86 laws; {foundation_candidates:,} candidates; 86 survivors; {foundation_controls} controls; 86 independent reconstructions and 86 empirical packages | All twelve foundational criteria are covered. This is current-evidence closure, never a permanent lock against lawful additions. |
| Live admitted Chemistry evidence | 176 laws; {live_candidates:,} candidates; 176 survivors; {foundation_controls + extension_controls} controls | The successor paper includes every foundational law and all 90 admitted extensions. Wider field coverage remains active rather than being hidden or declared complete. |
| One carrier across molecular properties | 13 property families; 9,025 complete source rows; 1,104 carriers; 676 overlap carriers and 6,676 overlap rows | The registered falsifier rejects any separately fitted carrier or coefficient and any omitted or guessed join. |
| Exact chemical entropy correspondence | 13 NIST water rows; phase jump `13637763/125000 J mol^-1 K^-1`; independent enthalpy/temperature record `4066845420/37275593` | The exact positive distinction ledger is primary; the measured entropy vector is opened post-seal and preserved in full. |
| Colligative response | 276 records: 144 boiling, 37 freezing and 95 osmotic | The common solvent/solute carrier preserves orientation as a held label and rejects conventional fitted constants at the derivational boundary. |
| Kinetic isotope effects | 90 explicit rate ratios and three direct decay KIEs across 47 pages and 23 worksheets | Normal, inverse, near-equal, reviewer challenges and source limitations are retained; favorable rows are not selected out. |
| Aromatic recurrence and stability | support sequence `6, 10, 14`; blind stability excess `150.39 kJ mol^-1`; uncertainty `6.60`; positive lower envelope `143.79` | Three outcome-unopened CCCBDB sources, 59 tables and 353 rows test the sealed recurrence consequence. |
| Molecular rearrangement | eight of eight exact endpoint inventories favorable: `C8H12O3`, `C9H14O3`, `C12H20O3`, `C15H18O3`, `C9H14O3`, `C11H18O3`, `C16H20O3`, `C16H26O3`; all eight have positive constitutional-incidence change | All 38 supporting-information pages and the earlier incomplete surface are preserved; unresolved first-surface rows are not relabelled as favorable. |

{mission}

## 1. Publication, authorship and license boundary

{boundary}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Submissions and reproducibility reports: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

The paper is prepared for CC BY 4.0 distribution; code is Apache-2.0. Copyright preserves authorship while the licenses preserve open inspection, reuse and criticism. The Ernos Labs designation denotes conformance to the published empirical and community standards; it is not transferred merely by copying the work.

## 2. Exact scope

The foundational inventory contains 86 obligations in ten ordered subbranches and all are admitted. The live Chemistry census contains those 86 foundations plus 90 admitted field-wide extensions. Closure means each of those 176 registered questions has one machine-admitted law at its exact generated and evidence boundary; it does not mean no later question or stronger observation may extend the branch. The active continuation ledger is 78 of 175 obligations beyond the trusted 98-claim checkpoint, leaving 97 declared operations. Its next lawful operation is ORG-012, the pericyclic-reaction law. Neither the 97 remaining operations nor any future discovery is absorbed into the claims documented here.

Materials bulk properties, biological function, clinical intervention, Earth-system fate and applications remain later branches. Observed absence beyond element 118 is not promoted into proof. The 121, 126 and 137 results are standing predictions. A frozen earlier discipline projection is retained for history and protected-verifier reproducibility; it is not silently rewritten to impersonate the live admission ledger.

## 3. Constitutional arithmetic

Structural absence is empty One, never numerical zero. Proof magnitudes are positive generated counts and exact positive rational parts or ratios. Opposition, orientation, gain/loss direction and charge sense are held labels, never negative proof quantities. Irrational, imaginary and floating proof values, completed infinity, imported equations, fitted coefficients, learned parameters and target-selected forms are prohibited. Host counters may enumerate artifacts but have no scientific value authority.

## 4. Single-engine admission

Every claim enters `SFTAdmissionEngine`. Registration verifies root identity, zero axioms, zero free parameters, admitted dependencies and exact source identity. The engine then requires complete candidate identity/cardinality, one decision per candidate, exactly one survivor, closure, minimality, named-shape uniqueness, four controls and an implementation-distinct reconstruction. Empirical claims additionally require an evaluator-verified derivation seal, capability isolation, target absence before seal, matching custody release, all-row retention and a falsification condition. Failure halts and is retained; it cannot be edited into admission.

## 5. External evidence and blind prediction

IUPAC terminology and periodic-table records test categorical consequences. NIST and IAEA records test sealed numerical or ordered-sequence consequences. External data never select the grammar or survivor. The capability-closed predictor cannot read the filesystem, network, clock, environment, subprocess, dynamic import or foreign function. A distinct target custodian releases only after a matching prediction seal, every registered row is compared, and a deliberately changed row must fail.

## 6. Preserved failure and lawful correction

The original prerequisite programs retained two capacity survivors, two nuclear-schedule survivors and no endpoint survivor. Their rejection receipts remain immutable. V3 then derived new discriminators: generator three, stable three-space, boundary rank two, exact orbit orientation, exact colour coupling, complete three-direction shell composition, the finite inverse-alpha promotion ladder and a greatest-whole order certificate. The later admissions do not rewrite the failed runs; they change the admitted dependency surface through separately proved claims.

## 7. V1/V2 reconciliation without proof import

V1/V2 identify mandatory questions, including magic numbers, Smithium, the g-block and endpoint. They supply no answer-bearing input to V3. `census/lineage_reconciliation.json` binds those sources by hash and now records the elements/nuclear/island-of-stability group as closed at the current V3 standard. Other lineage groups remain open for their own branches and the final TOE paper.

## 8. Foundation security audit

The twelve required foundation criteria are fully represented by the 86-claim inventory: identity and traceable observation; elements, isotopes, ions and atomic-weight records; periodic order and boundary; composition and stoichiometry; bond classes and bond distinctions; molecular organization; reaction, mechanism, rate, equilibrium and catalysis; acid/base and redox; thermochemical, phase and solution foundations; analytical traceability; and exact handoffs. Their complete evidence surface contains {foundation_candidates:,} candidate decisions, 86 unique survivors, {foundation_controls} adverse controls, 86 implementation-distinct reconstructions and 86 empirical packages. All 86 closures are depth-independent. No foundational receipt was regenerated for this paper.

The audit verifies two different things and does not conflate them. Foundation sufficiency asks whether all twelve declared prerequisites for starting Chemistry are evidenced; the answer is yes. Full-discipline sufficiency asks whether every present Chemistry family has completed the same route; the answer is not yet. This is why the foundation can support the paper and downstream work while the branch remains open to its 97 declared continuation operations and to later lawful extensions.

## 9. Full-field roadmap and present position

The ninety admitted extensions already cover six dependency-ordered families:

- sixteen molecular electronic and quantum-chemical laws;
- fourteen quantitative molecular-structure and property laws;
- nineteen statistical, thermodynamic, phase and transport laws;
- thirteen quantitative kinetics and reaction-dynamics laws;
- seventeen inorganic, coordination and organometallic laws; and
- eleven organic structure and mechanism laws through exact molecular rearrangement.

The remaining roadmap continues from ORG-012 through the unfinished organic family and then through quantitative electrochemistry; nuclear chemistry and radiochemistry; spectroscopy, separations and complete analytical performance; computational chemistry and cheminformatics; quantitative polymer chemistry; larger blind external-validation matrices; nanochemistry and confined-scale chemistry; energy-coupled transformation families; industrial/process boundaries; and the exact handoffs to Materials, Biology, Medicine, Earth Science and Astronomy. Every later family must earn its own grammar, complete enumeration, unique survivor, falsification controls, implementation-distinct reconstruction, unchanged-engine receipt and external comparison wherever an observation can be made.

## 10. How to read the claim ledger

Every section below projects the complete machine evidence: statement, dependencies, grammar, boundary, candidate cardinality, sole survivor, axis eliminations, controls, independent reconstruction, external rows, exclusions and immutable receipt identities. The JSON claim packages remain authoritative and are included in the release archive.
"""]
    section = 11
    order = 1
    for subbranch in inventory["subbranch_order"]:
        sections.append(f"\n## {section}. {subbranch.replace('_', ' ').title()}\n\n{SUBBRANCH_INTRO[subbranch]}\n")
        for row in (item for item in obligations if item["subbranch"] == subbranch):
            sections.append(claim_block(order, row["claim_id"], subbranch))
            order += 1
        section += 1
    offset = 0
    for context, count in EXTENSION_FAMILIES:
        family_rows = extension_rows[offset:offset + count]
        if len(family_rows) != count:
            raise SystemExit(f"incomplete extension family {context}")
        sections.append(
            f"\n## {section}. {context.replace('_', ' ').title()} — admitted field extension\n\n"
            f"{SUBBRANCH_INTRO[context]} This section projects all {count} receipt-backed claims in the family; none is credited from preparation files alone.\n"
        )
        for row in family_rows:
            sections.append(claim_block(order, row["claim_id"], context))
            order += 1
        offset += count
        section += 1
    if offset != len(extension_rows):
        raise SystemExit("extension family partition does not cover every live extension")
    sections.append(f"\n## {section}. Exact upstream prerequisite and validation appendix\n\nThese seven claims are not hidden assumptions. They are separately engine-admitted V3 laws with their own complete evidence.\n")
    for claim_id in UPSTREAM:
        sections.append(claim_block(order, claim_id, "upstream", level=3))
        order += 1
    sections.append(f"""
## {section + 1}. Integrated result and scientific meaning

The evidenced surface unifies chemical identity, exact composition, molecular electronic organization, bonding, quantitative properties, reactions, thermochemistry, transport, kinetics, inorganic coordination, stereochemistry, organic mechanisms, polymers, analysis and periodic organization under one provenance-preserving state-transition framework. Chemical laws do not begin with a periodic-table diagram or a fitted Hamiltonian. They begin with generated distinguishability, held labels, complete joint support, exclusion, recurrence, conservation and observation classes. Conventional names and measured scalar inscriptions appear only at the correspondence boundary.

The terminal sequence has two independent locks. First, three-space and its rank-two boundary force orbit orientation growth; the two Fold labels and exclusion force capacities 2, 6, 10, 14 and 18. Second, complete three-direction compositions and the separately sealed 2/3 colour coupling force the nuclear closures. The joint-cover fill walk then reproduces the known noble closures and extends to the 5g prediction. The terminal inverse-alpha object independently supplies the atomic existence ceiling. Agreement of the upstream known support does not constitute observation of the future coordinates.

## {section + 2}. Reproducibility route

The one-command repository validator rechecks schemas, source identities, engine unit/E2E coverage and every admitted receipt in order. The preserved foundational publication verifier still checks its frozen 86/86 release boundary. This successor manuscript additionally projects all 90 later Chemistry receipts, giving 176/176 live admitted Chemistry claims, with all evidence files, one survivor per claim, every control, empirical custody where applicable and implementation-distinct reconstruction. The paper build is a read-only projection and never changes a derivation. The full heavy repository verification is reserved for the later Chemistry Grand Lock and is not misrepresented as having been rerun for this manuscript preparation.

## {section + 3}. Limitations and falsifiers

- IUPAC correspondence through 118 does not confirm element 121, Smithium or element 137.
- The structural endpoint is the registered point-carrier One-ceiling result; other physical models cannot be silently substituted into its claim boundary.
- The predicted Smithium oxidation counts are structural model consequences awaiting direct chemical observation.
- Any official target mismatch, missing row, source-hash change, replay mismatch or accepted tampered control fails the corresponding claim.
- Open V1/V2 lineage groups outside Chemistry remain mandatory V3 work; this paper does not paper them over.
- Ninety admitted extensions do not constitute all chemical science; 97 declared continuation operations remain after ORG-011.
- A branch is never permanently locked. A lawful discovery may extend or correct it only through a new versioned claim and the unchanged admission route.

## {section + 4}. Conclusion

Chemistry's foundation is complete to the present standard: 86 required foundations, {foundation_candidates:,} candidate decisions, 86 unique survivors, {foundation_controls} controls, 86 independent reconstructions and 86 empirical packages. The wider reconstruction has already earned 90 further admissions, bringing the documented surface to 176 laws, {live_candidates:,} candidate decisions, 176 survivors and {foundation_controls + extension_controls} controls. It remains active and extension-open with 97 declared operations after ORG-011. The paper preserves the difference between exact derivation, known-domain correspondence, finite-complete evidence and unobserved prediction. Its authority is the open chain from the premise-free root theorem to inspectable receipts, not credential, consensus or opaque prediction.

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
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    PAPER.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} exhaustive claim sections")


if __name__ == "__main__":
    main()
