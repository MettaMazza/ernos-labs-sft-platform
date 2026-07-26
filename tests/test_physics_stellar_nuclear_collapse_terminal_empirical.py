import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.stellar_nuclear_collapse_terminal_empirical_v1 import SPEC
from sft.physics.stellar_nuclear_collapse_terminal_validation_v1 import authoritative_record, exact_analysis


ROOT = Path(__file__).resolve().parents[1]


class StellarNuclearCollapseTerminalEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_external_vector(self):
        analysis = exact_analysis(authoritative_record(ROOT))
        self.assertEqual(analysis["stage_row_count"], 6)
        self.assertTrue(analysis["stage_temperatures_strict"])
        self.assertFalse(analysis["durations_strictly_decreasing"])
        self.assertTrue(analysis["oxygen_neon_duration_irregularity_retained"])
        self.assertEqual(analysis["cno_rate"], Fraction(36, 5))
        self.assertEqual(analysis["collapse_detector_count"], 3)
        self.assertTrue(analysis["collapse_model_assisted_retained"])
        self.assertEqual(analysis["gamma_line_energies_kev"], (847, 1238))
        self.assertTrue(analysis["gamma_interval_contains_branch_ratio"])
        self.assertEqual(analysis["capture_identified_element"], "strontium")
        self.assertTrue(analysis["capture_model_assisted_retained"])

    def test_hostile_rows_reject(self):
        record = authoritative_record(ROOT)
        erased = json.loads(json.dumps(record)); erased["sources"][0]["rows"]["massive_star_burning_stages"]["complete_rows"].pop()
        self.assertNotEqual(exact_analysis(erased)["stage_row_count"], 6)
        hidden = json.loads(json.dumps(record)); hidden["sources"][0]["rows"]["massive_star_burning_stages"]["complete_rows"][4]["duration_years"] = "1/1000"
        self.assertFalse(exact_analysis(hidden)["oxygen_neon_duration_irregularity_retained"])
        detector = json.loads(json.dumps(record)); detector["sources"][2]["rows"]["sn1987a_neutrino_reanalysis"]["detectors"].pop()
        self.assertNotEqual(exact_analysis(detector)["collapse_detector_count"], 3)
        ratio = json.loads(json.dumps(record)); ratio["sources"][3]["rows"]["sn2014j_nickel_cobalt_gamma_lines"]["measured_line_ratio_uncertainty"] = "1/100"
        self.assertFalse(exact_analysis(ratio)["gamma_interval_contains_branch_ratio"])


if __name__ == "__main__":
    unittest.main()
