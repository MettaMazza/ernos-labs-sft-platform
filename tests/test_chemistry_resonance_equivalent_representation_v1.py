import json
from pathlib import Path

import pytest

from sft.chemistry.resonance_equivalent_representation_batch_v1 import (
    PRIMARY_PATH,
    RESONANCE_EQUIVALENT_REPRESENTATION_SPEC,
)
from sft.chemistry.resonance_equivalent_representation_law_v1 import (
    append_shared_successor,
    encoding,
    equivalent_pair,
)
from sft.chemistry.resonance_equivalent_representation_validation_v1 import (
    _source_rows,
    exact_analysis,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


def base_encodings():
    first = encoding(
        "first", "carrier", ("a", "b", "c"), ((1, 2), (2, 3)),
        ("fold-fibre-one", "fold-fibre-two"),
    )
    second = encoding(
        "second", "carrier", ("a", "b", "c"), ((1, 2), (2, 3)),
        ("fold-fibre-two", "fold-fibre-one"),
    )
    return first, second


def test_base_pair_and_depth_independent_successor():
    first, second = base_encodings()
    pair = equivalent_pair("carrier", first, second)
    successor = append_shared_successor(pair, "d")
    assert pair.representation_count == PositiveCount(2)
    assert len(pair.first.atoms) == 3
    assert len(pair.first.adjacency) == 2
    assert len(successor.first.atoms) == 4
    assert len(successor.first.adjacency) == 3
    assert successor.first.atoms[:-1] == pair.first.atoms
    assert successor.first.adjacency[:-1] == pair.first.adjacency


def test_carrier_adjacency_partial_and_identical_forms_halt():
    first, second = base_encodings()
    with pytest.raises(InadmissibleExactValue):
        other = encoding(
            "other", "other-carrier", ("a", "b", "c"), ((1, 2), (2, 3)),
            ("fold-fibre-two", "fold-fibre-one"),
        )
        equivalent_pair("carrier", first, other)
    with pytest.raises(InadmissibleExactValue):
        changed = encoding(
            "changed", "carrier", ("a", "b", "c"), ((1, 3), (2, 3)),
            ("fold-fibre-two", "fold-fibre-one"),
        )
        equivalent_pair("carrier", first, changed)
    with pytest.raises(InadmissibleExactValue):
        partial = encoding(
            "partial", "carrier", ("a", "b", "c"), ((1, 2), (2, 3)),
            ("fold-fibre-one", "fold-fibre-one"),
        )
        equivalent_pair("carrier", first, partial)
    with pytest.raises(InadmissibleExactValue):
        equivalent_pair("carrier", first, first)
    assert second != first


def test_complete_corrected_external_surface():
    rows = _source_rows(ROOT)
    analysis = exact_analysis(rows, json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8")))
    assert analysis["complete_target_count"] == 4
    assert analysis["complete_source_count"] == 4
    assert analysis["one_molecular_entity_representation_surface_present"]
    assert analysis["at_least_two_formal_structures_surface_present"]
    assert analysis["single_structure_insufficient_surface_present"]
    assert analysis["formal_not_species_surface_present"]
    assert analysis["not_equilibrium_surface_present"]
    assert analysis["nonlocal_support_surface_present"]
    assert analysis["external_wavefunction_and_coefficient_language_preserved"]
    assert analysis["external_signed_charge_inscription_preserved"]
    assert analysis["preserved_v1_charge_search_scope_false_result_count"] == 1
    assert analysis["v2_corrected_complete_record_search_count"] == 4


def test_prediction_program_is_value_free_and_complete():
    document = prediction_program_document(ROOT)
    encoded = json.dumps(document, sort_keys=True).casefold()
    assert len(RESONANCE_EQUIVALENT_REPRESENTATION_SPEC.target_rows) == 4
    assert "target_payload_hash" not in encoded
    assert "wavefunction" not in encoded
    assert "coefficient" not in encoded
    assert "o^{-}" not in encoded
    assert sha256_identity(document).startswith("sha256:")
