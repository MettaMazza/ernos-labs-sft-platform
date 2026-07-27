import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.conformer_generation_equivalence_batch_v1 import CONFORMER_GENERATION_EQUIVALENCE_SPEC, PRIMARY_PATH
from sft.chemistry.conformer_generation_equivalence_law_v1 import ANTI, GAUCHE_FORWARD, HeldTorsionAlphabet, butane_four_site_census
from sft.chemistry.conformer_generation_equivalence_validation_v1 import _source_rows, exact_analysis, prediction_program_document
from sft.engine.canonical import sha256_identity
from sft.engine.exact import InadmissibleExactValue

ROOT = Path(__file__).resolve().parents[1]


def test_complete_generation_automorphism_and_orbit_partition():
    census = butane_four_site_census()
    assert len(census.generated_assignments) == 3
    assert len(census.automorphisms) == 2
    assert [len(group) for group in census.equivalence_classes] == [1, 2]
    assert sum(len(group) for group in census.equivalence_classes) == 3


def test_incomplete_torsion_reversal_halts():
    with pytest.raises(InadmissibleExactValue):
        HeldTorsionAlphabet((ANTI, GAUCHE_FORWARD), ((ANTI, ANTI),))


def test_complete_development_observed_external_census():
    analysis = exact_analysis(_source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text()))
    assert analysis["complete_external_conformer_class_labels"] == ["Anti", "Gauche"]
    assert analysis["complete_external_conformer_class_count"] == analysis["equivalence_class_count"] == 2
    assert analysis["external_gauche_adverse_false_row_preserved"]
    assert analysis["cccbdb_complete_table_count"] == 19
    assert analysis["cccbdb_complete_row_count"] == 105


def test_value_free_program_and_execution_build():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True).casefold()
    for forbidden in ("anti", "gauche", "16.6", "-125.79", "target_payload_hash"):
        assert forbidden not in encoded
    path = ROOT / "claims/SFT-CHEM-CONFORMER-GENERATION-EQUIVALENCE-005/execution.py"
    definition = importlib.util.spec_from_file_location("org005_test_execution", path)
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(row).survives for row in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
    assert sha256_identity(document).startswith("sha256:")
