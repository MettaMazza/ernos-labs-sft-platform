from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import unittest

from sft.chemistry.bond_angle_batch_v1 import (
    BOND_ANGLE_SPEC, GeneratedFiniteBondAngleChemistryProgram, IDENTITY_PATH, TARGET_PATH,
)
from sft.chemistry.bond_angle_law_v1 import (
    DIMENSIONS, EXACT_RESULT, equal_sector_turn_fraction, molecular_angle_vector,
)
from sft.chemistry.bond_angle_validation_v1 import (
    _load_targets, _prediction_map, prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, fold_program_from_mapping
from sft.engine import ClosureScope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount


ROOT = Path(__file__).resolve().parents[1]


class BondAngleTests(unittest.TestCase):
    def test_complete_product_has_one_survivor_and_finite_boundary(self) -> None:
        generated = tuple(
            "__".join(choice.name for choice in row)
            for row in product(*(dimension.choices for dimension in DIMENSIONS))
        )
        self.assertEqual(len(generated), 256)
        self.assertEqual(len(set(generated)), 256)
        self.assertEqual(sum(candidate == EXACT_RESULT for candidate in generated), 1)
        program = GeneratedFiniteBondAngleChemistryProgram(BOND_ANGLE_SPEC, "sha256:" + "c" * 64)
        decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
        self.assertEqual(program.closure_evidence(decisions).scope, ClosureScope.FINITE_COMPLETE)

    def test_equal_sector_law_is_exact_and_rejects_ungenerated_geometry(self) -> None:
        vector = molecular_angle_vector()
        self.assertEqual(
            tuple(row.turn_fraction for row in vector),
            (Fraction(1, 3), Fraction(1, 2), Fraction(1, 4), Fraction(1, 2)),
        )
        with self.assertRaises(InadmissibleExactValue):
            equal_sector_turn_fraction(
                HeldLabel("molecular-geometry", "tetrahedral-continuum-angle"),
                PositiveCount(4), PositiveCount(1),
            )
        with self.assertRaises(InadmissibleExactValue):
            equal_sector_turn_fraction(
                HeldLabel("molecular-geometry", "square-planar-equal-four-sector"),
                PositiveCount(3), PositiveCount(1),
            )

    def test_prediction_is_degree_free_and_structurally_complete(self) -> None:
        document = prediction_program_document()
        target_document = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
        text = json.dumps(document, sort_keys=True)
        for row in target_document["rows"]:
            self.assertNotIn(f'"{row["inscription"]}"', text)
        execution = CapabilityClosedFoldInterpreter().execute(
            fold_program_from_mapping(document),
            {"registered-premise": HeldLabel("sealed-derivation", "unit-test")},
        )
        prediction = _prediction_map(execution.output)
        self.assertEqual(len(prediction), 4)
        self.assertEqual(
            {target_id: row["turn_fraction"] for target_id, row in prediction.items()},
            {carrier.target_id: carrier.turn_fraction for carrier in molecular_angle_vector()},
        )

    def test_complete_postseal_source_vector_matches_exact_degree_translation(self) -> None:
        targets = _load_targets(ROOT)
        self.assertEqual(len(targets), 4)
        structural = {row.target_id: row.turn_fraction for row in molecular_angle_vector()}
        for row in targets:
            self.assertEqual(structural[row["target_id"]] * Fraction(360, 1), row["source_degrees"])

    def test_identity_registry_has_no_angle_values_and_retains_conditions(self) -> None:
        identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
        self.assertTrue(identities["all_measurement_values_absent"])
        self.assertEqual(len(identities["rows"]), 4)
        self.assertTrue(all(row["target_value_absent"] for row in identities["rows"]))
        self.assertTrue(all("inscription" not in row and "central" not in row for row in identities["rows"]))
        required = ("species", "molecular_state", "geometry", "point_group", "angle_definition", "method_and_condition")
        self.assertTrue(all(all(str(row[field]).strip() for field in required) for row in identities["rows"]))

    def test_executable_law_contains_no_external_degree_value_or_target_path(self) -> None:
        source = (ROOT / "sft/chemistry/bond_angle_law_v1.py").read_text(encoding="utf-8")
        for forbidden in ("120", "180", "90", "360", "bond_angle_withheld_targets"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
