"""Regression checks for immutable empirical replay context."""

import json
import platform
from pathlib import Path
import tempfile
import unittest

from sft.verification import VerificationError, _sealed_replay_environment


class SealedReplayEnvironmentTests(unittest.TestCase):
    def _root(self, claim_id: str, payload: object) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        package = root / "claims" / claim_id
        package.mkdir(parents=True)
        (package / "empirical_validation.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )
        return temporary, root

    def test_formal_replay_does_not_replace_host_metadata(self):
        original = (platform.system(), platform.python_implementation())
        with _sealed_replay_environment(Path("."), "formal-claim", None):
            self.assertEqual((platform.system(), platform.python_implementation()), original)

    def test_empirical_replay_restores_sealed_metadata_then_releases_it(self):
        claim_id = "empirical-claim"
        temporary, root = self._root(
            claim_id,
            {
                "claim_id": claim_id,
                "isolation_certificate": {
                    "host_platform": "sealed-host",
                    "python_implementation": "sealed-python",
                },
            },
        )
        original = (platform.system(), platform.python_implementation())
        try:
            with _sealed_replay_environment(root, claim_id, object()):
                self.assertEqual(platform.system(), "sealed-host")
                self.assertEqual(platform.python_implementation(), "sealed-python")
            self.assertEqual((platform.system(), platform.python_implementation()), original)
        finally:
            temporary.cleanup()

    def test_malformed_empirical_context_halts(self):
        claim_id = "empirical-claim"
        temporary, root = self._root(claim_id, {"claim_id": claim_id})
        try:
            with self.assertRaises(VerificationError):
                with _sealed_replay_environment(root, claim_id, object()):
                    pass
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
