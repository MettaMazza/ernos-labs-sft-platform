from fractions import Fraction
from pathlib import Path

from sft.materials.surf_001_008_external_v1 import load_complete_vector
from sft.materials.surf_001_008_laws_v1 import ORDER, SPECS, adhesion, coating_stack, delamination, roughness_profile, surface_free_state, surface_reaction, tribofilm, wetting
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_surf_complete_grammars():
    assert len(ORDER) == 8
    for claim_id in ORDER:
        rows = candidate_rows(SPECS[claim_id])
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(SPECS[claim_id]) for row in rows) == 1
        assert all(witness.passed for witness in SPECS[claim_id].witnesses)


def test_surf_native_relations():
    assert surface_free_state(3, 2, ("free", "bound"), "held")["surface_part"] == Fraction(2, 5)
    assert wetting(3, 2, Fraction(3, 2), "water", "solid", "goniometry")["custody_complete"]
    assert adhesion(5, 3, 2, 4, "layer-substrate", ("joined", "separated"))["work_per_separated_link"] == 2
    assert coating_stack("substrate", ("bond", "top"), ("sb", "bt"), ("deposited", "cured"))["ordered"]
    assert roughness_profile((1, 3, 2), 5, "profilometry")["height_range"] == 2
    assert surface_reaction(3, ("a",), ("b",), "catalyst", "catalyst", ("adsorb", "transform", "desorb"))["chemistry_handoff"]
    assert tribofilm(5, 3, 2, "film", "substrate", ("initial", "formed"))["coverage_part"] == Fraction(3, 5)
    assert delamination(5, 3, 2, ("start", "front"), "layer", "substrate")["separated_part"] == Fraction(2, 5)


def test_surf_complete_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 8
    assert vector["captured_source_count"] == 8
    assert vector["unavailable_source_count"] == 0
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])

