"""Fold-native coupled mass, heat and charge transport law for THERMO-019."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class CoupledTransportAccount:
    component_identities: tuple[HeldLabel, ...]
    phase_identity: HeldLabel
    carrier_identities: tuple[HeldLabel, ...]
    source_cell: PositiveCount
    destination_cell: PositiveCount
    carrier_packet_support: tuple[PositiveCount, ...]
    shared_transition_count: PositiveCount
    tick_count: PositiveCount
    boundary_support: PositiveCount
    condition_support: tuple[PositiveRatio | EmptyOne, ...]

    def __post_init__(self) -> None:
        if not self.component_identities or any(
            not isinstance(row, HeldLabel) or row.family != "chemical-component" for row in self.component_identities
        ) or len(set(self.component_identities)) != len(self.component_identities):
            raise InadmissibleExactValue("coupled transport requires distinct complete component identities")
        if not isinstance(self.phase_identity, HeldLabel) or self.phase_identity.family != "chemical-phase":
            raise InadmissibleExactValue("coupled transport lost phase identity")
        if (
            len(self.carrier_identities) != 3
            or any(not isinstance(row, HeldLabel) or row.family != "transport-carrier" for row in self.carrier_identities)
            or tuple(row.label for row in self.carrier_identities) != ("mass", "heat", "charge")
        ):
            raise InadmissibleExactValue("coupled transport requires the complete ordered mass/heat/charge carrier triad")
        counts = (self.source_cell, self.destination_cell, self.shared_transition_count, self.tick_count, self.boundary_support)
        if any(not isinstance(row, PositiveCount) for row in counts):
            raise InadmissibleExactValue("coupled transport requires exact positive transition resources")
        if not (
            self.destination_cell.value == self.source_cell.value + 1
            or self.source_cell.value == self.destination_cell.value + 1
        ):
            raise InadmissibleExactValue("coupled transport is not adjacent")
        if len(self.carrier_packet_support) != 3 or any(not isinstance(row, PositiveCount) for row in self.carrier_packet_support):
            raise InadmissibleExactValue("coupled transport lost a carrier packet ledger")
        if not self.condition_support or any(not isinstance(row, (PositiveRatio, EmptyOne)) for row in self.condition_support):
            raise InadmissibleExactValue("coupled transport condition carrier is incomplete")


@dataclass(frozen=True)
class CountedCoupledTransportRelation:
    carrier_topology: HeldLabel
    orientations: tuple[HeldLabel, ...]
    response_support: tuple[PositiveRatio, ...]
    pairwise_projections: tuple[HeldLabel, ...]


def forced_coupled_transport(account: CoupledTransportAccount) -> CountedCoupledTransportRelation:
    if not isinstance(account, CoupledTransportAccount):
        raise InadmissibleExactValue("coupled transport requires a complete account")
    direction = "source-to-destination" if account.source_cell.value < account.destination_cell.value else "destination-to-source"
    mixture_class = {1: "pure", 2: "binary", 3: "ternary"}.get(len(account.component_identities), "higher-component")
    orientations = tuple(HeldLabel("transport-orientation", f"{carrier.label}:{direction}") for carrier in account.carrier_identities)
    responses = tuple(
        PositiveRatio.from_pair(
            packet.value * account.shared_transition_count.value,
            account.tick_count.value * account.boundary_support.value,
        ) for packet in account.carrier_packet_support
    )
    return CountedCoupledTransportRelation(
        HeldLabel("coupled-transport-topology", f"{mixture_class}-composition-phase-shared-mass-heat-charge-event-ledger"),
        orientations, responses,
        (
            HeldLabel("coupled-carrier-projection", "mass-heat"),
            HeldLabel("coupled-carrier-projection", "mass-charge"),
            HeldLabel("coupled-carrier-projection", "heat-charge"),
        ),
    )


def common_event_replication_preserves_relation(account: CoupledTransportAccount, replication: PositiveCount) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("coupled-transport replication requires exact positive support")
    prior = forced_coupled_transport(account)
    replicated = CoupledTransportAccount(
        account.component_identities, account.phase_identity, account.carrier_identities,
        account.source_cell, account.destination_cell, account.carrier_packet_support,
        PositiveCount(account.shared_transition_count.value * replication.value),
        PositiveCount(account.tick_count.value * replication.value), account.boundary_support, account.condition_support,
    )
    successor = forced_coupled_transport(replicated)
    return (
        successor.carrier_topology == prior.carrier_topology
        and successor.orientations == prior.orientations
        and successor.pairwise_projections == prior.pairwise_projections
        and tuple(row.fraction for row in successor.response_support) == tuple(row.fraction for row in prior.response_support)
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001", "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001", "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001",
    "SFT-PHYS-THERMO-TEMPERATURE-001", "SFT-PHYS-THERMO-HEAT-WORK-001", "SFT-PHYS-THERMO-FIRST-LAW-001",
    "SFT-PHYS-THERMO-KINETIC-TRANSPORT-001", "SFT-PHYS-THERMO-RESPONSE-001",
    "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013", "SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016",
    "SFT-CHEM-VISCOUS-TRANSPORT-RELATION-017", "SFT-CHEM-THERMAL-CONDUCTIVITY-RELATION-018",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "detached-cross-coefficient-or-answer-vector", "Detached coefficients erase the transported carriers.", "complete-composition-phase-mass-heat-charge-account", "Every component, phase and member of the mass/heat/charge triad remains held."),
    dimension("identity", "anonymous-collapsed-carriers-or-pair", "A collapsed carrier or pair cannot reconstruct the coupling.", "distinct-held-triad-and-pairwise-projections", "The ordered triad and all three pairwise projections remain distinguishable."),
    dimension("transition", "imported-Onsager-matrix-gradient-or-flux-equation", "A phenomenological matrix or continuum gradient imports the desired coupling.", "counted-shared-adjacent-cell-transition-ledger", "Mass, heat and charge packets share one counted adjacent transition record."),
    dimension("orientation", "signed-flux-proof-magnitudes", "Signed mass, heat or charge magnitudes violate exact proof arithmetic.", "held-per-carrier-transfer-orientations", "Each carrier direction is a held label with positive support."),
    dimension("resource", "unrecorded-packet-event-time-boundary-or-condition", "Unrecorded resources cannot reconstruct the coupled response.", "exact-positive-packet-event-tick-boundary-and-condition-support", "Each packet, shared event, tick, boundary and condition is exactly retained."),
    dimension("magnitude", "phenomenological-cross-coefficient-fit-or-target-value", "A fitted cross coefficient selects the result.", "exact-positive-postseal-pairwise-response-support", "Measured pairwise responses open only after the triad relation seals."),
    dimension("prediction", "substance-pair-property-condition-method-or-value-readable-before-seal", "Readable pairwise targets could select the coupling law.", "complete-value-free-232-record-pair-identity-seal", "All mass-heat, mass-charge and heat-charge identities seal before target content opens."),
    dimension("extension", "refit-after-event-replication-or-record-append", "Refitting destroys shared-event provenance.", "depth-independent-common-replication-and-record-append", "Common event/tick replication and complete append preserve every response."),
)


EXACT_RESULT = (
    "complete-composition-phase-mass-heat-charge-account__distinct-held-triad-and-pairwise-projections__"
    "counted-shared-adjacent-cell-transition-ledger__held-per-carrier-transfer-orientations__"
    "exact-positive-packet-event-tick-boundary-and-condition-support__exact-positive-postseal-pairwise-response-support__"
    "complete-value-free-232-record-pair-identity-seal__depth-independent-common-replication-and-record-append"
)


def _account(component_count: int = 2, reverse: bool = False) -> CoupledTransportAccount:
    return CoupledTransportAccount(
        tuple(HeldLabel("chemical-component", f"component-{index}") for index in range(1, component_count + 1)),
        HeldLabel("chemical-phase", "liquid"),
        tuple(HeldLabel("transport-carrier", name) for name in ("mass", "heat", "charge")),
        PositiveCount(5 if reverse else 4), PositiveCount(4 if reverse else 5),
        (PositiveCount(2), PositiveCount(3), PositiveCount(5)),
        PositiveCount(7), PositiveCount(11), PositiveCount(2),
        (PositiveRatio.from_pair(29815, 100), EmptyOne()),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    forward = forced_coupled_transport(_account())
    reverse = forced_coupled_transport(_account(reverse=True))
    return (
        ("complete-triad", "Mass, heat and charge remain distinct on one shared event ledger.", tuple(row.label for row in _account().carrier_identities) == ("mass", "heat", "charge")),
        ("complete-pairwise-projections", "All three pairwise projections are present once.", tuple(row.label for row in forward.pairwise_projections) == ("mass-heat", "mass-charge", "heat-charge")),
        ("held-orientations", "Opposed carrier directions are held labels without signed flux.", forward.orientations != reverse.orientations),
        ("exact-responses", "The triad response is exact positive packet/event support per tick and boundary.", tuple(row.fraction for row in forward.response_support) == tuple(PositiveRatio.from_pair(value, 22).fraction for value in (14, 21, 35))),
        ("replication-successor", "Common event/tick replication preserves all pairwise responses.", common_event_replication_preserves_relation(_account(3), PositiveCount(6))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "CoupledTransportAccount", "CountedCoupledTransportRelation",
    "OPERATIONAL_WITNESSES", "common_event_replication_preserves_relation", "forced_coupled_transport",
)
