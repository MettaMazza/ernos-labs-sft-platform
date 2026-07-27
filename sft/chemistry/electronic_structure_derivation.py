"""Fold derivation of molecular electronic-state identity.

This module derives a molecular electronic state as a complete, admissible
joint arrangement of retained electron occurrences inside an identified
molecular carrier.  It imports no molecular Hamiltonian, orbital table,
measured level, fitted coefficient or external definition.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class MolecularElectronicState:
    molecular_carrier_id: str
    electron_occurrence_ids: tuple[str, ...]
    held_spin_labels: tuple[HeldLabel, ...]
    joint_support: tuple[tuple[str, HeldLabel], ...]
    observation_signature: HeldLabel

    def __post_init__(self) -> None:
        if not self.molecular_carrier_id.strip():
            raise InadmissibleExactValue("an electronic state requires one identified molecular carrier")
        if not self.electron_occurrence_ids or len(set(self.electron_occurrence_ids)) != len(self.electron_occurrence_ids):
            raise InadmissibleExactValue("electron occurrences must be a nonempty exact finite set")
        if len(self.held_spin_labels) != len(self.electron_occurrence_ids):
            raise InadmissibleExactValue("every electron occurrence requires one held spin label")
        if any(label.family != "electron-spin" for label in self.held_spin_labels):
            raise InadmissibleExactValue("spin must remain a held electron label")
        support_ids = tuple(row[0] for row in self.joint_support)
        if len(support_ids) != len(set(support_ids)) or set(support_ids) != set(self.electron_occurrence_ids):
            raise InadmissibleExactValue("joint support must contain every electron occurrence exactly once")
        if any(label.family != "molecular-electronic-support" for _, label in self.joint_support):
            raise InadmissibleExactValue("every support coordinate requires the molecular electronic family")
        if self.observation_signature.family != "molecular-electronic-state":
            raise InadmissibleExactValue("the state requires a retained molecular observation signature")


def electronic_count(state: MolecularElectronicState) -> PositiveCount:
    return PositiveCount(len(state.electron_occurrence_ids))


def same_electronic_state(left: MolecularElectronicState, right: MolecularElectronicState) -> bool:
    return (
        left.molecular_carrier_id == right.molecular_carrier_id
        and tuple(sorted((row[1].label, spin.label) for row, spin in zip(left.joint_support, left.held_spin_labels)))
        == tuple(sorted((row[1].label, spin.label) for row, spin in zip(right.joint_support, right.held_spin_labels)))
        and left.observation_signature == right.observation_signature
    )


def distinguishable_electronic_states(left: MolecularElectronicState, right: MolecularElectronicState) -> bool:
    if left.molecular_carrier_id != right.molecular_carrier_id:
        raise InadmissibleExactValue("electronic-state distinction requires one retained molecular carrier")
    return not same_electronic_state(left, right)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-QUANTUM-STATE-COMPOSITION-001",
    "SFT-QUANTUM-MEASUREMENT-001",
    "SFT-QUANTUM-CLASSICAL-CORRESPONDENCE-001",
    "SFT-PHYS-QUANTUM-PHYSICAL-STATE-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "state-without-molecular-carrier", "A free state label cannot identify which chemical whole carries it.", "identified-molecular-carrier", "The electronic organization remains bound to one admitted molecular carrier."),
    dimension("occurrences", "anonymous-electron-number", "A number alone erases the separately retained electron occurrences.", "electron-occurrences-retained", "Every electron occurrence remains a distinct held member of the joint state."),
    dimension("arrangement", "energy-name-only", "An energy or state name cannot reconstruct the electronic organization.", "complete-joint-arrangement", "The complete finite support assigns every retained occurrence exactly once."),
    dimension("admissibility", "arbitrary-electron-arrangement", "An arbitrary arrangement can violate admitted spin, indistinguishability and exclusion laws.", "admitted-quantum-constraints", "Only arrangements preserving all admitted quantum distinctions survive."),
    dimension("composition", "independent-electron-list", "Independent labels omit the composed molecular state.", "molecular-composition-retained", "Electron support is composed with the identified molecular whole."),
    dimension("distinction", "state-name-without-observation", "A name without a retained observation class supplies no state distinction.", "observation-distinguishable-state", "Distinct joint support or signature yields a retained chemical state distinction."),
    dimension("record", "electronic-result-without-trace", "A result without carrier, occurrences and support cannot be reproduced.", "held-state-record", "Carrier, occurrences, spin, support and observation signature remain auditable."),
    dimension("extension", "free-electronic-exception", "A free exception can manufacture a desired state or target match.", "no-extra-rule", "No law beyond admitted dependencies and complete support is introduced."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    state_a = MolecularElectronicState(
        "molecule-one",
        ("electron-one", "electron-two"),
        (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-b")),
        (
            ("electron-one", HeldLabel("molecular-electronic-support", "joined-region")),
            ("electron-two", HeldLabel("molecular-electronic-support", "joined-region")),
        ),
        HeldLabel("molecular-electronic-state", "state-a"),
    )
    state_b = MolecularElectronicState(
        "molecule-one",
        ("electron-one", "electron-two"),
        (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-b")),
        (
            ("electron-one", HeldLabel("molecular-electronic-support", "separated-region")),
            ("electron-two", HeldLabel("molecular-electronic-support", "separated-region")),
        ),
        HeldLabel("molecular-electronic-state", "state-b"),
    )
    incomplete_rejected = False
    try:
        MolecularElectronicState(
            "molecule-one",
            ("electron-one", "electron-two"),
            (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-b")),
            (("electron-one", HeldLabel("molecular-electronic-support", "joined-region")),),
            HeldLabel("molecular-electronic-state", "incomplete"),
        )
    except InadmissibleExactValue:
        incomplete_rejected = True
    return (
        ("complete-two-electron-state", "Every electron occurrence is retained once in joint molecular support.", electronic_count(state_a).value == 2),
        ("state-distinction", "Changing complete joint support and the held signature changes the molecular electronic state.", distinguishable_electronic_states(state_a, state_b)),
        ("incomplete-support-control", "A support omitting a retained electron occurrence rejects.", incomplete_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "identified-molecular-carrier__electron-occurrences-retained__complete-joint-arrangement__admitted-quantum-constraints__molecular-composition-retained__observation-distinguishable-state__held-state-record__no-extra-rule"
PREDICTED_OBSERVATION_LABEL = "allowed-electronic-arrangement__electron-support-retained__molecular-carrier-bounded"


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "MolecularElectronicState",
    "OPERATIONAL_WITNESSES",
    "PREDICTED_OBSERVATION_LABEL",
    "distinguishable_electronic_states",
    "electronic_count",
    "same_electronic_state",
)
