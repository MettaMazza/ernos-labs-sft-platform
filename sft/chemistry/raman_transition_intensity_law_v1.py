"""Fold-native Raman transition, line-position and intensity law (ANAL-009)."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class RamanLineRecord:
    molecular_carrier: HeldLabel
    initial_state: HeldLabel
    final_state: HeldLabel
    polarizability_relation: HeldLabel
    scattering_side: HeldLabel
    shift_magnitude: Fraction | EmptyOne
    intensity_ratio: Fraction | EmptyOne
    condition: HeldLabel
    unit: HeldLabel
    position: PositiveCount

    def __post_init__(self) -> None:
        required = (
            (self.molecular_carrier, "molecular-carrier"),
            (self.initial_state, "molecular-state"),
            (self.final_state, "molecular-state"),
            (self.polarizability_relation, "polarizability-transition"),
            (self.scattering_side, "raman-scattering-side"),
            (self.condition, "raman-condition"),
            (self.unit, "reported-unit"),
        )
        if any(value.family != family for value, family in required):
            raise InadmissibleExactValue("complete held Raman line identity required")
        if self.scattering_side.label not in {"stokes", "anti-stokes", "coincident"}:
            raise InadmissibleExactValue("Raman scattering side is not generated")
        if self.scattering_side.label == "coincident":
            if self.shift_magnitude != EMPTY_ONE:
                raise InadmissibleExactValue("coincident scattering requires structural EmptyOne")
        elif not isinstance(self.shift_magnitude, Fraction) or self.shift_magnitude <= 0:
            raise InadmissibleExactValue("resolved Raman shift requires exact positive support")
        if self.intensity_ratio != EMPTY_ONE and (
            not isinstance(self.intensity_ratio, Fraction) or self.intensity_ratio <= 0
        ):
            raise InadmissibleExactValue("Raman intensity must be exact positive support or absent")


def exact_scattering_relation(incident: Fraction, scattered: Fraction):
    if incident <= 0 or scattered <= 0:
        raise InadmissibleExactValue("incident and scattered resources must be exact positive support")
    if incident == scattered:
        return HeldLabel("raman-scattering-side", "coincident"), EMPTY_ONE
    side = "stokes" if incident > scattered else "anti-stokes"
    return HeldLabel("raman-scattering-side", side), abs(incident - scattered)


def exact_relative_intensity(events: PositiveCount, reference_events: PositiveCount) -> Fraction:
    return Fraction(events.value, reference_events.value)


def complete_raman_vector(rows: tuple[RamanLineRecord, ...]) -> tuple[RamanLineRecord, ...]:
    if not rows or tuple(row.position.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("Raman vector must be complete and ordered")
    boundary = {(row.molecular_carrier, row.condition, row.unit) for row in rows}
    if len(boundary) != 1:
        raise InadmissibleExactValue("Raman vector crossed its retained measurement boundary")
    keys = {(row.initial_state, row.final_state, row.scattering_side) for row in rows}
    if len(keys) != len(rows):
        raise InadmissibleExactValue("Raman vector duplicated a transition-side identity")
    return rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001",
    "SFT-CHEM-MOLECULAR-POLARIZABILITY-006",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-SELECTION-RULE-STRUCTURE-010",
    "SFT-CHEM-VIBRATIONAL-FREQUENCY-009",
    "SFT-CHEM-NMR-RELAXATION-EXCHANGE-008",
)
DIMENSIONS = (
    dimension("carrier", "detached-raman-number", "A number cannot identify the scattering molecule.", "held-molecular-carrier", "Molecular identity remains held."),
    dimension("states", "peak-without-state-transition", "A peak alone loses its molecular transition.", "held-initial-and-final-state", "Both states remain held."),
    dimension("polarizability", "imported-raman-selection-rule", "A named rule cannot replace the derived response change.", "held-polarizability-state-transformation", "The polarizability transformation remains explicit."),
    dimension("position", "signed-floating-line-position", "A signed float is not a native exact relation.", "held-side-positive-exact-shift-or-EmptyOne", "Stokes/anti-Stokes side is held and magnitude is exact positive support or coincidence."),
    dimension("intensity", "arbitrary-normalized-height", "An arbitrary height loses counted comparison support.", "exact-positive-event-ratio-or-EmptyOne", "Intensity is an exact event ratio or recorded absence."),
    dimension("condition", "unconditioned-universal-spectrum", "Excitation, phase, temperature and instrument boundary affect observation.", "held-excitation-condition-and-unit", "All reported conditions and units remain."),
    dimension("custody", "selected-prominent-lines", "Selecting peaks hides weak, adverse, unresolved and absent rows.", "complete-line-intensity-uncertainty-custody", "Every line, intensity, error, bound, absence and unresolved row remains."),
    dimension("extension", "refitted-added-spectrum", "Renormalizing after extension changes prior evidence.", "successor-retains-and-appends-complete-lines", "New lines append without changing prior rows."),
)
EXACT_RESULT = "held-molecular-carrier__held-initial-and-final-state__held-polarizability-state-transformation__held-side-positive-exact-shift-or-EmptyOne__exact-positive-event-ratio-or-EmptyOne__held-excitation-condition-and-unit__complete-line-intensity-uncertainty-custody__successor-retains-and-appends-complete-lines"

_carrier = HeldLabel("molecular-carrier", "molecule-a")
_condition = HeldLabel("raman-condition", "condition-a")
_unit = HeldLabel("reported-unit", "inverse-length")
_state_a = HeldLabel("molecular-state", "state-a")
_state_b = HeldLabel("molecular-state", "state-b")
_state_c = HeldLabel("molecular-state", "state-c")
_stokes, _stokes_shift = exact_scattering_relation(Fraction(10), Fraction(7))
_coincident, _coincident_shift = exact_scattering_relation(Fraction(10), Fraction(10))
_rows = (
    RamanLineRecord(_carrier, _state_a, _state_b, HeldLabel("polarizability-transition", "changes"), _stokes, _stokes_shift, exact_relative_intensity(PositiveCount(3), PositiveCount(5)), _condition, _unit, PositiveCount(1)),
    RamanLineRecord(_carrier, _state_b, _state_c, HeldLabel("polarizability-transition", "unresolved"), _coincident, _coincident_shift, EMPTY_ONE, _condition, _unit, PositiveCount(2)),
)
_vector = complete_raman_vector(_rows)
OPERATIONAL_WITNESSES = (
    ("carrier", "Carrier remains held.", all(row.molecular_carrier == _carrier for row in _vector)),
    ("states", "Both endpoints remain distinct.", _vector[0].initial_state != _vector[0].final_state),
    ("polarizability", "Response transformation remains held.", _vector[0].polarizability_relation.label == "changes"),
    ("position", "Exact Stokes separation is three.", _vector[0].scattering_side.label == "stokes" and _vector[0].shift_magnitude == Fraction(3)),
    ("intensity", "Three events over five are exact.", _vector[0].intensity_ratio == Fraction(3, 5)),
    ("condition", "Condition and unit remain.", all(row.condition == _condition and row.unit == _unit for row in _vector)),
    ("custody", "Coincident and absent intensity remain structural.", _vector[1].shift_magnitude == EMPTY_ONE and _vector[1].intensity_ratio == EMPTY_ONE),
    ("extension", "Successor appends one complete line.", len(complete_raman_vector(_rows + (RamanLineRecord(_carrier, _state_a, _state_c, HeldLabel("polarizability-transition", "changes"), HeldLabel("raman-scattering-side", "anti-stokes"), Fraction(2), Fraction(1, 5), _condition, _unit, PositiveCount(3)),))) == 3),
)
