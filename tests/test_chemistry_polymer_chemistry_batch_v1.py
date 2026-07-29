import importlib.util
from pathlib import Path

import pytest

from sft.chemistry.polymer_chemistry_batch_v1 import SPECS
from sft.chemistry.polymer_chemistry_validation_v1 import exact_analysis


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("claim", SPECS, ids=tuple(f"poly-{index:03d}" for index in range(1, 14)))
def test_native_law(claim):
    assert len(claim.dimensions) == 8
    assert len(claim.operational_witnesses) == 8
    assert all(row[2] for row in claim.operational_witnesses)


@pytest.mark.parametrize("claim", SPECS, ids=tuple(f"poly-{index:03d}" for index in range(1, 14)))
def test_complete_external_reconstruction(claim):
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    assert len(checks) == len(claim.target_rows) == 8 and all(checks.values())
    assert analysis["complete_source_artifacts"] == 21
    assert analysis["complete_source_bytes"] == 28928563
    assert analysis["complete_source_pages"] == 279
    assert analysis["no_claim_retired_on_first_failure"]


@pytest.mark.parametrize("claim", SPECS, ids=tuple(f"poly-{index:03d}" for index in range(1, 14)))
def test_omission_halts(claim):
    with pytest.raises(ValueError):
        exact_analysis(ROOT, claim.claim_id, True)


@pytest.mark.parametrize("claim", SPECS, ids=tuple(f"poly-{index:03d}" for index in range(1, 14)))
def test_execution_generates_one_survivor(claim):
    path = ROOT / "claims" / claim.claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("focused_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())


def test_source_reconstruction_retry_is_not_retirement():
    document = __import__("json").loads((ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1/complete-postseal-analysis-v2.json").read_text())
    assert document["first_attempt_extraction_adverse_rows_preserved"]
    assert not document["extraction_adverse_rows"]
    assert not document["source_reconstruction_failures_retired_claims"]
    assert document["every_obligation_remained_open_until_untouched_engine_admission"]
    assert len(document["measurement_vectors"]["pams_source_internal_arithmetic_defects"]) == 1
