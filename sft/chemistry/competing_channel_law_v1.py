"""Fold-native complete competing-channel branching relation for Chemistry KIN-006."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ProductChannelSupport:
    channel_identity: HeldLabel
    support: PositiveRatio | EmptyOne
    source_row: PositiveCount

    def __post_init__(self) -> None:
        if not isinstance(self.channel_identity, HeldLabel) or self.channel_identity.family != "registered-product-channel":
            raise InadmissibleExactValue("branching relation requires registered product-channel identity")
        if not isinstance(self.support, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("branching relation requires positive support or structural EmptyOne")
        if not isinstance(self.source_row, PositiveCount):
            raise InadmissibleExactValue("branching relation requires positive source-row identity")


@dataclass(frozen=True)
class CompleteChannelRecord:
    reaction_identity: HeldLabel
    condition_identity: HeldLabel
    ordered_channels: tuple[ProductChannelSupport, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reaction_identity, HeldLabel) or self.reaction_identity.family != "registered-reaction":
            raise InadmissibleExactValue("branching relation requires registered reaction identity")
        if not isinstance(self.condition_identity, HeldLabel) or self.condition_identity.family != "held-condition":
            raise InadmissibleExactValue("branching relation requires held condition identity")
        if len(self.ordered_channels) < 2 or any(not isinstance(row, ProductChannelSupport) for row in self.ordered_channels):
            raise InadmissibleExactValue("branching relation requires complete competing-channel word")
        if len({row.channel_identity for row in self.ordered_channels}) != len(self.ordered_channels):
            raise InadmissibleExactValue("branching relation duplicates product-channel identity")
        if tuple(row.source_row.value for row in self.ordered_channels) != tuple(range(1, len(self.ordered_channels) + 1)):
            raise InadmissibleExactValue("branching relation requires complete source order without a gap")
        if not any(isinstance(row.support, PositiveRatio) for row in self.ordered_channels):
            raise InadmissibleExactValue("branching relation requires positive complete support")


@dataclass(frozen=True)
class ExactBranchRow:
    channel_identity: HeldLabel
    source_row: PositiveCount
    retained_support: PositiveRatio | EmptyOne
    share_of_complete_support: PositiveRatio | EmptyOne


@dataclass(frozen=True)
class ExactBranchingRelation:
    reaction_identity: HeldLabel
    condition_identity: HeldLabel
    complete_support: PositiveRatio
    ordered_rows: tuple[ExactBranchRow, ...]
    whole_identity: HeldLabel


def forced_competing_channel_branching(record: CompleteChannelRecord) -> ExactBranchingRelation:
    if not isinstance(record, CompleteChannelRecord):
        raise InadmissibleExactValue("branching relation requires one complete channel record")
    positive = tuple(row.support.fraction for row in record.ordered_channels if isinstance(row.support, PositiveRatio))
    total = sum(positive, Fraction(0, 1))
    if total <= 0:
        raise InadmissibleExactValue("branching relation requires positive complete support")
    complete = PositiveRatio.from_pair(total.numerator, total.denominator)
    rows = []
    for row in record.ordered_channels:
        share = (
            EmptyOne() if isinstance(row.support, EmptyOne)
            else PositiveRatio.from_pair(
                (row.support.fraction / total).numerator,
                (row.support.fraction / total).denominator,
            )
        )
        rows.append(ExactBranchRow(row.channel_identity, row.source_row, row.support, share))
    positive_shares = tuple(row.share_of_complete_support.fraction for row in rows if isinstance(row.share_of_complete_support, PositiveRatio))
    if sum(positive_shares, Fraction(0, 1)) != Fraction(1, 1):
        raise InadmissibleExactValue("complete retained channel partition does not reconstruct One")
    return ExactBranchingRelation(
        record.reaction_identity, record.condition_identity, complete, tuple(rows),
        HeldLabel("complete-channel-whole", "all-registered-product-support-reconstructs-One"),
    )


def complete_channel_append_preserves_prior_rows(record: CompleteChannelRecord, successor: ProductChannelSupport) -> bool:
    if successor.source_row.value != len(record.ordered_channels) + 1:
        raise InadmissibleExactValue("channel successor must be the next complete source row")
    extended = CompleteChannelRecord(record.reaction_identity, record.condition_identity, record.ordered_channels + (successor,))
    prior = forced_competing_channel_branching(record)
    result = forced_competing_channel_branching(extended)
    return (
        tuple(row.channel_identity for row in result.ordered_rows[: len(prior.ordered_rows)])
        == tuple(row.channel_identity for row in prior.ordered_rows)
        and tuple(row.retained_support for row in result.ordered_rows[: len(prior.ordered_rows)])
        == tuple(row.retained_support for row in prior.ordered_rows)
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-INFO-MUTUAL-CONDITIONAL-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011", "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001", "SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002",
    "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003", "SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004",
    "SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("support", "selected-dominant-or-favorable-channel-subset", "Selecting abundant products erases competing support.", "complete-registered-product-channel-support", "Every registered favorable, weak, adverse and absent channel remains held."),
    dimension("whole", "imported-probability-normalization-axiom", "An imported normalization premise could choose the relation.", "exact-sum-of-complete-retained-support", "The retained channel partition itself forces its complete support."),
    dimension("relation", "fitted-or-free-branching-ratio", "A fitted fraction is not forced by the channel record.", "exact-channel-support-over-complete-support", "Exact division of each retained support by the complete support forces every share."),
    dimension("identity", "reaction-condition-or-product-identity-collapsed", "Collapsed identity can combine unrelated products or conditions.", "held-reaction-condition-product-and-source-row-identities", "Every reaction, condition, product and row identity remains held."),
    dimension("absence", "unfavorable-null-or-unresolved-channel-omitted", "Omission can inflate remaining shares.", "structural-EmptyOne-channel-retained-without-invented-value", "An absent reported support remains a registered structural row without a fabricated number."),
    dimension("record", "ratio-answer-only-or-renormalized-table", "An answer-only table cannot reconstruct source support.", "complete-source-ordered-support-share-uncertainty-and-adverse-record", "Every source support, share, uncertainty and adverse row remains auditable."),
    dimension("provenance", "experimental-and-calculated-columns-mixed", "Mixing columns can substitute theory for measurement.", "experimental-vector-separated-from-calculated-and-analysis-disclosures", "Experimental values and all calculation/analysis disclosures remain distinct."),
    dimension("prediction", "branch-value-readable-before-seal-or-corrected-after-release", "Target access or correction can select the result.", "value-free-complete-eight-channel-identity-seal-and-depth-independent-successor", "All eight identities seal before values open; appending one channel retains every earlier identity and support."),
)


EXACT_RESULT = (
    "complete-registered-product-channel-support__exact-sum-of-complete-retained-support__"
    "exact-channel-support-over-complete-support__held-reaction-condition-product-and-source-row-identities__"
    "structural-EmptyOne-channel-retained-without-invented-value__"
    "complete-source-ordered-support-share-uncertainty-and-adverse-record__"
    "experimental-vector-separated-from-calculated-and-analysis-disclosures__"
    "value-free-complete-eight-channel-identity-seal-and-depth-independent-successor"
)


def _record(values: tuple[int | None, ...]) -> CompleteChannelRecord:
    return CompleteChannelRecord(
        HeldLabel("registered-reaction", "competing-products"), HeldLabel("held-condition", "condition-a"),
        tuple(
            ProductChannelSupport(
                HeldLabel("registered-product-channel", f"product-{ordinal}"),
                EmptyOne() if value is None else PositiveRatio.from_pair(value, 1), PositiveCount(ordinal),
            )
            for ordinal, value in enumerate(values, start=1)
        ),
    )


OPERATIONAL_WITNESSES = (
    ("exact-share", "Complete positive support forces every exact channel share.", tuple(row.share_of_complete_support.fraction for row in forced_competing_channel_branching(_record((2, 3))).ordered_rows) == (Fraction(2, 5), Fraction(3, 5))),
    ("whole", "All positive channel shares reconstruct One exactly.", sum(row.share_of_complete_support.fraction for row in forced_competing_channel_branching(_record((2, 3))).ordered_rows) == Fraction(1, 1)),
    ("unfavorable", "A structural absent channel remains in source order without invented support.", isinstance(forced_competing_channel_branching(_record((2, None, 3))).ordered_rows[1].share_of_complete_support, EmptyOne)),
    ("successor", "Appending one complete channel retains every prior identity and raw support.", complete_channel_append_preserves_prior_rows(_record((2, 3)), ProductChannelSupport(HeldLabel("registered-product-channel", "product-3"), PositiveRatio.from_pair(1, 1), PositiveCount(3)))),
)


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES", "CompleteChannelRecord",
    "ExactBranchRow", "ExactBranchingRelation", "ProductChannelSupport", "complete_channel_append_preserves_prior_rows",
    "forced_competing_channel_branching",
)
