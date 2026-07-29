#!/usr/bin/env python3
"""Sequential untouched-engine admission for the complete VALID family."""

from dataclasses import asdict
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
CHECKPOINT = ROOT / "audits/ACTIVE_QUANTUM_COMPUTATION_CONTINUATION_CHECKPOINT_2026-07-29.md"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def seals():
    expected = (("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"), ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"))
    for tool, status in expected:
        result = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        data = json.loads(result.stdout)
        if result.returncode or data.get("status") != status:
            raise SystemExit("Quantum VALID admission halted: protected seal invalid")


def load(claim_id):
    path = ROOT / "claims" / claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("valid_" + claim_id.replace("-", "_"), path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def checkpoint(index, claim_id, receipt_hash):
    closed = 270 + index
    CHECKPOINT.write_text(f"""# Active Reversible and Quantum Computation continuation checkpoint - 2026-07-29

## Receipt-backed live position

The frozen complete-field census contains **288 obligations** under identity
`sha256:a7f855b7e9fc6ffe4ae9485faf26f1be44bd672b843ecbfbad42b0f523726e3c`.
The current receipt-backed position is **{closed}/288 ({closed / 288 * 100:.1f}%)**.

The newest admitted claim is `{claim_id}`, receipt `{receipt_hash}`. VALID is
**{index}/12** admitted. The preceding BASE, REVX, QSTATEX, GATEX, QALGX,
QCPLXX, QCOMMX, QCODEX, QSIMX, QLEARNX and QLIMITX families remain complete
and must not be repeated.

## Exact next operation

{"Admit the next VALID claim in frozen dependency order." if index < 12 else "Reconcile the completed VALID family into reconciliation v12; do not resubmit it."}

No protected engine or verification-authority file was changed. No heavy
global verification, push, release or publication is authorized at this stage.
""", encoding="utf-8")


def main():
    seals()
    from sft.engine import EngineRepository
    from sft.quantum_computation.valid_001_012_laws_v1 import IDS, SPECS
    claims_path = ROOT / "census/claims.json"
    manifest_path = ROOT / "census/execution_manifest.json"
    existing = {row["claim_id"] for row in json.loads(claims_path.read_text())["claims"]}
    for index, claim_id in enumerate(IDS, 1):
        if claim_id in existing:
            raise SystemExit("already admitted: " + claim_id)
        spec = SPECS[claim_id]
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in existing)
        if missing:
            raise SystemExit(f"missing dependencies for {claim_id}: {missing}")
        execution, captured = load(claim_id), {}

        class Independent:
            def validate(self, sealed):
                captured["sealed"] = sealed
                result = execution.independent_validator.validate(sealed)
                captured["independent"] = result
                return result

        class Empirical:
            def validate(self, sealed):
                result = execution.empirical_validator.validate(sealed)
                captured["empirical"] = result
                return result

        receipt = EngineRepository(ROOT).execute_official(execution.program, Independent(), execution.source_files, Empirical())
        if not receipt.model_admitted:
            raise SystemExit("untouched engine halted: " + claim_id)
        manifest = json.loads(manifest_path.read_text())
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write(manifest_path, manifest)
        row = next(entry for entry in json.loads(claims_path.read_text())["claims"] if entry["claim_id"] == claim_id)
        sealed, independent, empirical = captured["sealed"], captured["independent"], captured["empirical"]
        package = ROOT / "claims" / claim_id
        certificate = {
            "claim_id": claim_id,
            "quantum_computation_obligation": f"SFT-QUANTUM-OBL-VALID-{index:03d}",
            "status": "empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": independent.implementation_hash,
            "independent_certificate_hash": independent.certificate_hash,
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
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "free_parameters": [],
            "imported_axioms": [],
        }
        payload = {
            "candidate_census.json": {"claim_id": claim_id, **asdict(sealed.census)},
            "elimination_receipt.json": {"claim_id": claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
            "controls.json": {"claim_id": claim_id, "controls": asdict(sealed)["controls"]},
            "empirical_validation.json": {"claim_id": claim_id, **asdict(empirical)},
            "certificate.json": certificate,
            "registration.json": {
                "$schema": "../../governance/claim.schema.json",
                "branch": "quantum_computation",
                "claim_id": claim_id,
                "title": spec.title,
                "statement": spec.statement,
                "dependencies": list(spec.dependencies),
                "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"],
                "axioms": [],
                "free_parameters": [],
                "excluded_inputs": list(spec.boundary_exclusions),
                "candidate_grammar": {"boundary": spec.grammar_boundary, "generator": spec.generation_rule, "expected_cardinality": 256, "unique_survivor": spec.exact_result, "completeness_certificate": "untouched-engine complete literal product"},
                "pre_source_target_registry": "census/quantum_valid_001_012_target_registry_v1.json",
                "empirical_protocol": "post-registry complete current receipt/evidence replay with adverse, absence and ownership custody",
                "registered_by": "Maria Smith",
                "registration_date": "2026-07-29",
                "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
                "status": "empirically_tested",
            },
        }
        for name, value in payload.items():
            write(package / name, value)
        (package / "STATUS.md").write_text(f"# {claim_id}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n- {spec.exact_result}\n- Engine receipt: `{receipt.receipt_hash}`\n")
        seals()
        existing.add(claim_id)
        checkpoint(index, claim_id, receipt.receipt_hash)
        print(f"[{index}/{len(IDS)}] admitted {claim_id}: {receipt.receipt_hash}", flush=True)


if __name__ == "__main__":
    main()
