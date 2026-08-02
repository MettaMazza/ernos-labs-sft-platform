#!/usr/bin/env python3
"""Materialize the twelve frozen SFT proof specifications without admitting them."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity
from sft.openai_2026.derivation_v1 import ROUTE_DIMENSIONS, validate_derivation_spec
from sft.openai_2026.obligations_v1 import BLUEPRINTS, ORDER


REGISTRY = ROOT / "census/openai_ten_advances_2026_sft_obligation_registry_v1.json"


def object_identity(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
            raise SystemExit(f"derivation materialization halted: {tool}")


def main() -> None:
    verify_seals()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry_identity = registry["registry_identity"]
    identity_input = dict(registry)
    identity_input.pop("registry_identity")
    if object_identity(identity_input) != registry_identity:
        raise SystemExit("derivation materialization halted: registry identity mismatch")
    rows = registry.get("rows")
    if not isinstance(rows, list) or tuple(row.get("claim_id") for row in rows) != ORDER:
        raise SystemExit("derivation materialization halted: registry order mismatch")
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    summaries = []
    for row in rows:
        claim_id = row["claim_id"]
        package = ROOT / "claims" / claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        source = json.loads((package / "source_statement.json").read_text(encoding="utf-8"))
        translation = json.loads((package / "translation.json").read_text(encoding="utf-8"))
        correspondence = json.loads((package / "correspondence_obligation.json").read_text(encoding="utf-8"))
        if object_identity(source) != row["source_statement_hash"]:
            raise SystemExit(f"derivation materialization halted: source record mismatch: {claim_id}")
        if source["exact_quantifier_and_conjunct_order"] != translation["source_quantifier_and_conjunct_order"]:
            raise SystemExit(f"derivation materialization halted: quantifier mismatch: {claim_id}")
        if registration["statement"] != translation["native_formula"] or row["native_formula"] != translation["native_formula"]:
            raise SystemExit(f"derivation materialization halted: native proposition mismatch: {claim_id}")
        dependencies = list(registration["dependencies"])
        if dependencies != row["governing_preexisting_claims"] or any(dep not in admitted for dep in dependencies):
            raise SystemExit(f"derivation materialization halted: dependency mismatch: {claim_id}")
        blueprint = deepcopy(BLUEPRINTS[claim_id])
        steps = blueprint.pop("mathematical_steps")
        dependency_steps = [step for step in steps if step["rule"] == "dependency_composition"]
        if not dependency_steps:
            raise SystemExit(f"derivation materialization halted: no dependency-composition step: {claim_id}")
        for step in steps:
            step["dependency_claims"] = []
        for index, dependency in enumerate(dependencies):
            dependency_steps[index % len(dependency_steps)]["dependency_claims"].append(dependency)
        spec = {
            "schema": "sft-v3-openai-2026-native-derivation/1",
            "claim_id": claim_id,
            "atomic_id": row["atomic_id"],
            "title": registration["title"],
            "branch": registration["branch"],
            "source_declaration": source["declaration"],
            "source_commit": source["source_commit"],
            "source_statement_hash": row["source_statement_hash"],
            "source_signature_hash": source["signature_sha256"],
            "translation_hash": sha256_identity(translation),
            "registry_identity": registry_identity,
            "native_formula": translation["native_formula"],
            "source_quantifier_and_conjunct_order": source["exact_quantifier_and_conjunct_order"],
            "translated_quantifier_and_conjunct_order": translation["source_quantifier_and_conjunct_order"],
            "correspondence_required_preservation": correspondence["required_preservation"],
            "governing_grammar_composition": row["governing_grammar_composition"],
            "dependencies": dependencies,
            "route_dimensions": ROUTE_DIMENSIONS,
            "steps": steps,
            "proof_outcome": "PROVED",
            "proof_kind": "constructive_proof",
            "outcome_axis_present": False,
            "upstream_proof_used_as_premise": False,
            **blueprint,
        }
        certificate = validate_derivation_spec(spec)
        spec["primary_preflight_certificate"] = certificate
        spec["derivation_identity"] = object_identity(spec)
        write_json(package / "derivation_spec_v1.json", spec)
        summaries.append({
            "claim_id": claim_id,
            "outcome": certificate["proof_outcome"],
            "steps": certificate["step_count"],
            "checks": certificate["check_count"],
            "derivation_identity": spec["derivation_identity"],
        })
    print(json.dumps({
        "status": "MATERIALIZED",
        "claims": len(summaries),
        "outcome_axis_present": False,
        "upstream_proof_used_as_premise": False,
        "summaries": summaries,
    }, indent=2))


if __name__ == "__main__":
    main()
