import importlib.util
from pathlib import Path
import pytest
from sft.chemistry.half_reaction_orientation_law_v1 import DIMENSIONS, OPERATIONAL_WITNESSES
from sft.chemistry.half_reaction_orientation_validation_v1 import exact_analysis

ROOT = Path(__file__).resolve().parents[1]

def test_native_law():
    assert len(DIMENSIONS) == 8
    assert len(OPERATIONAL_WITNESSES) == 10
    assert all(witness[2] for witness in OPERATIONAL_WITNESSES)

def test_complete_external_reconstruction():
    analysis, checks = exact_analysis(ROOT)
    assert len(checks) == 6 and all(checks.values())
    assert analysis["complete_nist_pdf_page_count"] == 22
    assert analysis["complete_nist_extracted_character_count"] == 99794

def test_omission_halts():
    with pytest.raises(ValueError):
        exact_analysis(ROOT, True)

def test_execution_generates_one_survivor():
    path = ROOT / "claims/SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001/execution.py"
    spec = importlib.util.spec_from_file_location("echem001", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
