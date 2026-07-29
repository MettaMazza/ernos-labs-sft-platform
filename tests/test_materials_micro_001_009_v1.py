from fractions import Fraction
from pathlib import Path

from sft.materials.micro_001_009_external_v1 import load_complete_vector
from sft.materials.micro_001_009_laws_v1 import ORDER, SPECS, coarsening_transfer, inclusion_boundary, interface_motion, multiscale_correspondence, site_balance
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_complete_micro_family_has_one_survivor_per_grammar():
    assert len(ORDER) == 9
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        rows = candidate_rows(spec)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1
        assert all(witness.passed for witness in spec.witnesses)


def test_exact_native_microstructure_boundaries():
    assert site_balance(8, (2, 7))["defect_part"] == Fraction(1, 4)
    assert inclusion_boundary(2, 3, 6)["boundary_class"].startswith("semicoherent")
    assert coarsening_transfer((2, 3), 1, 2, 2)["final"] == (None, 5)
    assert interface_motion((2, 4, 5), 6)["mobility"] == Fraction(1, 2)
    assert multiscale_correspondence((("a", 2, Fraction(1, 2)), ("b", 1, Fraction(1, 1))))["bulk_response"] == Fraction(2, 3)


def test_complete_micro_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 9
    assert vector["captured_source_count"] == 9
    assert vector["unavailable_source_count"] == 1
    assert vector["all_favourable_adverse_absent_unavailable_unresolved_rows_preserved"] is True
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_available_fragments_present"] for row in vector["claims"])
