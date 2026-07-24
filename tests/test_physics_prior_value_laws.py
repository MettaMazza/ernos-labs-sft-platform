from fractions import Fraction
import unittest

from sft.physics.prior_value_laws import (
    CHARGED_LEPTON_CUBIC_SPEC,
    charged_lepton_invariants,
    lepton_sharpened_invariant,
)
from sft.physics.structural_constants import StructuralPhysicsProgram, generator_period_three


class PhysicsPriorValueLawTests(unittest.TestCase):
    def test_charged_lepton_invariants_are_exact(self) -> None:
        self.assertEqual(
            charged_lepton_invariants(),
            (Fraction(1, 1), Fraction(1, 6), Fraction(1, 485), Fraction(3, 1454)),
        )

    def test_complete_neighbouring_channel_census_is_distinct(self) -> None:
        self.assertEqual(
            tuple(lepton_sharpened_invariant(channel) for channel in (2, 3, 4)),
            (Fraction(2, 969), Fraction(3, 1454), Fraction(4, 1939)),
        )
        self.assertEqual(generator_period_three(), 3)

    def test_generated_claim_has_one_survivor(self) -> None:
        program = StructuralPhysicsProgram(CHARGED_LEPTON_CUBIC_SPEC, "sha256:test")
        census = program.generate_candidates()
        decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
        self.assertEqual(census.expected_cardinality, 2304)
        self.assertEqual(sum(decision.survives for decision in decisions), 1)
        self.assertTrue(all(control.passed for control in program.run_controls()))


if __name__ == "__main__":
    unittest.main()
