import unittest
from pathlib import Path

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.particle_mode_generation_empirical_v1 import SOURCE_IDS, SPEC
from sft.physics.particle_mode_generation_validation_v1 import authoritative_record, exact_particle_mode_analysis


class ParticleModeGenerationEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_external_vector(self):
        root = Path(__file__).resolve().parents[1]
        record = authoritative_record(root)
        self.assertEqual(tuple(row["source_id"] for row in record["sources"]), SOURCE_IDS)
        result = exact_particle_mode_analysis(record["registered_target"])
        self.assertEqual(result["fit_interval"], (2989, 3003))
        self.assertEqual(result["direct_interval"], (287, 297))
        self.assertEqual(result["direct_standard_uncertainty_displacement"], (8, 5))
        self.assertTrue(all(value for key, value in result.items() if key not in {"fit_interval", "direct_interval", "direct_standard_uncertainty_displacement"}))

    def test_shifted_fit_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["neutrino_type_fit_center"] = 2800
        self.assertFalse(exact_particle_mode_analysis(target)["fit_contains_three"])

    def test_altered_direct_record_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["neutrino_direct_row_retained_without_adjustment"] = False
        self.assertFalse(exact_particle_mode_analysis(target)["measurement_boundaries_retained"])

    def test_reversed_lifetime_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["tau_mean_life_seconds"] = "3"
        self.assertFalse(exact_particle_mode_analysis(target)["charged_lepton_lifetimes_reverse_order"])


if __name__ == "__main__":
    unittest.main()
