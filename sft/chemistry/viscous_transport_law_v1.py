"""Fold-native composition-bound viscous transport law for THERMO-017."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ViscousChemicalAccount:
    component_identities: tuple[HeldLabel, ...]
    phase_identity: HeldLabel
    source_layer: PositiveCount
    destination_layer: PositiveCount
    momentum_packet_support: PositiveCount
    exchange_count: PositiveCount
    tick_count: PositiveCount
    condition_support: tuple[PositiveRatio | EmptyOne, ...]

    def __post_init__(self) -> None:
        if not self.component_identities or any(
            not isinstance(row, HeldLabel) or row.family != "chemical-component" for row in self.component_identities
        ):
            raise InadmissibleExactValue("viscous account requires complete component identities")
        if len(set(self.component_identities)) != len(self.component_identities):
            raise InadmissibleExactValue("viscous component identities collapsed")
        if not isinstance(self.phase_identity, HeldLabel) or self.phase_identity.family != "chemical-phase":
            raise InadmissibleExactValue("viscous account lost phase identity")
        if any(not isinstance(row, PositiveCount) for row in (
            self.source_layer, self.destination_layer, self.momentum_packet_support, self.exchange_count, self.tick_count
        )):
            raise InadmissibleExactValue("viscous transport requires exact positive counts")
        if abs(self.source_layer.value - self.destination_layer.value) != 1:
            raise InadmissibleExactValue("viscous exchange is not between adjacent generated layers")
        if not self.condition_support or any(not isinstance(row, (PositiveRatio, EmptyOne)) for row in self.condition_support):
            raise InadmissibleExactValue("viscous condition carrier is incomplete")


@dataclass(frozen=True)
class CountedViscousRelation:
    carrier: HeldLabel
    orientation: HeldLabel
    exchange_density: PositiveRatio


def forced_viscous_transport(account: ViscousChemicalAccount) -> CountedViscousRelation:
    if not isinstance(account, ViscousChemicalAccount):
        raise InadmissibleExactValue("viscous transport requires a complete account")
    classes = {1: "pure", 2: "binary", 3: "ternary"}
    mixture_class = classes.get(len(account.component_identities), "higher-component")
    orientation = "toward-later-generated-layer" if account.source_layer.value < account.destination_layer.value else "toward-earlier-generated-layer"
    return CountedViscousRelation(
        HeldLabel("viscous-chemical-carrier", f"{mixture_class}-composition-retained-momentum-exchange"),
        HeldLabel("viscous-orientation", orientation),
        PositiveRatio.from_pair(
            account.momentum_packet_support.value * account.exchange_count.value,
            account.tick_count.value,
        ),
    )


def external_viscosity_magnitude(inscription: str) -> PositiveRatio:
    if not isinstance(inscription, str) or not inscription.strip() or inscription.strip().startswith("-"):
        raise InadmissibleExactValue("viscosity requires exact positive external support")
    try:
        value = Fraction(inscription.strip().lstrip("+"))
        return PositiveRatio.from_pair(value.numerator, value.denominator)
    except Exception as exc:
        raise InadmissibleExactValue("viscosity is not exact positive finite support") from exc


def common_exchange_replication_preserves_relation(account: ViscousChemicalAccount, replication: PositiveCount) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("viscous replication requires exact positive support")
    prior = forced_viscous_transport(account)
    replicated = ViscousChemicalAccount(
        account.component_identities, account.phase_identity, account.source_layer, account.destination_layer,
        account.momentum_packet_support,
        PositiveCount(account.exchange_count.value * replication.value),
        PositiveCount(account.tick_count.value * replication.value), account.condition_support,
    )
    successor = forced_viscous_transport(replicated)
    return (
        successor.carrier == prior.carrier and successor.orientation == prior.orientation
        and successor.exchange_density.fraction == prior.exchange_density.fraction
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-GEOMETRY-TOPOLOGY-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-PHYS-MECH-MOMENTUM-001", "SFT-PHYS-FLUID-PRESSURE-STRESS-001", "SFT-PHYS-FLUID-CONSERVATION-001",
    "SFT-PHYS-FLUID-VISCOSITY-001", "SFT-PHYS-THERMO-KINETIC-TRANSPORT-001",
    "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013", "SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "detached-viscosity-number-or-continuum-field", "A detached number or field erases momentum exchange.", "complete-composition-phase-condition-momentum-account", "Every record retains components, phase, conditions, layers, packets, exchanges and ticks."),
    dimension("identity", "anonymous-or-collapsed-composition", "Collapsed composition cannot own a chemical viscosity relation.", "distinct-held-complete-component-identities", "Every pure, binary or ternary component identity remains held."),
    dimension("transfer", "continuous-velocity-gradient-premise", "A continuum gradient imports an ungenerated carrier.", "counted-adjacent-layer-momentum-exchange", "Momentum packets exchange across adjacent generated layers."),
    dimension("orientation", "signed-shear-or-stress-proof-magnitude", "Signed shear imports prohibited arithmetic.", "held-opposed-layer-transfer-orientation", "Opposed transfer directions are held labels with positive support."),
    dimension("resource", "unrecorded-packet-exchange-time-or-condition", "Unrecorded resources cannot reconstruct viscosity.", "exact-positive-packet-exchange-tick-and-condition-support", "Packets, exchanges, ticks and conditions are exact retained support."),
    dimension("magnitude", "imported-Newtonian-Arrhenius-WLF-VFT-or-fit", "An imported constitutive or fitted law selects the magnitude.", "exact-positive-postseal-viscosity-support", "Measured viscosity opens only after the structural relation seals."),
    dimension("prediction", "substance-composition-condition-method-or-value-readable-before-seal", "Readable targets could select the law.", "complete-value-free-425-record-identity-seal", "All pure, binary and ternary identities seal before target content opens."),
    dimension("extension", "refit-after-exchange-replication-or-record-append", "Refitting destroys exact exchange provenance.", "depth-independent-common-replication-and-record-append", "Common exchange/tick replication and complete append preserve the relation."),
)


EXACT_RESULT = (
    "complete-composition-phase-condition-momentum-account__distinct-held-complete-component-identities__"
    "counted-adjacent-layer-momentum-exchange__held-opposed-layer-transfer-orientation__"
    "exact-positive-packet-exchange-tick-and-condition-support__exact-positive-postseal-viscosity-support__"
    "complete-value-free-425-record-identity-seal__depth-independent-common-replication-and-record-append"
)


def _account(component_count: int = 2, reverse: bool = False) -> ViscousChemicalAccount:
    components = tuple(HeldLabel("chemical-component", f"component-{index}") for index in range(1, component_count + 1))
    return ViscousChemicalAccount(
        components, HeldLabel("chemical-phase", "liquid"),
        PositiveCount(5 if reverse else 4), PositiveCount(4 if reverse else 5),
        PositiveCount(3), PositiveCount(7), PositiveCount(5),
        (PositiveRatio.from_pair(29815, 100), EmptyOne()),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    forward = forced_viscous_transport(_account())
    reverse = forced_viscous_transport(_account(reverse=True))
    return (
        ("pure-binary-ternary-carriers", "Pure, binary and ternary compositions preserve distinct carriers.", tuple(forced_viscous_transport(_account(count)).carrier.label for count in (1, 2, 3)) == ("pure-composition-retained-momentum-exchange", "binary-composition-retained-momentum-exchange", "ternary-composition-retained-momentum-exchange")),
        ("held-layer-orientation", "Opposed layer directions are held labels without signed shear.", forward.orientation.label == "toward-later-generated-layer" and reverse.orientation.label == "toward-earlier-generated-layer"),
        ("exact-exchange-density", "Packet/exchange/tick support forms an exact positive relation.", forward.exchange_density.fraction == PositiveRatio.from_pair(21, 5).fraction),
        ("replication-successor", "Common exchange/tick replication preserves the composition-bound relation.", common_exchange_replication_preserves_relation(_account(3), PositiveCount(6))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "CountedViscousRelation", "OPERATIONAL_WITNESSES",
    "ViscousChemicalAccount", "common_exchange_replication_preserves_relation", "external_viscosity_magnitude",
    "forced_viscous_transport",
)
