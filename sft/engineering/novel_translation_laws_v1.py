"""Exact engineering translations of the sealed prior-return law families.

The laws in this module close reproducible *protocols*, not apparatus outcomes.
No successful Tesla, vacuum/inertia, vacuum-work, new-sector or Smithium
experiment is asserted here.  Each protocol instead fixes the complete record,
controls, stop conditions and acceptance boundary that any later execution must
preserve.  Apparatus data can test an operating boundary only after the protocol
and its upstream scientific receipts have sealed.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import (
    StructuralPhysicsProgram,
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
)


TESLA_ID = "SFT-ENG-TESLA-RESONANT-TRANSFER-PROTOCOL-002"
VACUUM_INERTIA_ID = "SFT-ENG-VACUUM-INERTIA-RESPONSE-PROTOCOL-002"
VACUUM_BEAT_ID = "SFT-ENG-VACUUM-BEAT-RESTORATION-PROTOCOL-002"
SECTOR_ID = "SFT-ENG-SECTOR-FIVE-SEVEN-DETECTION-PROTOCOL-002"
SMITHIUM_ID = "SFT-ENG-SMITHIUM-SYNTHESIS-IDENTIFICATION-PROTOCOL-002"
COMPLETE_ID = "SFT-ENG-NOVEL-TRANSLATIONS-COMPLETE-FAMILY-002"


COMMON_FIELDS = (
    "protocol-identity-and-version",
    "upstream-claim-identities-and-receipts",
    "declared-purpose-and-operating-boundary",
    "apparatus-and-configuration-identities",
    "measurands-units-instruments-and-calibration",
    "preregistered-acceptance-and-rejection-conditions",
    "favourable-adverse-absent-and-unresolved-results",
    "uncertainty-confounds-failures-and-anomalies",
    "hazards-stop-conditions-and-safe-state",
    "complete-source-transfer-loss-and-restoration-ledger",
    "raw-record-custody-environment-commands-and-hashes",
    "independent-reconstruction-and-repetition-record",
)


@dataclass(frozen=True)
class EngineeringProtocolSpec(StructuralPhysicsSpec):
    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-ENG-"):
            raise ValueError("engineering protocol identity is invalid")
        if not self.dependencies or len(self.axes) != 8 or not self.witnesses:
            raise ValueError("engineering protocol lacks dependencies, eight axes or witnesses")
        if len({axis.key for axis in self.axes}) != 8:
            raise ValueError("engineering protocol contains duplicate axes")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("engineering protocol axis is not binary-complete")
            axis.survivor
        if not all(witness.passed for witness in self.witnesses):
            raise ValueError("engineering protocol witness failed")


class EngineeringProtocolProgram(StructuralPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="engineering_translation",
            statement=self.spec.statement,
            evidence_mode=self.spec.evidence_mode,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=self.spec.provenance,
            source_hash=self.source_hash,
        )


def exact_ledger(input_support: Fraction, carriers: tuple[Fraction, ...]) -> bool:
    """Test a positive exact ledger without admitting a signed proof carrier."""
    if not isinstance(input_support, Fraction) or input_support <= 0:
        return False
    if not carriers or any(not isinstance(value, Fraction) or value <= 0 for value in carriers):
        return False
    return sum(carriers, Fraction(0, 1)) == input_support


def protocol_record(name: str, upstream: tuple[str, ...], domain_fields: tuple[str, ...], controls: tuple[str, ...], stops: tuple[str, ...]) -> dict[str, object]:
    return {
        "protocol": name,
        "upstream_receipt_slots": upstream,
        "required_fields": COMMON_FIELDS + domain_fields,
        "controls": controls,
        "stop_conditions": stops,
        "result_classes": ("favourable", "adverse", "absent", "unresolved"),
        "outcome_status": "unperformed-until-a-source-custodied-apparatus-run-is-attached",
        "law_selection_by_outcome": False,
    }


def tesla_protocol() -> dict[str, object]:
    return protocol_record(
        "tesla-resonant-connected-path-transfer",
        ("SFT-PHYS-TESLA-RESONANT-TRANSFER-081", "SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082"),
        ("source-drive-phase-history", "resonator-mode-and-boundary-record", "receiver-load-history", "stored-delivered-returned-and-loss-carriers"),
        ("drive-absent", "off-resonance", "disconnected-path", "phase-reversed", "dummy-load", "independent-power-ledger"),
        ("calibration-expired", "unclosed-energy-ledger", "undeclared-mode", "unsafe-field-or-temperature", "raw-record-custody-broken"),
    )


def vacuum_inertia_protocol() -> dict[str, object]:
    return protocol_record(
        "resonantly-driven-vacuum-inertial-response",
        ("SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083", "SFT-PHYS-VACUUM-INERTIA-COVARIATION-084", "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086", "SFT-PHYS-VALIDATION-VACUUM-INERTIA-DRIVE-FAMILY-087"),
        ("drive-and-resonance-history", "inertial-response-channel", "vacuum-proxy-channel", "thermal-electromagnetic-mechanical-and-gravitational-confounds", "restoration-history"),
        ("drive-absent", "off-resonance", "phase-reversed", "shielded-dummy", "thermal-matched", "orientation-reversed", "independent-inertial-reference"),
        ("unpaired-response-channel", "confound-unbounded", "restoration-unmeasured", "source-ledger-open", "safety-boundary-crossed"),
    )


def vacuum_beat_protocol() -> dict[str, object]:
    return protocol_record(
        "positive-vacuum-beat-transfer-and-complete-restoration",
        ("SFT-PHYS-VACUUM-ASYMMETRIC-BEAT-EXTRACTION-003", "SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003", "SFT-PHYS-VALIDATION-VACUUM-EXTRACTION-003"),
        ("initial-half-One-carrier", "generator-three-unit-carrier", "outward-one-sixth-transfer", "retained-one-third-carrier", "returned-one-sixth-transfer", "pump-boundary-and-final-state-identity"),
        ("pump-absent", "boundary-unchanged", "load-disconnected", "restoration-omitted", "calorimetric-and-electrical-independent-ledgers"),
        ("source-or-pump-unmeasured", "outward-or-return-carrier-missing", "final-state-not-identical", "net-gain-claim-with-open-ledger", "unsafe-state"),
    )


def sector_protocol() -> dict[str, object]:
    sectors = tuple({"sector": p, "charge_labels": p, "mediators": p * p - 1, "coupling": Fraction(p - 1, p)} for p in (5, 7))
    record = protocol_record(
        "sector-five-and-seven-blind-detection",
        ("SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002", "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003", "SFT-PHYS-NO-EXTRA-SECTOR-PARTICLE-BOUNDARY-093", "SFT-PHYS-VALIDATION-NEW-SECTOR-COMPLETE-FAMILY-095"),
        ("sealed-sector-signature-table", "blind-signal-region", "background-and-systematic-model", "detector-efficiency-and-resolution", "outside-list-falsification-record", "independent-channel-and-replication"),
        ("known-sector-injection", "null-injection", "sideband", "label-permutation", "detector-off", "independent-analysis"),
        ("unblinded-before-freeze", "background-not-closed", "look-elsewhere-record-absent", "detector-calibration-failed", "outside-list-result-discarded"),
    )
    return {**record, "sealed_signatures": sectors}


def smithium_protocol() -> dict[str, object]:
    return protocol_record(
        "Smithium-126-synthesis-and-joint-identification",
        ("SFT-CHEM-SMITHIUM-SYNTHESIS-CONSERVATION-001", "SFT-CHEM-SMITHIUM-JOINT-DETECTION-001", "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001"),
        ("sealed-126-184-310-coordinate", "target-projectile-and-beam-ledger", "production-cross-section-and-yield", "mass-and-nuclear-coordinate", "genetically-linked-decay-chain", "ion-oxidation-and-spectroscopic-record", "official-discovery-criterion-distinction"),
        ("blank-target", "neighboring-isotope", "known-decay-chain", "mass-calibration", "chemistry-separation-control", "independent-laboratory-reconstruction"),
        ("carrier-conservation-failed", "decay-linkage-broken", "mass-or-charge-identity-ambiguous", "calibration-expired", "single-channel-discovery-claim"),
    )


def family_completeness() -> dict[str, object]:
    records = (tesla_protocol(), vacuum_inertia_protocol(), vacuum_beat_protocol(), sector_protocol(), smithium_protocol())
    return {
        "protocol_count": len(records),
        "protocols": tuple(record["protocol"] for record in records),
        "all_common_fields": all(set(COMMON_FIELDS).issubset(record["required_fields"]) for record in records),
        "all_result_classes": all(record["result_classes"] == ("favourable", "adverse", "absent", "unresolved") for record in records),
        "all_unperformed": all(str(record["outcome_status"]).startswith("unperformed") for record in records),
        "all_forbid_outcome_selection": all(record["law_selection_by_outcome"] is False for record in records),
    }


EXCLUSIONS = (
    "no apparatus result, prototype, discovery, energy gain or synthesis success invented by the protocol",
    "no outcome, prior answer or application selects an upstream scientific law",
    "no favourable-only retention and no adverse, absent, unresolved or anomalous row discarded",
    "no numerical absence, signed, irrational, imaginary, floating, fitted, free or target-selected proof magnitude",
    "no open source, transfer, loss, information, material or restoration ledger",
    "no engine, verifier, protected authority, prior receipt or admitted claim modification",
)


def axes(relation: str, reason: str) -> tuple:
    return (
        binary_axis("authority", "What authorizes the protocol?", "application-selected-law", "An application cannot select its scientific law.", "sealed-upstream-receipts", "Every scientific premise is named by its admitted receipt dependency."),
        binary_axis("relation", "Which translation relation survives?", "informal-apparatus-sketch", "A sketch cannot force a reproducible test.", relation, reason),
        binary_axis("record", "What record is mandatory?", "reported-outcome-only", "An outcome hides source, loss, uncertainty and failure.", "complete-common-and-domain-record", "All common and domain-specific fields are retained."),
        binary_axis("controls", "How are alternatives tested?", "favourable-control-only", "Selective controls cannot expose confounds.", "complete-declared-control-family", "Null, reversal, confound and independent controls remain distinct."),
        binary_axis("outcomes", "Which result classes survive?", "success-only", "Success-only retention is not empirical.", "favourable-adverse-absent-unresolved", "Every outcome class is source-custodied."),
        binary_axis("safety", "What happens at violation?", "continue-after-violation", "Continuing destroys the declared boundary.", "visible-halt-and-bounded-safe-state", "Every broken calibration, ledger, custody or safety condition halts."),
        binary_axis("measurement", "When may outcomes be opened?", "outcome-before-protocol-seal", "Opening outcomes first permits fitting.", "protocol-seal-before-outcome", "Acceptance conditions seal before apparatus results."),
        binary_axis("extension", "May implementation rewrite the law?", "implementation-exception", "An exception introduces an unforced choice.", "no-law-rewrite", "Implementation may test but cannot change its upstream law."),
    )


BASE = ("SFT-ENG-REQUIREMENT-001", "SFT-ENG-MEASUREMENT-001", "SFT-ENG-CALIBRATION-001", "SFT-ENG-ACCEPTANCE-TEST-001", "SFT-ENG-SAFETY-001", "SFT-ENG-TRACEABILITY-001", "SFT-ENG-REPRODUCIBILITY-001", "SFT-ENG-DEMONSTRATION-001")


def make(cid: str, title: str, statement: str, dependencies: tuple[str, ...], relation: str, reason: str, exact: str, boundary: str, witnesses: tuple[Witness, ...]) -> EngineeringProtocolSpec:
    return EngineeringProtocolSpec(
        claim_id=cid,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=EvidenceMode.FORMAL,
        generation_rule=f"Generate the complete eight-axis engineering protocol product for {cid}, then reconstruct every protocol field and control independently.",
        grammar_boundary=boundary,
        axes=axes(relation, reason),
        exact_result=exact,
        induction_base="The least lawful protocol binds one sealed upstream law to one complete source-custodied record and visible halt boundary.",
        induction_step="Every added channel, carrier, control or apparatus state is admitted only with its identity, uncertainty, ledger relation, result class and stop condition retained.",
        exclusions=EXCLUSIONS,
        witnesses=witnesses,
    )


_tesla, _vi, _vb, _sector, _smith, _family = tesla_protocol(), vacuum_inertia_protocol(), vacuum_beat_protocol(), sector_protocol(), smithium_protocol(), family_completeness()

TESLA = make(TESLA_ID, "Tesla resonant-transfer engineering protocol", "A Tesla-family transfer test is lawful only as a sealed, calibrated connected-path protocol with phase, load, complete power ledger, adverse controls and visible halt retained.", BASE + tuple(_tesla["upstream_receipt_slots"]), "phase-bound-connected-path-complete-ledger-protocol", "The upstream recurrence and transfer law fixes the required mode, path and ledger records without selecting an apparatus outcome.", "The protocol requires all common records plus source phase, resonator mode, receiver load and stored, delivered, returned and loss carriers; it includes drive-absent, off-resonance, disconnected, reversed-phase, dummy-load and independent-ledger controls and makes no success claim before execution.", "Every bounded resonant-transfer apparatus and result class represented by the sealed upstream Tesla family.", (Witness("fields", "Common and Tesla-specific fields are complete.", len(_tesla["required_fields"]) == len(set(_tesla["required_fields"]))), Witness("controls", "The complete adverse-control family is retained.", len(_tesla["controls"]) == 6), Witness("status", "No apparatus outcome is fabricated.", str(_tesla["outcome_status"]).startswith("unperformed"))))

VACUUM_INERTIA = make(VACUUM_INERTIA_ID, "Driven vacuum/inertial-response engineering protocol", "A driven vacuum/inertial test is lawful only when drive, paired response channels, all ordinary confounds, complete restoration and source accounting remain independently measurable and preregistered.", (TESLA_ID,) + BASE + tuple(_vi["upstream_receipt_slots"]), "paired-drive-response-restoration-protocol", "The sealed source-bound co-variation law requires paired channels and a complete restoration ledger while forbidding an unmeasured response claim.", "The protocol separates resonant drive, vacuum proxy, inertial response, restoration and ordinary thermal, electromagnetic, mechanical and gravitational confounds; no driven-inertia observation is asserted.", "Every bounded source-driven apparatus state, confound, reversal and result class represented by the sealed vacuum/inertia family.", (Witness("fields", "All paired and confound channels are present.", all(x in _vi["required_fields"] for x in ("inertial-response-channel", "vacuum-proxy-channel", "restoration-history"))), Witness("controls", "Reversal, dummy and reference controls are distinct.", len(_vi["controls"]) == 7), Witness("status", "No prototype or response is fabricated.", str(_vi["outcome_status"]).startswith("unperformed"))))

VACUUM_BEAT = make(VACUUM_BEAT_ID, "Vacuum-beat transfer and restoration protocol", "A vacuum-beat test must distinguish the exact outward one-sixth transfer from complete returned-cycle restoration and must halt any net-gain claim whose source, pump, loss or final-state ledger remains open.", (VACUUM_INERTIA_ID,) + BASE + tuple(_vb["upstream_receipt_slots"]), "one-sixth-outward-and-one-sixth-return-ledger-protocol", "The upstream exact beat and complete-cycle law fixes both transfer directions; omission of either direction changes the tested claim.", "The protocol retains the half-One initial carrier, one-third residual, one-sixth outward work transfer, one-sixth restoration transfer and identical final state, with independent power ledgers and explicit no-unrecorded-gain acceptance boundary.", "The exact Fold beat-transfer grammar and every apparatus source, pump, boundary, restoration and result class needed to test it.", (Witness("outward-ledger", "Half-One splits exactly into retained third-One and outward sixth-One.", exact_ledger(Fraction(1, 2), (Fraction(1, 3), Fraction(1, 6)))), Witness("restoration", "Third-One plus returned sixth-One reconstructs half-One.", exact_ledger(Fraction(1, 2), (Fraction(1, 3), Fraction(1, 6)))), Witness("stop", "Open-ledger gain claims halt.", "net-gain-claim-with-open-ledger" in _vb["stop_conditions"])))

SECTOR = make(SECTOR_ID, "Sector-five/seven blind detection protocol", "A sector-five/seven search seals the complete p-fibre signatures before unblinding and retains backgrounds, systematics, nulls, outside-list events and independent reconstructions without relabelling a standing prediction as discovery.", BASE + tuple(_sector["upstream_receipt_slots"]), "sealed-p-five-p-seven-blind-signature-protocol", "The upstream prime-sector inventory fixes the signature counts while the engineering protocol fixes blind custody, controls and rejection boundaries.", "The protocol preregisters p=5 with 5 charge labels, 24 mediators and coupling 4/5, and p=7 with 7 labels, 48 mediators and coupling 6/7; those are standing signatures, not observed particles.", "The complete sector-five/seven signature table, detector/background alternatives, blind analysis states and outside-list falsification boundary.", (Witness("sector-five", "The p=5 signature is reconstructed exactly.", _sector["sealed_signatures"][0] == {"sector": 5, "charge_labels": 5, "mediators": 24, "coupling": Fraction(4, 5)}), Witness("sector-seven", "The p=7 signature is reconstructed exactly.", _sector["sealed_signatures"][1] == {"sector": 7, "charge_labels": 7, "mediators": 48, "coupling": Fraction(6, 7)}), Witness("blind", "Unblinding before freeze is a mandatory halt.", "unblinded-before-freeze" in _sector["stop_conditions"])))

SMITHIUM = make(SMITHIUM_ID, "Smithium synthesis and joint-identification protocol", "A Smithium test retains exact 126/184/310 conservation, apparatus and yield records, genetically linked decay, mass, ion, oxidation and spectroscopy channels, while preserving the distinction between SFT evidence and official discovery criteria.", BASE + tuple(_smith["upstream_receipt_slots"]), "Smithium-126-complete-synthesis-identification-protocol", "The sealed Smithium consequence family fixes the coordinates and evidence classes without selecting a target, projectile, beam energy or successful outcome.", "The protocol binds every synthesis attempt to Z=126, N=184 and A=310 conservation and requires joint mass, nuclear, decay, ion/oxidation and spectroscopic records; it does not claim Smithium has been produced.", "Every conservation-valid Smithium attempt, complete joint-evidence class, control, ambiguity and result class inside the sealed Smithium family.", (Witness("coordinate", "The exact Smithium nuclear coordinate is retained.", "sealed-126-184-310-coordinate" in _smith["required_fields"]), Witness("identity", "Joint identification channels remain distinct.", all(x in _smith["required_fields"] for x in ("mass-and-nuclear-coordinate", "genetically-linked-decay-chain", "ion-oxidation-and-spectroscopic-record"))), Witness("status", "No synthesis is fabricated.", str(_smith["outcome_status"]).startswith("unperformed"))))

COMPLETE = make(COMPLETE_ID, "Complete prior-return engineering protocol family", "The five mandatory prior-return translations form one traceable engineering family whose complete records, controls, result classes, safe halts and non-selection boundary are independently reconstructible without asserting unperformed experiments.", (TESLA_ID, VACUUM_INERTIA_ID, VACUUM_BEAT_ID, SECTOR_ID, SMITHIUM_ID, "SFT-ENG-E2E-001", "SFT-ENG-INDEPENDENT-CHECK-001", "SFT-ENG-PORTABLE-DATA-001"), "five-protocol-traceable-complete-family", "The frozen return census names exactly these five translation obligations, and the family reconstruction checks their common and domain-specific fields without adding an outcome.", "Exactly five protocols close the registered Engineering novel-return boundary. Every one carries sealed upstream identities, complete records, controls, all four result classes, safety halts, independent reconstruction and an explicit unperformed-outcome status.", "Exactly the five mandatory prior-corpus Engineering translations in the frozen 2026-07-28 return census; physical executions remain extension-open.", (Witness("count", "All five mandatory protocols are present once.", _family["protocol_count"] == 5 and len(set(_family["protocols"])) == 5), Witness("common", "Every protocol contains all common evidence fields.", _family["all_common_fields"]), Witness("outcomes", "Every result class remains retained.", _family["all_result_classes"]), Witness("boundary", "All protocols remain unperformed and cannot select laws.", _family["all_unperformed"] and _family["all_forbid_outcome_selection"])))

SPECS = {spec.claim_id: spec for spec in (TESLA, VACUUM_INERTIA, VACUUM_BEAT, SECTOR, SMITHIUM, COMPLETE)}
