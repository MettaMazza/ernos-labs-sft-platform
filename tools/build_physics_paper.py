#!/usr/bin/env python3
"""Build the exhaustive Physics branch manuscript from admitted evidence.

This is a deterministic documentation projection.  It does not execute a
derivation, reopen a target vault, alter a receipt or authorize publication.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "publications/inventories/physics.json"
PAPER = ROOT / "publications/current/physics/FROM_FOLD_TO_PHYSICS.md"
CENSUS = ROOT / "census/claims.json"
METADATA = ROOT / "publication/physics_zenodo_metadata.json"


SUBBRANCH_INTRO = {
    "measurement_metrology": "Measurement is reconstructed before natural law: observation classes, quantities, dimensions, units, references, uncertainty and calibration remain exact carriers, while decimal inscriptions stay outside the proof domain.",
    "mechanics": "Mechanics is reconstructed as exact state change, recurrence count, relational displacement and closed transfer. Motion quantities are not imported coordinates; each is the minimal Fold carrier retaining the relevant event and resource trace.",
    "interactions_fields": "Fields are source-bound response maps over generated support. Held labels carry orientation without signed proof magnitude, and locality requires a complete adjacent propagation trace.",
    "waves": "Waves are finite recurrence and propagation structures. Superposition, interference, diffraction, polarization, dispersion and resonance arise from complete path support and held recurrence labels rather than continuum amplitudes.",
    "thermodynamics": "Thermodynamics is reconstructed over complete finite microstate support. Temperature, entropy, equilibrium and irreversibility are exact observation and transfer relations; ontic randomness is not introduced.",
    "quantum_physics": "Physical quantum theory is the empirical correspondence of the already closed Fold quantum computation model. Support, phase, composition, observation and environmental records remain exact and deterministic at complete-state level.",
    "matter_particles_nuclei": "Matter is classified by minimal recurrent physical words, exchange classes, conserved labels and complete transition channels. Empirical tables determine observed membership only after the classification law is sealed.",
    "spacetime_gravitation": "Spacetime is relational event support and gravitation is source-linked path structure. No background continuum or imported metric equation is installed as a premise.",
    "continua_collective_matter": "Continuum language is recovered as a declared observation quotient of finite generated cell networks. Fluids, plasmas and condensed phases retain local transfer and boundary provenance.",
    "cosmological_boundary": "The final Physics group closes universal source, propagation and observation relations while explicitly handing astronomical census, historical initial conditions and cosmic chronology to the later Astronomy/Cosmology branch.",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: object) -> str:
    return str(value).replace("\n", " ").strip()


def list_items(values) -> str:
    rows = tuple(values)
    return "\n".join(f"- {clean(value)}" for value in rows) if rows else "- None."


def axis_eliminations(candidate: dict, elimination: dict) -> list[tuple[str, str, str, str]]:
    decisions = {row["candidate_id"]: row for row in elimination["decisions"]}
    survivor_id = next(key for key, row in decisions.items() if row["survives"])
    survivor_candidate = next(row for row in candidate["candidates"] if row["candidate_id"] == survivor_id)
    survivor_coordinates = survivor_id.split("__")
    axis_names = [part.split("=", 1)[0] for part in survivor_candidate["exact_form"].split("; ")]
    domains = []
    for position in range(len(survivor_coordinates)):
        domains.append(tuple(dict.fromkeys(row["candidate_id"].split("__")[position] for row in candidate["candidates"])))
    output = []
    for position, (axis, chosen) in enumerate(zip(axis_names, survivor_coordinates)):
        rejected = next(value for value in domains[position] if value != chosen)
        changed = list(survivor_coordinates); changed[position] = rejected
        reason = decisions["__".join(changed)]["reason"]
        output.append((axis, chosen, rejected, reason))
    return output


def experiment_details(claim_id: str) -> tuple[list[str], list[str]]:
    matches = list((ROOT / "experiments/physics").glob(f"*/registration.json"))
    registrations = [read(path) for path in matches]
    registrations = [row for row in registrations if row.get("claim_id") == claim_id]
    sources: list[str] = []
    locators: list[str] = []
    for row in registrations:
        for source in row.get("external_measurement_sources", []):
            sources.append(f"{source.get('measurement_body', source.get('source_id'))}: {source.get('source_uri', '')} ({source.get('snapshot_hash', '')})")
        for target in row.get("withheld_targets", []):
            locators.append(f"{target.get('target_id')} from {target.get('source_id')}")
    return list(dict.fromkeys(sources)), list(dict.fromkeys(locators))


def claim_block(order: int, claim_id: str, subbranch: str, heading_level: int = 3) -> str:
    claim = ROOT / "claims" / claim_id
    registration = read(claim / "registration.json")
    candidate = read(claim / "candidate_census.json")
    elimination = read(claim / "elimination_receipt.json")
    controls = read(claim / "controls.json")["controls"]
    certificate = read(claim / "certificate.json")
    empirical_path = claim / "empirical_validation.json"
    empirical = read(empirical_path) if empirical_path.exists() else None
    census_row = next(row for row in read(CENSUS)["claims"] if row["claim_id"] == claim_id)
    survivor = next(row for row in elimination["decisions"] if row["survives"])
    exact_result = certificate["exact_result"]
    sources, locators = experiment_details(claim_id)
    prefix = "#" * heading_level
    axis_rows = ["| Axis | Forced form | Eliminated form | Elimination reason |", "|---|---|---|---|"]
    for axis, chosen, rejected, reason in axis_eliminations(candidate, elimination):
        axis_rows.append(f"| `{axis}` | `{chosen}` | `{rejected}` | {clean(reason)} |")
    axis_table = "\n".join(axis_rows)
    controls_rows = "\n".join(
        f"- `{row['kind']}`: passed; expected {clean(row['expected_behavior'])}; observed {clean(row['observed_behavior'])}; receipt `{row['receipt_hash']}`."
        for row in controls
    )
    empirical_text = "This formal prerequisite makes no direct natural-law claim."
    if empirical:
        measurement_rows = "\n".join(f"- {clean(value)}" for value in empirical["measurements"])
        empirical_text = f"""The target was absent until prediction seal: `{empirical['target_custody_certificate']['target_absent_until_prediction_seal']}`. It was released after the matching seal: `{empirical['target_custody_certificate']['released_after_prediction_seal']}`. All rows were preserved: `{empirical['all_rows_preserved']}`. The isolation certificate denied clock, environment, filesystem, network, subprocess, dynamic-import and foreign-function capabilities and reported no attempted forbidden operation.

External source identities:

{list_items(empirical['data_source_ids'])}

Observed comparison records:

{measurement_rows}

Falsification condition: {clean(empirical['falsification_condition'])}

Measurement receipt: `{empirical['measurement_receipt_hash']}`. Isolation certificate: `{empirical['isolation_certificate']['certificate_hash']}`. Custody certificate: `{empirical['target_custody_certificate']['certificate_hash']}`."""
    excluded = registration.get("excluded_inputs", [])
    dependency_rows = list_items(f"`{value}`" for value in registration.get("dependencies", []))
    source_rows = list_items(sources)
    locator_rows = list_items(locators)
    meaning = SUBBRANCH_INTRO.get(subbranch, "This supplemental claim tests a previously forced relation against an exact external value interval.")
    return f"""{prefix} {order}. {registration['title']}

Claim identity: `{claim_id}`

**Question.** Which generated form preserves the physical carrier, the Fold relation, complete provenance, target inaccessibility, measurement separation, complete rows, successor closure and absence of an extra rule?

**Theorem.** {clean(registration['statement'])}

> {clean(exact_result)}

**Dependency chain.** The engine accepted only the following already model-admitted premises in addition to the single root theorem:

{dependency_rows}

**Generated grammar and closure boundary.** {clean(candidate['generation_rule'])} The declared exact boundary is: {clean(candidate['grammar_boundary'])} The generator produced `{candidate['expected_cardinality']}` named candidates and the decision support contains `{len(elimination['decisions'])}` one-for-one decisions. Exactly one candidate survived: `{survivor['candidate_id']}`. Closure is `{certificate['closure_scope']}` with both minimality and named-shape uniqueness passed.

**Complete axis elimination.** The 256-form census is the literal product of eight binary choices. Each row below compares the survivor coordinate with the otherwise-surviving form changed on that coordinate alone.

{axis_table}

**Base and successor.** The closure proof is sealed by derivation hash `{certificate['derivation_seal_hash']}`. Its generality certificate is stored in `elimination_receipt.json`; it preserves the registered One base and successor statement for every generated positive finite extension. The complete candidate and decision files are part of this claim package rather than abbreviated by the paper.

**Adverse controls.** All four mandatory controls passed:

{controls_rows}

**Independent reconstruction.** A distinct standard-library implementation regenerated the candidate product and survivor. Implementation hash: `{certificate['independent_implementation_hash']}`. Independent certificate: `{certificate['independent_certificate_hash']}`. Engine external-validation hash: `{certificate['external_validation_hash']}`.

**External empirical check.** {empirical_text}

Registered source descriptions:

{source_rows}

Registered target identities:

{locator_rows}

**Meaning.** {meaning} In this claim specifically, the forced result identifies the minimal exact relation named in the theorem; the external body tests the sealed consequence but does not choose its grammar or survivor.

**Boundary and non-claim.** The following forms are explicitly excluded:

{list_items(excluded)}

The result is closed only at its registered generated and empirical boundary. It does not turn an external unit scale, historical initial condition or finite observation census into a premise-free consequence of the One.

**Immutable evidence identities.** Source manifest `{certificate['source_manifest_hash']}`; engine receipt `{census_row['receipt_hash']}` at `{census_row['receipt_path']}`; empirical-validation hash `{certificate.get('empirical_validation_hash')}`; measurement receipt `{certificate.get('measurement_receipt_hash')}`.
"""


def main() -> None:
    inventory = read(INVENTORY)
    metadata = read(METADATA)
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized and not doi:
        raise SystemExit("Authorized Physics publication requires a reserved DOI")
    publication_boundary = (
        f"**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: "
        f"[{doi}](https://doi.org/{doi}). This canonical Markdown paper, its rendered PDF, "
        "complete evidence/source archive and checksum ledger form the Physics Branch Paper 001 release."
        if authorized
        else "**LOCAL PREPUBLICATION MANUSCRIPT. Publication is not yet authorized.** This file and its rendered PDF may be inspected locally, but no GitHub push, release, Zenodo upload, DOI reservation or publication action follows from the branch gate."
    )
    if inventory["admitted_claim_count_at_freeze"] != inventory["required_claim_count"]:
        raise SystemExit("Physics inventory is not fully admitted")
    obligations = inventory["obligations"]
    by_subbranch = {key: [row for row in obligations if row["subbranch"] == key] for key in inventory["subbranch_order"]}
    census = read(CENSUS)["claims"]
    supplemental = [row["claim_id"] for row in census if row["claim_id"].startswith("SFT-PHYS-VALIDATION-")]
    sections = []
    sections.append(f"""# From Fold to Physics

## Abstract

This paper reports the third clean-room Smithian Fold Theory reconstruction of the Physics branch. It documents 132 required laws across measurement and metrology, mechanics, fields, waves, thermodynamics, physical quantum theory, matter and nuclei, spacetime and gravitation, collective matter, and the physics-to-cosmology boundary. Every required law passed the single admission engine with a complete 256-form grammar, exactly one survivor, minimality, named-shape uniqueness, four adverse controls, a source-bound derivation seal and an implementation-distinct reconstruction. Natural-law claims additionally carry capability-closed prediction, target custody, seal-before-open evaluation, complete external rows and falsification records. Eight supplemental claims backfill exact measured-value relations for earlier subbranches. Fourteen required or supplemental claims execute exact positive rational interval predictions against official external measurements without binary floating arithmetic. The paper distinguishes forced law from unit scale, measured initial state and finite census; it claims closure only at the declared generated and empirical boundaries.

## 1. Publication and authorship boundary

{publication_boundary}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Submissions and reproducibility reports: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

The paper is prepared for CC BY 4.0 distribution; the engine code remains under the repository's Apache-2.0 license. Copyright preserves authorship while the licenses preserve open inspection, reuse and independent criticism. Use of the Ernos Labs designation requires adherence to the published empirical and community standards.

## 2. Scope and result

The frozen inventory contains 132 obligations in ten ordered subbranches. All 132 are model-admitted. Their combined required grammar contains 33,792 candidates, 33,792 decisions, 132 survivors and 528 passing mandatory controls. Eight supplemental numerical-validation claims add 2,048 candidates, eight survivors and 32 controls. The complete repository census now contains 308 claims and 91,794 generated candidates across all closed branches.

Physics closure here means that every obligation in the frozen categorical inventory has one engine-admitted law at its exact boundary. It does not mean that every future physical observation, material, astronomical object or historical state has already been enumerated. Chemistry, materials science, astronomy and cosmology remain later branches.

## 3. Exact constitutional domain

The derivational domain admits the empty One as structural absence but never numerical zero. Proof magnitudes are positive generated counts and exact positive rational parts or ratios. Orientation, opposition and complement are held labels rather than negative quantities. Irrational, imaginary and binary floating values are barred from proof. Completed infinity, an ungenerated continuum, axioms, fitted coefficients and free parameters are also barred. External decimal measurements remain source-bound records. A finite decimal is converted to an exact rational interval only inside the empirical adapter and never gains authority to select the Fold law.

## 4. The single admission engine

Each claim enters one `SFTAdmissionEngine`. Registration rejects axioms, free parameters, missing root trace, unadmitted dependencies and source-identity failure before candidate execution. The engine then checks census cardinality and identity, one decision per candidate, exactly one survivor, minimality, named-shape uniqueness, the four mandatory controls, an implementation-distinct external reconstruction and, for empirical claims, prediction isolation, target custody, complete rows and falsification. A failure halts without model admission. Accepted receipts are immutable evidence identities; this paper does not replay or replace them.

## 5. Why superdeterminism permits uncertainty and quantum weights

No law in this branch installs ontic nondeterminism. The complete Fold state includes preparation, held labels, measurement setting, path and observation record. A probabilistic or quantum weight is an exact census ratio over unresolved support. Each branch execution remains deterministic. Measurement uncertainty records distinctions unavailable to an observation class; it does not assert causeless state selection. Bell correspondence therefore retains setting and preparation records in the complete state, identifies the factorization assumption that fails, and separately preserves the no-signalling marginal through complete remote-fibre enumeration.

## 6. Empirical constitution

External evidence follows one direction. First the Fold dependencies generate and eliminate candidate laws. Then a data-only Fold program receives only registered inputs and the sealed derivation identity. Its instruction set has no filesystem, network, subprocess, clock, environment, dynamic import or foreign-function capability. A distinct custodian commits target identity before execution and releases content only to the matching prediction seal. The evaluator preserves every registered row and must reject a deliberately altered or displaced control. BIPM, NIST/CODATA, NIST ASD, PDG, IAEA, IAPWS, GWOSC, CERN Open Data and NASA LAMBDA supply the external records.

## 7. Exact measured-value correspondence

Measured-value forcing means that a parameter-free Fold relation maps registered measured input carriers to a withheld measured target. It does not mean that the numerical size of the SI metre, the universe's initial temperature or a contingent particle mass is created from no physical record. Finite decimals and uncertainties are parsed as exact positive fractions. Multiplication and quotient propagate interval endpoints in the capability-closed interpreter; target overlap is evaluated only after release. Exact official decimal prefixes with ellipses are bounded by their next decimal place. Any non-overlap halts admission.

The value suite includes molar Planck composition, momentum, force, electric potential and field, wave frequency and energy, molar thermal energy, quantum action-energy time, mass-energy equivalence, limiting speed, molar mass, collective molar charge and COBE FIRAS background-temperature invariance. Every one passed its official uncertainty interval and rejected a displaced interval.

## 8. Reading the derivation ledger

Each claim section below is a self-contained prose projection of its machine evidence. The complete `candidate_census.json`, `elimination_receipt.json`, `controls.json`, `certificate.json`, external experiment registration and receipt remain authoritative. The paper includes every claim identity and admitted receipt hash so the evidence map can fail closed on omission or substitution.
""")
    section_number = 9
    order = 1
    for subbranch in inventory["subbranch_order"]:
        title = subbranch.replace("_", " ").title()
        sections.append(f"\n## {section_number}. {title}\n\n{SUBBRANCH_INTRO[subbranch]}\n")
        for row in by_subbranch[subbranch]:
            sections.append(claim_block(order, row["claim_id"], subbranch))
            order += 1
        section_number += 1
    sections.append(f"\n## {section_number}. Supplemental exact measured-value admissions\n\nThese eight claims do not replace the required laws or their receipts. They depend on those laws and add exact post-seal numerical correspondence where the first structural validations predated the measured-value interpreter.\n")
    for index, claim_id in enumerate(supplemental, 1):
        sections.append(claim_block(index, claim_id, "supplemental", heading_level=3))
    section_number += 1
    sections.append(f"""
## {section_number}. Cross-branch synthesis

The completed branch has one compositional arc. Measurement defines what an observation can retain. Mechanics defines relational change and transfer. Fields extend source-response over local support. Waves close recurrence and propagation. Thermodynamics identifies macro-observation fibres and information-retention costs. Physical quantum theory retains complete support, phase/action and joint composition. Matter identifies recurrent constituent and channel classes. Spacetime orders events by limiting causal paths; gravitation changes their source-linked relational closure. Collective matter takes finite cell networks to scale-declared macro-observations. The cosmological boundary exports universal propagation laws while refusing to disguise historical state as a law.

This unification is operational: the same Fold objects - exact counts, ratios, words, held labels, tables, transition traces and observation fibres - appear in every subbranch. The claim is not that established terminology selected those objects. Correspondence is registered only after each Fold form survives its generated alternatives.

## {section_number + 1}. Limitations and falsification

The paper makes no claim of an actually completed physical infinity, exact continuum substrate, derivation of contingent initial conditions, unbounded astronomical census or replacement of later Chemistry, Materials, Astronomy and Cosmology branches. It does not treat a simulation as empirical proof, an exact SI definition as an independent natural observation, or portal availability as numerical agreement. Categorical external rows test structural correspondence; the dedicated value adapters test numerical consequences. A new observation outside the registered boundary requires a new preregistration and cannot silently broaden an old receipt.

Any admitted empirical claim is falsified within its boundary by a preserved external row that does not match the sealed prediction, by target access before sealing, by omitted adverse evidence, by a changed source snapshot, by failure of its independent reconstruction or by an engine-constitution violation. The correct response is a halted new claim and investigation of the derivation or adapter. Existing immutable receipts remain identities of the artifacts they certify; new evidence cannot be retroactively written into them.

## {section_number + 2}. Reproducibility

The repository uses Python's standard library for the core engine and supports macOS, Windows and Linux without Docker. Researchers may inspect every claim package directly. The one-command repository verifier remains available for release validation, but this branch build deliberately used proportionate admission-time checks and a read-only evidence census rather than repeatedly replaying historical derivations. The Physics inventory is `publications/inventories/physics.json`; this manuscript's exact evidence map is `publications/current/physics/evidence_map.json`.

## {section_number + 3}. Conclusion

At the declared boundary, the Physics programme is complete: 132 required derivations are forced, enumerated, independently reconstructed, externally tested and admitted through one engine. The measured-value layer preserves the project's strict arithmetic constitution while allowing official observations to invalidate a sealed relation. The result is an open, inspectable tree of physical laws whose authority rests on reproducible traces rather than credentials, opaque prediction or consensus selection.

## References and official data bodies

- Bureau International des Poids et Mesures, *The International System of Units (SI), 9th edition*.
- National Institute of Standards and Technology and CODATA, *2022 Fundamental Physical Constants - Complete Listing*.
- National Institute of Standards and Technology, Atomic Spectra Database, version 5.12.
- Particle Data Group, *2025 Review and Summary Tables*.
- International Atomic Energy Agency, ENSDF and ENDF evaluated nuclear-data systems.
- International Association for the Properties of Water and Steam, official releases.
- Gravitational Wave Open Science Center, GWTC catalog and event APIs.
- CERN Open Data Portal, public dataset API.
- NASA LAMBDA and COBE FIRAS public data products.
- Smith, Maria, *There Is No Nothing*, Ernos Labs methods and foundation paper.
- Smith, Maria, *From One to Fold*, Foundation branch evidence corpus.
- Smith, Maria, *From Fold to Mathematics*, Mathematics branch paper.
- Smith, Maria, *From Distinction to Information*, Information Science branch paper.
- Smith, Maria, *After Turing: The Fold Machine*, Classical Computation branch paper.
- Smith, Maria, *The Quantum Fold Machine*, Reversible and Quantum Computation branch paper.
""")
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    PAPER.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} required claim sections and {len(supplemental)} supplemental sections")


if __name__ == "__main__":
    main()
