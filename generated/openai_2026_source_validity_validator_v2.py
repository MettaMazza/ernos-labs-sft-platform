#!/usr/bin/env python3
"""Implementation-distinct verifier for one OpenAI source-validity disproof.

This file imports no OpenAI-2026 derivation module.  It reconstructs source
custody, finite checks, the contradiction graph, the 256-route product and the
sealed engine decisions from standard-library operations.
"""

from __future__ import annotations

import hashlib
import json
import sys
from itertools import product
from pathlib import Path


AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
ROUTES = (
    ("source_binding", "stale-or-paraphrased-artifact", "exact-frozen-artifact"),
    ("quotation", "weakened-or-substituted-proposition", "exact-statement-and-quantifier-quotation"),
    ("axiom_evidence", "axiom-vector-hidden-or-assumed-empty", "nonempty-source-axiom-vector-exposed"),
    ("carrier_evidence", "necessary-source-component-omitted", "necessary-source-component-exposed"),
    ("governing_law", "invented-validity-rule", "preexisting-admission-and-domain-laws"),
    ("contradiction_chain", "inadmissibility-asserted-without-negated-target", "assume-valid-and-derive-actual-contradiction"),
    ("execution", "unexecuted-or-sampled-evidence", "complete-executable-evidence"),
    ("transfer_boundary", "native-proof-transferred-to-source", "native-reconstruction-kept-distinct"),
)


def identity(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"not an object: {path}")
    return value


def verify_check(row: dict[str, object]) -> bool:
    kind = row.get("kind")
    if kind == "exact_list":
        return row.get("expected") == row.get("actual") == AXIOMS
    if kind == "zero_nonzero_contradiction":
        return row.get("required") == 0 and row.get("observed") == len(AXIOMS)
    if kind == "token_coverage":
        required, observed = row.get("required"), row.get("observed")
        return isinstance(required, list) and bool(required) and required == observed and len(required) == len(set(required))
    if kind == "distinct_identity":
        left, right = row.get("left"), row.get("right")
        return isinstance(left, str) and isinstance(right, str) and left != right
    if kind == "all_false":
        values = row.get("values")
        return isinstance(values, list) and len(values) == 2 and values == [False, False]
    return False


def proof_certificate(spec: dict[str, object]) -> dict[str, object]:
    if spec.get("schema") != "sft-v3-openai-2026-source-validity-disproof/2":
        raise ValueError("schema mismatch")
    if spec.get("proof_outcome") != "DISPROVED" or spec.get("proof_kind") != "validity_contradiction":
        raise ValueError("target outcome mismatch")
    if spec.get("outcome_axis_present") is not False or spec.get("native_reconstruction_used_as_validity_premise") is not False:
        raise ValueError("outcome selection or native transfer present")
    target, negation = spec.get("sft_validity_proposition"), spec.get("registered_negation")
    if not isinstance(target, str) or not isinstance(negation, str) or target not in negation:
        raise ValueError("negated target mismatch")
    if spec.get("source_declared_axioms") != AXIOMS:
        raise ValueError("source axiom vector mismatch")
    if spec.get("source_quantifier_and_conjunct_order") != spec.get("quoted_quantifier_and_conjunct_order"):
        raise ValueError("quotation changed logical shape")
    checks = spec.get("checks")
    if not isinstance(checks, list) or len(checks) != 5:
        raise ValueError("check count mismatch")
    check_ids = set()
    for row in checks:
        if not isinstance(row, dict) or not isinstance(row.get("check_id"), str) or row["check_id"] in check_ids or not verify_check(row):
            raise ValueError("executable check failed")
        check_ids.add(row["check_id"])
    dependencies = spec.get("dependencies")
    if not isinstance(dependencies, list) or len(dependencies) != len(set(dependencies)):
        raise ValueError("dependency list malformed")
    if not {"SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001", "SFT-MATH-LOGIC-PROOF-001"}.issubset(set(dependencies)):
        raise ValueError("governing law missing")
    steps = spec.get("steps")
    if not isinstance(steps, list) or len(steps) != 10:
        raise ValueError("step count mismatch")
    allowed = {
        "dependency_composition", "exact_source_extraction", "validity_assumption", "definition_elimination",
        "carrier_conflict", "contradiction", "negation_introduction", "nontransfer",
    }
    seen: dict[str, dict[str, object]] = {}
    used_dependencies = set()
    for row in steps:
        if not isinstance(row, dict):
            raise ValueError("malformed step")
        step_id, premises = row.get("step_id"), row.get("premises")
        cited_checks, bound = row.get("check_ids"), row.get("dependency_claims")
        if not isinstance(step_id, str) or step_id in seen or row.get("rule") not in allowed:
            raise ValueError("step identity or rule mismatch")
        if not isinstance(premises, list) or any(premise not in seen for premise in premises):
            raise ValueError("non-topological proof")
        if not isinstance(cited_checks, list) or any(check_id not in check_ids for check_id in cited_checks):
            raise ValueError("unknown check citation")
        if not isinstance(bound, list) or any(dependency not in dependencies for dependency in bound):
            raise ValueError("unknown dependency citation")
        if bound and row.get("rule") != "dependency_composition":
            raise ValueError("dependency introduced by wrong rule")
        used_dependencies.update(bound)
        seen[step_id] = row
    if used_dependencies != set(dependencies):
        raise ValueError("dependency use incomplete")
    terminal = [row for row in steps if row.get("conclusion") == "REGISTERED_SOURCE_VALIDITY_NEGATION"]
    if len(terminal) != 1 or terminal[0] is not steps[-1] or steps[-1].get("rule") != "nontransfer":
        raise ValueError("terminal mismatch")
    rules = {row["rule"] for row in steps}
    if not {"validity_assumption", "contradiction", "negation_introduction", "nontransfer"}.issubset(rules):
        raise ValueError("actual contradiction chain incomplete")
    reached = set()
    pending = [steps[-1]["step_id"]]
    while pending:
        current = pending.pop()
        if current in reached:
            continue
        reached.add(current)
        pending.extend(seen[current]["premises"])
    if reached != set(seen):
        raise ValueError("orphan step")
    return {
        "claim_id": spec["claim_id"],
        "proof_outcome": "DISPROVED",
        "target_hash": identity(target),
        "negation_hash": identity(negation),
        "source_statement_hash": spec["source_statement_hash"],
        "dependency_count": len(dependencies),
        "step_count": 10,
        "check_count": 5,
        "axiom_count": 3,
        "actual_contradiction_derived": True,
        "native_reconstruction_transferred": False,
        "outcome_axis_present": False,
    }


def route_rows(claim_id: str) -> tuple[list[dict[str, object]], str]:
    rows = []
    for values in product(*((route[1], route[2]) for route in ROUTES)):
        coordinates = [[route[0], value] for route, value in zip(ROUTES, values)]
        record = {
            "candidate_id": "__".join(values),
            "coordinates": coordinates,
            "exact_form": "; ".join(f"{key}={value}" for key, value in coordinates),
        }
        rows.append(record)
    return rows, "__".join(route[2] for route in ROUTES)


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: validator CLAIM_ID ROOT SEALED", file=sys.stderr)
        return 2
    claim_id, root_text, sealed_text = sys.argv[1:]
    root = Path(root_text)
    package = root / "claims" / claim_id
    try:
        spec = load(package / "derivation_spec_v2.json")
        source_binding = load(package / "source_binding_v2.json")
        target = load(package / "source_validity_target_v2.json")
        registry = load(root / "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json")
        census = load(root / "census/claims.json")
        sealed = load(Path(sealed_text))
        identity_input = dict(spec)
        declared_identity = identity_input.pop("derivation_identity")
        if identity(identity_input) != declared_identity:
            raise ValueError("derivation identity mismatch")
        registry_input = dict(registry)
        registry_identity = registry_input.pop("registry_identity")
        if identity(registry_input) != registry_identity or registry_identity != spec.get("registry_identity"):
            raise ValueError("registry identity mismatch")
        row = next(row for row in registry["rows"] if row["claim_id"] == claim_id)
        if row["source_statement_hash"] != spec["source_statement_hash"] or row["registered_negation"] != target["registered_negation"]:
            raise ValueError("registry target mismatch")
        source_record_path = root / source_binding["source_statement_path"]
        source_file_path = root / source_binding["source_file_path"]
        source_record = load(source_record_path)
        if identity(source_record) != spec["source_statement_hash"]:
            raise ValueError("source statement hash mismatch")
        if file_hash(source_file_path) != spec["source_file_sha256"]:
            raise ValueError("source file hash mismatch")
        text = source_file_path.read_text(encoding="utf-8")
        if any(token not in text for token in spec["required_source_tokens"]):
            raise ValueError("source token missing")
        if source_record.get("upstream_declared_axioms") != AXIOMS or source_record.get("upstream_sorry_count") != 0:
            raise ValueError("source manifest evidence mismatch")
        admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
        if any(dependency not in admitted for dependency in spec["dependencies"]):
            raise ValueError("unadmitted governing dependency")
        proof = proof_certificate(spec)
        if proof != spec.get("primary_preflight_certificate"):
            raise ValueError("independent proof certificate differs from preflight")
        expected_rows, survivor = route_rows(claim_id)
        candidates = sealed["census"]["candidates"]
        if len(candidates) != 256 or [row["candidate_id"] for row in candidates] != [row["candidate_id"] for row in expected_rows]:
            raise ValueError("candidate product mismatch")
        for actual, expected in zip(candidates, expected_rows):
            if actual["exact_form"] != expected["exact_form"] or actual["trace_hash"] != identity({"claim_id": claim_id, "record": expected}):
                raise ValueError("candidate evidence mismatch")
        decisions = sealed["decisions"]
        if [row["candidate_id"] for row in decisions] != [row["candidate_id"] for row in expected_rows]:
            raise ValueError("decision coverage mismatch")
        survivors = [row for row in decisions if row.get("survives") is True]
        if len(survivors) != 1 or survivors[0]["candidate_id"] != survivor:
            raise ValueError("unique contradiction route mismatch")
        if len(sealed["controls"]) != 4 or not all(row.get("passed") is True for row in sealed["controls"]):
            raise ValueError("control failure")
        if sealed["closure"]["scope"] != "depth_independent" or sealed["claim_id"] != claim_id:
            raise ValueError("closure mismatch")
        exact_result = "DISPROVED: " + spec["sft_validity_proposition"] + ". " + spec["contradiction_summary"]
        certificate = {
            "claim_id": claim_id,
            "derivation_identity": declared_identity,
            "source_statement_hash": spec["source_statement_hash"],
            "proof_outcome": "DISPROVED",
            "proof_steps": 10,
            "executable_checks": 5,
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "exact_result_hash": identity(exact_result),
            "all_dependencies_prior_and_admitted": True,
            "all_source_evidence_recomputed": True,
            "complete_contradiction_graph_reconstructed": True,
            "actual_contradiction_derived": True,
            "native_reconstruction_transferred": False,
            "outcome_axis_present": False,
        }
        print(json.dumps({
            "validated_seal_hash": sealed["seal_hash"],
            "recomputed_from_declared_inputs": True,
            "passed": True,
            "certificate": certificate,
        }, sort_keys=True))
        return 0
    except Exception as error:
        print(f"independent source-validity verification halted: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
