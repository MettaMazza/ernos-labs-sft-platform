"""Conditional conventional decision-family transport law."""

from sft.computation.correspondence_return_laws import RETURN_SPECS

SPEC = next(item for item in RETURN_SPECS if item.claim_id == "SFT-COMP-CPLX-CONVENTIONAL-TRANSLATION-003")

__all__ = ("SPEC",)
