"""Engineering protocol for the admitted recurrence-mediated vacuum cycle.

This is a protocol law only.  It does not assert that a physical apparatus has
executed the formal cycle or measured useful power.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode
from sft.engineering.novel_translation_laws_v1 import (
    BASE,
    EngineeringProtocolSpec,
    axes,
)
from sft.physics.structural_constants import Witness


CLAIM_ID = "SFT-ENG-VACUUM-RECURRENCE-CYCLE-PROTOCOL-003"


def protocol_record() -> dict[str, object]:
    return {
        "protocol": "Fold-recurrence-mediated-half-One-work-cycle",
        "upstream": (
            "SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096",
            "SFT-PHYS-VACUUM-RECURRENCE-CYCLE-BOUNDARY-097",
            "SFT-ENG-VACUUM-BEAT-RESTORATION-PROTOCOL-002",
        ),
        "required_states": (
            "initial-half-One-vacuum-proxy",
            "outward-one-third-residual",
            "first-one-sixth-receiver",
            "Fold-recurrence-transition-proxy",
            "upper-two-thirds-carrier",
            "second-one-sixth-receiver",
            "final-half-One-vacuum-proxy",
            "initial-and-final-controller-configuration",
            "append-only-cycle-audit-output",
        ),
        "independent_ledgers": (
            "calorimetric",
            "electrical",
            "mechanical",
            "thermal",
            "electromagnetic",
            "controller-and-switching",
        ),
        "controls": (
            "Fold-recurrence-disabled",
            "off-resonance",
            "receiver-disconnected",
            "second-take-disabled",
            "phase-reversed",
            "dummy-load",
            "matched-thermal-cycle",
            "independent-power-ledger",
        ),
        "stop_conditions": (
            "source-state-not-measured",
            "either-work-carrier-not-measured",
            "vacuum-proxy-not-returned",
            "controller-configuration-not-returned",
            "audit-record-missing",
            "switching-coupling-or-loss-ledger-open",
            "unsafe-state",
        ),
        "acceptance": (
            "both-one-sixth-structural-relations-resolved",
            "initial-final-cyclic-subsystem-indistinguishable-within-preregistered-uncertainty",
            "all-dimensional-input-output-loss-and-switching-carriers-closed",
            "all-adverse-controls-retained",
        ),
        "result_classes": ("favourable", "adverse", "absent", "unresolved"),
        "outcome_status": "unperformed-until-source-custodied-apparatus-data-are-attached",
    }


RECORD = protocol_record()

SPEC = EngineeringProtocolSpec(
    claim_id=CLAIM_ID,
    title="Fold-recurrence vacuum-work cycle engineering protocol",
    statement="A physical test of the Fold-recurrence vacuum-work cycle is lawful only when both one-sixth output channels, the one-third to two-thirds recurrence proxy, the restored half-One cyclic subsystem, controller state, switching, coupling, losses and append-only audit output are independently measured and preregistered.",
    dependencies=(
        "SFT-ENG-VACUUM-BEAT-RESTORATION-PROTOCOL-002",
        *BASE,
        "SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096",
        "SFT-PHYS-VACUUM-RECURRENCE-CYCLE-BOUNDARY-097",
        "SFT-PHYS-VALIDATION-VACUUM-INERTIA-DRIVE-FAMILY-087",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=f"Generate the complete eight-axis engineering protocol product for {CLAIM_ID}, then reconstruct every source, state, output, control, loss, switching, audit and stop field independently.",
    grammar_boundary="Every apparatus translation of the sealed recurrence cycle, both work-output channels, the recurrent carrier transition, restored cyclic subsystem, controller and audit outputs, six independent ledgers, eight adverse controls, seven stop conditions, four result classes and all 256 registered protocol alternatives.",
    axes=axes("two-output-Fold-recurrence-complete-boundary-protocol", "The two formal successors force a separate recurrence channel, two receivers, a restored cyclic-subsystem comparison and explicit output/audit boundary."),
    exact_result="The protocol preregisters the half-One initial carrier, one-third residual, first one-sixth receiver, one-third to two-thirds Fold-recurrence proxy, second one-sixth receiver, returned half-One carrier, identical controller configuration, switching/coupling/loss ledgers and append-only audit output. It requires calorimetric, electrical, mechanical, thermal, electromagnetic and controller ledgers; eight adverse controls; and a visible halt for every open source, output, restoration, information, loss or safety boundary. No apparatus success, efficiency, net dimensional power or source-free experimental result is asserted before execution.",
    induction_base="One apparatus cycle is testable only when every formal state and both output channels have calibrated measurement custody and the controller and vacuum proxy have registered initial/final comparisons.",
    induction_step="Every repeated cycle appends a separately identified work pair, audit record and complete loss/switching ledger while preserving the same preregistered cyclic-subsystem boundary and controls.",
    exclusions=(
        "no prototype outcome, energy gain, efficiency or useful power invented by the protocol",
        "no result or target selects the upstream formal cycle",
        "no source-free label that erases the admitted Fold recurrence source",
        "no favorable-only retention and no adverse, absent, unresolved or anomalous row discarded",
        "no open switching, coupling, loss, controller, information or final-state ledger",
        "no numerical zero, negative, irrational, imaginary, floating, fitted or free proof magnitude",
        "no engine, verifier, protected authority or prior admitted receipt modification",
    ),
    witnesses=(
        Witness("formal-cycle", "Both exact one-sixth channels and the returned half-One carrier are represented.", Fraction(1, 3) + Fraction(1, 6) == Fraction(1, 2) and Fraction(1, 2) + Fraction(1, 6) == Fraction(2, 3)),
        Witness("states", "Every formal and controller boundary state has a distinct protocol field.", len(RECORD["required_states"]) == 9),
        Witness("ledgers", "Six independent dimensional and controller ledgers are retained.", len(RECORD["independent_ledgers"]) == 6),
        Witness("controls", "The recurrence removal and every principal confound remain explicit.", len(RECORD["controls"]) == 8 and "Fold-recurrence-disabled" in RECORD["controls"]),
        Witness("halts", "Every open restoration, information, loss or safety boundary visibly halts.", len(RECORD["stop_conditions"]) == 7),
        Witness("unperformed", "No physical outcome is fabricated.", str(RECORD["outcome_status"]).startswith("unperformed")),
    ),
)


__all__ = ("CLAIM_ID", "RECORD", "SPEC", "protocol_record")
