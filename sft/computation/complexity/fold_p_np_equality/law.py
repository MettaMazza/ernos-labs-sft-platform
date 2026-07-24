"""Fold-P equals Fold-NP law."""

from sft.computation.lineage_laws import LINEAGE_SPECS

SPEC = next(item for item in LINEAGE_SPECS if item.claim_id == "SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002")

__all__ = ("SPEC",)
