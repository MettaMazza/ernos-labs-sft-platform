"""Complete observational reconciliation for the sealed Physics Grand Lock."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)


CLAIM_ID = "SFT-PHYS-VALIDATION-GRAND-LOCK-076"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-GRAND-LOCK-076"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/physics-grand-lock-empirical-reconciliation-record.json"
SOURCE_HASH = "sha256:e233cd761aa874893d2c2a4e2b09f071297aee1204d531fce3d93429948177a3"
OBSERVATION_LABEL = "complete-Physics-empirical-vector-with-all-adverse-and-scope-boundary-records-retained"
ROOT = Path(__file__).resolve().parents[2]


def source_record() -> dict[str, object]:
    path = ROOT / SOURCE_PATH
    if "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_HASH:
        raise ValueError("Grand Lock empirical reconciliation record changed")
    return json.loads(path.read_text(encoding="utf-8"))


def record_certificate(record: dict[str, object] | None = None) -> dict[str, object]:
    record = source_record() if record is None else record
    rows = tuple(record["empirical_claims"])
    ids = tuple(row["claim_id"] for row in rows)
    legacy = tuple(record["legacy_empirical_materialization_without_separate_measurement_receipt"])
    adverse = tuple(record["unfavorable_or_scope_boundary_ids"])
    boundary = record["methodological_boundary"]
    required_true = tuple(key for key in boundary if key != "measurements_select_formal_survivor")
    return {
        "unique_complete_empirical_vector": len(ids) == len(set(ids)) == record["empirical_claim_count"] == 234,
        "all_empirical_and_external_hashes": all(row["empirical_validation_hash"] and row["external_validation_hash"] for row in rows),
        "all_available_measurement_receipts_retained": all(row.get("measurement_receipt_hash") or row["claim_id"] in legacy for row in rows),
        "legacy_shape_exact": set(legacy) == {row["claim_id"] for row in rows if not row.get("measurement_receipt_hash")},
        "adverse_scope_vector_exact": len(adverse) == len(set(adverse)) == 14 and set(adverse).issubset(set(record["physics_claim_ids"])),
        "external_source_vector_exact": len(record["unique_external_source_ids"]) == len(set(record["unique_external_source_ids"])) == record["unique_external_source_id_count"] == 147,
        "methodological_boundary": boundary.get("measurements_select_formal_survivor") is False and all(boundary.get(key) is True for key in required_true),
        "formal_receipt_bound": record["formal_grand_lock"]["receipt_hash"] == "sha256:ae18f67371c8e7054430935d6b5e5f3162f24cf9cba073769384bf7ba467d817",
    }


class ObservationalGrandLockProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


_record = source_record()
_certificate = record_certificate(_record)
EMPIRICAL_DEPENDENCIES = tuple(row["claim_id"] for row in _record["empirical_claims"])

SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Complete Physics empirical-vector and adverse-result Grand Lock",
    statement=(
        "After formal Grand Lock 075 sealed, the complete pre-lock Physics empirical surface was reconciled as one "
        "immutable vector. All 234 empirically tested claim receipts, all 147 distinct registered external source "
        "identities, every empirical and external validation hash, every available measurement receipt, all six "
        "explicit legacy materialization shapes, and all fourteen detected unfavorable-result or scope-boundary "
        "claims remain present together. Observation is retained as empirical evidence; prior observations are not "
        "mislabelled as unseen predictions, and no measurement is allowed to select a formal survivor."
    ),
    dependencies=tuple(dict.fromkeys(("SFT-PHYS-GRAND-LOCK-TERMINAL-075",) + EMPIRICAL_DEPENDENCIES + (
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ))),
    generation_rule=(
        "Generate the complete eight-axis product of full empirical carrier, reconciliation relation, immutable "
        "provenance, sealed execution, separate observation record, complete favorable/adverse rows, successor "
        "closure and no-extra-rule."
    ),
    grammar_boundary=(
        "Every empirically tested pre-lock Physics claim; every source, validation and available measurement-receipt "
        "identity; every explicit legacy receipt shape; every retained unfavorable result and scope boundary; and all 256 alternatives."
    ),
    dimensions=empirical_dimensions(
        OBSERVATION_LABEL,
        "The complete reconciled record retains every empirical claim and every favorable, unfavorable, legacy and scope-boundary row.",
    ),
    exact_result=(
        "Exactly 234 pre-lock Physics claims carry independently replicated empirical validation; their complete "
        "vector binds 147 distinct registered external source identities. All 234 empirical and external validation "
        "hashes are retained. Every available separate measurement receipt is retained, while six older claim "
        "packages lacking that later materialization field are explicitly identified rather than silently upgraded. "
        "All fourteen detected unfavorable-result or scope-boundary claims remain inside the same vector. The formal "
        "Grand Lock receipt predates this aggregate reconciliation; observations validate or challenge their declared "
        "claims but never select or alter a formal survivor."
    ),
    induction_base="The sealed Grand Lock 075 fixes the complete formal branch identity before the aggregate empirical record is opened.",
    induction_step="Appending any empirical claim requires its immutable receipt, both validation hashes, every available measurement receipt, all source identities and any adverse or scope boundary; omission halts.",
    exclusions=(
        "no favorable-only selection or deletion of mismatch, non-observation, tension, uncertainty or scope boundary",
        "no prior observation relabelled as an unseen prediction",
        "no legacy certificate silently represented as having a later separate measurement-receipt field",
        "no measurement, consensus model, fit, parameter or tolerance selecting a formal survivor",
        "no edit to the canonical engine or any admitted receipt",
    ),
    operational_witnesses=tuple((key, key.replace("_", " "), passed) for key, passed in _certificate.items()),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(ExternalTargetRow(
        "SFT-V3-PHYSICS-COMPLETE-EMPIRICAL-RECONCILIATION",
        "SFT-V3-PHYSICS-IMMUTABLE-EMPIRICAL-EVIDENCE-SURFACE",
        "all 234 empirical receipts, 147 source identities and every adverse/scope record",
        OBSERVATION_LABEL,
    ),),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any empirical claim, validation hash, available measurement receipt, source identity, legacy "
        "receipt shape, unfavorable result or scope boundary is omitted or changed; if the formal receipt does not "
        "predate this reconciliation; if prior observations are relabelled as unseen; if measurement selects a "
        "formal survivor; or if any hostile control passes."
    ),
)

SPEC.validate()


__all__ = (
    "CLAIM_ID", "EMPIRICAL_DEPENDENCIES", "EXPERIMENT_ID", "OBSERVATION_LABEL",
    "ObservationalGrandLockProgram", "SOURCE_HASH", "SOURCE_PATH", "SPEC",
    "record_certificate", "source_record",
)
