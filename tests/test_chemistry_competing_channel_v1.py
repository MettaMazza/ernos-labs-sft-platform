from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.competing_channel_batch_v1 import COMPETING_CHANNEL_SPEC, PRIMARY_PATH
from sft.chemistry.competing_channel_law_v1 import (
    CompleteChannelRecord, ProductChannelSupport, complete_channel_append_preserves_prior_rows,
    forced_competing_channel_branching,
)
from sft.chemistry.competing_channel_validation_v1 import (
    _identities, _source_rows, exact_competing_channel_analysis, prediction_program_document,
)
from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def record(values: tuple[int | None, ...]) -> CompleteChannelRecord:
    return CompleteChannelRecord(
        HeldLabel("registered-reaction", "reaction"), HeldLabel("held-condition", "condition"),
        tuple(ProductChannelSupport(
            HeldLabel("registered-product-channel", f"product-{index}"),
            EmptyOne() if value is None else PositiveRatio.from_pair(value, 1), PositiveCount(index),
        ) for index, value in enumerate(values, start=1)),
    )


def test_exact_complete_support_forces_branch_shares() -> None:
    relation = forced_competing_channel_branching(record((2, 3)))
    assert relation.complete_support.fraction == Fraction(5)
    assert tuple(row.share_of_complete_support.fraction for row in relation.ordered_rows) == (Fraction(2, 5), Fraction(3, 5))


def test_complete_partition_reconstructs_one_and_retains_emptyone() -> None:
    relation = forced_competing_channel_branching(record((2, None, 3)))
    shares = tuple(row.share_of_complete_support for row in relation.ordered_rows)
    assert isinstance(shares[1], EmptyOne)
    assert sum(row.fraction for row in shares if isinstance(row, PositiveRatio)) == Fraction(1)


def test_complete_channel_successor_preserves_prior_identity_and_support() -> None:
    successor = ProductChannelSupport(HeldLabel("registered-product-channel", "product-3"), PositiveRatio.from_pair(1, 1), PositiveCount(3))
    assert complete_channel_append_preserves_prior_rows(record((2, 3)), successor)


def test_duplicate_or_gapped_channel_word_rejects() -> None:
    with pytest.raises(InadmissibleExactValue):
        CompleteChannelRecord(
            HeldLabel("registered-reaction", "r"), HeldLabel("held-condition", "c"),
            (
                ProductChannelSupport(HeldLabel("registered-product-channel", "p"), PositiveRatio.from_pair(1, 1), PositiveCount(1)),
                ProductChannelSupport(HeldLabel("registered-product-channel", "p"), PositiveRatio.from_pair(2, 1), PositiveCount(2)),
            ),
        )


def test_complete_value_free_eight_channel_identity_surface() -> None:
    rows = _identities(ROOT)
    forbidden = {"experimental_branching_percent_external_inscription", "experimental_uncertainty_exact_fraction"}
    assert len(rows) == 8
    assert all(not forbidden.intersection(row) for row in rows)


def test_complete_external_branching_analysis() -> None:
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_competing_channel_analysis(rows, primary)
    assert analysis["all_eight_source_rows_and_product_identities_retained"]
    assert analysis["forced_shares_match_complete_postseal_experimental_vector"]
    assert analysis["complete_channel_partition_reconstructs_One"]
    assert analysis["complete_article_nineteen_files_and_two_pdfs_retained"]
    assert analysis["exact_experimental_branching_range"] == {"minimum": "3/50", "maximum": "23/100"}


def test_prediction_contains_identities_not_branch_values() -> None:
    document = prediction_program_document(ROOT)
    serialized = json.dumps(document, sort_keys=True)
    assert "experimental_branching_percent_external_inscription" not in serialized
    assert "KIN-006-PRODUCT-CHANNEL-01" in serialized and "KIN-006-PRODUCT-CHANNEL-08" in serialized


def test_execution_package_builds_under_sealed_engine() -> None:
    path_file = ROOT / "claims/SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006/execution.py"
    definition = importlib.util.spec_from_file_location("kin006_execution_test", path_file)
    assert definition and definition.loader
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    assert execution.program.registration.claim_id == COMPETING_CHANNEL_SPEC.claim_id
