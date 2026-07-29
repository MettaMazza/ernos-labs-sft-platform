"""Fold-native radiochemical separation and decontamination law (NUCHEM-010)."""
from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class SeparationLedger:
    target: HeldLabel
    contaminant: HeldLabel
    feed_target: PositiveCount
    feed_contaminant: PositiveCount
    product_target: PositiveCount
    product_contaminant: PositiveCount
    waste_target: PositiveCount
    waste_contaminant: PositiveCount

    def __post_init__(self):
        if (self.target.family, self.contaminant.family) != ("target-species", "contaminant-species") or self.target.label == self.contaminant.label:
            raise InadmissibleExactValue("distinct target and contaminant identities required")
        if self.feed_target.value != self.product_target.value + self.waste_target.value or self.feed_contaminant.value != self.product_contaminant.value + self.waste_contaminant.value:
            raise InadmissibleExactValue("complete target and contaminant balance required")

    @property
    def recovery(self) -> Fraction:
        return Fraction(self.product_target.value, self.feed_target.value)

    @property
    def decontamination_factor(self) -> Fraction:
        return Fraction(self.feed_contaminant.value * self.product_target.value, self.feed_target.value * self.product_contaminant.value)

    @property
    def complete_recovery(self):
        return residual_custody(self.feed_target, self.product_target)


def residual_custody(feed: PositiveCount, product: PositiveCount):
    if product.value > feed.value:
        raise InadmissibleExactValue("product cannot exceed feed")
    return EMPTY_ONE if product.value == feed.value else PositiveCount(feed.value - product.value)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001",
    "SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002", "SFT-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009",
)
DIMENSIONS = (
    dimension("identity", "total-radioactivity-only", "Total activity loses target and contaminant identity.", "held-target-and-contaminant-species", "Both species remain held."),
    dimension("streams", "product-only-record", "A product alone hides feed and waste.", "complete-feed-product-waste-streams", "All streams remain."),
    dimension("inventory", "continuum-concentration-premise", "Continuum concentration hides occurrences.", "positive-species-resolved-counts", "Every stream/species count is positive."),
    dimension("balance", "unrecorded-process-loss", "Unrecorded loss breaks custody.", "exact-target-and-contaminant-conservation", "Both species balance exactly."),
    dimension("recovery", "percent-recovery-premise", "A displayed percentage cannot define recovery.", "exact-product-target-per-feed-target-ratio", "Recovery is forced by exact counts."),
    dimension("decontamination", "fitted-separation-factor", "A fit cannot define decontamination.", "exact-contaminant-fraction-ratio", "The factor is forced by cross-products."),
    dimension("absence", "numerical-zero-contaminant", "Numerical zero is not native absence.", "positive-Take-or-EmptyOne-residual", "Residual custody is positive or structurally absent."),
    dimension("extension", "selected-best-stage", "Selecting a best stage erases the process.", "successor-composes-balanced-stages", "Every stage composes only through balanced streams."),
)
EXACT_RESULT = "held-target-and-contaminant-species__complete-feed-product-waste-streams__positive-species-resolved-counts__exact-target-and-contaminant-conservation__exact-product-target-per-feed-target-ratio__exact-contaminant-fraction-ratio__positive-Take-or-EmptyOne-residual__successor-composes-balanced-stages"


_ledger = SeparationLedger(HeldLabel("target-species", "Sc"), HeldLabel("contaminant-species", "V"), PositiveCount(10), PositiveCount(12), PositiveCount(8), PositiveCount(2), PositiveCount(2), PositiveCount(10))
OPERATIONAL_WITNESSES = (
    ("identity", "Species distinct.", _ledger.target != _ledger.contaminant),
    ("streams", "Feed/product/waste complete.", len((_ledger.feed_target, _ledger.product_target, _ledger.waste_target)) == 3),
    ("inventory", "Counts positive.", min(_ledger.feed_target.value, _ledger.feed_contaminant.value, _ledger.product_target.value, _ledger.product_contaminant.value, _ledger.waste_target.value, _ledger.waste_contaminant.value) > 0),
    ("balance", "Both species balance.", _ledger.feed_target.value == 10 and _ledger.feed_contaminant.value == 12),
    ("recovery", "Recovery exact.", _ledger.recovery == Fraction(4, 5)),
    ("decontamination", "Factor exact.", _ledger.decontamination_factor == Fraction(24, 5)),
    ("absence", "Complete recovery closes structurally.", residual_custody(PositiveCount(10), PositiveCount(10)) == EMPTY_ONE and _ledger.complete_recovery.value == 2),
    ("extension", "Balanced successor reconstructs.", _ledger.product_target.value + _ledger.waste_target.value == _ledger.feed_target.value),
)
