from __future__ import annotations

from fractions import Fraction
import unittest

from sft.physics.finite_quantum_gravity_terminal_law_v1 import (
    EMPTY_ONE,
    SPEC,
    finite_loop_sum,
    finite_quantum_gravity_model,
    successor_preserves_model,
)


class FiniteQuantumGravityTerminalTests(unittest.TestCase):
    def test_joint_model(self) -> None:
        model = finite_quantum_gravity_model(5)
        self.assertEqual(model["spatial_directions"], 3)
        self.assertEqual(model["symmetric_rank"], 2)
        self.assertEqual(model["symmetric_slots"], 10)
        self.assertEqual(model["physical_polarizations"], 2)
        self.assertEqual(model["mass_record"], EMPTY_ONE)
        self.assertEqual(model["causal_advance"], Fraction(1, 1))

    def test_finite_loop_and_floor(self) -> None:
        self.assertEqual(finite_loop_sum(6), Fraction(63, 64))
        self.assertEqual(finite_quantum_gravity_model(6)["distance_floor"], Fraction(1, 64))

    def test_horizon_and_successor(self) -> None:
        self.assertTrue(finite_quantum_gravity_model(5)["horizon_quarter_law"])
        self.assertTrue(all(successor_preserves_model(depth) for depth in range(1, 8)))

    def test_spec(self) -> None:
        SPEC.validate()
        self.assertEqual(len(SPEC.axes), 10)


if __name__ == "__main__":
    unittest.main()
