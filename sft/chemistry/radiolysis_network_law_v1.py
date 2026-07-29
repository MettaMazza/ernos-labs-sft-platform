"""Fold-native radiation-chemistry reaction-network law (NUCHEM-012)."""
from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class RadiolysisChannel:
    medium: HeldLabel
    reactant: HeldLabel
    product: HeldLabel
    channel: HeldLabel
    product_events: PositiveCount
    deposited_resource: PositiveCount

    def __post_init__(self):
        if (self.medium.family, self.reactant.family, self.product.family, self.channel.family) != ("radiolysis-medium", "chemical-species", "chemical-species", "reaction-channel"):
            raise InadmissibleExactValue("complete radiolysis channel required")
        if self.reactant == self.product:
            raise InadmissibleExactValue("reactant and product must be distinct")

    @property
    def yield_ratio(self) -> Fraction:
        return Fraction(self.product_events.value, self.deposited_resource.value)


def radiolysis_network(rows: tuple[RadiolysisChannel, ...]):
    if not rows: return EMPTY_ONE
    if len({row.medium for row in rows}) != 1 or len({row.channel for row in rows}) != len(rows):
        raise InadmissibleExactValue("one medium and distinct complete channels required")
    total = sum(row.product_events.value for row in rows)
    return tuple((row.reactant, row.product, row.channel, row.yield_ratio, Fraction(row.product_events.value, total)) for row in rows)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001", "SFT-PHYS-MATTER-MASS-ENERGY-001", "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002", "SFT-CHEM-ACTIVITY-AMOUNT-TIME-003",
)
DIMENSIONS = (
    dimension("handoff", "chemistry-defines-deposited-energy", "Deposited resource belongs to Physics.", "explicit-positive-deposited-resource-handoff", "Chemistry receives a positive counted resource."),
    dimension("identity", "anonymous-radical-yield", "A yield needs medium and species identity.", "held-medium-reactant-product-identities", "All identities remain held."),
    dimension("network", "single-net-equation", "A net equation hides channels and intermediates.", "complete-directed-reaction-network", "Every directed channel remains."),
    dimension("events", "continuum-concentration-premise", "Continuum concentration hides occurrences.", "positive-product-event-counts", "Every product event is counted."),
    dimension("yield", "fitted-G-value", "A fitted value cannot define native yield.", "exact-product-per-deposited-resource-ratio", "Yield is forced by exact counts."),
    dimension("partition", "selected-major-products", "Major-product selection erases support.", "exact-complete-channel-partition-of-One", "All channels partition One."),
    dimension("closure", "negative-consumption-ledger", "Consumption cannot be a negative proof value.", "explicit-reaction-or-EmptyOne-termination", "Each path reacts explicitly or terminates structurally."),
    dimension("extension", "differential-kinetic-model-premise", "A continuum kinetic model is not required.", "successor-retains-and-recomputes-complete-network", "Every successor retains all channels and recomputes."),
)
EXACT_RESULT = "explicit-positive-deposited-resource-handoff__held-medium-reactant-product-identities__complete-directed-reaction-network__positive-product-event-counts__exact-product-per-deposited-resource-ratio__exact-complete-channel-partition-of-One__explicit-reaction-or-EmptyOne-termination__successor-retains-and-recomputes-complete-network"


def _row(reactant, product, channel, events):
    return RadiolysisChannel(HeldLabel("radiolysis-medium", "water"), HeldLabel("chemical-species", reactant), HeldLabel("chemical-species", product), HeldLabel("reaction-channel", channel), PositiveCount(events), PositiveCount(10))


_rows = (_row("water", "hydroxyl", "ionization", 3), _row("water", "hydrogen", "dissociation", 2))
OPERATIONAL_WITNESSES = (
    ("handoff", "Deposited resource positive.", _rows[0].deposited_resource.value == 10),
    ("identity", "Medium/species held.", _rows[0].medium.label == "water" and _rows[0].reactant != _rows[0].product),
    ("network", "Channels distinct.", len({row.channel for row in _rows}) == 2),
    ("events", "Products counted.", tuple(row.product_events.value for row in _rows) == (3, 2)),
    ("yield", "Yield exact.", _rows[0].yield_ratio == Fraction(3, 10)),
    ("partition", "Products partition One.", sum(row[-1] for row in radiolysis_network(_rows)) == 1),
    ("closure", "Empty network closes structurally.", radiolysis_network(()) == EMPTY_ONE),
    ("extension", "Successor retains network.", len(radiolysis_network(_rows + (_row("water", "peroxide", "recombination", 1),))) == 3),
)
