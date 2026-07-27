"""Fold-native molecular nuclear/electronic and rovibronic composition.

The law in this module composes already-admitted electronic, isotope,
vibrational, rotational and held-spin carriers into one auditable molecular
state.  It does not import a wavefunction, Born--Oppenheimer approximation,
rigid-rotor model, continuum surface, measured wavenumber or fitted molecular
constant.  Numerical spectroscopy remains owned by the admitted Physics
dependency and is opened only by the post-seal Chemistry validator.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.electronic_structure_derivation import MolecularElectronicState
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.molecular_spectroscopy_successor_laws_v1 import (
    odd_vibrational_carrier,
    rotational_level,
)
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class MolecularRovibronicState:
    """One exact finite molecular state at a declared observation resolution."""

    electronic_state: MolecularElectronicState
    nuclear_occurrence_ids: tuple[str, ...]
    isotope_labels: tuple[HeldLabel, ...]
    vibrational_ordinal: PositiveCount
    rotational_ordinal: PositiveCount
    held_spin_state: HeldLabel
    observation_record: HeldLabel

    def __post_init__(self) -> None:
        if not self.nuclear_occurrence_ids:
            raise InadmissibleExactValue("a molecular state requires retained nuclear occurrences")
        if len(set(self.nuclear_occurrence_ids)) != len(self.nuclear_occurrence_ids):
            raise InadmissibleExactValue("nuclear occurrences must be unique")
        if len(self.isotope_labels) != len(self.nuclear_occurrence_ids):
            raise InadmissibleExactValue("every nuclear occurrence requires one isotope label")
        if any(label.family != "molecular-isotope" for label in self.isotope_labels):
            raise InadmissibleExactValue("isotope identity must remain a held molecular label")
        if self.held_spin_state.family != "molecular-spin-state":
            raise InadmissibleExactValue("spin state must remain a held molecular label")
        if self.observation_record.family != "molecular-rovibronic-observation":
            raise InadmissibleExactValue("rovibronic state requires a retained observation record")

    @property
    def rotational_recurrence(self) -> PositiveCount:
        return PositiveCount(rotational_level(self.rotational_ordinal.value))

    @property
    def vibrational_recurrence(self) -> PositiveCount:
        return PositiveCount(odd_vibrational_carrier(self.vibrational_ordinal.value))

    @property
    def exact_state_key(self) -> tuple[object, ...]:
        return (
            self.electronic_state.molecular_carrier_id,
            tuple(label.label for label in self.isotope_labels),
            self.vibrational_recurrence.value,
            self.rotational_recurrence.value,
            self.held_spin_state.label,
            self.observation_record.label,
        )


def isotopologue_distinguishable(left: MolecularRovibronicState, right: MolecularRovibronicState) -> bool:
    if left.electronic_state.molecular_carrier_id != right.electronic_state.molecular_carrier_id:
        raise InadmissibleExactValue("isotopologue comparison requires one molecular carrier class")
    return left.exact_state_key != right.exact_state_key


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-QUANTUM-STATE-COMPOSITION-001",
    "SFT-QUANTUM-MEASUREMENT-001",
    "SFT-PHYS-QUANTUM-SPIN-001",
    "SFT-PHYS-MOLECULAR-SPECTRUM-HIERARCHY-004",
    "SFT-PHYS-MOLECULAR-SPECTROSCOPY-TERMINAL-005",
    "SFT-CHEM-ELEM-ISOTOPE-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "detached-state-name", "A detached name cannot identify the molecular whole carrying the state.", "identified-molecular-state-carrier", "Every component remains bound to one identified molecular carrier."),
    dimension("composition", "nuclei-or-electrons-erased", "Erasing either support merges distinguishable isotopologues or electronic states.", "nuclear-electronic-joint-support", "Nuclear occurrences, isotope labels and the electronic state are jointly retained."),
    dimension("scale", "imported-separation-approximation", "An imported approximation cannot select a fundamental state organization.", "admitted-electronic-vibrational-rotational-order", "The already-admitted hierarchy supplies distinct composed state coordinates without a new approximation."),
    dimension("vibration", "continuum-vibrational-coordinate", "A continuum coordinate is outside the exact generated grammar.", "positive-odd-vibrational-recurrence", "A positive ordinal generates the exact odd vibrational recurrence carrier."),
    dimension("rotation", "signed-or-continuum-rotation", "A signed continuum angle is not an exact proof carrier.", "positive-counted-rotational-recurrence", "A positive ordinal generates the exact J(J+1) rotational carrier."),
    dimension("spin", "spin-erased-state", "Erasing spin merges spectroscopically distinguishable molecular states.", "held-spin-state", "Spin remains a held label rather than a negative or imaginary scalar."),
    dimension("observation", "result-without-readout-record", "A state without a readout boundary cannot be reproduced or distinguished.", "retained-rovibronic-observation", "The exact readout record fixes the declared molecular-state resolution."),
    dimension("extension", "free-species-exception", "A species exception can fit any desired spectrum.", "no-extra-rule", "Only admitted dependencies and the complete finite product are used."),
)


def _electronic_state() -> MolecularElectronicState:
    return MolecularElectronicState(
        "homonuclear-hydrogen-carrier",
        ("electron-one", "electron-two"),
        (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-b")),
        (
            ("electron-one", HeldLabel("molecular-electronic-support", "joined-region")),
            ("electron-two", HeldLabel("molecular-electronic-support", "joined-region")),
        ),
        HeldLabel("molecular-electronic-state", "ground-state"),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    electronic = _electronic_state()
    hydrogen = MolecularRovibronicState(
        electronic,
        ("nucleus-one", "nucleus-two"),
        (HeldLabel("molecular-isotope", "protium"), HeldLabel("molecular-isotope", "protium")),
        PositiveCount(1),
        PositiveCount(1),
        HeldLabel("molecular-spin-state", "singlet"),
        HeldLabel("molecular-rovibronic-observation", "h2-ground-row"),
    )
    deuterium = MolecularRovibronicState(
        electronic,
        ("nucleus-one", "nucleus-two"),
        (HeldLabel("molecular-isotope", "deuterium"), HeldLabel("molecular-isotope", "deuterium")),
        PositiveCount(1),
        PositiveCount(1),
        HeldLabel("molecular-spin-state", "singlet"),
        HeldLabel("molecular-rovibronic-observation", "d2-ground-row"),
    )
    incomplete_rejected = False
    try:
        MolecularRovibronicState(
            electronic,
            ("nucleus-one", "nucleus-two"),
            (HeldLabel("molecular-isotope", "protium"),),
            PositiveCount(1),
            PositiveCount(1),
            HeldLabel("molecular-spin-state", "singlet"),
            HeldLabel("molecular-rovibronic-observation", "incomplete"),
        )
    except InadmissibleExactValue:
        incomplete_rejected = True
    return (
        ("exact-positive-recurrence", "The first positive vibration and rotation coordinates generate exact positive carriers.", hydrogen.vibrational_recurrence.value == 1 and hydrogen.rotational_recurrence.value == 2),
        ("isotopologue-distinction", "Changing retained nuclear isotope labels changes the joint molecular state while preserving its electronic carrier class.", isotopologue_distinguishable(hydrogen, deuterium)),
        ("incomplete-nuclear-support-control", "A missing isotope label rejects rather than being silently supplied.", incomplete_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "identified-molecular-state-carrier__nuclear-electronic-joint-support__admitted-electronic-vibrational-rotational-order__positive-odd-vibrational-recurrence__positive-counted-rotational-recurrence__held-spin-state__retained-rovibronic-observation__no-extra-rule"


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "MolecularRovibronicState",
    "OPERATIONAL_WITNESSES",
    "isotopologue_distinguishable",
)
