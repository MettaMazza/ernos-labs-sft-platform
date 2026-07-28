"""Post-seal empirical boundaries for the Consciousness foundation.

These bindings do not derive a law from literature.  They state which
consequence of each already sealed family can be tested by the preregistered
external source set, and which evidence boundary remains inaccessible.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.consciousness_cognitive_science.generated_law import CONSCIOUSNESS_BLUEPRINTS
from sft.consciousness_cognitive_science.obligations import CONSCIOUSNESS_OBLIGATIONS
from sft.consciousness_cognitive_science.sources import FAMILY_SOURCE_IDS, SOURCE_BY_ID


EXTERNAL_TARGETS_PATH = "experiments/consciousness/claim_specific_external_targets.json"
SOURCE_FEATURE_AUDIT_PATH = "experiments/consciousness/source_feature_audit.json"


@dataclass(frozen=True)
class FamilyConsequence:
    family: str
    expected_label: str
    evidence_scope: str
    empirical_disposition: str
    minimum_complete_sources: int


FAMILY_CONSEQUENCES = (
    FamilyConsequence("observation_interior_observation", "report-and-interior-observation-nonidentity-preserved", "Report/no-report experiments constrain observable registration while methodological adverse evidence forbids report-free signals from being relabelled as direct phenomenal access.", "mixed_boundary_constraint", 1),
    FamilyConsequence("access_report_presence", "access-report-and-presence-nonidentity-preserved", "Report/no-report and adversarial experiments test access and report correlates; phenomenal occurrence remains a separately named evidential coordinate.", "mixed_boundary_constraint", 1),
    FamilyConsequence("binding_unity", "integration-and-unity-evidence-boundary-preserved", "Split-brain and adversarial records test integration while preserving disagreement about whether a single phenomenal whole has been established.", "mixed_and_adverse_constraint", 1),
    FamilyConsequence("subject_perspective_interiority", "first-and-third-person-evidence-nonidentity-preserved", "External integration and no-report records constrain behavior and access but cannot replace the participant's first-person evidence class.", "boundary_constraint", 1),
    FamilyConsequence("self_observation_introspection", "introspective-report-and-retained-history-nonidentity-preserved", "Choice-blindness manipulation directly tests the boundary between reported reasons and the trace available to the reporter.", "direct_behavioural_constraint", 1),
    FamilyConsequence("memory_temporal_identity", "memory-report-state-and-lineage-boundary-preserved", "Dream and anesthesia-recovery records test changing availability and report across state transitions without making report alone numerical identity.", "direct_and_boundary_constraint", 1),
    FamilyConsequence("finite_self_model", "finite-self-model-remains-formal-with-empirical-representation-boundary", "Choice-blindness and open adversarial datasets constrain self-report and model representation; they do not directly observe a complete internal self-model.", "formal_with_external_boundary", 1),
    FamilyConsequence("attention_availability", "attention-selection-and-awareness-nonidentity-observed", "Attentional-blink and report/no-report evidence directly distinguish selection likelihood, representation precision, awareness and report.", "direct_psychophysical_constraint", 1),
    FamilyConsequence("cognition_inference_representation", "representation-inference-and-observation-boundary-preserved", "Attentional and multimodal adversarial records constrain representation and access while later outcome remains distinct from a sealed prediction.", "operational_and_boundary_constraint", 1),
    FamilyConsequence("substrate_realization", "realization-evidence-bound-without-theory-or-output-substitution", "Multimodal adversarial evidence tests physical realizations and competing predictions but does not turn a favored theory, signal or fluent output into consciousness.", "cross_substrate_boundary_constraint", 1),
    FamilyConsequence("qualia_resonance_composition", "within-subject-quality-reidentification-with-public-private-boundary", "Within-subject consistency and test–retest observations support stable reidentification while learned-category controls forbid public labels from being equated with private qualitative identity.", "direct_participant_bound_constraint", 2),
    FamilyConsequence("red_of_red", "physical-red-and-private-red-quality-nonidentity-with-reidentification-evidence", "CIE stimulus records, participant consistency, synesthetic-colour evidence and learned-category controls jointly test reidentification while direct third-person possession of another subject's red remains unclaimed.", "direct_participant_bound_and_boundary_constraint", 3),
)


CONSEQUENCE_BY_FAMILY = {row.family: row for row in FAMILY_CONSEQUENCES}


@dataclass(frozen=True)
class ClaimExternalBinding:
    claim_id: str
    family: str
    source_ids: tuple[str, ...]
    expected_label: str
    evidence_scope: str
    empirical_disposition: str
    minimum_complete_sources: int
    directness: str


def _directness(evidence_boundary: str) -> str:
    lowered = evidence_boundary.casefold()
    if "formal" in lowered and not any(token in lowered for token in ("behaviour", "psychophysical", "first-person", "clinical", "biological")):
        return "formal_reconstruction_with_external_boundary_only"
    if "first-person" in lowered or "phenomenal" in lowered or "private" in lowered:
        return "participant_bound_empirical_constraint"
    if "psychophysical" in lowered or "behaviour" in lowered or "report" in lowered:
        return "direct_observable_constraint"
    if "cross" in lowered or "realization" in lowered or "handoff" in lowered:
        return "cross_domain_correspondence_constraint"
    return "operational_or_record_constraint"


CLAIM_EXTERNAL_BINDINGS = tuple(
    ClaimExternalBinding(
        claim_id=blueprint.claim_id,
        family=blueprint.family,
        source_ids=FAMILY_SOURCE_IDS[blueprint.family],
        expected_label=CONSEQUENCE_BY_FAMILY[blueprint.family].expected_label,
        evidence_scope=CONSEQUENCE_BY_FAMILY[blueprint.family].evidence_scope,
        empirical_disposition=CONSEQUENCE_BY_FAMILY[blueprint.family].empirical_disposition,
        minimum_complete_sources=CONSEQUENCE_BY_FAMILY[blueprint.family].minimum_complete_sources,
        directness=_directness(next(row.evidence_boundary for row in CONSCIOUSNESS_OBLIGATIONS if row.claim_id == blueprint.claim_id)),
    )
    for blueprint in CONSCIOUSNESS_BLUEPRINTS
)
CLAIM_BINDING_BY_ID = {row.claim_id: row for row in CLAIM_EXTERNAL_BINDINGS}


def validate_bindings() -> None:
    if len(CLAIM_BINDING_BY_ID) != len(CONSCIOUSNESS_BLUEPRINTS):
        raise ValueError("Consciousness external bindings do not cover the frozen inventory")
    if set(CONSEQUENCE_BY_FAMILY) != set(FAMILY_SOURCE_IDS):
        raise ValueError("Consciousness family consequence coverage differs from source registration")
    for binding in CLAIM_EXTERNAL_BINDINGS:
        if not binding.source_ids or any(source_id not in SOURCE_BY_ID for source_id in binding.source_ids):
            raise ValueError("Consciousness binding contains an absent source identity")
        if binding.minimum_complete_sources < 1 or binding.minimum_complete_sources > len(binding.source_ids):
            raise ValueError("Consciousness evidence threshold is outside its registered source set")


validate_bindings()


__all__ = (
    "CLAIM_BINDING_BY_ID",
    "CLAIM_EXTERNAL_BINDINGS",
    "CONSEQUENCE_BY_FAMILY",
    "EXTERNAL_TARGETS_PATH",
    "SOURCE_FEATURE_AUDIT_PATH",
    "ClaimExternalBinding",
    "FamilyConsequence",
    "validate_bindings",
)
