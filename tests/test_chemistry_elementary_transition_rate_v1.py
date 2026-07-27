from fractions import Fraction
import importlib.util
from pathlib import Path

import pytest

from sft.chemistry.elementary_transition_rate_batch_v1 import ELEMENTARY_TRANSITION_RATE_SPEC
from sft.chemistry.elementary_transition_rate_law_v1 import (
    ElementaryTransitionAccount, common_event_resource_replication_preserves_rate,
    external_rate_magnitude, forced_elementary_transition_rate,
)
from sft.chemistry.elementary_transition_rate_validation_v1 import (
    _identities, _source_rows, exact_elementary_rate_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def account() -> ElementaryTransitionAccount:
    return ElementaryTransitionAccount(
        HeldLabel("registered-elementary-reaction", "r"), HeldLabel("molecular-state", "a"),
        HeldLabel("molecular-state", "b"), PositiveCount(6), PositiveCount(4), PositiveCount(3),
        (PositiveRatio.from_pair(638, 1), EmptyOne()),
    )


def test_exact_counted_rate_and_held_orientation() -> None:
    result = forced_elementary_transition_rate(account())
    assert result.event_response.fraction == Fraction(1, 2)
    assert result.orientation.label == "a-to-b"


def test_common_event_tick_replication_is_depth_independent() -> None:
    assert common_event_resource_replication_preserves_rate(account(), PositiveCount(11))


def test_identity_transition_is_rejected() -> None:
    with pytest.raises(InadmissibleExactValue):
        ElementaryTransitionAccount(
            HeldLabel("registered-elementary-reaction", "r"), HeldLabel("molecular-state", "a"),
            HeldLabel("molecular-state", "a"), PositiveCount(1), PositiveCount(1), PositiveCount(1),
            (EmptyOne(),),
        )


def test_external_exact_positive_rate_and_negative_control() -> None:
    assert external_rate_magnitude("6.37E-4").fraction == Fraction(637, 1_000_000)
    with pytest.raises(InadmissibleExactValue):
        external_rate_magnitude("-1")


def test_complete_value_free_identity_surface() -> None:
    rows = _identities(ROOT)
    assert len(rows) == 46
    assert all("rate_external_inscription" not in row for row in rows)


def test_complete_external_surface_and_exact_analysis() -> None:
    rows = _source_rows(ROOT)
    primary = __import__("json").loads((ROOT / "experiments/external_sources/chemistry/snapshots/kin-001-elementary-transition-rate-v1/elementary-transition-rate-primary-records-v1.json").read_text())
    analysis = exact_elementary_rate_analysis(rows, primary)
    assert analysis["all_46_rows_retained"]
    assert analysis["source_declared_order_row_counts"] == {"1": 4, "2": 24, "3": 18}


def test_prediction_program_contains_identities_not_targets() -> None:
    document = prediction_program_document(ROOT)
    serialized = __import__("json").dumps(document, sort_keys=True)
    assert "6.37E-4" not in serialized
    assert "SFT-CHEM-KIN-001-ELEMENTARY-RATE-0001" in serialized


def test_execution_package_builds_under_sealed_engine() -> None:
    path = ROOT / "claims/SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001/execution.py"
    definition = importlib.util.spec_from_file_location("kin001_execution_test", path)
    assert definition and definition.loader
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == ELEMENTARY_TRANSITION_RATE_SPEC.claim_id
