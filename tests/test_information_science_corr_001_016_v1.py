from pathlib import Path

from sft.information_science.generated_law import candidate_records, survivor_id
from sft.information_science.corr_001_016_external_v1 import load
from sft.information_science.corr_001_016_laws_v1 import IDS, OBS, SPECS

ROOT = Path(__file__).resolve().parents[1]


def test_complete_family_products():
    assert len(IDS) == len(SPECS) == 16
    for spec in SPECS.values():
        spec.validate()
        rows = candidate_records(spec)
        assert len(rows) == len({row["candidate_id"] for row in rows}) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1


def test_operational_observations():
    assert len(OBS) == 16
    assert all(passed for _statement, passed in OBS.values())


def test_registry_and_vector_order():
    registry, vector = load(ROOT)
    assert registry["target_content_present"] is False
    assert len(registry["claim_ids"]) == vector["record_count"] == 16
    assert vector["outcomes_opened_only_after_registry_freeze"]
    assert tuple(row["claim_id"] for row in vector["records"]) == tuple(registry["claim_ids"])


def test_all_rows_and_measures_are_preserved():
    _registry, vector = load(ROOT)
    assert vector["all_rows_preserved"]
    assert all(row["all_rows_preserved"] and row["source_ids"] for row in vector["records"])
