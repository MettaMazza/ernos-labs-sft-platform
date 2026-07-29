"""Fold-native NMR chemical-shift relation (ANAL-006)."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class NMRShiftRecord:
    molecular_carrier: HeldLabel
    nucleus: HeldLabel
    site: HeldLabel
    reference: HeldLabel
    solvent: HeldLabel
    condition: HeldLabel
    position: PositiveCount
    shift_side: HeldLabel
    shift_magnitude: Fraction | EmptyOne
    uncertainty: Fraction | EmptyOne

    def __post_init__(self) -> None:
        families = (
            self.molecular_carrier.family,
            self.nucleus.family,
            self.site.family,
            self.reference.family,
            self.solvent.family,
            self.condition.family,
            self.shift_side.family,
        )
        if families != (
            "molecular-carrier", "nmr-nucleus", "nuclear-site", "nmr-reference",
            "solvent", "nmr-condition", "chemical-shift-side",
        ):
            raise InadmissibleExactValue("complete held NMR shift identity required")
        if self.shift_side.label not in {"higher-frequency", "lower-frequency", "coincident"}:
            raise InadmissibleExactValue("chemical-shift side is not generated")
        if self.shift_side.label == "coincident":
            if self.shift_magnitude != EMPTY_ONE:
                raise InadmissibleExactValue("coincident shift requires structural EmptyOne")
        elif not isinstance(self.shift_magnitude, Fraction) or self.shift_magnitude <= 0:
            raise InadmissibleExactValue("a resolved NMR shift requires an exact positive magnitude")
        if self.uncertainty != EMPTY_ONE and (
            not isinstance(self.uncertainty, Fraction) or self.uncertainty <= 0
        ):
            raise InadmissibleExactValue("reported uncertainty must be positive or structurally absent")


def exact_shift_relation(sample_frequency: Fraction, reference_frequency: Fraction):
    """Return held direction and exact relative separation without a signed proof value."""
    if sample_frequency <= 0 or reference_frequency <= 0:
        raise InadmissibleExactValue("NMR frequencies require exact positive support")
    if sample_frequency == reference_frequency:
        return HeldLabel("chemical-shift-side", "coincident"), EMPTY_ONE
    side = "higher-frequency" if sample_frequency > reference_frequency else "lower-frequency"
    return HeldLabel("chemical-shift-side", side), abs(sample_frequency - reference_frequency) / reference_frequency


def complete_shift_vector(rows: tuple[NMRShiftRecord, ...]) -> tuple[NMRShiftRecord, ...]:
    if not rows or tuple(row.position.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("NMR shift vector must be complete and ordered")
    boundary = {
        (row.molecular_carrier, row.reference, row.solvent, row.condition)
        for row in rows
    }
    if len(boundary) != 1:
        raise InadmissibleExactValue("NMR shift vector crossed a retained comparison boundary")
    if len({(row.nucleus, row.site) for row in rows}) != len(rows):
        raise InadmissibleExactValue("NMR shift vector duplicated a nucleus-site identity")
    return rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-CHEM-MEAS-TRACEABILITY-001",
    "SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001",
    "SFT-CHEM-ANALYTICAL-SELECTIVITY-INTERFERENCE-005",
)
DIMENSIONS = (
    dimension("identity", "detached-shift-number", "A scalar cannot identify a molecular observation.", "held-molecular-carrier", "The molecular carrier remains held."),
    dimension("nucleus", "element-only-spectrum", "Element name loses isotope and observed nucleus.", "held-nucleus-identity", "The observed nucleus remains explicit."),
    dimension("site", "unordered-peak-list", "An unordered list loses molecular attribution.", "complete-nucleus-site-map", "Every shift retains its nuclear site."),
    dimension("reference", "absolute-frequency-relabeled-shift", "A shift exists only relative to a named reference.", "held-reference-comparison", "Reference identity and comparison remain."),
    dimension("environment", "unconditioned-universal-shift", "Solvent and conditions can change the observation.", "held-solvent-and-condition", "Solvent and all reported conditions remain."),
    dimension("relation", "signed-or-floating-shift-premise", "A sign or float is not a native exact relation.", "held-side-positive-exact-ratio-or-EmptyOne", "Direction is held and magnitude is exact positive support or coincidence."),
    dimension("custody", "selected-assigned-peaks", "Selection hides ambiguity and adverse rows.", "complete-shift-uncertainty-ambiguity-custody", "Every measured, uncertain, ambiguous, absent and adverse row remains."),
    dimension("extension", "renormalized-added-spectrum", "Renormalization erases prior custody.", "successor-retains-and-appends-complete-sites", "A successor appends complete sites without changing prior rows."),
)
EXACT_RESULT = "held-molecular-carrier__held-nucleus-identity__complete-nucleus-site-map__held-reference-comparison__held-solvent-and-condition__held-side-positive-exact-ratio-or-EmptyOne__complete-shift-uncertainty-ambiguity-custody__successor-retains-and-appends-complete-sites"

_carrier = HeldLabel("molecular-carrier", "molecule-a")
_reference = HeldLabel("nmr-reference", "reference-a")
_solvent = HeldLabel("solvent", "solvent-a")
_condition = HeldLabel("nmr-condition", "condition-a")
_side_a, _magnitude_a = exact_shift_relation(Fraction(1001), Fraction(1000))
_side_b, _magnitude_b = exact_shift_relation(Fraction(1000), Fraction(1000))
_rows = (
    NMRShiftRecord(_carrier, HeldLabel("nmr-nucleus", "one-H"), HeldLabel("nuclear-site", "site-a"), _reference, _solvent, _condition, PositiveCount(1), _side_a, _magnitude_a, Fraction(1, 10000)),
    NMRShiftRecord(_carrier, HeldLabel("nmr-nucleus", "one-H"), HeldLabel("nuclear-site", "site-b"), _reference, _solvent, _condition, PositiveCount(2), _side_b, _magnitude_b, EMPTY_ONE),
)
_vector = complete_shift_vector(_rows)
OPERATIONAL_WITNESSES = (
    ("identity", "Molecular carrier retained.", _vector[0].molecular_carrier == _carrier),
    ("nucleus", "Nucleus retained.", _vector[0].nucleus.label == "one-H"),
    ("site", "Distinct sites retained.", len({row.site for row in _vector}) == 2),
    ("reference", "Reference retained.", all(row.reference == _reference for row in _vector)),
    ("environment", "Solvent and condition retained.", all(row.solvent == _solvent and row.condition == _condition for row in _vector)),
    ("relation", "Exact relative separation forced.", _vector[0].shift_magnitude == Fraction(1, 1000) and _vector[1].shift_magnitude == EMPTY_ONE),
    ("custody", "Uncertainty and coincidence remain distinct.", _vector[0].uncertainty == Fraction(1, 10000) and _vector[1].shift_side.label == "coincident"),
    ("extension", "Complete successor appends one site.", len(complete_shift_vector(_rows + (NMRShiftRecord(_carrier, HeldLabel("nmr-nucleus", "one-H"), HeldLabel("nuclear-site", "site-c"), _reference, _solvent, _condition, PositiveCount(3), _side_a, _magnitude_a, EMPTY_ONE),))) == 3),
)
