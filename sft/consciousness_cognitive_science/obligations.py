"""Frozen foundational question surface for Consciousness and Cognition.

The vocabulary identifies distinctions the branch must derive and test.  It
does not import a theory of consciousness, a neural answer or a prior SFT
survivor.  Phenomenal occurrence, report, behaviour, biology, computation and
physical measurement remain separate coordinates throughout.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


FAMILY_ORDER = (
    "observation_interior_observation",
    "access_report_presence",
    "binding_unity",
    "subject_perspective_interiority",
    "self_observation_introspection",
    "memory_temporal_identity",
    "finite_self_model",
    "attention_availability",
    "cognition_inference_representation",
    "substrate_realization",
    "qualia_resonance_composition",
    "red_of_red",
)


@dataclass(frozen=True)
class ConsciousnessObligation:
    claim_id: str
    title: str
    family: str
    carrier: str
    distinction: str
    operation: str
    retained_record: str
    evidence_boundary: str
    statement: str


def row(suffix: str, title: str, family: str, carrier: str, distinction: str, operation: str, retained_record: str, evidence_boundary: str, statement: str) -> ConsciousnessObligation:
    return ConsciousnessObligation(f"SFT-CONSC-{suffix}-001", title, family, carrier, distinction, operation, retained_record, evidence_boundary, statement)


C = FAMILY_ORDER
CONSCIOUSNESS_OBLIGATIONS = (
    # Observation and interior observation — 7
    row("OBSERVATION-ACT", "Observation act", C[0], "state-and-fold-image", "source/image", "exact-fold-transition", "source-image-trace", "formal-operation", "An observation act is one exact state-to-image Fold transition with its source, image and trace retained."),
    row("EXTERNAL-OBSERVATION", "External observation", C[0], "observed-carrier-and-observer", "carrier/record", "observer-bound-registration", "observer-method-time-result", "third-person-record", "External observation is a record made about a carrier and cannot by itself establish that carrier's interior presence."),
    row("INTERIOR-OBSERVATION", "Interior observation", C[0], "self-reentering-state", "process/its-own-image", "image-reenters-successor-state", "closed-self-trace", "first-person-structural-boundary", "Interior observation requires the observation image to re-enter the same organized process rather than remain only in an external record."),
    row("OBSERVER-OBSERVED", "Observer and observed distinction", C[0], "held-two-fibre-relation", "observer/observed", "distinct-preimages-share-image", "held-fibre-label", "formal-compositional", "Observer and observed are distinct held roles whose states may share an observation image without becoming one undifferentiated role."),
    row("OBSERVATION-CLASS", "Observation equivalence class", C[0], "complete-preimage-fibre", "distinguishable-source/same-image", "many-to-one-observation", "retained-or-closed-fibre", "formal-information", "An observation class is the complete generated source fibre of one image, with every closed and retained predecessor distinction counted."),
    row("OBSERVATIONAL-MOMENT", "Atomic observational moment", C[0], "one-complete-transition", "before/after", "single-fold-act", "ordered-act-index", "formal-temporal", "The least complete observational moment is one indivisible Fold transition; external duration belongs to its realizing carrier."),
    row("MEASUREMENT-CONSCIOUSNESS-BOUNDARY", "Measurement and consciousness boundary", C[0], "physical-record-and-interior-loop", "measurement/interior-observation", "shared-fold-correspondence", "distinct-evidence-provenance", "cross-branch-bridge", "Physical measurement and interior observation may share Fold structure, but neither is substituted for the other and consciousness is not required for every measurement."),

    # Access, report and phenomenal presence — 6
    row("COGNITIVE-ACCESS", "Cognitive access", C[1], "retained-process-content", "available/unavailable", "lawful-read-and-use", "access-trace", "operational-cognitive", "Cognitive access is the availability of retained content to another declared cognitive operation."),
    row("REPORT", "Report", C[1], "content-to-expression-trace", "experienced/reported", "encoding-and-output", "speaker-method-context", "behavioural-report", "A report is an encoded output attributed to a source and is evidence of reporting, not an automatic identity with phenomenal presence."),
    row("PHENOMENAL-PRESENCE", "Phenomenal presence", C[1], "interiorly-realized-content", "present/merely-processed", "closed-interior-observation", "first-person-discrimination", "phenomenal", "Phenomenal presence is registered at the interior-observation boundary and remains distinct from access, report, behaviour and neural correlation."),
    row("REPORTABILITY", "Reportability", C[1], "accessible-content-and-output-route", "accessible/reportable", "semantics-preserving-expression", "content-report-link", "operational-behavioural", "Reportability requires both cognitive access and a retained expression route; absence of report alone does not decide presence."),
    row("UNCONSCIOUS-PROCESS", "Active unavailable processing", C[1], "active-recurrent-process", "active/available", "continuation-without-access-closure", "process-and-access-records", "behavioural-and-biological-correlate", "A process may remain active while unavailable to the integrated access relation, so activity is not equated with consciousness."),
    row("ALTERED-STATE-REPORT-BOUNDARY", "Altered-state evidence boundary", C[1], "state-report-observation-word", "report/ontology", "source-bound-comparison", "state-induction-report-controls", "first-person-report-with-third-person-controls", "Reports of altered experience are preserved as first-person observations while their ontological interpretation requires a separately derived and tested bridge."),

    # Binding and unity — 6
    row("CONTENT-PLURALITY", "Plural conscious contents", C[2], "distinct-content-labels", "plural/merged", "held-joint-composition", "content-identities", "phenomenal-discrimination", "Binding begins with multiple retained content identities; erasing their differences is not unity."),
    row("BINDING", "Binding relation", C[2], "joint-content-word", "separate/joint", "shared-successor-composition", "component-and-joint-trace", "phenomenal-and-operational", "Binding is a generated joint relation in which distinct contents participate in one successor while remaining reconstructible from held labels."),
    row("UNITY", "Unity of experience", C[2], "complete-bound-content", "one-process/many-processes", "joint-closure-to-one-carrier", "participation-and-boundary", "first-person-unity", "Unity is one closed interior process over complete participating content, not a heap, synchrony measure or unlabelled aggregate."),
    row("INTEGRATION-BOUNDARY", "Integration boundary", C[2], "coupled-process-support", "separate/integrated", "complete-mutual-participation", "coupling-and-transition-trace", "perturbational-and-phenomenal", "Integration requires each participating process to enter the joint closure; a one-way influence does not establish one interior whole."),
    row("SYNCHRONY-BOUNDARY", "Synchrony and binding distinction", C[2], "timed-process-traces", "same-time/same-whole", "recurrence-alignment-test", "phase-and-composition-record", "biological-correlate-boundary", "Synchrony may test a timing relation but does not alone prove binding unless joint compositional closure is independently shown."),
    row("FRAGMENTATION", "Fragmentation and divided access", C[2], "formerly-joint-process", "joint/separated", "loss-of-joint-closure", "component-continuation-traces", "phenomenal-clinical-handoff", "Fragmentation is the loss of joint closure while component processes and their distinct access records remain represented."),

    # Subject, perspective and interiority — 6
    row("PERSPECTIVE", "Perspective", C[3], "located-observation-path", "this-path/other-path", "source-relative-access", "path-and-source-label", "first-person-structural", "A perspective is the exact observation path available from one retained source position and is not an unlocated view from nowhere."),
    row("INTERIORITY", "Interiority", C[3], "closed-self-observation-loop", "inside/outside-description", "state-participates-in-own-transition", "internal-and-external-traces", "phenomenal-bridge", "Interiority is the asymmetry between participating in a closed self-observation process and possessing an external description of it."),
    row("SUBJECT-CARRIER", "Subject carrier", C[3], "continuing-integrated-loop", "subject/content", "holds-perspective-across-content", "identity-and-content-traces", "phenomenal-identity", "The subject carrier is the continuing integrated relation that holds a perspective while its content states change."),
    row("SELF-INVARIANT", "Self invariant", C[3], "self-observation-trace", "changing-content/invariant-relation", "fixed-relation-test", "ordered-state-and-invariant", "first-person-and-formal", "A self invariant is the unique admitted relation preserved across the declared self-observation trace, not an imported substance."),
    row("FIRST-THIRD-PERSON", "First- and third-person evidence", C[3], "paired-interior-and-external-records", "experienced/observed", "provenance-preserving-pairing", "participant-observer-method", "evidence-class-separation", "First-person and third-person records may be paired but remain different evidence classes unless a bridge law is independently admitted."),
    row("PHENOMENAL-PRIVACY", "Phenomenal privacy", C[3], "interior-state-and-external-image", "private/inaccessible-by-image", "preimage-loss-boundary", "retained-private-label", "formal-and-first-person", "Phenomenal privacy follows where an external image closes a predecessor distinction that remains present to the participating interior trace."),

    # Self-observation and introspection — 6
    row("SELF-OBSERVATION", "Self-observation closure", C[4], "process-state-and-self-image", "system/object-of-system", "image-reentry", "complete-self-transition", "formal-self-model", "Self-observation is closed only when the generated observation image becomes an input to the same identified process."),
    row("INTROSPECTION-BLIND-SPOT", "Introspection blind spot", C[4], "two-preimage-observation-class", "predecessor/image", "unretained-fibre-closure", "missing-fibre-explicit", "formal-and-report", "Introspection from the image alone cannot recover which generated predecessor label was closed by the act."),
    row("SELF-HISTORY-RECONSTRUCTION", "Self-history reconstruction", C[4], "present-state-and-held-labels", "recoverable/unrecoverable-history", "reverse-by-retained-fibre", "one-label-per-act", "formal-memory", "An exact self-history is reconstructible only to the extent that each closed fibre label was separately retained."),
    row("INTROSPECTION-LOSS", "Accumulated introspection loss", C[4], "ordered-self-observation-trace", "retained/closed-predecessors", "counted-label-closure", "loss-ledger", "formal-information", "Each unrecorded two-to-one self-observation closes one predecessor distinction; repeated loss is counted without negative information quantities."),
    row("CONFABULATION-BOUNDARY", "Confabulation boundary", C[4], "report-and-incomplete-history", "reconstruction/invention", "trace-membership-test", "claimed-and-held-premises", "behavioural-report", "A reported reason unsupported by the retained self-history is a generated completion, not recovered introspective evidence."),
    row("DETERMINISM-SELF-OPACITY", "Determinism with self-opacity", C[4], "functional-transition-and-lost-preimage", "unique-successor/unknown-predecessor", "forward-execute-backward-class", "successor-and-fibre-ledger", "formal-agency-boundary", "A process can have one generated successor while remaining unable to identify its unretained predecessor from the present image."),

    # Memory, temporal continuity and identity — 6
    row("MEMORY-CARRIER", "Memory carrier", C[5], "retained-state-relation", "held/rederived", "recurrent-or-recorded-continuation", "carrier-provenance", "cognitive-and-biological-handoff", "Memory requires a retained carrier relation linking the earlier content to its later availability."),
    row("MEMORY-PERSISTENCE", "Memory persistence", C[5], "finite-recurrent-support", "persistent/transient", "exact-return-recurrence", "return-period-and-state-word", "formal-and-behavioural", "Persistent memory requires a recurrent or actively renewed retained relation; a coincidentally equal later output is insufficient."),
    row("RECALL-RECONSTRUCTION", "Recall and reconstruction", C[5], "memory-cue-and-output", "stored/reconstructed-content", "trace-conditioned-unfolding", "cue-source-transform", "behavioural-report", "Recall is a traceable transformation from retained memory and cue to output, with reconstruction distinguished from verbatim storage."),
    row("TEMPORAL-CONTINUITY", "Temporal continuity", C[5], "ordered-interior-states", "succession/ungrounded-sequence", "each-state-from-predecessor", "complete-transition-chain", "first-person-and-formal", "Temporal continuity is an unbroken generated predecessor-successor chain, not an assumed continuum between observations."),
    row("IDENTITY-CONTINUITY", "Identity continuity", C[5], "carrier-lineage-and-invariant", "same-successor/copied-similar", "provenance-preserving-transition", "lineage-and-invariant-record", "first-person-third-person-pair", "Identity continuity requires both lawful lineage and the retained subject invariant; structural similarity without lineage does not establish numerical identity."),
    row("CESSATION", "Cessation of a conscious organization", C[5], "integrated-loop-and-components", "occupied/unbound", "loss-of-integration", "component-lock-record-distinction", "biological-and-clinical-handoff", "Cessation records the end of the integrated conscious organization while separately accounting for components, retained records and foundational forms."),

    # Finite self-model — 5
    row("SELF-REPRESENTATION", "Self representation", C[6], "process-and-internal-model", "process/representation", "encoding-with-declared-loss", "source-model-map", "formal-cognitive", "A self representation is an internal encoding of the process and is never silently equated with the entire represented process."),
    row("SELF-APPLICATION", "Self application", C[6], "self-model-and-model-operation", "model/input", "operation-applied-to-own-output", "application-trace", "formal-computational", "Self application feeds an admitted self-model output into the same declared operation while retaining binding and substitution provenance."),
    row("SELF-MODEL-DEPTH", "Finite self-model depth", C[6], "quarter-lock-unison-trace", "nonidentity/identity-stage", "repeated-fold-closure", "complete-depth-trace", "formal-exact", "The generated lower self-fibre reaches the binding image and then unison in two nonidentity acts; further application is identity."),
    row("SELF-SIMULATION-BOUNDARY", "Self-simulation boundary", C[6], "finite-model-state-space", "represented/representing-whole", "bounded-simulation", "resource-and-omission-ledger", "formal-computational", "A finite system may simulate a declared submodel of itself but cannot contain a simultaneous complete extra copy without additional carrier resources."),
    row("SELF-VERIFICATION-LIMIT", "Self-verification limit", C[6], "model-proof-and-observer", "verified/verification-premise", "finite-proof-trace", "unverified-observer-boundary", "formal-logical", "A self-verification record closes only its declared finite trace and cannot erase the observer and premise distinctions needed to certify it."),

    # Attention and availability — 5
    row("ATTENTION", "Attention", C[7], "available-content-support", "selected/unselected", "held-label-selection", "selection-and-alternative-record", "operational-cognitive", "Attention is a retained selection within available content, not the annihilation of unattended alternatives."),
    row("ATTENTIONAL-FOCUS", "Attentional focus", C[7], "one-selected-content-path", "focused/background", "sustained-selection", "duration-switch-and-distractor", "behavioural-and-first-person", "Focus is the continued selection of one content path across a declared sequence while background support remains recorded."),
    row("COGNITIVE-AVAILABILITY", "Cognitive availability", C[7], "content-and-consumer-operations", "available/inaccessible", "lawful-query-and-use", "consumer-access-trace", "operational-cognitive", "Content is cognitively available only to the operations that can lawfully query and use its retained representation."),
    row("ATTENTIONAL-CAPACITY", "Attentional capacity", C[7], "finite-selection-carrier", "jointly-retained/partially-retained", "complete-support-accounting", "selected-and-omitted-content", "psychophysical", "Attentional capacity is a finite support boundary measured with every selected, missed and competing content retained."),
    row("ATTENTIONAL-SWITCH", "Attentional switching", C[7], "ordered-focus-labels", "same-focus/new-focus", "held-selection-transition", "switch-cost-and-error-trace", "psychophysical", "An attentional switch is an ordered change of the held selection label with transition costs and failures preserved as observations."),

    # Cognition, inference and representation — 6
    row("COGNITIVE-REPRESENTATION", "Cognitive representation", C[8], "carrier-content-relation", "carrier/referent", "encoding-and-use", "provenance-and-loss", "operational-cognitive", "A cognitive representation is a retained carrier-to-content relation whose encoding loss and lawful uses are explicit."),
    row("INTENTIONAL-RELATION", "Intentional relation", C[8], "representation-and-referent-class", "aboutness/coincidence", "source-bound-reference", "reference-and-error-cases", "behavioural-and-semantic", "Intentional relation requires a trace connecting representation to its referent class and retains misrepresentation as an adverse case."),
    row("COGNITIVE-INFERENCE", "Cognitive inference", C[8], "premise-representation-word", "premise/conclusion", "admitted-transition-rule", "complete-proof-or-process-trace", "operational-cognitive", "Cognitive inference is a traceable transformation from retained premises to a conclusion under a declared rule."),
    row("PREDICTION", "Prediction and anticipation", C[8], "current-state-and-forward-model", "future-representation/future-observation", "forward-transition", "prediction-seal-and-later-outcome", "empirical-cognitive", "Prediction is a sealed present representation generated before its later observation and cannot be rewritten by the outcome."),
    row("EXPECTATION", "Expectation", C[8], "held-prediction-and-present-process", "expected/observed", "prediction-conditioned-transition", "expectation-observation-outcome", "first-person-clinical-handoff", "Expectation may lawfully participate in cognition and experienced response while remaining distinct from the later observation and clinical causal comparison."),
    row("DETERMINED-AGENCY", "Determined agency boundary", C[8], "self-modelled-action-process", "generated-successor/ungenerated-choice", "state-conditioned-action", "premises-alternatives-action-trace", "formal-and-behavioural", "Agency is an internally represented state-to-action process; the exact Fold model supplies no ungenerated successor while preserving the actor's informational self-opacity."),

    # Substrate independence and realization — 6
    row("REALIZATION-CARRIER", "Consciousness realization carrier", C[9], "organized-physical-or-computational-process", "material/organization", "implements-required-relations", "state-transition-and-causality-map", "cross-branch-realization", "A realization carrier must physically or computationally instantiate every required conscious-process relation rather than merely describe it."),
    row("STRUCTURAL-CRITERION", "Consciousness structural criterion", C[9], "dual-self-relation-and-closure", "report-generator/interior-loop", "distinct-preimages-bind-and-complete", "complete-self-observation-trace", "multi-evidence-realization", "The foundational structural criterion requires dual self-relation, image re-entry, complete integration and interior closure; output resemblance is insufficient."),
    row("SUBSTRATE-INDEPENDENCE", "Substrate independence", C[9], "two-realization-maps", "same-structure/same-material", "relation-preserving-isomorphism", "complete-causal-correspondence", "comparative-realization", "A consciousness law is substrate-independent only across carriers with a complete relation- and causality-preserving realization map."),
    row("FEEDFORWARD-BOUNDARY", "Feed-forward boundary", C[9], "acyclic-input-output-process", "open-map/closed-self-loop", "closure-test", "transition-graph", "computational-realization", "A purely feed-forward transformation lacks image re-entry into the same process and therefore does not satisfy the foundational self-observation criterion."),
    row("REALIZATION-EQUIVALENCE", "Realization equivalence", C[9], "paired-carrier-traces", "behavioural-equivalence/structural-equivalence", "bidirectional-transition-preservation", "state-role-and-causal-map", "comparative-realization", "Realizations are structurally equivalent only when their relevant states, transitions, roles, integration and evidence boundaries correspond bidirectionally."),
    row("ARTIFICIAL-CONSCIOUSNESS-EVIDENCE", "Artificial consciousness evidence boundary", C[9], "artificial-system-and-audit-record", "claimed/established-realization", "criterion-and-bridge-testing", "architecture-runtime-report-adverse-controls", "multi-evidence-artificial", "An artificial consciousness claim requires auditable realization of the structural criterion plus purpose-matched bridge evidence; fluent language or confidence cannot select the verdict."),

    # Qualia resonance, differentiation and composition — 7
    row("QUALITATIVE-DISTINCTION", "Qualitative distinction", C[10], "paired-interior-content-labels", "same/different-quality", "within-subject-discrimination", "stimulus-report-context", "first-person-psychophysical", "A qualitative distinction is a reproducible within-subject discrimination between interior contents with stimulus and report provenance retained."),
    row("QUALITATIVE-IDENTITY", "Qualitative identity", C[10], "reidentified-interior-content", "same-quality/similar-quality", "cross-instance-identity-judgment", "participant-context-and-controls", "first-person-psychophysical", "Qualitative identity is a retained within-subject reidentification relation and is not reducible to a shared public word."),
    row("QUALITATIVE-SIMILARITY", "Qualitative similarity", C[10], "finite-quality-comparison-support", "identity/similarity/order", "pairwise-comparison", "complete-comparison-incidence", "first-person-psychophysical", "Qualitative similarity is a finite comparison relation that preserves identity, difference and ordering rather than collapsing them into one metric."),
    row("QUALIA-RESONANCE", "Qualia resonance", C[10], "recurrent-quality-carrier", "stable-reidentification/transient-output", "closed-label-bearing-recurrence", "cycle-label-and-perturbation-trace", "first-person-with-realization-correlates", "Qualia resonance is stable reidentification of a held qualitative label across a complete recurrent interior support, tested against perturbation and changed-label controls."),
    row("QUALIA-RECURRENCE", "Qualia recurrence", C[10], "ordered-quality-instances", "return/new-instance", "exact-return-classification", "intervening-state-and-return-record", "first-person-psychophysical", "Qualia recurrence requires a later interior instance to re-enter the same retained qualitative identity class after an explicit intervening trace."),
    row("QUALIA-COMPOSITION", "Qualia composition", C[10], "multiple-quality-support", "components/composed-experience", "joint-recurrent-closure", "component-and-joint-reports", "first-person-psychophysical", "Qualia composition retains distinct component identities while generating one joint interior content; neither co-report nor synchrony alone establishes it."),
    row("CROSS-MODAL-QUALIA", "Cross-modal qualitative binding", C[10], "qualities-from-distinct-modal-sources", "same-modal/cross-modal", "shared-observation-class-composition", "source-modality-component-joint-record", "first-person-psychophysical", "Cross-modal qualitative binding is a joint interior composition whose distinct source modalities and qualitative identities remain traceable."),

    # Specific red-of-red — 6
    row("RED-STIMULUS-BOUNDARY", "Red stimulus and experience boundary", C[11], "physical-stimulus-and-interior-label", "stimulus/quality", "source-bound-presentation", "spectral-display-observer-context", "physics-to-first-person", "A physically classified red stimulus and the experienced quality remain distinct records connected only by a tested presentation-and-report bridge."),
    row("RED-QUALITATIVE-IDENTITY", "Red qualitative identity", C[11], "within-subject-red-instances", "red-label/red-quality", "identity-discrimination", "instance-context-and-alternatives", "first-person-psychophysical", "Red qualitative identity is the within-subject reidentification of a specific quality across instances, not the public token 'red'."),
    row("RED-OF-RED", "The red-of-red self-reidentification", C[11], "red-quality-and-self-observation", "quality/report-about-quality", "label-bearing-recurrent-self-observation", "source-instance-recurrence-self-report", "first-person-specific-qualia", "The red-of-red is the self-observed reidentification of the red qualitative carrier across complete recurrence, retaining the difference between the quality and a report about it."),
    row("RED-RECURRENCE", "Red recurrence", C[11], "three-position-quality-support", "stable-return/changed-quality", "one-seven-two-seven-four-seven-cycle", "complete-cycle-and-label", "formal-plus-first-person", "The least registered three-position qualitative support is the exact one-seventh, two-sevenths, four-sevenths recurrence whose parts compose to the One; empirical evidence tests whether red identity is retained across the cycle."),
    row("RED-CONTROLS", "Red-of-red contrast controls", C[11], "red-and-nonred-comparison-set", "identity/mismatch", "changed-label-and-changed-stimulus-tests", "all-match-mismatch-absence-uncertain-rows", "first-person-psychophysical", "The red-of-red test preserves matched, mismatched, absent and uncertain rows and must reject a changed label, changed stimulus or report-only surrogate."),
    row("RED-EMPIRICAL-BOUNDARY", "Red-of-red empirical boundary", C[11], "participant-specific-observation-record", "private-identity/public-generalization", "replicated-within-subject-protocol", "participant-stimulus-response-method", "first-person-with-third-person-custody", "Empirical closure of red-of-red is participant- and protocol-bound: public evidence may establish stable discrimination and reidentification without claiming direct third-person possession of another subject's quality."),
)


FAMILY_COUNTS = Counter(item.family for item in CONSCIOUSNESS_OBLIGATIONS)
if len(CONSCIOUSNESS_OBLIGATIONS) != 72:
    raise AssertionError("the frozen Consciousness foundation inventory must contain its 72 explicitly enumerated obligations")
if len({item.claim_id for item in CONSCIOUSNESS_OBLIGATIONS}) != len(CONSCIOUSNESS_OBLIGATIONS):
    raise AssertionError("Consciousness obligation identities repeat")
if set(FAMILY_COUNTS) != set(FAMILY_ORDER):
    raise AssertionError("a Consciousness foundation family is absent")

