from fractions import Fraction
import unittest
from sft.physics.structural_constants import candidate_rows
from sft.physics.thermal_equilibrium_response_terminal_law_v1 import SPEC,canonical_maximum_certificate,deterministic_noise_cycle,dyadic_canonical_counts,dyadic_canonical_weights,exact_temperature,fluctuation_response_ledger,paired_equilibrium_census,total_throw_identity
class Tests(unittest.TestCase):
 def test_temperature(self):
  x=(Fraction(1,4),Fraction(1,2),Fraction(3,4));self.assertEqual(exact_temperature(x),Fraction(1,2));self.assertTrue(total_throw_identity(x))
 def test_equilibrium(self):
  for n in range(1,15):self.assertEqual(paired_equilibrium_census(n)["survivors"],(n,));self.assertEqual(paired_equilibrium_census(n)["share"],Fraction(1,2))
 def test_canonical(self):
  for l in range(2,6):self.assertTrue(canonical_maximum_certificate(l)["unique"]);self.assertEqual(sum(dyadic_canonical_weights(l),Fraction(0)),1)
  self.assertEqual(dyadic_canonical_counts(4),(8,4,2,1))
 def test_response(self):
  r=fluctuation_response_ledger();self.assertTrue(r["complete"] and r["equal_departure"]);self.assertEqual(deterministic_noise_cycle(3)["mean"],Fraction(1,2))
 def test_invalid(self):
  with self.assertRaises(ValueError):exact_temperature(())
  with self.assertRaises(ValueError):paired_equilibrium_census(0)
  with self.assertRaises(ValueError):dyadic_canonical_counts(1)
  with self.assertRaises(ValueError):deterministic_noise_cycle(-1)
 def test_product(self):
  r=candidate_rows(SPEC);self.assertEqual(len(r),256);self.assertEqual(len({x["candidate_id"] for x in r}),256);SPEC.validate()
if __name__=="__main__":unittest.main()
