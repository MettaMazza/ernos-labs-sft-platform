from pathlib import Path

import pytest

from sft.chemistry.smithium_return_external_v1 import PREDICTION_LABEL, _source_derived_target
from sft.chemistry.smithium_return_laws_v1 import (
    SPECS,
    decay_channel_ledger,
    ion_ladder,
    joint_detection_record,
    lifetime_identifiability_record,
    positive_entrance_partitions,
    separation_distinction_record,
    spectroscopic_class_record,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def test_whole_family_has_eight_unique_specs_and_complete_products():
    assert len(SPECS) == 8
    assert len(set(SPECS)) == 8
    for spec in SPECS.values():
        spec.validate()
        rows = candidate_rows(spec)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1


def test_synthesis_partitions_are_complete_and_conserving():
    rows = positive_entrance_partitions()
    assert len(rows) == 22_875
    assert rows[0] == (1, 1, 125, 183)
    assert rows[-1] == (125, 183, 1, 1)
    assert all(z1 + z2 == 126 and n1 + n2 == 184 for z1, n1, z2, n2 in rows)


def test_decay_ledger_conserves_each_exact_coordinate():
    ledger = decay_channel_ledger()
    assert ledger["gamma"]["daughter"] == (126, 184, 310)
    assert ledger["alpha"]["daughter"] == (124, 182, 306)
    assert ledger["alpha"]["emitted"] == (2, 2, 4)
    assert sum(ledger["beta-minus"]["daughter"][:2]) == 310
    assert sum(ledger["beta-plus-or-electron-capture"]["daughter"][:2]) == 310
    assert len(ledger["labelled-fission-partitions"]) == 22_875


def test_lifetime_boundary_halts_false_numeric_output():
    row = lifetime_identifiability_record()
    assert row["required_for_numeric_lifetime"] == ("positive-transition-width", "registered-time-unit")
    assert row["numeric_lifetime"] == "unselected-standing-measurement"
    assert row["closed_boundary"] is True


def test_ion_ladder_is_exact_and_complete():
    rows = ion_ladder()
    assert tuple(row["positive_oxidation_count"] for row in rows) == (2, 3, 4, 5, 6, 7, 8)
    assert tuple(row["electron_count"] for row in rows) == (124, 123, 122, 121, 120, 119, 118)
    assert rows[0]["active_configuration"] == ((5, "g", 6),)
    assert rows[-1]["active_configuration"] == ()
    assert rows[-1]["closed_core"] is True


def test_spectroscopy_classes_do_not_fabricate_lines():
    row = spectroscopic_class_record()
    assert (row["conventional_orbital_rank"], row["fold_orbit_rank"]) == (4, 5)
    assert (row["capacity"], row["occupation"], row["holes"]) == (18, 6, 12)
    assert row["electric_dipole_adjacent_classes"] == ("g-to-f", "g-to-h", "f-to-g", "h-to-g")
    assert row["line_energy"] == row["wavelength"] == "unselected-standing-measurement"


def test_separation_and_joint_detection_are_complete_but_scoped():
    separation = separation_distinction_record()
    assert separation["pairwise_count"] == 21
    assert separation["pairwise_state_distinctions"][0] == (2, 3)
    assert separation["pairwise_state_distinctions"][-1] == (7, 8)
    detection = joint_detection_record()
    assert len(detection["required_records"]) == 5
    assert detection["protocol_scope"] == "complete-SFT-identification-record-not-an-IUPAC-minimum-rule"
    assert detection["current_status"] == "standing-unobserved-prediction"


def test_official_sources_reconstruct_frozen_postseal_label():
    label, registry_hash, source_rows, result_classes = _source_derived_target(ROOT)
    assert label == PREDICTION_LABEL
    assert registry_hash.startswith("sha256:")
    assert len(source_rows) == 3
    assert result_classes["favorable_correspondence"]
    assert result_classes["absent"]
    assert result_classes["unresolved"]


def test_invalid_synthesis_coordinate_halts():
    rows = positive_entrance_partitions()
    assert (126, 1, 0, 183) not in rows
    with pytest.raises(ValueError):
        # Structural Chemistry specs reject a missing axis, so a weakened
        # grammar cannot be executed through the family program.
        type(next(iter(SPECS.values())))(**{**next(iter(SPECS.values())).__dict__, "axes": next(iter(SPECS.values())).axes[:-1]}).validate()
