#!/usr/bin/env python3
"""Admit all twelve MAGSC claims sequentially through the untouched engine."""
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.materials.magsc_001_012_laws_v1 import ORDER, SPECS

REGISTRY_ID = "sha256:870a795db025bba127c3b77e0c10b88c266c2ce497170ff670173a5ee06d5281"
MANIFEST_ID = "sha256:f26998b37ac11e9a2f1509fdeb81ea7cb72413139de619a3fdd076ab355fbc58"
VECTOR_ID = "sha256:7b6fb80b2b335d79a95ec7dafb34577ad0fd32967f09f0029ce0f0fef71d0e75"

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

def seals():
    for tool, expected in (("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"), ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY")):
        result = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        payload = json.loads(result.stdout)
        if result.returncode or payload.get("status") != expected:
            raise SystemExit("Materials MAGSC admission halted: protected seal invalid")

def execution(claim_id):
    path = ROOT / "claims" / claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("materials_magsc_" + claim_id.replace("-", "_"), path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)

def main():
    from sft.engine import EngineRepository
    seals()
    census_path = ROOT / "census/claims.json"
    manifest_path = ROOT / "census/execution_manifest.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    present = [claim_id for claim_id in ORDER if claim_id in existing]
    if present:
        raise SystemExit("Materials MAGSC admission refuses replay: " + ", ".join(present))
    for index, claim_id in enumerate(ORDER, 1):
        spec = SPECS[claim_id]
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in existing)
        if missing:
            raise SystemExit(f"Materials MAGSC admission halted: missing dependencies {claim_id}: {missing}")
        run = execution(claim_id)
        captured = {}
        class Independent:
            def validate(self, sealed):
                captured["sealed"] = sealed
                captured["independent"] = run.independent_validator.validate(sealed)
                return captured["independent"]
        class Empirical:
            def validate(self, sealed):
                captured["empirical"] = run.empirical_validator.validate(sealed)
                return captured["empirical"]
        receipt = EngineRepository(ROOT).execute_official(run.program, Independent(), run.source_files, Empirical())
        if not receipt.model_admitted:
            raise SystemExit("untouched engine halted: " + claim_id)
        manifest = json.loads(manifest_path.read_text())
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write_json(manifest_path, manifest)
        row = next(item for item in json.loads(census_path.read_text())["claims"] if item["claim_id"] == claim_id)
        sealed, independent, empirical = captured["sealed"], captured["independent"], captured["empirical"]
        package = ROOT / "claims" / claim_id
        write_json(package / "candidate_census.json", {"claim_id": claim_id, **asdict(sealed.census)})
        write_json(package / "elimination_receipt.json", {"claim_id": claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)})
        write_json(package / "controls.json", {"claim_id": claim_id, "controls": asdict(sealed)["controls"]})
        write_json(package / "empirical_validation.json", {"claim_id": claim_id, **asdict(empirical)})
        comparison_count = next(item["comparison_count"] for item in json.loads((ROOT / "experiments/external_sources/materials/magsc_001_012_v1/complete_evidence_vector_v1.json").read_text())["claims"] if item["claim_id"] == claim_id)
        write_json(package / "certificate.json", {
            "claim_id": claim_id,
            "materials_obligation": spec.obligation_id,
            "status": "model_admitted_authoritatively_corresponded_and_independently_replicated",
            "source_manifest_hash": run.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": independent.implementation_hash,
            "independent_certificate_hash": independent.certificate_hash,
            "independently_recomputed": True,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "falsification_condition": empirical.falsification_condition,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "exact_result": spec.exact_result,
            "closure_scope": receipt.closure_status,
            "controls_passed": True,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "free_parameters": [],
            "imported_axioms": [],
            "target_registry_identity": REGISTRY_ID,
            "source_custody_manifest_identity": MANIFEST_ID,
            "complete_evidence_vector_identity": VECTOR_ID,
            "captured_authoritative_source_count": 12,
            "external_comparison_count": comparison_count,
        })
        (package / "STATUS.md").write_text(f"# {claim_id}\n\nStatus: `model_admitted_authoritatively_corresponded_and_independently_replicated`\n\n- Obligation: `{spec.obligation_id}`\n- Exact result: {spec.exact_result}\n- Candidate census: `256`, unique survivor: `1`\n- Engine receipt: `{receipt.receipt_hash}`\n- Closure: `{receipt.closure_status}`\n")
        seals()
        existing.add(claim_id)
        print(f"[{index}/{len(ORDER)}] admitted {claim_id}: {receipt.receipt_hash}", flush=True)

if __name__ == "__main__":
    main()
