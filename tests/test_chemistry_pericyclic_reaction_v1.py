import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.pericyclic_reaction_batch_v1 import PERICYCLIC_REACTION_SPEC
from sft.chemistry.pericyclic_reaction_law_v1 import DIMENSIONS, OPERATIONAL_WITNESSES
from sft.chemistry.pericyclic_reaction_validation_v1 import exact_analysis


ROOT = Path(__file__).resolve().parents[1]


def test_native_witnesses():
    assert len(DIMENSIONS) == 8
    assert len(OPERATIONAL_WITNESSES) == 10
    assert all(row[2] for row in OPERATIONAL_WITNESSES)


def test_complete_external_surface_and_reported_class_vector():
    analysis, checks = exact_analysis(ROOT)
    assert len(checks) == 38
    assert all(checks.values())
    assert analysis["archive_member_count"] == 44
    assert analysis["archive_regular_file_count"] == 43
    assert analysis["primary_table_row_count"] == 32
    assert analysis["reported_experimental_ratio_count"] == 28
    assert analysis["unresolved_experimental_ratio_count"] == 4
    assert analysis["first_class_preference_count"] == 22
    assert analysis["second_class_preference_count"] == 5
    assert analysis["equal_class_count"] == 1
    assert analysis["both_classes_reported_count"] == 28
    assert analysis["supplement_page_count"] == 203


def test_one_primary_row_omission_halts():
    source = json.loads((ROOT / PERICYCLIC_REACTION_SPEC.observation_registry_path).read_text())
    with pytest.raises(ValueError):
        exact_analysis(ROOT, tuple(source["primary_table_rows_in_source_order"][:-1]))


def test_execution_256_one_survivor():
    path = ROOT / "claims/SFT-CHEM-PERICYCLIC-REACTION-FAMILY-012/execution.py"
    definition = importlib.util.spec_from_file_location("org012_execution", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
    assert PERICYCLIC_REACTION_SPEC.exact_result in {candidate.candidate_id for candidate in census.candidates}
