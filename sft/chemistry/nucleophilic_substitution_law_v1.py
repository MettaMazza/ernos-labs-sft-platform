"""Fold-native entering/leaving carrier substitution law for Chemistry ORG-007.

The candidate generator contains no named conventional mechanism, measured
substrate, product, rate law, energy surface or external target.  Conventional
nucleophilic/SN correspondence is evaluated only after the derivation seal.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def occurrence(label: str) -> HeldLabel:
    return HeldLabel("substitution-atom-occurrence", label)


def electron(label: str) -> HeldLabel:
    return HeldLabel("held-electron-occurrence", label)


@dataclass(frozen=True)
class HeldPair:
    first: HeldLabel
    second: HeldLabel

    def __post_init__(self) -> None:
        if (
            self.first.family != "held-electron-occurrence"
            or self.second.family != "held-electron-occurrence"
            or self.first == self.second
        ):
            raise InadmissibleExactValue("a joining pair requires two distinct held electron occurrences")

    @property
    def occurrences(self) -> frozenset[HeldLabel]:
        return frozenset((self.first, self.second))


@dataclass(frozen=True)
class HeldBond:
    left: HeldLabel
    right: HeldLabel
    pair: HeldPair

    def __post_init__(self) -> None:
        if (
            self.left.family != "substitution-atom-occurrence"
            or self.right.family != "substitution-atom-occurrence"
            or self.left == self.right
        ):
            raise InadmissibleExactValue("a bond joins two distinct retained atom occurrences")

    @property
    def endpoints(self) -> frozenset[HeldLabel]:
        return frozenset((self.left, self.right))


@dataclass(frozen=True)
class FreeHeldPair:
    owner: HeldLabel
    pair: HeldPair

    def __post_init__(self) -> None:
        if self.owner.family != "substitution-atom-occurrence":
            raise InadmissibleExactValue("a free pair requires one retained carrier occurrence")


@dataclass(frozen=True)
class SubstitutionState:
    state_identity: HeldLabel
    atoms: tuple[HeldLabel, ...]
    retained_bonds: tuple[HeldBond, ...]
    free_pairs: tuple[FreeHeldPair, ...]

    def __post_init__(self) -> None:
        if self.state_identity.family != "substitution-state":
            raise InadmissibleExactValue("a substitution state requires one held state identity")
        if len(self.atoms) < 4 or len(set(self.atoms)) != len(self.atoms):
            raise InadmissibleExactValue("the complete substitution carrier requires distinct atom occurrences")
        allowed = set(self.atoms)
        if any(atom.family != "substitution-atom-occurrence" for atom in self.atoms):
            raise InadmissibleExactValue("the substitution carrier contains an invalid atom occurrence")
        if any(set(bond.endpoints) - allowed for bond in self.retained_bonds):
            raise InadmissibleExactValue("a retained bond leaves the declared carrier")
        if any(row.owner not in allowed for row in self.free_pairs):
            raise InadmissibleExactValue("a free pair leaves the declared carrier")
        edge_keys = tuple(frozenset(bond.endpoints) for bond in self.retained_bonds)
        if len(set(edge_keys)) != len(edge_keys):
            raise InadmissibleExactValue("a bond occurrence cannot be duplicated")
        pair_words = tuple(bond.pair.occurrences for bond in self.retained_bonds) + tuple(
            row.pair.occurrences for row in self.free_pairs
        )
        flattened = tuple(item for pair in pair_words for item in pair)
        if len(flattened) != len(set(flattened)):
            raise InadmissibleExactValue("each held electron occurrence must occupy exactly one support")

    @property
    def electron_occurrences(self) -> frozenset[HeldLabel]:
        return frozenset(
            item
            for pair in (
                tuple(bond.pair.occurrences for bond in self.retained_bonds)
                + tuple(row.pair.occurrences for row in self.free_pairs)
            )
            for item in pair
        )


@dataclass(frozen=True)
class SubstitutionCarrier:
    reaction_identity: HeldLabel
    centre: HeldLabel
    retained_neighbour: HeldLabel
    entering_carrier: HeldLabel
    leaving_carrier: HeldLabel
    entering_pair: HeldPair
    leaving_pair: HeldPair
    source: SubstitutionState

    def __post_init__(self) -> None:
        if self.reaction_identity.family != "registered-reaction":
            raise InadmissibleExactValue("substitution requires one registered reaction carrier")
        roles = (self.centre, self.retained_neighbour, self.entering_carrier, self.leaving_carrier)
        if len(set(roles)) != len(roles) or any(row not in self.source.atoms for row in roles):
            raise InadmissibleExactValue("substitution roles require four distinct retained occurrences")
        source_edges = {bond.endpoints: bond for bond in self.source.retained_bonds}
        retained_key = frozenset((self.centre, self.retained_neighbour))
        leaving_key = frozenset((self.centre, self.leaving_carrier))
        if retained_key not in source_edges or leaving_key not in source_edges:
            raise InadmissibleExactValue("source must contain the retained and displaced bonds")
        extra_edges = set(source_edges) - {retained_key, leaving_key}
        if any(self.centre in edge or self.entering_carrier in edge or self.leaving_carrier in edge for edge in extra_edges):
            raise InadmissibleExactValue("source extensions cannot change the single exchange slot or free carriers")
        if source_edges[leaving_key].pair != self.leaving_pair:
            raise InadmissibleExactValue("the displaced bond must retain its complete held pair")
        if self.source.free_pairs != (FreeHeldPair(self.entering_carrier, self.entering_pair),):
            raise InadmissibleExactValue("the entering carrier must hold exactly the entering pair")


@dataclass(frozen=True)
class SubstitutionTransition:
    occurrence: PositiveCount
    entry: SubstitutionState
    exit: SubstitutionState
    action: HeldLabel

    def __post_init__(self) -> None:
        if self.action.family != "substitution-action" or self.action.label not in {
            "cleave-displaced-support", "form-entering-support", "exchange-support-in-one-transition"
        }:
            raise InadmissibleExactValue("transition action is outside the generated substitution alphabet")
        if self.entry.atoms != self.exit.atoms:
            raise InadmissibleExactValue("every atom occurrence must survive a substitution transition")
        if self.entry.electron_occurrences != self.exit.electron_occurrences:
            raise InadmissibleExactValue("every held electron occurrence must survive a substitution transition")


@dataclass(frozen=True)
class ExactSubstitution:
    carrier: SubstitutionCarrier
    ordered_states: tuple[SubstitutionState, ...]
    ordered_transitions: tuple[SubstitutionTransition, ...]
    terminal: SubstitutionState
    path_class: HeldLabel
    transition_count: PositiveCount


def _bond_map(state: SubstitutionState) -> dict[frozenset[HeldLabel], HeldPair]:
    return {bond.endpoints: bond.pair for bond in state.retained_bonds}


def _free_map(state: SubstitutionState) -> dict[HeldLabel, HeldPair]:
    return {row.owner: row.pair for row in state.free_pairs}


def _validate_state_role(carrier: SubstitutionCarrier, state: SubstitutionState) -> str:
    bonds = _bond_map(state)
    free = _free_map(state)
    retained_key = frozenset((carrier.centre, carrier.retained_neighbour))
    leaving_key = frozenset((carrier.centre, carrier.leaving_carrier))
    entering_key = frozenset((carrier.centre, carrier.entering_carrier))
    if retained_key not in bonds:
        raise InadmissibleExactValue("the unchanged substrate bond must remain retained")
    if leaving_key in bonds and entering_key in bonds:
        raise InadmissibleExactValue("the single exchange slot cannot carry entering and leaving bonds together")
    if leaving_key in bonds:
        if bonds[leaving_key] != carrier.leaving_pair or free.get(carrier.entering_carrier) != carrier.entering_pair:
            raise InadmissibleExactValue("source support allocation changed")
        return "source"
    if entering_key in bonds:
        if bonds[entering_key] != carrier.entering_pair or free.get(carrier.leaving_carrier) != carrier.leaving_pair:
            raise InadmissibleExactValue("terminal support allocation changed")
        return "terminal"
    if free.get(carrier.entering_carrier) == carrier.entering_pair and free.get(carrier.leaving_carrier) == carrier.leaving_pair:
        return "cleaved-intermediate"
    raise InadmissibleExactValue("state is not generated by the exact exchange support")


def forced_substitution_path(
    carrier: SubstitutionCarrier,
    ordered_states: tuple[SubstitutionState, ...],
    ordered_transitions: tuple[SubstitutionTransition, ...],
) -> ExactSubstitution:
    if len(ordered_states) not in (2, 3) or len(ordered_transitions) != len(ordered_states) - 1:
        raise InadmissibleExactValue("substitution admits exactly one-transition or two-transition paths")
    if ordered_states[0] != carrier.source:
        raise InadmissibleExactValue("path must begin at the complete registered source")
    if tuple(row.occurrence.value for row in ordered_transitions) != tuple(range(1, len(ordered_transitions) + 1)):
        raise InadmissibleExactValue("transition occurrences must remain complete and gap-free")
    roles = tuple(_validate_state_role(carrier, state) for state in ordered_states)
    for left, edge, right in zip(ordered_states, ordered_transitions, ordered_states[1:]):
        if edge.entry != left or edge.exit != right:
            raise InadmissibleExactValue("every transition must meet its retained adjacent states")
    if roles == ("source", "terminal"):
        expected_actions = ("exchange-support-in-one-transition",)
        path_label = "one-transition-exchange"
    elif roles == ("source", "cleaved-intermediate", "terminal"):
        expected_actions = ("cleave-displaced-support", "form-entering-support")
        path_label = "cleavage-then-formation"
    else:
        raise InadmissibleExactValue("path order is outside the complete generated substitution family")
    if tuple(edge.action.label for edge in ordered_transitions) != expected_actions:
        raise InadmissibleExactValue("transition labels do not reconstruct the generated state changes")
    terminal_bonds = _bond_map(ordered_states[-1])
    source_bonds = _bond_map(carrier.source)
    leaving_key = frozenset((carrier.centre, carrier.leaving_carrier))
    entering_key = frozenset((carrier.centre, carrier.entering_carrier))
    expected_terminal = (set(source_bonds) - {leaving_key}) | {entering_key}
    if set(terminal_bonds) != expected_terminal:
        raise InadmissibleExactValue("terminal state must replace only the single exchange bond")
    return ExactSubstitution(
        carrier, ordered_states, ordered_transitions, ordered_states[-1],
        HeldLabel("substitution-path-class", path_label), PositiveCount(len(ordered_transitions)),
    )


def extend_retained_substrate(
    carrier: SubstitutionCarrier,
    result: ExactSubstitution,
    new_atom: HeldLabel,
    new_pair: HeldPair,
) -> bool:
    if new_atom in carrier.source.atoms or new_atom.family != "substitution-atom-occurrence":
        raise InadmissibleExactValue("successor requires one fresh retained substrate occurrence")
    new_atoms = carrier.source.atoms + (new_atom,)
    extended_states = tuple(
        SubstitutionState(
            state.state_identity, new_atoms,
            state.retained_bonds + (HeldBond(carrier.retained_neighbour, new_atom, new_pair),),
            state.free_pairs,
        )
        for state in result.ordered_states
    )
    extended_carrier = SubstitutionCarrier(
        carrier.reaction_identity, carrier.centre, carrier.retained_neighbour,
        carrier.entering_carrier, carrier.leaving_carrier, carrier.entering_pair,
        carrier.leaving_pair, extended_states[0],
    )
    extended_edges = tuple(
        SubstitutionTransition(edge.occurrence, extended_states[index], extended_states[index + 1], edge.action)
        for index, edge in enumerate(result.ordered_transitions)
    )
    extended = forced_substitution_path(extended_carrier, extended_states, extended_edges)
    return (
        extended.path_class == result.path_class
        and extended.transition_count == result.transition_count
        and all(
            state.retained_bonds[:-1] == prior.retained_bonds
            for state, prior in zip(extended.ordered_states, result.ordered_states)
        )
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
    "SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007", "SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "selected-product-label-or-disconnected-fragments", "A named answer cannot reconstruct one complete reaction carrier.", "complete-source-ordered-reaction-carrier", "Centre, retained neighbour, entering carrier and leaving carrier remain distinct occurrences in one source-ordered record."),
    dimension("source", "reactant-or-bond-support-omitted", "Omission prevents exact reconstruction of what changes.", "complete-source-bonds-and-free-entering-pair", "The source contains the retained bond, displaced bond and free entering pair exactly."),
    dimension("support", "electrons-created-destroyed-or-collapsed-to-charge-number", "A scalar charge or incomplete pair loses the transferred occurrences.", "every-held-pair-occurrence-conserved", "Both entering occurrences form the new bond and both displaced occurrences remain with the leaving carrier."),
    dimension("change", "endpoint-only-product-or-extra-bond-change", "An endpoint or extra edit does not prove the minimal substitution map.", "one-bond-cleaved-and-one-bond-formed", "Only the centre-leaving incidence is replaced by the centre-entering incidence."),
    dimension("path", "named-mechanism-rate-law-or-unordered-snapshots", "A conventional name or imported kinetic law can select a path.", "complete-one-transition-and-cleavage-first-path-family", "The single exchange slot forces either one exchange transition or cleavage followed by formation."),
    dimension("record", "intermediate-adverse-or-mechanism-row-omitted", "Selected records falsely collapse the path family.", "every-state-edge-status-and-source-record-retained", "Every generated state, edge, source response, favorable, adverse, absent and unresolved record remains auditable."),
    dimension("observation", "substrate-product-mechanism-readable-before-seal", "External structures or terminology could select the survivor.", "value-free-structure-and-mechanism-target-seal", "Law and complete target identities seal before any newly registered structure or mechanism outcome opens."),
    dimension("extension", "molecule-specific-exception-or-recomputed-prefix", "A special substrate rule is not depth-independent.", "fresh-retained-substrate-successor-no-extra-rule", "Adding one fresh retained substrate occurrence preserves every prior state, edge and support allocation."),
)


def _states_and_paths() -> tuple[SubstitutionCarrier, ExactSubstitution, ExactSubstitution]:
    centre, retained, entering, leaving = map(occurrence, ("centre", "retained", "entering", "leaving"))
    retained_pair = HeldPair(electron("retained-one"), electron("retained-two"))
    entering_pair = HeldPair(electron("entering-one"), electron("entering-two"))
    leaving_pair = HeldPair(electron("leaving-one"), electron("leaving-two"))
    atoms = (centre, retained, entering, leaving)
    source = SubstitutionState(
        HeldLabel("substitution-state", "source"), atoms,
        (HeldBond(centre, retained, retained_pair), HeldBond(centre, leaving, leaving_pair)),
        (FreeHeldPair(entering, entering_pair),),
    )
    intermediate = SubstitutionState(
        HeldLabel("substitution-state", "cleaved-intermediate"), atoms,
        (HeldBond(centre, retained, retained_pair),),
        (FreeHeldPair(entering, entering_pair), FreeHeldPair(leaving, leaving_pair)),
    )
    terminal = SubstitutionState(
        HeldLabel("substitution-state", "terminal"), atoms,
        (HeldBond(centre, retained, retained_pair), HeldBond(centre, entering, entering_pair)),
        (FreeHeldPair(leaving, leaving_pair),),
    )
    carrier = SubstitutionCarrier(
        HeldLabel("registered-reaction", "exchange-carrier"), centre, retained, entering, leaving,
        entering_pair, leaving_pair, source,
    )
    concerted_edge = SubstitutionTransition(
        PositiveCount(1), source, terminal, HeldLabel("substitution-action", "exchange-support-in-one-transition")
    )
    cleavage_edge = SubstitutionTransition(
        PositiveCount(1), source, intermediate, HeldLabel("substitution-action", "cleave-displaced-support")
    )
    formation_edge = SubstitutionTransition(
        PositiveCount(2), intermediate, terminal, HeldLabel("substitution-action", "form-entering-support")
    )
    return (
        carrier,
        forced_substitution_path(carrier, (source, terminal), (concerted_edge,)),
        forced_substitution_path(carrier, (source, intermediate, terminal), (cleavage_edge, formation_edge)),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    carrier, one_step, two_step = _states_and_paths()
    terminal = one_step.terminal
    entering_key = frozenset((carrier.centre, carrier.entering_carrier))
    formation_first_rejected = incomplete_pair_rejected = False
    try:
        source = carrier.source
        impossible = SubstitutionState(
            HeldLabel("substitution-state", "doubly-occupied-slot"), source.atoms,
            source.retained_bonds + (HeldBond(carrier.centre, carrier.entering_carrier, carrier.entering_pair),), (),
        )
        _validate_state_role(carrier, impossible)
    except InadmissibleExactValue:
        formation_first_rejected = True
    try:
        HeldPair(electron("same"), electron("same"))
    except InadmissibleExactValue:
        incomplete_pair_rejected = True
    successor = extend_retained_substrate(
        carrier, two_step, occurrence("successor"), HeldPair(electron("successor-one"), electron("successor-two"))
    )
    return (
        ("complete-carrier", "Every source atom and held electron occurrence survives both complete paths.", one_step.terminal.atoms == carrier.source.atoms and one_step.terminal.electron_occurrences == carrier.source.electron_occurrences),
        ("minimal-bond-change", "Exactly the displaced incidence closes and the entering incidence opens.", entering_key in _bond_map(terminal) and frozenset((carrier.centre, carrier.leaving_carrier)) not in _bond_map(terminal)),
        ("pair-retention", "The entering pair forms the terminal bond while the displaced pair remains free on the leaving carrier.", _bond_map(terminal)[entering_key] == carrier.entering_pair and _free_map(terminal)[carrier.leaving_carrier] == carrier.leaving_pair),
        ("complete-path-family", "The generated family contains one-transition exchange and cleavage-then-formation paths.", one_step.transition_count == PositiveCount(1) and two_step.transition_count == PositiveCount(2)),
        ("formation-first-control", "Formation before cleavage halts because it occupies the one exchange slot twice.", formation_first_rejected),
        ("pair-collapse-control", "A duplicated electron label cannot masquerade as a complete held pair.", incomplete_pair_rejected),
        ("successor", "Adding one retained substrate occurrence preserves the complete prior path without an extra rule.", successor),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-source-ordered-reaction-carrier__complete-source-bonds-and-free-entering-pair__"
    "every-held-pair-occurrence-conserved__one-bond-cleaved-and-one-bond-formed__"
    "complete-one-transition-and-cleavage-first-path-family__every-state-edge-status-and-source-record-retained__"
    "value-free-structure-and-mechanism-target-seal__fresh-retained-substrate-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactSubstitution", "FreeHeldPair", "HeldBond", "HeldPair",
    "OPERATIONAL_WITNESSES", "SubstitutionCarrier", "SubstitutionState", "SubstitutionTransition", "electron",
    "extend_retained_substrate", "forced_substitution_path", "occurrence",
)
