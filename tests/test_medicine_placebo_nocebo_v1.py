from fractions import Fraction

from sft.medicine.placebo_nocebo_laws_v1 import SPECS, clinical_record, expectation_fibre, reachable_state_record
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_complete_products_have_one_survivor():
    for spec in SPECS.values():
        rows = candidate_rows(spec)
        assert len(rows) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1


def test_expectation_fibre_is_exact():
    row = expectation_fibre()
    assert row["bodily_carrier"] == Fraction(1, 4)
    assert row["expectation_carrier"] == Fraction(3, 4)
    assert row["bodily_image"] == row["expectation_image"] == Fraction(1, 2)
    assert row["joint_carrier"] == 1


def test_expectation_does_not_create_a_state():
    row = reachable_state_record()
    assert row["state_set_preserved"]
    assert not row["new_state_created"]
    assert row["unavailable-cure"] == "structurally-absent"


def test_objective_and_report_records_are_distinct():
    row = clinical_record()
    assert len(row["fields"]) == len(set(row["fields"])) == 8
    assert len(row["pairwise_distinctions"]) == 28
    assert not row["report_only_is_objective"]
    assert row["adverse_absent_unresolved_retained"]
