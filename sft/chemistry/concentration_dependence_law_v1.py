"""Fold-native exact concentration-dependence relation for KIN-002."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ConcentrationRateRow:
    reactant_identity: HeldLabel
    condition_identity: HeldLabel
    concentration_support: PositiveRatio
    transition_rate_support: PositiveRatio
    source_row: PositiveCount
    uncertainty_support: tuple[PositiveRatio | EmptyOne, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reactant_identity, HeldLabel) or self.reactant_identity.family != "registered-reactant":
            raise InadmissibleExactValue("concentration relation requires one registered reactant")
        if not isinstance(self.condition_identity, HeldLabel) or self.condition_identity.family != "complete-condition":
            raise InadmissibleExactValue("concentration relation requires a complete condition identity")
        if not isinstance(self.concentration_support, PositiveRatio) or not isinstance(self.transition_rate_support, PositiveRatio):
            raise InadmissibleExactValue("concentration and rate require exact positive support")
        if not isinstance(self.source_row, PositiveCount):
            raise InadmissibleExactValue("concentration relation requires a positive source-row identity")
        if not self.uncertainty_support or any(not isinstance(row, (PositiveRatio, EmptyOne)) for row in self.uncertainty_support):
            raise InadmissibleExactValue("concentration relation requires complete uncertainty provenance")


@dataclass(frozen=True)
class ExactConcentrationDependence:
    carrier: HeldLabel
    ordered_rows: tuple[tuple[PositiveRatio, PositiveRatio, HeldLabel, PositiveCount], ...]


def forced_concentration_dependence(rows: tuple[ConcentrationRateRow, ...]) -> ExactConcentrationDependence:
    if not rows or any(not isinstance(row, ConcentrationRateRow) for row in rows):
        raise InadmissibleExactValue("concentration dependence requires a complete positive row census")
    if len({row.source_row.value for row in rows}) != len(rows):
        raise InadmissibleExactValue("concentration dependence contains duplicate source rows")
    reactants = {row.reactant_identity for row in rows}
    if len(reactants) != 1:
        raise InadmissibleExactValue("one concentration relation cannot collapse distinct reactants")
    ordered = tuple(sorted(rows, key=lambda row: row.source_row.value))
    return ExactConcentrationDependence(
        HeldLabel("concentration-dependence-carrier", next(iter(reactants)).label),
        tuple((row.concentration_support, row.transition_rate_support, row.condition_identity, row.source_row) for row in ordered),
    )


def external_positive_magnitude(inscription: str) -> PositiveRatio:
    if not isinstance(inscription, str) or not inscription.strip() or inscription.strip().startswith("-"):
        raise InadmissibleExactValue("concentration/rate inscription requires exact positive support")
    try:
        value = Fraction(inscription.strip().lstrip("+"))
        return PositiveRatio.from_pair(value.numerator, value.denominator)
    except Exception as exc:
        raise InadmissibleExactValue("concentration/rate inscription is not exact positive finite support") from exc


def complete_row_append_preserves_relation(rows: tuple[ConcentrationRateRow, ...], successor: ConcentrationRateRow) -> bool:
    prior = forced_concentration_dependence(rows)
    extended = forced_concentration_dependence(rows + (successor,))
    return extended.carrier == prior.carrier and extended.ordered_rows[: len(prior.ordered_rows)] == prior.ordered_rows


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001", "SFT-MATH-PROBABILITY-STATISTICS-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-RXN-MECHANISM-001", "SFT-CHEM-KIN-RATE-001", "SFT-CHEM-KIN-ORDER-001",
    "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("reactant", "anonymous-or-changing-reactant", "Rows for different reactants cannot define one dependence relation.", "one-held-registered-reactant-identity", "Every row retains the same registered reactant identity."),
    dimension("intervention", "concentration-erased-or-continuum-variable", "Erasing the intervention coordinate destroys the tested dependence.", "exact-positive-concentration-support-per-row", "Each source row carries its exact positive concentration support."),
    dimension("response", "answer-only-rate-or-unregistered-change", "A detached response cannot be traced to a transition.", "exact-positive-elementary-rate-response-per-row", "Each response is an exact positive post-seal rate support."),
    dimension("condition", "temperature-method-or-uncertainty-collapsed", "Condition collapse can manufacture a dependency.", "complete-held-condition-method-and-uncertainty-record", "Every temperature, method and uncertainty remains source-bound."),
    dimension("completeness", "selected-favorable-rows-or-averaged-answer", "Selection or averaging erases adverse and distinct responses.", "complete-source-ordered-row-census", "Every registered row is retained in source order."),
    dimension("relation", "imported-mass-action-power-order-fit-or-logarithm", "An imported exponent or fit could choose the relation.", "exact-condition-bound-concentration-rate-table", "The complete exact table is the relation; no exponent is fitted."),
    dimension("prediction", "species-condition-density-rate-or-value-readable-before-seal", "Readable targets could select the law.", "complete-value-free-9-row-identity-seal", "All nine source-row identities seal before values open."),
    dimension("extension", "refit-after-complete-row-append", "Refitting would alter prior evidence.", "depth-independent-complete-row-append-with-prior-trace-preserved", "Appending one complete row preserves every earlier pair and record."),
)


EXACT_RESULT = (
    "one-held-registered-reactant-identity__exact-positive-concentration-support-per-row__"
    "exact-positive-elementary-rate-response-per-row__complete-held-condition-method-and-uncertainty-record__"
    "complete-source-ordered-row-census__exact-condition-bound-concentration-rate-table__"
    "complete-value-free-9-row-identity-seal__depth-independent-complete-row-append-with-prior-trace-preserved"
)


def _row(number: int, concentration: int, rate: int) -> ConcentrationRateRow:
    return ConcentrationRateRow(
        HeldLabel("registered-reactant", "OH-plus-DME"), HeldLabel("complete-condition", f"condition-{number}"),
        PositiveRatio.from_pair(concentration, 1), PositiveRatio.from_pair(rate, 1), PositiveCount(number),
        (PositiveRatio.from_pair(1, 2), EmptyOne()),
    )


OPERATIONAL_WITNESSES = (
    ("source-order", "The complete relation retains source order rather than sorting by outcome.", tuple(row[3].value for row in forced_concentration_dependence((_row(1, 3, 5), _row(2, 7, 4))).ordered_rows) == (1, 2)),
    ("adverse-response-retention", "A lower later response remains retained rather than selected away.", forced_concentration_dependence((_row(1, 3, 5), _row(2, 7, 4))).ordered_rows[1][1].fraction == Fraction(4, 1)),
    ("structural-absence", "An absent uncertainty coordinate is structural EmptyOne.", isinstance(_row(1, 3, 5).uncertainty_support[1], EmptyOne)),
    ("append-successor", "Complete row append preserves the entire prior trace.", complete_row_append_preserves_relation((_row(1, 3, 5),), _row(2, 7, 4))),
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "ConcentrationRateRow",
    "ExactConcentrationDependence", "complete_row_append_preserves_relation", "external_positive_magnitude",
    "forced_concentration_dependence",
)
