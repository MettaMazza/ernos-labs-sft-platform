#!/usr/bin/env python3
"""Fail-closed 12/12 completeness audit for the corrected OpenAI response."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import SealedDerivation
from sft.engine.canonical import sha256_identity
from sft.engine.engine import ENGINE_ID
from sft.engine.source import build_source_manifest


REGISTRY_PATH = ROOT / "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json"
LEAN_PATH = ROOT / "generated/lean4_validation/reports/openai_2026_source_validity_lean4.json"
WHOLE_PATH = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"
JSON_REPORT = ROOT / "audits/OPENAI_2026_SFT_SOURCE_VALIDITY_COMPLETENESS_2026-08-02_V2.json"
MD_REPORT = ROOT / "audits/OPENAI_2026_SFT_SOURCE_VALIDITY_COMPLETENESS_2026-08-02_V2.md"


def identity(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"not a JSON object: {path}")
    return value


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("audit_" + claim_id.replace("-", "_"), path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load execution: {claim_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def seal_status(tool: str, expected: str) -> dict[str, object]:
    result = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
    payload = json.loads(result.stdout)
    if result.returncode or payload.get("status") != expected:
        raise ValueError(f"seal failure: {tool}")
    return payload


def main() -> None:
    engine_seal = seal_status("verify_engine_seal.py", "VALID_CANONICAL_ENGINE")
    authority_seal = seal_status("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY")
    registry = load(REGISTRY_PATH)
    registry_input = dict(registry)
    declared_registry_identity = registry_input.pop("registry_identity")
    if identity(registry_input) != declared_registry_identity:
        raise SystemExit("completeness audit halted: registry identity mismatch")
    rows = registry.get("rows")
    if not isinstance(rows, list) or len(rows) != 12:
        raise SystemExit("completeness audit halted: registry does not contain twelve rows")
    lean = load(LEAN_PATH)
    whole = load(WHOLE_PATH)
    census = load(ROOT / "census/claims.json")
    census_rows = {row["claim_id"]: row for row in census["claims"]}
    manifest = load(ROOT / "census/execution_manifest.json")
    manifest_counts = Counter(row["claim_id"] for row in manifest["claims"])
    theorem_names = set(lean.get("theorem_names", []))
    results = []
    global_issues: list[str] = []
    totals = Counter()

    for registry_row in rows:
        claim_id = registry_row["claim_id"]
        package = ROOT / "claims" / claim_id
        issues: list[str] = []
        certificate: dict[str, object] = {}
        try:
            registration = load(package / "registration.json")
            source_binding = load(package / "source_binding_v2.json")
            target = load(package / "source_validity_target_v2.json")
            spec = load(package / "derivation_spec_v2.json")
            certificate = load(package / "certificate.json")
            correspondence = load(package / "source_validity_correspondence_certificate_v2.json")
            trace = load(package / "dependency_trace.json")
            stored_census = load(package / "candidate_census.json")
            elimination = load(package / "elimination_receipt.json")
            stored_controls = load(package / "controls.json")
            independent_detail = load(package / "independent_verification.json")
            source_record = load(ROOT / source_binding["source_statement_path"])
            source_path = ROOT / source_binding["source_file_path"]

            source_binding_input = dict(source_binding)
            quotation_identity = source_binding_input.pop("quotation_identity")
            if identity(source_binding_input) != quotation_identity:
                issues.append("source quotation identity mismatch")
            spec_input = dict(spec)
            derivation_identity = spec_input.pop("derivation_identity")
            if identity(spec_input) != derivation_identity:
                issues.append("derivation identity mismatch")
            if identity(source_record) != registry_row["source_statement_hash"]:
                issues.append("exact source statement hash mismatch")
            if file_hash(source_path) != registry_row["source_file_sha256"]:
                issues.append("exact source file hash mismatch")
            source_text = source_path.read_text(encoding="utf-8")
            if any(token not in source_text for token in registry_row["required_source_tokens"]):
                issues.append("theorem-specific source token missing")
            if source_record.get("exact_quantifier_and_conjunct_order") != source_binding.get("exact_quantifier_and_conjunct_order"):
                issues.append("source quotation changed quantifier/conjunct order")
            if source_record.get("upstream_declared_axioms") != ["propext", "Classical.choice", "Quot.sound"]:
                issues.append("source axiom vector mismatch")
            if target.get("target") != registry_row["sft_validity_proposition"] or target.get("registered_negation") != registry_row["registered_negation"]:
                issues.append("validity target or its exact negation changed")
            if registration.get("statement") != registry_row["registered_negation"]:
                issues.append("registered theorem is not the exact validity negation")
            if registration.get("branch") != registry_row["owner"]:
                issues.append("categorical owner mismatch")
            if registration.get("dependencies") != registry_row["governing_preexisting_claims"]:
                issues.append("governing dependency composition mismatch")
            if any(dependency not in census_rows or census_rows[dependency].get("model_admitted") is not True for dependency in registration["dependencies"]):
                issues.append("governing dependency is not model-admitted")
            dimension_keys = [dimension["key"] for dimension in spec["route_dimensions"]]
            if len(dimension_keys) != 8 or len(set(dimension_keys)) != 8 or {"outcome", "verdict"}.intersection(dimension_keys):
                issues.append("proof-route grammar is incomplete or contains an outcome axis")
            rules = {step["rule"] for step in spec["steps"]}
            if len(spec["steps"]) != 10 or not {"validity_assumption", "contradiction", "negation_introduction", "nontransfer"}.issubset(rules):
                issues.append("actual assumption-to-contradiction proof chain incomplete")
            if len(spec["checks"]) != 5:
                issues.append("executable check count is not five")
            if spec.get("proof_outcome") != "DISPROVED" or spec.get("proof_kind") != "validity_contradiction":
                issues.append("derivation does not disprove the fixed validity target")
            if spec.get("native_reconstruction_used_as_validity_premise") is not False:
                issues.append("native reconstruction was transferred to source validity")

            execution = load_execution(claim_id)
            source_manifest = build_source_manifest(ROOT, execution.source_files)
            if source_manifest.manifest_hash != execution.program.registration.source_hash:
                issues.append("execution source manifest differs from registration")
            if source_manifest.manifest_hash != certificate.get("source_manifest_hash"):
                issues.append("certificate source manifest is stale")
            primary_census = execution.program.generate_candidates()
            primary_decisions = tuple(execution.program.decide_candidate(candidate) for candidate in primary_census.candidates)
            primary_closure = execution.program.closure_evidence(primary_decisions)
            primary_controls = execution.program.run_controls()
            primary_census_json = json.loads(json.dumps({"claim_id": claim_id, **asdict(primary_census)}))
            if primary_census_json != stored_census:
                issues.append("stored candidate census differs from frozen generator")
            if {"claim_id": claim_id, "decisions": [asdict(value) for value in primary_decisions], "closure": asdict(primary_closure)} != elimination:
                issues.append("stored decisions/closure differ from frozen generator")
            if {"claim_id": claim_id, "controls": [asdict(value) for value in primary_controls]} != stored_controls:
                issues.append("stored controls differ from frozen generator")
            expected_seal = sha256_identity({
                "engine_id": ENGINE_ID,
                "registration": execution.program.registration,
                "census": primary_census,
                "decisions": primary_decisions,
                "closure": primary_closure,
                "controls": primary_controls,
            })
            if expected_seal != certificate.get("derivation_seal_hash"):
                issues.append("derivation seal mismatch")
            sealed = SealedDerivation(
                claim_id=claim_id,
                source_hash=execution.program.registration.source_hash,
                census=primary_census,
                decisions=primary_decisions,
                closure=primary_closure,
                controls=primary_controls,
                seal_hash=expected_seal,
            )
            independent = execution.independent_validator.validate(sealed)
            if independent.passed is not True or independent.recomputed_from_declared_inputs is not True:
                issues.append("implementation-distinct verification did not pass")
            if independent.certificate_hash != certificate.get("independent_certificate_hash"):
                issues.append("independent certificate hash mismatch")
            if independent_detail.get("passed") is not True or independent_detail.get("validated_seal_hash") != expected_seal:
                issues.append("stored independent detail does not validate the current seal")

            survivors = [decision for decision in primary_decisions if decision.survives]
            if len(primary_census.candidates) != 256 or len(primary_decisions) != 256 or len(survivors) != 1:
                issues.append("finite route enumeration is not 256/256/one survivor")
            if len(primary_controls) != 4 or not all(control.passed for control in primary_controls):
                issues.append("four adverse controls did not all pass")
            receipt_path = ROOT / certificate["engine_receipt_path"]
            receipt = load(receipt_path)
            current = census_rows.get(claim_id)
            if current is None or current.get("receipt_hash") != certificate.get("engine_receipt_hash"):
                issues.append("claim census/current certificate receipt mismatch")
            if receipt.get("receipt_hash") != certificate.get("engine_receipt_hash") or receipt.get("model_admitted") is not True:
                issues.append("engine receipt is absent or not model-admitted")
            if not all(gate.get("passed") is True for gate in receipt.get("gate_results", [])) or len(receipt.get("gate_results", [])) != 8:
                issues.append("engine admission gates are incomplete")
            if manifest_counts[claim_id] != 1:
                issues.append("execution manifest does not contain exactly one entry")
            if trace.get("root_claim_id") != "SFT-ROOT-THERE-IS-NO-NOTHING" or trace.get("all_nodes_model_admitted") is not True or trace.get("all_edges_prior") is not True:
                issues.append("root-to-result dependency trace is incomplete")
            nodes = trace.get("nodes_topological_root_to_result", [])
            if not nodes or nodes[0].get("claim_id") != trace.get("root_claim_id") or nodes[-1].get("claim_id") != claim_id:
                issues.append("dependency trace endpoints are wrong")
            for node in nodes:
                live = census_rows.get(node.get("claim_id"))
                if live is None or live.get("receipt_hash") != node.get("receipt_hash"):
                    issues.append("dependency trace contains a stale receipt")
                    break
            if correspondence.get("status") != "TOTAL_SEMANTIC_CORRESPONDENCE_DISPROVED" or correspondence.get("exact_source_syntax_quotation_proved") is not True:
                issues.append("correspondence disposition is not the proved source quotation plus disproved total admission")
            if correspondence.get("total_truth_preserving_admission_exists") is not False or correspondence.get("native_reconstruction_transfers_source_validity") is not False:
                issues.append("correspondence certificate permits the invalid transfer")
            if correspondence.get("correspondence_identity") != certificate.get("correspondence_certificate_hash"):
                issues.append("correspondence certificate hash mismatch")
            correspondence_input = dict(correspondence)
            declared_correspondence_identity = correspondence_input.pop("correspondence_identity")
            if identity(correspondence_input) != declared_correspondence_identity:
                issues.append("correspondence identity does not recompute")
            trace_input = dict(trace)
            declared_trace_identity = trace_input.pop("trace_identity")
            if identity(trace_input) != declared_trace_identity or declared_trace_identity != certificate.get("dependency_trace_hash"):
                issues.append("dependency trace identity mismatch")
            if certificate.get("outcome") != "DISPROVED" or certificate.get("actual_contradiction_derived") is not True:
                issues.append("certificate does not record the actual validity disproof")
            if certificate.get("outcome_axis_present") is not False or certificate.get("native_reconstruction_transfers_source_validity") is not False:
                issues.append("certificate contains outcome selection or source-validity transfer")
            if certificate.get("axioms") != [] or certificate.get("free_parameters") != [] or certificate.get("sft_registered_axioms") != []:
                issues.append("SFT certificate is not zero-axiom/zero-parameter")
            if certificate.get("carrier_inadmissibility_used_as_negation_of_mathematical_conclusion") is not False:
                issues.append("carrier failure was mislabeled as negation of the mathematical conclusion")
            if certificate.get("lean_theorem") not in theorem_names or certificate.get("lean_axiom_audit") != "empty":
                issues.append("theorem-specific Lean axiom audit missing")
            if certificate.get("lean_report_sha256") != file_hash(LEAN_PATH):
                issues.append("Lean report hash mismatch")

            reconstruction_id = registry_row["reconstruction_claim_id"]
            reconstruction_certificate = load(ROOT / "claims" / reconstruction_id / "certificate.json")
            if reconstruction_certificate.get("outcome") != "PROVED" or target["native_reconstruction"].get("transfers_source_validity") is not False:
                issues.append("native reconstruction is not correctly retained as proved-but-distinct")

            totals.update({
                "steps": len(spec["steps"]),
                "checks": len(spec["checks"]),
                "candidates": len(primary_census.candidates),
                "decisions": len(primary_decisions),
                "controls": len(primary_controls),
            })
        except Exception as error:
            issues.append(f"{type(error).__name__}: {error}")
        results.append({
            "claim_id": claim_id,
            "atomic_id": registry_row["atomic_id"],
            "owner": registry_row["owner"],
            "declaration": registry_row["declaration"],
            "source_artifact_validity": "DISPROVED" if not issues else "HALT",
            "native_reconstruction": "PROVED_DISTINCT" if not issues else "UNVERIFIED",
            "open": False if not issues else True,
            "passed": not issues,
            "issues": issues,
            "engine_receipt_hash": certificate.get("engine_receipt_hash"),
            "lean_theorem": certificate.get("lean_theorem"),
        })

    owner_counts = Counter(row["owner"] for row in rows)
    expected_owners = Counter({"mathematics": 9, "computation": 2, "quantum_computation": 1})
    if owner_counts != expected_owners:
        global_issues.append(f"owner count mismatch: {dict(owner_counts)}")
    if totals != Counter({"steps": 120, "checks": 60, "candidates": 3072, "decisions": 3072, "controls": 48}):
        global_issues.append(f"aggregate proof totals mismatch: {dict(totals)}")
    if not (
        lean.get("status") == "PASS"
        and lean.get("source_validity_obligation_count") == 12
        and lean.get("disproved_count") == 12
        and lean.get("open_count") == 0
        and lean.get("theorem_axiom_audit") == "empty"
        and lean.get("sorry_or_admit_used") is False
    ):
        global_issues.append("aggregate source-validity Lean report did not pass")
    if not (
        whole.get("status") == "PASS"
        and whole.get("claim_count") == 2777
        and whole.get("accepted_claim_count") == 2777
        and whole.get("source_binding_passed_claim_count") == 2777
        and whole.get("source_binding_issue_count") == 0
        and whole.get("issue_count") == 0
    ):
        global_issues.append("updated whole-model Lean report did not pass 2777/2777")
    passed_count = sum(row["passed"] for row in results)
    status = "PASS" if passed_count == 12 and not global_issues else "HALT"
    report = {
        "schema": "sft-v3-openai-2026-source-validity-completeness-audit/2",
        "status": status,
        "audit_date": "2026-08-02",
        "corrected_target": "SFTValid(exact frozen OpenAI source artifact)",
        "source_artifact_validity": {"disproved": passed_count, "proved": 0, "open": 12 - passed_count},
        "native_reconstructions": {"proved_distinct": passed_count, "transferred_to_source_validity": 0},
        "ownership": dict(owner_counts),
        "proof_totals": dict(totals),
        "all_twelve_chains_pass": passed_count == 12,
        "engine_seal": engine_seal["seal_id"],
        "verification_authority_seal": authority_seal["authority_seal_id"],
        "registry_identity": declared_registry_identity,
        "lean_report_sha256": file_hash(LEAN_PATH),
        "whole_model_report_sha256": file_hash(WHOLE_PATH),
        "whole_model": {
            "status": whole.get("status"),
            "claims": whole.get("claim_count"),
            "source_bound": whole.get("source_binding_passed_claim_count"),
            "candidates": whole.get("candidate_count"),
            "decisions": whole.get("decision_count"),
            "controls": whole.get("control_count"),
            "issues": whole.get("issue_count"),
        },
        "global_issues": global_issues,
        "rows": results,
    }
    report["audit_identity"] = identity(report)
    JSON_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# OpenAI 2026 SFT Source-Validity Completeness Audit V2",
        "",
        f"Status: **{status}**",
        "",
        "This audit corrects the earlier category error. The target is the SFT validity of each exact frozen OpenAI artifact. The separately proved SFT-native reconstruction is not transferred back to that artifact.",
        "",
        f"- Exact source-artifact validity disproofs: **{passed_count}/12**",
        f"- Native reconstructions retained as distinct SFT results: **{passed_count}/12**",
        f"- Open chains: **{12 - passed_count}**",
        f"- Ownership: **9 Mathematics / 2 Classical Computation / 1 Quantum Computation**",
        f"- Proof execution: **{totals['steps']} steps / {totals['checks']} checks / {totals['candidates']} candidates / {totals['controls']} controls**",
        f"- Whole-model Lean: **{whole.get('status')} ({whole.get('claim_count')}/{whole.get('claim_count')})**",
        "",
        "| # | Owner | Frozen declaration | Source validity | Native reconstruction |",
        "|---:|---|---|---|---|",
    ]
    for index, row in enumerate(results, start=1):
        lines.append(f"| {index} | {row['owner']} | `{row['declaration']}` | {row['source_artifact_validity']} | {row['native_reconstruction']} |")
    lines.extend([
        "",
        "## Meaning of the result",
        "",
        "For each artifact, assuming SFT validity forces an empty axiom vector and admitted source carriers. The exact frozen source instead exposes `propext`, `Classical.choice`, and `Quot.sound`, plus the theorem-specific carrier conflict. Lean proves the contradiction and the resulting validity negation without user axioms. This does not assert that carrier rejection is the logical negation of the conventional mathematical conclusion; it proves the explicitly registered proposition that the submitted artifact is not an SFT-valid derivation.",
        "",
        f"Audit identity: `{report['audit_identity']}`",
    ])
    MD_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "chains_passed": passed_count,
        "source_validity_disproved": passed_count,
        "native_reconstructions_distinct": passed_count,
        "open": 12 - passed_count,
        "global_issues": global_issues,
        "json_report": JSON_REPORT.relative_to(ROOT).as_posix(),
        "markdown_report": MD_REPORT.relative_to(ROOT).as_posix(),
        "audit_identity": report["audit_identity"],
    }, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
