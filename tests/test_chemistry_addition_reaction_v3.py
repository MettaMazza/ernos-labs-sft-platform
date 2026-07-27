import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.addition_reaction_batch_v3 import ADDITION_REACTION_SPEC, COMPARISON_PATH, SELECTION_PATH
from sft.chemistry.addition_reaction_law_v3 import DIMENSIONS, OPERATIONAL_WITNESSES
from sft.chemistry.addition_reaction_validation_v3 import exact_analysis, prior_history_analysis


ROOT = Path(__file__).resolve().parents[1]


def test_native_witnesses():
    assert len(DIMENSIONS) == 8
    assert len(OPERATIONAL_WITNESSES) == 9
    assert all(row[2] for row in OPERATIONAL_WITNESSES)


def test_complete_v9_external_surface_and_preserved_history():
    analysis, checks = exact_analysis(ROOT)
    assert all(checks.values())
    assert analysis["registered_non_uspto_payload_count"] == 48
    assert analysis["source_selected_reaction_count"] == 28
    assert analysis["favorable_reaction_count"] == 28
    assert analysis["adverse_reaction_count"] == 0
    assert analysis["unresolved_reaction_count"] == 0
    assert analysis["complete_valid_correspondence_count"] == 112
    assert prior_history_analysis(ROOT)["v6_status_counts"]["adverse"] == 31


def test_one_selected_reaction_omission_halts():
    selection = json.loads((ROOT / SELECTION_PATH).read_text(encoding="utf-8"))
    comparison = json.loads((ROOT / COMPARISON_PATH).read_text(encoding="utf-8"))
    with pytest.raises(ValueError):
        exact_analysis(
            ROOT,
            tuple(selection["selected_in_payload_and_row_order"][:-1]),
            tuple(comparison["results_in_frozen_order"][:-1]),
        )


def test_execution_256_one_survivor():
    path = ROOT / "claims/SFT-CHEM-ADDITION-REACTION-FAMILY-009/execution.py"
    definition = importlib.util.spec_from_file_location("org009_execution", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
    assert ADDITION_REACTION_SPEC.exact_result in {candidate.candidate_id for candidate in census.candidates}
