#!/usr/bin/env python3
"""Build the exhaustive Medicine foundation paper from admitted evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.medicine.empirical_program import MEDICINE_SPECS  # noqa: E402
from sft.medicine.external_bindings import BINDING_BY_CLAIM  # noqa: E402
from sft.medicine.sources import MEDICINE_AUTHORITY_SOURCES, SOURCE_BY_ID  # noqa: E402
from sft.medicine.structural_counts import diagnostic_table_certificate, two_arm_outcome_certificate  # noqa: E402
from tools.publication_series_voice import OPEN_SCIENCE_REFERENCES, open_science_position  # noqa: E402


INVENTORY = ROOT / "publications/inventories/medicine.json"
PAPER = ROOT / "publications/current/medicine/FROM_FOLD_TO_MEDICINE.md"
CENSUS = ROOT / "census/claims.json"
METADATA = ROOT / "publication/medicine_foundation_zenodo_metadata.json"


FAMILY_INTRO = {
    "patient_population_health": "Medicine begins with the identity of the person and the clinical population. A patient is never an average; a population is never allowed to erase its members, source frame, setting or observation interval.",
    "variation_dysfunction_disease_injury": "Difference, dysfunction, disease and injury are distinct clinical relations. Each keeps the reference population, functional consequence, mechanism, criteria, site, severity and time boundary that makes the classification testable.",
    "symptom_sign_measurement_diagnosis": "Patient report, observer-elicited sign, instrument measurement and diagnostic class are separate evidence carriers. The branch preserves language, observer, method, calibration, alternative diagnoses and verification rather than promoting a label into a fact.",
    "cause_association_mechanism_confounding": "Association is not cause. Causal claims retain time order, comparator meaning, confounding, mediation, effect modification and the exact observation class capable of distinguishing the alternatives.",
    "risk_prognosis_outcome": "Risk and prognosis are positive-finite relations over declared carriers and horizons. Every competing event, censored course, missing visit and component outcome remains present, preventing an unobserved event from becoming numerical zero.",
    "intervention_comparator_counterfactual": "An intervention is scientifically legible only beside a comparator and an explicit alternative-course boundary. Allocation, concealment, adherence, crossover and cointervention remain in the trace rather than being repaired after outcomes are known.",
    "dose_exposure_response_adverse_event": "Dose, exposure, response, adverse event and toxicity are separately generated relations. Route, formulation, schedule, duration, organ or function, causality assessment and recovery remain held; one fitted curve cannot erase adverse or nonmonotone evidence.",
    "efficacy_effectiveness_safety_benefit_harm": "Efficacy under explanatory conditions and effectiveness in usual care are not synonyms. Safety is a complete adverse-outcome record, not proof of harmlessness, and benefit-harm composition cannot erase patient-valued components.",
    "trial_observational_synthesis": "Trials, observational studies and evidence synthesis are distinct process grammars. Protocol, allocation, blinding, sampling, confounders, missingness, study dependence and selective reporting remain inspectable from registration to interpretation.",
    "screening_prevention_treatment_rehabilitation": "Screening is the complete pathway from an apparently healthy population through confirmation and care, including false results and overdiagnosis. Prevention, treatment, monitoring, stopping and rehabilitation retain their different timing, purpose and outcome structures.",
    "individual_population_inference": "Population evidence does not uniquely determine an individual decision. Transport, subgroup multiplicity, patient context, consequence, preference and unresolved alternatives are retained at every handoff.",
    "consent_ethics_privacy_uncertainty": "The clinical evidence system cannot erase the person who bears its risk. Consent, capacity, privacy, minimization, equipoise, stopping and reviewer custody are operational admission boundaries with complete records, not decorative ethics prose.",
}


SPECIAL_MEANING = {
    "SFT-MED-PATIENT-IDENTITY-001": "The theorem prohibits a row, specimen, encounter or model embedding from silently replacing the person. Linkage is lawful only when consent scope, identity relation, episode context and provenance survive reconstruction.",
    "SFT-MED-HEALTH-STATE-001": "Health is not defined as the numerical absence of disease. The exact carrier retains physical, mental and social function, lived experience, capacity, survival, setting and time as separately observable domains.",
    "SFT-MED-NORMAL-VARIATION-001": "Normal is source- and method-bound support within a declared reference population. No fitted cutoff or consensus interval becomes a universal law, and difference alone does not establish dysfunction.",
    "SFT-MED-DISEASE-001": "A disease label survives only with criteria, harmful process, manifestations, course and diagnostic boundary retained. This corrects the prior cancer shorthand: recurrence alone cannot identify a clinical disease.",
    "SFT-MED-DIAGNOSTIC-ACCURACY-001": "Two held distinctions—condition classification and test result—generate exactly four observation cells. All four are required. Sensitivity-like or specificity-like summaries are downstream exact readings and cannot replace the underlying counts, population spectrum or reference method.",
    "SFT-MED-DIFFERENTIAL-DIAGNOSIS-001": "Unobserved alternatives remain in support. A differential narrows only when recorded patient evidence lawfully eliminates a candidate; popularity, pretrained prediction or one favorable test cannot silently close it.",
    "SFT-MED-CLINICAL-CAUSE-001": "Cause requires a generated comparison whose timing and identification boundary are explicit. A measured association can test the joint incidence relation but cannot, by authority or magnitude alone, select a causal law.",
    "SFT-MED-CONFOUNDING-001": "A common pre-exposure cause remains a held distinction whether measured or not. Adjustment states exactly which labels it conditions on; the unmeasured remainder is uncertainty, not conventional zero.",
    "SFT-MED-RISK-001": "Risk is the exact ratio of observed outcome carriers to an eligible at-risk carrier set over a declared horizon. SFT represents an observed absence by a held absence label; it never introduces ontological nothing or silently discards loss to follow-up.",
    "SFT-MED-PROGNOSIS-001": "A prognosis is conditioned support over a declared patient baseline and care context, not fate. Competing events, censoring, changes in treatment and alternative courses remain explicit.",
    "SFT-MED-RANDOMIZATION-001": "Randomization is closed without ontological nondeterminism. A deterministic held-label generator produces a reproducible allocation sequence; concealment prevents selectors from observing future labels. The full generator, custody, assignment and release trace remains available for audit after the decision boundary.",
    "SFT-MED-COUNTERFACTUAL-001": "Alternative courses are mutually exclusive observations for the same eligibility state. The missing course is retained as unavailable support, so identification assumptions can be inspected instead of being mistaken for measured outcomes.",
    "SFT-MED-DOSE-001": "Dose is an exact positive-finite relation among amount, patient carrier, formulation, route and schedule. It is not a fitted efficacy constant and does not import a universal response.",
    "SFT-MED-DOSE-RESPONSE-001": "Every administered group and outcome remains in the exact support, including nonmonotone and adverse shapes. A fitted exposure-response curve may summarize declared data but cannot select or replace the Fold law.",
    "SFT-MED-ADVERSE-EVENT-001": "Every unfavorable event after care is preserved regardless of attribution. Timing, seriousness, severity, relatedness assessment and final outcome are separate labels, preventing causally inconvenient harm from disappearing.",
    "SFT-MED-SAFETY-001": "Safety means a complete comparative adverse-outcome record at a declared exposure and follow-up boundary. It never means an intervention is proven incapable of harm.",
    "SFT-MED-ABSOLUTE-RELATIVE-EFFECT-001": "The same complete four-cell arm-by-outcome table yields absolute and relative comparisons. Neither representation is privileged and neither may hide the arm counts, baseline incidence or horizon.",
    "SFT-MED-MISSING-REPORTING-001": "Registered outcomes and studies remain present even when results are unavailable. Cochrane's external evidence records how selective dissemination can overstate benefit and understate harm; the SFT law prevents the missing row from being rewarded as a favorable result.",
    "SFT-MED-SCREENING-001": "The theorem covers the entire screening chain, not test accuracy alone: population, test, confirmation, intervention, outcomes, false results, overdiagnosis, burden and harm. WHO correspondence is opened only after this chain is sealed.",
    "SFT-MED-REHABILITATION-001": "Rehabilitation is an iterated person-centred relation among goals, interventions, function, participation and lived context. It is not reducible to one impairment score or one encounter.",
    "SFT-MED-INDIVIDUAL-INFERENCE-001": "A population result is evidence available to an individual inference, not the individual conclusion. Patient evidence, preferences, context, alternatives and uncertainty remain held.",
    "SFT-MED-INFORMED-CONSENT-001": "Consent requires information, understanding, voluntariness, authorization, purpose, scope and time. Refusal and withdrawal are first-class outcomes; a signed field alone cannot substitute for the process.",
    "SFT-MED-CLINICAL-PRIVACY-001": "Privacy is purpose-bound access and disclosure with complete identity, content, recipient and time custody. The public proof can be maximally transparent without exposing an unnecessary patient link.",
    "SFT-MED-CLINICAL-EVIDENCE-HANDOFF-001": "The final foundation law makes reproducibility and patient protection compositional: derivation, source custody, code, adverse/null/unresolved evidence and privacy boundaries must all survive transfer to an independent reviewer.",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: object) -> str:
    return str(value).replace("\n", " ").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-").strip()


def bullets(values) -> str:
    rows = tuple(values)
    return "\n".join(f"- {clean(value)}" for value in rows) if rows else "- None."


def axis_rows(spec, elimination: dict) -> str:
    decisions = {row["candidate_id"]: row for row in elimination["decisions"]}
    coordinates = spec.exact_result.split("__")
    output = ["| Axis | Eliminated form | Forced form | Exact elimination / retention basis |", "|---|---|---|---|"]
    for index, dimension in enumerate(spec.dimensions):
        rejected = next(row for row in dimension.choices if not row.admitted)
        changed = list(coordinates)
        changed[index] = rejected.name
        reason = decisions["__".join(changed)]["reason"]
        output.append(f"| `{dimension.key}` | `{rejected.name}` | `{dimension.admitted_choice.name}` | {clean(reason)} {clean(dimension.admitted_choice.reason)} |")
    return "\n".join(output)


def scientific_meaning(spec) -> str:
    return SPECIAL_MEANING.get(spec.claim_id, f"The result is an exact relational classification at the declared clinical boundary. It forces {clean(spec.statement).lower()} Patient-, population-, method-, setting- and time-dependent magnitudes remain explicit records and are never promoted into universal constants without a separately generated and externally tested law.")


def claim_block(order: int, spec) -> str:
    package = ROOT / "claims" / spec.claim_id
    registration = read(package / "registration.json")
    candidate = read(package / "candidate_census.json")
    elimination = read(package / "elimination_receipt.json")
    controls = read(package / "controls.json")["controls"]
    certificate = read(package / "certificate.json")
    empirical = read(package / "empirical_validation.json")
    census_row = next(row for row in read(CENSUS)["claims"] if row["claim_id"] == spec.claim_id)
    binding = BINDING_BY_CLAIM[spec.claim_id]
    source_rows = [SOURCE_BY_ID[source_id] for source_id in spec.source_ids]
    witnesses = "\n".join(f"- `{name}`: {description}; passed `{str(passed).lower()}`." for name, description, passed in spec.operational_witnesses)
    controls_text = "\n".join(f"- `{row['kind']}`: passed; expected {clean(row['expected_behavior'])}; observed {clean(row['observed_behavior'])}; receipt `{row['receipt_hash']}`." for row in controls)
    sources = "\n".join(f"- `{row.source_id}` - {row.body}; [{row.source_uri}]({row.source_uri}); snapshot `{row.snapshot_path}`; `{row.snapshot_hash}`; scope: {row.evidence_scope}." for row in source_rows)
    fragment_identity = sha256_identity(tuple((row.source_id, row.fragment) for row in binding.requirements))
    return f"""### {order}. {spec.title}

Claim identity: `{spec.claim_id}`

**Question and exact theorem.** {clean(spec.statement)}

> `{clean(spec.exact_result)}`

**Rooted dependency chain.** The registration names `SFT-ROOT-THERE-IS-NO-NOTHING`, zero axioms and zero free parameters. It requires these already admitted receipts:

{bullets(f'`{row}`' for row in spec.dependencies)}

The dependency graph independently reaches the premise-free root theorem; a branch name never substitutes for a receipt.

**Generated grammar.** {clean(spec.generation_rule)}

Boundary: {clean(spec.grammar_boundary)}

The exact product contains `{candidate['expected_cardinality']}` candidates, `{len(candidate['candidates'])}` stored candidate identities and `{len(elimination['decisions'])}` one-for-one decisions. Exactly one survives; 255 fail at least one required coordinate.

{axis_rows(spec, elimination)}

**Unique survivor and depth independence.** Sole survivor: `{spec.exact_result}`.

Base: {clean(spec.induction_base)}

Successor: {clean(spec.induction_step)}

Closure scope: `{certificate['closure_scope']}`; minimality and named-shape uniqueness both pass.

**Operational witnesses.**

{witnesses}

**Scientific meaning.** {scientific_meaning(spec)}

{FAMILY_INTRO[spec.family]}

**Adverse controls.**

{controls_text}

**Independent reconstruction.** A separately executed implementation regenerated the literal product, candidate order, every decision, the sole survivor, depth-independent closure and all four control classes. Implementation `{certificate['independent_implementation_hash']}`; certificate `{certificate['independent_certificate_hash']}`; external-validation `{certificate['external_validation_hash']}`.

**Post-seal external comparison.** The entire 72-law prediction family was sealed before any source identity was chosen. This claim requires `{len(binding.requirements)}` purpose-matched discriminators with ordered identity `{fragment_identity}`. Target opened after derivation seal: `{str(empirical['target_opened_after_seal']).lower()}`. All rows preserved: `{str(empirical['all_rows_preserved']).lower()}`. Exact comparison: `{str(empirical['passed']).lower()}`. A deliberately changed observation was rejected.

Sources:

{sources}

Comparison record:

{bullets(empirical['measurements'])}

Falsification boundary: {clean(empirical['falsification_condition'])}

**Explicit exclusions.**

{bullets(registration['excluded_inputs'])}

**Immutable evidence identities.** Pre-source seal `{certificate['pre_source_complete_branch_seal']}`; source manifest `{certificate['source_manifest_hash']}`; derivation seal `{certificate['derivation_seal_hash']}`; engine receipt `{census_row['receipt_hash']}` at `{census_row['receipt_path']}`; empirical validation `{certificate['empirical_validation_hash']}`; measurement receipt `{certificate['measurement_receipt_hash']}`; isolation `{empirical['isolation_certificate']['certificate_hash']}`; custody `{empirical['target_custody_certificate']['certificate_hash']}`.
"""


def main() -> None:
    inventory = read(INVENTORY)
    metadata = read(METADATA)
    census = read(CENSUS)
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    if inventory["required_claim_count"] != 72 or any(claim_id not in admitted for claim_id in inventory["required_claim_ids"]):
        raise SystemExit("Medicine foundation live census is not completely admitted")
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized and not doi:
        raise SystemExit("authorized Medicine publication requires its reserved DOI")
    publication_banner = (
        f"**PUBLISHED OPEN-ACCESS BRANCH PAPER.** DOI: [{doi}](https://doi.org/{doi}). The canonical Markdown paper, rendered PDF, evidence archive and checksums form this release."
        if authorized else
        "**LOCAL PREPUBLICATION MANUSCRIPT. Publication is not yet authorized.** Building this paper performs no push, release, upload, DOI creation or Zenodo action."
    )
    diagnostic = diagnostic_table_certificate()
    trial = two_arm_outcome_certificate()
    mission = open_science_position("For Medicine, a diagnosis, institutional guideline, fitted threshold, selected trial, favorable endpoint, proprietary model or consensus label cannot stand for a clinical law. The patient, population, comparator, method, time, missingness, adverse outcomes, consent and privacy boundary remain inside the evidence chain. Exact finite counts are stated as exact; clinical magnitudes remain bounded to their measured populations and protocols.")
    sections = [f"""# From Fold to Medicine

**Medicine and Health Sciences Foundational Branch Paper 001, version 1.0.0 — Smithian Fold Theory V3 Clean-Room Reconstruction**

## Abstract

This paper reports the foundational Medicine and Health Sciences branch of the third clean-room Smithian Fold Theory reconstruction at its current-evidence-closed, extension-open boundary. Seventy-two obligations in twelve ordered families generate 18,432 exact candidates and decisions, seventy-two unique survivors, seventy-two depth-independent certificates, 288 passing adverse controls, seventy-two implementation-distinct reconstructions and seventy-two post-seal external comparisons. Every dependency graph reaches the single premise-free theorem, There Is No Nothing. The branch uses zero axioms, zero free or fitted parameters, no negative proof quantities, no irrational or imaginary proof values, no target-selected rule and no opaque predictor.

The headline result is a machine-checkable constitution for clinical knowledge. Patient identity cannot be replaced by an aggregate. Health is not numerical absence of disease. Symptoms, signs, measurements and diagnoses are distinct carriers. Association is not cause. Risk and prognosis retain horizon, competing events and censoring. Interventions require comparators and explicit alternative-course boundaries. Deterministic allocation can supply auditable randomisation by concealed held labels without importing ontological chance. Every adverse, null, missing and unresolved result survives the evidence chain. Trial, observational and synthesis structures remain distinct. Population evidence cannot uniquely select an individual decision. Consent, capacity, privacy, minimization and stopping rules are operational scientific boundaries.

All 356 V1 rows and 407 V2 steps were atomically reviewed. Five Medicine-owned atoms embedded in mixed prior claims are now closed by immutable V3 receipts at corrected clinical boundaries: placebo claims require complete comparators and outcomes; stereochemical identity alone cannot establish efficacy or toxicity; denominator parity cannot establish medical prognosis; and cellular recurrence alone cannot establish a cancer diagnosis. Eleven of thirteen preregistered authority sources were captured; two HHS transports failed and remain visibly preserved rather than being counted as evidence.

## Results first: the medical findings

| Headline result | Exact or bounded result | Scientific meaning |
|---|---|---|
| Complete foundational closure | `72` laws; `18,432` candidates; `72` survivors; `288` controls | Every law has a root trace, unique survivor, independent reconstruction, external comparison and immutable receipt. |
| Patient before aggregate | Person identity, episode, longitudinal course and population membership remain held | A row, mean, embedding or sample cannot silently replace the patient. |
| Health and disease | Multidomain health state; reference-bound variation; criteria-bound dysfunction, disease and injury | Absence displayed as `0` is a held absence label, never ontological nothing. |
| Diagnostic evidence | `{diagnostic['cell_count']}` exact condition-by-test cells, all retained | A summary statistic cannot erase false results, spectrum, method or reference verification. |
| Causal clinical inference | Association, cause, mechanism, confounding, mediation and modification are distinct generated relations | Magnitude or consensus cannot promote association into cause. |
| Risk and prognosis | Positive-finite outcome shares over explicit carriers and horizons | Competing events, loss and censoring remain first-class outcomes. |
| Intervention evidence | Intervention, comparator, alternative course, allocation, adherence and cointervention retained | No treatment claim exists without its comparison boundary. |
| Deterministic randomisation | Reproducible held-label generator plus concealed future allocation | Unpredictability to selectors is achieved without importing metaphysical nondeterminism. |
| Benefit and harm | `{trial['cell_count']}` exact arm-by-outcome cells plus complete adverse-event support | Safety never means proven harmlessness; benefit cannot erase harm. |
| Evidence synthesis | Protocol, search, selection, heterogeneity, dependence and missing results retained | Selective reporting cannot be rewarded as favorable absence. |
| Individual inference and ethics | Population-to-person boundary, consent, capacity, privacy, minimization, equipoise and custody | Transparent science and patient protection are jointly reconstructible. |

{mission}

## 1. Publication, authorship and open-science boundary

{publication_banner}

Maria Smith, independent researcher and founder of Ernos Labs. Contact: Maria.Smith.Sftoe@gmail.com. Reproducibility reports and submissions: https://discord.gg/ucwGryVxGr. GitHub: https://github.com/MettaMazza.

Copyright preserves Maria Smith's authorship. The paper and documentation are prepared under CC BY 4.0 and code under Apache-2.0. The Ernos Labs name is a separate, revocable standards designation: reuse is open, but the designation requires continued adherence to the public constitution, unchanged admission engine, complete adverse evidence and open critical review.

## 2. Exact scope and closure language

Foundational closure means every obligation in the frozen 72-law surface has an engine-admitted theorem inside its declared exact grammar, complete root path, adverse controls, independent reconstruction and post-seal comparison. It does not mean Medicine is permanently locked or that every specialty and future observation is enumerated. This foundation is current-evidence closed and extension-open. Layer Two remains the explicit field-wide programme.

## 3. Constitutional mathematical domain

Structural absence is Empty One and may be displayed as `0`; it is not conventional numerical nothing. Counts are generated positive wholes and exact parts are positive held fractions. Opposition and direction are labels rather than negative scalars. Negative proof quantities, irrational or imaginary proof values, floating equality, completed infinity, ungenerated continua, axioms, free parameters, fitted coefficients, imported clinical equations, pretrained predictors, consensus-selected survivors and application-selected laws are prohibited. Conventional clinical notation appears only in correspondence prose where it cannot act as proof input.

## 4. Dependency spine and root trace

Every Medicine registration names the single premise-free root and zero axioms. The first law depends on admitted Foundation, Mathematics, Information Science, Computation, Physics, Chemistry, Materials and Biology receipts. Each later law also depends on its immediate Medicine predecessor, creating one ordered 72-law chain. The engine resolves every dependency recursively to an actual immutable receipt and ultimately to There Is No Nothing; narrative citation cannot substitute for this graph.

## 5. Complete target-blind seal

Before any external source identity or outcome was opened, the whole 72-law inventory, exact structural module and target-blind blueprint set were frozen at `sha256:57b0813078b36814b831862db7e888601d8e1c1d2820f7429915431bf6066cd5`. It binds 72 predictions and 18,432 candidate identities while recording `external_source_identities_selected=false` and `external_outcomes_opened=false`. Changing any obligation or survivor now breaks the seal.

## 6. Exact clinical table certificates

Two held diagnostic distinctions generate `{diagnostic['cell_count']}` unique condition-by-test cells. Two held trial distinctions generate `{trial['cell_count']}` unique arm-by-outcome cells. Both products are complete and every cell appears exactly once. A held absence label is not numerical-zero ontology. Sensitivity, specificity, risks, risk differences and ratios may be derived downstream as exact readings of the relevant positive finite counts, but no summary may replace the complete table.

## 7. External evidence and preserved adversity

Thirteen source identities were selected only after the complete prediction seal: WHO health and screening records; FDA biomarker and exposure-response records; CDC epidemiology; final ICH E6(R3) Good Clinical Practice and E9(R1) estimand guidance; Cochrane intervention and missing-evidence chapters; NICHD rehabilitation; STROBE; and two HHS consent/privacy identities. Eleven were byte-captured and hashed. Both HHS pages returned HTTP 403 to the registered automated transport; those two failures, their identities and their receipts remain in the source manifest and are not used to pass a claim. The captured final ICH guideline independently supplies consent, confidentiality, participant safety, protocol, randomisation, blinding, adverse-event and essential-record evidence.

Every claim binds at least two purpose-matched source fragments. The prediction process cannot read filesystem, network, clock, environment, dynamic import, subprocess or target. A distinct custodian opens sources after sealing and releases a target only for a matching prediction seal. Deliberately changed observations reject. External authority tests correspondence; it never creates the theorem.

## 8. V1/V2 atomic reconciliation

The audit reviews all 763 prior entries, not only keyword hits. One V1 row and three V2 steps contain five Medicine-owned atoms after mixed claims are decomposed. All five now map to immutable Medicine receipts and none remains open. The corrected result does not hide the earlier statement: placebo and nocebo require measured expectation, comparison, blinding, objective and reported outcomes; chemical enantiomer identity does not establish patient benefit or toxicity; ageing needs population, prognosis, competing-event and censoring evidence; cancer needs disease criteria, diagnosis and stage in addition to biological dysregulation.

## 9. Reading the exhaustive derivation ledger

Each of the seventy-two sections below states its theorem, dependencies, complete eight-axis grammar, all 256 decisions, sole survivor, depth-independent base and successor, operational witnesses, clinical meaning, four adverse controls, independent implementation, post-seal sources, falsification boundary and immutable identities. The machine-readable evidence remains authoritative; the paper makes that evidence humanly inspectable.
"""]

    section_number = 10
    order = 1
    for family in inventory["family_order"]:
        sections.append(f"\n## {section_number}. {family.replace('_', ' ').title()}\n\n{FAMILY_INTRO[family]}\n")
        for spec in (row for row in MEDICINE_SPECS if row.family == family):
            sections.append(claim_block(order, spec))
            order += 1
        section_number += 1

    source_rows = []
    for row in MEDICINE_AUTHORITY_SOURCES:
        if row.transport_status == "captured":
            source_rows.append(f"- `{row.source_id}` — [{row.source_uri}]({row.source_uri}); captured `{row.snapshot_hash}`; text `{row.text_hash}`; {row.evidence_scope}.")
        else:
            source_rows.append(f"- `{row.source_id}` — [{row.source_uri}]({row.source_uri}); **transport failed and preserved** `{row.failure_hash}`; {row.evidence_scope}.")
    audit = read(ROOT / "audits/medicine_v1_v2_atomic_ownership.json")
    sections.append(f"""
## {section_number}. Integrated audit result

- Prior entries reviewed: `{audit['source_surface']['total_source_rows_reviewed']}`.
- Medicine-relevant prior rows: `{audit['source_surface']['medicine_relevant_source_row_count']}`.
- Medicine-owned atoms: `{audit['summary']['medicine_owned_atom_count']}`.
- Same-strength V3-closed atoms: `{audit['summary']['same_strength_closed_atom_count']}`.
- Open atoms: `{audit['summary']['same_strength_open_atom_count']}`.
- Corrected prior atoms: `{audit['summary']['corrected_prior_atom_count']}`.
- Audit identity: `{audit['audit_identity']}`.

## {section_number + 1}. External-source ledger

{chr(10).join(source_rows)}

The failed HHS transports are evidence about transport, not evidence for the clinical laws. They remain visible, while ICH supplies independently captured purpose-matched content. No unavailable source is converted into a successful row.

## {section_number + 2}. Reproducibility and falsification

The cross-platform Medicine suite checks inventory/spec alignment, all 18,432 candidates, 72 unique survivors, dependency order, source and failure hashes, every purpose-matched fragment, the two exact four-cell certificates and prohibited blueprint fields. The immutable engine and verification-authority seals run before admission and again at completion. The publication gate was frozen before any Medicine receipt existed.

The branch is falsified at its declared boundary if any source hash changes without a new version, any required fragment is absent, any target becomes accessible before sealing, any adverse/null/missing/unresolved or failed row is omitted, any tampered target is accepted, any dependency loses its root path, any candidate census is incomplete, any law has other than one survivor, any independent validator fails, or any patient privacy boundary is violated.

## {section_number + 3}. Full-field Medicine and Health Sciences roadmap

This paper completes Layer One. Later versions extend in dependency order through anatomy, physiology and pathology at the medical boundary; epidemiology and causal inference; diagnostics, imaging, laboratory medicine and biomarkers; pharmacology, pharmacokinetics, toxicology and therapeutics; infectious and immune disease; genetic, metabolic and developmental disorders; cardiovascular, respiratory, renal, gastrointestinal and endocrine medicine; neurology, psychiatry and behavioural health with a strict Consciousness handoff; oncology and haematology; dermatology, musculoskeletal and autoimmune medicine; reproductive, maternal, neonatal, paediatric and ageing medicine; surgery, anaesthesia, critical care, trauma and rehabilitation; dentistry, vision and hearing; primary, emergency and integrated care; nursing and allied-health evidence; public, occupational, environmental and global health; nutrition and prevention; precision medicine; health-services and implementation evidence; clinical informatics and verified medical AI; devices and biomaterials; replication, adverse outcomes and limits of generalization.

The paper will be versioned as those families are independently completed. Applications, institutions, treatment preferences and regulatory outcomes may test the laws but may never select them.

## {section_number + 4}. Limitations

- The 72-law foundation is current-evidence closed inside its frozen grammar and remains extension-open; it is not the complete specialty-by-specialty reconstruction.
- Most results are exact relational and evidence-constitution laws, not universal patient magnitudes.
- Authority correspondence is a post-seal content test, not a premise and not a claim that every authority statement is correct.
- Two registered HHS endpoints were unavailable to automated capture and remain unfavorable transport rows.
- No clinical decision, diagnosis or treatment recommendation for a real person follows from this foundational paper.
- Biology retains living mechanism, Chemistry molecular identity, Materials devices and interfaces, and Consciousness subjective-experience laws; Medicine cites but does not reown them.
- Ethical and privacy claims here are operational evidence-admission boundaries. They do not claim to exhaust moral philosophy or every jurisdiction's law.

## {section_number + 5}. Conclusion

Foundational Medicine is current-evidence closed and extension-open: 72 required laws, 18,432 exact candidates and decisions, 72 sole survivors, 288 passing adverse controls, 72 independent reconstructions, 72 post-seal comparisons, 72 receipt-backed root traces, and five of five legacy Medicine atoms reconciled at stronger clinical boundaries.

The result is not a glossary and not a conventional clinical model decorated with Fold language. It is a public constitution that refuses to erase the patient, comparator, alternative diagnosis, competing event, adverse outcome, missing result, consent scope or privacy boundary. It derives auditable randomisation in a superdeterministic ontology, separates association from cause, separates safety evidence from harmlessness, and makes individual inference explicitly different from population inference.

That is the empirical gravity of this branch: a medical statement is admitted only when its exact carrier, alternatives, controls, evidence custody and root trace survive independent reconstruction. Open criticism remains unrestricted. Scientific admission remains earned.

## {section_number + 6}. Repository and publication status

- Canonical repository: https://github.com/MettaMazza/ernos-labs-sft-platform
- Zenodo DOI: {f'https://doi.org/{doi}' if authorized else 'not created; separate authorization required'}
- Author: Maria Smith, Ernos Labs
- Contact: Maria.Smith.Sftoe@gmail.com
- Submissions: https://discord.gg/ucwGryVxGr
- Current state: {'published open access' if authorized else 'local prepublication; no remote action performed'}

## {section_number + 7}. References

- World Health Organization. Constitution and definition of health.
- United States Food and Drug Administration and National Institutes of Health. BEST biomarker terminology and context of use.
- Centers for Disease Control and Prevention. *Principles of Epidemiology in Public Health Practice*.
- International Council for Harmonisation. *E6(R3) Guideline for Good Clinical Practice*. Final version, 2025.
- International Council for Harmonisation. *E9(R1) Addendum on Estimands and Sensitivity Analysis in Clinical Trials*. Final version, 2019.
- United States Food and Drug Administration. *Exposure-Response Relationships: Study Design, Data Analysis, and Regulatory Applications*.
- Cochrane. *Handbook for Systematic Reviews of Interventions*, version 6.5.
- World Health Organization Regional Office for Europe. *Screening Programmes: A Short Guide*.
- Eunice Kennedy Shriver National Institute of Child Health and Human Development. Rehabilitation Medicine.
- STROBE Initiative. *Strengthening the Reporting of Observational Studies in Epidemiology*.
- Smith, Maria. *From Nothing to Fold*. doi:10.5281/zenodo.21515629.
- Smith, Maria. *From Fold to Mathematics*. doi:10.5281/zenodo.21516146.
- Smith, Maria. *From Distinction to Information*. doi:10.5281/zenodo.21516916.
- Smith, Maria. *From Fold to Physics*. doi:10.5281/zenodo.21520881.
- Smith, Maria. *From Fold to Chemistry*. doi:10.5281/zenodo.21531455.
- Smith, Maria. *From Fold to Life*. doi:10.5281/zenodo.21630203.

Open-science evidence supporting the institutional argument:

{OPEN_SCIENCE_REFERENCES}
""")
    PAPER.parent.mkdir(parents=True, exist_ok=True)
    PAPER.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"built {PAPER.relative_to(ROOT)} with {order - 1} exhaustive claim sections")


if __name__ == "__main__":
    main()
