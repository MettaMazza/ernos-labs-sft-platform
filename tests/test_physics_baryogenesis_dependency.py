from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.baryogenesis_dependency_terminal_law_v1 import (
    EMPTY_ONE,
    ResidueRecord,
    SPEC,
    complete_condition_census,
    retained_baryon_residue,
    unique_positive_process,
)


class BaryogenesisDependencyTests(unittest.TestCase):
    def test_complete_condition_census(self) -> None:
        rows = complete_condition_census()
        self.assertEqual(len(rows), 8)
        self.assertEqual(sum(bool(row["positive_residue"]) for row in rows), 1)

    def test_all_conditions_retain_one_residue(self) -> None:
        self.assertEqual(
            retained_baryon_residue(
                baryon_tally_changes=True,
                conjugate_paths_distinguished=True,
                reverse_completion_held=True,
            ),
            ResidueRecord("matter", Fraction(1, 1)),
        )

    def test_each_omission_closes_residue(self) -> None:
        self.assertEqual(retained_baryon_residue(baryon_tally_changes=False, conjugate_paths_distinguished=True, reverse_completion_held=True), EMPTY_ONE)
        self.assertEqual(retained_baryon_residue(baryon_tally_changes=True, conjugate_paths_distinguished=False, reverse_completion_held=True), EMPTY_ONE)
        self.assertEqual(retained_baryon_residue(baryon_tally_changes=True, conjugate_paths_distinguished=True, reverse_completion_held=False), EMPTY_ONE)

    def test_spec(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 10)
        self.assertTrue(unique_positive_process())


if __name__ == "__main__":
    unittest.main()
