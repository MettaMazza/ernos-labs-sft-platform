"""Fold-native kinetic isotope-effect relation for Chemistry KIN-012."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True, order=True)
class ExactPositiveEventRate:
    completed_events: PositiveCount
    observation_parts: PositiveCount
    value: Fraction

    @classmethod
    def from_counts(cls, completed_events: PositiveCount, observation_parts: PositiveCount) -> "ExactPositiveEventRate":
        if not isinstance(completed_events, PositiveCount) or not isinstance(observation_parts, PositiveCount):
            raise InadmissibleExactValue("isotopologue rate requires exact positive counts")
        return cls(completed_events, observation_parts, Fraction(completed_events.value, observation_parts.value))

    def __post_init__(self) -> None:
        if not isinstance(self.value, Fraction) or self.value <= 0:
            raise InadmissibleExactValue("isotopologue event rate must be exact and positive")
        if self.value != Fraction(self.completed_events.value, self.observation_parts.value):
            raise InadmissibleExactValue("isotopologue event rate must equal its complete exact count relation")


@dataclass(frozen=True)
class RetainedIsotopologuePath:
    reaction_identity: HeldLabel
    path_identity: HeldLabel
    isotopologue_identity: HeldLabel
    ordered_path_roles: tuple[HeldLabel, ...]
    condition_identity: HeldLabel
    event_rate: ExactPositiveEventRate
    evidence_status: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "held-isotope-reaction-identity":
            raise InadmissibleExactValue("isotope reaction identity must remain held")
        if not isinstance(self.path_identity, HeldLabel) or self.path_identity.family != "held-complete-reaction-path":
            raise InadmissibleExactValue("complete reaction path identity must remain held")
        if not isinstance(self.isotopologue_identity, HeldLabel) or self.isotopologue_identity.family != "held-isotopologue-identity":
            raise InadmissibleExactValue("isotopologue identity must remain held")
        if len(self.ordered_path_roles) < 2 or any(
            not isinstance(role, HeldLabel) or role.family != "registered-reaction-path-role"
            for role in self.ordered_path_roles
        ):
            raise InadmissibleExactValue("isotopologue comparison requires a complete finite reaction path")
        if len(set(self.ordered_path_roles)) != len(self.ordered_path_roles):
            raise InadmissibleExactValue("reaction path roles must remain distinct and ordered")
        if not isinstance(self.condition_identity, HeldLabel) or self.condition_identity.family != "held-isotope-reaction-condition":
            raise InadmissibleExactValue("isotopologue condition must remain held")
        if not isinstance(self.event_rate, ExactPositiveEventRate):
            raise InadmissibleExactValue("isotopologue path requires an exact positive event rate")
        if not isinstance(self.evidence_status, HeldLabel) or self.evidence_status.family != "held-isotope-rate-status":
            raise InadmissibleExactValue("isotopologue evidence status must remain held")


@dataclass(frozen=True)
class CompleteIsotopologueRatePair:
    ordered_pair_identity: HeldLabel
    numerator_path: RetainedIsotopologuePath
    denominator_path: RetainedIsotopologuePath

    def __post_init__(self) -> None:
        if not isinstance(self.ordered_pair_identity, HeldLabel) or self.ordered_pair_identity.family != "registered-ordered-isotopologue-pair":
            raise InadmissibleExactValue("isotopologue comparison pair must be registered")
        if not isinstance(self.numerator_path, RetainedIsotopologuePath) or not isinstance(self.denominator_path, RetainedIsotopologuePath):
            raise InadmissibleExactValue("isotopologue comparison requires two retained paths")
        if self.numerator_path.isotopologue_identity == self.denominator_path.isotopologue_identity:
            raise InadmissibleExactValue("isotopologue comparison requires two distinct held isotope identities")
        for field in ("reaction_identity", "path_identity", "ordered_path_roles", "condition_identity"):
            if getattr(self.numerator_path, field) != getattr(self.denominator_path, field):
                raise InadmissibleExactValue("isotopologue rates must retain the same reaction, path and condition")


@dataclass(frozen=True)
class ExactKineticIsotopeEffectRelation:
    ordered_pair_identity: HeldLabel
    numerator_isotopologue: HeldLabel
    denominator_isotopologue: HeldLabel
    complete_reaction_path: tuple[HeldLabel, ...]
    exact_rate_ratio: Fraction
    ratio_orientation: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.exact_rate_ratio, Fraction) or self.exact_rate_ratio <= 0:
            raise InadmissibleExactValue("kinetic isotope-effect relation must be exact and positive")


def forced_kinetic_isotope_effect_relation(pair: CompleteIsotopologueRatePair) -> ExactKineticIsotopeEffectRelation:
    if not isinstance(pair, CompleteIsotopologueRatePair):
        raise InadmissibleExactValue("kinetic isotope relation requires one complete ordered isotopologue pair")
    numerator = pair.numerator_path.event_rate.value
    denominator = pair.denominator_path.event_rate.value
    ratio = numerator / denominator
    if ratio > 1:
        orientation = "numerator-rate-greater"
    elif ratio < 1:
        orientation = "denominator-rate-greater"
    else:
        orientation = "rates-exactly-equal"
    return ExactKineticIsotopeEffectRelation(
        pair.ordered_pair_identity,
        pair.numerator_path.isotopologue_identity,
        pair.denominator_path.isotopologue_identity,
        pair.numerator_path.ordered_path_roles,
        ratio,
        HeldLabel("held-rate-ratio-orientation", orientation),
    )


@dataclass(frozen=True)
class RegisteredIsotopologuePairOccurrence:
    source_occurrence: PositiveCount
    pair: CompleteIsotopologueRatePair

    def __post_init__(self) -> None:
        if not isinstance(self.source_occurrence, PositiveCount):
            raise InadmissibleExactValue("isotopologue pair source occurrence must be positive")
        forced_kinetic_isotope_effect_relation(self.pair)


@dataclass(frozen=True)
class CompleteKineticIsotopeFamily:
    ordered_occurrences: tuple[RegisteredIsotopologuePairOccurrence, ...]

    def __post_init__(self) -> None:
        if not self.ordered_occurrences or any(not isinstance(row, RegisteredIsotopologuePairOccurrence) for row in self.ordered_occurrences):
            raise InadmissibleExactValue("kinetic isotope family requires at least one complete pair")
        if tuple(row.source_occurrence.value for row in self.ordered_occurrences) != tuple(range(1, len(self.ordered_occurrences) + 1)):
            raise InadmissibleExactValue("kinetic isotope pair occurrences must be complete and gap-free")


def append_isotopologue_pair_preserves_complete_family(
    family: CompleteKineticIsotopeFamily,
    successor: RegisteredIsotopologuePairOccurrence,
) -> bool:
    if successor.source_occurrence.value != len(family.ordered_occurrences) + 1:
        raise InadmissibleExactValue("kinetic isotope successor must be the next positive occurrence")
    prior = tuple(forced_kinetic_isotope_effect_relation(row.pair) for row in family.ordered_occurrences)
    extended = CompleteKineticIsotopeFamily(family.ordered_occurrences + (successor,))
    results = tuple(forced_kinetic_isotope_effect_relation(row.pair) for row in extended.ordered_occurrences)
    return results[: len(prior)] == prior and len(results) == len(prior) + 1


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-ELEM-ISOTOPE-001", "SFT-CHEM-NUCLEAR-ELECTRONIC-COMPOSITION-012",
    "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001", "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002",
    "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003", "SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004",
    "SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005", "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006",
    "SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007", "SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
    "SFT-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-CORRESPONDENCE-009",
    "SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010",
    "SFT-CHEM-DIFFUSION-LIMITED-REACTION-BOUNDARY-011",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("identity", "isotopologue-identities-collapsed-or-replaced-by-numerical-mass", "Collapsed or numerical identities cannot preserve which reaction carrier changed.", "two-distinct-held-isotopologue-identities", "Both isotope identities remain exact held labels."),
    dimension("path", "different-truncated-or-answer-only-paths-compared", "Different or truncated paths do not isolate an isotope relation.", "same-complete-reaction-path-and-condition", "Every path role and condition is identical except the held isotope label."),
    dimension("rate", "imported-rate-law-continuum-time-or-fitted-rate", "An imported or fitted rate can select the result.", "completed-events-per-exact-positive-observation-parts", "Each rate is independently forced by exact positive counts."),
    dimension("relation", "imported-KIE-mass-frequency-exponent-or-statistical-law", "An imported isotope-effect model is not forced by the retained pair.", "ordered-quotient-of-two-exact-positive-event-rates", "The pair itself forces one exact positive rate ratio."),
    dimension("orientation", "signed-difference-negative-or-zero-number", "A signed difference imports forbidden numerical structure.", "positive-ratio-plus-held-greater-less-or-equal-orientation", "Magnitude stays exact positive and direction is a held label."),
    dimension("observation", "selected-average-or-single-favorable-isotope-effect", "Selection or averaging erases replicates, normal, inverse and equal cases.", "complete-90-rate-ratio-3-decay-and-adverse-vector", "All rate-ratio replicates, direct decays and adverse records remain distinct."),
    dimension("provenance", "experimental-fitted-calculated-and-interpretive-records-mixed", "Mixed provenance lets an interpretation masquerade as measurement.", "experimental-vectors-separated-from-source-models-and-review-questions", "Measurements, models and reviewer challenges remain separately classified."),
    dimension("prediction", "rate-ratio-value-workbook-or-target-readable-before-seal", "Target access can select the law.", "value-free-71-record-identity-seal-and-depth-independent-pair-successor", "All identities seal before values and pair extension preserves prior results."),
)


EXACT_RESULT = (
    "two-distinct-held-isotopologue-identities__same-complete-reaction-path-and-condition__"
    "completed-events-per-exact-positive-observation-parts__ordered-quotient-of-two-exact-positive-event-rates__"
    "positive-ratio-plus-held-greater-less-or-equal-orientation__complete-90-rate-ratio-3-decay-and-adverse-vector__"
    "experimental-vectors-separated-from-source-models-and-review-questions__"
    "value-free-71-record-identity-seal-and-depth-independent-pair-successor"
)


def _path(isotope: str, events: int, parts: int, pair_label: str = "pair-a") -> RetainedIsotopologuePath:
    return RetainedIsotopologuePath(
        HeldLabel("held-isotope-reaction-identity", "reaction-a"),
        HeldLabel("held-complete-reaction-path", "path-a"),
        HeldLabel("held-isotopologue-identity", isotope),
        tuple(HeldLabel("registered-reaction-path-role", role) for role in ("entry", "boundary", "event", "product")),
        HeldLabel("held-isotope-reaction-condition", "condition-a"),
        ExactPositiveEventRate.from_counts(PositiveCount(events), PositiveCount(parts)),
        HeldLabel("held-isotope-rate-status", pair_label),
    )


def _pair(label: str, first_events: int, second_events: int) -> CompleteIsotopologueRatePair:
    return CompleteIsotopologueRatePair(
        HeldLabel("registered-ordered-isotopologue-pair", label),
        _path("light-held-label", first_events, 5, label),
        _path("heavy-held-label", second_events, 5, label),
    )


_BASE_PAIR = _pair("pair-a", 3, 2)
_BASE_FAMILY = CompleteKineticIsotopeFamily((RegisteredIsotopologuePairOccurrence(PositiveCount(1), _BASE_PAIR),))
OPERATIONAL_WITNESSES = (
    ("held-identities", "Two distinct isotope identities remain held on one otherwise identical path.", _BASE_PAIR.numerator_path.isotopologue_identity != _BASE_PAIR.denominator_path.isotopologue_identity),
    ("exact-rate-ratio", "Two independently counted positive event rates force one exact positive quotient.", forced_kinetic_isotope_effect_relation(_BASE_PAIR).exact_rate_ratio == Fraction(3, 2)),
    ("held-orientation", "Ratio direction is retained without a signed proof scalar.", forced_kinetic_isotope_effect_relation(_BASE_PAIR).ratio_orientation.label == "numerator-rate-greater"),
    ("successor", "Appending the next complete pair preserves every prior result.", append_isotopologue_pair_preserves_complete_family(_BASE_FAMILY, RegisteredIsotopologuePairOccurrence(PositiveCount(2), _pair("pair-b", 2, 3)))),
)


__all__ = (
    "CompleteIsotopologueRatePair", "CompleteKineticIsotopeFamily", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT",
    "ExactKineticIsotopeEffectRelation", "ExactPositiveEventRate", "OPERATIONAL_WITNESSES",
    "RegisteredIsotopologuePairOccurrence", "RetainedIsotopologuePath",
    "append_isotopologue_pair_preserves_complete_family", "forced_kinetic_isotope_effect_relation",
)
