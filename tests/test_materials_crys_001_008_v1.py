import json

from sft.materials.crys_001_008_external_v1 import load_complete_vector
from sft.materials.crys_001_008_laws_v1 import ORDER, SPECS, diffraction_ledger, exact_distribution, modulation_ledger, pair_distribution, stacking_fault_ledger, twin_domain_ledger
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_complete_family_candidate_products_have_one_survivor():
    assert len(ORDER) == 8
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        rows = candidate_rows(spec)
        assert len(rows) == 256
        assert len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1
        assert all(witness.passed for witness in spec.witnesses)


def test_native_exact_operations_preserve_sft_boundaries():
    assert diffraction_ledger((("phase-one", 2), ("phase-three", 2)))["coherent_ordered_pair_count"] is None
    assert exact_distribution(("a", "b", "a"))[0][1].denominator == 3
    assert stacking_fault_ledger(tuple("ABCABC"))["fault_count"] is None
    assert twin_domain_ledger(((1, 2, 3),))["operation_is_involution"] is True
    assert modulation_ledger(5)["base_translation_restores_modulation"] is False
    assert pair_distribution((1, 2, 4))[0][0] == 1


def test_complete_post_registry_external_vector():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    vector = load_complete_vector(root)
    assert vector["claim_count"] == 8
    assert vector["captured_source_count"] == 8
    assert vector["unavailable_source_count"] == 2
    assert vector["all_favourable_adverse_absent_unavailable_unresolved_rows_preserved"] is True
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_available_fragments_present"] for row in vector["claims"])


def test_target_registry_remains_value_free():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "census/materials_crys_001_008_target_registry_v1.json").read_text())
    assert registry["target_count"] == 8
    assert registry["target_content_present"] is False
    assert registry["survivor_identity_present"] is False
    assert registry["measured_value_present"] is False
    assert registry["outcome_present"] is False
