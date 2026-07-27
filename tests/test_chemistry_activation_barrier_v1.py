from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.activation_barrier_batch_v1 import ACTIVATION_BARRIER_SPEC
from sft.chemistry.activation_barrier_law_v1 import (
    BarrierPathRecord, BarrierPathState, complete_path_append_preserves_collection,
    external_nonnegative_support, forced_activation_barrier, forced_barrier_collection,
)
from sft.chemistry.activation_barrier_validation_v1 import (
    _identities, _source_rows, exact_activation_barrier_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def path(target: int, species: str, path_id: str, supports: tuple[int | None, ...]) -> BarrierPathRecord:
    return BarrierPathRecord(
        HeldLabel("registered-species", species), HeldLabel("generated-reaction-path", path_id),
        tuple(BarrierPathState(
            HeldLabel("generated-path-state", f"state-{index}"),
            EmptyOne() if value is None else PositiveRatio.from_pair(value, 1),
        ) for index, value in enumerate(supports, start=1)),
        PositiveCount(target), EmptyOne(), EmptyOne(), EmptyOne(),
    )


def test_greatest_positive_path_boundary_is_forced() -> None:
    barrier = forced_activation_barrier(path(1, "a", "p", (None, 2, 5, 3)))
    assert barrier.barrier_support.fraction == Fraction(5)


def test_structural_least_state_and_source_order_are_retained() -> None:
    assert isinstance(external_nonnegative_support("0.00"), EmptyOne)
    collection = forced_barrier_collection((path(1, "a", "p1", (None, 5)), path(2, "b", "p2", (None, 3))))
    assert tuple(row[4].value for row in collection.ordered_rows) == (1, 2)


def test_complete_append_preserves_prior_trace() -> None:
    assert complete_path_append_preserves_collection((path(1, "a", "p1", (None, 5)),), path(2, "b", "p2", (None, 3)))


def test_duplicate_target_and_negative_external_support_reject() -> None:
    with pytest.raises(InadmissibleExactValue):
        forced_barrier_collection((path(1, "a", "p1", (None, 5)), path(1, "b", "p2", (None, 3))))
    with pytest.raises(InadmissibleExactValue):
        external_nonnegative_support("-1")


def test_complete_value_free_identity_surface() -> None:
    rows = _identities(ROOT)
    assert len(rows) == 44
    assert all("barrier_kJ_mol_minus1_external_inscription" not in item for item in rows)


def test_complete_nist_collection_analysis() -> None:
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/kin-004-activation-barrier-v1/activation-barrier-primary-records-v1.json").read_text())
    analysis = exact_activation_barrier_analysis(rows, primary)
    assert analysis["all_forty_one_species_retained"]
    assert analysis["all_seven_hundred_eighty_two_path_states_retained"]
    assert analysis["unresolved_source_row_preserved"]


def test_prediction_contains_identities_not_values() -> None:
    serialized = json.dumps(prediction_program_document(ROOT), sort_keys=True)
    assert "505.77" not in serialized
    assert "SFT-CHEM-KIN-004-BARRIER-0001" in serialized


def test_execution_package_builds_under_sealed_engine() -> None:
    path_file = ROOT / "claims/SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004/execution.py"
    definition = importlib.util.spec_from_file_location("kin004_execution_test", path_file)
    assert definition and definition.loader
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == ACTIVATION_BARRIER_SPEC.claim_id
