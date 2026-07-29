"""Fold-native initiation, propagation and termination law for ORG-013.

No conventional radical symbol, rate equation, random collision, numerical
zero, species rule or measured chain length is a premise.  Two exact held
support labels are present before initiation, remain through every propagation
step and close together at termination.  Structural absence is EmptyOne.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.chemistry.addition_reaction_law_v1 import AdditionBond, atom, support
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def radical_support(label: str) -> HeldLabel:
    return HeldLabel("radical-held-support", label)


@dataclass(frozen=True)
class ActiveRadical:
    held_support: HeldLabel
    owner: HeldLabel

    def __post_init__(self) -> None:
        if self.held_support.family != "radical-held-support" or self.owner.family != "addition-atom-occurrence":
            raise InadmissibleExactValue("active radical requires one held support at one retained atom")


@dataclass(frozen=True)
class ClosedRadicalPair:
    first: HeldLabel
    second: HeldLabel
    endpoints: frozenset[HeldLabel]

    def __post_init__(self) -> None:
        if self.first == self.second or any(row.family != "radical-held-support" for row in (self.first, self.second)):
            raise InadmissibleExactValue("closed radical pair requires two distinct held supports")
        if len(self.endpoints) != 2 or any(row.family != "addition-atom-occurrence" for row in self.endpoints):
            raise InadmissibleExactValue("closed radical pair requires two retained endpoints")


@dataclass(frozen=True)
class RadicalNetworkState:
    identity: HeldLabel
    atoms: tuple[HeldLabel, ...]
    bonds: tuple[AdditionBond, ...]
    active: tuple[ActiveRadical, ...] | EmptyOne
    closed: tuple[ClosedRadicalPair, ...] | EmptyOne

    def __post_init__(self) -> None:
        if self.identity.family != "radical-network-state" or not self.atoms or len(self.atoms) != len(set(self.atoms)):
            raise InadmissibleExactValue("radical network requires one exact state and distinct retained atoms")
        allowed = set(self.atoms)
        if any(row.family != "addition-atom-occurrence" for row in self.atoms):
            raise InadmissibleExactValue("radical network contains an invalid atom occurrence")
        if any(set(row.endpoints) - allowed for row in self.bonds):
            raise InadmissibleExactValue("radical-network bond leaves the complete carrier")
        active_rows = () if isinstance(self.active, EmptyOne) else self.active
        closed_rows = () if isinstance(self.closed, EmptyOne) else self.closed
        if not isinstance(self.active, EmptyOne) and not active_rows:
            raise InadmissibleExactValue("structural active-site absence must be EmptyOne")
        if not isinstance(self.closed, EmptyOne) and not closed_rows:
            raise InadmissibleExactValue("structural closed-pair absence must be EmptyOne")
        if any(row.owner not in allowed for row in active_rows) or any(set(row.endpoints) - allowed for row in closed_rows):
            raise InadmissibleExactValue("radical support leaves the complete carrier")
        labels = tuple(row.held_support for row in active_rows) + tuple(
            label for row in closed_rows for label in (row.first, row.second)
        )
        if len(labels) != len(set(labels)):
            raise InadmissibleExactValue("each radical held support must occur exactly once")

    @property
    def radical_supports(self) -> frozenset[HeldLabel]:
        active_rows = () if isinstance(self.active, EmptyOne) else self.active
        closed_rows = () if isinstance(self.closed, EmptyOne) else self.closed
        return frozenset(
            tuple(row.held_support for row in active_rows)
            + tuple(label for row in closed_rows for label in (row.first, row.second))
        )


@dataclass(frozen=True)
class RadicalStep:
    kind: HeldLabel
    source: RadicalNetworkState
    terminal: RadicalNetworkState
    retained_radical_supports: frozenset[HeldLabel]


def forced_initiation(source: RadicalNetworkState, terminal: RadicalNetworkState) -> RadicalStep:
    if source.atoms != terminal.atoms or source.bonds != terminal.bonds or source.radical_supports != terminal.radical_supports:
        raise InadmissibleExactValue("initiation must retain every atom, bond and radical support")
    if not isinstance(source.active, EmptyOne) or isinstance(source.closed, EmptyOne) or len(source.closed) != 1:
        raise InadmissibleExactValue("initiation source requires one closed pair and structural active absence")
    if isinstance(terminal.active, EmptyOne) or len(terminal.active) != 2 or not isinstance(terminal.closed, EmptyOne):
        raise InadmissibleExactValue("initiation terminal requires two active supports and structural pair absence")
    pair = source.closed[0]
    active = {row.held_support: row.owner for row in terminal.active}
    if set(active) != {pair.first, pair.second} or frozenset(active.values()) != pair.endpoints:
        raise InadmissibleExactValue("initiation must open the retained pair at its exact endpoints")
    return RadicalStep(HeldLabel("radical-step", "initiation"), source, terminal, source.radical_supports)


def forced_propagation(source: RadicalNetworkState, terminal: RadicalNetworkState) -> RadicalStep:
    if source.atoms != terminal.atoms or source.radical_supports != terminal.radical_supports:
        raise InadmissibleExactValue("propagation must retain every atom and radical support")
    if isinstance(source.active, EmptyOne) or isinstance(terminal.active, EmptyOne):
        raise InadmissibleExactValue("propagation requires retained active support")
    if not isinstance(source.closed, EmptyOne) or not isinstance(terminal.closed, EmptyOne):
        raise InadmissibleExactValue("propagation cannot silently close the active support")
    source_active = {row.held_support: row.owner for row in source.active}
    terminal_active = {row.held_support: row.owner for row in terminal.active}
    moved_active = tuple(key for key in source_active if source_active[key] != terminal_active.get(key))
    if set(source_active) != set(terminal_active) or len(moved_active) != 1:
        raise InadmissibleExactValue("one propagation step moves exactly one retained active support")
    source_bonds = {row.held_support: row for row in source.bonds}
    terminal_bonds = {row.held_support: row for row in terminal.bonds}
    moved_bonds = tuple(key for key in source_bonds if source_bonds[key] != terminal_bonds.get(key))
    if set(source_bonds) != set(terminal_bonds) or len(moved_bonds) != 1:
        raise InadmissibleExactValue("one propagation step relocates exactly one retained bond layer")
    active = moved_active[0]
    layer = moved_bonds[0]
    old_owner = source_active[active]
    new_owner = terminal_active[active]
    source_edge = source_bonds[layer].endpoints
    terminal_edge = terminal_bonds[layer].endpoints
    if new_owner not in source_edge or old_owner not in terminal_edge or len(source_edge & terminal_edge) != 1:
        raise InadmissibleExactValue("propagation must open one monomer layer and join its other endpoint to the prior owner")
    return RadicalStep(HeldLabel("radical-step", "propagation"), source, terminal, source.radical_supports)


def forced_termination(source: RadicalNetworkState, terminal: RadicalNetworkState) -> RadicalStep:
    if source.atoms != terminal.atoms or source.bonds != terminal.bonds or source.radical_supports != terminal.radical_supports:
        raise InadmissibleExactValue("termination must retain every atom, bond and radical support")
    if isinstance(source.active, EmptyOne) or len(source.active) != 2 or not isinstance(source.closed, EmptyOne):
        raise InadmissibleExactValue("termination source requires exactly two active supports")
    if not isinstance(terminal.active, EmptyOne) or isinstance(terminal.closed, EmptyOne) or len(terminal.closed) != 1:
        raise InadmissibleExactValue("termination must close active support to structural EmptyOne")
    pair = terminal.closed[0]
    active = {row.held_support: row.owner for row in source.active}
    if set(active) != {pair.first, pair.second} or frozenset(active.values()) != pair.endpoints:
        raise InadmissibleExactValue("termination must pair the two exact active supports at their owners")
    return RadicalStep(HeldLabel("radical-step", "termination"), source, terminal, source.radical_supports)


@dataclass(frozen=True)
class ExactRadicalNetwork:
    initiation: RadicalStep
    propagation: tuple[RadicalStep, ...]
    propagation_count: PositiveCount
    termination: RadicalStep


def forced_radical_network(initiation: RadicalStep, propagation: tuple[RadicalStep, ...], termination: RadicalStep) -> ExactRadicalNetwork:
    if initiation.kind.label != "initiation" or termination.kind.label != "termination" or not propagation:
        raise InadmissibleExactValue("complete radical network requires initiation, positive propagation and termination")
    steps = (initiation, *propagation, termination)
    if any(step.terminal != steps[index + 1].source for index, step in enumerate(steps[:-1])):
        raise InadmissibleExactValue("radical network trace must be exact and contiguous")
    if any(step.kind.label != "propagation" for step in propagation):
        raise InadmissibleExactValue("intermediate radical-network steps must be propagation")
    if any(step.retained_radical_supports != initiation.retained_radical_supports for step in steps):
        raise InadmissibleExactValue("every step must retain the same radical-support identities")
    return ExactRadicalNetwork(initiation, propagation, PositiveCount(len(propagation)), termination)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-BOND-ORDER-001", "SFT-CHEM-MOL-MOLECULE-001", "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-RXN-MECHANISM-001", "SFT-CHEM-RXN-INTERMEDIATE-001", "SFT-CHEM-ORGANIC-REACTION-FAMILY-001",
    "SFT-CHEM-ADDITION-REACTION-FAMILY-009", "SFT-CHEM-PERICYCLIC-REACTION-FAMILY-012",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "selected-chain-fragment-or-erased-coproduct", "A fragment cannot close a radical network.", "complete-retained-network-carrier", "Every atom and bond carrier remains explicit through every step."),
    dimension("support", "created-destroyed-or-dot-only-radical", "A typographic dot does not retain support identity.", "two-exact-held-radical-supports", "Two held labels remain identifiable before, during and after the chain."),
    dimension("initiation", "free-radical-assumed-or-randomly-created", "An assumed active center is not generated.", "closed-pair-opens-to-two-retained-active-sites", "The exact pair opens at its retained endpoints."),
    dimension("propagation", "mass-increase-story-or-measured-chain-selector", "A name or observed chain length cannot select the step.", "one-active-support-and-one-bond-layer-relocate", "One retained active label and one retained monomer layer move per step."),
    dimension("recurrence", "single-step-or-unbounded-assertion", "One example does not force the chain family.", "positive-finite-contiguous-propagation-family", "Every positive finite repetition uses the same exact local rule."),
    dimension("termination", "active-support-erased-or-numerical-zero", "Erasure or numerical zero destroys reversibility.", "two-active-supports-close-to-EmptyOne", "Both exact labels close together and active-site absence is structural EmptyOne."),
    dimension("observation", "external-chain-vector-open-before-seal", "Opened outcomes could choose the law.", "value-free-initiation-propagation-termination-seal", "The complete trace law and target identities seal before outcomes."),
    dimension("extension", "species-exception-or-recomputed-prefix", "A species exception is not a general chain law.", "fresh-unchanged-carrier-successor-no-extra-rule", "A fresh unchanged carrier preserves every prior trace decision."),
)


def _state(label, atoms, bonds, active, closed):
    return RadicalNetworkState(HeldLabel("radical-network-state", label), atoms, bonds, active, closed)


def _example() -> ExactRadicalNetwork:
    i, j, m1, m2, n1, n2 = map(atom, ("rad-i", "rad-j", "rad-m1", "rad-m2", "rad-n1", "rad-n2"))
    base_m, layer_m, base_n, layer_n = map(support, ("rad-base-m", "rad-layer-m", "rad-base-n", "rad-layer-n"))
    first, second = radical_support("rad-first"), radical_support("rad-second")
    atoms = (i, j, m1, m2, n1, n2)
    bonds0 = (AdditionBond(m1, m2, base_m), AdditionBond(m1, m2, layer_m), AdditionBond(n1, n2, base_n), AdditionBond(n1, n2, layer_n))
    s0 = _state("r0", atoms, bonds0, EMPTY_ONE, (ClosedRadicalPair(first, second, frozenset((i, j))),))
    s1 = _state("r1", atoms, bonds0, (ActiveRadical(first, i), ActiveRadical(second, j)), EMPTY_ONE)
    bonds1 = (AdditionBond(m1, m2, base_m), AdditionBond(i, m1, layer_m), AdditionBond(n1, n2, base_n), AdditionBond(n1, n2, layer_n))
    s2 = _state("r2", atoms, bonds1, (ActiveRadical(first, m2), ActiveRadical(second, j)), EMPTY_ONE)
    bonds2 = (AdditionBond(m1, m2, base_m), AdditionBond(i, m1, layer_m), AdditionBond(n1, n2, base_n), AdditionBond(m2, n1, layer_n))
    s3 = _state("r3", atoms, bonds2, (ActiveRadical(first, n2), ActiveRadical(second, j)), EMPTY_ONE)
    s4 = _state("r4", atoms, bonds2, EMPTY_ONE, (ClosedRadicalPair(first, second, frozenset((n2, j))),))
    return forced_radical_network(
        forced_initiation(s0, s1),
        (forced_propagation(s1, s2), forced_propagation(s2, s3)),
        forced_termination(s3, s4),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    result = _example()
    omitted = False
    discontinuous = False
    try:
        forced_radical_network(result.initiation, (), result.termination)
    except InadmissibleExactValue:
        omitted = True
    try:
        forced_radical_network(result.initiation, tuple(reversed(result.propagation)), result.termination)
    except InadmissibleExactValue:
        discontinuous = True
    labels = result.initiation.retained_radical_supports
    return (
        ("complete-carrier", "Every state retains the complete atom carrier.", all(step.source.atoms == step.terminal.atoms for step in (result.initiation, *result.propagation, result.termination))),
        ("support-conservation", "The same two radical labels remain through every step.", len(labels) == 2 and all(step.retained_radical_supports == labels for step in (result.initiation, *result.propagation, result.termination))),
        ("initiation", "One closed pair opens to two retained active sites.", result.initiation.kind.label == "initiation"),
        ("propagation", "Each propagation relocates one active support and one bond layer.", all(step.kind.label == "propagation" for step in result.propagation)),
        ("positive-recurrence", "Two steps instantiate the positive finite recurrence.", result.propagation_count == PositiveCount(2)),
        ("termination", "Two active supports close together.", result.termination.kind.label == "termination"),
        ("EmptyOne", "Closed endpoints contain structural active-site absence.", isinstance(result.termination.terminal.active, EmptyOne)),
        ("contiguous", "Every terminal is the next exact source.", result.initiation.terminal == result.propagation[0].source and result.propagation[-1].terminal == result.termination.source),
        ("omission-control", "A network without positive propagation halts.", omitted),
        ("order-control", "A reordered noncontiguous trace halts.", discontinuous),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-retained-network-carrier__two-exact-held-radical-supports__"
    "closed-pair-opens-to-two-retained-active-sites__one-active-support-and-one-bond-layer-relocate__"
    "positive-finite-contiguous-propagation-family__two-active-supports-close-to-EmptyOne__"
    "value-free-initiation-propagation-termination-seal__fresh-unchanged-carrier-successor-no-extra-rule"
)

__all__ = (
    "ActiveRadical", "ClosedRadicalPair", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactRadicalNetwork",
    "OPERATIONAL_WITNESSES", "RadicalNetworkState", "RadicalStep", "forced_initiation", "forced_propagation",
    "forced_radical_network", "forced_termination", "radical_support",
)
