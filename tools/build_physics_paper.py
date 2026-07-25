#!/usr/bin/env python3
"""Build the exhaustive Physics branch manuscript from admitted evidence.

This is a deterministic documentation projection.  It does not execute a
derivation, reopen a target vault, alter a receipt or authorize publication.
"""

from __future__ import annotations

from collections import Counter
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "publications/inventories/physics.json"
PAPER = ROOT / "publications/current/physics/FROM_FOLD_TO_PHYSICS.md"
CENSUS = ROOT / "census/claims.json"
METADATA = ROOT / "publication/physics_zenodo_metadata.json"


SUBBRANCH_INTRO = {
    "measurement_metrology": "Measurement is reconstructed before natural law: observation classes, quantities, dimensions, units, references, uncertainty and calibration remain exact carriers, while decimal inscriptions stay outside the proof domain.",
    "mechanics_dynamics": "Mechanics and dynamics are reconstructed as exact state change, recurrence count, relational displacement, closed transfer and coupled evolution. Motion quantities are not imported coordinates; each is the minimal Fold carrier retaining the relevant event and resource trace.",
    "fields_forces_waves_geometry": "Three-space, rank-two boundaries, inverse-square dilution, force sectors, fields and waves are generated from Fold support and source-bound response. Held labels carry orientation without signed proof magnitude, and locality requires a complete adjacent propagation trace.",
    "thermodynamics_vacuum": "Thermodynamics and vacuum structure are reconstructed over complete finite support. Temperature, entropy, equilibrium, irreversibility, zero-point structure and extraction limits are exact observation and transfer relations; ontic randomness and unaccounted energy are not introduced.",
    "physical_quantum_relativistic": "Physical quantum and relativistic theory provide empirical correspondence for exact Fold support, phase, composition, observation and causal propagation. Complete-state evolution remains deterministic.",
    "constants_scales_precision": "Dimensionless constants, mass scales and precision values are kept in Physics. Each reported value is tied to its zero-parameter Fold relation, sealed prediction, exact rational measurement adapter and immutable receipt.",
    "matter_interactions_flavour": "Matter, interaction and flavour sectors are classified by minimal recurrent physical words, exchange classes, conserved labels and complete transition channels. External tables test membership and value only after the classification law is sealed.",
    "atomic_molecular": "Atomic and molecular laws are reconstructed from exact Fold support, transition, shell, splitting, rate and spectral relations, including terminal precision successors rather than leaving the measured-value work in Chemistry.",
    "nuclear_hadronic": "Nuclear and hadronic laws close composition, residual interaction, binding, levels, decay, reaction, fission, fusion and spectral support at their registered exact boundaries.",
    "spacetime_gravitation": "Spacetime is relational event support and gravitation is source-linked path structure. No background continuum or imported metric equation is installed as a premise.",
    "continua_collective_matter": "Continuum language is recovered as a declared observation quotient of finite generated cell networks. Fluids, plasmas and condensed phases retain local transfer and boundary provenance.",
    "physical_cosmology_boundary": "The Physics boundary closes universal source, propagation and observation relations while explicitly handing astronomical census, historical initial conditions and cosmic chronology to Astronomy/Cosmology.",
    "post_seal_empirical_validation": "These claims are not supplemental footnotes. They are Physics-owned post-seal empirical tests of forced relations, including exact measured values, and remain first-class engine-admitted claims.",
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
    axis_names = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=", survivor_candidate["exact_form"])
    if len(axis_names) != len(survivor_coordinates):
        axis_names = [f"axis_{index}" for index in range(1, len(survivor_coordinates) + 1)]
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

**Axis-by-axis uniqueness witness.** The complete census is the literal product declared above. Each row below changes one survivor coordinate to a generated alternative while holding the other survivor coordinates fixed. The cited elimination is therefore a direct local witness; the complete decision file records every candidate, including every further value on non-binary axes.

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
    if inventory["admitted_claim_count"] != inventory["required_claim_count"]:
        raise SystemExit("Physics inventory is not fully admitted")
    obligations = inventory["obligations"]
    by_subbranch = {key: [row for row in obligations if row["subbranch"] == key] for key in inventory["subbranch_order"]}
    census = read(CENSUS)["claims"]
    census_by_id = {row["claim_id"]: row for row in census}
    candidate_counts = {
        row["claim_id"]: read(ROOT / "claims" / row["claim_id"] / "candidate_census.json")["expected_cardinality"]
        for row in obligations
    }
    candidate_total = sum(candidate_counts.values())
    empirical_count = sum((ROOT / "claims" / row["claim_id"] / "empirical_validation.json").is_file() for row in obligations)
    control_total = sum(len(read(ROOT / "claims" / row["claim_id"] / "controls.json")["controls"]) for row in obligations)
    cardinalities = Counter(candidate_counts.values())
    headline_ids = [
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-VACUUM-ASYMMETRIC-BEAT-EXTRACTION-003",
        "SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003",
        "SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003",
        "SFT-PHYS-ATOMIC-HYPERFINE-TERMINAL-005",
        "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
        "SFT-PHYS-STATIC-EXTERIOR-CLOCK-TERMINAL-011",
        "SFT-PHYS-QUADRUPOLE-RADIATED-POWER-TERMINAL-012",
        "SFT-PHYS-STRONG-FIELD-NONLINEAR-FIXED-POINT-TERMINAL-014",
    ]
    if any(claim_id not in census_by_id for claim_id in headline_ids):
        missing = [claim_id for claim_id in headline_ids if claim_id not in census_by_id]
        raise SystemExit(f"headline claim missing: {missing}")
    headline_table = "\n".join(
        ["| Result | Claim | Immutable engine receipt |", "|---|---|---|"]
        + [f"| {census_by_id[cid]['title']} | `{cid}` | `{census_by_id[cid]['receipt_hash']}` |" for cid in headline_ids]
    )
    value_rows = [row for row in obligations if row["subbranch"] in {"constants_scales_precision", "post_seal_empirical_validation"}]
    value_table = "\n".join(
        ["| Physics value or post-seal comparison | Claim | Status |", "|---|---|---|"]
        + [f"| {row['title']} | `{row['claim_id']}` | `{census_by_id[row['claim_id']]['external_status']}` |" for row in value_rows]
    )
    sections = []
    sections.append(f"""# From Fold to Physics

## Abstract

This corrected and expanded draft reports the 285 claims currently registered to Physics and admitted by the unchanged engine: {candidate_total:,} explicitly generated candidates, the same number of recorded decisions, {len(obligations)} unique survivors, {control_total:,} passing adverse controls and {empirical_count} claim packages carrying post-seal empirical validation. It does not yet prove that these 285 claims exhaust every Physics-owned atomic obligation in V1/V2: the required one-owner decomposition of that complete source surface remains open and blocks publication. Candidate grammars range across {len(cardinalities)} exact cardinalities ({', '.join(f'{count} claims at {cardinality:,}' for cardinality, count in sorted(cardinalities.items()))}); the paper no longer misstates every derivation as one 256-form template. The current derivation ledger includes the generator-three law, three-dimensional stability, boundary rank two, inverse-square dilution, the exact inverse fine-structure result and CODATA comparison, physical constants and scale relations, vacuum and extraction boundaries, force sectors, relativistic and quantum correspondence, matter and flavour, atomic and molecular precision, nuclear and hadronic structure, gravitation, collective dynamics and the universal Physics-to-Cosmology boundary. Every included claim is traced to its root dependency chain, complete generated grammar, unique survivor, controls, independent reconstruction, external comparison where registered, and immutable engine receipt.

## 1. Publication and authorship boundary

{publication_boundary}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Submissions and reproducibility reports: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

The paper is prepared for CC BY 4.0 distribution; the engine code remains under the repository's Apache-2.0 license. Copyright preserves authorship while the licenses preserve open inspection, reuse and independent criticism. Use of the Ernos Labs designation requires adherence to the published empirical and community standards.

## 2. Results first: what this Physics reconstruction claims

The current categorical inventory contains {len(obligations)} Physics claims in {len(inventory['subbranch_order'])} ordered subbranches. All {len(obligations)} have immutable model-admitted receipts. This corrected scope replaces a faulty bookkeeping ledger that bulk-labelled cross-disciplinary V1/V2 observations as Physics. No Chemistry, Materials, Biology, Consciousness, astronomical-history or application claim is counted here. The correction changes publication organization, not a derivation, receipt or engine decision.

**Publication blocker.** The global V1/V2 ownership constitution is not complete, so the corpus cannot yet certify that every Physics-owned atomic obligation has entered this inventory. The 285-claim coverage proof is exact for the live categorical V3 census only. It must not be represented as exhaustive V1/V2 Physics reconstruction until the one-owner audit closes with zero Physics-owned omissions.

{headline_table}

These are not detached assertions. Their full sections below expose the exact theorem statement, dependencies, candidate generator, cardinality, survivor, axis-level uniqueness witnesses, base/successor or finite-boundary certificate, adverse controls, independent implementation, empirical custody record and receipt hashes.

Physics closure means that every claim in the current categorical Physics inventory has passed the common admission standard at its declared generated and empirical boundary. It does not reassign downstream chemical consequences, materials properties, organisms, consciousness, observed astronomical populations or cosmic history to Physics.

Even after the V1/V2 ownership audit closes, branch closure will mean current-knowledge closure at a dated evidence boundary—not permanent completion of Physics. New discoveries, falsifications, corrections and stronger evidence remain lawful extensions when submitted as new versioned claims through the unchanged engine. Existing receipts remain immutable.

## 3. Exact constitutional domain

The derivational domain admits the empty One as structural absence but never numerical zero. Proof magnitudes are positive generated counts and exact positive rational parts or ratios. Orientation, opposition and complement are held labels rather than negative quantities. Irrational, imaginary and binary floating values are barred from proof. Completed infinity, an ungenerated continuum, axioms, fitted coefficients and free parameters are also barred. External decimal measurements remain source-bound records. A finite decimal is converted to an exact rational interval only inside the empirical adapter and never gains authority to select the Fold law.

## 4. The single admission engine

Each claim entered the same `SFTAdmissionEngine`. Registration rejects axioms, free parameters, missing root trace, unadmitted dependencies and source-identity failure before candidate execution. The engine then checks census cardinality and identity, one decision per candidate, exactly one survivor, minimality, named-shape uniqueness, the four mandatory controls, an implementation-distinct external reconstruction and, for empirical claims, prediction isolation, target custody, complete rows and falsification. A failure halts without model admission. Accepted receipts are immutable evidence identities. The engine source is not edited by this publication correction, and the paper cannot confer admission.

## 5. Why superdeterminism permits uncertainty and quantum weights

No law in this branch installs ontic nondeterminism. The complete Fold state includes preparation, held labels, measurement setting, path and observation record. A probabilistic or quantum weight is an exact census ratio over unresolved support. Each branch execution remains deterministic. Measurement uncertainty records distinctions unavailable to an observation class; it does not assert causeless state selection. Bell correspondence therefore retains setting and preparation records in the complete state, identifies the factorization assumption that fails, and separately preserves the no-signalling marginal through complete remote-fibre enumeration.

## 6. Empirical constitution

External evidence follows one direction. First the Fold dependencies generate and eliminate candidate laws. Then a data-only Fold program receives only registered inputs and the sealed derivation identity. Its instruction set has no filesystem, network, subprocess, clock, environment, dynamic import or foreign-function capability. A distinct custodian commits target identity before execution and releases content only to the matching prediction seal. The evaluator preserves every registered row and must reject a deliberately altered or displaced control. BIPM, NIST/CODATA, NIST ASD, PDG, IAEA, IAPWS, GWOSC, CERN Open Data and NASA LAMBDA supply the external records.

## 7. Exact measured-value correspondence

Measured-value forcing means that a zero-parameter Fold relation produces a sealed consequence and a registered exact adapter compares it with withheld observation. The observation is evidence, not a tunable parameter: it cannot enter candidate generation, choose a survivor or add a correction. Finite decimals and uncertainties are parsed as exact positive fractions. Multiplication and quotient propagate interval endpoints in the capability-closed interpreter; target overlap is evaluated only after release. Exact official decimal prefixes with ellipses are bounded by their next decimal place. Any non-overlap halts admission.

The inverse fine-structure result belongs here, in Physics: `SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001` forces the terminal exact ratio and `SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001` performs its sealed CODATA comparison. The same rule applies to every constant, scale and precision claim in the inventory. They are listed here rather than hidden in a later Chemistry narrative:

{value_table}

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

At the declared boundary, the current 285-claim V3 Physics inventory is internally evidence-closed, while publication and exhaustive V1/V2 closure remain blocked by the one-owner audit. Its {len(obligations)} derivations are forced, enumerated, independently reconstructed and admitted through one unchanged engine; {empirical_count} additionally carry registered empirical validation. When the broader audit closes, that status will still be current-knowledge closure rather than permanent completion: Physics remains open to lawful versioned extension and falsification. The measured-value layer preserves the strict arithmetic constitution while allowing official observations to invalidate a sealed relation. The result is an open, inspectable tree of physical laws whose authority rests on reproducible traces rather than credentials, institutional permission, opaque prediction or consensus selection. Open science is not ornamental here: every authority claim is made vulnerable to computational reproduction, adverse control and public falsification.

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
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} categorical Physics claim sections")


if __name__ == "__main__":
    main()
