import json
import unittest
from fractions import Fraction
from pathlib import Path

from sft.physics.compact_horizon_terminal_empirical_v1 import SPEC
from sft.physics.compact_horizon_terminal_validation_v1 import authoritative_record, exact_analysis
from sft.physics.generated_empirical_law import candidate_rows


ROOT = Path(__file__).resolve().parents[1]


class CompactHorizonTerminalEmpiricalTests(unittest.TestCase):
    def test_complete_candidate_product(self):
        rows = candidate_rows(SPEC)
        self.assertEqual(len(rows), 256)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 256)

    def test_complete_object_boundary(self):
        analysis = exact_analysis(authoritative_record(ROOT))
        self.assertEqual(analysis["white_dwarf_limit_solar"], Fraction(7, 5))
        self.assertEqual(analysis["neutron_star_interval_solar"], (Fraction(201, 100), Fraction(215, 100)))
        self.assertTrue(analysis["neutron_star_interval_wholly_above_white_dwarf_limit"])
        self.assertFalse(analysis["neutron_star_mass_is_direct_maximum_measurement"])
        self.assertTrue(analysis["both_conditional_uppers_above_neutron_interval"])
        self.assertTrue(analysis["conditional_roles_retained"])
        self.assertFalse(analysis["hawking_directly_measured"])
        self.assertFalse(analysis["hawking_nonobservation_rewarded_as_match"])

    def test_unfavourable_controls_reject(self):
        record = authoritative_record(ROOT)
        reversed_order = json.loads(json.dumps(record))
        reversed_order["sources"][1]["rows"]["massive_neutron_star"]["reported_mass_solar"] = "13/10"
        self.assertFalse(exact_analysis(reversed_order)["neutron_star_interval_wholly_above_white_dwarf_limit"])
        collapsed_upper = json.loads(json.dumps(record))
        collapsed_upper["sources"][2]["rows"]["conditional_hypermassive_maximum"]["maximum_baryonic_mass_solar"] = "2/1"
        self.assertFalse(exact_analysis(collapsed_upper)["both_conditional_uppers_above_neutron_interval"])
        erased_condition = json.loads(json.dumps(record))
        erased_condition["sources"][2]["rows"]["conditional_nonrotating_maximum"]["use_boundary"] = "direct measurement"
        self.assertFalse(exact_analysis(erased_condition)["conditional_roles_retained"])


if __name__ == "__main__":
    unittest.main()
