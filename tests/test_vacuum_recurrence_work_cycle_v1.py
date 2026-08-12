from fractions import Fraction

import pytest

from sft.engineering.vacuum_recurrence_cycle_protocol_v1 import RECORD, SPEC
from sft.physics.structural_constants import candidate_rows
from sft.physics.vacuum_recurrence_work_cycle_law_v1 import (
    SPECS,
    complete_boundary_record,
    finite_repetition,
    recurrence_work_cycle,
)


def test_complete_registered_grammars_have_one_of_256_survivors():
    for spec in (*SPECS.values(), SPEC):
        rows = candidate_rows(spec)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert all(witness.passed for witness in spec.witnesses)


def test_fold_recurrence_cycle_restores_half_and_retains_two_sixths():
    record = recurrence_work_cycle()
    assert record["initial_vacuum"] == record["final_vacuum"] == Fraction(1, 2)
    assert record["outward_retained_vacuum"] == Fraction(1, 3)
    assert record["recurrent_vacuum"] == Fraction(2, 3)
    assert record["work_outputs"] == (Fraction(1, 6), Fraction(1, 6))
    assert record["combined_work"] == Fraction(1, 3)


def test_positive_finite_repetition_retains_one_pair_per_cycle():
    record = finite_repetition(4)
    assert record["cycle_count"] == 4
    assert len(record["work_pairs"]) == 4
    assert record["all_pairs_exact"] is True
    assert record["final_vacuum"] == Fraction(1, 2)
    with pytest.raises(ValueError):
        finite_repetition(0)


def test_complete_boundary_separates_reset_subsystem_from_outputs():
    record = complete_boundary_record()
    assert record["cyclic_subsystem_restored"] is True
    assert record["global_state_restored"] is False
    assert record["controller_initial"] == record["controller_final"]
    assert record["work_outputs"] == (Fraction(1, 6), Fraction(1, 6))
    assert len(record["audit_output"]) == 5


def test_engineering_protocol_retains_states_ledgers_controls_and_halts():
    assert len(RECORD["required_states"]) == 9
    assert len(RECORD["independent_ledgers"]) == 6
    assert len(RECORD["controls"]) == 8
    assert len(RECORD["stop_conditions"]) == 7
    assert RECORD["result_classes"] == ("favourable", "adverse", "absent", "unresolved")
    assert str(RECORD["outcome_status"]).startswith("unperformed")
