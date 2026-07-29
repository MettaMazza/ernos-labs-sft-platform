from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.tesla_resonance_family_empirical_v1 import (
    ObservationalEmpiricalPhysicsProgram,
    SOURCE_IDS,
    SPEC,
)
from sft.physics.tesla_resonance_family_empirical_validation_v1 import TeslaResonanceFamilyMeasurementValidator


ROOT = Path(__file__).resolve().parents[1]


def test_empirical_family_exhausts_complete_comparison_grammar():
    rows = candidate_rows(SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert len(SPEC.target_rows) == len(SOURCE_IDS) == 5


def test_direct_source_certificate_retains_every_favorable_and_adverse_row():
    certificate = TeslaResonanceFamilyMeasurementValidator(ROOT).direct_source_certificate()
    assert certificate["all_passed"]
    assert certificate["observation_row_count"] == 5
    assert certificate["unsupported_power_inference_rejected"]
    assert len(certificate["checks"]) == 9


def test_empirical_claim_is_observational_and_depends_on_complete_formal_chain():
    assert tuple(SPEC.dependencies[:4]) == (
        "SFT-PHYS-TESLA-BOUNDED-CAVITY-078",
        "SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079",
        "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080",
        "SFT-PHYS-TESLA-RESONANT-TRANSFER-081",
    )
    registration = ObservationalEmpiricalPhysicsProgram(SPEC, "sha256:" + "1" * 64).registration
    assert registration.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
