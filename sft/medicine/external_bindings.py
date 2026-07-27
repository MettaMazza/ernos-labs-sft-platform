"""Claim-specific post-seal Medicine authority bindings."""

from __future__ import annotations

from dataclasses import dataclass

from sft.medicine.obligations import MEDICINE_OBLIGATIONS


@dataclass(frozen=True)
class SourceRequirement:
    source_id: str
    fragment: str


@dataclass(frozen=True)
class MedicineBinding:
    claim_id: str
    requirements: tuple[SourceRequirement, ...]


def req(source_id: str, fragment: str) -> SourceRequirement:
    return SourceRequirement(source_id, fragment)


FAMILY_REQUIREMENTS = {
    "patient_population_health": (req("MED-WHO-HEALTH-001", "physical, mental and social well-being"), req("MED-ICH-E6R3-001", "rights, safety and well-being")),
    "variation_dysfunction_disease_injury": (req("MED-FDA-BIOMARKER-001", "normal biological processes"), req("MED-FDA-BIOMARKER-001", "pathogenic processes"), req("MED-CDC-EPIDEMIOLOGY-001", "disease and injury occurrence")),
    "symptom_sign_measurement_diagnosis": (req("MED-FDA-BIOMARKER-001", "feels, functions, or survives"), req("MED-FDA-BIOMARKER-001", "source/matrix"), req("MED-FDA-BIOMARKER-001", "analytic method"), req("MED-FDA-BIOMARKER-001", "diagnostic")),
    "cause_association_mechanism_confounding": (req("MED-CDC-EPIDEMIOLOGY-001", "frequency, patterns, and causes"), req("MED-CDC-EPIDEMIOLOGY-001", "population and comparison"), req("MED-STROBE-001", "what was planned")),
    "risk_prognosis_outcome": (req("MED-FDA-BIOMARKER-001", "susceptibility/risk"), req("MED-FDA-BIOMARKER-001", "prognostic"), req("MED-ICH-E9R1-001", "population of interest"), req("MED-ICH-E9R1-001", "intercurrent events")),
    "intervention_comparator_counterfactual": (req("MED-ICH-E6R3-001", "trial protocol"), req("MED-ICH-E6R3-001", "randomisation"), req("MED-ICH-E6R3-001", "blinding"), req("MED-ICH-E9R1-001", "treatment effect")),
    "dose_exposure_response_adverse_event": (req("MED-FDA-EXPOSURE-RESPONSE-001", "exposure-response"), req("MED-ICH-E6R3-001", "adverse event"), req("MED-FDA-BIOMARKER-001", "responses to an exposure or intervention")),
    "efficacy_effectiveness_safety_benefit_harm": (req("MED-ICH-E6R3-001", "rights, safety and well-being"), req("MED-ICH-E9R1-001", "population-level summary"), req("MED-COCHRANE-HANDBOOK-001", "Adverse effects")),
    "trial_observational_synthesis": (req("MED-ICH-E6R3-001", "quality by design"), req("MED-STROBE-001", "what was done"), req("MED-STROBE-001", "what was found"), req("MED-COCHRANE-MISSING-EVIDENCE-001", "missing evidence")),
    "screening_prevention_treatment_rehabilitation": (req("MED-WHO-SCREENING-001", "apparently healthy population"), req("MED-WHO-SCREENING-001", "maximize benefits and minimize harm"), req("MED-NICHD-REHABILITATION-001", "maximize function, participation, independence, and quality of life")),
    "individual_population_inference": (req("MED-ICH-E9R1-001", "population of interest"), req("MED-ICH-E9R1-001", "missing data"), req("MED-ICH-E9R1-001", "sensitivity analysis"), req("MED-CDC-EPIDEMIOLOGY-001", "health-related states or events in populations")),
    "consent_ethics_privacy_uncertainty": (req("MED-ICH-E6R3-001", "informed consent"), req("MED-ICH-E6R3-001", "confidentiality"), req("MED-ICH-E6R3-001", "essential records"), req("MED-COCHRANE-MISSING-EVIDENCE-001", "selective dissemination")),
}


MEDICINE_BINDINGS = tuple(MedicineBinding(row.claim_id, FAMILY_REQUIREMENTS[row.family]) for row in MEDICINE_OBLIGATIONS)
BINDING_BY_CLAIM = {row.claim_id: row for row in MEDICINE_BINDINGS}


def validate_bindings() -> None:
    if len(BINDING_BY_CLAIM) != len(MEDICINE_OBLIGATIONS):
        raise ValueError("Medicine bindings do not cover the frozen inventory exactly")
    if any(not row.requirements for row in MEDICINE_BINDINGS):
        raise ValueError("Medicine claim lacks a purpose-matched source requirement")
    if any(requirement.source_id.startswith("MED-HHS-") for row in MEDICINE_BINDINGS for requirement in row.requirements):
        raise ValueError("A failed Medicine source transport may not support a passing claim")


validate_bindings()

__all__ = ("SourceRequirement", "MedicineBinding", "MEDICINE_BINDINGS", "BINDING_BY_CLAIM", "validate_bindings")
