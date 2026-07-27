import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.coordination_geometry_batch_v1 import (
    COORDINATION_GEOMETRY_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.coordination_geometry_law_v1 import (
    CompleteCoordinationGeometry,
    OPERATIONAL_WITNESSES,
    _GEOMETRY_TWO,
)
from sft.chemistry.coordination_geometry_validation_v1 import (
    _source_rows,
    exact_coordination_geometry_analysis,
    prediction_program_document,
)
from sft.engine.exact import InadmissibleExactValue
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_004_exact_law_and_complete_256_form_grammar():
    assert all(passed for _, _, passed in OPERATIONAL_WITNESSES)
    spec = COORDINATION_GEOMETRY_SPEC
    assert len(spec.dimensions) == 8
    assert all(len(row.choices) == 2 for row in spec.dimensions)
    assert 2 ** len(spec.dimensions) == 256


def test_inorg_004_rejects_collapsed_orientation():
    rows = _GEOMETRY_TWO.ordered_positions
    with pytest.raises(InadmissibleExactValue):
        CompleteCoordinationGeometry(
            _GEOMETRY_TWO.central_occurrence,
            (rows[0], type(rows[1])(rows[1].attachment_ordinal, rows[1].ligand_occurrence, rows[0].orientation_word)),
            _GEOMETRY_TWO.ordered_adjacencies,
        )


def test_inorg_004_value_free_identity_and_bound_source_hashes():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    identities = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert identities["target_values_or_payload_hashes_present"] is False
    assert identities["complete_registered_target_count"] == 53
    assert len({row["target_id"] for row in identities["rows"]}) == 53


def test_inorg_004_complete_postseal_external_vector_and_adverse_rows():
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_coordination_geometry_analysis(rows, primary)
    assert analysis["complete_external_positive_incidence_vector"] == (2, 3, 4, 5, 6)
    assert analysis["complete_external_point_group_vector"] == ("C 2v", "D 3h", "T d", "D 3h", "O h")
    assert analysis["all_original_target_identity_mismatches_preserved"]
    assert analysis["coordinate_absence_rows_retained"] == 3
    assert analysis["point_group_or_coordinate_used_as_fold_parameter"] is False
    assert analysis["coordination_count_used_to_select_shape"] is False


def test_inorg_004_prediction_is_capability_closed_and_target_free():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in encoded
    assert "source_inscription" not in encoded
    assert "point-group-inscription" in encoded
    assert {row["opcode"] for row in document["instructions"]} <= {"input", "label", "word", "table", "emit"}


def test_inorg_004_execution_builds_without_engine_or_gate_mutation():
    path = ROOT / "claims/SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004/execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_004_test", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(row) for row in census.candidates)
    assert census.expected_cardinality == 256
    assert len(census.candidates) == 256
    assert sum(row.survives for row in decisions) == 1
    assert all(row.passed for row in execution.program.run_controls())
