from fractions import Fraction
import json
from pathlib import Path

import pytest

from sft.chemistry.formation_energy_batch_v1 import FORMATION_ENERGY_SPEC
from sft.chemistry.formation_energy_law_v1 import (
    EXACT_RESULT, MolecularFormationEnergyCarrier, exact_formation_state_relation,
    exact_reference_state_composition, repeated_formation_relation,
    shared_state_extension_preserves_formation_relation,
)
from sft.chemistry.formation_energy_validation_v1 import _prediction_map, _source_rows, prediction_program_document
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.claim_evidence import CapabilityClosedFoldInterpreter, EmptyOne, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def test_exact_reference_relation_orientations_and_successor() -> None:
    reference = exact_reference_state_composition((PositiveRatio.from_pair(5, 2), PositiveRatio.from_pair(7, 3)))
    assert reference.fraction == Fraction(29, 6)
    below_orientation, below = exact_formation_state_relation(PositiveRatio.from_pair(4, 1), reference)
    assert below_orientation.label == "product-below-reference" and isinstance(below, PositiveRatio) and below.fraction == Fraction(5, 6)
    above_orientation, above = exact_formation_state_relation(PositiveRatio.from_pair(6, 1), reference)
    assert above_orientation.label == "product-above-reference" and isinstance(above, PositiveRatio) and above.fraction == Fraction(7, 6)
    equal_orientation, equal = exact_formation_state_relation(reference, reference)
    assert equal_orientation.label == "product-reference-equal" and isinstance(equal, EmptyOne)
    assert shared_state_extension_preserves_formation_relation(PositiveRatio.from_pair(4, 1), reference, PositiveRatio.from_pair(11, 5))
    repeated_orientation, repeated = repeated_formation_relation(PositiveRatio.from_pair(4, 1), reference, PositiveCount(3))
    assert repeated_orientation == below_orientation and isinstance(repeated, PositiveRatio) and repeated.fraction == Fraction(5, 2)


def test_invalid_reference_or_state_halts() -> None:
    with pytest.raises(InadmissibleExactValue):
        exact_reference_state_composition(())
    with pytest.raises(InadmissibleExactValue):
        exact_formation_state_relation(PositiveRatio.from_pair(2, 1), HeldLabel("state", "not-a-ratio"))


def test_complete_carrier_retains_product_reference_condition_and_phase() -> None:
    carrier = MolecularFormationEnergyCarrier(
        HeldLabel("molecular-product", "water"), HeldLabel("molecular-product-state", "gas-state"),
        (HeldLabel("chemical-constituent", "hydrogen"), HeldLabel("chemical-constituent", "oxygen")),
        (HeldLabel("constituent-reference-state", "hydrogen-reference"), HeldLabel("constituent-reference-state", "oxygen-reference")),
        HeldLabel("thermochemical-reference-state-convention", "official-reference"), HeldLabel("temperature-reference", "held-temperature"),
        HeldLabel("phase-identity", "gas"), HeldLabel("held-energy-unit", "kJ-per-mol"),
    )
    assert carrier.product_identity.label == "water"
    with pytest.raises(InadmissibleExactValue):
        MolecularFormationEnergyCarrier(
            carrier.product_identity, carrier.product_state, carrier.constituent_identities,
            carrier.constituent_reference_states[:1], carrier.reference_state_convention,
            carrier.temperature_reference, carrier.phase_identity, carrier.energy_unit,
        )


def test_candidate_grammar_is_complete_unique_and_depth_independent() -> None:
    program = GeneratedObservationalChemistryProgram(FORMATION_ENERGY_SPEC, "sha256:" + "d" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    closure = program.closure_evidence(decisions)
    assert len(candidates) == len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(FORMATION_ENERGY_SPEC) == EXACT_RESULT
    assert closure.scope.value == "depth_independent"


def test_identity_registry_contains_no_values_presence_or_orientations() -> None:
    document = json.loads((ROOT / "experiments/external_sources/chemistry/formation_energy_target_identities_v1.json").read_text(encoding="utf-8"))
    forbidden = {"source_value_present", "source_value_inscription", "native_value", "external_state_orientation", "exact_positive_magnitude_kJ_per_mol", "structural_absence"}
    assert document["all_formation_values_presence_flags_and_orientations_absent"] is True
    assert len(document["rows"]) == 2098
    assert all(row["target_value_absent"] is True and not forbidden.intersection(row) for row in document["rows"])


def test_prediction_is_value_free_and_complete() -> None:
    document = prediction_program_document(ROOT)
    assert not any(instruction["opcode"] == "ratio" for instruction in document["instructions"])
    execution = CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(document), {"registered-premise": HeldLabel("sealed-derivation", "test-seal")})
    assert len(_prediction_map(execution.output)) == 2098


def test_complete_external_vector_preserves_all_classes() -> None:
    rows = _source_rows(ROOT)
    assert len(rows) == len({row["target_id"] for row in rows}) == 2098
    assert sum(isinstance(row["vault_value"], PositiveRatio) for row in rows) == 1463
    assert sum(row["result_class"] == "printed-equality-structural-EmptyOne" for row in rows) == 22
    assert sum(row["result_class"] == "unmeasured-structural-EmptyOne" for row in rows) == 613
    assert sum(row["source_orientation"] == "product-state-below-reference-state" for row in rows) == 756
    assert sum(row["source_orientation"] == "product-state-above-reference-state" for row in rows) == 707


def test_complete_source_boundary_is_explicit() -> None:
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/prop-013-formation-energy-v1/formation-energy-primary-records-v1.json").read_text(encoding="utf-8"))
    assert primary["complete_listed_species_count"] == 2186
    assert primary["complete_unique_formula_composition_query_count"] == 1193
    assert primary["complete_returned_charge_state_choice_count"] == 1832
    assert primary["complete_listed_composition_without_returned_choice_count"] == 83
    assert primary["complete_displayed_molecular_row_count"] == 1049
    assert primary["complete_reference_axis_cell_count"] == 2098
