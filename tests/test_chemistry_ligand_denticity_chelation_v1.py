import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.coordination_entity_law_v1 import CompleteCoordinationEntity, RetainedCoordinationAttachment
from sft.chemistry.ligand_denticity_chelation_batch_v1 import IDENTITY_PATH, LIGAND_DENTICITY_CHELATION_SPEC, PRIMARY_PATH, TARGET_PATH
from sft.chemistry.ligand_denticity_chelation_law_v1 import CompleteLigandDonorTopology, forced_ligand_denticity_and_chelation
from sft.chemistry.ligand_denticity_chelation_validation_v1 import _source_rows, exact_ligand_denticity_chelation_analysis, prediction_program_document
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def entity(width):
    central = HeldLabel("coordination-central-occurrence", "M")
    group = HeldLabel("coordination-ligand-group", "L")
    rows = tuple(RetainedCoordinationAttachment(PositiveCount(n), central, HeldLabel("coordination-ligand-occurrence", f"d-{n}"), group, HeldLabel("positive-coordination-incidence", f"e-{n}")) for n in range(1, width + 1))
    return CompleteCoordinationEntity(HeldLabel("coordination-entity", f"x-{width}"), HeldLabel("coordination-central-element", "M"), central, rows)


def topology(value, width=None):
    rows = value.ordered_attachments if width is None else value.ordered_attachments[:width]
    return CompleteLigandDonorTopology(HeldLabel("coordination-ligand-carrier-occurrence", "carrier"), HeldLabel("coordination-ligand-group", "L"), value.central_occurrence, tuple(r.ligand_occurrence for r in rows), tuple(r.attachment_trace for r in rows), tuple(HeldLabel("positive-ligand-internal-incidence", f"p-{n}") for n in range(1, len(rows))))


def test_spec():
    assert len(LIGAND_DENTICITY_CHELATION_SPEC.dimensions) == 8
    assert all(len(d.choices) == 2 for d in LIGAND_DENTICITY_CHELATION_SPEC.dimensions)


def test_open_and_closed_topologies():
    one = forced_ligand_denticity_and_chelation(entity(1), topology(entity(1)))
    two = forced_ligand_denticity_and_chelation(entity(2), topology(entity(2)))
    assert one.positive_denticity == PositiveCount(1) and not one.closed_topology_trace
    assert two.positive_denticity == PositiveCount(2) and len(two.closed_topology_trace) == 3


def test_centre_mismatch_rejected():
    value = entity(2)
    base = topology(value)
    wrong = CompleteLigandDonorTopology(base.ligand_carrier_occurrence, base.ligand_group_identity, HeldLabel("coordination-central-occurrence", "other"), base.ordered_donor_site_occurrences, base.ordered_attachment_traces, base.ordered_internal_connection_traces)
    with pytest.raises(InadmissibleExactValue):
        forced_ligand_denticity_and_chelation(value, wrong)


def test_incomplete_internal_path_rejected():
    value = entity(2)
    with pytest.raises(InadmissibleExactValue):
        CompleteLigandDonorTopology(HeldLabel("coordination-ligand-carrier-occurrence", "carrier"), HeldLabel("coordination-ligand-group", "L"), value.central_occurrence, tuple(r.ligand_occurrence for r in value.ordered_attachments), tuple(r.attachment_trace for r in value.ordered_attachments), ())


def test_identity_value_free():
    document = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert document["target_values_or_hashes_present"] is False and len(document["rows"]) == 24


def test_complete_analysis():
    analysis = exact_ligand_denticity_chelation_analysis(_source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text()))
    assert analysis["complete_registered_target_count"] == 24
    assert all(value for key, value in analysis.items() if key not in {"complete_registered_target_count", "source_class_census"})


def test_prediction_has_no_long_target_content():
    text = json.dumps(prediction_program_document(ROOT), sort_keys=True)
    targets = json.loads((ROOT / TARGET_PATH).read_text())
    assert all(row["source_inscription"] not in text for row in targets["rows"] if len(row["source_inscription"]) > 12)


def test_execution_and_dependencies():
    path = ROOT / "claims/SFT-CHEM-LIGAND-DENTICITY-CHELATION-TOPOLOGY-003/execution.py"
    spec = importlib.util.spec_from_file_location("inorg003", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    admitted = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    assert set(LIGAND_DENTICITY_CHELATION_SPEC.dependencies) <= admitted
    assert execution.program.registration.claim_id == LIGAND_DENTICITY_CHELATION_SPEC.claim_id
