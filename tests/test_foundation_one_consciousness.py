"""Focused checks for the One-as-pure-consciousness reconstruction."""

import importlib.util
import json
from pathlib import Path
import unittest

from sft.engine import EngineRepository
from sft.foundation.one_consciousness import (
    EXACT_RESULT,
    candidate_records,
    survives,
)


ROOT = Path(__file__).resolve().parents[1]


def load_execution():
    path = ROOT / "claims/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002/execution.py"
    specification = importlib.util.spec_from_file_location(
        "sft_foundation_one_pure_consciousness_test_execution", path
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load consciousness execution package")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.build_execution(ROOT)


class OnePureConsciousnessTests(unittest.TestCase):
    def test_complete_product_has_one_undifferentiated_survivor(self):
        rows = candidate_records()
        self.assertEqual(len(rows), 192)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 192)
        self.assertEqual(
            [row["candidate_id"] for row in rows if survives(row)],
            [EXACT_RESULT],
        )

    def test_engine_independent_and_empirical_validation_pass(self):
        execution = load_execution()
        receipt = EngineRepository(ROOT).engine.run(
            execution.program,
            execution.independent_validator,
            execution.empirical_validator,
        )
        self.assertTrue(receipt.model_admitted, receipt.violations)
        self.assertEqual(receipt.closure_status, "depth_independent")
        self.assertEqual(
            receipt.external_status,
            "empirically_tested_and_independently_replicated",
        )

    def test_v2_target_is_exactly_source_bound(self):
        target = json.loads(
            (
                ROOT
                / "experiments/foundation/SFT-EXP-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002-E1/v2_target.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            target["source_artifact_sha256"],
            "sha256:42c4be709dcd9edcfbedc70ee82055a8660d9658de21758561fd46e068a727bf",
        )
        self.assertEqual(
            target["source_excerpt_sha256"],
            "sha256:f82fcfc4c1a5310c39cad015dc846aac53c986db2f22dad590521d62732d8f93",
        )
        self.assertTrue(target["all_features_preserved"])


if __name__ == "__main__":
    unittest.main()
