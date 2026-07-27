"""Fold-native inorganic magnetic-state law (INORG-009)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


UnpairedCount = Union[EmptyOne, PositiveCount]


@dataclass(frozen=True)
class CompleteUnpairedSupport:
    complex_identity: HeldLabel
    electron_occurrences: tuple[HeldLabel, ...]
    spin_fibres: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if self.complex_identity.family != "coordination-entity":
            raise InadmissibleExactValue("magnetic state requires one retained coordination entity")
        if len(self.electron_occurrences) != len(self.spin_fibres):
            raise InadmissibleExactValue("every unpaired occurrence requires one held spin fibre")
        if len(set(self.electron_occurrences)) != len(self.electron_occurrences):
            raise InadmissibleExactValue("unpaired electron support cannot duplicate an occurrence")
        if any(row.family != "electron-occurrence" for row in self.electron_occurrences):
            raise InadmissibleExactValue("unpaired support contains an invalid electron occurrence")
        if any(row.family != "electron-spin" or row.label not in {"fibre-a", "fibre-b"} for row in self.spin_fibres):
            raise InadmissibleExactValue("unpaired support must retain one of the two forced spin fibres")

    @property
    def unpaired_count(self) -> UnpairedCount:
        return EMPTY_ONE if not self.electron_occurrences else PositiveCount(len(self.electron_occurrences))

    @property
    def spin_width(self) -> PositiveCount:
        count = 0 if isinstance(self.unpaired_count, EmptyOne) else self.unpaired_count.value
        return PositiveCount(count + 1)


@dataclass(frozen=True)
class ExactInorganicMagneticState:
    support: CompleteUnpairedSupport
    moment_support: UnpairedCount
    spin_width: PositiveCount
    field_relation: HeldLabel
    magnetic_class: HeldLabel

    def __post_init__(self) -> None:
        if self.moment_support != self.support.unpaired_count or self.spin_width != self.support.spin_width:
            raise InadmissibleExactValue("magnetic state must preserve complete unpaired support exactly")
        if self.field_relation.family != "held-field-relation" or self.field_relation.label not in {"drawn-into-field", "repelled-from-field"}:
            raise InadmissibleExactValue("field response is a held direction, not a signed scalar")
        if self.magnetic_class.family != "inorganic-magnetic-class" or self.magnetic_class.label not in {"paramagnetic", "diamagnetic"}:
            raise InadmissibleExactValue("magnetic class is outside the forced pair")
        if isinstance(self.moment_support, EmptyOne):
            if self.magnetic_class.label != "diamagnetic" or self.field_relation.label != "repelled-from-field":
                raise InadmissibleExactValue("balanced paired support forces the diamagnetic class")
        elif self.magnetic_class.label != "paramagnetic" or self.field_relation.label != "drawn-into-field":
            raise InadmissibleExactValue("positive unpaired support forces the paramagnetic class")


def forced_inorganic_magnetic_state(support: CompleteUnpairedSupport) -> ExactInorganicMagneticState:
    if isinstance(support.unpaired_count, EmptyOne):
        relation, magnetic_class = "repelled-from-field", "diamagnetic"
    else:
        relation, magnetic_class = "drawn-into-field", "paramagnetic"
    return ExactInorganicMagneticState(
        support,
        support.unpaired_count,
        support.spin_width,
        HeldLabel("held-field-relation", relation),
        HeldLabel("inorganic-magnetic-class", magnetic_class),
    )


def complete_unpaired_support(complex_label: str, positive_unpaired_count: UnpairedCount) -> CompleteUnpairedSupport:
    count = 0 if isinstance(positive_unpaired_count, EmptyOne) else positive_unpaired_count.value
    return CompleteUnpairedSupport(
        HeldLabel("coordination-entity", complex_label),
        tuple(HeldLabel("electron-occurrence", f"unpaired-{index}") for index in range(1, count + 1)),
        tuple(HeldLabel("electron-spin", "fibre-a" if index % 2 else "fibre-b") for index in range(1, count + 1)),
    )


def append_unpaired_successor(support: CompleteUnpairedSupport) -> CompleteUnpairedSupport:
    next_index = len(support.electron_occurrences) + 1
    return CompleteUnpairedSupport(
        support.complex_identity,
        support.electron_occurrences + (HeldLabel("electron-occurrence", f"unpaired-{next_index}"),),
        support.spin_fibres + (HeldLabel("electron-spin", "fibre-a" if next_index % 2 else "fibre-b"),),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-QUANTUM-SPIN-001", "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002", "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    "SFT-CHEM-MOLECULAR-EXCLUSION-EXCHANGE-006", "SFT-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012",
    "SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001", "SFT-CHEM-LIGAND-STATE-SPLITTING-006",
    "SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "free-magnetic-number", "A free magnetic number is detached from the inorganic state.", "one-retained-complex-carrier", "Every magnetic state remains bound to one coordination entity."),
    dimension("support", "selected-or-averaged-spin", "A selected or averaged spin loses electron occurrences.", "complete-unpaired-occurrence-support", "Every unpaired electron occurrence and held spin fibre remains explicit."),
    dimension("balance", "numerical-zero-paired-state", "Numerical zero is not a native state or proof magnitude.", "pairwise-closure-to-EmptyOne", "Complete complementary pairing closes unpaired support to structural EmptyOne."),
    dimension("moment", "square-root-spin-only-formula", "A square-root formula imports irrational continuum magnitude.", "exact-unpaired-support-count", "Native magnetic moment support is exactly the positive unpaired count or structural EmptyOne."),
    dimension("width", "asserted-multiplicity", "An asserted multiplicity can contradict complete support.", "unpaired-successor-spin-width", "Spin width is exactly one successor beyond unpaired support."),
    dimension("direction", "signed-susceptibility-proof", "A signed scalar imports negative proof quantity.", "held-drawn-or-repelled-field-relation", "Opposed field relations remain held labels while external signs remain source inscriptions."),
    dimension("classification", "species-magnetic-lookup", "A species lookup lets observed class select the rule.", "EmptyOne-diamagnetic-positive-paramagnetic", "Balanced EmptyOne support forces diamagnetic; positive unpaired support forces paramagnetic."),
    dimension("extension", "fitted-g-factor-or-complex-exception", "A fitted factor or species exception destroys zero-parameter closure.", "unpaired-successor-with-no-extra-rule", "Each appended unpaired occurrence increments support and width once while preserving the paramagnetic class."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    balanced = forced_inorganic_magnetic_state(complete_unpaired_support("balanced", EMPTY_ONE))
    high = forced_inorganic_magnetic_state(complete_unpaired_support("high", PositiveCount(4)))
    successor = forced_inorganic_magnetic_state(append_unpaired_successor(high.support))
    duplicate_rejected = False
    try:
        occurrence = HeldLabel("electron-occurrence", "same")
        CompleteUnpairedSupport(HeldLabel("coordination-entity", "bad"), (occurrence, occurrence), (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-b")))
    except InadmissibleExactValue:
        duplicate_rejected = True
    return (
        ("balanced-diamagnetic", "Structural EmptyOne unpaired support forces the repelled diamagnetic class.", isinstance(balanced.moment_support, EmptyOne) and balanced.spin_width.value == 1 and balanced.magnetic_class.label == "diamagnetic"),
        ("positive-paramagnetic", "Four complete unpaired occurrences force moment support four and spin width five.", high.moment_support.value == 4 and high.spin_width.value == 5 and high.magnetic_class.label == "paramagnetic"),
        ("unpaired-successor", "Appending one unpaired occurrence increments moment support and spin width exactly once.", successor.moment_support.value == 5 and successor.spin_width.value == 6 and successor.magnetic_class.label == "paramagnetic"),
        ("duplicate-control", "Duplicating one unpaired occurrence rejects.", duplicate_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "one-retained-complex-carrier__complete-unpaired-occurrence-support__pairwise-closure-to-EmptyOne__exact-unpaired-support-count__unpaired-successor-spin-width__held-drawn-or-repelled-field-relation__EmptyOne-diamagnetic-positive-paramagnetic__unpaired-successor-with-no-extra-rule"


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactInorganicMagneticState", "OPERATIONAL_WITNESSES",
    "CompleteUnpairedSupport", "append_unpaired_successor", "complete_unpaired_support", "forced_inorganic_magnetic_state",
)
