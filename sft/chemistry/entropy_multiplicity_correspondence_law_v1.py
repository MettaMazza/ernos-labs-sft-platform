"""Fold-native chemical entropy/multiplicity correspondence for THERMO-005."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ChemicalEntropyClass:
    macro_observation: HeldLabel
    microstates: tuple[HeldLabel, ...]
    multiplicity: PositiveCount
    exact_support_part: PositiveRatio
    unresolved_distinctions: tuple[tuple[HeldLabel, HeldLabel], ...] | EmptyOne


@dataclass(frozen=True)
class ChemicalEntropyLedger:
    complete_support: tuple[HeldLabel, ...]
    classes: tuple[ChemicalEntropyClass, ...]


def _validate_support_and_observation(
    support: tuple[HeldLabel, ...],
    observation: tuple[tuple[HeldLabel, HeldLabel], ...],
) -> dict[HeldLabel, HeldLabel]:
    if not isinstance(support, tuple) or not support:
        raise InadmissibleExactValue("chemical entropy requires finite nonempty microstate support")
    if any(not isinstance(state, HeldLabel) or state.family != "chemical-microstate" for state in support):
        raise InadmissibleExactValue("chemical entropy support lost microstate identity")
    if len(set(support)) != len(support):
        raise InadmissibleExactValue("chemical entropy support duplicated a microstate")
    if not isinstance(observation, tuple) or len(observation) != len(support):
        raise InadmissibleExactValue("chemical entropy requires a total observation")
    images = dict(observation)
    if len(images) != len(observation) or set(images) != set(support):
        raise InadmissibleExactValue("chemical observation is partial or duplicated")
    if any(not isinstance(label, HeldLabel) or label.family != "chemical-macro-observation" for label in images.values()):
        raise InadmissibleExactValue("chemical macro-observation lost held identity")
    return images


def _unresolved_pairs(members: tuple[HeldLabel, ...]) -> tuple[tuple[HeldLabel, HeldLabel], ...] | EmptyOne:
    pairs = tuple(
        (left, right)
        for position, left in enumerate(members)
        for right in members[position + 1 :]
    )
    return pairs if pairs else EmptyOne()


def chemical_entropy_ledger(
    support: tuple[HeldLabel, ...],
    observation: tuple[tuple[HeldLabel, HeldLabel], ...],
) -> ChemicalEntropyLedger:
    """Retain exact multiplicities and every distinction closed by observation."""

    images = _validate_support_and_observation(support, observation)
    labels = tuple(dict.fromkeys(images[state] for state in support))
    classes = []
    for label in labels:
        members = tuple(state for state in support if images[state] == label)
        classes.append(ChemicalEntropyClass(
            label,
            members,
            PositiveCount(len(members)),
            PositiveRatio.from_pair(len(members), len(support)),
            _unresolved_pairs(members),
        ))
    return ChemicalEntropyLedger(support, tuple(classes))


def closed_distinction_pairs(ledger: ChemicalEntropyLedger) -> tuple[tuple[HeldLabel, HeldLabel], ...] | EmptyOne:
    if not isinstance(ledger, ChemicalEntropyLedger):
        raise InadmissibleExactValue("closed distinctions require a chemical entropy ledger")
    pairs = tuple(
        pair
        for entropy_class in ledger.classes
        if not isinstance(entropy_class.unresolved_distinctions, EmptyOne)
        for pair in entropy_class.unresolved_distinctions
    )
    return pairs if pairs else EmptyOne()


def chemical_observation_refines(
    support: tuple[HeldLabel, ...],
    fine: tuple[tuple[HeldLabel, HeldLabel], ...],
    coarse: tuple[tuple[HeldLabel, HeldLabel], ...],
) -> bool:
    fine_images = _validate_support_and_observation(support, fine)
    coarse_images = _validate_support_and_observation(support, coarse)
    return all(
        coarse_images[left] == coarse_images[right]
        for left in support
        for right in support
        if fine_images[left] == fine_images[right]
    )


def append_microstate_preserves_ledger(
    support: tuple[HeldLabel, ...],
    observation: tuple[tuple[HeldLabel, HeldLabel], ...],
    new_state: HeldLabel,
    new_image: HeldLabel,
) -> bool:
    prior = chemical_entropy_ledger(support, observation)
    if new_state in support:
        raise InadmissibleExactValue("entropy successor requires one fresh microstate")
    extended = chemical_entropy_ledger(support + (new_state,), observation + ((new_state, new_image),))
    prior_by_label = {item.macro_observation: item for item in prior.classes}
    extended_by_label = {item.macro_observation: item for item in extended.classes}
    for label, prior_class in prior_by_label.items():
        current = extended_by_label[label]
        if label == new_image:
            if current.microstates[:-1] != prior_class.microstates or current.microstates[-1] != new_state:
                return False
        elif current.microstates != prior_class.microstates:
            return False
    return extended.complete_support[:-1] == prior.complete_support


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-QUANTITY-001", "SFT-INFO-ENTROPY-UNCERTAINTY-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-PHYS-THERMO-ENTROPY-001",
    "SFT-PHYS-THERMO-SECOND-LAW-001", "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    "SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002", "SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
    "SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("support", "selected-or-completed-infinite-chemical-support", "A selected or completed-infinite support cannot establish complete multiplicity.", "complete-finite-chemical-microstate-support", "Every generated chemical microstate occurs exactly once."),
    dimension("partition", "overlapping-or-partial-macroclasses", "Overlap or omission destroys exact observation multiplicity.", "disjoint-exhaustive-chemical-observation-classes", "Every microstate occurs once in one macro-observation class."),
    dimension("multiplicity", "fitted-probability-or-floating-weight", "A fit imports a distribution and precision choice.", "exact-positive-class-count-and-whole-part", "Multiplicity is a positive count and its part is exact relative to complete support."),
    dimension("entropy", "logarithmic-or-irrational-scalar-proof", "A logarithmic scalar imports forbidden irrational proof values and erases provenance.", "complete-unresolved-distinction-ledger", "Entropy retains every class, member, exact part and closed pair."),
    dimension("certainty", "numerical-zero-singleton-entropy", "Numerical zero is not an SFT proof value.", "structural-EmptyOne-singleton-certainty", "A singleton class has structural EmptyOne unresolved support."),
    dimension("prediction", "entropy-or-phase-target-readable-before-seal", "Observed entropy could select multiplicity or ordering.", "complete-value-free-entropy-phase-identity-seal", "All state and column identities seal before entropy or phase values open."),
    dimension("record", "selected-entropy-or-single-phase-row", "A selected row can hide a phase transition or adverse orientation.", "complete-13-row-entropy-phase-transition-vector", "Every liquid, boundary and vapour entropy row is retained."),
    dimension("extension", "resample-or-refit-after-new-microstate", "Resampling changes prior evidence and cannot prove every finite support.", "depth-independent-one-microstate-ledger-successor", "One fresh microstate updates one class and preserves all prior identities."),
)


EXACT_RESULT = (
    "complete-finite-chemical-microstate-support__disjoint-exhaustive-chemical-observation-classes__"
    "exact-positive-class-count-and-whole-part__complete-unresolved-distinction-ledger__"
    "structural-EmptyOne-singleton-certainty__complete-value-free-entropy-phase-identity-seal__"
    "complete-13-row-entropy-phase-transition-vector__depth-independent-one-microstate-ledger-successor"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    support = tuple(HeldLabel("chemical-microstate", label) for label in ("aa", "ab", "ba", "bb"))
    fine = tuple((state, HeldLabel("chemical-macro-observation", state.label)) for state in support)
    prefix = tuple((state, HeldLabel("chemical-macro-observation", state.label[0])) for state in support)
    coarse = tuple((state, HeldLabel("chemical-macro-observation", "unresolved")) for state in support)
    prefix_ledger = chemical_entropy_ledger(support, prefix)
    fresh = HeldLabel("chemical-microstate", "ac")
    return (
        ("exact-multiplicity", "Two prefix classes each retain multiplicity two and exact half support.", all(item.multiplicity == PositiveCount(2) and item.exact_support_part.fraction == Fraction(1, 2) for item in prefix_ledger.classes)),
        ("singleton-EmptyOne", "Fine observation gives every singleton structural EmptyOne uncertainty.", all(isinstance(item.unresolved_distinctions, EmptyOne) for item in chemical_entropy_ledger(support, fine).classes)),
        ("complete-pair-ledger", "One coarse class retains all six unresolved pairs.", len(closed_distinction_pairs(chemical_entropy_ledger(support, coarse))) == 6),
        ("refinement", "Fine observation refines prefix, and prefix refines the coarse class.", chemical_observation_refines(support, fine, prefix) and chemical_observation_refines(support, prefix, coarse)),
        ("successor", "One fresh microstate updates its class without changing prior identities.", append_microstate_preserves_ledger(support, prefix, fresh, HeldLabel("chemical-macro-observation", "a"))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "ChemicalEntropyClass", "ChemicalEntropyLedger", "append_microstate_preserves_ledger",
    "chemical_entropy_ledger", "chemical_observation_refines", "closed_distinction_pairs",
)
