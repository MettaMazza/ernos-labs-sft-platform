from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.transition_boundary_batch_v1 import PRIMARY_PATH, TRANSITION_BOUNDARY_SPEC
from sft.chemistry.transition_boundary_law_v1 import (
    TransitionPath, TransitionPathState, complete_path_append_preserves_boundaries,
    external_barrier_signature, forced_boundary_collection, forced_transition_boundary,
)
from sft.chemistry.transition_boundary_validation_v1 import (
    _identities, _source_rows, exact_transition_boundary_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def path(row: int, isotope: str, supports: tuple[int | None, ...]) -> TransitionPath:
    return TransitionPath(
        HeldLabel("registered-reaction", "activation"),
        HeldLabel("generated-reaction-path", f"path-{row}"),
        HeldLabel("held-isotopologue", isotope),
        tuple(
            TransitionPathState(
                HeldLabel("generated-path-state", f"state-{index}"),
                EmptyOne() if support is None else PositiveRatio.from_pair(support, 1),
            )
            for index, support in enumerate(supports, start=1)
        ),
        PositiveCount(row),
    )


def test_unique_finite_boundary_is_forced() -> None:
    carrier = forced_transition_boundary(path(1, "H2", (None, 2, 5, 3)))
    assert carrier.boundary_state.relative_support.fraction == Fraction(5)
    assert len(carrier.entry_word) == 2 and len(carrier.exit_word) == 1


def test_isotopologue_identity_and_source_order_are_retained() -> None:
    collection = forced_boundary_collection((path(1, "H2", (None, 5, 2)), path(2, "D2", (None, 3, 1))))
    assert tuple(row[2].label for row in collection.ordered_rows) == ("H2", "D2")


def test_complete_append_preserves_prior_boundary_trace() -> None:
    assert complete_path_append_preserves_boundaries((path(1, "H2", (None, 5, 2)),), path(2, "D2", (None, 3, 1)))


def test_tied_boundary_and_signed_orientation_mismatch_reject() -> None:
    with pytest.raises(InadmissibleExactValue):
        path(1, "H2", (None, 5, 5))
    with pytest.raises(InadmissibleExactValue):
        external_barrier_signature("−0.023", "held-temperature-order", "0.005")


def test_complete_value_free_identity_surface() -> None:
    rows = _identities(ROOT)
    serialized = json.dumps(rows, sort_keys=True)
    assert len(rows) == 2
    assert tuple(row["isotopologue_identity"] for row in rows) == ("H2", "D2")
    assert all(token not in serialized for token in ("0.01", "0.023", "0.045", "0.005", "75", "193"))


def test_complete_article_supplement_and_measured_pair_analysis() -> None:
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_transition_boundary_analysis(rows, primary)
    assert analysis["complete_article_and_thirteen_supplement_files_retained"]
    assert analysis["both_opposite_measured_temperature_directions_retained"]
    assert analysis["experimental_and_calculated_provenance_separated"]
    assert analysis["exact_measured_H2_apparent_barrier_magnitude_eV"] == "23/1000"
    assert analysis["exact_measured_D2_apparent_barrier_magnitude_eV"] == "9/200"


def test_prediction_contains_identities_not_values() -> None:
    serialized = json.dumps(prediction_program_document(ROOT), sort_keys=True)
    assert all(token not in serialized for token in ("0.01", "0.023", "0.045", "0.005", "75", "193"))
    assert "KIN-005-H2-EXPERIMENTAL-BOUNDARY-SIGNATURE" in serialized
    assert "KIN-005-D2-EXPERIMENTAL-BOUNDARY-SIGNATURE" in serialized


def test_execution_package_builds_under_sealed_engine() -> None:
    path_file = ROOT / "claims/SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005/execution.py"
    definition = importlib.util.spec_from_file_location("kin005_execution_test", path_file)
    assert definition and definition.loader
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == TRANSITION_BOUNDARY_SPEC.claim_id
