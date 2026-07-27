"""Fold-native representation-equivalence law for Chemistry ORG-002."""
from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def atom(label: str) -> HeldLabel:
    return HeldLabel("representation-atom-occurrence", label)


def fibre(label: str) -> HeldLabel:
    if label not in ("fold-fibre-one", "fold-fibre-two"):
        raise InadmissibleExactValue("representation support admits exactly two Fold fibres")
    return HeldLabel("representation-support-fibre", label)


@dataclass(frozen=True)
class ExactMolecularEncoding:
    encoding: HeldLabel
    carrier: HeldLabel
    atoms: tuple[HeldLabel, ...]
    adjacency: tuple[tuple[HeldLabel, HeldLabel], ...]
    fibres: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if self.encoding.family != "molecular-representation":
            raise InadmissibleExactValue("representation identity is invalid")
        if self.carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("one molecular carrier must remain held")
        if len(self.atoms) < 3 or len(set(self.atoms)) != len(self.atoms):
            raise InadmissibleExactValue("representation atom support is incomplete")
        if len(self.adjacency) != len(self.fibres) or not self.adjacency:
            raise InadmissibleExactValue("every adjacency requires one held fibre")
        if any(left not in self.atoms or right not in self.atoms or left == right for left, right in self.adjacency):
            raise InadmissibleExactValue("representation adjacency is invalid")
        if len(set(self.adjacency)) != len(self.adjacency):
            raise InadmissibleExactValue("representation adjacency is duplicated")
        if any(row.family != "representation-support-fibre" for row in self.fibres):
            raise InadmissibleExactValue("representation fibre identity is invalid")


def complement_labels(labels: tuple[HeldLabel, ...]) -> tuple[HeldLabel, ...]:
    return tuple(
        fibre("fold-fibre-two") if row.label == "fold-fibre-one" else fibre("fold-fibre-one")
        for row in labels
    )


@dataclass(frozen=True)
class ExactEquivalentRepresentationPair:
    carrier: HeldLabel
    first: ExactMolecularEncoding
    second: ExactMolecularEncoding

    def __post_init__(self) -> None:
        if self.carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("representation class carrier is invalid")
        if self.first.carrier != self.carrier or self.second.carrier != self.carrier:
            raise InadmissibleExactValue("different carriers cannot be representation-equivalent")
        if self.first.encoding == self.second.encoding:
            raise InadmissibleExactValue("an alternative representation requires a distinct encoding identity")
        if self.first.atoms != self.second.atoms:
            raise InadmissibleExactValue("representation equivalence must retain every atom occurrence")
        if self.first.adjacency != self.second.adjacency:
            raise InadmissibleExactValue("representation equivalence must retain complete adjacency")
        if self.first.fibres == self.second.fibres:
            raise InadmissibleExactValue("identical fibre assignment is one encoding, not two alternatives")
        if complement_labels(self.first.fibres) != self.second.fibres:
            raise InadmissibleExactValue("alternative encoding must be the complete Fold-fibre complement")

    @property
    def representation_count(self) -> PositiveCount:
        return PositiveCount(2)


def encoding(
    encoding_label: str,
    carrier_label: str,
    atom_labels: tuple[str, ...],
    adjacency_indices: tuple[tuple[int, int], ...],
    fibre_labels: tuple[str, ...],
) -> ExactMolecularEncoding:
    atoms = tuple(atom(label) for label in atom_labels)
    if any(left < 1 or right < 1 for left, right in adjacency_indices):
        raise InadmissibleExactValue("representation adjacency indices must be positive")
    try:
        adjacency = tuple((atoms[left - 1], atoms[right - 1]) for left, right in adjacency_indices)
    except IndexError as exc:
        raise InadmissibleExactValue("representation adjacency index is outside its atom support") from exc
    return ExactMolecularEncoding(
        HeldLabel("molecular-representation", encoding_label),
        HeldLabel("molecular-carrier", carrier_label),
        atoms,
        adjacency,
        tuple(fibre(label) for label in fibre_labels),
    )


def equivalent_pair(
    carrier_label: str,
    first: ExactMolecularEncoding,
    second: ExactMolecularEncoding,
) -> ExactEquivalentRepresentationPair:
    return ExactEquivalentRepresentationPair(HeldLabel("molecular-carrier", carrier_label), first, second)


def append_shared_successor(
    pair: ExactEquivalentRepresentationPair,
    atom_label: str,
) -> ExactEquivalentRepresentationPair:
    fresh = atom(atom_label)
    if fresh in pair.first.atoms:
        raise InadmissibleExactValue("representation successor atom must be fresh")
    first_atoms = pair.first.atoms + (fresh,)
    second_atoms = pair.second.atoms + (fresh,)
    first_edge = (pair.first.atoms[-1], fresh)
    second_edge = (pair.second.atoms[-1], fresh)
    first_next = fibre("fold-fibre-two") if pair.first.fibres[-1].label == "fold-fibre-one" else fibre("fold-fibre-one")
    second_next = fibre("fold-fibre-two") if pair.second.fibres[-1].label == "fold-fibre-one" else fibre("fold-fibre-one")
    return ExactEquivalentRepresentationPair(
        pair.carrier,
        ExactMolecularEncoding(
            pair.first.encoding,
            pair.carrier,
            first_atoms,
            pair.first.adjacency + (first_edge,),
            pair.first.fibres + (first_next,),
        ),
        ExactMolecularEncoding(
            pair.second.encoding,
            pair.carrier,
            second_atoms,
            pair.second.adjacency + (second_edge,),
            pair.second.fibres + (second_next,),
        ),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOL-ISOMER-001",
    "SFT-CHEM-BOND-ORDER-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
    "SFT-CHEM-CONJUGATED-SUPPORT-001",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "different-molecular-carriers", "Different carriers are different molecular identities.", "one-retained-molecular-carrier", "Every encoding points to the same held molecular carrier."),
    dimension("atoms", "atom-occurrence-change", "Adding, deleting or replacing an occurrence changes the carrier description.", "complete-equal-atom-occurrence-support", "Every encoding retains the same ordered atom occurrences."),
    dimension("adjacency", "connectivity-change", "Changed adjacency is a distinct constitution, not an encoding alternative.", "complete-equal-adjacency-support", "Every encoding retains the same complete adjacency graph."),
    dimension("encodings", "one-encoding-only", "One inscription supplies no representation equivalence class.", "multiple-distinct-encoding-identities", "At least two distinct inscriptions are retained without multiplying the carrier."),
    dimension("fibres", "partial-or-arbitrary-label-change", "An arbitrary partial change does not preserve the generated Fold relation.", "complete-opposed-fibre-complement", "Every support incidence changes to its exact opposed Fold fibre."),
    dimension("identity", "representations-counted-as-species", "Formal encodings do not create new chemical carriers.", "one-carrier-many-representations", "Carrier identity remains one while representation identity remains plural."),
    dimension("process", "equilibrium-or-transition-imported", "A representation relation does not imply a physical interconversion process.", "representation-relation-only", "No time, transition or equilibrium law enters equivalence."),
    dimension("extension", "named-resonance-exception", "A named exception adds an unforced classification rule.", "shared-complement-successor-no-extra-rule", "Appending one fresh occurrence to both encodings preserves complete complement and the one-carrier relation."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    first = encoding("first", "carrier", ("a", "b", "c"), ((1, 2), (2, 3)), ("fold-fibre-one", "fold-fibre-two"))
    second = encoding("second", "carrier", ("a", "b", "c"), ((1, 2), (2, 3)), ("fold-fibre-two", "fold-fibre-one"))
    pair = equivalent_pair("carrier", first, second)
    successor = append_shared_successor(pair, "d")
    carrier_rejected = adjacency_rejected = partial_rejected = False
    try:
        other = encoding("other", "other-carrier", ("a", "b", "c"), ((1, 2), (2, 3)), ("fold-fibre-two", "fold-fibre-one"))
        equivalent_pair("carrier", first, other)
    except InadmissibleExactValue:
        carrier_rejected = True
    try:
        changed = encoding("changed", "carrier", ("a", "b", "c"), ((1, 3), (2, 3)), ("fold-fibre-two", "fold-fibre-one"))
        equivalent_pair("carrier", first, changed)
    except InadmissibleExactValue:
        adjacency_rejected = True
    try:
        partial = encoding("partial", "carrier", ("a", "b", "c"), ((1, 2), (2, 3)), ("fold-fibre-one", "fold-fibre-one"))
        equivalent_pair("carrier", first, partial)
    except InadmissibleExactValue:
        partial_rejected = True
    return (
        ("base-pair", "Two complete global-complement encodings retain one carrier.", pair.representation_count == PositiveCount(2)),
        ("successor", "A shared fresh occurrence preserves adjacency and complete complement.", successor.first.atoms[:-1] == pair.first.atoms and complement_labels(successor.first.fibres) == successor.second.fibres),
        ("carrier-control", "A different molecular carrier rejects.", carrier_rejected),
        ("adjacency-control", "Changed adjacency rejects.", adjacency_rejected),
        ("partial-control", "A partial non-complement label change rejects.", partial_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "one-retained-molecular-carrier__complete-equal-atom-occurrence-support__"
    "complete-equal-adjacency-support__multiple-distinct-encoding-identities__"
    "complete-opposed-fibre-complement__one-carrier-many-representations__"
    "representation-relation-only__shared-complement-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactEquivalentRepresentationPair",
    "ExactMolecularEncoding",
    "OPERATIONAL_WITNESSES",
    "append_shared_successor",
    "complement_labels",
    "encoding",
    "equivalent_pair",
)
