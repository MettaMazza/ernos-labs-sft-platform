import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.coordination_entity_batch_v1 import COORDINATION_ENTITY_SPEC, IDENTITY_PATH, PRIMARY_PATH, TARGET_PATH
from sft.chemistry.coordination_entity_law_v1 import CompleteCoordinationEntity, RetainedCoordinationAttachment, append_ligand_preserves_coordination_identity, forced_coordination_entity_identity_law
from sft.chemistry.coordination_entity_validation_v1 import _source_rows, exact_coordination_entity_analysis, prediction_program_document
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def attachment(number, central, ligand=None):
    return RetainedCoordinationAttachment(PositiveCount(number), central, HeldLabel("coordination-ligand-occurrence", ligand or f"L-{number}"), HeldLabel("coordination-ligand-group", "L"), HeldLabel("positive-coordination-incidence", f"edge-{number}"))


def entity(width=3):
    central = HeldLabel("coordination-central-occurrence", "central")
    return CompleteCoordinationEntity(HeldLabel("coordination-entity", "entity"), HeldLabel("coordination-central-element", "Fe"), central, tuple(attachment(number, central) for number in range(1, width + 1)))


def test_spec_is_256_form_depth_independent_law():
    assert len(COORDINATION_ENTITY_SPEC.dimensions) == 8
    assert all(len(dimension.choices) == 2 for dimension in COORDINATION_ENTITY_SPEC.dimensions)
    assert len({COORDINATION_ENTITY_SPEC.exact_result}) == 1


def test_complete_entity_retains_every_occurrence_and_incidence():
    result = forced_coordination_entity_identity_law(entity())
    assert len(set(result.ordered_ligand_occurrences)) == 3
    assert len(set(result.ordered_attachment_traces)) == 3


def test_successor_preserves_prior_entity():
    base = entity()
    assert append_ligand_preserves_coordination_identity(base, attachment(4, base.central_occurrence))


def test_mismatched_central_and_duplicate_ligand_rejected():
    base = entity(1)
    with pytest.raises(InadmissibleExactValue):
        CompleteCoordinationEntity(base.entity_identity, base.central_element_identity, base.central_occurrence, (attachment(1, HeldLabel("coordination-central-occurrence", "other")),))
    with pytest.raises(InadmissibleExactValue):
        CompleteCoordinationEntity(base.entity_identity, base.central_element_identity, base.central_occurrence, (attachment(1, base.central_occurrence, "same"), attachment(2, base.central_occurrence, "same")))


def test_identity_registry_is_value_free_and_complete():
    document = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert document["target_values_or_hashes_present"] is False
    assert document["complete_registered_target_count"] == 20
    assert len(document["rows"]) == 20


def test_source_vector_and_limitations_are_complete():
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_coordination_entity_analysis(rows, primary)
    assert analysis["complete_registered_target_count"] == 20
    assert all(value for key, value in analysis.items() if key not in {"complete_registered_target_count", "source_class_census"})


def test_prediction_program_contains_no_withheld_content():
    program = prediction_program_document(ROOT)
    text = json.dumps(program, sort_keys=True)
    target = json.loads((ROOT / TARGET_PATH).read_text())
    assert all(row["source_inscription"] not in text for row in target["rows"] if len(row["source_inscription"]) > 12)


def test_execution_builds_and_dependencies_are_admitted():
    path = ROOT / "claims/SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001/execution.py"
    definition = importlib.util.spec_from_file_location("inorg001_execution", path)
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    admitted = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    assert set(COORDINATION_ENTITY_SPEC.dependencies) <= admitted
    assert execution.program.registration.claim_id == COORDINATION_ENTITY_SPEC.claim_id
