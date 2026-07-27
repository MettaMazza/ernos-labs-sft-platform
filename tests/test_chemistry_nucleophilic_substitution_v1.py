import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.nucleophilic_substitution_batch_v1 import NUCLEOPHILIC_SUBSTITUTION_SPEC, PRIMARY_PATH
from sft.chemistry.nucleophilic_substitution_law_v1 import HeldPair, OPERATIONAL_WITNESSES, electron
from sft.chemistry.nucleophilic_substitution_validation_v1 import _source_rows, exact_analysis
from sft.engine.exact import InadmissibleExactValue


ROOT = Path(__file__).resolve().parents[1]


def test_native_operational_witnesses_and_pair_control():
    assert len(OPERATIONAL_WITNESSES) == 7
    assert all(passed for _, _, passed in OPERATIONAL_WITNESSES)
    with pytest.raises(InadmissibleExactValue):
        HeldPair(electron("same"), electron("same"))


def test_complete_external_structure_and_mechanism_vector():
    rows = _source_rows(ROOT)
    analysis, checks = exact_analysis(rows, json.loads((ROOT / PRIMARY_PATH).read_text()))
    assert len(rows) == analysis["complete_target_count"] == 9
    assert analysis["postseal_outcome_unopened_target_count"] == 7
    assert all(checks.values())
    assert analysis["complete_formula_inventory_conserved"]
    assert analysis["source_formula_vector"] == analysis["terminal_formula_vector"] == {"Br": 1, "C": 1, "H": 4, "O": 1}
    assert (analysis["source_substrate_connectivity"], analysis["terminal_product_connectivity"]) == ("CBr", "CO")


def test_omitted_external_row_halts():
    rows = _source_rows(ROOT)
    with pytest.raises(ValueError):
        exact_analysis(rows[:-1], {})


def test_execution_generates_one_of_256_and_controls_pass():
    path = ROOT / "claims/SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007/execution.py"
    definition = importlib.util.spec_from_file_location("org007_test_execution", path)
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(row).survives for row in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
    assert NUCLEOPHILIC_SUBSTITUTION_SPEC.exact_result in {row.candidate_id for row in census.candidates}
