"""Focused whole-subfield COMP-001--014 tests; heavy verification stays deferred."""

import importlib.util
from pathlib import Path

import pytest

from sft.chemistry.computational_chemistry_batch_v1 import SPECS
from sft.chemistry.computational_chemistry_validation_v1 import exact_analysis


ROOT = Path(__file__).resolve().parents[1]
IDS = tuple(f"comp{number:03d}" for number in range(1, 15))


@pytest.mark.parametrize("claim", SPECS, ids=IDS)
def test_native_law_is_exhaustive_and_operational(claim):
    assert len(claim.dimensions) == 8
    assert len(claim.operational_witnesses) == 8
    assert all(witness[2] for witness in claim.operational_witnesses)


@pytest.mark.parametrize("claim", SPECS, ids=IDS)
def test_complete_external_reconstruction(claim):
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    assert len(checks) == len(claim.target_rows) == 8
    assert all(checks.values())
    assert analysis["complete_family_source_count"] == 59
    assert analysis["complete_family_source_bytes"] == 444644830
    assert analysis["implementation_distinct_value_vector_reconstruction_passed"]


@pytest.mark.parametrize("claim", SPECS, ids=IDS)
def test_omission_halts(claim):
    with pytest.raises(ValueError):
        exact_analysis(ROOT, claim.claim_id, True)


@pytest.mark.parametrize("claim", SPECS, ids=IDS)
def test_execution_generates_exactly_one_survivor(claim):
    path = ROOT / "claims" / claim.claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("focused_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
