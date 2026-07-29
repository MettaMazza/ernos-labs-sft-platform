from sft.chemistry.pericyclic_missing_measurement_status_v2 import reconstruct_missing_measurements


def test_four_blank_rows_remain_active_measurement_obligations() -> None:
    rows = reconstruct_missing_measurements()
    assert len(rows) == 4
    assert [row.ordinal for row in rows] == [6, 19, 27, 30]
    assert all(row.source_status == "measurement-not-reported-in-primary-table" for row in rows)
    assert all(not row.scientific_result_retired for row in rows)


def test_calculation_columns_cannot_substitute_for_missing_experiment() -> None:
    rows = reconstruct_missing_measurements()
    assert all("endo_exo_experimental_conventional" in row.absent_fields for row in rows)
    assert rows[1].absent_fields == (
        "temperature_conventional",
        "time_conventional",
        "isolated_yield_conventional",
        "endo_exo_experimental_conventional",
    )
