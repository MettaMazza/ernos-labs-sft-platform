"""Fold-native exact temperature-dependence relation for KIN-003."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class TemperatureRateRow:
    reaction_identity: HeldLabel
    condition_identity: HeldLabel
    temperature_support: PositiveRatio
    transition_rate_support: PositiveRatio
    source_condition_row: PositiveCount
    source_target_row: PositiveCount
    uncertainty_support: tuple[PositiveRatio | EmptyOne, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "registered-reaction":
            raise InadmissibleExactValue("temperature relation requires a registered reaction identity")
        if not isinstance(self.condition_identity, HeldLabel) or self.condition_identity.family != "complete-condition":
            raise InadmissibleExactValue("temperature relation requires a complete condition identity")
        if not isinstance(self.temperature_support, PositiveRatio) or not isinstance(self.transition_rate_support, PositiveRatio):
            raise InadmissibleExactValue("temperature and rate require exact positive support")
        if not isinstance(self.source_condition_row, PositiveCount) or not isinstance(self.source_target_row, PositiveCount):
            raise InadmissibleExactValue("temperature relation requires positive source-row identities")
        if not self.uncertainty_support or any(not isinstance(row, (PositiveRatio, EmptyOne)) for row in self.uncertainty_support):
            raise InadmissibleExactValue("temperature relation requires complete uncertainty provenance")


@dataclass(frozen=True)
class ExactTemperatureDependence:
    carrier: HeldLabel
    ordered_rows: tuple[tuple[HeldLabel, PositiveRatio, PositiveRatio, HeldLabel, PositiveCount, PositiveCount], ...]


def forced_temperature_dependence(rows: tuple[TemperatureRateRow, ...]) -> ExactTemperatureDependence:
    if not rows or any(not isinstance(row, TemperatureRateRow) for row in rows):
        raise InadmissibleExactValue("temperature dependence requires a complete positive row census")
    target_rows = tuple(row.source_target_row.value for row in rows)
    if len(set(target_rows)) != len(target_rows):
        raise InadmissibleExactValue("temperature dependence contains duplicate source target rows")
    ordered = tuple(sorted(rows, key=lambda row: row.source_target_row.value))
    return ExactTemperatureDependence(
        HeldLabel("temperature-dependence-carrier", "complete-registered-reaction-census"),
        tuple(
            (
                row.reaction_identity,
                row.temperature_support,
                row.transition_rate_support,
                row.condition_identity,
                row.source_condition_row,
                row.source_target_row,
            )
            for row in ordered
        ),
    )


def external_positive_magnitude(inscription: str) -> PositiveRatio:
    if not isinstance(inscription, str) or not inscription.strip() or inscription.strip().startswith("-"):
        raise InadmissibleExactValue("temperature/rate inscription requires exact positive support")
    try:
        value = Fraction(inscription.strip().lstrip("+"))
        return PositiveRatio.from_pair(value.numerator, value.denominator)
    except Exception as exc:
        raise InadmissibleExactValue("temperature/rate inscription is not exact positive finite support") from exc


def complete_row_append_preserves_relation(rows: tuple[TemperatureRateRow, ...], successor: TemperatureRateRow) -> bool:
    prior = forced_temperature_dependence(rows)
    extended = forced_temperature_dependence(rows + (successor,))
    return extended.carrier == prior.carrier and extended.ordered_rows[: len(prior.ordered_rows)] == prior.ordered_rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001", "SFT-MATH-PROBABILITY-STATISTICS-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-KIN-RATE-001", "SFT-CHEM-KIN-ORDER-001", "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    "SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002", "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007", "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001",
    "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("reaction", "anonymous-collapsed-or-changing-reaction", "Collapsing reaction identity can manufacture one temperature relation from distinct processes.", "held-registered-reaction-identity-per-row", "Every row retains its registered reaction identity."),
    dimension("temperature", "temperature-erased-signed-or-continuum-variable", "Erasing the intervention coordinate destroys the tested dependence.", "exact-positive-temperature-support-per-row", "Every source row carries exact positive temperature support."),
    dimension("response", "answer-only-rate-or-unregistered-change", "A detached response cannot be traced to a chemical transition.", "exact-positive-elementary-rate-response-per-row", "Each response is an exact positive post-seal elementary-rate support."),
    dimension("condition", "density-bath-method-or-uncertainty-collapsed", "Condition collapse can manufacture an apparent temperature effect.", "complete-held-density-bath-method-and-uncertainty-record", "Every density, bath gas, method and uncertainty remains source-bound."),
    dimension("completeness", "selected-favorable-rows-reaction-or-averaged-answer", "Selection or averaging erases repeated, absent and adverse observations.", "complete-two-reaction-source-ordered-row-census", "Every measured row for both registered reactions is retained in source order."),
    dimension("relation", "imported-arrhenius-exponential-logarithm-prefactor-or-activation-fit", "An imported form or fitted value could choose the answer.", "exact-condition-bound-temperature-rate-table", "The complete exact table is the relation; no fitted functional form enters."),
    dimension("prediction", "temperature-density-rate-or-target-value-readable-before-seal", "Readable targets could select the law.", "complete-value-free-19-target-identity-seal", "All nineteen measured target identities seal before values open."),
    dimension("extension", "refit-after-complete-row-append", "Refitting would alter prior evidence.", "depth-independent-complete-row-append-with-prior-trace-preserved", "Appending one complete target row preserves every earlier reaction/temperature/rate record."),
)


EXACT_RESULT = (
    "held-registered-reaction-identity-per-row__exact-positive-temperature-support-per-row__"
    "exact-positive-elementary-rate-response-per-row__complete-held-density-bath-method-and-uncertainty-record__"
    "complete-two-reaction-source-ordered-row-census__exact-condition-bound-temperature-rate-table__"
    "complete-value-free-19-target-identity-seal__depth-independent-complete-row-append-with-prior-trace-preserved"
)


def _row(target: int, condition: int, reaction: str, temperature: int, rate: int) -> TemperatureRateRow:
    return TemperatureRateRow(
        HeldLabel("registered-reaction", reaction), HeldLabel("complete-condition", f"condition-{condition}"),
        PositiveRatio.from_pair(temperature, 1), PositiveRatio.from_pair(rate, 1),
        PositiveCount(condition), PositiveCount(target), (PositiveRatio.from_pair(1, 2), EmptyOne()),
    )


OPERATIONAL_WITNESSES = (
    ("source-order", "The complete relation retains source-target order rather than sorting by temperature or outcome.", tuple(row[5].value for row in forced_temperature_dependence((_row(1, 1, "r-a", 3, 5), _row(2, 2, "r-a", 7, 4))).ordered_rows) == (1, 2)),
    ("adverse-nonmonotone-retention", "A later higher-temperature, lower-rate response remains retained.", forced_temperature_dependence((_row(1, 1, "r-a", 3, 5), _row(2, 2, "r-a", 7, 4))).ordered_rows[1][2].fraction == Fraction(4, 1)),
    ("reaction-separation", "Distinct registered reactions remain explicit within one complete source table.", len({row[0].label for row in forced_temperature_dependence((_row(1, 1, "r-a", 3, 5), _row(2, 1, "r-b", 3, 7))).ordered_rows}) == 2),
    ("append-successor", "Complete target-row append preserves the entire prior trace.", complete_row_append_preserves_relation((_row(1, 1, "r-a", 3, 5),), _row(2, 2, "r-a", 7, 4))),
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "ExactTemperatureDependence",
    "TemperatureRateRow", "complete_row_append_preserves_relation", "external_positive_magnitude",
    "forced_temperature_dependence",
)
