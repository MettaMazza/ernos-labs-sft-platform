"""Frozen, answer-free foundational question surface for Medicine.

The familiar medical nouns below identify distinctions that must be retained;
they do not import medical answers.  External observations may test these laws
only after this complete inventory and its candidate grammar are sealed.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


FAMILY_ORDER = (
    "patient_population_health",
    "variation_dysfunction_disease_injury",
    "symptom_sign_measurement_diagnosis",
    "cause_association_mechanism_confounding",
    "risk_prognosis_outcome",
    "intervention_comparator_counterfactual",
    "dose_exposure_response_adverse_event",
    "efficacy_effectiveness_safety_benefit_harm",
    "trial_observational_synthesis",
    "screening_prevention_treatment_rehabilitation",
    "individual_population_inference",
    "consent_ethics_privacy_uncertainty",
)


@dataclass(frozen=True)
class MedicineObligation:
    claim_id: str
    title: str
    family: str
    carrier: str
    relation: str
    organization: str
    observation: str
    statement: str


def row(
    suffix: str,
    title: str,
    family: str,
    carrier: str,
    relation: str,
    organization: str,
    observation: str,
    statement: str,
) -> MedicineObligation:
    return MedicineObligation(
        f"SFT-MED-{suffix}-001", title, family, carrier, relation,
        organization, observation, statement,
    )


MEDICINE_OBLIGATIONS = (
    # Patient, population, health state and clinical observation — 6
    row("PATIENT-IDENTITY", "Patient identity", FAMILY_ORDER[0], "consented-person-record", "same-person-across-episodes", "identity-with-held-linkage", "declared-care-context-and-interval", "A patient is one consent-bound person carrier whose episode records may compose only while their exact linkage, context and provenance remain held."),
    row("CLINICAL-EPISODE", "Clinical episode", FAMILY_ORDER[0], "patient-episode", "ordered-observation-and-action-trace", "bounded-episode-with-start-and-stop", "declared-setting-and-follow-up", "A clinical episode is a finite ordered patient trace with explicit entry, observations, actions, exit and retained follow-up boundary."),
    row("CLINICAL-POPULATION", "Clinical population", FAMILY_ORDER[0], "finite-person-carriers", "membership-under-declared-criteria", "population-with-each-person-held", "place-time-source-frame", "A clinical population is a finite set of retained person carriers selected by declared criteria, never an average that erases membership or source frame."),
    row("HEALTH-STATE", "Health state", FAMILY_ORDER[0], "person-or-population-state", "function-and-capacity-relation", "multidomain-state-with-context", "declared-measures-and-time", "A health state is a context- and time-bound organization of retained functional, experiential and survival distinctions rather than an unqualified single label."),
    row("CLINICAL-OBSERVATION", "Clinical observation", FAMILY_ORDER[0], "patient-state-and-observer-record", "observation-with-retained-method", "source-method-result-provenance", "declared-observer-instrument-setting-time", "A clinical observation binds the observed carrier to observer, method, setting, time and result so the observation cannot silently become the law."),
    row("LONGITUDINAL-COURSE", "Longitudinal clinical course", FAMILY_ORDER[0], "ordered-patient-states", "within-person-transition-relation", "course-with-missing-visits-held", "declared-follow-up-and-censoring", "A longitudinal course is an ordered within-person state relation that preserves every observed interval, missing visit, intervention and censoring event."),

    # Normal variation, dysfunction, disease and injury — 6
    row("NORMAL-VARIATION", "Normal clinical variation", FAMILY_ORDER[1], "reference-person-states", "variation-within-declared-reference", "distribution-with-subgroups-held", "population-method-time-boundary", "Normal variation is the observed support within a declared reference population and method; it is not a universal numerical threshold."),
    row("DYSFUNCTION", "Dysfunction boundary", FAMILY_ORDER[1], "person-function-state", "impaired-relation-to-declared-function", "function-context-and-consequence", "method-and-baseline-boundary", "Dysfunction requires a retained functional relation, baseline, context and consequence and cannot be inferred from difference alone."),
    row("DISEASE", "Disease state", FAMILY_ORDER[1], "patient-process-state", "persistent-or-recurrent-harmful-process", "mechanism-manifestation-course", "diagnostic-criteria-and-time", "A disease state is a criteria-bound harmful process whose mechanism, manifestations and course remain distinct; a label alone is not the state."),
    row("INJURY", "Injury state", FAMILY_ORDER[1], "patient-tissue-or-function-state", "damage-following-declared-exposure", "exposure-damage-consequence-trace", "site-time-severity-method", "An injury binds a declared exposure to damage and consequence at a retained site, time, severity and observation method."),
    row("COMORBIDITY", "Comorbidity composition", FAMILY_ORDER[1], "joint-patient-condition-state", "co-occurrence-with-interaction-held", "noncollapsed-joint-condition-word", "shared-patient-and-interval", "Comorbidity is a joint condition word on one patient and interval; component conditions and their interactions may not be collapsed into one label."),
    row("SEVERITY-STAGE", "Severity and stage", FAMILY_ORDER[1], "disease-or-injury-course", "ordered-extent-relation", "criteria-specific-partial-order", "method-time-and-organ-system", "Severity and stage are declared finite order relations over retained criteria and may not be silently treated as interchangeable or universal scales."),

    # Symptom, sign, measurement and diagnostic classification — 6
    row("SYMPTOM", "Symptom record", FAMILY_ORDER[2], "patient-reported-experience", "report-to-person-state-relation", "content-intensity-timing-context", "elicitation-method-and-language", "A symptom is a patient-reported observation whose content, timing, context, elicitation and reporting uncertainty remain held."),
    row("SIGN", "Clinical sign", FAMILY_ORDER[2], "observer-elicited-patient-feature", "feature-to-method-relation", "observer-method-result-record", "setting-time-and-observer", "A sign is an observer-elicited feature with method, observer, setting and time retained; it is not interchangeable with a symptom."),
    row("CLINICAL-MEASUREMENT", "Clinical measurement", FAMILY_ORDER[2], "patient-specimen-or-signal", "traceable-measurement-relation", "method-unit-calibration-result", "preanalytic-analytic-postanalytic-boundary", "A clinical measurement retains carrier, unit, method, calibration, preanalytic state, result, uncertainty and reporting transformation."),
    row("DIAGNOSTIC-CLASSIFICATION", "Diagnostic classification", FAMILY_ORDER[2], "patient-evidence-word", "criteria-to-class-relation", "classification-with-alternatives-held", "reference-standard-and-verification", "Diagnostic classification maps a complete patient evidence word to a declared class while retaining alternative classes, criteria and verification boundary."),
    row("DIFFERENTIAL-DIAGNOSIS", "Differential diagnosis", FAMILY_ORDER[2], "candidate-condition-support", "evidence-conditioned-elimination", "retained-alternative-support", "patient-context-and-test-sequence", "A differential diagnosis is a retained finite support of candidate conditions reduced only by recorded patient evidence; an untested alternative may not disappear."),
    row("DIAGNOSTIC-ACCURACY", "Diagnostic accuracy", FAMILY_ORDER[2], "paired-index-and-reference-results", "agreement-disagreement-incidence", "complete-two-by-two-observation-table", "target-population-spectrum-and-verification", "Diagnostic accuracy requires all four cells generated by held condition and test-result distinctions plus population spectrum, reference method and verification record."),

    # Cause, association, mechanism and confounding — 6
    row("CLINICAL-ASSOCIATION", "Clinical association", FAMILY_ORDER[3], "paired-exposure-outcome-records", "joint-incidence-relation", "strata-and-missingness-held", "population-time-and-selection", "A clinical association is an exact joint-incidence relation at a declared population and interval and does not by itself assert cause."),
    row("CLINICAL-CAUSE", "Clinical causal claim", FAMILY_ORDER[3], "exposure-intervention-and-outcome-traces", "difference-under-lawful-comparison", "counterfactual-or-interventional-contrast", "exchangeability-time-and-follow-up", "A clinical causal claim requires a lawful contrast with timing, exchangeability boundary, intervention or counterfactual meaning and complete outcome follow-up."),
    row("CLINICAL-MECHANISM", "Clinical mechanism", FAMILY_ORDER[3], "ordered-biological-clinical-mediators", "exposure-to-mediator-to-outcome", "noncollapsed-causal-chain", "patient-condition-and-temporal-order", "A clinical mechanism is an ordered, independently observed chain connecting exposure to outcome; a plausible biological name alone cannot close it."),
    row("CONFOUNDING", "Clinical confounding", FAMILY_ORDER[3], "exposure-outcome-common-cause-word", "common-cause-distortion-relation", "measured-and-unmeasured-support", "design-and-adjustment-boundary", "Confounding is retained whenever a pre-exposure cause bears on both exposure and outcome; adjustment must state exactly which distinctions it conditions on."),
    row("MEDIATION", "Clinical mediation", FAMILY_ORDER[3], "exposure-mediator-outcome-word", "ordered-indirect-and-direct-paths", "path-specific-support", "intervention-and-measurement-times", "Mediation separates direct and mediator-carried paths only when their temporal and intervention meanings are explicitly generated and observed."),
    row("EFFECT-MODIFICATION", "Clinical effect modification", FAMILY_ORDER[3], "stratified-patient-carriers", "contrast-varies-by-held-stratum", "joint-treatment-stratum-outcome", "predeclared-strata-and-scale", "Effect modification is a retained variation of a treatment or exposure contrast across predeclared strata on a declared comparison scale."),

    # Risk, prognosis and outcomes — 6
    row("RISK", "Clinical risk", FAMILY_ORDER[4], "eligible-person-support", "outcome-incidence-over-follow-up", "at-risk-set-with-competing-events", "population-start-time-and-horizon", "Risk is an exact outcome share among an explicitly eligible at-risk set over a declared positive finite horizon, with competing events and loss retained."),
    row("INCIDENCE-PREVALENCE", "Incidence and prevalence", FAMILY_ORDER[4], "population-condition-records", "new-event-versus-state-support", "flow-and-stock-kept-distinct", "population-and-time-boundary", "Incidence counts new condition transitions while prevalence counts supported states; the two observation relations may not be merged."),
    row("PROGNOSIS", "Clinical prognosis", FAMILY_ORDER[4], "patient-baseline-state", "baseline-to-future-outcome-support", "conditioned-course-alternatives", "care-context-horizon-and-censoring", "Prognosis is the exact support of future outcomes conditional on a complete baseline and care context, never an unqualified fate label."),
    row("CLINICAL-OUTCOME", "Clinical outcome", FAMILY_ORDER[4], "patient-endpoint-state", "change-or-event-from-baseline", "endpoint-definition-and-components", "assessment-time-method-and-blinding", "A clinical outcome retains endpoint definition, baseline, assessment time, method, assessor and every component or adverse alternative."),
    row("CENSORING-COMPETING", "Censoring and competing events", FAMILY_ORDER[4], "incomplete-patient-course", "observability-and-competing-transition", "retained-unobserved-support", "reason-time-and-follow-up", "Censoring and competing events are explicit course outcomes; neither may be silently treated as absence of the target event."),
    row("PROGNOSTIC-CALIBRATION", "Prognostic calibration", FAMILY_ORDER[4], "predicted-and-observed-risk-groups", "prediction-observation-incidence", "complete-calibration-table", "new-population-and-time-window", "Calibration compares predeclared risk groups with every observed outcome row in a distinct population and interval without post-outcome retuning."),

    # Intervention, comparator and counterfactuals — 6
    row("INTERVENTION", "Clinical intervention", FAMILY_ORDER[5], "patient-directed-action", "action-to-course-transition", "content-delivery-and-adherence", "eligibility-setting-time-and-provider", "An intervention is a completely specified patient-directed action whose content, delivery, adherence, context and timing remain recorded."),
    row("COMPARATOR", "Clinical comparator", FAMILY_ORDER[5], "alternative-care-action", "contrast-with-intervention", "concurrent-or-declared-reference", "same-eligibility-outcome-and-time", "A comparator is an explicit alternative action evaluated under the same eligibility, outcome and time boundary; omitted care is not numerical zero."),
    row("COUNTERFACTUAL", "Clinical counterfactual", FAMILY_ORDER[5], "same-eligibility-patient-state", "alternative-action-outcome-relation", "mutually-exclusive-potential-courses", "identification-assumption-boundary", "A counterfactual denotes alternative courses for the same eligibility state; because only one course is observed, the missing course and identification boundary must remain explicit."),
    row("ALLOCATION", "Intervention allocation", FAMILY_ORDER[5], "eligible-participant-records", "assignment-to-declared-arm", "allocation-sequence-with-concealment", "generation-implementation-and-time", "Allocation is a fully traced deterministic assignment sequence whose concealment can prevent selection even though SFT imports no ontological nondeterminism."),
    row("ADHERENCE-CROSSOVER", "Adherence and crossover", FAMILY_ORDER[5], "assigned-and-received-care-record", "assignment-delivery-use-relation", "protocol-deviation-trace", "participant-time-and-reason", "Adherence and crossover preserve assignment, received care, timing and reason as distinct labels rather than rewriting the allocated history."),
    row("COINTERVENTION", "Clinical cointervention", FAMILY_ORDER[5], "joint-care-word", "additional-action-to-outcome-relation", "all-concurrent-actions-held", "arm-setting-and-time", "Every concurrent care action that can change an outcome remains in the intervention word and may not be hidden inside an arm label."),

    # Dose, exposure, response and adverse event — 6
    row("DOSE", "Dose", FAMILY_ORDER[6], "administered-substance-or-action", "amount-per-declared-carrier-and-time", "unit-route-formulation-schedule", "delivered-and-received-record", "Dose is an exact positive finite relation among amount, recipient carrier, formulation, route and schedule; no universal effect follows from dose alone."),
    row("EXPOSURE", "Clinical exposure", FAMILY_ORDER[6], "person-agent-contact-word", "contact-intensity-duration-route", "source-path-person-time", "measurement-and-reconstruction-method", "Exposure retains source, path, route, intensity, duration, person and measurement or reconstruction method."),
    row("RESPONSE", "Clinical response", FAMILY_ORDER[6], "patient-baseline-and-follow-up-state", "change-after-exposure-or-intervention", "multidomain-course-with-controls", "outcome-method-and-time", "A response is a recorded change from baseline after an exposure or intervention, with controls required before the temporal relation becomes causal."),
    row("DOSE-RESPONSE", "Dose-response relation", FAMILY_ORDER[6], "ordered-dose-groups-and-outcomes", "outcome-incidence-by-dose", "complete-dose-support-with-adverse-shapes", "population-route-and-time", "A dose-response relation retains every administered dose group, outcome, route, interval and nonmonotone or adverse pattern; no fitted curve is the law."),
    row("ADVERSE-EVENT", "Adverse event", FAMILY_ORDER[6], "participant-unfavorable-event", "event-after-exposure-or-care", "seriousness-severity-relatedness-outcome", "solicitation-time-and-follow-up", "Every unfavorable event after care remains recorded with seriousness, severity, timing, relatedness assessment and final outcome, whether or not causally attributed."),
    row("TOXICITY", "Clinical toxicity", FAMILY_ORDER[6], "exposure-and-harm-state", "exposure-linked-dysfunction-or-injury", "organ-course-dose-and-recovery", "method-population-and-time", "Toxicity requires an exposure-linked harmful transition with dose, organ or function, timing, recovery and alternative causes retained."),

    # Efficacy, effectiveness, safety and benefit-harm — 6
    row("EFFICACY", "Efficacy", FAMILY_ORDER[7], "controlled-intervention-comparison", "outcome-contrast-under-explanatory-conditions", "assigned-arms-and-complete-outcomes", "protocol-population-and-horizon", "Efficacy is a complete intervention-comparator outcome contrast under declared explanatory trial conditions."),
    row("EFFECTIVENESS", "Effectiveness", FAMILY_ORDER[7], "practice-intervention-comparison", "outcome-contrast-under-usual-care", "delivery-adherence-context-variation", "practice-population-and-horizon", "Effectiveness is the corresponding contrast under retained real-care delivery, adherence, population and setting variation."),
    row("SAFETY", "Safety evidence", FAMILY_ORDER[7], "all-exposed-and-comparator-participants", "favorable-and-unfavorable-event-incidence", "complete-event-severity-time-support", "exposure-duration-and-follow-up", "Safety is a complete comparative adverse-outcome record at a declared exposure and follow-up boundary, never proof that harm is absent."),
    row("BENEFIT-HARM", "Benefit-harm composition", FAMILY_ORDER[7], "joint-benefit-and-harm-outcomes", "noncollapsed-outcome-comparison", "patient-valued-components-held", "population-horizon-and-preference-boundary", "Benefit and harm remain separate outcome components and may compose only under an explicit population, horizon and value boundary."),
    row("ABSOLUTE-RELATIVE-EFFECT", "Absolute and relative effects", FAMILY_ORDER[7], "arm-specific-outcome-counts", "absolute-and-relative-comparison", "complete-two-arm-event-table", "population-and-horizon", "Absolute and relative effects are distinct exact readings of the same complete arm-by-outcome table; neither may replace the underlying counts."),
    row("TREATMENT-HETEROGENEITY", "Treatment-effect heterogeneity", FAMILY_ORDER[7], "predeclared-patient-strata", "arm-contrast-by-stratum", "joint-stratum-arm-outcome", "multiplicity-and-scale-boundary", "Treatment heterogeneity requires the complete joint stratum, arm and outcome support with predeclared comparisons and multiplicity retained."),

    # Trials, observational studies and evidence synthesis — 6
    row("CLINICAL-TRIAL", "Clinical trial", FAMILY_ORDER[8], "eligible-participant-traces", "prospective-allocation-and-outcome", "protocol-arms-flow-and-analysis", "registered-setting-time-and-endpoints", "A trial is a prospective finite process retaining protocol, eligibility, allocation, arm flow, outcomes, deviations and all analyses."),
    row("RANDOMIZATION", "Randomized allocation in a deterministic model", FAMILY_ORDER[8], "eligible-participants-and-held-generator-state", "concealed-unpredictable-assignment", "reconstructible-sequence-and-custody", "generation-concealment-release-boundary", "Randomization is a reproducible held-label allocation process whose future labels are concealed from selectors; it imports no nondeterministic ontology."),
    row("BLINDING", "Clinical blinding", FAMILY_ORDER[8], "participant-carer-assessor-role-word", "role-to-allocation-access-restriction", "access-and-unblinding-trace", "stage-role-and-information-boundary", "Blinding is an exact information-access restriction by role and stage with every planned or accidental unblinding event retained."),
    row("OBSERVATIONAL-STUDY", "Observational clinical study", FAMILY_ORDER[8], "sampled-person-records", "observed-exposure-outcome-relation", "sampling-selection-and-confounders", "source-population-time-and-follow-up", "An observational study retains source population, sampling, exposure, outcomes, confounders, missingness and follow-up and does not silently become an intervention."),
    row("EVIDENCE-SYNTHESIS", "Clinical evidence synthesis", FAMILY_ORDER[8], "study-level-evidence-carriers", "question-matched-composition", "heterogeneity-bias-and-dependence-held", "protocol-search-selection-and-date", "Evidence synthesis composes purpose-matched study carriers while retaining design differences, dependence, heterogeneity, bias, adverse and absent results."),
    row("MISSING-REPORTING", "Missing and selective reporting", FAMILY_ORDER[8], "registered-and-observed-study-results", "registration-publication-correspondence", "reported-unreported-support", "registry-search-and-cutoff-date", "A registered outcome or study absent from the visible report remains an explicit missing distinction and cannot be interpreted as a favorable absence."),

    # Screening, prevention, treatment and rehabilitation — 6
    row("SCREENING", "Screening", FAMILY_ORDER[9], "asymptomatic-eligible-population", "test-to-follow-up-care-path", "benefit-harm-and-overdiagnosis-chain", "population-interval-and-program", "Screening is the whole test-to-confirmation-to-care pathway in a declared asymptomatic population, including false results, overdiagnosis and downstream harms."),
    row("PREVENTION", "Prevention", FAMILY_ORDER[9], "at-risk-person-or-population", "action-before-target-outcome", "primary-secondary-tertiary-boundary", "risk-frame-time-and-outcomes", "Prevention is an action preceding a declared outcome in an at-risk carrier, with prevention level, comparator and all later outcomes retained."),
    row("TREATMENT", "Treatment", FAMILY_ORDER[9], "patient-with-declared-condition", "therapeutic-action-to-course", "content-delivery-response-and-harm", "indication-setting-time-and-follow-up", "Treatment binds a declared indication to delivered therapeutic action, comparator, response, harm and follow-up rather than to intent alone."),
    row("REHABILITATION", "Rehabilitation", FAMILY_ORDER[9], "person-function-and-participation-state", "iterated-action-to-capacity-change", "goals-interventions-context-and-course", "baseline-follow-up-and-lived-setting", "Rehabilitation is an iterated, goal-bound relation among intervention, function, participation and lived context across retained timepoints."),
    row("MONITORING", "Clinical monitoring", FAMILY_ORDER[9], "ordered-patient-measurements", "change-to-decision-relation", "schedule-threshold-action-trace", "method-interval-and-care-context", "Monitoring is a predeclared sequence of measurements and action rules; the measurement history may not be replaced by the latest value."),
    row("STOPPING-WITHDRAWAL", "Stopping and withdrawal", FAMILY_ORDER[9], "ongoing-care-and-patient-state", "stop-continue-change-decision", "reason-transition-and-aftercare", "decision-time-and-follow-up", "Stopping or withdrawal is a recorded care transition with reason, alternative, taper or aftercare and post-transition outcomes held."),

    # Individual versus population inference — 6
    row("INDIVIDUAL-INFERENCE", "Individual clinical inference", FAMILY_ORDER[10], "one-patient-evidence-word", "evidence-to-patient-support", "alternatives-and-uncertainty-held", "patient-values-context-and-time", "Individual inference conditions only on the available patient evidence and preserves unsupported alternatives, values, context and uncertainty."),
    row("POPULATION-INFERENCE", "Population clinical inference", FAMILY_ORDER[10], "sample-and-source-population", "sample-to-population-relation", "selection-weights-and-missingness", "eligibility-place-time-and-method", "Population inference requires an explicit sample-to-source relation with selection, missingness, eligibility, place and time retained."),
    row("TRANSPORTABILITY", "Clinical transportability", FAMILY_ORDER[10], "source-and-target-populations", "invariant-and-different-features", "joint-population-treatment-outcome", "setting-time-and-care-system", "Transportability requires explicit source-target comparison and may carry only relations invariant under every retained population and setting difference."),
    row("SUBGROUP-MULTIPLICITY", "Subgroups and multiplicity", FAMILY_ORDER[10], "generated-subgroup-comparisons", "comparison-count-and-result-incidence", "complete-tested-family", "predeclaration-and-selection-boundary", "Every generated subgroup and outcome comparison remains in one complete family so selection after outcomes cannot masquerade as prior inference."),
    row("CLINICAL-DECISION", "Clinical decision boundary", FAMILY_ORDER[10], "patient-action-alternatives", "evidence-consequence-preference-relation", "all-actions-outcomes-and-values", "decision-maker-time-and-resource-boundary", "A clinical decision composes evidence with explicit actions, consequences and patient values; a population average cannot uniquely select an individual action."),
    row("CLINICAL-UNCERTAINTY", "Clinical uncertainty", FAMILY_ORDER[10], "retained-admissible-clinical-states", "evidence-conditioned-support", "known-missing-and-unknown-record", "decision-and-observation-boundary", "Clinical uncertainty is the exact retained support after available evidence, including known missingness and unresolved alternatives, not an ontological nondeterminism claim."),

    # Consent, ethics, privacy and uncertainty boundaries — 6
    row("INFORMED-CONSENT", "Informed consent boundary", FAMILY_ORDER[11], "person-information-choice-record", "understanding-voluntariness-authorization", "versioned-scope-and-withdrawal", "purpose-time-capacity-and-recorder", "A consent record is valid only for its declared person, information, understanding, voluntariness, purpose, scope and time, with refusal and withdrawal retained."),
    row("DECISION-CAPACITY", "Decision capacity boundary", FAMILY_ORDER[11], "person-decision-context", "understand-retain-weigh-communicate", "decision-specific-support-and-assistance", "time-decision-and-assessment-method", "Capacity is decision- and time-specific evidence over retained abilities and assistance; diagnosis or status alone cannot erase the person's choice."),
    row("CLINICAL-PRIVACY", "Clinical privacy", FAMILY_ORDER[11], "person-linked-health-record", "purpose-bound-access-and-disclosure", "identity-content-recipient-trace", "consent-law-purpose-and-time", "Clinical privacy requires purpose-bound access, minimized disclosure and a complete identity-content-recipient-time trace; public evidence may not expose an unnecessary person link."),
    row("DATA-MINIMIZATION", "Clinical data minimization", FAMILY_ORDER[11], "purpose-declared-data-fields", "field-necessity-to-purpose", "included-excluded-and-derived-fields", "protocol-access-and-retention-period", "A clinical dataset may retain only fields forced by its declared purpose while preserving an auditable record of exclusion, derivation, access and retention."),
    row("CLINICAL-EQUIPOISE", "Clinical equipoise and stopping boundary", FAMILY_ORDER[11], "competing-care-support", "unresolved-comparative-benefit-harm", "monitoring-and-stopping-rules", "evidence-date-population-and-oversight", "A comparative study remains admissible only while its declared evidence support leaves the care alternatives unresolved and its harm-stopping rules remain active."),
    row("CLINICAL-EVIDENCE-HANDOFF", "Clinical evidence handoff", FAMILY_ORDER[11], "consented-deidentified-evidence-record", "claim-to-reviewer-reconstruction", "derivation-data-code-adverse-results", "purpose-access-version-and-custody", "A medical claim may cross to a reviewer only with reconstructible derivation, data provenance, code, adverse/null/unresolved rows, privacy boundary and custody record."),
)


def validate_obligations() -> None:
    if len(MEDICINE_OBLIGATIONS) != 72:
        raise ValueError("Medicine foundational obligation count changed")
    if len({row.claim_id for row in MEDICINE_OBLIGATIONS}) != len(MEDICINE_OBLIGATIONS):
        raise ValueError("Medicine claim identities repeat")
    counts = Counter(row.family for row in MEDICINE_OBLIGATIONS)
    if tuple(counts) != FAMILY_ORDER or any(counts[name] != 6 for name in FAMILY_ORDER):
        raise ValueError("Medicine foundation must contain exactly six obligations in each ordered family")
    for item in MEDICINE_OBLIGATIONS:
        if not item.claim_id.startswith("SFT-MED-"):
            raise ValueError("invalid Medicine claim prefix")
        if not all((item.title, item.carrier, item.relation, item.organization, item.observation, item.statement)):
            raise ValueError(f"empty Medicine obligation field: {item.claim_id}")


validate_obligations()

__all__ = ("FAMILY_ORDER", "MedicineObligation", "MEDICINE_OBLIGATIONS", "validate_obligations")

