from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from sft import publication_compliance
from sft.publication_compliance import (
    audit_branch,
    require_current_publication_ready,
)


ROOT = Path(__file__).resolve().parents[1]


class PublicationComplianceTests(unittest.TestCase):
    def test_all_currently_closed_branches_are_ready(self) -> None:
        foundation = require_current_publication_ready(ROOT, "foundation")
        self.assertTrue(foundation.current_publication_ready)
        self.assertEqual(foundation.live_claim_count, 16)
        self.assertEqual(foundation.blockers, ())

        for branch in ("mathematics", "information_science", "computation", "quantum_computation"):
            with self.subTest(branch=branch):
                result = require_current_publication_ready(ROOT, branch)
                self.assertTrue(result.current_publication_ready)
                self.assertEqual(result.blockers, ())

        physics = require_current_publication_ready(ROOT, "physics")
        self.assertTrue(physics.current_publication_ready)
        self.assertEqual(physics.live_claim_count, 349)
        self.assertEqual(physics.blockers, ())

        for branch in (
            "chemistry",
            "materials",
        ):
            with self.subTest(branch=branch):
                result = require_current_publication_ready(ROOT, branch)
                self.assertTrue(result.current_publication_ready)
                self.assertTrue(result.archive_integrity_boundary_preserved)
                self.assertEqual(result.blockers, ())

    def test_physics_categorical_inventory_equals_live_claims_and_closes_prior_ownership(self) -> None:
        result = audit_branch(ROOT, "physics")
        self.assertEqual(result.live_claim_count, 349)
        self.assertEqual(result.frozen_inventory_claim_count, 349)
        self.assertEqual(result.archival_paper_claim_count, 349)
        self.assertTrue(result.current_publication_ready)
        self.assertEqual(result.blockers, ())

    def test_incomplete_branch_specific_review_halts_successor(self) -> None:
        real_read = publication_compliance._read

        def read_with_incomplete_foundation_ledger(path: Path):
            if path.name == "foundation_prior_obligations.json":
                return {
                    "reviewed_source_surface": {
                        "review_complete_for_branch_ownership": False,
                        "reviewed_entry_count": 763,
                    },
                    "foundation_summary": {"open_count": 1},
                    "status": "open",
                }
            return real_read(path)

        with patch(
            "sft.publication_compliance._read",
            side_effect=read_with_incomplete_foundation_ledger,
        ):
            result = audit_branch(ROOT, "foundation")
        self.assertFalse(result.current_publication_ready)
        self.assertIn(
            "branch-specific full-source ownership review or same-strength closure is incomplete",
            result.blockers,
        )

    def test_incomplete_physics_atomic_ownership_halts_successor(self) -> None:
        real_read = publication_compliance._read

        def read_with_incomplete_physics_audit(path: Path):
            if path.name == "physics_v1_v2_atomic_ownership.json":
                return {
                    "source_surface": {"total_source_rows_reviewed": 763},
                    "summary": {
                        "physics_owned_atom_count": 488,
                        "same_strength_closed_atom_count": 487,
                        "same_strength_open_atom_count": 1,
                        "unique_atom_ids": True,
                        "all_declared_composite_rows_decomposed": True,
                        "publication_blocked": True,
                    },
                    "audit_status": "open_blocking",
                }
            return real_read(path)

        with patch(
            "sft.publication_compliance._read",
            side_effect=read_with_incomplete_physics_audit,
        ):
            result = audit_branch(ROOT, "physics")
        self.assertFalse(result.current_publication_ready)
        self.assertIn(
            "Physics atomic ownership review or same-strength closure is incomplete",
            result.blockers,
        )

    def test_cli_reports_completed_physics_ownership(self) -> None:
        completed = subprocess.run(
            (
                sys.executable,
                str(ROOT / "tools/verify_publication_compliance.py"),
                "--branch",
                "physics",
                "--require-ready",
            ),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("physics: READY; live=349; frozen=349; paper=349", completed.stdout)

    def test_zenodo_publish_compliance_precondition_accepts_completed_physics(self) -> None:
        result = require_current_publication_ready(ROOT, "physics")
        self.assertTrue(result.current_publication_ready)
        self.assertEqual(result.blockers, ())

    def test_invalid_branch_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            audit_branch(ROOT, "not_a_branch")

    def test_closed_complete_branch_can_pass(self) -> None:
        def read_fixture(path: Path):
            name = path.name
            if name == "physics.json":
                return {"required_claim_ids": ["SFT-PHYS-X"]}
            if name == "manifest.json":
                return {"ready_to_publish": True}
            if name == "evidence_map.json":
                return {"claims": [{"claim_id": "SFT-PHYS-X"}]}
            if name == "v1_theorem_manifest_observation_census.json":
                return {"source_row_count": 356}
            if name == "v2_407_step_observation_census.json":
                return {"source_step_count": 407}
            if name == "lineage_reconciliation.json":
                return {"status": "closed"}
            if name == "prior_obligation_ownership.json":
                return {
                    "assignment_complete": True,
                    "branch_summary": {"physics": {"status": "closed_same_strength"}},
                }
            if name == "physics_v1_v2_atomic_ownership.json":
                return {
                    "source_surface": {"total_source_rows_reviewed": 763},
                    "summary": {
                        "physics_owned_atom_count": 1,
                        "same_strength_closed_atom_count": 1,
                        "same_strength_open_atom_count": 0,
                        "unique_atom_ids": True,
                        "all_declared_composite_rows_decomposed": True,
                        "publication_blocked": False,
                    },
                    "audit_status": "current_evidence_closed_extension_open",
                }
            raise AssertionError(path)

        with patch("sft.publication_compliance._read", side_effect=read_fixture):
            with patch(
                "sft.publication_compliance._live_claim_ids",
                return_value=("SFT-PHYS-X",),
            ):
                result = require_current_publication_ready(ROOT, "physics")
        self.assertTrue(result.current_publication_ready)
        self.assertEqual(result.blockers, ())

    def test_invalid_lineage_stale_paper_and_unready_manifest_are_blockers(self) -> None:
        def read_fixture(path: Path):
            name = path.name
            if name == "physics.json":
                return {"required_claim_ids": ["SFT-PHYS-X"]}
            if name == "manifest.json":
                return {"ready_to_publish": False}
            if name == "evidence_map.json":
                return {
                    "claims": [
                        {"claim_id": "SFT-PHYS-X"},
                        {"claim_id": "SFT-PHYS-STALE"},
                    ]
                }
            if name == "v1_theorem_manifest_observation_census.json":
                return {"source_row_count": 356}
            if name == "v2_407_step_observation_census.json":
                return {"source_step_count": 407}
            if name == "lineage_reconciliation.json":
                return {"status": "invalid"}
            if name == "prior_obligation_ownership.json":
                return {
                    "assignment_complete": True,
                    "branch_summary": {"physics": {"status": "closed_same_strength"}},
                }
            if name == "physics_v1_v2_atomic_ownership.json":
                return {
                    "source_surface": {"total_source_rows_reviewed": 763},
                    "summary": {
                        "physics_owned_atom_count": 1,
                        "same_strength_closed_atom_count": 1,
                        "same_strength_open_atom_count": 0,
                        "unique_atom_ids": True,
                        "all_declared_composite_rows_decomposed": True,
                        "publication_blocked": False,
                    },
                    "audit_status": "current_evidence_closed_extension_open",
                }
            raise AssertionError(path)

        with patch("sft.publication_compliance._read", side_effect=read_fixture):
            with patch(
                "sft.publication_compliance._live_claim_ids",
                return_value=("SFT-PHYS-X",),
            ):
                result = audit_branch(ROOT, "physics")
        self.assertFalse(result.current_publication_ready)
        self.assertTrue(any("invalid status" in row for row in result.blockers))
        self.assertTrue(any("non-live" in row for row in result.blockers))
        self.assertTrue(any("not internally ready" in row for row in result.blockers))


if __name__ == "__main__":
    unittest.main()
