import importlib.util
import json
from pathlib import Path

from sft.chemistry.inorganic_acid_base_redox_network_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    INORGANIC_ACID_BASE_REDOX_NETWORK_SPEC,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.inorganic_acid_base_redox_network_law_v1 import (
    OPERATIONAL_WITNESSES,
    lewis_step,
    redox_step,
    reverse_redox,
)
from sft.chemistry.inorganic_acid_base_redox_network_validation_v1 import (
    _source_rows,
    exact_analysis,
    prediction_program_document,
)
from sft.engine.exact import PositiveCount
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_017_law():
    assert all(witness[2] for witness in OPERATIONAL_WITNESSES)
    assert len(INORGANIC_ACID_BASE_REDOX_NETWORK_SPEC.dimensions) == 8
    pair = lewis_step("pair", "base", "acid", "adduct")
    forward = redox_step("forward", "donor", "acceptor", PositiveCount(2))
    reverse = reverse_redox(forward, "reverse")
    assert len(pair.electron_pair) == 2
    assert reverse.electron_support == forward.electron_support
    assert reverse.electron_donor == forward.electron_acceptor


def test_inorg_017_hashes():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH


def test_inorg_017_external_vector():
    analysis = exact_analysis(
        _source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
    )
    assert analysis["complete_target_count"] == 15
    assert analysis["complete_source_count"] == 5
    assert analysis["development_observed_target_count"] == 7
    assert analysis["identity_only_unopened_target_count"] == 8
    assert analysis["rendered_structure_absence_count"] == 1
    assert analysis["all_rows_preserved"]


def test_inorg_017_survivor_and_value_free_prediction():
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert "complete_definition_text" not in serialized
    assert "target_payload_hash" not in serialized
    assert "For example:" not in serialized
    assert "oxidation number" not in serialized
    path = ROOT / "claims/SFT-CHEM-INORGANIC-ACID-BASE-REDOX-NETWORK-017/execution.py"
    spec = importlib.util.spec_from_file_location("inorg017_execution", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(candidate) for candidate in census.candidates)
    assert len(census.candidates) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert all(control.passed for control in execution.program.run_controls())
