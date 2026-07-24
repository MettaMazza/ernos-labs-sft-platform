from pathlib import Path

from sft.physics.relativistic_field_validation_v1 import (
    DYNAMICS_LABEL,
    FIELD_LABEL,
    LOOP_LABEL,
    OPTICS_LABEL,
    authoritative_record,
    classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_complete_relativistic_field_record_and_classification():
    record = authoritative_record(ROOT)
    assert len(record["sources"]) == 7
    assert len(record["unfavorable_and_scope_controls"]) == 5
    assert classification(ROOT, "dynamics_and_spectra") == DYNAMICS_LABEL
    assert classification(ROOT, "relativistic_and_electromagnetic_fields") == FIELD_LABEL
    assert classification(ROOT, "optical_operations") == OPTICS_LABEL
    assert classification(ROOT, "finite_loops") == LOOP_LABEL
