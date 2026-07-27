import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.ligand_state_splitting_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, LIGAND_STATE_SPLITTING_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.ligand_state_splitting_law_v1 import (
    LigandInteractionGeometry, OPERATIONAL_WITNESSES, forced_ligand_state_splitting,
    four_complete_axis_geometry, generate_complete_rank_two_support, removed_ligand_remerging,
    six_direct_axis_geometry,
)
from sft.chemistry.ligand_state_splitting_validation_v1 import (
    _source_rows, exact_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_006_exact_law_and_complete_256_form_grammar():
    assert len(generate_complete_rank_two_support()) == 5
    assert all(passed for _, _, passed in OPERATIONAL_WITNESSES)
    spec = LIGAND_STATE_SPLITTING_SPEC
    assert len(spec.dimensions) == 8
    assert all(len(row.choices) == 2 for row in spec.dimensions)
    assert 2 ** len(spec.dimensions) == 256


def test_inorg_006_exact_partitions_separations_balances_and_remerging():
    six = forced_ligand_state_splitting(six_direct_axis_geometry())
    four = forced_ligand_state_splitting(four_complete_axis_geometry())
    removed = removed_ligand_remerging(HeldLabel("coordination-central-occurrence", "test-centre"))
    assert tuple(level.positive_multiplicity.value for level in six.levels) == (3, 2)
    assert tuple(str(part.value) for part in six.adjacent_positive_separations) == ("2/3",)
    assert (str(six.lower_distance_from_unsplit_or_absence.value), str(six.upper_distance_from_unsplit_or_absence.value)) == ("2/5", "3/5")
    assert tuple(level.positive_multiplicity.value for level in four.levels) == (2, 3)
    assert tuple(str(part.value) for part in four.adjacent_positive_separations) == ("1",)
    assert (str(four.lower_distance_from_unsplit_or_absence.value), str(four.upper_distance_from_unsplit_or_absence.value)) == ("3/5", "2/5")
    assert len(removed.levels) == 1 and removed.levels[0].positive_multiplicity.value == 5


def test_inorg_006_rejects_third_fibre_and_empty_geometry():
    with pytest.raises(InadmissibleExactValue):
        LigandInteractionGeometry(
            HeldLabel("coordination-central-occurrence", "bad"),
            ((HeldLabel("fold-orientation-fibre", "fibre-three"), EmptyOne(), EmptyOne()),),
        )
    with pytest.raises(InadmissibleExactValue):
        LigandInteractionGeometry(HeldLabel("coordination-central-occurrence", "bad"), ())


def test_inorg_006_value_free_identity_and_complete_postseal_vector():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    identities = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert identities["complete_registered_target_count"] == 32
    assert identities["target_values_peak_positions_intensities_band_counts_definitions_and_outcomes_present"] is False
    assert len({row["target_id"] for row in identities["rows"]}) == 32


def test_inorg_006_empirical_vector_preserves_blind_adverse_and_ancillary_rows():
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_analysis(rows, primary)
    assert analysis["blind_spectrum_payload_count"] == 1
    assert analysis["blind_complete_interior_maximum_counts"] == (2,)
    assert analysis["blind_exact_interior_peak_positions"] == (("48361/200", "77817/200"),)
    assert analysis["blind_exact_adjacent_peak_separations"] == (("3682/25",),)
    assert analysis["blind_distinguishability_condition_passed"]
    assert analysis["law_sealed_adverse_absence_count"] == 2
    assert analysis["development_ancillary_count"] == 12
    assert analysis["complete_32_rows_preserved"]


def test_inorg_006_prediction_is_capability_closed_and_target_free():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True)
    assert TARGET_HASH not in encoded
    assert "target_payload_hash" not in encoded
    assert "48361/200" not in encoded
    assert {row["opcode"] for row in document["instructions"]} <= {"input", "label", "word", "table", "emit"}


def test_inorg_006_execution_builds_and_enumerates_one_survivor():
    path = ROOT / "claims/SFT-CHEM-LIGAND-STATE-SPLITTING-006/execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_inorg_006_test", path)
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
