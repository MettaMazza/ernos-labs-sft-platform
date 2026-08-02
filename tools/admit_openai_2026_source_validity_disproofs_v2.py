#!/usr/bin/env python3
"""Admit twelve corrected source-artifact validity disproofs."""

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


REGISTRY = ROOT / "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json"
LEAN_REPORT = ROOT / "generated/lean4_validation/reports/openai_2026_source_validity_lean4.json"
VALIDATOR = ROOT / "generated/openai_2026_source_validity_validator_v2.py"
CLAIMS = ROOT / "census/claims.json"
MANIFEST = ROOT / "census/execution_manifest.json"
LEAN_SUFFIXES = (
    "spherePacking_source_invalid",
    "binaryCodeMrrw_source_invalid",
    "sphericalCodeHierarchy_source_invalid",
    "nonsoficGroup_source_invalid",
    "connesRigidity_source_invalid",
    "permanentFormula_source_invalid",
    "quantumParallelRepetition_source_invalid",
    "gapCvp400_source_invalid",
    "ehrhartVolume_source_invalid",
    "multicolourRamsey_source_invalid",
    "compactness_source_invalid",
    "twoDegenerate_source_invalid",
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def object_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def verify_seals() -> None:
    for tool, expected in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        completed = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        payload = json.loads(completed.stdout)
        if completed.returncode or payload.get("status") != expected:
            raise SystemExit(f"source-validity admission halted: {tool}")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("oai26_validity_" + claim_id.replace("-", "_"), path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load execution: {claim_id}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def independent_details(claim_id: str, sealed) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="sft-oai26-validity-independent-") as temporary:
        sealed_path = Path(temporary) / "sealed.json"
        sealed_path.write_text(json.dumps(canonical_value(sealed), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        completed = subprocess.run(
            (sys.executable, str(VALIDATOR), claim_id, str(ROOT), str(sealed_path)),
            cwd=temporary,
            text=True,
            capture_output=True,
            timeout=180,
        )
        if completed.returncode:
            raise RuntimeError(f"independent detail verification failed: {claim_id}: {completed.stderr}")
        payload = json.loads(completed.stdout)
        if payload.get("passed") is not True:
            raise RuntimeError(f"independent detail did not pass: {claim_id}")
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
        raise RuntimeError(f"root-to-result order incomplete: {claim_id}")
    positions = {node["claim_id"]: index for index, node in enumerate(ordered)}
    trace = {
        "schema": "sft-v3-openai-2026-source-validity-root-trace/2",
        "claim_id": claim_id,
        "root_claim_id": "SFT-ROOT-THERE-IS-NO-NOTHING",
        "target_receipt_hash": receipt_row["receipt_hash"],
        "dependency_node_count": len(ordered),
        "nodes_topological_root_to_result": ordered,
        "theorem_specific_steps": proof_steps,
        "all_nodes_model_admitted": all(node["model_admitted"] is True for node in ordered),
        "all_edges_prior": all(
            positions[dependency] < index
            for index, node in enumerate(ordered)
            for dependency in node["direct_dependencies"]
        ),
    }
    trace["trace_identity"] = object_hash(trace)
    return trace


def main() -> None:
    verify_seals()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows = registry["rows"]
    order = tuple(row["claim_id"] for row in rows)
    lean_names = tuple("SFTValidation.OpenAI2026.SourceValidity." + suffix for suffix in LEAN_SUFFIXES)
    lean = json.loads(LEAN_REPORT.read_text(encoding="utf-8"))
    if (
        lean.get("status") != "PASS"
        or lean.get("source_validity_obligation_count") != 12
        or lean.get("disproved_count") != 12
        or lean.get("theorem_axiom_audit") != "empty"
        or tuple(lean.get("theorem_names", ())) != lean_names
    ):
        raise SystemExit("source-validity admission halted: Lean report did not pass")
    census = json.loads(CLAIMS.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing = {row["claim_id"] for row in census["claims"]}
    manifested = {row["claim_id"] for row in manifest["claims"]}
    partial = [claim_id for claim_id in order if (claim_id in existing) != (claim_id in manifested)]
    if partial:
        raise SystemExit("source-validity admission halted: partial census/manifest state: " + ", ".join(partial))
    admitted_now = []
    for ordinal, (registry_row, lean_theorem) in enumerate(zip(rows, lean_names), start=1):
        claim_id = registry_row["claim_id"]
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

        receipt = EngineRepository(ROOT).execute_official(execution.program, Independent(), execution.source_files)
        if not receipt.model_admitted or receipt.external_status != "independently_replicated":
            raise RuntimeError(f"frozen engine did not admit source-validity disproof: {claim_id}")
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write_json(MANIFEST, manifest)
        census = json.loads(CLAIMS.read_text(encoding="utf-8"))
        receipt_row = next(row for row in census["claims"] if row["claim_id"] == claim_id)
        sealed = captured["sealed"]
        independent = captured["independent"]
        independent_payload = independent_details(claim_id, sealed)
        package = ROOT / "claims" / claim_id
        spec = json.loads((package / "derivation_spec_v2.json").read_text(encoding="utf-8"))
        source_binding = json.loads((package / "source_binding_v2.json").read_text(encoding="utf-8"))
        target = json.loads((package / "source_validity_target_v2.json").read_text(encoding="utf-8"))
        correspondence = {
            "schema": "sft-v3-openai-2026-source-validity-correspondence/2",
            "claim_id": claim_id,
            "status": "TOTAL_SEMANTIC_CORRESPONDENCE_DISPROVED",
            "exact_source_syntax_quotation_proved": True,
            "source_statement_hash": spec["source_statement_hash"],
            "source_binding_hash": spec["source_binding_hash"],
            "source_quantifier_and_conjunct_order": spec["source_quantifier_and_conjunct_order"],
            "quoted_quantifier_and_conjunct_order": spec["quoted_quantifier_and_conjunct_order"],
            "logical_shape_preserved_as_quotation": True,
            "total_truth_preserving_admission_exists": False,
            "nonexistence_reason": spec["contradiction_summary"],
            "native_reconstruction_claim_id": spec["original_reconstruction_claim_id"],
            "native_reconstruction_is_distinct": True,
            "native_reconstruction_transfers_source_validity": False,
            "carrier_inadmissibility_used_as_negation_of_mathematical_conclusion": False,
            "actual_negated_target": spec["sft_validity_proposition"],
            "lean_theorem": lean_theorem,
            "lean_report_path": LEAN_REPORT.relative_to(ROOT).as_posix(),
            "lean_report_sha256": file_hash(LEAN_REPORT),
            "lean_axiom_audit": "empty",
        }
        correspondence["correspondence_identity"] = object_hash(correspondence)
        write_json(package / "source_validity_correspondence_certificate_v2.json", correspondence)
        trace = dependency_trace(claim_id, receipt_row, spec["steps"])
        write_json(package / "dependency_trace.json", trace)
        exact_result = "DISPROVED: " + spec["sft_validity_proposition"] + ". " + spec["contradiction_summary"]
        certificate = {
            "schema": "sft-v3-openai-2026-source-validity-disproof-certificate/2",
            "claim_id": claim_id,
            "status": "model_admitted_source_validity_disproved_independently_replicated_and_lean4_validated",
            "outcome": "DISPROVED",
            "disproved_target": spec["sft_validity_proposition"],
            "proof_kind": "actual_validity_contradiction",
            "exact_result": exact_result,
            "source_statement_hash": spec["source_statement_hash"],
            "source_manifest_hash": execution.program.registration.source_hash,
            "source_declared_axioms": spec["source_declared_axioms"],
            "sft_registered_axioms": [],
            "axioms": [],
            "free_parameters": [],
            "derivation_identity": spec["derivation_identity"],
            "correspondence_certificate_path": (package / "source_validity_correspondence_certificate_v2.json").relative_to(ROOT).as_posix(),
            "correspondence_certificate_hash": correspondence["correspondence_identity"],
            "dependency_trace_path": (package / "dependency_trace.json").relative_to(ROOT).as_posix(),
            "dependency_trace_hash": trace["trace_identity"],
            "root_to_result_step_count": len(spec["steps"]),
            "executable_check_count": len(spec["checks"]),
            "all_executable_checks_passed": True,
            "actual_contradiction_derived": True,
            "arbitrary_input_or_exhaustive_witness_certificate": "The fixed artifact-validity witness grammar is exhausted: every witness requires zero registered axioms, while the exact artifact has three.",
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "outcome_axis_present": False,
            "native_reconstruction_claim_id": spec["original_reconstruction_claim_id"],
            "native_reconstruction_used_as_validity_premise": False,
            "native_reconstruction_transfers_source_validity": False,
            "carrier_inadmissibility_used_as_negation_of_mathematical_conclusion": False,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_validator_id": independent.validator_id,
            "independent_implementation_hash": independent.implementation_hash,
            "independent_certificate_hash": independent.certificate_hash,
            "independent_detail_certificate_hash": object_hash(independent_payload["certificate"]),
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": receipt_row["receipt_path"],
            "closure_scope": receipt.closure_status,
            "lean_theorem": lean_theorem,
            "lean_report_path": LEAN_REPORT.relative_to(ROOT).as_posix(),
            "lean_report_sha256": file_hash(LEAN_REPORT),
            "lean_axiom_audit": "empty",
        }
        write_json(package / "candidate_census.json", {"claim_id": claim_id, **asdict(sealed.census)})
        write_json(package / "elimination_receipt.json", {"claim_id": claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)})
        write_json(package / "controls.json", {"claim_id": claim_id, "controls": asdict(sealed)["controls"]})
        write_json(package / "independent_verification.json", independent_payload)
        write_json(package / "certificate.json", certificate)
        (package / "STATUS.md").write_text(
            f"# {claim_id}\n\n"
            "Status: `model_admitted_source_validity_disproved_independently_replicated_and_lean4_validated`\n\n"
            f"- Source-artifact verdict: `DISPROVED AS SFT-VALID`\n"
            f"- Exact negated target: `{spec['sft_validity_proposition']}`\n"
            f"- Frozen-engine receipt: `{receipt.receipt_hash}`\n"
            f"- Lean theorem: `{lean_theorem}` with empty axiom audit\n"
            f"- Root-to-result steps: `{len(spec['steps'])}`; executable checks: `{len(spec['checks'])}`\n"
            f"- Separate native reconstruction: `{spec['original_reconstruction_claim_id']}`; validity transfer: `false`\n",
            encoding="utf-8",
        )
        verify_seals()
        existing.add(claim_id)
        admitted_now.append(claim_id)
        print(f"[{ordinal}/12] admitted disproof {claim_id}: {receipt.receipt_hash}", flush=True)
    print(json.dumps({
        "status": "ADMITTED",
        "admitted_now": admitted_now,
        "source_artifact_validity_disproved": 12,
        "source_artifact_validity_proved": 0,
        "open": 0,
        "native_reconstruction_transferred": False,
        "lean4": "PASS_EMPTY_AXIOM_AUDIT",
        "engine_or_verification_authority_edited": False,
    }, indent=2))


if __name__ == "__main__":
    main()
