from fractions import Fraction
from pathlib import Path
import unittest

from sft.engine.source import build_source_manifest
from sft.physics.atomic_constants import (
    ATOMIC_CONSTANT_SPECS,
    atomic_endpoint,
    colour_coupling,
    fine_structure_blocks,
    inverse_fine_structure,
    nuclear_closure,
    nuclear_closure_prefix,
    orbit_capacity,
    promotion_rungs,
    spin_orbit_threshold,
)
from sft.physics.atomic_constants_validation import (
    ALPHA_SPEC,
    NUCLEAR_SPEC,
    codata_inverse_alpha_interval,
    iaea_magic_sequence,
)
from sft.physics.structural_constants import StructuralPhysicsProgram, candidate_rows


ROOT = Path(__file__).resolve().parent.parent


class PhysicsAtomicConstantsTests(unittest.TestCase):
    def test_fine_structure_is_exact_and_terminal(self):
        self.assertEqual(
            fine_structure_blocks(),
            {"binary": 2, "generator": 3, "down": 5, "up": 7, "tower": 128, "boundary": 9, "cover": 250},
        )
        self.assertEqual(promotion_rungs(), (125, 175, 245, 343))
        self.assertEqual(inverse_fine_structure(1), Fraction(34259, 250))
        self.assertEqual(inverse_fine_structure(), Fraction(503846395469, 3676744786))

    def test_orbit_capacity_is_successor_general(self):
        self.assertEqual(tuple(orbit_capacity(rank) for rank in range(1, 6)), (2, 6, 10, 14, 18))
        for rank in range(1, 50):
            self.assertEqual(orbit_capacity(rank + 1), orbit_capacity(rank) + 4)

    def test_colour_coupling_and_nuclear_closure(self):
        self.assertEqual(colour_coupling(), Fraction(2, 3))
        self.assertEqual(spin_orbit_threshold(), 3)
        self.assertEqual(nuclear_closure_prefix(8), (2, 8, 20, 28, 50, 82, 126, 184))
        for rank in range(4, 50):
            self.assertEqual(nuclear_closure(rank), (rank - 1) * rank * (rank + 1) // 3 + 2 * rank)

    def test_endpoint_uses_exact_order_not_a_bounded_scan(self):
        value = inverse_fine_structure()
        self.assertEqual(atomic_endpoint(), 137)
        self.assertLessEqual(Fraction(atomic_endpoint(), 1), value)
        self.assertLess(value, Fraction(atomic_endpoint() + 1, 1))

    def test_every_spec_has_one_survivor_and_controls(self):
        source_files = (ROOT / "sft/physics/structural_constants.py", ROOT / "sft/physics/atomic_constants.py")
        source_hash = build_source_manifest(ROOT, source_files).manifest_hash
        for spec in ATOMIC_CONSTANT_SPECS:
            with self.subTest(spec.claim_id):
                program = StructuralPhysicsProgram(spec, source_hash)
                census = program.generate_candidates()
                decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
                self.assertEqual(len(census.candidates), len(candidate_rows(spec)))
                self.assertEqual(sum(row.survives for row in decisions), 1)
                self.assertTrue(all(control.passed for control in program.run_controls()))
                self.assertEqual(program.closure_evidence(decisions).scope.value, "depth_independent")

    def test_postseal_external_records_reconstruct_exactly(self):
        lower, central, upper = codata_inverse_alpha_interval(
            ROOT / ALPHA_SPEC.source_snapshot_path
        )
        self.assertLess(lower, central)
        self.assertLess(central, upper)
        self.assertLessEqual(lower, inverse_fine_structure())
        self.assertLessEqual(inverse_fine_structure(), upper)
        self.assertEqual(
            iaea_magic_sequence(ROOT / NUCLEAR_SPEC.source_snapshot_path),
            nuclear_closure_prefix(8),
        )


if __name__ == "__main__":
    unittest.main()
