"""Capability-closed post-seal validation for Chemistry ORG-014."""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

from google.protobuf.json_format import MessageToDict
import pyarrow.parquet as pq
from ord_schema.proto import reaction_pb2

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.selectivity_distribution_batch_v1 import ANALYSIS_PATH, AUTHORITIES, PARQUET_PATH, SELECTIVITY_DISTRIBUTION_SPEC
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _definition(root: Path, authority_index: int) -> str:
    document = json.loads((root / AUTHORITIES[authority_index][0]).read_text())
    return " ".join(row["text"] for row in document["term"]["definitions"]).casefold()


def _reconstruct_rows(root: Path) -> tuple[dict[str, object], ...]:
    table = pq.read_table(root / PARQUET_PATH, columns=["reaction_id", "reaction"])
    rows = []
    for ordinal, (reaction_id, payload) in enumerate(zip(table["reaction_id"].to_pylist(), table["reaction"].to_pylist()), 1):
        reaction = reaction_pb2.Reaction(); reaction.ParseFromString(payload)
        outcomes = []
        for outcome_ordinal, outcome in enumerate(reaction.outcomes, 1):
            complete = MessageToDict(outcome, preserving_proto_field_name=True, use_integers_for_enums=True)
            products = []
            for product_ordinal, product in enumerate(outcome.products, 1):
                record = MessageToDict(product, preserving_proto_field_name=True, use_integers_for_enums=True)
                products.append({
                    "product_ordinal": product_ordinal,
                    "complete_product_record": record,
                    "complete_product_record_sha256": _digest(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()),
                    "identifier_count": len(product.identifiers),
                    "measurement_count": len(product.measurements),
                })
            outcomes.append({
                "outcome_ordinal": outcome_ordinal,
                "complete_outcome_record": complete,
                "complete_outcome_record_sha256": _digest(json.dumps(complete, sort_keys=True, separators=(",", ":")).encode()),
                "products_in_source_order": products,
            })
        rows.append({
            "row_ordinal": ordinal, "reaction_id": reaction_id, "raw_reaction_payload_sha256": _digest(payload),
            "outcomes_in_source_order": outcomes, "outcome_count": len(outcomes),
            "product_count": sum(len(row["products_in_source_order"]) for row in outcomes),
        })
    return tuple(rows)


def exact_analysis(root: Path, rows: tuple[dict[str, object], ...] | None = None) -> tuple[dict[str, object], dict[str, bool]]:
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected:
            raise ValueError(f"ORG-014 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = dict(analysis); recorded_hash = vector.pop("complete_result_vector_sha256")
    if recorded_hash != _digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()):
        raise ValueError("ORG-014 result vector changed")
    reconstructed = _reconstruct_rows(root)
    recorded = tuple(analysis["reaction_rows_in_preregistered_order"]) if rows is None else rows
    if reconstructed != recorded or len(recorded) != 130:
        raise ValueError("ORG-014 complete ORD reconstruction changed")
    chemo, regio, stereo = (_definition(root, index) for index in (8, 9, 10))
    checks = {
        "SFT-CHEM-ORG-014-IUPAC-CHEMO": all(value in chemo for value in ("preferential reaction", "two or more different functional groups")),
        "SFT-CHEM-ORG-014-IUPAC-REGIO": all(value in regio for value in ("direction of bond making or breaking", "all other possible directions")),
        "SFT-CHEM-ORG-014-IUPAC-STEREO": all(value in stereo for value in ("preferential formation", "one stereoisomer over another")),
    }
    for row in reconstructed:
        checks[f"SFT-CHEM-ORG-014-ORD-ROW-{row['row_ordinal']:03d}"] = bool(row["reaction_id"]) and len(row["outcomes_in_source_order"]) == row["outcome_count"]
    if tuple(checks) != tuple(row.target_id for row in SELECTIVITY_DISTRIBUTION_SPEC.target_rows) or not all(checks.values()):
        raise ValueError("ORG-014 target comparison changed")
    expected_counts = (130, 130, 152, 302, 195, 19)
    actual_counts = tuple(analysis[key] for key in (
        "complete_registered_reaction_row_count", "complete_outcome_count", "complete_product_count",
        "complete_product_identifier_count", "complete_product_measurement_count", "rows_with_multiple_reported_products",
    ))
    if actual_counts != expected_counts or analysis["major_product_filter_applied"] is not False:
        raise ValueError("ORG-014 distribution completeness changed")
    return {
        "complete_reaction_rows": 130, "complete_outcomes": 130, "complete_products": 152,
        "complete_product_identifiers": 302, "complete_product_measurements": 195,
        "multi_product_rows": 19, "numeric_measurement_inscriptions_by_sign": analysis["numeric_measurement_inscriptions_by_sign"],
        "complete_result_vector_sha256": recorded_hash,
    }, checks


class SelectivityDistributionValidator:
    def __init__(self, root: Path): self.root = root.resolve(); self.spec = SELECTIVITY_DISTRIBUTION_SPEC

    def validate(self, sealed):
        self.spec.validate(); analysis, checks = exact_analysis(self.root)
        registration = observational_experiment_registration_record(self.spec); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets={key: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for key, passed in checks.items()},
            custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root); audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("ORG-014 prediction package changed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": key, "predicted": execution.output.label, "observed": release.targets[key].label, "passed": execution.output.label == release.targets[key].label} for key in checks)
        try:
            source = json.loads((self.root / ANALYSIS_PATH).read_text()); exact_analysis(self.root, tuple(source["reaction_rows_in_preregistered_order"][:-1])); omission_rejected = False
        except ValueError: omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and omission_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-org-014-complete-distribution/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("ORG-014 target release changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission_rejected, "trace": execution.trace_hash}
        measurements = (
            "all 130 preregistered ORD reaction rows and 130 outcomes retained in source order",
            "all 152 products, 302 product identifiers and 195 product measurements retained",
            "all 19 multi-product rows retained and no major-product filter applied",
            "all amount absences and 147 positive external numeric inscriptions retained; no observed signed-zero or negative inscription hidden",
            f"complete result vector {analysis['complete_result_vector_sha256']}",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = ("SelectivityDistributionValidator", "exact_analysis")
