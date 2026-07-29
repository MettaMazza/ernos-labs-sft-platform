from fractions import Fraction
from pathlib import Path

from sft.materials.therm_001_007_external_v1 import load_complete_vector
from sft.materials.therm_001_007_laws_v1 import ORDER, SPECS, boundary_resistance, diffusivity_relation, phase_storage, phonon_mean_path, radiative_partition, thermal_shock_fatigue, thermoelectric_boundary
from sft.physics.structural_constants import candidate_rows, survivor_id

def test_therm_complete_grammars():
    assert len(ORDER) == 7
    for claim_id in ORDER:
        rows = candidate_rows(SPECS[claim_id])
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(SPECS[claim_id]) for row in rows) == 1
        assert all(witness.passed for witness in SPECS[claim_id].witnesses)

def test_therm_native_relations():
    assert diffusivity_relation(12, 2, 3)["diffusivity_part"] == 2
    assert boundary_resistance(3, 6, 2, "film-substrate")["resistance_part"] == 1
    assert phonon_mean_path((2, 4, 3), ("boundary", "isotope", "interface"))["mean_path"] == 3
    assert radiative_partition(10, 2, 3, 5, "infrared", "toward")["closes"]
    assert thermoelectric_boundary(2, 3, 2, 3)["performance_part"] == 2
    assert phase_storage(2, 5, 3, ("solid", "transition", "liquid"))["latent_part"] == Fraction(1, 2)
    assert thermal_shock_fatigue((2, 5, 3), ("heating", "cooling", "heating"), (None, 1, 2), 5)["first_crack_cycle"] == 2

def test_therm_complete_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 7
    assert vector["captured_source_count"] == 12
    assert vector["unavailable_source_count"] == 0
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
