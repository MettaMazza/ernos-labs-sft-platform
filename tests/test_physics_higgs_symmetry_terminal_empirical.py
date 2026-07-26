import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.higgs_symmetry_terminal_empirical_v1 import SPEC
from sft.physics.higgs_symmetry_terminal_validation_v1 import authoritative_record, exact_analysis


ROOT = Path(__file__).resolve().parents[1]


class HiggsSymmetryTerminalEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_measured_vector(self):
        analysis = exact_analysis(authoritative_record(ROOT))
        self.assertEqual(analysis["predicted_mass_gev"], Fraction(31557437733819647, 251923197734500))
        self.assertEqual(analysis["pdg_interval_gev"], (Fraction(12509, 100), Fraction(12531, 100)))
        self.assertTrue(analysis["pdg_aggregate_contains_prediction"])
        self.assertFalse(analysis["atlas_one_reported_uncertainty_contains_prediction"])
        self.assertFalse(analysis["cms_one_reported_uncertainty_contains_prediction"])
        self.assertTrue(analysis["individual_offsets_retained"])
        self.assertTrue(analysis["kappa_interval_contains_prediction"])
        self.assertFalse(analysis["direct_coupling_is_precision_measurement"])

    def test_unfavourable_controls_reject(self):
        record = authoritative_record(ROOT)
        outside_mass = json.loads(json.dumps(record))
        outside_mass["sources"][1]["rows"]["higgs_mass_world_average"]["reported_interval_from_listed_uncertainty_gev"] = ["124/1", "125/1"]
        self.assertFalse(exact_analysis(outside_mass)["pdg_aggregate_contains_prediction"])
        outside_coupling = json.loads(json.dumps(record))
        outside_coupling["sources"][4]["rows"]["trilinear_self_coupling_constraint"]["upper_coordinate"] = "9/10"
        self.assertFalse(exact_analysis(outside_coupling)["kappa_interval_contains_prediction"])


if __name__ == "__main__":
    unittest.main()
