import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.strong_cp_baryon_stability_empirical_v1 import SPEC
from sft.physics.strong_cp_baryon_stability_validation_v1 import authoritative_record, exact_analysis


ROOT = Path(__file__).resolve().parents[1]


class StrongCpBaryonStabilityEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_measured_vector(self):
        analysis = exact_analysis(authoritative_record(ROOT))
        self.assertTrue(analysis["nedm_direct_record_consistent"])
        self.assertEqual(analysis["nedm_upper_limit"], Fraction(9, 500000000000000000000000000))
        self.assertEqual(analysis["proton_mode_count"], 6)
        self.assertEqual(analysis["proton_lifetime_lower_limits_years"], (
            24 * 10 ** 33,
            16 * 10 ** 33,
            14 * 10 ** 33,
            73 * 10 ** 32,
            72 * 10 ** 32,
            45 * 10 ** 32,
        ))
        self.assertTrue(analysis["no_significant_decay_signal"])
        self.assertTrue(analysis["background_candidates_retained"])

    def test_confirmed_signal_controls_reject(self):
        record = authoritative_record(ROOT)
        tampered_edm = json.loads(json.dumps(record))
        tampered_edm["sources"][0]["rows"]["neutron_electric_dipole_moment"]["reported_central_status"] = "confirmed-nonempty-displacement"
        self.assertFalse(exact_analysis(tampered_edm)["nedm_direct_record_consistent"])
        tampered_decay = json.loads(json.dumps(record))
        tampered_decay["sources"][1]["rows"]["p_to_e_plus_pi0"]["interpretation"] = "confirmed-proton-decay"
        self.assertFalse(exact_analysis(tampered_decay)["no_significant_decay_signal"])


if __name__ == "__main__":
    unittest.main()
