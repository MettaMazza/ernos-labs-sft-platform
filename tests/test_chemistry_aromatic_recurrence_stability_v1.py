import json
from pathlib import Path

import pytest

from sft.chemistry.aromatic_recurrence_stability_batch_v1 import (
    AROMATIC_RECURRENCE_STABILITY_SPEC,
    PRIMARY_PATH,
)
from sft.chemistry.aromatic_recurrence_stability_law_v1 import (
    ExactAromaticRecurrence,
    append_complete_pair_layer,
    aromatic_recurrence,
    aromatic_stability_order,
    complete_ordered_pair_cells,
)
from sft.chemistry.aromatic_recurrence_stability_validation_v1 import (
    _source_rows,
    exact_analysis,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def test_support_sequence_first_return_and_positive_order():
    base = aromatic_recurrence("carrier", tuple(f"c{i}" for i in range(1, 7)), PositiveCount(1))
    first = append_complete_pair_layer(base)
    second = append_complete_pair_layer(first)
    assert (base.positive_support_count, first.positive_support_count, second.positive_support_count) == (
        PositiveCount(6), PositiveCount(10), PositiveCount(14)
    )
    assert base.first_return_trace[0] == base.first_return_trace[-1]
    assert base.complete_registered_perturbation_closure
    assert aromatic_stability_order(base).closed_recurrence_precedes_opened_reference


def test_incomplete_layer_duplicate_boundary_and_open_cycle_halt():
    base = aromatic_recurrence("carrier", tuple(f"c{i}" for i in range(1, 7)), PositiveCount(1))
    with pytest.raises(InadmissibleExactValue):
        ExactAromaticRecurrence(
            base.molecular_carrier, base.cycle, base.boundary_fibres,
            ((complete_ordered_pair_cells()[0], complete_ordered_pair_cells()[1]),),
        )
    with pytest.raises(InadmissibleExactValue):
        ExactAromaticRecurrence(
            base.molecular_carrier, base.cycle,
            (base.boundary_fibres[0], base.boundary_fibres[0]), base.pair_cell_layers,
        )
    with pytest.raises(InadmissibleExactValue):
        aromatic_recurrence("invalid", ("left", "right"), PositiveCount(1))


def test_complete_blind_and_development_surfaces():
    rows = _source_rows(ROOT)
    analysis = exact_analysis(rows, json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8")))
    assert analysis["complete_target_count"] == 9
    assert analysis["development_observed_target_count"] == 6
    assert analysis["outcome_unopened_blind_target_count"] == 3
    assert analysis["blind_hfg_298_external_strings"] == {
        "benzene": "82.93", "cyclohexene": "-4.32", "cyclohexane": "-123.14"
    }
    assert analysis["blind_recurrence_stability_excess_magnitude_kj_per_mol"] == "150.39"
    assert analysis["blind_conservative_uncertainty_envelope_kj_per_mol"] == "6.60"
    assert analysis["blind_stability_excess_lower_envelope_kj_per_mol"] == "143.79"
    assert sum(analysis["blind_cccbdb_complete_row_counts"].values()) == 353
    assert sum(analysis["development_webbook_complete_row_counts"].values()) == 121


def test_prediction_program_is_value_free_and_complete():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True).casefold()
    assert len(AROMATIC_RECURRENCE_STABILITY_SPEC.target_rows) == 9
    for forbidden in ("hückel", "huckel", "4n+2", "82.93", "-4.32", "-123.14", "150.39", "target_payload_hash"):
        assert forbidden not in encoded
    assert sha256_identity(document).startswith("sha256:")
