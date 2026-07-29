import importlib.util
from pathlib import Path

import pytest

from sft.chemistry.nuchem_initial_batch_v1 import SPECS
from sft.chemistry.nuchem_initial_validation_v1 import exact_analysis


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("claim", SPECS, ids=("nuchem001", "nuchem002", "nuchem003", "nuchem004"))
def test_native_law(claim):
    assert len(claim.dimensions) == 8
    assert len(claim.operational_witnesses) == 8
    assert all(row[2] for row in claim.operational_witnesses)


@pytest.mark.parametrize("claim", SPECS, ids=("nuchem001", "nuchem002", "nuchem003", "nuchem004"))
def test_complete_external_reconstruction(claim):
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    assert len(checks) == len(claim.target_rows) == 8 and all(checks.values())
    assert analysis["complete_family_pdf_pages"] == 8
    assert analysis["complete_family_html_documents"] == 2
    assert analysis["complete_family_characters"] == 34442


@pytest.mark.parametrize("claim", SPECS, ids=("nuchem001", "nuchem002", "nuchem003", "nuchem004"))
def test_omission_halts(claim):
    with pytest.raises(ValueError):
        exact_analysis(ROOT, claim.claim_id, True)


@pytest.mark.parametrize("claim", SPECS, ids=("nuchem001", "nuchem002", "nuchem003", "nuchem004"))
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
