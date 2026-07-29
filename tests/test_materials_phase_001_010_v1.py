from fractions import Fraction
from pathlib import Path

from sft.materials.phase_001_010_external_v1 import load_complete_vector
from sft.materials.phase_001_010_laws_v1 import ORDER, SPECS, kinetic_arrest, order_disorder, phase_fraction_ledger, reconstructive_transform, spinodal_organization, tie_line_partition, time_temperature_path
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_complete_phase_family_has_one_survivor_per_grammar():
    assert len(ORDER) == 10
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        rows = candidate_rows(spec)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1
        assert all(witness.passed for witness in spec.witnesses)


def test_exact_native_phase_boundaries():
    assert phase_fraction_ledger((("a", 2), ("b", 3), ("c", 5)))["recomposes_one"]
    assert tie_line_partition(2, 4, 8)["left_phase_part"] == Fraction(2, 3)
    assert spinodal_organization(2, 5, 3)["orientation"] == "separation-amplifying"
    assert reconstructive_transform(("a", "b", "c"), (("a", "b"),), (("a", "c"),))["topology_changed"]
    assert order_disorder(("a", "b", "a", "b"), ("a", "a", "b", "b"))["matching_part"] == Fraction(1, 2)
    assert kinetic_arrest(5, 2, ("glass", "glass"))["status"].startswith("kinetically-arrested")
    assert time_temperature_path(((1, 8, 0, 8), (2, 7, 2, 8)))["records"][0][2] is None


def test_complete_phase_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 10
    assert vector["captured_source_count"] == 11
    assert vector["unavailable_source_count"] == 0
    assert vector["all_favourable_adverse_absent_unavailable_unresolved_rows_preserved"] is True
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
