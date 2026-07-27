import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.complex_spin_state_order_batch_v1 import (
    COMPLEX_SPIN_STATE_ORDER_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.complex_spin_state_order_law_v1 import (
    OPERATIONAL_WITNESSES, SpinOccupancySignature, SplitSupportCapacity,
    enumerate_complete_spin_signatures, forced_high_spin_state, forced_low_spin_state,
    forced_six_electron_order_vector,
)
from sft.chemistry.complex_spin_state_order_validation_v1 import (
    _source_rows, exact_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne
from sft.engine.exact import InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_007_exact_law_and_complete_256_form_grammar():
    assert all(passed for _, _, passed in OPERATIONAL_WITNESSES)
    spec = COMPLEX_SPIN_STATE_ORDER_SPEC
    assert len(spec.dimensions) == 8
    assert all(len(row.choices) == 2 for row in spec.dimensions)
    assert 2 ** len(spec.dimensions) == 256


def test_inorg_007_complete_six_electron_census_and_extrema():
    rows = enumerate_complete_spin_signatures(PositiveCount(6))
    assert len(rows) == 10 and len(set(rows)) == 10
    low = forced_low_spin_state(rows)
    high = forced_high_spin_state(rows)
    assert isinstance(low.lower_singles, EmptyOne) and isinstance(low.upper_pairs, EmptyOne) and isinstance(low.upper_singles, EmptyOne)
    assert low.lower_pairs.value == 3 and low.spin_width.value == 1 and isinstance(low.split_crossing_count, EmptyOne)
    assert (high.lower_pairs.value, high.lower_singles.value, high.upper_singles.value) == (1, 2, 2)
    assert isinstance(high.upper_pairs, EmptyOne) and high.spin_width.value == 5 and high.split_crossing_count.value == 2


def test_inorg_007_exact_order_and_cost_vectors():
    vector = forced_six_electron_order_vector()
    assert tuple(row.order.label for row in vector) == ("high-precedes-low", "crossover-coincidence", "low-precedes-high")
    assert tuple((row.high_cost.value, row.low_cost.value) for row in vector) == ((1, 3), (3, 3), (5, 3))


def test_inorg_007_rejects_wrong_capacity_and_overfill():
    with pytest.raises(InadmissibleExactValue):
        SplitSupportCapacity(PositiveCount(2), PositiveCount(3))
    with pytest.raises(InadmissibleExactValue):
        SpinOccupancySignature(PositiveCount(6), PositiveCount(3), PositiveCount(1), EmptyOne(), EmptyOne())


def test_inorg_007_value_free_identity_and_complete_postseal_vector():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    identities = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert identities["complete_registered_target_count"] == 3
    assert identities["target_values_definitions_terms_distances_temperatures_outcomes_or_payload_hashes_present"] is False


def test_inorg_007_empirical_vector_preserves_values_and_transport_mismatch():
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_analysis(rows, primary)
    assert analysis["transport_mismatch_preserved"]
    assert analysis["external_distance_vector_pm"] == ("1016/5", "2199/10")
    assert analysis["external_temperature_vector_k"] == ("115", "227")
    assert analysis["external_term_vector"] == ("1A1", "5T2")
    assert analysis["external_state_vector"] == ("low-spin", "high-spin")
    assert analysis["external_dilution_direction_match"]


def test_inorg_007_prediction_is_target_free_and_execution_has_one_survivor():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True)
    assert "target_payload_hash" not in encoded and "203.2" not in encoded and "227" not in encoded
    path = ROOT / "claims/SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007/execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_007_test", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(row) for row in census.candidates)
    assert census.expected_cardinality == 256
    assert len(census.candidates) == 256
    assert sum(row.survives for row in decisions) == 1
    assert execution.program.closure_evidence(decisions).scope.value == "depth_independent"
    assert all(row.passed for row in execution.program.run_controls())
