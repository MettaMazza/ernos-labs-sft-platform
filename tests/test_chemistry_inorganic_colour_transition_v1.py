import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.inorganic_colour_transition_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, INORGANIC_COLOUR_TRANSITION_SPEC, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.inorganic_colour_transition_law_v1 import (
    OPERATIONAL_WITNESSES, build_exact_transition, forced_selective_absorption, generate_complete_carrier_transition_classes,
)
from sft.chemistry.inorganic_colour_transition_validation_v1 import _source_rows, exact_analysis, prediction_program_document
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[1]


def test_inorg_008_exact_law_and_complete_grammar():
    assert all(row[2] for row in OPERATIONAL_WITNESSES)
    assert len(INORGANIC_COLOUR_TRANSITION_SPEC.dimensions) == 8
    assert 2 ** len(INORGANIC_COLOUR_TRANSITION_SPEC.dimensions) == 256
    assert tuple(row.label for row in generate_complete_carrier_transition_classes()) == ("ligand-to-ligand", "ligand-to-metal", "metal-to-ligand", "metal-to-metal")


def test_inorg_008_exact_transition_and_colour_partition():
    transition = build_exact_transition("c", "ligand", "metal", "a", "b", PositiveCount(1), PositiveCount(3))
    incident = tuple(HeldLabel("observation-distinction", f"d-{i}") for i in range(1, 4))
    result = forced_selective_absorption(transition, incident, (incident[1],))
    assert transition.positive_order_gap.value == 2
    assert result.absorbed_count.value == 1 and result.retained_colour_count.value == 2
    with pytest.raises(InadmissibleExactValue):
        forced_selective_absorption(transition, incident, incident)


def test_inorg_008_value_free_identity_and_postseal_hashes():
    assert hash_file(ROOT / IDENTITY_PATH) == IDENTITY_HASH
    assert hash_file(ROOT / TARGET_PATH) == TARGET_HASH
    assert hash_file(ROOT / PRIMARY_PATH) == PRIMARY_HASH
    identities = json.loads((ROOT / IDENTITY_PATH).read_text())
    assert identities["complete_registered_target_count"] == 8
    assert identities["target_values_definitions_peak_positions_intensities_band_counts_outcomes_or_payload_hashes_present"] is False


def test_inorg_008_complete_external_vector_and_custody():
    analysis = exact_analysis(_source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text()))
    assert analysis["spectrum_count"] == 4
    assert analysis["point_count_vector"] == (224, 79, 80, 73) and analysis["total_point_count"] == 456
    assert analysis["interior_maximum_count_vector"] == (2, 2, 1, 2)
    assert analysis["all_spectra_selective"] and analysis["originally_blind_count"] == 1
    assert analysis["source_recapture_count"] == 0


def test_inorg_008_prediction_target_free_and_one_survivor():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True)
    assert "target_payload_hash" not in encoded and "48361/200" not in encoded
    path = ROOT / "claims/SFT-CHEM-INORGANIC-COLOUR-ELECTRONIC-TRANSITION-008/execution.py"
    definition = importlib.util.spec_from_file_location("inorg008_test", path)
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    census = execution.program.generate_candidates()
    decisions = tuple(execution.program.decide_candidate(row) for row in census.candidates)
    assert len(census.candidates) == 256 and sum(row.survives for row in decisions) == 1
    assert execution.program.closure_evidence(decisions).scope.value == "depth_independent"
    assert all(row.passed for row in execution.program.run_controls())
