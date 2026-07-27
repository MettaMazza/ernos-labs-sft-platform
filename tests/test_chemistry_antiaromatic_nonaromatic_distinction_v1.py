import json
from pathlib import Path

import pytest

from sft.chemistry.antiaromatic_nonaromatic_distinction_batch_v1 import (
    ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC,
    PRIMARY_PATH,
)
from sft.chemistry.antiaromatic_nonaromatic_distinction_law_v1 import (
    ANTIAROMATIC,
    BROKEN_PLANE,
    COMPLETE_CONJUGATION,
    ExactSameCycleAlternative,
    append_complete_layer,
    complete_ordered_pair_cells,
    nonaromatic_alternative,
    same_cycle_census,
    same_cycle_stability_order,
)
from sft.chemistry.antiaromatic_nonaromatic_distinction_validation_v1 import (
    _source_rows,
    exact_analysis,
    prediction_program_document,
)
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine.canonical import sha256_identity
from sft.engine.exact import InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def test_three_class_support_order_and_depth_independent_successor():
    census = same_cycle_census("carrier", tuple(f"c{i}" for i in range(1, 7)))
    order = same_cycle_stability_order(census)
    assert [census[0].recurrence_support, census[1].recurrence_support, census[2].recurrence_support] == [
        PositiveCount(6), EMPTY_ONE, PositiveCount(4)
    ]
    assert tuple(row.label for row in order.exact_order) == (
        "closed-aromatic-recurrence", "broken-nonaromatic-recurrence", "frustrated-antiaromatic-recurrence"
    )
    assert [append_complete_layer(census[0]).recurrence_support, append_complete_layer(census[1]).recurrence_support, append_complete_layer(census[2]).recurrence_support] == [
        PositiveCount(10), EMPTY_ONE, PositiveCount(8)
    ]


def test_inconsistent_class_missing_break_and_numerical_zero_halt():
    census = same_cycle_census("carrier", tuple(f"c{i}" for i in range(1, 7)))
    with pytest.raises(InadmissibleExactValue):
        ExactSameCycleAlternative(
            census[2].molecular_carrier,
            census[2].cycle,
            BROKEN_PLANE,
            COMPLETE_CONJUGATION,
            ANTIAROMATIC,
            PositiveCount(4),
            (complete_ordered_pair_cells(),),
        )
    with pytest.raises(InadmissibleExactValue):
        nonaromatic_alternative(census[1].cycle, break_plane=False, break_conjugation=False)
    with pytest.raises(InadmissibleExactValue):
        PositiveCount(0)


def test_complete_blind_and_development_structure_energy_surfaces():
    rows = _source_rows(ROOT)
    analysis = exact_analysis(rows, json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8")))
    assert analysis["complete_target_count"] == 5
    assert analysis["development_observed_target_count"] == 3
    assert analysis["outcome_unopened_blind_target_count"] == 2
    assert analysis["blind_conformation_external_strings"] == {
        "cyclobutadiene": "D2H", "cyclooctatetraene": "D2D"
    }
    assert analysis["blind_cyclooctatetraene_alternating_cc_bond_external_strings_angstrom"] == ["1.337", "1.470"]
    assert analysis["blind_cyclobutadiene_hfg_absence_preserved"]
    assert analysis["exact_repeated_ch_unit_hfg_gap_kj_per_mol"] == "14027/600"
    assert analysis["exact_repeated_ch_unit_lower_gap_kj_per_mol"] == "578/25"
    assert sum(analysis["blind_cccbdb_complete_row_counts"].values()) == 172


def test_prediction_program_is_value_free_and_complete():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True).casefold()
    assert len(ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC.target_rows) == 5
    for forbidden in (
        "cyclobutadiene", "cyclooctatetraene", "d2h", "d2d", "1.337", "1.470",
        "82.93", "297.60", "8.160", "hfg", "target_payload_hash",
    ):
        assert forbidden not in encoded
    assert sha256_identity(document).startswith("sha256:")
