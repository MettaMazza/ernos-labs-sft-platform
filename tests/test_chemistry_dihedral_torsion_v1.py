from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import unittest

from sft.chemistry.dihedral_torsion_batch_v1 import (
    DIHEDRAL_TORSION_SPEC, GeneratedFiniteDihedralTorsionChemistryProgram, IDENTITY_PATH, TARGET_PATH,
)
from sft.chemistry.dihedral_torsion_law_v1 import (
    DIMENSIONS, EXACT_RESULT, generated_dihedral_coordinate, ordered_positive_barrier_take,
)
from sft.chemistry.dihedral_torsion_validation_v1 import (
    _cycles, _prediction_map, _source_rows, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, PositiveRatio, fold_program_from_mapping
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine import ClosureScope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


class DihedralTorsionTests(unittest.TestCase):
    def test_complete_product_has_one_survivor_and_finite_boundary(self) -> None:
        generated = tuple(
            "__".join(choice.name for choice in row)
            for row in product(*(dimension.choices for dimension in DIMENSIONS))
        )
        self.assertEqual(len(generated), 256)
        self.assertEqual(len(set(generated)), 256)
        self.assertEqual(sum(candidate == EXACT_RESULT for candidate in generated), 1)
        program = GeneratedFiniteDihedralTorsionChemistryProgram(DIHEDRAL_TORSION_SPEC, "sha256:" + "d" * 64)
        decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
        self.assertEqual(program.closure_evidence(decisions).scope, ClosureScope.FINITE_COMPLETE)

    def test_generated_coordinate_uses_EmptyOne_positive_parts_and_recurrent_One(self) -> None:
        sectors = PositiveCount(24)
        self.assertIs(generated_dihedral_coordinate(PositiveCount(1), sectors), EMPTY_ONE)
        self.assertEqual(generated_dihedral_coordinate(PositiveCount(2), sectors).fraction, Fraction(1, 24))
        self.assertEqual(generated_dihedral_coordinate(PositiveCount(25), sectors).fraction, Fraction(1, 1))
        with self.assertRaises(InadmissibleExactValue):
            generated_dihedral_coordinate(PositiveCount(26), sectors)

    def test_prediction_is_value_free_and_complete(self) -> None:
        document = prediction_program_document()
        text = json.dumps(document, sort_keys=True)
        for forbidden in ("degree", "kJ", "cm_inverse", "5.41", "15.92", "0.52"):
            self.assertNotIn(forbidden, text)
        execution = CapabilityClosedFoldInterpreter().execute(
            fold_program_from_mapping(document),
            {"registered-premise": HeldLabel("sealed-derivation", "unit-test")},
        )
        prediction = _prediction_map(execution.output)
        self.assertEqual(len(prediction), 50)
        self.assertEqual(sum(row["coordinate"] is EMPTY_ONE for row in prediction.values()), 2)

    def test_postseal_complete_surface_matches_coordinates_and_forces_states(self) -> None:
        rows = _source_rows(ROOT)
        self.assertEqual(len(rows), 50)
        full_turn = Fraction(360, 1)
        for row in rows:
            coordinate = row["coordinate"]
            if coordinate is EMPTY_ONE:
                self.assertIs(row["angle"], EMPTY_ONE)
            else:
                self.assertEqual(coordinate.fraction * full_turn, row["angle"].fraction)
        cycles_kj = _cycles(rows, "energy_kj")
        cycles_cm = _cycles(rows, "energy_cm")
        self.assertEqual(sum(len(cycle.local_conformer_positions()) for cycle in cycles_kj.values()), 6)
        self.assertEqual(sum(len(cycle.local_barrier_positions()) for cycle in cycles_kj.values()), 6)
        self.assertEqual(sum(len(cycle.barrier_transitions()) for cycle in cycles_kj.values()), 12)
        for index in (1, 2):
            self.assertEqual(cycles_kj[index].local_conformer_positions(), cycles_cm[index].local_conformer_positions())
            self.assertEqual(cycles_kj[index].local_barrier_positions(), cycles_cm[index].local_barrier_positions())

    def test_reversed_take_and_negative_coordinate_halt(self) -> None:
        with self.assertRaises(InadmissibleExactValue):
            ordered_positive_barrier_take(PositiveRatio.from_pair(2, 1), PositiveRatio.from_pair(5, 1))
        with self.assertRaises(InadmissibleExactValue):
            PositiveRatio.from_pair(-1, 24)

    def test_identity_registry_contains_no_angle_or_energy_values(self) -> None:
        identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
        targets = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
        self.assertTrue(identities["all_angle_and_energy_values_absent"])
        self.assertEqual(len(identities["rows"]), 50)
        self.assertEqual(len(targets["rows"]), 50)
        self.assertTrue(all(row["target_value_absent"] for row in identities["rows"]))
        self.assertTrue(all("angle_inscription_degrees" not in row and "energy_inscription_kj_mol" not in row for row in identities["rows"]))

    def test_executable_law_contains_no_measured_surface_or_target_path(self) -> None:
        source = (ROOT / "sft/chemistry/dihedral_torsion_law_v1.py").read_text(encoding="utf-8")
        for forbidden in ("5.41", "15.92", "452", "1331", "dihedral_torsion_withheld_targets"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
