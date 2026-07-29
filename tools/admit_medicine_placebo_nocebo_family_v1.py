#!/usr/bin/env python3
"""Admit the Medicine placebo/nocebo family without changing protected code."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

FORMAL = (
    "SFT-MED-PLACEBO-EXPECTATION-FIBRE-002",
    "SFT-MED-PLACEBO-AVAILABLE-STATE-BOUNDARY-002",
    "SFT-MED-PLACEBO-OBJECTIVE-REPORT-SEPARATION-002",
)
EMPIRICAL = "SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002"


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def seals() -> None:
    for tool, status in (("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"), ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY")):
        run = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        data = json.loads(run.stdout) if run.stdout.strip() else {}
        if run.returncode or data.get("status") != status: raise SystemExit(run.stdout + run.stderr + "\nMedicine admission halted")


def load(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("med_return_" + claim_id.replace("-", "_"), path)
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def manifest(claim_id: str) -> None:
    path = ROOT / "census/execution_manifest.json"; data = json.loads(path.read_text())
    if claim_id not in {x["claim_id"] for x in data["claims"]}:
        data["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"}); write_json(path, data)


def materialize(spec, execution, receipt, captured) -> None:
    sealed, independent, empirical = captured["sealed"], captured["independent"], captured.get("empirical")
    row = next(x for x in json.loads((ROOT / "census/claims.json").read_text())["claims"] if x["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    certificate = {
        "claim_id": spec.claim_id, "status": "authoritatively_corresponded_and_independently_replicated" if empirical else "independently_replicated",
        "source_manifest_hash": execution.program.registration.source_hash, "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash, "derivation_seal_hash": sealed.seal_hash,
        "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash,
        "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": row["receipt_path"], "exact_result": spec.exact_result,
        "closure_scope": receipt.closure_status, "controls_passed": all(x.passed for x in sealed.controls), "independently_recomputed": independent.passed,
        "free_parameters": [], "imported_axioms": [],
    }
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "certificate.json": certificate,
        "registration.json": {"$schema": "../../governance/claim.schema.json", "branch": "medicine", "claim_id": spec.claim_id, "title": spec.title,
            "statement": spec.exact_result, "dependencies": list(spec.dependencies), "excluded_inputs": list(spec.exclusions),
            "candidate_grammar": {"boundary": spec.grammar_boundary, "generator": spec.generation_rule, "completeness_certificate": "untouched-engine complete literal product"},
            "intended_certificate": "Complete 256-form depth-independent census and implementation-distinct reconstruction.",
            "provenance_classes": [x.value for x in spec.provenance], "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"], "status": "empirically_tested" if empirical else "independently_replicated"},
    }
    if empirical:
        payloads["empirical_validation.json"] = {"claim_id": spec.claim_id, **asdict(empirical)}
        certificate.update({"measurement_receipt_hash": empirical.measurement_receipt_hash, "all_external_rows_preserved": empirical.all_rows_preserved,
                            "external_data_source_ids": list(empirical.data_source_ids), "falsification_condition": empirical.falsification_condition})
        from sft.medicine.placebo_nocebo_external_v1 import external_registration_record
        write_json(ROOT / "experiments/medicine/SFT-EXP-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002/registration.json", {**external_registration_record(), "status": "authoritatively_corresponded"})
    for name, value in payloads.items(): write_json(package / name, value)
    (package / "STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `{certificate['status']}`\n\n- {spec.exact_result}\n- Every one of 256 forms was enumerated; one survived; all controls passed.\n- Engine receipt: `{receipt.receipt_hash}`\n", encoding="utf-8")


def admit(order) -> None:
    from sft.engine import EngineRepository
    from sft.medicine.placebo_nocebo_laws_v1 import SPECS
    existing = {x["claim_id"] for x in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    for index, claim_id in enumerate(order, 1):
        if claim_id in existing: raise SystemExit(f"already admitted: {claim_id}")
        spec = SPECS[claim_id]
        current = {x["claim_id"] for x in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
        missing = tuple(x for x in spec.dependencies if x not in current)
        if missing: raise SystemExit(f"{claim_id} dependencies absent: {missing}")
        execution = load(claim_id); captured = {}
        class I:
            def validate(self, sealed):
                captured["sealed"] = sealed; result = execution.independent_validator.validate(sealed); captured["independent"] = result; return result
        class E:
            def validate(self, sealed):
                result = execution.empirical_validator.validate(sealed); captured["empirical"] = result; return result
        receipt = EngineRepository(ROOT).execute_official(execution.program, I(), execution.source_files, E() if execution.empirical_validator else None)
        if not receipt.model_admitted: raise RuntimeError(f"{claim_id} did not enter the model")
        manifest(claim_id); materialize(spec, execution, receipt, captured); seals(); existing.add(claim_id)
        print(f"[{index}/{len(order)}] admitted {claim_id}: {receipt.receipt_hash}", flush=True)


def main() -> None:
    seals()
    if "--formal-only" in sys.argv: admit(FORMAL)
    elif "--empirical-only" in sys.argv: admit((EMPIRICAL,))
    else: admit(FORMAL + (EMPIRICAL,))


if __name__ == "__main__": main()
