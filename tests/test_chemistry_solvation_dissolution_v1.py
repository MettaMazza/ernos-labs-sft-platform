import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.solvation_dissolution_batch_v1 import SOLVATION_DISSOLUTION_SPEC
from sft.chemistry.solvation_dissolution_law_v1 import (
    SolvationDissolutionAccount, common_support_replication_preserves_carrier,
    exact_solubility_capacity, external_order_as_fold_relation, forced_transfer_carrier,
)
from sft.chemistry.solvation_dissolution_validation_v1 import (
    SolvationDissolutionValidator, _identities, _prediction_map, _source_rows,
    exact_solvation_dissolution_analysis, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(mixed=False, reference=False):
    solvents = (HeldLabel("chemical-component", "water"),)
    if mixed:
        solvents += (HeldLabel("chemical-component", "ethanol"),)
    return SolvationDissolutionAccount(
        HeldLabel("chemical-component", "solute"), solvents,
        HeldLabel("chemical-state", "separated"), HeldLabel("chemical-state", "solution"),
        EmptyOne() if reference else PositiveRatio.from_pair(7, 5),
    )


def test_held_order_and_structural_absence():
    assert external_order_as_fold_relation("-2.49").orientation.label == "destination-solution-retained"
    assert external_order_as_fold_relation("1.23").orientation.label == "source-separated-state-retained"
    assert isinstance(external_order_as_fold_relation("0.00").magnitude, EmptyOne)
    assert exact_solubility_capacity("0.00015").fraction == PositiveRatio.from_pair(3, 20000).fraction


def test_complete_single_and_mixed_solvent_carriers():
    assert "single-solvent" in forced_transfer_carrier(account()).label
    assert "mixed-solvent" in forced_transfer_carrier(account(True)).label
    assert common_support_replication_preserves_carrier(account(), PositiveCount(5))


def test_invalid_collapsed_identity_and_negative_capacity_halt():
    with pytest.raises(InadmissibleExactValue):
        SolvationDissolutionAccount(
            HeldLabel("chemical-component", "same"), (HeldLabel("chemical-component", "same"),),
            HeldLabel("chemical-state", "source"), HeldLabel("chemical-state", "destination"), EmptyOne(),
        )
    with pytest.raises(InadmissibleExactValue):
        exact_solubility_capacity("-1")


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(SOLVATION_DISSOLUTION_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(SOLVATION_DISSOLUTION_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free():
    rows = _identities(ROOT)
    forbidden = {"solute_compound_id", "component_orgnums", "experimental_hydration_free_energy_kcal_per_mol_external_inscription", "solubility_mole_fraction_external_inscription", "target_payload_hash"}
    assert len(rows) == 799
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    assert "experimental_hydration_free_energy" not in rendered
    assert "solubility_mole_fraction" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")}
    )
    assert len(_prediction_map(execution.output)) == 799


def test_complete_external_vector_retains_every_class_and_row():
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-015-solvation-dissolution-v1/solvation-dissolution-primary-records-v1.json").read_text())
    analysis = exact_solvation_dissolution_analysis(_source_rows(ROOT), primary)
    assert analysis["all_799_records_retained"]
    assert analysis["all_642_solvation_and_157_dissolution_records_retained"]
    assert analysis["all_favorable_opposed_and_EmptyOne_solvation_rows_retained"]
    assert analysis["all_seven_dissolution_datasets_complete"]
    assert analysis["all_93_mixed_solvent_records_retained"]
    assert analysis["all_10_absent_solvent_condition_coordinates_are_EmptyOne"]
    assert analysis["calculated_or_correlated_companions_excluded_from_measurements"]
    assert analysis["no_imported_model_equation_logarithm_correlation_fit_or_selection"]


def test_postseal_validator_preserves_rows_and_controls():
    result = SolvationDissolutionValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 810
