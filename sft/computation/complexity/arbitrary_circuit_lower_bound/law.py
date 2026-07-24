"""Arbitrary admitted Fold-circuit lower-bound law."""

from sft.computation.lineage_laws import LINEAGE_SPECS

SPEC = next(item for item in LINEAGE_SPECS if item.claim_id == "SFT-COMP-CPLX-ARBITRARY-CIRCUIT-LOWER-BOUND-002")

__all__ = ("SPEC",)
