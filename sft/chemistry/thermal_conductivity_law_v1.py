"""Fold-native composition-bound thermal-conductivity law for THERMO-018."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ThermalConductionAccount:
    component_identities: tuple[HeldLabel, ...]
    phase_identity: HeldLabel
    source_cell: PositiveCount
    destination_cell: PositiveCount
    source_thermal_order: PositiveCount
    destination_thermal_order: PositiveCount
    energy_packet_support: PositiveCount
    transfer_count: PositiveCount
    tick_count: PositiveCount
    boundary_support: PositiveCount
    condition_support: tuple[PositiveRatio | EmptyOne, ...]

    def __post_init__(self) -> None:
        if not self.component_identities or any(
            not isinstance(row, HeldLabel) or row.family != "chemical-component" for row in self.component_identities
        ):
            raise InadmissibleExactValue("thermal conduction requires complete component identities")
        if len(set(self.component_identities)) != len(self.component_identities):
            raise InadmissibleExactValue("thermal-conduction component identities collapsed")
        if not isinstance(self.phase_identity, HeldLabel) or self.phase_identity.family != "chemical-phase":
            raise InadmissibleExactValue("thermal conduction lost phase identity")
        counts = (
            self.source_cell, self.destination_cell, self.source_thermal_order, self.destination_thermal_order,
            self.energy_packet_support, self.transfer_count, self.tick_count, self.boundary_support,
        )
        if any(not isinstance(row, PositiveCount) for row in counts):
            raise InadmissibleExactValue("thermal conduction requires exact positive counts")
        if not (
            self.destination_cell.value == self.source_cell.value + 1
            or self.source_cell.value == self.destination_cell.value + 1
        ):
            raise InadmissibleExactValue("thermal conduction is not between adjacent generated cells")
        if self.source_thermal_order.value == self.destination_thermal_order.value:
            raise InadmissibleExactValue("thermal-conduction direction is absent at equal thermal order")
        if not self.condition_support or any(not isinstance(row, (PositiveRatio, EmptyOne)) for row in self.condition_support):
            raise InadmissibleExactValue("thermal-conduction condition carrier is incomplete")


@dataclass(frozen=True)
class CountedThermalConductivityRelation:
    carrier: HeldLabel
    orientation: HeldLabel
    transfer_response: PositiveRatio


def forced_thermal_conductivity(account: ThermalConductionAccount) -> CountedThermalConductivityRelation:
    if not isinstance(account, ThermalConductionAccount):
        raise InadmissibleExactValue("thermal conductivity requires a complete account")
    mixture_class = {1: "pure", 2: "binary", 3: "ternary"}.get(len(account.component_identities), "higher-component")
    orientation = (
        "source-higher-to-destination-lower-thermal-order"
        if account.source_thermal_order.value > account.destination_thermal_order.value
        else "destination-higher-to-source-lower-thermal-order"
    )
    thermal_separation = (
        account.source_thermal_order.value - account.destination_thermal_order.value
        if account.source_thermal_order.value > account.destination_thermal_order.value
        else account.destination_thermal_order.value - account.source_thermal_order.value
    )
    return CountedThermalConductivityRelation(
        HeldLabel("thermal-conductivity-chemical-carrier", f"{mixture_class}-composition-phase-energy-packet-transfer"),
        HeldLabel("thermal-transfer-orientation", orientation),
        PositiveRatio.from_pair(
            account.energy_packet_support.value * account.transfer_count.value,
            account.tick_count.value * account.boundary_support.value * thermal_separation,
        ),
    )


def external_thermal_conductivity_magnitude(inscription: str) -> PositiveRatio:
    if not isinstance(inscription, str) or not inscription.strip() or inscription.strip().startswith("-"):
        raise InadmissibleExactValue("thermal conductivity requires exact positive external support")
    try:
        value = Fraction(inscription.strip().lstrip("+"))
        return PositiveRatio.from_pair(value.numerator, value.denominator)
    except Exception as exc:
        raise InadmissibleExactValue("thermal conductivity is not exact positive finite support") from exc


def common_transfer_replication_preserves_relation(account: ThermalConductionAccount, replication: PositiveCount) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("thermal-conduction replication requires exact positive support")
    prior = forced_thermal_conductivity(account)
    replicated = ThermalConductionAccount(
        account.component_identities, account.phase_identity, account.source_cell, account.destination_cell,
        account.source_thermal_order, account.destination_thermal_order, account.energy_packet_support,
        PositiveCount(account.transfer_count.value * replication.value),
        PositiveCount(account.tick_count.value * replication.value), account.boundary_support, account.condition_support,
    )
    successor = forced_thermal_conductivity(replicated)
    return (
        successor.carrier == prior.carrier and successor.orientation == prior.orientation
        and successor.transfer_response.fraction == prior.transfer_response.fraction
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001", "SFT-PHYS-THERMO-TEMPERATURE-001", "SFT-PHYS-THERMO-HEAT-WORK-001",
    "SFT-PHYS-THERMO-FIRST-LAW-001", "SFT-PHYS-THERMO-KINETIC-TRANSPORT-001", "SFT-PHYS-THERMO-RESPONSE-001",
    "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013", "SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016",
    "SFT-CHEM-VISCOUS-TRANSPORT-RELATION-017",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "detached-conductivity-number-or-continuum-field", "A detached number or field erases the chemical energy-transfer account.", "complete-composition-phase-condition-energy-transfer-account", "Every record retains components, phase, conditions, cells, thermal orders, packets, transfers, ticks and boundary support."),
    dimension("identity", "anonymous-or-collapsed-composition-phase", "Collapsed composition or phase cannot own a chemical conductivity relation.", "distinct-held-complete-component-and-phase-identities", "Every pure, binary or ternary component and gas, liquid or crystalline phase identity remains held."),
    dimension("transfer", "Fourier-gradient-or-continuum-carrier-premise", "A continuum temperature gradient imports an ungenerated carrier.", "counted-adjacent-cell-energy-packet-transfer", "Energy packets transfer across adjacent generated cells under the admitted physical carrier."),
    dimension("orientation", "signed-heat-flux-proof-magnitude", "Signed heat flux imports prohibited arithmetic.", "held-higher-to-lower-thermal-order-orientation", "The two opposed directions are held labels with positive support."),
    dimension("resource", "unrecorded-energy-transfer-time-boundary-order-or-condition", "Unrecorded resources cannot reconstruct conductivity.", "exact-positive-packet-transfer-tick-boundary-order-and-condition-support", "Packets, transfers, ticks, boundary, thermal separation and conditions are exact retained support."),
    dimension("magnitude", "imported-Fourier-kinetic-mixing-temperature-fit-or-logarithm", "An imported constitutive or fitted law selects the magnitude.", "exact-positive-postseal-thermal-conductivity-support", "Measured conductivity opens only after the structural relation seals."),
    dimension("prediction", "substance-composition-phase-condition-method-or-value-readable-before-seal", "Readable targets could select the law.", "complete-value-free-655-record-identity-seal", "All pure, binary and ternary identities seal before target content opens."),
    dimension("extension", "refit-after-transfer-replication-or-record-append", "Refitting destroys exact transfer provenance.", "depth-independent-common-replication-and-record-append", "Common transfer/tick replication and complete append preserve the relation."),
)


EXACT_RESULT = (
    "complete-composition-phase-condition-energy-transfer-account__distinct-held-complete-component-and-phase-identities__"
    "counted-adjacent-cell-energy-packet-transfer__held-higher-to-lower-thermal-order-orientation__"
    "exact-positive-packet-transfer-tick-boundary-order-and-condition-support__exact-positive-postseal-thermal-conductivity-support__"
    "complete-value-free-655-record-identity-seal__depth-independent-common-replication-and-record-append"
)


def _account(component_count: int = 2, reverse: bool = False) -> ThermalConductionAccount:
    components = tuple(HeldLabel("chemical-component", f"component-{index}") for index in range(1, component_count + 1))
    return ThermalConductionAccount(
        components, HeldLabel("chemical-phase", "liquid"), PositiveCount(4), PositiveCount(5),
        PositiveCount(3 if reverse else 7), PositiveCount(7 if reverse else 3),
        PositiveCount(5), PositiveCount(11), PositiveCount(7), PositiveCount(2),
        (PositiveRatio.from_pair(29815, 100), EmptyOne()),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    forward = forced_thermal_conductivity(_account())
    reverse = forced_thermal_conductivity(_account(reverse=True))
    return (
        ("pure-binary-ternary-carriers", "Pure, binary and ternary compositions preserve distinct energy-transfer carriers.", tuple(forced_thermal_conductivity(_account(count)).carrier.label for count in (1, 2, 3)) == ("pure-composition-phase-energy-packet-transfer", "binary-composition-phase-energy-packet-transfer", "ternary-composition-phase-energy-packet-transfer")),
        ("held-thermal-orientation", "Opposed thermal directions are held labels without signed heat flux.", forward.orientation.label != reverse.orientation.label),
        ("exact-transfer-response", "Packet/transfer/tick/boundary/order support forms an exact positive relation.", forward.transfer_response.fraction == PositiveRatio.from_pair(55, 56).fraction),
        ("replication-successor", "Common transfer/tick replication preserves the composition-bound relation.", common_transfer_replication_preserves_relation(_account(3), PositiveCount(6))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "CountedThermalConductivityRelation", "OPERATIONAL_WITNESSES",
    "ThermalConductionAccount", "common_transfer_replication_preserves_relation",
    "external_thermal_conductivity_magnitude", "forced_thermal_conductivity",
)
