"""Fold-native equilibrium isotope-fractionation law (NUCHEM-007)."""
from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class EquilibriumIsotopePartition:
    light_isotope: HeldLabel
    heavy_isotope: HeldLabel
    phase_a: HeldLabel
    phase_b: HeldLabel
    light_a: PositiveCount
    heavy_a: PositiveCount
    light_b: PositiveCount
    heavy_b: PositiveCount

    def __post_init__(self):
        if (self.light_isotope.family, self.heavy_isotope.family, self.phase_a.family, self.phase_b.family) != ("isotope", "isotope", "chemical-phase", "chemical-phase"):
            raise InadmissibleExactValue("complete equilibrium isotope partition required")
        if self.light_isotope == self.heavy_isotope or self.phase_a == self.phase_b:
            raise InadmissibleExactValue("distinct isotopes and phases required")

    @property
    def ratio_a(self) -> PositiveRatio:
        return PositiveRatio.from_pair(self.heavy_a.value, self.light_a.value)

    @property
    def ratio_b(self) -> PositiveRatio:
        return PositiveRatio.from_pair(self.heavy_b.value, self.light_b.value)

    @property
    def factor(self) -> PositiveRatio:
        return PositiveRatio.from_pair(self.heavy_a.value * self.light_b.value, self.light_a.value * self.heavy_b.value)

    @property
    def orientation(self):
        left = self.heavy_a.value * self.light_b.value
        right = self.light_a.value * self.heavy_b.value
        if left == right:
            return EMPTY_ONE
        return HeldLabel("fractionation-orientation", "phase-A-heavy-enriched" if left > right else "phase-B-heavy-enriched")


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-CHEM-ELEM-ISOTOPE-001",
    "SFT-CHEM-EQ-CHEMICAL-001",
    "SFT-CHEM-ISOTOPE-EXCHANGE-006",
)
DIMENSIONS = (
    dimension("identity", "anonymous-heavy-light", "Heavy/light labels need isotope identity.", "held-light-heavy-isotopes", "Both isotopes remain held."),
    dimension("phases", "single-phase-ratio", "Fractionation compares two carriers or phases.", "held-distinct-phase-pair", "Both phases remain held."),
    dimension("inventory", "continuum-abundance-premise", "Continuum abundance hides occurrences.", "positive-complete-isotope-counts", "All four isotope/phase counts remain."),
    dimension("ratios", "decimal-isotope-ratio", "A decimal is only a display form.", "exact-heavy-per-light-ratios", "Each phase ratio is exact."),
    dimension("factor", "fitted-fractionation-factor", "No fitted factor is admissible.", "exact-ratio-of-ratios", "The factor is forced by cross-products."),
    dimension("orientation", "signed-delta-premise", "A signed delta imports negative proof values.", "held-enrichment-or-EmptyOne-coincidence", "Enrichment is held; equality is structural absence."),
    dimension("equilibrium", "named-equilibrium-assumption", "A label cannot prove equilibrium.", "exchange-balance-plus-stable-factor", "Balanced exchange and invariant factor establish the class."),
    dimension("extension", "selected-isotope-pair", "One selected pair hides the complete system.", "complete-vector-successor-recomputes", "New rows preserve prior identities and recompute exactly."),
)
EXACT_RESULT = "held-light-heavy-isotopes__held-distinct-phase-pair__positive-complete-isotope-counts__exact-heavy-per-light-ratios__exact-ratio-of-ratios__held-enrichment-or-EmptyOne-coincidence__exchange-balance-plus-stable-factor__complete-vector-successor-recomputes"


def _partition(la=4, ha=2, lb=6, hb=1):
    return EquilibriumIsotopePartition(HeldLabel("isotope", "light"), HeldLabel("isotope", "heavy"), HeldLabel("chemical-phase", "A"), HeldLabel("chemical-phase", "B"), PositiveCount(la), PositiveCount(ha), PositiveCount(lb), PositiveCount(hb))


_p, _equal = _partition(), _partition(4, 2, 6, 3)
OPERATIONAL_WITNESSES = (
    ("identity", "Isotopes distinct.", _p.light_isotope != _p.heavy_isotope),
    ("phases", "Phases distinct.", _p.phase_a != _p.phase_b),
    ("inventory", "Counts positive.", min(_p.light_a.value, _p.heavy_a.value, _p.light_b.value, _p.heavy_b.value) > 0),
    ("ratios", "Phase ratios exact.", _p.ratio_a.fraction == Fraction(1, 2) and _p.ratio_b.fraction == Fraction(1, 6)),
    ("factor", "Factor forced exactly.", _p.factor.fraction == 3),
    ("orientation", "Enrichment held.", _p.orientation.label == "phase-A-heavy-enriched"),
    ("coincidence", "Equal ratios close.", _equal.orientation == EMPTY_ONE and _equal.factor.fraction == 1),
    ("extension", "Fresh vector recomputes.", _partition(6, 3, 8, 2).factor.fraction == 2),
)
