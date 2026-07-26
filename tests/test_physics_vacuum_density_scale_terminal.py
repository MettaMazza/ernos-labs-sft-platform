from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.structural_constants import candidate_rows
from sft.physics.vacuum_density_scale_terminal_law_v1 import (
    SPEC,
    boundary_record_depth,
    cosmological_constant_scale_transport,
    finite_zero_point_ledger,
    generation_volume,
    least_binary_cover_depth,
    local_floor_candidates,
    local_vacuum_amplitude_floor,
    local_vacuum_energy_floor,
    normalized_cosmological_constant,
    theorem_certificate,
)


class VacuumDensityScaleTerminalTests(unittest.TestCase):
    def test_generator_volume_forces_cover_and_floor(self) -> None:
        self.assertEqual(generation_volume(), 27)
        self.assertEqual(least_binary_cover_depth(27), 5)
        self.assertEqual(boundary_record_depth(), 10)
        self.assertEqual(local_vacuum_amplitude_floor(), Fraction(1, 1024))
        self.assertEqual(local_vacuum_energy_floor(), Fraction(1, 1048576))

    def test_complete_local_floor_subgrammar(self) -> None:
        rows = local_floor_candidates()
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(bool(row["survives"]) for row in rows), 1)
        survivor = next(row for row in rows if row["survives"])
        self.assertEqual(survivor["observable_depth"], 20)

    def test_finite_radiative_ledger_closes_at_every_depth(self) -> None:
        for depth in range(1, 10):
            row = finite_zero_point_ledger(depth)
            self.assertEqual(row["total"], Fraction(row["support"], 2))
            self.assertEqual(row["mean"], Fraction(1, 2))
            self.assertTrue(row["closed"])

    def test_cosmic_quantities_remain_typed_and_scale_covariant(self) -> None:
        self.assertEqual(normalized_cosmological_constant(), Fraction(33, 16))
        self.assertNotEqual(local_vacuum_energy_floor(), Fraction(11, 16))
        reference = cosmological_constant_scale_transport(Fraction(2, 3), Fraction(3, 4))
        self.assertEqual(reference, cosmological_constant_scale_transport(Fraction(4, 3), Fraction(3, 2)))
        self.assertTrue(theorem_certificate()["scale_covariance"])

    def test_invalid_inputs_halt(self) -> None:
        for value in (0, -1):
            with self.assertRaises(ValueError):
                least_binary_cover_depth(value)
            with self.assertRaises(ValueError):
                finite_zero_point_ledger(value)
        with self.assertRaises(ValueError):
            cosmological_constant_scale_transport(Fraction(0), Fraction(1))
        with self.assertRaises(ValueError):
            cosmological_constant_scale_transport(Fraction(1), Fraction(-1))

    def test_complete_engine_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 4096)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 4096)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
