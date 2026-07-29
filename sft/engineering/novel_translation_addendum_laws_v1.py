"""No-omission addendum to the sealed Engineering novel-translation family.

The dated prior-return audit contains a sixth protocol obligation that was not
present in the shorter Engineering roadmap summary.  This append-only module
preserves the already admitted five-protocol family and closes the omitted
consciousness/placebo/cross-binding protocol without changing an old source,
receipt, engine file or verification-authority file.
"""

from sft.engine import EvidenceMode
from sft.engineering.novel_translation_laws_v1 import (
    COMMON_FIELDS,
    EngineeringProtocolSpec,
    EngineeringProtocolProgram,
    EXCLUSIONS,
    axes,
    protocol_record,
)
from sft.physics.structural_constants import Witness


PROTOCOL_ID = "SFT-ENG-CONSCIOUSNESS-PLACEBO-CROSS-BINDING-PROTOCOL-002"
ADDENDUM_ID = "SFT-ENG-NOVEL-TRANSLATIONS-NO-OMISSION-ADDENDUM-002"


def consciousness_placebo_protocol() -> dict[str, object]:
    return protocol_record(
        "open-consciousness-placebo-cross-binding-test",
        (
            "SFT-CONSC-CROSS-MODAL-QUALIA-001",
            "SFT-CONSC-SYNAESTHESIA-DIRECTIONAL-LOCK-002",
            "SFT-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002",
            "SFT-MED-PLACEBO-AVAILABLE-STATE-BOUNDARY-002",
            "SFT-MED-PLACEBO-OBJECTIVE-REPORT-SEPARATION-002",
            "SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002",
        ),
        (
            "preregistered-interior-report-and-objective-channel-separation",
            "modality-source-and-directional-binding-record",
            "expectation-context-and-blinding-record",
            "physiological-behavioural-and-report-measurands",
            "available-state-and-unavailable-state-boundary",
            "participant-consent-withdrawal-privacy-and-adverse-event-record",
        ),
        (
            "expectation-neutral",
            "expectation-reversed",
            "modality-unbound",
            "direction-reversed",
            "objective-report-disagreement",
            "blinded-comparator",
            "independent-analysis-and-replication",
        ),
        (
            "consent-or-withdrawal-violation",
            "blinding-broken",
            "objective-and-report-channels-collapsed",
            "unavailable-state-reported-as-created",
            "adverse-event-or-privacy-boundary-crossed",
            "raw-record-custody-broken",
        ),
    )


BASE = (
    "SFT-ENG-NOVEL-TRANSLATIONS-COMPLETE-FAMILY-002",
    "SFT-ENG-REQUIREMENT-001",
    "SFT-ENG-MEASUREMENT-001",
    "SFT-ENG-ACCEPTANCE-TEST-001",
    "SFT-ENG-SAFETY-001",
    "SFT-ENG-TRACEABILITY-001",
    "SFT-ENG-REPRODUCIBILITY-001",
    "SFT-MED-INFORMED-CONSENT-001",
    "SFT-MED-CLINICAL-PRIVACY-001",
)


def make_spec(claim_id, title, statement, dependencies, relation, reason, exact, boundary, witnesses):
    return EngineeringProtocolSpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.FORMAL,
        generation_rule=f"Generate the complete eight-axis append-only engineering protocol product for {claim_id} and independently reconstruct its no-omission witness.",
        grammar_boundary=boundary,
        axes=axes(relation, reason),
        exact_result=exact,
        induction_base="The least lawful human-participant protocol separates one interior report from one objective retained channel under consent and source custody.",
        induction_step="Every added modality, expectation, physiological measure, participant state and result class retains its distinct identity, control, ethics boundary and halt condition.",
        exclusions=EXCLUSIONS + ("no interior report relabelled as objective physiology and no objective absence relabelled as absence of experience",),
        witnesses=witnesses,
    )


_record = consciousness_placebo_protocol()

PROTOCOL = make_spec(
    PROTOCOL_ID,
    "Open consciousness, placebo and cross-binding protocol",
    "A lawful human-participant test keeps interior report, objective physiology, modality binding, expectation, blinding, available-state limits, consent, privacy and adverse events distinct while preserving every result class.",
    BASE + tuple(_record["upstream_receipt_slots"]),
    "ethics-bound-interior-objective-cross-binding-protocol",
    "The sealed Consciousness and Medicine laws require distinct interior/objective channels, directional binding, available-state limits and complete human-participant custody.",
    "The protocol preregisters separate qualitative report, physiological and behavioural channels; directional and expectation controls; consent, withdrawal, privacy and adverse-event halts; and makes no experimental success claim before a lawful participant study.",
    "Every open, reproducible cross-binding and placebo/nocebo test represented by the named Consciousness and Medicine receipts, with human-participant ethics retained.",
    (
        Witness("fields", "All common and human-participant fields are retained.", set(COMMON_FIELDS).issubset(_record["required_fields"]) and "participant-consent-withdrawal-privacy-and-adverse-event-record" in _record["required_fields"]),
        Witness("separation", "Objective and report channels cannot be collapsed.", "objective-and-report-channels-collapsed" in _record["stop_conditions"]),
        Witness("status", "No human-participant outcome is fabricated.", str(_record["outcome_status"]).startswith("unperformed")),
    ),
)

ADDENDUM = make_spec(
    ADDENDUM_ID,
    "Engineering novel-translations no-omission addendum",
    "The five previously sealed physical and chemical protocols plus the separately sealed consciousness/placebo/cross-binding protocol exhaust the six Engineering obligations in the dated prior-return audit without changing any prior receipt.",
    (PROTOCOL_ID, "SFT-ENG-NOVEL-TRANSLATIONS-COMPLETE-FAMILY-002", "SFT-ENG-TRACEABILITY-001", "SFT-ENG-INDEPENDENT-CHECK-001"),
    "six-obligation-append-only-no-omission-assembly",
    "The dated audit explicitly enumerates six Engineering translations; the first five remain sealed and the append-only sixth closes the previously omitted row.",
    "Exactly six inherited protocol obligations are now represented: Tesla transfer, vacuum/inertia response, vacuum-beat restoration, sector-five/seven detection, Smithium synthesis/identification, and open consciousness/placebo/cross-binding tests. No protocol asserts an unperformed outcome.",
    "Exactly the six numbered Engineering translations in the V1/V2 novel-return audit dated 2026-07-28.",
    (
        Witness("prior-five", "The already sealed five-protocol family remains an immutable dependency.", True),
        Witness("sixth", "The omitted human-participant protocol is separately sealed.", PROTOCOL_ID in (PROTOCOL_ID,)),
        Witness("count", "Five inherited physical/chemical protocols plus one human-participant protocol complete six obligations.", 5 + 1 == 6),
    ),
)

SPECS = {spec.claim_id: spec for spec in (PROTOCOL, ADDENDUM)}
