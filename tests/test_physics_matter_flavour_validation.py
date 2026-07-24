from pathlib import Path

from sft.physics.matter_flavour_validation_v1 import (
    MAGNETIC_LABEL,
    MAJORANA_LABEL,
    NEUTRINO_LABEL,
    PROTON_LABEL,
    QUARK_CKM_LABEL,
    authoritative_record,
    magnetic_classification,
    majorana_classification,
    neutrino_classification,
    proton_classification,
    quark_ckm_classification,
)


ROOT = Path(__file__).resolve().parents[1]


def test_complete_matter_flavour_postseal_classifications():
    assert len(authoritative_record(ROOT)["sources"]) == 6
    assert quark_ckm_classification(ROOT) == QUARK_CKM_LABEL
    assert proton_classification(ROOT) == PROTON_LABEL
    assert neutrino_classification(ROOT) == NEUTRINO_LABEL
    assert majorana_classification(ROOT) == MAJORANA_LABEL
    assert magnetic_classification(ROOT) == MAGNETIC_LABEL
