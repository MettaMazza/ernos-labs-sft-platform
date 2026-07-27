import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.rearrangement_reaction_batch_v1 import REARRANGEMENT_REACTION_SPEC
from sft.chemistry.rearrangement_reaction_law_v1 import DIMENSIONS, OPERATIONAL_WITNESSES
from sft.chemistry.rearrangement_reaction_validation_v1 import exact_analysis


ROOT = Path(__file__).resolve().parents[1]


def test_native_witnesses():
    assert len(DIMENSIONS) == 8
    assert len(OPERATIONAL_WITNESSES) == 11
    assert all(row[2] for row in OPERATIONAL_WITNESSES)


def test_complete_external_surface_and_atom_enumeration():
    analysis, checks = exact_analysis(ROOT)
    assert len(checks) == 16
    assert all(checks.values())
    assert analysis["supplementary_pdf_page_count"] == 38
    assert analysis["explicit_source_product_pair_count"] == 8
    assert analysis["exact_endpoint_inventory_favorable_count"] == 8
    assert analysis["exact_endpoint_inventory_adverse_count"] == 0
    assert analysis["exact_endpoint_inventory_unresolved_count"] == 0
    assert analysis["positive_constitutional_incidence_change_count"] == 8
    assert analysis["first_blind_surface_preserved_unresolved"] is True


def test_one_pair_omission_halts():
    source = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/org-011-claisen-blind-v2/complete-postseal-analysis-v2.json").read_text())
    with pytest.raises(ValueError):
        exact_analysis(ROOT, tuple(source["explicit_claisen_source_product_pairs_in_source_order"][:-1]))


def test_execution_256_one_survivor():
    path = ROOT / "claims/SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011/execution.py"
    definition = importlib.util.spec_from_file_location("org011_execution", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
    assert REARRANGEMENT_REACTION_SPEC.exact_result in {candidate.candidate_id for candidate in census.candidates}
