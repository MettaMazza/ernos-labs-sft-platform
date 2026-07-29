from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.new_sector_complete_family_empirical_v1 import ObservationalEmpiricalPhysicsProgram, SOURCE_IDS, SPEC
from sft.physics.new_sector_complete_family_empirical_validation_v1 import NewSectorCompleteFamilyMeasurementValidator


ROOT = Path(__file__).resolve().parents[1]


def test_complete_empirical_grammar_and_sources():
    rows = candidate_rows(SPEC)
    assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
    assert len(SPEC.target_rows) == len(SOURCE_IDS) == 5


def test_direct_sources_retain_all_result_types_and_standing_predictions():
    certificate = NewSectorCompleteFamilyMeasurementValidator(ROOT).direct_source_certificate()
    assert certificate["all_passed"]
    assert certificate["source_count"] == 5
    assert certificate["standing_predictions_retained"]
    assert certificate["nonobservation_not_retirement"]
    assert len(certificate["checks"]) == 10


def test_observational_provenance_and_seven_formal_predecessors():
    assert len(SPEC.dependencies[:7]) == 7
    registration = ObservationalEmpiricalPhysicsProgram(SPEC, "sha256:" + "1" * 64).registration
    assert registration.provenance == (ProvenanceClass.OBSERVATIONAL_DERIVATION,)
