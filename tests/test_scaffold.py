import json
import unittest
from pathlib import Path

from sft.cli import ROOT, engine_status, repository_status


class ScaffoldTests(unittest.TestCase):
    def test_census_starts_without_imported_claims(self) -> None:
        census = json.loads((ROOT / "census" / "claims.json").read_text(encoding="utf-8"))
        self.assertEqual(census["claims"], [])
        self.assertEqual(census["unclassified_obligations"], [])

    def test_status_registers_accessible_v3_and_self_hosted_v4(self) -> None:
        status = repository_status()
        self.assertEqual(status["generation"], "v3-python-accessible")
        self.assertEqual(status["registered_claims"], 0)
        self.assertEqual(status["admitted_claims"], 0)
        self.assertEqual(status["future_generation"], "v4-sft-derived-self-hosted")

    def test_single_engine_policy_is_fail_closed(self) -> None:
        status = engine_status()
        self.assertFalse(status["axioms_permitted"])
        self.assertFalse(status["free_parameters_permitted"])
        self.assertTrue(status["halt_on_any_violation"])
        self.assertTrue(status["census_admission_requires_accepted_receipt"])

    def test_every_json_artifact_parses(self) -> None:
        for path in ROOT.rglob("*.json"):
            with self.subTest(path=path.relative_to(ROOT)):
                json.loads(path.read_text(encoding="utf-8"))

    def test_core_guidance_exists(self) -> None:
        for relative in (
            "CONSTITUTION.md",
            "docs/CLEAN_ROOM_PROTOCOL.md",
            "docs/EMPIRICAL_METHOD.md",
            "docs/V4_SELF_HOSTED_REBUILD.md",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((Path(ROOT) / relative).is_file())


if __name__ == "__main__":
    unittest.main()
