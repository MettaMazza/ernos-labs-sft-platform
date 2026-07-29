import json
from fractions import Fraction

import pytest

import sft.chemistry.pericyclic_missing_measurement_reconstruction_v3 as reconstruction


def test_all_four_missing_identities_remain_present_and_active() -> None:
    rows = reconstruction.reconstruct_missing_identity_measurements()
    assert [row.ordinal for row in rows] == [6, 19, 27, 30]
    assert [row.adduct_pair for row in rows] == [
        "5CPD-n, 5CPD-x",
        "12BD-n, 12BD-x",
        "17BD-n, 17BD-x",
        "18CPD-n, 18CPD-x",
    ]
    assert all(not row.scientific_result_retired for row in rows)
    assert all(not row.calculated_ratio_used_as_measurement for row in rows)


def test_condition_distinguished_measurement_census_is_complete() -> None:
    rows = reconstruction.reconstruct_missing_identity_measurements()
    assert sum(len(row.measured_ratios) for row in rows) == 21
    assert sum(len(row.structural_measurements) for row in rows) == 4
    assert all(
        not observation.exact_target_condition
        for row in rows
        for observation in (*row.measured_ratios, *row.structural_measurements)
    )


def test_ordinal_six_preserves_all_seventeen_primary_ratios_exactly() -> None:
    row = reconstruction.reconstruct_missing_identity_measurements()[0]
    assert len(row.measured_ratios) == 17
    assert [item.first_to_second for item in row.measured_ratios[:7]] == [
        Fraction(77, 20),
        Fraction(17, 2),
        Fraction(25, 1),
        Fraction(89, 10),
        Fraction(52, 5),
        Fraction(28, 1),
        Fraction(22, 1),
    ]
    assert row.exact_condition_ratio_status.startswith("active-")


def test_structure_only_sources_are_not_promoted_to_stereochemical_ratios() -> None:
    rows = reconstruction.reconstruct_missing_identity_measurements()
    assert len(rows[1].structural_measurements) == 1
    assert not rows[1].measured_ratios
    assert len(rows[2].structural_measurements) == 2
    assert not rows[2].measured_ratios
    assert rows[1].exact_condition_ratio_status.startswith("active-")
    assert rows[2].exact_condition_ratio_status.startswith("active-")


def test_ordinal_thirty_keeps_four_populations_distinct() -> None:
    row = reconstruction.reconstruct_missing_identity_measurements()[3]
    assert [item.first_to_second for item in row.measured_ratios] == [
        Fraction(4, 1),
        Fraction(41, 9),
        Fraction(8145, 1822),
        Fraction(3, 1),
    ]
    assert len({item.condition_identity for item in row.measured_ratios}) == 4


def test_custody_metadata_change_halts_before_reconstruction(tmp_path, monkeypatch) -> None:
    document = json.loads(reconstruction.MANIFEST.read_text(encoding="utf-8"))
    document["all_registered_sources_captured"] = False
    manifest = tmp_path / "source-manifest-v3.json"
    manifest.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setattr(reconstruction, "MANIFEST", manifest)
    with pytest.raises(ValueError, match="custody changed"):
        reconstruction.reconstruct_missing_identity_measurements()


def test_independent_reconstruction_matches_primary_boundary() -> None:
    artifact = reconstruction.SNAPSHOT / "complete-missing-measurement-reconstruction-v3.json"
    document = json.loads(artifact.read_text(encoding="utf-8"))
    assert document["identity_count"] == 4
    assert document["measured_ratio_count"] == 21
    assert document["structural_measurement_count"] == 4
    assert document["scientific_results_retired"] == 0
    assert document["calculated_ratios_used_as_measurements"] == 0
    assert [row["ordinal"] for row in document["identities"]] == [6, 19, 27, 30]
    assert all(row["exact_condition_obligation_active"] for row in document["identities"])
