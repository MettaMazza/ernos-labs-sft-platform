from pathlib import Path

from sft.physics.vacuum_lineage_validation_v1 import (
    EXTRACTION_LABEL,
    FLOOR_LABEL,
    INERTIA_LABEL,
    POLARIZATION_LABEL,
    authoritative_record,
    extraction_classification,
    floor_classification,
    inertia_classification,
    polarization_classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_complete_authoritative_vacuum_record_and_classifications():
    assert len(authoritative_record(ROOT)["sources"]) == 4
    assert floor_classification(ROOT) == FLOOR_LABEL
    polarization, values = polarization_classification(ROOT)
    assert polarization == POLARIZATION_LABEL
    assert values["low_inverse_lower"] > values["high_inverse_upper"]
    assert inertia_classification(ROOT) == INERTIA_LABEL
    assert extraction_classification(ROOT) == EXTRACTION_LABEL
