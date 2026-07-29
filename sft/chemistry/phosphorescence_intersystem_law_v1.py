"""Fold-native phosphorescence and intersystem-transition law (ANAL-011)."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class PhosphorescenceRecord:
    molecular_carrier: HeldLabel
    excitation_state: HeldLabel
    intersystem_state: HeldLabel
    final_state: HeldLabel
    excitation_spin: HeldLabel
    intersystem_spin: HeldLabel
    emission_resource: Fraction | EmptyOne
    outcome_count: PositiveCount | EmptyOne
    excitation_count: PositiveCount
    lifetime: Fraction | EmptyOne
    condition: HeldLabel
    position: PositiveCount

    def __post_init__(self) -> None:
        required = (
            (self.molecular_carrier, "molecular-carrier"),
            (self.excitation_state, "molecular-state"),
            (self.intersystem_state, "molecular-state"),
            (self.final_state, "molecular-state"),
            (self.excitation_spin, "spin-state"),
            (self.intersystem_spin, "spin-state"),
            (self.condition, "photoluminescence-condition"),
        )
        if any(value.family != family for value, family in required):
            raise InadmissibleExactValue("complete phosphorescence identity required")
        if self.excitation_spin == self.intersystem_spin:
            raise InadmissibleExactValue("intersystem transition requires a held spin-state distinction")
        if self.outcome_count == EMPTY_ONE:
            if self.emission_resource != EMPTY_ONE or self.lifetime != EMPTY_ONE:
                raise InadmissibleExactValue("unobserved phosphorescence requires structural EmptyOne")
        else:
            if self.outcome_count.value > self.excitation_count.value:
                raise InadmissibleExactValue("phosphorescence outcomes cannot exceed excitations")
            if not isinstance(self.emission_resource, Fraction) or self.emission_resource <= 0:
                raise InadmissibleExactValue("observed phosphorescence requires exact positive emission")
            if not isinstance(self.lifetime, Fraction) or self.lifetime <= 0:
                raise InadmissibleExactValue("observed phosphorescence requires exact positive lifetime")

    @property
    def exact_yield(self) -> Fraction | EmptyOne:
        if self.outcome_count == EMPTY_ONE:
            return EMPTY_ONE
        return Fraction(self.outcome_count.value, self.excitation_count.value)


def complete_phosphorescence_vector(rows: tuple[PhosphorescenceRecord, ...]) -> tuple[PhosphorescenceRecord, ...]:
    if not rows or tuple(row.position.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("phosphorescence vector must be complete and ordered")
    if len({(row.molecular_carrier, row.condition) for row in rows}) != 1:
        raise InadmissibleExactValue("phosphorescence vector crossed its molecular condition boundary")
    keys = {(row.excitation_state, row.intersystem_state, row.final_state, row.excitation_spin, row.intersystem_spin) for row in rows}
    if len(keys) != len(rows):
        raise InadmissibleExactValue("phosphorescence vector duplicated an intersystem path")
    return rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-SELECTION-RULE-STRUCTURE-010",
    "SFT-CHEM-PHOTOCHEM-001",
    "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006",
    "SFT-CHEM-FLUORESCENCE-YIELD-LIFETIME-010",
)
DIMENSIONS = (
    dimension("carrier", "detached-phosphorescence-number", "A number cannot identify the emitting molecule.", "held-molecular-carrier", "Molecular identity remains held."),
    dimension("spin", "phosphorescence-without-spin-path", "The process loses its defining intersystem distinction.", "held-distinct-source-and-intersystem-spin-states", "Both spin states remain held and distinct."),
    dimension("path", "single-emission-arrow", "A direct arrow erases the intermediate state.", "held-excitation-intersystem-final-state-path", "All three states remain."),
    dimension("emission", "signed-floating-emission-value", "A signed float is not native exact support.", "exact-positive-emission-support-or-EmptyOne", "Emission is exact positive support or structural absence."),
    dimension("yield", "fitted-phosphorescence-yield", "A fitted scalar can hide lost channels.", "exact-outcome-over-excitation-ratio-or-EmptyOne", "Yield is counted exactly or absent."),
    dimension("lifetime", "imported-continuous-tail", "A continuum tail is not a finite observation ledger.", "exact-positive-finite-lifetime-or-EmptyOne", "Lifetime is a finite exact interval or absence."),
    dimension("custody", "selected-long-lived-emissions", "Selection erases quenched, unavailable and unresolved rows.", "complete-emission-lifetime-spin-condition-custody", "Every value, unit, error, condition, adverse and absent row remains."),
    dimension("extension", "refitted-added-intersystem-path", "Refitting changes earlier paths.", "successor-retains-and-appends-complete-paths", "New paths append without changing prior evidence."),
)
EXACT_RESULT = "held-molecular-carrier__held-distinct-source-and-intersystem-spin-states__held-excitation-intersystem-final-state-path__exact-positive-emission-support-or-EmptyOne__exact-outcome-over-excitation-ratio-or-EmptyOne__exact-positive-finite-lifetime-or-EmptyOne__complete-emission-lifetime-spin-condition-custody__successor-retains-and-appends-complete-paths"

_carrier = HeldLabel("molecular-carrier", "molecule-a")
_excited = HeldLabel("molecular-state", "excited-a")
_inter = HeldLabel("molecular-state", "intersystem-a")
_ground = HeldLabel("molecular-state", "ground-a")
_spin_a = HeldLabel("spin-state", "hand-a")
_spin_b = HeldLabel("spin-state", "hand-b")
_condition = HeldLabel("photoluminescence-condition", "condition-a")
_rows = (
    PhosphorescenceRecord(_carrier, _excited, _inter, _ground, _spin_a, _spin_b, Fraction(5, 2), PositiveCount(1), PositiveCount(4), Fraction(7, 3), _condition, PositiveCount(1)),
    PhosphorescenceRecord(_carrier, HeldLabel("molecular-state", "excited-b"), HeldLabel("molecular-state", "intersystem-b"), _ground, _spin_b, _spin_a, EMPTY_ONE, EMPTY_ONE, PositiveCount(4), EMPTY_ONE, _condition, PositiveCount(2)),
)
_vector = complete_phosphorescence_vector(_rows)
OPERATIONAL_WITNESSES = (
    ("carrier", "Carrier remains held.", all(row.molecular_carrier == _carrier for row in _vector)),
    ("spin", "Spin states remain distinct.", all(row.excitation_spin != row.intersystem_spin for row in _vector)),
    ("path", "Intermediate state remains distinct.", _vector[0].intersystem_state not in {_vector[0].excitation_state, _vector[0].final_state}),
    ("emission", "Observed and absent emission remain distinct.", _vector[0].emission_resource == Fraction(5, 2) and _vector[1].emission_resource == EMPTY_ONE),
    ("yield", "One outcome over four excitations is exact.", _vector[0].exact_yield == Fraction(1, 4)),
    ("lifetime", "Finite lifetime remains exact.", _vector[0].lifetime == Fraction(7, 3)),
    ("custody", "Unobserved path remains structural absence.", _vector[1].exact_yield == EMPTY_ONE and _vector[1].lifetime == EMPTY_ONE),
    ("extension", "Complete vector preserves both paths.", complete_phosphorescence_vector(_rows) == _rows),
)
