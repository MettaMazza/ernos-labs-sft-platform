from fractions import Fraction

import pytest

from sft.engine.exact import InadmissibleExactValue, PositiveCount
from sft.materials.successor_derivation import MATERIALS_SUCCESSOR_BLUEPRINTS, successor_candidate_ids
from sft.materials.successor_structural_counts import (
    displacement_mode_certificate,
    ferrimagnetic_gap,
    primary_fractional_hall_classes,
    rational_inflation_fixed_point_certificate,
    rectification_certificate,
    substitution_populations,
    topological_edge_count,
    water_bulk_ledger_certificate,
)


def test_complete_successor_surface_has_eight_unique_256_form_claims():
    assert len(MATERIALS_SUCCESSOR_BLUEPRINTS) == 8
    assert len({row.claim_id for row in MATERIALS_SUCCESSOR_BLUEPRINTS}) == 8
    for row in MATERIALS_SUCCESSOR_BLUEPRINTS:
        candidates = successor_candidate_ids(row)
        assert len(candidates) == 256
        assert len(set(candidates)) == 256
        assert candidates.count(row.exact_result) == 1


def test_substitution_recurrence_and_depth_independent_rational_exclusion():
    assert [(x.first.value, x.second.value) for x in substitution_populations(PositiveCount(7))] == [
        (1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (13, 8), (21, 13)
    ]
    certificate = rational_inflation_fixed_point_certificate()
    assert certificate["least_candidate_rejected"] is True
    assert certificate["positive_rational_fixed_scale"].label == "structural-absence"


def test_phonon_mode_classes_and_rank_three_counts():
    certificate = displacement_mode_certificate()
    assert certificate["acoustic_class"].label == "shared"
    assert certificate["optical_class"].label == "opposed"
    assert certificate["directions_per_site"].value == 3
    assert certificate["sample_cube_counts"] == (1, 8, 27, 64)


def test_rectification_uses_orientations_without_signed_values():
    closed = rectification_certificate(PositiveCount(5), PositiveCount(2))
    opened = rectification_certificate(PositiveCount(2), PositiveCount(5))
    assert closed["forward_orientation"].value == 3
    assert closed["reverse_orientation"].value == 7
    assert opened["forward_orientation"].label == "open"
    assert opened["reverse_orientation"].value == 7


def test_ferrimagnetic_gap_and_equal_opposition():
    unequal = ferrimagnetic_gap(PositiveCount(7), PositiveCount(4))
    equal = ferrimagnetic_gap(PositiveCount(4), PositiveCount(4))
    assert unequal["net_support"].value == 3
    assert unequal["orientation"].label == "first-sublattice"
    assert equal["net_support"].label == "structural-absence"


def test_primary_hall_hierarchy_is_reduced_positive_and_odd_denominator():
    rows = primary_fractional_hall_classes(PositiveCount(9))
    assert Fraction(1, 3) in rows and Fraction(2, 5) in rows and Fraction(4, 9) in rows
    assert all(row > 0 and row <= 1 and row.denominator % 2 == 1 for row in rows)
    assert len(rows) == len(set(rows))


def test_topological_edge_gap_and_equal_boundary_halt():
    assert topological_edge_count(PositiveCount(8), PositiveCount(3))["count"].value == 5
    with pytest.raises(InadmissibleExactValue):
        topological_edge_count(PositiveCount(3), PositiveCount(3))


def test_water_bulk_ledger_is_complete():
    certificate = water_bulk_ledger_certificate()
    assert certificate["complete"] is True
    assert certificate["field_count"].value == len(certificate["required_fields"]) == 9
