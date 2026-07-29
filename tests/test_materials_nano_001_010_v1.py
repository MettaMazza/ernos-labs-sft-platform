from fractions import Fraction
from pathlib import Path

from sft.materials.nano_001_010_external_v1 import load_complete_vector
from sft.materials.nano_001_010_laws_v1 import (
    ORDER,
    SPECS,
    aggregation_dispersion,
    collective_state,
    layer_stack,
    moire_supercell,
    nanocomposite_interface,
    nanoparticle_distribution,
    nanoscale_phase_boundary,
    nanowire_confinement,
    quantum_dot,
    surface_volume,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_nano_complete_grammars():
    assert len(ORDER) == 10
    for claim_id in ORDER:
        rows = candidate_rows(SPECS[claim_id])
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(SPECS[claim_id]) for row in rows) == 1
        assert all(witness.passed for witness in SPECS[claim_id].witnesses)


def test_nano_native_relations():
    assert nanoparticle_distribution((("p1", (1, 2, 3), "rod"), ("p2", (1, 1, 1), "compact")))["all_particles_retained"]
    assert nanowire_confinement(5, 1, 1, ("left", "right"))["one_extended_axis"]
    assert layer_stack(("a", "b", "c"), ("ab", "bc"), ("aligned", "twisted"))["ordered"]
    assert quantum_dot(5, 4, "exciton", ("ground", "excited"))["boundary_held"]
    assert surface_volume(3)["surface_part"] == Fraction(26, 27)
    assert surface_volume(3)["successor_surface_part"] == Fraction(56, 64)
    assert nanoscale_phase_boundary("three-unit-particle", 1, Fraction(3, 2), 2, "ordered", "disordered", "exact-calorimetry")["conditional_boundary"]
    assert collective_state(3, ("a", "b", "a"), "correlated", "nontrivial", (("a", "b"), ("b", "c")))["local_and_collective_retained"]
    assert moire_supercell(2, 3, "layer-a", "layer-b", "twisted")["joint_recurrence"] == 6
    assert nanocomposite_interface(3, 2, 4, "matrix", "inclusion")["interface_contacts_per_unit"] == Fraction(4, 5)
    assert aggregation_dispersion(("p1", "p2", "p3"), (("p1", "p2"), ("p3",)), "water", ("prepared", "measured"))["complete_partition"]


def test_nano_complete_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 10
    assert vector["captured_source_count"] == 10
    assert vector["unavailable_source_count"] == 0
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])

