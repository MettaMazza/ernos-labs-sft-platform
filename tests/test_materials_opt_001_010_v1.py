from fractions import Fraction
from pathlib import Path

from sft.materials.opt_001_010_external_v1 import load_complete_vector
from sft.materials.opt_001_010_laws_v1 import ORDER, SPECS, absorption_extinction, birefringence, exciton_dynamics, light_scattering, luminescence_yield, nonlinear_mixing, photonic_gap, plasmonic_response, reflection_transmission, waveguide_confinement
from sft.physics.structural_constants import candidate_rows, survivor_id

def test_opt_complete_grammars():
    assert len(ORDER) == 10
    for claim_id in ORDER:
        rows = candidate_rows(SPECS[claim_id])
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(SPECS[claim_id]) for row in rows) == 1
        assert all(witness.passed for witness in SPECS[claim_id].witnesses)

def test_opt_native_relations():
    assert absorption_extinction(8, 2, 2, 3, 1, "sample")["extinction_part"] == Fraction(1, 2)
    assert reflection_transmission(8, 2, 3, 3, "normal")["reflection_part"] == Fraction(1, 4)
    assert luminescence_yield(5, 3, 2, "pump", "emission")["quantum_yield"] == Fraction(3, 5)
    assert light_scattering(8, 2, 2, 4, "bidirectional")["scattered_part"] == Fraction(1, 2)
    assert birefringence(5, 3, "ordinary", "extraordinary", "crystal")["gap_magnitude"] == 2
    assert nonlinear_mixing((2, 3), 5, "sum", ("p", "s", "p"))["complete_path"]
    assert waveguide_confinement(5, 3, 2, "core", "cladding", ("input", "output"))["guided_part"] == Fraction(3, 5)
    assert photonic_gap(2, 6, 4, "periodic", "defect")["confined"]
    assert plasmonic_response(5, 3, 2, "metal-dielectric", "surface")["collective_part"] == Fraction(3, 5)
    assert exciton_dynamics(5, 3, 2, 4, ("generated", "transported", "terminal"))["retained_part"] == Fraction(2, 5)

def test_opt_complete_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 10
    assert vector["captured_source_count"] == 11
    assert vector["unavailable_source_count"] == 0
    assert vector["initial_source_limitation_preserved"]
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
