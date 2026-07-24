from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import unittest

from sft.verification import CoverageReport, VerificationReport, verify_all


class VerificationProgressTests(unittest.TestCase):
    def test_progress_callback_does_not_change_report(self) -> None:
        coverage = CoverageReport(304, 18, 1746, 1746)
        events: list[str] = []
        with patch("sft.verification.run_repository_validation") as repository:
            with patch("sft.verification.run_core_coverage", return_value=coverage) as core:
                with patch("sft.verification.rerun_registered_claims", return_value=407) as replay:
                    report = verify_all(Path("."), progress=events.append)
        self.assertEqual(report, VerificationReport(coverage, 407))
        repository.assert_called_once_with(Path("."))
        core.assert_called_once_with(Path("."), progress=events.append)
        replay.assert_called_once_with(Path("."), progress=events.append)
        self.assertEqual(
            events,
            [
                "repository integrity: start",
                "repository integrity: pass",
                "unit/E2E tests and core coverage: start",
                "unit/E2E tests and core coverage: pass (304 tests; 1746/1746 lines)",
                "complete verification: pass",
            ],
        )

    def test_cli_progress_writer_flushes_each_line(self) -> None:
        report = VerificationReport(CoverageReport(304, 18, 1746, 1746), 407)

        def fake_verify(root: Path, progress) -> VerificationReport:
            progress("repository integrity: start")
            progress("complete verification: pass")
            return report

        from sft import cli

        output = StringIO()
        with patch("sys.argv", ["sft", "verify-all"]):
            with patch("sft.verification.verify_all", side_effect=fake_verify):
                with redirect_stdout(output):
                    cli.main()
        lines = output.getvalue().splitlines()
        self.assertEqual(lines[0], "[SFT verify-all] repository integrity: start")
        self.assertEqual(lines[1], "[SFT verify-all] complete verification: pass")
        self.assertIn("SFT COMPLETE VERIFICATION: PASS", lines)


if __name__ == "__main__":
    unittest.main()
