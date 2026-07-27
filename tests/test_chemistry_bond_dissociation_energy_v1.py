from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import unittest

from sft.chemistry.bond_dissociation_energy_batch_v1 import (
    BOND_DISSOCIATION_ENERGY_SPEC,
    GeneratedFiniteDissociationChemistryProgram,
    IDENTITY_PATH,
    TARGET_PATH,
)
from sft.chemistry.bond_dissociation_energy_law_v1 import DIMENSIONS, EXACT_RESULT, ground_dissociation_from_transition
from sft.chemistry.bond_dissociation_energy_validation_v1 import _load_targets, _validate_structural_prediction, prediction_program_document
from sft.claim_evidence import CapabilityClosedFoldInterpreter, fold_program_from_mapping
from sft.engine import ClosureScope
from sft.engine.exact import HeldLabel, InadmissibleExactValue


ROOT = Path(__file__).resolve().parents[1]


class BondDissociationEnergyTests(unittest.TestCase):
    def test_complete_product_has_one_survivor_and_finite_boundary(self) -> None:
        generated = tuple("__".join(choice.name for choice in row) for row in product(*(item.choices for item in DIMENSIONS)))
        self.assertEqual(len(generated), 256)
        self.assertEqual(len(set(generated)), 256)
        self.assertEqual(sum(candidate == EXACT_RESULT for candidate in generated), 1)
        program = GeneratedFiniteDissociationChemistryProgram(BOND_DISSOCIATION_ENERGY_SPEC, "sha256:" + "b" * 64)
        decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
        self.assertEqual(program.closure_evidence(decisions).scope, ClosureScope.FINITE_COMPLETE)

    def test_ordered_positive_take_is_exact_and_reversal_halts(self) -> None:
        self.assertEqual(ground_dissociation_from_transition(Fraction(9, 8), Fraction(3, 4)), Fraction(3, 8))
        with self.assertRaises(InadmissibleExactValue):
            ground_dissociation_from_transition(Fraction(3, 4), Fraction(9, 8))

    def test_prediction_is_value_free_and_structurally_complete(self) -> None:
        document = prediction_program_document()
        text = json.dumps(document, sort_keys=True)
        targets = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
        for row in targets["rows"]:
            self.assertNotIn(str(row["inscription"]), text)
        execution = CapabilityClosedFoldInterpreter().execute(
            fold_program_from_mapping(document),
            {"registered-premise": HeldLabel("sealed-derivation", "unit-test")},
        )
        _validate_structural_prediction(execution.output)

    def test_complete_eight_row_postseal_vector_reconstructs_exact_relation(self) -> None:
        rows = _load_targets(ROOT)
        self.assertEqual(len(rows), 8)
        grouped = {(row["species"], row["measurement_role"]): row for row in rows}
        for species in ("H2", "D2"):
            threshold = grouped[(species, "path-threshold")]
            atomic = grouped[(species, "atomic-path-segment")]
            lower = ground_dissociation_from_transition(threshold["lower"], atomic["upper"])
            upper = ground_dissociation_from_transition(threshold["upper"], atomic["lower"])
            for role in ("historical-ground-dissociation", "later-ground-dissociation"):
                target = grouped[(species, role)]
                self.assertFalse(upper < target["lower"] or target["upper"] < lower)

    def test_identity_registry_contains_no_measurement_values(self) -> None:
        identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
        self.assertTrue(identities["all_measurement_values_absent"])
        self.assertEqual(len(identities["rows"]), 8)
        self.assertTrue(all(row["target_value_absent"] for row in identities["rows"]))
        self.assertTrue(all("central" not in row and "uncertainty" not in row and "inscription" not in row for row in identities["rows"]))

    def test_executable_law_contains_no_measured_value_or_target_path(self) -> None:
        source = (ROOT / "sft/chemistry/bond_dissociation_energy_law_v1.py").read_text(encoding="utf-8")
        for forbidden in ("118377.06", "119029.72", "36118.11", "36118.06962", "36748.38", "36748.362282", "bond_dissociation_energy_withheld_targets"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
