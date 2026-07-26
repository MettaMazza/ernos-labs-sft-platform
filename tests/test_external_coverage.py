from pathlib import Path
import unittest

from sft.external_coverage import audit_external_measurement_coverage


class ExternalCoverageTests(unittest.TestCase):
    def test_live_corpus_exposes_every_current_gap(self) -> None:
        root = Path(__file__).resolve().parents[1]
        report = audit_external_measurement_coverage(root)
        self.assertEqual(report.registered_claims, 686)
        self.assertEqual(report.empirical_claims, 390)
        self.assertEqual(len(report.missing_empirical_contexts), 0)
        self.assertEqual(
            len(report.physics_results_without_empirical_descendant),
            14,
        )
        self.assertFalse(report.complete)


if __name__ == "__main__":
    unittest.main()
