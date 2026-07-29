#!/usr/bin/env python3
"""Freeze the complete pre-Synthesis receipt and dependency surface."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "census/cross_branch_synthesis_prior_input_v1.json"
ROOT_ID = "SFT-ROOT-THERE-IS-NO-NOTHING"


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def identity(payload: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("cross-branch prior input already exists; append-only freeze preserved")
    census_path = ROOT / "census/claims.json"
    census = json.loads(census_path.read_text())
    rows = census["claims"]
    identities = {row["claim_id"] for row in rows}
    claims = []
    dependencies = {}
    branches = Counter()
    prediction_ids = []
    empirical_ids = []
    for row in rows:
        claim_id = row["claim_id"]
        registration_path = ROOT / "claims" / claim_id / "registration.json"
        package = ROOT / "claims" / claim_id
        controls_path = ROOT / "claims" / claim_id / "controls.json"
        registration = json.loads(registration_path.read_text())
        matching_certificates = []
        for candidate_path in sorted(package.glob("certificate*.json")):
            candidate = json.loads(candidate_path.read_text())
            if candidate.get("engine_receipt_hash") == row["receipt_hash"]:
                matching_certificates.append(candidate_path)
        if len(matching_certificates) != 1:
            raise SystemExit(f"{claim_id} requires exactly one current receipt-bound certificate; found {len(matching_certificates)}")
        certificate_path = matching_certificates[0]
        certificate = json.loads(certificate_path.read_text())
        deps = tuple(registration.get("dependencies", ()))
        missing = tuple(dep for dep in deps if dep not in identities)
        if missing:
            raise SystemExit(f"{claim_id} has missing dependencies: {missing}")
        controls = json.loads(controls_path.read_text()).get("controls", ())
        if not controls or not all(control.get("passed") for control in controls):
            raise SystemExit(f"{claim_id} lacks complete passing controls")
        branch = row["branch"]
        branches[branch] += 1
        dependencies[claim_id] = deps
        text = " ".join((claim_id, row["title"], row["statement"])).lower()
        if "predict" in text or "standing test" in text:
            prediction_ids.append(claim_id)
        if (ROOT / "claims" / claim_id / "empirical_validation.json").is_file():
            empirical_ids.append(claim_id)
        claims.append({
            "claim_id": claim_id,
            "branch": branch,
            "receipt_hash": row["receipt_hash"],
            "receipt_path": row["receipt_path"],
            "registration_hash": sha(registration_path),
            "certificate_hash": sha(certificate_path),
            "certificate_path": certificate_path.relative_to(ROOT).as_posix(),
            "controls_hash": sha(controls_path),
            "dependencies": deps,
            "statement_hash": identity(row["statement"]),
        })

    roots = tuple(claim_id for claim_id, deps in dependencies.items() if not deps)
    state = {}
    def reaches_root(claim_id: str, trail=frozenset()) -> bool:
        if claim_id in state:
            return state[claim_id]
        if claim_id in trail:
            return False
        deps = dependencies[claim_id]
        result = claim_id == ROOT_ID if not deps else all(reaches_root(dep, trail | {claim_id}) for dep in deps)
        state[claim_id] = result
        return result
    root_failures = tuple(claim_id for claim_id in dependencies if not reaches_root(claim_id))
    if roots != (ROOT_ID,) or root_failures:
        raise SystemExit(f"dependency root failure: roots={roots}, failures={root_failures[:8]}")

    programme_path = ROOT / "census/v1_v2_novel_return_subcategories_2026-07-28.json"
    programme = json.loads(programme_path.read_text())
    if programme["completed_subcategory_count"] != 13:
        raise SystemExit("the thirteen prerequisite return subcategories are not complete")
    ownership_files = tuple(sorted(
        path for path in (ROOT / "audits").glob("*v1_v2*ownership*.json")
        if path.is_file()
    ))
    foundation_reconciliation = ROOT / "audits/ALL_FOUNDATIONAL_BRANCHES_RECONCILIATION_2026-07-28.json"
    return_audit = ROOT / "audits/V1_V2_NOVEL_DERIVATION_RETURN_AUDIT_2026-07-28.md"
    payload = {
        "schema": "sft-v3-cross-branch-synthesis-prior-input/1",
        "freeze_date": "2026-07-29",
        "scope": "Every model-admitted V3 claim before Cross-Branch Synthesis plus all registered V1/V2 ownership and novel-return ledgers.",
        "claim_count": len(claims),
        "claims": claims,
        "branch_counts": dict(sorted(branches.items())),
        "dependency_edge_count": sum(len(deps) for deps in dependencies.values()),
        "unique_dependency_root": ROOT_ID,
        "all_claims_root_traced": not root_failures,
        "root_trace_failure_count": len(root_failures),
        "prediction_claim_count": len(prediction_ids),
        "prediction_claim_ids": sorted(prediction_ids),
        "empirical_claim_count": len(empirical_ids),
        "empirical_claim_ids": sorted(empirical_ids),
        "all_claims_have_passing_controls": True,
        "all_claims_have_unique_branch_owner": sum(branches.values()) == len(claims),
        "current_census_hash": sha(census_path),
        "programme_census_hash": sha(programme_path),
        "prerequisite_subcategories_complete": programme["completed_subcategory_count"],
        "ownership_inputs": [{"path": path.relative_to(ROOT).as_posix(), "hash": sha(path)} for path in ownership_files],
        "foundation_reconciliation": {"path": foundation_reconciliation.relative_to(ROOT).as_posix(), "hash": sha(foundation_reconciliation)},
        "novel_return_audit": {"path": return_audit.relative_to(ROOT).as_posix(), "hash": sha(return_audit)},
        "boundary": "This is a dated complete pre-Synthesis surface. Later lawful extensions append new receipts and require a successor synthesis input; they do not change this freeze.",
    }
    payload["input_identity"] = identity(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("claim_count", "dependency_edge_count", "unique_dependency_root", "all_claims_root_traced", "prediction_claim_count", "empirical_claim_count", "input_identity")}, indent=2))


if __name__ == "__main__":
    main()
