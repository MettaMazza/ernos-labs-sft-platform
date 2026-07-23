"""Publication-readiness checks for the two local computation manuscripts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent.parent


class ComputationPublicationTests(unittest.TestCase):
    def test_local_publication_gate_passes_without_authorization(self) -> None:
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools/verify_computation_publications.py")),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("SFT COMPUTATION LOCAL PUBLICATION GATE: PASS", completed.stdout)
        self.assertIn("SFT QUANTUM_COMPUTATION LOCAL PUBLICATION GATE: PASS", completed.stdout)

    def test_evidence_maps_cover_frozen_inventories_exactly(self) -> None:
        for branch, expected in (("computation", 113), ("quantum_computation", 21)):
            with self.subTest(branch=branch):
                inventory = json.loads((ROOT / f"publications/inventories/{branch}.json").read_text(encoding="utf-8"))
                evidence = json.loads((ROOT / f"publications/current/{branch}/evidence_map.json").read_text(encoding="utf-8"))
                self.assertEqual(tuple(row["claim_id"] for row in evidence["claims"]), tuple(inventory["required_claim_ids"]))
                self.assertEqual(len(evidence["claims"]), expected)
                self.assertTrue(evidence["complete_claim_coverage"])

    def test_manifests_are_ready_but_not_authorized(self) -> None:
        for branch in ("computation", "quantum_computation"):
            with self.subTest(branch=branch):
                manifest = json.loads((ROOT / f"publications/current/{branch}/manifest.json").read_text(encoding="utf-8"))
                self.assertTrue(manifest["ready_to_publish"])
                self.assertFalse(manifest["publication_authorized"])

    def test_rendered_papers_are_real_nontrivial_pdfs(self) -> None:
        paths = (
            ROOT / "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001.pdf",
            ROOT / "output/pdf/the-quantum-fold-machine-branch-paper-001.pdf",
        )
        for path in paths:
            with self.subTest(path=path.name):
                self.assertGreater(path.stat().st_size, 100_000)
                self.assertEqual(path.read_bytes()[:5], b"%PDF-")


if __name__ == "__main__":
    unittest.main()
