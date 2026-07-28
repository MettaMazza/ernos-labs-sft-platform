from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from sft.chemistry.composition_stoichiometry_batch_1 import (
    COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS,
    CompositionComponent,
    ReactionSpecies,
    exact_composition,
    exact_yield,
    limiting_component_positions,
    primitive_coefficients,
    reaction_is_balanced,
)
from sft.chemistry.generated_law import BlindExternalChemistryValidator
from sft.engine.canonical import sha256_identity
from sft.engine.exact import ExactPart, HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import candidate_rows, survivor_id


ROOT = Path(__file__).resolve().parent.parent


def abstract_reaction(scale: int = 1) -> tuple[ReactionSpecies, ...]:
    return (
        ReactionSpecies(HeldLabel("reaction-side", "reactant"), "AB", PositiveCount(scale), (("A", PositiveCount(1)), ("B", PositiveCount(1)))),
        ReactionSpecies(HeldLabel("reaction-side", "reactant"), "A", PositiveCount(scale), (("A", PositiveCount(1)),)),
        ReactionSpecies(HeldLabel("reaction-side", "product"), "A2B", PositiveCount(scale), (("A", PositiveCount(2)), ("B", PositiveCount(1)))),
    )


class ChemistryCompositionStoichiometryBatchTests(unittest.TestCase):
    def test_batch_closes_all_seven_registered_obligations(self) -> None:
        self.assertEqual(
            tuple(spec.claim_id for spec in COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS),
            (
                "SFT-CHEM-STOICH-COMPOSITION-001",
                "SFT-CHEM-STOICH-CONSERVATION-001",
                "SFT-CHEM-STOICH-COEFFICIENT-001",
                "SFT-CHEM-STOICH-LIMITING-001",
                "SFT-CHEM-STOICH-YIELD-001",
                "SFT-CHEM-STOICH-MIXTURE-001",
                "SFT-CHEM-STOICH-SOLUTION-001",
            ),
        )

    def test_each_content_grammar_is_complete_and_unique(self) -> None:
        for spec in COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS:
            rows = candidate_rows(spec)
            identities = tuple(str(row["candidate_id"]) for row in rows)
            self.assertEqual(len(rows), 256)
            self.assertEqual(len(set(identities)), 256)
            self.assertEqual(sum(item == survivor_id(spec) for item in identities), 1)

    def test_exact_composition_closes_to_one_and_rejects_incomplete_parts(self) -> None:
        complete = exact_composition(
            (
                CompositionComponent("A", ExactPart.from_pair(1, 3)),
                CompositionComponent("B", ExactPart.from_pair(2, 3)),
            )
        )
        self.assertEqual(tuple(row.part.value for row in complete), (Fraction(1, 3), Fraction(2, 3)))
        with self.assertRaises(InadmissibleExactValue):
            exact_composition(
                (
                    CompositionComponent("A", ExactPart.from_pair(1, 3)),
                    CompositionComponent("B", ExactPart.from_pair(1, 3)),
                )
            )

    def test_balance_uses_held_sides_and_primitive_positive_counts(self) -> None:
        primitive = abstract_reaction()
        rescaled = abstract_reaction(2)
        self.assertTrue(reaction_is_balanced(primitive))
        self.assertTrue(primitive_coefficients(primitive))
        self.assertTrue(reaction_is_balanced(rescaled))
        self.assertFalse(primitive_coefficients(rescaled))
        self.assertTrue(all(row.coefficient.value > 0 for row in primitive))
        self.assertEqual({row.side.label for row in primitive}, {"reactant", "product"})

    def test_limiting_support_retains_ties_with_positive_positions(self) -> None:
        self.assertEqual(
            limiting_component_positions(
                (ExactPart.from_pair(1, 2), ExactPart.from_pair(3, 4)),
                (PositiveCount(1), PositiveCount(1)),
            ),
            (PositiveCount(1),),
        )
        self.assertEqual(
            limiting_component_positions(
                (ExactPart.from_pair(1, 2), ExactPart.from_pair(1, 2)),
                (PositiveCount(1), PositiveCount(1)),
            ),
            (PositiveCount(1), PositiveCount(2)),
        )

    def test_yield_remains_an_exact_positive_part(self) -> None:
        value = exact_yield(ExactPart.from_pair(7, 8))
        self.assertEqual(value.value, Fraction(7, 8))
        self.assertNotIsInstance(value.value, float)

    def test_post_seal_iupac_rows_and_tampered_controls_pass(self) -> None:
        for spec in COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS:
            result = BlindExternalChemistryValidator(ROOT, spec).validate(
                SimpleNamespace(seal_hash=sha256_identity((spec.claim_id, "stoichiometry-test")))
            )
            self.assertTrue(result.passed)
            self.assertTrue(result.target_opened_after_seal)
            self.assertTrue(result.all_rows_preserved)
            self.assertIn("tampered unfavorable control rejected", result.measurements[-1])

    def test_observation_registry_contains_extractions_not_observed_labels(self) -> None:
        registry = json.loads(
            (
                ROOT
                / "experiments/external_sources/chemistry/observations_composition_stoichiometry_batch_1.json"
            ).read_text(encoding="utf-8")
        )
        for row in registry["observations"]:
            self.assertNotIn("observed_label", row)
            self.assertNotIn("expected_observation_label", row)

    def test_all_preceding_chemistry_authorities_remain_byte_frozen(self) -> None:
        expected = {
            "sft/chemistry/generated_law.py": "sha256:678de1061dcd4b4a24deefd7757045729d89677d6170bd907cde70bc9ca2e15a",
            "sft/chemistry/catalog.py": "sha256:90750420738638bdadd783f0fb83bc667ee414cc48036e5cdc2f9a2a61089fd6",
            "sft/chemistry/obligations.py": "sha256:b502afe57640149166b4ca69b433d02b3361155eb624f9af8cb8918f77ac0ad7",
            "sft/chemistry/measurement_identity_batch_2.py": "sha256:39560a34d9ffa3e6504fad03ccbd5e5d9d0cf59f16b4da050d3fe4e2ef2a52a1",
            "sft/chemistry/elements_periodicity_batch_1.py": "sha256:a311a161899600a5b2a6bc7eaf48db552ca7cd29452578fe888ba13a69c420d1",
            "sft/chemistry/elements_periodicity_batch_2.py": "sha256:0db053985b28ab518b6b7cae11e03904b9409c29aee9e4a179e547a2669c3b4f",
        "sft/chemistry/generated_periodic_law.py": "sha256:3681af2f6f16947a6f0a58bdebcc161a7c11b2f096269d550a9e97e9a3b69926",
            "experiments/external_sources/chemistry/observations_elements_periodicity_batch_2.json": "sha256:f67e0026a0320f47e52855f8dced9038a1148cfa5cd91763d7aa276b16313be5",
        }
        self.assertEqual({path: hash_file(ROOT / path) for path in expected}, expected)


if __name__ == "__main__":
    unittest.main()
