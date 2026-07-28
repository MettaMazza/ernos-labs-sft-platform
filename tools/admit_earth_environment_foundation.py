#!/usr/bin/env python3
"""Admit and materialize the 74 Earth foundation laws in receipt order."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def verify_boundaries() -> None:
    from sft.engine_seal import require_engine_seal

    require_engine_seal(ROOT)
    verifier_path = ROOT / "tools/verify_verification_authority_seal.py"
    definition = importlib.util.spec_from_file_location("_earth_authority_seal_check", verifier_path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load verification-authority seal checker")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    attestation = module.verify()
    if attestation["violations"]:
        raise RuntimeError("VOID_INVALID_HALTED: " + "; ".join(attestation["violations"]))


verify_boundaries()

from sft.earth_environment.empirical_program import EARTH_SPECS, PRE_SOURCE_SEAL_PATH  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402
from tools.scaffold_earth_environment_foundation_claims import EXACT_RESULTS  # noqa: E402


CHECKPOINT = ROOT / "census/earth_environment_continuation_checkpoint.json"


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_earth_" + claim_id.replace("-", "_"), path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def admitted_rows() -> dict[str, dict[str, object]]:
    return {
        row["claim_id"]: row
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
        if row.get("model_admitted") is True
    }


def manifest_entry(claim_id: str) -> None:
    path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write_json(path, manifest)


def update_checkpoint(last_claim_id: str | None, receipt_hash: str | None, admitted_count: int, next_operation: str, status: str = "in_progress") -> None:
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    checkpoint.update(
        {
            "schema": "sft-v3-earth-environment-continuation-checkpoint/1",
            "branch": "earth_environment",
            "foundation_required_claim_count": len(EARTH_SPECS),
            "admitted_claim_count": admitted_count,
            "remaining_claim_count": len(EARTH_SPECS) - admitted_count,
            "last_admitted_claim_id": last_claim_id,
            "last_admitted_receipt_hash": receipt_hash,
            "closure_status": "depth_independent" if last_claim_id else None,
            "status": status,
            "next_exact_operation": next_operation,
            "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
            "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
            "protected_authority_modified": False,
            "remote_publication_authorized": False,
        }
    )
    write_json(CHECKPOINT, checkpoint)


def materialize(spec, execution, receipt, captured) -> None:
    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
    row = admitted_rows()[spec.claim_id]
    package = ROOT / "claims" / spec.claim_id
    audit = json.loads((ROOT / "experiments/earth_environment/source_feature_audit.json").read_text(encoding="utf-8"))
    targets = json.loads((ROOT / "experiments/earth_environment/claim_specific_external_targets.json").read_text(encoding="utf-8"))
    target = next(item for item in targets["targets"] if item["claim_id"] == spec.claim_id)
    preserved_failure_count = sum(
        transport["transport_status"] != "captured"
        for source in audit["sources"]
        for transport in source["transport_history"]
    )
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "status": "model_admitted_empirically_tested_and_independently_reconstructed",
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
            "exact_structural_or_numeric_result": EXACT_RESULTS.get(spec.claim_id, "unique exact structural relation; dimensional Earth magnitudes remain source-, place-, time-, instrument- and protocol-bounded records"),
            "closure_scope": receipt.closure_status,
            "controls_passed": all(item.passed for item in sealed.controls),
            "independently_recomputed": external.passed,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "external_evidence_class": spec.empirical_disposition,
            "evidence_directness": spec.directness,
            "registered_source_feature_count": audit["registered_feature_count"],
            "present_source_feature_count": audit["present_feature_count"],
            "absent_source_feature_count_preserved": audit["absent_feature_count"],
            "transport_failure_rows_preserved": preserved_failure_count,
            "claim_target_evaluation": target,
            "external_evidence_selected_survivor": False,
            "formal_structure_relabelled_as_direct_measurement": False,
            "model_or_forecast_relabelled_as_observation": False,
            "free_parameters": [],
            "axioms": [],
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/earth_environment" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["status"] = "empirical_boundary_corresponded"
    write_json(experiment_path, experiment)
    certificate = payloads["certificate.json"]
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_empirically_tested_and_independently_reconstructed`\n\n"
        f"- Closure: `{certificate['closure_scope']}`\n"
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
        f"- Independent validation: `{certificate['external_validation_hash']}`\n"
        f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`\n"
        f"- External receipt: `{certificate['measurement_receipt_hash']}`\n"
        f"- Engine receipt: `{row['receipt_hash']}`\n"
        f"- Evidence directness: `{spec.directness}`\n"
        f"- Evidence disposition: `{spec.empirical_disposition}`\n"
        f"- Source features: `{audit['present_feature_count']} present / {audit['absent_feature_count']} absent preserved / {audit['registered_feature_count']} registered`\n"
        f"- Preserved transport failures: `{preserved_failure_count}`\n"
        "- External evidence selected the structural survivor: `false`\n"
        "- Model, forecast, retrieval or proxy relabelled as direct observation: `false`\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="maximum new admissions in this invocation")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive")
    verify_boundaries()
    repository = EngineRepository(ROOT)
    already = admitted_rows()
    ordered_ids = [row.claim_id for row in EARTH_SPECS]
    prefix = 0
    for claim_id in ordered_ids:
        if claim_id in already:
            prefix += 1
        else:
            break
    if any(claim_id in already for claim_id in ordered_ids[prefix:]):
        raise RuntimeError("Earth receipts are not a continuous dependency prefix")
    last = ordered_ids[prefix - 1] if prefix else None
    last_hash = already[last]["receipt_hash"] if last else None
    next_id = ordered_ids[prefix] if prefix < len(ordered_ids) else None
    update_checkpoint(last, last_hash, prefix, f"admit_{next_id}" if next_id else "reconcile_audit_inventory_and_publication_gate")
    pending = EARTH_SPECS[prefix:]
    if args.limit is not None:
        pending = pending[: args.limit]
    for index, spec in enumerate(pending, prefix + 1):
        verify_boundaries()
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

        try:
            receipt = repository.execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
        except Exception:
            update_checkpoint(last, last_hash, index - 1, f"repair_or_preserve_halt_{spec.claim_id}", status="halted_on_claim")
            raise
        verify_boundaries()
        manifest_entry(spec.claim_id)
        materialize(spec, execution, receipt, captured)
        last = spec.claim_id
        last_hash = receipt.receipt_hash
        next_claim = ordered_ids[index] if index < len(ordered_ids) else None
        update_checkpoint(spec.claim_id, receipt.receipt_hash, index, f"admit_{next_claim}" if next_claim else "reconcile_audit_inventory_and_publication_gate")
        if index == 1 or index % 5 == 0 or index == len(ordered_ids):
            print(f"[{index}/{len(ordered_ids)}] admitted {spec.claim_id}: {receipt.receipt_hash}", flush=True)


if __name__ == "__main__":
    main()
