from fractions import Fraction

from sft.chemistry.sequential_mechanism_observation_class_v2 import reconstruct_late_observation_classes


def test_late_states_are_complete_source_observation_classes_not_failed_singletons() -> None:
    rows = reconstruct_late_observation_classes()
    assert len(rows) == 4
    assert rows[0].elapsed_seconds == Fraction(1, 1000)
    assert rows[1].elapsed_seconds == Fraction(17, 1000)
    assert all(not row.unique_atomic_structure_selected for row in rows)
    assert "possible-third-CO-release" in rows[1].members
    assert "possible-CO-rebinding" in rows[1].members


def test_adverse_control_cannot_be_removed_or_relabelled_favorable() -> None:
    rows = reconstruct_late_observation_classes()
    adverse = next(row for row in rows if row.target_id == "KIN-007-SEQUENTIAL-RECORD-16")
    assert adverse.members == ("possible-light-contamination", "reduced-COax-difference-density")
