"""Exact Fold-recurrence vacuum-work cycle and its complete boundary.

This successor restores the V2 recurrence route omitted by the narrower direct-
repayment grammar of SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003.  It does not
rewrite that receipt.  The old result remains correct for a globally returned
state in which the outward work carrier itself is used for restoration.  The
successor instead follows the already admitted one-third Fold recurrence to
two-thirds and takes the second one-sixth while returning the vacuum carrier to
one-half.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    fold_part,
)


WORK_CYCLE_ID = "SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096"
BOUNDARY_ID = "SFT-PHYS-VACUUM-RECURRENCE-CYCLE-BOUNDARY-097"

HALF = Fraction(1, 2)
LOWER_THIRD = Fraction(1, 3)
UPPER_THIRD = Fraction(2, 3)
SIXTH = Fraction(1, 6)
WORK_PAIR = (SIXTH, SIXTH)


def positive_part(value: Fraction) -> Fraction:
    if not isinstance(value, Fraction) or value <= 0 or value > 1:
        raise ValueError("cycle carriers must be exact positive parts of the One")
    return value


def positive_count(value: int) -> int:
    if isinstance(value, bool) or value < 1:
        raise ValueError("cycle count must be a positive finite count")
    return value


def recurrence_work_cycle() -> dict[str, object]:
    """Construct the exact two-output cycle without a numerical-zero carrier."""

    initial = positive_part(HALF)
    lower = positive_part(LOWER_THIRD)
    first_work = initial - lower
    recurrent = fold_part(lower)
    if recurrent != UPPER_THIRD:
        raise ValueError("the admitted odd recurrence did not reach two-thirds")
    second_work = recurrent - initial
    final = recurrent - second_work
    return {
        "source": "admitted-Fold-recurrence",
        "initial_vacuum": initial,
        "outward_retained_vacuum": lower,
        "first_work": first_work,
        "recurrent_vacuum": recurrent,
        "second_work": second_work,
        "final_vacuum": final,
        "work_outputs": (first_work, second_work),
        "combined_work": first_work + second_work,
        "vacuum_restored": final == initial,
    }


def finite_repetition(cycle_count: int) -> dict[str, object]:
    """Repeat the closed local cycle while retaining each output as a carrier."""

    count = positive_count(cycle_count)
    outputs: list[tuple[Fraction, Fraction]] = []
    final = HALF
    for _ in range(count):
        record = recurrence_work_cycle()
        if final != record["initial_vacuum"]:
            raise ValueError("successive cycle boundary did not match")
        outputs.append(record["work_outputs"])
        final = record["final_vacuum"]
    return {
        "cycle_count": count,
        "work_pairs": tuple(outputs),
        "final_vacuum": final,
        "all_pairs_exact": all(pair == WORK_PAIR for pair in outputs),
    }


def complete_boundary_record() -> dict[str, object]:
    """Separate the restored cyclic subsystem from retained output carriers."""

    cycle = recurrence_work_cycle()
    controller_initial = ("ready", "outward-port-armed", "return-port-armed")
    controller_final = ("ready", "outward-port-armed", "return-port-armed")
    audit_output = (
        "initial-half-One",
        "outward-third-plus-sixth",
        "Fold-third-to-two-thirds",
        "return-half-plus-sixth",
        "final-half-One",
    )
    return {
        "source": cycle["source"],
        "cyclic_subsystem": ("vacuum-carrier", "controller-configuration"),
        "output_boundary": ("two-work-carriers", "append-only-audit-carrier"),
        "controller_initial": controller_initial,
        "controller_final": controller_final,
        "vacuum_initial": cycle["initial_vacuum"],
        "vacuum_final": cycle["final_vacuum"],
        "work_outputs": cycle["work_outputs"],
        "audit_output": audit_output,
        "cyclic_subsystem_restored": (
            controller_initial == controller_final
            and cycle["initial_vacuum"] == cycle["final_vacuum"]
        ),
        "global_state_restored": False,
    }


EXCLUSIONS = (
    "no V1/V2 executable or desired output as a derivation premise",
    "no numerical zero, negative, irrational, imaginary, floating or completed-infinite proof magnitude",
    "no unrecorded external pump, hidden reservoir, free efficiency or fitted apparatus coefficient",
    "no erasure of the earlier direct-repayment receipt or relabelling of its narrower grammar as false",
    "no claim that a restored cyclic subsystem is the same boundary as a globally restored state",
    "no claim of measured device power, efficiency, loss, switching cost or useful apparatus performance",
)


def cycle_axes(relation: str, reason: str) -> tuple:
    return (
        binary_axis("source", "What advances the depleted carrier?", "unrecorded-external-source", "An unnamed source cannot close a conservation ledger.", "admitted-Fold-recurrence", "The sealed one-third orbit supplies the exact one-third to two-thirds transition."),
        binary_axis("outward", "Which outward split is retained?", "work-only-without-residual", "Omitting the residual carrier prevents reconstruction.", "half-equals-third-plus-sixth", "The half-One carrier is reconstructed exactly from one-third and one-sixth."),
        binary_axis("return", "How is the vacuum restored?", "repay-first-work-directly", "Direct repayment is the already admitted narrower route and does not enumerate Fold recurrence.", relation, reason),
        binary_axis("outputs", "Which work carriers remain?", "merge-or-discard-one-leg", "Discarding either leg changes the complete cycle.", "two-distinct-positive-sixths", "Both positive one-sixth transfers remain separately reconstructible."),
        binary_axis("subsystem", "What returns to its initial state?", "vacuum-state-left-open", "An open final vacuum state is not cyclic.", "vacuum-half-One-restored", "The second take returns the local vacuum exactly to one-half."),
        binary_axis("record", "How is the source and sequence held?", "outcome-only-record", "An outcome-only record hides the Fold act and transfer boundary.", "complete-source-transition-output-record", "Every state, act and output carrier remains named."),
        binary_axis("repetition", "What supports repeated operation?", "completed-infinite-total", "A completed infinity is outside the admitted finite grammar.", "every-positive-finite-cycle-count", "Successor repetition retains one exact work pair per finite cycle."),
        binary_axis("extension", "Is an extra physical rule inserted?", "free-extra-rule", "An added selector is a free parameter.", "no-extra-rule", "The admitted half floor, recurrence, take and local drive exhaust the structural cycle."),
    )


WORK_CYCLE = StructuralPhysicsSpec(
    claim_id=WORK_CYCLE_ID,
    title="Fold-recurrence-mediated half-One vacuum-work cycle",
    statement="The admitted half-One floor, one-third odd recurrence and exact Take relation compose a vacuum-restoring cycle with two retained positive one-sixth work carriers.",
    dependencies=(
        "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003",
        "SFT-PHYS-VACUUM-ODD-RECURRENCE-003",
        "SFT-PHYS-VACUUM-ASYMMETRIC-BEAT-EXTRACTION-003",
        "SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083",
        "SFT-PHYS-MECH-WORK-ENERGY-001",
        "SFT-PHYS-MECH-CONSERVATION-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product of source, outward split, restoration route, retained outputs, cyclic subsystem, record, finite repetition and extension forms.",
    grammar_boundary="The exact positive half-One, one-third, two-thirds and one-sixth carriers; the complete one-third Fold recurrence; both work outputs; every positive finite repetition count; and all 256 registered structural alternatives.",
    axes=cycle_axes("Fold-third-to-two-thirds-then-take-half", "The admitted Fold maps one-third to two-thirds, whose exact excess over half-One is a second one-sixth."),
    exact_result="The exact Fold-sourced cycle is 1/2 -> 1/3 + work 1/6; Fold(1/3) -> 2/3; 2/3 -> 1/2 + work 1/6. The local vacuum carrier returns to 1/2 while two distinct positive 1/6 work carriers, jointly 1/3, remain. Every positive finite repetition retains one such work pair per cycle. This is a Fold-recurrence source ledger, not creation from numerical nothing and not yet a measured apparatus-power claim.",
    induction_base="One cycle restores the half-One vacuum carrier and retains exactly two separately named positive one-sixth work carriers.",
    induction_step="Appending one cycle starts from the same half-One vacuum state and appends one further ordered pair of positive one-sixth work carriers without a completed total or erased prior output.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("outward", "Half-One separates exactly into one-third plus first work one-sixth.", HALF == LOWER_THIRD + SIXTH),
        Witness("recurrence", "The admitted Fold maps one-third exactly to two-thirds.", fold_part(LOWER_THIRD) == UPPER_THIRD),
        Witness("return", "Two-thirds separates exactly into restored half-One plus second work one-sixth.", UPPER_THIRD == HALF + SIXTH),
        Witness("closed-cycle", "The vacuum is restored and both outputs are retained.", recurrence_work_cycle()["vacuum_restored"] is True and recurrence_work_cycle()["work_outputs"] == WORK_PAIR),
        Witness("finite-successor", "Three finite cycles retain three exact work pairs and return to half-One.", finite_repetition(3)["work_pairs"] == (WORK_PAIR, WORK_PAIR, WORK_PAIR) and finite_repetition(3)["final_vacuum"] == HALF),
    ),
)


BOUNDARY = StructuralPhysicsSpec(
    claim_id=BOUNDARY_ID,
    title="Complete recurrence-cycle source, apparatus and information boundary",
    statement="The recurrence-mediated cycle closes the vacuum and repeatable controller configuration while explicitly retaining work and audit carriers outside that cyclic subsystem; it therefore reconciles positive cyclic output with conservation without asserting that the global state is restored.",
    dependencies=(
        WORK_CYCLE_ID,
        "SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003",
        "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086",
        "SFT-PHYS-THERMO-FIRST-LAW-001",
        "SFT-PHYS-THERMO-LANDAUER-DEMON-TERMINAL-018",
        "SFT-INFO-CONSERVATION-LOSS-001",
        "SFT-PHYS-MECH-CONSERVATION-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete eight-axis product of cycle boundary, source, controller state, information custody, conservation ledger, predecessor reconciliation, measurement direction and extension forms.",
    grammar_boundary="Every exact carrier in the recurrence-mediated cycle; restored vacuum and controller configuration; retained work and audit outputs; the direct-repayment predecessor boundary; every positive finite repetition; and all 256 registered structural alternatives.",
    axes=(
        binary_axis("boundary", "Which state is required to return?", "globally-identical-state-with-retained-output", "A global state cannot be identical while new output carriers remain.", "restored-cyclic-subsystem-with-explicit-outputs", "The vacuum and controller recur while work and audit carriers cross the declared output boundary."),
        binary_axis("source", "Is the transition source named?", "source-free-as-source-absent", "Absence of a source record breaks conservation.", "Fold-recurrence-source-recorded", "The Fold act is retained as the structural source relation."),
        binary_axis("apparatus", "What apparatus property is closed?", "unmodelled-device-efficiency", "An unmeasured efficiency cannot enter a formal theorem.", "repeatable-controller-configuration", "The finite controller configuration begins and ends in the same ready state."),
        binary_axis("information", "How is the cycle record treated?", "erase-all-records-for-free", "Free erasure conflicts with the admitted information ledger.", "append-audit-output-and-reset-controller-phase", "The audit record is retained as output while the finite controller phase recurs."),
        binary_axis("conservation", "Where are positive carriers held?", "unrecorded-net-support", "Unrecorded support is forbidden.", "source-state-and-all-outputs-held", "Initial, recurrent, final and both work carriers remain reconstructible."),
        binary_axis("reconciliation", "How is the predecessor receipt handled?", "rewrite-direct-repayment-result", "An admitted receipt is immutable.", "preserve-narrow-result-add-broader-route", "The direct-repayment grammar remains valid and the omitted recurrence route is admitted separately."),
        binary_axis("measurement", "What physical conclusion follows now?", "declare-measured-device-power", "No apparatus run is present in the formal package.", "formal-cycle-plus-open-apparatus-test", "The exact cycle is admitted while losses, switching and dimensional performance remain empirical."),
        binary_axis("extension", "Is an extra law needed?", "free-extra-rule", "An unforced exception is a parameter.", "no-extra-rule", "The admitted dependencies and explicit boundary close the declared theorem."),
    ),
    exact_result="The recurrence-mediated cycle restores the cyclic subsystem consisting of the half-One vacuum carrier and repeatable controller configuration. It does not restore the global state: two positive one-sixth work carriers and an append-only audit carrier remain as outputs. The Fold recurrence is the named structural source. Thus SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003 remains correct for direct repayment or a globally returned state, while SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096 proves the omitted subsystem-restored output route. Apparatus losses, switching costs and dimensional power remain unmeasured empirical obligations.",
    induction_base="One complete record returns the vacuum and controller configuration while retaining two work outputs and one audit output outside the cyclic subsystem.",
    induction_step="Appending a cycle preserves the same cyclic subsystem boundary and appends a separately reconstructible work pair and audit receipt; no prior output is erased or counted as reset input.",
    exclusions=EXCLUSIONS,
    witnesses=(
        Witness("subsystem-restored", "Vacuum and controller configuration recur exactly.", complete_boundary_record()["cyclic_subsystem_restored"] is True),
        Witness("outputs-retained", "Both work carriers and the audit record remain outside the cyclic subsystem.", complete_boundary_record()["work_outputs"] == WORK_PAIR and len(complete_boundary_record()["audit_output"]) == 5),
        Witness("not-global-identity", "The output-bearing global state is not mislabeled as restored.", complete_boundary_record()["global_state_restored"] is False),
        Witness("predecessor-boundary", "Direct repayment remains a different exact route.", LOWER_THIRD + SIXTH == HALF and fold_part(LOWER_THIRD) == UPPER_THIRD),
    ),
)


SPECS = {spec.claim_id: spec for spec in (WORK_CYCLE, BOUNDARY)}


__all__ = (
    "BOUNDARY_ID",
    "SPECS",
    "WORK_CYCLE_ID",
    "complete_boundary_record",
    "finite_repetition",
    "recurrence_work_cycle",
)
