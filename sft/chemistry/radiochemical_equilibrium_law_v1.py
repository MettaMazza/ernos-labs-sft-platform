"""Fold-native transient and secular radiochemical equilibrium law (NUCHEM-005)."""
from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class ParentDaughterInterval:
    parent: HeldLabel
    daughter: HeldLabel
    rank: PositiveCount
    parent_transformations: PositiveCount
    daughter_transformations: PositiveCount
    resource_intervals: PositiveCount

    def __post_init__(self):
        if (self.parent.family, self.daughter.family) != ("parent-nuclide", "daughter-nuclide"):
            raise InadmissibleExactValue("held parent/daughter identities required")

    @property
    def parent_activity(self) -> Fraction:
        return Fraction(self.parent_transformations.value, self.resource_intervals.value)

    @property
    def daughter_activity(self) -> Fraction:
        return Fraction(self.daughter_transformations.value, self.resource_intervals.value)

    @property
    def daughter_parent_ratio(self) -> PositiveRatio:
        return PositiveRatio.from_pair(self.daughter_transformations.value, self.parent_transformations.value)


def equilibrium_regime(rows: tuple[ParentDaughterInterval, ...]):
    if not rows:
        return EMPTY_ONE
    if tuple(row.rank.value for row in rows) != tuple(range(1, len(rows) + 1)):
        raise InadmissibleExactValue("complete ordered interval support required")
    if len({(row.parent, row.daughter) for row in rows}) != 1:
        raise InadmissibleExactValue("one parent/daughter recurrence required")
    ratios = tuple(row.daughter_parent_ratio.fraction for row in rows)
    if len(set(ratios)) != 1:
        return EMPTY_ONE
    ratio = PositiveRatio.from_pair(ratios[0].numerator, ratios[0].denominator)
    if ratios[0] == 1:
        return HeldLabel("equilibrium-regime", "secular-One-ratio"), ratio
    return HeldLabel("equilibrium-regime", "transient-held-ratio"), ratio


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-CHEM-EQ-CHEMICAL-001",
    "SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002",
    "SFT-CHEM-ACTIVITY-AMOUNT-TIME-003",
    "SFT-CHEM-RADIOACTIVE-BRANCHING-CHEMICAL-YIELD-004",
)
DIMENSIONS = (
    dimension("identity", "anonymous-activity-pair", "Equilibrium needs parent/daughter identity.", "held-parent-daughter-identity", "Both identities remain held."),
    dimension("support", "continuous-time-premise", "Continuum time is not proof support.", "positive-ordered-resource-intervals", "Every interval is positive and ordered."),
    dimension("activity", "fitted-decay-curve", "A fitted curve cannot define activity.", "exact-counted-activity-pair", "Both activities are exact event/resource ratios."),
    dimension("relation", "signed-activity-difference", "A signed scalar imports negative values.", "held-ratio-or-structural-absence", "The exact positive ratio is held or recurrence is absent."),
    dimension("transient", "named-transient-assumption", "A name cannot establish a regime.", "persistent-nonOne-ratio-forces-transient", "A persistent exact non-One ratio forces the transient class."),
    dimension("secular", "approximate-equality-tolerance", "A tolerance is a free parameter.", "persistent-One-ratio-forces-secular", "A persistent exact One ratio forces the secular class."),
    dimension("record", "selected-timepoint", "One point cannot establish recurrence.", "complete-parent-daughter-time-vector", "Every registered interval remains."),
    dimension("extension", "differential-equation-premise", "No imported differential equation is needed.", "finite-successor-recomputes-regime", "Each successor recomputes the complete exact ratio vector."),
)
EXACT_RESULT = "held-parent-daughter-identity__positive-ordered-resource-intervals__exact-counted-activity-pair__held-ratio-or-structural-absence__persistent-nonOne-ratio-forces-transient__persistent-One-ratio-forces-secular__complete-parent-daughter-time-vector__finite-successor-recomputes-regime"


def _row(rank, parent, daughter):
    return ParentDaughterInterval(HeldLabel("parent-nuclide", "p"), HeldLabel("daughter-nuclide", "d"), PositiveCount(rank), PositiveCount(parent), PositiveCount(daughter), PositiveCount(2))


_transient = (_row(1, 2, 4), _row(2, 3, 6))
_secular = (_row(1, 2, 2), _row(2, 3, 3))
OPERATIONAL_WITNESSES = (
    ("identity", "Parent and daughter held.", _transient[0].parent.label == "p" and _transient[0].daughter.label == "d"),
    ("support", "Ranks are complete.", tuple(x.rank.value for x in _transient) == (1, 2)),
    ("activity", "Activities exact.", _transient[0].parent_activity == 1 and _transient[0].daughter_activity == 2),
    ("ratio", "Ratio positive and exact.", _transient[0].daughter_parent_ratio.fraction == 2),
    ("transient", "Persistent non-One ratio classified.", equilibrium_regime(_transient)[0].label == "transient-held-ratio"),
    ("secular", "Persistent One ratio classified.", equilibrium_regime(_secular)[0].label == "secular-One-ratio"),
    ("absence", "Changing ratio is structural absence.", equilibrium_regime((_row(1, 2, 4), _row(2, 3, 3))) == EMPTY_ONE),
    ("successor", "Successor preserves exact regime.", equilibrium_regime(_transient + (_row(3, 4, 8),))[1].fraction == 2),
)
