import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_diffusion_batch_v1 import MOLECULAR_DIFFUSION_SPEC
from sft.chemistry.molecular_diffusion_law_v1 import (
    MolecularDiffusionAccount, complete_constituent_conservation, external_diffusion_magnitude,
    forced_counted_diffusion, transition_replication_preserves_relation,
)
from sft.chemistry.molecular_diffusion_validation_v1 import (
    MolecularDiffusionValidator, _identities, _prediction_map, _source_rows,
    exact_molecular_diffusion_analysis, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def account(diffusion_class="binary", reverse=False):
    components = (HeldLabel("chemical-component", "migrant"), HeldLabel("chemical-component", "medium"))
    return MolecularDiffusionAccount(
        components[0], components, HeldLabel("diffusion-class", diffusion_class), HeldLabel("chemical-phase", "liquid"),
        PositiveCount(4 if reverse else 3), PositiveCount(3 if reverse else 4),
        PositiveCount(7), PositiveCount(5), (PositiveRatio.from_pair(29815, 100), EmptyOne()),
    )


def test_three_classes_held_orientation_and_exact_density():
    assert forced_counted_diffusion(account("binary")).carrier.label.startswith("binary-")
    assert forced_counted_diffusion(account("self")).carrier.label.startswith("self-")
    assert forced_counted_diffusion(account("tracer")).carrier.label.startswith("tracer-")
    assert forced_counted_diffusion(account()).orientation.label == "toward-later-generated-cell"
    assert forced_counted_diffusion(account(reverse=True)).orientation.label == "toward-earlier-generated-cell"
    assert forced_counted_diffusion(account()).transition_density.fraction == PositiveRatio.from_pair(7, 5).fraction


def test_conservation_replication_and_positive_external_support():
    components = account().constituent_identities
    assert complete_constituent_conservation(components, tuple(reversed(components)))
    assert transition_replication_preserves_relation(account("tracer"), PositiveCount(6))
    assert external_diffusion_magnitude("1.945e-09").fraction.numerator > 0


def test_nonadjacent_and_negative_magnitude_halt():
    with pytest.raises(InadmissibleExactValue):
        MolecularDiffusionAccount(
            HeldLabel("chemical-component", "migrant"), (HeldLabel("chemical-component", "migrant"),),
            HeldLabel("diffusion-class", "self"), HeldLabel("chemical-phase", "liquid"),
            PositiveCount(2), PositiveCount(4), PositiveCount(1), PositiveCount(1), (EmptyOne(),),
        )
    with pytest.raises(InadmissibleExactValue):
        external_diffusion_magnitude("-1")


def test_candidate_grammar_complete_unique_depth_independent():
    program = GeneratedObservationalChemistryProgram(MOLECULAR_DIFFUSION_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(MOLECULAR_DIFFUSION_SPEC)
    assert closure.scope.value == "depth_independent"


def test_identity_registry_is_complete_and_value_free():
    rows = _identities(ROOT)
    forbidden = {"component_orgnums", "measurement_method", "diffusion_coefficient_m2_per_s_external_inscription", "target_payload_hash"}
    assert len(rows) == 164
    assert all(not forbidden.intersection(row) for row in rows)


def test_prediction_is_complete_and_value_free():
    document = prediction_program_document(ROOT)
    rendered = json.dumps(document, sort_keys=True)
    assert "diffusion_coefficient_m2_per_s_external_inscription" not in rendered
    assert "measurement_method" not in rendered
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "unit-check")}
    )
    assert len(_prediction_map(execution.output)) == 164


def test_complete_external_vector_retains_classes_sources_and_companions():
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-016-molecular-diffusion-v1/molecular-diffusion-primary-records-v1.json").read_text())
    analysis = exact_molecular_diffusion_analysis(_source_rows(ROOT), primary)
    assert analysis["all_164_records_retained"]
    assert analysis["all_138_binary_4_self_22_tracer_records_retained"]
    assert analysis["all_11_diffusion_datasets_complete"]
    assert analysis["all_three_methods_and_classes_retained"]
    assert analysis["all_liquid_and_subsupercritical_phase_rows_retained"]
    assert analysis["all_26_absent_condition_coordinates_are_EmptyOne"]
    assert analysis["complete_three_sources_and_companions_preserved"]
    assert analysis["non_diffusion_companions_excluded_from_measurements"]
    assert analysis["no_imported_transport_model_random_premise_fit_or_selection"]


def test_postseal_validator_preserves_rows_and_controls():
    result = MolecularDiffusionValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "a" * 64))
    assert result.passed is True
    assert result.all_rows_preserved is True
    assert len(result.measurements) == 174
