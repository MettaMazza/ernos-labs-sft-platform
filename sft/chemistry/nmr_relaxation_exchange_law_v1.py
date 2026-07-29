"""Fold-native NMR relaxation and molecular exchange law (ANAL-008)."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class NMRTimedTransitionRecord:
    molecular_carrier: HeldLabel
    site: HeldLabel
    process: HeldLabel
    source_state: HeldLabel
    destination_state: HeldLabel
    condition: HeldLabel
    position: PositiveCount
    magnitude: Fraction | EmptyOne
    unit: HeldLabel
    uncertainty: Fraction | EmptyOne
    status: HeldLabel

    def __post_init__(self) -> None:
        if (
            self.molecular_carrier.family,
            self.site.family,
            self.process.family,
            self.source_state.family,
            self.destination_state.family,
            self.condition.family,
            self.unit.family,
            self.status.family,
        ) != (
            "molecular-carrier", "nucleus-site", "nmr-process", "molecular-state",
            "molecular-state", "nmr-condition", "reported-unit", "measurement-status",
        ):
            raise InadmissibleExactValue("complete held NMR transition identity required")
        if self.process.label not in {"longitudinal-relaxation", "transverse-relaxation", "rotating-frame-relaxation", "hydrogen-exchange"}:
            raise InadmissibleExactValue("NMR transition process is not generated")
        if self.status.label not in {"measured", "bounded", "unavailable", "unresolved"}:
            raise InadmissibleExactValue("NMR transition status is not generated")
        if self.status.label in {"unavailable", "unresolved"}:
            if self.magnitude != EMPTY_ONE:
                raise InadmissibleExactValue("unavailable transition magnitude requires structural EmptyOne")
        elif not isinstance(self.magnitude, Fraction) or self.magnitude <= 0:
            raise InadmissibleExactValue("measured transition magnitude must be exact and positive")
        if self.uncertainty != EMPTY_ONE and (
            not isinstance(self.uncertainty, Fraction) or self.uncertainty <= 0
        ):
            raise InadmissibleExactValue("transition uncertainty must be positive or structurally absent")


def exact_transition_rate(event_count: PositiveCount, observation_interval: Fraction) -> Fraction:
    if observation_interval <= 0:
        raise InadmissibleExactValue("transition interval must be exact positive support")
    return Fraction(event_count.value, 1) / observation_interval


def complete_transition_vector(rows: tuple[NMRTimedTransitionRecord, ...]) -> tuple[NMRTimedTransitionRecord, ...]:
    if not rows or tuple(row.position.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("NMR transition vector must be complete and ordered")
    if len({(row.process, row.site, row.source_state, row.destination_state) for row in rows}) != len(rows):
        raise InadmissibleExactValue("NMR transition vector duplicated a process-state identity")
    if len({(row.molecular_carrier, row.condition) for row in rows}) != 1:
        raise InadmissibleExactValue("NMR transition vector crossed its molecular condition boundary")
    return rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001",
    "SFT-CHEM-NMR-SPIN-COUPLING-007",
)
DIMENSIONS = (
    dimension("carrier", "detached-relaxation-or-exchange-number", "A number alone cannot identify the relaxing or exchanging molecule.", "held-molecular-carrier-and-site", "Molecule and observed site remain held."),
    dimension("states", "single-state-decay-label", "A transition requires source and destination states.", "held-source-and-destination-states", "Both molecular states remain."),
    dimension("process", "generic-dynamics-label", "Different NMR processes cannot be conflated.", "held-relaxation-or-exchange-process", "T1, T2, T1rho and exchange remain distinct process classes."),
    dimension("resource", "continuous-time-premise", "An ungenerated continuum is not an observation ledger.", "finite-positive-observation-interval", "Every value is bound to a finite measured interval or rate unit."),
    dimension("relation", "imported-exponential-or-fitted-rate", "A fitted decay form cannot force the transition law.", "exact-positive-time-or-counted-transition-rate", "The relation is an exact time or counted-event rate."),
    dimension("observation", "unconditioned-universal-dynamics", "Relaxation and exchange are method and condition bound.", "held-condition-unit-and-uncertainty", "Condition, unit and uncertainty remain."),
    dimension("adversity", "missing-or-unfavorable-rows-erased", "Erasure manufactures a complete trend.", "measured-bounded-unavailable-unresolved-custody", "All outcome classes remain, with EmptyOne for absent magnitudes."),
    dimension("extension", "refitted-added-timescale", "Refitting changes prior evidence.", "successor-retains-and-appends-complete-transitions", "New process rows append without altering earlier records."),
)
EXACT_RESULT = "held-molecular-carrier-and-site__held-source-and-destination-states__held-relaxation-or-exchange-process__finite-positive-observation-interval__exact-positive-time-or-counted-transition-rate__held-condition-unit-and-uncertainty__measured-bounded-unavailable-unresolved-custody__successor-retains-and-appends-complete-transitions"

_carrier = HeldLabel("molecular-carrier", "molecule-a")
_condition = HeldLabel("nmr-condition", "condition-a")
_site_a = HeldLabel("nucleus-site", "site-a")
_site_b = HeldLabel("nucleus-site", "site-b")
_state_a = HeldLabel("molecular-state", "state-a")
_state_b = HeldLabel("molecular-state", "state-b")
_rows = (
    NMRTimedTransitionRecord(_carrier, _site_a, HeldLabel("nmr-process", "longitudinal-relaxation"), _state_a, _state_a, _condition, PositiveCount(1), Fraction(3, 2), HeldLabel("reported-unit", "seconds"), Fraction(1, 100), HeldLabel("measurement-status", "measured")),
    NMRTimedTransitionRecord(_carrier, _site_b, HeldLabel("nmr-process", "hydrogen-exchange"), _state_a, _state_b, _condition, PositiveCount(2), Fraction(5, 3), HeldLabel("reported-unit", "per-second"), EMPTY_ONE, HeldLabel("measurement-status", "measured")),
    NMRTimedTransitionRecord(_carrier, _site_a, HeldLabel("nmr-process", "rotating-frame-relaxation"), _state_a, _state_a, _condition, PositiveCount(3), EMPTY_ONE, HeldLabel("reported-unit", "seconds"), EMPTY_ONE, HeldLabel("measurement-status", "unavailable")),
)
_vector = complete_transition_vector(_rows)
OPERATIONAL_WITNESSES = (
    ("carrier", "Carrier and sites retained.", all(row.molecular_carrier == _carrier for row in _vector) and len({row.site for row in _vector}) == 2),
    ("states", "Source and destination states retained.", _vector[1].source_state != _vector[1].destination_state),
    ("process", "Relaxation and exchange remain distinct.", len({row.process for row in _vector}) == 3),
    ("resource", "Finite positive interval retained.", _vector[0].magnitude == Fraction(3, 2)),
    ("relation", "Counted rate exact.", exact_transition_rate(PositiveCount(5), Fraction(3)) == Fraction(5, 3)),
    ("observation", "Condition, unit and uncertainty retained.", _vector[0].condition == _condition and _vector[0].unit.label == "seconds" and _vector[0].uncertainty == Fraction(1, 100)),
    ("adversity", "Unavailable row remains EmptyOne.", _vector[2].status.label == "unavailable" and _vector[2].magnitude == EMPTY_ONE),
    ("extension", "Complete successor appends transition.", len(complete_transition_vector(_rows + (NMRTimedTransitionRecord(_carrier, _site_b, HeldLabel("nmr-process", "transverse-relaxation"), _state_b, _state_b, _condition, PositiveCount(4), Fraction(4, 3), HeldLabel("reported-unit", "seconds"), EMPTY_ONE, HeldLabel("measurement-status", "bounded")),))) == 4),
)
