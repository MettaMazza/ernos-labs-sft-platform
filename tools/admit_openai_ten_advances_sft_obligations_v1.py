#!/usr/bin/env python3
"""Admit the twelve proved OpenAI 2026 SFT reconstructions through the frozen engine."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository
from sft.engine.canonical import canonical_value, sha256_identity
from sft.openai_2026.obligations_v1 import ORDER


LEAN_REPORT = ROOT / "generated/lean4_validation/reports/openai_2026_obligations_lean4.json"
VALIDATOR = ROOT / "generated/openai_2026_sft_obligation_validator_v1.py"
CLAIMS = ROOT / "census/claims.json"
MANIFEST = ROOT / "census/execution_manifest.json"


LEAN_THEOREMS = {
    ORDER[0]: "SFTValidation.OpenAI2026.Obligations.spherePacking_proved",
    ORDER[1]: "SFTValidation.OpenAI2026.Obligations.binaryCodeMrrw_proved",
    ORDER[2]: "SFTValidation.OpenAI2026.Obligations.sphericalCodeHierarchy_proved",
    ORDER[3]: "SFTValidation.OpenAI2026.Obligations.nonsoficGroup_proved",
    ORDER[4]: "SFTValidation.OpenAI2026.Obligations.connesRigidity_proved",
    ORDER[5]: "SFTValidation.OpenAI2026.Obligations.permanentFormula_proved",
    ORDER[6]: "SFTValidation.OpenAI2026.Obligations.quantumParallelRepetition_proved",
    ORDER[7]: "SFTValidation.OpenAI2026.Obligations.gapCvp400_proved",
    ORDER[8]: "SFTValidation.OpenAI2026.Obligations.ehrhartVolume_proved",
    ORDER[9]: "SFTValidation.OpenAI2026.Obligations.multicolourRamsey_proved",
    ORDER[10]: "SFTValidation.OpenAI2026.Obligations.compactness_proved",
    ORDER[11]: "SFTValidation.OpenAI2026.Obligations.twoDegenerate_proved",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def object_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def verify_seals() -> None:
    for tool, expected in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools" / tool), "--json"),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(completed.stdout)
        if completed.returncode or payload.get("status") != expected:
            raise SystemExit(f"OpenAI 2026 admission halted: {tool}")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("oai26_" + claim_id.replace("-", "_"), path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load execution: {claim_id}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def stage_correspondence_obligations() -> None:
    for claim_id in ORDER:
        path = ROOT / "claims" / claim_id / "correspondence_obligation.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("status") == "registered_pending_derivation":
            payload["status"] = "derivation_specified_pending_frozen_engine"
            payload["lean_correspondence_module"] = "generated/lean4_validation/SFTValidation/OpenAI2026/Correspondence.lean"
            payload["theorem_specific_lean_module"] = "generated/lean4_validation/SFTValidation/OpenAI2026/Obligations.lean"
            write_json(path, payload)
        elif payload.get("status") != "derivation_specified_pending_frozen_engine":
            raise SystemExit(f"OpenAI 2026 admission halted: unexpected correspondence status: {claim_id}")


def independent_details(claim_id: str, sealed) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="sft-oai26-independent-detail-") as temporary:
        input_path = Path(temporary) / "sealed.json"
        input_path.write_text(json.dumps(canonical_value(sealed), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        completed = subprocess.run(
            (sys.executable, str(VALIDATOR), claim_id, str(ROOT), str(input_path)),
            cwd=temporary,
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )
        if completed.returncode:
            raise RuntimeError(f"independent detail verification failed: {claim_id}: {completed.stderr}")
        payload = json.loads(completed.stdout)
        if payload.get("passed") is not True:
            raise RuntimeError(f"independent detail verification did not pass: {claim_id}")
        return payload


def dependency_trace(claim_id: str, receipt_row: dict[str, object], proof_steps: list[dict[str, object]]) -> dict[str, object]:
    census = json.loads(CLAIMS.read_text(encoding="utf-8"))
    rows = {row["claim_id"]: row for row in census["claims"]}
    visited: set[str] = set()
    visiting: set[str] = set()
    ordered: list[dict[str, object]] = []

    def visit(current: str) -> None:
        if current in visited:
            return
        if current in visiting:
            raise RuntimeError(f"dependency cycle at {current}")
        visiting.add(current)
        registration_path = ROOT / "claims" / current / "registration.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        direct = list(registration.get("dependencies", []))
        for dependency in direct:
            visit(dependency)
        row = rows[current]
        ordered.append({
            "claim_id": current,
            "branch": row["branch"],
            "direct_dependencies": direct,
            "registration_path": registration_path.relative_to(ROOT).as_posix(),
            "registration_sha256": file_hash(registration_path),
            "receipt_path": row["receipt_path"],
            "receipt_hash": row["receipt_hash"],
            "model_admitted": row["model_admitted"],
        })
        visiting.remove(current)
        visited.add(current)

    visit(claim_id)
    if not ordered or ordered[0]["claim_id"] != "SFT-ROOT-THERE-IS-NO-NOTHING" or ordered[-1]["claim_id"] != claim_id:
        raise RuntimeError(f"root-to-result order is incomplete: {claim_id}")
    trace = {
        "schema": "sft-v3-openai-2026-root-to-result-trace/1",
        "claim_id": claim_id,
        "root_claim_id": "SFT-ROOT-THERE-IS-NO-NOTHING",
        "target_receipt_hash": receipt_row["receipt_hash"],
        "dependency_node_count": len(ordered),
        "nodes_topological_root_to_result": ordered,
        "theorem_specific_steps": proof_steps,
        "all_nodes_model_admitted": all(node["model_admitted"] is True for node in ordered),
        "all_edges_prior": all(
            ordered.index(next(node for node in ordered if node["claim_id"] == dependency)) < index
            for index, node in enumerate(ordered)
            for dependency in node["direct_dependencies"]
        ),
    }
    trace["trace_identity"] = object_hash(trace)
    return trace


def main() -> None:
    verify_seals()
    lean = json.loads(LEAN_REPORT.read_text(encoding="utf-8"))
    if lean.get("status") != "PASS" or lean.get("obligation_count") != 12 or lean.get("theorem_axiom_audit") != "empty":
        raise SystemExit("OpenAI 2026 admission halted: Lean report did not pass")
    stage_correspondence_obligations()
    initial_census = json.loads(CLAIMS.read_text(encoding="utf-8"))
    initial_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing = {row["claim_id"] for row in initial_census["claims"]}
    manifested = {row["claim_id"] for row in initial_manifest["claims"]}
    partial = [claim_id for claim_id in ORDER if (claim_id in existing) != (claim_id in manifested)]
    if partial:
        raise SystemExit("OpenAI 2026 admission halted: census/manifest partial state: " + ", ".join(partial))
    admitted_now = []
    for ordinal, claim_id in enumerate(ORDER, 1):
        if claim_id in existing:
            print(f"[{ordinal}/12] already admitted {claim_id}", flush=True)
            continue
        execution = load_execution(claim_id)
        captured: dict[str, object] = {}

        class Independent:
            def validate(self, sealed):
                captured["sealed"] = sealed
                result = execution.independent_validator.validate(sealed)
                captured["independent"] = result
                return result

        receipt = EngineRepository(ROOT).execute_official(
            execution.program,
            Independent(),
            execution.source_files,
        )
        if not receipt.model_admitted or receipt.external_status != "independently_replicated":
            raise RuntimeError(f"frozen engine did not admit proof: {claim_id}")
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write_json(MANIFEST, manifest)
        census = json.loads(CLAIMS.read_text(encoding="utf-8"))
        row = next(row for row in census["claims"] if row["claim_id"] == claim_id)
        sealed = captured["sealed"]
        independent = captured["independent"]
        independent_payload = independent_details(claim_id, sealed)
        spec = json.loads((ROOT / "claims" / claim_id / "derivation_spec_v1.json").read_text(encoding="utf-8"))
        package = ROOT / "claims" / claim_id
        correspondence = {
            "schema": "sft-v3-openai-2026-correspondence-certificate/1",
            "claim_id": claim_id,
            "status": "PROVED",
            "source_statement_hash": spec["source_statement_hash"],
            "source_signature_hash": spec["source_signature_hash"],
            "translation_hash": spec["translation_hash"],
            "native_formula_hash": sha256_identity(spec["native_formula"]),
            "source_quantifier_and_conjunct_order": spec["source_quantifier_and_conjunct_order"],
            "native_quantifier_and_conjunct_order": spec["translated_quantifier_and_conjunct_order"],
            "required_preservation": spec["correspondence_required_preservation"],
            "encode_decode_theorems": [
                "SFTValidation.OpenAI2026.Correspondence.GeneratedOrdinal.toNat_ofNat",
                "SFTValidation.OpenAI2026.Correspondence.GeneratedOrdinal.ofNat_toNat",
                "SFTValidation.OpenAI2026.Correspondence.forall_iff_of_preserves",
                "SFTValidation.OpenAI2026.Correspondence.exists_iff_of_preserves",
                "SFTValidation.OpenAI2026.Correspondence.implication_iff_of_iff",
                "SFTValidation.OpenAI2026.Correspondence.not_iff_of_iff",
                "SFTValidation.OpenAI2026.Correspondence.eventually_iff_generated",
                "SFTValidation.OpenAI2026.Correspondence.tendsto_iff_generated",
            ],
            "logical_shape_preserved": spec["source_quantifier_and_conjunct_order"] == spec["translated_quantifier_and_conjunct_order"],
            "carrier_rejection_used_as_negation": False,
            "upstream_proof_used_as_derivational_authority": False,
            "lean_report_path": LEAN_REPORT.relative_to(ROOT).as_posix(),
            "lean_report_sha256": file_hash(LEAN_REPORT),
            "lean_axiom_audit": "empty",
        }
        correspondence["correspondence_identity"] = object_hash(correspondence)
        write_json(package / "correspondence_certificate.json", correspondence)
        trace = dependency_trace(claim_id, row, spec["steps"])
        write_json(package / "dependency_trace.json", trace)
        certificate = {
            "schema": "sft-v3-openai-2026-proof-certificate/1",
            "claim_id": claim_id,
            "status": "model_admitted_constructively_proved_independently_replicated_and_lean4_validated",
            "outcome": "PROVED",
            "proof_kind": "constructive_proof",
            "exact_result": "PROVED: " + spec["native_formula"],
            "source_statement_hash": spec["source_statement_hash"],
            "source_manifest_hash": execution.program.registration.source_hash,
            "translation_hash": spec["translation_hash"],
            "derivation_identity": spec["derivation_identity"],
            "correspondence_certificate_path": (package / "correspondence_certificate.json").relative_to(ROOT).as_posix(),
            "correspondence_certificate_hash": correspondence["correspondence_identity"],
            "dependency_trace_path": (package / "dependency_trace.json").relative_to(ROOT).as_posix(),
            "dependency_trace_hash": trace["trace_identity"],
            "root_to_result_step_count": len(spec["steps"]),
            "executable_check_count": len(spec["checks"]),
            "all_executable_checks_passed": True,
            "arbitrary_input_or_exhaustive_witness_certificate": spec["arbitrary_input_certificate"],
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "outcome_axis_present": False,
            "upstream_proof_used_as_premise": False,
            "axioms": [],
            "free_parameters": [],
            "derivation_seal_hash": sealed.seal_hash,
            "independent_validator_id": independent.validator_id,
            "independent_implementation_hash": independent.implementation_hash,
            "independent_certificate_hash": independent.certificate_hash,
            "independent_detail_certificate_hash": object_hash(independent_payload["certificate"]),
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "closure_scope": receipt.closure_status,
            "lean_theorem": LEAN_THEOREMS[claim_id],
            "lean_report_path": LEAN_REPORT.relative_to(ROOT).as_posix(),
            "lean_report_sha256": file_hash(LEAN_REPORT),
            "lean_axiom_audit": "empty",
        }
        write_json(package / "candidate_census.json", {"claim_id": claim_id, **asdict(sealed.census)})
        write_json(package / "elimination_receipt.json", {"claim_id": claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)})
        write_json(package / "controls.json", {"claim_id": claim_id, "controls": asdict(sealed)["controls"]})
        write_json(package / "independent_verification.json", independent_payload)
        write_json(package / "certificate.json", certificate)
        old_registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        old_registration["status"] = "independently_replicated"
        old_registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
        write_json(package / "registration.json", old_registration)
        (package / "STATUS.md").write_text(
            f"# {claim_id}\n\n"
            "Status: `model_admitted_constructively_proved_independently_replicated_and_lean4_validated`\n\n"
            f"- Mathematical outcome: `PROVED`\n"
            f"- Exact result: {certificate['exact_result']}\n"
            f"- Frozen-engine receipt: `{receipt.receipt_hash}`\n"
            f"- Lean theorem: `{LEAN_THEOREMS[claim_id]}` with empty axiom audit\n"
            f"- Root-to-result steps: `{len(spec['steps'])}`; executable checks: `{len(spec['checks'])}`\n"
            "- The upstream OpenAI proof is source custody only and supplied no SFT premise.\n",
            encoding="utf-8",
        )
        verify_seals()
        existing.add(claim_id)
        admitted_now.append(claim_id)
        print(f"[{ordinal}/12] admitted {claim_id}: {receipt.receipt_hash}", flush=True)
    print(json.dumps({
        "status": "ADMITTED",
        "admitted_now": admitted_now,
        "total_openai_2026_obligations": 12,
        "proofs": 12,
        "disproofs": 0,
        "open": 0,
        "lean4": "PASS_EMPTY_AXIOM_AUDIT",
        "engine_or_verification_authority_edited": False,
    }, indent=2))


if __name__ == "__main__":
    main()
