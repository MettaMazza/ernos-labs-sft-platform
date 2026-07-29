"""Fold-native isotope-exchange reaction law (NUCHEM-006)."""
from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class IsotopeExchangeState:
    element: HeldLabel
    light_isotope: HeldLabel
    heavy_isotope: HeldLabel
    carrier_a: HeldLabel
    carrier_b: HeldLabel
    light_a: PositiveCount
    heavy_a: PositiveCount
    light_b: PositiveCount
    heavy_b: PositiveCount

    def __post_init__(self):
        if (self.element.family, self.light_isotope.family, self.heavy_isotope.family, self.carrier_a.family, self.carrier_b.family) != ("element", "isotope", "isotope", "chemical-carrier", "chemical-carrier"):
            raise InadmissibleExactValue("complete isotope-exchange state required")
        if self.light_isotope == self.heavy_isotope or self.carrier_a == self.carrier_b:
            raise InadmissibleExactValue("distinct isotopes and carriers required")

    @property
    def quotient(self) -> Fraction:
        return Fraction(self.heavy_b.value * self.light_a.value, self.light_b.value * self.heavy_a.value)


def exchange_transition(before: IsotopeExchangeState, after: IsotopeExchangeState):
    identities = (before.element, before.light_isotope, before.heavy_isotope, before.carrier_a, before.carrier_b)
    if identities != (after.element, after.light_isotope, after.heavy_isotope, after.carrier_a, after.carrier_b):
        raise InadmissibleExactValue("exchange identities changed")
    conserved = (
        before.light_a.value + before.light_b.value == after.light_a.value + after.light_b.value,
        before.heavy_a.value + before.heavy_b.value == after.heavy_a.value + after.heavy_b.value,
        before.light_a.value + before.heavy_a.value == after.light_a.value + after.heavy_a.value,
        before.light_b.value + before.heavy_b.value == after.light_b.value + after.heavy_b.value,
    )
    if not all(conserved):
        raise InadmissibleExactValue("isotope or carrier total not conserved")
    if before == after:
        return EMPTY_ONE
    return HeldLabel("exchange-orientation", "heavy-A-to-B" if after.heavy_b.value > before.heavy_b.value else "heavy-B-to-A")


def event_balance(forward: PositiveCount, reverse: PositiveCount):
    if forward.value == reverse.value:
        return EMPTY_ONE
    if forward.value > reverse.value:
        return HeldLabel("exchange-event-balance", "forward-excess"), PositiveCount(forward.value - reverse.value)
    return HeldLabel("exchange-event-balance", "reverse-excess"), PositiveCount(reverse.value - forward.value)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-CHEM-ELEM-ISOTOPE-001",
    "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-EQ-CHEMICAL-001",
    "SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001",
    "SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002",
)
DIMENSIONS = (
    dimension("identity", "mass-number-only", "Mass number alone loses elemental and isotope identity.", "held-element-light-heavy-isotopes", "Element and both isotopes remain held."),
    dimension("carriers", "phase-free-exchange", "Exchange requires two chemical carriers.", "held-distinct-chemical-carriers", "Both carriers remain held."),
    dimension("inventory", "continuum-concentration-premise", "Continuum concentration hides occurrences.", "positive-complete-four-count-inventory", "Every light/heavy carrier occurrence is counted."),
    dimension("conservation", "isotope-label-overwrite", "Overwriting destroys custody.", "exact-isotope-and-carrier-conservation", "Both isotope totals and carrier totals are invariant."),
    dimension("direction", "signed-exchange-extent", "A signed scalar imports negative values.", "held-direction-positive-Take", "Direction is held and excess is positive."),
    dimension("quotient", "fitted-exchange-constant", "A fit cannot define exchange.", "exact-cross-product-exchange-quotient", "The quotient is forced by four exact counts."),
    dimension("equilibrium", "numerical-zero-net", "Numerical zero is not native balance.", "equal-forward-reverse-closes-EmptyOne", "Equal counted directions close structurally."),
    dimension("extension", "lookup-fractionation-factor", "A lookup cannot select a transition.", "successor-preserves-identities-and-totals", "Every successor preserves complete custody."),
)
EXACT_RESULT = "held-element-light-heavy-isotopes__held-distinct-chemical-carriers__positive-complete-four-count-inventory__exact-isotope-and-carrier-conservation__held-direction-positive-Take__exact-cross-product-exchange-quotient__equal-forward-reverse-closes-EmptyOne__successor-preserves-identities-and-totals"


def _state(la, ha, lb, hb):
    return IsotopeExchangeState(HeldLabel("element", "oxygen"), HeldLabel("isotope", "light"), HeldLabel("isotope", "heavy"), HeldLabel("chemical-carrier", "A"), HeldLabel("chemical-carrier", "B"), PositiveCount(la), PositiveCount(ha), PositiveCount(lb), PositiveCount(hb))


_before, _after = _state(4, 2, 3, 1), _state(5, 1, 2, 2)
OPERATIONAL_WITNESSES = (
    ("identity", "Isotopes held.", _before.light_isotope != _before.heavy_isotope),
    ("carriers", "Carriers held.", _before.carrier_a != _before.carrier_b),
    ("inventory", "Four positive counts retained.", min(_before.light_a.value, _before.heavy_a.value, _before.light_b.value, _before.heavy_b.value) > 0),
    ("conservation", "Exchange conserves totals.", exchange_transition(_before, _after).label == "heavy-A-to-B"),
    ("direction", "Event excess held.", event_balance(PositiveCount(3), PositiveCount(1))[0].label == "forward-excess"),
    ("quotient", "Quotient exact.", _before.quotient == Fraction(2, 3)),
    ("equilibrium", "Balanced events close.", event_balance(PositiveCount(2), PositiveCount(2)) == EMPTY_ONE),
    ("successor", "Return successor preserves totals.", exchange_transition(_after, _before).label == "heavy-B-to-A"),
)
