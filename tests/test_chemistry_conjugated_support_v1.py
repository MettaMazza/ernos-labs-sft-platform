import json
from pathlib import Path

import pytest

from sft.chemistry.conjugated_support_batch_v1 import (
    CONJUGATED_SUPPORT_SPEC,
    PRIMARY_PATH,
)
from sft.chemistry.conjugated_support_law_v1 import (
    append_opposed_fibre,
    conjugated_support,
)
from sft.chemistry.conjugated_support_validation_v1 import (
    _source_rows,
    exact_analysis,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def test_base_and_depth_independent_successor():
    base = conjugated_support(
        "base",
        ("a", "b", "c"),
        ("fold-fibre-one", "fold-fibre-two"),
    )
    successor = append_opposed_fibre(base, "d")
    assert base.atom_count == PositiveCount(3)
    assert base.support_count == PositiveCount(2)
    assert successor.atom_count == PositiveCount(4)
    assert successor.support_count == PositiveCount(3)
    assert successor.incidences[:2] == base.incidences


def test_repetition_omission_and_duplicate_halt():
    with pytest.raises(InadmissibleExactValue):
        conjugated_support(
            "repeated",
            ("a", "b", "c"),
            ("fold-fibre-one", "fold-fibre-one"),
        )
    with pytest.raises(InadmissibleExactValue):
        conjugated_support("omitted", ("a", "b", "c"), ("fold-fibre-one",))
    base = conjugated_support(
        "base",
        ("a", "b", "c"),
        ("fold-fibre-one", "fold-fibre-two"),
    )
    with pytest.raises(InadmissibleExactValue):
        append_opposed_fibre(base, "b")


def test_complete_corrected_external_surface():
    rows = _source_rows(ROOT)
    analysis = exact_analysis(rows, json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8")))
    assert analysis["complete_target_count"] == 10
    assert analysis["complete_source_count"] == 7
    assert analysis["conjugated_rcc_external_strings"] == ("1.476", "1.337")
    assert analysis["separated_control_rcc_external_strings"] == ("1.511", "1.339")
    assert analysis["uv_visible_declared_point_count"] == 502
    assert analysis["uv_visible_preserved_point_count"] == 502
    assert analysis["preserved_v1_parser_overrun_count"] == 1
    assert analysis["v2_corrected_table_count"] == 2
    assert analysis["external_signed_control_inscription_preserved"]


def test_prediction_program_is_value_free_and_complete():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True)
    assert len(CONJUGATED_SUPPORT_SPEC.target_rows) == 10
    assert "target_payload_hash" not in encoded
    assert "1.476" not in encoded
    assert "NPOINTS" not in encoded
    assert sha256_identity(document).startswith("sha256:")
