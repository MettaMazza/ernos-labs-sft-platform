"""Fold-native kinetic isotope-fractionation law (NUCHEM-008)."""
from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class KineticIsotopeInterval:
    reaction: HeldLabel
    light_isotope: HeldLabel
    heavy_isotope: HeldLabel
    rank: PositiveCount
    light_initial: PositiveCount
    heavy_initial: PositiveCount
    light_product: PositiveCount
    heavy_product: PositiveCount
    resource_intervals: PositiveCount

    def __post_init__(self):
        if (self.reaction.family, self.light_isotope.family, self.heavy_isotope.family) != ("reaction-path", "isotope", "isotope"):
            raise InadmissibleExactValue("complete kinetic isotope interval required")
        if self.light_isotope == self.heavy_isotope or self.light_product.value > self.light_initial.value or self.heavy_product.value > self.heavy_initial.value:
            raise InadmissibleExactValue("bounded distinct isotope path required")

    @property
    def light_rate(self) -> Fraction:
        return Fraction(self.light_product.value, self.resource_intervals.value)

    @property
    def heavy_rate(self) -> Fraction:
        return Fraction(self.heavy_product.value, self.resource_intervals.value)

    @property
    def factor(self) -> PositiveRatio:
        return PositiveRatio.from_pair(self.light_product.value, self.heavy_product.value)

    @property
    def orientation(self):
        if self.light_product.value == self.heavy_product.value:
            return EMPTY_ONE
        return HeldLabel("kinetic-isotope-orientation", "light-faster" if self.light_product.value > self.heavy_product.value else "heavy-faster")

    @property
    def remaining(self):
        light = self.light_initial.value - self.light_product.value
        heavy = self.heavy_initial.value - self.heavy_product.value
        return (EMPTY_ONE if light == 0 else PositiveCount(light), EMPTY_ONE if heavy == 0 else PositiveCount(heavy))


def time_series(rows: tuple[KineticIsotopeInterval, ...]):
    if not rows or tuple(row.rank.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("complete ordered kinetic series required")
    if len({(row.reaction, row.light_isotope, row.heavy_isotope) for row in rows}) != 1:
        raise InadmissibleExactValue("one complete reaction/isotope path required")
    return tuple((row.light_rate, row.heavy_rate, row.factor.fraction, row.orientation) for row in rows)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-CHEM-ELEM-ISOTOPE-001",
    "SFT-CHEM-KIN-RATE-001",
    "SFT-CHEM-ACTIVITY-AMOUNT-TIME-003",
    "SFT-CHEM-ISOTOPE-EXCHANGE-006",
    "SFT-CHEM-EQUILIBRIUM-ISOTOPE-FRACTIONATION-007",
)
DIMENSIONS = (
    dimension("identity", "mass-only-rate", "Rate needs reaction and isotope identity.", "held-reaction-light-heavy-identities", "The complete path and both isotopes remain held."),
    dimension("support", "continuous-time-premise", "Continuum time is not proof support.", "positive-ordered-resource-intervals", "Every interval is positive and ordered."),
    dimension("events", "expected-product-yield", "Expectation is not event custody.", "positive-counted-isotope-products", "Both isotope product events are counted."),
    dimension("rates", "fitted-rate-constants", "Fitted constants cannot define the native rates.", "exact-products-per-resource-rates", "Both rates are exact count/resource ratios."),
    dimension("factor", "imported-kinetic-isotope-effect", "No imported factor is admissible.", "exact-light-heavy-rate-ratio", "The factor is forced by counted rates."),
    dimension("orientation", "signed-rate-difference", "A signed difference imports negative values.", "held-faster-class-or-EmptyOne", "The faster class is held; equality closes structurally."),
    dimension("inventory", "negative-depleted-reactant", "Depletion cannot produce a negative proof value.", "positive-Take-or-EmptyOne-remainder", "Each remainder is positive or structurally absent."),
    dimension("extension", "Rayleigh-continuum-premise", "A continuum law is not required.", "finite-time-series-successor-recomputes", "Each successor retains the path and recomputes exact rates."),
)
EXACT_RESULT = "held-reaction-light-heavy-identities__positive-ordered-resource-intervals__positive-counted-isotope-products__exact-products-per-resource-rates__exact-light-heavy-rate-ratio__held-faster-class-or-EmptyOne__positive-Take-or-EmptyOne-remainder__finite-time-series-successor-recomputes"


def _row(rank, lp, hp):
    return KineticIsotopeInterval(HeldLabel("reaction-path", "electrolysis"), HeldLabel("isotope", "light"), HeldLabel("isotope", "heavy"), PositiveCount(rank), PositiveCount(8), PositiveCount(8), PositiveCount(lp), PositiveCount(hp), PositiveCount(2))


_rows = (_row(1, 4, 2), _row(2, 6, 3))
OPERATIONAL_WITNESSES = (
    ("identity", "Reaction and isotopes held.", _rows[0].reaction.label == "electrolysis" and _rows[0].light_isotope != _rows[0].heavy_isotope),
    ("support", "Ranks complete.", tuple(x.rank.value for x in _rows) == (1, 2)),
    ("events", "Products counted.", _rows[0].light_product.value == 4 and _rows[0].heavy_product.value == 2),
    ("rates", "Rates exact.", _rows[0].light_rate == 2 and _rows[0].heavy_rate == 1),
    ("factor", "Factor exact.", _rows[0].factor.fraction == 2),
    ("orientation", "Faster class held.", _rows[0].orientation.label == "light-faster"),
    ("inventory", "Remainders positive or absent.", _rows[0].remaining[0].value == 4 and _row(1, 8, 8).remaining == (EMPTY_ONE, EMPTY_ONE)),
    ("successor", "Series recomputes.", time_series(_rows)[1][2] == 2),
)
