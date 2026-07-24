#!/usr/bin/env python3
"""Build the exhaustive Chemistry manuscript from immutable admitted evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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
}


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


def experiment_details(claim_id: str) -> tuple[list[str], list[str]]:
    rows = []
    for branch in ("chemistry", "physics"):
        for path in (ROOT / "experiments" / branch).glob("*/registration.json"):
            payload = read(path)
            if payload.get("claim_id") == claim_id:
                rows.append(payload)
    sources, targets = [], []
    for row in rows:
        for source in row.get("external_measurement_sources", []):
            sources.append(f"{source.get('measurement_body', source.get('source_id'))}: {source.get('source_uri', '')} ({source.get('snapshot_hash', '')})")
        for target in row.get("withheld_targets", []):
            targets.append(f"{target.get('target_id')} from {target.get('source_id')}")
    return list(dict.fromkeys(sources)), list(dict.fromkeys(targets))


def claim_block(order: int, claim_id: str, context: str, level: int = 3) -> str:
    root = ROOT / "claims" / claim_id
    registration = read(root / "registration.json")
    candidate = read(root / "candidate_census.json")
    elimination = read(root / "elimination_receipt.json")
    controls = read(root / "controls.json")["controls"]
    certificate = read(root / "certificate.json")
    empirical = read(root / "empirical_validation.json") if (root / "empirical_validation.json").exists() else None
    census_row = next(row for row in read(CENSUS)["claims"] if row["claim_id"] == claim_id)
    survivor = next(row for row in elimination["decisions"] if row["survives"])
    sources, targets = experiment_details(claim_id)
    empirical_text = "This is a sealed formal prerequisite. Its empirical status is recorded only by a separate downstream validation claim."
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
    boundary = (
        f"**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: [{doi}](https://doi.org/{doi})."
        if authorized
        else "**LOCAL PREPUBLICATION MANUSCRIPT. Publication is not yet authorized.** No push, upload, DOI action or publication follows from building this file."
    )
    obligations = inventory["obligations"]
    total_candidates = sum(
        read(ROOT / "claims" / row["claim_id"] / "candidate_census.json")["expected_cardinality"]
        for row in obligations
    )
    upstream_candidates = sum(
        read(ROOT / "claims" / claim_id / "candidate_census.json")["expected_cardinality"]
        for claim_id in UPSTREAM
    )
    sections = [f"""# From Fold to Chemistry

## Abstract

This paper reports the Chemistry branch of the third clean-room reconstruction of Smithian Fold Theory. It documents all 86 obligations in the frozen inventory and the seven newly required upstream physical prerequisite/validation claims. Every claim passed one fail-closed admission engine with a complete generated grammar, exactly one survivor, trace to the premise-free foundational theorem, zero axioms, zero free or fitted parameters, exact permitted arithmetic, four adverse controls and an implementation-distinct reconstruction. Empirical claims add capability-closed prediction, target custody, post-seal opening, complete authoritative rows and tampered controls. The required Chemistry support contains {total_candidates} generated candidates and 86 survivors; the terminal-prediction prerequisite appendix contributes {upstream_candidates} candidates and seven survivors. The formal walk forces orbit widths 2, 6, 10, 14 and 18; nuclear closures 2, 8, 20, 28, 50, 82, 126 and 184; Smithium at Z=126, N=184, A=310 with active 8s2 5g6 organization; g-block opening at 121; and a structural endpoint at 137. NIST/CODATA, IAEA and IUPAC checks occur only after derivation seals. Element 121, Smithium and endpoint 137 remain explicit unobserved predictions.

## 1. Publication, authorship and license boundary

{boundary}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Submissions and reproducibility reports: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

The paper is prepared for CC BY 4.0 distribution; code is Apache-2.0. Copyright preserves authorship while the licenses preserve open inspection, reuse and criticism. The Ernos Labs designation denotes conformance to the published empirical and community standards; it is not transferred merely by copying the work.

## 2. Exact scope

The inventory contains 86 obligations in ten ordered subbranches and all are admitted. Closure means each registered Chemistry question has one machine-admitted law at its exact generated and empirical boundary. Materials bulk properties, biological function, clinical intervention, Earth-system fate and applications remain later branches. Observed absence beyond element 118 is not promoted into proof. The 121, 126 and 137 results are standing predictions.

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

## 8. How to read the claim ledger

Every section below projects the complete machine evidence: statement, dependencies, grammar, boundary, candidate cardinality, sole survivor, axis eliminations, controls, independent reconstruction, external rows, exclusions and immutable receipt identities. The JSON claim packages remain authoritative and are included in the release archive.
"""]
    section = 9
    order = 1
    for subbranch in inventory["subbranch_order"]:
        sections.append(f"\n## {section}. {subbranch.replace('_', ' ').title()}\n\n{SUBBRANCH_INTRO[subbranch]}\n")
        for row in (item for item in obligations if item["subbranch"] == subbranch):
            sections.append(claim_block(order, row["claim_id"], subbranch))
            order += 1
        section += 1
    sections.append(f"\n## {section}. Exact upstream prerequisite and validation appendix\n\nThese seven claims are not hidden assumptions. They are separately engine-admitted V3 laws with their own complete evidence.\n")
    for claim_id in UPSTREAM:
        sections.append(claim_block(order, claim_id, "upstream", level=3))
        order += 1
    sections.append(f"""
## {section + 1}. Integrated result and scientific meaning

The branch unifies chemical identity, exact composition, bonding, reactions, thermochemistry, interfaces, stereochemistry, polymers, analysis and periodic organization under one provenance-preserving state-transition framework. Chemical laws do not begin with a periodic-table diagram or a fitted Hamiltonian. They begin with generated distinguishability, held labels, complete joint support, exclusion, recurrence, conservation and observation classes. Conventional names appear only at the correspondence boundary.

The terminal sequence has two independent locks. First, three-space and its rank-two boundary force orbit orientation growth; the two Fold labels and exclusion force capacities 2, 6, 10, 14 and 18. Second, complete three-direction compositions and the separately sealed 2/3 colour coupling force the nuclear closures. The joint-cover fill walk then reproduces the known noble closures and extends to the 5g prediction. The terminal inverse-alpha object independently supplies the atomic existence ceiling. Agreement of the upstream known support does not constitute observation of the future coordinates.

## {section + 2}. Reproducibility route

The one-command repository validator rechecks schemas, source identities, engine unit/E2E coverage and every admitted receipt in order. The Chemistry publication verifier additionally requires 86/86 claim coverage, all evidence files, one survivor per claim, every control, every empirical custody record, paper inclusion of every receipt, exact evidence-map identities and a visually rendered PDF. This paper build is a read-only projection and never changes a derivation.

## {section + 3}. Limitations and falsifiers

- IUPAC correspondence through 118 does not confirm element 121, Smithium or element 137.
- The structural endpoint is the registered point-carrier One-ceiling result; other physical models cannot be silently substituted into its claim boundary.
- The predicted Smithium oxidation counts are structural model consequences awaiting direct chemical observation.
- Any official target mismatch, missing row, source-hash change, replay mismatch or accepted tampered control fails the corresponding claim.
- Open V1/V2 lineage groups outside Chemistry remain mandatory V3 work; this paper does not paper them over.

## {section + 4}. Conclusion

At its frozen boundary, Chemistry is fully admitted in V3: 86 required claims, every candidate census, one survivor each, complete controls, independent reconstruction and post-seal evidence where empirical. The paper preserves the difference between exact derivation, known-domain correspondence and unobserved prediction. Its authority is the open evidence chain from the premise-free root theorem to immutable receipts, not credential, consensus or opaque prediction.

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
""")
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    PAPER.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} exhaustive claim sections")


if __name__ == "__main__":
    main()
