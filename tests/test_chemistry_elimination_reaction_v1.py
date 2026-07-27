import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.elimination_reaction_batch_v1 import ELIMINATION_REACTION_SPEC
from sft.chemistry.elimination_reaction_law_v1 import DIMENSIONS, OPERATIONAL_WITNESSES
from sft.chemistry.elimination_reaction_validation_v1 import exact_analysis


ROOT = Path(__file__).resolve().parents[1]


def test_native_witnesses():
    assert len(DIMENSIONS) == 8
    assert len(OPERATIONAL_WITNESSES) == 8
    assert all(row[2] for row in OPERATIONAL_WITNESSES)


def test_complete_external_surface_and_honest_unresolved_boundary():
    analysis, checks = exact_analysis(ROOT)
    assert len(checks) == 47
    assert all(checks.values())
    assert analysis["supplementary_pdf_page_count"] == 117
    assert analysis["characterized_product_count"] == 32
    assert analysis["observable_unsaturation_product_count"] == 32
    assert analysis["full_carrier_favorable_count"] == 0
    assert analysis["full_carrier_adverse_count"] == 0
    assert analysis["full_carrier_unresolved_count"] == 32
    assert analysis["unsuccessful_or_low_elimination_row_count"] == 5
    assert analysis["optimization_row_count_including_source_gap"] == 34


def test_one_product_omission_halts():
    source = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1/complete-postseal-analysis-v1.json").read_text())
    with pytest.raises(ValueError):
        exact_analysis(ROOT, tuple(source["characterized_product_rows_in_source_order"][:-1]))


def test_execution_256_one_survivor():
    path = ROOT / "claims/SFT-CHEM-ELIMINATION-REACTION-FAMILY-010/execution.py"
    definition = importlib.util.spec_from_file_location("org010_execution", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
    assert ELIMINATION_REACTION_SPEC.exact_result in {candidate.candidate_id for candidate in census.candidates}
