import importlib.util
import json
from pathlib import Path

from sft.chemistry.defect_nonstoichiometry_batch_v1 import (
    DEFECT_NONSTOICHIOMETRY_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
    V1_PRIMARY_HASH,
    V1_PRIMARY_PATH,
    V1_TARGET_HASH,
    V1_TARGET_PATH,
)
from sft.chemistry.defect_nonstoichiometry_law_v1 import (
    EMPTY_ONE,
    OPERATIONAL_WITNESSES,
    defect_state,
)
from sft.chemistry.defect_nonstoichiometry_validation_v1 import (
    _source_rows,
    exact_analysis,
    prediction_program_document,
)
from sft.claim_evidence import EmptyOne
from sft.engine.exact import PositiveCount
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_016_law():
    assert all(witness[2] for witness in OPERATIONAL_WITNESSES)
    assert len(DEFECT_NONSTOICHIOMETRY_SPEC.dimensions) == 8
    vacancy = defect_state(
        "vacancy", ("A", "A", "B", "B"), ("A", EMPTY_ONE, "B", "B")
    )
    row = next(item for item in vacancy.reconciliation if item.species.label == "A")
    assert row.missing_support == PositiveCount(1)
    assert isinstance(row.added_support, EmptyOne)


def test_inorg_016_hashes_and_preserved_predecessor():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / V1_TARGET_PATH) == V1_TARGET_HASH
    assert hash_file(ROOT / V1_PRIMARY_PATH) == V1_PRIMARY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH


def test_inorg_016_external_vector():
    primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
    v1 = json.loads((ROOT / V1_TARGET_PATH).read_text(encoding="utf-8"))
    analysis = exact_analysis(_source_rows(ROOT), primary, v1)
    assert analysis["complete_target_count"] == 15
    assert analysis["complete_source_count"] == 5
    assert analysis["identity_only_unopened_target_count"] == 15
    assert analysis["v1_missing_registered_surface_count"] == 2
    assert analysis["definition_note_surface_count"] == 2
    assert analysis["scope_mismatch_or_distinction_count"] == 2
    assert analysis["all_rows_preserved"]


def test_inorg_016_survivor_and_value_free_prediction():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert "complete_definition_text" not in serialized
    assert "complete_source_note_text" not in serialized
    assert "target_payload_hash" not in serialized
    assert "Surface vacancies" not in serialized
    path = ROOT / "claims/SFT-CHEM-DEFECT-NONSTOICHIOMETRY-016/execution.py"
    spec = importlib.util.spec_from_file_location("inorg016_execution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(candidate) for candidate in census.candidates)
    assert len(census.candidates) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert all(control.passed for control in execution.program.run_controls())
