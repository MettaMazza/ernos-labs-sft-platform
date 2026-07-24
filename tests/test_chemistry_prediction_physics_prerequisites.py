from __future__ import annotations

from pathlib import Path
import unittest

from sft.engine import EngineHalt, EngineRepository
from sft.engine.source import build_source_manifest
from sft.physics.chemistry_prediction_prerequisites import (
    ATOMIC_BOUNDARY,
    CELL_CAPACITY,
    NUCLEAR_CLOSURE,
    QUESTIONS,
    build_program,
    candidate_records,
    survives,
)


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "sft/physics/chemistry_prediction_prerequisites.py"


class UnreachableIndependentValidator:
    def validate(self, sealed):  # pragma: no cover - forcing must halt first
        raise AssertionError("an unclosed prerequisite reached independent validation")


class ChemistryPredictionPhysicsPrerequisiteTests(unittest.TestCase):
    def test_complete_registered_grammar_sizes(self) -> None:
        self.assertEqual(len(candidate_records(CELL_CAPACITY)), 384)
        self.assertEqual(len(candidate_records(NUCLEAR_CLOSURE)), 384)
        self.assertEqual(len(candidate_records(ATOMIC_BOUNDARY)), 192)

    def test_current_dependencies_retain_two_two_and_no_survivors(self) -> None:
        counts = tuple(
            sum(1 for record in candidate_records(question) if survives(question, record))
            for question in QUESTIONS
        )
        self.assertEqual(counts, (2, 2, 0))

    def test_single_engine_halts_every_prerequisite_at_forcing(self) -> None:
        repository = EngineRepository(ROOT)
        source_hash = build_source_manifest(ROOT, (SOURCE,)).manifest_hash
        for question in QUESTIONS:
            with self.subTest(question=question.claim_id):
                program = build_program(question, source_hash)
                with self.assertRaises(EngineHalt) as caught:
                    repository.engine.run(
                        program,
                        UnreachableIndependentValidator(),
                        executed_source_hash=source_hash,
                    )
                receipt = caught.exception.receipt
                self.assertEqual(receipt.halted_stage, "forcing")
                self.assertFalse(receipt.accepted_evidence)
                self.assertFalse(receipt.model_admitted)
                self.assertTrue(any("survivor" in violation for violation in receipt.violations))


if __name__ == "__main__":
    unittest.main()
