from pathlib import Path
from fractions import Fraction

from sft.materials.magsc_001_012_external_v1 import load_complete_vector
from sft.materials.magsc_001_012_laws_v1 import ORDER, SPECS, anisotropy, coherence_boundary, critical_fields, domain_walls, hysteresis, magnetoresistance, spin_glass, spin_relaxation, superfluid_flow, susceptibility, vortex_pinning
from sft.physics.structural_constants import candidate_rows, survivor_id

def test_magsc_complete_grammars():
    assert len(ORDER) == 12
    for claim_id in ORDER:
        rows = candidate_rows(SPECS[claim_id])
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(SPECS[claim_id]) for row in rows) == 1
        assert all(witness.passed for witness in SPECS[claim_id].witnesses)

def test_magsc_native_relations():
    assert susceptibility(2, 4, "parallel")["susceptibility_part"] == Fraction(1, 2)
    assert susceptibility(2, 4, "opposed")["orientation"] == "opposed"
    assert spin_glass((5, 3), ("mobile", "frozen"), ("cooled",))["first_frozen_position"] == 2
    assert domain_walls(4, 2, ("nucleated", "grown", "moved"))["complete"]
    assert hysteresis(((1, 2, "forward"), (2, 3, "forward"), (2, 2, "reverse"), (1, 2, "reverse")))["loop_closed"]
    assert anisotropy(3, 5, "c")["anisotropy_gap"] == 2
    assert magnetoresistance(4, 6, 3, "parallel")["response_part"] == Fraction(3, 2)
    assert spin_relaxation(5, 3, 2, "parallel")["retained_part"] == Fraction(3, 5)
    assert critical_fields(2, 5, ("Meissner", "mixed", "normal"))["mixed_width"] == 3
    assert vortex_pinning(5, 3, 2, "triangular")["closes"]
    assert coherence_boundary(2, 4, "type-II")["ratio"] == 2
    assert superfluid_flow(5, 3, 2, 4)["closes"]

def test_magsc_complete_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 12
    assert vector["captured_source_count"] == 12
    assert vector["unavailable_source_count"] == 0
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
