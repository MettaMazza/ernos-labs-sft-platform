from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import unittest

from sft.chemistry.equilibrium_bond_length_batch_v1 import (
    EQUILIBRIUM_BOND_LENGTH_SPEC,
    GeneratedFiniteQuantitativeChemistryProgram,
    IDENTITY_PATH,
    SCALE_PATH,
    TARGET_PATH,
)
from sft.chemistry.equilibrium_bond_length_law_v1 import (
    D2_MULTIPLIER,
    DIMENSIONS,
    EXACT_RESULT,
    H2_MULTIPLIER,
)
from sft.chemistry.equilibrium_bond_length_validation_v1 import (
    _load_scale,
    _load_targets,
    _ratio,
    prediction_program_document,
)
from sft.claim_evidence import CapabilityClosedFoldInterpreter, FoldPair, FoldTable
from sft.engine import ClosureScope


ROOT = Path(__file__).resolve().parents[1]


class EquilibriumBondLengthTests(unittest.TestCase):
    def test_complete_product_has_one_survivor_and_finite_boundary(self) -> None:
        generated = tuple(
            "__".join(choice.name for choice in row)
            for row in product(*(item.choices for item in DIMENSIONS))
        )
        self.assertEqual(len(generated), 256)
        self.assertEqual(len(set(generated)), 256)
        self.assertEqual(sum(candidate == EXACT_RESULT for candidate in generated), 1)
        program = GeneratedFiniteQuantitativeChemistryProgram(EQUILIBRIUM_BOND_LENGTH_SPEC, "sha256:" + "b" * 64)
        decisions = tuple(program.decide_candidate(candidate) for candidate in program.generate_candidates().candidates)
        self.assertEqual(program.closure_evidence(decisions).scope, ClosureScope.FINITE_COMPLETE)

    def test_exact_relations_use_forced_counts(self) -> None:
        from sft.physics.molecular_spectroscopy_successor_laws_v1 import exact_alpha

        alpha = exact_alpha()
        self.assertEqual(H2_MULTIPLIER, Fraction(7, 5) + 21 * alpha**2)
        self.assertEqual(D2_MULTIPLIER, Fraction(7, 5) + 24 * alpha**2)
        self.assertGreater(D2_MULTIPLIER, H2_MULTIPLIER)

    def test_public_scale_and_withheld_targets_are_separate(self) -> None:
        identity = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
        scale = json.loads((ROOT / SCALE_PATH).read_text(encoding="utf-8"))
        targets = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
        self.assertTrue(all(row["target_value_absent"] for row in identity["rows"]))
        self.assertTrue(scale["target_values_absent"])
        self.assertNotIn("rows", scale)
        self.assertTrue(targets["scale_input_values_absent"])
        self.assertNotIn("registered_scale_input", targets)

    def test_capability_closed_prediction_overlaps_both_targets(self) -> None:
        _central, lower, upper = _load_scale(ROOT)
        execution = CapabilityClosedFoldInterpreter().execute(
            __import__("sft.claim_evidence", fromlist=["fold_program_from_mapping"]).fold_program_from_mapping(prediction_program_document()),
            {"atomic-lower": _ratio(lower), "atomic-upper": _ratio(upper)},
        )
        self.assertIsInstance(execution.output, FoldTable)
        predicted = {entry.left.label: entry.right for entry in execution.output.entries}
        for row in _load_targets(ROOT):
            interval = predicted[row["species"]]
            self.assertIsInstance(interval, FoldPair)
            self.assertFalse(interval.right.fraction < row["lower"] or row["upper"] < interval.left.fraction)

    def test_executable_law_contains_no_target_distance(self) -> None:
        source = (ROOT / "sft/chemistry/equilibrium_bond_length_law_v1.py").read_text(encoding="utf-8")
        self.assertNotIn("0.74144", source)
        self.assertNotIn("0.74152", source)
        self.assertNotIn("equilibrium_bond_length_withheld_targets", source)
        self.assertNotIn("nist-webbook-h2", source.casefold())
        self.assertNotIn("nist-webbook-d2", source.casefold())


if __name__ == "__main__":
    unittest.main()
