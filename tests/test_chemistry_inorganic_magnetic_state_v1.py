import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.inorganic_magnetic_state_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, INORGANIC_MAGNETIC_STATE_SPEC, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.inorganic_magnetic_state_law_v1 import (
    CompleteUnpairedSupport, OPERATIONAL_WITNESSES, append_unpaired_successor, complete_unpaired_support, forced_inorganic_magnetic_state,
)
from sft.chemistry.inorganic_magnetic_state_validation_v1 import _source_rows, exact_analysis, prediction_program_document
from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_009_exact_law_and_complete_grammar():
    assert all(row[2] for row in OPERATIONAL_WITNESSES)
    assert len(INORGANIC_MAGNETIC_STATE_SPEC.dimensions) == 8
    assert 2 ** len(INORGANIC_MAGNETIC_STATE_SPEC.dimensions) == 256
    balanced = forced_inorganic_magnetic_state(complete_unpaired_support("balanced", EmptyOne()))
    high = forced_inorganic_magnetic_state(complete_unpaired_support("high", PositiveCount(4)))
    successor = forced_inorganic_magnetic_state(append_unpaired_successor(high.support))
    assert isinstance(balanced.moment_support, EmptyOne) and balanced.spin_width.value == 1
    assert (high.moment_support.value, high.spin_width.value) == (4, 5)
    assert (successor.moment_support.value, successor.spin_width.value) == (5, 6)


def test_inorg_009_duplicate_occurrence_halts():
    occurrence = HeldLabel("electron-occurrence", "same")
    with pytest.raises(InadmissibleExactValue):
        CompleteUnpairedSupport(HeldLabel("coordination-entity", "bad"), (occurrence, occurrence), (HeldLabel("electron-spin", "fibre-a"), HeldLabel("electron-spin", "fibre-b")))


def test_inorg_009_value_free_identity_and_postseal_hashes():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    identities = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert identities["complete_registered_target_count"] == 177
    assert identities["target_values_orientations_presence_flags_definitions_outcomes_or_payload_hashes_present"] is False


def test_inorg_009_complete_external_vector_and_custody():
    analysis = exact_analysis(_source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text()))
    assert analysis["complete_magnetic_count"] == 174
    assert analysis["positive_magnitude_count"] == 136 and analysis["structural_absence_count"] == 38
    assert analysis["orientation_class_counts"] == {"source-aligned": 6, "source-opposed": 62, "source-orientation-unspecified": 68, "structural-absence": 38}
    assert analysis["source_recapture_count"] == 0 and analysis["all_rows_preserved"]


def test_inorg_009_prediction_target_free_and_one_survivor():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True)
    assert "source_value_inscription" not in encoded and "target_payload_hash" not in encoded and "-0.09237" not in encoded
    path = ROOT / "claims/SFT-CHEM-INORGANIC-MAGNETIC-STATE-009/execution.py"
    definition = importlib.util.spec_from_file_location("inorg009_test", path)
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(row) for row in census.candidates)
    assert len(census.candidates) == 256 and sum(row.survives for row in decisions) == 1
    assert execution.program.closure_evidence(decisions).scope.value == "depth_independent"
    assert all(row.passed for row in execution.program.run_controls())
