import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.organometallic_metal_carbon_bond_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, ORGANOMETALLIC_METAL_CARBON_BOND_SPEC, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.organometallic_metal_carbon_bond_law_v1 import (
    OPERATIONAL_WITNESSES, append_direct_incidence, direct_incidence, forced_organometallic_bond,
)
from sft.chemistry.organometallic_metal_carbon_bond_validation_v1 import _source_rows, exact_analysis, prediction_program_document
from sft.claim_evidence import EmptyOne
from sft.engine.exact import InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_010_exact_law_and_complete_grammar():
    assert all(row[2] for row in OPERATIONAL_WITNESSES)
    assert len(ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.dimensions) == 8
    assert 2 ** len(ORGANOMETALLIC_METAL_CARBON_BOND_SPEC.dimensions) == 256
    assert isinstance(forced_organometallic_bond("absent", EmptyOne()), EmptyOne)
    first = forced_organometallic_bond("one", (direct_incidence("M1", "C1", PositiveCount(2)),))
    second = append_direct_incidence(first, direct_incidence("M1", "C2", PositiveCount(2)))
    assert first.direct_incidence_count.value == 1 and second.direct_incidence_count.value == 2


def test_inorg_010_empty_tuple_halts():
    with pytest.raises(InadmissibleExactValue):
        forced_organometallic_bond("bad", ())


def test_inorg_010_value_free_identity_and_postseal_hashes():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    identities = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert identities["complete_registered_target_count"] == 12
    assert identities["target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present"] is False


def test_inorg_010_complete_external_vector_and_custody():
    analysis = exact_analysis(_source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text()))
    assert analysis["complete_target_count"] == 12 and analysis["complete_source_count"] == 1
    assert analysis["example_count"] == 6 and analysis["explicit_exclusion_count"] == 1
    assert analysis["source_recapture_count"] == 0 and analysis["all_rows_preserved"]


def test_inorg_010_prediction_target_free_and_one_survivor():
    document = prediction_program_document(ROOT); encoded = json.dumps(document, sort_keys=True)
    assert "complete_definition_text" not in encoded and "target_payload_hash" not in encoded and "MeMgI" not in encoded
    path = ROOT / "claims/SFT-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010/execution.py"
    definition = importlib.util.spec_from_file_location("inorg010_test", path)
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    execution = module.build_execution(ROOT); census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(row) for row in census.candidates)
    assert len(census.candidates) == 256 and sum(row.survives for row in decisions) == 1
    assert execution.program.closure_evidence(decisions).scope.value == "depth_independent"
    assert all(row.passed for row in execution.program.run_controls())
