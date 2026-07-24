from fractions import Fraction
import unittest

from sft.physics.lineage_particle_laws import (
    LINEAGE_PARTICLE_SPECS,
    colour_running_prefix,
    dirac_g_factor,
    electroweak_mixing,
    mediator_count,
    parity_fibre,
    pmns_squared_support,
    prime_sector_ladder,
    proton_planck_squared_ratio,
    sector_coupling,
    wz_squared_ratio,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


class PhysicsLineageParticleLawTests(unittest.TestCase):
    def test_every_law_has_one_survivor_in_complete_product(self) -> None:
        for spec in LINEAGE_PARTICLE_SPECS:
            rows = candidate_rows(spec)
            self.assertEqual(len(rows), 256)
            self.assertEqual(sum(row["candidate_id"] == survivor_id(spec) for row in rows), 1)

    def test_force_ladder(self) -> None:
        self.assertEqual(prime_sector_ladder(), (2, 3, 5, 7))
        self.assertEqual(tuple(mediator_count(p) for p in prime_sector_ladder()), (3, 8, 24, 48))
        self.assertEqual(tuple(sector_coupling(p) for p in prime_sector_ladder()), (Fraction(1, 2), Fraction(2, 3), Fraction(4, 5), Fraction(6, 7)))

    def test_electroweak_and_wz(self) -> None:
        self.assertEqual(electroweak_mixing(), {"unified": Fraction(1, 2), "sin_squared": Fraction(1, 4), "cos_squared": Fraction(3, 4)})
        self.assertEqual(wz_squared_ratio(), Fraction(3, 4))

    def test_scale_and_pmns(self) -> None:
        self.assertEqual(proton_planck_squared_ratio(), 2**127)
        self.assertEqual(pmns_squared_support(), {"atmospheric": Fraction(1, 2), "solar": Fraction(1, 3), "reactor": Fraction(1, 48)})

    def test_running_g_and_parity(self) -> None:
        self.assertEqual(colour_running_prefix(5), (1, 3, 5, 7, 9))
        self.assertEqual(dirac_g_factor(), 2)
        self.assertEqual(parity_fibre(), {"left_held": Fraction(1, 4), "image": Fraction(1, 2), "right_held": Fraction(3, 4)})


if __name__ == "__main__":
    unittest.main()
