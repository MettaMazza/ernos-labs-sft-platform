import unittest
from pathlib import Path

from sft.physics.criticality_universality_turbulence_empirical_v1 import SOURCE_IDS, SPEC
from sft.physics.criticality_universality_turbulence_validation_v1 import authoritative_record, exact_criticality_turbulence_analysis
from sft.physics.generated_empirical_law import candidate_rows


class CriticalityUniversalityTurbulenceEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_external_vector(self):
        root = Path(__file__).resolve().parents[1]
        record = authoritative_record(root)
        self.assertEqual(tuple(row["source_id"] for row in record["sources"]), SOURCE_IDS)
        result = exact_criticality_turbulence_analysis(record["registered_target"])
        self.assertEqual(result["structure_interval"], (666, 692))
        self.assertEqual(tuple(sample for sample, matches in result["manganite_matches"].items() if matches), ("La00", "La04", "La06", "La08"))
        self.assertTrue(result["erbium_complete_vector_matches"])
        self.assertTrue(all(value for key, value in result.items() if key not in {"manganite_components", "manganite_matches", "structure_interval", "manganite_nonmatch_retained", "manganite_nonmatch_gamma_rejects", "manganite_nonmatch_delta_rejects"}))
        self.assertTrue(result["manganite_nonmatch_retained"])
        self.assertTrue(result["manganite_nonmatch_gamma_rejects"])
        self.assertTrue(result["manganite_nonmatch_delta_rejects"])

    def test_shifted_structure_interval_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["turbulence_measured_structure_center"] = 620
        self.assertFalse(exact_criticality_turbulence_analysis(target)["structure_interval_contains_two_thirds"])

    def test_relabelled_nonmatch_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["manganite_expected_complete_vector_matches"] = ["La00", "La02", "La04", "La06", "La08"]
        self.assertFalse(exact_criticality_turbulence_analysis(target)["manganite_expected_matches_exact"])

    def test_removed_measurement_row_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["manganite_rows"] = list(target["manganite_rows"][:-1])
        self.assertFalse(exact_criticality_turbulence_analysis(target)["manganite_complete_five_rows"])

    def test_reversed_spectrum_rejects(self):
        root = Path(__file__).resolve().parents[1]
        target = dict(authoritative_record(root)["registered_target"])
        target["turbulence_spectrum_orientation"] = "rising"
        self.assertFalse(exact_criticality_turbulence_analysis(target)["spectrum_falling_orientation"])


if __name__ == "__main__":
    unittest.main()
