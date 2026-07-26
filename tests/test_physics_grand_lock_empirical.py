from sft.physics.grand_lock_empirical_v1 import record_certificate, source_record


def test_complete_empirical_reconciliation_vector():
    certificate = record_certificate()
    assert all(certificate.values())
    record = source_record()
    assert record["empirical_claim_count"] == 234
    assert record["unique_external_source_id_count"] == 147


def test_adverse_and_legacy_rows_are_retained():
    record = source_record()
    assert len(record["unfavorable_or_scope_boundary_ids"]) == 14
    assert len(record["legacy_empirical_materialization_without_separate_measurement_receipt"]) == 6
    assert record["methodological_boundary"]["measurements_select_formal_survivor"] is False
