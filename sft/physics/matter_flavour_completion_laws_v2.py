"""Dependency-corrected specifications after the retained V1 admission halt.

The first two V1 completion claims are immutable.  The rejected mass-ratio
attempt named a nonexistent dependency and is preserved.  This successor binds
that law to the admitted discrete-induction claim without changing its
mathematical statement, candidate grammar, survivor or witnesses.
"""

from __future__ import annotations

from dataclasses import replace

from sft.physics.matter_flavour_completion_laws_v1 import (
    CONFINEMENT_LIFT_SPEC,
    GENERATION_DEPTH_SPEC,
    INTER_ENTRY_SPEC,
    MASS_RATIO_FAMILY_SPEC,
    MIRROR_MASS_SPEC,
)


MASS_RATIO_FAMILY_SPEC_V2 = replace(
    MASS_RATIO_FAMILY_SPEC,
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-FOUNDATION-COUNT-001",
        "SFT-MATH-DISCRETE-001",
    ),
)

REMAINING_SPECS = (
    MASS_RATIO_FAMILY_SPEC_V2,
    MIRROR_MASS_SPEC,
    INTER_ENTRY_SPEC,
    GENERATION_DEPTH_SPEC,
    CONFINEMENT_LIFT_SPEC,
)
SPEC_BY_ID = {spec.claim_id: spec for spec in REMAINING_SPECS}
for _spec in REMAINING_SPECS:
    _spec.validate()


__all__ = ("MASS_RATIO_FAMILY_SPEC_V2", "REMAINING_SPECS", "SPEC_BY_ID")
