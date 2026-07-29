import importlib.util
from pathlib import Path
import pytest
from sft.chemistry.echem_potential_batch_v1 import CELL_POTENTIAL_SPEC, CONCENTRATION_POTENTIAL_SPEC, ELECTRODE_POTENTIAL_SPEC
from sft.chemistry.echem_potential_validation_v1 import exact_analysis

ROOT = Path(__file__).resolve().parents[1]
SPECS = (ELECTRODE_POTENTIAL_SPEC, CELL_POTENTIAL_SPEC, CONCENTRATION_POTENTIAL_SPEC)

@pytest.mark.parametrize("claim", SPECS, ids=("echem002", "echem003", "echem004"))
def test_native_law(claim):
    assert len(claim.dimensions) == 8
    assert len(claim.operational_witnesses) >= 7
    assert all(row[2] for row in claim.operational_witnesses)

@pytest.mark.parametrize("claim", SPECS, ids=("echem002", "echem003", "echem004"))
def test_complete_external_reconstruction(claim):
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    assert len(checks) == len(claim.target_rows) and all(checks.values())
    assert analysis["complete_pdf_pages"] == 8 and analysis["complete_pdf_characters"] == 37013

@pytest.mark.parametrize("claim", SPECS, ids=("echem002", "echem003", "echem004"))
def test_omission_halts(claim):
    with pytest.raises(ValueError): exact_analysis(ROOT, claim.claim_id, True)

@pytest.mark.parametrize("claim", SPECS, ids=("echem002", "echem003", "echem004"))
def test_execution_generates_one_survivor(claim):
    path = ROOT / "claims" / claim.claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("focused_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    execution = module.build_execution(ROOT); census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
