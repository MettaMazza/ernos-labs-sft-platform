"""Fold-native electrode-potential chemical relation (ECHEM-002)."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension

def _ratio(value: Fraction) -> PositiveRatio:
    return PositiveRatio.from_pair(value.numerator, value.denominator)

@dataclass(frozen=True)
class StandardHalfCellAccount:
    half_reaction: HeldLabel
    reference_electrode: HeldLabel
    condition: HeldLabel
    species_phase_signature: tuple[HeldLabel, ...]
    retained_transfer_work: PositiveRatio
    transferred_carriers: PositiveCount
    def __post_init__(self):
        if self.half_reaction.family != "half-reaction-identity":
            raise InadmissibleExactValue("standard half-cell account requires a half-reaction identity")
        if self.reference_electrode.family != "reference-electrode":
            raise InadmissibleExactValue("standard half-cell account requires a held reference electrode")
        if self.condition.family != "electrochemical-condition":
            raise InadmissibleExactValue("standard half-cell account requires one held condition")
        if not self.species_phase_signature or any(row.family != "species-phase" for row in self.species_phase_signature):
            raise InadmissibleExactValue("complete species and phases must be retained")
        if len(set(self.species_phase_signature)) != len(self.species_phase_signature):
            raise InadmissibleExactValue("species-phase occurrences must remain distinct")
        if not isinstance(self.retained_transfer_work, PositiveRatio) or not isinstance(self.transferred_carriers, PositiveCount):
            raise InadmissibleExactValue("transfer work and carrier count must be exact positive values")
    @property
    def work_per_carrier(self) -> Fraction:
        return self.retained_transfer_work.fraction / self.transferred_carriers.value

@dataclass(frozen=True)
class ElectrodePotentialRelation:
    orientation: HeldLabel
    separation: PositiveRatio | EmptyOne
    subject: HeldLabel
    reference: HeldLabel
    condition: HeldLabel

def electrode_potential_relation(subject: StandardHalfCellAccount, reference: StandardHalfCellAccount) -> ElectrodePotentialRelation:
    if subject.reference_electrode != reference.reference_electrode:
        raise InadmissibleExactValue("electrode potential comparison changed reference electrode")
    if subject.condition != reference.condition:
        raise InadmissibleExactValue("electrode potential comparison changed condition")
    left, right = subject.work_per_carrier, reference.work_per_carrier
    if left == right:
        orientation, separation = "coincident-with-reference", EMPTY_ONE
    elif left > right:
        orientation, separation = "subject-above-reference", _ratio(left - right)
    else:
        orientation, separation = "subject-below-reference", _ratio(right - left)
    return ElectrodePotentialRelation(HeldLabel("electrode-potential-orientation", orientation), separation, subject.half_reaction, reference.half_reaction, subject.condition)

def common_work_successor_preserves_relation(subject: StandardHalfCellAccount, reference: StandardHalfCellAccount, extension: PositiveRatio) -> bool:
    if subject.transferred_carriers != reference.transferred_carriers:
        raise InadmissibleExactValue("common-work successor requires equal transfer counts")
    prior = electrode_potential_relation(subject, reference)
    count = subject.transferred_carriers.value
    def extend(row):
        value = row.retained_transfer_work.fraction + extension.fraction * count
        return StandardHalfCellAccount(row.half_reaction, row.reference_electrode, row.condition, row.species_phase_signature, _ratio(value), row.transferred_carriers)
    return electrode_potential_relation(extend(subject), extend(reference)).orientation == prior.orientation

DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-ORDER-LATTICE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-REDOX-COUPLING-001", "SFT-CHEM-ELECTROCHEM-CELL-001",
    "SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001",
)
DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("account", "voltage-answer-only", "A displayed voltage does not retain the chemical transfer account.", "complete-half-cell-transfer-account", "Half-reaction, species, phases, work and transfer count remain held."),
    dimension("reference", "unbound-electrode-number", "An unbound number has no electrode reference.", "one-held-reference-electrode", "Every comparison retains one exact reference identity."),
    dimension("condition", "mixed-temperature-or-state", "Changing conditions destroys comparability.", "same-held-standard-condition", "Subject and reference share one declared condition."),
    dimension("normalization", "unnormalized-total-work", "Total work changes with carrier multiplicity.", "exact-work-per-held-transfer-carrier", "Potential compares exact positive work per transferred carrier."),
    dimension("orientation", "signed-native-number", "A sign imports a negative proof magnitude.", "held-above-below-or-coincident-orientation", "Direction is a held label and magnitude remains positive."),
    dimension("coincidence", "numerical-zero-potential", "Numerical zero is not a native magnitude.", "structural-EmptyOne-reference-coincidence", "Exact equality closes the distinction to EmptyOne."),
    dimension("record", "selected-standard-potential", "A selected value can hide species, phase, uncertainty or estimates.", "complete-standard-potential-reference-vector", "Every registered row and provenance field remains downstream."),
    dimension("extension", "species-specific-offset", "A fitted offset adds an unforced rule.", "common-work-successor-preserves-order", "Adding the same exact work per carrier preserves the relation."),
)
EXACT_RESULT = "complete-half-cell-transfer-account__one-held-reference-electrode__same-held-standard-condition__exact-work-per-held-transfer-carrier__held-above-below-or-coincident-orientation__structural-EmptyOne-reference-coincidence__complete-standard-potential-reference-vector__common-work-successor-preserves-order"

def _account(name, numerator, denominator=1):
    return StandardHalfCellAccount(HeldLabel("half-reaction-identity", name), HeldLabel("reference-electrode", "held-reference"), HeldLabel("electrochemical-condition", "standard-condition"), (HeldLabel("species-phase", name + "-aqueous"), HeldLabel("species-phase", name + "-solid")), PositiveRatio.from_pair(numerator, denominator), PositiveCount(1))

def _witnesses():
    reference, high, low = _account("reference", 3), _account("high", 5), _account("low", 1)
    equal = electrode_potential_relation(_account("equal", 3), reference)
    changed_condition = False
    try:
        bad = StandardHalfCellAccount(low.half_reaction, low.reference_electrode, HeldLabel("electrochemical-condition", "other"), low.species_phase_signature, low.retained_transfer_work, low.transferred_carriers)
        electrode_potential_relation(bad, reference)
    except InadmissibleExactValue:
        changed_condition = True
    return (
        ("above", "Higher exact per-carrier account is held above reference.", electrode_potential_relation(high, reference).orientation.label == "subject-above-reference"),
        ("below", "Lower exact per-carrier account is held below reference.", electrode_potential_relation(low, reference).orientation.label == "subject-below-reference"),
        ("positive-magnitude", "Both directed separations are exact and positive.", all(isinstance(electrode_potential_relation(row, reference).separation, PositiveRatio) for row in (high, low))),
        ("coincidence", "Exact equality closes to EmptyOne.", equal.separation == EMPTY_ONE),
        ("reference", "Reference identity is retained.", equal.reference == reference.half_reaction),
        ("condition", "Condition identity is retained.", equal.condition == reference.condition),
        ("condition-control", "Changed condition halts.", changed_condition),
        ("successor", "Common work successor preserves order.", common_work_successor_preserves_relation(high, reference, PositiveRatio.from_pair(2, 1))),
    )
OPERATIONAL_WITNESSES = _witnesses()
__all__ = ("DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ElectrodePotentialRelation", "OPERATIONAL_WITNESSES", "StandardHalfCellAccount", "common_work_successor_preserves_relation", "electrode_potential_relation")
