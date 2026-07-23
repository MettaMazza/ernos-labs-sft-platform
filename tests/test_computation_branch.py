"""Unit and integration checks for the complete classical-computation catalog."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import unittest

from sft.computation.catalog import SPECS, validate_catalog
from sft.computation.generated_law import GeneratedComputationProgram, candidate_records, survivor_id
from sft.computation.operations import (
    ExactTransitionSystem,
    causal_closure,
    complete_enumeration,
    consistent_hypotheses,
    evaluate_expression,
    exact_error_ledger,
    exact_search,
    generated_words,
    self_negating_boundary,
)
from sft.computation.spec_data import EXPECTED_GROUP_COUNTS


class ComputationCatalogTests(unittest.TestCase):
    def test_catalog_is_frozen_complete_unique_and_ordered(self) -> None:
        validate_catalog()
        self.assertEqual(len(SPECS), 113)
        self.assertEqual(Counter(spec.group for spec in SPECS), Counter(EXPECTED_GROUP_COUNTS))
        self.assertEqual(len({spec.claim_id for spec in SPECS}), 113)

    def test_every_claim_has_complete_product_and_one_survivor(self) -> None:
        for spec in SPECS:
            with self.subTest(claim_id=spec.claim_id):
                records = candidate_records(spec)
                self.assertEqual(len(records), 256)
                self.assertEqual(len({record["candidate_id"] for record in records}), 256)
                program = GeneratedComputationProgram(spec, "sha256:" + "a" * 64)
                census = program.generate_candidates()
                survivor = next(candidate for candidate in census.candidates if candidate.candidate_id == survivor_id(spec))
                self.assertTrue(program.decide_candidate(survivor).survives)
                self.assertFalse(program.decide_candidate(census.candidates[0]).survives)
                closure = program.closure_evidence((program.decide_candidate(survivor),))
                self.assertTrue(closure.minimality_passed)
                self.assertTrue(closure.named_shape_uniqueness_passed)
                self.assertTrue(all(control.passed for control in program.run_controls()))
                self.assertTrue(all(witness.passed for witness in spec.witnesses))


class ComputationOperationalBoundaryTests(unittest.TestCase):
    def test_transition_system_rejects_duplicate_source_action(self) -> None:
        with self.assertRaises(ValueError):
            ExactTransitionSystem(("a", "b"), ("go",), (("a", "go", "b"), ("a", "go", "a")))

    def test_word_generator_includes_empty_one_and_complete_depth_two_support(self) -> None:
        words = generated_words(("a", "b"), ("p1", "p2"))
        self.assertEqual(len(words), 7)
        self.assertEqual(words[0], ("empty-One",))

    def test_self_negation_has_no_fixed_verdict(self) -> None:
        self.assertNotEqual(self_negating_boundary("accept"), "accept")
        self.assertNotEqual(self_negating_boundary("reject"), "reject")

    def test_enumeration_rejects_duplicates(self) -> None:
        with self.assertRaises(ValueError):
            complete_enumeration(("same", "same"))

    def test_search_rejects_external_target(self) -> None:
        with self.assertRaises(ValueError):
            exact_search(("a", "b"), "outside")

    def test_semantics_rejects_unbound_name(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_expression(("name", "x"), ())

    def test_causal_closure_rejects_cycle(self) -> None:
        with self.assertRaises(ValueError):
            causal_closure(("a", "b"), (("a", "b"), ("b", "a")))

    def test_learning_retains_all_consistent_hypotheses(self) -> None:
        support = consistent_hypotheses(
            (("x", "a"),),
            (("h1", (("x", "a"),)), ("h2", (("x", "a"), ("y", "b")))),
        )
        self.assertEqual(support, ("h1", "h2"))

    def test_error_ledger_uses_orientation_not_negative_values(self) -> None:
        ledger = exact_error_ledger((Fraction(1, 2),), (Fraction(2, 3),))
        self.assertEqual(ledger, (("cell-1", Fraction(1, 6), "held-above"),))


if __name__ == "__main__":
    unittest.main()
