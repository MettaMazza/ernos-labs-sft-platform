from fractions import Fraction
from pathlib import Path

from sft.materials.class_001_012_external_v1 import load_complete_vector
from sft.materials.class_001_012_laws_v1 import ORDER, SPECS, alloy_phase, architected_cellular, cementitious_composite, ceramic_subclass, complex_alloy, fibre_load_transfer, functionally_graded, metallic_glass, ordered_intermetallic, particle_load_transfer, polymer_subclasses, refractory_class
from sft.physics.structural_constants import candidate_rows, survivor_id

def test_class_complete_grammars():
    assert len(ORDER) == 12
    for claim_id in ORDER:
        rows = candidate_rows(SPECS[claim_id])
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(SPECS[claim_id]) for row in rows) == 1
        assert all(witness.passed for witness in SPECS[claim_id].witnesses)

def test_class_native_relations():
    assert alloy_phase(("A", "B"), (3, 2), ("solution", "compound"))["closes"]
    assert ordered_intermetallic(("alpha", "beta"), (2, 3), "AB")["ordered"]
    assert len(complex_alloy((2, 3, 5), ("A", "B", "C"), ("solution",))["component_parts"]) == 3
    assert refractory_class(5, 4, ("phase-a",), "sample")["survival_part"] == Fraction(4, 5)
    assert len(cementitious_composite(2, 5, 1, 2, "sample")["constituent_parts"]) == 4
    assert fibre_load_transfer(8, 4, 3, 1, "aligned")["reinforcement_part"] == Fraction(1, 2)
    assert particle_load_transfer(8, 3, 4, 1, "dispersed")["reinforcement_part"] == Fraction(3, 8)
    assert metallic_glass(("near", "medium"), "absent", "metastable", "alloy")["noncrystalline"]
    assert ceramic_subclass(("load",), ("dielectric",), "oxide", "sintered")["roles_distinct"]
    assert polymer_subclasses(("softens", "reshape", "retains-chain"), ("crosslinked", "permanent-shape", "does-not-commonly-soften"), ("elastic", "deform", "recover"))["classes_distinct"]
    assert functionally_graded(("left", "middle", "right"), (2, 3, 5))["complete_gradient"]
    assert architected_cellular(4, 6, 3, ("auxetic",), "lattice")["topology_retained"]

def test_class_complete_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 12
    assert vector["captured_source_count"] == 11
    assert vector["unavailable_source_count"] == 0
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
