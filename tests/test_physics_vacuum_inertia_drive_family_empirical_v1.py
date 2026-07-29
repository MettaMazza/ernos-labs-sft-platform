from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.vacuum_inertia_drive_family_empirical_v1 import (
    ObservationalEmpiricalPhysicsProgram,
    SOURCE_IDS,
    SPEC,
)
from sft.physics.vacuum_inertia_drive_family_empirical_validation_v1 import VacuumInertiaDriveFamilyMeasurementValidator


ROOT = Path(__file__).resolve().parents[1]


def test_empirical_family_exhausts_complete_comparison_grammar():
    rows = candidate_rows(SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert len(SPEC.target_rows) == len(SOURCE_IDS) == 5


def test_direct_source_certificate_retains_favorable_adverse_and_absent_rows():
    certificate = VacuumInertiaDriveFamilyMeasurementValidator(ROOT).direct_source_certificate()
    assert certificate["all_passed"]
    assert certificate["source_count"] == 5
    assert certificate["apparatus_measurement_not_invented"]
    assert certificate["formal_channel_not_falsified_by_absent_apparatus_row"]
    assert len(certificate["checks"]) == 10


def test_empirical_claim_is_observational_and_depends_on_complete_formal_chain():
    assert tuple(SPEC.dependencies[:4]) == (
        "SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083",
        "SFT-PHYS-VACUUM-INERTIA-COVARIATION-084",
        "SFT-PHYS-VACUUM-INERTIA-POSITIVE-FLOOR-085",
        "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086",
    )
    registration = ObservationalEmpiricalPhysicsProgram(SPEC, "sha256:" + "1" * 64).registration
    assert registration.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
