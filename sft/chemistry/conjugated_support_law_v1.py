"""Fold-native connected alternating support law for Chemistry ORG-001."""
from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def atom(label: str) -> HeldLabel:
    return HeldLabel("conjugated-atom-occurrence", label)


def fibre(label: str) -> HeldLabel:
    if label not in ("fold-fibre-one", "fold-fibre-two"):
        raise InadmissibleExactValue("conjugated support admits exactly the two forced Fold fibres")
    return HeldLabel("conjugated-support-fibre", label)


@dataclass(frozen=True)
class ExactConjugatedSupport:
    """One finite complete path whose adjacent support fibres alternate exactly."""

    carrier: HeldLabel
    atoms: tuple[HeldLabel, ...]
    support_fibres: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if self.carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("conjugated support requires one retained molecular carrier")
        if len(self.atoms) < 3 or len(set(self.atoms)) != len(self.atoms):
            raise InadmissibleExactValue("conjugated support requires at least three distinct atom occurrences")
        if any(row.family != "conjugated-atom-occurrence" for row in self.atoms):
            raise InadmissibleExactValue("conjugated atom identity is invalid")
        if len(self.support_fibres) != len(self.atoms) - 1:
            raise InadmissibleExactValue("every adjacent atom pair must retain exactly one support fibre")
        if any(
            row.family != "conjugated-support-fibre"
            or row.label not in ("fold-fibre-one", "fold-fibre-two")
            for row in self.support_fibres
        ):
            raise InadmissibleExactValue("support contains a non-Fold fibre")
        if any(left == right for left, right in zip(self.support_fibres, self.support_fibres[1:])):
            raise InadmissibleExactValue("adjacent support fibres must alternate")

    @property
    def atom_count(self) -> PositiveCount:
        return PositiveCount(len(self.atoms))

    @property
    def support_count(self) -> PositiveCount:
        return PositiveCount(len(self.support_fibres))

    @property
    def incidences(self) -> tuple[tuple[HeldLabel, HeldLabel, HeldLabel], ...]:
        return tuple(
            (self.atoms[index], self.support_fibres[index], self.atoms[index + 1])
            for index in range(len(self.support_fibres))
        )


def conjugated_support(
    carrier_label: str,
    atom_labels: tuple[str, ...],
    fibre_labels: tuple[str, ...],
) -> ExactConjugatedSupport:
    return ExactConjugatedSupport(
        HeldLabel("molecular-carrier", carrier_label),
        tuple(atom(label) for label in atom_labels),
        tuple(fibre(label) for label in fibre_labels),
    )


def append_opposed_fibre(
    support: ExactConjugatedSupport,
    atom_label: str,
) -> ExactConjugatedSupport:
    if atom(atom_label) in support.atoms:
        raise InadmissibleExactValue("successor atom occurrence must be fresh")
    next_label = (
        "fold-fibre-two"
        if support.support_fibres[-1].label == "fold-fibre-one"
        else "fold-fibre-one"
    )
    return ExactConjugatedSupport(
        support.carrier,
        support.atoms + (atom(atom_label),),
        support.support_fibres + (fibre(next_label),),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-BOND-ORDER-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-ORGANIC-FUNCTIONAL-GROUP-001",
    "SFT-CHEM-ORGANIC-REACTION-FAMILY-001",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier",
        "selected-unbound-bond-marks",
        "Selected marks do not define one molecular subcarrier.",
        "one-retained-molecular-subcarrier",
        "Every atom occurrence and support incidence belongs to one held carrier.",
    ),
    dimension(
        "connectivity",
        "disconnected-support-fragments",
        "Disconnected fragments cannot propagate one support distinction.",
        "complete-connected-adjacency-path",
        "Every successive atom occurrence shares one exact incidence.",
    ),
    dimension(
        "fibres",
        "bond-support-label-erased",
        "Erasure merges the two required support distinctions.",
        "two-forced-held-support-fibres",
        "Every incidence retains one of the two forced Fold fibre labels.",
    ),
    dimension(
        "alternation",
        "arbitrary-adjacent-fibre-repetition",
        "Repeated adjacent fibres close the alternating path.",
        "exact-opposed-adjacent-fibre-recurrence",
        "Every adjacent incidence carries the opposed held fibre.",
    ),
    dimension(
        "coverage",
        "favourable-subpath-only",
        "A selected subpath can hide a failing incidence.",
        "complete-atom-and-incidence-support",
        "Every atom and every path incidence enters the decision.",
    ),
    dimension(
        "propagation",
        "independent-bond-pairs",
        "Independent pairs do not share a propagation centre.",
        "shared-centre-support-propagation",
        "Successive incidences meet at the same retained atom occurrence.",
    ),
    dimension(
        "observation",
        "spectrum-or-name-selects-structure",
        "An external name or spectrum cannot select the Fold law.",
        "structure-sealed-before-external-observation",
        "The complete structural prediction closes before source outcomes open.",
    ),
    dimension(
        "extension",
        "named-conjugation-exception",
        "A named exception introduces an unforced rule.",
        "opposed-fibre-successor-no-extra-rule",
        "A fresh atom extends the path only with the uniquely opposed fibre.",
    ),
)


def _operational_witnesses() -> tuple[tuple[str, str, bool], ...]:
    base = conjugated_support(
        "base",
        ("atom-a", "atom-b", "atom-c"),
        ("fold-fibre-one", "fold-fibre-two"),
    )
    successor = append_opposed_fibre(base, "atom-d")
    repeated_rejected = False
    incomplete_rejected = False
    duplicate_rejected = False
    try:
        conjugated_support(
            "repeated",
            ("atom-a", "atom-b", "atom-c"),
            ("fold-fibre-one", "fold-fibre-one"),
        )
    except InadmissibleExactValue:
        repeated_rejected = True
    try:
        conjugated_support(
            "incomplete",
            ("atom-a", "atom-b", "atom-c"),
            ("fold-fibre-one",),
        )
    except InadmissibleExactValue:
        incomplete_rejected = True
    try:
        append_opposed_fibre(base, "atom-b")
    except InadmissibleExactValue:
        duplicate_rejected = True
    return (
        (
            "base-support",
            "Three atom occurrences and two opposed support fibres form the first connected alternating path.",
            base.atom_count == PositiveCount(3)
            and base.support_count == PositiveCount(2)
            and len(base.incidences) == 2,
        ),
        (
            "successor",
            "A fresh occurrence receives the uniquely opposed next fibre and retains every prior incidence.",
            successor.atom_count == PositiveCount(4)
            and successor.support_count == PositiveCount(3)
            and successor.incidences[:2] == base.incidences,
        ),
        ("repetition-control", "Equal adjacent fibres reject.", repeated_rejected),
        ("coverage-control", "An omitted incidence rejects.", incomplete_rejected),
        ("identity-control", "A duplicated successor occurrence rejects.", duplicate_rejected),
    )


OPERATIONAL_WITNESSES = _operational_witnesses()
EXACT_RESULT = (
    "one-retained-molecular-subcarrier__complete-connected-adjacency-path__"
    "two-forced-held-support-fibres__exact-opposed-adjacent-fibre-recurrence__"
    "complete-atom-and-incidence-support__shared-centre-support-propagation__"
    "structure-sealed-before-external-observation__opposed-fibre-successor-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactConjugatedSupport",
    "OPERATIONAL_WITNESSES",
    "append_opposed_fibre",
    "atom",
    "conjugated_support",
    "fibre",
)
