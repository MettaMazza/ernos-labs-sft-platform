import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

from sft.chemistry.conformer_population_ordering_batch_v1 import CONFORMER_POPULATION_ORDERING_SPEC, PRIMARY_PATH
from sft.chemistry.conformer_population_ordering_law_v1 import append_observation, conditioned_population_census, ordered_positive_take
from sft.chemistry.conformer_population_ordering_validation_v1 import _source_rows, exact_analysis, prediction_program_document
from sft.chemistry.conformer_generation_equivalence_law_v1 import ExactConformerAssignment, butane_four_site_census
from sft.claim_evidence import PositiveRatio
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, InadmissibleExactValue

ROOT = Path(__file__).resolve().parents[1]


def test_exact_conditioned_populations_and_successor():
    conformers = butane_four_site_census(); anti, gauche_forward, gauche_reverse = conformers.generated_assignments
    census = conditioned_population_census(conformers, HeldLabel("observation-condition", "fixed-condition-and-timescale"), (anti, anti, gauche_forward, anti), (EMPTY_ONE, PositiveRatio.from_pair(3, 1)))
    assert [row.population.fraction for row in census.rows] == [Fraction(3, 4), Fraction(1, 4)]
    successor = append_observation(census, gauche_reverse)
    assert [row.population.fraction for row in successor.rows] == [Fraction(3, 5), Fraction(2, 5)]


def test_invalid_trace_and_reverse_take_halt():
    conformers = butane_four_site_census()
    with pytest.raises(InadmissibleExactValue):
        conditioned_population_census(conformers, HeldLabel("observation-condition", "fixed"), (ExactConformerAssignment((HeldLabel("torsion-state", "foreign"),)),), (EMPTY_ONE, PositiveRatio.from_pair(3, 1)))
    with pytest.raises(InadmissibleExactValue):
        ordered_positive_take(PositiveRatio.from_pair(1, 1), PositiveRatio.from_pair(3, 1))


def test_complete_blind_energy_population_and_adverse_vector():
    analysis = exact_analysis(_source_rows(ROOT), json.loads((ROOT / PRIMARY_PATH).read_text()))
    assert analysis["complete_target_count"] == 14
    assert analysis["ordered_population_fraction_sum"] == "1"
    assert analysis["ordered_population_order"] == ["tg", "tt", "pp", "pm"]
    assert analysis["fold_positive_energy_gaps"] == ["480", "178", "2605"]
    assert analysis["acs_supporting_measurement_table_count"] == 8
    assert analysis["acs_supporting_measurement_row_count"] == 224
    assert analysis["isotropic_population_exact_display_sum"] == "201/200"
    assert analysis["failed_v3_recorder_preserved"] and analysis["failed_core_legacy_route_preserved"]


def test_value_free_program_and_execution_build():
    document = prediction_program_document(ROOT); encoded = json.dumps(document, sort_keys=True).casefold()
    for forbidden in ("0.33", "0.51", "441", "3263", "298.5", "target_payload_hash"):
        assert forbidden not in encoded
    path = ROOT / "claims/SFT-CHEM-CONFORMER-POPULATION-ORDERING-006/execution.py"
    definition = importlib.util.spec_from_file_location("org006_test_execution", path); module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    execution = module.build_execution(ROOT); census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(row).survives for row in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
    assert sha256_identity(document).startswith("sha256:")
