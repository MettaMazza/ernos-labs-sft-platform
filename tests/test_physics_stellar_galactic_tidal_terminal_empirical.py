import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.stellar_galactic_tidal_terminal_empirical_v1 import SPEC
from sft.physics.stellar_galactic_tidal_terminal_validation_v1 import authoritative_record, exact_analysis


ROOT = Path(__file__).resolve().parents[1]


class StellarGalacticTidalTerminalEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_external_vector(self):
        analysis = exact_analysis(authoritative_record(ROOT))
        self.assertTrue(analysis["solar_reference_inside_observed_interval"])
        self.assertTrue(analysis["solar_reference_not_sft_prediction"])
        self.assertEqual(analysis["solar_sound_precision_order"], Fraction(1, 10000))
        self.assertEqual(analysis["stellar_row_count"], 6)
        self.assertTrue(analysis["only_high_mass_row_contains_four"])
        self.assertTrue(analysis["only_very_high_mass_row_contains_three"])
        self.assertEqual(analysis["sparc_galaxy_count"], 175)
        self.assertEqual(analysis["btfr_galaxy_count"], 153)
        self.assertFalse(analysis["btfr_central_contains_four"])
        self.assertTrue(analysis["btfr_systematic_contains_four"])
        self.assertEqual(analysis["bullet_separation_significance"], 8)
        self.assertTrue(analysis["moon_one_to_one"])
        self.assertTrue(analysis["mercury_is_three_to_two_boundary"])

    def test_unfavourable_controls_reject(self):
        record = authoritative_record(ROOT)
        erased = json.loads(json.dumps(record))
        erased["sources"][1]["rows"]["piecewise_main_sequence_mass_luminosity"]["complete_rows"] = erased["sources"][1]["rows"]["piecewise_main_sequence_mass_luminosity"]["complete_rows"][-2:]
        self.assertFalse(exact_analysis(erased)["all_six_stellar_rows_retained"])
        central_only = json.loads(json.dumps(record))
        central_only["sources"][3]["rows"]["baryonic_tully_fisher"]["reported_systematic_slope_interval"] = ["7/2", "399/100"]
        self.assertFalse(exact_analysis(central_only)["btfr_systematic_contains_four"])
        false_moon = json.loads(json.dumps(record))
        false_moon["sources"][5]["rows"]["lunar_synchronous_rotation"]["rotation_duration_hours"] = "654/1"
        self.assertFalse(exact_analysis(false_moon)["moon_one_to_one"])
        erased_mercury = json.loads(json.dumps(record))
        erased_mercury["sources"][6]["rows"]["mercury_spin_orbit_resonance"]["orbital_cycles"] = 3
        self.assertFalse(exact_analysis(erased_mercury)["mercury_is_three_to_two_boundary"])


if __name__ == "__main__":
    unittest.main()
