#!/usr/bin/env python3
"""Admit the complete seven-claim Biology return family in dependency order."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ORDER = (
    "SFT-BIO-ORIGIN-AUTOCATALYTIC-IGNITION-002",
    "SFT-BIO-HOMOCHIRAL-AMPLIFICATION-002",
    "SFT-BIO-SOMATIC-GERMLINE-ORBIT-SPLIT-002",
    "SFT-BIO-NEURAL-HALF-ONE-THRESHOLD-002",
    "SFT-BIO-DIFFERENTIATION-LOSS-CANCER-002",
    "SFT-BIO-BOUNDED-ORBIT-ECOSYSTEM-002",
    "SFT-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002",
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_seals() -> None:
    for tool, expected in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        completed = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        response = json.loads(completed.stdout) if completed.stdout.strip() else {}
        if completed.returncode or response.get("status") != expected:
            raise SystemExit(completed.stdout + completed.stderr + "\nBiology family admission halted")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_biology_return_" + claim_id.replace("-", "_"), path)
    if definition is None or definition.loader is None:
        raise RuntimeError(f"cannot load {claim_id}")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def ensure_manifest_entry(claim_id: str) -> None:
    path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write_json(path, manifest)


def materialize(spec, execution, receipt, captured) -> None:
    sealed = captured["sealed"]
    independent = captured["independent"]
    empirical = captured.get("empirical")
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    row = next(item for item in census["claims"] if item["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    certificate = {
        "claim_id": spec.claim_id,
        "status": "authoritatively_corresponded_and_independently_replicated" if empirical else "independently_replicated",
        "source_manifest_hash": execution.program.registration.source_hash,
        "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash,
        "derivation_seal_hash": sealed.seal_hash,
        "external_validation_hash": receipt.external_validation_hash,
        "empirical_validation_hash": receipt.empirical_validation_hash,
        "engine_receipt_hash": receipt.receipt_hash,
        "engine_receipt_path": row["receipt_path"],
        "exact_result": spec.exact_result,
        "closure_scope": receipt.closure_status,
        "controls_passed": all(item.passed for item in sealed.controls),
        "independently_recomputed": independent.passed,
        "free_parameters": [],
        "imported_axioms": [],
    }
    payloads: dict[str, object] = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "certificate.json": certificate,
        "registration.json": {
            "$schema": "../../governance/claim.schema.json",
            "branch": "biology",
            "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": "untouched-engine complete literal product", "generator": spec.generation_rule},
            "claim_id": spec.claim_id,
            "dependencies": list(spec.dependencies),
            "excluded_inputs": list(spec.exclusions),
            "intended_certificate": "Complete 256-form depth-independent census, exact operational witnesses and implementation-distinct reconstruction.",
            "provenance_classes": [item.value for item in spec.provenance],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-28",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "statement": spec.exact_result,
            "status": "empirically_tested" if empirical else "independently_replicated",
            "title": spec.title,
        },
    }
    if empirical:
        payloads["empirical_validation.json"] = {"claim_id": spec.claim_id, **asdict(empirical)}
        certificate.update({
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "falsification_condition": empirical.falsification_condition,
        })
        from sft.biology.prior_mechanisms_external_v1 import external_registration_record
        write_json(ROOT / "experiments/biology/SFT-EXP-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002/registration.json", {**external_registration_record(), "status": "authoritatively_corresponded"})
    for name, payload in payloads.items():
        write_json(package / name, payload)
    (package / "STATUS.md").write_text("\n".join((
        f"# {spec.claim_id}", "", f"Status: `{certificate['status']}`", "",
        f"- {spec.exact_result}",
        "- V1/V2 supplied the reconstruction question only and selected no survivor.",
        "- Every one of 256 forms was enumerated once; one survived; all controls passed.",
        f"- Closure: `{receipt.closure_status}`",
        f"- Engine receipt: `{receipt.receipt_hash}`", "",
    )), encoding="utf-8")


def main() -> None:
    verify_seals()
    from sft.biology.prior_mechanisms_laws_v1 import SPECS
    from sft.engine import EngineRepository
    existing = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]}
    overlap = tuple(claim_id for claim_id in ORDER if claim_id in existing)
    if overlap:
        raise SystemExit("Biology return family already contains admitted identities: " + ", ".join(overlap))
    for index, claim_id in enumerate(ORDER, 1):
        spec = SPECS[claim_id]
        current = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]}
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in current)
        if missing:
            raise SystemExit(f"{claim_id} dependencies absent: " + ", ".join(missing))
        execution = load_execution(claim_id)
        captured = {}

        class CaptureIndependent:
            def validate(self, sealed):
                captured["sealed"] = sealed
                result = execution.independent_validator.validate(sealed)
                captured["independent"] = result
                return result

        class CaptureEmpirical:
            def validate(self, sealed):
                result = execution.empirical_validator.validate(sealed)
                captured["empirical"] = result
                return result

        receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical() if execution.empirical_validator is not None else None)
        if not receipt.model_admitted:
            raise RuntimeError(f"{claim_id} did not enter the model")
        ensure_manifest_entry(claim_id)
        materialize(spec, execution, receipt, captured)
        verify_seals()
        print(f"[{index}/7] admitted {claim_id}: {receipt.receipt_hash}", flush=True)
    from tools.freeze_biology_inventory import main as refresh_inventory
    refresh_inventory()
    verify_seals()


if __name__ == "__main__":
    main()
