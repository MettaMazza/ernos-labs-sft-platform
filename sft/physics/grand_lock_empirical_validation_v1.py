"""Independent empirical reconciliation checks for Grand Lock 076."""

from dataclasses import replace
import json
from pathlib import Path

from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator
from sft.physics.grand_lock_empirical_v1 import CLAIM_ID, SOURCE_HASH, SOURCE_PATH, SPEC, record_certificate


class GrandLockEmpiricalValidator(BlindExternalMeasurementValidator):
    def validate(self, sealed):
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong Grand Lock empirical seal")
        path = self.root / SOURCE_PATH
        if hash_file(path) != SOURCE_HASH:
            raise ValueError("Grand Lock empirical source changed")
        record = json.loads(path.read_text(encoding="utf-8"))
        formal = record["formal_grand_lock"]
        if hash_file(self.root / formal["receipt_path"]) != formal["receipt_file_sha256"]:
            raise ValueError("formal Grand Lock receipt file changed")
        if hash_file(self.root / record["prelock_input_path"]) != record["prelock_input_sha256"]:
            raise ValueError("pre-lock Grand Lock input changed")
        certificate = record_certificate(record)
        if not all(certificate.values()):
            raise ValueError("complete empirical reconciliation did not close")

        missing_row = json.loads(json.dumps(record))
        missing_row["empirical_claims"] = missing_row["empirical_claims"][1:]
        missing_rejected = not record_certificate(missing_row)["unique_complete_empirical_vector"]
        missing_adverse = json.loads(json.dumps(record))
        missing_adverse["unfavorable_or_scope_boundary_ids"] = missing_adverse["unfavorable_or_scope_boundary_ids"][1:]
        adverse_rejected = not record_certificate(missing_adverse)["adverse_scope_vector_exact"]
        false_legacy = json.loads(json.dumps(record))
        false_legacy["legacy_empirical_materialization_without_separate_measurement_receipt"] = []
        legacy_rejected = not record_certificate(false_legacy)["legacy_shape_exact"]
        selector = json.loads(json.dumps(record))
        selector["methodological_boundary"]["measurements_select_formal_survivor"] = True
        selector_rejected = not record_certificate(selector)["methodological_boundary"]
        controls = (missing_rejected, adverse_rejected, legacy_rejected, selector_rejected)
        if not all(controls):
            raise ValueError("Grand Lock empirical hostile control failed")

        base = super().validate(sealed)
        payload = {
            "sealed": sealed.seal_hash,
            "source": SOURCE_HASH,
            "certificate": certificate,
            "controls": controls,
            "empirical_claim_ids": tuple(row["claim_id"] for row in record["empirical_claims"]),
            "external_source_ids": tuple(record["unique_external_source_ids"]),
            "adverse_ids": tuple(record["unfavorable_or_scope_boundary_ids"]),
            "legacy_ids": tuple(record["legacy_empirical_materialization_without_separate_measurement_receipt"]),
        }
        measurements = (
            "Complete immutable reconciliation of 234 empirically tested Physics claims.",
            "All 147 distinct registered external source identities remain present.",
            "Every empirical and external validation hash and every available separate measurement receipt remains bound.",
            "Six older materialization shapes without a separate measurement-receipt field are explicitly retained, not silently upgraded.",
            "All fourteen detected unfavorable-result or scope-boundary claims remain in the same evidence vector.",
            "Observation remains empirical evidence; prior observations are not relabelled as unseen predictions and never select a formal survivor.",
        )
        return replace(
            base,
            all_rows_preserved=True,
            data_source_ids=tuple(record["unique_external_source_ids"]),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(payload),
            passed=base.passed and all(certificate.values()) and all(controls),
        )


__all__ = ("GrandLockEmpiricalValidator",)
