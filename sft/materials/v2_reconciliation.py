"""Question-level reconciliation of the V2 Materials surface.

This is a coverage guard, never a proof import.  It records the earlier
questions that V3 had to regenerate.  No V2 answer, number or certificate is
available to the target-blind Materials derivation.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.materials.obligations import MATERIALS_OBLIGATIONS


@dataclass(frozen=True)
class V2MaterialsQuestion:
    step: int
    question: str
    required_v3_claim_ids: tuple[str, ...]
    routed_remainder: str = ""


V2_MATERIALS_QUESTIONS = (
    V2MaterialsQuestion(47, "cubic lattice and six nearest neighbours", ("SFT-MAT-CRYST-CUBIC-COORDINATION-001",)),
    V2MaterialsQuestion(49, "crystalline order and crystallographic restriction", ("SFT-MAT-CRYST-TRANSLATION-001", "SFT-MAT-CRYST-ROTATION-RESTRICTION-001", "SFT-MAT-CRYST-SYSTEMS-001", "SFT-MAT-CRYST-BRAVAIS-001")),
    V2MaterialsQuestion(52, "paired-carrier superconducting response", ("SFT-MAT-SC-PAIR-001", "SFT-MAT-SC-ZERO-RESISTANCE-001", "SFT-MAT-SC-MEISSNER-001", "SFT-MAT-SC-FLUX-QUANTIZATION-001", "SFT-MAT-SC-JOSEPHSON-001")),
    V2MaterialsQuestion(54, "electronic bands, gaps and transport classes", ("SFT-MAT-ELEC-BAND-GAP-001", "SFT-MAT-ELEC-CONDUCTOR-CLASS-001")),
    V2MaterialsQuestion(72, "three acoustic lattice-excitation branches", ("SFT-MAT-CRYST-PHONON-001",)),
    V2MaterialsQuestion(74, "aligned and opposed magnetic order", ("SFT-MAT-MAG-FERROMAGNETISM-001", "SFT-MAT-MAG-ANTIFERROMAGNETISM-001")),
    V2MaterialsQuestion(75, "semiconductor carrier types, doping and junction balance", ("SFT-MAT-ELEC-CARRIER-DUALITY-001", "SFT-MAT-SEMI-DOPING-001", "SFT-MAT-SEMI-PN-TYPE-001", "SFT-MAT-SEMI-JUNCTION-001", "SFT-MAT-SEMI-TRANSPORT-001")),
    V2MaterialsQuestion(133, "quasicrystalline order without periodic translation", ("SFT-MAT-CRYST-ROTATION-RESTRICTION-001", "SFT-MAT-CRYST-RECIPROCAL-001", "SFT-MAT-CRYST-QUASICRYSTAL-001")),
    V2MaterialsQuestion(137, "superfluid flow and quantized circulation", ("SFT-MAT-SF-SUPERFLUID-001", "SFT-MAT-SF-CIRCULATION-001")),
    V2MaterialsQuestion(143, "topological class and bulk-boundary protection", ("SFT-MAT-TOPO-INVARIANT-001", "SFT-MAT-TOPO-BULK-BOUNDARY-001")),
    V2MaterialsQuestion(193, "elastic, plastic, slip, strength, fracture, fatigue and creep response", ("SFT-MAT-MECH-STRESS-STRAIN-001", "SFT-MAT-MECH-ELASTICITY-001", "SFT-MAT-MECH-PLASTICITY-001", "SFT-MAT-MECH-SLIP-001", "SFT-MAT-MECH-MODULUS-001", "SFT-MAT-MECH-STRENGTH-HARDNESS-001", "SFT-MAT-MECH-FRACTURE-001", "SFT-MAT-MECH-FATIGUE-CREEP-001")),
    V2MaterialsQuestion(291, "quasicrystal component of the mixed materials-and-astrophysics step", ("SFT-MAT-CRYST-QUASICRYSTAL-001",), "Planetary and Tully-Fisher claims are not Materials results and remain assigned to Astronomy and Cosmology."),
)


def validate_v2_materials_reconciliation() -> None:
    obligation_ids = {row.claim_id for row in MATERIALS_OBLIGATIONS}
    steps = tuple(row.step for row in V2_MATERIALS_QUESTIONS)
    if len(steps) != len(set(steps)):
        raise ValueError("V2 Materials reconciliation contains duplicate steps")
    missing = sorted(
        claim_id
        for row in V2_MATERIALS_QUESTIONS
        for claim_id in row.required_v3_claim_ids
        if claim_id not in obligation_ids
    )
    if missing:
        raise ValueError("V2 Materials questions lack V3 obligations: " + ", ".join(missing))
    mixed = next(row for row in V2_MATERIALS_QUESTIONS if row.step == 291)
    if not mixed.routed_remainder:
        raise ValueError("mixed V2 step 291 lacks an explicit non-Materials route")


validate_v2_materials_reconciliation()


__all__ = (
    "V2MaterialsQuestion",
    "V2_MATERIALS_QUESTIONS",
    "validate_v2_materials_reconciliation",
)
