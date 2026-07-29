"""Fold-native fluorescence emission, yield and lifetime law (ANAL-010)."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class FluorescenceChannelRecord:
    molecular_carrier: HeldLabel
    initial_state: HeldLabel
    final_state: HeldLabel
    channel: HeldLabel
    emitted_resource: Fraction | EmptyOne
    outcome_count: PositiveCount | EmptyOne
    excitation_count: PositiveCount
    lifetime: Fraction | EmptyOne
    condition: HeldLabel
    position: PositiveCount

    def __post_init__(self) -> None:
        required = (
            (self.molecular_carrier, "molecular-carrier"),
            (self.initial_state, "molecular-state"),
            (self.final_state, "molecular-state"),
            (self.channel, "fluorescence-channel"),
            (self.condition, "photoluminescence-condition"),
        )
        if any(value.family != family for value, family in required):
            raise InadmissibleExactValue("complete fluorescence channel identity required")
        if self.channel.label not in {"radiative-fluorescence", "nonradiative", "unresolved"}:
            raise InadmissibleExactValue("fluorescence channel is not generated")
        if self.channel.label == "radiative-fluorescence":
            if not isinstance(self.emitted_resource, Fraction) or self.emitted_resource <= 0:
                raise InadmissibleExactValue("radiative fluorescence requires exact positive emitted support")
        elif self.emitted_resource != EMPTY_ONE:
            raise InadmissibleExactValue("non-emitting or unresolved channel requires structural EmptyOne")
        if self.outcome_count != EMPTY_ONE and self.outcome_count.value > self.excitation_count.value:
            raise InadmissibleExactValue("channel outcomes cannot exceed excitations")
        if self.lifetime != EMPTY_ONE and (not isinstance(self.lifetime, Fraction) or self.lifetime <= 0):
            raise InadmissibleExactValue("fluorescence lifetime must be exact positive support or absent")

    @property
    def exact_yield(self) -> Fraction | EmptyOne:
        if self.outcome_count == EMPTY_ONE:
            return EMPTY_ONE
        return Fraction(self.outcome_count.value, self.excitation_count.value)


def complete_fluorescence_partition(rows: tuple[FluorescenceChannelRecord, ...]) -> tuple[FluorescenceChannelRecord, ...]:
    if not rows or tuple(row.position.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("fluorescence channel vector must be complete and ordered")
    if len({(row.molecular_carrier, row.initial_state, row.condition, row.excitation_count) for row in rows}) != 1:
        raise InadmissibleExactValue("fluorescence partition crossed its excitation boundary")
    if len({(row.final_state, row.channel) for row in rows}) != len(rows):
        raise InadmissibleExactValue("fluorescence partition duplicated a channel endpoint")
    resolved = tuple(row.outcome_count for row in rows if row.outcome_count != EMPTY_ONE)
    if sum(item.value for item in resolved) != rows[0].excitation_count.value:
        raise InadmissibleExactValue("resolved fluorescence channels must partition every excitation")
    return rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-SELECTION-RULE-STRUCTURE-010",
    "SFT-CHEM-PHOTOCHEM-001",
    "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006",
    "SFT-CHEM-NMR-RELAXATION-EXCHANGE-008",
    "SFT-CHEM-RAMAN-TRANSITION-INTENSITY-009",
)
DIMENSIONS = (
    dimension("carrier", "detached-fluorescence-number", "A number cannot identify the emitting molecule.", "held-molecular-carrier-and-excitation", "Molecule and excitation remain held."),
    dimension("transition", "emission-peak-without-states", "A peak alone loses its transition endpoints.", "held-initial-and-final-molecular-states", "Both states remain."),
    dimension("channels", "radiative-channel-only", "Ignoring nonradiative outcomes inflates yield.", "complete-radiative-nonradiative-partition", "Every excitation terminates in one retained channel."),
    dimension("emission", "signed-floating-emission-value", "A signed float is not a native emission relation.", "exact-positive-emission-support-or-EmptyOne", "Emission is exact positive support or structural absence."),
    dimension("yield", "fitted-quantum-yield", "A fitted scalar can hide omitted outcomes.", "exact-outcome-over-excitation-ratio", "Yield is a counted exact ratio."),
    dimension("lifetime", "imported-continuous-decay-law", "A continuum decay form cannot force a finite observation.", "exact-positive-observation-lifetime-or-EmptyOne", "Lifetime is a finite exact resource interval or absence."),
    dimension("custody", "selected-bright-favorable-records", "Selection erases quenching, uncertainty and missing rows.", "complete-emission-yield-lifetime-condition-custody", "Every value, unit, error, condition, adverse and absent row remains."),
    dimension("extension", "refitted-added-channel", "Refitting changes prior yields.", "successor-retains-and-repartitions-complete-counts", "A successor retains prior counts and recomputes the complete partition."),
)
EXACT_RESULT = "held-molecular-carrier-and-excitation__held-initial-and-final-molecular-states__complete-radiative-nonradiative-partition__exact-positive-emission-support-or-EmptyOne__exact-outcome-over-excitation-ratio__exact-positive-observation-lifetime-or-EmptyOne__complete-emission-yield-lifetime-condition-custody__successor-retains-and-repartitions-complete-counts"

_carrier = HeldLabel("molecular-carrier", "molecule-a")
_initial = HeldLabel("molecular-state", "excited-a")
_ground = HeldLabel("molecular-state", "ground-a")
_other = HeldLabel("molecular-state", "other-a")
_condition = HeldLabel("photoluminescence-condition", "condition-a")
_rows = (
    FluorescenceChannelRecord(_carrier, _initial, _ground, HeldLabel("fluorescence-channel", "radiative-fluorescence"), Fraction(7, 3), PositiveCount(3), PositiveCount(5), Fraction(2, 3), _condition, PositiveCount(1)),
    FluorescenceChannelRecord(_carrier, _initial, _other, HeldLabel("fluorescence-channel", "nonradiative"), EMPTY_ONE, PositiveCount(2), PositiveCount(5), EMPTY_ONE, _condition, PositiveCount(2)),
)
_vector = complete_fluorescence_partition(_rows)
OPERATIONAL_WITNESSES = (
    ("carrier", "Carrier and excitation remain.", all(row.molecular_carrier == _carrier and row.initial_state == _initial for row in _vector)),
    ("transition", "Both channel endpoints remain.", len({row.final_state for row in _vector}) == 2),
    ("channels", "Radiative and nonradiative counts partition five.", sum(row.outcome_count.value for row in _vector) == 5),
    ("emission", "Only the radiative channel emits.", _vector[0].emitted_resource == Fraction(7, 3) and _vector[1].emitted_resource == EMPTY_ONE),
    ("yield", "Radiative yield is three fifths.", _vector[0].exact_yield == Fraction(3, 5)),
    ("lifetime", "Finite lifetime remains exact.", _vector[0].lifetime == Fraction(2, 3)),
    ("custody", "Nonradiative absence is retained.", _vector[1].lifetime == EMPTY_ONE),
    ("extension", "Complete partition is ordered and stable.", complete_fluorescence_partition(_rows) == _rows),
)
