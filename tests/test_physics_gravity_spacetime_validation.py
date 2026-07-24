from pathlib import Path

from sft.physics.gravity_spacetime_validation_v1 import (
    CLOCK_LABEL,
    HORIZON_LABEL,
    NONSTANDARD_LABEL,
    WAVE_LABEL,
    authoritative_record,
    classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_complete_gravity_spacetime_source_vector_and_classifications():
    record = authoritative_record(ROOT)
    assert len(record["sources"]) == 6
    assert len(record["unfavorable_and_scope_controls"]) == 6
    assert classification(ROOT, "weak_gravity_clock_equivalence") == CLOCK_LABEL
    assert classification(ROOT, "gravitational_waves") == WAVE_LABEL
    assert classification(ROOT, "horizons_information") == HORIZON_LABEL
    assert classification(ROOT, "nonstandard_spacetime") == NONSTANDARD_LABEL
