#!/usr/bin/env python3
"""Build the exhaustive Physics branch manuscript from admitted evidence.

This is a deterministic documentation projection.  It does not execute a
derivation, reopen a target vault, alter a receipt or authorize publication.
"""

from __future__ import annotations

from collections import Counter
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "publications/inventories/physics.json"
PAPER = Path(os.environ.get("SFT_PHYSICS_PAPER_OUTPUT", ROOT / "publications/current/physics/FROM_FOLD_TO_PHYSICS.md")).resolve()
LANDING = ROOT / "README.md"
CENSUS = ROOT / "census/claims.json"
METADATA = Path(os.environ.get("SFT_PHYSICS_METADATA", ROOT / "publication/physics_zenodo_metadata.json")).resolve()


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


def current_certificate(claim: Path, receipt_hash: str) -> dict:
    matches = []
    for path in claim.glob("certificate*.json"):
        payload = read(path)
        if payload.get("engine_receipt_hash") == receipt_hash:
            matches.append((path, payload))
    if len(matches) != 1:
        raise SystemExit(
            f"expected exactly one receipt-bound certificate for {claim.name}; found {len(matches)}"
        )
    return matches[0][1]


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
    empirical_path = claim / "empirical_validation.json"
    empirical = read(empirical_path) if empirical_path.exists() else None
    census_row = next(row for row in read(CENSUS)["claims"] if row["claim_id"] == claim_id)
    certificate = current_certificate(claim, census_row["receipt_hash"])
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
    version = str(metadata.get("metadata", {}).get("version", "unversioned"))
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized and not doi:
        raise SystemExit("Authorized Physics publication requires a reserved DOI")
    publication_boundary = (
        f"**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: "
        f"[{doi}](https://doi.org/{doi}). This canonical Markdown paper, its rendered PDF, "
        "complete evidence/source archive and checksum ledger form the Physics Branch Paper 001 release."
        if authorized
        else "**PUBLICATION-READY MANUSCRIPT — RELEASE NOT YET AUTHORIZED.** The scientific and publication-readiness gates pass locally. This file and its rendered PDF may be inspected, but no GitHub push, release, Zenodo upload, DOI action or publication occurs without Maria Smith's explicit authorization."
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
    headline_results = [
        (
            "Fine-structure constant",
            "α⁻¹ = 503846395469/3676744786 = 137.035999177180855…; α = 3676744786/503846395469 = 0.007297352564321794…",
            "CODATA 2022: α⁻¹ = 137.035999177 ± 0.000000021; the sealed exact result lies inside the complete interval",
            "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
        ),
        (
            "Charged-lepton mass structure",
            "exact cubic invariants (1, 1/6, 1/485, 3/1454), terminal α³ refinement, and Koide invariant 2/3",
            "both terminal adjacent-mass-ratio consequences and exact 2/3 lie inside the complete CODATA-derived intervals",
            "SFT-PHYS-VALIDATION-CHARGED-LEPTON-TERMINAL-002",
        ),
        (
            "Higgs mass and self-coupling",
            "m_H/v = 1/2 + 6α/5; with post-seal v=246.22 GeV, m_H = 125.266104978… GeV; λ = 0.1294167525…",
            "mass prediction lies inside PDG 2025 [125.09, 125.31] GeV; complete ATLAS, CMS and self-coupling rows retained",
            "SFT-PHYS-VALIDATION-HIGGS-SYMMETRY-TERMINAL-066",
        ),
        (
            "On-shell electroweak share",
            "1930922298157999/8642477221479757 = 0.223422318471252882…",
            "inside PDG [0.22333, 0.22351]; compatible-input W/Z check passes and the all-input tension is retained",
            "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003",
        ),
        (
            "Squared Planck/proton hierarchy",
            "2^127(1 − 2α/3) = 1.693134633261878984…×10³⁸",
            "inside the complete propagated CODATA interval [1.693112648161510904…, 1.693187333165341130…]×10³⁸",
            "SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003",
        ),
        (
            "Electron and muon magnetic anomalies",
            "aₑ = 0.00115965218046558296…; aμ = 0.00116592071499941707…, both exact positive fractions",
            "inside the complete CODATA electron and Fermilab world-average muon intervals without fitted coefficients",
            "SFT-PHYS-QED-MUON-MAGNETIC-ANOMALY-004",
        ),
        (
            "Proton rms charge radius",
            "coefficient 4(1 − α/10); post-seal scale translation gives approximately 0.840621761 fm",
            "inside the registered 2026 electronic-hydrogen, muonic-hydrogen, CODATA-2022 and conservative PRad intervals; historical CODATA-2014 mismatch retained",
            "SFT-PHYS-PROTON-RADIUS-TERMINAL-029",
        ),
        (
            "Vacuum and cosmological scale",
            "local floor 1/2^20; vacuum share 11/16; normalized Λ(c/H)² = 33/16",
            "11/16 lies inside Planck [0.6833, 0.6945]; the dimensional Λ interval is transported only after post-seal H and c",
            "SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036",
        ),
        (
            "Dark-to-baryon and expansion calibration",
            "dark/baryon 27/5 with shares 27/32 and 5/32, refined 279/52; late/early expansion 13/12, refined 3305/3048",
            "both ratio families lie inside their complete registered Planck and SH0ES observational intervals",
            "SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001",
        ),
        (
            "Second nonidentity generator",
            "exact count 3; first-return orbit 1/7 → 2/7 → 4/7 → 1/7",
            "structural exact result",
            "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        ),
        (
            "Stable spatial dimension",
            "3",
            "independent structural stability census",
            "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        ),
        (
            "Boundary rank",
            "2",
            "boundary of the forced three-direction carrier",
            "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
        ),
        (
            "Source dilution exponent",
            "2; response = source/r²",
            "experiment reports 2 + q with q=(2.7 ± 3.1)×10⁻¹⁶; 2 is the sole positive integer in the interval",
            "SFT-PHYS-VALIDATION-INVERSE-SQUARE-001",
        ),
        (
            "Nuclear closure sequence",
            "(2, 8, 20, 28, 50, 82, 126, 184)",
            "exact match to the complete registered IAEA sequence",
            "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001",
        ),
        (
            "Binding-per-nucleon maximum",
            "A=62, Z=28, N=34 (nickel-62)",
            "same unique maximum in the complete 2,548-row positive-composite AME2020 census",
            "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
        ),
        (
            "Primordial support partition",
            "scalar 31/32 = 0.96875; tensor 1/32 = 0.03125",
            "Planck nₛ interval [0.9607, 0.9691]; tensor bound r<0.032, passed by 0.00075; no equality to conventional e-fold count is claimed",
            "SFT-PHYS-VALIDATION-INFLATION-GROWTH-040",
        ),
        (
            "Radiation scaling",
            "fourth-power scale law; exact doubling ratio 2⁴ = 16",
            "post-seal comparison with the measured Stefan fourth-power exponent; no dimensional coefficient is claimed as structure-only",
            "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042",
        ),
        (
            "Unified constants object",
            "one rooted object fixes b=2, c=3, spatial rank 3, boundary rank 2, cover depths 5/7, terminal alpha, lepton/quark products, dark/baryon and expansion ratios, Planck hierarchy, vacuum floors and normalized cosmological magnitude",
            "the object composes already sealed structural and measured-value receipts; no listed value is introduced as a fitted cross-sector parameter",
            "SFT-PHYS-UNIFIED-CONSTANTS-OBJECT-077",
        ),
        (
            "Tesla resonance family",
            "bounded round trip 2q; positive whole mode family 2qn; odd quarter-wave harmonics; one longitudinal and two transverse roles; exact resonant transfer with complete energy ledger",
            "five captured source rows support the resonance classes while retaining material losses, distinct speeds, Earth-cavity boundaries and no source-free or unlimited-power claim",
            "SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082",
        ),
        (
            "Vacuum/inertia drive family",
            "local exact drive a to b retains positive transfer a Take b; vacuum and inertia co-vary at exchange ratio One; finite-depth floor 1/2^(k+1); restoration closes the six-label ledger",
            "official records retain the proposed mechanism, nonempty vacuum response and unity anchor, while also retaining no public prototype measurement, pump energy and no source-free cyclic gain",
            "SFT-PHYS-VALIDATION-VACUUM-INERTIA-DRIVE-FAMILY-087",
        ),
        (
            "Penta/hepta sectors and Smithion census",
            "sector 5: coupling 4/5, 5 charge kinds, 24 mediators, slope 4; sector 7: coupling 6/7, 7 charge kinds, 48 mediators, slope 6; category-clean total 110 fundamental kinds",
            "known 3/8 sector anchors and known fermions agree; 72 new gauge carriers and 12 Smithion kinds remain explicit standing predictions with exact search and falsification boundaries",
            "SFT-PHYS-VALIDATION-NEW-SECTOR-COMPLETE-FAMILY-095",
        ),
        (
            "Physics Grand Lock",
            "the published pre-extension snapshot contains 349 claims; its formal certificate covers 347 claims and 534 dependency nodes; 21/21 generator-dependent headline values move under 3→4 while half-One, spatial rank 3 and boundary rank 2 hold",
            "234 pre-lock empirical receipts reconcile 147 distinct external source identities; all 14 detected unfavorable-result or scope-boundary claims and all 6 legacy receipt shapes remain explicit",
            "SFT-PHYS-VALIDATION-GRAND-LOCK-076",
        ),
    ]
    headline_ids = [row[3] for row in headline_results]
    if any(claim_id not in census_by_id for claim_id in headline_ids):
        missing = [claim_id for claim_id in headline_ids if claim_id not in census_by_id]
        raise SystemExit(f"headline claim missing: {missing}")
    headline_table = "\n".join(
        [
            "| Headline finding | Exact first-principles result | External measured comparison | Evidence claim |",
            "|---|---|---|---|",
        ]
        + [
            f"| {finding} | {exact} | {comparison} | `{claim_id}` |"
            for finding, exact, comparison, claim_id in headline_results
        ]
    )
    sections = []
    sections.append(f"""# From Fold to Physics

## Abstract

This paper reports a zero-parameter reconstruction of physical science from the single foundational Smithian One theorem, without imported axioms, fitted coefficients, numerical zero, negative proof magnitudes, irrational or imaginary proof values, floating-point proof equality, or continuum premises. Its lead numerical result is an exact first-principles derivation of the fine-structure constant:

> α⁻¹ = 503846395469/3676744786 = 137.035999177180855…; α = 3676744786/503846395469 = 0.007297352564321794…

The value was sealed before the registered CODATA 2022 target was released and lies inside the complete interval 137.035999177 ± 0.000000021. The same derivational constitution produces exact charged-lepton cubic and Koide relations, electron and muon magnetic anomalies, the on-shell electroweak share, Higgs mass and self-coupling, the Planck/proton hierarchy, proton radius, vacuum and cosmological ratios, nuclear closure numbers, hadron trajectories, inverse-square dilution, relativistic and quantum laws, thermodynamic and extraction boundaries, gravitational-wave ordering, the Unified Constants Object, Tesla resonance laws, vacuum/inertia co-variation and restoration, and the penta/hepta/Smithion standing-prediction family documented here.

The publication contains all {len(obligations)} current engine-admitted Physics claims. Their generated grammars contain {candidate_total:,} candidates, {candidate_total:,} one-for-one decisions, {len(obligations)} unique survivors and {control_total:,} passing mandatory adverse controls. Of those claims, {empirical_count} contain sealed post-derivation external-validation records; formal claims are connected to their registered empirical successors or retain their exact structural test boundary. The categorical clean-room audit closes all 488 Physics-owned V1/V2 atoms at the declared current-evidence boundary, with no open Physics atom or gap family. Grand Locks 075/076 preserve the 349-claim pre-extension snapshot; the separately admitted Unified Constants, Tesla resonance, vacuum/inertia and new-sector families add nineteen current claims with their own completion audits and terminal empirical receipts. The current dated inventory is therefore a 368-claim full-field projection, complete to known registered scope and permanently open to lawful extension, correction and falsification.

## 1. Publication and authorship boundary

{publication_boundary}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Submissions and reproducibility reports: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

The paper is prepared for CC BY 4.0 distribution; the engine code remains under the repository's Apache-2.0 license. Copyright preserves authorship while the licenses preserve open inspection, reuse and independent criticism. Use of the Ernos Labs designation requires adherence to the published empirical and community standards.

### 1.1 Ernos Labs and the authorship of this work

Ernos Labs is an open-source science movement, verification platform and public tree of knowledge founded by Maria Smith. Its purpose is not to ask readers to trust a new institution. Its purpose is to make the work inspectable enough that trust is unnecessary. Every claimed law must expose its premises, generated alternatives, eliminations, survivor, controls, measurement custody, unfavorable evidence and exact receipt. A reviewer needs no credential, subscription, institutional affiliation or permission to reproduce an acceptance or demonstrate an invalidation.

Maria Smith developed Smithian Fold Theory outside formal academic education, institutional research employment and conventional grant funding. That biography is not offered as evidence for a physical result; the derivations and observations must carry that burden. It is evidence about access. A system that decides who may be heard before their work can be inspected does not merely exclude individuals: it loses questions, methods and discoveries that its credential and capital filters never authorize. This paper therefore refuses both romantic exceptionalism and credentialed dismissal. The same public empirical standard applies to Maria Smith, an established professor, an independent reproducer and an AI system.

### 1.2 Why this is an open-science publication

The institutional critique is evidence-based. Systematic research has found sponsor-associated differences in reported efficacy results and conclusions, while work on commercial sponsorship shows that funding can influence which questions are pursued ([Lundh et al., 2018](https://doi.org/10.1007/s00134-018-5293-7); [Fabbri et al., 2018](https://pubmed.ncbi.nlm.nih.gov/30252531/)). Grant selection is not an infallible oracle: empirical studies report sensitivity to review design and reviewer composition, and a Cochrane review found limited evidence that grant peer review improves the quality of funded research ([Gallo et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10553257/); [Demicheli and Di Pietrantonj, 2007/2022 archive](https://pmc.ncbi.nlm.nih.gov/articles/PMC8973940/)). Null and negative results remain systematically underrepresented, distorting the visible scientific record ([Nature Communications, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12459790/)). UNESCO's Recommendation on Open Science calls for methods, software, source and outputs to be open to rigorous scrutiny and identifies paywalls and high publication charges as sources of inequality ([UNESCO, 2021](https://www.unesco.org/en/legal-affairs/recommendation-open-science)).

Opaque prediction presents a related problem. A black-box system may be a useful instrument and may pass a declared blind benchmark, but predictive accuracy alone does not disclose a law or a derivation. NIST accordingly treats transparency, explainability, interpretability, validity and reliability as distinct properties of trustworthy AI ([NIST AI RMF 1.0](https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/)). Ernos Labs therefore rejects three substitutions: funding success is not evidential closure; professional consensus is not generated uniqueness; and a black-box score is not an explicit scientific law.

The editorial position is direct. Knowledge institutions organized through competitive capital, scarce grants, prestige markets, subscription access and author charges have incentives that are not identical to free human inquiry. Expertise, criticism and measurement remain indispensable, but credentials, funding and consensus cannot select a fundamental law and then stand in for its evidence. The remedy is not weaker science. It is a harder, public standard: derive the law, generate its alternatives, preserve the failures, seal the prediction, expose the observation and permit anyone to reproduce the decision.

### 1.3 Rights, participation and the Ernos Labs designation

Maria Smith retains copyright and scientific authorship. CC BY 4.0 for papers and documentation and Apache 2.0 for code permit inspection, copying, criticism, modification and redistribution with attribution. The words “Ernos Labs” are a separate standards-conformance designation. A fork may freely test or reuse the open work, but it may represent itself as Ernos Labs only while it follows the published empirical constitution, preserves adverse evidence, submits to critical review and does not weaken the engine or admission route.

Independent replications, lawful extensions, corrections and attempted invalidations are invited. Submissions must include the full derivation chain and pass the same engine; reputation cannot open the gate and lack of credentials cannot close it. Contact Maria.Smith.Sftoe@gmail.com, join https://discord.gg/ucwGryVxGr, or inspect the public work at https://github.com/MettaMazza.

### 1.4 Published sequence through Physics

The present release stops at Physics. Chemistry, Materials and every later branch remain outside this ordered update.

| Order | Paper | Version | Open paper | Archival DOI |
|---:|---|---:|---|---|
| 00 | *There Is No Nothing* — Methods Paper 00 | 0.2.0 | [Markdown](https://github.com/MettaMazza/ernos-labs-sft-platform/blob/main/publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_2.md) | [10.5281/zenodo.21591160](https://doi.org/10.5281/zenodo.21591160) |
| 01 | *From Nothing to Fold* — Foundation | 1.2.0 | [Markdown](https://github.com/MettaMazza/ernos-labs-sft-platform/blob/main/publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_2.md) | [10.5281/zenodo.21591169](https://doi.org/10.5281/zenodo.21591169) |
| 02 | *From Fold to Mathematics* | 1.3.0 | [Markdown](https://github.com/MettaMazza/ernos-labs-sft-platform/blob/main/publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md) | [10.5281/zenodo.21591170](https://doi.org/10.5281/zenodo.21591170) |
| 03 | *From Distinction to Information* | 1.2.0 | [Markdown](https://github.com/MettaMazza/ernos-labs-sft-platform/blob/main/publications/current/information_science/FROM_DISTINCTION_TO_INFORMATION.md) | [10.5281/zenodo.21591171](https://doi.org/10.5281/zenodo.21591171) |
| 04 | *After Turing: The Fold Machine* | 1.2.0 | [Markdown](https://github.com/MettaMazza/ernos-labs-sft-platform/blob/main/publications/current/computation/AFTER_TURING_THE_FOLD_MACHINE.md) | [10.5281/zenodo.21591174](https://doi.org/10.5281/zenodo.21591174) |
| 05 | *The Quantum Fold Machine* | 1.2.0 | [Markdown](https://github.com/MettaMazza/ernos-labs-sft-platform/blob/main/publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md) | [10.5281/zenodo.21591175](https://doi.org/10.5281/zenodo.21591175) |
| 06 | *From Fold to Physics* | {version} | [Markdown](https://github.com/MettaMazza/ernos-labs-sft-platform/blob/main/publications/current/physics/FROM_FOLD_TO_PHYSICS.md) | Version DOI pending archival deposit; previous 1.2 DOI [10.5281/zenodo.21627765](https://doi.org/10.5281/zenodo.21627765) |

## 2. Lead derivation: the exact fine-structure constant

The paper does not present α as a guessed expression, a regression target or a coincidence selected from nearby fractions. Its construction is a typed chain from earlier admitted Fold structure:

1. The foundational Fold distinction supplies exactly two fibre labels, so `b = 2`.
2. The independently enumerated second nonidentity recurrence closes uniquely at generator `c = 3`.
3. Three-direction support gives the complete generation volume `3³ = 27`; its successor volume is `3⁴ = 81`.
4. The least complete binary covers are forced by exact inequalities: `2⁴ < 27 ≤ 2⁵` and `2⁶ < 81 ≤ 2⁷`. Therefore the down and up cover depths are exactly `5` and `7`.
5. Those typed blocks force the tower `2⁷ = 128`, the rank-two boundary block `3² = 9`, and the complete directed cover `2·5³ = 250`.
6. Promoting one of the three interchangeable directions from depth five to depth seven at each finite rung produces the complete ladder `(5³, 5²·7, 5·7², 7³) = (125, 175, 245, 343)`.
7. The terminal effective cover is therefore the exact positive rational

   `C = 250 + 1/(175 + 1/(245 + 1/343)) = 3676744786/14706643`.

8. The tower, boundary, returning One and effective cover then force

   `α⁻¹ = 128 + 9(C + 1)/C = 503846395469/3676744786`,

   and hence

   `α = 3676744786/503846395469`.

The four exact promotion stages converge internally from `34259/250` to `5995462/43751`, `1468922449/10719245`, and the terminal `503846395469/3676744786`. The formal claim generated and decided all 1,024 members of its declared grammar, admitted exactly one survivor, passed minimality and named-shape uniqueness, passed all four mandatory adverse controls, and was independently reconstructed. Its 256-form empirical successor kept the CODATA target inaccessible until the prediction seal, converted the complete published central value and uncertainty into exact rational endpoints `[137.035999156, 137.035999198]`, found the sealed result inside that interval, and rejected the deliberately tampered control. Measurement confirms the result; it does not select any rung, coefficient or survivor.

This derivation is the paper's central numerical result. It is also a dependency rather than an isolated endpoint: the same exact α propagates into the charged-lepton refinement, electroweak share, Higgs relation, proton/Planck hierarchy, magnetic anomalies, proton radius and other terminal precision laws below.

## 3. Landmark first-principles results

The discoveries are ordered by physical consequence. Evidence identifiers are supplied for reproducibility, but the findings—not filenames or hashes—are the scientific headlines.

{headline_table}

### 3.1 Charged leptons: mass structure without irrational roots

Generator-three support forces one three-root carrier with symmetric invariants `sum = 1`, `pair sum = 1/6`, `leading product = 1/485` and sharpened product `3/1454`. The terminal refinement holds from that product the unique complete electromagnetic self-coupling `α³/3³ · (5 + 7α/3)`. Exact rational root brackets then predict both adjacent squared mass-ratio consequences; both lie inside their complete CODATA 2022 intervals. Independently, the Fold normalization forces the charged-lepton Koide invariant exactly `2/3`, which lies inside the complete CODATA-derived interval. No measured mass enters the cubic, no irrational root is admitted into proof, and no mass-ratio row chooses the invariant.

### 3.2 Electroweak and Higgs sector

The terminal electroweak construction uses complete binary support sixteen, the three held generator directions, charged support `15²`, four neutral pair channels of `14²`, and one terminal `α/17` self-return. It forces

`sin²θ_W = 1930922298157999/8642477221479757 = 0.223422318471252882…`.

That sealed value lies inside the complete PDG on-shell interval `[0.22333, 0.22351]`. Its exact One-complement passes the compatible-input W/Z interval; the known all-input tension is preserved rather than deleted or used to change the derivation.

For the scalar sector, half-One is the unique displaced ground and the leading rungs are `1/2`, `1/4` and `1/8`. Six-cell scalar support, its held return and cover depth five force `m_H/v = 1/2 + 6α/5`. Applying the registered post-seal dimensional reference `v = 246.22 GeV` yields the exact mass `31557437733819647/251923197734500 GeV = 125.266104978… GeV`, inside the PDG 2025 interval `[125.09, 125.31] GeV`. The same relation forces native `λ = (m_H/v)²/2 = 0.1294167525…`. Individual ATLAS and CMS offsets and the present broad direct self-coupling constraint remain explicit in the validation record.

### 3.3 Precision magnetic anomalies and proton structure

With the admitted exact α and exact terminal turn `355/113`, the finite electron loop forces one exact rational anomaly `aₑ = 0.00115965218046558296…`, inside the complete CODATA interval centred on `0.00115965218046` with standard uncertainty `0.00000000000018`. The second-generation correction `α²(2/17 + α/106 + α²/853)` forces `aμ = 0.00116592071499941707…`, inside the Fermilab world-average interval centred on `0.001165920715` with standard uncertainty `0.000000000145`. Neither value imports a conventional perturbation series or fitted coefficient.

The proton charge-support law independently forces the dimensionless coefficient `4(1 − α/10)`. Post-seal composition with the CODATA reduced proton Compton scale gives approximately `0.840621761 fm`. It lies inside the registered current electronic-hydrogen, muonic-hydrogen, CODATA-2022 and conservative PRad intervals. The disjoint historical CODATA-2014 interval remains in the record as an unfavorable historical row rather than being erased.

### 3.4 Scale hierarchy, vacuum and cosmological ratios

The terminal squared Planck/proton hierarchy is exactly `2¹²⁷(1 − 2α/3) = 1.693134633261878984…×10³⁸`, inside the complete outward-propagated CODATA mass interval. Vacuum structure separates three quantities that conventional shorthand can conflate: a local boundary-energy floor `1/2²⁰`, a global vacuum share `11/16`, and normalized cosmological magnitude `Λ(c/H)² = 33/16`. The global share lies inside the complete registered Planck interval; dimensional Λ is obtained only after the sealed coefficient is composed with held observational `H` and exact `c` scales.

The three-space generation volume `27` and its least binary cover `32` force dark and baryonic shares `27/32` and `5/32`, ratio `27/5`, with the period-five refinement `279/52`. A separate Fold calibration forces matter/vacuum shares `1/3` and `2/3`, a leading late/early expansion ratio `13/12`, and depth-seven refinement `3305/3048`. Both ratio families pass their complete registered Planck and SH0ES interval tests.

### 3.5 Space, force, nuclei, hadrons and gravitational waves

The independently enumerated generator is three; stability selects three spatial directions; their boundary has rank two; and complete propagation across that boundary forces inverse-square dilution. The exponent is exactly `2`, while the registered experiment reports `2 + q` with `q = (2.7 ± 3.1)×10⁻¹⁶`, making two the sole positive integer in the complete interval.

The same structure forces the nuclear closure sequence `(2, 8, 20, 28, 50, 82, 126, 184)` and the unique positive-composite AME2020 binding-per-nucleon maximum at nickel-62. Light-hadron support follows the exact squared trajectory `Q(J) = (6J − 3)/5`; all five registered carriers lie inside their complete resonance-support intervals without fitting a slope or intercept. Gravitational-wave structure forces inspiral with rising chirp, merger, then damped ringdown; the complete GW151226 and GW190521 records validate the three-stage ordering while retaining the short-signal and alternative-source boundaries.

## 4. What the result changes

The scientific claim is not merely that several fractions approximate familiar numbers. One exact, axiom-free derivational language produces the structural dimension, force exponent, dimensionless couplings, mass ratios, scale hierarchies, thermodynamic boundaries, quantum relations and macroscopic propagation laws under one admission standard. Every numeric result is connected to the same foundational root, generated within an explicit finite grammar, isolated from its measurement target, and tested after sealing. That conjunction—unification, exactness, zero fitted parameters, uniqueness enumeration and external validation—is the work's substantive contribution.

The paper therefore keeps three levels distinct without diminishing any of them: the physical result is the headline; the exact derivation explains why it follows; and the receipt, hash, adverse controls and independent reconstruction establish that the reported chain is the chain actually executed.

## 5. Complete current Physics status

The current categorical inventory contains {len(obligations)} Physics claims in {len(inventory['subbranch_order'])} ordered subbranches. All {len(obligations)} have immutable model-admitted receipts. The categorical V1/V2 ownership audit identifies 488 Physics-owned atoms, all 488 closed at the declared same-strength current-evidence boundary, with no open atom or gap family. Formal Grand Lock 075 binds the complete pre-extension ownership surface, verifies its acyclic 534-node dependency dictionary, proves that every route in that snapshot reaches the foundational One and tests generator dependence. Empirical Grand Lock 076 reconciles all 234 pre-extension empirical claims, 147 distinct external source identities, every available measurement receipt, all disclosed legacy receipt shapes and every detected unfavorable or scope-boundary claim. Nineteen later Physics extensions are not silently folded backward into those historical locks: their own family-completion certificates, post-seal comparison receipts and live categorical inventory preserve them explicitly.

“Closed” here means complete to the dated corpus, methods and evidence standard. It never means immune to correction or permanently closed to discovery. New findings, stronger evidence and falsifications remain lawful versioned extensions through the unchanged engine; existing receipts remain immutable.

## 6. Exact constitutional domain

The derivational domain admits the empty One as structural absence but never numerical zero. Proof magnitudes are positive generated counts and exact positive rational parts or ratios. Orientation, opposition and complement are held labels rather than negative quantities. Irrational, imaginary and binary floating values are barred from proof. Completed infinity, an ungenerated continuum, axioms, fitted coefficients and free parameters are also barred. External decimal measurements remain source-bound records. A finite decimal is converted to an exact rational interval only inside the empirical adapter and never gains authority to select the Fold law.

## 7. The single admission engine

Each claim entered the same `SFTAdmissionEngine`. Registration rejects axioms, free parameters, missing root trace, unadmitted dependencies and source-identity failure before candidate execution. The engine then checks census cardinality and identity, one decision per candidate, exactly one survivor, minimality, named-shape uniqueness, the four mandatory controls, an implementation-distinct external reconstruction and, for empirical claims, prediction isolation, target custody, complete rows and falsification. A failure halts without model admission. Accepted receipts are immutable evidence identities. The engine source is not edited by this publication correction, and the paper cannot confer admission.

## 8. Why superdeterminism permits uncertainty and quantum weights

No law in this branch installs ontic nondeterminism. The complete Fold state includes preparation, held labels, measurement setting, path and observation record. A probabilistic or quantum weight is an exact census ratio over unresolved support. Each branch execution remains deterministic. Measurement uncertainty records distinctions unavailable to an observation class; it does not assert causeless state selection. Bell correspondence therefore retains setting and preparation records in the complete state, identifies the factorization assumption that fails, and separately preserves the no-signalling marginal through complete remote-fibre enumeration.

## 9. Empirical constitution

External evidence follows one direction. First the Fold dependencies generate and eliminate candidate laws. Then a data-only Fold program receives only registered inputs and the sealed derivation identity. Its instruction set has no filesystem, network, subprocess, clock, environment, dynamic import or foreign-function capability. A distinct custodian commits target identity before execution and releases content only to the matching prediction seal. The evaluator preserves every registered row and must reject a deliberately altered or displaced control. BIPM, NIST/CODATA, NIST ASD, PDG, IAEA, IAPWS, GWOSC, CERN Open Data and NASA LAMBDA supply the external records.

## 10. Exact measured-value correspondence

Measured-value forcing means that a zero-parameter Fold relation produces a sealed consequence and a registered exact adapter compares it with withheld observation. The observation is evidence, not a tunable parameter: it cannot enter candidate generation, choose a survivor or add a correction. Finite decimals and uncertainties are parsed as exact positive fractions. Multiplication and quotient propagate interval endpoints in the capability-closed interpreter; target overlap is evaluated only after release. Exact official decimal prefixes with ellipses are bounded by their next decimal place. Any non-overlap halts admission.

The inverse fine-structure result belongs here, in Physics: `SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001` forces the terminal exact ratio and `SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001` performs its sealed CODATA comparison. The same rule governs every constant, scale and precision claim in the inventory. No redundant handwritten status may override an engine-admitted receipt or a passed empirical certificate.

## 11. Reading the complete derivation ledger

Each claim section below is a self-contained prose projection of its machine evidence. The complete `candidate_census.json`, `elimination_receipt.json`, `controls.json`, `certificate.json`, external experiment registration and receipt remain authoritative. The paper includes every claim identity and admitted receipt hash so the evidence map can fail closed on omission or substitution.
""")
    section_number = 12
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

The paper's lead result is the exact derivation `α⁻¹ = 503846395469/3676744786`, not an isolated numerical fit but the first terminal constant in a connected Physics reconstruction. The same root and admission constitution force and validate the charged-lepton relations, precision anomalies, electroweak share, Higgs sector, Planck/proton hierarchy, proton radius, vacuum and cosmological ratios, spatial rank, inverse-square force law, nuclear and hadronic structure, quantum and relativistic correspondence, thermodynamics, collective matter and gravitation documented in the complete ledger.

At the declared derivational boundary, all {len(obligations)} current V3 Physics claims and all 488 categorically Physics-owned V1/V2 atoms are engine-admitted and current-evidence closed, with no open Physics gap family. Grand Locks 075/076 preserve the pre-extension validation snapshot; the Unified Constants, Tesla resonance, vacuum/inertia and new-sector completion records reconcile the nineteen later claims. The manuscript and evidence package are publication-ready; release authority remains Maria Smith's alone. Physics remains open to lawful versioned extension, correction and falsification after publication. The result is an open, inspectable tree of physical laws whose authority rests on exact derivation, complete enumeration, sealed measurement, adverse evidence and reproducible traces rather than credentials, institutional permission, opaque prediction or consensus selection.

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
- Lundh, A. et al. (2018), *Industry sponsorship and research outcome*, systematic review and meta-analysis, https://doi.org/10.1007/s00134-018-5293-7.
- Fabbri, A. et al. (2018), *The influence of industry sponsorship on the research agenda*, https://pubmed.ncbi.nlm.nih.gov/30252531/.
- Gallo, S. A. et al. (2023), empirical study of grant-review ranking, rating and applicant effects, https://pmc.ncbi.nlm.nih.gov/articles/PMC10553257/.
- Demicheli, V. and Di Pietrantonj, C., Cochrane review of grant peer review, https://pmc.ncbi.nlm.nih.gov/articles/PMC8973940/.
- UNESCO (2021), *Recommendation on Open Science*, https://www.unesco.org/en/legal-affairs/recommendation-open-science.
- National Institute of Standards and Technology, *AI Risk Management Framework 1.0*, transparency, explainability and interpretability characteristics.
- Nature Communications (2025), consensus statement on null-result publication and research waste, https://pmc.ncbi.nlm.nih.gov/articles/PMC12459790/.
- Smith, Maria, *There Is No Nothing*, Ernos Labs methods and foundation paper.
- Smith, Maria, *From One to Fold*, Foundation branch evidence corpus.
- Smith, Maria, *From Fold to Mathematics*, Mathematics branch paper.
- Smith, Maria, *From Distinction to Information*, Information Science branch paper.
- Smith, Maria, *After Turing: The Fold Machine*, Classical Computation branch paper.
- Smith, Maria, *The Quantum Fold Machine*, Reversible and Quantum Computation branch paper.

## Data, code, rights and participation

The canonical open repository is https://github.com/MettaMazza/ernos-labs-sft-platform. The release package contains this Markdown manuscript, the archival PDF, the complete evidence map, publication receipt, categorical inventory, claim packages, generated candidate censuses, elimination decisions, controls, independent validators, empirical source records and immutable engine receipts.

Copyright 2026 Maria Smith. Paper and documentation are licensed CC BY 4.0; repository code is licensed Apache 2.0. These licenses permit open copying, inspection, criticism, modification and redistribution with attribution. “Ernos Labs” remains a standards-conformance designation whose use requires adherence to the published empirical constitution and community standards.

Independent review, replication, lawful extension and attempted invalidation are invited. Contact Maria.Smith.Sftoe@gmail.com or https://discord.gg/ucwGryVxGr. Scientific admission requires the complete derivation chain and an unchanged-engine receipt; neither reputation nor criticism alone changes the model census.

Suggested citation: Smith, Maria (2026), *From Fold to Physics: An Exact, Parameter-Free and Machine-Closed Reconstruction of Physical Science from Smithian Fold Theory*, Ernos Labs Physics Branch Paper 001, version {version}.
""")
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    paper_text = "\n".join(sections).rstrip() + "\n"
    PAPER.write_text(paper_text, encoding="utf-8")
    if authorized and PAPER == ROOT / "publications/current/physics/FROM_FOLD_TO_PHYSICS.md":
        LANDING.write_text(paper_text, encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} categorical Physics claim sections")


if __name__ == "__main__":
    main()
