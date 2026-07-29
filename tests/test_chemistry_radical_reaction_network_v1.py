import importlib.util
import json
from pathlib import Path
import pytest

from sft.chemistry.radical_reaction_network_batch_v1 import RADICAL_REACTION_NETWORK_SPEC
from sft.chemistry.radical_reaction_network_law_v1 import DIMENSIONS, OPERATIONAL_WITNESSES
from sft.chemistry.radical_reaction_network_validation_v1 import exact_analysis

ROOT = Path(__file__).resolve().parents[1]

def test_native_witnesses():
    assert len(DIMENSIONS) == 8 and len(OPERATIONAL_WITNESSES) == 10 and all(row[2] for row in OPERATIONAL_WITNESSES)

def test_complete_external_surface():
    analysis, checks = exact_analysis(ROOT)
    assert len(checks) == 73 and all(checks.values())
    assert analysis["archive_member_count"] == 24 and analysis["complete_table_row_count"] == 67
    assert analysis["article_page_count"] == 24 and analysis["supplement_page_count"] == 5

def test_table_omission_halts():
    source = json.loads((ROOT / RADICAL_REACTION_NETWORK_SPEC.observation_registry_path).read_text())
    with pytest.raises(ValueError): exact_analysis(ROOT, tuple(source["tables_in_source_order"][:-1]))

def test_execution_256_one_survivor():
    path = ROOT / "claims/SFT-CHEM-RADICAL-REACTION-NETWORK-013/execution.py"
    spec = importlib.util.spec_from_file_location("org013_execution", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    execution = module.build_execution(ROOT); census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(row).survives for row in census.candidates) == 1
    assert all(row.passed for row in execution.program.run_controls())
