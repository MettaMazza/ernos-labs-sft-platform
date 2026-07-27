import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.coordination_isomerism_batch_v1 import (
    COORDINATION_ISOMERISM_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRELIMINARY_IDENTITY_HASH,
    PRELIMINARY_IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.coordination_isomerism_law_v1 import (
    FiniteCoordinationForm,
    OPERATIONAL_WITNESSES,
)
from sft.chemistry.coordination_isomerism_validation_v1 import (
    _form,
    _source_rows,
    exact_coordination_isomerism_analysis,
    prediction_program_document,
)
from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_005_exact_law_and_complete_256_form_grammar():
    assert all(passed for _, _, passed in OPERATIONAL_WITNESSES)
    spec = COORDINATION_ISOMERISM_SPEC
    assert len(spec.dimensions) == 8
    assert all(len(row.choices) == 2 for row in spec.dimensions)
    assert 2 ** len(spec.dimensions) == 256
    assert "complete-three-axis-two-fibre-relation" in spec.exact_result


def test_inorg_005_rejects_third_fibre_label():
    with pytest.raises(InadmissibleExactValue):
        FiniteCoordinationForm(
            (HeldLabel("coordination-composition-label", "L"),),
            (HeldLabel("coordination-attachment-mode", "mode-one"),),
            ((HeldLabel("fold-orientation-fibre", "fibre-three"), EmptyOne(), EmptyOne()),),
            (),
        )


def test_inorg_005_value_free_identity_and_preserved_incomplete_predecessor():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / PRELIMINARY_IDENTITY_PATH) == PRELIMINARY_IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    identities = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert identities["target_values_or_payload_hashes_present"] is False
    assert identities["complete_registered_target_count"] == 17
    assert identities["preserved_incomplete_preliminary_identity_sha256"] == PRELIMINARY_IDENTITY_HASH
    assert len({row["target_id"] for row in identities["rows"]}) == 17


def test_inorg_005_complete_postseal_external_vector_and_absence_rows():
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_coordination_isomerism_analysis(rows, primary)
    assert analysis["complete_registered_target_count"] == 17
    assert analysis["attachment_class_reconstructed"]
    assert analysis["orientation_adjacency_class_reconstructed"]
    assert analysis["mirror_complement_class_reconstructed"]
    assert analysis["registered_to_presented_identity_redirect_count"] == 2
    assert analysis["registered_to_presented_identity_redirects_preserved"]
    assert analysis["explicit_linkage_literal_absence_preserved"]
    assert analysis["imported_catalogue_or_observed_class_used_as_fold_parameter"] is False


def test_inorg_005_prediction_is_capability_closed_and_target_free():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in encoded
    assert "source_inscription" not in encoded
    assert "target_payload_hash" not in encoded
    assert {row["opcode"] for row in document["instructions"]} <= {"input", "label", "word", "table", "emit"}


def test_inorg_005_different_composition_and_third_fibre_controls_reject():
    with pytest.raises(InadmissibleExactValue):
        from sft.chemistry.coordination_isomerism_law_v1 import forced_coordination_isomer_relation
        forced_coordination_isomer_relation(_form(), _form(compositions=("L", "M")))
    with pytest.raises(InadmissibleExactValue):
        _form(words=(("fibre-one", "EmptyOne", "EmptyOne"), ("fibre-three", "EmptyOne", "EmptyOne")))


def test_inorg_005_execution_builds_without_engine_or_gate_mutation():
    path = ROOT / "claims/SFT-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005/execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_005_test", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(row) for row in census.candidates)
    assert census.expected_cardinality == 256
    assert len(census.candidates) == 256
    assert sum(row.survives for row in decisions) == 1
    assert execution.program.closure_evidence(decisions).scope.value == "depth_independent"
    assert all(row.passed for row in execution.program.run_controls())
