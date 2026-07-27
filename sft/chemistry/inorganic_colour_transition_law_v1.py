"""Fold-native inorganic electronic-transition and colour law (INORG-008)."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ComplexStateOccurrence:
    complex_identity: HeldLabel
    carrier_kind: HeldLabel
    state_identity: HeldLabel
    order_position: PositiveCount

    def __post_init__(self) -> None:
        if self.complex_identity.family != "coordination-entity":
            raise InadmissibleExactValue("electronic state requires one retained coordination entity")
        if self.carrier_kind.family != "complex-electronic-carrier" or self.carrier_kind.label not in {"ligand", "metal"}:
            raise InadmissibleExactValue("complex electronic support has exactly ligand and metal carrier kinds")
        if self.state_identity.family != "complex-electronic-state":
            raise InadmissibleExactValue("electronic transition requires retained state identity")


@dataclass(frozen=True)
class ExactComplexElectronicTransition:
    source: ComplexStateOccurrence
    target: ComplexStateOccurrence
    positive_order_gap: PositiveCount
    transfer_class: HeldLabel

    def __post_init__(self) -> None:
        if self.source.complex_identity != self.target.complex_identity:
            raise InadmissibleExactValue("transition endpoints must remain in one coordination entity")
        if self.source.state_identity == self.target.state_identity:
            raise InadmissibleExactValue("a transition must retain two distinguishable states")
        if self.target.order_position.value <= self.source.order_position.value:
            raise InadmissibleExactValue("absorption transition must reach a positive state-order successor")
        if self.positive_order_gap.value != self.target.order_position.value - self.source.order_position.value:
            raise InadmissibleExactValue("transition gap must equal the exact positive order separation")
        expected = f"{self.source.carrier_kind.label}-to-{self.target.carrier_kind.label}"
        if self.transfer_class.family != "complex-transition-class" or self.transfer_class.label != expected:
            raise InadmissibleExactValue("transition class must preserve both directed carrier endpoints")


def generate_complete_carrier_transition_classes() -> tuple[HeldLabel, ...]:
    rows = tuple(
        HeldLabel("complex-transition-class", f"{source}-to-{target}")
        for source, target in product(("ligand", "metal"), repeat=2)
    )
    if len(rows) != 4 or len(set(rows)) != 4:
        raise InadmissibleExactValue("two carrier kinds must force four directed transition classes")
    return rows


def build_exact_transition(
    complex_label: str,
    source_carrier: str,
    target_carrier: str,
    source_state: str,
    target_state: str,
    source_position: PositiveCount,
    target_position: PositiveCount,
) -> ExactComplexElectronicTransition:
    complex_identity = HeldLabel("coordination-entity", complex_label)
    source = ComplexStateOccurrence(
        complex_identity,
        HeldLabel("complex-electronic-carrier", source_carrier),
        HeldLabel("complex-electronic-state", source_state),
        source_position,
    )
    target = ComplexStateOccurrence(
        complex_identity,
        HeldLabel("complex-electronic-carrier", target_carrier),
        HeldLabel("complex-electronic-state", target_state),
        target_position,
    )
    if target_position.value <= source_position.value:
        raise InadmissibleExactValue("target position must be a positive successor")
    return ExactComplexElectronicTransition(
        source,
        target,
        PositiveCount(target_position.value - source_position.value),
        HeldLabel("complex-transition-class", f"{source_carrier}-to-{target_carrier}"),
    )


@dataclass(frozen=True)
class ExactSelectiveAbsorption:
    transition: ExactComplexElectronicTransition
    incident_distinctions: tuple[HeldLabel, ...]
    absorbed_distinctions: tuple[HeldLabel, ...]
    retained_colour_distinctions: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if not self.incident_distinctions or len(set(self.incident_distinctions)) != len(self.incident_distinctions):
            raise InadmissibleExactValue("incident observation support must be positive and distinct")
        if any(label.family != "observation-distinction" for label in self.incident_distinctions):
            raise InadmissibleExactValue("incident support contains an invalid distinction")
        incident = set(self.incident_distinctions)
        absorbed = set(self.absorbed_distinctions)
        retained = set(self.retained_colour_distinctions)
        if not absorbed or not retained:
            raise InadmissibleExactValue("colour requires both a positive absorbed and retained distinction class")
        if absorbed & retained or absorbed | retained != incident:
            raise InadmissibleExactValue("absorbed and retained classes must partition complete incident support")
        if len(absorbed) != len(self.absorbed_distinctions) or len(retained) != len(self.retained_colour_distinctions):
            raise InadmissibleExactValue("absorption partition cannot duplicate distinctions")

    @property
    def absorbed_count(self) -> PositiveCount:
        return PositiveCount(len(self.absorbed_distinctions))

    @property
    def retained_colour_count(self) -> PositiveCount:
        return PositiveCount(len(self.retained_colour_distinctions))


def forced_selective_absorption(
    transition: ExactComplexElectronicTransition,
    incident_distinctions: tuple[HeldLabel, ...],
    absorbed_distinctions: tuple[HeldLabel, ...],
) -> ExactSelectiveAbsorption:
    absorbed = set(absorbed_distinctions)
    retained = tuple(label for label in incident_distinctions if label not in absorbed)
    return ExactSelectiveAbsorption(transition, incident_distinctions, absorbed_distinctions, retained)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-SELECTION-RULE-STRUCTURE-010",
    "SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001",
    "SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004",
    "SFT-CHEM-LIGAND-STATE-SPLITTING-006",
    "SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "anonymous-complex-transition", "An anonymous transition erases which retained complex carries it.", "one-retained-coordination-entity", "Every endpoint remains in one identified coordination entity."),
    dimension("endpoints", "imported-orbital-symbol-pair", "Conventional orbital names would select the endpoint grammar.", "complete-ligand-metal-carrier-pair", "Two retained carrier kinds force the complete four-class directed product."),
    dimension("state", "energy-only-endpoints", "Energy-only endpoints lose electronic-state identity.", "two-retained-state-identities", "Source and target remain distinct reconstructible electronic states."),
    dimension("direction", "signed-charge-displacement", "A signed scalar imports negative quantity and erases endpoint direction.", "held-source-target-direction", "Direction is the ordered pair of retained ligand or metal carriers."),
    dimension("gap", "floating-or-dimensional-energy-gap", "A dimensional or floating gap imports an unforced scale.", "positive-state-order-separation", "The gap is exactly the positive successor count between ordered states."),
    dimension("absorption", "selected-colour-name", "A named colour cannot establish what distinction was absorbed.", "proper-absorbed-distinction-class", "Absorption retains a positive proper subset of complete incident observation support."),
    dimension("colour", "conventional-colour-wheel", "A colour wheel imports a continuum convention into forcing.", "retained-complement-observation-class", "Inorganic colour is the exact nonempty observation class left after selective absorption."),
    dimension("extension", "species-peak-or-threshold-exception", "A selected peak or smoothing threshold can manufacture agreement.", "complete-spectra-with-no-extra-rule", "The same endpoint, gap and observation-partition law applies to every complete exact spectrum."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    classes = generate_complete_carrier_transition_classes()
    transition = build_exact_transition("complex", "ligand", "metal", "lower", "upper", PositiveCount(1), PositiveCount(3))
    incident = tuple(HeldLabel("observation-distinction", f"distinction-{index}") for index in range(1, 4))
    absorption = forced_selective_absorption(transition, incident, (incident[1],))
    same_state_rejected = False
    try:
        build_exact_transition("complex", "metal", "metal", "same", "same", PositiveCount(1), PositiveCount(2))
    except InadmissibleExactValue:
        same_state_rejected = True
    complete_absorption_rejected = False
    try:
        forced_selective_absorption(transition, incident, incident)
    except InadmissibleExactValue:
        complete_absorption_rejected = True
    return (
        ("complete-directed-carrier-product", "Ligand and metal endpoints force four directed transition classes.", tuple(row.label for row in classes) == ("ligand-to-ligand", "ligand-to-metal", "metal-to-ligand", "metal-to-metal")),
        ("positive-exact-gap", "The state-order separation is the exact positive successor count.", transition.positive_order_gap.value == 2),
        ("selective-absorption-partition", "One absorbed distinction leaves the exact two-member colour class.", absorption.absorbed_count.value == 1 and absorption.retained_colour_count.value == 2),
        ("same-state-control", "A transition with one erased endpoint identity rejects.", same_state_rejected),
        ("complete-absorption-control", "Absorbing all support leaves no colour class and rejects.", complete_absorption_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "one-retained-coordination-entity__complete-ligand-metal-carrier-pair__two-retained-state-identities__held-source-target-direction__positive-state-order-separation__proper-absorbed-distinction-class__retained-complement-observation-class__complete-spectra-with-no-extra-rule"


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactComplexElectronicTransition",
    "ExactSelectiveAbsorption", "OPERATIONAL_WITNESSES", "build_exact_transition",
    "forced_selective_absorption", "generate_complete_carrier_transition_classes",
)
