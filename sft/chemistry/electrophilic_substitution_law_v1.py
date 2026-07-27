"""Fold-native acceptor-driven aromatic substitution law for Chemistry ORG-008.

No conventional electrophilic name, rate law, energy surface, solvent rule,
substrate example or external target enters the candidate generator.  Those
records are opened only at the correspondence boundary after sealing.
"""
from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.nucleophilic_substitution_law_v1 import (
    HeldBond, HeldPair, SubstitutionState, electron, occurrence,
)
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ElectrophilicExchangeCarrier:
    reaction_identity: HeldLabel
    aromatic_left: HeldLabel
    centre: HeldLabel
    aromatic_right: HeldLabel
    entering_acceptor: HeldLabel
    leaving_carrier: HeldLabel
    donor_pair: HeldPair
    recurrence_pair: HeldPair
    leaving_pair: HeldPair
    acceptor_slot: EmptyOne
    source: SubstitutionState

    def __post_init__(self) -> None:
        if self.reaction_identity.family != "registered-reaction":
            raise InadmissibleExactValue("acceptor-driven substitution requires one registered reaction")
        roles = (
            self.aromatic_left, self.centre, self.aromatic_right,
            self.entering_acceptor, self.leaving_carrier,
        )
        if len(set(roles)) != len(roles) or any(row not in self.source.atoms for row in roles):
            raise InadmissibleExactValue("aromatic exchange roles require five distinct retained occurrences")
        if self.acceptor_slot is not EMPTY_ONE:
            raise InadmissibleExactValue("the unoccupied entering acceptor slot is structural EmptyOne")
        bonds = _bond_map(self.source)
        required = {
            frozenset((self.aromatic_left, self.centre)): self.donor_pair,
            frozenset((self.centre, self.aromatic_right)): self.recurrence_pair,
            frozenset((self.centre, self.leaving_carrier)): self.leaving_pair,
        }
        if any(bonds.get(edge) != pair for edge, pair in required.items()) or self.source.free_pairs:
            raise InadmissibleExactValue("source must retain the complete aromatic donor, recurrence and leaving supports")
        extras = set(bonds) - set(required)
        if any(self.centre in edge or self.entering_acceptor in edge or self.leaving_carrier in edge for edge in extras):
            raise InadmissibleExactValue("source extensions cannot alter the local aromatic exchange support")
        if any(self.entering_acceptor in edge for edge in bonds):
            raise InadmissibleExactValue("the source acceptor cannot already carry the entering bond")


@dataclass(frozen=True)
class ElectrophilicTransition:
    occurrence: PositiveCount
    entry: SubstitutionState
    exit: SubstitutionState
    action: HeldLabel

    def __post_init__(self) -> None:
        if self.action.family != "acceptor-substitution-action" or self.action.label not in {
            "exchange-and-restore-in-one-transition",
            "transfer-aromatic-pair-to-entering-support",
            "relinquish-leaving-pair-to-restore-recurrence",
        }:
            raise InadmissibleExactValue("transition action is outside the generated acceptor-exchange alphabet")
        if self.entry.atoms != self.exit.atoms:
            raise InadmissibleExactValue("every atom occurrence must survive the transition")
        if self.entry.electron_occurrences != self.exit.electron_occurrences:
            raise InadmissibleExactValue("every held electron occurrence must survive the transition")


@dataclass(frozen=True)
class ExactElectrophilicExchange:
    carrier: ElectrophilicExchangeCarrier
    ordered_states: tuple[SubstitutionState, ...]
    ordered_transitions: tuple[ElectrophilicTransition, ...]
    terminal: SubstitutionState
    path_class: HeldLabel
    transition_count: PositiveCount


def _bond_map(state: SubstitutionState) -> dict[frozenset[HeldLabel], HeldPair]:
    return {bond.endpoints: bond.pair for bond in state.retained_bonds}


def _state_role(carrier: ElectrophilicExchangeCarrier, state: SubstitutionState) -> str:
    bonds = _bond_map(state)
    donor_edge = frozenset((carrier.aromatic_left, carrier.centre))
    recurrence_edge = frozenset((carrier.centre, carrier.aromatic_right))
    leaving_edge = frozenset((carrier.centre, carrier.leaving_carrier))
    entering_edge = frozenset((carrier.centre, carrier.entering_acceptor))
    allowed = {donor_edge, recurrence_edge, leaving_edge, entering_edge}
    background = {edge: pair for edge, pair in bonds.items() if edge not in allowed}
    if any(carrier.centre in edge or carrier.entering_acceptor in edge or carrier.leaving_carrier in edge for edge in background):
        raise InadmissibleExactValue("an extension cannot alter the local exchange support")
    if bonds.get(recurrence_edge) != carrier.recurrence_pair or state.free_pairs:
        raise InadmissibleExactValue("the retained aromatic recurrence support changed")
    local = {edge: pair for edge, pair in bonds.items() if edge in allowed}
    if local == {
        donor_edge: carrier.donor_pair,
        recurrence_edge: carrier.recurrence_pair,
        leaving_edge: carrier.leaving_pair,
    }:
        return "source"
    if local == {
        recurrence_edge: carrier.recurrence_pair,
        leaving_edge: carrier.leaving_pair,
        entering_edge: carrier.donor_pair,
    }:
        return "addition-intermediate"
    if local == {
        donor_edge: carrier.leaving_pair,
        recurrence_edge: carrier.recurrence_pair,
        entering_edge: carrier.donor_pair,
    }:
        return "restored-terminal"
    raise InadmissibleExactValue("state is not generated by the complete acceptor-driven aromatic exchange")


def forced_electrophilic_exchange_path(
    carrier: ElectrophilicExchangeCarrier,
    ordered_states: tuple[SubstitutionState, ...],
    ordered_transitions: tuple[ElectrophilicTransition, ...],
) -> ExactElectrophilicExchange:
    if len(ordered_states) not in (2, 3) or len(ordered_transitions) != len(ordered_states) - 1:
        raise InadmissibleExactValue("acceptor exchange admits exactly one-transition or two-transition paths")
    if ordered_states[0] != carrier.source:
        raise InadmissibleExactValue("path must begin at the complete registered source")
    if tuple(row.occurrence.value for row in ordered_transitions) != tuple(range(1, len(ordered_transitions) + 1)):
        raise InadmissibleExactValue("transition occurrences must remain complete and gap-free")
    roles = tuple(_state_role(carrier, state) for state in ordered_states)
    for left, edge, right in zip(ordered_states, ordered_transitions, ordered_states[1:]):
        if edge.entry != left or edge.exit != right:
            raise InadmissibleExactValue("every transition must meet its retained adjacent states")
    if roles == ("source", "restored-terminal"):
        expected = ("exchange-and-restore-in-one-transition",)
        path_label = "one-transition-exchange-and-restoration"
    elif roles == ("source", "addition-intermediate", "restored-terminal"):
        expected = (
            "transfer-aromatic-pair-to-entering-support",
            "relinquish-leaving-pair-to-restore-recurrence",
        )
        path_label = "addition-then-recurrence-restoration"
    else:
        raise InadmissibleExactValue("path order is outside the complete generated acceptor-exchange family")
    if tuple(row.action.label for row in ordered_transitions) != expected:
        raise InadmissibleExactValue("transition actions do not reconstruct the generated states")
    return ExactElectrophilicExchange(
        carrier, ordered_states, ordered_transitions, ordered_states[-1],
        HeldLabel("acceptor-substitution-path-class", path_label), PositiveCount(len(ordered_transitions)),
    )


def extend_aromatic_carrier(
    result: ExactElectrophilicExchange,
    new_atom: HeldLabel,
    new_pair: HeldPair,
) -> bool:
    carrier = result.carrier
    if new_atom in carrier.source.atoms or new_atom.family != "substitution-atom-occurrence":
        raise InadmissibleExactValue("aromatic successor requires one fresh retained occurrence")
    atoms = carrier.source.atoms + (new_atom,)
    states = tuple(
        SubstitutionState(
            state.state_identity, atoms,
            state.retained_bonds + (HeldBond(carrier.aromatic_left, new_atom, new_pair),),
            state.free_pairs,
        )
        for state in result.ordered_states
    )
    extended_carrier = ElectrophilicExchangeCarrier(
        carrier.reaction_identity, carrier.aromatic_left, carrier.centre, carrier.aromatic_right,
        carrier.entering_acceptor, carrier.leaving_carrier, carrier.donor_pair, carrier.recurrence_pair,
        carrier.leaving_pair, EMPTY_ONE, states[0],
    )
    edges = tuple(
        ElectrophilicTransition(edge.occurrence, states[index], states[index + 1], edge.action)
        for index, edge in enumerate(result.ordered_transitions)
    )
    extended = forced_electrophilic_exchange_path(extended_carrier, states, edges)
    return (
        extended.path_class == result.path_class and extended.transition_count == result.transition_count
        and all(state.retained_bonds[:-1] == prior.retained_bonds for state, prior in zip(states, result.ordered_states))
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-BOND-COVALENT-001", "SFT-CHEM-BOND-ORDER-001",
    "SFT-CHEM-MOL-MOLECULE-001", "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-ORGANIC-FUNCTIONAL-GROUP-001", "SFT-CHEM-ORGANIC-REACTION-FAMILY-001",
    "SFT-CHEM-CONJUGATED-SUPPORT-001", "SFT-CHEM-RESONANCE-EQUIVALENT-REPRESENTATION-002",
    "SFT-CHEM-AROMATIC-RECURRENCE-STABILITY-003", "SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "selected-product-label-or-nonaromatic-fragments", "A named answer or disconnected fragments cannot reconstruct one aromatic reaction carrier.", "complete-aromatic-source-ordered-carrier", "Aromatic left, centre, right, entering acceptor and leaving carrier remain distinct occurrences in one complete source."),
    dimension("acceptor", "incoming-pair-imported-or-acceptor-slot-filled", "Giving the acceptor a pre-existing pair changes which carrier supplies the new bond.", "structural-EmptyOne-entering-acceptor-slot", "The entering carrier begins with structural EmptyOne and accepts the complete donor pair."),
    dimension("donor", "donor-pair-erased-created-or-collapsed-to-charge", "A scalar charge or incomplete pair loses the transferred occurrences.", "complete-aromatic-donor-pair-transfer", "Both donor occurrences move from one aromatic incidence to the centre-entering incidence."),
    dimension("change", "endpoint-only-product-or-extra-support-change", "An endpoint or extra edit does not prove the local exchange.", "entering-bond-formed-leaving-bond-cleaved", "Exactly the entering bond forms and the leaving bond closes while all other local incidences remain retained."),
    dimension("path", "named-rate-law-cleavage-first-or-unordered-snapshots", "A conventional name, kinetic law or wrong order can select a mechanism.", "complete-concerted-and-addition-then-restoration-path-family", "The generated family retains direct exchange and donor transfer followed by leaving-pair recurrence restoration."),
    dimension("recurrence", "aromatic-support-destroyed-or-fitted-restoration", "An unclosed or fitted recurrence does not return the carrier to its exact class.", "leaving-pair-restores-aromatic-incidence", "The leaving pair relinquishes both occurrences to restore the opened aromatic incidence exactly."),
    dimension("observation", "substrate-product-mechanism-readable-before-seal", "External structures or terminology could select the survivor.", "value-free-aromatic-structure-and-mechanism-target-seal", "Law and complete target identities seal before newly registered structure or mechanism outcomes open."),
    dimension("extension", "substrate-specific-exception-or-recomputed-prefix", "A special aromatic substrate rule is not depth-independent.", "fresh-aromatic-successor-no-extra-rule", "Adding one fresh retained aromatic occurrence preserves every prior state, edge and pair allocation."),
)


def _example_paths() -> tuple[ElectrophilicExchangeCarrier, ExactElectrophilicExchange, ExactElectrophilicExchange]:
    left, centre, right, entering, leaving = map(occurrence, ("aromatic-left", "centre", "aromatic-right", "entering-acceptor", "leaving"))
    donor = HeldPair(electron("donor-one"), electron("donor-two"))
    recurrence = HeldPair(electron("recurrence-one"), electron("recurrence-two"))
    displaced = HeldPair(electron("leaving-one"), electron("leaving-two"))
    atoms = (left, centre, right, entering, leaving)
    source = SubstitutionState(
        HeldLabel("substitution-state", "aromatic-source"), atoms,
        (HeldBond(left, centre, donor), HeldBond(centre, right, recurrence), HeldBond(centre, leaving, displaced)), (),
    )
    intermediate = SubstitutionState(
        HeldLabel("substitution-state", "addition-intermediate"), atoms,
        (HeldBond(centre, right, recurrence), HeldBond(centre, leaving, displaced), HeldBond(centre, entering, donor)), (),
    )
    terminal = SubstitutionState(
        HeldLabel("substitution-state", "restored-terminal"), atoms,
        (HeldBond(left, centre, displaced), HeldBond(centre, right, recurrence), HeldBond(centre, entering, donor)), (),
    )
    carrier = ElectrophilicExchangeCarrier(
        HeldLabel("registered-reaction", "acceptor-exchange"), left, centre, right, entering, leaving,
        donor, recurrence, displaced, EMPTY_ONE, source,
    )
    direct = ElectrophilicTransition(PositiveCount(1), source, terminal, HeldLabel("acceptor-substitution-action", "exchange-and-restore-in-one-transition"))
    add = ElectrophilicTransition(PositiveCount(1), source, intermediate, HeldLabel("acceptor-substitution-action", "transfer-aromatic-pair-to-entering-support"))
    restore = ElectrophilicTransition(PositiveCount(2), intermediate, terminal, HeldLabel("acceptor-substitution-action", "relinquish-leaving-pair-to-restore-recurrence"))
    return carrier, forced_electrophilic_exchange_path(carrier, (source, terminal), (direct,)), forced_electrophilic_exchange_path(carrier, (source, intermediate, terminal), (add, restore))


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    carrier, direct, staged = _example_paths()
    source, intermediate, terminal = staged.ordered_states
    donor_edge = frozenset((carrier.aromatic_left, carrier.centre))
    entering_edge = frozenset((carrier.centre, carrier.entering_acceptor))
    leaving_edge = frozenset((carrier.centre, carrier.leaving_carrier))
    cleavage_first_rejected = False
    try:
        impossible = SubstitutionState(
            HeldLabel("substitution-state", "cleavage-first"), source.atoms,
            source.retained_bonds + (HeldBond(carrier.aromatic_left, carrier.centre, carrier.leaving_pair),), (),
        )
        _state_role(carrier, impossible)
    except InadmissibleExactValue:
        cleavage_first_rejected = True
    successor = extend_aromatic_carrier(
        staged, occurrence("aromatic-successor"), HeldPair(electron("successor-one"), electron("successor-two"))
    )
    return (
        ("complete-carrier", "Every atom and held electron occurrence survives both generated paths.", source.atoms == terminal.atoms and source.electron_occurrences == intermediate.electron_occurrences == terminal.electron_occurrences),
        ("acceptor-transfer", "The structural EmptyOne entering carrier accepts the complete aromatic donor pair.", carrier.acceptor_slot is EMPTY_ONE and _bond_map(terminal)[entering_edge] == carrier.donor_pair),
        ("leaving-relinquishment", "The displaced pair leaves its source bond and restores the opened aromatic incidence.", leaving_edge not in _bond_map(terminal) and _bond_map(terminal)[donor_edge] == carrier.leaving_pair),
        ("recurrence-restored", "The terminal retains both aromatic incidences and the unchanged recurrence pair.", donor_edge in _bond_map(terminal) and _bond_map(terminal)[frozenset((carrier.centre, carrier.aromatic_right))] == carrier.recurrence_pair),
        ("complete-path-family", "The generated family retains one-transition and addition-then-restoration paths.", direct.transition_count == PositiveCount(1) and staged.transition_count == PositiveCount(2)),
        ("cleavage-first-control", "Cleavage-first cannot duplicate the still occupied aromatic incidence.", cleavage_first_rejected),
        ("successor", "Appending one retained aromatic occurrence preserves the complete prior path without another rule.", successor),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-aromatic-source-ordered-carrier__structural-EmptyOne-entering-acceptor-slot__"
    "complete-aromatic-donor-pair-transfer__entering-bond-formed-leaving-bond-cleaved__"
    "complete-concerted-and-addition-then-restoration-path-family__leaving-pair-restores-aromatic-incidence__"
    "value-free-aromatic-structure-and-mechanism-target-seal__fresh-aromatic-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ElectrophilicExchangeCarrier", "ElectrophilicTransition",
    "ExactElectrophilicExchange", "OPERATIONAL_WITNESSES", "extend_aromatic_carrier", "forced_electrophilic_exchange_path",
)
