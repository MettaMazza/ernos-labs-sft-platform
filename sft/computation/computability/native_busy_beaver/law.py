"""Unrestricted native Fold Busy-Beaver law."""

from sft.computation.lineage_laws import LINEAGE_SPECS

SPEC = next(item for item in LINEAGE_SPECS if item.claim_id == "SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002")

__all__ = ("SPEC",)
