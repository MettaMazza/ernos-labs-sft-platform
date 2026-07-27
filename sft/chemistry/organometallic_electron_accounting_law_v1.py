"""Fold-native organometallic electron-accounting law (INORG-011)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


PairSupport = Union[EmptyOne, tuple[tuple[HeldLabel, HeldLabel], ...]]


def forced_spd_capacity() -> PositiveCount:
    s_width = PositiveCount(2)
    p_width = PositiveCount(6)
    d_width = PositiveCount(10)
    sp_width = PositiveCount(s_width.value + p_width.value)
    return PositiveCount(sp_width.value + d_width.value)


def complete_pairs(prefix: str, pair_count: PositiveCount) -> tuple[tuple[HeldLabel, HeldLabel], ...]:
    return tuple(
        (HeldLabel("held-electron-occurrence", f"{prefix}-{index}-fibre-a"), HeldLabel("held-electron-occurrence", f"{prefix}-{index}-fibre-b"))
        for index in range(1, pair_count.value + 1)
    )


@dataclass(frozen=True)
class ExactOrganometallicElectronAccount:
    entity: HeldLabel
    nonbonded_pairs: PairSupport
    bond_pairs: PairSupport
    complete_electron_count: PositiveCount
    capacity: PositiveCount
    capacity_relation: HeldLabel
    magnetic_class: HeldLabel

    def __post_init__(self) -> None:
        if self.entity.family != "organometallic-entity":
            raise InadmissibleExactValue("electron account requires one retained organometallic entity")
        supports = tuple(() if isinstance(rows, EmptyOne) else rows for rows in (self.nonbonded_pairs, self.bond_pairs))
        pairs = supports[0] + supports[1]
        if not pairs:
            raise InadmissibleExactValue("an empty account must be structural EmptyOne, not a positive electron account")
        flat = tuple(cell for pair in pairs for cell in pair)
        if any(len(pair) != 2 or pair[0].label.removesuffix("fibre-a") != pair[1].label.removesuffix("fibre-b") for pair in pairs):
            raise InadmissibleExactValue("stable diamagnetic account requires complete complementary fibre pairs")
        if len(set(flat)) != len(flat) or self.complete_electron_count.value != len(flat):
            raise InadmissibleExactValue("electron count must equal complete distinct held support")
        if self.capacity != forced_spd_capacity():
            raise InadmissibleExactValue("capacity must be generated from exact s, p and d support widths")
        expected = "capacity-complete" if self.complete_electron_count == self.capacity else "capacity-incomplete"
        if self.complete_electron_count.value > self.capacity.value or self.capacity_relation != HeldLabel("capacity-relation", expected):
            raise InadmissibleExactValue("electron support exceeds or misstates the forced capacity")
        if self.magnetic_class != HeldLabel("magnetic-class", "diamagnetic"):
            raise InadmissibleExactValue("complete pair support forces the diamagnetic held class")


def forced_electron_account(entity: str, nonbonded_pairs: PairSupport, bond_pairs: PairSupport) -> Union[EmptyOne, ExactOrganometallicElectronAccount]:
    if isinstance(nonbonded_pairs, EmptyOne) and isinstance(bond_pairs, EmptyOne):
        return EMPTY_ONE
    supports = tuple(() if isinstance(rows, EmptyOne) else rows for rows in (nonbonded_pairs, bond_pairs))
    count = PositiveCount(len(tuple(cell for pair in supports[0] + supports[1] for cell in pair)))
    capacity = forced_spd_capacity()
    relation = "capacity-complete" if count == capacity else "capacity-incomplete"
    return ExactOrganometallicElectronAccount(
        HeldLabel("organometallic-entity", entity), nonbonded_pairs, bond_pairs, count, capacity,
        HeldLabel("capacity-relation", relation), HeldLabel("magnetic-class", "diamagnetic"),
    )


def append_pair(account: ExactOrganometallicElectronAccount, destination: str) -> ExactOrganometallicElectronAccount:
    if account.complete_electron_count == account.capacity:
        raise InadmissibleExactValue("capacity-complete account rejects an additional pair")
    existing = () if isinstance(account.nonbonded_pairs if destination == "nonbonded" else account.bond_pairs, EmptyOne) else (account.nonbonded_pairs if destination == "nonbonded" else account.bond_pairs)
    next_pair = complete_pairs(destination, PositiveCount(len(existing) + 1))[-1]
    if destination == "nonbonded":
        return forced_electron_account(account.entity.label, existing + (next_pair,), account.bond_pairs)
    if destination == "bond":
        return forced_electron_account(account.entity.label, account.nonbonded_pairs, existing + (next_pair,))
    raise InadmissibleExactValue("pair destination must be retained as nonbonded or bond")


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-QUANTUM-SPIN-001", "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-CHEM-ELECTRON-COUNT-SPIN-002", "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    "SFT-CHEM-MOLECULAR-EXCLUSION-EXCHANGE-006", "SFT-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012",
    "SFT-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "free-electron-number", "A free number is detached from the complex.", "one-retained-organometallic-entity", "Every electron account belongs to one retained entity."),
    dimension("support", "selected-valence-electrons", "Selected electrons lose complete occurrence support.", "complete-nonbonded-and-bond-pair-support", "Both account parts retain every complementary pair occurrence."),
    dimension("capacity", "imported-eighteen-rule", "Importing eighteen assumes the target.", "forced-two-plus-six-plus-ten-capacity", "Admitted s, p and d widths force exact capacity 2+6+10=18."),
    dimension("balance", "signed-spin-sum", "A signed sum imports negative proof values.", "complete-complementary-fibre-pairing", "Stable diamagnetic support is organized into complete held fibre pairs."),
    dimension("partition", "oxidation-state-bookkeeping", "Conventional oxidation bookkeeping can change labels without support.", "exact-nonbonded-plus-bond-partition", "The total is the exact disjoint union of nonbonded and bond electron occurrences."),
    dimension("relation", "species-stability-lookup", "A species lookup lets observed stability choose the rule.", "capacity-complete-or-incomplete-held-relation", "Exact support is held as complete or incomplete relative to generated capacity."),
    dimension("comparison", "measured-total-selects-capacity", "An observed count cannot select the capacity.", "postseal-stable-complex-correspondence", "The frozen external rule is compared only after structural sealing."),
    dimension("extension", "complex-specific-exception", "An exception destroys zero-parameter closure.", "pair-successor-until-capacity-then-halt", "Each fresh pair adds twice and capacity-complete support rejects another pair."),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    capacity = forced_spd_capacity()
    complete = forced_electron_account("complete", complete_pairs("nonbonded", PositiveCount(4)), complete_pairs("bond", PositiveCount(5)))
    partial = forced_electron_account("partial", EMPTY_ONE, complete_pairs("bond", PositiveCount(1)))
    successor = append_pair(partial, "bond")
    overflow_rejected = False
    try: append_pair(complete, "bond")
    except InadmissibleExactValue: overflow_rejected = True
    return (
        ("forced-capacity", "Exact admitted widths two, six and ten force capacity eighteen.", capacity.value == 18),
        ("complete-account", "Four nonbonded plus five bond pairs force eighteen and capacity completeness.", complete.complete_electron_count.value == 18 and complete.capacity_relation.label == "capacity-complete"),
        ("pair-successor", "One fresh pair increments the exact count from two to four.", partial.complete_electron_count.value == 2 and successor.complete_electron_count.value == 4),
        ("capacity-control", "A capacity-complete account rejects another pair.", overflow_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "one-retained-organometallic-entity__complete-nonbonded-and-bond-pair-support__forced-two-plus-six-plus-ten-capacity__complete-complementary-fibre-pairing__exact-nonbonded-plus-bond-partition__capacity-complete-or-incomplete-held-relation__postseal-stable-complex-correspondence__pair-successor-until-capacity-then-halt"


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "ExactOrganometallicElectronAccount",
    "append_pair", "complete_pairs", "forced_electron_account", "forced_spd_capacity",
)
