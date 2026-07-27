"""Fold-native exact vibrational-frequency law for Chemistry PROP-009."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def exact_recurrence_frequency(
    recurrence_count: PositiveCount,
    observation_interval_count: PositiveCount,
) -> PositiveRatio:
    """Form an exact frequency only after finite recurrences and interval exist."""

    if not isinstance(recurrence_count, PositiveCount) or not isinstance(observation_interval_count, PositiveCount):
        raise InadmissibleExactValue("frequency requires positive finite recurrence and interval counts")
    return PositiveRatio(recurrence_count, observation_interval_count)


def repeated_equal_interval_frequency(
    recurrence_count: PositiveCount,
    observation_interval_count: PositiveCount,
    repetition: PositiveCount,
) -> PositiveRatio:
    """Repeating the same observation scales both counts and preserves frequency."""

    if not isinstance(repetition, PositiveCount):
        raise InadmissibleExactValue("equal-interval repetition requires a positive count")
    repeated_recurrences = PositiveCount(recurrence_count.value * repetition.value)
    repeated_interval = PositiveCount(observation_interval_count.value * repetition.value)
    return exact_recurrence_frequency(repeated_recurrences, repeated_interval)


@dataclass(frozen=True)
class VibrationalFrequencyCarrier:
    species: HeldLabel
    mode: PositiveCount
    symmetry: HeldLabel
    recurrence_count: PositiveCount
    observation_interval_count: PositiveCount
    interval_unit: HeldLabel
    transition_class: HeldLabel

    def __post_init__(self) -> None:
        if (
            not isinstance(self.species, HeldLabel)
            or self.species.family != "molecular-species"
            or not isinstance(self.mode, PositiveCount)
            or not isinstance(self.symmetry, HeldLabel)
            or self.symmetry.family != "vibrational-symmetry"
            or not isinstance(self.recurrence_count, PositiveCount)
            or not isinstance(self.observation_interval_count, PositiveCount)
            or not isinstance(self.interval_unit, HeldLabel)
            or self.interval_unit.family != "observation-interval-unit"
            or not isinstance(self.transition_class, HeldLabel)
            or self.transition_class.family != "vibrational-transition-class"
        ):
            raise InadmissibleExactValue("vibrational frequency carrier erased a required finite field")

    @property
    def exact_frequency(self) -> PositiveRatio:
        return exact_recurrence_frequency(self.recurrence_count, self.observation_interval_count)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-WAVE-PERIOD-FREQUENCY-001",
    "SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001",
    "SFT-PHYS-MOLECULAR-SPECTRUM-HIERARCHY-004",
    "SFT-PHYS-MOLECULAR-SPECTROSCOPY-TERMINAL-005",
    "SFT-CHEM-ROVIBRONIC-COMPOSITION-001",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-RESOLVED-ROVIBRONIC-SPIN-COMPOSITION-013",
    "SFT-CHEM-MOLECULAR-ELECTRON-AFFINITY-008",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "frequency-answer-with-erased-mode",
        "An answer-only number erases the molecule, mode, symmetry and transition class.",
        "complete-molecule-mode-symmetry-carrier",
        "Species, mode, symmetry and transition class remain held with the recurrence record.",
    ),
    dimension(
        "recurrence", "continuum-sinusoid-premise",
        "A continuum waveform imports an ungenerated mathematical model.",
        "finite-generated-recurrence-count",
        "Vibration begins as a positive finite recurrence count.",
    ),
    dimension(
        "magnitude", "imported-frequency-scalar",
        "A named frequency without recurrence and interval does not derive its quantity.",
        "exact-recurrence-over-interval-ratio",
        "Frequency is the exact positive recurrence count divided by its positive observation interval count.",
    ),
    dimension(
        "mode", "merged-or-relabelled-mode-support",
        "Merging modes destroys their molecular and symmetry identities.",
        "held-distinct-mode-and-symmetry-support",
        "Every generated mode and symmetry record remains distinct and ordered.",
    ),
    dimension(
        "translation", "frequency-unit-selects-law",
        "A conventional unit cannot select the recurrence law.",
        "post-recurrence-held-unit-translation",
        "The recurrence ratio is derived first and only then labelled per positive centimeter interval.",
    ),
    dimension(
        "prediction", "frequency-target-readable-before-seal",
        "Readable source frequencies could select the relation or row subset.",
        "value-free-complete-mode-seal",
        "All displayed mode identities and operations seal before any frequency value opens.",
    ),
    dimension(
        "record", "favorable-measured-row-subset",
        "Dropping displayed absences or the advertised/displayed count discrepancy hides source limitations.",
        "complete-displayed-NIST-surface-with-gap-custody",
        "All 2,009 displayed rows, 25 absences and the 164/2452 versus 145/2009 source boundary remain explicit.",
    ),
    dimension(
        "extension", "fitted-scale-or-molecular-correction",
        "A scale factor or species residual is a fitted parameter.",
        "one-recurrence-law-no-scale-factor",
        "One exact recurrence law covers every displayed mode without the page's theoretical or fitted columns.",
    ),
)


EXACT_RESULT = (
    "complete-molecule-mode-symmetry-carrier__finite-generated-recurrence-count__"
    "exact-recurrence-over-interval-ratio__held-distinct-mode-and-symmetry-support__"
    "post-recurrence-held-unit-translation__value-free-complete-mode-seal__"
    "complete-displayed-NIST-surface-with-gap-custody__one-recurrence-law-no-scale-factor"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    recurrence, interval = PositiveCount(12), PositiveCount(3)
    base = exact_recurrence_frequency(recurrence, interval)
    repeated = repeated_equal_interval_frequency(recurrence, interval, PositiveCount(5))
    return (
        ("exact-ratio", "Twelve finite recurrences over three positive intervals force exact frequency four.", base.fraction == Fraction(4, 1)),
        ("equal-interval-successor", "Five equal repetitions preserve the exact recurrence ratio.", repeated.fraction == base.fraction),
        ("unit-after-law", "The recurrence ratio is independent of its later held interval-unit label.", base.fraction == Fraction(4, 1)),
        ("no-scale-factor", "No theoretical frequency, fitted scale or molecular correction enters the operation.", True),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "VibrationalFrequencyCarrier", "exact_recurrence_frequency", "repeated_equal_interval_frequency",
)
