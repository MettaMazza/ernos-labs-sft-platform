"""Versioned ORG-010 carrier-custody reconstruction.

The product-characterisation block establishes product unsaturation, but it
does not contain every reactant and coproduct carrier.  Missing carrier custody
therefore remains an active empirical obligation; it is neither an adverse SFT
result nor a closed balance proof.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1"
    / "complete-postseal-analysis-v1.json"
)


@dataclass(frozen=True)
class EliminationCarrierObligation:
    ordinal: int
    product_code: str
    reported_name: str
    source_block_hash: str
    product_unsaturation_observed: bool
    complete_carrier_custody_observed: bool
    scientific_result_retired: bool = False


def reconstruct_carrier_obligations(path: Path = ANALYSIS) -> tuple[EliminationCarrierObligation, ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = tuple(document["characterized_product_rows_in_source_order"])
    if (
        len(rows) != 32
        or document["characterized_product_count"] != 32
        or document["products_with_observable_unsaturation_count"] != 32
        or document["products_with_full_carrier_balance_in_characterization_block_count"] != 0
        or document["unresolved_complete_carrier_balance_count"] != 32
    ):
        raise ValueError("ORG-010 characterized-product census changed")
    result = tuple(
        EliminationCarrierObligation(
            ordinal=row["ordinal"],
            product_code=row["product_code"],
            reported_name=row["reported_name"],
            source_block_hash=row["source_block_sha256"],
            product_unsaturation_observed=row["observable_unsaturation_in_reported_product_name"],
            complete_carrier_custody_observed=row["full_reactant_byproduct_carrier_present_in_characterization_block"],
        )
        for row in rows
    )
    if tuple(row.ordinal for row in result) != tuple(range(1, 33)):
        raise ValueError("ORG-010 source order changed")
    if not all(row.product_unsaturation_observed for row in result):
        raise ValueError("ORG-010 favorable product-unsaturation record changed")
    if any(row.complete_carrier_custody_observed for row in result):
        raise ValueError("ORG-010 product block unexpectedly supplies complete carrier custody")
    return result


def reconstruct_unsuccessful_controls(path: Path = ANALYSIS) -> tuple[tuple[int, str, str], ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = tuple(document["unsuccessful_substrate_rows"])
    result = tuple((row["ordinal"], row["substrate"], row["observed"]) for row in rows)
    if len(result) != 5 or document["unsuccessful_substrate_count"] != 5:
        raise ValueError("ORG-010 unsuccessful-control census changed")
    return result


__all__ = (
    "ANALYSIS",
    "EliminationCarrierObligation",
    "reconstruct_carrier_obligations",
    "reconstruct_unsuccessful_controls",
)
