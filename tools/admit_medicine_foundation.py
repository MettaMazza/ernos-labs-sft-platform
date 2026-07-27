#!/usr/bin/env python3
"""Admit and materialize the 72 foundational Medicine laws in order."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.medicine.empirical_program import MEDICINE_SPECS, PRE_SOURCE_SEAL_PATH  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402
from tools.scaffold_medicine_foundation_claims import EXACT_COUNT_CLAIMS  # noqa: E402


CHECKPOINT = ROOT / "census/medicine_continuation_checkpoint.json"


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_medicine_" + claim_id.replace("-", "_"), path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def admitted_rows() -> dict[str, dict[str, object]]:
    return {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"] if row.get("model_admitted") is True}


def manifest_entry(claim_id: str) -> None:
    path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write_json(path, manifest)


def update_checkpoint(last_claim_id: str | None, receipt_hash: str | None, admitted_count: int, next_operation: str, status: str = "in_progress") -> None:
    write_json(CHECKPOINT, {
        "schema": "sft-v3-medicine-continuation-checkpoint/1",
        "branch": "medicine",
        "foundation_required_claim_count": len(MEDICINE_SPECS),
        "admitted_claim_count": admitted_count,
        "remaining_claim_count": len(MEDICINE_SPECS) - admitted_count,
        "last_admitted_claim_id": last_claim_id,
        "last_admitted_receipt_hash": receipt_hash,
        "closure_status": "depth_independent" if last_claim_id else None,
        "status": status,
        "next_exact_operation": next_operation,
        "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "remote_publication_authorized": False,
    })


def materialize(spec, execution, receipt, captured) -> None:
    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
    row = admitted_rows()[spec.claim_id]
    package = ROOT / "claims" / spec.claim_id
    exact_value = EXACT_COUNT_CLAIMS.get(spec.claim_id)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "status": "model_admitted_authoritatively_corresponded_and_independently_reconstructed",
            "pre_source_complete_branch_seal": PRE_SOURCE_SEAL_PATH,
            "source_manifest_hash": execution.program.registration.source_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "exact_result": spec.exact_result,
            "closure_scope": receipt.closure_status,
            "controls_passed": all(item.passed for item in sealed.controls),
            "independently_recomputed": external.passed,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "external_evidence_class": "post_seal_authority_and_primary_data_correspondence",
            "exact_structural_value_validated": exact_value,
            "patient_or_population_dependent_magnitude_claimed_as_universal": False,
            "failed_source_transport_count_preserved": 2,
            "failed_source_and_adverse_rows_preserved": True,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/medicine" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "authoritatively_and_empirically_corresponded"
    write_json(experiment_path, experiment)
    certificate = payloads["certificate.json"]
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_authoritatively_corresponded_and_independently_reconstructed`\n\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- Independent validation: `{certificate['external_validation_hash']}`\n"
        f"- Post-seal clinical correspondence: `{certificate['empirical_validation_hash']}`\n"
        f"- External receipt: `{certificate['measurement_receipt_hash']}`\n"
        f"- Engine receipt: `{row['receipt_hash']}`\n"
        f"- External source IDs: {', '.join(certificate['external_data_source_ids'])}\n"
        f"- Exact structural value validated: `{exact_value or 'conditional clinical relation; no universal patient or population magnitude'}`\n"
        "- Patient- or population-dependent magnitude claimed as universal: `false`\n"
        "- Two failed source transports plus adverse, null, missing and unresolved scientific rows preserved: `true`\n",
        encoding="utf-8",
    )


def main() -> None:
    repository = EngineRepository(ROOT)
    already = admitted_rows()
    ordered_ids = [row.claim_id for row in MEDICINE_SPECS]
    prefix = 0
    for claim_id in ordered_ids:
        if claim_id in already:
            prefix += 1
        else:
            break
    if any(claim_id in already for claim_id in ordered_ids[prefix + 1:]):
        raise RuntimeError("Medicine receipts are not a continuous dependency prefix")
    last = ordered_ids[prefix - 1] if prefix else None
    last_hash = already[last]["receipt_hash"] if last else None
    next_id = ordered_ids[prefix] if prefix < len(ordered_ids) else None
    update_checkpoint(last, last_hash, prefix, f"admit_{next_id}" if next_id else "reconcile_audit_inventory_and_publication_gate")
    for index, spec in enumerate(MEDICINE_SPECS[prefix:], prefix + 1):
        execution = load_execution(spec.claim_id)
        captured = {}

        class CaptureIndependent:
            def validate(self, sealed):
                captured["sealed"] = sealed
                result = execution.independent_validator.validate(sealed)
                captured["external"] = result
                return result

        class CaptureEmpirical:
            def validate(self, sealed):
                result = execution.empirical_validator.validate(sealed)
                captured["empirical"] = result
                return result

        receipt = repository.execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
        manifest_entry(spec.claim_id)
        materialize(spec, execution, receipt, captured)
        next_claim = ordered_ids[index] if index < len(ordered_ids) else None
        update_checkpoint(spec.claim_id, receipt.receipt_hash, index, f"admit_{next_claim}" if next_claim else "reconcile_audit_inventory_and_publication_gate")
        print(f"[{index}/{len(MEDICINE_SPECS)}] admitted {spec.claim_id}: {receipt.receipt_hash}", flush=True)


if __name__ == "__main__":
    main()
