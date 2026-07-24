"""Exact tests for the non-label Materials count laws."""

from __future__ import annotations

import unittest

from sft.engine.exact import PositiveCount
from sft.materials.obligations import MATERIALS_OBLIGATIONS, SUBBRANCH_ORDER, validate_inventory
from sft.materials.structural_counts import (
    acoustic_branch_census,
    allowed_crystallographic_orders,
    bravais_census,
    crystal_system_census,
    crystallographic_rotation_admitted,
    rotation_factor_certificate,
    simple_cubic_coordination,
    simple_cubic_neighbours,
)


class MaterialsInventoryTests(unittest.TestCase):
    def test_inventory_is_complete_unique_and_ordered(self) -> None:
        validate_inventory()
        self.assertEqual(len(MATERIALS_OBLIGATIONS), 84)
        self.assertEqual(len({row.claim_id for row in MATERIALS_OBLIGATIONS}), 84)
        self.assertEqual(tuple(dict.fromkeys(row.subbranch for row in MATERIALS_OBLIGATIONS)), SUBBRANCH_ORDER)


class MaterialsStructuralCountTests(unittest.TestCase):
    def test_rank_three_two_orientation_neighbours_force_six(self) -> None:
        rows = simple_cubic_neighbours(("axis-one", "axis-two", "axis-three"))
        self.assertEqual(len(rows), 6)
        self.assertEqual(len(set(rows)), 6)
        self.assertEqual(simple_cubic_coordination(), PositiveCount(6))

    def test_crystallographic_orders_are_exact_and_five_is_least_excluded(self) -> None:
        admitted = tuple(row.value for row in allowed_crystallographic_orders())
        self.assertEqual(admitted, (1, 2, 3, 4, 6))
        self.assertFalse(crystallographic_rotation_admitted(PositiveCount(5)))
        self.assertEqual(rotation_factor_certificate()["least_excluded"], PositiveCount(5))

    def test_rank_three_metric_grammar_has_seven_systems(self) -> None:
        rows = crystal_system_census()
        self.assertEqual(len(rows), 7)
        self.assertEqual(
            {row.name for row in rows},
            {"triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"},
        )

    def test_system_centering_grammar_has_fourteen_bravais_classes(self) -> None:
        rows = bravais_census()
        self.assertEqual(len(rows), 14)
        self.assertEqual(len(set(rows)), 14)

    def test_rank_three_displacements_force_three_acoustic_branches(self) -> None:
        rows = acoustic_branch_census()
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row.orientation == "longitudinal" for row in rows), 1)
        self.assertEqual(sum(row.orientation == "transverse" for row in rows), 2)


if __name__ == "__main__":
    unittest.main()
