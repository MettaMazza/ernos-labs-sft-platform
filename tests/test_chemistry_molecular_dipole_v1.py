from fractions import Fraction
import json
from pathlib import Path

import pytest

from sft.chemistry.molecular_dipole_batch_v1 import (
    GeneratedFiniteMolecularDipoleChemistryProgram,
    MOLECULAR_DIPOLE_SPEC,
)
from sft.chemistry.molecular_dipole_law_v1 import (
    DipoleComponent,
    EXACT_RESULT,
    exact_squared_magnitude,
    registered_molecular_dipole_carriers,
)
from sft.chemistry.molecular_dipole_validation_v1 import (
    _load_targets,
    _validate_structural_prediction,
    prediction_program_document,
)
from sft.claim_evidence import EMPTY_ONE, CapabilityClosedFoldInterpreter, PositiveRatio, fold_program_from_mapping
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[1]


def component(axis: str, numerator: int, denominator: int) -> DipoleComponent:
    return DipoleComponent(
        HeldLabel("dipole-axis", axis),
        HeldLabel("held-dipole-orientation", "retained-side"),
        PositiveRatio.from_pair(numerator, denominator),
    )


def test_exact_squared_magnitude_uses_empty_one_and_positive_exact_junction() -> None:
    assert exact_squared_magnitude(()) is EMPTY_ONE
    assert exact_squared_magnitude((component("b", 3, 2),)).fraction == Fraction(9, 4)
    assert exact_squared_magnitude((component("a", 3, 5), component("b", 4, 5))).fraction == Fraction(1, 1)


def test_duplicate_axis_and_invalid_forms_halt() -> None:
    item = component("a", 1, 1)
    with pytest.raises(InadmissibleExactValue):
        exact_squared_magnitude((item, item))
    with pytest.raises(InadmissibleExactValue):
        DipoleComponent(
            HeldLabel("not-an-axis", "a"),
            HeldLabel("held-dipole-orientation", "side"),
            PositiveRatio.from_pair(1, 1),
        )


def test_registered_symmetry_forces_complete_component_pattern() -> None:
    carriers = registered_molecular_dipole_carriers()
    assert tuple(row.species.label for row in carriers) == ("H2", "D2", "H2O", "D2O", "HDO")
    assert tuple(len(row.component_axes) for row in carriers) == (0, 0, 1, 1, 2)
    assert tuple(row.structural_magnitude_class.label for row in carriers) == (
        "structural-EmptyOne",
        "structural-EmptyOne",
        "one-positive-component",
        "one-positive-component",
        "multiple-orthogonal-positive-components",
    )


def test_candidate_grammar_is_complete_and_unique() -> None:
    program = GeneratedFiniteMolecularDipoleChemistryProgram(MOLECULAR_DIPOLE_SPEC, "sha256:" + "e" * 64)
    candidates = program.generate_candidates().candidates
    decisions = tuple(program.decide_candidate(candidate) for candidate in candidates)
    assert len(candidates) == 256
    assert len({candidate.candidate_id for candidate in candidates}) == 256
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(MOLECULAR_DIPOLE_SPEC) == EXACT_RESULT


def test_prediction_is_value_free_and_structurally_complete() -> None:
    document = prediction_program_document()
    target_document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_dipole_withheld_targets_v1.json").read_text(encoding="utf-8")
    )
    program_text = json.dumps(document, sort_keys=True)
    assert all(str(row["inscription"]) not in program_text for row in target_document["rows"])
    execution = CapabilityClosedFoldInterpreter().execute(
        fold_program_from_mapping(document),
        {"registered-premise": HeldLabel("sealed-derivation", "test-seal")},
    )
    _validate_structural_prediction(execution.output)


def test_all_nine_postseal_rows_reconstruct_and_match_exact_relations() -> None:
    rows = _load_targets(ROOT)
    assert len(rows) == 9
    by_species = {
        species: tuple(row for row in rows if row["species"] == species)
        for species in ("H2", "D2", "H2O", "D2O", "HDO")
    }
    assert by_species["H2"][0]["value"] is EMPTY_ONE
    assert by_species["D2"][0]["value"] is EMPTY_ONE
    for species, count in (("H2O", 1), ("D2O", 1), ("HDO", 2)):
        components = tuple(row for row in by_species[species] if row["measurement_role"] == "component-magnitude")
        total = next(row for row in by_species[species] if row["measurement_role"] == "total-magnitude")
        assert len(components) == count
        lower_parts = tuple(row["lower"] ** 2 for row in components)
        upper_parts = tuple(row["upper"] ** 2 for row in components)
        derived_lower, derived_upper = lower_parts[0], upper_parts[0]
        for part in lower_parts[1:]:
            derived_lower += part
        for part in upper_parts[1:]:
            derived_upper += part
        observed_lower, observed_upper = total["lower"] ** 2, total["upper"] ** 2
        assert not (derived_upper < observed_lower or observed_upper < derived_lower)


def test_identity_registry_contains_no_measurement_value() -> None:
    document = json.loads(
        (ROOT / "experiments/external_sources/chemistry/molecular_dipole_target_identities_v1.json").read_text(encoding="utf-8")
    )
    forbidden = {"central", "uncertainty", "lower", "upper", "inscription", "raw_source_inscription", "source_glyph"}
    assert document["all_measurement_values_absent"] is True
    assert len(document["rows"]) == 9
    assert all(row["target_value_absent"] is True and not forbidden.intersection(row) for row in document["rows"])
