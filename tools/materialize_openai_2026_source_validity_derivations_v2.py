#!/usr/bin/env python3
"""Materialize twelve exact source-validity contradiction specifications."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.openai_2026.source_validity_v2 import ROUTE_DIMENSIONS, validate_spec


REGISTRY = ROOT / "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json"


def identity(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_seals() -> None:
    for tool, status in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        result = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        payload = json.loads(result.stdout)
        if result.returncode or payload.get("status") != status:
            raise SystemExit(f"materialization halted: {tool}")


def step(step_id: str, rule: str, premises: tuple[str, ...], conclusion: str,
         checks: tuple[str, ...] = (), dependencies: tuple[str, ...] = ()) -> dict[str, object]:
    return {
        "step_id": step_id,
        "rule": rule,
        "premises": list(premises),
        "conclusion": conclusion,
        "check_ids": list(checks),
        "dependency_claims": list(dependencies),
    }


def main() -> None:
    verify_seals()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry_input = dict(registry)
    declared_registry_identity = registry_input.pop("registry_identity")
    if identity(registry_input) != declared_registry_identity:
        raise SystemExit("materialization halted: registry identity mismatch")
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    summaries = []
    for row in registry["rows"]:
        claim_id = row["claim_id"]
        package = ROOT / "claims" / claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        source_binding = json.loads((package / "source_binding_v2.json").read_text(encoding="utf-8"))
        target = json.loads((package / "source_validity_target_v2.json").read_text(encoding="utf-8"))
        source_record = json.loads((ROOT / source_binding["source_statement_path"]).read_text(encoding="utf-8"))
        source_text = (ROOT / source_binding["source_file_path"]).read_text(encoding="utf-8")
        if identity(source_record) != row["source_statement_hash"]:
            raise SystemExit(f"source statement mismatch: {claim_id}")
        if source_binding["declaration"] != row["declaration"] or target["target"] != row["sft_validity_proposition"]:
            raise SystemExit(f"source target mismatch: {claim_id}")
        observed_tokens = [token for token in row["required_source_tokens"] if token in source_text]
        if observed_tokens != row["required_source_tokens"]:
            raise SystemExit(f"source token coverage failed: {claim_id}")
        dependencies = registration["dependencies"]
        if dependencies != row["governing_preexisting_claims"] or any(dep not in admitted for dep in dependencies):
            raise SystemExit(f"dependency mismatch: {claim_id}")
        generic = tuple(dep for dep in dependencies if dep in {
            "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001",
            "SFT-MATH-LOGIC-PROOF-001",
        })
        domain = tuple(dep for dep in dependencies if dep not in generic)
        source_axioms = source_binding["source_declared_axioms"]
        native_formula = target["native_reconstruction"]["native_formula"]
        checks = [
            {
                "check_id": "source-axiom-vector",
                "kind": "exact_list",
                "expected": ["propext", "Classical.choice", "Quot.sound"],
                "actual": source_axioms,
            },
            {
                "check_id": "axiom-zero-nonzero-contradiction",
                "kind": "zero_nonzero_contradiction",
                "required": 0,
                "observed": len(source_axioms),
            },
            {
                "check_id": "source-token-coverage",
                "kind": "token_coverage",
                "required": row["required_source_tokens"],
                "observed": observed_tokens,
            },
            {
                "check_id": "source-native-distinct",
                "kind": "distinct_identity",
                "left": row["source_statement_hash"],
                "right": identity(native_formula),
            },
            {
                "check_id": "nontransfer-flags",
                "kind": "all_false",
                "values": [
                    target["native_reconstruction"]["transfers_source_validity"],
                    source_binding["semantic_native_correspondence_asserted"],
                ],
            },
        ]
        steps = [
            step(
                "admission-laws",
                "dependency_composition",
                (),
                "SFT validity requires empty registered axioms, zero free parameters, generated-domain proof objects and a root-bound complete trace",
                dependencies=generic,
            ),
            step(
                "domain-laws",
                "dependency_composition",
                (),
                row["domain_contradiction"],
                dependencies=domain,
            ),
            step(
                "exact-artifact",
                "exact_source_extraction",
                (),
                "the exact frozen declaration, quantifiers, axiom vector and theorem-specific source tokens are fixed",
                checks=("source-axiom-vector", "source-token-coverage"),
            ),
            step(
                "assume-source-valid",
                "validity_assumption",
                ("exact-artifact",),
                row["sft_validity_proposition"],
            ),
            step(
                "validity-requirements",
                "definition_elimination",
                ("admission-laws", "assume-source-valid"),
                "the submitted artifact has zero registered axioms and every necessary source carrier is SFT-admitted",
            ),
            step(
                "source-failures",
                "exact_source_extraction",
                ("exact-artifact", "domain-laws"),
                f"the artifact has three registered axioms and requires {row['necessary_source_component']}",
                checks=("source-axiom-vector", "source-token-coverage"),
            ),
            step(
                "axiom-contradiction",
                "contradiction",
                ("validity-requirements", "source-failures"),
                "the same exact artifact has both zero registered axioms and three registered axioms",
                checks=("axiom-zero-nonzero-contradiction",),
            ),
            step(
                "carrier-conflict",
                "carrier_conflict",
                ("validity-requirements", "source-failures"),
                "the same necessary source component is both SFT-admitted and excluded by the governing SFT domain law",
            ),
            step(
                "validity-negation",
                "negation_introduction",
                ("assume-source-valid", "axiom-contradiction", "carrier-conflict"),
                target["registered_negation"],
            ),
            step(
                "nontransfer",
                "nontransfer",
                ("validity-negation",),
                "REGISTERED_SOURCE_VALIDITY_NEGATION",
                checks=("source-native-distinct", "nontransfer-flags"),
            ),
        ]
        spec = {
            "schema": "sft-v3-openai-2026-source-validity-disproof/2",
            "claim_id": claim_id,
            "atomic_id": row["atomic_id"],
            "title": registration["title"],
            "branch": registration["branch"],
            "source_declaration": row["declaration"],
            "source_commit": registry["source_commit"],
            "source_statement_hash": row["source_statement_hash"],
            "source_file_sha256": row["source_file_sha256"],
            "source_binding_hash": identity(source_binding),
            "source_declared_axioms": source_axioms,
            "source_quantifier_and_conjunct_order": row["source_quantifier_and_conjunct_order"],
            "quoted_quantifier_and_conjunct_order": source_binding["exact_quantifier_and_conjunct_order"],
            "required_source_tokens": row["required_source_tokens"],
            "necessary_source_component": row["necessary_source_component"],
            "domain_contradiction": row["domain_contradiction"],
            "sft_validity_proposition": row["sft_validity_proposition"],
            "registered_negation": row["registered_negation"],
            "contradiction_summary": (
                "SFT validity forces an empty axiom vector and admitted carriers; the exact source exposes three axioms "
                "and the theorem-specific excluded component. The assumption therefore entails a contradiction."
            ),
            "original_reconstruction_claim_id": row["reconstruction_claim_id"],
            "original_reconstruction_formula_hash": identity(native_formula),
            "native_reconstruction_used_as_validity_premise": False,
            "dependencies": dependencies,
            "route_dimensions": ROUTE_DIMENSIONS,
            "checks": checks,
            "steps": steps,
            "proof_outcome": "DISPROVED",
            "proof_kind": "validity_contradiction",
            "outcome_axis_present": False,
            "registry_identity": declared_registry_identity,
        }
        certificate = validate_spec(spec)
        spec["primary_preflight_certificate"] = certificate
        spec["derivation_identity"] = identity(spec)
        write_json(package / "derivation_spec_v2.json", spec)
        summaries.append({
            "claim_id": claim_id,
            "outcome": certificate["proof_outcome"],
            "steps": certificate["step_count"],
            "checks": certificate["check_count"],
            "derivation_identity": spec["derivation_identity"],
        })
    verify_seals()
    print(json.dumps({
        "status": "MATERIALIZED",
        "claims": len(summaries),
        "disproved": len(summaries),
        "proved": 0,
        "open": 0,
        "outcome_axis_present": False,
        "native_reconstruction_transferred": False,
        "summaries": summaries,
    }, indent=2))


if __name__ == "__main__":
    main()
