from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from sft.physics.generated_empirical_law import candidate_rows
from sft.physics.vacuum_density_planck_empirical_v1 import SPEC
from sft.physics.vacuum_density_planck_validation_v1 import authoritative_record, exact_vacuum_analysis


ROOT = Path(__file__).resolve().parents[1]


class VacuumDensityPlanckTests(unittest.TestCase):
    def test_primary_source_record_is_complete(self) -> None:
        record = authoritative_record(ROOT)
        self.assertEqual(record["sources"][0]["source_page"], 225)
        self.assertEqual(record["registered_target"]["planck_hubble_central_km_s_mpc"], "67.68")
        self.assertTrue(record["historical_knowledge_boundary"]["historical_blindness_claimed"] is False)

    def test_exact_share_and_normalized_magnitude_pass(self) -> None:
        analysis = exact_vacuum_analysis(authoritative_record(ROOT)["registered_target"])
        self.assertEqual(analysis["vacuum_interval"], (Fraction(6833, 10000), Fraction(1389, 2000)))
        self.assertEqual(analysis["predicted_share"], Fraction(11, 16))
        self.assertTrue(analysis["share_inside_interval"])
        self.assertEqual(analysis["normalized_interval"], (Fraction(20499, 10000), Fraction(4167, 2000)))
        self.assertEqual(analysis["predicted_normalized"], Fraction(33, 16))
        self.assertTrue(analysis["normalized_inside_interval"])

    def test_budget_scale_and_type_controls(self) -> None:
        analysis = exact_vacuum_analysis(authoritative_record(ROOT)["registered_target"])
        self.assertTrue(analysis["central_budget_closes"])
        self.assertTrue(analysis["dimensional_transport_positive"])
        self.assertTrue(analysis["local_floor_outside_global_interval"])
        self.assertTrue(analysis["half_one_mode_mean_outside_global_interval"])
        self.assertTrue(analysis["primary_hubble_correction_retained"])

    def test_tampered_measurement_fails(self) -> None:
        target = dict(authoritative_record(ROOT)["registered_target"])
        target["planck_vacuum_fraction_central"] = "0.6000"
        self.assertFalse(exact_vacuum_analysis(target)["share_inside_interval"])

    def test_complete_empirical_candidate_product(self) -> None:
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)
        SPEC.validate()


if __name__ == "__main__":
    unittest.main()
