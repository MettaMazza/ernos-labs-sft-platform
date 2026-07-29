#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
ORDER = ("SFT-ENG-CONSCIOUSNESS-PLACEBO-CROSS-BINDING-PROTOCOL-002", "SFT-ENG-NOVEL-TRANSLATIONS-NO-OMISSION-ADDENDUM-002")

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

def seals():
    for tool, expected in (("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"), ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY")):
        run = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True); payload = json.loads(run.stdout)
        if run.returncode or payload.get("status") != expected: raise SystemExit("Engineering addendum halted: protected seal invalid")

def load(claim_id):
    path = ROOT / "claims" / claim_id / "execution.py"; spec = importlib.util.spec_from_file_location("eng_addendum_" + claim_id.replace("-", "_"), path); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module.build_execution(ROOT)

def main():
    from sft.engine import EngineRepository
    from sft.engineering.novel_translation_addendum_laws_v1 import SPECS
    seals(); census_path = ROOT / "census/claims.json"; manifest_path = ROOT / "census/execution_manifest.json"; existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    for index, claim_id in enumerate(ORDER, 1):
        if claim_id in existing: raise SystemExit("already admitted: " + claim_id)
        spec = SPECS[claim_id]; missing = tuple(dependency for dependency in spec.dependencies if dependency not in existing)
        if missing: raise SystemExit(f"missing dependencies for {claim_id}: {missing}")
        execution = load(claim_id); captured = {}
        class Capture:
            def validate(self, sealed): captured["sealed"] = sealed; result = execution.independent_validator.validate(sealed); captured["independent"] = result; return result
        receipt = EngineRepository(ROOT).execute_official(execution.program, Capture(), execution.source_files)
        if not receipt.model_admitted: raise SystemExit("untouched engine halted: " + claim_id)
        manifest = json.loads(manifest_path.read_text()); manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"}); write_json(manifest_path, manifest)
        row = next(row for row in json.loads(census_path.read_text())["claims"] if row["claim_id"] == claim_id); sealed, independent, package = captured["sealed"], captured["independent"], ROOT / "claims" / claim_id
        certificate = {"claim_id": claim_id, "status": "independently_replicated", "source_manifest_hash": execution.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash, "independent_implementation_hash": independent.implementation_hash, "independent_certificate_hash": independent.certificate_hash, "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": row["receipt_path"], "exact_result": spec.exact_result, "closure_scope": receipt.closure_status, "controls_passed": True, "apparatus_outcome_claimed": False, "free_parameters": [], "imported_axioms": []}
        payloads = {
            "candidate_census.json": {"claim_id": claim_id, **asdict(sealed.census)},
            "elimination_receipt.json": {"claim_id": claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
            "controls.json": {"claim_id": claim_id, "controls": asdict(sealed)["controls"]},
            "certificate.json": certificate,
            "registration.json": {"$schema": "../../governance/claim.schema.json", "branch": "engineering_translation", "claim_id": claim_id, "title": spec.title, "statement": spec.exact_result, "dependencies": list(spec.dependencies), "excluded_inputs": list(spec.exclusions), "candidate_grammar": {"boundary": spec.grammar_boundary, "generator": spec.generation_rule, "completeness_certificate": "untouched-engine complete literal product"}, "registered_by": "Maria Smith", "registration_date": "2026-07-29", "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"], "status": "independently_replicated"},
        }
        for name, value in payloads.items(): write_json(package / name, value)
        (package / "STATUS.md").write_text(f"# {claim_id}\n\nStatus: `independently_replicated`\n\n- {spec.exact_result}\n- Physical or participant outcome: `not claimed by this protocol law`\n- Engine receipt: `{receipt.receipt_hash}`\n")
        seals(); existing.add(claim_id); print(f"[{index}/{len(ORDER)}] admitted {claim_id}: {receipt.receipt_hash}", flush=True)

if __name__ == "__main__": main()
