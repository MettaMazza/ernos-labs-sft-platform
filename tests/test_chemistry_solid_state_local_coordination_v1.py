import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.solid_state_local_coordination_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SOLID_STATE_LOCAL_COORDINATION_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.solid_state_local_coordination_law_v1 import (
    OPERATIONAL_WITNESSES,
    append_occurrence,
    local_solid,
)
from sft.chemistry.solid_state_local_coordination_validation_v1 import (
    _source_rows,
    exact_analysis,
    prediction_program_document,
)
from sft.engine.exact import InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_015_law():
    assert all(witness[2] for witness in OPERATIONAL_WITNESSES)
    assert len(SOLID_STATE_LOCAL_COORDINATION_SPEC.dimensions) == 8
    solid = local_solid(
        "AB",
        (("A", PositiveCount(2)), ("B", PositiveCount(2))),
        ((('A', 1), ('B', 1)), (('A', 2), ('B', 2))),
        PositiveCount(2),
    )
    successor = append_occurrence(solid, "A", solid.occurrences[1])
    assert tuple(entry.primitive_count.value for entry in successor.formula) == (3, 2)
    with pytest.raises(InadmissibleExactValue):
        local_solid("bad", (("A", PositiveCount(1)),), (), PositiveCount(4))


def test_inorg_015_hashes():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH


def test_inorg_015_external_vector():
    analysis = exact_analysis(
        _source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
    )
    assert analysis["complete_target_count"] == 10
    assert analysis["complete_source_count"] == 2
    assert analysis["development_observed_target_count"] == 5
    assert analysis["identity_only_unopened_target_count"] == 5
    assert analysis["scope_mismatch_or_distinction_count"] == 1
    assert analysis["all_rows_preserved"]


def test_inorg_015_survivor_and_value_free_prediction():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert "complete_definition_text" not in serialized
    assert "target_payload_hash" not in serialized
    assert "A crystal containing" not in serialized
    path = ROOT / "claims/SFT-CHEM-SOLID-STATE-LOCAL-COORDINATION-015/execution.py"
    spec = importlib.util.spec_from_file_location("inorg015_execution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(candidate) for candidate in census.candidates)
    assert len(census.candidates) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert all(control.passed for control in execution.program.run_controls())
