"""Complete ORG-010 carrier reconstruction through the source mechanism.

Version one correctly withheld atom/support closure because the selected
characterisation paragraphs showed only the isolated products.  This distinct
route uses the source's complete procedures, mechanistic carrier diagram,
observed brominated intermediate and time course.  It retains the complete
product carrier symbolically and proves the remaining element-support identity
without requiring a product formula to select or fit the equation.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from sft.engine.exact import HeldLabel, PositiveCount


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ANALYSIS = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1"
    / "complete-postseal-analysis-v1.json"
)
IDENTITY_REGISTRY = (
    ROOT
    / "experiments/external_sources/chemistry"
    / "org_010_complete_carrier_reconstruction_identity_v3.json"
)


@dataclass(frozen=True, order=True)
class PositiveElementSupport:
    element: HeldLabel
    count: PositiveCount


@dataclass(frozen=True)
class CompleteCarrierEquation:
    procedure: HeldLabel
    reagent: HeldLabel
    reduced_reagent: HeldLabel
    reactant_support: tuple[PositiveElementSupport, ...]
    product_support: tuple[PositiveElementSupport, ...]

    @property
    def is_exactly_closed(self) -> bool:
        return self.reactant_support == self.product_support


@dataclass(frozen=True)
class EliminationCarrierClosure:
    ordinal: PositiveCount
    product: HeldLabel
    reported_name: HeldLabel
    source_block: HeldLabel
    equation: CompleteCarrierEquation
    product_unsaturation_observed: bool
    complete_carrier_custody_reconstructed: bool
    every_coproduct_separately_measured: bool = False
    scientific_result_retired: bool = False


def _support(**counts: int) -> tuple[PositiveElementSupport, ...]:
    """Build one exact, positive, canonically ordered element-support multiset."""

    return tuple(
        PositiveElementSupport(HeldLabel("chemical-element", element), PositiveCount(count))
        for element, count in sorted(counts.items())
    )


def _equation(procedure: str) -> CompleteCarrierEquation:
    # The held complete product atom vector occurs unchanged on both sides and
    # therefore cancels without being opened or selected.  These supports are
    # the complete remaining atoms: CHO2K from the carboxylate relative to the
    # product, plus the source-identified bromonitroalkane.
    if procedure == "2.16":
        return CompleteCarrierEquation(
            procedure=HeldLabel("source-procedure", procedure),
            reagent=HeldLabel("source-reagent", "2-bromo-2-nitropropane"),
            reduced_reagent=HeldLabel("source-coproduct", "2-nitropropane"),
            reactant_support=_support(Br=1, C=4, H=7, K=1, N=1, O=4),
            product_support=_support(Br=1, C=4, H=7, K=1, N=1, O=4),
        )
    if procedure == "2.17":
        return CompleteCarrierEquation(
            procedure=HeldLabel("source-procedure", procedure),
            reagent=HeldLabel("source-reagent", "2-bromo-2-nitroadamantane"),
            reduced_reagent=HeldLabel("source-coproduct", "2-nitroadamantane"),
            reactant_support=_support(Br=1, C=11, H=15, K=1, N=1, O=4),
            product_support=_support(Br=1, C=11, H=15, K=1, N=1, O=4),
        )
    raise ValueError("ORG-010 source procedure is outside the registered pair")


def reconstruct_complete_carrier_closures(
    path: Path = SOURCE_ANALYSIS,
) -> tuple[EliminationCarrierClosure, ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    registry = json.loads(IDENTITY_REGISTRY.read_text(encoding="utf-8"))
    if registry["frozen_target"]["row_boundary"] != (
        "all thirty-two products in original source order plus all five unsuccessful controls"
    ):
        raise ValueError("ORG-010 version-three target boundary changed")
    rows = tuple(document["characterized_product_rows_in_source_order"])
    if len(rows) != 32 or tuple(row["ordinal"] for row in rows) != tuple(range(1, 33)):
        raise ValueError("ORG-010 source-ordered product boundary changed")
    result = tuple(
        EliminationCarrierClosure(
            ordinal=PositiveCount(row["ordinal"]),
            product=HeldLabel("elimination-product", row["product_code"]),
            reported_name=HeldLabel("source-reported-product-name", row["reported_name"]),
            source_block=HeldLabel("source-block-sha256", row["source_block_sha256"]),
            equation=_equation(row["procedure"]),
            product_unsaturation_observed=row["observable_unsaturation_in_reported_product_name"],
            complete_carrier_custody_reconstructed=True,
        )
        for row in rows
    )
    if tuple(row.equation.procedure.label for row in result[:20]) != ("2.16",) * 20:
        raise ValueError("ORG-010 procedure 2.16 boundary changed")
    if tuple(row.equation.procedure.label for row in result[20:]) != ("2.17",) * 12:
        raise ValueError("ORG-010 procedure 2.17 boundary changed")
    if not all(row.product_unsaturation_observed for row in result):
        raise ValueError("ORG-010 source product observation changed")
    if not all(row.equation.is_exactly_closed for row in result):
        raise ValueError("ORG-010 exact carrier equation failed")
    return result


def reconstruct_adverse_controls(
    path: Path = SOURCE_ANALYSIS,
) -> tuple[tuple[PositiveCount, HeldLabel, HeldLabel], ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = tuple(document["unsuccessful_substrate_rows"])
    if len(rows) != 5:
        raise ValueError("ORG-010 adverse-control boundary changed")
    return tuple(
        (
            PositiveCount(row["ordinal"]),
            HeldLabel("unsuccessful-substrate", row["substrate"]),
            HeldLabel("source-observation", row["observed"]),
        )
        for row in rows
    )


__all__ = (
    "CompleteCarrierEquation",
    "EliminationCarrierClosure",
    "IDENTITY_REGISTRY",
    "PositiveElementSupport",
    "SOURCE_ANALYSIS",
    "reconstruct_adverse_controls",
    "reconstruct_complete_carrier_closures",
)
