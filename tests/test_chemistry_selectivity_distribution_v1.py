import importlib.util
import json
from pathlib import Path
import pytest

from sft.chemistry.selectivity_distribution_batch_v1 import ANALYSIS_PATH, SELECTIVITY_DISTRIBUTION_SPEC
from sft.chemistry.selectivity_distribution_law_v1 import DIMENSIONS, OPERATIONAL_WITNESSES
from sft.chemistry.selectivity_distribution_validation_v1 import exact_analysis

ROOT = Path(__file__).resolve().parents[1]


def test_native_witnesses():
    assert len(DIMENSIONS) == 8 and len(OPERATIONAL_WITNESSES) == 10 and all(row[2] for row in OPERATIONAL_WITNESSES)


def test_complete_external_surface():
    analysis, checks = exact_analysis(ROOT)
    assert len(checks) == 133 and all(checks.values())
    assert (analysis["complete_reaction_rows"], analysis["complete_outcomes"], analysis["complete_products"]) == (130, 130, 152)
    assert (analysis["complete_product_identifiers"], analysis["complete_product_measurements"], analysis["multi_product_rows"]) == (302, 195, 19)


def test_row_omission_halts():
    source = json.loads((ROOT / ANALYSIS_PATH).read_text())
    with pytest.raises(ValueError): exact_analysis(ROOT, tuple(source["reaction_rows_in_preregistered_order"][:-1]))


def test_execution_256_one_survivor():
    path = ROOT / "claims/SFT-CHEM-SELECTIVITY-COMPLETE-DISTRIBUTION-014/execution.py"
    spec = importlib.util.spec_from_file_location("org014_execution", path); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    execution = module.build_execution(ROOT); census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(row).survives for row in census.candidates) == 1
    assert all(row.passed for row in execution.program.run_controls())
