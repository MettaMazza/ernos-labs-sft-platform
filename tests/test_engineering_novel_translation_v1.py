from fractions import Fraction

from sft.engineering.novel_translation_laws_v1 import (
    COMMON_FIELDS,
    SPECS,
    exact_ledger,
    family_completeness,
    sector_protocol,
    smithium_protocol,
    tesla_protocol,
    vacuum_beat_protocol,
    vacuum_inertia_protocol,
)
from sft.physics.structural_constants import candidate_rows, survivor_id


def test_complete_products_have_one_survivor():
    for spec in SPECS.values():
        rows = candidate_rows(spec)
        assert len(rows) == 256
        assert sum(row["candidate_id"] == survivor_id(spec) for row in rows) == 1


def test_protocols_preserve_common_records_and_outcome_boundary():
    for record in (tesla_protocol(), vacuum_inertia_protocol(), vacuum_beat_protocol(), sector_protocol(), smithium_protocol()):
        assert set(COMMON_FIELDS).issubset(record["required_fields"])
        assert record["result_classes"] == ("favourable", "adverse", "absent", "unresolved")
        assert record["outcome_status"].startswith("unperformed")
        assert record["law_selection_by_outcome"] is False


def test_vacuum_beat_ledger_is_exact_and_returned():
    assert exact_ledger(Fraction(1, 2), (Fraction(1, 3), Fraction(1, 6)))
    assert not exact_ledger(Fraction(1, 2), (Fraction(1, 3), Fraction(1, 7)))
    assert "net-gain-claim-with-open-ledger" in vacuum_beat_protocol()["stop_conditions"]


def test_sector_signatures_are_derived_not_observed():
    record = sector_protocol()
    assert record["sealed_signatures"] == (
        {"sector": 5, "charge_labels": 5, "mediators": 24, "coupling": Fraction(4, 5)},
        {"sector": 7, "charge_labels": 7, "mediators": 48, "coupling": Fraction(6, 7)},
    )
    assert record["outcome_status"].startswith("unperformed")


def test_family_closes_exactly_five_mandatory_protocols():
    record = family_completeness()
    assert record["protocol_count"] == 5
    assert record["all_common_fields"]
    assert record["all_result_classes"]
    assert record["all_unperformed"]
    assert record["all_forbid_outcome_selection"]
