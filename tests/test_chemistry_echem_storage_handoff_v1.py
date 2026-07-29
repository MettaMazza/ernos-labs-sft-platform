import importlib.util
from pathlib import Path

import pytest

from sft.chemistry.echem_storage_handoff_batch_v1 import STORAGE_SPEC
from sft.chemistry.echem_storage_handoff_validation_v1 import exact_analysis

ROOT = Path(__file__).resolve().parents[1]


def test_native_law():
    assert len(STORAGE_SPEC.dimensions) == 8
    assert len(STORAGE_SPEC.operational_witnesses) == 8
    assert all(row[2] for row in STORAGE_SPEC.operational_witnesses)


def test_complete_external_reconstruction():
    analysis, checks = exact_analysis(ROOT)
    assert len(checks) == 8 and all(checks.values())
    assert analysis["complete_owner_count"] == 3
    assert analysis["complete_directed_handoff_count"] == 2
    assert analysis["complete_nist_source_bytes"] == 97292


def test_omission_halts():
    with pytest.raises(ValueError):
        exact_analysis(ROOT, True)


def test_execution_generates_one_survivor():
    path = ROOT / "claims/SFT-CHEM-ELECTROCHEMICAL-STORAGE-HANDOFF-013/execution.py"
    module_spec = importlib.util.spec_from_file_location("focused_echem013", path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
