#!/usr/bin/env python3
"""Admit the frozen AIX-001--002 Classical Computation specializations."""

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

from sft.computation.aix_001_002_laws_v1 import IDS, SPECS  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


REGISTRY = "census/computation_aix_001_002_target_registry_v1.json"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{tool} returned malformed evidence") from exc
        if completed.returncode or payload.get("status") != expected:
            raise SystemExit(f"{tool} failed; AIX admission halted")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("aix_" + claim_id.replace("-", "_"), path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def materialize(claim_id: str, execution, receipt, captured: dict[str, object], row: dict[str, object], index: int) -> None:
    spec = SPECS[claim_id]
    sealed = captured["sealed"]
    external = captured["external"]
    package = ROOT / "claims" / claim_id
    payloads = {
        "candidate_census.json": {"claim_id": claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": claim_id, "controls": asdict(sealed)["controls"]},
        "certificate.json": {
            "claim_id": claim_id,
            "classical_computation_obligation": f"SFT-COMP-OBL-AIX-{index:03d}",
            "status": "independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "exact_result": spec.exact_result,
            "closure_scope": receipt.closure_status,
            "controls_passed": all(control.passed for control in sealed.controls),
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "independently_recomputed": external.passed,
            "free_parameters": [],
            "imported_axioms": [],
        },
        "registration.json": {
            "$schema": "../../governance/claim.schema.json",
            "branch": "computation",
            "claim_id": claim_id,
            "title": spec.title,
            "statement": spec.statement,
            "dependencies": list(spec.dependencies),
            "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"],
            "axioms": [],
            "free_parameters": [],
            "excluded_inputs": list(spec.boundary_exclusions),
            "candidate_grammar": {
                "boundary": spec.grammar_boundary,
                "generator": spec.generation_rule,
                "expected_cardinality": 256,
                "unique_survivor": spec.exact_result,
                "completeness_certificate": "untouched-engine complete literal product",
            },
            "pre_source_target_registry": REGISTRY,
            "empirical_protocol": None,
            "intended_certificate": "Independent regeneration of all 256 candidates, the sole survivor, depth-independent closure, exact operational witnesses and four adverse controls.",
            "provenance_classes": ["forward_forcing"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-31",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "status": "independently_replicated",
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    (package / "STATUS.md").write_text(
        f"# {claim_id}\n\nStatus: `independently_replicated`\n\n"
        f"- Formal Classical Computation specialization; no trained-model or conversational result is admitted.\n"
        f"- Closure: `{receipt.closure_status}`\n"
        f"- Exact result: {spec.exact_result}\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
        f"- Receipt path: `{row['receipt_path']}`\n",
        encoding="utf-8",
    )


def main() -> None:
    verify_seals()
    claims_path = ROOT / "census/claims.json"
    manifest_path = ROOT / "census/execution_manifest.json"
    existing = {row["claim_id"] for row in json.loads(claims_path.read_text(encoding="utf-8"))["claims"]}
    for index, claim_id in enumerate(IDS, 1):
        if claim_id in existing:
            raise SystemExit("already admitted: " + claim_id)
        missing = tuple(dependency for dependency in SPECS[claim_id].dependencies if dependency not in existing)
        if missing:
            raise SystemExit(f"missing dependencies for {claim_id}: {missing}")
        execution = load_execution(claim_id)
        captured: dict[str, object] = {}

        class Independent:
            def validate(self, sealed):
                captured["sealed"] = sealed
                result = execution.independent_validator.validate(sealed)
                captured["external"] = result
                return result

        receipt = EngineRepository(ROOT).execute_official(
            execution.program,
            Independent(),
            execution.source_files,
        )
        if not receipt.model_admitted:
            raise SystemExit("untouched engine did not admit " + claim_id)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write_json(manifest_path, manifest)
        row = next(row for row in json.loads(claims_path.read_text(encoding="utf-8"))["claims"] if row["claim_id"] == claim_id)
        materialize(claim_id, execution, receipt, captured, row, index)
        verify_seals()
        existing.add(claim_id)
        print(f"[{index}/{len(IDS)}] admitted {claim_id}: {receipt.receipt_hash}", flush=True)


if __name__ == "__main__":
    main()

