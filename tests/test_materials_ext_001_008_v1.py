from pathlib import Path

from sft.materials.ext_001_008_external_v1 import load_complete_vector
from sft.materials.ext_001_008_laws_v1 import (
    ORDER,
    SPECS,
    combined_extreme,
    cryogenic_response,
    electric_field_response,
    high_pressure_state,
    high_temperature_state,
    magnetic_field_response,
    radiation_response,
    shock_response,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_ext_complete_grammars():
    assert len(ORDER) == 8
    for claim_id in ORDER:
        rows = candidate_rows(SPECS[claim_id])
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(SPECS[claim_id]) for row in rows) == 1
        assert all(witness.passed for witness in SPECS[claim_id].witnesses)


def test_ext_native_relations():
    args = ("s", (1, 2), ("a", "b"), (("a", "b"),), "m", "u")
    assert high_pressure_state(*args)["pressure_state_held"]
    assert high_temperature_state(*args)["temperature_state_held"]
    assert cryogenic_response("s", (2, 1), ("a", "b"), (("a", "b"),), "m", "u")["descending_path_held"]
    assert electric_field_response(*args)["field_response_held"]
    assert magnetic_field_response(*args)["field_response_held"]
    assert shock_response("s", (1, 2), ("a", "b"), (("a", "b"),), ("load", "impact"), "m", "u")["shock_path_held"]
    assert radiation_response("s", (1, 2), ("a", "b"), (("a", "b"),), (("d1", "a", "b"),), "m", "u")["defect_custody_held"]
    assert combined_extreme("s", ("heat", "force"), ((1, 1), (2, 2)), ("a", "b"), (("a", "b"),), "m", "u")["combined_path_held"]


def test_ext_complete_external_vector():
    vector = load_complete_vector(Path(__file__).resolve().parents[1])
    assert vector["claim_count"] == 8
    assert vector["captured_source_count"] == 8
    assert vector["unavailable_source_count"] == 0
    assert {row["claim_id"] for row in vector["claims"]} == set(ORDER)
    assert all(row["all_comparisons_preserved"] and row["all_registered_fragments_present"] for row in vector["claims"])
