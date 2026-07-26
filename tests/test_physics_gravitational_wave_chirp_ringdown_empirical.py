import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.gravitational_wave_chirp_ringdown_empirical_v1 import SPEC
from sft.physics.gravitational_wave_chirp_ringdown_validation_v1 import authoritative_record, exact_analysis


ROOT = Path(__file__).resolve().parents[1]


class GravitationalWaveChirpRingdownEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_empirical_sequence(self):
        row = exact_analysis(authoritative_record(ROOT))
        self.assertTrue(row["development_source_not_blind"])
        self.assertEqual(row["chirp_frequency_interval_hz"], (Fraction(35), Fraction(450)))
        self.assertTrue(row["chirp_frequency_rises"])
        self.assertTrue(row["chirp_amplitude_rises"])
        self.assertEqual(row["chirp_cycle_count"], 55)
        self.assertTrue(row["positive_radiated_energy"])
        self.assertTrue(row["chirp_two_to_one"])
        self.assertTrue(row["ring_two_to_one"])
        self.assertTrue(row["ringdown_quadrupolar"])
        self.assertTrue(row["ringdown_decays"])
        self.assertTrue(row["half_One_not_directly_measured"])
        self.assertTrue(row["conditional_role_retained"])
        self.assertTrue(row["alternative_interpretations_retained"])

    def test_hostile_controls_reject(self):
        record = authoritative_record(ROOT)
        reversed_frequency = json.loads(json.dumps(record))
        reversed_frequency["withheld_postseal_sources"][0]["rows"]["signal"]["frequency_end_hz"] = "30/1"
        self.assertFalse(exact_analysis(reversed_frequency)["chirp_frequency_rises"])
        relabelled = json.loads(json.dumps(record))
        relabelled["development_context"][0]["blind_validation_role"] = "blind"
        self.assertFalse(exact_analysis(relabelled)["development_source_not_blind"])
        erased_scope = json.loads(json.dumps(record))
        erased_scope["withheld_postseal_sources"][1]["rows"]["scope"]["interpretation_role"] = "unconditional"
        self.assertFalse(exact_analysis(erased_scope)["conditional_role_retained"])


if __name__ == "__main__":
    unittest.main()
