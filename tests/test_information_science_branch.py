"""Unit and integration checks for the complete information-science catalog."""

from __future__ import annotations

import unittest

from sft.information_science.catalog import SPECS, validate_catalog
from sft.information_science.channels_capacity.law import FiniteChannel
from sft.information_science.classical_probabilistic_information.law import classical_state
from sft.information_science.coding_theory.law import complete_support
from sft.information_science.compression_redundancy.law import reconstruct
from sft.information_science.conservation_loss_transformation.law import validate_transformation
from sft.information_science.encoding_decoding.law import validate_encoding
from sft.information_science.entropy_uncertainty.law import exact_partition
from sft.information_science.generated_law import (
    GeneratedInformationProgram,
    candidate_records,
    survivor_id,
)
from sft.information_science.information_quantity.law import complete_word_support
from sft.information_science.mutual_conditional_information.law import validate_observation
from sft.information_science.noise_error.law import ErrorRelation, error_trace
from sft.information_science.quantum_information_correspondence.law import reconstruct_support
from sft.information_science.symbols_distinguishability.law import canonical_alphabet


class InformationScienceCatalogTests(unittest.TestCase):
    def test_catalog_is_complete_unique_and_dependency_ordered(self) -> None:
        validate_catalog()
        self.assertEqual(len(SPECS), 12)
        self.assertEqual(len({spec.claim_id for spec in SPECS}), 12)

    def test_every_product_is_complete_and_has_one_survivor(self) -> None:
        for spec in SPECS:
            with self.subTest(claim_id=spec.claim_id):
                records = candidate_records(spec)
                expected = 2 ** len(spec.dimensions)
                self.assertEqual(len(records), expected)
                self.assertEqual(len({record["candidate_id"] for record in records}), expected)
                program = GeneratedInformationProgram(spec, "sha256:" + "a" * 64)
                census = program.generate_candidates()
                expected_survivor = survivor_id(spec)
                survivor_candidate = next(
                    candidate for candidate in census.candidates
                    if candidate.candidate_id == expected_survivor
                )
                sampled = (census.candidates[0], survivor_candidate, census.candidates[-1])
                decisions = tuple(program.decide_candidate(candidate) for candidate in sampled)
                self.assertTrue(program.decide_candidate(survivor_candidate).survives)
                self.assertTrue(any(not decision.survives for decision in decisions))
                closure = program.closure_evidence(decisions)
                self.assertTrue(closure.minimality_passed)
                self.assertTrue(closure.named_shape_uniqueness_passed)
                self.assertTrue(all(control.passed for control in program.run_controls()))

    def test_operational_witnesses_are_live(self) -> None:
        for spec in SPECS:
            with self.subTest(claim_id=spec.claim_id):
                self.assertTrue(all(witness.passed for witness in spec.witnesses))


class InformationScienceBoundaryTests(unittest.TestCase):
    def test_symbol_alphabet_rejects_duplicate_labels(self) -> None:
        with self.assertRaises(ValueError):
            canonical_alphabet(("form-a", "held-a"), ("form-a", "held-a"))

    def test_encoding_rejects_partial_source_relation(self) -> None:
        self.assertFalse(
            validate_encoding(("a", "b"), (("x",), ("y",)), (("a", ("x",)),))
        )

    def test_quantity_rejects_duplicate_positions(self) -> None:
        with self.assertRaises(ValueError):
            complete_word_support(("a", "b"), ("p", "p"))

    def test_entropy_rejects_partial_observation(self) -> None:
        with self.assertRaises(ValueError):
            exact_partition(("a", "b"), (("a", "seen"),))

    def test_compression_rejects_unknown_token(self) -> None:
        with self.assertRaises(ValueError):
            reconstruct(("outside",), (("token", ("a",)),))

    def test_channel_rejects_unrepresented_input(self) -> None:
        with self.assertRaises(ValueError):
            FiniteChannel(("a", "b"), ("x",), (("a", "x", "path"),))

    def test_noise_rejects_external_received_form(self) -> None:
        with self.assertRaises(ValueError):
            ErrorRelation((("a",),), (("b",),), ((("a",), ("outside",), "change"),))

    def test_coding_rejects_missing_positions(self) -> None:
        with self.assertRaises(ValueError):
            complete_support(("a", "b"), ())

    def test_mutual_information_rejects_partial_view(self) -> None:
        with self.assertRaises(ValueError):
            validate_observation(("a", "b"), (("a", "seen"),))

    def test_transformation_rejects_multivalued_source(self) -> None:
        with self.assertRaises(ValueError):
            validate_transformation(("a",), (("a", "x"), ("a", "y")))

    def test_classical_state_requires_supported_form(self) -> None:
        with self.assertRaises(ValueError):
            classical_state(("a", "b"), "outside")

    def test_quantum_record_rejects_duplicate_branch(self) -> None:
        with self.assertRaises(ValueError):
            reconstruct_support(((('a',), "x"), (('a',), "y")))

    def test_error_comparison_requires_common_positions(self) -> None:
        with self.assertRaises(ValueError):
            error_trace(("a",), ("a", "b"))


if __name__ == "__main__":
    unittest.main()
