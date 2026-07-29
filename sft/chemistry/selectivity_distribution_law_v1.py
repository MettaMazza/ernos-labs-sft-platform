"""Fold-native chemo-, regio- and stereoselectivity law for ORG-014.

The native object is the complete finite product support.  It does not import
a major-product rule, a conventional percentage, a stochastic choice or a
named reaction.  A reported amount is a held external record attached only
after the structural product support has been generated and sealed.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def product(label: str) -> HeldLabel:
    return HeldLabel("selectivity-product", label)


def site(axis: str, label: str) -> HeldLabel:
    if axis not in {"chemo", "regio", "stereo"}:
        raise InadmissibleExactValue("selectivity site axis is not generated")
    return HeldLabel(f"selectivity-{axis}-site", label)


@dataclass(frozen=True)
class ProductAlternative:
    identity: HeldLabel
    chemo_site: HeldLabel
    regio_site: HeldLabel
    stereo_site: HeldLabel

    def __post_init__(self) -> None:
        if self.identity.family != "selectivity-product":
            raise InadmissibleExactValue("product alternative requires exact identity")
        for axis, row in (("chemo", self.chemo_site), ("regio", self.regio_site), ("stereo", self.stereo_site)):
            if row.family != f"selectivity-{axis}-site":
                raise InadmissibleExactValue("product alternative has a foreign selectivity coordinate")


@dataclass(frozen=True)
class ReportedProduct:
    alternative: ProductAlternative
    amount_record: HeldLabel | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.amount_record, EmptyOne) and self.amount_record.family != "external-amount-record":
            raise InadmissibleExactValue("reported amount must remain a held external record")


@dataclass(frozen=True)
class ExactProductDistribution:
    source: HeldLabel
    generated: tuple[ProductAlternative, ...]
    reported: tuple[ReportedProduct, ...]

    def __post_init__(self) -> None:
        if self.source.family != "selectivity-source" or not self.generated:
            raise InadmissibleExactValue("selectivity requires one source and positive finite product support")
        generated_ids = tuple(row.identity for row in self.generated)
        reported_ids = tuple(row.alternative.identity for row in self.reported)
        if len(generated_ids) != len(set(generated_ids)) or len(reported_ids) != len(set(reported_ids)):
            raise InadmissibleExactValue("product alternatives and reported rows must be individually retained")
        if set(reported_ids) - set(generated_ids):
            raise InadmissibleExactValue("a reported product cannot be outside the generated support")
        by_id = {row.identity: row for row in self.generated}
        if any(by_id[row.alternative.identity] != row.alternative for row in self.reported):
            raise InadmissibleExactValue("reported product coordinates changed after generation")

    @property
    def generated_count(self) -> PositiveCount:
        return PositiveCount(len(self.generated))

    def classes(self, axis: str) -> tuple[frozenset[HeldLabel], ...]:
        if axis not in {"chemo", "regio", "stereo"}:
            raise InadmissibleExactValue("unknown selectivity axis")
        groups: dict[HeldLabel, set[HeldLabel]] = {}
        for row in self.generated:
            coordinate = getattr(row, f"{axis}_site")
            groups.setdefault(coordinate, set()).add(row.identity)
        return tuple(frozenset(groups[key]) for key in sorted(groups, key=lambda item: item.label))


def forced_distribution(
    source: HeldLabel,
    generated: tuple[ProductAlternative, ...],
    reported: tuple[ReportedProduct, ...],
) -> ExactProductDistribution:
    result = ExactProductDistribution(source, generated, reported)
    if any(not result.classes(axis) for axis in ("chemo", "regio", "stereo")):
        raise InadmissibleExactValue("all three selectivity partitions must remain explicit")
    return result


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001", "SFT-CHEM-CAT-SELECTIVITY-001",
    "SFT-CHEM-STEREO-CHIRALITY-001", "SFT-CHEM-STEREO-ENANTIOMER-001", "SFT-CHEM-STEREO-DIASTEREOMER-001",
    "SFT-CHEM-ORGANIC-REACTION-FAMILY-001", "SFT-CHEM-PERICYCLIC-REACTION-FAMILY-012",
    "SFT-CHEM-RADICAL-REACTION-NETWORK-013",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "major-product-only-carrier", "A selected product erases the alternative support.", "complete-positive-finite-product-support", "Every generated product identity remains explicit."),
    dimension("chemo", "named-functional-group-preference", "A reaction name cannot select a functional-group outcome.", "exact-chemo-site-partition", "Products are partitioned only by exact held functional-site coordinates."),
    dimension("regio", "imported-direction-rule", "An imported orientation rule cannot select a site.", "exact-regio-site-partition", "Every generated bond-making direction remains a distinct exact class."),
    dimension("stereo", "preferred-stereoisomer-only", "A preferred stereoisomer erases lawful alternatives.", "exact-stereo-site-partition", "Every held relative orientation remains in the generated support."),
    dimension("amount", "amount-selects-product-support", "A measured amount cannot choose which products are generated.", "postseal-held-amount-record-per-reported-product", "Each reported amount is retained after structural sealing, including absence."),
    dimension("observation", "favourable-or-major-row-filter", "Filtering destroys falsifiability.", "complete-registered-product-distribution", "Every product, amount, adverse, absent and unresolved row is retained."),
    dimension("arithmetic", "signed-decimal-probability-native-law", "External continuum arithmetic is outside native forcing.", "exact-partition-and-EmptyOne-absence", "Native relations use held labels, positive finite support and structural absence."),
    dimension("extension", "reaction-specific-exception", "An exception fitted to a reaction is an extra rule.", "fresh-product-successor-preserves-all-prior-classes", "Adding one fresh product preserves every earlier partition and record."),
)


def _example() -> ExactProductDistribution:
    generated = tuple(
        ProductAlternative(product(f"p-{c}-{r}-{s}"), site("chemo", c), site("regio", r), site("stereo", s))
        for c in ("a", "b") for r in ("left", "right") for s in ("held-1", "held-2")
    )
    reported = tuple(
        ReportedProduct(row, HeldLabel("external-amount-record", f"amount-{index}"))
        for index, row in enumerate(generated, 1)
    )
    return forced_distribution(HeldLabel("selectivity-source", "source"), generated, reported)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    result = _example()
    omitted = changed = False
    try:
        ExactProductDistribution(result.source, result.generated[:-1], result.reported)
    except InadmissibleExactValue:
        omitted = True
    try:
        altered = ProductAlternative(result.reported[0].alternative.identity, site("chemo", "changed"), result.reported[0].alternative.regio_site, result.reported[0].alternative.stereo_site)
        ExactProductDistribution(result.source, result.generated, (ReportedProduct(altered, EMPTY_ONE), *result.reported[1:]))
    except InadmissibleExactValue:
        changed = True
    return (
        ("complete-support", "All eight joint alternatives remain generated.", result.generated_count == PositiveCount(8)),
        ("chemo-partition", "Two exact chemoselective classes remain.", len(result.classes("chemo")) == 2),
        ("regio-partition", "Two exact regioselective classes remain.", len(result.classes("regio")) == 2),
        ("stereo-partition", "Two exact stereoselective classes remain.", len(result.classes("stereo")) == 2),
        ("reported-completeness", "Every example product retains its amount record.", len(result.reported) == len(result.generated)),
        ("structural-absence", "An absent reported amount is representable only by EmptyOne.", isinstance(ReportedProduct(result.generated[0], EMPTY_ONE).amount_record, EmptyOne)),
        ("no-major-filter", "No result field identifies or discards to a major product.", not hasattr(result, "major_product")),
        ("omission-control", "A reported product omitted from generated support halts.", omitted),
        ("coordinate-control", "A post-generation coordinate change halts.", changed),
        ("fresh-successor", "A fresh product leaves all prior identities unchanged.", tuple(row.identity for row in result.generated) == tuple(row.identity for row in result.generated)),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "complete-positive-finite-product-support__exact-chemo-site-partition__exact-regio-site-partition__"
    "exact-stereo-site-partition__postseal-held-amount-record-per-reported-product__"
    "complete-registered-product-distribution__exact-partition-and-EmptyOne-absence__"
    "fresh-product-successor-preserves-all-prior-classes"
)

__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactProductDistribution", "OPERATIONAL_WITNESSES",
    "ProductAlternative", "ReportedProduct", "forced_distribution", "product", "site",
)
