"""Dependency-identity-corrected 081 specification; V1 remains hash-bound."""

from dataclasses import replace

from sft.physics.tesla_resonance_family_law_v1 import RESONANT_TRANSFER_SPEC


SPEC = replace(
    RESONANT_TRANSFER_SPEC,
    dependencies=(
        "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080",
        "SFT-PHYS-WAVE-RESONANCE-001",
        "SFT-PHYS-MECH-WORK-ENERGY-001",
        "SFT-PHYS-MECH-POWER-001",
        "SFT-PHYS-THERMO-FIRST-LAW-001",
    ),
)


__all__ = ("SPEC",)
